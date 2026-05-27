# AGENTS.md

This file defines repo-local workflow rules for whoever executes work on this repository.

The default operating model for new ASK projects is single-node: Claude Code is both control surface and executor. An advisor in chat-based form — typically GPT or Claude — remains available outside the execution thread.

(An earlier split-execution model — ChatGPT as prompt compiler, Codex as executor, Claude Code as optional advisor — is referred to historically as **Model A** and is retained as legacy across the family. New projects should default to single-node unless there is a specific reason otherwise.)

The rules below are agent-agnostic — they apply to whoever is executing.

For repo-external context (project intent, audience, philosophy, foundational premises, durable loose threads), read the grounding note maintained outside this repository.

For project state (artifacts, decisions, current navigation), read the repo itself.

This file owns workflow rules. It does not track project state, current direction, or recommended next paths.

---

## Source-of-Truth Boundaries

- **Repo** = project truth: artifacts, decisions, findings, architecture docs, navigation.
- **`AGENTS.md`** (this file) = workflow rules for repo execution.
- **Grounding note** (external) = repo-external context: intent, audience, philosophy, foundational premises, durable loose threads.
- **Per-conversation memory** (operator-side: Claude Code's MEMORY.md, ChatGPT thread history, task lists) = ephemeral session state that does NOT belong in the grounding note.
- `[project-specific live truth surfaces, e.g. public datasets, document sources, schema registries]`

### Aging-Rate Principle

The split is separation by *aging rate*. A doc that tracks state ages fast; a doc that points to state ages slowly. If a statement would become stale when a PR lands, a chain closes, or a next path changes, it does not belong in this file or in the grounding note.

---

## Required Reading Before Meaningful Work

Before any meaningful repo work, read:

- `README.md`
- `AGENTS.md` (this file)
- `docs/architecture.md`
- `[repo-specific entry-point doc]`

Then read the latest milestone or finding artifact relevant to the task.

For external context, read the grounding note.

---

## Inbound Handoff TBI Marker

When an inbound handoff memo in `urban-observatory-EXTERNAL/sources of intent/` carries the `-TBI.md` suffix, treat the suffix as ASK ingestion-state only: to be ingested, not to be absorbed. When ASK feeds that memo into the active surface, the first action is to rename the file in place to remove `-TBI`; do not edit the memo body. Then classify the memo and record any absorption / hold / rejection in a separate scratch derivative. Copy + suffix do not authorize implementation.

Domain-authority-originated handoff memos may also carry `-TBI` while in transit when the originating review surface has read-only access to UO external files. ASK routes those memos into UO `sources of intent/` with the suffix intact; UO removes the suffix on ingestion.

Method-altitude articulation: `method-ASK/docs/source-of-intent.md` §Inbound handoff TBI marker.

---

## Repo Workflow Discipline

### Session-Start Discipline

Before any new repo work in a session:

1. Confirm the working directory is the session-owned worktree or approved repo root for this session. Cross-worktree absolute paths are a known failure surface; verify before any edit, write, or cross-root `git -C` command.
2. Verify `HEAD` is attached to a named branch. Detached `HEAD` is a stop condition.
3. Verify the working tree is clean.
4. If the working tree is not clean, stop. Identify whether the changes belong to the current thread before touching anything. Inheriting another thread's uncommitted state is a stop condition until provenance is established.

This does not replace Branch Freshness or Default Verification. It is the session-entry gate before meaningful repo work begins.

### Branch Freshness

For repo implementation work, follow this sequence:

1. verify local repo attachment
2. verify clean working tree
3. `git fetch origin --prune`
4. `git checkout main`
5. `git pull --ff-only origin main`
6. create task branch from refreshed `main`
7. stop if any verification fails

### Default Verification

Before meaningful work, verify:

```text
pwd
git rev-parse --show-toplevel
git remote get-url origin
git branch --show-current
git status --short
```

Stop if repo root, remote, branch, or working tree does not match the task requirements.

### Terminal-State Discipline

Use explicit terminal states:

```text
exact scoped diff ready for approval
committed locally only
pushed branch only
PR created
merged
merged branches cleaned up
```

### Exact Scoped Diff Gate

Stop at exact scoped diff unless ASK has already approved commit / push / PR. Once approved in the executor session, the executor may complete the remaining git workflow without separate manual GitHub UI ceremony.

### Structured Change Summary

Meaningful changes require:

- why this change exists
- what changed
- what did not change
- what remains out of scope

If a PR is used, this belongs in the PR description. If no PR is used, the same summary belongs in the executor handoff or approval record.

### Default: Hold or Carry Through Per Adversarial-Collaboration Preconditions

When ASK has approved the scoped diff, the workflow continues through commit and push to PR creation.

If the project meets the preconditions for adversarial collaboration (per [*Adversarial Collaboration*](https://atomicspacekitten.substack.com/p/adversarial-collaboration)) — hardened backbone, active architectural uncertainty, configured advisor surface — hold at `PR created` until the advisor relay returns approval, then continue to merge. The pushed-not-merged PR is the advisor's structural review window.

ASK forwarding an advisor approval to the executor is the relay. Forwarding may be done by pasting the advisor's approval, summary, or equivalent review result. No additional approval phrase is required after the forwarding act.

Forwarding advisor notes that contain required fixes, blocking concerns, or open questions is not approval relay; it is fix-direction or question-forwarding.

If no advisor surface is configured, carry through to merged + cleanup once diff approval is given. The pattern is proportional to architectural uncertainty live at any moment.

### PR Creation

When creating a PR, report: branch name, commit SHA, PR number, PR URL, actual base branch, actual head branch, validation performed, terminal state.

### Direct Push to Main

Branch plus PR is the default for meaningful structure or rule changes. Narrow low-risk edits or explicitly scoped bootstrap tasks may allow direct push to `main` when scope is made explicit and approved.

---

## Session Topology / Single-Writer Discipline

Multiple operator sessions can mutate the same repo files concurrently. Rules:

- One writer at a time per branch.
- Treat repo and remote as the audit trail when sessions disagree.
- Stop on suspected concurrent mutation. Re-orient against the repo before continuing.

---

## Scope Discipline

For implementation, prefer the smallest honest unit. For conceptual architecture, prefer the largest tractable structural question. Do not let "smallest unit" prevent zooming out to architecture scale.

Do not bundle unrelated work. Do not widen scope mid-task unless explicitly chosen. Do not create artifacts merely because a process pattern exists.

---

## Plan-Before-Execute Rule

Before executing a meaningful repo change, state: files in scope, scope in vs out, non-actions, expected terminal state.

The plan-before-execute step preserves the explicit reasoning surface that prompt-compilation provides when execution is split across a prompt-compiler and an executor. In a single-node model, plan-before-execute is the rule that restores it.

---

## Comments, Docs, and PR Roles

- Comments belong in implementation artifacts only when local clarity needs them.
- Docs hold durable repo-local truth, boundary definitions, and architecture framing.
- PRs hold change-specific explanation, reviewer guidance, tradeoffs.

---

## Project-Specific Defaults

Fill in local expectations here:

- `[testing or verification commands]`
- `[protected paths or high-risk areas]`
- `[external systems with their own mutation discipline, e.g. a live database, a CMS, a workflow tool]`
- `[terminology to preserve]`
- `[domain-specific creative or governance acts that should be modeled as first-class — see Architecture-Specific Rules below]`

---

## Architecture-Specific Rules (optional, project-by-project)

If the project's information architecture has a load-bearing creative or governance act (e.g. curation, capture, ratification, selection), model it as first-class in the schema and in the rules. Generic process rules cannot stand in for domain-specific structural decisions.

If the project has a prototype surface, decide whether the prototype is a pressure surface for studying the architecture or a deliverable in its own right. Document the answer.

If the project has external systems (databases, CMSs, workflow tools), decide how mutations to those systems are governed (Plan-Before-Execute applies; Structured Change Summary applies; per-action authorization may or may not be required depending on reversibility).

---

## Refresh Cadences

### Grounding Note

Refresh the grounding note only when external handoff context changes:

- new strategic direction
- philosophical reframing
- audience or positioning shift
- foundational premises change
- operating model changes

Do not refresh for routine repo chronology. Possible future directions belong in the grounding note only as durable loose threads, not as recommended next paths.

### `AGENTS.md`

Refresh this file only when a workflow rule is added, removed, or materially revised.

Do not refresh because project state changed. Do not refresh because a PR landed. Do not refresh because the next direction changed.

---

## Short Version

- Verify repo state before meaningful work.
- Read repo-local truth and grounding note before responding.
- Stop at exact scoped diff before commit; carry through to merged + cleanup once approved.
- State the plan before executing.
- Single-writer per branch. Repo is the audit trail.
- Match unit of work to level of question.
- Keep this file workflow-only. Repo holds state. Grounding note holds external context.
