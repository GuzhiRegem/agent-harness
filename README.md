# Agent harness

A small local workspace around your coding agent: operating rules, one selected
task, an isolated checkout, evidence and a way to resume from files.

Requires **Python 3.10+ and Git**. No pip install, service, account connection or
agent runtime is installed. Use your existing agent. Keep the coordination
workspace outside the product repository.

## Create a workspace

From a checkout of this project that contains `harness.py`, run:

```bash
python3 harness.py init --repo /path/to/your-product --workspace /path/to/your-product-agent
cd /path/to/your-product-agent
python3 tools/harness.py doctor
python3 tools/harness.py context
```

Replace the two paths; quote paths containing spaces. `init` creates a **new**
directory and refuses an existing destination. It reads the reference repository
and creates an independent clone on a task branch in `worktrees/development`.
The base is the reference's committed `HEAD`; uncommitted source edits stay in
the reference. Use `--ref LOCAL_REF` to choose another locally available commit.
There is no network fetch or claim that local refs are current upstream.

If testing an unmerged change, check out its branch before running these commands.
Reading a proposal or PR does not make this version available on the default branch.

```text
your-product-agent/
  AGENTS.md, AGENT.md        entry and durable rules
  WORKSPACE.md              file map
  harness.json              paths and selected committed base
  tasks.md                  one selected task; completed work below
  decisions.md              accepted decisions
  templates/                task and handoff starters
  tasks/, handoffs/          scope, progress, transfer and closure
  evidence/                 dated receipts; excluded from default context
  tools/harness.py           self-contained installed tool
  worktrees/development/    independent product checkout
```

The installed workspace works without this tool's original checkout. Its bindings
are relative: moving the product and workspace together preserves them. `init`
does not add files to the reference repository, change protected branches or
modify global agent configuration. Each task still needs its own scope, ownership
and checkout inspection. Choose a fresh task branch when beginning a new change.

## Start an agent and select work

Give the agent this prompt with the real workspace path:

> Workspace: /path/to/your-product-agent. Start at AGENTS.md. Orient read-only
> with `python3 tools/harness.py context`. Report the selected task, checkout,
> existing edits, evidence limits and next action. Read any omitted rules and
> applicable instructions in the task checkout before acting.

For authorized implementation, copy `templates/task.md` to `tasks/your-task.md`,
record the full request and acceptance, and change the single selection line in
`tasks.md` to `Selected task: [your-task](tasks/your-task.md)`. The agent can do
this as part of a task the user has already selected. At closure, return selection
to `none` and retain a completed-work link. A historical next step never selects work.

`context` returns only current rules, bindings, board, decisions and selected task.
It does not dump old tasks, handoffs, evidence or full source files. Content beyond
the default 12,000-character document budget is explicitly omitted with a read
instruction; use `--max-chars` to adjust it. Read the selected task's evidence and
handoff when needed. This limit is not a model-token budget.

## Verify and record

`doctor` checks required files, current Markdown paths and Git isolation/branch state.
It follows the selected task's adopted handoff; unselected task/handoff history
does not block current work.
It ignores inline/fenced code examples. It is a lightweight path checker, not a
Markdown renderer or proof of task acceptance, security, CI, publication or deployment.
Dirty task checkouts are reported so work can be preserved; they are not rejected.
`doctor --json` and `context --json` provide structured output. Exit codes are
0 for success, 1 for doctor findings and 2 for invalid setup or arguments.

For runs that need command-level evidence, provide this recording syntax in the
launch prompt **before the first shell read**:

```bash
python3 tools/harness.py record --label smoke-a --cwd . -- python3 tools/harness.py context
python3 tools/harness.py record --label smoke-a --cwd worktrees/development -- git status --short --branch
```

Receipts go to `evidence/smoke-a/commands.jsonl` and preserve argv, cwd, elapsed
subprocess time, exit code, stdout and stderr. Labels must be lowercase words
separated by hyphens. Exit codes propagate. Recording does not launch an agent,
measure its tokens or model latency, or sandbox the command; the agent environment
owns permissions. Record only commands/output appropriate for those local files.

## Learn and test

- [Complete portable operating guide](docs/guide.md): authority, implementation,
  review, verification, publication boundaries and session handoffs.
- [Smoke protocol](docs/smoke.md): baseline failure, preserved owner work and
  transfer between fresh agent sessions, with clear evidence limits.
- Contributor checks: `python3 -m unittest discover -s tests -v` and
  `git diff --check`.

To remove an unused generated workspace, first preserve its task changes,
untracked files and evidence. There is no global installation to undo; the
reference repository remains separate. Re-running `init` is not an update command.
