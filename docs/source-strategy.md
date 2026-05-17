# Source Strategy

This document describes the public-data source posture for `urban-observatory`'s v0 work. It is prioritized but open-ended: it names source tiers and reliability considerations, not specific canonical datasets.

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

## Tier A — core v0 source categories

Tier A sources are the categories v0 attempts first. The Housing Element inventory and APR are the natural starting points; pipeline, planning applications, and DBI permits follow. Tier A categories include:

- San Francisco Housing Element site inventory and opportunity-site data
- San Francisco APR / Housing Element annual progress reporting data
- SF Planning development pipeline data
- SF Planning applications and entitlement records
- DBI building permit records
- Planning Code and zoning GIS layers
- Parcel, assessor, and land-use GIS layers

Specific datasets within each category are not named here as v0-canonical. Dataset selection within these categories is part of the prototype's own work and depends on what is available, current, and reliable.

## Tier B — implementation-condition source categories

Tier B sources illuminate the conditions under which implementation occurs. They are selective: not every Tier B category is required for v0, but several are likely needed for Tier-2 deeper interpretation of flagged sites.

Tier B categories include:

- capital plan and infrastructure investment references
- transportation plans and transit access layers
- affordable housing project and funding signals
- public subsidy and financing award signals
- environmental constraint layers
- construction cost, interest rate, and vacancy indicators
- policy and program documents related to Housing Element implementation

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

## Posture

The source strategy is a posture, not a manifest. New sources may emerge during prototype work, and some named categories may turn out to be less useful than expected. The category-level naming is durable; specific dataset choices remain candidate.

No data is fetched as part of this document; retrieval is a separate, later phase.
