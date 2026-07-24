# AGENTS.md — urban-observatory

This repo's `AGENTS.md` is a **resolved carrier**: the shared execution protocol (below, resolved from `control-surface/protocol/AGENTS.shared.md`) + the standing upstream-conformance grant + the urban-observatory-local delta. It installs no profile. The shared block and grant are machine-maintained — do not hand-edit between the markers.

<!-- BEGIN carrier-metadata -->
CARRIER_TYPE: resolved-local
SHARED_BLOCK_SOURCE: apexSolarKiss/control-surface/protocol/AGENTS.shared.md
SHARED_BLOCK_PIN: c94f252edf6a94845a11558de4959d1faddedb5b
PROFILES: []
GRANT_FRAGMENT: standing-upstream-conformance-grant@c94f252edf6a94845a11558de4959d1faddedb5b
OPERATING_SURFACE: separately-operated
<!-- END carrier-metadata -->

<!-- BEGIN shared: AGENTS.shared.md -->
<!-- protocol/AGENTS.shared.md — distributable shared execution-protocol body (fixed, byte-identical text only). Owner explanation + authoring contract: apexSolarKiss/control-surface/protocol/README.md. This body is inserted verbatim between the BEGIN/END shared markers in each resolved AGENTS.md (the owner root and every consumer); it carries no owner-canonical H1, no project parameters, no coordinator orchestration, no consumer grant, and no repo-local delta. The rules are agent-agnostic — they apply to whoever is executing. -->

## Source-of-Truth Boundaries
<!-- rule-id: source-of-truth-boundaries -->

