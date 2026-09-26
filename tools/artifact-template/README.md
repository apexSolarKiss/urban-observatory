# UO artifact template

Reusable rendering machinery for **[urban-observatory](../../README.md) human-readable artifacts** —
the sealed, single-file HTML documents the project produces for human review
(e.g. planning-validity reviews). This directory is the repo-local **source of
truth** for *how* those artifacts are rendered. It does **not** contain any
rendered artifact, review package, or project evidence — those are produced and
held operator-side.

## Purpose

Turn a canonical Markdown source into one **self-contained HTML file**:
[design-system-ASK](https://github.com/apexSolarKiss/design-system-ASK) token CSS + the design-system document register (four
modules, verbatim) + the UO overlay and geometry stylesheet + base64-embedded
fonts + the assigned wordmark as inline svg, all inlined. The output has no
external dependencies — it opens with full styling from any location (local
file, email attachment, copied folder), no network, no sidecar. That portability
is the point: review artifacts must survive delivery without a stylesheet or
font going missing.

Every piece of text the renderer emits takes a role of the design-system
document register, so its type is the register's and is checked on the sealed
file (see "Rendered conformance check"). This is the Class B `output-artifact`
v3 contract, applied through this renderer.

## Files

```text
tools/artifact-template/
├── README.md               this file
├── artifact.template.html  the <head> shell + the UO overlay: line tokens and chrome geometry (CSS)
├── build.py                the renderer: Markdown source -> sealed single-file HTML + package MANIFEST
├── pin_check.py            clone-side pin checks for a pinned extraction
├── requirements.txt        the pinned `markdown` version
├── tests/                  unit tests (synthetic sources only)
├── _dsa-tokens/            VENDORED, PINNED design-system-ASK token snapshot (build input)
│   ├── MANIFEST.md         records the upstream commit SHA + per-file sha256
│   ├── colors_and_type.css foundational tokens (used verbatim; never edited here)
│   ├── assets/logo-ASK.svg the assigned ASK wordmark (the masthead's mark; see "Inheritance")
│   └── fonts/*.woff2        Inter + JetBrains Mono (embedded at build)
└── _dsa-surface/           VENDORED, PINNED design-system-ASK document register (build input)
    ├── MANIFEST.md         the same commit as _dsa-tokens/, + per-file sha256
    └── surface-panel.css · surface-text-link.css · surface-document.css · surface-treatments.css
                            inlined verbatim, in that order, after the token CSS
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
:::part NN                         top level; NN is 01 to 10                section.doc-section[data-uo-part]
:::question [central]              directly inside :::part 03               div.doc-section[data-uo-role="question"]
:::finding                         directly inside :::part 06               div.doc-section[data-uo-role="finding"]
:::disclose question-detail "S"    inside a non-central :::question,        details.uo-details in the disclosure
                                   after its prompt                         treatment[data-uo-disclose]: summary S,
:::disclose evidence "S"           inside :::finding, after visible lines   then its content in
:::disclose provenance "S"         directly inside :::part 10, at most once div.uo-details__body
:::table [dense] <role per column> inside a part, :::question, :::finding   data-uo-cell on every th and td;
         ["C"]                     or :::disclose, around exactly one pipe  data-uo-label + label element per td;
  (a role may add :authored-case)  table                                    caption C; dense: table.doc-dense-table;
                                                                            authored-case: span.uo-authored-case
:::banner review-status            directly inside :::part 01, at most      a cyan emphasis panel: its chip, then
                                   once                                     its body in div.uo-reviewer-status__body
:::banner proof ["T"]              directly inside :::part 01, at most      a violet emphasis panel: its chip, title
                                   once                                     T if given, its body in div.uo-proof__body
:::quote ["A"]                     inside a part, :::question, :::finding,  blockquote.doc-quote; attribution A in
                                   :::disclose or :::callout                its footer
:::callout                         inside a part, :::question, :::finding   p.doc-body.surface-emphasis-rail for one
                                   or :::disclose                           paragraph, else div.surface-emphasis-rail
:::framing thesis|question         directly inside a part 02 to 09, at      the flat panel, chipped "thesis" or
                                   most once, before its first ### or ####  "question space"
:::synthesis                       directly inside a part 02 to 09, at      the flat panel, chipped "compression"
                                   most once, as the part's last content
:::structure                       inside a part, :::question, :::finding,  div.doc-pre.doc-pre--structured
                                   :::disclose or :::callout
:::group                           directly inside :::structure             div.doc-pre-group, a declared peer group
```

