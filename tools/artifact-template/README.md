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
prose stylesheet + base64-embedded fonts + the assigned wordmark as inline svg,
all inlined. The output has no external dependencies — it opens with full
styling from any location (local file, email
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
    ├── assets/logo-ASK.svg the assigned ASK wordmark (the masthead's mark; see "Inheritance")
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
  and `audience`, each once, each a single line containing visible text. Any other key fails
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
:::disclose question-detail "S"    inside a non-central :::question,        details.uo-details[data-uo-disclose]
                                   after its prompt                         with summary S and its content in
:::disclose evidence "S"           inside :::finding, after visible lines   div.uo-details__body
:::disclose provenance "S"         directly inside :::part 10, at most once
:::table <role per column> ["C"]   inside a part, around exactly one        data-uo-cell on every th and td;
                                   pipe table                               data-uo-label + label element per td; caption C
:::banner review-status            directly inside :::part 01, at most      div.uo-reviewer-status: its flag, then
                                   once                                     its body in div.uo-reviewer-status__body
:::banner proof ["T"]              directly inside :::part 01, at most      div.uo-proof: its flag, title T if given,
                                   once                                     then its body in div.uo-proof__body
```

- Parts 01 and 10 are generated even when the source omits them. The meta
  block drives 01's status rail (classification · audience · kind · round) and
  masthead (title; id, kind and round), and 10 always ends with the seal line.
  The masthead title is the document's only `h1`; authored headings use `##`
  to `####`.
- Every part's `section` carries a stable id, `uo-part-NN`; a repeated 06
  takes `uo-part-06-2`, `uo-part-06-3` and so on, in order. The masthead opens
  with the mark slot: the assigned wordmark, followed by the label "sections".
  Selecting it opens the section index, a native `details` element with no
  script, holding one link per section the document contains, in order, each
  labeled with its part number and name. The index works from a local file.
  These generated links are the only in-document links: a source link is
  `https://` or `http://` (below).
- A banner holds Markdown only. The renderer writes its flag ("review status"
  or "proof of assembly"); the source supplies the body and, for proof, an
  optional one-line title with visible text. A banner may not hold a
  container, a heading or a quotation. A banner is the document's own
  statement, not a represented voice, and a quotation's rule would draw a
  second edge inside the banner's ruled frame (in the proof banner, a second
  violet edge), so a quotation sits outside the banner, on its own rail. A
  banner takes no `local=` hook. Within part 01 a banner sits where the source
  places it; the build fixes neither its position nor the two banners' order.
  What a banner may say is checked at package review, as in "Approval before a
  reviewer sees a document".
- Table roles are `key`, `text`, `num` and `status`, one per column. Every
  pipe table is wrapped in `:::table`. Column alignment colons are not
  accepted. The build records each column's role as `data-uo-cell` on every
  cell. Every row must have as many cells as the header row (an escaped `\|`
  or a `|` inside a code span is not a cell boundary).
- Role styling comes from the template's data-table roles: a `num` column,
  header included, is right-aligned with tabular figures; a `key` cell takes
  the key emphasis. `text` and `status` cells take no role styling.
- An optional quoted caption follows the roles and must contain visible text.
  It renders as the table's `caption`, in the template's data-table caption
  style, except that it keeps the case the author wrote: the renderer's
  stylesheet sets `text-transform: none` for the caption and the disclosure
  summary, because those two roles carry authored payload text whose case can
  carry meaning (`mW`, `pH`). The rest of the role — mono face, 11px, weight
  500, letter-spacing and colour — is the template's. The template's own
  `.uo-data-table` caption is not changed. The design-system `.caption` class
  is not emitted.
- Every body cell carries `data-uo-label`, its column's header text with tags
  removed and whitespace collapsed, and a `span.uo-cell-label` holding that
  header cell's own inline markup. The build checks the attribute against its
  header and the element's text against the same header.
- The payload table is the review document's dense review table: a UO profile
  role, not a design-system rule. Its values are the renderer stylesheet's
  (`MD_CSS` in `build.py`: the mono face at `--fs-caption`, 14px, with a 1px
  `--artifact-line` grid), with the template's `num`, `key` and caption roles
  on top. They are not the template's `.uo-data-table` values (12px, soft row
  rules), which the renderer does not reach. Which values govern is not
  decided here: it is left to ASK and to the unit that adopts the final
  presentation (U6), and every value stays provisional until then.
- Text outside a preformatted block wraps: an ordinary word moves to the next
  line whole, and only a token longer than the line breaks inside itself. On
  screen a preformatted block keeps its lines and scrolls inside its own box.
- Table cells, the header row included, fit the table to the prose measure
  first: a word moves to the next line whole when it fits its column, and a
  word wider than its column breaks inside itself, so the table does not
  grow past the measure. In a table with many columns, above 960px, header
  and body words in narrow columns break inside the word, and so do numeric
  and status values: a number or a status word can split across lines, even
  one character per line, and a reader can take the pieces for separate
  values. The rows view below does not apply at those widths.
- At widths of 960px and below, the template's existing narrow-width
  threshold, every table shows one row at a time: each body cell is a block
  whose `span.uo-cell-label` shows its column's header above its value. The
  header row stays in the document but is moved out of view with a clip, not
  removed with `display: none`. In Chrome's accessibility tree the table, its
  rows and its column headers remain, and a stacked cell's accessible name
  begins with its label ("Count 12"). Screen readers and other browsers are
  not tested. No cell is dropped and nothing scrolls sideways. In print the
  page width decides, so a portrait page shows rows this way too.
