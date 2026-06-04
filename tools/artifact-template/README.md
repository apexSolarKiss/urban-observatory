# UO artifact template

Reusable rendering machinery for **urban-observatory human-readable artifacts** —
the sealed, single-file HTML documents the project produces for human review
(e.g. planning-validity reviews). This directory is the repo-local **source of
truth** for *how* those artifacts are rendered. It does **not** contain any
rendered artifact, review package, or project evidence — those are produced and
held operator-side.

## Purpose

Turn a canonical Markdown source into one **self-contained HTML file**:
design-system-ASK token CSS + the UO artifact-template overlay + a token-based
prose stylesheet + base64-embedded fonts, all inlined. The output has no external
dependencies — it opens with full styling from any location (local file, email
attachment, copied folder), no network, no sidecar. That portability is the point:
review artifacts must survive delivery without a stylesheet or font going missing.

## Files

```text
tools/artifact-template/
├── README.md               this file
├── artifact.template.html  the design-system <head> shell + UO overlay (CSS) + banner styles
├── build.py                the renderer: Markdown source -> sealed single-file HTML
└── _dsa-tokens/            VENDORED, PINNED design-system-ASK token snapshot (build input)
    ├── MANIFEST.md         records the upstream commit SHA + per-file sha256
    ├── colors_and_type.css foundational tokens (used verbatim; never edited here)
    └── fonts/*.woff2        Inter + JetBrains Mono (embedded at build)
```

## Usage

```bash
# requires python3 + the `markdown` package (pip install markdown)
python3 tools/artifact-template/build.py \
  --source path/to/source.md \
  --out    path/to/output.html \
  --title  "optional <title>"
```

The output is a single `.html` file. The build fails loudly if it would emit a
non-self-contained file (an external `<link>`/`@import`, a relative font URL, or
an unreplaced template marker).

## Inheritance from design-system-ASK

The visual language is **inherited from
[`design-system-ASK`](https://github.com/apexSolarKiss/design-system-ASK) by
reference**, following the family tier model:

- **Tier 1 + Tier 2** (foundational tokens, the ASK palette, Inter + JetBrains
  Mono) are consumed **verbatim** from the vendored `colors_and_type.css`. This
  repo never edits the foundational tokens.
- **No Tier 3.** No `logo-ASK`, no ASK wordmark, no ASK-as-project chrome. The
  artifact carries the *design language*, not the design-system's own identity.
- **No fork.** The diagram-tree scaffold's light-mode fix was *mirrored as a
  pattern* (see the light/dark contract below), not copied. `diagrams.css` is not
  vendored, imported, or forked.

### Vendored token snapshot — a build input, not a source of truth

`_dsa-tokens/` is a **pinned snapshot** of the design-system tokens + fonts,
vendored so artifact builds are **reproducible without a sibling checkout** of
`design-system-ASK`. It is explicitly:

- **a build dependency snapshot, not a fork** and not a second source of truth;
- **pinned** — `_dsa-tokens/MANIFEST.md` records the exact upstream commit SHA and
  a per-file `sha256`; the rendered footer records the pinned SHA so any drift is
  auditable;
- **updated only by explicit re-sync** from upstream (a deliberate operator
  action), never silently.

`design-system-ASK` remains the upstream source of truth for the tokens. This repo
holds a frozen copy for reproducible rendering.

## Light / dark contract

The foundational `--fg-*` foreground ramp resolves to **white** — correct on the
dark gradient, but **invisible** on the light lavender gradient. The artifact
template fixes this with a **local `--fg` / `--line` rebind in
`artifact.template.html`** (the `:root` light block), mirroring the design-system
diagram-tree light palette. The foundational `colors_and_type.css` is left
untouched.

| Role | Token | Light | Dark (unchanged) |
|---|---|---|---|
| Primary text | `--fg-1` | `#6A637F` | lavender (`--ask-lavender-dark`) |
| Secondary text | `--fg-2` | `#827399` | `rgba(212,198,225,.72)` |
| Tertiary / separators | `--fg-3` | `rgba(130,115,153,.62)` | `rgba(212,198,225,.48)` |
| Box borders · edges · rules | `--line-1` | white `rgba(255,255,255,.90)` | lavender |
| Held / softer strokes | `--line-2` | white `rgba(255,255,255,.55)` | lavender |

Design principles (carried from the design-system handoff):

- **Small text needs dark ink in light mode** — white is unreadable at body /
  caption sizes on the lavender field. Light text uses the diagram inks above.
- **Structural lines read fine in white** in light mode — they're large enough,
  and white lines preserve the light-mode character. Keep them white.
- **Dark mode is left exactly as-is** — only the light values are overridden; the
  dark `@media (prefers-color-scheme: dark)` / `[data-theme="dark"]` blocks keep
  the prior lavender ramp and lines.

**Why a local `--fg` rebind and not scoped tokens:** the design-system handoff
suggested mirroring with scoped tokens (e.g. `--diagram-*`). For this artifact
class that is insufficient — the foundation's **base element rules**
(`p`, `h1`, `h2` style `color: var(--fg-1)` directly) win over any scoped
*container* color, leaving base-rule body text white. Rebinding `--fg-*` itself at
the artifact-template layer fixes **every** text path (base-element and class),
while still leaving the foundational stylesheet untouched. This is an
artifact-template-layer override, not a design-system change.

## What stays operator-side (not in this repo)

This directory is the *machinery*. The following are produced from it but held
operator-side, and are **not** committed here:

- rendered artifact HTML and review packages (e.g. TMK guided-review packages,
  with their own review-status banners and orchestration files);
- the canonical Markdown content sources for specific artifacts;
- any project evidence, absorption memos, or private working material.

Review-package banners (`.uo-reviewer-status`, `.uo-proof`) are styled by the
template so operator-side packaging can use them, but a *specific* package's
banner text and review-orchestration files are assembled operator-side.

## How a human-review package is generated

1. Author / finalize the canonical Markdown source operator-side.
2. Render it with `build.py` to a sealed single-file HTML.
3. Operator-side, assemble the review package around it: the sealed HTML, the
   canonical Markdown as audit substrate, a MANIFEST binding the render to the
   pinned design-system SHA, and the review-orchestration files (bootstrap,
   questions, handoff template).
4. Deliver the package for human review.

Steps 1, 3, and 4 are operator-side; step 2 is this template's job.

## Re-syncing the token snapshot

When the design-system tokens change upstream and a refresh is wanted (a
deliberate operator decision), re-copy `colors_and_type.css` + `fonts/*.woff2`
from the target `design-system-ASK` commit, regenerate `_dsa-tokens/MANIFEST.md`
with the new commit SHA and per-file hashes, and re-render any artifacts that
should track the new state. Until then, builds are pinned to the recorded SHA.