- Parts 01 and 10 are generated even when the source omits them. The meta
  block drives 01's status rail (classification · audience · kind · round) and
  masthead (title; id, kind and round), and 10 always ends with the seal line.
  The masthead title is the document's only `h1`, in the document-title role;
  authored headings use `##` (section title), `###` (subsection title) and
  `####` (deep heading). A heading governs what follows it until a heading of
  its level or above: each opens a nested section, and the space around it is
  the register's. Every container that may hold a heading is itself a section
  (a part, a question, a finding, a disclosure's body), so a subsection takes
  the register's lead wherever it nests; a section's run of other blocks is a
  prose run.
- Every part's `section` carries a stable id, `uo-part-NN`; a repeated 06
  takes `uo-part-06-2`, `uo-part-06-3` and so on, in order. The masthead opens
  with the mark slot: the assigned wordmark, followed by the label "sections",
  as the trigger of a design-system disclosure. It opens the section index,
  the register's contents role, with no script: one link per section the
  document contains, in order, each labeled with its part number and name.
  The index works from a local file. These generated links are the only
  in-document links: a source link is `https://` or `http://` (below).
- Every element the renderer emits takes a role of the design-system document
  register. A paragraph or list item is document body; a quotation's own
  paragraphs take the quotation's rule; headings take the ladder above; inline
  code is `code.doc-code`; a link is `a.surface-text-link`. A fenced or
  indented code block is `pre.doc-pre`, carrying its text directly, on the
  magenta passage rail. `>` is a quotation, `blockquote.doc-quote`, on the
  violet rail; it holds no heading. An indented code block inside `>` is a
  quoted code excerpt and keeps the quotation's one rail (a fenced block inside
  `>` renders as inline code, python-markdown's behavior). A quotation's parts
  sit `--space-4` apart.
- `:::quote "A"` is a quotation whose attribution the source supplies; A
  renders in its `footer`, in the metadata metrics. It holds paragraphs,
  lists, preformatted blocks and quotations.
- `:::callout` is the document's own thesis, posed question or contrast, set
  apart on the magenta rail: one paragraph becomes
  `p.doc-body.surface-emphasis-rail`, anything more a railed group. It is never
  a heading and holds none. It may hold paragraphs, lists, quotations,
  preformatted blocks and structured blocks; what it holds draws no second
  rail.
- `:::framing thesis` or `:::framing question` frames a whole part before its
  sections: it comes after the part's introduction and before its first `###`
  or `####` heading. `:::synthesis` closes a part: nothing follows it there.
  Both take the design-system flat panel, chipped "thesis", "question space"
  or "compression" in magenta, and hold paragraphs and lists only. A thesis or
  question inside the argument is a callout, not a framing.
- `:::structure` is a structured block: its lines are text, not Markdown, and
  each line is one `pre.doc-pre-part`. Two spaces of indentation are one level
  (a tab fails), and the lines beneath a line sit on a hierarchy rail, one per
  level; a line is never more than one level beneath the line before it. One
  to three blank lines before a line are recorded as `data-lead-lines`; more
  fail. `:::group` declares a peer group: a structure that declares groups
  holds only groups, and each group opens on its label, its first line, and
  holds no blank line. Groups sit exactly one line apart. A structure line may
  not begin with `:::`.
- A banner holds Markdown only. The renderer writes its flag ("review status"
  or "proof of assembly"); the source supplies the body and, for proof, an
  optional one-line title with visible text. A banner is a design-system
  emphasis panel, cyan for review status and violet for proof, whose flag is
  the emphasis chip, whose title takes the subsection-title role and whose body
  takes the document roles. A banner may not hold a container, a heading or a
  quotation. A banner is the document's own statement, not a represented
  voice, and a quotation's violet rail would draw a second edge inside the
  banner's accented perimeter, so a quotation sits outside the banner, on its
  own rail. A banner takes no `local=` hook. Within part 01 a banner sits where
  the source places it; the build fixes neither its position nor the two
  banners' order. What a banner may say is checked at package review, as in
  "Approval before a reviewer sees a document".
- Table roles are `key`, `text`, `num` and `status`, one per column. Every
  pipe table is wrapped in `:::table`. Column alignment colons are not
  accepted. The build records each column's role as `data-uo-cell` on every
  cell. Every row must have as many cells as the header row (an escaped `\|`
  or a `|` inside a code span is not a cell boundary).
- `:::table dense ...` declares a dense table: tabular, technical payload such
  as a review matrix or a status ledger. It is `table.doc-dense-table`, its
  headers take the label role and its values the dense cell role (mono at the
  Small step, tabular figures). Any other table is a narrative table: label
  headers and document-body cells, the design-system `output-artifact` v3
  rule until the shared table composition lands. Which tables are dense is the
  author's declaration, never inferred.
- The table's geometry is UO's: a 1px `--artifact-line` grid, a 2px rule under
  the header row, and in a dense table the 1px 6px cell padding of ASK's
  2026-06-16 dense-table direction. A `num` column, header included, is
  right-aligned. A `key` cell's value is inline emphasis.
- An optional quoted caption follows the roles and must contain visible text.
  It renders as the table's `caption` in the metadata role, which keeps the
  case the author wrote: a caption carries payload text whose case can carry
  meaning (`mW`, `pH`).
- A header takes the label role, which sets its text in capitals. Where a
  header's case carries meaning (`mW` is not `MW`), its column role carries
  the one modifier `:authored-case`, as in `:::table dense key text
  num:authored-case`. That column's header, and its label in every body cell,
  sit in `span.uo-authored-case`, which keeps the case the author wrote and
  changes no other value of the label role; every other header keeps the
  capitals. An authored-case header must contain visible text, and holds text
  and inline emphasis only. The span is a UO value on the label role, declared
  to the rendered check as a profile with its exact count.
- Every body cell carries `data-uo-label`, its column's header text with tags
  removed and whitespace collapsed, and a `span.uo-cell-label` holding that
  header cell's own inline markup, in the label role. The build checks the
  attribute against its header and the element's text against the same
  header.
- Text outside a table and a preformatted block wraps: an ordinary word moves
  to the next line whole, and only a token longer than the line breaks inside
  itself. On screen a preformatted block keeps its lines and scrolls inside
  its own box.
- In a table cell, the header row included, a word moves to the next line
  whole and breaks inside itself only when it is wider than its column. A
  `key`, `num` or `status` value never breaks. Code and links may break
  anywhere: they are the long unbroken tokens. A column never narrows below
  its longest word, so a table whose values cannot fit shows as rows instead
  (below).
- Every table shows one row at a time at widths of 960px and below (a screen,
  or a print page that narrow), and so does a table with more columns than the
  reading column can hold: a dense table of 7 or more columns or a narrative
  table of 6 or more while the column is below its full 1120px, and a dense
  table of 9 or more or a narrative table of 8 or more at any width. The
  thresholds were measured on synthetic tables of 2 to 9 columns (identifiers,
  dates, numbers, status words, long words, links and digests) at widths from
  375px to 1920px; a table with unusually long words can still need more room
  than its column count suggests. In the rows view each body cell is a block
  whose `span.uo-cell-label` shows its column's header above its value. The
  header row stays in the document but is moved out of view with a clip, not
  removed with `display: none`. In Chrome's accessibility tree the table, its
  rows and its column headers remain, and a stacked cell's accessible name
  begins with its label ("Count 12"). Screen readers and other browsers are
  not tested. No cell is dropped and nothing scrolls sideways.
- The visible label is an element carrying the header cell's own inline
  markup, not generated text, so a link in a header is a working link in
  every stacked cell of that column and inline code is still code. A run of
  whitespace, no-break and other space characters included, shows as one
  space in the checked attribute; the element reproduces the header's own
  text. The label is left-aligned in every column, a `num` column's included,
  and selecting a stacked row copies the labels with the values.
- Because the header row is out of view in the rows view, a header link inside
  it would otherwise take keyboard focus while invisible. When anything in
  that row is focused the row returns to view, stacked, so the focused
  element is on screen. The same link is reachable without it, in the visible
  label of every cell in its column.
- A disclosure takes the design-system disclosure treatment: a flat panel, a
  summary in the operative-label metrics and a trailing indicator, turned while
  closed. Its summary keeps the case the author wrote, for the reason given for
  the caption above: a UO value on the treatment, declared to the rendered
  check as a profile. Its content sits in `div.uo-details__body`, a section
  whose runs of blocks are prose runs.
- Keyboard focus on a disclosure's summary, the mark slot's included, is the
  design system's: the treatment draws a 2px outline around the trigger and
  turns its indicator magenta. A link's focus is also the design system's:
  `surface-text-link`'s own underline. No UO stylesheet declares an outline.
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

### Emitted classes

The build emits these class sets only, each on the element listed, and the
final-HTML allowlist compares each element's class tokens with them. A
`uo-*` class is a UO chrome or geometry hook, styled by
`artifact.template.html` or the renderer's geometry stylesheet, or a
structural hook the allowlist places. Every other class is design-system-ASK's:
a document-register role or composition, a treatment or a panel axis, styled
by the vendored `_dsa-surface/` modules.

```text
element   emitted class set
main      uo-md doc-flow
section   doc-section
div       uo-shell
div       uo-status-rail
div       doc-prose
div       doc-section
div       doc-hierarchy
div       uo-details__body surface-disclosure-body doc-section
div       uo-reviewer-status surface-separate surface-emphasis surface-emphasis--cyan surface-material-page surface-attach-free surface-elevation-flush doc-group
div       uo-reviewer-status__body doc-prose
div       uo-proof surface-separate surface-emphasis surface-emphasis--violet surface-material-page surface-attach-free surface-elevation-flush doc-group
div       uo-proof__body doc-prose
div       surface-emphasis-rail doc-group
div       surface-separate surface-material-panel surface-attach-free surface-elevation-flush doc-group
div       doc-pre doc-pre--structured
div       doc-pre-group
header    uo-head doc-titled
dl        uo-head__meta
dt        doc-label
dd        doc-meta
details   uo-index surface-disclosure surface-material-panel surface-attach-free surface-elevation-flush
details   uo-details surface-disclosure surface-material-panel surface-attach-free surface-elevation-flush
summary   uo-index__mark
nav       uo-index__list surface-disclosure-body
svg       uo-mark
span      doc-label
span      uo-status-rail__sep
span      surface-disclosure-label
span      surface-disclosure-indicator
span      uo-cell-label doc-label
span      uo-authored-case
footer    uo-foot
p         doc-body
p         doc-body surface-emphasis-rail
p         doc-meta
p         uo-reviewer-status__flag surface-emphasis-chip
p         uo-proof__flag surface-emphasis-chip
p         uo-proof__title doc-subsection-title
p         surface-emphasis-chip surface-emphasis--magenta
h1        doc-title
h2        doc-section-title
h3        doc-subsection-title
h4        doc-deep-title
li        doc-body
ol        doc-toc-list
blockquote doc-quote
pre       doc-pre
pre       doc-pre-part
code      doc-code
a         surface-text-link
a         doc-toc-link surface-text-link
table     doc-dense-table
caption   doc-meta
th        doc-label
td        doc-table-cell
td        doc-body
```

These elements may also carry no class, each only where named: a quotation's
own `p` and its attribution `footer`; a contents entry's `li`; an authored
disclosure's `summary`; a narrative `table`; and `ul`, `ol`, `strong`, `em`,
`br`, `hr`, `thead`, `tbody` and `tr`. A container's element may add its
`uo-local-<name>` class (below) to the set it emits: a part's section, a
question's or finding's section, an authored disclosure, a table, a quotation,
a callout group, a framing or synthesis panel and a structured block. The
allowlist also places each set: the wordmark's `svg` only in the mark slot's
label, a structured line only inside a structured block, a peer group only
directly in its block, a dense table's cells as `.doc-table-cell` and a
narrative table's as `.doc-body`, and so on. Any other class or placement
fails the build.

### Payload-local CSS

Any container except `:::part 01` and `:::part 10`, which carry the generated
masthead and seal line, `:::banner` and `:::group` may carry one
`local=<name>` token, where `<name>` matches `[a-z][a-z0-9-]{0,31}`. It emits
`class="uo-local-<name>"` on that container's element only (a callout with a
hook renders as a railed group, never as one paragraph). `--local-css` adds a third `<style>` block holding
the file's bytes unchanged; the package MANIFEST records their sha256. The file:

