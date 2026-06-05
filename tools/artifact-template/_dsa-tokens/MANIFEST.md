# _dsa-tokens / MANIFEST

Generated snapshot. Do not hand-edit. Refreshed by the urban-observatory
review-packet rendering workflow (see
`2026-05-24_urban-observatory_review-packet-rendering-workflow.md`).

| Field | Value |
| --- | --- |
| upstream | https://github.com/apexSolarKiss/design-system-ASK.git |
| commit | `040e7caa7e3a2fefe045f0be2b247fdd1706636d` |
| short | `040e7ca` |
| commit date | `2026-06-04 17:09:22 -0700` |
| commit subject | `feat(output-artifact): mature Class B scaffold to v2 (#19) (#21)` |
| synced at | `2026-06-04` |
| consuming project | `urban-observatory` |
| files copied | `colors_and_type.css`, `fonts/InterVariable.woff2`, `fonts/InterVariable-Italic.woff2`, `fonts/JetBrainsMono.woff2`, `fonts/JetBrainsMono-Italic.woff2` |
| colors_and_type.css sha256 | `1aeed0fda84cef41a60789613e2a5195b0cae3c208cb047d592f27959bca973c` |
| fonts/InterVariable.woff2 sha256 | `693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3` |
| fonts/InterVariable-Italic.woff2 sha256 | `e564f652916db6c139570fefb9524a77c4d48f30c92928de9db19b6b5c7a262a` |
| fonts/JetBrainsMono.woff2 sha256 | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |
| fonts/JetBrainsMono-Italic.woff2 sha256 | `76a805b6ea613ce2e3973f1bac6fa29db23116b2881390b59247d22890844ecc` |

**Re-sync 2026-06-04 (`3395833` → `040e7ca`):** picks up the foundation light-mode foreground ramp (design-system PR #18 / `f9eed18`) — light `--fg-1/-2/-3` now resolve to dark ink (`#6A637F` / `#827399` / `rgba(130,115,153,.62)`) instead of white — and aligns to the matured Class B v2 `output-artifact` contract. Only `colors_and_type.css` changed (new sha256 above); the four font files are byte-identical to the `3395833` snapshot (same hashes). Consequence in the artifact template: the local `--fg-*` rebind was dropped (now redundant — foreground inherited from the foundation), and the local `--line-*` light rebind was replaced by the Class B-scoped `--artifact-line` / `--artifact-line-soft` overlay. See the handoff `sources of intent/2026-06-04_design-system-ASK_to_urban-observatory_token-resync-class-b-v2-handoff.md` and the absorption record in `scratch/`.

## Binding

This manifest binds the rendered HTML packets in this scratch directory to a
known upstream `design-system-ASK` state.

If the upstream commit SHA recorded above differs from what a rendered
packet's footer records, the packet is reading tokens that have drifted
from its audit point. To regenerate against a newer upstream, re-run the
sync workflow and re-render the packet from template + content source.

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
- To pick up upstream changes (palette, type, radii, surface opacity, motion), run the sync workflow defined in `2026-05-24_urban-observatory_review-packet-rendering-workflow.md`.
- To propose changes to the tokens themselves, hand them up to the `design-system-ASK` control-surface thread (see `2026-05-24_urban-observatory_control-surface-handoff-to-design-system-ASK.md`).
