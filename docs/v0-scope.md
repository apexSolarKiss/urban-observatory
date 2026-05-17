# v0 Scope

`urban-observatory`'s v0 is a **bounded whole-city San Francisco Housing Element implementation-intelligence prototype**, structured as an APR-augmentation companion rather than an APR replacement.

This document defines what v0 is, how it is bounded, and what it intentionally is not. It complements [`project-scope.md`](project-scope.md), which defines the project's overall scope and anti-goals.

## v0 direction

v0 tests whether the implementation-intelligence method — centered on the interpretive chain described in [`object-model.md`](object-model.md) — can produce credible memo-form interpretations of whether the assumptions embedded in San Francisco's adopted Housing Element, Annual Progress Report, and related public planning documents remain plausible as conditions change.

## Implementation surface

v0 uses a hybrid implementation surface:

- APR interpretation
- the full Housing Element opportunity-site inventory
- the citywide housing pipeline and project universe
- opportunity-site viability
- pipeline fragility
- implementation assumption stress-testing
- constraint exposure
- intervention candidates
- feasibility shifts
- infrastructure dependency warnings
- mismatch between adopted plan assumptions and current conditions

The surface is hybrid because no single view interprets implementation alone; the views reinforce each other.

## How v0 is bounded

v0 is bounded by **analytical depth, automation level, confidence representation, interpreted outputs, signal coverage, and review posture** — not by shrinking geography below whole-city San Francisco.

In practice this means a two-tier pass:

- **Tier 1.** Every Housing Element opportunity site receives a shallow baseline signal card.
- **Tier 2.** Deeper interpretation is reserved for flagged sites, selected typologies, and non-obvious implementation-risk cases.

The typology grouping itself is not finalized; see [`object-model.md`](object-model.md) for why this stays conceptual until prototype work has reviewed the inventory.

Quantitative outputs are assistive, not authoritative (see [`methodology.md`](methodology.md)). Public phrasing is evidence-supported implementation sensitivity, not failure or enforcement language. First reviewer is an implementation-oriented San Francisco or city planner, or a senior planning consultant. Public site-level analysis is deferred until after expert review and is not a v0 deliverable.

## First artifact

The first artifact is the **Housing Element Implementation Risk Brief**, framed as a forward-looking APR-augmentation companion. Its outline lives in [`report-outline.md`](report-outline.md).

## What v0 is not

v0 is not complete citywide intelligence, an HCD enforcement tool, a city-grading system, an APR compliance check, a developer underwriting platform, a deterministic feasibility engine, a dashboard-first product, or a smart-city platform. For the canonical anti-goal list, see [`project-scope.md`](project-scope.md).

## Posture

v0 is the working scope; it is not immutable doctrine. As prototype work tests the method against real public-data conditions, the scope may be refined. Subsequent scoped work — schema implementation, source inventory, first report skeleton — is deferred to later phases that depend on what v0 reveals.
