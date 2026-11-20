# _dsa-surface / MANIFEST

Generated snapshot. Do not hand-edit. Refreshed only by the procedure in
`tools/artifact-template/README.md`, "Re-syncing the token snapshot", in the same operation as `../_dsa-tokens/`.

| Field | Value |
| --- | --- |
| upstream | https://github.com/apexSolarKiss/design-system-ASK.git |
| commit | `aa7bfb00df9ac7f80b15ab118ff1c46403f265db` |
| short | `aa7bfb0` |
| commit date | `2026-11-19 15:22:10 -0800` |
| commit subject | `fix(review): reword two comment passages that a consumer's style scan rejects (#230)` |
| synced at | `2026-11-19` |
| consuming project | `urban-observatory` |
| files copied | `surface-panel.css`, `surface-text-link.css`, `surface-document.css`, `surface-treatments.css`, `spectral-state.css`, `evidence-state.css`, `review-semantics.css` |
| surface-panel.css sha256 | `883e24ac5407a4fe24f9149b0d8964a06995cc88b6b6150b1a1bdfd9aee2976e` |
| surface-text-link.css sha256 | `9a6acf457ffbe2a0bb31ae28507855b6446195ff9dcd3cc7112f04ec5bf0fce3` |
| surface-document.css sha256 | `57140e0d5383f95d4d88001e535c682d0c47152e2165e92516ece2ba4cf999ed` |
| surface-treatments.css sha256 | `ae03dda052475be5d6ea14e0fab8dd3f1608fdf5b9d09b4859a1f146a08fc0dc` |
| spectral-state.css sha256 | `770324231461b629d18a0b41c4beecb9b5015e203f6a49b2e84ef56bc29020cf` |
| evidence-state.css sha256 | `7467c69aa4da4220792132d338ef3fc937ecfcf44cfdbe5f167c4b4ddea4957d` |
| review-semantics.css sha256 | `347ea6cf5886171a4e00c81144e935c6c824a7e76ffc63fd94d01c6288fe5bcc` |

**Created 2026-09-25 at U6.** The design-system-ASK document register: the four modules the owner's sealed-use rule inlines after the
foundation, in this order: `surface-panel.css`, `surface-text-link.css`, `surface-document.css`, `surface-treatments.css`. They are
copied verbatim from the commit above. `surface-document-overflow.js` is not copied: a sealed review document carries no script.

**Re-sync 2026-11-19 (`842f272` → `aa7bfb0`; one register module and three semantic-state modules change):**
crosses the owner events **#224–#230**. **#224–#226** and **#228** change no file this renderer vendors; **#227**, **#229** and
**#230** do. At **#227** (`ccb9cda`) `surface-treatments.css` adds the marker tokens and `.surface-marker` classes, the rail-paint
color names `--surface-rail-paint-green`, `-yellow` and `-red`, still `none` in every theme, with the earlier names kept as
aliases, and the ink on brown, `--surface-fill-ink-on-brown`; `spectral-state.css` (v1.4) adds the keyed state label,
`.state-label`, and the range it opens; `evidence-state.css` (v0.4) adds each role's ink and the keyed evidence label,
`.evidence-label`, with its range; and `review-semantics.css` adds the filled decision record, `.review-record`, and its inks,
reads the existing marks' size, corners and hollow edge from the marker tokens at the values it wrote before (10px, 50%, 2px and
2px), and binds an accepted or declined range to the new rail-paint names, which resolve to the same `none`. At **#229**
(`a6f48fb`) `surface-treatments.css` adds PERIMETER PAINT, `.surface-perimeter`, whose color `--surface-perimeter-color` is
registered with `@property` as non-inheriting, and the content-emphasis panel now draws its edge, ring and bloom through the same
rule; `review-semantics.css` (v0.3) makes a decision record shown on its own a panel. At **#230** (`aa7bfb0`)
`review-semantics.css` changes in comment text only: its rules are byte-identical to #229's with comments removed, and its comments
no longer match this build's resource-function refusal, which #229's matched twice. This renderer adopts none of the additions: it
emits no `.surface-marker`, `.surface-perimeter`, `.state-label`, `.evidence-label`, `.review-record` or fill class, and the
final-HTML allowlist admits no class set that carries one. The composition's classes, attributes and `data-review`,
`data-evidence` and `data-state` values are unchanged. The one resolved value that changes is the foundation's brown, at #227 in
`../_dsa-tokens/colors_and_type.css`, which `evidence-state.css` reads for the weakened role.