- **Repo** = project truth: artifacts, decisions, docs, templates, examples.
- **`AGENTS.md`** = workflow rules for repo execution, resolved as: this shared core + applicable profiles + opt-in fragments + repo-local delta.
- **Grounding note** (external) = repo-external context: intent, audience, philosophy, foundational premises, durable loose threads.
- **Per-conversation / task state** (ChatGPT thread history, task lists, in-flight session context) = ephemeral; does NOT belong in the grounding note.
- **Private agent memory** (e.g. Claude Code's MEMORY.md) = non-authoritative operator context. It MAY retain ASK-authorized incidents, anti-re-derivation pointers, worked examples, refusal/supersession records, tool/vendor occupancy, and other operator context **within that memory's authorized owning surface** — but it NEVER owns durable project truth or workflow protocol (see §Verification Claims). Wall-bound material remains on the owning side of the wall; this rule creates no cross-wall read, copy, or retention authority. Retention conditions and the authorization required for any memory write are governed by §Learning Disposition and §Private-Memory Write Gate.

### Aging-Rate Principle
<!-- rule-id: aging-rate-principle -->

The split between repo, `AGENTS.md`, grounding note, ephemeral per-conversation / task state, and non-authoritative private agent memory is separation by *aging rate*.

- A doc that *tracks state* ages fast and must be refreshed often.
- A doc that *points to state* ages slowly and stays useful across many sessions.
- A rules doc that contains rules only ages slowly.
- A context doc that contains context only ages slowly.
- A doc that mixes rules, context, and state ages at the rate of its fastest-aging contents — usually badly.

If a statement would become stale when a PR lands, a chain closes, or a next path changes, it does not belong in this file or in the grounding note.

---

## Learning Disposition
<!-- rule-id: learning-disposition -->

When a reusable learning appears — a correction, a discovered constraint, a convention, a calibration, a failure and its remedy — classify it **before** deciding where it is retained. Classify per claim limb: one observation often carries a shared rule, a local exception, current state, and historical provenance at once, and those limbs do not share a destination.

Route each limb to its visible durable owner:

- **shared workflow rule** → the owner canonical at `apexSolarKiss/control-surface/protocol/`; classify it as shared core, an applicable profile, an opt-in fragment, or an explicit hold before changing any resolved consumer
- **project-local workflow rule or exception** → the owning repo's `AGENTS.md` local delta
- **project truth, guidance, architecture, implementation contract, or maintained procedure** → the owning repo's code, tests, or docs
- **cross-surface maintenance state, pins, obligations, propagation, or currency** → the applicable operator ledger; ordinary project state remains with the owning repo
- **event, experiment, failure, review disposition, or closure evidence** → the owning surface's scratch, a PR record, or a named closure artifact
- **slow external intent, audience, or durable external constraint** → the owning grounding note
- **temporary task state** → current task state only, then no retention
- **an unearned generalization** → an explicit nomination or hold
- **material that earns no durable retention** → no retention

Private agent memory is not a durable owner, protocol-candidate inbox, state ledger, or pre-absorption staging surface. It becomes a candidate only after the visible-owner test establishes either:

1. a durable owner has intentionally omitted the non-operative residue; or
2. no visible owner is appropriate because the payload is machine-local, wall-bound, or deliberately non-operative.

The absence of a visible owner never authorizes memory to carry knowledge required for correctness.

Subject to §Private-Memory Write Gate, private memory may retain narrowly scoped origin or incident history, refusal or supersession evidence, worked examples, evidence of a local exception whose operative rule or constraint is visibly owned, machine-local calibration, machine-local or deliberately non-operative tool/vendor occupancy whose structural role and durable procedure are visibly owned, anti-re-derivation pointers, and wall-bound residue within the memory's authorized owning surface.

Removing private memory may make an executor slower. It must never make an executor wrong. If a decision cannot be made correctly without a memory entry, that entry carries operative knowledge and is in the wrong place.

A generic request to "remember this" requests durable retention, not a predetermined storage surface. Classify and propose the appropriate owner. Only a request that explicitly names private agent memory, followed by ASK's approval of the exact target and payload, authorizes that destination.

---

## Private-Memory Write Gate
<!-- rule-id: private-memory-write-gate -->

**Default deny.** A private-memory mutation is a separate approval unit. It may occur inside an explicitly scoped memory-maintenance operation, but it is never incidental to another task, inferred from another approval, or added during task closure.

For this rule, a **private persistent mutation** means creating, editing, or deleting any governed auto-memory, subagent-memory, user-instruction, user-rule, or gitignored local-instruction artifact. References below to a private-memory mutation use that broader meaning.

This gate governs **private persistent agent surfaces**: auto-memory stores and their indexes, subagent memory, and private instruction files that load across sessions without repo review — user-scope instructions and rules, and gitignored local instruction files. A checked-in repo adapter is not one of these: it is a visible carrier under ordinary diff and review gates.

A private persistent instruction imported from any other path is governed by this gate as well. It must not be used unless its exact path is declared, a matching `Edit(...)` ask rule is installed, and the active-session receipt classifies it as covered. A private import outside the standard guarded paths is a stop condition.

Any governed private persistent creation or edit requires all of:

1. the learning has been classified under §Learning Disposition and its visible owner has been named;
2. a stated reason the visible owner is insufficient for the residual payload;
3. the exact target and exact proposed mutation, shown before execution: full payload for creation; exact diff or replacement payload for an edit;
4. explicit ASK authorization of that exact target and exact mutation;
5. a recorded aging or review trigger.

Any governed private persistent deletion requires all of:

1. the artifact's current role and disposition have been classified, including its visible owner or a no-retention result;
2. a stated reason deletion is warranted — for example unauthorized creation, supersession, owner absorption, or expiry of its review trigger;
3. the exact path plus a pre-deletion size/hash receipt and, when restoring a prior state, the exact baseline bytes or diff;
4. explicit ASK authorization of that exact deletion;
5. a post-operation absence receipt, or exact restored-byte/hash verification when deletion is one step in a rollback.

Approval of a plan, a diff, a PR, a merge, or a task completion is **not** authorization of that private persistent mutation. Neither is advisor agreement.

**Authorization is per artifact.** Approval of a topic file does not authorize an index entry, and approval of an index entry does not authorize the topic file. Every created, modified, or deleted artifact requires its own displayed change or deletion receipt and its own ASK decision. Never select a session-wide or standing approval for a governed private persistent path, including "allow Claude to edit its own settings for this session."

**Live credentials, authorization tokens, private keys, and other secrets are never admissible payloads** for a private persistent surface or for any disposition record.

Specifically prohibited without the authorization above:

- banking "one durable note" at task close;
- using memory as a protocol-candidate inbox;
- post-merge memory mutation framed as cleanup;
- automatic index (`MEMORY.md`) updates.

Do not bypass the gate through Bash, Python, Node, another subprocess, a helper agent, or an alternate write tool. Subagents, census agents, staging agents, and read-only workers never perform private persistent mutations; they return the candidate learning and proposed disposition to the parent coordinator.

Before memory-bearing work, confirm that the required ask rules are active and that every governed private persistent path — including the effective auto-memory root and every loaded private instruction import — is covered. Missing rules, unmatched rules, or an uncovered governed path are stop conditions.

Do not perform private persistent-context maintenance in a mode that disables the runtime's safety checks. This is defense in depth: explicit ask rules currently still apply in that mode, but the gate must not depend on one product carve-out while other checks are disabled.

Where the runtime enforces this gate with a permission prompt, treat the prompt as the technical gate only. The visible disposition above is the semantic gate, and a runtime status message is not evidence that a write did or did not persist — verify the filesystem.

---

## Required Reading Before Meaningful Work
<!-- rule-id: required-reading -->

Before any meaningful repo work, read:

- this repository's `README.md`;
- this `AGENTS.md` — the shared execution-protocol core and this repo's own Required Reads named in its local delta;
- the repo-local Required Reads and architecture docs that delta names.

For external context, read the grounding note. Then read whatever templates, prompts, examples, milestones, or findings are relevant to the task.

---

## Inbound Handoff TBI Marker
<!-- rule-id: inbound-tbi-marker -->

When a routed handoff memo in a shared intake carries the `-TBI.md` suffix, treat the suffix as ASK ingestion-state only: a received handoff awaiting ingestion, not a statement about absorption. When ASK feeds that memo into the active surface, the first recipient-side action is to rename the file in place to remove `-TBI`; do not edit the memo body. Then classify the memo. When classification produces a durable action, hold, rejection, or route, record the required closure in scratch. Copy + suffix do not authorize implementation.

`-TBI` marks material that ASK has saved but has not yet fed into the operating surface responsible for ingesting it. It is an unconsumed ingestion-queue marker — not a repo-ownership marker and not a pending-action marker. That is why the suffix is struck **on ingestion** rather than at absorption: the item leaves the queue when it is fed in.

**Do not create a `-TBI` addressed to a surface the acting surface already operates.** Moving between repos inside one operating surface is a hard repo-boundary reset — read that repo's grounding note and `AGENTS.md`, verify live state, work under its own branch, diff, review, and merge gates — not an ingestion event. A handoff addressed back to the surface that authored it tracks nothing: the destination operating surface already has the material, so no ingestion boundary was crossed.

Separate repo authority is real and unaffected by this rule. **It does not create a separate ingestion boundary.** Pending owner classification or repo action is repo state — carried by the closure, the relay, or task state — not `-TBI` state.

Method-altitude articulation: `method-ASK/docs/source-of-intent.md` §Inbound handoff TBI marker.

---

## Provenance Transcript PTX Marker
<!-- rule-id: ptx-marker -->

A filename ending in `-PTX.md` or `-PTX_vN.md` identifies an ASK-assembled **Provenance Transcript**: a record of a source conversation or cross-surface exchange, retained for lineage and later verification.

The `-PTX` segment is the artifact-role marker. An optional `_vN` suffix records the version of the transcript artifact itself. It does not make the artifact a model draft or draft-zero, and it confers no lifecycle state or authority.

A `-PTX` artifact is not a canonical, a model draft or model draft-zero, a versioned canonical snapshot, a handoff, an approval or execution instruction, or an ingestion-state marker.

- `-PTX.md` is an unversioned singleton transcript.
- `-PTX_vN.md` is a numbered member of an explicit transcript version lineage. `_v0` means the first numbered PTX version, not draft-zero.
- Infer version precedence only from an explicit `_vN`, never from the `-PTX` marker itself.
- Neither `-PTX` nor `_vN` establishes whether the transcript is still being assembled, complete, closed, or frozen. PTX lifecycle and version progression are ASK-owned; do not edit, extend, rename, close, freeze, or advance a PTX unless ASK explicitly directs the exact operation.
- The PTX files are themselves the lineage; do not create a separate canonical-plus-snapshot chain for them.
- Do not absorb a PTX as project truth without classification.
- If the transcript creates work for another surface, route a separate handoff rather than stacking `-PTX` with `-TBI`.
- The convention is prospective. Historical transcripts are not renamed for conformance, so the absence of `-PTX` does not establish that a file is a model draft — classify an unmarked artifact from the file and its scratch context before versioning or superseding it.

Forms:

```text
YYYY-MM-DD_<surface-or-subject>_<topic>-PTX.md
YYYY-MM-DD_<surface-or-subject>_<topic>-PTX_vN.md
```

`-TBI`, `-PTX`, and `_vN` do not share an axis: `-TBI` is a lifecycle state, renamed off on ingestion; `-PTX` is an artifact role, and the role marker is retained throughout any version lineage; `_vN` is an optional version index for the transcript artifact. Neither `-PTX` nor `_vN` confers state, authority, or canonical status.

---

## Cross-Surface Change Routing
<!-- rule-id: cross-surface-change-routing -->

Before choosing direct operation or `-TBI` routing, first establish whether the material crosses an operating-surface boundary at all. Only then classify the change's authority and the surface's write jurisdiction.

- **Destination inside the same operating surface** → **no `-TBI`, under any authority class.** Change repo context through a hard repo-boundary reset and operate the owning repo directly under its own gates. Answer this test first; a `yes` disposes of the routing question on its own, and the authority and jurisdiction tests below never run.
- **Candidate source-of-intent, project-specific direction, or other material whose recipient must classify** → preserve the origin record, route a recipient copy through `sources of intent/` with `-TBI`, and let the recipient surface own ingestion and absorption. This branch presumes the recipient is a *different* operating surface; recipient-owned classification inside one surface is a hat swap, not a handoff.
- **ASK-authorized conformance to a protocol owned upstream** → propagate directly only where the active surface has write jurisdiction over the consumer. Apply the change through the consumer repo's own branch, diff, PR, review, and merge gates. Do not create a `-TBI` handoff merely to carry an already-authoritative protocol update.
- **No direct write jurisdiction** → route to the owning surface even when the upstream protocol is authoritative. Protocol ownership does not pierce a wall, create a grant, or bypass a surface boundary.

Write jurisdiction may be standing or explicitly granted by ASK for the scoped conformance change. Neither protocol ownership, connector capability, nor this rule itself creates write jurisdiction over another surface.

Direct propagation authorizes only the scoped conformance change. It does not authorize unrelated changes to the consumer's project truth, architecture, source of intent, or implementation.

**Conformance targets canonical state, not literal carrier strings.** Name the owner canonical by path — and SHA where available — as the authority. Quoted recipient text is a search anchor or illustration, not an exhaustive change target unless that carrier has been verified byte-identical to the owner. The acting or recipient surface reads its live carrier, corrects every materially equivalent occurrence within the explicitly named clause or section, and re-syncs that bounded scope to canonical substance without widening beyond the authorized rule. When the originating surface cannot inspect the recipient carrier — across a wall, for example — the handoff leads with the canonical re-sync instruction and marks any quoted find-and-replace text explicitly non-exhaustive.

Method-altitude articulation: `method-ASK/docs/source-of-intent.md` §Scope guard: handoff routing vs protocol conformance.

---

## Verification Claims and Evidence Boundaries
<!-- rule-id: verification-claims-evidence-boundaries -->

A verification statement is bounded by the evidence actually gathered.

- For claims such as `clean`, `complete`, `current`, `zero residue`, `byte-identical`, or `verified`, name the exact carrier set, path or query, ref or time boundary, and property actually tested.
- **Verify the measurement target at the point of execution.** A passing, failing, or zero-result check is not evidence until the command's repository or worktree, carrier or path set, ref or time boundary, and query or predicate are explicit and independently confirmed. Do not rely on inherited `cwd`, a preceding `cd` in a compound command, or an earlier attachment check in cross-repo or multi-root work. When the claim concerns change across a mutation, capture the baseline before editing; a clean post-edit result cannot establish the pre-edit state.
- **Verify execution completion and result semantics.** Confirm that a verification check actually executed before interpreting its output. Distinguish a valid no-match from an execution error; preserve the raw completion status before any pipe or transformation; quote or otherwise validate paths, globs, and input expansion. State whether a count measures files, matched lines, occurrences, records, or claim units. **Empty output from a failed or unrun check is no evidence.**
<!-- rule-id: verification-execution-completion -->
- **The boundary of a search is the boundary of the claim.** Absence from one folder, one pattern, one connector result, or one carrier class is not absence from the corpus.
- **A check verifies only its direct result.** Separate observation from inference; do not attach an inference to a checked fact and label the composite `verified`.
- Pattern lists are hypotheses about how a defect may appear, not exhaustive evidence. An exhaustive claim requires enumerating and dispositioning the actual occurrence or carrier set.
- Where coverage is partial, state the result as: `no unexplained findings in <exact set tested>`.
- If a **completed audit, closure, provenance record, or other frozen record** overstates its evidence, preserve the original statement and append a correction. Do not silently tidy the audit trail.
- If a **live canonical or current instruction** overstates its evidence, correct the operative statement under that carrier's version and snapshot discipline, preserving the prior state in its lineage — rather than leaving a false current instruction in force.

Private agent memory may record an incident or point to this canonical rule **only when ASK explicitly authorizes that memory write**. This section does not itself authorize creating, extending, or revising memory. Private agent memory is not the owner of durable workflow protocol. Any retention under this clause remains subject to §Learning Disposition and §Private-Memory Write Gate.
<!-- rule-id: private-memory-not-owner -->

---

## Rule-to-Artifact Conformance Gate
<!-- rule-id: rule-to-artifact-conformance-gate -->

Before adding, materially revising, or applying a workflow rule that changes artifact naming, versioning, snapshots, routing, or lifecycle:

1. read the current canonical rule;
2. inspect the current artifacts, relevant lineage, and live citations the rule governs;
3. test the rule against the artifacts and the artifacts against the rule.

A long-standing written rule may have drifted. Repeated artifact practice may also be wrong. **If the rule and governed artifacts disagree, stop and obtain an ASK ruling before mutating either.**

Do not retroactively rename, normalize, or rewrite historical artifacts solely to force apparent conformance. After the ruling: **if the ruling changes the canonical rule**, update that rule first, then conform current active carriers within the authorized scope. **If the rule stands**, leave it unchanged and conform the current artifacts instead.

---

## Path Migration: Reverse-Consumer Enumeration
<!-- rule-id: path-migration-reverse-consumer-enumeration -->

Moving or renaming a canonical path breaks every surface that *points at* it, which is a strictly larger set than the surfaces that *move*. Enumerate consumers; do not reason about scope.

Before the cutover, list:

1. objects that move;
2. direct references inside the owning surface;
3. every external source index that maps the path;
4. downstream trackers, adapters, prompts, and routing instructions;
5. walled or private consumer indexes;
6. actual Project-source inventories and retrieval behavior — mounted Sources, Instructions, live connector paths, standing mounts, on-demand fallbacks, and any claim about which of those exists;
7. local launch configs, scripts, agent memory, aliases, symlinks;
8. human applications keyed to the path;
9. current locators versus historical event-time paths.

**A surface being out of scope for moving does not put it out of scope for referencing.** That inference is the characteristic failure: a downstream project keeps its own root, so it is excluded from the migration — and its index, trackers, and prompts keep pointing at an address that no longer exists.

**Post-cutover fail-closed claims apply §Verification Claims and Evidence Boundaries.** "No stale references remain" is a claim about what was scanned. Name the exact carrier set tested, or the result will be read as broader evidence than the check supports.

**Per-line disposition, never a blanket swap.** A current locator tells the reader where to find a retained artifact — update it. A historical record states where something lived at event time — leave it. A line doing both keeps its narrative and gets its locator corrected, or states both paths explicitly. Ambiguous function stops for an ASK ruling rather than a guess.

**A migration is also an audit.** Reading every consumer may surface drift that predates the move — stale bases, retired conventions, or declarations that disagree with disk or Project UI. Record it as adjacent. Repair it only when the active scope explicitly authorizes that correction and the acting surface has write jurisdiction; otherwise flag or route it under §Cross-Surface Change Routing.

---

## Repo Workflow Discipline

### Session-Start Discipline
<!-- rule-id: session-start-discipline -->

Before any new repo work in a session:

1. Confirm the working directory is the session-owned worktree or approved repo root for this session. Cross-worktree absolute paths are a known failure surface; verify before any edit, write, or cross-root `git -C` command.
2. Verify `HEAD` is attached to a named branch. Detached `HEAD` is a stop condition.
3. Verify the working tree is clean.
4. If the working tree is not clean, stop. Identify whether the changes belong to the current thread before touching anything. Inheriting another thread's uncommitted state is a stop condition until provenance is established.

This does not replace Branch Freshness or Default Verification. It is the session-entry gate before meaningful repo work begins.

### Branch Freshness
<!-- rule-id: branch-freshness -->

For repo implementation work, follow this sequence:

1. verify local repo attachment
2. verify clean working tree
3. `git fetch origin --prune`
4. `git checkout main`
5. `git pull --ff-only origin main`
6. create task branch from refreshed `main`
7. stop if any verification fails

Do not start meaningful repo work from a stale, dirty, detached, or ambiguous branch.

### Default Verification
<!-- rule-id: default-verification -->

Before meaningful work, verify:

```text
pwd
git rev-parse --show-toplevel
git remote get-url origin
git branch --show-current
git status --short
```

Stop if repo root, remote, branch, or working tree does not match the task requirements.

### Terminal-State Discipline — do not conflate
<!-- rule-id: terminal-state-do-not-conflate -->

Do not conflate distinct terminal states. Each is a separate, independently verifiable fact:

- local edits
- exact scoped diff
- local commit
- pushed branch
- PR created
- merged PR
- branch cleanup

A report that collapses two of these (e.g. "done" for a change that is only committed locally, or "merged" for a change only pushed) is a defect regardless of the vocabulary used.

### Terminal-State vocabulary
<!-- rule-id: terminal-state-vocabulary -->

Use these explicit terminal states by name:

```text
exact scoped diff ready for approval
committed locally only
pushed branch only
PR created
merged
merged branches cleaned up
```

### Explicit Artifact-Lifecycle Verbs
<!-- rule-id: explicit-artifact-lifecycle-verbs -->

Do not use `cut` as an operation verb for drafts, changes, files, versions, snapshots, handoffs, releases, or other artifacts. It is ambiguous between creation and destruction.

Name the actual operation instead: draft, write, revise, save, create a version, create a snapshot, copy at byte parity, rename, route, supersede, retire, or delete.

This rule applies to plans, instructions, handoffs, change summaries, and status reports. Historical quotations, provenance records, frozen artifacts, and unambiguous domain terms such as a film's rough cut are not rewritten solely to enforce it.

### Exact Scoped Diff Gate
<!-- rule-id: exact-scoped-diff-gate -->

Stop at exact scoped diff unless ASK has already approved commit / push / PR.

The default implementation terminal state is:

```text
exact scoped diff ready for approval
```

Exact scoped diff review is the mandatory approval checkpoint before meaningful write actions complete. Approval may be given inside the executor session after the diff is reviewed; once given, the executor may complete the remaining git workflow without separate manual GitHub UI ceremony.

### Advisor-Readable Review Objects
<!-- rule-id: advisor-readable-review-objects -->

When exact-byte advisor review is required and the advisor cannot read the executor's session-local scratch, publish the minimum named review object to the narrowest authorized shared-scratch path mapped by the surface's source index (`_INDEX`). This is the normal transport surface for cross-surface exact review. **Use an already advisor-readable exact surface first:** a pushed PR is the review object for repo changes once it exists — do not create a duplicate shared-scratch packet merely because session-local scratch is unreadable. Session-local scratch remains appropriate for intermediate construction and for objects not intended for cross-surface review; manual operator upload is fallback only when the payload is already authorized for this advisor and the mapped shared path is temporarily unavailable or technically unreachable.

**Path authorization is not content authorization.** A mapped scratch path authorizes a retrieval route, not every payload that could travel it. Do not copy secrets, wall-bound material, or any payload the advisor is not authorized to read into shared scratch or into a manual upload. If the mapped path or the payload is outside the advisor's authorized read surface, stop and ask ASK to name an authorized review surface; upload does not cure an authorization boundary and never bypasses a wall.

A request to prepare an exact artifact for advisor review authorizes one declared proposal-only review object or bounded review bundle, provided its exact path(s), filename(s), role, and lifecycle (supersession trigger) are stated before creation. It does **not** authorize the target canonical, a version snapshot, a companion artifact, a repo commit, or a private-memory write — each of those remains a separate approval unit.

The review object carries its proposal status in its **scratch path, filename, and handoff**, never in wrapper text that would alter bytes intended to match a target. It takes one of three forms:

- **single-artifact exact-byte review** — the `-PROPOSED` object is byte-identical to the proposed target bytes;
- **single-file multi-target review** — one `-PROPOSED` packet carries the complete exact patch, the target file set, the baseline refs, the proposed hashes, and the declared role and lifecycle, **when the advisor can retrieve it completely**;
- **connector-bounded review bundle** — when one packet cannot be retrieved completely (connector text-extraction truncation), or a target is not representable as a text patch, publish one declared bundle of ordered exact-object or exact-patch parts in mapped shared scratch. Its manifest records, per part: ordered path, `part_type` (`exact-object` | `exact-patch`), the target path or set, byte size, SHA-256, a baseline ref/hash where applicable, the reconstruction operation, and the proposed target hash — plus the complete target set, the package hash, role, and lifecycle. A text or repo diff is an `exact-patch` against a declared baseline; a binary or non-patch artifact (a PNG, a diagram export, any exact object) is carried as its exact proposed object bytes; a mixed package may contain both part types. Prefer one bounded part per target over arbitrary prose truncation, but never force binary target bytes into a text-extraction representation. The manifest itself and every part must be individually retrievable through the intended advisor path; every physical path is declared before creation; the bundle is one logical transport operation, not open-ended scratch authority.

**Once its path and hash have been reported for review, a review object or bundle is immutable.** Never overwrite it in place. A revision receives a new unique dated or `_vN` `-PROPOSED` name, identifies its predecessor, and reports new hashes; the superseded object remains scratch provenance unless ASK separately authorizes retirement.

Report the target path(s), baseline ref/hash, and proposed hash in the handoff. A shared-scratch review object is an ordinary named operator-scratch artifact — a visible surface under normal proposal/scratch discipline, **not** a private persistent surface governed by §Private-Memory Write Gate.

### Structured Change Summary
<!-- rule-id: structured-change-summary -->

Meaningful changes require a structured change summary covering:

- why this change exists
- what changed
- what did not change
- what remains out of scope

If a PR is used, this belongs in the PR description. If no PR is used, the same summary must be produced in the executor handoff or approval record before write actions complete.

When the work surfaces a potentially reusable learning, include a one-line learning disposition: visible owner · nomination/hold · private-memory candidate pending separate authorization · or no retention. "Reusable" is not itself a destination.

### Operator-Side Voice Scan
<!-- rule-id: operator-side-voice-scan -->

Before presenting an exact scoped diff for approval, scan added prose for voice / surface-boundary risk against the project's named operator-side voice owner(s) and grounding-note voice guidance. Do not assume a private-memory artifact exists or owns those constraints. Any private-memory contribution must already have survived §Learning Disposition and remains subject to §Private-Memory Write Gate.

Flag any matches or concerns honestly in the structured change summary. Do not auto-sanitize: some apparent matches may be legitimate domain vocabulary that the project needs to name directly.

The scan rule may live in `AGENTS.md`; the token list, translation table, and protected domain-vocabulary list do not. Route those specifics to the narrowest authorized operator-side owner suited to their wall and cadence; do not copy them into repo-local artifacts. Private memory may retain only ASK-authorized machine-local, wall-bound, or deliberately non-operative residue under the two gates.

### Default: Hold or Carry Through Per Adversarial-Collaboration Preconditions
<!-- rule-id: default-hold-or-carry-through -->

When ASK has approved the scoped diff, the workflow continues through commit and push to PR creation.

If the project meets the preconditions for adversarial collaboration (per [*Adversarial Collaboration*](https://atomicspacekitten.substack.com/p/adversarial-collaboration)) — hardened backbone, active architectural uncertainty, configured advisor surface — hold at `PR created` until the advisor relay returns approval, then continue to merge. The pushed-not-merged PR is the advisor's structural review window.

ASK forwarding an advisor approval to the executor is the relay. Forwarding may be done by pasting the advisor's approval, summary, or equivalent review result. No additional approval phrase is required after the forwarding act.

Forwarding advisor notes that contain required fixes, blocking concerns, or open questions is not approval relay; it is fix-direction or question-forwarding.

If no advisor surface is configured, carry through to merged + cleanup once diff approval is given. The pattern is proportional to architectural uncertainty live at any moment.

### PR Creation
<!-- rule-id: pr-creation -->

When creating a PR, report:

- branch name
- commit SHA
- PR number
- PR URL
- actual base branch
- actual head branch
- validation performed
- terminal state: `PR created`

### Post-Merge Cleanup
<!-- rule-id: post-merge-cleanup -->

After merge, verify `main`, delete merged task branches where safe, verify remote branch state, and report:

- current main HEAD
- whether merge commit is present
- whether expected changes are present
- local branch cleanup
- remote branch cleanup
- final branches
- final working tree status
- terminal state: `merged branches cleaned up`

Post-merge cleanup never includes private-memory mutation unless a separately planned and explicitly authorized memory operation remains open.

### Direct Push to Main
<!-- rule-id: direct-push-to-main -->

Branch plus PR is the default for meaningful structure or rule changes. Narrow low-risk edits or explicitly scoped bootstrap tasks may allow direct push to `main` when scope is made explicit and approved.

---

## Session Topology / Single-Writer Discipline
<!-- rule-id: session-topology-single-writer -->

Multiple operator sessions (multiple Claude Code threads, parallel Codex sessions, ChatGPT thread plus Codex thread) can mutate the same repo files concurrently. This is a real failure mode, not a hypothetical.

Rules:

- **One writer at a time per branch.** A second operator session on the same branch must verify state freshly, treat the working tree as authoritative over its own memory, and not assume mid-flight context from another session.
- **Treat repo and remote as the audit trail.** When two sessions disagree about state, prefer `git status`, `git log`, and remote-branch state over either session's recollection.
- **Stop on suspected concurrent mutation.** If a working tree contains changes the current session did not make, do not overwrite. Re-orient against the repo before continuing.

This rule applies whether the second session is the same agent, a different agent, or a human editor.

---

## Scope Discipline
<!-- rule-id: scope-discipline -->

Match the unit of work to the level of the question.

For implementation and repo hygiene, prefer the smallest honest unit. Small bounded PRs are usually best. Avoid bundling, widening, or design-in-advance.

For conceptual architecture, prefer the largest tractable structural question. The smallest honest unit at the architecture layer is often a structural question or a model attempt against a concrete example, not another local prototype probe.

Do not let "smallest unit" become a rule that prevents zooming out to the right scale. A series of small honest units at the wrong layer can add up to ceremony without architectural progress.

Do not bundle unrelated work. Do not widen scope mid-task unless the widening is explicitly chosen. Do not create artifacts merely because a process pattern exists.

---

## Plan-Before-Execute Rule
<!-- rule-id: plan-before-execute -->

Before executing a meaningful repo change, state the plan: what files will change, what scope is in vs out, what non-actions apply, what terminal state is expected.

This applies whether the executor is a separate process (Codex) or the same agent doing the planning (Claude Code).

The plan-before-execute step preserves the explicit reasoning surface that prompt-compilation provides when execution is split across a prompt-compiler and an executor. In a single-node model, plan-before-execute is the rule that restores it. Do not collapse plan and execution into a single opaque step.

Any proposed private persistent mutation must be named as a separate planned operation with its exact target, exact proposed mutation, visible-owner or no-retention disposition, and terminal state.

For a creation, include the full proposed payload. For an edit, include the exact diff or replacement payload. For a deletion, include the exact path, deletion warrant, pre-deletion size/hash receipt, and expected absence or restored-byte/hash receipt.

If the operation is absent from the approved plan, the private persistent mutation is out of scope.

---

## Tool-Dependent Workflow Rules
<!-- rule-id: tool-dependent-workflow-rules -->

When a project workflow depends on an external tool, vendor, model, rendering surface, extraction surface, diagram-generation surface, or other operator-supplied system whose identity may change, encode the repo-local rule tool-agnostically.

In `AGENTS.md`, name the structural role the tool plays, when it is invoked, what inputs and outputs it expects, the authority boundary, and any refresh cadence. Carry the current approved tool / vendor / surface identity, the substitution path, and any operational details that depend on the specific tool outside that repo rule.

The repo rule names the structural role. The current occupant, substitution path, and vendor-specific operating details belong in the narrowest visible or operator-side owner suited to their cadence. Private memory may cache only machine-local or deliberately non-operative residue, and only under §Learning Disposition and §Private-Memory Write Gate.

---

## Comments, Docs, and PR Roles
<!-- rule-id: comments-docs-pr-roles -->

- Comments belong in implementation artifacts only when local clarity needs them.
- Docs describe architecture, boundaries, operating contracts, and reusable guidance.
- Structured change summaries and PR descriptions hold change-specific framing.

Do not push PR-only explanation into permanent repo docs, and do not hide durable operating rules inside a PR or approval record.

---

## Refresh Cadences

### Grounding Note
<!-- rule-id: refresh-cadence-grounding-note -->

Refresh the grounding note only when external handoff context changes: new strategic direction, philosophical reframing, audience or positioning shift, foundational premises change, operating model changes.

Do not refresh for routine repo chronology. Possible future directions belong in the grounding note only as durable loose threads, not as recommended next paths.

### `AGENTS.md`
<!-- rule-id: refresh-cadence-agents-md -->

Refresh this file only when a workflow rule is added, removed, or materially revised.

Do not refresh because project state changed. Do not refresh because a PR landed. Do not refresh because the next direction changed.

If a proposed update says "the project currently should do X," it does not belong in this file.

---

## Defaults
<!-- rule-id: defaults-shared -->

- Prefer ASK reuse over world-scale abstraction.
- Prefer explicit structure over clever indirection.
- Prefer the smallest coherent scaffold that clarifies the workflow boundary.
- Use clean technical language. Avoid manifesto phrasing, speculative systems, or generic process bloat. *(Voice/register specifics route to the operator voice canonical, not to a second authority here.)*

---

## Short Version

- Verify repo state before meaningful work.
- Read repo-local truth and grounding note before responding.
- Stop at exact scoped diff before commit; carry through to merged + cleanup once approved.
- State the plan before executing.
- Single-writer per branch. Treat repo as audit trail.
- Match the unit of work to the level of the question.
- Refresh `AGENTS.md` only for rule changes.
- Keep this file workflow-only. Repo holds state. Grounding note holds external context.
- Bound every verification claim to the exact evidence gathered; separate checked facts from inferences, and test rules against the live artifacts they govern before applying them.
<!-- END shared -->

<!-- BEGIN grant: standing-upstream-conformance-grant (OPTIONAL — separately-operated opt-in only) -->
## Standing upstream conformance grants

This repo grants the **active ASK control surface** standing write jurisdiction for **GREEN mechanical conformance** to merged upstream owner changes explicitly marked for propagation, under the control-surface propagation-wave protocol (`control-surface/AGENTS.md` §Cross-Repo Propagation Waves and `control-surface/prompts/cross-repo-propagation-wave.md`). "Active ASK control surface" is the executor; ecology-ASK is the coordination altitude and ledger; this repo remains the owner of its project truth.

### Design-system vendor maintenance

Covers: byte-identical re-vendoring of DS-owned files (engines, helper, exporter, CSS, font carrier); an owner-required support file and deterministic script load order; deterministic local pin / MANIFEST / README records; an existing, unambiguous source/render/date operation; and derived-artifact (raster/companion) regeneration where this repo's existing contract requires it.

### Execution-protocol maintenance

Covers: exact or substantively deterministic re-sync of inherited `control-surface` protocol clauses in declared carriers (`AGENTS.md`, templates, prompts); deterministic carrier additions/removals/load-order changes required by the merged protocol; and local provenance/pin/README/manifest updates recording the operation.

### Both lanes — bounds

**Covered:** preparation of a bounded branch and PR under this repo's normal diff / review / merge / cleanup gates.

**Not covered:** source of intent · product/domain decisions · project architecture · source data or diagram semantics · consumer-authored visual identity or geometry · bespoke adapters requiring design judgment · intentional local protocol exceptions · review/merge/release/sealing-policy changes · changes to this grant itself · unrelated cleanup.

**Active only when:** the upstream change is merged and its canonical path + SHA are identified; the affected carriers are confirmed at rest (human + machine, per the propagation-wave at-rest gate); the change is classified GREEN; repo-local deltas and intentional exceptions are preserved; and no unresolved interpretation or project-specific policy choice is required.

**On any stop condition** (active work, unexpected diff, locally-modified owner file, ambiguous mapping, ambiguous version/raster action, project-specific judgment, conflict with a local exception): do not improvise, do not merge, leave the obligation queued as re-sync due. Route a `-TBI` handoff only when recipient classification or a new grant is genuinely required — never as a deferred-task envelope.

Execution jurisdiction does not transfer artifact ownership. ASK may suspend or revoke this grant for a wave or for the repo.
<!-- END grant -->

<!-- BEGIN local-delta -->
## urban-observatory-Local

These rules are the repo-local delta for `urban-observatory` (a separately-operated ASK ecology consumer) on top of the shared protocol above. It installs no profile and opts into the standing upstream-conformance grant (installed above). `urban-observatory`'s local delta wins for `urban-observatory` where an explicit conflict exists.

## Required Reading Before Meaningful Work (UO layer)

Before any meaningful repo work, read:

- `README.md`
- `AGENTS.md` (this file)
- `docs/architecture.md`
- `docs/project-scope.md` and `docs/v0-scope.md` (scope + current phase), then the task-relevant `docs/` files (`object-model.md` · `source-strategy.md` · `methodology.md` · … — see `docs/architecture.md` for the full set)

Then read the latest milestone or finding artifact relevant to the task.

## Inbound handoff intake (UO layer)

The generic `-TBI` ingestion, rename-on-ingestion, and classification mechanics are owned by the shared §Inbound Handoff TBI Marker. Two UO-local specifics extend it.

The exact intake destination for routed inbound handoff memos is `urban-observatory-EXTERNAL/sources of intent/`.

Domain-authority-originated handoff memos may also carry `-TBI` while in transit when the originating review surface has read-only access to UO external files. ASK routes those memos into UO `sources of intent/` with the suffix intact; UO removes the suffix on ingestion.

## Project-Specific Defaults

UO has not yet defined project-specific verification/terminology defaults beyond standard repo discipline. Until it does, apply: clean tree · scoped diff · one branch per change · honor `docs/architecture.md` for domain structure and the **Architecture-Specific Rules** below for any load-bearing creative/governance act. Replace this section with concrete UO defaults (verification commands, protected paths, terminology-to-preserve, domain governance acts) once they earn a place.

## Architecture-Specific Rules (optional, project-by-project)

If the project's information architecture has a load-bearing creative or governance act (e.g. curation, capture, ratification, selection), model it as first-class in the schema and in the rules. Generic process rules cannot stand in for domain-specific structural decisions.

If the project has a prototype surface, decide whether the prototype is a pressure surface for studying the architecture or a deliverable in its own right. Document the answer.

If the project has external systems (databases, CMSs, workflow tools), decide how mutations to those systems are governed (Plan-Before-Execute applies; Structured Change Summary applies; per-action authorization may or may not be required depending on reversibility).
<!-- END local-delta -->
