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
├── build.py                the renderer: Markdown source -> sealed single-file HTML + package MANIFEST
├── pin_check.py            clone-side pin checks for a pinned extraction
├── requirements.txt        the pinned `markdown` version
├── tests/                  unit tests (synthetic sources only)
└── _dsa-tokens/            VENDORED, PINNED design-system-ASK token snapshot (build input)
    ├── MANIFEST.md         records the upstream commit SHA + per-file sha256
    ├── colors_and_type.css foundational tokens (used verbatim; never edited here)
    └── fonts/*.woff2        Inter + JetBrains Mono (embedded at build)
```

## Usage

For a seal, this is the invocation from a pinned extraction of this directory
(see "Pinned extraction and pin checks"), not from a working clone:

```bash
# requires python3 + the `markdown` version pinned in requirements.txt
python3 -B <render-dir>/tools/artifact-template/build.py \
  --source    path/to/source.md \
  --out       path/to/output.html \
  --manifest  path/to/MANIFEST.md \
  --uo-commit <40-hex commit the renderer was extracted from> \
  [--local-css path/to/local.css]
```

`--out` and `--manifest` must not exist: a regenerated render is a new
artifact. On success the build writes the sealed `.html` file and its package
MANIFEST; on failure it writes neither. `<title>` comes from the source's meta
block.

Run `build.py` and `pin_check.py` with `python3 -B`. A `__pycache__` directory
or `.pyc` file in this directory fails the build and the pin check, because a
compiled file can be imported in place of its source.

Run the tests from a clone with
`python3 -B -m unittest discover -s tools/artifact-template/tests`.

### Source grammar

A source is one meta block followed by containers. Markdown sits inside the
containers; nothing but blank lines sits outside them.

```text
:::meta
kind: guided-review
title: <one line>
id: <one line>
round: <one line>
classification: <one line>
audience: <one line>
:::

:::part 02
Markdown.
:::
```

- The meta keys are exactly `kind`, `title`, `id`, `round`, `classification`
  and `audience`, each once, each a non-empty single line. Any other key fails
  the build.
- A container opens with `:::<kind> <tokens>` and closes with `:::`, both at
  the start of a line. Containers nest. A `:::` line inside fenced or
  indented code is code text.
- Unclosed containers, a close with nothing open, unknown kinds or tokens,
  repeated tokens, and a container in a position its row does not allow all
  fail the build with the line number.

```text
container                          allowed position                         emits
:::part NN                         top level; NN is 01 to 10                section[data-uo-part]
:::question [central]              directly inside :::part 03               div[data-uo-role="question"]
:::finding                         directly inside :::part 06               div[data-uo-role="finding"]
:::disclose question-detail "S"    inside a non-central :::question,        details[data-uo-disclose] with
                                   after its prompt                         summary S
:::disclose evidence "S"           inside :::finding, after visible lines
:::disclose provenance "S"         directly inside :::part 10, at most once
:::table <role per column>         inside a part, around exactly one        data-uo-cell on every th and td
                                   pipe table
```

- Parts 01 and 10 are generated even when the source omits them. The meta
  block drives 01's status rail (classification · audience · kind · round) and
  masthead (title; id, kind and round), and 10 always ends with the seal line.
  The masthead title is the document's only `h1`; authored headings use `##`
  to `####`.
- Table roles are `key`, `text`, `num` and `status`, one per column. Every
  pipe table is wrapped in `:::table`. Column alignment colons are not
  accepted. The build records each column's role as `data-uo-cell` on every
  cell; it applies no role styling yet, numeric alignment included, so every
  cell renders left-aligned. Every row must have as many cells as the header
  row (an escaped `\|` or a `|` inside a code span is not a cell boundary).
- Only payload table cells wrap. Outside a table cell, a long unbroken token
  in prose or a code span, a heading, a disclosure summary or the masthead
  title can make the page scroll horizontally.
- The empty-container checks, the lines that must precede a disclosure and a
  disclosure's summary count visible text only: at least one character that
  is not whitespace, a control or format character, a default ignorable code
  point (zero-width space, Hangul filler and the like), U+2800 BRAILLE PATTERN
  BLANK or a combining mark on its own. Other glyph-blank characters are
  checked at package review.
- **Raw HTML in the source fails the build**, including comments. Put literal
  tags in a code span or write `&lt;`; `\<` is not an escape.
- Links are `https://` or `http://` only. Images are not accepted: an image is
  a relative dependency.

### Payload-local CSS

Any container except `:::part 01` and `:::part 10`, which carry the generated
masthead and seal line, may carry one `local=<name>` token, where `<name>`
matches `[a-z][a-z0-9-]{0,31}`. It emits `class="uo-local-<name>"` on that
container's element only. `--local-css` adds a third `<style>` block holding
the file's bytes unchanged; the package MANIFEST records their sha256. The file:

- must scope every selector under `main.uo-md .uo-local-<name>`, for a name
  the source uses, with no sibling (`~`, `+`) or column combinator outside
  brackets and parentheses, no quote character (write attribute values
  unquoted) and balanced brackets and parentheses;
- may not contain comments, at-rules, `url(`, `image-set(` or another function
  that can load a resource, a quoted string inside a function, `</`,
  backslashes, custom property declarations or `!important`.

The build checks selectors, not the effect of declarations: a scoped rule can
still move, hide or overlay its own container's content. Package review checks
the rendered effect, and that local CSS does not re-derive a shared role.
Local names and local CSS belong to the payload and stay operator-side; none
enters this repo.

### What the build refuses

The build fails, writing nothing, when:

- the source breaks the grammar or the anatomy checks below, or contains raw
  HTML;
- the final HTML carries an element, class or attribute outside the renderer's
  allowlist, or its CSS carries `@import`, a `url(` other than an embedded
  font, or `image-set(` or another function that can load a resource;
- a vendored `_dsa-tokens/` file is missing, or its bytes do not match the
  sha256 recorded in `_dsa-tokens/MANIFEST.md`, or that manifest's commit or
  short row is malformed;
- the installed `markdown` is not the pinned version;
- this directory holds a `__pycache__` directory or a `.pyc` file;
- the output would not be self-contained (an external `<link>`/`@import`, a
  relative font URL, or an unreplaced template marker).

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
  a per-file `sha256`; the build verifies every vendored file's bytes against
  those hashes before sealing, and the seal line and package MANIFEST record the
  manifest's commit only when every file matches, so any drift is auditable.
  That the commit row names the upstream state those bytes came from is
  established when the snapshot is re-synced and reviewed; the build has no
  upstream checkout and does not re-check it;
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
template, but a *specific* package's banner text and review-orchestration files
are assembled operator-side. `build.py` cannot emit them yet: raw HTML fails
the build and the final-HTML allowlist rejects their classes.

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

`build.py` enforces these checks when it renders, fail-closed, through the
source grammar in "Usage". The build cannot see which sentences an author
placed inside an allowed disclosure; package review checks that nothing this
section keeps ALWAYS VISIBLE sits inside one.

A document sealed before this contract keeps its bytes and its structure. This
contract gives no reason to regenerate one.

## Pinned extraction and pin checks

The renderer is not run from a working clone. Per render, extract this
directory at a pinned commit into that render's own build directory, run it
there, and discard the extraction after sealing. The pin checks run from the
clone, never from the extraction: an extracted `build.py` cannot vouch for its
own descent.

```bash
git -C <clone> fetch origin --prune
git -C <clone> merge-base --is-ancestor <sha> origin/main     # exit 0 required
git -C <clone> archive <sha> tools/artifact-template | tar -x -C <render-dir>
python3 -B <render-dir>/tools/artifact-template/build.py --uo-commit <sha> ...
```

`pin_check.py` runs the same checks from the clone's own tree and performs no
fetch:

```bash
python3 -B <clone>/tools/artifact-template/pin_check.py --clone <clone> \
  --commit <sha> [--extracted <render-dir>/tools/artifact-template] [--descends-from <sha>]
```

- It fails unless `<sha>` exists and is an ancestor of `origin/main`.
- With `--extracted`, it fails unless the extraction's tree digest equals the
  digest of a fresh `git archive <sha>`. Package review recomputes that digest
  from `git archive <sha>` in an empty directory and compares it with the
  package MANIFEST; a mismatch fails the package.
- With `--descends-from`, it fails unless that commit is an ancestor of
  `<sha>`.

The tree digest is the SHA-256 of the lines `<sha256>  ./<relpath>\n` for every
regular file under `tools/artifact-template/`, paths in byte order. A
`__pycache__` directory or `.pyc` file fails the digest instead of being
skipped. The package MANIFEST's digest is recorded by the renderer running from
the extraction; `pin_check.py --extracted`, run from the clone on the final
extraction, is what verifies it.

A seal for a TMK-facing artifact must also descend from the urban-observatory
merge of the unit (U6) that adopts the final presentation. That anchor does not
exist yet; it is recorded here when that unit lands, and no TMK-facing artifact
is sealed through this path before it.
The renderer does not enforce audience. The checker runs from the clone's
mutable working tree: the git objects vouch, not the checker's bytes.

## How a human-review package is generated

1. Author the canonical Markdown source operator-side, in the source grammar
   and the review-document anatomy above.
2. Extract this directory at a pinned commit and run the clone-side pin checks.
3. Render. `build.py` writes the sealed single-file HTML and its package
   MANIFEST.
4. Operator-side, assemble the review package: the sealed HTML, its MANIFEST,
   the canonical Markdown as audit substrate, and the review-orchestration
   files.
5. Run the mandatory preflight on the sealed HTML.
6. Deliver the package for human review.

Steps 2 and 3 are this template's job. Steps 1, 4, 5 and 6 are operator-side.

## Re-syncing the token snapshot

When the design-system tokens change upstream and a refresh is wanted (a
deliberate operator decision), re-copy `colors_and_type.css` + `fonts/*.woff2`
from the target [`design-system-ASK`](https://github.com/apexSolarKiss/design-system-ASK) commit, regenerate `_dsa-tokens/MANIFEST.md`
with the new commit SHA and per-file hashes, and render new artifacts at the
new pin. A sealed artifact keeps the pin it was sealed with and is never
regenerated to track the new state. Until a re-sync lands, builds are pinned to
the recorded SHA.