Measured on renders of synthetic sources at both pins in headless Chrome 157, light and dark, at 1280 and 390 wide: a document
without annotations that carries both banners, and an annotated document that carries both banners and every state and evidence
role. Every element's computed style is identical at both pins, except the Weakened mark's dot. The two banners' border, ring and
bloom compute the same, cyan and violet, and their pixels do not change. The only differing pixels are the Weakened mark's dot,
`rgb(177, 122, 67)` → `rgb(137, 85, 56)` (`#B17A43` → `#895538`) in both themes, and the seal line's design-system pin. Every
render passes the final-HTML check, with no match for the resource-function refusal. The four files are copied verbatim from the
commit above:

- `surface-treatments.css` sha256 `272bb52c…` → `ae03dda0…`, 55,223 → 69,299 B;
- `spectral-state.css` sha256 `d93aa47a…` → `77032423…`, 6,581 → 11,065 B;
- `evidence-state.css` sha256 `9d70966f…` → `7467c69a…`, 5,060 → 11,225 B;
- `review-semantics.css` sha256 `1647f1d5…` → `347ea6cf…`, 33,137 → 44,233 B.

`surface-panel.css`, `surface-text-link.css` and `surface-document.css` are byte-identical at both commits (same hashes).
`surface-document-overflow.js` is still not copied, and `criterion-assessment.css`, which #227 also changes, `three-functions.css`
and the new `surface-cta.css` are not vendored. **No frozen/sealed artifact regenerated**; renders made after this re-sync use the
new pin.

**Prior re-sync 2026-11-17 (`e88e92b` → `842f272`; two register modules and two semantic-state modules change, and one more in comment text only):**
crosses the owner events **#213–#223**. **#213**, **#215–#218**, **#220** and **#221** change no file this renderer vendors; **#214**,
**#219**, **#222** and **#223** do. `surface-document.css` changes at **#214** (`1f5461f`): it adds the ordered sequence,
`.doc-sequence` on a list and `.doc-sequence-step` on each step, with a print rule that keeps a step whole, and it declares the
hierarchy rail's geometry once for `.doc-hierarchy` and `.doc-sequence`, so `.doc-hierarchy` keeps its declarations. This renderer
does not adopt the sequence: it emits no `.doc-sequence`, and the final-HTML allowlist admits no class set that carries it.
`spectral-state.css` changes at **#219** (`ea0057c`): every role takes one value in both themes (Spectral State v1.2), so
accepted and declined, which take the earned and deflated values, no longer change with the theme; and it adds the
`--state-*-ink` bindings to the fill paint, which nothing here reads. At **#223** (`842f272`) it reads its four health-ramp values
from the foundation's reserved state values (v1.3), with no value changed. `evidence-state.css` changes at the same two events:
weakened takes `hsl(30, 45%, 48%)` and not-yet-testable `hsl(264, 8%, 53%)` in both themes (v0.2), read from the foundation at
#223 (v0.3); the three roles it reuses follow Spectral State. `surface-treatments.css` changes at **#219**: it adds the fill paint
(`.surface-fill`, `.surface-fill-ink`, `.surface-fill--neutral` and the `--surface-fill-*` inks), which this renderer does not
adopt; a bordered label's dark edge reinforcement goes from 0.5px to 0, so a review mark, neutral label or emphasis chip draws
the plain 1px border under a dark theme; and the structural rail paint becomes `none` everywhere, which nothing here binds. At
**#222** (`b6dc02c`) it changes the orange and cyan inks, which nothing here reads. `review-semantics.css` changes at **#219** in
comment text only; its rules are byte-identical with comments removed, so the composition's classes, attributes and `data-review`
values are unchanged. The modules' load order (tokens, the four register modules ending with `surface-treatments.css`, then
`spectral-state.css`, `evidence-state.css` and `review-semantics.css`) satisfies the order `evidence-state.css` now states.

