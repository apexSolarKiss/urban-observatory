# Project Scope

[`urban-observatory`](../README.md) is an open-source **civic implementation observatory**: a public-data method for reconstructing how public plans, policies, capital programs, and other civic commitments move from decision into delivery, and for maintaining a partial, public, provenance-preserving, contestable account of what the evidence shows — and cannot show — about that delivery as conditions change. It broadens an earlier *implementation-intelligence* framing: implementation intelligence remains the project's interpretive method, now set inside a wider observatory purpose whose object is **public commitments and their delivery**, not the method alone. The method still reconstructs how intent is carried into practice and identifies relationships separate reports do not show — shared dependencies, conflicting assumptions, sequencing gaps, misaligned investment, and implementation drift over time. Observed outcomes enter as evidence within that interpretation, not as a scorecard.

This document defines what the project is, what it is not, and how its scope is sequenced.

## What this project is

Urban Observatory is, first, an **observatory**: it maintains a shared, inspectable record of how civic commitments move through responsible actors, funding, approvals, actions, milestones, completion, and outcomes, and gives public-interest readers comparison, continuity, transparency, and clearer points of action. "Actionability" here means better evidence and more legible intervention points — not legal authority, funding, enforcement, or guaranteed institutional response. A **secondary, connected capability** — a reusable planning-intelligence substrate, the same maintained evidence reused across recurring analyses — remains to be validated, not a coequal promise.

It holds three complementary layers: a **commitment-lifecycle world model** (what it tracks — commitment → responsible actors → funding and approvals → actions and milestones → completion → outcomes → updated analysis, stated as a *grammar*, not a rigid schema or a linear pipeline: real implementation branches, loops, stalls, reverses, changes actors, carries parallel funding and approval paths, and produces partial, interim, or contested outcomes), an **assumption-centered interpretive method** (how it reads what it tracks; `Assumption` is a load-bearing primitive, no longer the sole object of observation), and a **civic governance envelope** (how it stays trustworthy — contestable selection, declared information gaps, even-handed evidence, visible maintenance failures, and traceable decision relationships). The same evidence standards apply to progress and to delay; missing information is recorded as an observability limit, never converted into success, stability, or failure. Public data is an auditable common floor, not a completeness claim.

What is settled is the purpose, the function hierarchy, and the layered *direction* — **not the data structure.** The lifecycle's schema, fields, state vocabularies, object relationships, and its representation of state, time, provenance, gaps, and re-analysis remain open, to be pressure-tested on real cases before any object-model change.

`urban-observatory` is method-first. It is being developed to test:

- **a maintained public account of commitments and their delivery** — tracking how civic commitments move through responsible actors, funding, approvals, actions, milestones, completion, and outcomes, updated as conditions change; the observatory function the tests below serve;
- **continuous interpretation** of public-data signals about urban implementation reality;
- **synthesis of fragmented documents** (plans, environmental reviews, agendas, permits, progress reports, capital plans, policy documents, funding records) into coherent interpretations;
- **detection of contradictions** between what one document assumes and what another (or on-the-ground evidence) actually shows;
- **tracking of implementation drift** — the gap between planning assumptions and current conditions, over time;
- a **memo-like + schema-backed artifact posture** for outputs, with explicit uncertainty, categorical risk tiers, and source provenance;
- a **candidate ontology** for representing the entities involved (sites, projects, infrastructure dependencies, policy programs, market signals, implementation risks, feasibility shifts, intervention candidates).

The project's intended outputs are written analyses over a maintained, provenance-preserving account. It is not intended to produce dashboards, decisions, predictions, or compliance determinations.

## What this project is not (anti-goals)

`urban-observatory` is **not**, and is not trying to become:

- a GIS replacement
- a planning-department replacement
- an HCD or other agency enforcement tool
- a deterministic feasibility engine
- a public-budget voting tool
- a comprehensive national dataset
- a dashboard-first civic product
- a predictive authority
- a developer underwriting platform
- a city-optimization system
- an AI replacement for planners
- a smart-city platform

It does not replace planners, policy experts, legal review, CEQA review, community processes, agency judgment, or professional feasibility analysis.

It does not claim to determine: true feasibility, legal compliance, CEQA conclusions, agency compliance, or final planning judgments.

It is not an advocacy tool, an accountability scorecard, or a grading system. Its aim is that the public account of implementation stays inspectable and contestable when responsibility and decisive information are fragmented across institutions — pursued through an **even-handed method**: the same standards apply to evidence of progress and evidence of delay, and to supporting and weakening evidence alike.

It interprets implementation conditions with explicit uncertainty. Its outputs are advisory, not authoritative.

## In scope (now)

- The civic implementation observatory as the primary purpose; implementation-intelligence as its interpretive method.
- Public-data-only synthesis discipline.
- Candidate ontology for the entities the method reasons over.
- Uncertainty representation (approximately 70% qualitative interpretation / 30% lightweight scoring; categorical tiers; confidence ranges; directional change).
- Source-provenance discipline (every claim cites a public source, retrieval date, and confidence level).
- Methodology documentation for how synthesis works.

