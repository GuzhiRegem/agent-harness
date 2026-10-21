# Agent harness

A portable operating handoff for working with coding agents across repositories. Use it to establish project context, carry out authorized work in an isolated checkout, verify the result, and leave a session another person or agent can resume.

This is the complete manual operating guide. You can send it as one file. It describes a workflow and includes starter instructions and templates; it does not install an agent runtime, skills, connectors, or browser tools. Use your project's existing tooling and instructions where available. The project's optional `harness.py` CLI automates first-time setup and local context checks; this guide remains usable on its own.

## Start here

Give a new collaborator this file, the actual project location, and a task or a request for orientation. They should be able to identify the sources of authority, the authorized scope, the working checkout, and the next verifiable action.

For an existing project, begin with the [orientation prompt](#orientation-prompt). For a new coordination workspace, follow [first-time setup](#first-time-setup). At a session boundary, use the [handoff template](#handoff-template).

## Separate coordination from product code

The harness is the operating context around an agent: instructions, task state, evidence, tools, and a way to resume work. Keep those responsibilities distinct from the application being changed.

| Place | Contents |
| --- | --- |
| Coordination workspace | Local priorities, decisions, task records, evidence, handoffs, and optional orchestration tools |
| Product repository | Application code, shared project documentation, tests, dependency manifests, and build configuration |
| Task checkout | A dedicated branch and worktree, or an isolated clone, for one authorized change |

A coordination workspace can be a separate directory or an agreed location inside a repository. Follow the project's convention. Put shared deliverables in the product repository and keep private operational records in their agreed storage. Check Git tracking before saving private material inside a repository.

Use a dedicated task checkout for implementation. Preserve unrelated edits, existing task ownership, and the project's protected branches.

## Know what owns each fact

| Question | Authority |
| --- | --- |
| What is authorized now? | The user's instructions and applicable project rules |
| What are the working conventions? | The project's agent instructions, contribution guide, and scoped instructions in the selected checkout |
| What is the local work sequence? | The designated operating board or task record |
| What code is actually present? | The selected checkout's commit, index, working files, and untracked files |
| What is the current PR, review, merge, or CI state? | The live source host and CI system |
| What is the current issue status or assignment? | The live issue tracker |
| Who made a decision or commitment? | The actual conversation, attributed meeting record, or linked message |
| What is running or deployed? | The relevant runtime, service, or deployment system |
| What happened previously? | Dated evidence, receipts, progress logs, and handoffs |

Local records are saved evidence. Record the observation time and source when external state matters. A recent file edit does not make every statement in the file current. A green check, merged commit, or successful local experiment establishes only the scope it actually verifies.

When sources disagree, state the disagreement and its consequence. Updating a local board does not update the issue tracker. An old plan does not select today's implementation. An unavailable connector leaves a fact unverified.

## First-time setup

First inspect the project for existing instructions and coordination records. Reuse their names and responsibilities. If the user has requested a new workspace, the following layout is sufficient to start. Add records only when there is something to record.

```text
coordination/
  AGENTS.md                 # Entry instructions, if the agent supports this filename
  AGENT.md                  # Operating authority and durable constraints
  WORKSPACE.md              # Paths, source owners, and tool entry points
  tasks.md                  # Current sequencing and selected task links
  decisions.md              # Accepted decisions, dates, and source links
  tasks/
    task-name.md            # Scope, progress, verification, and resume point
  evidence/
    task-name/              # Commands, receipts, and shareable artifacts
  handoffs/                 # Transfer records when a task needs a separate handoff
  worktrees/                # Isolated product checkouts
```

`AGENTS.md` is an example entrypoint, not a universal discovery mechanism. Use the instruction mechanism supported by your agent. If discovery is unavailable, include the entry file's path in the startup prompt. Keep the operating rules in one place and point other entry files to it.

Record these project bindings in `WORKSPACE.md`:

- The coordination directory, product repository, and task checkout locations.
- The entry instructions, current task board, and accepted decision record.
- The source host, issue tracker, and runtime systems that own live facts, where used.
- Where to discover setup, validation, release, and recovery commands in the selected revision.
- Available skills, role launchers, browser tools, and their documented entrypoints, where installed.
- Shared resource ownership, capacity limits, and actions requiring separate approval.

Use each collaborator's own accounts and required permissions. A connector's presence does not establish its identity, repository access, or write authorization. Verify the relevant identity and access before relying on an assigned-to-me query or performing a write. Keep credentials and persistent browser profiles out of handoffs and version control.

### Starter entry instructions

Adapt this block to the actual workspace. Create the referenced files before using it as an entrypoint.

```markdown
# Workspace entry

Read AGENT.md first for operating authority, constraints, and source ownership.
Read WORKSPACE.md to locate the project and its tools, then tasks.md for the
selected work. Read the selected task's latest record before acting.

Treat local records as dated evidence. Verify current external state in the
system that owns it when the task depends on that state.

Orientation is read-only. Report context, conflicts, and missing evidence before
selecting implementation. When the user has already selected a task, continue
its authorized scope after orientation.

Use a dedicated task checkout and preserve existing edits and ownership. Record
verification and a concrete resume point in the selected task record. Follow
the user's existing authorization and the project's publication rules.
```

In `AGENT.md`, name the authoritative records and record enduring constraints, such as protected checkouts, private-data boundaries, and shared-service ownership. Put changing task status in the task record. This keeps the startup instructions useful without accumulating old project history.

## Orient before acting

1. Read the entry instructions and follow their authority and navigation pointers. Include scoped instructions in the task checkout. Finish when you can name the applicable rules and source owners.
2. Read the operating board and the selected task's latest scope, decisions, handoff, and holds. Finish when you can distinguish the user's request from historical suggestions and other people's assignments.
3. Inspect the relevant checkout's branch, commit, tracked edits, and untracked files. Inspect task ownership before reusing it. Finish when the starting state and existing work are accounted for.
4. Refresh external facts needed for this request, such as the selected issue, exact PR head, checks, or deployment revision. For local-only orientation, retain their saved dates and mark live state unverified. Finish when each decision-driving claim has current evidence or an explicit limit.
5. Report the goal, authorized scope, meaningful drift, dependencies, and next action. For an orientation-only request, stop here. For an already selected task, continue authorized work.

Orientation itself does not install packages, edit boards, start services, launch workers, or publish changes. An existing task instruction can authorize those actions after orientation.

### Orientation prompt

Replace the bracketed fields before sending. The prompt is intentionally limited to reading and reporting.

```text
Read the attached agent harness guide.

Coordination workspace: [actual location, or none yet]
Product repository: [actual location or repository URL]
Focus: [task, issue, handoff, or general orientation]
External reads: [relevant live systems, or local-only]

Read the project's entry instructions first, then its operating authority,
navigation, task records, and the relevant latest handoff. Distinguish saved
evidence from current external state. Inspect existing edits and ownership.

Report the relevant goal, scope, constraints, meaningful drift, evidence gaps,
and next concrete step. Keep this orientation read-only. Do not select or resume
implementation, install dependencies, launch services, or publish changes.
```

## Carry out a selected task

Before changing files, record the problem, expected behavior, deliverables, acceptance criteria, source of the request, and authorized actions. For a multi-part task, keep every requested outcome visible until it is completed, explicitly deferred by the user, or reported as unverified. Resolve routine choices within the authorized scope; ask only for missing information that affects the result.

Use an existing task checkout only after checking its state and ownership. Otherwise create a dedicated checkout from an explicitly selected base. Verify the live base when current upstream code matters; cached remote refs can be stale. Never infer that another agent is idle from an empty terminal or a clean branch.

For a Git project, these commands inspect a selected checkout. Set `REPO_PATH` to its actual location first.

```bash
REPO_PATH=/path/to/product-checkout
git -C "$REPO_PATH" status --short --branch
git -C "$REPO_PATH" rev-parse HEAD
git -C "$REPO_PATH" diff --stat
git -C "$REPO_PATH" worktree list
```

For a new Git worktree, replace all values below. `BASE_SHA` must be a verified existing commit, `TASK_BRANCH` a new task branch, and `TASK_PATH` an unused path outside the source checkout. Inspect the result before editing.

```bash
REPO_PATH=/path/to/product-checkout
TASK_PATH=/path/to/coordination/worktrees/task-name
TASK_BRANCH=task/describe-the-change
BASE_SHA=REPLACE_WITH_VERIFIED_COMMIT_SHA
git -C "$REPO_PATH" worktree add -b "$TASK_BRANCH" "$TASK_PATH" "$BASE_SHA"
git -C "$TASK_PATH" status --short --branch
git -C "$TASK_PATH" rev-parse HEAD
```

Use an isolated clone or the project's equivalent when worktrees are unsuitable. Read the selected revision's setup instructions and dependency locks before installing anything. Preserve its tool pins and package policies. Record required but unavailable tools as a verification limit.

Implement the complete requested behavior with the smallest justified change. Include affected callers, configuration, documentation, and meaningful tests. Preserve error handling and unrelated work. When requirements conflict, explain the conflict and continue independent work while the necessary decision is pending.

## Use tools and delegation deliberately

Discover available tools from the environment and project documentation. Read applicable skill instructions and required references when using a skill. A role or skill supplies job guidance; it does not grant permission, credentials, or capacity.

Use a project's role launcher when its instructions require one. This guide ships no launcher and assumes no particular agent CLI. Confirm the selected role, required skills, working directory, and scope from the installed tool's documentation before launch.

Delegate only when the user or applicable project instructions authorize it and shared capacity permits it. Give each worker a bounded task, exact checkout or source revision, allowed writes, required evidence, and completion criteria. Keep one owner for each mutable task checkout. The coordinating agent owns integration, conflicting findings, and final verification.

For shared services or persistent browsers, identify the actual owner and live process or job before taking action. Inspect active work and queues before an authorized restart. An observation timeout is not evidence a process stopped; recheck the same handle before replacing it. Use separate browser instances when concurrent tasks require isolation, and stop only resources owned by the task.

## Verify the behavior being claimed

Derive checks from the requirements and affected behavior. Run the project's required checks and the smallest additional experiments that resolve material uncertainty. Keep the command, working directory, revision, environment, result, and evidence location together. If files change after verification, identify which results still apply and rerun affected checks.

| Evidence | Supports |
| --- | --- |
| Source inspection | A claim about the inspected implementation at that revision |
| Local test or controlled probe | The behavior exercised with those inputs in that environment |
| Fresh browser observation | The visible result and state actually inspected |
| CI receipt | The checks that ran at the recorded commit |
| Deployment and runtime readback | The version, configuration, and behavior actually observed in that environment |

For a bug, reproduce the failure and a useful control where feasible. For performance, compare representative workloads before and after. For UI work, inspect fresh screenshots after actions and test persistence or recovery when relevant. An input-dispatch receipt alone does not prove the resulting state.

Report passing, failing, skipped, blocked, and unrun checks separately. Preserve exact failures and baseline controls where they affect the conclusion. Synthetic data and mocked services are useful experiments; label their scope. Source completion, test success, deployment, and user acceptance each need their own evidence.

Before claiming completion, check every deliverable and acceptance criterion against current evidence. Missing, indirect, or contradictory evidence leaves that item open. Report the remaining work instead of narrowing the goal to the checks that happened to pass.

## Review and publish within scope

For a code review, bind the review to an exact head and base. Understand the originating requirement and before/after behavior, account for every changed file, and read connected callers and contracts. Group the work by behavior when that makes coverage clearer. Use independent reviewers when the authorized workflow calls for them.

For each finding, provide the affected behavior, concrete trigger, supporting location, consequence, and a proportionate correction. Recheck findings for validity, scope, and fairness before presenting them. Keep detailed evidence behind a concise human-facing result. A changed head needs an assessment of the changed scope and fresh evidence; a merged-PR retrospective remains a dated review of that revision.

For pushes, PRs, reviews, tracker changes, deployments, or messages, match the exact action and destination to existing authorization. Complete the authorized preparation and checks first. If separate approval is required, show the literal outgoing content, target, revision, and effect so approval is the final step. Carry forward approval already given for that action; avoid requesting it twice.

After an external write, read back the resulting identifier, content, head or version, and state. Record the receipt. Creating a PR, passing CI, merging, and deploying are separate actions. A tool's availability or a successful request is not proof of authorization or final success.

## Leave a resumable session

Update the selected task record when task tracking is in scope. Keep accepted decisions and their reasons in the designated decision record; keep chronological events in evidence or a progress log. Link to existing facts rather than copying changing status into several files. Mark superseded records with the replacement pointer and preserve useful historical evidence.

A handoff should let the next collaborator take one concrete action without reconstructing the conversation. Separate completed work, pending decisions, and actions awaiting authorization. Include source links and observation dates for external claims. For a shareable handoff, remove personal assignments, machine-specific paths, connected identities, credentials, private logs, and browser state unless the recipient explicitly needs an approved subset. Use project-relative paths where possible.

### Handoff template

Keep the fields that apply and write `none` or `unverified` explicitly where that distinction matters.

```markdown
# Task handoff

Updated at: [timestamp and timezone]
Goal and source request: [requested outcome and authoritative reference]
Scope and authorization: [allowed work, boundaries, approval already given]
Acceptance criteria: [each required outcome and its evidence or open status]

## Current state

- Result: [what is complete and what remains]
- Checkout and branch: [location relative to workspace, branch]
- Base and current commit: [exact revisions]
- Working changes: [tracked edits, untracked files, or verified clean]
- Decisions: [accepted choices, reasons, and source links]
- Live systems checked: [system, observation time, result, receipt]
- Active resources: [owner, actual process/session/job handle, last live check]

## Verification

- Commands and environment: [working directory, revision, relevant configuration]
- Results: [passed, failed, skipped, blocked, and unrun checks]
- Evidence: [artifact paths and receipts]
- Limits: [what the evidence does not establish]

## Resume

- Next concrete step: [action, location, and expected result]
- Dependencies or decisions: [what is needed and from whom, if applicable]
- Separate authorization required: [exact action and prepared preview, or none]
- Recovery or cleanup: [owned resources, preserved work, restoration instructions]
```

### Resume prompt

```text
Read the agent harness guide and the selected task handoff at [actual path].
The requested outcome is [full goal]. Continue the authorized scope recorded
there, incorporating this message's direction.

Verify the checkout, existing changes, task ownership, and decision-driving
external facts before relying on saved state. Preserve completed work and
unrelated edits. Recheck claimed live resources by their actual handles before
waiting on or replacing them.

Complete the remaining authorized work, verify every acceptance criterion,
and update the task record with evidence and an exact resume or completion
point. Carry forward existing approval and preserve any separate publication,
merge, deployment, or shared-service boundaries.
```

The workflow is ready for use when a new collaborator can identify the authorized task, find the real source of each needed fact, verify the checkout, and take the next step using the handoff alone.
