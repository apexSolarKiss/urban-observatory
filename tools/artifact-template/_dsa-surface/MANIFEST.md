# _dsa-surface / MANIFEST

Generated snapshot. Do not hand-edit. Refreshed only by the procedure in
`tools/artifact-template/README.md`, "Re-syncing the token snapshot", in the same operation as `../_dsa-tokens/`.

| Field | Value |
| --- | --- |
| upstream | https://github.com/apexSolarKiss/design-system-ASK.git |
| commit | `705a1958cc763ebd008392d696a286e8abe4e765` |
| short | `705a195` |
| commit date | `2026-10-15 09:36:14 -0700` |
| commit subject | `treatments + semantics: exact words take a scope underline, a whole list item becomes its own range, and Open question takes the emphasis cyan (#185)` |
| synced at | `2026-10-21` |
| consuming project | `urban-observatory` |
| files copied | `surface-panel.css`, `surface-text-link.css`, `surface-document.css`, `surface-treatments.css`, `spectral-state.css`, `evidence-state.css`, `review-semantics.css` |
| surface-panel.css sha256 | `883e24ac5407a4fe24f9149b0d8964a06995cc88b6b6150b1a1bdfd9aee2976e` |
| surface-text-link.css sha256 | `9a6acf457ffbe2a0bb31ae28507855b6446195ff9dcd3cc7112f04ec5bf0fce3` |
| surface-document.css sha256 | `7dbc392202aab5bb3f849f2947e585f7a6c4bccd7d8cd09171a6e12bd05bf888` |
| surface-treatments.css sha256 | `836f5957d28fce2ef06c01e4aedf82f84fc92b7615bbb880bbbe43ae9f7a5e91` |
| spectral-state.css sha256 | `dd30fdc0b7b9174801129f0d01f45e22da5bbd92ff47e58d7aabaeea64f0d05b` |
| evidence-state.css sha256 | `1256fb8c9178a29aa4ee9d4b586da40087e1ea30a1264689bd9a0b4e0aab209e` |
| review-semantics.css sha256 | `13e0debf0a93d98779a3afb23f366619fb440784decc917be2f1b09d9b35d88c` |

**Created 2026-09-25 at U6.** The design-system-ASK document register: the four modules the owner's sealed-use rule inlines after the
foundation, in this order: `surface-panel.css`, `surface-text-link.css`, `surface-document.css`, `surface-treatments.css`. They are
copied verbatim from the commit above. `surface-document-overflow.js` is not copied: a sealed review document carries no script.

**Re-sync 2026-10-21 (`53fa86e` → `705a195`; three semantic-state modules added, three register modules change):**
crosses the owner events **#170–#185**. **#170–#177** change no file this renderer vendors. **#178** (`e0ee2e1`) adds
`review-semantics.css`, which carries the opt-in Review Semantics composition; **#182–#185** replace that composition's first
model, so this repo adopts it in its #185 form only and never vendored the #178 form. **#179** and **#180** change no vendored
file. `surface-text-link.css` changes at **#181** (`e198a55`) in comment text only, with no render effect.
`surface-treatments.css` changes at **#182** (`d7ee25d`: one bordered-label box for neutral labels, emphasis chips and review
marks), **#183** (`aa88830`: the labeled range's scope rail) and **#185** (`705a195`: the scope underline, the item host and the
list-edge buffer). `surface-document.css` changes at **#183**: it adds `.doc-table-scroll--range-lane`, which this renderer does
not adopt, since it emits no `.doc-table-scroll`. After #178 adds it, `review-semantics.css` changes at **#182** (a review mark's
box becomes the bordered label's; Proposed takes the emphasis magenta), **#183** (the annotation range's rail color), **#184**
(`55c6cf7`, comment text) and **#185** (the passage mark's tint is retired for the scope underline, a decided judgment keeps its
passage mark, the note's 12px attachment in a list item, and Open question takes the emphasis cyan). This re-sync adds the three
semantic-state modules: `review-semantics.css`, and `spectral-state.css` and `evidence-state.css`, which it builds on and which
are unchanged upstream in this range (their last changes are #56 and #44). When a document annotates, the three are inlined
after the four register modules in the owner's order: `spectral-state.css`, `evidence-state.css`, `review-semantics.css`
(README, "Review annotations"). Through #182 the framing, synthesis and banner chips this renderer already emits take the
shared bordered label's box with no markup change. `surface-panel.css` is byte-identical at both commits (same hash). The six
files are copied verbatim from the commit above:

- `surface-text-link.css` sha256 `cf3d6061…` → `9a6acf45…`, 7,948 → 7,921 B;
- `surface-document.css` sha256 `e6999aba…` → `7dbc3922…`, 57,701 → 59,833 B;
- `surface-treatments.css` sha256 `484e8134…` → `836f5957…`, 20,556 → 42,117 B;
- `spectral-state.css` added, sha256 `dd30fdc0…`, 5,235 B;
- `evidence-state.css` added, sha256 `1256fb8c…`, 4,362 B;
- `review-semantics.css` added, sha256 `13e0debf…`, 32,642 B.

The bytes alone do not adopt the change: with these stylesheets, the markup of the composition's first model (#178) draws no
outline on a review mark and no cue on a passage mark. The renderer's emitted markup, source grammar, final-HTML allowlist and
tests move with this re-sync (README, "Review annotations"). `surface-document-overflow.js` is still not copied. **No
frozen/sealed artifact regenerated**; renders made after this re-sync use the new pin.

**Prior re-sync 2026-10-06 (`d374ea4` → `53fa86e`, `surface-treatments.css` only):** crosses one carrier-changing owner event, **#169**
(`53fa86e`). It adds a controlled trigger to the disclosure grammar, `.surface-disclosure-trigger` on a `button`, which this
renderer does not adopt: it emits no `button`, and the final-HTML allowlist refuses both the element and the class. The rules for
the details disclosure this renderer emits keep their declarations; the summary's are split between a rule it now shares with the
controlled trigger and its own. The rest of the change is comment text, with no render effect.
`surface-document-overflow.js` is still not copied. The other three modules are byte-identical at both commits (same hashes).
`surface-treatments.css` sha256 `d0bd9918…` → `484e8134…`, 18,276 → 20,556 B. **No frozen/sealed artifact regenerated**; renders
made after this re-sync use the new pin.

**Prior re-sync 2026-09-27 (`c5f5f6e` → `d374ea4`, `surface-document.css` only):** crosses one carrier-changing owner event, **#164**
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

`build.py` verifies every file above against its sha256 before it seals, on every render. It inlines the four register modules byte
for byte, in the order above, after the token CSS, and, only in a document that annotates, the three semantic-state modules after
them, in the order above. The commit row must equal `../_dsa-tokens/MANIFEST.md`'s: the build fails when the two pins differ, so the register is
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
├── surface-treatments.css   disclosure, emphasis rail and chip, panel treatments (upstream verbatim)
├── spectral-state.css       Spectral State role values (upstream verbatim)
├── evidence-state.css       Evidence State role values (upstream verbatim)
└── review-semantics.css     Review Semantics: Review State and the annotation composition (upstream verbatim)
```

## Do not hand-edit

- Any file here, this manifest included, is overwritten on the next sync; a local change is silently lost.
- To propose changes to the register itself, take them to `design-system-ASK`.
