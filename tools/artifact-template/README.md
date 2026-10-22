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
modules, verbatim) + in a document that annotates, the three semantic-state
modules (verbatim) + the UO overlay and geometry stylesheet + base64-embedded
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
└── _dsa-surface/           VENDORED, PINNED design-system-ASK document register and
                            semantic-state modules (build input)
    ├── MANIFEST.md         the same commit as _dsa-tokens/, + per-file sha256
    ├── surface-panel.css · surface-text-link.css · surface-document.css · surface-treatments.css
    │                       inlined verbatim, in that order, after the token CSS
    └── spectral-state.css · evidence-state.css · review-semantics.css
                            the semantic-state modules (the last carries the Review Semantics
                            composition): inlined verbatim, in that order, after the register,
                            only in a document that annotates
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
:::disclose detail "S"             directly inside :::part 04 of a          div.uo-details__body
                                   guided-review document, after a visible
                                   block in its own section
:::disclose provenance "S"         directly inside :::part 10, at most once
:::table [dense] <role per column> inside a part, :::question, :::finding,  data-uo-cell on every th and td;
         ["C"]                     :::disclose or :::range, around exactly  data-uo-label + label element per td;
  (a role may add :authored-case)  one pipe table                           caption C; dense: table.doc-dense-table;
                                                                            authored-case: span.uo-authored-case
:::banner review-status            directly inside :::part 01, at most      a cyan emphasis panel: its chip, then
                                   once                                     its body in div.uo-reviewer-status__body
:::banner proof ["T"]              directly inside :::part 01, at most      a violet emphasis panel: its chip, title
                                   once                                     T if given, its body in div.uo-proof__body
:::quote ["A"]                     inside a part, :::question, :::finding,  blockquote.doc-quote; attribution A in
                                   :::disclose, :::callout or :::range      its footer
:::callout                         inside a part, :::question, :::finding,  p.doc-body.surface-emphasis-rail for one
                                   :::disclose or :::range                  paragraph, else div.surface-emphasis-rail
:::framing thesis|question         directly inside a part 02 to 09, or in   the flat panel, chipped "thesis" or
                                   a :::range directly inside one, at most  "question space"
                                   once, before its first ### or ####
:::synthesis                       directly inside a part 02 to 09, or in   the flat panel, chipped "compression"
                                   a :::range directly inside one, at most
                                   once, as the part's last content; only
                                   notes, and rows or lists without a
                                   review item, follow it
:::structure                       inside a part, :::question, :::finding,  div.doc-pre.doc-pre--structured
                                   :::disclose, :::callout or :::range
:::group                           directly inside :::structure             div.doc-pre-group, a declared peer group
:::range                           directly inside a part 02 to 09,         div.doc-group.doc-annotation-range
                                   :::question, :::finding or :::disclose   .surface-labeled-range: its row first,
                                   (not provenance); never nested           then the blocks it covers
:::annotate                        where :::range sits: first in a          div.doc-annotations, an annotation row:
                                   :::range; holding a review item, as an   its items, in order
                                   explicit-target prompt immediately
                                   before a :::range; holding none, after
                                   a heading or a block. Or first in a
                                   :::note
:::annotate list                   as :::annotate without a review item,    dl.doc-annotation-list: its Item line,
                                   never in a :::note or a :::range         then per axis a dt.doc-label key and a dd
:::annotate document               at top level, between :::meta and the    div.doc-annotations under the masthead
                                   first :::part, at most once              title in part 01
:::note <name>                     directly inside a part 02 to 09,         div.doc-hierarchy.doc-group
                                   :::question, :::finding or :::disclose   .doc-annotation-note, id uo-note-<name>;
                                   (not provenance), after the block or     in a plain list item, inside that item
                                   range holding a passage mark naming it,  after its text
                                   with only notes and rows or lists
                                   without a review item between