Measured on renders of synthetic sources at both pins in headless Chrome 157, light and dark: a document without annotations
renders identically (computed styles of all 132 elements, and screenshots, in both themes; the fixture carries no bordered label).
In an annotated document, under light accepted's green moves `rgb(17, 212, 17)` → `rgb(56, 250, 56)`, declined's red
`rgb(212, 17, 17)` → `rgb(250, 56, 56)`, and the Spectral State markers' earned green, structural yellow and partial orange
take their single values; under dark every bordered review mark loses its 0.5px reinforcement, partial's orange moves `rgb(250, 153, 56)` →
`rgb(255, 128, 0)`, and not-yet-testable's edge moves `rgb(161, 152, 174)` → `rgb(133, 126, 145)`. Open and proposed do not
change. The five files are copied verbatim from the commit above:

- `surface-document.css` sha256 `1c122ddf…` → `57140e0d…`, 82,587 → 88,017 B;
- `surface-treatments.css` sha256 `a277e97e…` → `272bb52c…`, 48,906 → 55,223 B;
- `spectral-state.css` sha256 `dd30fdc0…` → `d93aa47a…`, 5,235 → 6,581 B;
- `evidence-state.css` sha256 `1256fb8c…` → `9d70966f…`, 4,362 → 5,060 B;
- `review-semantics.css` sha256 `74345c46…` → `1647f1d5…`, 33,109 → 33,137 B.

`surface-panel.css` and `surface-text-link.css` are byte-identical at both commits (same hashes). `surface-document-overflow.js` is
still not copied, and `criterion-assessment.css` and `three-functions.css` are not vendored. **No frozen/sealed artifact
regenerated**; renders made after this re-sync use the new pin.

**Prior re-sync 2026-11-12 (`e84394b` → `e88e92b`; no byte change):**
crosses the owner event **#212**, which changes no file in this snapshot. The commit row moves only to keep this snapshot and
`../_dsa-tokens/` at one commit, which the build requires; at this re-sync that snapshot's `colors_and_type.css` changes at
**#212** (`e88e92b`). `surface-panel.css`, `surface-text-link.css`, `surface-document.css`, `surface-treatments.css`,
`spectral-state.css`, `evidence-state.css` and `review-semantics.css` are byte-identical at both commits (same hashes).
`surface-document-overflow.js` is still not copied. **No frozen/sealed artifact regenerated**; renders made after this re-sync
use the new pin.

