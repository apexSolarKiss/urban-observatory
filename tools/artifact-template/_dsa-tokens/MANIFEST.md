# _dsa-tokens / MANIFEST

Generated snapshot. Do not hand-edit. Refreshed only by the procedure in
`tools/artifact-template/README.md`, "Re-syncing the token snapshot".

| Field | Value |
| --- | --- |
| upstream | https://github.com/apexSolarKiss/design-system-ASK.git |
| commit | `6a824b9ea38f783aae61bd2f2d1c02497b347fea` |
| short | `6a824b9` |
| commit date | `2026-09-16 11:53:26 -0700` |
| commit subject | `docs(output-artifact): permit the logo-ASK wordmark on an explicit ASK assignment (#153)` |
| synced at | `2026-09-16` |
| consuming project | `urban-observatory` |
| files copied | `colors_and_type.css`, `fonts/InterVariable.woff2`, `fonts/InterVariable-Italic.woff2`, `fonts/JetBrainsMono.woff2`, `fonts/JetBrainsMono-Italic.woff2` |
| colors_and_type.css sha256 | `fd8207bf361eff3e4071f699b87a7f29c829a0e3605c551b5f310ae52da92e9a` |
| fonts/InterVariable.woff2 sha256 | `693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3` |
| fonts/InterVariable-Italic.woff2 sha256 | `e564f652916db6c139570fefb9524a77c4d48f30c92928de9db19b6b5c7a262a` |
| fonts/JetBrainsMono.woff2 sha256 | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |
| fonts/JetBrainsMono-Italic.woff2 sha256 | `76a805b6ea613ce2e3973f1bac6fa29db23116b2881390b59247d22890844ecc` |

**Re-sync 2026-09-16 (`28e9318` → `6a824b9`, `colors_and_type.css` only):** crosses **three** carrier-changing owner events. **#129** (`85181c11`) adds the root-only browser / under-page edge: the `--bg-edge` role, a root-only `color-scheme` on each theme path (`:root`, `:root[data-theme="dark"]` and `:root.theme-dark`, and the `prefers-color-scheme` bridge), `html { background-color: var(--bg-edge) }`, `body { background-color: transparent }`, and the base background moved from the `background` shorthand to the `background-image` longhand. **#136** (`b8d1f563`) binds the light edge to `--ask-lavender-light` instead of `--ask-white`. **#137** (`6b513cf9`) is comment-only in this carrier. Commits after `6b513cf9` up to `6a824b9` change neither `colors_and_type.css` nor `fonts/`. **Composition with this template was reviewed before the copy:** renders of synthetic documents at `28e9318` and `6a824b9`, opened from `file://` in headless Chrome, across OS light and dark × `data-theme` absent / light / dark, `.theme-dark` on the root, and print. No cell regressed against `28e9318`: `color-scheme` and the page edge matched each cell's theme, every variable resolved to that theme except in the one cell below, and pixels were unchanged beyond the variance measured between repeated renders of identical files, apart from the browser-drawn page scrollbar, which now follows the theme. One incoherence exists at both pins and is not introduced by this copy: with `.theme-dark` on the root under an OS light scheme, the template's `--artifact-line`, `--artifact-line-soft`, `--uo-code-bg` and `--uo-soft-bg` stay light. Only `colors_and_type.css` changed (sha256 `acd76409…` → `fd8207bf…`, 13,375 → 15,463 B; new value in the field table); the four font files are **byte-identical** between `28e9318` and `6a824b9` (same hashes). **No frozen/sealed artifact regenerated**; renders made after this re-sync use the new pin.

**Prior re-sync 2026-08-14 (`3d8b113` → `28e9318`, `colors_and_type.css` only):** crosses **three** carrier-changing owner events. **#93** (`410b3980`) — comment/contract only: `--fg-high-contrast` moves from a *reserved* value with no approved surface to its **first approved bounded use** (the Class B message-archive ramp); no token value changed. **#103** (`8fbb0c01`) — the **value-bearing** event: `--fg-on-card` is rebound `var(--fg-1)` → `var(--fg-high-contrast)` (`#201D26`) and **both** dark-mode `--fg-on-card: var(--ask-lavender-dark)` overrides (the `[data-theme="dark"]` block and the `prefers-color-scheme` auto-bridge) are **removed**, so the role stops flipping with theme against the fixed `--surface-solid` fill it exists to sit on. **#104** (`28e93188`) — comment/contract only, and the **final vendoring pin**: it retains #103's value unchanged and replaces the bounded-use prose with the central **registered-use and admission-gate contract** for `--fg-high-contrast`. **Render-neutral for this Class B artifact-template by non-use:** nothing here reads `var(--fg-on-card)` (verified), and the carrier itself never consumes it — neutrality is by non-use, not because the change is comment-only. Only `colors_and_type.css` changed (sha256 `246aae65…` → `acd76409…`, 13,022 → 13,375 B; new value in the field table); the four font files are **byte-identical** between `3d8b113` and `28e9318` (same hashes). **One consumer-owned edit accompanied this re-sync, outside the mirror:** `artifact.template.html` carried a local `--fg-on-card: var(--ask-lavender-dark);` in its copied dark block, whose selector `:root:not([data-theme="light"])` has **higher specificity** than the owner's plain `:root`, so it overrode the owner binding whenever it matched — regardless of source order — silently re-creating locally the theme flip #103 removed. That single declaration was deleted; no other template byte changed. **No frozen/sealed artifact regenerated** — future renders pick up the current tokens.

