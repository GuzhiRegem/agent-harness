# Smoke: preserve owner work across a fresh agent handoff

This case tests whether agents use entry instructions, select the correct task
checkout, preserve existing work and continue from files. Use a disposable
fixture repository and an external coordination workspace. No external write,
service, credential, package installation or production data is needed.

## Scripted installation and handoff control

From this project's checkout:

```bash
python3 -m unittest discover -s tests -v
```

The suite executes installation, path/byte preservation, configuration errors,
code-example link checking, read-only context, command recording and a scripted
baseline-to-handoff-to-verification loop. These are programmatic controls, not
evidence of agent intelligence, session independence, latency or token savings.

## Actual agent run

Prepare a disposable Git repository with these committed files:

- `handoff.md` contains `[evidence](evidence/old.txt)`.
- `evidence/local.txt` exists; `evidence/old.txt` does not.

Create its workspace with the documented `init` command. In the **task checkout**,
append an owner note to `handoff.md` and leave an unrelated untracked owner draft.
Record initial bytes/hashes, HEAD, refs and source state outside agent write scope.
Create a selected task from the installed template that requires:

1. Read entry/current context and scoped product instructions, inspect Git and
   existing ownership before edits. Use a local check to demonstrate the broken link.
2. Repair only the evidence target in `handoff.md`. Preserve every other document
   byte, the owner draft, checker, evidence files, HEAD, refs and reference repository.
3. Agent A stops before final verification, updates the task and writes a concise
   handoff with checkout, exact next command, pending acceptance, evidence and release.
4. Agent B starts as a new session using only entry/task/handoff pointers. It
   inspects and verifies the change, records evidence and closes/releases ownership.

Give A and B the installed recording syntax before their first read, with distinct
labels such as `smoke-a` and `smoke-b`. The agent chooses its commands. For example,
its first context command can be:

```bash
python3 tools/harness.py record --label smoke-a -- python3 tools/harness.py context
```

Do not pass the correct replacement or A's transcript/conversation in B's dispatch.
Pass the handoff path. Snapshot A's handoff and pending state before launching B.
The launcher owns actual session IDs, fresh-session behavior and terminal status;
do not invent IDs or infer a finished agent from a timeout or empty terminal.

## Independent acceptance and performance

Inspect actual command, cwd, exit code and result for baseline/final checks.
Displayed source text containing a success marker is not an executed check.
Compare target **bytes**, not normalized text, against the one permitted replacement.
Check owner/protected-file hashes and Git state independently. Review the task and
handoff for truthful pending/completed acceptance and released ownership.

Test the evaluator too: restoring the broken link must fail; LF-to-CRLF changes
must fail preservation even if link checks pass; source text containing `OK`
without the real final check must not count as verification. Restore control
changes and keep their evidence separate from agent execution.

Report observed session times, time to first recorded command and recorded command
counts, with launch/observation timestamps and session IDs. Recorder subprocess
time is not model time. Large stdout is not a token count. Report unavailable
token/cost metrics as unavailable. Keep setup, pilots and coordinator work separate.
Do not infer a speedup without a controlled comparison and representative tasks.

Current release checks establish the scripted workflow and clean installation.
An actual fresh-agent run needs its own dated receipts; the tool does not launch
models or certify that a set of saved commands came from independent agents.
