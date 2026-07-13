# Data Dictionary

This document is the **working data dictionary** for the conceptual objects, attributes, and patterns [`urban-observatory`](../README.md) is being developed around. It is a deeper expression of the interpretive chain named in [`object-model.md`](object-model.md) — a per-concept treatment with candidate fields, source / provenance requirements, and relationship notes — held at the conceptual level rather than as executable schema.

It is **not** a schema. It is **not** a final data model. It is a **working hypothesis**, pressure-tested in part by manual chain extraction work, and explicitly deferred from machine-validated form until further prototype work justifies the commitment.

For the chain and primitives at a higher level, see [`object-model.md`](object-model.md). For the method, see [`methodology.md`](methodology.md). For source strategy, see [`source-strategy.md`](source-strategy.md). For the first artifact's structure, see [`report-outline.md`](report-outline.md). For v0 scope, see [`v0-scope.md`](v0-scope.md).

## Purpose

This dictionary documents:

- the core interpretive objects (the chain primitives);
- supporting objects (first-class and light);
- relationship statuses;
- output classifications and direction labels that are *not* objects in v0;
- candidate signal subtypes (taxonomy at the v0 conceptual level, not final schema);
- the reported-units / APR interpretation layer's data-shape implications (reporting surfaces and the candidate crosswalk planning pattern);
- confidence and provenance attributes that cross-cut signals, findings, and signal cards.

What it does not do:

- name final controlled vocabularies for direction labels, risk tiers, confidence levels, signal types, or candidate-actor types beyond a candidate sketch;
- specify field types, cardinality rules, or required-vs-optional contracts in a machine-validatable form;
- enumerate datasets, sample data, or executable extraction logic;
- foreclose object placement decisions (notably `ReportedCategory`, which remains a reporting surface in v0 rather than a top-level object);
- specify field-level schemas of the chain primitives — these stay conceptual until source contact justifies otherwise.

## Interpretive chain overview

The validated interpretive chain for the method is:

```text
Assumption → ImplementationSignal → ImplementationFinding → InterventionCandidate
```

`Assumption` is the load-bearing interpretive primitive for v0. `ImplementationSignal` is the source-anchored interpretive observation. `ImplementationFinding` is the synthesis produced by comparing assumptions against signals. `InterventionCandidate` is a downstream, non-prescriptive option attached to findings. The chain is a working hypothesis to be pressure-tested by prototype work; see [`object-model.md`](object-model.md).

Surrounding the chain are supporting objects (`OpportunitySite`, `HousingProject`, `PolicyProgram`, `InfrastructureDependency`, `Constraint`, `Outcome`, `Source`), reusable attributes (`Confidence`, source / provenance fields), relationship statuses (`direct_match`, `nearby_or_related`, `citywide_context`, `inventory_only`), output classifications and direction labels that are not objects (`ImplementationRisk`, `FeasibilityShift`, `SiteViabilityDrift`), candidate signal subtypes (named below), and reporting surfaces (`ReportedCategory`).

## Object / concept index

| Concept | Treatment | Section |
|---|---|---|
| `Assumption` | core interpretive object | §Core interpretive primitives |
| `ImplementationSignal` | core interpretive object | §Core interpretive primitives |
| `ImplementationFinding` | core interpretive object | §Core interpretive primitives |
| `InterventionCandidate` | core (downstream, non-prescriptive) | §Core interpretive primitives |
| `OpportunitySite` | supporting object (first-class) | §Supporting primitives |
| `HousingProject` | supporting object (first-class) | §Supporting primitives |
| `Source` | supporting object (first-class, provenance anchor) | §Supporting primitives |
| `PolicyProgram` | supporting object (light) | §Supporting primitives |
| `InfrastructureDependency` | supporting object (light) | §Supporting primitives |
| `Constraint` | supporting object (light) | §Supporting primitives |
| `Outcome` | supporting object | §Supporting primitives |
| `direct_match` / `nearby_or_related` / `citywide_context` / `inventory_only` | relationship statuses | §Relationship statuses |
| `ImplementationRisk` | output classification (not object in v0) | §Output classifications and direction labels |
| `FeasibilityShift` | direction label (not object in v0) | §Output classifications and direction labels |
| `SiteViabilityDrift` | direction label (not object in v0) | §Output classifications and direction labels |
| Signal subtypes (10 candidates, see below) | candidate `ImplementationSignal` subtypes | §Candidate signal subtypes |
| `ReportedCategory` | reporting surface / attribute on `Assumption` (not top-level object in v0) | §Reported categories and the interpretation layer |
| `Confidence` | reusable attribute | §Confidence and provenance |
| `known` / `inferred` / `missing` status | reusable attribute | §Confidence and provenance |

