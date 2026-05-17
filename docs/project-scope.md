# Project Scope

`urban-observatory` is an open-source prototype exploring **implementation intelligence**: methods for continuously interpreting whether public plans, policies, infrastructure commitments, and capital investments are actually translating into urban outcomes — and what would most effectively close the gap when they aren't.

This document defines what the project is, what it is not, and how its scope is sequenced.

## What this project is

`urban-observatory` is method-first. It is being developed to test:

- **continuous interpretation** of public-data signals about urban implementation reality;
- **synthesis of fragmented documents** (plans, environmental reviews, agendas, permits, progress reports, capital plans, policy documents, funding records) into coherent interpretations;
- **detection of contradictions** between what one document assumes and what another (or on-the-ground evidence) actually shows;
- **tracking of implementation drift** — the gap between planning assumptions and current conditions, over time;
- a **memo-like + schema-backed artifact posture** for outputs, with explicit uncertainty, categorical risk tiers, and source provenance;
- a **candidate ontology** for representing the entities involved (sites, projects, infrastructure dependencies, policy programs, market signals, implementation risks, feasibility shifts, intervention candidates).

The project's intended outputs are written analyses. It is not intended to produce dashboards, decisions, predictions, or compliance determinations.

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

It interprets implementation conditions with explicit uncertainty. Its outputs are advisory, not authoritative.

## In scope (now)

- Implementation-intelligence as a method.
- Public-data-only synthesis discipline.
- Candidate ontology for the entities the method reasons over.
- Uncertainty representation (approximately 70% qualitative interpretation / 30% lightweight scoring; categorical tiers; confidence ranges; directional change).
- Source-provenance discipline (every claim cites a public source, retrieval date, and confidence level).
- Methodology documentation for how synthesis works.

## First operational domain

The first operational domain is **housing implementation**, specifically the post-adoption interpretation question California's 7th-cycle Housing Element environment puts on cities: are adopted assumptions about opportunity sites, production pipelines, infrastructure dependencies, and funding still plausible as conditions change?

**Housing is a first domain, not the project's identity.** Other domains — capital improvement programs, transportation–housing coordination, climate-adaptation implementation, infrastructure sequencing — may follow once the method is credible in housing.

### Current v0 direction (scoped recommendation, not doctrine)

The current scoped v0 direction for this first domain is **APR augmentation + opportunity-site implementation stress testing** — interpreting whether adopted Housing Element opportunity sites and pipeline assumptions remain plausible as conditions change, framed as an augmentation of the existing Annual Progress Reporting workflow rather than a replacement of it, a compliance check, or a grading system.

This is the **current best-scoped direction**, not immutable doctrine. The exact implementation surface — which specific sites, which corridor or subarea, which datasets, which interpretations — remains an open decision that subsequent scoped work will refine.

APR augmentation here means *adding implementation interpretation* to an existing reporting workflow — making the question of whether adopted assumptions still hold visible in a form planners and consultants can act on. It does not mean producing the APR itself, replacing it, or determining its compliance status.

## Deferred / out of scope for now

The following are intentionally deferred until subsequent scoping decisions are made and validated:

- **Specific case-study selection.** No city, corridor, subarea, or site is currently canonical.
- **Specific dataset selection.** Candidate first-corpus categories appear in the methodology document; specific source choices await initial scoping work.
- **Schema files, sample data, analysis notebooks, and report artifacts.** These are **candidate later phases, not guaranteed deliverables.** They depend on resolving a set of preceding scoping decisions (specific implementation surface, geography, dataset, and computed interpretations) that have not been made and that the prototype work itself will inform.
- **Application UI, maps, dashboards, public query interfaces.**
- **AI extraction / ingestion pipelines** beyond what's needed for a first prototype analysis.
- **Any commitment to a specific load-bearing ontology primitive** (`intervention`, `implementation`, `site`, `constraint`, `outcome` — all remain credible candidates).

## Where this comes from

External context (intent, audience, philosophy, foundational premises, unresolved questions, voice discipline) lives in the project's grounding note, which is operator-side and not in this repo. The repo itself is the operative source of truth for what the project actually is and does. See [`docs/architecture.md`](architecture.md) for repo-local boundaries and [`AGENTS.md`](../AGENTS.md) for workflow rules.

## What is still open

- Which specific implementation surface (which sites, which corridor, which subarea) a first prototype interprets.
- Which specific public-data sources are included in the first corpus.
- Which specific interpretations a first prototype produces (site viability drift / pipeline fragility / entitlement-to-delivery risk / assumption stress test / constraint exposure / intervention candidates).
- Which load-bearing ontology primitive(s) the prototype demonstrates as most useful.
- The final public name and framing.

These will be resolved in subsequent scoped work. Until they are, the repo holds method documentation, not analyses.
