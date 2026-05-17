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
- repo docs: `README.md`, `docs/architecture.md` (this file), [`docs/project-scope.md`](project-scope.md), [`docs/implementation-intelligence.md`](implementation-intelligence.md), [`docs/methodology.md`](methodology.md)
- external context: grounding note at `urban-observatory-EXTERNAL/sources of intent/urban-observatory_grounding-note.md` (operator-side)
- further artifact classes (schemas, sample datasets, analysis notebooks, report artifacts, examples) do not yet exist. They are candidate later phases that depend on Tier 1 scoping decisions — specific implementation surface, geography, dataset, and computed interpretations — that have not been made.

## How The Pieces Relate

- `README.md` states the public thesis and entry points.
- [`project-scope.md`](project-scope.md) defines what is in and out of scope; housing implementation is the first operational domain.
- [`implementation-intelligence.md`](implementation-intelligence.md) defines the core concept the method is built around.
- [`methodology.md`](methodology.md) describes how interpretation works — public-data-only, memo-like, uncertainty- and provenance-first, modest in claims.
- This file holds repo-local structural framing and source-of-truth boundaries; it does not duplicate scope or method content.
- `AGENTS.md` holds workflow rules, agent-agnostic.
- The external grounding note carries source-of-intent context (audience, voice discipline, market/opportunity framing) and does not override repo-local truth once files exist.
- Repo-local docs are explanatory + structural; `AGENTS.md` is operational; the grounding note is external context.

## Architecture-Specific Anchors

The project's load-bearing primitive is not yet decided. Credible candidates that remain open include `intervention`, `implementation`, `site`, `risk`, `constraint`, and `outcome`. Each names a plausible organizing unit for the method. None is canonical at this stage, and the first concrete prototype work is what will reveal which carries the most weight.

One illustrative candidate sketch, organized around `intervention`:

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

This sketch is held as one working hypothesis among several, not a fixed schema or a foreclosed choice. Alternative primitives (`implementation`, `site`, `risk`, `constraint`, `outcome`) would yield different but equally plausible relational sketches. Do not foreclose between them before prototype work has tested them.

Evidence quality, provenance, and uncertainty are first-class properties of any structured output. Outputs without provenance are not the same artifact class as outputs with provenance; the architecture should preserve the distinction.

## Ownership Notes

- local source of truth: repo-local files — this doc, `AGENTS.md`, `README.md`, [`docs/project-scope.md`](project-scope.md), [`docs/implementation-intelligence.md`](implementation-intelligence.md), [`docs/methodology.md`](methodology.md).
- external dependencies or governing artifacts: external grounding note for source-of-intent context; public-data sources to be enumerated as the data model takes shape.
