# _dsa-tokens / MANIFEST

Generated snapshot. **Do not hand-edit.** A pinned mirror of design-system-ASK
foundation tokens + fonts, vendored so the `docs/diagrams/` artifacts render
**offline, with no CDN and no runtime fetch** — they inherit at generation time
and freeze for audit.

This mirror is a **build input, not a fork** and not a second source of truth.
`design-system-ASK` remains upstream truth; this repo holds a pinned copy.

| Field | Value |
| --- | --- |
| upstream | https://github.com/apexSolarKiss/design-system-ASK.git |
| commit | `2bbab417863d3cffe74c7324899f494a840d69b7` |
| short | `2bbab41` |
| commit date | `2026-09-03 13:16:29 -0700` |
| commit subject | `feat(identity): add canonical ASK browser icons (#138)` |
| synced at | `2026-09-03` |
| consuming surface | `urban-observatory/docs/diagrams/` |
| scope | Tier 1 + Tier 2 only (no Tier 3) |

## Files in this snapshot

```text
_dsa-tokens/
├── MANIFEST.md                     this file
├── colors_and_type.css             Tier 1 + Tier 2 tokens + @font-face
│                                   (light default · [data-theme="dark"] · prefers-color-scheme auto-bridge)
├── spectral-state.css              Spectral State v1.1 — 8 --state-* roles (interactive spine only)
└── fonts/
    ├── InterVariable.woff2         Inter (interface + display), OFL
    ├── InterVariable-Italic.woff2
    ├── JetBrainsMono.woff2         JetBrains Mono (code + technical + tabular), OFL
    ├── JetBrainsMono-Italic.woff2
    ├── Inter-OFL.txt               SIL Open Font License (Inter)
    └── JetBrainsMono-OFL.txt       SIL Open Font License (JetBrains Mono)
```

| file | sha256 |
| --- | --- |
| `colors_and_type.css` | `fd8207bf361eff3e4071f699b87a7f29c829a0e3605c551b5f310ae52da92e9a` |
| `spectral-state.css` | `dd30fdc0b7b9174801129f0d01f45e22da5bbd92ff47e58d7aabaeea64f0d05b` |
| `fonts/InterVariable.woff2` | `693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3` |
| `fonts/InterVariable-Italic.woff2` | `e564f652916db6c139570fefb9524a77c4d48f30c92928de9db19b6b5c7a262a` |
| `fonts/JetBrainsMono.woff2` | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |
| `fonts/JetBrainsMono-Italic.woff2` | `76a805b6ea613ce2e3973f1bac6fa29db23116b2881390b59247d22890844ecc` |

**Re-sync 2026-09-03 (`28e9318` → `2bbab41`, `colors_and_type.css` only):** crosses **three** carrier-changing owner events, and is the first re-sync in this mirror's history that is **not** render-neutral. **#129** (`85181c1`) — the **structural** event: it adds the root-only `--bg-edge` Tier-1 role and a root `color-scheme` declaration, and it rewrites the base reset's `background: var(--bg-gradient)` **shorthand** into the `background-image` **longhand**, adding `html { background-color: var(--bg-edge) }` and `body { background-color: transparent }`. The shorthand had been resetting `background-color` to `transparent`, leaving the canvas with no solid layer for the browser to derive its over-scroll pocket from. **#136** (`b8d1f56`) — the **value-bearing** event: the light `--bg-edge` is rebound `var(--ask-white)` → `var(--ask-lavender-light)` (`#E2D3F0`), and `--ask-lavender-light` gains a comment naming that second duty. No existing palette value changed — `--ask-lavender-light` is `#E2D3F0` before and after; what is new is the **role**, not the colour. **#137** (`6b513cf`) — comment-only follow-through inside the same block. One file re-vendored: `colors_and_type.css` (sha256 `acd76409…` → `fd8207bf…`, 13,375 → 15,463 B; new value in the file table). `spectral-state.css` and the four fonts are **byte-identical** between `28e9318` and `2bbab41` and remain pinned at `1231d03` — this mirror stays at **mixed pins**.