## Core interpretive primitives

### Assumption

**Treatment:** core interpretive object. Center of the chain. Load-bearing interpretive primitive in v0 planning.

**Purpose:** capture a claim or premise embedded in a public plan, policy, inventory, program, APR, capital plan, infrastructure plan, or related document. The project tests assumptions for current plausibility under changing conditions.

**Candidate fields:**

- a unique identifier;
- the verbatim text of the assumption;
- the source document or dataset where the assumption is embedded;
- the location within that source (page, table, section, parcel reference, etc.);
- the original date of the assumption (when it was stated, not when it was inspected);
- the context (Housing Element / APR / Capital Plan / etc.);
- the relevant supporting objects this assumption references (one or more `OpportunitySite`, `HousingProject`, `PolicyProgram`, etc.);
- the attachment scale (see below).

**Attachment scale:** an `Assumption` is not necessarily tied to a single site or project. Assumptions may attach to:

- a specific site (e.g., an opportunity-site capacity assumption);
- a specific project (e.g., a project's delivery expectation);
- a typology or corridor (e.g., expected redevelopment across a class of sites);
- a program or policy (e.g., expected outcomes from a rezoning ordinance);
- an aggregate strategy (e.g., total ADU / small-infill production assumed across many parcels at once).

The ontology should not force per-site framing on aggregate strategies. A residential parcel's individual capacity assumption may be effectively zero or fractional while the aggregate strategy that includes it carries meaningful weight. The chain should be able to test assumptions at the scale they were stated.

**Source / provenance requirement:** every `Assumption` cites the source document or dataset from which it is drawn, with the location within the source identified.

**Relationship notes:** referenced by `ImplementationSignal` (signal-anchored to assumption) and `ImplementationFinding` (finding tests one or more assumptions). May reference one or more supporting objects via a `relevant_objects` association; the exact mechanism (polymorphic list, typed relations, etc.) remains operator-pending.

**What stays conceptual:** field-level schema; the `relevant_objects` reference mechanism; the controlled vocabulary for `context`; whether aggregate-attachment cases need their own object class or remain a parameter of `Assumption`.

### ImplementationSignal

**Treatment:** core interpretive object. The source-anchored interpretive observation.

**Purpose:** capture a public-data observation that bears on whether one or more assumptions remain supported, weakened, contradicted, or uncertain.

**Candidate fields:**

- a unique identifier;
- the assumption(s) the signal bears on (one or more `Assumption` references);
- the signal text (free-form description of what the signal asserts);
- the source document or dataset cited;
- the retrieval / access date;
- the relevant location within the source;
- the signal subtype (one of the candidate subtypes; see §Candidate signal subtypes);
- the direction of the signal relative to the assumption: `supports`, `weakens`, `contradicted`, or `uncertain`;
- confidence (see §Confidence and provenance);
- known / inferred / missing status of the underlying fields.

**Signal aggregation policy:** multiple similar raw records may be summarized as one `ImplementationSignal` where they support the same interpretation about the same assumption — for example, a series of related permit records that collectively bear on a single assumption can be summarized as one signal rather than recorded as many separate signals. The summary signal cites the underlying records. The choice between per-record signals and summary signals is operational and depends on whether the underlying records carry distinct interpretive force.

**A row in a database is not a signal.** The interpretation that the row's content weakens or supports a specific assumption is the signal. The interpretive step is real and load-bearing.

**Bounded absence of a record can also count as signal evidence**, when the source searched, the search scope, the time horizon, and the expected downstream record are explicitly defined. For example, a sustained absence of any DBI permit activity on a parcel over a defined horizon — anchored to a Pipeline approval date and to a specific downstream-record expectation such as a building permit application — is an interpretable signal about whether an approved entitlement is advancing. The signal is bounded absence, not absence in the abstract; an unbounded absence is not interpretable. Provenance discipline still applies: the bounding parameters must be cited along with the source.

**Source / provenance requirement:** every signal cites a retrievable public source with retrieval date. Outputs without provenance are not the same artifact class as outputs with provenance (see [`methodology.md`](methodology.md)).

**Relationship notes:** anchored to one or more `Assumption` records. Synthesized into `ImplementationFinding` records. May reference supporting objects via the same `relevant_objects` mechanism used by `Assumption`.

**What stays conceptual:** field-level schema; direction-label final vocabulary; aggregation policy (whether summary signals get their own record class or remain a `summary` flag on a signal); cross-signal clustering as a higher-level pattern.

### ImplementationFinding

**Treatment:** core interpretive object. The primary interpretive artifact.

**Purpose:** the interpretive synthesis produced by comparing one or more assumptions against implementation signals. A finding is what the project publishes; everything upstream (assumptions, signals, supporting objects) is the apparatus that produces the finding.

**Candidate structure** (mirrored from [`object-model.md`](object-model.md)):

```text
Assumption being tested:
Relevant object(s):
Observed signals:
Interpretation:
Direction: supports / weakens / contradicted / uncertain
Confidence: low / medium / high (with basis)
Possible intervention candidates:
Sources:
```

**Three-layer assessment treatment:** the method operates with three distinct assessment layers; they are deliberately not collapsed:

- *Signal-level direction.* The direction of an `ImplementationSignal` relative to the assumption it anchors to (the signal-level field listed in §ImplementationSignal candidate fields above). Working vocabulary: `supports` / `weakens` / `contradicts` / `uncertain`.
- *Matrix row-level assessment.* The reading of one document-claim row against its supporting and weakening evidence within the Living Implementation Consistency matrix (see [`methodology.md`](methodology.md)). Working vocabulary: `confirmed` / `weakened` / `contradicted` / `unresolved` / `not yet testable`.
- *Finding-level composite treatment.* When the row assessments within a finding diverge, the finding-level reading is composite. The composite is explained in the finding's interpretation prose rather than forced into a single controlled value. No controlled enum is committed for finding-level composite treatment.

Manual chain extraction has surfaced cases where a single direction value does not capture the implementation condition cleanly — for example, an entitled-but-not-advancing case where row assessments diverge across the surface-specific readings of inventory snapshot, entitlement event, rolling advancement, and completion. The row-level vocabulary has held across operator-side scratch extractions but is not yet expert-reviewed. Final controlled vocabularies remain deferred to later prototype work.

**Cross-cutting findings:** some findings are not about a single assumption but about a pattern across many (e.g., a typology-level drift pattern). These are aggregate findings that reference multiple constituent findings; the mechanism (cross-cutting object class vs attribute on `ImplementationFinding` vs narrative-only) remains operator-pending.

**Source / provenance requirement:** a finding cites both the assumption's source and the constituent signals' sources. Public phrasing follows evidence-supported implementation-sensitivity language, not failure language (see [`methodology.md`](methodology.md)).

**Relationship notes:** synthesized from `Assumption` + `ImplementationSignal` records. May surface zero or more `InterventionCandidate` records. Carries an `ImplementationRisk` classification.

**What stays conceptual:** final direction vocabulary; cross-cutting / aggregate finding mechanism; whether findings can themselves chain (a finding citing other findings as evidence).

### InterventionCandidate

**Treatment:** core, downstream, non-prescriptive. Attached to findings as an option set.

**Purpose:** a downstream, non-prescriptive option that could plausibly change the trajectory of a weakened or contradicted assumption. Candidates are surfaced, not endorsed.

**Candidate fields:**

- a unique identifier;
- the finding(s) the candidate is attached to (one or more);
- the candidate text (free-form description of the option);
- the actor type the candidate is addressed to (one of: city / county / state / regional / private / hybrid; controlled vocabulary candidate, not final);
- the evidence basis (free-form reference to the analogous prior interventions, named policy programs, or conceptual basis for surfacing the option);
- confidence;
- dependencies on other interventions, infrastructure, or policy actions.

**Discipline:**

- vocabulary: "candidate," not "recommendation";
- plural where possible: surface multiple candidates per finding to signal the project is mapping the action space, not choosing inside it;
- conditional language: "if [actor type] wanted to address [the weakened assumption], possible candidate interventions include…" rather than "[actor] should do X";
- actor-typed: candidates carry an actor-type tag so they read to their potential audience without becoming a directive *to* that audience;
- basis-cited: candidates do not appear without basis (analogous prior interventions, named policy programs, or conceptual options).

**Source / provenance requirement:** tied to a finding; cites the same provenance chain as the finding it attaches to.

**Relationship notes:** attached to one or more `ImplementationFinding` records. May reference `PolicyProgram` records (where the candidate cites an analogous program).

**What stays conceptual:** the cross-finding mechanism (whether a candidate can reference multiple findings as one object or only one finding at a time); the actor-type vocabulary final set.

## Supporting primitives

### OpportunitySite

**Treatment:** supporting object (first-class).

**Purpose:** a Housing Element opportunity site. The anchor object for the citywide signal-card pass.

**Candidate fields:**

- a unique identifier (typically Block / Lot);
- address;
- parcel reference (BLKLOT, mapblklot);
- Housing Element capacity assumption (planned unit count, planning typology);
- current use / existing condition;
- ownership type (where available);
- supervisor district / planning district / neighborhood;
- environmental and infrastructure flags (where available).

**Relationship to `HousingProject`:** linkable via relationship statuses (`direct_match`, `nearby_or_related`, `citywide_context`, `inventory_only`). See §Relationship statuses.

**Source / provenance requirement:** every populated field cites the source (typically Housing Element site inventory + parcel / assessor GIS overlay).

**Relationship notes:** anchor for `Assumption` records about per-site or aggregate capacity. Referenced by `ImplementationSignal` records (permit, pipeline, market, infrastructure, environmental, current-use, participatory). Carries an `ImplementationRisk` classification at the signal-card level.

**What stays conceptual:** field-level schema; the typology list (categories of opportunity sites are not hard-coded before reviewing the actual inventory).

### HousingProject

**Treatment:** supporting object (first-class).

**Purpose:** a project in the citywide housing pipeline. Separate from `OpportunitySite`, linkable via relationship statuses.

**Candidate fields:**

- a unique identifier (e.g., planning case number);
- address;
- parcel reference (BLKLOT);
- project name;
- current status;
- proposed unit count;
- affordable unit breakdown;
- entitlement and permit dates;
- planning district / supervisorial district.

**Relationship to `OpportunitySite`:** linkable via relationship statuses. A `HousingProject` not on an HE inventory site can still be a `citywide_context` signal source.

**Source / provenance requirement:** every populated field cites the source (typically SF Development Pipeline, Planning applications, DBI permits, Housing Production datasets per [`source-strategy.md`](source-strategy.md)).

**Relationship notes:** referenced by `ImplementationSignal` records about project-level activity. Pipeline status is itself a signal class.

**What stays conceptual:** field-level schema; the controlled vocabulary for status values.

### Source

**Treatment:** supporting object (first-class). Provenance anchor.

**Purpose:** a public document or dataset cited as provenance. First-class so that every signal, finding, and signal-card claim can be inspected to its source.

**Candidate fields:**

- a unique identifier;
- name (human-readable);
- owner (agency or publisher);
- URL or path;
- retrieval / access date;
- tier (A / B / C per [`source-strategy.md`](source-strategy.md));
- notes (caveats, data-quality notes).

**Source / provenance requirement:** the `Source` object *is* the provenance discipline. Every other object that makes a claim cites one or more `Source` records.

**Relationship notes:** referenced by `Assumption` (the source of the assumption), `ImplementationSignal` (the source of the signal), `ImplementationFinding` (cumulative source citations), `InterventionCandidate` (where the candidate cites analogous programs or prior interventions).

**What stays conceptual:** controlled vocabulary for `tier` (A / B / C is the working set per [`source-strategy.md`](source-strategy.md)); the cataloging mechanism (whether `Source` records live in their own file or are referenced inline).

### PolicyProgram

**Treatment:** supporting object (light). Minimal v0 detail.

**Purpose:** a city or state policy or program relevant to Housing Element implementation (rezoning, adaptive-reuse ordinance, financing program, affordability incentive, etc.).

**Candidate fields:**

- a unique identifier;
- program name;
- jurisdiction;
- brief description;
- relevance flag or tag.

**Source / provenance requirement:** cites the ordinance, program documentation, or policy decision record.

**What stays conceptual:** deeper modeling of program structure, eligibility rules, funding mechanism, etc. — these are deferred. v0 carries program references as anchors, not as full program models.

### InfrastructureDependency

**Treatment:** supporting object (light). Minimal v0 detail.

**Purpose:** an upstream constraint (utility, transit, sewer, capital sequencing) that affects what an `OpportunitySite` or `HousingProject` can deliver.

**Candidate fields:**

- a unique identifier;
- type (utility / transit / sewer / etc.);
- brief description;
- reference (capital plan, transportation plan, infrastructure-capacity document).

**What stays conceptual:** deeper modeling of capacity, sequencing, and timing — these are second-pilot-phase work. v0 carries dependency references as anchors.

### Constraint

**Treatment:** supporting object (light). **Not** the core primitive (per [`object-model.md`](object-model.md) cautions).

**Purpose:** a regulatory, environmental, or policy constraint on a site or project.

**Candidate fields:**

- a unique identifier;
- type (regulatory / environmental / policy);
- brief description;
- reference.

**What stays conceptual:** deeper modeling. Per the cautions in [`object-model.md`](object-model.md): do not make `Constraint` the core primitive — the project risks becoming a static constraint inventory rather than a continuously-interpretive system.

### Outcome

**Treatment:** supporting object.

**Purpose:** observed outcomes (delivered units, withdrawn projects, abandoned entitlements). Counted at the completion milestone.

**Candidate fields:**

- a unique identifier;
- type (units delivered / project withdrawn / entitlement abandoned / etc.);
- count or extent;
- date observed;
- related `OpportunitySite` or `HousingProject`;
- source.

**Source / provenance requirement:** cites the production dataset, status change record, or other observation source.

## Relationship statuses

`OpportunitySite` and `HousingProject` are separate but linkable. The relationship between them can be:

- **`direct_match`** — a `HousingProject` is clearly on a Housing Element opportunity site (same parcel).
- **`nearby_or_related`** — a project is near or within the planning area of an opportunity site, but not at the same parcel.
- **`citywide_context`** — a project is not tied to an opportunity site but helps interpret broader pipeline / delivery conditions.
- **`inventory_only`** — a Housing Element opportunity site is present in the inventory but has no matched `HousingProject`. The site exists as an assumption surface; no project signal has yet materialized.

**Caveat:** `nearby_or_related` requires a spatial-proximity method (e.g., parcel-buffer overlay) that v0 has not yet exercised. The status name is preserved as a working slot; the method to populate it remains operator-pending.

The four-status split protects against several failure modes: ignoring citywide pipeline reality, forcing false project-to-site matches, collapsing the method into parcel feasibility, and treating an unmatched inventory site as either silently absent or as having an implicit project relationship it does not have.

## Output classifications and direction labels (not objects in v0)

The following appear in the method's vocabulary but are **not** top-level objects in v0:

### ImplementationRisk

**Treatment:** output classification / classification field. Attached to an `ImplementationFinding` or to a signal card; combines direction, confidence, and structural conditions into a quick-scan tier.

**Candidate vocabulary:** working tier values exist in repo-level prose (e.g., low / elevated / high / uncertain). The final controlled vocabulary remains deferred.

**Why not its own object:** would duplicate `ImplementationFinding`'s direction and confidence fields.

### FeasibilityShift

**Treatment:** direction label. Describes change over time in feasibility at the aggregate, typology, or corridor level.

**Why not its own object:** longitudinal change over time is captured as a finding-direction descriptor in v0's snapshot framing. A future longitudinal phase may justify graduating it to an object class.

### SiteViabilityDrift

**Treatment:** direction label. Describes per-site, per-assumption drift over time.

**Why not its own object:** same as `FeasibilityShift`.

Promoting any of these three to objects would duplicate the chain's direction and confidence fields and would prematurely add overlapping "direction-of-change" classes. They are useful project vocabulary, not separate schema entities in v0.

## Candidate signal subtypes

`ImplementationSignal` subtypes are operationally useful for categorizing signals but are **candidate taxonomy, not final schema doctrine in v0**. The working set, surfaced by grounding-note context and by manual chain extraction:

- **`AdministrativeSignal`** — pipeline / planning / case-management activity.
- **`PermitSignal`** — building-permit activity.
- **`PipelineSignal`** — project-status changes.
- **`MarketSignal`** — market-level indicators.
- **`InfrastructureSignal`** — capital plan or infrastructure-capacity signals.
- **`EnvironmentalSignal`** — environmental review or constraint signals.
- **`ParticipatorySignal`** — public-input signals; **reserved by default in v0**.
- **`EnforcementPromptedSignal`** — permits or activity prompted by enforcement actions rather than voluntary market activity.
- **`CurrentUseSignal`** — signals about the current operating use of a property (e.g., active commercial tenancy at a site flagged for residential redevelopment).
- **`ProgrammaticTemporalSignal`** — signals about the implementation environment rather than the site (e.g., long approval cycles, citywide entitlement-stage stalls).

These subtypes may consolidate, split, or be renamed as further prototype work accumulates.

**`ParticipatorySignal` posture:** participatory input is a first-class implementation signal layer at the source-of-intent level, but is **reserved by default for v0**. Use only where public input bears directly on implementation assumptions, with explicit provenance, recurrence, representativeness caveats, confidence, and reviewer notes. Avoid sentiment framing.

## Reported categories and the interpretation layer

APR / pipeline / production reporting defines counts, categories, statuses, and milestones. Urban Observatory adds an interpretation layer over the implementation assumptions behind reported categories. The two layers complement each other; they are not redundant.

### ReportedCategory (reporting surface)

**Treatment:** reporting surface / attribute on `Assumption`. **Not a top-level object in v0.**

**Purpose:** a reporting-side concept (e.g., "Authorized Units," "Pipeline Units," "HE opportunity-site capacity," "Major Multiphase Projects"). A reported category is a surface from which assumptions can be extracted or inferred. Treating it as an attribute on `Assumption` (i.e., "this assumption is associated with reported category X") is the lightweight pattern.

**Why not its own object in v0:** the lightweight attribute pattern has been pressure-tested in operator-side scratch examples and is held as the v0 working pattern. Promoting `ReportedCategory` to a top-level object would require schema commitments about its fields, vocabulary, and relationships that the lightweight pattern does not yet need. The placement decision can be revisited if future cases break the lightweight pattern; v0 retains it as the working approach.

**What stays conceptual:** the final placement (object class / attribute / surface concept), the controlled vocabulary for category names, and the mechanism by which `Assumption` references `ReportedCategory`.

### Candidate reported-units crosswalk planning pattern

For documenting a reported category and the assumptions behind it, the following candidate planning pattern can be used:

```text
Reported category:
Counting rule:
Source:
Explicit assumption:
Implied implementation assumption (analyst-defined):
Signals needed to test it:
Possible interpretation:
Confidence:
```

This is a candidate planning pattern, not a final schema. The first six rows map cleanly to fields and definitions present in source datasets and HCD forms. The "Implied implementation assumption" row is **analyst-defined** and is *not* attributed to the city or to HCD — Urban Observatory's role is to articulate what an implementation reading of the reported category would test, then to look for the signals.

## Confidence and provenance

Confidence and provenance are reusable attributes that cross-cut `ImplementationSignal`, `ImplementationFinding`, signal cards, and (where applicable) supporting objects.

### Confidence

**Treatment:** reusable attribute. Not an object.

**Candidate vocabulary:** `low` / `medium` / `high`. Final vocabulary remains deferred.

**Every confidence value carries a basis-of-confidence prose field** explaining what the level is grounded in (signal redundancy, source authority, freshness, internal consistency, etc.). The basis-of-confidence taxonomy itself is conceptual; v0 documents it as free-form prose rather than enumerating final basis values.

### Known / inferred / missing status

**Treatment:** reusable attribute. Per-field status.

**Candidate vocabulary:** `known` / `inferred` / `missing` / `uncertain`.

Applied to populated fields where the source confidence is variable (e.g., a signal card field that is directly sourced is `known`; a field reconstructed from related signals is `inferred`; a field with no usable source is `missing`).

### Provenance discipline

Per [`methodology.md`](methodology.md) and [`source-strategy.md`](source-strategy.md), every claim the method produces should be inspectable to its source. Each source contributing to a signal, finding, or signal-card field is recorded with:

- the source document or dataset;
- the retrieval date;
- the relevant location within the source;
- the confidence in the interpretation derived from it;
- any limits or caveats the source carries.

Outputs without provenance are not the same artifact class as outputs with provenance.

## What stays conceptual

The following remain conceptual in v0; the dictionary names them as candidate but does not commit:

1. Field-level schema of `Assumption` and `ImplementationSignal` (the `relevant_objects` mechanism, in particular).
2. The exact mechanism by which assumptions reference supporting objects (polymorphic list vs typed relations).
3. Controlled vocabularies (direction labels, risk tiers, confidence levels, signal types, finding directions, candidate actor types).
4. Typology list for opportunity sites (categories not hard-coded before reviewing the actual inventory).
5. Specific datasets within the Tier-A / Tier-B source ladder (see [`source-strategy.md`](source-strategy.md)).
6. Cross-cutting finding and intervention-candidate mechanisms.
7. Pattern summary representation (as object class vs as brief section).
8. Confidence basis taxonomy.
9. APR-augmentation companion mechanism (how findings relate structurally to APR sections).
10. `ReportedCategory` placement (object / attribute / surface concept).
11. Spatial-proximity method for `nearby_or_related` relationship status.
12. Whether aggregate-attachment cases need their own object class or remain a parameter of `Assumption`.

If prototype work surfaces substantial revisions to several of these, the right response is to slim the data dictionary down to the chain plus supporting primitives only and accept that source-data pressure has done its job.

## Posture

This data dictionary is a working hypothesis. It is Markdown-first by design — executable schema (YAML, JSON), data files, notebooks, and reports are deferred to later phases that depend on what prototype work reveals.

Per-concept fields are described in prose, not in a code-shaped contract. Candidate vocabularies are named as candidates. The discipline is to make the conceptual model legible to contributors and reviewers, not to bind tooling to it.

Field-level commitments, controlled-vocabulary finalizations, and machine-validatable schemas all wait until prototype work justifies the commitment.

For this apparatus exercised on a single site-abstracted case — the chain, the matrix, the bounded-absence signal, and the three-layer assessment in one worked pattern — see [`method-appendix-worked-pattern.md`](method-appendix-worked-pattern.md).