## First operational domain

The first operational domain is **housing implementation**, specifically the post-adoption interpretation question California's 2023–2031 RHNA-cycle Housing Element environment puts on cities: are adopted assumptions about opportunity sites, production pipelines, infrastructure dependencies, and funding still plausible as conditions change?

**Housing is a first domain, not the project's identity.** Other domains — capital improvement programs, transportation–housing coordination, climate-adaptation implementation, infrastructure sequencing — may follow once the method is credible in housing.

### Current v0 direction (scoped recommendation, not doctrine)

The current scoped v0 direction is a **bounded whole-city San Francisco Housing Element implementation-intelligence prototype**, structured as an APR-augmentation companion. v0 is bounded by analytical depth, automation level, confidence representation, interpreted outputs, signal coverage, and review posture — not by shrinking geography below whole-city San Francisco.

v0 is a **narrower proof component** of the broader observatory purpose — a bounded slice through which the assumption-centered interpretive method is tested — not the full scope of what the observatory is for. v0 predates the commitment-lifecycle framing and does not yet exercise it.

For the v0 scope statement, the hybrid implementation surface, and what v0 is and is not, see [`v0-scope.md`](v0-scope.md). For the interpretive chain the prototype reasons over, see [`object-model.md`](object-model.md). For the public-data source posture, see [`source-strategy.md`](source-strategy.md). For the structure of the first artifact, see [`report-outline.md`](report-outline.md).

APR augmentation here means *adding implementation interpretation* to an existing reporting workflow — making the question of whether adopted assumptions still hold visible in a form planners and consultants can act on. It does not mean producing the APR itself, replacing it, or determining its compliance status.

This is the current scoped direction, not immutable doctrine. As prototype work tests the method, the direction may be refined.

## Deferred / out of scope for now

The following are intentionally deferred until subsequent scoping decisions are made and validated:

- **Later case studies, second-pilot themes, and public-facing examples.** Beyond the current v0 San Francisco Housing Element implementation-intelligence prototype, additional case studies and pilot themes remain deferred.
- **Specific dataset selection.** Candidate first-corpus categories appear in the methodology document; specific source choices await initial scoping work.
- **Schema files, sample data, analysis notebooks, and report artifacts.** These are **candidate later phases, not guaranteed deliverables.** They depend on resolving a set of preceding scoping decisions (specific implementation surface, geography, dataset, and computed interpretations) that have not been made and that the prototype work itself will inform.
- **Application UI, maps, dashboards, public query interfaces.**
- **AI extraction / ingestion pipelines** beyond what's needed for a first prototype analysis.

## Where this comes from

External context (intent, audience, philosophy, foundational premises, unresolved questions, voice discipline) lives in the project's grounding note, which is operator-side and not in this repo. The repo itself is the operative source of truth for what the project actually is and does. See [`docs/architecture.md`](architecture.md) for repo-local boundaries and [`AGENTS.md`](../AGENTS.md) for workflow rules.

The project also holds **operator-side evidence** that is not in this repo: named-site, fully-sourced case material the method has been **internally exercised** against, retained operator-side pending review, abstraction, and publication gates. The repo publishes the method and one **site-abstracted public pattern** ([`method-appendix-worked-pattern.md`](method-appendix-worked-pattern.md)); named-site evidence and full site-level citations are held back deliberately — to preserve abstraction discipline and because named-site publication has not been authorized. What the repo shows is the method and its abstracted demonstration, not the underlying **held case material**.

## What is still open

- Specific datasets within the Tier-A / Tier-B source ladder (see [`source-strategy.md`](source-strategy.md)).
- Field-level schema, controlled vocabularies, and the exact mechanism by which assumptions reference supporting objects (see [`object-model.md`](object-model.md) for what stays conceptual in v0).
- Whether the validated `Assumption`-centered interpretive chain survives prototype pressure-testing as the load-bearing primitive of the interpretive layer.
- The final public-facing concept name and framing.
- **The representation of the commitment lifecycle** — its schema, fields, state vocabularies, object relationships, and how state, time, provenance, gaps, and re-analysis are represented. The layered direction is settled; the data structure is not.
- **Whether the observatory delivers value proportionate to its effort** — at least one material contribution not already available through existing reports, dashboards, or informed professional practice: a decision-relevant insight, meaningful time saving, coordination benefit, distinct accountability function, attributable delivery or lifecycle granularity not already common knowledge, or maintained interpretive value exceeding a one-time familiar conclusion. This is treated as an open, unproven question, to be tested before any major buildout through a **separately authorized**, narrow real-world value test with pre-committed **value criteria**. No currently authorized or in-progress work discharges this gate. A result consisting mostly of already-known conclusions plus declared gaps is a legitimate partial or negative result, not proof of value.

These will be resolved in subsequent scoped work. Until they are, the repo holds method documentation, not analyses.
