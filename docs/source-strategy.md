# Source Strategy

This document describes the public-data source posture for [`urban-observatory`](../README.md)'s v0 work. It is prioritized but open-ended: it names source tiers and reliability considerations, not specific canonical datasets.

For the broader method, see [`methodology.md`](methodology.md). For the v0 scope this source strategy supports, see [`v0-scope.md`](v0-scope.md).

## Public-data only

The project uses only publicly available data — plans, environmental reviews, agendas, permit records, progress reports, capital plans, funding records, policy documents, and other artifacts accessible to any researcher or member of the public. This is a deliberate architectural choice; see [`methodology.md`](methodology.md).

The method's value comes from connecting and interpreting public sources, not from acquiring novel data.

## Provenance discipline

Every claim the method produces should be inspectable to its source. Each source contributing to a finding or signal card is recorded with:

- the source document or dataset
- the retrieval date
- the relevant location within the source
- the confidence in the interpretation derived from it
- any limits or caveats the source carries

Outputs without provenance are not the same artifact class as outputs with provenance; see [`methodology.md`](methodology.md).

## Two tier axes — keep them distinct

This document's **source ladder** (Tier A / Tier B) is a different axis from the **analytical-depth pass** (Tier 1 / Tier 2) used in v0 scoping (see [`v0-scope.md`](v0-scope.md)). The source ladder describes *what kind of reading a source supports* — signal visibility (Tier A) versus dependency interpretation (Tier B). The depth pass describes *how far v0 interprets* — a shallow citywide baseline (Tier 1) versus deeper interpretation of flagged cases (Tier 2). A Tier-A source can be read at Tier-1 or Tier-2 depth; the two axes are independent.

## Tier A — cross-system signal visibility

Tier A is the **signal-visibility** layer: shallow, source-linked public-record signals across the systems that bear on implementation, not housing records alone. Tier A states what the record shows — *signal present / absent / unclear · source found / not found · status changed · dependency flagged · public-record silence · procedural gate visible · public-record wall* — and **implies no causation**.

Tier A is a **visibility posture, not a source-collection mandate.** It can surface signals across the bearing systems where those signals are shallowly visible in authorized public sources or already-pinned records:

- **Housing / planning** — Housing Element site inventory, APR, development pipeline, planning applications, DBI building permits, completions, zoning and parcel GIS *(the sources pinned and exercised in v0)*
- **Infrastructure** — capital plan and infrastructure-investment references
- **Transportation** — transportation plans and transit-access layers
- **Capital / funding** — affordable-housing and public funding / subsidy signals
- **Environmental / resilience** — environmental-constraint and resilience layers
- **Public / institutional** — public and institutional records

v0 operates on the housing / planning sources already pinned (see [`source-inventory.md`](source-inventory.md)); the non-housing systems are named here as the Tier-A visibility posture — surfaced where public records make them shallowly visible — not as a present collection requirement. Specific datasets within each system are not named here as v0-canonical; dataset selection is part of the prototype's own work.

## Tier B — cross-system dependency interpretation

Tier B is the **interpretation** layer, triggered when the project must read *how systems interact* or whether a dependency *materially affects* implementation: explanation, causality, delivery-risk claims, intervention priority, cross-system dependency interpretation, and higher-confidence, expert-review-facing, or public-facing claims. Tier B is **gated** — Tier-A visibility never implies a Tier-B interpretation on its own.

Tier B is a *function*, not a separate source list. It interprets deeper reads of the same public records (and, where a specific finding, claim, reviewer need, or demo concept requires it, additional sources such as capital / infrastructure references, transportation plans, funding / subsidy records, environmental-constraint layers, construction-cost / interest-rate / vacancy indicators, or policy / program documents). It is not exercised in v0 by default.

## Tier C — selective supporting source categories

Tier C sources are used selectively for Tier-2 deeper interpretation of flagged sites. They are not expected to be exhaustively retrieved in v0's Tier-1 shallow pass.

Tier C categories include:

- Board of Supervisors and Planning Commission agendas and decision records
- CEQA notices and environmental impact reports
- public comments and meeting transcripts
- code enforcement records
- ownership fragmentation analysis
- litigation and appeals data
- utility-capacity documents
- neighborhood-specific and area plans

Tier C predates the Tier-A / Tier-B visibility-versus-interpretation reframe; its placement on the revised ladder is reserved for a separate source-taxonomy review and is left unchanged here.

## Posture

The source strategy is a posture, not a manifest. New sources may emerge during prototype work, and some named categories may turn out to be less useful than expected. The category-level naming is durable; specific dataset choices remain candidate. Tier A names a visibility posture across systems, not a commitment to collect every system's data: v0 exercises the housing / planning sources, and other systems' signals enter only where public records make them shallowly visible.

No data is fetched as part of this document; retrieval is a separate, later phase.
