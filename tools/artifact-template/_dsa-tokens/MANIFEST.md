# _dsa-tokens / MANIFEST

Generated snapshot. Do not hand-edit. Refreshed by the urban-observatory
review-packet rendering workflow (see
`2026-05-24_urban-observatory_review-packet-rendering-workflow.md`).

| Field | Value |
| --- | --- |
| upstream | https://github.com/apexSolarKiss/design-system-ASK.git |
| commit | `3395833bb1951d08e2340ab06152606ca5903ba7` |
| short | `3395833` |
| commit date | `2026-05-24 11:41:44 -0700` |
| commit subject | `docs: update README Caveats with urban-observatory inheritance (#3)` |
| synced at | `2026-05-24T20:30:00Z` |
| consuming project | `urban-observatory` |
| files copied | `colors_and_type.css`, `fonts/InterVariable.woff2`, `fonts/InterVariable-Italic.woff2`, `fonts/JetBrainsMono.woff2`, `fonts/JetBrainsMono-Italic.woff2` |
| colors_and_type.css sha256 | `8923adce5bf56ce218061058b37939c66b8fdac02a1a5fd800b2bbfc16db742e` |
| fonts/InterVariable.woff2 sha256 | `693b77d4f32ee9b8bfc995589b5fad5e99adf2832738661f5402f9978429a8e3` |
| fonts/InterVariable-Italic.woff2 sha256 | `e564f652916db6c139570fefb9524a77c4d48f30c92928de9db19b6b5c7a262a` |
| fonts/JetBrainsMono.woff2 sha256 | `31ec365b93e4bad6f202ce23352a56d01ca4462b2afc782ed2cf6fa42ca9ac0e` |
| fonts/JetBrainsMono-Italic.woff2 sha256 | `76a805b6ea613ce2e3973f1bac6fa29db23116b2881390b59247d22890844ecc` |

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
