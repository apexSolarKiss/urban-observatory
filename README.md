# urban-observatory

![urban-observatory banner](urban-observatory-banner.jpg)

An open-source **civic implementation observatory**: a public-data method for reconstructing how public plans, policies, capital programs, and other civic commitments move from decision into delivery — and for maintaining a partial, public, provenance-preserving, contestable account of what the evidence shows, and cannot show, about that delivery as conditions change.

`urban-observatory` is being developed to track civic commitments across the responsible actors, resources, funding, approvals, actions, milestones, delivery conditions, completion, and outcomes that carry them into practice, updating its reading as conditions change. As designed, it shows progress, delay, change, completion, outcomes, and uncertainty rather than collapsing implementation into a single verdict, and it holds evidence of progress and evidence of delay to the same standards. Missing information is recorded as an observability limit — never read as success, stability, or failure. By maintaining a publicly inspectable, provenance-preserving, contestable record of the evidence, its sources and methods, its interpretations and alternative readings, its known gaps, and the limits of what can be concluded, the project works toward a public reading of implementation that does not rest on any single institution's account. **Public data is treated as an auditable common floor, not a claim to completeness.**

Its **primary** function is the observatory — maintaining that account. A **secondary, connected capability** is a reusable planning-intelligence substrate: the same maintained evidence, current conditions, source linkages, and analytical inputs may reduce duplicated assembly and inconsistent assumptions across recurring analyses. That capability remains to be validated, not a coequal promise. The project holds three complementary layers: a **commitment-lifecycle world model** (what it tracks — a *grammar*, not a rigid schema or a linear pipeline); an **assumption-centered interpretive method** — *implementation intelligence*, which reads public plans, reports, inventories, and programs for where adopted assumptions still hold or are drifting, and identifies relationships separate reports do not show (shared dependencies, conflicting assumptions, sequencing gaps, misaligned investment, drift over time); and a **civic governance envelope** of contestable selection, declared information gaps, even-handed evidence, visible maintenance failures, and traceable decision relationships. The layered *direction* is settled; its schema, fields, state vocabularies, and object relationships remain a working hypothesis. Observed outcomes enter as evidence within the interpretation, not as a scorecard. The logic is cross-system: housing implementation is read against the infrastructure, transportation, capital, environmental, and institutional conditions it depends on. **Housing implementation is the first institutional domain tested, not the analytical boundary.**

The project is method-first, public-data based, and modest in its claims. It does not predict, optimize, or replace planning judgment. Whether the observatory produces value beyond existing reports, dashboards, and expert analysis is treated as an **open, unproven question**, not a settled claim. See [`docs/project-scope.md`](docs/project-scope.md) for what is in and out of scope, [`docs/implementation-intelligence.md`](docs/implementation-intelligence.md) for the interpretive method, and [`docs/methodology.md`](docs/methodology.md) for how interpretation works. For the v0 working scope — a narrower proof component of the broader observatory, not its full scope — see [`docs/v0-scope.md`](docs/v0-scope.md); for the interpretive chain and supporting primitives, [`docs/object-model.md`](docs/object-model.md); for the public-data source posture, [`docs/source-strategy.md`](docs/source-strategy.md); and for the structure of the first artifact, [`docs/report-outline.md`](docs/report-outline.md). For a worked-pattern method appendix demonstrating the interpretive chain on one site-abstracted case, see [`docs/method-appendix-worked-pattern.md`](docs/method-appendix-worked-pattern.md).

## Sources of Truth

- **Repo** = project state (artifacts, decisions, current navigation)
- **[`AGENTS.md`](AGENTS.md)** = workflow rules, agent-agnostic
- **External grounding note** = intent, audience, philosophy, foundational premises, durable loose threads
- **[`docs/architecture.md`](docs/architecture.md)** = repo-local architecture and source-of-truth boundaries

## Status

`urban-observatory` is in active prototype development, method-first. The repo carries workflow rules (`AGENTS.md`), an architecture sketch (`docs/architecture.md`), the public scope, concept, methodology, v0-scope, object-model, source-strategy, source-inventory, data-dictionary, and report-outline documents in `docs/`, and one site-abstracted **worked-pattern method appendix** ([`docs/method-appendix-worked-pattern.md`](docs/method-appendix-worked-pattern.md)) demonstrating the interpretive chain on one abstracted case. The method has also been **internally exercised** operator-side against additional named public-record cases and contrast conditions; that **held case material** remains operator-side pending review, abstraction, and publication gates, and is not in this repo (see [`docs/project-scope.md`](docs/project-scope.md)). **No datasets, notebooks, repo-resident named-site analyses, or report artifacts exist in the repo yet** — those are candidate later phases that depend on decisions that have not been made.

## Background Articles

Background articles, in chronological order (Substack is the source of truth):

- [*From Conversation to Control Surface*](https://atomicspacekitten.substack.com/p/from-conversation-to-control-surface) — the project's inception story: messy AI-mediated exploration recovered into intent, validated constraint, and a load-bearing repo (cross-listed from the workflow/method series).
- [*A Parcel Is Never Just a Parcel*](https://atomicspacekitten.substack.com/p/a-parcel-is-never-just-a-parcel) — the first domain-facing public argument: housing implementation cannot be read from housing records alone; reading the cross-system dependency field with explicit uncertainty.

## License

Copyright 2026 Andrew S Klug // ASK

Licensed under the Apache License 2.0 // see [`LICENSE`](LICENSE)