:::note not-yet-testable           directly inside a part 02 to 09,         div.doc-group.doc-annotation-note
                                   :::question, :::finding or :::disclose   [data-evidence="not-yet-testable"]
                                   (not provenance), after a heading, a
                                   block or a range, or after a row, list
                                   or another note
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
  or `####` heading. `:::synthesis` closes a part: after it come only notes,
  and rows or lists without a review item, outside its panel; a review
  judgment on it is a `:::range` around it, which then closes the part in its
  place. Both take the design-system flat panel, chipped "thesis", "question space"
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
  rule. A table's text takes these shared roles; its geometry stays UO's
  (below), and UO does not adopt the design system's document table
  composition, which scrolls a table sideways in its own box. Which tables are
  dense is the author's declaration, never inferred.
- The table's geometry is UO's: a 1px `--artifact-line` grid, a 2px rule under
  the header row, and in a dense table the 1px 6px cell padding of ASK's
  2026-06-16 dense-table direction. A `num` column, header included, is
  right-aligned. A `key` cell's value is inline emphasis.
- An optional quoted caption follows the roles and must contain visible text.
  It renders as the table's `caption` in the metadata role, which keeps the
  case the author wrote: a caption carries payload text whose case can carry
  meaning (`mW`, `pH`).
- A header takes the label role, which sets its ordinary text in capitals.
  Inline code in a header keeps its source case, in the header row and in the
  header's repeated label in every body cell alike: the label role leaves code
  in the case its source wrote. Where a header's case carries meaning (`mW` is
  not `MW`), its column role carries the one modifier `:authored-case`, as in
  `:::table dense key text num:authored-case`. That column's header, and its
  label in every body cell, sit in `span.uo-authored-case`, which keeps the
  case the author wrote and changes no other value of the label role; every
  other header's ordinary text keeps the capitals. An authored-case header
  must contain visible text, and holds text and inline emphasis only. The span
  is a UO value on the label role, declared to the rendered check as a profile
  with its exact count.
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
  `key`, `num` or `status` value never breaks, except an annotation row: a
  status cell's annotation row wraps its metadata, each mark staying whole,
  rather than widen the column. Code and links may break anywhere: they are
  the long unbroken tokens. A column never narrows below its longest word, so
  a table whose values cannot fit shows as rows instead (below).
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
- `:::disclose detail` is a guided review's optional closed detail ("What
  stays visible"): directly in part 04, never in 08. The build requires a
  visible block before it in its own section, the one its last heading opens
  (or part 04 itself before any heading): a paragraph, list, code block,
  table, quotation, callout, structure, range or panel. A heading alone, a
  rule, an annotation row, list or note, or another disclosure is not one. The
  build cannot check that this block is the reading the detail details, or
  that it states every claim and qualification: that stays a package-review
  check. Its body is a section, so `###` and `####` headings compose inside
  it, and it may hold tables, quotations, callouts, structures, ranges,
  annotation rows and lists, notes and Markdown blocks, but no request for a
  judgment ("Disclosures and the synthesis", below). In a document of another
  kind, or anywhere else, it fails the build.
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
- `:::range`, `:::annotate`, `:::annotate list`, `:::annotate document`,
  `:::note` and the inline `{{...}}` forms carry review annotations ("Review
  annotations", below). Any other `{{`
  fails the build, in Markdown text, a container token or a meta value: a
  literal `{{` belongs in a code span. Code, preformatted and structured
  blocks keep their text as written.
- **Raw HTML in the source fails the build**, including comments, in Markdown
  text and in structure lines. Put literal tags in a code span or write
  `&lt;`; `\<` is not an escape. Plain-text carriers are escaped instead and
  show their text as written: meta values, quoted container tokens (a
  caption, a summary, an attribution, a banner title), annotation item text
  and passage-mark words (which may also hold a link).
- Links are `https://` or `http://` only. Images are not accepted: an image is
  a relative dependency.

### Review annotations

A review document may show review state, evidence state, architectural state,
basis and checks beside the content they concern, through `design-system-ASK`'s
opt-in Review Semantics composition (`review-semantics.md`), adopted for
presentation. UO's review anatomy (its parts, banners, table roles and domain
vocabulary) stays `urban-observatory`'s own; annotation presentation and the
scopes it draws are `design-system-ASK`'s. The renderer follows the composition
as of `design-system-ASK` `705a195` (#185), the commit both snapshot manifests
pin. The re-sync that adopted it moved this repo's pin from `53fa86e` (#169)
and crosses the owner's events #170 to #185, which `_dsa-surface/MANIFEST.md`
records file by file: #170 to #177 change no vendored file; #178 added the
composition; #179 and #180 change no vendored file, and #181 only comment
text; #182 to #185 replaced the composition's first model, so this repo
adopts it only in its #185 form. A review mark is the shared bordered label
(#182); a judgment on whole blocks opens a labeled range with a scope rail
(#183, #184); exact words take the scope underline, pending or decided, and a
whole list item can be its own range (#185). The three semantic-state modules,
`spectral-state.css`, `evidence-state.css` and `review-semantics.css` (the
last carries the composition), are inlined verbatim after the register, in
that order, only in a document that holds at least one annotation; the
package MANIFEST's row "modules inlined, in order" records what a render
embedded, and the seal line names the semantic-state modules when they are
sealed. A document without annotations inlines the four register modules
alone. The owner's decision-record and composition rules bind authors as
written there (`review-semantics.md`, "The decision record" and "Composition
rules"): a shown decision names what, who and scope; a note quotes the words
it concerns; No decision recorded appears only where its absence matters;
origin survives adoption.

```text
item line                    renders
item: <name>                 the key Item, then the name (an annotation list's first line)
state <role>[: <meta>]       a state mark (a square), then its metadata
basis: <value>               the key Basis, then its value
evidence <role>[: <meta>]    an evidence mark (a dot), then its metadata
review <word>[: <meta>]      a review mark (a bordered label), then its metadata
check: <value>               the key Check, then its value

review     proposed (Proposed) · correction-requested (Correction requested,
           shown as proposed) · open (Open question) · accepted (Accepted) ·
           declined (Declined) · none (No decision recorded)
evidence   supported · partially-supported · unresolved · weakened ·
           not-yet-testable
state      earned · structural · partial · deflated · held · external ·
           proposed · neutral
```

- Items read in one fixed order: state, basis, evidence, review, then check;
  repeats of one axis sit together. A row that opens a range or stands as a
  prompt leads with its one review item, and its other items follow in that
  order: review, state, basis, evidence, check. A note's row and the
  document's record keep the fixed order. An item out of order, an unknown
  axis or word, or a value with no visible text fails the build with its line.
- `<meta>` and `<value>` are plain text, shown as written: no Markdown, and
  markup characters are escaped, as in a title or a caption. `basis` and
  `check` need a value. `review accepted` and `review declined` show a
  decision and need its record (what, who, scope). `review
  correction-requested` names a pending request for existing words to change
  and needs its record (on what, who asked). The review item that opens a
  range or an item host, and a prompt's, need their record too, whatever
  their word. The build can only require that something is written.
- `state proposed` and `review proposed` on one item share a word and a
  value, so the keyed list carries them, one key each: a row, a note's row or
  a table cell holding both fails. The document's record is a row and never a
  list, so it cannot carry the pair either: a UO capability limit for now.
  `review correction-requested` beside `state proposed` is not that pair.

**Whole blocks: a range.** A review judgment on one or more whole blocks
opens a range, even over one paragraph: a row placed after a block can be read
as introducing what follows it.

```text
:::range
:::annotate
review open: <what it concerns · its scope · who decides>
basis: <value>
:::
<the blocks it covers>
:::
```

- `:::range` emits `div.doc-group.doc-annotation-range.surface-labeled-range`.
  Its first child is one `:::annotate` row, which names exactly one review
  judgment, first, with its record after `:`; the blocks it covers follow,
  runs of blocks in a prose run. It covers at least one block. It takes no
  token and no `local=` hook.
- A range covers paragraphs, plain lists, quotations, callouts, structures and
  a whole `:::table`; a range sitting directly in a part may also cover that
  part's `:::framing` or `:::synthesis`, whose own position rules still hold.
  A quotation or callout inside a range keeps its own rail, a panel its own
  perimeter: the range's scope rail sits outside the content edge.
- One judgment per range. Inside a range the build refuses, naming the line:
  another range (ranges never nest; blocks judged otherwise are a sibling
  range), another row or list after its first row, a note, a heading (a range
  over a heading alone is a UO capability limit for now), a list item that
  opens as an item host, and a `:::table` whose cells carry review items.
- Words inside a range judged on their own take a passage mark, and their note
  follows the range.
- Two ranges in a row keep the owner's 24px passage buffer, so their rails
  never read as one. The owner composes it between siblings, and for a list
  that opens or closes on an item host one wrapper deep. UO's own wrappers (a
  heading's section, a question, a finding and a prose run) can hold a range
  or a host list as their last or first block; and a range around a panel
  follows them in its part after the sections close. So the renderer's
  stylesheet composes the same buffer across them: where one block ends on a
  scope rail through its last children and the next starts on one through its
  first, the next block takes `--space-5` as its top margin. It adds a block
  margin only, never an inline margin, padding, border or rail on a range;
  only a document that annotates carries it, as only it inlines the
  semantic-state modules. The rendered check's buffer rule counts siblings
  only, so it does not see through these wrappers; the renderer's tests check
  which block pairs the rule's selectors reach, and no maintained check
  measures the rendered gap.
- A range sits directly in a part 02 to 09, a `:::question`, a `:::finding` or
  a question-detail, evidence or detail disclosure; never in part 01 or 10 or
  the provenance disclosure.

**A separate question: a prompt.** A row holding a review item outside a
range stands only as an explicit-target prompt: its own row, review item
first, immediately before the `:::range` whose content it asks about, or
before another prompt to that range. Its record names the content below as its
target, the scope of its question and who decides; a bare label that names no
target is no prompt, so a prompt without a record fails. Anywhere else, after
a block included, a review row fails: a whole-block judgment opens a range.

**Rows without a review item.** A row holding only state, basis, evidence or
check items opens no range and follows the heading or block it qualifies (a
range included), outside any prose run; as its parent's first child, or right
after another row, list or note, it fails. The owner also lets such a row
follow the text of a plain list item; UO cannot express that yet, a UO
capability limit for now: a row sits only between blocks, and a list item
that opens with items other than a review item fails as an item host. Raise
it with the owner.

**An item: an annotation list.** `:::annotate list` is one item answering
several questions: a `dl.doc-annotation-list` with one key per axis present,
in the fixed order. It names its item first, in an `item: <name>` line of its
own, rendered as the key Item; the line is required whenever the list holds a
review line, and its review lines judge that item, never the blocks beside the
list. A list answers each question once: a second judgment at another scope
is its own `:::annotate list`, naming its item in its own `item:` line, and a
second record of one non-review axis at another scope goes with the first in
one row, which may repeat that axis. It sits where a row without a review
item sits, and never in a note or a range. `list` and `document` are the only
tokens `:::annotate` takes; it takes no `local=` hook.

**The whole document: its record.** `:::annotate document` holds the record
that names the document, under its title: at top level, between `:::meta` and
the first `:::part`, at most once. It renders as a plain row in part 01's
masthead, directly under the title and before its identity list: no range, no
rail. Its items keep the fixed order, and a review item is optional. Its
record names the document (for example its id and version).

**A whole list item: an item host.** A list item whose text opens with
items, the first a review item, is its own range:

```text
- {{review accepted: <record>}}{{basis: <value>}} The item's words…
```

- It emits `li.doc-annotation-range.surface-labeled-range`, the item's row
  first, then its words in a `p.doc-body` of their own (the item itself takes
  no content role); a loose item keeps its further paragraphs, and a tight one
  its nested list, after them.
- Item hosts may follow one another, and plain items may sit between them.
  UO's lists keep the owner's default 24px indentation, so no
  `--surface-labeled-range-indent` is set.
- One review item per host, first, with its record after `:`, before any of
  the item's words; the build refuses a bare review item (whatever its word),
  a second review item, words before the row, an item host in a nested list,
  and one inside a range, a note, a quotation or a callout. A table's cells
  hold no list, and a structure's lines are text, shown as written. A passage
  mark in a host's words has its note after the list.

**Exact words: a passage mark.** `{{mark <role> <note>: exact words}}`, with
role `proposed`, `open`, `accepted` or `declined`, marks the words a judgment
concerns, pending or decided. It emits
`mark.doc-passage-mark.surface-scope-underline`, the shared scope underline:
one solid line under words that keep their own color, never a tint. It names
its note through `aria-describedby`. No decision recorded marks no words:
`none` fails.

- It sits in a paragraph or list item directly inside a part 02 to 09, a
  `:::question`, a `:::finding`, a `:::range` or a question-detail, evidence
  or detail disclosure; never in a heading, link text, a quotation, a
  callout, a banner, a framing or synthesis panel, a table, a structure, a
  note or the provenance disclosure.
- The marked words are plain text and may hold a link written `[text](url)`,
  which keeps its own `a.surface-text-link` treatment inside the mark; the
  link's text is plain text too. Inside `{{...}}` (a cell item or passage-mark
  words) a backslash escape or a code span fails the build, and so does a link
  anywhere but in passage-mark words; in an `:::annotate` row the same
  characters show as written.

**Notes.** `:::note <name>` is the record a passage mark points to: `<name>`
matches `[a-z][a-z0-9-]{0,31}` and is unique in the document, and the note's id
is `uo-note-<name>`. It holds one `:::annotate` row first, then paragraphs and
lists only. Its row records the judgment its marks show: a proposed mark needs
a `review proposed` or `review correction-requested` item, an open mark
`review open`, an accepted mark `review accepted` and a declined mark `review
declined`. It holds no other review item: one whose role no mark naming the
note shows, `review none` included, fails, since it would judge the blocks
before the note from a row placed after them. Its other items (state, basis,
evidence, check) may sit beside them.

- The author writes a note after the block holding the mark, or after the
  range that holds it, in the same container, with only notes and rows or
  lists without a review item between: another block, a container or a
  heading before it fails, a heading inside a container included. So a mark
  inside a disclosure has its note inside that disclosure, and a mark outside
  one never names a note inside it.
- For words in a plain list item, one that is neither an item host nor held
  by a range, the author writes the note after the list, and the renderer
  places it inside that list item, after the item's text, where it takes the
  owner's 12px attachment. For words in an item host, the note stays after the
  list; for words in a list a range holds, it follows the range.
- A note records the words of one list item, as it records those of one
  block: marks naming one note in two items of a list, an item and its nested
  item, or a plain item and an item host, fail the build.
- `:::note not-yet-testable` is Evidence State's not-yet-testable note: its
  row carries an `evidence not-yet-testable` item and no review item, it draws
  that role's dashed rail instead of the hierarchy rail, and no passage mark
  names it.

**Tables.** UO's tables keep their own grid and rows view; every field stays
visible, and UO does not adopt `.doc-table-scroll` or its range lane.

- In a `:::table` body cell of a `text` or `status` column, `{{<item line>}}`
  is an item, for example `{{review accepted: v3 · owner · this copy}}`. A
  cell holding items holds them only, in the fixed order; they emit the
  cell's annotation row, `span.doc-annotations`, on its first baseline, and
  judge that cell, or its row where the table makes the association
  unambiguous. An item is never in a header, a `key` or a `num` column.
- A judgment on a whole table is a `:::range` around the `:::table`. A table
  whose cells carry review items cannot sit in a range: the owner raises that
  composition rather than drawing it.
- A per-cell block range is a UO capability limit: UO's cells hold inline
  text, so a `:::range` inside a `:::table`, and `{{range` in a cell, fail the
  build with that diagnostic. Raise it with the owner.

**Disclosures and the synthesis.**

- Inside a question-detail, evidence or detail disclosure, rows, lists,
  ranges, notes, passage marks and cell items are scoped as anywhere else, and
  a mark and its note stay in one disclosure. They never carry what "What
  stays visible" keeps ALWAYS VISIBLE: an evidence row's assessed state, a
  live constraint, a finding's limit or a qualification a short-reading claim
  needs stays in the visible lines. Nor do they stand in for a record about
  the question, finding or claim itself. A closed disclosure hides its
  annotations with its content.
- A guided review's detail disclosure holds no request for a judgment: an
  Open question, Proposed or Correction requested item there, in a row, list,
  range, note, cell, item host or passage mark, fails the build, since what
  the reviewer is asked to judge stays visible. Its review items record
  judgments: Accepted, Declined or No decision recorded.
- A synthesis, or the range around it, is its part's last substantive
  content; only notes, and rows or lists without a review item, follow it, and
  a review row after it fails: a judgment on the synthesis is a range around
  it.
- No annotation sits in part 01 or 10 or in a provenance disclosure, a table
  cell's included, but the document's record under the masthead title; none
  sits inside a callout, quotation, banner or panel.

Boundaries:

- The shared composition supplies presentation only. It never replaces UO's
  review anatomy, its banners, its table roles or its domain vocabulary, and
  UO mints no review palette of its own: a role's value appears only on a
  mark's geometry, a range's scope rail, a passage mark's line and the
  not-yet-testable rail, each with its visible words.
- Map by meaning, not color. The cyan review-status banner is not an Open
  question, though both are the emphasis cyan, and the violet proof banner is
  not an evidence judgment; neither banner is recolored. A status column stays
  a status column unless its author chooses marks.
- A displayed decision reports an authority relation and creates none. Color
  confers no evidence and no authority.
- Proof status: the unit suite exercises this grammar, the guided-review
  detail disclosure and the final-HTML allowlist on synthetic sources only.
  The build checks structure and placement. The rendered check checks
  presentation on the sealed file it is run on: its rule C13 applies to every
  bordered label and emphasis chip in every document, and wherever a document
  annotates, its rules C12, C14 and C15 also apply, judging a mark inside a
  closed disclosure once its runner has opened the disclosure. A pass shows
  that a range or a passage mark is drawn as the composition says, not that
  it covers the right content.
  Neither establishes that a judgment's scope is the right one; that stays
  with the author and the reviewer. Neither lifts a kind profile's
  PROVISIONAL status; only a reviewed change to "Kinds" does.

### Emitted classes

The build emits these class sets only, each on the element listed, and the
final-HTML allowlist compares each element's class tokens with them. A
`uo-*` class is a UO chrome or geometry hook, styled by
`artifact.template.html` or the renderer's geometry stylesheet, or a
structural hook the allowlist places. Every other class is design-system-ASK's:
a document-register role or composition, a treatment, a panel axis or a
Review Semantics composition, styled by the vendored `_dsa-surface/` modules.

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
div       doc-annotations
div       doc-hierarchy doc-group doc-annotation-note
div       doc-group doc-annotation-note
div       doc-group doc-annotation-range surface-labeled-range
header    uo-head doc-titled
dl        uo-head__meta
dl        doc-annotation-list
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
span      doc-annotations
span      doc-annotation-item
span      doc-mark doc-label
span      doc-mark doc-label surface-bordered-label
span      doc-meta
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
li        doc-annotation-range surface-labeled-range
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
mark      doc-passage-mark surface-scope-underline
```

These elements may also carry no class, each only where named: a quotation's own
`p` and its attribution `footer`; a contents entry's `li`; an authored
disclosure's `summary`; a narrative `table`; an annotation list's `dd`; and
`ul`, `ol`, `strong`, `em`, `br`, `hr`, `thead`, `tbody` and `tr`. A container's
element may add its `uo-local-<name>` class (below) to the set it emits: a
part's section, a question's or finding's section, an authored disclosure, a
table, a quotation, a callout group, a framing or synthesis panel and a
structured block. The allowlist also places each set: the wordmark's `svg` only
in the mark slot's label, a structured line only inside a structured block, a
peer group only directly in its block, a dense table's cells as
`.doc-table-cell` and a narrative table's as `.doc-body`, an annotation range
directly in a section and never inside another, its row first naming one review
judgment first and no other review mark inside it, an item host only as an item
of a top-level list with its row and then its words, a review row outside a
range only immediately before a range or another such row, an annotation item
only in an annotation row, a review mark only as the bordered label and an
evidence or state mark never one, a mark or its metadata only in an item or a
list's value, a list's Item line first wherever it holds a Review line, a
passage mark only in document body text holding its words and any link inside
them, a facet attribute only on a mark, a passage mark or the not-yet-testable
note, each note's row as its first child, a note directly in a section or in a
plain list item and never in a range, a not-yet-testable note's row carrying
that evidence mark, each note's id named by a passage mark whose role the note's
first row records, no annotation in part 01 or 10 (a provenance disclosure
included) but the document's record directly under the masthead title, and so
on. Any other class or placement fails the build.

### Payload-local CSS

Any container except `:::part 01` and `:::part 10`, which carry the generated
masthead and seal line, `:::banner`, `:::group` and the annotation containers
(`:::range`, `:::annotate`, `:::note`) may carry one `local=<name>` token, where `<name>` matches `[a-z][a-z0-9-]{0,31}`. It emits
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
  carried: no "ASK Design System" chrome. UO's review anatomy — the anatomy,
  the banners, the table roles — is `urban-observatory`'s own; annotation
  presentation is `design-system-ASK`'s Review Semantics. The token CSS
  header's "TIER 3 — ASK instance identity (NOT inherited by children)" stays
  true under an assignment.
- **The document register, adopted.** The design-system document register
  (`surface-panel.css`, `surface-text-link.css`, `surface-document.css`,
  `surface-treatments.css`) is consumed **verbatim** and inlined at seal time,
  after the foundation, in the owner's sealed-use order. Every text element the
  renderer emits takes one of its roles, and the Class B `output-artifact` v3
  contract applies: the UO stylesheets set no type metric and no text
  foreground, and write their geometry at zero specificity.
- **The semantic-state modules, adopted for annotation.** `spectral-state.css`,
  `evidence-state.css` and `review-semantics.css` (which carries the Review
  Semantics composition) are consumed **verbatim**
  and inlined after the register, in that order, only in a document that
  annotates ("Review annotations"). They supply the marks' presentation; UO
  supplies which content carries which mark and the records' values.
- **No fork.** `diagrams.css` is not vendored, imported, or forked, and the
  register's modules are never edited here: a change to a role is a
  design-system change.

### Vendored snapshots — build inputs, not sources of truth

`_dsa-tokens/` is a **pinned snapshot** of the design-system tokens + fonts and
the assigned wordmark, and `_dsa-surface/` of the document register's four
modules and the three semantic-state modules, vendored so artifact builds are
**reproducible without a sibling checkout** of `design-system-ASK`. They are
explicitly:

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

`design-system-ASK` remains the upstream source of truth for the tokens, the
register and the semantic-state modules. This repo holds frozen copies for
reproducible rendering.

## Light / dark contract (Class B v3)

This template follows the [design-system-ASK](https://github.com/apexSolarKiss/design-system-ASK) **Class B `output-artifact` v3**
contract, at the revision the two snapshot manifests record
(`_dsa-tokens/MANIFEST.md`, `_dsa-surface/MANIFEST.md`).
**Foreground is inherited, not rebound.** The
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
The check's rule C13 applies to every bordered label and emphasis chip, in
every document: the framing, synthesis and banner chips, and review marks; it
checks the label's box and edge. Wherever a document annotates, its rules C12,
C14 and C15 also apply: C12 checks the annotation composition's classes,
attributes and vocabulary and its computed outlines, markers, scope rails,
passage lines and note attachment; C14 a range's scope rail, lane, host and
buffer between siblings; C15 a passage mark's line and unchanged words. None
judges whether an item's role is the right one, or whether a range holds the
right blocks. A mark inside a closed disclosure has its words checked at rest
and its presentation once the runner has opened every disclosure.
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
guided-review   04 · 08                         PROVISIONAL
confirmation    07                              PROVISIONAL
```

A profile stays provisional until a declared proof document of its kind has
been rendered and reviewed against it. Only a reviewed change to this section
lifts that status. A kind without a profile must not be rendered through this
template until one is added here.

A guided review's short reading, its 04, is required, and its detail is
optional: closed detail after the visible reading it details ("What stays
visible"). The build places the detail after a visible block in its own
section; whether the visible reading states every claim and the
qualifications each needs is a package-review check, which no build makes.
A guided review's dates stay visible in 02: when the sources it reports were
observed, and when this copy was rendered, which re-checks nothing. A guided
review requires no 06: a finding unit's significance field would have the
author pre-answer the judgment the reviewer is asked to make. The
guided-review profile stays PROVISIONAL until fixture review
earns a reviewed status change; a build that passes does not lift it.

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
  04   every claim of the short reading and each qualification it needs
  06   each unit's status or identifier, finding, significance and limit;
       each evidence surface's title, summary lines, and what it does and
       does not mean; each evidence row's labels, claim and assessed state;
       any quoted source passage the finding relies on; any live constraint,
       confidence cap or other uncertainty on the evidence
  08   the whole register, never reduced to the limits each finding unit states
       (except as below for a guided review)
  10   the seal line

MAY DISCLOSE
  03   a non-central question's detail
  04   (guided-review only) per-finding detail, quoted passages and locators,
       and supporting records, as closed detail after the visible reading; a
       disclosed finding or claim keeps its own status, limit and
       qualifications inside the same detail
  06   field-level evidence listings and finding metadata, beneath visible
       summary lines
  10   the provenance table, as one block
```

In a guided review, unresolved items already stated visibly beside their claims
in 04 are not repeated in 08, and 08 carries the document-level non-claims. In
a guided review, the detail disclosure holds no request for a judgment
("Review annotations").

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
placed inside an allowed disclosure, an annotation's included; package review
checks that nothing this section keeps ALWAYS VISIBLE sits inside one, and
that a guided review's visible reading states every claim and qualification
its detail relies on.

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
A source that uses review annotations must likewise be sealed from a renderer
commit that descends from the commit that landed them on `main`, checked with
`--descends-from <that commit>`: an older renderer renders `{{...}}` literally,
without an error. The operator render workflow records that commit when the
change lands.
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

When the design-system tokens, the document register or the semantic-state
modules change upstream and a refresh is wanted (a deliberate operator
decision), re-copy, from one target
[`design-system-ASK`](https://github.com/apexSolarKiss/design-system-ASK) commit, `colors_and_type.css`, `fonts/*.woff2` and
`assets/logo-ASK.svg` into `_dsa-tokens/`, and the four register modules and
`spectral-state.css`, `evidence-state.css` and `review-semantics.css` into
`_dsa-surface/`; regenerate both `MANIFEST.md` files with that commit SHA and
the per-file hashes; and render new artifacts at the new pin. The two
snapshots are always re-synced together: the build refuses two commits. A
sealed artifact keeps the pin it was sealed with and is never regenerated to
track the new state. Until a re-sync lands, builds are pinned to the recorded
SHA.
