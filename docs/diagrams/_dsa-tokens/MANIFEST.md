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
| commit | `20fc5d6505da16a848dda529545b144f3c7a90ac` |
| short | `20fc5d6` |
| commit date | `2026-06-05 20:04:25 -0700` |
| commit subject | `feat(diagram-interactive-spine): graduate the interactive IA state spine (Class A interactive) (#28)` |
| synced at | `2026-06-05` |
| consuming surface | `urban-observatory/docs/diagrams/` |
| scope | Tier 1 + Tier 2 only (no Tier 3) |

## Files in this snapshot

```text
_dsa-tokens/
├── MANIFEST.md                     this file
├── colors_and_type.css             Tier 1 + Tier 2 tokens + @font-face
│                                   (light default · [data-theme="dark"] · prefers-color-scheme auto-bridge)
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
| `colors_and_type.css` | `1aeed0fda84cef41a60789613e2a5195b0cae3c208cb047d592f27959bca973c` |
| `fonts/InterVariable.woff2` | `693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3` |
| `fonts/InterVariable-Italic.woff2` | `e564f652916db6c139570fefb9524a77c4d48f30c92928de9db19b6b5c7a262a` |
| `fonts/JetBrainsMono.woff2` | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |
| `fonts/JetBrainsMono-Italic.woff2` | `76a805b6ea613ce2e3973f1bac6fa29db23116b2881390b59247d22890844ecc` |

## Scope note — static diagrams only (so far)

This mirror carries `colors_and_type.css` + fonts, which is everything the
**static** Class A diagrams need (`diagram-static-H`). The **interactive** IA
spine additionally requires `spectral-state.css`; that file is **not** vendored
here yet and will be added (at the same pin) when the interactive spine is built.
Static scaffolds do **not** load `spectral-state.css`.

## Binding

This manifest binds the rendered diagram files in `docs/diagrams/` to a known
upstream `design-system-ASK` state (`20fc5d6`). The diagram `<head>` records the
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
