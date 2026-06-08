/* urban-observatory_ia-state-spine.data.js
   Source data for the urban-observatory INTERACTIVE IA STATE SPINE.
   Rendered by diagrams-interactive-spine-engine.js (Class A · diagram-interactive-spine,
   by reference @ pin 20fc5d6), consuming Spectral State v1.1.

   WHAT THIS DIAGRAM ASSERTS
     The operational STATE surface: each surface / seam / open question colored by
     ONE Spectral State role — "what state is each part of the work in, and where."
     It is NOT the architecture tree (repo atlas / structure) and NOT the ontology
     (kinds). There is no inheritance spine (UO has no Axis-B ladder).

   DISCIPLINE
     - Color encodes STATE only — never importance. Evidence / qualifier / pointer
       are inspector metadata, never hue. One state role per node.
     - `earned` is reserved for working, merged INFRASTRUCTURE (the renderer + the
       merged static diagrams). Nothing analytical is earned; nothing public is earned.
     - The state map was reviewed + gated by ASK (2026-06-05): doc corpus = structural
       (not earned); no modes in v1.
     - Illustrative; repo prose remains source truth.

   ENGINE CONSTRAINTS honored here (the engine is consumed verbatim, never edited):
     - exactly one `root` node and at most one `external` node are placed by the
       engine. UO's four owned-elsewhere surfaces are therefore CONSOLIDATED into the
       single `external` node and enumerated in its inspector evidence.
     - `mode` group is unused in v1 (ASK gate: no modes); no node carries `modes`.

   Node: { id, group, label, state, evidence, qualifier?, pointer }
     group: 'root' | 'spine' | 'question' | 'external'   (no 'mode' in v1)
     state: one of the eight Spectral State roles in `states` below.
*/