**Render impact — declared, not neutral.** Two effects reach this repo's surfaces, and neither touches the composition inside the viewport. First, the **browser edge**: `html` now carries a solid `--bg-edge` under the gradient, so the over-scroll pocket resolves lavender in light and near-black in dark instead of the browser default. Second, **`color-scheme`**: the root now declares it, which is what the three diagram pages gain — `index.html` already carried `<meta name="color-scheme" content="light dark">`, the other three did not, and they now take theme-appropriate scrollbars and form-control rendering from the foundation. Both are the point of the owner change rather than a side effect of vendoring it.

**What the local sheets do to it.** `diagrams.css` and `diagrams-interactive-spine.css` each restate `body { background: var(--bg-gradient) }` as a shorthand **after** the foundation loads. That shorthand resets `background-color` to `transparent`, which happens to be exactly what the foundation now asks of `body` — so the required split holds on those pages, but it holds by coincidence rather than by intent. Neither local sheet touches `html`, so the solid edge is never overridden. Measured headless in both themes on all four surfaces: `html` `rgb(226, 211, 240)` light / `rgb(10, 9, 12)` dark, `body` `rgba(0, 0, 0, 0)` in both. **Render stamps held** (UO commits no diagram rasters; live `.html` exports on demand).

**Prior re-sync 2026-08-14 (`3d8b113` → `28e9318`, `colors_and_type.css` only):** crosses **three** carrier-changing owner events. **#93** (`410b3980`) — comment/contract only: `--fg-high-contrast` moves from a *reserved* value with no approved surface to its **first approved bounded use** (the Class B message-archive ramp); no token value changed. **#103** (`8fbb0c01`) — the **value-bearing** event: `--fg-on-card` is rebound `var(--fg-1)` → `var(--fg-high-contrast)` (`#201D26`) and **both** dark-mode `--fg-on-card: var(--ask-lavender-dark)` overrides (the `[data-theme="dark"]` block and the `prefers-color-scheme` auto-bridge) are **removed**, so the role stops flipping with theme against the fixed `--surface-solid` fill it exists to sit on. **#104** (`28e93188`) — comment/contract only, and the **final vendoring pin**: it retains #103's value unchanged and replaces the bounded-use prose with the central **registered-use and admission-gate contract** for `--fg-high-contrast`. **Render-neutral for this mirror by non-use:** nothing in `docs/diagrams/` reads `var(--fg-on-card)` (verified), and the carrier itself never consumes it — neutrality here is by non-use, not because the change is comment-only. One file re-vendored: `colors_and_type.css` (sha256 `246aae65…` → `acd76409…`, 13,022 → 13,375 B; new value in the file table). `spectral-state.css` and the four fonts are **byte-identical** between `3d8b113` and `28e9318` and remain pinned at `1231d03` — this mirror stays at **mixed pins**. **Render stamps held** (UO commits no diagram rasters; live `.html` exports on demand).

**Prior re-sync 2026-07-23 (`1231d03` → `3d8b113`, `colors_and_type.css` only):** picks up design-system PR **#88** — a **comment-only** correction of the tier-model header in `colors_and_type.css` (no token value, role name, selector, `@font-face`, theme behavior, or rendered-output change). The `--ask-*` variable prefix is reclassified from Tier 3 to the canonical **Tier-2 implementation namespace** — it travels with Tier 2 by reference and does not itself create Tier 3 identity; **Tier 3** is the ASK name + `logo-ASK` wordmark; and the file header identifies the **owner carrier for provenance**, not child-instance identity, so this vendored mirror does not inherit ASK's Tier 3 by carrying the header. One file re-vendored: `colors_and_type.css` (sha256 `bcd11e0e…` → `246aae65…`, new value in the file table). `spectral-state.css` and the four fonts are **byte-identical** to the `1231d03` snapshot and remain pinned there — this mirror is now at **mixed pins**. **Render-neutral:** the stylesheet is `<link>`ed, never inlined, so the changed comment enters no committed HTML or raster. **Render stamps held** (UO commits no diagram rasters; live `.html` exports on demand).

