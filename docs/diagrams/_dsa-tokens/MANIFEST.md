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
| commit | `1231d03040c74eb4eedf7be2e3214da9766e63f7` |
| short | `1231d03` |
| commit date | `2026-06-26 20:26:43 -0700` |
| commit subject | `tokens: comment-only conformance — retire "Core 5"/"five-color" + "each neon" (no value change) (#56)` |
| synced at | `2026-06-26` |
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
| `colors_and_type.css` | `bcd11e0efeae2851c8653a425f94a76cb6423c770e23cb18b3a0315519a7375f` |
| `spectral-state.css` | `dd30fdc0b7b9174801129f0d01f45e22da5bbd92ff47e58d7aabaeea64f0d05b` |
| `fonts/InterVariable.woff2` | `693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3` |
| `fonts/InterVariable-Italic.woff2` | `e564f652916db6c139570fefb9524a77c4d48f30c92928de9db19b6b5c7a262a` |
| `fonts/JetBrainsMono.woff2` | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |
| `fonts/JetBrainsMono-Italic.woff2` | `76a805b6ea613ce2e3973f1bac6fa29db23116b2881390b59247d22890844ecc` |

**Re-sync 2026-06-26 (`b5d158e` → `1231d03`):** picks up design-system PR **#56** — a **comment-only** conformance cleanup of the vendored token files (no token value, role name, selector, theme behavior, or rendered-output change). `colors_and_type.css`: "five-color core" → "a core identity set"; "Core 5 — backgrounds + text" → "Core set — backgrounds, wordmark, dark-mode text". `spectral-state.css`: "each mapped to a neon hue" → "eight roles: seven sparse neon state signals plus a neutral role that resolves to the theme foreground" (`--state-neutral = var(--fg-1)`, not a neon). **Render-neutral:** light `--fg-1` still resolves to `#6A637F`, dark unchanged, `--state-neutral = var(--fg-1)` unchanged — comment text + file hashes only differ. Two files re-vendored: `colors_and_type.css` (`8b8917e5` → `c7618b2d`, new sha256 above) and `spectral-state.css` (`566bf14d` → `b82083d2`, new sha256 above); the four fonts are byte-identical to the `b5d158e` snapshot. **Render stamps held** (UO commits no diagram rasters; live `.html` exports on demand). See the handoff `sources of intent/2026-06-26_design-system-ASK_to_urban-observatory_vendored-css-comment-resync.md` and the absorption record in `scratch/`.

**Prior re-sync 2026-06-26 (`20fc5d6` → `b5d158e`):** design-system PR **#52** (light-mode foreground conformance — white = wordmark pairing only; `#6A637F` = canonical default light foreground / the approved dark purple; `#201D26` = reserved opt-in high-contrast) + **#53** (`diagrams.css` aliases `--diagram-ink/-muted/-faint` → foundation `--fg-1/-2/-3`). Render-neutral. Handoff `…foreground-conformance-resync.md`.

## Scope note — static vs interactive load

This mirror carries `colors_and_type.css` + fonts (everything the **static**
Class A diagrams need, `diagram-static-H`) **and** `spectral-state.css` (Spectral
State v1.1), required by the **interactive** IA spine (`diagram-interactive-spine`,
in `../interactive/`). All vendored at the same pin (current pin `1231d03`; prior
pin `b5d158e` — see the table above and the re-sync note).

**Static scaffolds do NOT load `spectral-state.css`** — only the interactive
spine does, in load order `colors_and_type.css → spectral-state.css →
diagrams-interactive-spine.css`. Color on the interactive surface encodes
**state only**.

## Binding

This manifest binds the rendered diagram files in `docs/diagrams/` to a known
upstream `design-system-ASK` state (current pin `1231d03`; prior `b5d158e`). The diagram `<head>` records the
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