window.IA_STATE_SPINE = {
  meta: {
    title: 'Information architecture — state',
    subtitle: 'operational state surface · earned / structural / partial / held / proposed / external, and where · color encodes state only',
    stamp: { source: 'source-v1', render: 'render-v1', date: '2026-06-05' },
  },

  // The eight Spectral State v1.1 roles (inherited vocabulary — do not rename).
  states: [
    { role: 'earned',     label: 'earned',     meaning: 'operationally grounded at full depth' },
    { role: 'structural', label: 'structural', meaning: 'structurally / schema proven; not full-flow pressured' },
    { role: 'partial',    label: 'partial',    meaning: 'operational at bounded depth' },
    { role: 'proposed',   label: 'proposed',   meaning: 'articulated as a candidate; not yet pressured' },
    { role: 'deflated',   label: 'deflated',   meaning: 'pressure showed it unnecessary / dead' },
    { role: 'held',       label: 'held',       meaning: 'a named open question, not yet resolved' },
    { role: 'external',   label: 'external',   meaning: 'owned elsewhere (inherited / upstream)' },
    { role: 'neutral',    label: 'neutral',    meaning: 'no asserted state (the lavender field)' },
  ],

  nodes: [
    // ---- root / framing (asserts no state) ----
    { id: 'root', group: 'root', label: 'urban-observatory · operational state', state: 'neutral',
      evidence: 'Framing node — asserts no state. The lived state of the work, surface by surface.',
      pointer: 'docs/architecture.md' },

    // ---- spine: upstream (docs/method) → sources → worked artifacts → working infrastructure ----
    { id: 's-docs', group: 'spine', label: 'repo documentation corpus (README + docs/*)', state: 'structural',
      evidence: 'Authoritative repo structure / source truth — it exists and structures the project, but it is not operational proof of the method. (ASK gate: structural, not earned.)',
      qualifier: 'source truth, not method proof', pointer: 'README.md + docs/' },
    { id: 's-chain', group: 'spine', label: 'interpretive chain (Assumption→Signal→Finding→Candidate)', state: 'structural',
      evidence: 'Validated as a concept by manual operator-side extraction; not full-flow pressured. The repo names it a working hypothesis.',
      pointer: 'docs/object-model.md' },
    { id: 's-objmodel', group: 'spine', label: 'object model + ontology concepts', state: 'structural',
      evidence: 'Named primitives + chain; schema-level decisions explicitly deferred. Structurally articulated, not schema-frozen.',
      pointer: 'docs/object-model.md · docs/diagrams/urban-observatory_ontology.html' },
    { id: 's-method', group: 'spine', label: 'methodology (matrix · surfaces · uncertainty · provenance)', state: 'structural',
      evidence: 'Method defined and exercised in operator-side scratch examples; not expert-reviewed or public.',
      pointer: 'docs/methodology.md' },
    { id: 's-srcstrategy', group: 'spine', label: 'source strategy (Tier A/B/C posture)', state: 'structural',
      evidence: 'Posture defined; not yet exercised by retrieval / extraction.',
      pointer: 'docs/source-strategy.md' },
    { id: 's-tierA', group: 'spine', label: 'Tier A sources (B.4 · APR · Pipeline · PPTS · DBI · zoning · parcels)', state: 'structural',
      evidence: 'Access pinned + schema inspected at INVENTORY level; no data retrieved or extracted. Source inventory ≠ sufficiency — so structural, not earned.',
      qualifier: 'access pinned; no extraction', pointer: 'docs/source-inventory.md' },
    { id: 's-tierB', group: 'spine', label: 'Tier B / MOHCD aaxw-2cb8 (candidate source)', state: 'proposed',
      evidence: 'Tier-B candidate; operator-side readiness probe worked but ladder-semantics capped (no published source definition). Articulated candidate, deep-probe pending.',
      pointer: 'docs/source-inventory.md (B.3)' },
    { id: 's-tierC', group: 'spine', label: 'Tier C / deferred sources', state: 'held',
      evidence: 'Category-level only; deferred to Tier-2 deeper interpretation; not pinned in v0.',
      pointer: 'docs/source-inventory.md (Tier C)' },
    { id: 's-sec4', group: 'spine', label: '§4 citywide-inventory baseline (internal)', state: 'partial',
      evidence: 'Worked baseline; TMK-reviewed + absorbed; internal / operator-side, bounded depth.',
      qualifier: 'internal · TMK-reviewed', pointer: 'operator-side scratch (not in repo)' },
    { id: 's-sec7', group: 'spine', label: '§7 assumption stress tests (2 worked, internal)', state: 'partial',
      evidence: 'Two demonstrated examples (issuance-to-delivery; redevelopment-likelihood); TMK-reviewed + absorbed; not comprehensive.',
      qualifier: 'two examples, not comprehensive', pointer: 'operator-side scratch (not in repo)' },
    { id: 's-sec5', group: 'spine', label: '§5 pipeline-fragility signal (worked stage-aging)', state: 'partial',
      evidence: 'T3 met (≥2 of 4 stages); a single-snapshot pattern candidate; worked operator-side.',
      qualifier: 'single-snapshot pattern candidate', pointer: 'operator-side scratch (not in repo)' },
    { id: 's-artifacts', group: 'spine', label: 'internal review artifacts (stage-1 → 9-of-13)', state: 'partial',
      evidence: 'Internal skeleton artifacts, TMK-reviewed; 9 of 13 report sections at bounded depth; not public.',
      qualifier: '9 of 13 sections · internal', pointer: 'operator-side scratch (not in repo)' },
    { id: 's-renderer', group: 'spine', label: 'artifact renderer · Class B (tools/artifact-template)', state: 'earned',
      evidence: 'Operational end-to-end: merged (#16/#17), used to render real TMK review packages.',
      pointer: 'tools/artifact-template/' },
    { id: 's-diagrams', group: 'spine', label: 'static diagrams · Class A (architecture tree + ontology)', state: 'earned',
      evidence: 'Merged (#18/#19); render in light and dark; this state spine sits beside them as the third diagram.',
      pointer: 'docs/diagrams/' },

    // ---- question: open questions / candidates / held seams ----
    { id: 'q-sec5t4', group: 'question', label: '§5 T4 forward-snapshot closure', state: 'held',
      evidence: 'Time-gated on a Pipeline data refresh; HOLD.', pointer: 'operator-side scratch (not in repo)' },
    { id: 'q-sec8', group: 'question', label: '§8 constraint-exposure findings', state: 'held',
      evidence: 'Sources not pinned; HOLD.', pointer: 'docs/report-outline.md (§8) · operator-side scratch' },
    { id: 'q-aaxw', group: 'question', label: 'aaxw ladder-semantics confirmation', state: 'held',
      evidence: 'Capped — no published source definition available.', pointer: 'operator-side scratch (not in repo)' },
    { id: 'q-sections', group: 'question', label: 'remaining report sections (unbuilt)', state: 'proposed',
      evidence: 'Named in the report outline; candidate, not yet worked.', pointer: 'docs/report-outline.md' },
    { id: 'q-public', group: 'question', label: 'public Risk Brief / public site-level analysis', state: 'held',
      evidence: 'Deferred until after expert review; public site-level analysis is explicitly not a v0 deliverable.',
      pointer: 'docs/v0-scope.md · docs/report-outline.md' },
    { id: 'q-thisspine', group: 'spine', label: 'interactive IA spine (this surface)', state: 'earned',
      evidence: 'Merged (#20); renders in light and dark beside the static diagrams. Earned-as-artifact.',
      pointer: 'docs/diagrams/interactive/' },
    { id: 'q-roadmap', group: 'question', label: 'future audience / market roadmap', state: 'held',
      evidence: 'Recorded in grounding note v18 as durable future posture but explicitly NOT v0; authorizes nothing. Execution is held.',
      pointer: 'grounding note v18 (operator-side)' },
    { id: 'q-bucketbc', group: 'question', label: 'Bucket-B/C promotion', state: 'held',
      evidence: 'Not authorized; a v0 anti-goal as current execution.', pointer: 'docs/project-scope.md (anti-goals)' },

    // ---- external: owned elsewhere (ONE anchor; engine places one external node) ----
    { id: 'x-owned-elsewhere', group: 'external', label: 'owned elsewhere · operator-side + upstream', state: 'external',
      evidence: 'Four owned-elsewhere surfaces, consolidated into the engine’s single external anchor: grounding note (source-of-intent) · sources-of-intent + handoff/absorption records · TMK interim domain reviews · design-system-ASK (upstream Class A/B patterns + Spectral State). UO points to / consumes them; they are not repo truth.',
      pointer: 'docs/diagrams/_dsa-tokens/MANIFEST.md (upstream pin) + operator-side sources-of-intent' },
  ],
};
