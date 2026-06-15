# Carried-Forward Screening: A Negative Result

This note records a small, aggregate analysis run with this project's method, and reports its result — which was a *negative* one. It is included to show the [finding discipline](methodology.md#finding-discipline-completeness-screening-and-reliance) in practice, on a real question, using only public data.

## Purpose

A recurring question about a housing-element opportunity-site inventory is whether **carried-forward sites** — sites counted again in a later cycle after appearing in a prior one — are systematically *less* likely to be realized than sites identified fresh. If they were, that would be a meaningful implementation signal: capacity carried on paper while its delivery quietly erodes.

This note reports a screening test of that question, and what the test did and did not establish.

## Method boundary

The test was **classifier-first, not aggregate-first**. Each site was classified on its own evidence *before* any cohort comparison, and the carried-forward cohort was compared against a **fresh-site baseline** drawn from the same inventory and capacity range. Without that baseline, a count of "stalled" carried-forward sites would have no comparator and could be made to imply a trend that the data does not support.

Two boundaries from the method govern what this test can claim:

- **Screening signals are not findings.** A population-scale classification produces *provisional screening signals*, useful for testing whether a pattern exists and for prioritizing attention. They are not site-level findings.
- **A named-site finding would require per-site reconciliation.** Establishing that any individual site is weakening would require reconciling that site's current state across the relevant record surfaces — which a population-scale pass does not perform. No such claim is made here.

The universe was the inventory's opportunity sites at or above a minimum capacity threshold, partitioned into a carried-forward cohort and a fresh-site cohort.

## Result

**The screening did not find a defensible carried-forward drift pattern.** Classified on public data and compared against the fresh-site baseline, the screening did not support a worse-than-baseline carried-forward pattern.

This is stated narrowly and deliberately. The result is: *a classifier-first screening did not surface a defensible drift pattern.* It is **not** a positive conclusion that carried-forward sites are fine, not at risk, or certain to deliver. Individual sites may still face real implementation constraints; this test was not designed to clear them, and does not.

Site-level classifications and any prioritized follow-up list are held as operator-side working material and are not published here. Precise cohort distributions are likewise held; this note is centered on the null result and the discipline that produced it, not on provisional numbers.

## Why a negative result is reported

A disciplined method declines claims the evidence does not support — including dramatic ones. The value of running this test and reporting its null result is that it **prevents over-narration**: it stops a handful of vivid individual cases from being assembled into a citywide "drift" story the data does not establish. Reporting the absence of a pattern is as much a contribution as reporting one would be. It is not, however, evidence that no risk exists — only that *this screening, on this evidence, did not find a population pattern*.

## Source lineage

The screening drew, at the aggregate level, on public source classes:

- Housing Element site inventory (Appendix B.4, Table A)
- SF Planning project / entitlement records
- SF development pipeline
- SF housing production / completions
- DBI building-permit records
- Assessor ownership / land-use data
- MOHCD affordable-delivery records

All records are public and retrievable. Each carries a **retrieval date**; conditions change, and a screening reflects the data as of when it was run. Consistent with the method's bounded-absence discipline, "not found in a given source under a given query on a given date" was treated as exactly that — not as evidence that something does not exist.

## Caveats

- **Screening-grade / provisional.** The site classifications underlying the cohort comparison are provisional screening signals, not findings.
- **No exhaustive off-record pass.** The screening did not run a full owner/developer and off-dataset reconciliation across every site; that reconciliation is reserved for any individual site that would be carried forward into a finding.
- **No public claim about any individual site** is made or implied by this note.
- **Build correction.** An initial query-path error in one dataset was identified and corrected before the screening result was finalized; the result reported here reflects the corrected run.
- **Null is not positive.** The absence of a defensible pattern is not a conclusion that carried-forward sites are without risk.

## See also

For the method this note exercises — completeness before findings, screening versus findings, the reliance gate, and negative/null results — see the [finding-discipline section of the methodology](methodology.md#finding-discipline-completeness-screening-and-reliance).
