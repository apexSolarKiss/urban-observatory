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

An `Assumption` is not necessarily tied to a single site or project. Manual chain extraction has pressure-tested the per-site framing and surfaced that some assumptions operate at scales other than the site. Assumptions may attach to:

- a specific site (e.g., an opportunity-site capacity assumption);
- a specific project (e.g., a project's delivery expectation);
- a typology or corridor (e.g., expected redevelopment across a class of sites);
- a program or policy (e.g., expected outcomes from a rezoning ordinance);
- an aggregate strategy (e.g., total ADU / small-infill production assumed across many parcels at once).

The ontology should not force per-site framing on aggregate strategies. A residential parcel's individual capacity assumption may be effectively zero or fractional while the aggregate strategy that includes it carries meaningful weight. The chain should be able to test assumptions at the scale they were stated.

Prototype source contact has confirmed that a single interpretive case can carry per-site, per-project, and aggregate-level assumptions simultaneously; the per-scale hierarchy is operational, and collapsing to a single scale loses interpretive coherence.

### ImplementationSignal

A public-data observation that bears on whether one or more assumptions remain supported, weakened, contradicted, or uncertain. A signal is source-anchored (cites a public document or dataset), assumption-anchored (only counts as evidence about a specific assumption), directional, and typed. A row in a permit database is not a signal; the interpretation that the row's content weakens or supports a specific assumption is the signal.

**Signal aggregation.** Multiple similar raw records may be summarized as one `ImplementationSignal` where they support the same interpretation about the same assumption — for example, a series of related permit records that collectively bear on a single assumption can be summarized as one signal rather than recorded as many separate signals. Source and provenance remain inspectable: the summary signal cites the underlying records. The choice between per-record signals and summary signals is operational and depends on whether the underlying records carry distinct interpretive force. The chain does not require one signal per raw row.

**Candidate signal subtypes.** Signal subtypes are operationally useful for categorizing signals but are not final schema doctrine in v0. Candidate subtypes — surfaced by grounding-note context and by manual chain extraction — include:

- `AdministrativeSignal` — pipeline / planning / case-management activity.
- `PermitSignal` — building-permit activity.
- `PipelineSignal` — project-status changes.
- `MarketSignal` — market-level indicators.
- `InfrastructureSignal` — capital plan or infrastructure-capacity signals.
- `EnvironmentalSignal` — environmental review or constraint signals.
- `ParticipatorySignal` — public-input signals (per grounding-note v7; reserved by default in v0).
- `EnforcementPromptedSignal` — permits or activity prompted by enforcement actions rather than voluntary market activity.
- `CurrentUseSignal` — signals about the current operating use of a property (e.g., active commercial tenancy at a site flagged for residential redevelopment).
- `ProgrammaticTemporalSignal` — signals about the implementation environment rather than the site (e.g., long approval cycles, citywide entitlement-stage stalls).

These subtypes are candidates, not final schema. Prototype source contact in v0 has operated against `CurrentUseSignal` and `ProgrammaticTemporalSignal` as load-bearing subtypes; both are retained. The list as a whole remains candidate-level and may consolidate, split, or be renamed as further prototype work accumulates.

### ImplementationFinding

The interpretive synthesis produced by comparing one or more assumptions against implementation signals. A finding carries direction, confidence, possible intervention candidates, and source provenance. Findings are the project's primary interpretive artifact; the Housing Element Implementation Risk Brief is a curated presentation of findings (see [`report-outline.md`](report-outline.md)).

**Three-layer assessment treatment.** The method operates with three distinct assessment layers; they are deliberately not collapsed into a single direction value:

1. *Signal-level direction.* An `ImplementationSignal`'s direction relative to the assumption it anchors to. Working vocabulary: `supports` / `weakens` / `contradicts` / `uncertain`.
2. *Matrix row-level assessment.* The matrix row's reading of one document-claim against its supporting and weakening evidence (see the Living Implementation Consistency matrix in [`methodology.md`](methodology.md)). Working vocabulary: `confirmed` / `weakened` / `contradicted` / `unresolved` / `not yet testable`.
3. *Finding-level composite treatment.* When the row assessments within a finding diverge — including across the temporally distinct surfaces noted in [`methodology.md`](methodology.md) — the finding-level reading is composite. The composite is explained in the finding's interpretation prose rather than forced into a single controlled value.

Prototype source contact has surfaced cases where a single direction value cannot capture the implementation condition cleanly — partial support and partial weakening can coexist within one finding, and surface-specific readings can diverge across inventory snapshot, entitlement event, rolling advancement, and completion. The row-level vocabulary has held across operator-side scratch extractions but is not yet expert-reviewed; the finding-level composite treatment is held as prose, not as schema, and no controlled enum is committed for it. Final controlled vocabularies remain deferred to later prototype work.

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

`OpportunitySite` and `HousingProject` are separate but linkable. The relationship between them can be:

- `direct_match` — a `HousingProject` is clearly on a Housing Element opportunity site (same parcel).
- `nearby_or_related` — a project is near or within the planning area of an opportunity site, but not at the same parcel.
- `citywide_context` — a project is not tied to an opportunity site but helps interpret broader pipeline / delivery conditions.
- `inventory_only` — a Housing Element opportunity site is present in the inventory but has no matched `HousingProject`. The site exists as an assumption surface; no project signal has yet materialized.

The four-status split protects against several failure modes: ignoring citywide pipeline reality, forcing false project-to-site matches, collapsing the method into parcel feasibility, and treating an unmatched inventory site as either silently absent or as having an implicit project relationship it does not have.

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

This object model is a working hypothesis. Repo-local schema files and runnable schema artifacts are deferred to later phases. The chain and the supporting primitives are named here because they are method-bearing; schema-shape decisions are deferred because they are data-shape decisions.

For per-concept field-level treatment (candidate fields, source / provenance requirements, and the relationship between objects, signal subtypes, classifications, and reporting surfaces), see [`data-dictionary.md`](data-dictionary.md). For the chain exercised once, end to end, on a single site-abstracted case, see [`method-appendix-worked-pattern.md`](method-appendix-worked-pattern.md).
