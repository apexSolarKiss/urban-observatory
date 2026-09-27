# _dsa-surface / MANIFEST

Generated snapshot. Do not hand-edit. Refreshed only by the procedure in
`tools/artifact-template/README.md`, "Re-syncing the token snapshot", in the same operation as `../_dsa-tokens/`.

| Field | Value |
| --- | --- |
| upstream | https://github.com/apexSolarKiss/design-system-ASK.git |
| commit | `d374ea45270055dacf6815e527a4ae7cbe2862da` |
| short | `d374ea4` |
| commit date | `2026-09-26 22:16:42 -0700` |
| commit subject | `surfaces: main + inspector, document locators and end-anchored action rows (PRG-019) (#164)` |
| synced at | `2026-09-27` |
| consuming project | `urban-observatory` |
| files copied | `surface-panel.css`, `surface-text-link.css`, `surface-document.css`, `surface-treatments.css` |
| surface-panel.css sha256 | `883e24ac5407a4fe24f9149b0d8964a06995cc88b6b6150b1a1bdfd9aee2976e` |
| surface-text-link.css sha256 | `cf3d6061c885df9d48fcd8e92b3d4b5f02f3a07ac0ef3057b29885b5931e7d82` |
| surface-document.css sha256 | `e6999aba3697865049854288e3bdb1efcb50a166258261e05e199ebc9474eb70` |
| surface-treatments.css sha256 | `d0bd9918f7f2276446c28023d6501b77dad6a902bc787c235852527fd35e136b` |

**Created 2026-09-25 at U6.** The design-system-ASK document register: the four modules the owner's sealed-use rule inlines after the
foundation, in this order: `surface-panel.css`, `surface-text-link.css`, `surface-document.css`, `surface-treatments.css`. They are
copied verbatim from the commit above. `surface-document-overflow.js` is not copied: a sealed review document carries no script.

**Re-sync 2026-09-27 (`c5f5f6e` → `d374ea4`, `surface-document.css` only):** crosses one carrier-changing owner event, **#164**
(`d374ea4`). It adds one opt-in rule, `.doc-actions--end`, which this renderer does not adopt: it emits no `.doc-actions`, and the
final-HTML allowlist refuses both classes. The rest of the change is comment text (catalog entries, the load-order note and rule
comments), with no render effect.
`surface-document-overflow.js` is still not copied. The other three modules are byte-identical at both commits (same hashes).
`surface-document.css` sha256 `c2f90dc7…` → `e6999aba…`, 49,308 → 57,701 B. **No frozen/sealed artifact regenerated**; renders made
after this re-sync use the new pin.

**Prior re-sync 2026-09-26 (`c7de5ff` → `c5f5f6e`, `surface-document.css` only):** crosses one carrier-changing owner event, **#163**
(`c5f5f6e`). It adds an opt-in table composition keyed on `.doc-table-scroll`, which this renderer does not adopt: it emits none of
the composition's classes, the final-HTML allowlist refuses them, and UO's tables keep their own geometry. It also sets inline code
inside a `.doc-label` in its source case, with no marker: code in a table header, and in that header's repeated label in each body
cell, no longer renders in capitals, while the label's own text keeps them. `surface-document-overflow.js` is still not copied. The
other three modules are byte-identical at both commits (same hashes). `surface-document.css` sha256 `7f875b9e…` → `c2f90dc7…`,
41,470 → 49,308 B. **No frozen/sealed artifact regenerated**; renders made after this re-sync use the new pin.

## Binding

`build.py` verifies every file above against its sha256 before it seals, and inlines each one byte for byte, in the order above, after
the token CSS. The commit row must equal `../_dsa-tokens/MANIFEST.md`'s: the build fails when the two pins differ, so the register is
never sealed against a foundation from another design-system state. The commit row itself is established by the re-sync that wrote this
manifest and its review; `build.py` does not re-check it against `design-system-ASK`.

A sealed artifact keeps the pin it was sealed with. It is never regenerated to track a newer snapshot.

## Files in this snapshot

```text
_dsa-surface/
├── MANIFEST.md              this file
├── surface-panel.css        panel material, attachment and elevation (upstream verbatim)
├── surface-text-link.css    governed links and the contents list (upstream verbatim)
├── surface-document.css     the document register: roles, rails, compositions (upstream verbatim)
└── surface-treatments.css   disclosure, emphasis rail and chip, panel treatments (upstream verbatim)
```

## Do not hand-edit

- Any file here, this manifest included, is overwritten on the next sync; a local change is silently lost.
- To propose changes to the register itself, take them to `design-system-ASK`.
