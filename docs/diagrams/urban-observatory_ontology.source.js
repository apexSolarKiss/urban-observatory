/* urban-observatory_ontology.source.js
   Source data for the urban-observatory ONTOLOGY diagram.
   Rendered by diagrams-static-H-engine.js (Class A · diagram-static-H, by reference).

   WHAT THIS DIAGRAM ASSERTS
     Axis A — the KINDS of concepts the method reasons over: the interpretive
     chain, the candidate signal subtypes, the supporting primitives, the
     assessment vocabularies, and the output classifications that are NOT objects.
     It is a STRUCTURAL classification, not a maturity-state diagram: no status is
     asserted on any node, and no Spectral State is loaded. (Status / provenness
     is the interactive IA spine's job, on a different axis.)

   FAITHFUL EXTRACTION from docs/object-model.md + docs/data-dictionary.md. This
   diagram introduces no ontology doctrine beyond what those repo docs support.
   The object model is a stated WORKING HYPOTHESIS, not a schema — labels here
   carry that provisionality in their notes, not in color.

   Node shape: { kind: 'root'|'section'|'group'|'node', label, note?, tag?, children? }
     No `status` is used here (structural map). Bump the source-v / render-v stamp
     in the .html when the model changes.
*/

window.TREE_ONTOLOGY = {
  kind: 'root',
  label: 'urban-observatory · object model',
  note: 'Axis A — the kinds of concepts the method reasons over. A working hypothesis, not a schema. Structure, not status.',
  children: [
    {
      kind: 'section', label: 'interpretive chain', tag: 'working hypothesis · the center',
      children: [
        { label: 'Assumption', note: 'a claim embedded in a plan / policy / inventory / APR, tested for plausibility under changing conditions. Kept at the center (not Site / Intervention / Constraint). May attach at site · project · typology · program · aggregate scale.' },
        { label: 'ImplementationSignal', note: 'a public-data observation bearing on whether assumptions hold; source- and assumption-anchored, directional, typed. Many records may aggregate to one signal. → subtypes below.' },
        { label: 'ImplementationFinding', note: 'interpretive synthesis comparing assumptions against signals; carries direction, confidence, candidates, provenance. The primary interpretive artifact. → three assessment layers.' },
        { label: 'InterventionCandidate', note: 'a downstream, non-prescriptive option that could change a weakened assumption’s trajectory. Surfaced, not endorsed; plural, actor-typed. Not a recommendation.' },
      ],
    },
    {
      kind: 'section', label: 'implementation-signal subtypes', tag: 'candidate · not final schema',
      children: [
        { label: 'AdministrativeSignal', note: 'pipeline / planning / case-management activity' },
        { label: 'PermitSignal', note: 'building-permit activity' },
        { label: 'PipelineSignal', note: 'project-status changes' },
        { label: 'MarketSignal', note: 'market-level indicators (also listed as a supporting primitive)' },
        { label: 'InfrastructureSignal', note: 'capital-plan / infrastructure-capacity signals' },
        { label: 'EnvironmentalSignal', note: 'environmental review or constraint signals' },
        { label: 'ParticipatorySignal', note: 'public-input signals (reserved by default in v0)' },
        { label: 'EnforcementPromptedSignal', note: 'activity prompted by enforcement, not voluntary market' },
        { label: 'CurrentUseSignal', note: 'current operating use of a property (load-bearing; retained)' },
        { label: 'ProgrammaticTemporalSignal', note: 'the implementation environment, not the site (load-bearing; retained)' },
      ],
    },
    {
      kind: 'section', label: 'supporting primitives', tag: 'not the center',
      children: [
        { label: 'OpportunitySite', note: 'a Housing Element opportunity site; anchor for the citywide signal-card pass' },
        { label: 'HousingProject', note: 'a project in the citywide pipeline; separate from sites, linkable' },
        { label: 'PolicyProgram', note: 'a city / state policy or program relevant to implementation' },
        { label: 'InfrastructureDependency', note: 'an upstream constraint on what a site or project can deliver' },
        { label: 'Constraint', note: 'a regulatory / environmental / policy constraint' },
        { label: 'Outcome', note: 'an observed outcome (delivered units, withdrawn projects, abandoned entitlements)' },
        { label: 'Source', note: 'a public document or dataset cited as provenance. First-class.' },
        { label: 'Confidence', note: 'a reusable confidence value on signals, findings, signal cards' },
        { kind: 'group', label: 'OpportunitySite ↔ HousingProject link',
          children: [
            { label: 'direct_match', note: 'project on the same opportunity-site parcel' },
            { label: 'nearby_or_related', note: 'near / within the site’s planning area, not same parcel' },
            { label: 'citywide_context', note: 'not tied to a site; interprets broader pipeline / delivery' },
            { label: 'inventory_only', note: 'site in inventory, no matched project; an assumption surface only' },
          ],
        },
      ],
    },
    {
      kind: 'section', label: 'assessment vocabulary', tag: 'working · not final schema',
      children: [
        { label: 'signal-level direction', note: 'supports / weakens / contradicts / uncertain — a signal vs. the assumption it anchors' },
        { label: 'matrix row-level assessment', note: 'confirmed / weakened / contradicted / unresolved / not yet testable — one document-claim vs. its evidence' },
        { label: 'finding-level composite', note: 'held as interpretation prose when row assessments diverge; no controlled enum committed' },
      ],
    },
    {
      kind: 'section', label: 'output classifications', tag: 'not objects in v0',
      children: [
        { label: 'ImplementationRisk', note: 'an output classification field; combines direction + confidence + structure into a quick-scan tier' },
        { label: 'FeasibilityShift', note: 'a direction label; feasibility change over time at aggregate / typology / corridor level' },
        { label: 'SiteViabilityDrift', note: 'a direction label; per-site, per-assumption drift over time' },
      ],
    },
  ],
};