**Prior re-sync 2026-07-23 (`1231d03` → `3d8b113`, `colors_and_type.css` only):** picks up design-system PR **#88** — a **comment-only** correction of the tier-model header in `colors_and_type.css` (no token value, role name, selector, `@font-face`, theme behavior, or rendered-output change). The `--ask-*` variable prefix is reclassified from Tier 3 to the canonical **Tier-2 implementation namespace** — it travels with Tier 2 by reference and does not itself create Tier 3 identity; **Tier 3** is the ASK name + `logo-ASK` wordmark; and the file header identifies the **owner carrier for provenance**, not child-instance identity, so this vendored mirror does not inherit ASK's Tier 3 by carrying the header. Only `colors_and_type.css` changed (sha256 `bcd11e0e…` → `246aae65…`, new value in the field table); the four font files are byte-identical to the `1231d03` snapshot (same hashes). **No frozen/sealed artifact regenerated** — future renders pick up the current tokens.

**Prior re-sync 2026-06-26 (`040e7ca` → `1231d03`):** token catch-up bringing this mirror current with the foundation (it had been deferred at the pre-#52 `040e7ca` snapshot). Crosses design-system **#52** (light-mode foreground conformance: `--ask-white` relabel, `--ask-fg-light` / `--fg-high-contrast` added, `--fg-on-card` / `.bg-ask-light` rebind), **#53**, and **#56** (comment-only conformance). **Render-neutral for this Class B artifact-template:** the template binds prose to the foundation `--fg-*` and forbids a local `--fg` rebind, so it uses none of the rebind-affected roles (`--fg-on-card` / `.bg-ask-light`) and `--fg-1` still resolves to `#6A637F` (verified before/after). Only `colors_and_type.css` changed (`602578ee` → `c7618b2d`; sha256 `bcd11e0efeae2851c8653a425f94a76cb6423c770e23cb18b3a0315519a7375f` at that event); the four font files are byte-identical to the `040e7ca` snapshot (same hashes). **No frozen/sealed artifact regenerated** — future renders pick up the current tokens. See the handoff `sources of intent/2026-06-26_design-system-ASK_to_urban-observatory_vendored-css-comment-resync.md` and the absorption record in `scratch/`.

**Prior re-sync 2026-06-04 (`3395833` → `040e7ca`):** foundation light-mode foreground ramp (design-system PR #18 / `f9eed18`) + Class B v2 `output-artifact` contract; the local `--fg-*` rebind was dropped (foreground inherited from the foundation) and the local `--line-*` light rebind replaced by the Class B-scoped `--artifact-line` / `--artifact-line-soft` overlay. Handoff `…token-resync-class-b-v2-handoff.md`.

## Binding

This manifest binds the token snapshot in this directory to a known upstream
`design-system-ASK` state. `build.py` verifies every file listed above against
its sha256 before it seals, and records this manifest's commit in each render's
seal line and package MANIFEST only when every file matches. The commit row
itself is established by the re-sync that wrote this manifest and its review;
`build.py` does not re-check it against `design-system-ASK`.

A sealed artifact keeps the pin it was sealed with. It is never regenerated to
track a newer snapshot; renders made after a re-sync use the new pin.

Final HTML packets are frozen review artifacts. They do not hot-link to
live `design-system-ASK` CSS. The mirror exists to prevent that.

## Files in this snapshot

```text
_dsa-tokens/
├── MANIFEST.md                        this file
├── colors_and_type.css                Tier 1 + Tier 2 tokens (upstream verbatim)
└── fonts/
    ├── InterVariable.woff2            Inter (interface + display), OFL
    ├── InterVariable-Italic.woff2
    ├── JetBrainsMono.woff2            JetBrains Mono (code + technical), OFL
    └── JetBrainsMono-Italic.woff2
```

## Do not hand-edit

- Any file in `_dsa-tokens/` (including this manifest) is overwritten on the next sync.
- Local changes are silently lost.
- To pick up upstream changes (palette, type, radii, surface opacity, motion), follow `tools/artifact-template/README.md`, "Re-syncing the token snapshot".
- To propose changes to the tokens themselves, take them to `design-system-ASK`.