- The visible label is an element carrying the header cell's own inline
  markup, not generated text, so a link in a header is a working link in
  every stacked cell of that column and inline code is still code. A run of
  whitespace, no-break and other space characters included, shows as one
  space in the checked attribute; the element reproduces the header's own
  text. The label is left-aligned in every column, a `num` column's included,
  and selecting a stacked row copies the labels with the values.
- Because the header row is out of view at those widths, a header link inside
  it would otherwise take keyboard focus while invisible. When anything in
  that row is focused the row returns to view, stacked, so the focused
  element is on screen. The same link is reachable without it, in the visible
  label of every cell in its column.
- A disclosure takes the template's disclosure role. Its summary is set in the
  mono face at the template's 11px label size, weight 500 and letter-spaced,
  as an inline box with a `+` or `–` marker in place of the browser's
  triangle, dimmer than body text. The summary keeps the case the author
  wrote, for the reason given for the caption above; the marker, and every
  other value of the role, is the template's. Its content sits in
  `div.uo-details__body`, whose padding and 1.55 line height apply to content
  that sets no line height of its own (list items, table cells). Inside it a
  paragraph takes the template's smaller bottom margin and a code span the
  template's code padding; a preformatted block renders as it does outside a
  disclosure.
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

### Renderer chrome classes

The build emits these classes only, each on the element listed. Every one is
styled by the template or the renderer's stylesheet.

```text
element   renderer chrome classes
div       uo-shell · uo-status-rail · uo-details__body · uo-reviewer-status · uo-reviewer-status__body · uo-proof · uo-proof__body
main      uo-md
header    uo-head
dl        uo-head__meta
span      uo-status-rail__primary · uo-status-rail__sep · uo-cell-label · uo-index__label
footer    uo-foot
details   uo-details · uo-index
summary   uo-index__mark
nav       uo-index__list
svg       uo-mark
p         uo-reviewer-status__flag · uo-proof__flag · uo-proof__title
```

Beyond these, a container may carry its `uo-local-<name>` class (below), and
a fenced code block's `code` may carry `language-<name>`. An authored
disclosure's `details` carries `uo-details`, followed by its local class if it
has one. `uo-details__body` sits only directly inside `details`, and
`uo-cell-label` only directly inside `td`. The section index sits only in the
masthead, its mark slot only in the index, and the wordmark's `svg`, holding
`path` elements only, only in the mark slot; a document carries exactly one of
each, and the index links every section, in order. A banner sits only directly
in part 01, and its flag, title and body only directly in their banner. Any
other class or placement fails the build.

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
- the vendored wordmark is not one `svg` of `path` elements with a numeric
  `viewBox` and `fill="currentColor"`, or its `svg` carries any attribute but
  `id`, `xmlns`, `viewBox` and `fill`;
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
- **Tier 3 by assignment, for review documents only.** ASK has assigned the
  `logo-ASK` wordmark to the review documents this template renders, as their
  locally supplied Tier 3. That is the assignment's recorded scope: the
  wordmark heads each such document's masthead and opens its section index.
  It is an assignment, not inheritance, and it does not make
  urban-observatory ASK-the-entity. No other design-system identity is
  carried: no "ASK Design System" chrome. The review semantics — the anatomy,
  the banners, the table roles — are urban-observatory's own. The token CSS
  header's "TIER 3 — ASK instance identity (NOT inherited by children)" stays
  true under an assignment.
- **No fork.** The diagram-tree scaffold's light-mode fix was *mirrored as a
  pattern* (see the light/dark contract below), not copied. `diagrams.css` is not
  vendored, imported, or forked.

### Vendored token snapshot — a build input, not a source of truth

`_dsa-tokens/` is a **pinned snapshot** of the design-system tokens + fonts and
the assigned wordmark, vendored so artifact builds are **reproducible without a
sibling checkout** of `design-system-ASK`. It is explicitly:

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

The template's dark selectors are the foundation's own
(`:root[data-theme="dark"], .theme-dark`), so `--artifact-line`,
`--artifact-line-soft`, `--uo-code-bg`, `--uo-mark` and `--uo-soft-bg` resolve
dark wherever the foundation's tokens do.

The wordmark takes the design system's pairing, never the text color:
`--uo-mark` is `--ask-white` on the light gradient and `--ask-lavender-ask` on
the dark one.

**Print.** The page prints on its own theme ground
(`print-color-adjust: exact` on the root), as it reads on screen. Without it the
ground drops out: the light theme's white lines vanish on white paper and the
dark theme's lavender text prints on white. No token is rebound for print. The
rule also prints the ground when a reader has turned background graphics off.
The ground does not extend into page margins a browser applies. A preformatted
block wraps in print instead of being cut off at the page edge.

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
template and emitted by `build.py` from a `:::banner` container in part 01. A
*specific* package's banner text belongs to that package's source, and its
review-orchestration files are assembled operator-side.

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
banners belong to 01, and the build places them there; the rendered footer is
10's seal line. Review questions and response templates that a package carries
as separate orchestration files stay there; they are not moved into the
document.

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
deliberate operator decision), re-copy `colors_and_type.css`, `fonts/*.woff2`
and `assets/logo-ASK.svg` from the target [`design-system-ASK`](https://github.com/apexSolarKiss/design-system-ASK) commit, regenerate `_dsa-tokens/MANIFEST.md`
with the new commit SHA and per-file hashes, and render new artifacts at the
new pin. A sealed artifact keeps the pin it was sealed with and is never
regenerated to track the new state. Until a re-sync lands, builds are pinned to
the recorded SHA.