- must scope every selector under `main.uo-md .uo-local-<name>`, for a name
  the source uses, with no sibling (`~`, `+`) or column combinator outside
  brackets and parentheses, no quote character (write attribute values
  unquoted) and balanced brackets and parentheses, and after that scope may
  name no renderer hook (a `uo-` class, in any form) and may not select by the
  `class` attribute;
- may not contain comments, at-rules, `url(`, `image-set(` or another function
  that can load a resource, a quoted string inside a function, `</`,
  backslashes, custom property declarations or `!important`.

The build checks selectors, not the effect of declarations: a scoped rule can
still move, hide or overlay its own container's content. Package review checks
the rendered effect, and that local CSS does not re-derive a shared role; its
rendered check fails a local rule that changes a governed role's type, except
inside a declared UO profile (an authored-case disclosure summary or table
header), whose own text the check does not re-measure: there, package review
reads the local rules that can reach it.
Local names and local CSS belong to the payload and stay operator-side; none
enters this repo.

### What the build refuses

The build fails, writing nothing, when:

- the source breaks the grammar or the anatomy checks below, or contains raw
  HTML;
- a table role carries a modifier other than `:authored-case`, or an
  authored-case header is empty or holds anything but text and inline
  emphasis;
- the final HTML carries an element, class or attribute outside the renderer's
  allowlist, or its CSS carries `@import`, a `url(` other than an embedded
  font, or `image-set(` or another function that can load a resource;