**Prior re-sync 2026-06-26 (`b5d158e` → `1231d03`):** picks up design-system PR **#56** — a **comment-only** conformance cleanup of the vendored token files (no token value, role name, selector, theme behavior, or rendered-output change). `colors_and_type.css`: "five-color core" → "a core identity set"; "Core 5 — backgrounds + text" → "Core set — backgrounds, wordmark, dark-mode text". `spectral-state.css`: "each mapped to a neon hue" → "eight roles: seven sparse neon state signals plus a neutral role that resolves to the theme foreground" (`--state-neutral = var(--fg-1)`, not a neon). **Render-neutral:** light `--fg-1` still resolves to `#6A637F`, dark unchanged, `--state-neutral = var(--fg-1)` unchanged — comment text + file hashes only differ. Two files re-vendored: `colors_and_type.css` (`8b8917e5` → `c7618b2d`, sha256 `bcd11e0efeae2851c8653a425f94a76cb6423c770e23cb18b3a0315519a7375f` at that event) and `spectral-state.css` (`566bf14d` → `b82083d2`, sha256 `dd30fdc0b7b9174801129f0d01f45e22da5bbd92ff47e58d7aabaeea64f0d05b` at that event); the four fonts are byte-identical to the `b5d158e` snapshot. **Render stamps held** (UO commits no diagram rasters; live `.html` exports on demand). See the handoff `sources of intent/2026-06-26_design-system-ASK_to_urban-observatory_vendored-css-comment-resync.md` and the absorption record in `scratch/`.

**Prior re-sync 2026-06-26 (`20fc5d6` → `b5d158e`):** design-system PR **#52** (light-mode foreground conformance — white = wordmark pairing only; `#6A637F` = canonical default light foreground / the approved dark purple; `#201D26` = reserved opt-in high-contrast) + **#53** (`diagrams.css` aliases `--diagram-ink/-muted/-faint` → foundation `--fg-1/-2/-3`). Render-neutral. Handoff `…foreground-conformance-resync.md`.

## Scope note — static vs interactive load

This mirror carries `colors_and_type.css` + fonts (everything the **static**
Class A diagrams need, `diagram-static-H`) **and** `spectral-state.css` (Spectral
State v1.1), required by the **interactive** IA spine (`diagram-interactive-spine`,
in `../interactive/`). Now at **mixed pins**: `colors_and_type.css` @ `2bbab41` (DS #137);
`spectral-state.css` + the four fonts @ `1231d03` (prior `b5d158e`) — see the
field table and the re-sync notes.

**Static scaffolds do NOT load `spectral-state.css`** — only the interactive
spine does, in load order `colors_and_type.css → spectral-state.css →
diagrams-interactive-spine.css`. Color on the interactive surface encodes
**state only**.

## Binding

This manifest binds the rendered diagram files in `docs/diagrams/` to a known
upstream `design-system-ASK` state (current pins: `colors_and_type.css` @ `2bbab41`, `spectral-state.css` + fonts @ `1231d03`; prior `b5d158e`). The diagram `<head>` records the
`source-vN` / `render-vN` stamp; this manifest records the upstream pin. If the
two diverge, the diagram is reading tokens that have drifted from its audit point.

The diagram files do **not** hot-link to live `design-system-ASK` CSS or to any
font CDN. This mirror exists to prevent that.

## Do not hand-edit

- Any file in `_dsa-tokens/` (including this manifest) is overwritten on the next
  deliberate re-sync. Local changes are silently lost.
- To pick up upstream changes (palette, type, fonts, or — later — Spectral State),
  re-sync from the new commit, regenerate this manifest, and bump the consuming
  diagrams' `render-vN` stamp.
- To propose changes to the tokens themselves, hand them up to the
  `design-system-ASK` control surface — never edit them here.
