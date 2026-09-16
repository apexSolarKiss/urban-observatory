# UO artifact template

Reusable rendering machinery for **[urban-observatory](../../README.md) human-readable artifacts** —
the sealed, single-file HTML documents the project produces for human review
(e.g. planning-validity reviews). This directory is the repo-local **source of
truth** for *how* those artifacts are rendered. It does **not** contain any
rendered artifact, review package, or project evidence — those are produced and
held operator-side.

## Purpose

Turn a canonical Markdown source into one **self-contained HTML file**:
[design-system-ASK](https://github.com/apexSolarKiss/design-system-ASK) token CSS + the UO artifact-template overlay + a token-based
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

## Light / dark contract (Class B v2)

This template follows the [design-system-ASK](https://github.com/apexSolarKiss/design-system-ASK) **Class B `output-artifact` v2**
contract (`040e7ca`). **Foreground is inherited, not rebound.** Since the
foundation light-mode foreground ramp landed (design-system PR #18 / `f9eed18`),
`colors_and_type.css` resolves `--fg-1/-2/-3` to **dark ink in light**
(`#6A637F` / `#827399` / `rgba(130,115,153,.62)`) and lavender in dark — so
base-element prose (`p` / `h1` / `h2`) inherits the correct color directly. The
template adds **no local `--fg` rebind**, and `colors_and_type.css` is consumed
verbatim.

The **one sanctioned artifact-layer override is line intensity.** The foundation
hairlines (`--line-*`, white `.45` / `.22`) read too faint for report rules,
borders, table lines, and dividers on the light field. So the template defines a
**scoped `--artifact-line` / `--artifact-line-soft`** (stronger white in light;
the foundation lavender lines in dark) and points its own structural elements at
it — applied by class, never to base elements, so it cannot affect inherited
prose color. The foundation `--line-*` tokens are left untouched.

| Role | Token | Light | Dark |
|---|---|---|---|
| Foreground (text) | `--fg-1/-2/-3` | **inherited** dark ink (`#6A637F` / `#827399` / `rgba(130,115,153,.62)`) | inherited lavender |
| Structural lines | `--artifact-line` | white `rgba(255,255,255,.90)` | `var(--line-1)` (foundation lavender) |
| Softer dividers | `--artifact-line-soft` | white `rgba(255,255,255,.55)` | `var(--line-2)` (foundation lavender) |

Design principles:

- **Foreground is the foundation's job.** The foundation light ramp is dark ink;
  the artifact does not re-declare `--fg-*`. (Re-declaring it is a v2 hard-fail.)
- **Line intensity is the one artifact override** — scoped to structural lines
  (by class), white at higher alpha in light, foundation lavender in dark. White
  is in-palette; the override never touches foreground.
- **Dark mode is the foundation's** — the dark `@media` / `[data-theme="dark"]`
  blocks resolve `--fg-*` and `--line-*` to lavender; `--artifact-line` inherits
  the foundation lines in dark.

**History (resolved):** an earlier version of this template carried a local
`--fg` rebind, because the foundation light ramp was still white and base-element
rules (`p`/`h1`/`h2 { color: var(--fg-1) }`) win over scoped container color. The
foundation fix (`f9eed18`) made that rebind redundant; the 2026-06-04 re-sync to
`040e7ca` dropped it and adopted the scoped `--artifact-line` line-intensity
overlay, aligning to the matured Class B v2 contract. The template is now a clean
consumer of the shared pattern rather than the sole owner of the matured behavior.

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

## Review-document anatomy

A human-review document rendered from this template must follow one ordering
and anatomy contract. The contract fixes the order of the parts and what each
part keeps visible. It does not require a document to carry every part.

### The parts

```text
01  locator + masthead          the document's identity, kind and round, and its
                                classification and audience, fixed when sealed
02  reviewer brief              what the document tests and why; what the reviewer
                                is asked to judge, and what not to judge
03  decision request            one bounded question set with exactly one central
                                question, and any response choices it offers
04  executive result            the result the document reports; where source
                                contact occurred, what it changed
05  finding index               one entry per finding unit
06  finding unit (repeated)     status or identifier · finding · significance ·
                                limit (what it does not establish) · evidence and
                                its locator
07  prior-position delta        what changed, stayed or was withdrawn against a
                                named earlier position
08  unresolved + later-check    what the document cannot conclude; its staleness
    register                    and observability limits; missing sources; what
                                must be checked later
09  response / handoff format   how the reviewer answers
10  seal + provenance           the render seal and the provenance behind the
                                document
```

Parts must appear in this order. The review-status and proof-of-assembly
banners the template styles belong to 01; the rendered footer is 10's seal
line. Review questions and response templates that a package carries as
separate orchestration files stay there; they are not moved into the document.

A document declares one kind, and its kind decides which parts are required.
Any other part appears only when it has content — never as an empty band or a
"not applicable" placeholder.

### Kinds

Every kind requires 01, 02 and 10. A kind profile adds the parts a document of
that kind cannot be read without. Profiles differ because review kinds differ:
a document built to withhold a result from its reader cannot require an
executive result.

```text
kind            requires, beyond 01 · 02 · 10   status
guided-review   04 · 06 · 08                    PROVISIONAL
confirmation    07                              PROVISIONAL
```

A profile stays provisional until a declared proof document of its kind has
been rendered and reviewed against it. Only a reviewed change to this section
lifts that status. A kind without a profile must not be rendered through this
template until one is added here.

**A contract failure is a finding about the contract, never a reason to change
the content.** When a real document cannot satisfy the contract, the profile or
the anatomy is reviewed. Source content is never added, moved or reworded to
make a check pass.

### What stays visible

Each part and sub-part is ALWAYS VISIBLE unless it is listed under MAY
DISCLOSE. Disclosure uses the native `<details>` / `<summary>` element, with
no script.

```text
ALWAYS VISIBLE, including
  03   every question's prompt; the central question's prompt and its detail
  06   each unit's status or identifier, finding, significance and limit;
       each evidence surface's title, summary lines, and what it does and
       does not mean; each evidence row's labels, claim and assessed state;
       any quoted source passage the finding relies on; any live constraint,
       confidence cap or other uncertainty on the evidence
  08   the whole register, never reduced to the limits each finding unit states
  10   the seal line

MAY DISCLOSE
  03   a non-central question's detail
  06   field-level evidence listings and finding metadata, beneath visible
       summary lines
  10   the provenance table, as one block
```

### Approval before a reviewer sees a document

Approval to show a document to its reviewer is a gate in the operator-side
package workflow. It is not a document part: a sealed review document carries
no approval block, and its status records no approval state.

### Checks

A document fails the contract when:

- it declares no kind, or a kind without a profile;
- a part its kind requires is missing;
- a part is empty or out of order, or a part other than 06 repeats;
- 03 is present without exactly one central question;
- an ALWAYS VISIBLE element sits inside a disclosure;
- it carries content outside the ten parts.

`build.py` has no syntax for declaring a kind or a part yet; that arrives with
the renderer change that enforces these checks. Until then, package review
applies them to the rendered document.

A document sealed before this contract keeps its bytes and its structure. This
contract gives no reason to regenerate one.

## How a human-review package is generated

1. Author / finalize the canonical Markdown source operator-side, in the
   review-document anatomy above.
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
from the target [`design-system-ASK`](https://github.com/apexSolarKiss/design-system-ASK) commit, regenerate `_dsa-tokens/MANIFEST.md`
with the new commit SHA and per-file hashes, and re-render any artifacts that
should track the new state. Until then, builds are pinned to the recorded SHA.
