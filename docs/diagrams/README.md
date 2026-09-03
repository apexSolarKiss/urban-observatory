# docs/diagrams/

Illustrative **Class A diagrams** for [urban-observatory](../../README.md), rendered by consuming
the shared diagram patterns from
[`design-system-ASK`](https://github.com/apexSolarKiss/design-system-ASK)
**by reference** (pinned local mirror; no CDN, no fork).

These diagrams are **illustrative orientation aids**, not source truth. The repo
prose under `docs/` is authoritative; a diagram may lag the repo — refresh it or
trust the prose.

## The trifecta (three diagrams, not four)

Following the axis-separation lesson (see [asset-pipeline-ASK](https://github.com/apexSolarKiss/asset-pipeline-ASK)'s
`docs/layer-disambiguation-note-v1.md`), these are **different artifacts on
different meta-axes** — not four views of one picture. Each is fixed by two
orthogonal questions: *what is it slicing* (the whole repo, or one conceptual
axis) and *structure or state*.

| Diagram | Slice | Structure / state | Pattern | Status |
|---|---|---|---|---|
| **Architecture tree** | whole repo (the atlas) | structure | `diagram-static-H` | built |
| **Ontology** | one axis — *kinds* of concepts (Axis A) | structure | `diagram-static-H` | built |
| **Interactive IA spine** | the operational whole | **state** (Spectral State v1.1) | `diagram-interactive-spine` | built |

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
│   ├── spectral-state.css                         Spectral State v1.1 (verbatim) — interactive spine only
│   └── fonts/                                      Inter + JetBrains Mono (+ OFL licenses)
├── diagrams-fit.js                                upstream fit contract (#77-#80) — loaded BEFORE the engine, verbatim, DO NOT EDIT
├── diagrams-static-H-engine.js                    upstream engine — consumed verbatim, DO NOT EDIT
├── diagrams.css                                   upstream style layer — consumed verbatim, DO NOT EDIT
├── export-png.js                                  upstream PNG export (static) — consumed verbatim, DO NOT EDIT
├── urban-observatory_architecture-tree.html       UO chrome (title · subtitle · stamp · legend)
├── urban-observatory_architecture-tree.source.js  UO data (window.TREE_ARCHITECTURE)
├── urban-observatory_ontology.html                UO chrome (legend repurposed as an Axis-A reading note)
├── urban-observatory_ontology.source.js           UO data (window.TREE_ONTOLOGY)
└── interactive/                                    Class A INTERACTIVE (diagram-interactive-spine)
    ├── diagrams-interactive-spine-engine.js        upstream engine — consumed verbatim, DO NOT EDIT
    ├── diagrams-interactive-spine.css              upstream style layer — consumed verbatim, DO NOT EDIT
    ├── export-png.js                               upstream PNG export (interactive) — verbatim, DO NOT EDIT
    ├── urban-observatory_ia-state-spine.html       UO chrome (loads ../_dsa-tokens/)
    └── urban-observatory_ia-state-spine.data.js    UO data (window.IA_STATE_SPINE)
```

All three diagrams share one pinned `_dsa-tokens/` mirror. The two **static**
diagrams (architecture tree, ontology) sit at top level and load
`colors_and_type.css` + `diagrams.css`. The **interactive** IA spine sits in
`interactive/` and additionally loads `spectral-state.css` (load order:
`colors_and_type.css → spectral-state.css → diagrams-interactive-spine.css`); it
references the shared mirror one level up at `../_dsa-tokens/`. The interactive
surface is the only one that consumes Spectral State; **color encodes state only**.

### Live navigation surface

- `index.html` — ASK-branded live navigation surface for this folder's three diagram pages. It consumes the local Tier 1 + Tier 2 mirror and vendored `_dsa-surface/` carriers; its locally assigned Tier 3 does not propagate into any of the three diagrams.
- `_dsa-surface/` — pinned, byte-identical `surface-shell`, `surface-panel`, `surface-action` and `surface-text-link` carriers, the optional `surface-shell.js` navigation runtime, and the mode-aware ASK wordmark pair, all used only by `index.html`. `surface-shell.js` is vendored because that surface **adopts** the shell's responsive navigation; the three diagram pages adopt none of it and load none of these files. `surface-text-link.css` is vendored as the fourth Foundations sibling but is deliberately **not** linked: it is opt-in by class, and `index.html` currently carries no unboxed textual link that qualifies — its breadcrumb links are styled by `surface-shell.css`'s own rule, its routes are full-panel links, and its footer destinations are compact actions.

## Consumption discipline

- **Consume by reference; no fork.** The engine, `diagrams.css`, and
  `export-png.js` are copied **verbatim** from the upstream pattern and are
  **never edited** here — modifying them breaks inheritance. UO authors **only**
  source data (`window.TREE_*` for the static diagrams, `window.IA_STATE_SPINE`
  for the interactive one) and HTML chrome (`.mark`, title, subtitle, `.stamp`,
  legend, `<title>`, `<meta>`, file names).
- **Pinned, offline, no CDN.** `_dsa-tokens/` is a pinned snapshot
  (`MANIFEST.md` records the commit SHA + per-file sha256). The diagrams inherit
  at generation time and **freeze for audit** — no runtime fetch, no font CDN.
- **Tier 1 + Tier 2 only, in the diagrams.** All three diagram artifacts remain
  Tier 1 + Tier 2; no ASK **Tier 3** leaks into them. The exception is the
  separate live navigation surface below: `index.html` carries an ASK-assigned
  Tier-3 value for the current UO front door only. That value does **not**
  propagate into the diagrams, does **not** make UO ASK-the-entity, and does
  **not** come from `surface-shell`, which ships a mark slot and no mark. Any
  future independent urban-observatory brand is a separate identity migration.
- **Light + dark both work** (verified for the architecture tree, both themes).
- **Pin:** see [`_dsa-tokens/MANIFEST.md`](_dsa-tokens/MANIFEST.md) for the current
  upstream pin (single source of truth — this README does not duplicate fast-aging pin state).
- **Renderer generation.** The current diagram renderer contract combines the DS panel-aware
  fit helper (#77/#79), the dynamic interaction floor in the H and interactive-spine engines
  (#78), and the static page exporter through #80. Exact owner pins and propagation state live
  in the operator consumer ledger.

## Theme by embedding surface

Adopted from the [design-system-ASK](https://github.com/apexSolarKiss/design-system-ASK) convention ***Theme by embedding surface***, pinned at
design-system-ASK `main` **`7921b79`** (PR #49, merged 2026-06-21). This is a visual-consumption
convention, not an engine/CSS/token change — it only settles which existing theme variant a surface
embeds. Both `-light` and `-dark` exports are always generated and retained; the surface selects the
default, and a stated local exception may override per figure.

**UO default:**

- **Repository documentation embeds dark** — these in-repo diagrams (the `diagram-static-H`
  architecture tree and ontology; the `diagram-interactive-spine` static export) are repository
  documentation and default to **dark**.
- **Editorial / Substack embeds light** — if a UO diagram is ever published in a Substack or other
  long-form editorial piece, that figure defaults to **light**.
- **Both exports retained; a stated local exception may override** a specific figure.

UO currently commits **no rasters** — the diagrams are live `.html` that export a poster PNG on
demand (the `PNG` button), so there is nothing to re-select today. The default governs which export
is embedded when a raster is committed or published going forward. (Convention owner:
design-system-ASK; UO owns its adoption record and which render each UO surface embeds.)

## Viewing

Open any diagram `.html` directly in a browser (it loads its CSS/JS/fonts from
this directory and the pinned `_dsa-tokens/` mirror — no server required). Pan by
dragging, zoom with the wheel or the HUD, fit with `⤢`, and export a poster PNG
with the `PNG` button.

## Re-syncing

When the upstream tokens/fonts (or, later, Spectral State) change and a refresh
is wanted, re-sync `_dsa-tokens/` from the new commit, regenerate `MANIFEST.md`,
and bump the affected diagram's `source-vN` / `render-vN` stamp. Propose changes
to the tokens themselves upstream at the [`design-system-ASK`](https://github.com/apexSolarKiss/design-system-ASK) control surface —
never edit the vendored mirror or the upstream engine/CSS here.
