# Source Inventory

This document is the working source inventory for `urban-observatory`'s v0 prototype. It documents the public-data sources `urban-observatory` may draw on, the access posture for each, and the role each source plays in the interpretive chain. Specific dataset choices remain candidate; the inventory is not a manifest and not a claim of source sufficiency.

For the source-strategy posture (Tier A / B / C categories at the category level), see [`source-strategy.md`](source-strategy.md). For the interpretive chain the inventory supports, see [`object-model.md`](object-model.md). For provenance discipline, see [`methodology.md`](methodology.md). For repo-local architecture context, see [`architecture.md`](architecture.md).

## Source inventory boundary

These stages are distinct and must not be blurred:

```text
inventory       documents source candidates, access paths, provenance expectations,
                format, update posture, and limitations.  No data is pulled.

retrieval       pulls data from a documented source.  Produces raw artifacts.

extraction      transforms retrieved raw artifacts into chain entries
                (ImplementationSignal records, ImplementationFinding interpretations).
                Source-anchored, assumption-anchored.

interpretation  packages extraction into the Housing Element Implementation Risk Brief
                and related interpretive surfaces.
```

This document is the inventory stage only. An inventory entry says: "this source is reachable, structured like X, with limits Y." It does not say: "this source proves assumption Z."

Source inventory ≠ source sufficiency. Sufficiency is a finding-level question, decided per-assumption during chain extraction.

## Status markers

Controlled vocabulary for `v0_status`:

```text
pinned                  canonical URL or resource ID verified; structure inspected;
                        usable in v0 at the access level recorded
partial                 access path partially verified; some pattern works, others not yet
candidate               pinned at catalog level; not deep-probed for fields
needs verification      category real; specific source URL or resource ID not pinned
category-level only     recorded as a category without a specific source identified
deferred (Tier-2 case)  not pinned in v0 by default; revisited only for Tier-2 deeper
                        interpretation
```

## Source classification

Controlled vocabulary for `source_classification` — what a source *is* in the inventory model:

```text
raw evidence            primary source carrying the data itself
operational aggregate   curated / aggregated view over raw upstream feeds
companion source        pairs with another canonical source for a chain pair
identity anchor         provides cross-source join keys; not a signal source
enrichment layer        context layer (zoning, parcels, administrative overlays)
meta-source / discovery viewer / dashboard / catalog over raw sources
reference / lookup      controlled-vocabulary / code-lookup datasets
deferred (Tier-2 case)  category-level only; not pinned in v0
candidate               pinned at catalog level; intended classification pending deep probe
```

`source_classification` answers what a source *is*. `v0_status` answers what is verified about access to it. The two are independent fields.

## Tier A — canonical sources

