#!/usr/bin/env python3
"""Create and inspect a local coding-agent workspace. Python 3.10+, Git; no packages."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.parse import unquote, urlsplit


FILES = {
    "README.md": """# Agent coordination workspace

Start at [AGENTS.md](AGENTS.md), or run `python3 tools/harness.py context`.
The [task board](tasks.md) owns the current selection; [WORKSPACE.md](WORKSPACE.md)
maps the files. Run `python3 tools/harness.py doctor` for local validation.
Path bindings live in `harness.json`. Keep product code in `worktrees/`.
""",
    "AGENTS.md": """# Workspace entry

Start with `python3 tools/harness.py context` from this directory. It reads the
operating rules, map, task board and selected task; follow any explicit pointers
it reports as omitted. Read scoped instructions in the task checkout before edits.

For `init context`, orient read-only and report scope, drift and the next action.
For a task already selected by the user, continue its authorized work after
orientation. Preserve existing edits and ownership; verify before claiming done.

If a run requires command receipts, use the recording command supplied in its
launch prompt from the very first shell read. Recording is optional otherwise.
""",
    "AGENT.md": """# Operating authority

The user's instructions define scope and authorization. `tasks.md` selects local
work; its selected task owns acceptance, progress, ownership and the resume point.
`decisions.md` holds accepted durable decisions. `harness.json` owns path bindings.
The selected checkout owns code; live source hosting, trackers and runtimes own
their external state. Date saved evidence and refresh external facts when needed.

Keep the reference repository unchanged. Work in the configured task checkout on
a task branch. Inspect existing edits, ownership and scoped instructions first.
One agent owns each mutable checkout. Delegate only when authorized. Do not put
secrets, personal profiles or private logs in product commits.

Verify each acceptance criterion with source or executed evidence appropriate to
the claim. Local checks, CI, publication and deployment prove different things.
Record failures and limits. Finish authorized preparation before seeking a
separate publication decision; carry forward existing approvals. Keep a concise
handoff when transferring work and release ownership explicitly.
""",
    "WORKSPACE.md": """# Workspace map

`harness.json` contains the reference repo, committed base and isolated checkout.
Paths resolve from this directory. Inspect current Git state with `doctor`.

- `tasks.md`: the single current selection and links to completed work.
- `tasks/`: individual scopes, acceptance and progress.
- `decisions.md`: accepted decisions with reasons and sources.
- `evidence/`: dated command receipts and observations, excluded from default context.
- `handoffs/`: task transfers; read only the handoff adopted by the selected task.
- `templates/`: task and handoff starting points.
- `worktrees/`: isolated product checkouts.
- `tools/harness.py`: installed self-contained CLI; no service or agent is launched.

Use `python3 tools/harness.py doctor` for local checks. Runtime, source-host and
tracker access come from your environment and are not installed by this tool.
""",
    "tasks.md": """# Task board

Selected task: none

To select user-authorized work, copy `templates/task.md` to `tasks/your-task.md`
and replace the line above with `Selected task: [your-task](tasks/your-task.md)`.
Keep exactly one selection line. Set it back to `none` when the task is closed;
keep dated completed-work links below instead of marking them selected.

## Completed work

None recorded.
""",
    "decisions.md": "# Accepted decisions\n\nNo decisions recorded. Add a date, source and reason when a decision is accepted.\n",
    "templates/task.md": """# Task: replace this title

## Request and scope

Record the full requested outcome, source and authorization. Name the task
checkout, owner and any actions reserved for a separate decision.

## Acceptance

List each deliverable and the evidence needed to accept it.

## State and verification

Record branch, base/HEAD, existing edits, commands, results and evidence paths.
Keep protected-file hashes when preservation is material. Prefer hashes over
embedding unrelated file contents in the default context.

## Resume

Give the next concrete action, expected result, dependencies and ownership.
Link a handoff only if a transfer needs one. Release ownership at closure.
""",
    "templates/handoff.md": """# Task handoff

- Updated at and source request:
- Selected task and full remaining goal:
- Authorized actions and acceptance still open:
- Checkout, owner, branch, base/HEAD and existing edits:
- Verified result and evidence links:
- Failed, blocked or unrun checks and claim limits:
- Next exact action and expected result:
- Active resource handles, ownership release and any recovery steps:

