# docs/diagrams/

Illustrative **Class A diagrams** for urban-observatory, rendered by consuming
the shared diagram patterns from
[`design-system-ASK`](https://github.com/apexSolarKiss/design-system-ASK)
**by reference** (pinned local mirror; no CDN, no fork).

These diagrams are **illustrative orientation aids**, not source truth. The repo
prose under `docs/` is authoritative; a diagram may lag the repo — refresh it or
trust the prose.

## The trifecta (three diagrams, not four)

Following the axis-separation lesson (see asset-pipeline-ASK's
`docs/layer-disambiguation-note-v1.md`), these are **different artifacts on
different meta-axes** — not four views of one picture. Each is fixed by two
orthogonal questions: *what is it slicing* (the whole repo, or one conceptual
axis) and *structure or state*.

| Diagram | Slice | Structure / state | Pattern | Status |
|---|---|---|---|---|
| **Architecture tree** | whole repo (the atlas) | structure | `diagram-static-H` | built |
| **Ontology** | one axis — *kinds* of concepts (Axis A) | structure | `diagram-static-H` | planned |
| **Interactive IA spine** | the operational whole | **state** (Spectral State v1.1) | `diagram-interactive-spine` | planned |

- The **structure** diagrams keep **one axis each** (axis purity) and assert no
  maturity. The **state** diagram is the one place the mixed operational whole is
  the right subject — "is this proven yet?" is asked of the lived surface, not an
  abstract single axis. On the state surface, **color encodes state only**.
- urban-observatory builds **three, not four**: there is **no inheritance
  (Axis-B) spine**, because UO has no genuine linear inheritance ladder. UO's
  load-bearing chain (Assumption → ImplementationSignal → ImplementationFinding →
  InterventionCandidate) is a runtime/process axis, not a scope/inheritance one.
  A fourth diagram is not manufactured just to mirror the reference set.

## Files

```text
docs/diagrams/
├── README.md                                      this file
├── _dsa-tokens/                                   VENDORED, PINNED design-system-ASK mirror
│   ├── MANIFEST.md                                upstream commit + per-file sha256
│   ├── colors_and_type.css                        Tier 1 + Tier 2 tokens (verbatim)
│   └── fonts/                                      Inter + JetBrains Mono (+ OFL licenses)
├── diagrams-static-H-engine.js                    upstream engine — consumed verbatim, DO NOT EDIT
├── diagrams.css                                   upstream style layer — consumed verbatim, DO NOT EDIT
├── export-png.js                                  upstream PNG export — consumed verbatim, DO NOT EDIT
├── urban-observatory_architecture-tree.html       UO chrome (title · subtitle · stamp · legend)
└── urban-observatory_architecture-tree.source.js  UO data (window.TREE_ARCHITECTURE)
```

The ontology and interactive IA spine will add their own `*.html` + `*.source.js`
/ `*.data.js`; the ontology reuses this same static scaffold, and the interactive
spine additionally vendors `spectral-state.css` into `_dsa-tokens/` (at the same
pin) and copies the interactive engine/CSS/export.

## Consumption discipline

- **Consume by reference; no fork.** The engine, `diagrams.css`, and
  `export-png.js` are copied **verbatim** from the upstream pattern and are
  **never edited** here — modifying them breaks inheritance. UO authors **only**
  source data (`window.TREE_*`) and HTML chrome (`.mark`, title, subtitle,
  `.stamp`, legend, `<title>`, `<meta>`, file names).
- **Pinned, offline, no CDN.** `_dsa-tokens/` is a pinned snapshot
  (`MANIFEST.md` records the commit SHA + per-file sha256). The diagrams inherit
  at generation time and **freeze for audit** — no runtime fetch, no font CDN.
- **Tier 1 + Tier 2 only.** No ASK **Tier 3** (`logo-ASK`, "ASK Design System"
  chrome) leaks into UO surfaces. UO owns its own content and its own Tier 3.
- **Light + dark both work** (verified for the architecture tree, both themes).
- **Pin:** design-system-ASK `main` **`20fc5d6`**.

## Viewing

Open any diagram `.html` directly in a browser (it loads its CSS/JS/fonts from
this directory and the pinned `_dsa-tokens/` mirror — no server required). Pan by
dragging, zoom with the wheel or the HUD, fit with `⤢`, and export a poster PNG
with the `PNG` button.

## Re-syncing

When the upstream tokens/fonts (or, later, Spectral State) change and a refresh
is wanted, re-sync `_dsa-tokens/` from the new commit, regenerate `MANIFEST.md`,
and bump the affected diagram's `source-vN` / `render-vN` stamp. Propose changes
to the tokens themselves upstream at the `design-system-ASK` control surface —
never edit the vendored mirror or the upstream engine/CSS here.
