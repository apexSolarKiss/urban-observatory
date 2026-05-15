# Architecture

## Repo Purpose

- repo purpose: open-source prototype for structuring fragmented public planning, housing, environmental, and budget information into intervention-oriented evidence briefs. Focuses on constraints, tradeoffs, sequencing, evidence quality, and likely consequences rather than predictive certainty.
- non-goals: not a GIS replacement; not a city optimizer; not a predictive planning authority; not a public-budget voting platform; not a generic civic dashboard; not a comprehensive national dataset; does not replace planners, policy experts, community processes, legal review, or environmental review; does not claim complete or neutral data.

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
- repo docs: `README.md`, `docs/architecture.md`, `[further docs as added — e.g. project-scope, intervention-brief-model, data-model, case studies]`
- external context: grounding note at `urban-observatory-EXTERNAL/sources of intent/urban-observatory_grounding-note.md` (operator-side)
- `[further artifact classes as the project takes shape — e.g. intervention briefs, schema definitions, case-study folders, evidence registries]`

## How The Pieces Relate

- `[to be filled in once initial bootstrap PR establishes the first concrete artifacts]`
- The grounding note carries source-of-intent context (audience, voice discipline, market/opportunity framing) and does not override repo-local truth once files exist.
- Repo-local docs are explanatory + structural; `AGENTS.md` is operational; the grounding note is external context.

## Architecture-Specific Anchors

The project's load-bearing primitive is likely the **intervention** rather than the parcel, neighborhood, or dashboard. A candidate primitive relationship:

```text
intervention
  has constraints
  depends on evidence items
  affects outcomes
  creates tradeoffs
  has sequencing dependencies
  carries uncertainty
  may shift burdens / benefits across groups or geographies
```

This is held as a working hypothesis, not as a fixed schema. The first concrete brief should pressure-test whether `intervention` is the right primitive or whether the load-bearing unit is something else (constraint, site, outcome).

Evidence quality, provenance, and uncertainty are first-class properties of any structured output. Outputs without provenance are not the same artifact class as outputs with provenance; the architecture should preserve the distinction.

## Ownership Notes

- local source of truth: repo-local files (this doc, `AGENTS.md`, `README.md`, future docs)
- external dependencies or governing artifacts: external grounding note for source-of-intent context; public-data sources to be enumerated as the data model takes shape
