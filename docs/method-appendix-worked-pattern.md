# Method Appendix: A Worked Pattern

This appendix demonstrates the interpretive chain
(`Assumption → ImplementationSignal → ImplementationFinding → InterventionCandidate`, see
[`object-model.md`](object-model.md)) on a single real San Francisco Housing Element opportunity site.
The site is **abstracted to a pattern**: identifying details and exact figures are withheld, and the
named instance is held outside this repo (see *Provenance and checkability* below). The purpose is to
show *how the method reasons*, not to make a site-level claim.

It is one worked pattern, not a survey. It demonstrates that the chain can surface a non-obvious,
cross-surface reading that a unit-count view would miss — and it does so under the method's standing
uncertainty discipline.

## The pattern

This pattern — the **entitled-but-unadvanced high-capacity opportunity-site pattern** — has a
load-bearing finding: an **advancement gap**. A high-capacity Housing Element opportunity site holds an
**approved entitlement** and continues to read as an active pipeline contribution, yet is **operationally
un-advanced** — building permits have been filed but not issued over a multi-year horizon, and no units
are completed. The static pipeline status does not distinguish "entitled and advancing" from "entitled
and long-stalled"; the permit-and-completion record shows the latter.

A **secondary** cross-surface mismatch accompanies it: the entitled project has drifted from the adopted
inventory snapshot — it is materially larger than the adopted capacity, and its income mix diverges from
the adopted assignment. This inventory-vs-project drift is supporting texture that the same chain
surfaces; it is **not** the core finding.

The condition the pattern names: *formally alive but partially stale and operationally un-advanced* —
with the **operationally un-advanced** half load-bearing and the **partially stale** half secondary.

## The four surfaces

The method reads a single case across temporally distinct surfaces (see
[`methodology.md`](methodology.md) §Surface-specific interpretation). Each draws on a class of public
source; no surface alone is sufficient.

| Surface | Public source class | What it shows here (abstracted) |
|---|---|---|
| Adopted inventory assumption | Housing Element site inventory | a high-capacity site with an adopted capacity and income-tier assignment |
| Current project | development pipeline | an approved project materially larger than the adopted figure, with an affordability mix that diverges from the adopted income-tier assignment |
| Permit advancement | building-permit records | new-construction permits filed together several years ago; none subsequently issued; no construction-document date |
| Completion | housing-production records | no completed units recorded |

## Consistency matrix

The basic visible form (see [`methodology.md`](methodology.md) §Living Implementation Consistency
matrix). Row vocabulary: `confirmed / weakened / contradicted / unresolved / not yet testable`.

| Document claim (adopted) | Supporting evidence | Weakening / contradicting evidence | Assessment |
|---|---|---|---|
| The adopted capacity is realistic | the current entitled project is at least as large as the adopted figure | — | **confirmed** (the adopted figure is, if anything, conservative) |
| The adopted income-tier assignment reflects the site's likely delivered mix | — | the current project's affordability mix diverges from the adopted income-tier assignment | **weakened** |
| The inventory listing rests on a current entitlement | an approved entitlement exists | the public record carries an ambiguity about the entitlement's current status | **unresolved / weakened** |
| The pipeline status implies the capacity is advancing toward delivery | building-permit applications exist | the permits were filed years ago and remain un-issued, with no construction-document date | **weakened** (bounded-absence signal) |
| The site contributes deliverable units within the cycle | an active entitled project | no completed units; multi-year permit stall | **not yet testable / weakened** |

The finding-level reading is **composite** and is deliberately not collapsed to a single value (see
[`object-model.md`](object-model.md) §Three-layer assessment treatment).

## Signals (abstracted)

Each signal is source-anchored and assumption-anchored, typed and directional, and in the real run
carries confidence and known/inferred/missing status (see [`data-dictionary.md`](data-dictionary.md)).

- **Project-larger-than-adopted** (pipeline-class) — *supports/exceeds* the capacity-magnitude assumption.
- **Income-mix divergence** (pipeline / administrative) — *weakens* the income-tier assumption: the
  current project's affordability mix diverges from the adopted assignment.