Each entry below belongs to the housing / planning subset of the Tier-A **signal-visibility** posture described in [`source-strategy.md`](source-strategy.md). These seven pinned source categories are the sources exercised in v0; they do not exhaust the cross-system Tier-A posture. Specific dataset choices are working candidates, not v0-canonical doctrine. (A full re-tag of every source's `tier` field onto the revised visibility / interpretation ladder is a separate follow-on; the pinned content here is unchanged.)

### A.1 — SF Housing Element site inventory / opportunity sites

| Field | Value |
|---|---|
| `source_id` | `sf_he_appendix_b4` |
| `source_name` | Appendix B.4 Sites Inventory (SF submission) |
| `source_owner` | California HCD (template); SF Planning Department (submission) |
| `source_category` | Housing Element site inventory / opportunity sites |
| `source_classification` | raw evidence |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | `https://sfplanning.org/sites/default/files/documents/housing-for-all/Appendix_B4.xlsx` |
| `platform` | static `.xlsx` on SF Planning site |
| `access_type` | direct download |
| `format` | XLSX (HCD-standard multi-sheet template) |
| `update_frequency` | per Housing Element submission cycle |
| `coverage_period` | 2023–2031 (6th-cycle Housing Element; Dec-2022 submission) |
| `geographic_scope` | whole SF (~121,053 SF rows in Table A; 121,055 total) |
| `primary_keys` | BLKLOT (hyphenated, e.g., `3704-045`); Site Address; ZIP |
| `relevant_objects` | `OpportunitySite` (anchor); `Assumption` (per-site capacity); `Source` |
| `relevant_chain_stage` | `Assumption` |
| `reported_category_relevance` | opportunity-site capacity (structures the RHNA target); Site Status; Pipeline flag; Publicly-Owned flag; Identified-in-Prior-Cycle flag |
| `known_limitations` | Mega-Development-Agreement projects (Treasure Island, Candlestick, Parkmerced, Stonestown, Potrero Power Station, Pier 70, Mission Rock, Hope SF Sunnydale, Freedom West, 610 Brannan / Flower Mart) live in Appendix B.1, not B.4 |
| `data_quality_caveats` | Capacity is planning-stated, not delivery-verified. ~99.6% of rows are < 5-unit ADU-strategy parcels. Only ~171 sites have capacity ≥ 20; 80% of those are already Pipeline-flagged. |
| `provenance_requirements` | Cite as HCD-template Appendix B.4 (SF submission); record table name and BLKLOT; note hyphenated BLKLOT format |

### A.2 — SF APR / Housing Element annual progress reporting

| Field | Value |
|---|---|
| `source_id` | `hcd_apr_portal` |
| `source_name` | HCD Annual Progress Reports portal |
| `source_owner` | California HCD |
| `source_category` | APR / Housing Element annual progress reporting |
| `source_classification` | raw evidence |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | `https://www.hcd.ca.gov/planning-and-community-development/annual-progress-reports` |
| `platform` | HCD web portal + California Open Data Portal |
| `access_type` | landing page + downloadable raw datasets + APR Dashboard |
| `format` | CSV (raw); interactive dashboard |
| `update_frequency` | annual reporting cycle |
| `coverage_period` | 2018–present (raw datasets) |
| `geographic_scope` | statewide; SF filtered as one jurisdiction |
| `primary_keys` | Jurisdiction; Reporting Year; project-level rows in site-level tables |
| `relevant_objects` | `Assumption` (against adopted HE targets); `ImplementationSignal` (production, permits, completions); `Source`; `Confidence` |
| `relevant_chain_stage` | `Assumption` + `ImplementationSignal` |
| `reported_category_relevance` | RHNA progress — HCD's primary benchmark is issued building permits (verbatim from HCD landing) |
| `known_limitations` | Methodology is distributed across HCD APR Forms, Instructions PDF, dataset metadata, and Building Blocks guidance — not consolidated in one place |
| `data_quality_caveats` | SF most-recent APR currency requires direct verification. The "explicit counting" layer is documented; the implementation-assumption layer is `urban-observatory`'s interpretive contribution, not explicit in HCD source materials |
| `provenance_requirements` | Cite HCD APR statewide dataset (or jurisdiction-level table) with reporting year and table identifier; note retrieval date |

### A.3 — SF Planning development pipeline

| Field | Value |
|---|---|
| `source_id` | `sf_dev_pipeline_6jgi-cpb4` |
| `source_name` | San Francisco Development Pipeline |
| `source_owner` | SF Planning + SF DBI (combined); DataSF (publishing) |
| `source_category` | SF Planning development pipeline data |
| `source_classification` | operational aggregate (over raw PPTS feeds at A.4 and raw PTS feed at A.5) |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | DataSF Socrata resource ID `6jgi-cpb4` |
| `platform` | DataSF / Socrata (SODA API) |
| `access_type` | API + CSV / JSON / GeoJSON download |
| `format` | Socrata-hosted tabular |
| `update_frequency` | regular |
| `coverage_period` | active pipeline (current and historic statuses) |
| `geographic_scope` | whole SF |
| `primary_keys` | planning case number; BLKLOT (concatenated, e.g., `3704045`); address |
| `relevant_objects` | `HousingProject`; `ImplementationSignal`; `OpportunitySite ↔ HousingProject` relationship statuses |
| `relevant_chain_stage` | `ImplementationSignal` |
| `reported_category_relevance` | Pipeline status values: `PL Filed`, `PL Approved`, `BP Filed`, `BP Approved`, `BP Issued`, `Construction`. TCO/CFC exit trigger. `DA` (Development Agreement) field flags major multi-phased projects |
| `known_limitations` | Aggregate over upstream raw feeds; for Tier-2 deeper interpretation, raw PPTS (A.4) and PTS (A.5) may surface signal that Pipeline collapses |
| `data_quality_caveats` | Verbatim metadata: "Significant data and systems improvements are underway; data may change at any time." BLKLOT format = concatenated; normalize against B.4 |
| `provenance_requirements` | Cite DataSF resource ID `6jgi-cpb4` + `data_as_of` + query / filter |

#### A.3.b — Production / completion companion (post-TCO/CFC)

| Field | Value |
|---|---|
| `source_id` | `sf_housing_production_xdht-4php` |
| `source_name` | San Francisco Housing Production |
| `source_owner` | SF Planning Department; DataSF (publishing) |
| `source_category` | post-TCO/CFC companion to pipeline |
| `source_classification` | companion source (post-TCO/CFC pair to A.3) |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | DataSF Socrata resource ID `xdht-4php` |
| `platform` | DataSF / Socrata (SODA API) |
| `access_type` | API + CSV / JSON / GeoJSON download |
| `format` | Socrata-hosted tabular |
| `update_frequency` | annual (April 1) |
| `coverage_period` | 2005–present |
| `geographic_scope` | whole SF |
| `primary_keys` | planning case number; BLKLOT (concatenated); address |
| `relevant_objects` | `HousingProject` (completion side); `Outcome` (delivered units); `Source` |
| `relevant_chain_stage` | `ImplementationSignal` (delivery milestone) |
| `reported_category_relevance` | Completed units counted at TCO/CFC. Pipeline and Production are mutually exclusive views. Affordable-unit tiers reported |
| `known_limitations` | Counts at completion, not issuance — authorized-but-not-completed sits in Pipeline. Pipeline and Production are not summed |
| `data_quality_caveats` | Shares Pipeline's data-systems caveat by adjacency. Coverage from 2005 — earlier delivered units are not included |
| `provenance_requirements` | Cite DataSF resource ID `xdht-4php` + query / filter; when pairing with Pipeline for entitlement-to-delivery interpretation, cite both resource IDs |

### A.4 — SF Planning applications / entitlement records (PPTS raw)

| Field | Value |
|---|---|
| `source_id` | `sf_planning_records_projects_qvu5-m3a2` |
| `source_name` | Planning Department Records - Projects (PRJ) |
| `source_owner` | SF Planning Department |
| `source_category` | SF Planning applications / entitlement records |
| `source_classification` | raw evidence (upstream feed for A.3 Pipeline aggregate) |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | DataSF Socrata resource ID `qvu5-m3a2` |
| `platform` | DataSF / Socrata (SODA API) |
| `access_type` | API + CSV / JSON download |
| `format` | Socrata-hosted tabular |
| `update_frequency` | nightly |
| `coverage_period` | active Accela project records |
| `geographic_scope` | whole SF |
| `primary_keys` | RECORD_ID (PRJ); BLOCK + LOT; PROJECT_ADDRESS |
| `relevant_objects` | `HousingProject` (raw project case records); `ImplementationSignal` (entitlement-stage activity); `OpportunitySite` (via BLOCK + LOT) |
| `relevant_chain_stage` | `ImplementationSignal` |
| `reported_category_relevance` | Raw upstream for the Planning side of Pipeline's combined view. 103 columns of project, housing-feature, environmental-review, and unit-count fields |
| `known_limitations` | Pipeline (A.3) provides easier first-pass interpretation; raw PRJ records have higher column count and may include cases not yet promoted to Pipeline |
| `data_quality_caveats` | Accela record states (open, closed, withdrawn) require careful filtering; non-housing PRJ records will be present |
| `provenance_requirements` | Cite DataSF resource ID `qvu5-m3a2` + RECORD_ID + query / filter |

| Field | Value |
|---|---|
| `source_id` | `sf_planning_records_non_projects_y673-d69b` |
| `source_name` | Planning Department Records - Non-Projects |
| `source_owner` | SF Planning Department |
| `source_category` | SF Planning applications / entitlement records (companion to `qvu5-m3a2`) |
| `source_classification` | raw evidence (upstream feed for A.3 Pipeline aggregate) |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | DataSF Socrata resource ID `y673-d69b` |
| `platform` | DataSF / Socrata (SODA API) |
| `access_type` | API + CSV / JSON download |
| `format` | Socrata-hosted tabular |
| `update_frequency` | nightly |
| `geographic_scope` | whole SF |
| `primary_keys` | RECORD_ID; BLOCK + LOT; PROJECT_ADDRESS; PARENT_ID (links to PRJ parent) |
| `relevant_objects` | `ImplementationSignal` (supplemental application activity); child-record link to `HousingProject` via PARENT_ID |
| `relevant_chain_stage` | `ImplementationSignal` |
| `reported_category_relevance` | Supplemental applications during project review (variance, conditional use, environmental review filings); finer signal layer than Pipeline status alone |
| `known_limitations` | Records from Accela database excluding PRJ records; includes child records linked to PRJ parents |
| `data_quality_caveats` | Heterogeneous record types; filtering by RECORD_TYPE required; non-housing records present |
| `provenance_requirements` | Cite DataSF resource ID `y673-d69b` + RECORD_ID + PARENT_ID where applicable |

### A.5 — DBI building permit records (PTS raw)

| Field | Value |
|---|---|
| `source_id` | `dbi_building_permits_i98e-djp9` |
| `source_name` | DBI Building Permits |
| `source_owner` | SF Department of Building Inspection; DataSF (publishing) |
| `source_category` | DBI building permit records |
| `source_classification` | raw evidence (upstream feed for A.3 Pipeline aggregate) |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | DataSF Socrata resource ID `i98e-djp9` |
| `platform` | DataSF / Socrata (SODA API) |
| `access_type` | API + CSV / JSON / GeoJSON download (bulk export warned against in Excel due to ~1M rows) |
| `format` | Socrata-hosted tabular |
| `update_frequency` | nightly / multiple times per hour |
| `coverage_period` | full DBI permits history; since 2024-12-10 only new and updated records republished, identifiable via `data_as_of` and `data_loaded_at` |
| `geographic_scope` | whole SF |
| `primary_keys` | Permit Number; Block + Lot (separate fields); address; Location (lat/lon) |
| `relevant_objects` | `ImplementationSignal` (permit activity, status, dates); links to `OpportunitySite` and `HousingProject` via BLKLOT |
| `relevant_chain_stage` | `ImplementationSignal` |
| `reported_category_relevance` | Issued building permits = HCD's primary RHNA benchmark |
| `known_limitations` | Bulk export not Excel-friendly; SODA queries needed for site-scoped fetches. Block and Lot are separate fields. Site-permit / fire-only / re-roofing flags must be respected when filtering for housing-relevant permits |
| `data_quality_caveats` | License: Open Data Commons Public Domain Dedication (PDDL). Housing-relevant permit filtering requires care |
| `provenance_requirements` | Cite DataSF resource ID `i98e-djp9` + `data_as_of` / `data_loaded_at` + Permit Number + Block + Lot |

### A.6 — Planning Code and zoning GIS layers

Three current canonical bulk datasets, all published by SF Planning, all PDDL-licensed, all updated quarterly. All `source_classification: enrichment layer`. All `tier: A`. All `v0_status: pinned`.

| `source_id` | Resource ID | Coverage |
|---|---|---|
| `sf_zoning_districts_3i4a-hu95` | `3i4a-hu95` | base zoning districts; multipolygon; fields include `the_geom`, `zoning_sim`, `districtname`, `gen`, `zoning`, `codesection` |
| `sf_height_bulk_districts_h9wh-cg3m` | `h9wh-cg3m` | height-and-bulk districts; multipolygon |
| `sf_special_use_districts_5yf5-ms5f` | `5yf5-ms5f` | Special Use District overlays per Article 2 of the SF Planning Code; multipolygon |

Common fields:

- `source_owner` — SF Planning Department
- `source_category` — Planning Code and zoning GIS layers
- `platform` / `access_type` / `format` — DataSF / Socrata (geospatial) / API + CSV / JSON / GeoJSON / multipolygon GIS layer
- `update_frequency` — quarterly
- `primary_keys` — `the_geom` (geographic primary key); district / overlay attribute fields
- `relevant_objects` — `Constraint`; `OpportunitySite` enrichment
- `relevant_chain_stage` — site-context enrichment
- `reported_category_relevance` — defines the zoning / height-bulk / SUD constraint surface that B.4 capacity assumptions are built against
- `known_limitations` — district-level; per-parcel application requires spatial join against parcels. SUD `5yf5-ms5f` is overlay-only and must be combined with base Districts
- `data_quality_caveats` — quarterly cadence; codesection references may lag formal Planning Code amendments
- `provenance_requirements` — cite DataSF resource ID + `rowsUpdatedAt` + spatial filter

### A.7 — Parcel / assessor / land-use GIS layers

Two parcel datasets plus one assessor records dataset.

| Field | Value |
|---|---|
| `source_id` | `sf_parcels_overlay_9grn-xjpx` |
| `source_name` | Parcels with Overlay Attributes |
| `source_owner` | City and County of San Francisco (DataSF) |
| `source_category` | Parcel / assessor / land-use GIS |
| `source_classification` | identity anchor |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | DataSF Socrata resource ID `9grn-xjpx` |
| `platform` | DataSF / Socrata |
| `access_type` | API + CSV / JSON / GeoJSON download |
| `format` | tabular with geospatial fields |
| `geographic_scope` | whole SF |
| `primary_keys` | parcel identifier (BLOCK + LOT); geographic boundary; pre-joined overlay fields (neighborhoods, supervisor districts, police districts, planning districts) |
| `relevant_objects` | identity anchor for cross-source joins; `OpportunitySite` enrichment; `Constraint` (administrative overlays) |
| `relevant_chain_stage` | identity anchor / site-context enrichment |
| `reported_category_relevance` | Not a reporting source; provides the parcel identity layer underlying other sources |
| `known_limitations` | Pre-joined overlays may lag if administrative boundaries change between updates |
| `data_quality_caveats` | Derived from base parcels (`acdm-wktn`); use base parcels if overlay fields are not needed |
| `provenance_requirements` | Cite DataSF resource ID `9grn-xjpx` + BLOCK + LOT |

| Field | Value |
|---|---|
| `source_id` | `sf_parcels_base_acdm-wktn` |
| `source_name` | Parcels – Active and Retired |
| `source_owner` | City and County of San Francisco |
| `source_category` | Parcel / assessor / land-use GIS |
| `source_classification` | identity anchor |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | DataSF Socrata resource ID `acdm-wktn` |
| `platform` | DataSF / Socrata |
| `access_type` | API + CSV / JSON / GeoJSON download |
| `format` | tabular with geospatial fields |
| `coverage_period` | active and retired parcels with date-added / date-retired |
| `primary_keys` | parcel identifier; date-added; date-retired |
| `relevant_objects` | identity anchor / `OpportunitySite` enrichment |
| `relevant_chain_stage` | identity anchor |
| `reported_category_relevance` | Canonical authority for parcel existence at a point in time |
| `known_limitations` | Does not include the administrative overlays of `9grn-xjpx` |
| `data_quality_caveats` | Retired parcels are included — filter on date-retired for current view |
| `provenance_requirements` | Cite DataSF resource ID `acdm-wktn` + BLOCK + LOT + as-of date |

| Field | Value |
|---|---|
| `source_id` | `sf_assessor_property_rolls_wv5m-vpq2` |
| `source_name` | Assessor Historical Secured Property Tax Rolls |
| `source_owner` | SF Office of the Assessor-Recorder |
| `source_category` | Parcel / assessor / land-use GIS (assessor side) |
| `source_classification` | enrichment layer |
| `tier` | A |
| `v0_status` | pinned |
| `url_or_identifier` | DataSF Socrata resource ID `wv5m-vpq2` |
| `platform` | DataSF / Socrata |
| `access_type` | API + CSV / JSON download |
| `format` | tabular |
| `update_frequency` | annual / per fiscal-year roll |
| `coverage_period` | July 1, 2007 to June 30, 2024 (current published coverage) |
| `geographic_scope` | whole SF |
| `primary_keys` | parcel identifier (BLOCK + LOT); fiscal-year roll |
| `relevant_objects` | `Constraint` (ownership context, use-code); `OpportunitySite` enrichment |
| `relevant_chain_stage` | site-context enrichment |
| `reported_category_relevance` | Property value, owner, last sale, square footage, use codes, classification codes |
| `known_limitations` | "Historical" naming: dataset covers through June 2024. Current-year rolls may require a separate / sibling dataset. LLC / trust ownership opacity remains a known limitation |
| `data_quality_caveats` | Use codes use Assessor-Recorder reference codes (companion reference / lookup datasets `pa56-ek2h` Property Class, `dx7g-zwbx` Neighborhood, `g77e-ikb4` Exemption, `2367-5au8` Assessor Block Maps; all `source_classification: reference / lookup`) |
| `provenance_requirements` | Cite DataSF resource ID `wv5m-vpq2` + fiscal-year roll + BLOCK + LOT |

## Meta-sources and discovery surfaces

These are navigation / interpretive entry points, not raw Tier A evidence. They surface or aggregate raw sources cataloged above. On their own they do not bear on `Assumption → ImplementationSignal → ImplementationFinding` interpretation; they help locate the raw sources that do.

### M.1 — SF Planning Property Information Map (PIM)

| Field | Value |
|---|---|
| `source_id` | `sf_pim` |
| `source_name` | SF Planning Property Information Map |
| `source_owner` | SF Planning Department |
| `source_classification` | meta-source / discovery (site-level lookup tool) |
| `url_or_identifier` | `https://sfplanninggis.org/pim/` |
| `platform` | ArcGIS-based GIS viewer; underlying ArcGIS REST endpoints not pinned in v0; bulk substrate lives in the Tier A datasets above |
| `access_type` | interactive web viewer (site-level by address / parcel / planning application number) |
| `primary_keys` | BLKLOT; address; planning application number |
| `chain_relevance` | site-level navigation only; raw chain support routes through the Tier A sources surfaced by PIM |
| `v0_status` | pinned (as meta-source) |
| `known_limitations` | "Housing Element Reused Sites and Low-Income Sites" layer is a subset / visualization; the comprehensive table is Appendix B.4 |
| `provenance_requirements` | When used as a lookup tool, cite the underlying authoritative source for any field extracted via PIM |

### M.2 — SF Housing Dashboard

| Field | Value |
|---|---|
| `source_id` | `sf_housing_dashboard` |
| `source_name` | San Francisco Housing Dashboard |
| `source_owner` | SF Planning Department |
| `source_classification` | meta-source / discovery (aggregated reporting + discovery hub) |
| `url_or_identifier` | `https://sfplanning.org/san-francisco-housing-dashboard` |
| `platform` | SF Planning web portal (interactive dashboard) |
| `access_type` | web UI; references underlying DataSF datasets via data-source links |
| `chain_relevance` | aggregated reporting only; raw chain support routes through `xdht-4php` (A.3.b) and `6jgi-cpb4` (A.3) |
| `v0_status` | pinned (as meta-source) |
| `reported_category_relevance` | "Authorized Units" = SF's primary RHNA-tracking metric (verbatim from dashboard) |
| `data_quality_caveats` | Pipeline and Completed views are mutually exclusive |
| `provenance_requirements` | When citing a dashboard view, also cite the underlying dataset that backs it |

### M.3 — MOHCD discovery surfaces

| `source_id` | URL | Role |
|---|---|---|
| `mohcd_dashboards_data` | `https://sfmohcd.org/dashboards-and-data` | MOHCD Dashboards and Data hub |
| `mohcd_bmr_listings` | `https://housing.sfgov.org/listings/for-sale` | First Come First Served BMR Listings |
| `mohcd_plans_reports` | `https://www.sf.gov/mohcd-plans-and-reports` | MOHCD Plans and Reports |
| `mohcd_department_landing` | `https://sf.gov/departments/mayors-office-housing-and-community-development` | MOHCD main department landing |

Common fields: `source_classification: meta-source / discovery`; `chain_relevance: aggregated reporting / navigation only`; `v0_status: pinned (as meta-source)`. Raw MOHCD evidence routes through the Tier B B.3 candidate datasets below.

## Tier B — candidate dependency-interpretation sources

Tier B is the **dependency-interpretation** layer (causal / delivery-risk / cross-system) — gated and not exercised in v0 by default (see [`source-strategy.md`](source-strategy.md)). The candidate sources below illuminate the conditions under which implementation occurs; reading them as dependency interpretation is Tier-B work, triggered by a specific finding, claim, reviewer need, or demo concept.

### B.1 — Capital plan and infrastructure investment references

`source_classification: deferred (Tier-2 case)` · `v0_status: category-level only` · **Chain consumption:** `Assumption` (infrastructure-dependency assumptions per flagged site); `InfrastructureDependency`. **v0 need:** none for Tier-1; activated only when a flagged site's assumption depends on infrastructure not yet sequenced. **Verification posture:** no pinning needed unless Tier-2 work surfaces a specific infrastructure-dependent assumption.

### B.2 — Transportation plans and transit access

`source_classification: deferred (Tier-2 case)` · `v0_status: category-level only` · **Chain consumption:** `Assumption` (TOD / transit-proximity capacity assumptions); `Constraint`. **v0 need:** none for Tier-1; PIM surfaces transit-served-area flags at site level as a partial substitute. **Verification posture:** no pinning needed unless Tier-2 work surfaces a transit-dependent capacity assumption.

### B.3 — Affordable housing project / funding signals (MOHCD)

Three candidate-pinned datasets. v0 posture: candidate Tier B (not promoted to Tier A); deep-probe required before any signal extraction.

| Field | Value |
|---|---|
| `source_id` | `mohcd_affordable_housing_pipeline_aaxw-2cb8` |
| `source_name` | MOHCD Affordable Housing Pipeline |
| `source_owner` | Mayor's Office of Housing and Community Development (MOHCD) + Office of Community Investment and Infrastructure (OCII) — joint |
| `source_classification` | candidate (intended: raw evidence pending deep probe) |
| `tier` | B |
| `v0_status` | candidate |
| `url_or_identifier` | DataSF Socrata resource ID `aaxw-2cb8` |
| `platform` / `access_type` / `format` | DataSF / Socrata / API + CSV / JSON / tabular (~70+ columns) |
| `update_frequency` / `coverage_period` | snapshot / active pipeline |
| `relevant_objects` | `HousingProject` (affordable); `Assumption` (affordable-pipeline assumptions); `ImplementationSignal` (funding-side momentum) |
| `relevant_chain_stage` | `ImplementationSignal` (funding) |
| `reported_category_relevance` | MOHCD/OCII affordable-housing pipeline, including units produced through the Inclusionary Affordable Housing Program; nonprofit / for-profit partnerships; AMI 20%–150% |
| `known_limitations` | Joint MOHCD+OCII view; partition between the two not pinned. Field-level structure not deep-probed |
| `provenance_requirements` | Cite DataSF resource ID `aaxw-2cb8` + snapshot date |

| Field | Value |
|---|---|
| `source_id` | `mohcd_affordable_housing_portfolio_pyxv-n29e` |
| `source_name` | MOHCD Affordable Housing Portfolio |
| `source_owner` | Mayor's Office of Housing and Community Development (MOHCD) |
| `source_classification` | candidate |
| `tier` | B |
| `v0_status` | candidate |
| `url_or_identifier` | DataSF Socrata resource ID `pyxv-n29e` |
| `platform` / `access_type` / `format` | DataSF / Socrata / API + CSV / JSON / tabular (34 columns) |
| `coverage_period` | completed affordable rental and ownership developments |
| `relevant_objects` | `HousingProject` (affordable, completed); `Outcome` (affordable delivered units) |
| `relevant_chain_stage` | `ImplementationSignal` (delivery, affordable side) |
| `reported_category_relevance` | MOHCD/OCII-financed and Planning Code §415 inclusionary 10+ unit projects, completed |
| `provenance_requirements` | Cite DataSF resource ID `pyxv-n29e` + retrieval date |

| Field | Value |
|---|---|
| `source_id` | `mohcd_non_unit_inclusionary_alternatives_g6kh-9pnv` |
| `source_name` | MOHCD Non-Unit Inclusionary Housing Alternatives |
| `source_owner` | Mayor's Office of Housing and Community Development (MOHCD) |
| `source_classification` | candidate (intended: raw evidence) |
| `tier` | B |
| `v0_status` | candidate |
| `url_or_identifier` | DataSF Socrata resource ID `g6kh-9pnv` |
| `platform` / `access_type` / `format` | DataSF / Socrata / API + CSV / JSON / tabular |
| `relevant_objects` | `ImplementationSignal` (alternative-compliance signals — fee payments, land dedication, off-site BMR); `PolicyProgram` (§415 Inclusionary) |
| `relevant_chain_stage` | `ImplementationSignal` |
| `reported_category_relevance` | §415 Inclusionary Housing requirements fulfilled through alternatives to on-site units — fee payments, land dedication, off-site construction |
| `provenance_requirements` | Cite DataSF resource ID `g6kh-9pnv` + retrieval date |

### B.4 — Construction cost, interest rate, vacancy indicators

`source_classification: deferred (Tier-2 case)` · `v0_status: category-level only` · **Chain consumption:** `Assumption` (feasibility); `ImplementationSignal` (market-condition signals); `MarketSignal` candidate subtype. **v0 need:** none for Tier-1; public-data-only discipline rules out vendor sources. **Verification posture:** no pinning needed unless Tier-2 work surfaces a market-condition-dependent assumption.

### B.5 — Policy and program documents related to HE implementation

`source_classification: deferred (Tier-2 case)` · `v0_status: category-level pinned` · **Chain consumption:** `PolicyProgram`; `Assumption` (program-level). **v0 need:** category-level only for Tier-1; specific documents identified case-by-case (includes SF's adopted Housing Element 2023–2031 — the policy document that sets the assumption surface Appendix B.4 derives from). **Verification posture:** case-by-case as a specific PolicyProgram interpretation requires.

## Tier C — selective / deferred supporting sources

Tier C sources are selective for Tier-2 deeper interpretation of flagged sites. They are listed at the category level in [`source-strategy.md`](source-strategy.md). Specific Tier C datasets are **not pinned in v0 by default**. All Tier C entries carry `source_classification: deferred (Tier-2 case)` and `v0_status: deferred (Tier-2 case)`.

`ParticipatorySignal` candidate sources (public comments, meeting transcripts, comment letters, survey summaries) are reserved by default in v0. If activated, representativeness and bias documentation are required per source.

## Source inventory fields / metadata model

The field set used throughout this inventory:

```text
source_id                       short, lowercase, underscore-delimited; stable;
                                used as canonical short reference
source_name                     human-readable name
source_owner                    publishing organization (and underlying agency if different)
source_category                 category from docs/source-strategy.md
source_classification           raw evidence / operational aggregate / companion source /
                                identity anchor / enrichment layer / meta-source / discovery /
                                reference / lookup / deferred (Tier-2 case) / candidate
tier                            A / B / C
url_or_identifier               canonical URL or DataSF / ArcGIS resource ID
platform                        DataSF/Socrata, ArcGIS, HCD portal, static download, etc.
access_type                     direct download, API, web viewer, etc.
format                          CSV, JSON, GeoJSON, XLSX, PDF, GIS layer, etc.
update_frequency                nightly, quarterly, per-cycle, etc. (when known)
coverage_period                 time range covered by the data (when known)
geographic_scope                SF whole-city, neighborhood, statewide, etc.
primary_keys                    join keys; BLKLOT format variant noted where relevant
relevant_objects                which object-model primitives this source supports
relevant_chain_stage            Assumption / ImplementationSignal / ImplementationFinding /
                                InterventionCandidate
reported_category_relevance     how this source maps to APR / Pipeline / Production reporting
known_limitations               structural limits
data_quality_caveats            data-quality notes (verbatim where dataset publishes them)
provenance_requirements         what to cite when using this source
v0_status                       pinned / partial / candidate / needs verification /
                                category-level only / deferred (Tier-2 case)
```

Notes on field use:

- `source_classification` is the role discipline — what the source *is* in the inventory model. `v0_status` is the access-verification state. Separate fields, separate questions.
- `relevant_chain_stage` is restricted to the four chain stages from [`object-model.md`](object-model.md): `Assumption / ImplementationSignal / ImplementationFinding / InterventionCandidate`. Supporting primitives (`Outcome`, `Constraint`, `OpportunitySite`, etc.) belong in `relevant_objects`, not `relevant_chain_stage`.
- Meta-source entries omit fields not applicable to viewers and substitute `chain_relevance` (descriptive prose) for `relevant_chain_stage` since meta-sources do not bear on the chain directly.

This field set is documentation, not an executable schema. The inventory is Markdown-first and consistent with [`data-dictionary.md`](data-dictionary.md). Promotion to a runnable manifest (YAML, JSON, CSV) is deferred until a v0 consumer requires it.

## Known caveats

The cautions below belong with the inventory itself; they are not commentary about it.

1. **Source inventory ≠ source sufficiency.** Naming a source in the inventory does not certify that the source carries enough signal to weaken or support a given assumption. Sufficiency is a finding-level question, decided per-assumption during chain extraction.
2. **Metadata accessibility ≠ row-level use.** A confirmed-accessible metadata endpoint says nothing about whether the rows behind it are clean, current, or interpretable.
3. **DataSF / Socrata resource IDs may change.** IDs are generally stable but not guaranteed permanent. Cite IDs with retrieval / verification dates.
4. **Source dashboards are often JS-rendered.** Cite the linked dataset, not the dashboard view, when source-anchoring a signal.
5. **PIM is site-level via the viewer; bulk is via the canonical Tier A datasets.** Do not treat PIM as a bulk dataset.
6. **Appendix B.4 is large and statewide-format.** ~99.6% of rows are < 5-unit ADU-strategy parcels. Only ~171 sites have capacity ≥ 20; 80% of those are already Pipeline-flagged. The aggregate ADU strategy means testing the chain at any individual RH-1 site does not really test SF's strategy.
7. **SF Pipeline has data-quality caveats.** Verbatim metadata: "Significant data and systems improvements are underway; data may change at any time." Any signal sourced from Pipeline must carry this caveat.
8. **Public-input sources are deferred / cautious.** `ParticipatorySignal` candidate sources are reserved by default in v0.
9. **BLKLOT formats vary.** Any cross-source join requires explicit normalization.

| Source | BLKLOT format | Example |
|---|---|---|
| Appendix B.4 | hyphenated | `3704-045` |
| SF Pipeline `6jgi-cpb4` | concatenated | `3704045` |
| DBI Permits `i98e-djp9` | separate Block + Lot | `3704` + `045` |
| Planning Non-Projects `y673-d69b` | separate Block + Lot | `3704` + `045` |
| Parcels with Overlay `9grn-xjpx` | parcel identifier (BLOCK + LOT) | per dataset |
| Assessor Property Rolls `wv5m-vpq2` | parcel identifier (BLOCK + LOT) | per dataset |

Lots with letter suffix (e.g., `0044-002A` / `0044002A`) require consistent handling.

10. **Category-level entry ≠ pinned source.** Tier B abstract entries (B.1, B.2, B.4) and Tier C entries are category-level placeholders, not pinned sources. Do not let category-level entries imply more verification than has happened.
11. **Pipeline (`6jgi-cpb4`) is an operational aggregate, not a primary source.** Pipeline curates upstream raw feeds: PPTS (Planning Accela: `qvu5-m3a2` + `y673-d69b`) and PTS (DBI: `i98e-djp9`). For Tier-2 deeper interpretation, dropping back to the raw feeds may surface signal that Pipeline collapses.

## Posture

This inventory is a working snapshot. Specific dataset choices remain candidate per the posture set in [`source-strategy.md`](source-strategy.md). Entries will be revised as prototype work tests them. No data has been retrieved as part of this document; retrieval is a separate, later stage.
