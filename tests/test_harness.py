"""Behavioral integration checks for installation, context and preservation."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

CLI = Path(__file__).resolve().parents[1] / "harness.py"


def git(root, *args):
    return subprocess.check_output(["git", "--no-optional-locks", "-C", str(root), *args], text=True).strip()


def tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file()}


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="harness test ")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "product repo"
        self.repo.mkdir()
        git(self.repo, "init", "-b", "main")
        (self.repo / "README.md").write_text("# Fixture product\n")
        git(self.repo, "add", "README.md")
        git(self.repo, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
            "commit", "-m", "initial fixture")
        self.workspace = self.root / "agent workspace"

    def command(self, *arguments, installed=False):
        script = self.workspace / "tools/harness.py" if installed else CLI
        return subprocess.run([sys.executable, str(script), *arguments], capture_output=True, text=True)

    def install(self, *extra):
        result = self.command("init", "--repo", str(self.repo), "--workspace", str(self.workspace), *extra)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_install_isolated_with_spaces_preserves_dirty_source_and_git_metadata(self):
        (self.repo / "README.md").write_text("# Owner's uncommitted edit\n")
        (self.repo / "owner.txt").write_text("private untracked draft\n")
        before = tree(self.repo)
        self.install()
        self.assertEqual(tree(self.repo), before)
        checkout = self.workspace / "worktrees/development"
        self.assertEqual((checkout / "README.md").read_text(), "# Fixture product\n")
        self.assertNotEqual((checkout / ".git/objects").resolve(), (self.repo / ".git/objects").resolve())
        self.assertNotEqual(git(checkout, "branch", "--show-current"), "main")
        result = self.command("doctor", "--workspace", str(self.workspace), "--json", installed=True)
        self.assertTrue(json.loads(result.stdout)["ok"], result.stderr)

    def test_existing_destination_and_dangling_symlink_are_preserved(self):
        self.workspace.mkdir()
        (self.workspace / "owner.txt").write_text("keep\n")
        before = tree(self.workspace)
        result = self.command("init", "--repo", str(self.repo), "--workspace", str(self.workspace))
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(tree(self.workspace), before)
        alias = self.root / "alias"
        alias.symlink_to(self.root / "missing")
        result = self.command("init", "--repo", str(self.repo), "--workspace", str(alias))
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue(alias.is_symlink())
        self.assertFalse((self.root / "missing").exists())

    def test_bad_base_and_overlapping_destination_leave_source_unchanged(self):
        before = tree(self.repo)
        for destination, ref in ((self.workspace, "missing-ref"), (self.repo / "private-agent", "HEAD")):
            result = self.command("init", "--repo", str(self.repo), "--workspace", str(destination), "--ref", ref)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(destination.exists())
        self.assertEqual(tree(self.repo), before)

    def test_install_from_source_already_on_default_task_branch(self):
        git(self.repo, "switch", "-c", "task/development")
        self.install()
        self.assertEqual(git(self.workspace / "worktrees/development", "branch", "--show-current"),
                         "task/development-2")

    def test_installed_copy_survives_moving_both_directories(self):
        self.install()
        moved = self.root / "moved"
        moved.mkdir()
        self.repo.rename(moved / self.repo.name)
        self.workspace.rename(moved / self.workspace.name)
        self.workspace = moved / self.workspace.name
        result = self.command("doctor", "--workspace", str(self.workspace), "--json", installed=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["ok"])

    def test_doctor_and_context_are_read_only_and_context_omits_history(self):
        self.install()
        (self.workspace / "tasks/current.md").write_text("# Current\n\nACTIVE-ACCEPTANCE\n")
        (self.workspace / "tasks/old.md").write_text("# Old\n\nOLD-TASK-CANARY\n\n[old](missing-history.md)\n")
        (self.workspace / "evidence/large.txt").write_text("ARCHIVE-CANARY\n" * 1000)
        board = self.workspace / "tasks.md"
        board.write_text(board.read_text().replace("Selected task: none", "Selected task: [current](tasks/current.md)"))
        before = tree(self.workspace)
        result = self.command("context", "--workspace", str(self.workspace), installed=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ACTIVE-ACCEPTANCE", result.stdout)
        self.assertNotIn("OLD-TASK-CANARY", result.stdout)
        self.assertNotIn("ARCHIVE-CANARY", result.stdout)
        self.assertEqual(tree(self.workspace), before)

    def test_context_marks_omitted_rules_explicitly_when_budget_small(self):
        self.install()
        result = self.command("context", "--workspace", str(self.workspace), "--max-chars", "10", "--json")
        payload = json.loads(result.stdout)
        self.assertTrue(any(not document["included"] for document in payload["documents"]))
        self.assertTrue(all("read this file explicitly" in document["text"]
                            for document in payload["documents"] if not document["included"]))

    def test_link_checks_ignore_code_but_reject_real_broken_link(self):
        self.install()
        doc = self.workspace / "handoffs/test.md"
        (self.workspace / "tasks/current.md").write_text("# Current\n\n[Adopted handoff](../handoffs/test.md)\n")
        board = self.workspace / "tasks.md"
        board.write_text(board.read_text().replace("Selected task: none", "Selected task: [current](tasks/current.md)"))
        doc.write_text("# Handoff\n\n`[literal](missing.txt)`\n\n```md\n[fenced](absent.txt)\n```\n")
        self.assertEqual(self.command("doctor", "--workspace", str(self.workspace)).returncode, 0)
        doc.write_text(doc.read_text() + "\n[real](not-found.md)\n")
        result = self.command("doctor", "--workspace", str(self.workspace))
        self.assertEqual(result.returncode, 1)
        self.assertIn("not-found.md", result.stdout)

    def test_doctor_rejects_main_checkout_and_invalid_task_selection(self):
        self.install()
        checkout = self.workspace / "worktrees/development"
        git(checkout, "switch", "main")
        self.assertEqual(self.command("doctor", "--workspace", str(self.workspace)).returncode, 1)
        git(checkout, "switch", "task/development")
        board = self.workspace / "tasks.md"
        board.write_text(board.read_text() + "\nSelected task: none\n")
        self.assertEqual(self.command("doctor", "--workspace", str(self.workspace)).returncode, 2)

    def test_record_keeps_actual_command_exit_code_output_and_cwd(self):
        self.install()
        result = self.command("record", "--workspace", str(self.workspace), "--label", "smoke-a",
                              "--cwd", "worktrees/development", "--", sys.executable, "-c",
                              "import sys; print('stdout'); print('stderr',file=sys.stderr); sys.exit(7)", installed=True)
        self.assertEqual(result.returncode, 7)
        receipt = json.loads((self.workspace / "evidence/smoke-a/commands.jsonl").read_text())
        self.assertEqual(receipt["exit_code"], 7)
        self.assertEqual(receipt["stdout"], result.stdout)
        self.assertEqual(receipt["stderr"], result.stderr)
        self.assertEqual(receipt["cwd"], "worktrees/development")
        self.assertGreaterEqual(receipt["elapsed_seconds"], 0)
        escape = self.command("record", "--workspace", str(self.workspace), "--label", "smoke-a",
                              "--cwd", "..", "--", "echo", "not-run")
        self.assertEqual(escape.returncode, 2)

    def test_scripted_baseline_handoff_and_recovery_preserve_owner_bytes(self):
        self.install()
        checkout = self.workspace / "worktrees/development"
        (checkout / "evidence").mkdir()
        (checkout / "evidence/local.txt").write_text("local evidence\n")
        original = b"# Handoff\n\n[evidence](evidence/old.txt)\n\nOwner note: keep exactly.\n"
        document = checkout / "handoff.md"
        document.write_bytes(original)
        owner = checkout / "owner.txt"
        owner.write_bytes(b"untracked owner draft\n")
        owner_before = owner.read_bytes()
        check = "from pathlib import Path; import re,sys; p=Path('handoff.md'); target=re.search(r'\\]\\(([^)]+)\\)',p.read_text()).group(1); sys.exit(0 if Path(target).is_file() else 1)"
        baseline = self.command("record", "--workspace", str(self.workspace), "--label", "smoke-a",
                                "--cwd", "worktrees/development", "--", sys.executable, "-c", check)
        self.assertEqual(baseline.returncode, 1)
        fixed = original.replace(b"evidence/old.txt", b"evidence/local.txt")
        document.write_bytes(fixed)
        task = self.workspace / "tasks/repair.md"
        task.write_text("# Repair\n\nFinal verification pending. Resume: run local link check.\n")
        board = self.workspace / "tasks.md"
        board.write_text(board.read_text().replace("Selected task: none", "Selected task: [repair](tasks/repair.md)"))
        (self.workspace / "handoffs/repair.md").write_text("# Handoff\n\nVerification pending; owner released. Read task and run local link check.\n")
        recovered = self.command("context", "--workspace", str(self.workspace), "--json", installed=True)
        self.assertIn("Final verification pending", recovered.stdout)
        verification = self.command("record", "--workspace", str(self.workspace), "--label", "smoke-b",
                                    "--cwd", "worktrees/development", "--", sys.executable, "-c", check,
                                    installed=True)
        self.assertEqual(verification.returncode, 0)
        self.assertEqual(document.read_bytes(), fixed)
        self.assertEqual(owner.read_bytes(), owner_before)
        self.assertEqual(git(checkout, "rev-parse", "HEAD"), git(self.repo, "rev-parse", "HEAD"))
        # A path-only check may pass CRLF, so acceptance must separately compare exact bytes.
        document.write_bytes(fixed.replace(b"\n", b"\r\n"))
        self.assertNotEqual(document.read_bytes(), fixed)
        document.write_bytes(fixed)


if __name__ == "__main__":
    unittest.main()
