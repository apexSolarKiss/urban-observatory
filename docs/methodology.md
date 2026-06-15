# Methodology

This document describes the proposed method `urban-observatory` is being developed to test, and what its method does *not* do.

The methodology is method-first and public-data-only. It is designed to produce written interpretations with explicit uncertainty, traceable provenance, and modest claims. A first site-abstracted worked pattern now demonstrates the method on one real case (see [`method-appendix-worked-pattern.md`](method-appendix-worked-pattern.md)); beyond it, no datasets, notebooks, or named-site analyses have been produced, and this document describes the method as a working hypothesis still being tested by concrete prototype work.

## Public-data only

The method uses only publicly available data — plans, environmental reviews, agendas, permit records, progress reports, capital plans, funding records, policy documents, and other artifacts that any researcher or member of the public can access. The method does not require proprietary data, scraped private sources, or vendor partnerships.

This is a deliberate architectural choice, not a starting compromise. Most of the signals relevant to interpreting urban implementation already exist publicly — they are fragmented, inconsistently updated, and difficult to synthesize, but they exist. The method's value comes from connecting and interpreting them, not from acquiring novel data.

The implication: claims the method makes can be inspected and challenged against their source. The method cites what it draws on.

## Continuous interpretation, not retrieval

The method does not retrieve documents in response to queries. It does not present dashboards of metrics. It produces *interpretations* — written analyses that synthesize across documents and time, framed with confidence levels and explicit limits.

An interpretation might say:

> Pipeline momentum on the [corridor / subarea / site set] has weakened over the [time window]. Two contributing signals: [signal A from source X], [signal B from source Y]. Adopted assumption [assumption text, from document Z] is becoming less plausible as a result. Confidence: moderate. This does not yet constitute a determination of infeasibility; it indicates rising implementation risk that warrants attention.

The form is **memo-like, not chart-like**. Charts and maps may support interpretation but do not substitute for it.

## Synthesis of fragmented documents

The method's value sits in reading across documents that no single workflow currently connects. Examples of documents whose signals are typically siloed in practice:

- planning documents (general plans, area plans, element documents)
- environmental review materials
- approval and entitlement records
- permit activity records (issued, inactive, withdrawn)
- progress and production reports
- capital improvement programs
- transit and infrastructure plans
- funding award records
- policy and program documents (rezonings, ordinances, incentive programs)
- meeting agendas and decision records

The method synthesizes signals from these sources into interpretations about specific implementation questions — for example, whether adopted opportunity-site assumptions remain plausible, whether pipeline projects are showing momentum or drift, whether infrastructure sequencing is keeping pace with housing assumptions, where financing conditions are constraining what current plans assume.

## Surface-specific interpretation

Implementation assumptions may need to be interpreted across temporally distinct surfaces. Prototype source contact against San Francisco Housing Element, APR, and pipeline material has surfaced at least four such surfaces for a single project: an **inventory snapshot** dated at Housing Element adoption; an **entitlement event** anchored to a Planning approval; a **rolling advancement** signal in building-permit activity; and a **completion or production signal** in certificate-of-occupancy and permit-closeout records.

Each surface has its own temporal grammar — snapshot, event, rolling, milestone — and a single project may produce diverging readings across them. Summary / aggregate sources may collapse these surfaces, obscuring substructure within the advancement signal or rendering inventory coverage rules indistinguishable from project condition.

Findings should preserve surface-specific evidence and avoid forcing a single direction label where surfaces diverge.

Schema treatment of these surfaces, source-by-source operativeness ranking, and controlled vocabulary for surface-specific labels remain conceptual at v0.

## Living Implementation Consistency matrix

The method's basic visible extraction form is a four-column matrix, applied per surface-relevant assumption within a single case:

| Column | Content |
|---|---|
| Document claim | The claim or commitment being tested, with source citation |
| Supporting evidence | Current evidence consistent with the claim |
| Weakening evidence | Current evidence that lowers confidence in the claim or introduces contradiction |
| Assessment | Row-level reading of the claim against the evidence |

Row-level assessment uses a working vocabulary: `confirmed / weakened / contradicted / unresolved / not yet testable`. The vocabulary is candidate-strength, not final controlled-enum doctrine.

A single case typically requires multiple rows — one per surface-relevant assumption — because the chain's surfaces (inventory snapshot, entitlement event, rolling advancement, completion; see §Surface-specific interpretation) can carry distinct assumptions whose readings diverge.

When row assessments diverge within a single case, the finding-level reading is composite. The composite is explained in prose rather than forced into a single value; this method does not commit to a controlled-enum vocabulary for finding-level composite treatment. See [`object-model.md`](object-model.md) and [`data-dictionary.md`](data-dictionary.md) for the explicit distinction between signal direction, matrix row-level assessment, and finding-level composite treatment.

Sustained absence of a record can also operate as signal evidence within the matrix when the source searched, the search scope, the time horizon, and the expected downstream record are bounded. The form is bounded absence rather than absence in the abstract; an unbounded absence is not interpretable. Provenance discipline still applies: the bounding parameters are cited along with the source.

This extraction form has been used in operator-side scratch examples and is held as a working hypothesis at the method level. It is not yet an expert-reviewed or public artifact, and prototype work may refine its shape.

## Uncertainty representation

