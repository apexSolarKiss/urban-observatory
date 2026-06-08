# Architecture

## Repo Purpose

- repo purpose: open-source prototype for **implementation intelligence** — a public-data method for continuously interpreting whether public plans, policies, infrastructure commitments, and capital investments are translating into actual urban outcomes, and what would most effectively close the gap when they aren't. Outputs are memo-form interpretations with explicit uncertainty and provenance.
- first operational domain: housing implementation. Housing is the first domain, not the whole project. See [`project-scope.md`](project-scope.md) for what is in and out of scope and [`implementation-intelligence.md`](implementation-intelligence.md) for the core concept.
- non-goals: the canonical anti-goal list lives in [`project-scope.md`](project-scope.md). Briefly: not a GIS replacement, not a planning-department replacement, not an enforcement tool, not a deterministic feasibility engine, not a dashboard-first product, not a predictive authority, not a developer underwriting platform, not a smart-city platform. Does not replace planners, policy experts, community processes, legal review, or environmental review. Does not claim complete or neutral data.

## Operating Model

- operating model: single-node (Claude Code as control surface and executor) — default for new ASK projects
- live operator: Claude Code
- optional advisors: GPT

The workflow rules apply regardless of which agent does the executing. Rules live in repo-local `AGENTS.md`.

## Sources Of Truth

- **Repo** = project state
- **`AGENTS.md`** = workflow rules
- **Grounding note** (external) = intent, audience, philosophy, foundational premises, durable loose threads
- **Per-conversation memory** (operator-side) = ephemeral session state; not durable
- `[public-data sources and document collections used as evidence inputs — to be enumerated as the data model takes shape]`

## Artifact Model

- repo-local execution files: `AGENTS.md`, `CLAUDE.md`, `LICENSE`
- repo docs: `README.md`, `docs/architecture.md` (this file), [`docs/project-scope.md`](project-scope.md), [`docs/implementation-intelligence.md`](implementation-intelligence.md), [`docs/methodology.md`](methodology.md), [`docs/v0-scope.md`](v0-scope.md), [`docs/object-model.md`](object-model.md), [`docs/source-strategy.md`](source-strategy.md), [`docs/source-inventory.md`](source-inventory.md), [`docs/data-dictionary.md`](data-dictionary.md), [`docs/report-outline.md`](report-outline.md), [`docs/method-appendix-worked-pattern.md`](method-appendix-worked-pattern.md)
- external context: grounding note at `urban-observatory-EXTERNAL/sources of intent/urban-observatory_grounding-note.md` (operator-side)
- a site-abstracted worked-pattern method appendix ([`method-appendix-worked-pattern.md`](method-appendix-worked-pattern.md)) now exists, demonstrating the interpretive chain on one real case (the named instance is held operator-side). Further artifact classes (schemas, sample datasets, analysis notebooks, report artifacts, named-site examples) do not yet exist; they are candidate later phases that depend on decisions that have not been made.

## How The Pieces Relate

- `README.md` states the public thesis and entry points.
- [`project-scope.md`](project-scope.md) defines what is in and out of scope; housing implementation is the first operational domain.
- [`implementation-intelligence.md`](implementation-intelligence.md) defines the core concept the method is built around.
- [`methodology.md`](methodology.md) describes how interpretation works — public-data-only, memo-like, uncertainty- and provenance-first, modest in claims.
- [`v0-scope.md`](v0-scope.md) defines the current v0 working scope: bounded whole-city San Francisco Housing Element implementation-intelligence prototype, bounded by depth rather than geography.
- [`object-model.md`](object-model.md) names the interpretive chain (`Assumption → ImplementationSignal → ImplementationFinding → InterventionCandidate`) and supporting primitives as a working hypothesis.
- [`source-strategy.md`](source-strategy.md) describes the public-data source posture (Tier A / B / C categories), prioritized but open-ended.
- [`report-outline.md`](report-outline.md) describes the structure of the first artifact (Housing Element Implementation Risk Brief) at heading level only.
- [`method-appendix-worked-pattern.md`](method-appendix-worked-pattern.md) is a site-abstracted worked-pattern appendix demonstrating the interpretive chain on one real case; the named instance is held operator-side.
- This file holds repo-local structural framing and source-of-truth boundaries; it does not duplicate scope or method content.
- `AGENTS.md` holds workflow rules, agent-agnostic.
- The external grounding note carries source-of-intent context (audience, voice discipline, market/opportunity framing) and does not override repo-local truth once files exist.
- Repo-local docs are explanatory + structural; `AGENTS.md` is operational; the grounding note is external context.

## Architecture-Specific Anchors

At current v0 planning depth, the repo is organized around the interpretive chain `Assumption → ImplementationSignal → ImplementationFinding → InterventionCandidate`. `Assumption` is the v0 load-bearing interpretive primitive: the method tests whether assumptions embedded in public plans, reports, inventories, programs, and related documents remain plausible under changing implementation conditions. This is a working ontology direction, not final schema doctrine.

Supporting primitives such as `OpportunitySite`, `HousingProject`, `PolicyProgram`, `InfrastructureDependency`, `Constraint`, `Outcome`, `Source`, and `Confidence` remain essential but are not the conceptual center; their schema-shape decisions remain open at v0 depth. See [`object-model.md`](object-model.md) for the chain, supporting primitives, candidate signal subtypes, and what stays conceptual in v0, and [`data-dictionary.md`](data-dictionary.md) for the per-concept Markdown-first treatment.

Evidence quality, provenance, and uncertainty are first-class properties of any structured output. Outputs without provenance are not the same artifact class as outputs with provenance; the architecture should preserve the distinction.

## Ownership Notes

- local source of truth: repo-local files — this doc, `AGENTS.md`, `README.md`, [`docs/project-scope.md`](project-scope.md), [`docs/implementation-intelligence.md`](implementation-intelligence.md), [`docs/methodology.md`](methodology.md), [`docs/v0-scope.md`](v0-scope.md), [`docs/object-model.md`](object-model.md), [`docs/source-strategy.md`](source-strategy.md), [`docs/report-outline.md`](report-outline.md), [`docs/data-dictionary.md`](data-dictionary.md).
- external dependencies or governing artifacts: external grounding note for source-of-intent context; public-data sources to be enumerated as the data model takes shape.
