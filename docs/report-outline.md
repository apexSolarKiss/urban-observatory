# Report Outline

This document describes the structure of the project's first artifact: the **Housing Element Implementation Risk Brief**, framed as a forward-looking APR-augmentation companion rather than an APR replacement.

The outline is a description, not a template. Section headings and artifact-class composition are named here so contributors and reviewers can read the intended structure; specific findings, signal cards, and pattern summaries are deferred to later phases.

For the v0 scope this artifact supports, see [`v0-scope.md`](v0-scope.md). For the method, see [`methodology.md`](methodology.md). For the object model the artifact reflects, see [`object-model.md`](object-model.md).

## Section structure

The brief is organized as follows:

1. Executive implementation finding
2. APR progress context
3. What the APR does not explain
4. Citywide Housing Element inventory signal summary
5. Pipeline fragility summary
6. Site viability drift patterns
7. Implementation assumption stress tests
8. Constraint exposure findings
9. Intervention candidates
10. APR augmentation implications
11. Uncertainty, confidence, and missing data
12. Source / provenance appendix
13. Schema / data appendix

These are section headings only. v0 may produce a partial or skeletal version of the brief; findings, specific stress tests, and constituent signal cards are deferred until prototype work is authorized.

## Artifact-class composition

The brief is not a single fixed template. It is a composition of internal artifact classes:

- **Narrative section** — interpretive prose; the brief's voice.
- **Finding card** — a structured `ImplementationFinding` rendered for human reading.
- **Signal card** — a shallow per-site or per-project baseline (Tier 1). A signal card is not itself a finding.
- **Pattern summary** — a cross-cutting interpretation across multiple findings (typology drift, pipeline fragility, and similar).
- **Source / provenance appendix** — the brief's citation backbone.
- **Schema / data appendix** — method disclosure: the chain, the working object model, and the limits.
- **Uncertainty surface** — an explicit catalogue of missing data, low-confidence findings, fields the brief could not populate, and assumptions about coverage.

The composition is named so contributors and reviewers can distinguish narrative from structured content. It is not authorized as a fixed template; prototype work may refine the composition.

## Posture

The brief is interpretive support, not enforcement, grading, prediction, or compliance determination. Public phrasing follows the discipline of evidence-supported implementation sensitivity, not failure language (see [`methodology.md`](methodology.md)).

v0 brief work is staged:

1. Private or internal methodology test.
2. Expert-reviewed version.
3. Public site-level analysis only after expert review.
4. Generalized or typology-level treatment for sensitive or low-confidence cases.

Public site-level analysis is not a v0 deliverable. The outline structure here makes the artifact's eventual shape readable; producing it is a later phase.