The method represents uncertainty as a first-class property of every interpretation. The initial posture is approximately **70% qualitative interpretation, 30% lightweight scoring**, with strong preference for:

- categorical risk tiers (e.g., low / elevated / high implementation risk)
- directional change (e.g., weakening pipeline momentum, deteriorating feasibility, stable redevelopment probability)
- confidence ranges (low / moderate / high), with the basis of confidence named
- signal clustering (where multiple independent signals point in the same direction)

The method avoids:

- false numerical precision
- deterministic feasibility scores
- overconfident probability claims
- single-number "feasibility scores" or "risk scores" that hide the underlying signals

Quantitative scoring, where used, is **assistive, not authoritative**. A score never substitutes for the interpretive explanation that produces it.

## Source provenance discipline

Every claim the method produces should be inspectable to its source. The method treats provenance as a first-class property:

- the source document or dataset
- the retrieval date
- the relevant location within the source
- the confidence in the interpretation derived from it
- any limits or caveats the source carries

Interpretations that combine signals from multiple sources should make the combination logic visible — *which signal contributed what to which conclusion* — so that a reader or reviewer can disagree with specific components without rejecting the whole.

Outputs without provenance are not the same artifact class as outputs with provenance. The method distinguishes them.

## Finding discipline: completeness, screening, and reliance

The method holds findings to a discipline that separates what the evidence supports from what it does not, and separates private validation from public reliance.

**Completeness before findings.** A finding requires source coverage sufficient for the specific claim it makes. Before a site- or entity-level finding is issued, the current state — active applications, project identity, the relevant process records — is reconciled across the surfaces where it could appear, rather than inferred from a single query. A *bounded absence* is recorded precisely: "not found in this source, under this query, on this date." A bounded absence supports only that statement; it is not evidence that something does not exist. Promoting "not found" to "does not exist" requires reconciling the surfaces where the thing would appear if it did.

**Screening versus findings.** Population-scale classification and site-level findings are different artifact classes. A classifier run across many sites produces *provisional screening signals* — useful for prioritizing attention and for testing whether a pattern exists, but not themselves findings. A named finding requires per-site or per-entity reconciliation first. A population aggregate is not converted into a claim about an individual site without that reconciliation.

**Reliance gate.** Private method validation — an analysis checked internally, or confirmed by a domain reviewer — is not the same as public or repo-local reliance. A worked example that is published, or relied on within this repository, requires the readily available evidence for its subject to be reconciled first, not only the subset convenient to the original analysis.

**Negative and null results.** A disciplined method declines claims the evidence does not support, including dramatic ones. When a population-scale test is run and no defensible pattern emerges, that negative result is a valid contribution: it prevents over-narration — turning a few vivid cases into a trend the data does not establish — and it is reported as plainly as a positive result would be.

## Why this is not deterministic

Urban implementation systems are probabilistic. Data quality is uneven. Causality is partially observable. False precision is dangerous. Politically sensitive findings require interpretive restraint. Over-scoring reduces credibility. Premature numerical certainty freezes ontology and analysis prematurely.

The method's epistemic stance is: interpret what is currently knowable, frame it carefully, name what is uncertain, and do not pretend to know more than the evidence supports.

## What method validation would look like

A first prototype analysis, when it exists, would succeed if:

- a senior planning consultant or implementation-oriented city planner can read it and find it operationally credible — recognizing the signals, agreeing with the interpretive logic, identifying where the analysis is over- or under-reading;
- the analysis cites its sources cleanly enough that a reviewer can check any specific claim;
- the analysis represents uncertainty in a form that survives scrutiny rather than collapsing under it;
- the interpretation is useful enough to affect a real decision or workflow, not merely interesting.

A first prototype analysis would *not* succeed by:

- being comprehensive
- making confident predictions
- producing impressive visualizations
- claiming to grade or rank cities or sites
- automating planning judgment

## Limitations

The method has known limits that should be stated, not hidden:

- Public data is partial. Some signals are not publicly available; the method works only with what is.
- Interpretation depends on the documents the method has read. Documents not in the corpus do not contribute, and the method's outputs reflect the corpus's coverage.
- Document synthesis at scale is hard. The method does not claim to do it perfectly; it claims to do it more usefully than not doing it at all.
- The method does not establish legal status, regulatory compliance, environmental review conclusions, or final feasibility. Those judgments require professional and institutional processes the method does not substitute for.
- Interpretations are dated. Conditions change. An interpretation produced at time T may no longer hold at time T+N; that is the point of the *continuous* posture, but it also means any single interpretation has a useful lifespan.

## Where this method is being developed

A first site-abstracted worked pattern now demonstrates the method on one real case (see [`method-appendix-worked-pattern.md`](method-appendix-worked-pattern.md)). Beyond that published pattern, the method has been **internally exercised** operator-side against additional named public-record cases and contrast conditions; that **operator-side evidence** is **publication-gated** — held pending review, abstraction, and publication gates — and is not reproduced in this repo. The current v0 test surface is the bounded whole-city San Francisco Housing Element implementation-intelligence prototype described in [`v0-scope.md`](v0-scope.md). Until prototype work produces signal cards, findings, or a first brief more broadly, this document describes the method as a working hypothesis still being pressure-tested by concrete public-data interpretation work — one published worked pattern is a demonstration, not a settled claim.
