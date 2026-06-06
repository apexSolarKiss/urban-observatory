/* urban-observatory_architecture-tree.source.js
   Source data for the urban-observatory ARCHITECTURE TREE.
   Rendered by diagrams-static-H-engine.js (Class A · diagram-static-H, by reference).

   WHAT THIS DIAGRAM ASSERTS
     The atlas of the whole repo: WHERE urban-observatory's surfaces live —
     execution rules, project prose, tooling, the diagrams themselves, external
     context, and the not-yet-built surfaces. It is STRUCTURAL. It makes no
     maturity / provenness claim about the work (that is the interactive IA
     spine's job, on a different axis, via Spectral State). The only status used
     here is the static pattern's structural earned/held: earned = present in the
     repo today; held = authorized but not yet built. No Spectral State here.

   Node shape: { kind: 'root'|'section'|'group'|'node', label, note?, tag?, status?, children? }
     kind defaults to 'node'; status defaults to 'earned'.

   Bump the source-v / render-v stamp in the .html when topology changes
   (e.g. when the ontology / IA-spine diagrams land, flip them earned).
*/

window.TREE_ARCHITECTURE = {
  kind: 'root',
  label: 'urban-observatory',
  note: 'implementation intelligence — continuously interpreting whether urban plans become real outcomes. method-first, public-data, pre-prototype.',
  children: [
    {
      kind: 'section', label: 'execution & governance',
      children: [
        { label: 'AGENTS.md', note: 'workflow rules — branch · scope · plan-before-execute · single-writer · structured summaries (agent-agnostic)' },
        { label: 'CLAUDE.md', note: 'entry point; defers to AGENTS.md + the external grounding note' },
        { label: 'LICENSE · NOTICE', note: 'Apache-2.0 · © Andrew S Klug (ASK)' },
      ],
    },
    {
      kind: 'section', label: 'docs/ · project prose', tag: 'source truth',
      children: [
        { label: 'README.md', note: 'project thesis + entry points' },
        { label: 'architecture.md', note: 'repo-local architecture + source-of-truth boundaries' },
        { kind: 'group', label: 'concept',
          children: [
            { label: 'implementation-intelligence.md', note: 'the core concept' },
            { label: 'methodology.md', note: 'how interpretation works' },
            { label: 'object-model.md', note: 'interpretive chain + supporting primitives' },
          ],
        },
        { kind: 'group', label: 'scope',
          children: [
            { label: 'project-scope.md', note: 'what is in / out of scope' },
            { label: 'v0-scope.md', note: 'bounded whole-city SF prototype · two-tier pass' },
            { label: 'report-outline.md', note: 'first artifact: Housing Element Implementation Risk Brief' },
          ],
        },
        { kind: 'group', label: 'sources',
          children: [
            { label: 'source-strategy.md', note: 'public-data posture (Tier A / B / C)' },
            { label: 'source-inventory.md', note: 'inventory of public-data sources' },
            { label: 'data-dictionary.md', note: 'per-concept Markdown-first treatment' },
          ],
        },
      ],
    },
    {
      kind: 'section', label: 'tools/ · reusable machinery',
      children: [
        { kind: 'group', label: 'artifact-template/ · Class B (output-artifact)',
          children: [
            { label: 'build.py', note: 'Markdown → sealed single-file HTML' },
            { label: 'artifact.template.html', note: 'Class B v2 shell + UO Tier-3 overlay' },
            { label: '_dsa-tokens/', note: 'vendored design-system mirror @ 040e7ca' },
          ],
        },
      ],
    },
    {
      kind: 'section', label: 'docs/diagrams/ · Class A', tag: 'this atlas',
      children: [
        { label: 'architecture tree', note: 'this diagram — atlas of where surfaces live (structure)' },
        { label: 'ontology', status: 'held', note: 'Axis A · what kinds of concepts exist (structure) — this PR series' },
        { label: 'interactive IA spine', status: 'held', note: 'operational surface colored by state (Spectral State) — this PR series' },
        { kind: 'group', label: 'shared · consumed by reference',
          children: [
            { label: 'diagrams-static-H-engine.js', note: 'upstream engine — copied verbatim, not edited' },
            { label: 'diagrams.css', note: 'upstream style layer — copied verbatim, not edited' },
            { label: 'export-png.js', note: 'upstream PNG export — copied verbatim, not edited' },
            { label: '_dsa-tokens/', note: 'vendored design-system mirror @ 20fc5d6' },
          ],
        },
      ],
    },
    {
      kind: 'section', label: 'external context', tag: 'operator-side · not in repo',
      children: [
        { label: 'grounding note', note: 'intent · audience · philosophy · durable threads (source of intent)' },
        { label: 'handoff + absorption records', note: 'inbound / outbound handoffs + absorptions (operator-side)' },
        { label: 'operator memory', note: 'operator-side only; not project state' },
      ],
    },
    {
      kind: 'section', label: 'not yet built', tag: 'pre-prototype',
      children: [
        { label: 'schemas', status: 'held', note: 'object-model schemas — authorized, not yet built' },
        { label: 'sample datasets', status: 'held' },
        { label: 'analysis notebooks', status: 'held' },
        { label: 'report artifacts', status: 'held', note: 'the Housing Element Implementation Risk Brief — interpreted output' },
      ],
    },
  ],
};