- a vendored `_dsa-tokens/` or `_dsa-surface/` file is missing, or its bytes
  do not match the sha256 recorded in its directory's `MANIFEST.md`, or either
  manifest's commit or short row is malformed, or the two manifests name
  different commits;
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
- **The document register, adopted.** The design-system document register
  (`surface-panel.css`, `surface-text-link.css`, `surface-document.css`,
  `surface-treatments.css`) is consumed **verbatim** and inlined at seal time,
  after the foundation, in the owner's sealed-use order. Every text element the
  renderer emits takes one of its roles, and the Class B `output-artifact` v3
  contract applies: the UO stylesheets set no type metric and no text
  foreground, and write their geometry at zero specificity.
- **No fork.** `diagrams.css` is not vendored, imported, or forked, and the
  register's modules are never edited here: a change to a role is a
  design-system change.

### Vendored snapshots — build inputs, not sources of truth

`_dsa-tokens/` is a **pinned snapshot** of the design-system tokens + fonts and
the assigned wordmark, and `_dsa-surface/` of the document register's four
modules, vendored so artifact builds are **reproducible without a sibling
checkout** of `design-system-ASK`. They are explicitly:

- **build dependency snapshots, not forks** and not second sources of truth;
- **pinned, at one commit** — each `MANIFEST.md` records the exact upstream
  commit SHA and a per-file `sha256`, and the two commits must be equal; the
  build verifies every vendored file's bytes against those hashes before
  sealing, and the seal line and package MANIFEST record the commit only when
  every file matches, so any drift is auditable. That the commit row names the
  upstream state those bytes came from is established when the snapshots are
  re-synced and reviewed; the build has no upstream checkout and does not
  re-check it;