Reference existing evidence rather than copying transcripts or large source
files. The next agent must inspect the checkout and verify current facts.
""",
    ".gitignore": "worktrees/\n__pycache__/\n*.pyc\n.env\n.env.*\n!.env.example\n",
}


def git(directory, *arguments):
    return subprocess.check_output(
        ["git", "--no-optional-locks", "-C", str(directory), *arguments],
        text=True, stderr=subprocess.PIPE,
    ).strip()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def initialize(args):
    repository = Path(git(Path(args.repo).resolve(), "rev-parse", "--show-toplevel")).resolve()
    requested = Path(args.workspace).expanduser()
    if requested.exists() or requested.is_symlink():
        raise ValueError(f"Destination already exists; nothing changed: {requested}")
    destination = requested.resolve()
    if destination.exists():
        raise ValueError(f"Destination already exists; nothing changed: {destination}")
    if destination.is_relative_to(repository) or repository.is_relative_to(destination):
        raise ValueError("Workspace and reference repository must be separate directories")
    if args.ref.startswith("-"):
        raise ValueError("Reference cannot start with a dash")
    revision = git(repository, "rev-parse", "--verify", f"{args.ref}^{{commit}}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".harness-init-", dir=destination.parent))
    try:
        checkout = staging / "worktrees/development"
        checkout.parent.mkdir()
        subprocess.run(["git", "clone", "--no-hardlinks", "--no-checkout", str(repository), str(checkout)],
                       check=True, capture_output=True, text=True)
        branches = git(checkout, "for-each-ref", "--format=%(refname:short)", "refs/heads").splitlines()
        branch, suffix = "task/development", 1
        while branch in branches:
            suffix += 1
            branch = f"task/development-{suffix}"
        git(checkout, "switch", "-c", branch, revision)
        try:
            upstream = git(repository, "remote", "get-url", "origin")
        except subprocess.CalledProcessError:
            git(checkout, "remote", "remove", "origin")
        else:
            git(checkout, "remote", "set-url", "origin", upstream)
        for name, content in FILES.items():
            path = staging / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        for name in ("tasks", "evidence", "handoffs", "tools"):
            (staging / name).mkdir(exist_ok=True)
        shutil.copyfile(Path(__file__).resolve(), staging / "tools/harness.py")
        write_json(staging / "harness.json", {
            "schema_version": 1, "repository": os.path.relpath(repository, destination),
            "checkout": "worktrees/development", "base_revision": revision,
        })
        # Rename only a directory created by this invocation; never merge into existing state.
        if destination.exists():
            raise ValueError("Destination appeared during setup; refusing to replace it")
        staging.rename(destination)
    finally:
        if staging.exists():
            shutil.rmtree(staging)
    print(f"Created: {destination}\nBase: {revision}\nNext: cd {destination}\n"
          "python3 tools/harness.py doctor\npython3 tools/harness.py context")
    return 0


def load(workspace):
    root = Path(workspace).expanduser().resolve()
    config = json.loads((root / "harness.json").read_text(encoding="utf-8"))
    if config.get("schema_version") != 1:
        raise ValueError("Unsupported harness.json schema_version")
    repository = (root / config["repository"]).resolve()
    checkout = (root / config["checkout"]).resolve()
    if not checkout.is_relative_to(root / "worktrees"):
        raise ValueError("Configured checkout must be under this workspace's worktrees/")
    return root, config, repository, checkout


def prose(markdown):
    """Ignore fenced and inline code for local-path checks; not a full Markdown renderer."""
    lines, fence = [], None
    for line in markdown.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines), flags=re.DOTALL)


def selected_task(root):
    board = (root / "tasks.md").read_text(encoding="utf-8")
    selections = re.findall(r"^Selected task: (.+)$", board, flags=re.MULTILINE)
    if len(selections) != 1:
        raise ValueError("tasks.md must contain exactly one 'Selected task:' line")
    if selections[0] == "none":
        return None
    match = re.fullmatch(r"\[[^\]]+\]\((tasks/[^)]+\.md)\)", selections[0])
    if not match:
        raise ValueError("Selected task must be 'none' or a Markdown link under tasks/")
    path = (root / match.group(1)).resolve()
    if not path.is_relative_to(root / "tasks") or not path.is_file():
        raise ValueError("Selected task does not resolve to a file under tasks/")
    return path


def inspect(workspace):
    root, config, repository, checkout = load(workspace)
    errors = [f"Missing: {name}" for name in FILES if not (root / name).is_file()]
    if not (root / "tools/harness.py").is_file():
        errors.append("Missing: tools/harness.py")
    task = selected_task(root)
    documents = list(root.glob("*.md"))
    documents.extend((root / "templates").glob("*.md"))
    if task:
        documents.append(task)
        # Only a handoff adopted by the selected task can affect current checks.
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", prose(task.read_text(encoding="utf-8"))):
            handoff = (task.parent / target.split("#", 1)[0]).resolve()
            if handoff.is_relative_to(root / "handoffs") and handoff.is_file():
                documents.append(handoff)
    for document in documents:
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", prose(document.read_text(encoding="utf-8"))):
            target = target.strip().removeprefix("<").removesuffix(">")
            parsed = urlsplit(target)
            if parsed.scheme or not parsed.path:
                continue
            if not (document.parent / unquote(parsed.path)).exists():
                errors.append(f"Broken local path: {document.relative_to(root)} -> {target}")
    source_top = Path(git(repository, "rev-parse", "--show-toplevel")).resolve()
    top = Path(git(checkout, "rev-parse", "--show-toplevel")).resolve()
    branch = git(checkout, "branch", "--show-current")
    if source_top != repository or top != checkout or source_top == top:
        errors.append("Reference and task checkout must be distinct repository roots")
    if not branch or branch in {"main", "master"}:
        errors.append("Task checkout must be on a task branch")
    git(checkout, "cat-file", "-e", f"{config['base_revision']}^{{commit}}")
    return {
        "ok": not errors, "workspace": str(root), "repository": str(repository),
        "checkout": str(checkout), "branch": branch, "head": git(checkout, "rev-parse", "HEAD"),
        "status": git(checkout, "status", "--porcelain=v1"),
        "selected_task": str(task.relative_to(root)) if task else None, "errors": errors,
        "scope": "Local paths and Git only; external state and task acceptance are unverified.",
    }


def doctor(args):
    result = inspect(args.workspace)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("Workspace: " + ("OK" if result["ok"] else "REVIEW"))
        print(f"Checkout: {result['checkout']}\nBranch: {result['branch']} @ {result['head']}")
        print("Changes: " + (result["status"] or "clean"))
        print("Selected task: " + (result["selected_task"] or "none"))
        for error in result["errors"]:
            print("ERROR: " + error)
        print(result["scope"])
    return 0 if result["ok"] else 1


def context(args):
    if args.max_chars < 1:
        raise ValueError("--max-chars must be positive")
    state = inspect(args.workspace)
    if not state["ok"]:
        raise ValueError("Workspace checks failed: " + "; ".join(state["errors"]))
    root = Path(state["workspace"])
    names = ["AGENTS.md", "AGENT.md", "WORKSPACE.md", "tasks.md", "decisions.md"]
    if state["selected_task"]:
        names.append(state["selected_task"])
    documents, remaining = [], args.max_chars
    for name in names:
        content = (root / name).read_text(encoding="utf-8")
        included = len(content) <= remaining
        documents.append({"path": name, "included": included,
                          "text": content if included else "Omitted for size; read this file explicitly before acting."})
        if included:
            remaining -= len(content)
    if args.json:
        print(json.dumps({"state": state, "documents": documents}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(state, ensure_ascii=False, indent=2))
        for document in documents:
            print(f"\n--- {document['path']} ---\n{document['text']}")
    return 0


def record(args):
    root, _, _, _ = load(args.workspace)
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", args.label):
        raise ValueError("Label must use lowercase words separated by hyphens")
    cwd = (root / args.cwd).resolve()
    if not cwd.is_relative_to(root):
        raise ValueError("Command directory must be within the workspace")
    if not args.command:
        raise ValueError("Supply a command after --")
    directory = root / "evidence" / args.label
    directory.mkdir(parents=True, exist_ok=True)
    started, timestamp = time.monotonic(), datetime.now(timezone.utc).isoformat()
    completed = subprocess.run(args.command, cwd=cwd, capture_output=True, text=True, errors="replace")
    receipt = {"started_at_utc": timestamp, "elapsed_seconds": time.monotonic() - started,
               "cwd": str(cwd.relative_to(root)), "argv": args.command,
               "exit_code": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}
    with (directory / "commands.jsonl").open("a", encoding="utf-8") as log:
        log.write(json.dumps(receipt, ensure_ascii=False) + "\n")
    print(completed.stdout, end="")
    print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    setup = sub.add_parser("init", help="Create a new workspace and isolated committed-base checkout")
    setup.add_argument("--repo", required=True)
    setup.add_argument("--workspace", required=True)
    setup.add_argument("--ref", default="HEAD", help="Local committed base, default HEAD; no network fetch")
    for name in ("doctor", "context", "record"):
        command = sub.add_parser(name)
        command.add_argument("--workspace", default=".")
        if name != "record":
            command.add_argument("--json", action="store_true")
        if name == "context":
            command.add_argument("--max-chars", type=int, default=12000)
        if name == "record":
            command.add_argument("--label", required=True)
            command.add_argument("--cwd", default=".")
    arguments = sys.argv[1:]
    command_args = []
    if arguments[:1] == ["record"] and "--" in arguments:
        boundary = arguments.index("--")
        command_args, arguments = arguments[boundary + 1:], arguments[:boundary]
    args = parser.parse_args(arguments)
    args.command = command_args
    try:
        return {"init": initialize, "doctor": doctor, "context": context, "record": record}[args.action](args)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        message = error.stderr.strip() if isinstance(error, subprocess.CalledProcessError) else str(error)
        print("ERROR: " + message, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
