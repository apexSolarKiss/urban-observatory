# Object Model

This document describes the conceptual object model `urban-observatory` is being developed around. It is a **working hypothesis**, not a schema. It names the interpretive chain and the supporting primitives the method reasons over, and explicitly defers schema-level decisions until prototype work has pressure-tested the model against real public-data conditions.

For the project's core concept, see [`implementation-intelligence.md`](implementation-intelligence.md). For methodology, see [`methodology.md`](methodology.md). For repo-local architecture context, see [`architecture.md`](architecture.md).

## Interpretive chain

The validated interpretive chain for the method is:

```text
Assumption → ImplementationSignal → ImplementationFinding → InterventionCandidate
```

This is a working hypothesis to be pressure-tested by prototype work, not final schema doctrine. The supporting primitives below remain useful regardless of which schema shape ultimately consumes the chain.

### Assumption

A claim or premise embedded in a public plan, policy, inventory, program, APR, capital plan, infrastructure plan, or related document. The project tests assumptions for current plausibility under changing conditions.

The project's core move is testing whether assumptions embedded in plans still hold under changing real-world conditions. `Assumption` is the load-bearing interpretive primitive in v0 planning.

### ImplementationSignal

A public-data observation that bears on whether one or more assumptions remain supported, weakened, contradicted, or uncertain. A signal is source-anchored (cites a public document or dataset), assumption-anchored (only counts as evidence about a specific assumption), directional, and typed. A row in a permit database is not a signal; the interpretation that the row's content weakens or supports a specific assumption is the signal.

### ImplementationFinding

The interpretive synthesis produced by comparing one or more assumptions against implementation signals. A finding carries direction, confidence, possible intervention candidates, and source provenance. Findings are the project's primary interpretive artifact; the Housing Element Implementation Risk Brief is a curated presentation of findings (see [`report-outline.md`](report-outline.md)).

### InterventionCandidate

A downstream, non-prescriptive option that could plausibly change the trajectory of a weakened or contradicted assumption. Candidates are surfaced, not endorsed. They are plural and actor-typed where possible. They are not recommendations.

## Supporting primitives

The following remain essential supporting primitives but are not the conceptual center of the method:

- `OpportunitySite` — a Housing Element opportunity site. Anchor object for the citywide signal-card pass.
- `HousingProject` — a project in the citywide pipeline. Separate from `OpportunitySite`, linkable through relationship statuses.
- `PolicyProgram` — a city or state policy or program relevant to Housing Element implementation.
- `InfrastructureDependency` — an upstream constraint that affects what a site or project can deliver.
- `MarketSignal` — a market-level indicator that bears on feasibility.
- `Constraint` — a regulatory, environmental, or policy constraint on a site or project.
- `Outcome` — an observed outcome (delivered units, withdrawn projects, abandoned entitlements).
- `Source` — a public document or dataset cited as provenance. First-class.
- `Confidence` — a reusable confidence value attached to signals, findings, and signal cards.

`OpportunitySite` and `HousingProject` are separate but linkable. The relationship between them can be `direct_match`, `nearby_or_related`, or `citywide_context`. This split protects against three failure modes: ignoring citywide pipeline reality, forcing false project-to-site matches, and collapsing the method into parcel feasibility.

## Output classifications and direction labels (not objects in v0)

The following appear in the method's vocabulary but are **not** top-level objects in v0:

- **`ImplementationRisk`** — an output classification / classification field, not an object. Attached to a finding or a signal card; combines direction, confidence, and structural conditions into a quick-scan tier. Specific terms are deferred.
- **`FeasibilityShift`** — a direction label describing change over time in feasibility at the aggregate, typology, or corridor level.
- **`SiteViabilityDrift`** — a direction label describing per-site, per-assumption drift over time.

Promoting these to objects would duplicate `ImplementationFinding`'s direction and confidence fields and would prematurely add overlapping "direction-of-change" classes. They are useful project vocabulary, not separate schema entities in v0.

## Cautions against alternative centers

The method's coherence depends on keeping `Assumption` at the center. Specifically:

- Do **not** make `Site` the core primitive — the project risks collapsing into parcel feasibility.
- Do **not** make `Intervention` the core primitive — the project risks sounding prescriptive too early.
- Do **not** make `Constraint` the core primitive — the project risks becoming a static constraint inventory rather than a continuously-interpretive system.

The core is **assumptions under changing conditions**.

## What stays conceptual in v0

The object model is a working hypothesis at the level of named primitives and the interpretive chain. The following remain conceptual until prototype work — specifically, a manual sample extraction step on a small set of opportunity sites — has tested the model against real public-data shape:

1. Field-level schema of `Assumption` and `ImplementationSignal`.
2. The exact mechanism by which assumptions reference supporting objects.
3. Controlled vocabularies (direction labels, risk tiers, confidence levels, signal types, finding directions, candidate actor types).
4. Typology list (the categories of opportunity sites are not hard-coded before reviewing the actual inventory).
5. Specific datasets within source tiers (see [`source-strategy.md`](source-strategy.md)).
6. Cross-cutting finding and intervention-candidate mechanisms.
7. Pattern summary representation (as object vs. as brief section).
8. Confidence basis taxonomy.
9. APR-augmentation companion mechanism (how findings relate structurally to APR sections).

If prototype work surfaces substantial revisions to several of these, the right response is to slim the object model down to the chain plus supporting primitives and accept that source-data pressure has done its job.

## Posture

This object model is a working hypothesis. Repo-local schema files, data dictionaries, and runnable schema artifacts are deferred to later phases. The chain and the supporting primitives are named here because they are method-bearing; schema-shape decisions are deferred because they are data-shape decisions.