- **updated only by explicit re-sync** from upstream (a deliberate operator
  action), never silently, and always together.

`design-system-ASK` remains the upstream source of truth for the tokens and the
register. This repo holds frozen copies for reproducible rendering.

## Light / dark contract (Class B v3)

This template follows the [design-system-ASK](https://github.com/apexSolarKiss/design-system-ASK) **Class B `output-artifact` v3**
contract (`c7de5ff`). **Foreground is inherited, not rebound.** The
foundation resolves `--fg-1/-2/-3` to **dark ink in light**
(`#6A637F` / `#827399` / `rgba(130,115,153,.62)`) and lavender in dark, and
every text role sets its foreground through them. The template adds **no local
`--fg` or `--line` rebind** and copies none of the foundation's theme blocks;
`colors_and_type.css` is consumed verbatim, and its own `prefers-color-scheme`
bridge carries the automatic dark theme.

The **one sanctioned artifact-layer override is line intensity.** The foundation
hairlines (`--line-*`, white `.45` / `.22`) read too faint for report rules,
borders, table lines, and dividers on the light field. So the template defines a
**scoped `--artifact-line` / `--artifact-line-soft`** (stronger white in light;
the foundation lavender lines in dark) and points UO's own lines at it: the
status rail, the table grid and the seal line. It never reaches a text
foreground, a passage rail, a hierarchy rail or a panel, which stay the
register's. The foundation `--line-*` tokens are left untouched.

| Role | Token | Light | Dark |
|---|---|---|---|
| Foreground (text) | `--fg-1/-2/-3` | **inherited** dark ink (`#6A637F` / `#827399` / `rgba(130,115,153,.62)`) | inherited lavender |
| UO's own lines | `--artifact-line` | white `rgba(255,255,255,.90)` | `var(--line-1)` (foundation lavender) |
| UO's softer dividers | `--artifact-line-soft` | white `rgba(255,255,255,.55)` | `var(--line-2)` (foundation lavender) |

Design principles:

- **Foreground is the foundation's job**, through the register's roles. The
  artifact does not re-declare `--fg-*`. (Re-declaring it is a hard fail.)
- **Line intensity is the one artifact override** — on UO's own lines only,
  white at higher alpha in light, foundation lavender in dark. White is
  in-palette; the override never touches foreground. The register's hierarchy
  rail keeps its own `--line-2`.
- **Dark mode is the foundation's** — its dark `@media` / `[data-theme="dark"]`
  blocks resolve `--fg-*` and `--line-*` to lavender; `--artifact-line`
  inherits the foundation lines in dark.

The template's dark selectors are the foundation's own
(`:root[data-theme="dark"], .theme-dark`, and the `prefers-color-scheme`
bridge), so `--artifact-line`, `--artifact-line-soft` and `--uo-mark` resolve
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
block and a structured line wrap in print instead of being cut off at the page
edge. A closed disclosure prints closed: its content prints only if a reader
opened it first.

**History (resolved):** an earlier version of this template carried a local
`--fg` rebind, because the foundation light ramp was still white and base-element
rules (`p`/`h1`/`h2 { color: var(--fg-1) }`) win over scoped container color. The
foundation fix (`f9eed18`) made that rebind redundant; the 2026-06-04 re-sync to
`040e7ca` dropped it and adopted the scoped `--artifact-line` line-intensity
overlay, aligning to the Class B v2 contract. The adoption of the document
register (U6) moved every text style to the register's roles, retired the
template's own prose, heading, table and disclosure styles and its unreached
card, candidate, chip and panel styles, and retired its copy of the
foundation's dark block.

## Rendered conformance check

Package review runs design-system-ASK's rendered checker,
`tools/check-role-conformance.mjs`, on the sealed file, at the design-system
commit the package MANIFEST records, with `--profiles` naming a file that
holds exactly the JSON the MANIFEST's "Rendered-check profiles" section gives.
The check must pass at 1440 and at 375 with mobile emulation, in both themes,
with no finding and nothing listed as `unmapped`. A page that reports
`vacuous` has adopted nothing. The profiles declare the document's UO-owned
roles, each with its exact count: today two, the authored-case disclosure
summary, present when the document has an authored disclosure, and the
authored-case table header, present when a column is declared
`:authored-case`. The rendered check does not compare letter case; the build
places the authored-case span and the unit suite checks its one declaration.
The build checks structure; only the rendered check proves computed
presentation.

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

A seal for a TMK-facing artifact must also descend from the commit that landed
the document-register adoption (U6) on `main`: the merge of the change that
added this paragraph. Check it with `--descends-from <that commit>`. A commit
cannot name its own merge, so the operator render workflow records that
commit when U6 lands; no TMK-facing artifact is sealed through this path
before it.
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
5. Run the mandatory preflight and the rendered conformance check on the
   sealed HTML.
6. Deliver the package for human review.

Steps 2 and 3 are this template's job. Steps 1, 4, 5 and 6 are operator-side.

## Re-syncing the token snapshot

When the design-system tokens or the document register change upstream and a
refresh is wanted (a deliberate operator decision), re-copy, from one target
[`design-system-ASK`](https://github.com/apexSolarKiss/design-system-ASK) commit, `colors_and_type.css`, `fonts/*.woff2` and
`assets/logo-ASK.svg` into `_dsa-tokens/` and the four register modules into
`_dsa-surface/`; regenerate both `MANIFEST.md` files with that commit SHA and
the per-file hashes; and render new artifacts at the new pin. The two
snapshots are always re-synced together: the build refuses two commits. A
sealed artifact keeps the pin it was sealed with and is never regenerated to
track the new state. Until a re-sync lands, builds are pinned to the recorded
SHA.