- **Entitlement-status ambiguity** (administrative) — *uncertain / weakens*: an approved entitlement
  whose current status carries an ambiguity in the public record.
- **Bounded absence of permit issuance** (permit-class) — *weakens* the advancement assumption. The
  signal is a *bounded* absence, not absence in the abstract: it names the source searched
  (building-permit records at the site), the scope (new-construction permits), the horizon (from filing
  to the present, a multi-year span), and the expected-but-absent downstream record (permit issuance /
  construction-document date). Bounding parameters are part of the signal.
- **No completion** (production-class) — *weakens / not-yet-testable*: absence from completion records,
  a well-bounded absence.

## Finding

**Composite.** The adopted inventory entry appears **formally alive but partially stale and operationally
un-advanced** — the *operationally un-advanced* reading load-bearing. The core finding is that
*advancement* and *delivery* are **weakened**: the entitlement is approved and the site reads as active
pipeline, yet permits were filed years ago and remain un-issued and nothing is completed. The
*entitlement* itself carries a public-record status ambiguity that compounds this.

Two **secondary** mismatches ride alongside, surfaced by the same chain but not the headline: capacity
*magnitude* is supported (the entitled project is in fact larger than the adopted figure), and the
*income-tier* assignment has drifted from the current project's affordability mix.

The non-obvious value: a progress-report or pipeline-status view would carry this site as so many active
adopted units. The chain shows that the units are, in fact, at least one un-issued building permit and
several years from any completion signal — the site reads as *over-ready* relative to its own permit
record. (Secondarily, the inventory's unit count and income mix no longer match the current entitled
project.)

This is an interpretation under uncertainty, framed as implementation sensitivity. It is **not** a
determination that the site will or will not deliver, that the inventory is unreliable, or that any
party is at fault.

## Intervention candidates (surfaced, not recommended)

Non-prescriptive, actor-typed, basis-cited (see [`data-dictionary.md`](data-dictionary.md)). "Candidate,"
"possible," "may."

- **City / inventory-maintenance.** *Possible candidate:* refresh the site's inventory attributes (unit
  count and income-tier split) to reflect the current entitled project, so progress accounting matches
  the project on record rather than the older inventory snapshot.
- **City + project sponsor.** *Possible candidate:* a status check on what is gating permit issuance
  (entitlement-status questions, financing, phasing) would clarify whether the capacity should be
  treated as near-term or longer-horizon.
- **Monitoring.** *Candidate:* track permit issuance as a leading delivery indicator rather than relying
  on a static pipeline flag.

## Uncertainty and limits

- The entitlement-record ambiguity is flagged, not resolved.
- The **cause** of the multi-year permit stall is **not diagnosed** — financing, market conditions,
  phasing, and entitlement-status questions all remain open. The method surfaces the bounded
  absence; it does not assert its cause.
- The inventory snapshot predates the current project state, so the unit/income divergence is assumption
  *staleness over time*, not error.
- This pattern draws only on core public-record sources; conditions such as infrastructure, financing,
  and market feasibility would require additional source classes not used here.

## Provenance and checkability

The real run from which this pattern is drawn followed the method's provenance discipline: every signal
cited its source, retrieval date, and location within the source; the bounded-absence signal cited its
bounding parameters. The source classes were the San Francisco Housing Element site inventory, the city
development pipeline, building-permit records, and housing-production records.

This appendix **abstracts the figures and withholds identifying detail** to prevent re-identification of
the parcel. As a result, the text here is a **demonstration of the method's reasoning, not an
independently re-runnable artifact** — the full site-level citations are not reproduced. They are held
operator-side.

> This generalized pattern is derived from a real, fully sourced San Francisco case reviewed for internal
> planning-validity. Identifying details and full site-level citations are held operator-side because
> named-site publication has not been authorized.

## What this demonstrates

This appendix is the concrete illustration of the chain that [`methodology.md`](methodology.md),
[`object-model.md`](object-model.md), and [`data-dictionary.md`](data-dictionary.md) describe: the
four-surface reading, the consistency matrix, the bounded-absence signal, the three-layer assessment, and
the composite finding — exercised once, on a real site, under uncertainty discipline. One worked pattern;
not a general proof.