**Prior re-sync 2026-11-11 (`8fbda72` → `e84394b`; one register module changes):**
crosses the owner events **#209–#211**. **#209** and **#210** change no file this renderer vendors; only **#211** does.
`surface-document.css` changes at **#211** (`e84394b`): a `.doc-pre` or `.doc-table-scroll` that shows keyboard focus draws a
2px `--fg-1` outline `--space-1` out, and its edge fade is dropped while focus shows; it adds an opt-in marker for a compact
narrative table, `table.doc-compact-table`, which takes no measure; and the 32rem measure rule, still at zero specificity inside
`:where()`, now leaves out a compact table and keeps a comparison table's measure even when it is marked compact; the rest of the
change is comment text. This renderer does not adopt the compact marker: the final-HTML allowlist admits only `doc-dense-table`
on a `table`, and the renderer emits no `.doc-table-scroll`, so neither the marker nor the measure rule matches anything here.
The focus rule reaches new renders: the renderer emits `pre.doc-pre`, and a structured block as `div.doc-pre`, and both scroll on
screen (`overflow-x: auto`; this renderer's `pre-wrap` applies in print only), so where a browser makes a scrolling block
focusable, keyboard focus on it draws the 2px `--fg-1` outline. That is the owner's intended change. A sealed document carries
no script, so no overflow attribute is set and no edge fade is drawn for focus to drop. `surface-panel.css`,
`surface-text-link.css`, `surface-treatments.css`, `spectral-state.css`, `evidence-state.css` and `review-semantics.css` are
byte-identical at both commits (same hashes). The one file is copied verbatim from the commit above:

- `surface-document.css` sha256 `d0c67bed…` → `1c122ddf…`, 79,800 → 82,587 B.

`surface-document-overflow.js` is still not copied. **No frozen/sealed artifact regenerated**; renders made after this re-sync
use the new pin.

**Prior re-sync 2026-11-11 (`14e1bb0` → `8fbda72`; two register modules change):**
crosses the owner events **#205–#208**. **#205** and **#207** change no file this renderer vendors; only **#206** and **#208** do.
`surface-treatments.css` changes at **#206** (`241ca4a`): the structural rail paint is now dosed per field rather than per theme,
and a root that declares a `data-surface-field` other than `ask-lavender` sets `--surface-rail-paint-structural` to `none`; the
rest of the change is comment text. This renderer declares no `data-surface-field`, and nothing it vendors binds the structural
paint: Review Semantics binds an accepted range to the earned paint and a declined range to the deflated paint, and only
Criterion Assessment, which is not vendored, binds the structural one. `surface-document.css` changes at **#208** (`8fbda72`):
in print, a `.doc-pre` or `.doc-table-scroll` that carries the overflow helper's attributes draws neither the scroll label nor
the edge fade; the rest of the change is comment text. A sealed document carries no script, so no overflow attribute is ever
set and the print rule matches nothing here. `surface-panel.css`, `surface-text-link.css`, `spectral-state.css`,
`evidence-state.css` and `review-semantics.css` are byte-identical at both commits (same hashes). The two files are copied
verbatim from the commit above:

- `surface-document.css` sha256 `fc912a50…` → `d0c67bed…`, 78,786 → 79,800 B;
- `surface-treatments.css` sha256 `ee6f1dc6…` → `a277e97e…`, 47,403 → 48,906 B.

`surface-document-overflow.js` is still not copied, and `criterion-assessment.css`, which #206 also changes, is not vendored. **No
frozen/sealed artifact regenerated**; renders made after this re-sync use the new pin.

**Prior re-sync 2026-11-06 (`705a195` → `14e1bb0`; two register modules and one semantic-state module change):**
crosses the owner events **#186–#204**. **#186–#202** change no file this renderer vendors; only **#203** and **#204** do.
`surface-document.css` changes at **#203** (`021bb2a`): it adds the `.doc-section > .doc-flow` lead, for a flow of peer parts
nested in a section, which this renderer's markup does not match: its one `.doc-flow` is the `main` element, never a child of a
`.doc-section`. At **#204** (`14e1bb0`) it adds the comparison-table composition (`.doc-compare-table` in a `.doc-table-scroll`,
with its assessment rails), which this renderer does not adopt: it emits none of the composition's classes, and the final-HTML
allowlist refuses them. `surface-treatments.css` changes at **#204**: it adds the rail-paint variables on the root
(`--surface-rail-paint-earned`, `--surface-rail-paint-structural` and `--surface-rail-paint-deflated`), and the labeled range's
rail now sets its own `color` to the range's color and draws its 2px stroke in `currentColor`, with a `box-shadow` from
`--surface-labeled-range-paint`, else `none`. `review-semantics.css` changes at **#204**: an accepted range binds
`--surface-labeled-range-paint` to `--surface-rail-paint-earned` and a declined range to `--surface-rail-paint-deflated`; both
are `none` in every theme, so the bindings resolve to no paint. The composition's classes, attributes and `data-review` values
are unchanged. `surface-panel.css`, `surface-text-link.css`, `spectral-state.css` and `evidence-state.css` are byte-identical
at both commits (same hashes). The three files are copied verbatim from the commit above:

- `surface-document.css` sha256 `7dbc3922…` → `fc912a50…`, 59,833 → 78,786 B;
- `surface-treatments.css` sha256 `836f5957…` → `ee6f1dc6…`, 42,117 → 47,403 B;
- `review-semantics.css` sha256 `13e0debf…` → `74345c46…`, 32,642 → 33,109 B.

`surface-document-overflow.js` is still not copied, and `criterion-assessment.css`, which #204 adds, is not vendored. **No
frozen/sealed artifact regenerated**; renders made after this re-sync use the new pin.

**Prior re-sync 2026-10-21 (`53fa86e` → `705a195`; three semantic-state modules added, three register modules change):**
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
