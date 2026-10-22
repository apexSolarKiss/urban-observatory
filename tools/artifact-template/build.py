#!/usr/bin/env python3
"""
Render a urban-observatory human-readable artifact to a sealed, single-file HTML.

Takes a canonical Markdown source and produces one self-contained HTML file:
design-system-ASK token CSS + the design-system-ASK document register (four
modules, verbatim) + in a document that annotates, the three semantic-state
modules (verbatim) + the UO overlay and geometry stylesheet + base64-embedded
fonts + the assigned wordmark as inline svg, all inlined. The output has no
external dependencies — it opens with full styling from any location (local
file, email attachment, copied folder) with no network and no sidecar.

This is the REUSABLE rendering machinery for the UO artifact class. Specific
review packages (e.g. TMK guided-review packages, with their own banner text and
review-orchestration files) are assembled operator-side from this template; they
are not part of this repo.

Design-system inheritance
-------------------------
The visual language is inherited from design-system-ASK by reference. This repo
vendors two PINNED snapshots at one design-system commit (reproducible build
inputs, NOT forks and NOT second sources of truth): `_dsa-tokens/` holds the
tokens, fonts and wordmark, and `_dsa-surface/` the document register's four
modules and the three semantic-state modules (`spectral-state.css`,
`evidence-state.css`, `review-semantics.css`, the last carrying the Review
Semantics composition); each carries a MANIFEST.md, and the two commits must be
equal. Every vendored file is verified on every build, used verbatim and never
edited here; the three semantic-state modules are inlined only when the
document annotates (README, "Review annotations"). The
renderer emits the register's roles, so the type is the register's; the UO
stylesheets carry geometry, and their only value override is line intensity
(`--artifact-line` / `--artifact-line-soft`) on UO's own rules. See README.md,
"Light / dark contract (Class B v3)".

Usage
-----
    python3 -B build.py --source PATH.md --out PATH.html --manifest PATH.md \
        --uo-commit SHA [--local-css PATH.css]

Requires: python3 + the `markdown` package at the version pinned in
requirements.txt.
"""
import argparse
import base64
import hashlib
import html
import json
import os
import re
import sys
import tempfile
import unicodedata
from datetime import datetime, timezone
from html.parser import HTMLParser

import markdown
from markdown.extensions import Extension
from markdown.inlinepatterns import InlineProcessor
from markdown.preprocessors import Preprocessor
from markdown.util import AtomicString
import xml.etree.ElementTree as etree

HERE = os.path.dirname(os.path.abspath(__file__))
# A compiled file beside pin_check.py would be imported in its place, so the
# renderer refuses to start before importing it (README: run with python3 -B).
if os.path.lexists(os.path.join(HERE, "__pycache__")):
    sys.exit("ERROR: __pycache__ directory not allowed in the renderer directory: %s (run build.py with python3 -B)"
             % os.path.join(HERE, "__pycache__"))
sys.dont_write_bytecode = True
if HERE not in sys.path:
    sys.path.insert(0, HERE)
from pin_check import PinCheckError, tree_digest  # noqa: E402
from markdown.extensions.tables import TableProcessor  # noqa: E402

TEMPLATE = os.path.join(HERE, "artifact.template.html")
MANIFEST = os.path.join(HERE, "_dsa-tokens", "MANIFEST.md")
SURFACE_MANIFEST = os.path.join(HERE, "_dsa-surface", "MANIFEST.md")
# The document register's modules, in the owner's sealed-use order: each is inlined verbatim, in this order,
# after the token CSS (design-system-ASK README, "Sealed use").
MODULES = ["surface-panel.css", "surface-text-link.css", "surface-document.css", "surface-treatments.css"]
# The three semantic-state modules (design-system-ASK review-semantics.md, "How to use it"): Spectral State and Evidence
# State, then review-semantics.css, which carries the Review Semantics composition, in the owner's load order. Each is
# inlined verbatim after MODULES, in this order, only in a document that annotates; every build verifies all seven
# _dsa-surface/ files.
STATE_MODULES = ["spectral-state.css", "evidence-state.css", "review-semantics.css"]
BUILD_PY = os.path.abspath(__file__)

MARKDOWN_PIN = "3.8.2"

FONTS = [
    "InterVariable.woff2", "InterVariable-Italic.woff2",
    "JetBrainsMono.woff2", "JetBrainsMono-Italic.woff2",
]

# The renderer's stylesheet: GEOMETRY ONLY. Every text style comes from the
# document register's roles, which the renderer emits; nothing here sets a
# family, size, weight, leading, tracking or text foreground, and every rule
# sits at zero specificity inside :where(), so no rule can beat a role. It
# carries the reading column (its measure, and the container its tables
# query), list, rule and table geometry, cell wrapping, the stacked-rows view
# and print. Three rules are deliberately not zero-specificity, each named:
#   - the authored-case disclosure summary: text-transform: none on an authored
#     disclosure's label, because a summary carries payload text whose case can
#     carry meaning (mW, pH). It changes no other value of the treatment, and it
#     is the rendered check's one declared UO profile (package MANIFEST);
#   - print: a preformatted block wraps on paper rather than being cut at the
#     page edge;
#   - print: the page prints on its own theme ground (in the template).
# One zero-specificity rule sets a type value, also named: text-transform: none on span.uo-authored-case, the
# header text of a column declared :authored-case (a unit such as mW is not MW), the rendered check's second
# declared UO profile. The label role's capitals reach that span only by inheritance, so no specificity is needed.
# Cell wrapping: an ordinary word moves to the next line whole, and hyphenates
# only when it is wider than its column; a number or status value never splits;
# code and links may break anywhere, since they are the long unbroken tokens. A
# status cell's annotation row is the exception: its metadata is a decision
# record, which wraps (white-space: normal on the row; each mark stays whole by
# its own rule) instead of widening the column past the reading width. At
# 960px and below (a screen, or a print page that narrow) every table shows one
# row at a time: each body cell shows its column's header above its value, in a
# span.uo-cell-label carrying the header's own inline markup, and the header row
# is moved out of view with a clip, returning to view when it takes focus.
# The stacked-rows view: each body cell a block whose span.uo-cell-label shows its column's header above
# its value; the header row stays in the document, clipped out of view, and returns to view when it takes
# focus. It applies to every table at 960px and below (a screen, or a print page that narrow), and to a
# table whose columns cannot all hold their values at the reading column's width: measured on the renderer's
# own fixtures (README, "Tables"), a dense table of 7 or more columns and a narrative table of 6 or more
# below the column's full 1120px, and a dense table of 9 or more and a narrative table of 8 or more at any
# width.
WIDE_BELOW_CAP = ("table.doc-dense-table:has(> thead > tr > th:nth-child(7)), "
                  "table:not(.doc-dense-table):has(> thead > tr > th:nth-child(6))")
WIDE_ALWAYS = ("table.doc-dense-table:has(> thead > tr > th:nth-child(9)), "
               "table:not(.doc-dense-table):has(> thead > tr > th:nth-child(8))")
ROWS_VIEW = (
    ":where(.uo-md) :where({t}) {{ display: block; }}",
    ":where(.uo-md) :where({t}) :where(caption, tbody, tr, td) {{ display: block; }}",
    ":where(.uo-md) :where({t}) > :where(thead) {{ position: absolute; width: 1px; height: 1px; overflow: hidden; "
    "clip-path: inset(50%); white-space: nowrap; }}",
    ":where(.uo-md) :where({t}) > :where(thead:focus-within) {{ position: static; width: auto; height: auto; "
    "overflow: visible; clip-path: none; white-space: normal; }}",
    ":where(.uo-md) :where({t}) > :where(thead:focus-within) :where(tr, th) {{ display: block; }}",
    ":where(.uo-md) :where({t}) :where(tbody tr + tr) {{ margin-top: var(--space-3); }}",
    ":where(.uo-md) :where({t}) :where(td + td) {{ border-top: 0; }}",
    ":where(.uo-md) :where({t}) :where(td[data-uo-cell=\"key\"], td[data-uo-cell=\"num\"], td[data-uo-cell=\"status\"]) "
    "{{ white-space: normal; }}",
    ":where(.uo-md) :where({t}) :where(.uo-cell-label) {{ display: block; text-align: left; }}",
)


def rows_view(tables, indent="  "):
    return "\n".join(indent + rule.format(t=tables) for rule in ROWS_VIEW)


# The passage buffer across UO's own wrappers. design-system-ASK keeps 24px (--space-5) between two ranges in a row,
# and between a range and a list that opens or closes on an item host, for siblings and for a list one wrapper deep
# (surface-treatments.css, "THE LABELED RANGE'S LANE" and "THE ITEM HOST"); a host that nests its ranges deeper
# composes its own buffer. UO does: a range or a host list can be the last block of a heading's section, a question,
# a finding or a prose run, and the next one the first block of the next; a range around a panel is lifted to its
# part after the sections close. Where a block ends on a scope rail through a chain of last children inside
# div.doc-section and div.doc-prose wrappers, and the next block starts on one through first children, the next
# block takes the buffer as its top margin: a block margin only, never an inline margin, padding, border or rail on a
# range. A disclosure, a callout, a note or a panel ends the chain: its rails sit inside its own box. RAIL_DEPTH
# bounds the chain at UO's deepest nesting: three heading levels, a prose run, a question or finding, three heading
# levels inside it and its prose run. Only a document that annotates holds a range or an item host, so only its
# stylesheet carries the rule (md_css), as only it inlines the semantic-state modules (inlined_modules).
RAIL_WRAPPER = ":is(div.doc-section, div.doc-prose)"
RAIL_DEPTH = 9


def _rail_edge(edge):
    """The selectors for a block whose first or last (edge) descendant chain, through UO's wrappers, is a range or a
    list that opens or closes on an item host."""
    sels = ["div.surface-labeled-range", ":is(ul, ol):has(> li.surface-labeled-range:%s-child)" % edge]
    for depth in range(1, RAIL_DEPTH + 1):
        chain = RAIL_WRAPPER + ":has(> " + "".join("%s:%s-child > " % (RAIL_WRAPPER, edge) for _ in range(depth - 1))
        sels.append(chain + "div.surface-labeled-range:%s-child)" % edge)
        sels.append(chain + ":is(ul, ol):%s-child > li.surface-labeled-range:%s-child)" % (edge, edge))
    return ", ".join(sels)


RAIL_BUFFER = (":where(.uo-md :is(%s) + :is(%s)) { margin-top: var(--space-5); }"
               % (_rail_edge("last"), _rail_edge("first")))


MD_CSS = """
:where(.uo-md) { max-width: 80ch; margin: 0 auto; overflow-wrap: anywhere; container: uo-body / inline-size; }
:where(.uo-md) :where(ul, ol) { margin: 0; padding-left: var(--space-5); display: flex; flex-direction: column; gap: var(--space-2); }
:where(.uo-md) :where(hr) { border: 0; border-top: 1px solid var(--artifact-line-soft); margin: 0; width: 100%; }
:where(.uo-md) :where(.doc-quote) { display: flex; flex-direction: column; gap: var(--space-4); }
:where(.uo-md) :where(table) { width: 100%; border-collapse: collapse; }
:where(.uo-md) :where(caption) { caption-side: top; text-align: left; padding: 0 0 var(--space-2); }
:where(.uo-md) :where(th, td) { border: 1px solid var(--artifact-line); padding: var(--space-2) var(--space-3); text-align: left; vertical-align: top; overflow-wrap: break-word; }
:where(.uo-md) :where(thead th) { border-bottom-width: 2px; }
:where(.uo-md) :where(table.doc-dense-table) :where(th, td) { padding: 1px 6px; }
:where(.uo-md) :where(th[data-uo-cell="num"], td[data-uo-cell="num"]) { text-align: right; }
:where(.uo-md) :where(td[data-uo-cell="key"], td[data-uo-cell="num"], td[data-uo-cell="status"]) { white-space: nowrap; }
:where(.uo-md) :where(td[data-uo-cell="status"]) > :where(.doc-annotations) { white-space: normal; }
:where(.uo-md) :where(th, td) :where(code, a) { overflow-wrap: anywhere; }
:where(.uo-md) :where(.uo-cell-label) { display: none; }
:where(.uo-md) :where(.uo-authored-case) { text-transform: none; }
:where(.uo-md) :where(.uo-foot) { display: flex; flex-direction: column; gap: var(--space-2); padding-top: var(--space-5); border-top: 1px solid var(--artifact-line); }
.uo-details > summary > .surface-disclosure-label { text-transform: none; }
@media (max-width: 960px) {
%(narrow)s
}
@container uo-body (max-width: 1119.98px) {
%(laptop)s
}
%(always)s
@media print {
  .uo-md .doc-pre, .uo-md .doc-pre-part { white-space: pre-wrap; }
}
""".replace("%(narrow)s", rows_view("table")).replace("%(laptop)s", rows_view(WIDE_BELOW_CAP)).replace(
    "%(always)s", rows_view(WIDE_ALWAYS, indent=""))


def md_css(annotated):
    """The renderer's stylesheet for one render: MD_CSS, then, in a document that annotates, the passage buffer
    (RAIL_BUFFER), last, so it follows the list rule it overrides. The rule is gated where the semantic-state modules
    are (inlined_modules): a document without annotations holds no range or item host."""
    return MD_CSS + RAIL_BUFFER + "\n" if annotated else MD_CSS


class BuildError(Exception):
    """A fail-closed rule rejected the source, its inputs or the output."""


# ---------------------------------------------------------------------------
# Closed vocabularies. README.md is the contract; tests assert these tables
# equal the README's.

PART_NUMBERS = tuple("%02d" % n for n in range(1, 11))
BASE_REQUIRED_PARTS = ("01", "02", "10")
KIND_PROFILES = {
    "guided-review": ("04", "08"),
    "confirmation": ("07",),
}
GENERATED_PARTS = ("01", "10")          # the renderer generates their chrome

META_KEYS = ("kind", "title", "id", "round", "classification", "audience")
TITLE_MAX = 200

CONTAINER_KINDS = ("part", "question", "finding", "disclose", "table", "banner",
                   "quote", "callout", "framing", "synthesis", "structure", "group", "annotate", "note", "range")
DISCLOSE_CLASSES = ("question-detail", "evidence", "detail", "provenance")
# The part each disclosure class sits in, the kinds a class is limited to, and the part no disclosure sits in
# (README, "What stays visible": tests assert that its two tables' part numbers and kind qualifiers equal these).
DISCLOSE_PARTS = {"question-detail": "03", "evidence": "06", "detail": "04", "provenance": "10"}
DISCLOSE_KINDS = {"detail": ("guided-review",)}
NO_DISCLOSE_PARTS = ("08",)
# A section framing names what it frames; its chip carries the word (design-system-ASK, SECTION FRAMING).
FRAMING_WORDS = {"thesis": "thesis", "question": "question space"}
SYNTHESIS_WORD = "compression"
PANELS = ("framing", "synthesis")
# Containers that may sit inside an authored disclosure: none of them is an ALWAYS VISIBLE anatomy element.
DISCLOSABLE = ("table", "quote", "callout", "structure", "annotate", "note", "range")
# Where each of these containers may sit: directly inside one of the listed kinds.
PARENT_KINDS = {
    "table": ("part", "question", "finding", "disclose", "range"),
    "quote": ("part", "question", "finding", "disclose", "callout", "range"),
    "callout": ("part", "question", "finding", "disclose", "range"),
    "structure": ("part", "question", "finding", "disclose", "callout", "range"),
    "group": ("structure",),
    "framing": ("part", "range"),
    "synthesis": ("part", "range"),
    "annotate": ("part", "question", "finding", "disclose", "note", "range"),
    "note": ("part", "question", "finding", "disclose"),
    "range": ("part", "question", "finding", "disclose"),
}
# What a :::range holds: its one :::annotate row first, then the blocks it covers (README, "Review annotations").
RANGE_HOLDS = ("annotate", "table", "quote", "callout", "structure", "framing", "synthesis")

# Review annotations: design-system-ASK Review Semantics (review-semantics.md), adopted for presentation only. The
# vocabularies are the owner's (tools/role-conformance.js C12 VOCAB) and the words are the owner key's labels. A source
# word maps to the role it paints and the label it shows; correction-requested shares the proposed role's paint and
# keeps its own words.
REVIEW_WORDS = {"proposed": ("proposed", "Proposed"), "correction-requested": ("proposed", "Correction requested"),
                "open": ("open", "Open question"), "accepted": ("accepted", "Accepted"),
                "declined": ("declined", "Declined"), "none": ("none", "No decision recorded")}
# A shown decision (accepted, declined) names what, who and scope (review-semantics.md, "The decision record"); a correction
# request (correction-requested) is pending, not a decision, and names what it asks to change and who asked. Either needs its
# record after ':'; the build can only require that something is written.
REVIEW_NEEDS_META = ("accepted", "declined", "correction-requested")
EVIDENCE_WORDS = {"supported": "Supported", "partially-supported": "Partially supported", "unresolved": "Unresolved",
                  "weakened": "Weakened", "not-yet-testable": "Not yet testable"}
STATE_WORDS = {"earned": "Earned", "structural": "Structural", "partial": "Partial", "deflated": "Deflated",
               "held": "Held", "external": "External", "proposed": "Proposed", "neutral": "Neutral"}
# The axes of an annotation, in the owner's fixed order (state, basis, evidence, review), then a neutral check. A row
# that opens a range or stands as a prompt leads with its review item, then the others in the same order (LEAD_ORDER).
ANNOTATION_AXES = ("state", "basis", "evidence", "review", "check")
LEAD_ORDER = ("review", "state", "basis", "evidence", "check")
AXIS_KEYS = {"item": "Item", "state": "State", "basis": "Basis", "evidence": "Evidence", "review": "Review",
             "check": "Check"}
# An annotation list's first line, `item: <name>`, names the item its lines judge (review-semantics.html, "One item,
# several questions"); it is required whenever the list carries a review line.
ITEM_LINE = re.compile(r"^item *:(?P<value>.*)$")
MARK_AXES = {"state": STATE_WORDS, "evidence": EVIDENCE_WORDS, "review": {k: v[1] for k, v in REVIEW_WORDS.items()}}
# The facet attribute a mark carries, and the values each may take in the final HTML.
FACET_VALUES = {"data-review": tuple(sorted(set(v[0] for v in REVIEW_WORDS.values()))),
                "data-evidence": tuple(EVIDENCE_WORDS), "data-state": tuple(STATE_WORDS)}
MARK_LABELS = {("data-review", role): set(label for r, label in REVIEW_WORDS.values() if r == role)
               for role in FACET_VALUES["data-review"]}
MARK_LABELS.update({("data-evidence", k): {v} for k, v in EVIDENCE_WORDS.items()})
MARK_LABELS.update({("data-state", k): {v} for k, v in STATE_WORDS.items()})
# A passage mark names the judgment its words take, pending or decided; No decision recorded marks no words
# (review-semantics.md, "Passage mark").
PASSAGE_ROLES = ("proposed", "open", "accepted", "declined")
# The emitted classes of the composition (review-semantics.md, "Annotation // the composition"): a review mark is a
# bordered label and an evidence or state mark is not; a passage mark carries the scope underline; a range, a div in
# the flow or a whole list item (the item host), carries the labeled range.
REVIEW_MARK = "doc-mark doc-label surface-bordered-label"
PLAIN_MARK = "doc-mark doc-label"
PASSAGE_CLASS = "doc-passage-mark surface-scope-underline"
RANGE_CLASS = "doc-annotation-range surface-labeled-range"
RANGE_DIV = "doc-group " + RANGE_CLASS
NYT_NOTE = "not-yet-testable"           # the evidence note's token; never a note name
NOTE_NAME = r"[a-z][a-z0-9-]{0,31}"   # a note's name; its element's id is uo-note-<name>
NOTE_ID = re.compile(r"^uo-note-" + NOTE_NAME + "$")
# Part 01's two review banners. The renderer writes each flag; the source
# supplies the body (and, for proof, an optional title).
BANNERS = {
    "review-status": ("uo-reviewer-status", "review status"),
    "proof": ("uo-proof", "proof of assembly"),
}
# The anatomy's part names, as the masthead's section index lists them.
PART_NAMES = {
    "01": "locator + masthead", "02": "reviewer brief", "03": "decision request",
    "04": "executive result", "05": "finding index", "06": "finding unit",
    "07": "prior-position delta", "08": "unresolved + later-check register",
    "09": "response / handoff format", "10": "seal + provenance",
}
TABLE_ROLES = ("key", "text", "num", "status")
# A column role may carry this one modifier (key:authored-case): the column's header, and its label in every
# body cell, keep the case the author wrote instead of the label role's uppercase (a unit such as mW).
AUTHORED_CASE = "authored-case"
LOCAL_NAME = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
CHROME_PARTS = ("01", "10")             # carry generated identity and seal chrome; no local= hook
# CSS functions that can load a resource from a string argument (url( is rejected separately).
RESOURCE_FUNCTION = re.compile(r"(?<![\w-])(-webkit-image-set|image-set|image|cross-fade|element|src|paint)\s*\(", re.I)

# Final-HTML allowlist.
BODY_ELEMENTS = frozenset(
    "div section header main footer h1 h2 h3 h4 p ul ol li blockquote pre code em strong a hr br "
    "table caption thead tbody tr th td details summary dl dt dd span nav svg path mark".split()
)
HEAD_ELEMENTS = frozenset(("meta", "title", "style"))
VOID_ELEMENTS = frozenset(("meta", "br", "hr"))
# The classes the renderer emits, as exact sets, by element; the allowlist compares an element's set of
# class tokens with these. A uo-* class is a UO chrome or geometry hook, styled by artifact.template.html
# or MD_CSS. Every other class is design-system-ASK's: a document-register role or composition, a
# treatment, or a panel axis, styled by the vendored _dsa-surface/ modules. Tests assert that each uo-*
# class exists in the template or MD_CSS, that each other class exists in a vendored module, and that
# README.md's "Emitted classes" table lists the same sets.
DISCLOSURE = "surface-disclosure surface-material-panel surface-attach-free surface-elevation-flush"
FLAT_PANEL = "surface-separate surface-material-panel surface-attach-free surface-elevation-flush doc-group"
EMPHASIS_PANEL = ("surface-separate surface-emphasis surface-emphasis--%s surface-material-page surface-attach-free "
                  "surface-elevation-flush doc-group")
CLASS_SETS = {
    "main": ("uo-md doc-flow",),
    "section": ("doc-section",),
    "div": ("uo-shell", "uo-status-rail", "doc-prose", "doc-section", "doc-hierarchy",
            "uo-details__body surface-disclosure-body doc-section",
            "uo-reviewer-status " + EMPHASIS_PANEL % "cyan", "uo-reviewer-status__body doc-prose",
            "uo-proof " + EMPHASIS_PANEL % "violet", "uo-proof__body doc-prose",
            "surface-emphasis-rail doc-group", FLAT_PANEL, "doc-pre doc-pre--structured", "doc-pre-group",
            "doc-annotations", "doc-hierarchy doc-group doc-annotation-note", "doc-group doc-annotation-note",
            RANGE_DIV),
    "header": ("uo-head doc-titled",),
    "dl": ("uo-head__meta", "doc-annotation-list"),
    "dt": ("doc-label",),
    "dd": ("doc-meta",),
    "details": ("uo-index " + DISCLOSURE, "uo-details " + DISCLOSURE),
    "summary": ("uo-index__mark",),
    "nav": ("uo-index__list surface-disclosure-body",),
    "svg": ("uo-mark",),
    "span": ("doc-label", "uo-status-rail__sep", "surface-disclosure-label", "surface-disclosure-indicator",
             "uo-cell-label doc-label", "uo-authored-case", "doc-annotations", "doc-annotation-item",
             PLAIN_MARK, REVIEW_MARK, "doc-meta"),
    "footer": ("uo-foot",),
    "p": ("doc-body", "doc-body surface-emphasis-rail", "doc-meta", "uo-reviewer-status__flag surface-emphasis-chip",
          "uo-proof__flag surface-emphasis-chip", "uo-proof__title doc-subsection-title",
          "surface-emphasis-chip surface-emphasis--magenta"),
    "h1": ("doc-title",),
    "h2": ("doc-section-title",),
    "h3": ("doc-subsection-title",),
    "h4": ("doc-deep-title",),
    "li": ("doc-body", RANGE_CLASS),
    "ol": ("doc-toc-list",),
    "blockquote": ("doc-quote",),
    "pre": ("doc-pre", "doc-pre-part"),
    "code": ("doc-code",),
    "a": ("surface-text-link", "doc-toc-link surface-text-link"),
    "table": ("doc-dense-table",),
    "caption": ("doc-meta",),
    "th": ("doc-label",),
    "td": ("doc-table-cell", "doc-body"),
    "mark": (PASSAGE_CLASS,),
}
# uo-* classes no stylesheet styles: structural hooks the allowlist places (the banners and their parts,
# the masthead and its index, authored disclosures and their bodies). A test holds this list exact.
STRUCTURAL_HOOKS = ("uo-head", "uo-index", "uo-index__list", "uo-details__body", "uo-reviewer-status",
                    "uo-reviewer-status__flag", "uo-reviewer-status__body", "uo-proof", "uo-proof__flag",
                    "uo-proof__title", "uo-proof__body")
# Elements that may carry no class, and only where each is named.
UNCLASSED = frozenset("p li ul ol summary footer table strong em br hr thead tbody tr dd".split())
# The container elements that may add their uo-local-<name> class, and the set each adds it to.
LOCAL_SETS = frozenset([("section", "doc-section"), ("div", "doc-section"), ("details", "uo-details " + DISCLOSURE),
                        ("table", "doc-dense-table"), ("table", ""), ("blockquote", "doc-quote"),
                        ("div", "surface-emphasis-rail doc-group"), ("div", FLAT_PANEL),
                        ("div", "doc-pre doc-pre--structured")])
# The assigned ASK wordmark, a vendored build input (README, "Inheritance").
WORDMARK = "assets/logo-ASK.svg"
# A section id names its part; a repeated 06 takes -2, -3, ... in order.
SECTION_ID = re.compile(r"^uo-part-(0[1-9]|10)(-[2-9]|-[1-9][0-9]+)?$")
DATA_VALUES = {
    "data-uo-part": PART_NUMBERS,
    "data-uo-role": ("question", "finding", "callout", "framing", "synthesis"),
    "data-uo-disclose": DISCLOSE_CLASSES,
    "data-uo-cell": TABLE_ROLES,
    "data-lead-lines": ("1", "2", "3"),
}
# A structured block records at most this many blank source lines before a line (design-system-ASK LIMITS).
MAX_LEAD_LINES = 3


def _esc(text):
    return html.escape(text, quote=True)


def check_markdown_pin():
    if markdown.__version__ != MARKDOWN_PIN:
        raise BuildError("markdown %s is installed; this renderer is pinned to markdown==%s (requirements.txt)"
                         % (markdown.__version__, MARKDOWN_PIN))


# ---------------------------------------------------------------------------
# Raw HTML guard for python-markdown

class _GuardedHtmlBlock(Preprocessor):
    """Wraps the html_block preprocessor: if it stashed anything, the segment
    contained raw HTML. fenced_code (priority 25) has already stashed code blocks
    before this runs, so they are not counted."""

    def __init__(self, md, inner):
        super().__init__(md)
        self.inner = inner

    def run(self, lines):
        before = self.md.htmlStash.html_counter
        out = self.inner.run(lines)
        if self.md.htmlStash.html_counter != before:
            raise BuildError("raw HTML block in source (put literal tags in a code span, or write &lt;)")
        return out


class _FailInlineHtml(InlineProcessor):
    def handleMatch(self, m, data):
        raise BuildError("raw inline HTML in source: %r (put literal tags in a code span, or write &lt;)"
                         % m.group(0)[:60])


class NoRawHtml(Extension):
    def extendMarkdown(self, md):
        inner = md.preprocessors["html_block"]
        md.preprocessors.register(_GuardedHtmlBlock(md, inner), "html_block", 20)
        pattern = md.inlinePatterns["html"].pattern
        md.inlinePatterns.register(_FailInlineHtml(pattern, md), "html", 90)


class _ConstructError(BuildError):
    """A `{{...}}` construct failed. needle locates its source line (_line_of): its line's text around the construct,
    as far as it survives python-markdown's earlier patterns, then the construct's exact text; occurrence counts the
    identical needles this segment met before it."""

    def __init__(self, msg, needle, occurrence=0):
        super().__init__(msg)
        self.needle = needle
        self.occurrence = occurrence


# Where an inline annotation may sit, set on the Markdown instance before each segment renders (_inline_context):
#   BODY                the Markdown directly inside a part 02 to 09, a question, a finding or an authored disclosure other
#                       than provenance: a passage mark may sit there, and an item host opens a top-level list item;
#   RANGE_BODY          the Markdown a :::range covers: a passage mark may sit there; an item host may not;
#   TABLE               a :::table in any of those: its body cells take annotation items;
#   ("chrome-table", L) a :::table in part 01 or 10 or in a provenance disclosure: no annotation;
#   ("none", L)         any other container: no annotation;
#   PROBE               the visibility probe: a construct closed on its line is consumed as plain text, checked nowhere.
BODY, RANGE_BODY, TABLE, PROBE = ("body", None), ("range", None), ("table", None), ("probe", None)
PLACEHOLDER = re.compile("[\x02\x03]")       # python-markdown's stash placeholders: a code span, an escape, a link
STASH_RUN = re.compile("\x02[^\x02\x03]*\x03")
INLINE_PH = re.compile("\x02klzzwxh:([0-9]+)\x03")      # an inline node python-markdown stashed: a code span, a link
HTML_PH = re.compile("\x02wzxhzdk:([0-9]+)\x03")        # raw HTML this renderer stashed: an annotation item
HEADING_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6")
AUTOLINK_OPEN = re.compile(r"<(?:[Hh][Tt][Tt][Pp][Ss]?|[Ff][Tt][Pp])://[^<>\s]*$")
# A per-cell block range is a UO capability limit: UO's tables hold inline cell text (README, "Review annotations").
CELL_RANGE_LIMIT = ("a per-cell block range is a UO capability limit: UO's table cells hold inline text, so no :::range "
                    "opens inside or around one cell; raise it with the owner. A judgment on a whole table is a :::range "
                    "around the :::table, and a cell's own judgment is a {{review ...}} item in that cell")


def mark_html(axis, word):
    """A mark: one review, evidence or state role, in its words (review-semantics.md, "Mark"). A review mark is the
    shared bordered label; an evidence or state mark draws its marker and is not."""
    role, label = REVIEW_WORDS[word] if axis == "review" else (word, MARK_AXES[axis][word])
    return '<span class="%s" data-%s="%s">%s</span>' % (REVIEW_MARK if axis == "review" else PLAIN_MARK, axis, role, label)


def meta_html(value):
    return '<span class="doc-meta">%s</span>' % _esc(value)


def item_html(axis, word, value):
    """An item: a mark and the metadata that qualifies it, or a basis or check key and its value."""
    if axis in ("basis", "check"):
        inner = '<span class="doc-label">%s</span>%s' % (AXIS_KEYS[axis], meta_html(value))
    else:
        inner = mark_html(axis, word) + (meta_html(value) if value is not None else "")
    return '<span class="doc-annotation-item">%s</span>' % inner


def _rank_order(axes, order, line):
    """Items read in order; repeats of one axis sit together."""
    ranks = [order.index(a) for a in axes]
    for a, b in zip(ranks, ranks[1:]):
        if b < a:
            raise BuildError("line %d: annotation items read in the order %s; %s comes after %s"
                             % (line, ", ".join(order), order[a], order[b]))


class _AnnotationInline(InlineProcessor):
    """`{{...}}`: a passage mark in body text, an annotation item in a :::table body cell, or the items that open a
    whole list item as its own range, an item host (README, "Review annotations"). Any other `{{` fails, so an
    author never gets silent literal braces; a literal `{{` belongs in a code span. Registered below the code-span,
    escape and link patterns: code stays literal, an escaped brace is not a construct, and a construct inside a link
    text is seen inside the link. Construct text is plain text, consumed here before the raw-HTML guard and escaped,
    in the probe as in a render, so a source builds the same whichever checks reach it; a passage mark's words may
    also hold a link, which keeps its own treatment."""

    def _stashed(self, placeholder):
        m = INLINE_PH.fullmatch(placeholder)
        return self.md.treeprocessors["inline"].stashed_nodes.get(m.group(1)) if m else None

    def handleMatch(self, m, data):
        context = getattr(self.md, "uo_context", PROBE)
        start = m.start(0)
        line = data[start:].split("\n", 1)[0]
        close = line.find("}}", 2)
        if context == PROBE:
            if close < 0:
                return None, None, None
            el = etree.Element("span")
            el.text = AtomicString(line[:close + 2])
            return el, start, start + close + 2
        prefix = PLACEHOLDER.split(data[data.rfind("\n", 0, start) + 1:start])[-1]
        full = prefix + PLACEHOLDER.split(line)[0]
        seen = self.md.uo_seen
        occurrence = seen.get(full, 0)
        seen[full] = occurrence + 1
        needle = (full, PLACEHOLDER.split(line[:close + 2] if close >= 0 else line[:80])[0])

        def fail(msg):
            raise _ConstructError(msg, needle, occurrence)
        if close < 0:
            fail("`{{` opens no annotation: a construct closes with `}}` on its line; a literal `{{` belongs in a code span")
        inner = line[2:close]
        if "{{" in inner:
            fail("`{{` inside an annotation; a literal `{{` belongs in a code span")
        head = re.match(r"[^\s:\x02]*", inner).group(0)
        stashed = [self._stashed(s.group(0)) for s in STASH_RUN.finditer(inner)]
        if PLACEHOLDER.sub("", "".join(STASH_RUN.split(inner))) != "".join(STASH_RUN.split(inner)):
            stashed.append(None)          # a stray stash character: never a link
        if stashed and head != "mark":
            fail("an annotation is plain text: no code span, escape or link inside `{{...}}`; only a passage mark's words "
                 "may hold a link")
        for node in stashed:
            if not (isinstance(node, etree.Element) and node.tag == "a"):
                fail("a passage mark's words are plain text and may hold a link written [text](url): no code span, escape "
                     "or other construct inside `{{mark ...}}`")
            if len(node) or STASH_RUN.search(node.text or "") or PLACEHOLDER.search(node.text or ""):
                fail("a link inside marked words holds plain text: no code span, escape or emphasis in its text")
        if AUTOLINK_OPEN.search(data[:start].rsplit("\n", 1)[-1]):
            fail("an annotation never sits inside an autolink")
        ancestors = self.md.treeprocessors["inline"].ancestors
        if head == "range":
            fail(CELL_RANGE_LIMIT if context == TABLE else
                 "`{{range` is not an annotation: a judgment on whole blocks opens a :::range container around them")
        try:
            if head == "mark":
                fields = _passage_fields(inner, lambda w: STASH_RUN.sub(lambda s: self._stashed(s.group(0)).text or "", w))
            elif head in ANNOTATION_AXES:
                fields = _item_fields(inner)
            else:
                raise ValueError("`{{%s` is not an annotation: a passage mark is {{mark ...}}, and a table cell's or an "
                                 "item host's item {{state|basis|evidence|review|check ...}}; a literal `{{` belongs in "
                                 "a code span" % head[:30])
        except ValueError as e:
            fail(str(e))
        if context[0] == "chrome-table":
            fail("no annotation sits in part 01 or 10 or in a provenance disclosure; this :::table is in %s" % context[1])
        if head == "mark":
            if context not in (BODY, RANGE_BODY):
                fail("a passage mark sits in body text directly inside a part 02 to 09, a :::question, a :::finding, a "
                     ":::range or an authored disclosure other than provenance, not in %s"
                     % ("a :::table" if context == TABLE else context[1]))
            barrier = [a for a in ancestors if a in HEADING_TAGS + ("blockquote", "a")]
            if barrier:
                fail("a passage mark sits in a paragraph or list item, not inside <%s>" % barrier[0])
            role, name, words = fields
            # The words are plain text, escaped; a link inside them keeps its own element, which takes the
            # renderer's link role (assign_roles), so its line and states stay its own.
            parts, pos = [], 0
            for s in STASH_RUN.finditer(words):
                link = self._stashed(s.group(0))
                parts.append(_esc(words[pos:s.start()]))
                parts.append("<a%s>%s</a>" % ("".join(' %s="%s"' % (k, _esc(v)) for k, v in sorted(link.items())),
                                              _esc(link.text or "")))
                pos = s.end()
            parts.append(_esc(words[pos:]))
            html_ = '<mark class="%s" data-review="%s" aria-describedby="uo-note-%s">%s</mark>' % (
                PASSAGE_CLASS, role, name, "".join(parts))
            return self.md.htmlStash.store(html_), start, start + close + 2
        if context == TABLE:
            if "th" in ancestors:
                fail("an annotation item sits in a body cell, never in a header")
            if not ancestors or ancestors[-1] != "td":
                fail("an annotation item sits directly in its cell, not inside <%s>" % ancestors[-1])
            return self.md.htmlStash.store(item_html(*fields)), start, start + close + 2
        return self._host_item(fields, data, start, start + close + 2, ancestors, context, fail), start, start + close + 2

    def _host_item(self, fields, data, start, end, ancestors, context, fail):
        """An item host's item: the items that open a whole list item make that item its own range, its row first
        (review-semantics.md, "Annotation range"). They open a top-level list item directly in body text, review item
        first, before any of the item's words; the renderer moves them into the item's row (_item_hosts)."""
        axis = fields[0]
        if context == RANGE_BODY:
            fail("an item host never sits inside a :::range: one judgment governs a range, and a list item it holds "
                 "carries no review row of its own")
        if context != BODY:
            fail("an annotation item {{%s ...}} sits in a :::table body cell, or opens a list item in body text as an "
                 "item host; not in %s" % (axis, context[1]))
        if "li" not in ancestors:
            fail("an annotation item {{%s ...}} sits in a :::table body cell, or opens a list item as an item host; "
                 "elsewhere an :::annotate row carries it" % axis)
        barrier = [a for a in ancestors if a in HEADING_TAGS + ("blockquote", "a")]
        if barrier:
            fail("an item host's items open its list item, not inside <%s>" % barrier[0])
        if ancestors.count("li") > 1:
            fail("an item host is an item of a top-level list, never of a nested list")
        if ancestors[-1] != "li" and ancestors[-2:] != ["li", "p"]:
            fail("an item host's items open its list item directly, not inside <%s>" % ancestors[-1])
        prior = []

        def take(s):
            node = self._stashed(s.group(0))
            held = HTML_PH.fullmatch(node) if isinstance(node, str) else None
            if held and int(held.group(1)) in self.md.uo_hosts:
                prior.append(self.md.uo_hosts[int(held.group(1))])
                return ""
            return "\x00"
        before = STASH_RUN.sub(take, data[:start])
        if "\x00" in before or has_visible_text(before):
            fail("an item host's row opens its list item: its items come first, before any of the item's words")
        if not prior and axis != "review":
            fail("an item host's row leads with its review item, {{review <word>: <record>}}, then any state, basis, "
                 "evidence and check items")
        if not prior and fields[2] is None:
            # An item host is its own range, so its review item names its judgment as a range's row does (README,
            # "Review annotations"); accepted, declined and correction-requested already need theirs (_item_fields).
            fail("the review item that opens an item host carries its record after ':': what the item holds, the scope "
                 "of the judgment and who decides or asks, as in {{review %s: <record>}}" % fields[1])
        if prior and axis == "review":
            fail("an item host carries one review judgment; a second judgment on one whole list item is raised with the "
                 "owner")
        after = STASH_RUN.sub("x", re.sub(r"\{\{[^\n]*?\}\}", "", data[end:]))
        if not has_visible_text(after):
            fail("an item host's words follow its row: the list item holds words after its items")
        try:
            _rank_order(prior[1:] + [axis] if prior else [], LEAD_ORDER, 0)
        except BuildError:
            fail("an item host's items read in the order %s; %s comes after %s"
                 % (", ".join(LEAD_ORDER), prior[-1], axis))
        placeholder = self.md.htmlStash.store(item_html(*fields))
        self.md.uo_hosts[int(HTML_PH.fullmatch(placeholder).group(1))] = axis
        return placeholder


class Annotations(Extension):
    def extendMarkdown(self, md):
        md.inlinePatterns.register(_AnnotationInline(r"\{\{", md), "uo_annotation", 155)


def new_markdown():
    return markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", NoRawHtml(), Annotations()])


_PROBE = []


def _probe_markdown():
    if not _PROBE:
        _PROBE.append(new_markdown())
    return _PROBE[0]


# ---------------------------------------------------------------------------
# Source model: one meta block plus a container tree

# The opening-fence shape python-markdown's fenced_code accepted at 3.4.1. The pinned
# version opens a fence on every line this matches, and also on an {attrs} block that
# holds a quoted "}", which this refuses as a malformed opening line: a ":::" line is
# code text exactly where python-markdown renders code, or the build fails.
FENCE_OPEN = re.compile(r"""^(?P<fence>~{3,}|`{3,})[ ]*((\{[^\}\n]*\})|(\.?[\w#.+-]*[ ]*)?(hl_lines=("|').*?\6[ ]*)?)$""")
FENCE_START = re.compile(r"^(~{3,}|`{3,})")
TOKEN_RE = re.compile(r'\s*(?:"([^"]*)"|([^\s"]+))')


class Node:
    def __init__(self, kind, line, parent=None):
        self.kind = kind
        self.line = line
        self.parent = parent
        self.children = []
        self.number = None        # part
        self.central = False      # question
        self.disclose = None      # disclose class
        self.summary = None       # disclose
        self.roles = None         # table
        self.cased = None         # table: per column, whether its header keeps the author's case
        self.caption = None       # table
        self.dense = False        # table: declared dense
        self.banner = None        # banner: its kind
        self.title = None         # banner proof: optional title
        self.attribution = None   # quote: optional attribution
        self.word = None          # framing: what it frames
        self.local = None
        self.listed = False       # annotate: an annotation list, not a row
        self.items = None         # annotate: its parsed items, (axis, word, value, line)
        self.name = None          # note: its name; None for the not-yet-testable evidence note
        self.document = False     # annotate: the document's own record, at top level

    def ancestors(self):
        n = self.parent
        while n is not None:
            yield n
            n = n.parent

    def has_child_before(self):
        """True when something visible precedes the next child: a container, or
        Markdown that renders to non-whitespace text."""
        for c in self.children:
            if isinstance(c, Node) or c.renders_text():
                return True
        return False

    def has_content(self):
        for c in self.children:
            if isinstance(c, Node):
                if c.kind == "annotate":          # item lines are not Markdown; parsed when the row closes
                    if c.items:
                        return True
                elif c.kind == "table" or c.has_content():
                    return True
            elif c.renders_text():
                return True
        return False

    def last_visible(self):
        """The child the next child follows: the last container, or the last Markdown segment that renders
        visible text. None when nothing visible precedes."""
        for c in reversed(self.children):
            if isinstance(c, Node) or c.renders_text():
                return c
        return None


# Default_Ignorable_Code_Point, hard-coded from Unicode 14.0.0
# DerivedCoreProperties.txt, the Unicode version python3.11's unicodedata reports.
DEFAULT_IGNORABLE = (
    (0x00AD, 0x00AD), (0x034F, 0x034F), (0x061C, 0x061C), (0x115F, 0x1160), (0x17B4, 0x17B5),
    (0x180B, 0x180D), (0x180E, 0x180E), (0x180F, 0x180F), (0x200B, 0x200F), (0x202A, 0x202E),
    (0x2060, 0x2064), (0x2065, 0x2065), (0x2066, 0x206F), (0x3164, 0x3164), (0xFE00, 0xFE0F),
    (0xFEFF, 0xFEFF), (0xFFA0, 0xFFA0), (0xFFF0, 0xFFF8), (0x1BCA0, 0x1BCA3), (0x1D173, 0x1D17A),
    (0xE0000, 0xE0000), (0xE0001, 0xE0001), (0xE0002, 0xE001F), (0xE0020, 0xE007F), (0xE0080, 0xE00FF),
    (0xE0100, 0xE01EF), (0xE01F0, 0xE0FFF),
)
NOT_VISIBLE_CATEGORIES = frozenset(("Cc", "Cf", "Zs", "Zl", "Zp", "Mn", "Me"))
BRAILLE_PATTERN_BLANK = "\u2800"


def has_visible_text(text):
    """True when text holds at least one character that is not whitespace, not in
    categories Cc, Cf, Zs, Zl, Zp, not Default_Ignorable_Code_Point and not U+2800.
    Combining marks (Mn, Me) do not count on their own. Other glyph-blank
    characters are a package-review check."""
    for ch in text:
        if ch.isspace() or ch == BRAILLE_PATTERN_BLANK:
            continue
        if unicodedata.category(ch) in NOT_VISIBLE_CATEGORIES:
            continue
        cp = ord(ch)
        if any(lo <= cp <= hi for lo, hi in DEFAULT_IGNORABLE):
            continue
        return True
    return False


class Text:
    def __init__(self):
        self.lines = []           # (lineno, text)

    def nonblank(self):
        return any(t.strip() for _, t in self.lines)

    def renders_text(self):
        """True when the segment's rendered HTML carries visible text
        (has_visible_text) or an <img> (which the allowlist then rejects with its
        own message). Source lines that render to no visible text (a link
        reference definition, a bare rule, a zero-width space) are not content."""
        if not self.nonblank():
            return False
        rendered = _render_markdown(_probe_markdown(), self, PROBE)
        if re.search(r"<img\b", rendered):
            return True
        text = html.unescape(re.sub(r"<[^>]*>", "", rendered))
        return has_visible_text(text)

    def first_nonblank_line(self):
        for n, t in self.lines:
            if t.strip():
                return n
        return self.lines[0][0] if self.lines else 0


def _label(node):
    if node is None:
        return "top level"
    if node.kind == "part":
        return ":::part %s (line %d)" % (node.number, node.line)
    if node.kind == "question" and node.central:
        return ":::question central (line %d)" % node.line
    if node.kind == "disclose":
        return ":::disclose %s (line %d)" % (node.disclose, node.line)
    if node.kind == "banner":
        return ":::banner %s (line %d)" % (node.banner, node.line)
    if node.kind == "annotate" and (node.listed or node.document):
        return ":::annotate %s (line %d)" % ("list" if node.listed else "document", node.line)
    if node.kind == "note":
        return ":::note %s (line %d)" % (node.name or NYT_NOTE, node.line)
    return ":::%s (line %d)" % (node.kind, node.line)


def _tokenize(rest, lineno):
    tokens = []
    pos = 0
    rest = rest.rstrip()
    while pos < len(rest):
        m = TOKEN_RE.match(rest, pos)
        if not m or m.end() == pos:
            raise BuildError("line %d: malformed container token (an unterminated quote?)" % lineno)
        if m.group(1) is not None:
            tokens.append(("quoted", m.group(1)))
        else:
            word = m.group(2)
            if '"' in word:
                raise BuildError("line %d: malformed container token %r" % (lineno, word))
            tokens.append(("word", word))
        pos = m.end()
        if pos < len(rest) and not rest[pos].isspace() and m.group(1) is not None:
            raise BuildError("line %d: a quoted token must be followed by a space" % lineno)
    return tokens


def _parse_meta(lines, start):
    """lines[start] is ':::meta'. Returns (meta dict, index after the close)."""
    meta = {}
    i = start + 1
    while i < len(lines):
        n, t = i + 1, lines[i]
        if t.rstrip() == ":::":
            break
        m = re.match(r"^([a-z]+): (.*)$", t)
        if not m:
            raise BuildError("meta line %d is not 'key: value' on one line (multi-line values are not allowed)" % n)
        key, value = m.group(1), m.group(2).strip()
        if key not in META_KEYS:
            raise BuildError("meta line %d: unknown meta key %r (allowed: %s)" % (n, key, ", ".join(META_KEYS)))
        if key in meta:
            raise BuildError("meta line %d: meta key %r repeated" % (n, key))
        if not value:
            raise BuildError("meta line %d: meta key %r has an empty value" % (n, key))
        if not has_visible_text(value):
            raise BuildError("meta line %d: meta key %r has no visible text" % (n, key))
        if "{{" in value:
            raise BuildError("meta line %d: meta key %r holds `{{`; an annotation sits in body text or a table cell only"
                             % (n, key))
        meta[key] = value
        i += 1
    else:
        raise BuildError("line %d: unclosed :::meta block" % (start + 1))
    if "kind" not in meta:
        raise BuildError("K1: the document declares no kind (meta key 'kind' is required)")
    if meta["kind"] not in KIND_PROFILES:
        raise BuildError("K1: kind %r has no profile (closed set: %s)" % (meta["kind"], ", ".join(KIND_PROFILES)))
    for key in META_KEYS:
        if key not in meta:
            raise BuildError("meta key %r is required" % key)
    if len(meta["title"]) > TITLE_MAX:
        raise BuildError("meta title is longer than %d characters" % TITLE_MAX)
    return meta, i + 1


def _open_container(kind, tokens, lineno, parent, root, doc_kind):
    if kind == "meta":
        raise BuildError("line %d: :::meta is not allowed here; it must be the first non-blank line" % lineno)
    if kind not in CONTAINER_KINDS:
        raise BuildError("line %d: unknown container kind %r (closed set: %s)" % (lineno, kind, ", ".join(CONTAINER_KINDS)))
    node = Node(kind, lineno, parent)
    seen = set()
    positional = []
    if any("{{" in val for _, val in tokens):
        raise BuildError("line %d: a container token holds `{{`; an annotation sits in body text or a table cell only"
                         % lineno)
    for typ, val in tokens:
        if typ == "word" and "=" in val:
            name, _, value = val.partition("=")
            if name != "local":
                raise BuildError("line %d: unknown token %r on :::%s" % (lineno, val, kind))
            if "local" in seen:
                raise BuildError("line %d: repeated token: a container carries at most one local= hook" % lineno)
            seen.add("local")
            if not LOCAL_NAME.match(value):
                raise BuildError("line %d: invalid local name %r (must match [a-z][a-z0-9-]{0,31})" % (lineno, value))
            node.local = value
        else:
            positional.append((typ, val))

    if kind == "part":
        if len(positional) != 1 or positional[0][0] != "word":
            raise BuildError("line %d: :::part takes exactly one part number 01..10" % lineno)
        if positional[0][1] not in PART_NUMBERS:
            raise BuildError("line %d: unknown token %r on :::part (part numbers 01..10 only)" % (lineno, positional[0][1]))
        node.number = positional[0][1]
        if node.local and node.number in CHROME_PARTS:
            raise BuildError("line %d: :::part %s carries generated masthead or seal chrome and takes no local= hook"
                             % (lineno, node.number))
    elif kind == "question":
        for typ, val in positional:
            if typ != "word" or val != "central":
                raise BuildError("line %d: unknown token %r on :::question" % (lineno, val))
            if node.central:
                raise BuildError("line %d: repeated token 'central' on :::question" % lineno)
            node.central = True
    elif kind == "finding":
        if positional:
            raise BuildError("line %d: unknown token %r on :::finding" % (lineno, positional[0][1]))
    elif kind == "disclose":
        words = [v for t, v in positional if t == "word"]
        quoted = [v for t, v in positional if t == "quoted"]
        if len(words) != 1 or words[0] not in DISCLOSE_CLASSES:
            raise BuildError("line %d: :::disclose takes one class from %s" % (lineno, ", ".join(DISCLOSE_CLASSES)))
        if len(quoted) != 1 or not has_visible_text(quoted[0]):
            raise BuildError("line %d: :::disclose takes one non-empty quoted summary" % lineno)
        if positional[0][0] != "word":
            raise BuildError("line %d: :::disclose class comes before its summary" % lineno)
        node.disclose, node.summary = words[0], quoted[0]
    elif kind == "table":
        roles, cased = [], []
        if positional and positional[0] == ("word", "dense"):
            node.dense = True
            positional = positional[1:]
        for i, (typ, val) in enumerate(positional):
            if typ == "quoted":
                if i != len(positional) - 1:
                    raise BuildError("line %d: :::table takes at most one quoted caption, after its column roles" % lineno)
                if not has_visible_text(val):
                    raise BuildError("line %d: a :::table caption must contain visible text" % lineno)
                node.caption = val
                continue
            if val == "dense":
                raise BuildError("line %d: 'dense' comes first on :::table, once" % lineno)
            base, sep, modifier = val.partition(":")
            if base == "dense":
                raise BuildError("line %d: 'dense' takes no modifier; it comes first on :::table, once" % lineno)
            if base not in TABLE_ROLES:
                raise BuildError("line %d: table role %r outside the closed set %s" % (lineno, base, ", ".join(TABLE_ROLES)))
            if sep and modifier != AUTHORED_CASE:
                raise BuildError("line %d: table role modifier %r: the one modifier is '%s'" % (lineno, modifier, AUTHORED_CASE))
            roles.append(base)
            cased.append(bool(sep))
        if not roles:
            raise BuildError("line %d: :::table takes one role per column" % lineno)
        node.roles, node.cased = roles, cased
    elif kind == "quote":
        if any(t == "word" for t, _ in positional) or len(positional) > 1:
            raise BuildError("line %d: :::quote takes at most one quoted attribution" % lineno)
        if positional:
            if not has_visible_text(positional[0][1]):
                raise BuildError("line %d: a :::quote attribution must contain visible text" % lineno)
            node.attribution = positional[0][1]
    elif kind == "framing":
        if len(positional) != 1 or positional[0][0] != "word" or positional[0][1] not in FRAMING_WORDS:
            raise BuildError("line %d: :::framing takes one of %s" % (lineno, ", ".join(FRAMING_WORDS)))
        node.word = positional[0][1]
    elif kind in ("callout", "synthesis", "structure", "group"):
        if positional:
            raise BuildError("line %d: unknown token %r on :::%s" % (lineno, positional[0][1], kind))
        if kind == "group" and node.local:
            raise BuildError("line %d: :::group takes no local= hook; its structure may carry one" % lineno)
    elif kind == "banner":
        if node.local:
            raise BuildError("line %d: :::banner sits in part 01, which carries generated chrome, and takes no local= hook"
                             % lineno)
        words = [v for t, v in positional if t == "word"]
        quoted = [v for t, v in positional if t == "quoted"]
        if len(words) != 1 or words[0] not in BANNERS or positional[0][0] != "word":
            raise BuildError("line %d: :::banner takes one kind from %s, first" % (lineno, ", ".join(BANNERS)))
        if quoted and words[0] != "proof":
            raise BuildError("line %d: only :::banner proof takes a quoted title" % lineno)
        if len(quoted) > 1 or (quoted and not has_visible_text(quoted[0])):
            raise BuildError("line %d: :::banner proof takes at most one non-empty quoted title" % lineno)
        node.banner = words[0]
        node.title = quoted[0] if quoted else None
    elif kind == "annotate":
        if node.local:
            raise BuildError("line %d: :::annotate takes no local= hook" % lineno)
        if positional not in ([], [("word", "list")], [("word", "document")]):
            raise BuildError("line %d: :::annotate takes no token but an optional 'list' or 'document'" % lineno)
        node.listed = positional == [("word", "list")]
        node.document = positional == [("word", "document")]
    elif kind == "range":
        if node.local:
            raise BuildError("line %d: :::range takes no local= hook" % lineno)
        if positional:
            raise BuildError("line %d: unknown token %r on :::range" % (lineno, positional[0][1]))
    elif kind == "note":
        if node.local:
            raise BuildError("line %d: :::note takes no local= hook" % lineno)
        if len(positional) != 1 or positional[0][0] != "word":
            raise BuildError("line %d: :::note takes one note name, or %s" % (lineno, NYT_NOTE))
        word = positional[0][1]
        if word != NYT_NOTE:
            if not re.fullmatch(NOTE_NAME, word):
                raise BuildError("line %d: invalid note name %r (must match %s)" % (lineno, word, NOTE_NAME))
            node.name = word

    _check_position(node, parent, root, doc_kind)
    return node


def _panel_kinds(part):
    """The framing and synthesis panels a part holds, directly or inside a :::range that sits directly in it."""
    kinds = []
    for c in part.children:
        if isinstance(c, Node):
            if c.kind in PANELS:
                kinds.append(c.kind)
            elif c.kind == "range":
                kinds += [k.kind for k in c.children if isinstance(k, Node) and k.kind in PANELS]
    return kinds


def _holds_panel(node):
    return node.kind == "range" and any(isinstance(k, Node) and k.kind in PANELS for k in node.children)


# The containers that are visible blocks of a reading, and Markdown blocks that are not: a heading opens a section
# and a thematic break separates; neither is the reading a detail disclosure details.
READING_NODES = ("table", "quote", "callout", "structure", "range", "framing", "synthesis")
NOT_READING = re.compile(r"<(h[1-6]|hr)\b")


def _reading_before(parent):
    """True when the section a next child of parent would sit in, from the last heading before it (or parent's start),
    holds a visible block: a Markdown block other than a heading or a rule that shows visible text, or one of
    READING_NODES. Annotation rows, lists and notes, and another disclosure, are not the reading."""
    seen = False
    for c in parent.children:
        if isinstance(c, Text):
            if not c.nonblank():
                continue
            for b in top_blocks(_render_markdown(_probe_markdown(), c, PROBE), c.first_nonblank_line()):
                m = NOT_READING.match(b)
                if m and m.group(1).startswith("h"):
                    seen = False
                elif not m and has_visible_text(html.unescape(re.sub(r"<[^>]*>", "", b))):
                    seen = True
        elif c.kind in READING_NODES:
            seen = True
    return seen


def _check_position(node, parent, root, doc_kind):
    """Where a container may open; doc_kind is the document's declared kind, which decides where a guided review's
    detail disclosure may sit."""
    at = _label(None if parent is root else parent)
    if node.kind == "annotate" and node.document:
        # The whole document's record, set under its title (review-semantics.md, "Annotation row").
        if parent is not root:
            raise BuildError("line %d: :::annotate document is the document's own record: it sits at top level, between "
                             ":::meta and the first :::part, not inside %s" % (node.line, at))
        if any(isinstance(c, Node) and c.kind == "part" for c in root.children):
            raise BuildError("line %d: :::annotate document comes before the first :::part" % node.line)
        if any(isinstance(c, Node) and c.kind == "annotate" for c in root.children):
            raise BuildError("line %d: a document carries one :::annotate document record" % node.line)
        return
    if parent is not root and parent.kind == "banner":
        raise BuildError("line %d: :::%s sits inside %s; a banner holds Markdown only" % (node.line, node.kind, _label(parent)))
    if node.kind not in DISCLOSABLE and parent is not root and parent.kind == "disclose":
        raise BuildError("K7: :::%s at line %d sits inside %s; ALWAYS VISIBLE content cannot be disclosed"
                         % (node.kind, node.line, _label(parent)))
    if node.kind == "range" and parent is not root and parent.kind == "table":
        raise BuildError("line %d: :::range inside %s: %s" % (node.line, at, CELL_RANGE_LIMIT))
    if parent is not root and parent.kind == "range" and node.kind not in RANGE_HOLDS:
        if node.kind == "range":
            raise BuildError("line %d: :::range sits inside %s; ranges never nest: blocks judged otherwise are a sibling "
                             ":::range" % (node.line, at))
        if node.kind == "note":
            raise BuildError("line %d: %s sits inside %s; a note on words a range holds follows the range, since a range "
                             "carries one judgment" % (node.line, _label(node), at))
        raise BuildError("line %d: :::%s sits inside %s; a range holds its :::annotate row, then the blocks it covers: "
                         "paragraphs, plain lists, quotations, callouts, structures, a :::table, or a part's :::framing or "
                         ":::synthesis" % (node.line, node.kind, at))
    if node.kind in PARENT_KINDS:
        if parent is root or parent.kind not in PARENT_KINDS[node.kind]:
            raise BuildError("line %d: :::%s is allowed inside %s only, not %s"
                             % (node.line, node.kind, ", ".join(":::" + k for k in PARENT_KINDS[node.kind]), at))
    if node.kind in ("annotate", "note", "range"):
        _check_annotation_position(node, parent)
    if node.kind in PANELS:
        part = parent
        if parent.kind == "range":
            part = parent.parent
            if part is root or part.kind != "part":
                raise BuildError("line %d: a :::%s sits in a :::range only where that range sits directly in a part, not "
                                 "in %s" % (node.line, node.kind, _label(None if part is root else part)))
        if part.number in CHROME_PARTS:
            raise BuildError("line %d: :::%s is not allowed in part %s, which carries generated chrome"
                             % (node.line, node.kind, part.number))
        kinds = _panel_kinds(part)
        if node.kind in kinds:
            raise BuildError("line %d: part %s carries at most one :::%s" % (node.line, part.number, node.kind))
        if node.kind == "framing" and "synthesis" in kinds:
            raise BuildError("line %d: a :::framing opens a part and comes before its :::synthesis" % node.line)
    if node.kind == "part":
        if parent is not root:
            raise BuildError("line %d: :::part is allowed at top level only, not inside %s" % (node.line, at))
    elif node.kind == "question":
        if parent is root or parent.kind != "part" or parent.number != "03":
            raise BuildError("line %d: :::question is allowed directly inside :::part 03 only, not %s" % (node.line, at))
    elif node.kind == "finding":
        if parent is root or parent.kind != "part" or parent.number != "06":
            raise BuildError("line %d: :::finding is allowed directly inside :::part 06 only, not %s" % (node.line, at))
    elif node.kind == "banner":
        if parent is root or parent.kind != "part" or parent.number != "01":
            raise BuildError("line %d: :::banner is allowed directly inside :::part 01 only, not %s" % (node.line, at))
        if any(isinstance(c, Node) and c.kind == "banner" and c.banner == node.banner for c in parent.children):
            raise BuildError("line %d: part 01 carries at most one :::banner %s" % (node.line, node.banner))
    elif node.kind == "disclose":
        chain = [] if parent is root else [parent] + list(parent.ancestors())
        home = next((a for a in chain if a is not root and a.kind == "part"), None)
        if home is not None and home.number in NO_DISCLOSE_PARTS:
            raise BuildError("K7: :::disclose at line %d is inside part %s; the register stays whole and visible"
                             % (node.line, home.number))
        if node.disclose in DISCLOSE_KINDS and doc_kind not in DISCLOSE_KINDS[node.disclose]:
            raise BuildError("line %d: :::disclose %s belongs to a %s document only; this document's kind is %s"
                             % (node.line, node.disclose, " or ".join(DISCLOSE_KINDS[node.disclose]), doc_kind))
        if node.disclose == "question-detail":
            if parent is root or parent.kind != "question":
                raise BuildError("line %d: :::disclose question-detail is allowed inside a non-central :::question only, not %s"
                                 % (node.line, at))
            if parent.central:
                raise BuildError("K7: :::disclose at line %d is inside the central question; its detail stays visible"
                                 % node.line)
            if not parent.has_child_before():
                raise BuildError("K7: :::disclose at line %d is the first child of %s; the question's prompt must precede it"
                                 % (node.line, _label(parent)))
        elif node.disclose == "evidence":
            if parent is root or parent.kind != "finding":
                raise BuildError("line %d: :::disclose evidence is allowed inside :::finding only, not %s" % (node.line, at))
            if not parent.has_child_before():
                raise BuildError("K7: :::disclose at line %d is the first child of %s; visible finding lines must precede it"
                                 % (node.line, _label(parent)))
        elif node.disclose == "detail":
            # A guided review's optional detail: closed, directly in its part 04, after the visible reading it details
            # (README, "What stays visible"). Its own section, from the last heading before it, holds a visible block
            # of that reading before it: a heading alone is not one.
            if parent is root or parent.kind != "part" or parent.number != DISCLOSE_PARTS["detail"]:
                raise BuildError("line %d: :::disclose detail is allowed directly inside :::part %s only, not %s"
                                 % (node.line, DISCLOSE_PARTS["detail"], at))
            if not parent.has_child_before():
                raise BuildError("K7: :::disclose at line %d is the first child of %s; the visible reading it details must "
                                 "precede it" % (node.line, _label(parent)))
            if not _reading_before(parent):
                raise BuildError("K7: :::disclose at line %d follows no visible block in its own section of %s; the "
                                 "visible reading it details, a paragraph, list, code block, table, quotation, callout, "
                                 "structure, range or panel after the section's heading, must precede it"
                                 % (node.line, _label(parent)))
        elif node.disclose == "provenance":
            if parent is root or parent.kind != "part" or parent.number != "10":
                raise BuildError("line %d: :::disclose provenance is allowed directly inside :::part 10 only, not %s"
                                 % (node.line, at))
            if any(isinstance(c, Node) and c.kind == "disclose" for c in parent.children):
                raise BuildError("line %d: part 10 carries at most one provenance disclosure" % node.line)
        if home is None or home.number != DISCLOSE_PARTS[node.disclose]:
            raise BuildError("line %d: :::disclose %s sits in part %s only, not %s"
                             % (node.line, node.disclose, DISCLOSE_PARTS[node.disclose], at))


def _check_annotation_position(node, parent):
    """An annotation row, list, note or range sits in a part 02 to 09, a question, a finding or a non-provenance
    disclosure. A note's row is the note's first child, and a range's row is the range's first child. Where a row or
    list sits among its siblings depends on whether it holds a review item, which is known once it closes
    (_check_flow)."""
    what = _label(node)
    if parent.kind == "part" and parent.number in CHROME_PARTS:
        raise BuildError("line %d: %s is not allowed in part %s, which carries generated chrome"
                         % (node.line, what, parent.number))
    if parent.kind == "disclose" and parent.disclose == "provenance":
        raise BuildError("line %d: %s is not allowed in a provenance disclosure" % (node.line, what))
    if parent.kind == "note":
        if node.listed:
            raise BuildError("line %d: a :::note holds an annotation row, not a list" % node.line)
        if parent.has_child_before():
            raise BuildError("line %d: a :::note holds one :::annotate row, as its first child" % node.line)
    elif parent.kind == "range":
        if parent.has_child_before():
            raise BuildError("line %d: %s sits inside %s, which holds one :::annotate row, as its first child: one "
                             "judgment per range. A row or list with no review item follows the range, and a separate "
                             "question about its content is a prompt before it" % (node.line, what, _label(parent)))
        if node.listed:
            raise BuildError("line %d: a :::range opens with an :::annotate row naming its one judgment, not a list"
                             % node.line)


def _item_fields(text):
    """One annotation item: `state <role>[: <meta>]`, `basis: <value>`, `evidence <role>[: <meta>]`,
    `review <word>[: <meta>]` or `check: <value>`. Returns (axis, word, value); raises ValueError. Meta and
    values are plain text and must show visible text."""
    if "{{" in text:
        raise ValueError("an annotation item is plain text and holds no `{{`")
    m = re.match(r"^(?P<axis>[a-z]+)(?: +(?P<word>[^\s:]+))? *(?::(?P<value>.*))?$", text)
    if not m or m.group("axis") not in ANNOTATION_AXES:
        raise ValueError("%r is not an annotation item (state, basis, evidence, review or check)" % text[:60])
    axis, word, value = m.group("axis"), m.group("word"), m.group("value")
    if value is not None:
        value = value.strip()
        if not has_visible_text(value):
            raise ValueError("the %s item's text after ':' must contain visible text" % axis)
    if axis in ("basis", "check"):
        if word is not None or value is None:
            raise ValueError("a %s item is '%s: <value>'" % (axis, axis))
        return axis, None, value
    vocab = REVIEW_WORDS if axis == "review" else MARK_AXES[axis]
    if word not in vocab:
        raise ValueError("%s %r is outside the closed set: %s" % (axis, word, ", ".join(vocab)))
    if axis == "review" and word in REVIEW_NEEDS_META and value is None:
        if word == "correction-requested":
            raise ValueError("review correction-requested names a request to change existing words and needs its record "
                             "after ':' (on what, who asked)")
        raise ValueError("review %s shows a decision and needs its record after ':' (what, who, scope)" % word)
    return axis, word, value


def _parse_item(text, lineno):
    try:
        return _item_fields(text)
    except ValueError as e:
        raise BuildError("line %d: %s" % (lineno, e))


PASSAGE_SOURCE = re.compile(r"^mark +(?P<role>[^\s:]+) +(?P<name>[^\s:]+) *:(?P<words>.*)$")


def _passage_fields(text, shown=None):
    """`mark <proposed|open|accepted|declined> <note>: <exact words>`. Returns (role, note name, words); raises
    ValueError. shown gives the words as a reader sees them (a link placeholder as its text)."""
    m = PASSAGE_SOURCE.match(text)
    if not m:
        raise ValueError("a passage mark is {{mark proposed|open|accepted|declined <note>: exact words}}")
    role, name, words = m.group("role"), m.group("name"), m.group("words").strip()
    if role == "none":
        raise ValueError("No decision recorded marks no words: a passage mark names the judgment its words take, %s, "
                         "not 'none'" % ", ".join(PASSAGE_ROLES))
    if role not in PASSAGE_ROLES:
        raise ValueError("a passage mark names the judgment its words take, %s, not %r" % (", ".join(PASSAGE_ROLES), role))
    if name == NYT_NOTE:
        raise ValueError("a passage mark names its note; the %s evidence note takes no passage mark" % NYT_NOTE)
    if not re.fullmatch(NOTE_NAME, name):
        raise ValueError("invalid note name %r in a passage mark (must match %s)" % (name, NOTE_NAME))
    if not has_visible_text(shown(words) if shown else words):
        raise ValueError("a passage mark's words after ':' must contain visible text")
    return role, name, words


def _check_item_order(items, line, order=ANNOTATION_AXES):
    """Items read in order: the owner's fixed order, state, basis, evidence, review, then check, or, in a row that
    leads with its review item, LEAD_ORDER; repeats of one axis sit together."""
    _rank_order(items, order, line)


def _reviews(node):
    """An annotate node's review items."""
    return [it for it in node.items if it[0] == "review"]


def _leads(node):
    """A row that opens a range or stands as a prompt leads with its one review item: any row holding a review
    item, but a note's row and the document's record, which keep the fixed order."""
    return not node.listed and not node.document and node.parent.kind != "note" and bool(_reviews(node))


def _close_annotate(node):
    """Parses a row's or list's item lines when it closes: each non-blank line is one item. A list may open with an
    `item: <name>` line naming the item it judges."""
    items = []
    for c in node.children:
        for n, t in c.lines:
            t = t.strip()
            if not t:
                continue
            m = ITEM_LINE.match(t)
            if m:
                if not node.listed:
                    raise BuildError("line %d: an `item:` line names the item an :::annotate list judges; a row takes "
                                     "none" % n)
                if items:
                    raise BuildError("line %d: an annotation list names its item first, in one `item:` line" % n)
                if not has_visible_text(m.group("value")):
                    raise BuildError("line %d: the item line's text after ':' must contain visible text" % n)
                items.append(("item", None, m.group("value").strip(), n))
                continue
            items.append(_parse_item(t, n) + (n,))
    records = [it for it in items if it[0] != "item"]
    if not records:
        raise BuildError("line %d: %s is empty; it holds at least one item line%s"
                         % (node.line, _label(node), " after its `item:` line" if items else ""))
    node.items = items
    reviews = _reviews(node)
    if node.parent.kind == "range" and not reviews:
        raise BuildError("line %d: a :::range's row names its one review judgment first; evidence and state never open "
                         "a range, and a row with no review item follows the block it qualifies" % node.line)
    if _leads(node):
        if records[0][0] != "review":
            raise BuildError("line %d: a row holding a review item opens a :::range or stands as a prompt before one, and "
                             "leads with its review item" % reviews[0][3])
        if len(reviews) > 1:
            raise BuildError("line %d: one judgment per %s: a second review item; blocks judged otherwise are a sibling "
                             ":::range, and a separate question about the same blocks is a prompt row of its own"
                             % (reviews[1][3], "range" if node.parent.kind == "range" else "row"))
        if node.parent.kind == "range" and records[0][2] is None:
            # A range's label names its one judgment: what it holds, the scope and who decides (README, "Review
            # annotations"). A prompt's record is checked once its place is known (_check_flow).
            raise BuildError("line %d: the review item that opens a :::range carries its record after ':': what the "
                             "range holds, the scope of the judgment and who decides or asks, as in `review %s: "
                             "<record>`" % (records[0][3], records[0][1]))
        order, axes = LEAD_ORDER, records[1:]
    else:
        order, axes = ANNOTATION_AXES, records
    for i in range(1, len(axes)):
        _check_item_order([axes[i - 1][0], axes[i][0]], axes[i][3], order)
    for i in range(1, len(records)):
        if node.listed and records[i][0] == records[i - 1][0]:
            if records[i][0] == "review":
                raise BuildError("line %d: a list answers each question once; a second judgment at another scope is its "
                                 "own :::annotate list, naming its item in its `item:` line" % records[i][3])
            raise BuildError("line %d: a list answers each question once, and this is a second %s record; two records "
                             "of one axis at different scopes take one row, which may repeat that axis"
                             % (records[i][3], records[i][0]))
    if node.listed and reviews and items[0][0] != "item":
        raise BuildError("line %d: an :::annotate list with a review line names the item it judges first, in an "
                         "`item: <name>` line: its review lines judge that item, never the blocks beside the list"
                         % node.line)
    both = [n for a, w, v, n in records if (a, w) == ("review", "proposed")]
    if not node.listed and both and any((a, w) == ("state", "proposed") for a, w, v, n in records):
        # review-semantics.css: Spectral's Proposed and review's Proposed share a word and a value; where both apply to
        # one item, the keyed list carries them, one key each.
        if node.parent.kind == "note":
            raise BuildError("line %d: a note's row cannot carry both state proposed and review proposed; keep the state "
                             "item in the block's own row or list" % both[0])
        if node.document:
            raise BuildError("line %d: the document's record cannot carry both state proposed and review proposed: they "
                             "read as one word twice, and the record is a row, never a list. Keep one of them in the "
                             "record; this pair on the whole document is a UO capability limit for now" % both[0])
        raise BuildError("line %d: state proposed and review proposed on one item read as one word twice; an :::annotate "
                         "list carries them, one key each" % both[0])


def _close_note(node):
    rows = [c for c in node.children if isinstance(c, Node)]
    first = next((c for c in node.children if isinstance(c, Node) or c.nonblank()), None)
    if not rows or rows[0].kind != "annotate" or first is not rows[0]:
        raise BuildError("line %d: %s holds an :::annotate row first" % (node.line, _label(node)))
    if len(rows) > 1:
        raise BuildError("line %d: %s holds one :::annotate row, then Markdown" % (rows[1].line, _label(node)))
    if node.name is None and not any(a == "evidence" and w == NYT_NOTE for a, w, _, _ in rows[0].items):
        raise BuildError("line %d: a :::note %s row carries an 'evidence %s' item" % (node.line, NYT_NOTE, NYT_NOTE))
    if node.name is None and _reviews(rows[0]):
        # No passage mark names the evidence note, so a review item in it would judge the blocks before it from a
        # row placed after them: the trailing row a whole-block judgment never takes (README, "Review annotations").
        raise BuildError("line %d: a :::note %s row carries no review item: it is an evidence note, and no passage mark "
                         "names it. A judgment on whole blocks opens a :::range around them; a judgment on exact words "
                         "is a passage mark and the note it names" % (_reviews(rows[0])[0][3], NYT_NOTE))


def parse_source(text):
    """Returns (meta, root Node). Raises BuildError naming the line."""
    if text.startswith("﻿"):
        text = text[1:]
    lines = [ln[:-1] if ln.endswith("\r") else ln for ln in text.split("\n")]
    i = 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i >= len(lines) or lines[i].rstrip() != ":::meta":
        raise BuildError("line %d: the source must begin with a :::meta block" % (i + 1 if i < len(lines) else 1))
    meta, i = _parse_meta(lines, i)

    root = Node("root", 0)
    stack = [root]
    fence = None
    fence_line = 0
    while i < len(lines):
        lineno, t = i + 1, lines[i]
        i += 1
        if fence is not None:
            _append_text(stack[-1], lineno, t)
            if re.match(r"^" + re.escape(fence) + r"[ ]*$", t):
                fence = None
            continue
        # structure lines and annotation item lines are text, not Markdown
        if FENCE_START.match(t) and stack[-1].kind not in ("structure", "group", "annotate"):
            if len(stack) == 1:
                raise BuildError("K8: line %d is content outside the ten parts (a fenced code block)" % lineno)
            m = FENCE_OPEN.match(t)
            if not m:
                raise BuildError("line %d: malformed fenced-code opening line" % lineno)
            fence, fence_line = m.group("fence"), lineno
            _append_text(stack[-1], lineno, t)
            continue
        if t.startswith(":::"):
            rest = t[3:].rstrip()
            if rest == "":
                if len(stack) == 1:
                    raise BuildError("line %d: stray ':::' closes nothing" % lineno)
                node = stack.pop()
                if node.kind == "annotate":
                    _close_annotate(node)
                    continue
                if node.kind not in ("part", "table") and not node.has_content():
                    raise BuildError("line %d: %s is empty" % (lineno, _label(node)))
                if node.kind == "note":
                    _close_note(node)
                continue
            m = re.match(r"^([a-z]+)(?:[ ]+(.*))?$", rest)
            if not m:
                raise BuildError("line %d: malformed container line %r" % (lineno, t))
            node = _open_container(m.group(1), _tokenize(m.group(2) or "", lineno), lineno, stack[-1], root, meta["kind"])
            stack[-1].children.append(node)
            stack.append(node)
            continue
        if len(stack) == 1:
            if t.strip():
                raise BuildError("K8: line %d is content outside the ten parts" % lineno)
            continue
        _append_text(stack[-1], lineno, t)
    if fence is not None:
        raise BuildError("line %d: unclosed fenced code block" % fence_line)
    if len(stack) > 1:
        raise BuildError("unclosed container %s at end of file" % _label(stack[-1]))
    _check_parts(meta, root)
    _check_note_names(root, {})
    _check_flow(root)
    return meta, root


FLOW_KINDS = ("part", "question", "finding", "disclose", "range")


def _is_review_row(node):
    return isinstance(node, Node) and node.kind == "annotate" and not node.listed and not node.document \
        and bool(_reviews(node))


def _check_flow(node):
    """Where each row and list sits among its siblings, once every container is parsed (review-semantics.md, rule
    2). A row holding a review item opens a :::range as its first child; outside a range it stands only as an
    explicit-target prompt, immediately before the :::range whose content it asks about or before another prompt to
    it. A row or list without a review item follows the heading or block it qualifies, never directly after another
    row, list or note. A range covers at least one block after its row."""
    for c in node.children:
        if isinstance(c, Node) and c.kind in FLOW_KINDS:
            _check_flow(c)
    if node.kind not in FLOW_KINDS:
        return
    visible = [c for c in node.children if isinstance(c, Node) or c.renders_text()]
    if node.kind == "range":
        if not visible or not (isinstance(visible[0], Node) and visible[0].kind == "annotate"):
            raise BuildError("line %d: %s opens with its :::annotate row, whose first item is its one review judgment"
                             % (node.line, _label(node)))
        if len(visible) < 2:
            raise BuildError("line %d: %s covers at least one block after its row" % (node.line, _label(node)))
        return
    for i, c in enumerate(visible):
        if not (isinstance(c, Node) and c.kind == "annotate"):
            continue
        if _is_review_row(c):
            j = i + 1
            while j < len(visible) and _is_review_row(visible[j]):
                j += 1
            if j < len(visible) and isinstance(visible[j], Node) and visible[j].kind == "range":
                review = _reviews(c)[0]
                if review[2] is None:
                    # review-semantics.md, rule 2: a bare label that names no target is no prompt.
                    raise BuildError("line %d: a prompt's review item carries its record after ':': the content below "
                                     "as its target, the scope of its question and who decides, as in `review %s: "
                                     "<record>`; a bare label that names no target is no prompt" % (review[3], review[1]))
                continue
            raise BuildError("line %d: a review judgment on whole blocks opens a :::range, even over one paragraph: its "
                             ":::annotate row is the range's first child. A row holding a review item outside a range "
                             "stands only as an explicit-target prompt, immediately before the :::range whose content it "
                             "asks about" % c.line)
        prev = visible[i - 1] if i else None
        if prev is None:
            raise BuildError("line %d: %s is the first child of %s; a row or list without a review item follows the "
                             "heading or block it qualifies" % (c.line, _label(c), _label(node)))
        if isinstance(prev, Node) and prev.kind in ("annotate", "note"):
            raise BuildError("line %d: %s follows %s; a row or list without a review item follows the heading or block "
                             "it qualifies" % (c.line, _label(c), _label(prev)))


def _check_note_names(node, seen):
    """A note's name is unique in the document: it becomes the note's id, uo-note-<name>."""
    for c in node.children:
        if isinstance(c, Node):
            if c.kind == "note" and c.name is not None:
                if c.name in seen:
                    raise BuildError("line %d: note name %r is already used at line %d" % (c.line, c.name, seen[c.name]))
                seen[c.name] = c.line
            _check_note_names(c, seen)


def _append_text(node, lineno, t):
    if not node.children or not isinstance(node.children[-1], Text):
        node.children.append(Text())
    node.children[-1].lines.append((lineno, t))


def _check_parts(meta, root):
    parts = [c for c in root.children if isinstance(c, Node) and c.kind == "part"]
    prev = None
    seen = set()
    for p in parts:
        if p.number in seen and p.number != "06":
            raise BuildError("K5: part %s repeated at line %d; only 06 may repeat" % (p.number, p.line))
        if prev is not None and p.number < prev:
            raise BuildError("K4: part %s at line %d is out of order (after part %s); parts appear in numeric order"
                             % (p.number, p.line, prev))
        seen.add(p.number)
        prev = p.number
        if p.number not in GENERATED_PARTS and not p.has_content():
            raise BuildError("K3: part %s at line %d is empty" % (p.number, p.line))
        if p.number == "03":
            central = [c for c in p.children if isinstance(c, Node) and c.kind == "question" and c.central]
            if len(central) != 1:
                raise BuildError("K6: part 03 at line %d has %d central questions; exactly one is required"
                                 % (p.line, len(central)))
        visible = [c for c in p.children if isinstance(c, Node) or c.nonblank()]
        holder = next((c for c in visible if isinstance(c, Node) and (c.kind == "synthesis" or (
            c.kind == "range" and any(isinstance(k, Node) and k.kind == "synthesis" for k in c.children)))), None)
        if holder is not None:
            # The synthesis, or the :::range that wraps it, is its part's last substantive content: a judgment on it
            # is that range; only notes, and rows or lists without a review item, follow it outside the panel
            # (review-semantics.md, "Panels take no inner note").
            synth = holder if holder.kind == "synthesis" else next(
                k for k in holder.children if isinstance(k, Node) and k.kind == "synthesis")
            if holder is not synth:
                inside = [k for k in holder.children if isinstance(k, Node) or k.nonblank()]
                after = inside[inside.index(synth) + 1:]
                if after:
                    raise BuildError("line %d: a :::synthesis closes its part, and closes the :::range that holds it; line "
                                     "%d follows it" % (synth.line, after[0].line if isinstance(after[0], Node)
                                                         else after[0].first_nonblank_line()))
            for later in visible[visible.index(holder) + 1:]:
                if isinstance(later, Node) and later.kind == "note":
                    continue
                if isinstance(later, Node) and later.kind == "annotate":
                    if _reviews(later):
                        raise BuildError("line %d: a :::synthesis closes its part, and a review judgment on it opens a "
                                         ":::range around it; the review row or list at line %d follows it"
                                         % (synth.line, later.line))
                    continue
                raise BuildError("line %d: a :::synthesis closes its part; only notes, and rows or lists without a review "
                                 "item, may follow it in part %s, and line %d does not"
                                 % (synth.line, p.number, later.line if isinstance(later, Node)
                                    else later.first_nonblank_line()))
    required = BASE_REQUIRED_PARTS + KIND_PROFILES[meta["kind"]]
    for number in required:
        if number not in GENERATED_PARTS and number not in seen:
            raise BuildError("K2: kind %s requires part %s, which is missing" % (meta["kind"], number))


# ---------------------------------------------------------------------------
# Rendering

def _render_markdown(md, text_node, context):
    """A Markdown segment rendered where context says it sits (BODY, TABLE, PROBE or ("none", label)). Outside the
    probe, any `{{` left in the output outside code is a stray brace and fails."""
    source = "\n".join(t for _, t in text_node.lines)
    md.reset()
    md.uo_context = context
    md.uo_seen = {}                   # the construct needles met so far in this segment (_ConstructError.occurrence)
    md.uo_hosts = {}                  # the item hosts' items stored so far: their stash index -> axis
    try:
        out = md.convert(source)
    except _ConstructError as e:
        raise BuildError("line %d: %s" % (_line_of(text_node, e.needle, e.occurrence), e))
    except BuildError as e:
        raise BuildError("line %d: %s" % (text_node.first_nonblank_line(), e))
    if context != PROBE and "{{" in re.sub(r"<(code|pre)\b[^>]*>.*?</\1>", "", out, flags=re.S):
        stray = [n for n, t in text_node.lines if "{{" in re.sub(r"`[^`]*`", "", t)]
        raise BuildError("line %d: `{{` outside a code span that is not an annotation (an escaped brace, a link "
                         "target or a title); a literal `{{` belongs in a code span"
                         % (stray[0] if stray else text_node.first_nonblank_line()))
    return out


CODE_SPAN = re.compile(r"`[^`]*`")


def _line_of(text_node, needles, occurrence=0):
    """The source line holding a construct. Code spans are removed from each line first, so literal braces in code
    never match. The first needle (the construct with its line's surrounding text) is taken at its occurrence-th
    appearance, which separates identical constructs on lines that differ only in what python-markdown reads first
    (paragraphs and headings in order; nested list items and table cells are read after them, so two identical
    constructs with identical surrounding text there may still name the first line); the construct's exact text is
    the fallback, at its first appearance, then the segment's first line."""
    lines = [(n, CODE_SPAN.sub("", t)) for n, t in text_node.lines]
    for k, needle in enumerate(needles if isinstance(needles, tuple) else (needles,)):
        found = [n for n, t in lines for _ in range(t.count(needle))] if needle else []
        want = occurrence if k == 0 else 0
        if len(found) > want:
            return found[want]
    return text_node.first_nonblank_line()


# ---------------------------------------------------------------------------
# Roles: the Markdown renderer's output, mapped onto the design-system-ASK document register. A role
# follows the text's use, never the element alone: a paragraph is document body, except directly inside
# a quotation, where the register's quotation rule sets it; a preformatted block is .doc-pre, carrying its
# text directly, because the foundation's element rule would set a nested <code> at 0.9em of the block.

TAG_RE = re.compile(r"<(/?)([a-zA-Z][a-zA-Z0-9]*)((?:\s[^<>]*?)?)\s*(/?)>")
PRE_CODE = re.compile(r'<pre><code(?: class="language-[^"<>]*")?>(.*?)</code></pre>', re.S)
TAG_ROLE = {"li": "doc-body", "h2": "doc-section-title", "h3": "doc-subsection-title", "h4": "doc-deep-title",
            "blockquote": "doc-quote", "a": "surface-text-link", "code": "doc-code"}
HEADING_LEVEL = re.compile(r"^<h([2-4])\b")


def assign_roles(fragment, line, in_quote=False):
    """Adds each rendered element's register role. in_quote renders the fragment as a quotation's body,
    whose top-level paragraphs the quotation rule sets."""
    fragment = PRE_CODE.sub(lambda m: '<pre class="doc-pre">%s</pre>' % m.group(1), fragment)
    out, stack, pos = [], (["blockquote"] if in_quote else []), 0
    for m in TAG_RE.finditer(fragment):
        out.append(fragment[pos:m.start()])
        pos = m.end()
        tag = m.group(2).lower()
        if m.group(1):
            if stack and stack[-1] == tag:
                stack.pop()
            out.append(m.group(0))
            continue
        parent = stack[-1] if stack else None
        if tag in ("h2", "h3", "h4") and "blockquote" in stack:
            raise BuildError("line %d: a quotation holds no heading" % line)
        cls = None
        if tag == "p":
            cls = None if parent == "blockquote" else "doc-body"
        elif tag in TAG_ROLE:
            cls = TAG_ROLE[tag]
        if cls and not re.search(r"\sclass=", m.group(3)):
            # an element that already carries a class (a fenced block's attributes) is left for the allowlist
            out.append(m.group(0)[:1 + len(tag)] + ' class="%s"' % cls + m.group(0)[1 + len(tag):])
        else:
            out.append(m.group(0))
        if not m.group(4) and tag not in VOID_ELEMENTS:
            stack.append(tag)
    out.append(fragment[pos:])
    return "".join(out)


def top_blocks(fragment, line):
    """The top-level elements of a rendered fragment, in order. Anything but whitespace between them is an
    internal error: python-markdown wraps every block."""
    blocks, depth, start, last = [], 0, 0, 0
    for m in TAG_RE.finditer(fragment):
        tag, closing, void = m.group(2).lower(), bool(m.group(1)), bool(m.group(4)) or m.group(2).lower() in VOID_ELEMENTS
        if depth == 0 and not closing:
            if fragment[last:m.start()].strip():
                raise BuildError("line %d: internal: text outside a block: %r" % (line, fragment[last:m.start()].strip()[:40]))
            start = m.start()
        if closing:
            depth -= 1
            if depth == 0:
                blocks.append(fragment[start:m.end()])
                last = m.end()
        elif void:
            if depth == 0:
                blocks.append(m.group(0))
                last = m.end()
        else:
            depth += 1
    if depth != 0 or fragment[last:].strip():
        raise BuildError("line %d: internal: unbalanced rendered fragment" % line)
    return blocks


def _text_items(md, text_node, context, in_quote=False):
    """A Markdown segment as composition items: ("h", level, html) for a heading, ("b", html) otherwise. context
    is where the segment sits (_inline_context)."""
    rendered = _render_markdown(md, text_node, context)
    if "<table" in rendered:
        raise BuildError("line %d: a pipe table must be wrapped in :::table with its column roles"
                         % text_node.first_nonblank_line())
    line = text_node.first_nonblank_line()
    fragment = assign_roles(rendered, line, in_quote)
    if context == BODY and '<span class="doc-annotation-item">' in fragment:
        fragment = _item_hosts(fragment, line)
    items = []
    for b in top_blocks(fragment, line):
        h = HEADING_LEVEL.match(b)
        items.append(("h", int(h.group(1)), b) if h else ("b", b))
    return items


# A rendered fragment as a lossless tree: an element keeps its raw start and end tags, text stays text, and joining
# the parts back reproduces the fragment byte for byte. The item hosts and the notes attached in a list item are
# placed on it.
class _El:
    def __init__(self, tag, open_tag):
        self.tag, self.open, self.kids, self.close = tag, open_tag, [], ""

    def html(self):
        return self.open + _joined(self.kids) + self.close


def _joined(kids):
    return "".join(k if isinstance(k, str) else k.html() for k in kids)


def _fragment_tree(fragment, line):
    root = _El("", "")
    stack, pos = [root], 0
    for m in TAG_RE.finditer(fragment):
        if fragment[pos:m.start()]:
            stack[-1].kids.append(fragment[pos:m.start()])
        pos = m.end()
        tag = m.group(2).lower()
        if m.group(1):
            if len(stack) < 2 or stack[-1].tag != tag:
                raise BuildError("line %d: internal: unbalanced rendered fragment" % line)
            stack.pop().close = m.group(0)
            continue
        el = _El(tag, m.group(0))
        stack[-1].kids.append(el)
        if not m.group(4) and tag not in VOID_ELEMENTS:
            stack.append(el)
    if fragment[pos:]:
        stack[-1].kids.append(fragment[pos:])
    if len(stack) != 1:
        raise BuildError("line %d: internal: unbalanced rendered fragment" % line)
    return root


ITEM_OPEN = '<span class="doc-annotation-item">'
FLOW_BLOCKS = ("ul", "ol", "p", "div", "pre", "blockquote", "table", "hr", "h2", "h3", "h4")


def _item_hosts(fragment, line):
    """Each list item its items open becomes an item host (design-system-ASK review-semantics.md, "Annotation
    range"): li.doc-annotation-range.surface-labeled-range, its row first, then its words in a p.doc-body of their
    own, since a range takes no content role; a loose item keeps its other blocks after them, and a tight item its
    nested list. The items were placed and ordered where they were parsed (_AnnotationInline._host_item)."""
    root = _fragment_tree(fragment, line)

    def walk(el):
        for k in el.kids:
            if isinstance(k, _El):
                if k.tag == "li" and k.open == '<li class="doc-body">':
                    _host(k)
                walk(k)

    def _host(li):
        lead = next((k for k in li.kids if not (isinstance(k, str) and not k.strip())), None)
        loose = isinstance(lead, _El) and lead.tag == "p"
        kids = lead.kids if loose else li.kids
        i = 0
        while i < len(kids) and isinstance(kids[i], str) and not kids[i].strip():
            i += 1
        if not (i < len(kids) and isinstance(kids[i], _El) and kids[i].open == ITEM_OPEN):
            return
        items = []
        while i < len(kids) and (isinstance(kids[i], _El) and kids[i].open == ITEM_OPEN
                                 or isinstance(kids[i], str) and not kids[i].strip()):
            if isinstance(kids[i], _El):
                items.append(kids[i].html())
            i += 1
        if loose:
            words, after = kids[i:], li.kids[li.kids.index(lead) + 1:]
        else:
            end = next((j for j in range(i, len(kids)) if isinstance(kids[j], _El) and kids[j].tag in FLOW_BLOCKS),
                       len(kids))
            words, after = kids[i:end], kids[end:]
        if words and isinstance(words[0], str):
            words = [words[0].lstrip()] + words[1:]
        if words and isinstance(words[-1], str):
            words = words[:-1] + [words[-1].rstrip()]
        if not has_visible_text(html.unescape(re.sub(r"<[^>]*>", "", _joined(words)))):
            raise BuildError("line %d: an item host's words follow its row: the list item holds words after its items"
                             % line)
        if ITEM_OPEN in _joined(words) + _joined(after):
            raise BuildError("line %d: internal: an item host's items are not all at its start" % line)
        li.open = '<li class="%s">' % RANGE_CLASS
        li.kids = ['<div class="doc-annotations">\n%s\n</div>' % "\n".join(items),
                   '<p class="doc-body">%s</p>' % _joined(words)] + after
    walk(root)
    return _joined(root.kids)


def _check_note_items(list_html, text_node):
    """A note records the words of one list item, as it records those of one block: passage marks naming one note
    in two items of a list, an item and its nested item included, fail, whether the note would sit in a plain item,
    follow the list after an item host or follow the range that holds the list."""
    root = _fragment_tree(list_html, text_node.first_nonblank_line())
    items = {}                    # note name -> the innermost list items holding a mark naming it

    def walk(el, li):
        for k in el.kids:
            if isinstance(k, _El):
                if k.tag == "mark":
                    m = re.search(r'aria-describedby="uo-note-(%s)"' % NOTE_NAME, k.open)
                    if m and li is not None and all(li is not x for x in items.setdefault(m.group(1), [])):
                        items[m.group(1)].append(li)
                    continue
                walk(k, k if k.tag == "li" else li)
    walk(root, None)
    for name, lis in items.items():
        if len(lis) > 1:
            lines = [n for n, t in text_node.lines
                     if re.search(r"\{\{mark +[^\s:]+ +" + re.escape(name) + r" *:", CODE_SPAN.sub("", t))]
            raise BuildError("line %d: passage marks in %d list items name note %r; a note records the words of one "
                             "list item, as it does those of one block: give each item's marks a note of their own"
                             % (lines[1] if len(lines) > 1 else text_node.first_nonblank_line(), len(lis), name))


def _attach_note(list_html, name, note_html, line):
    """A note on words in a plain list item, one that is neither a range nor held by one, sits inside that item,
    after the item's text, where it takes the owner's 12px attachment (design-system-ASK review-semantics.md,
    "Annotation note"). Returns the list with the note placed, or None where the words sit in an item host, whose
    note follows the list. A second note on the same item follows the first. The marks naming the note sit in one
    list item (_check_note_items)."""
    root = _fragment_tree(list_html, line)
    needle = 'aria-describedby="uo-note-%s"' % name

    def path_to(el, trail):
        for k in el.kids:
            if isinstance(k, _El):
                if k.tag == "mark" and needle in k.open:
                    return trail + [k]
                found = path_to(k, trail + [k])
                if found:
                    return found
        return None
    path = path_to(root, [])
    lis = [e for e in path or [] if e.tag == "li"]
    if not lis or any(RANGE_CLASS in e.open for e in lis):
        return None
    li = lis[-1]
    child = path[path.index(li) + 1]
    # After the item's text: its inline words, or a loose item's paragraphs, and before any nested list.
    start = li.kids.index(child) + (1 if child.tag in FLOW_BLOCKS else 0)
    nested = ("ul", "ol") if child.tag in FLOW_BLOCKS else FLOW_BLOCKS
    at = next((j for j in range(start, len(li.kids)) if isinstance(li.kids[j], _El) and li.kids[j].tag in nested),
              len(li.kids))
    while at > start and isinstance(li.kids[at - 1], str) and not li.kids[at - 1].strip():
        at -= 1
    while True:
        j = at
        while j < len(li.kids) and isinstance(li.kids[j], str) and not li.kids[j].strip():
            j += 1
        if j < len(li.kids) and isinstance(li.kids[j], _El) and "doc-annotation-note" in li.kids[j].open:
            at = j + 1
            continue
        break
    li.kids[at:at] = ["\n", note_html] + (["\n"] if at < len(li.kids) and isinstance(li.kids[at], _El) else [])
    return _joined(root.kids)


class _Section:
    def __init__(self, level, open_tag, close_tag):
        self.level, self.open, self.close = level, open_tag, close_tag
        self.parts, self.run = [], []

    def flush(self):
        if self.run:
            self.parts.append('<div class="doc-prose">\n%s\n</div>' % "\n".join(self.run))
            self.run = []

    def html(self):
        self.flush()
        return "%s\n%s\n%s" % (self.open, "\n".join(self.parts), self.close)


def compose(items, open_tag, close_tag, title=False):
    """Composition: a heading governs what follows it until a heading of its level or above, so each heading
    opens a nested div.doc-section; runs of other blocks sit in div.doc-prose. The container is itself a
    section (a part, a question, a finding, a disclosure's body), so a section's nesting takes the register's
    lead wherever it occurs. ("c", html) items sit directly in their current section, outside any run;
    ("part", html) items close every nested section and sit directly in the container (a framing or a
    synthesis belongs to its part). With title=True a first heading is its container's own title (a part's
    ## heading)."""
    root = _Section(1, open_tag, close_tag)
    stack = [root]
    for i, item in enumerate(items):
        if item[0] == "h":
            level, html_ = item[1], item[2]
            stack[-1].flush()
            while len(stack) > 1 and stack[-1].level >= level:
                done = stack.pop()
                stack[-1].parts.append(done.html())
            if title and i == 0:
                root.level = level
                root.parts.append(html_)
                continue
            sec = _Section(level, '<div class="doc-section">', "</div>")
            sec.parts.append(html_)
            stack.append(sec)
        elif item[0] == "c":
            stack[-1].flush()
            stack[-1].parts.append(item[1])
        elif item[0] == "part":             # a framing or synthesis belongs to the part itself: close every section
            stack[-1].flush()
            while len(stack) > 1:
                done = stack.pop()
                stack[-1].parts.append(done.html())
            stack[-1].flush()
            root.parts.append(item[1])
        else:
            stack[-1].run.append(item[1])
    while len(stack) > 1:
        done = stack.pop()
        stack[-1].parts.append(done.html())
    return root.html()


TABLE_CELL = re.compile(r"<(th|td)((?:\s[^>]*)?)>(.*?)</\1>", re.S)
HEADER_CELL = re.compile(r"<th(?:\s[^>]*)?>(.*?)</th>", re.S)


def cell_label(text):
    """A header cell's text as a body cell's data-uo-label carries it: whitespace
    runs collapsed to one space, outer whitespace removed. The renderer applies it
    to the header's rendered text with tags removed and character references
    decoded; the allowlist applies it to the parsed header text and compares."""
    return re.sub(r"\s+", " ", text).strip()


CELL_ITEM = re.compile(r'<span class="doc-annotation-item">(?:<span class="[^"<>]*"(?: data-[a-z]+="[^"<>]*")?>[^<>]*</span>)'
                       r'{1,2}</span>')
CELL_ITEM_AXIS = re.compile(r'data-(state|evidence|review)="|<span class="doc-label">(Basis|Check)</span>')


def _cell_items(value, role, column, line):
    """A body cell's annotation items, written {{...}} in the cell: the cell holds them only, in a text or status
    column, in the fixed order. They become one annotation row on the cell's first baseline, span.doc-annotations
    (design-system-ASK review-semantics.html, "A table cell")."""
    items = CELL_ITEM.findall(value)
    if not items:
        return value
    if role not in ("text", "status"):
        raise BuildError("line %d: column %d is a %s column; annotation items sit in a text or status column"
                         % (line, column + 1, role))
    if CELL_ITEM.sub("", value).strip():
        raise BuildError("line %d: a cell holding annotation items holds them only (column %d)" % (line, column + 1))
    axes = []
    for item in items:
        m = CELL_ITEM_AXIS.search(item)
        axes.append(m.group(1) or m.group(2).lower())
    _check_item_order(axes, line)
    joined = "".join(items)
    if 'data-state="proposed"' in joined and 'data-review="proposed">Proposed<' in joined:
        raise BuildError("line %d: state proposed and review proposed in one cell read as one word twice; carry them in an "
                         ":::annotate list, one key each (column %d)" % (line, column + 1))
    return '<span class="doc-annotations">%s</span>' % joined


def _render_table(md, node):
    """A declared dense table is table.doc-dense-table: .doc-label headers, .doc-table-cell values. Any other
    table is a narrative table: .doc-label headers and .doc-body cells (design-system-ASK DENSE TABLE; the
    output-artifact v3 narrative-table rule). A key cell's value is inline emphasis. A text or status cell may
    hold annotation items instead of a value."""
    texts = [c for c in node.children if isinstance(c, Text) and c.nonblank()]
    if any(isinstance(c, Node) for c in node.children) or len(texts) != 1:
        raise BuildError("line %d: a :::table container holds exactly one pipe table and nothing else" % node.line)
    out = _render_markdown(md, texts[0], _table_context(node))
    n_tables = out.count("<table")
    stripped = re.sub(r"<table>.*?</table>", "", out, flags=re.S).strip() if n_tables == 1 else out
    if n_tables != 1 or stripped:
        raise BuildError("line %d: a :::table container holds exactly one pipe table and nothing else (found %d tables)"
                         % (node.line, n_tables))
    _check_row_cells(texts[0])
    out = assign_roles(out, node.line)
    rows = re.findall(r"<tr>(.*?)</tr>", out, flags=re.S)
    columns = len(TABLE_CELL.findall(rows[0])) if rows else 0
    if columns != len(node.roles):
        raise BuildError("line %d: :::table declares %d roles for %d columns" % (node.line, len(node.roles), columns))
    heads = HEADER_CELL.findall(rows[0])
    labels = [cell_label(html.unescape(re.sub(r"<[^>]*>", "", h))) for h in heads]
    # The visible narrow-width label is a real element carrying the header cell's own inline markup, so a
    # header's link stays a link and its inline code stays code.
    label_html = [h.strip() for h in heads]
    for column, cased in enumerate(node.cased):
        if not cased:
            continue
        if not has_visible_text(labels[column]):
            raise BuildError("line %d: column %d's header is declared %s and must contain visible text"
                             % (node.line, column + 1, AUTHORED_CASE))
        if re.search(r"<(?!/?(?:strong|em)>)", label_html[column]):
            raise BuildError("line %d: column %d's header is declared %s and holds text and inline emphasis only"
                             % (node.line, column + 1, AUTHORED_CASE))
    body_role = "doc-table-cell" if node.dense else "doc-body"

    def as_authored(column, inner):
        return '<span class="uo-authored-case">%s</span>' % inner if node.cased[column] else inner

    row_lines = [n for n, t in texts[0].lines if t.strip()]     # the header row, the delimiter row, the body rows
    row_no = [0]

    def fix_row(m):
        i = [0]
        k = row_no[0]
        row_no[0] += 1
        line = row_lines[0] if k == 0 else row_lines[k + 1] if k + 1 < len(row_lines) else node.line

        def cell(cm):
            role = node.roles[i[0]] if i[0] < len(node.roles) else None
            i[0] += 1
            if role is None:
                raise BuildError("line %d: a table row has more cells than declared roles" % node.line)
            column = i[0] - 1
            if cm.group(1) != "td":
                return '<th class="doc-label" data-uo-cell="%s"%s>%s</th>' % (role, cm.group(2), as_authored(column, cm.group(3)))
            value = _cell_items(cm.group(3), role, column, line)
            value = "<strong>%s</strong>" % value if role == "key" and value.strip() else value
            return '<td class="%s" data-uo-cell="%s" data-uo-label="%s"%s><span class="uo-cell-label doc-label">%s</span>%s</td>' % (
                body_role, role, _esc(labels[column]), cm.group(2), as_authored(column, label_html[column]), value)
        return "<tr>" + TABLE_CELL.sub(cell, m.group(1)) + "</tr>"

    out = re.sub(r"<tr>(.*?)</tr>", fix_row, out, flags=re.S)
    classes = (["doc-dense-table"] if node.dense else []) + (["uo-local-%s" % node.local] if node.local else [])
    if classes:
        out = out.replace("<table>", '<table class="%s">' % " ".join(classes), 1)
    if node.caption is not None:
        out = re.sub(r"(<table[^>]*>)", lambda t: '%s\n<caption class="doc-meta">%s</caption>' % (t.group(1), _esc(node.caption)),
                     out, count=1)
    return out


def _check_row_cells(text_node):
    """Counts the cells of every source row with python-markdown's own row
    splitter (unescaped | outside code spans; outer pipes stripped when the
    header row has them), and fails when a row's count differs from the
    header's. python-markdown would otherwise drop extra cells or pad missing
    ones without an error."""
    rows = [(n, t.strip(" ")) for n, t in text_node.lines if t.strip()]
    splitter = TableProcessor.__new__(TableProcessor)
    header = rows[0][1]
    splitter.border = 0
    if header.startswith("|"):
        splitter.border |= 1
    if TableProcessor.RE_END_BORDER.search(header) is not None:
        splitter.border |= 2
    expected = len(splitter._split_row(header))
    for n, row in rows[1:]:
        count = len(splitter._split_row(row))
        if count != expected:
            raise BuildError("line %d: table row has %d cells; the header row has %d" % (n, count, expected))


def _classes(base, node):
    return base + (" uo-local-%s" % node.local if node.local else "")


def _inline_context(node):
    """Where a container's own Markdown sits: BODY directly inside a part 02 to 09, a question, a finding or an
    authored disclosure other than provenance, and RANGE_BODY inside a :::range there, where a passage mark may sit;
    anywhere else ("none", label), no annotation construct."""
    if node.kind == "range":
        return RANGE_BODY
    if ((node.kind == "part" and node.number not in CHROME_PARTS) or node.kind in ("question", "finding")
            or (node.kind == "disclose" and node.disclose != "provenance")):
        return BODY
    return ("none", _label(node))


def _table_context(node):
    """A table's cells take annotation items where its container's text may carry annotations: a part 02 to 09, a
    question, a finding, a :::range or an authored disclosure other than provenance. In part 01 or 10 or in a
    provenance disclosure, no annotation sits."""
    return TABLE if _inline_context(node.parent) in (BODY, RANGE_BODY) else ("chrome-table", _label(node.parent))


PASSAGE_HTML = re.compile(r'<mark class="' + PASSAGE_CLASS + r'" data-review="([a-z]+)" aria-describedby="uo-note-('
                          + NOTE_NAME + r')">')
# The review words in a note's row that record the judgment each passage mark shows.
RECORDS_ROLE = {"proposed": ("proposed", "correction-requested"), "open": ("open",), "accepted": ("accepted",),
                "declined": ("declined",)}


def _mark_line(text_node, name, role):
    """The line of the first passage mark painting role that names note name, code spans removed first."""
    for n, t in text_node.lines:
        if re.search(r"\{\{mark +" + re.escape(role) + r" +" + re.escape(name) + r" *:", CODE_SPAN.sub("", t)):
            return n
    return text_node.first_nonblank_line()


def _first_pending(pending):
    """The earliest passage mark still waiting for its note: (line, note name)."""
    return min((line, name) for name, roles in pending.items() for line in roles.values())


def _check_note_roles(note, roles):
    """A note records the judgment its passage marks show, pending or decided: proposed by a review proposed or review
    correction-requested item, open by review open, accepted by review accepted and declined by review declined, in
    the note's row. Its row holds no other review item: one whose role no mark naming the note shows would judge
    something other than the marked words, from a row placed after the blocks."""
    reviews = [(w, n) for a, w, v, n in next(c for c in note.children if isinstance(c, Node)).items if a == "review"]
    words = {w for w, n in reviews}
    for role, line in sorted(roles.items(), key=lambda x: x[1]):
        if not words & set(RECORDS_ROLE[role]):
            raise BuildError("line %d: a passage mark showing %s names note %r, whose row records no %s item; a note "
                             "records the judgment its mark shows"
                             % (line, role, note.name, " or ".join("review " + w for w in RECORDS_ROLE[role])))
    for w, n in reviews:
        if w == "none":
            raise BuildError("line %d: the row of note %r holds review none: No decision recorded marks no words, so no "
                             "passage mark records it in a note" % (n, note.name))
        if REVIEW_WORDS[w][0] not in roles:
            raise BuildError("line %d: the row of note %r holds review %s, but no passage mark naming the note shows %s: "
                             "a note's review items record only what its marks show. A judgment on whole blocks opens a "
                             ":::range around them, and other words take a passage mark of their own"
                             % (n, note.name, w, REVIEW_WORDS[w][0]))


def _items(md, node, counts, in_quote=False, carry=False):
    """A container's children as composition items. An annotation row, list, note or range sits directly in its
    section, outside any prose run. A passage mark's note follows the block or the :::range holding the mark, in the
    same container, with only notes and rows or lists without a review item between and no heading; a named note
    follows a mark that names it. A note on words in a plain list item is placed inside that item (_attach_note).
    With carry, the container is a :::range: the blocks it covers follow a mark before its note, since that note
    follows the whole range, and the marks still waiting for their note are returned with the items, for the
    container the range sits in. A note still records the words of one block, so a later block's mark naming a note
    already waiting fails."""
    items, origin = [], []        # origin: the child each item came from
    pending, holder = {}, {}      # note name -> {role shown: line of the first mark showing it}; -> its item's index
    context = _inline_context(node)

    def heading_between():
        line, name = _first_pending(pending)
        return BuildError("line %d: the passage mark naming note %r has no note before the next heading; its note follows "
                          "its block in the same section" % (line, name))

    def block_between():
        line, name = _first_pending(pending)
        return BuildError("line %d: the passage mark naming note %r is followed by another block or container before its "
                          "note; a note follows the block or range holding its mark, with only other notes and rows or "
                          "lists without a review item between" % (line, name))

    for c in node.children:
        if isinstance(c, Text):
            if not c.nonblank():
                continue
            seen = {}             # note name -> marks naming it read so far in this text, for a later mark's line
            for item in _text_items(md, c, context, in_quote):
                if pending and not carry:
                    raise heading_between() if item[0] == "h" else block_between()
                if item[0] == "h" and node.kind == "range":
                    raise BuildError("line %d: %s holds a heading: a range covers blocks under their heading, and a range "
                                     "over a heading alone is a UO capability limit for now; raise it with the owner"
                                     % (next((n for n, t in c.lines if re.match(r"^ {0,3}#", t)), c.first_nonblank_line()),
                                        _label(node)))
                if item[0] == "b" and re.match(r"<[uo]l\b", item[1]) and PASSAGE_HTML.search(item[1]):
                    _check_note_items(item[1], c)
                for role, name in PASSAGE_HTML.findall(item[-1]):
                    counts["passage_marks"] += 1
                    seen[name] = seen.get(name, 0) + 1
                    if name in pending and holder[name] != len(items):
                        lines = [n for n, t in c.lines for _ in re.findall(
                            r"\{\{mark +[^\s:]+ +" + re.escape(name) + r" *:", CODE_SPAN.sub("", t))]
                        raise BuildError("line %d: passage marks in two blocks name note %r; a note records the words of "
                                         "one block, as it does those of one list item: give each block's marks a note "
                                         "of their own" % (lines[seen[name] - 1] if seen[name] <= len(lines)
                                                           else c.first_nonblank_line(), name))
                    pending.setdefault(name, {}).setdefault(role, _mark_line(c, name, role))
                    holder[name] = len(items)
                counts["item_hosts"] += item[-1].count('<li class="%s">' % RANGE_CLASS)
                items.append(item)
                origin.append(c)
            continue
        if c.kind == "note" and c.name is not None:
            if c.name not in pending:
                raise BuildError("line %d: %s follows no passage mark naming it in %s; a note records a passage "
                                 "mark before it" % (c.line, _label(c), _label(node)))
            _check_note_roles(c, pending.pop(c.name))
            html_ = _render_node(md, c, counts)
            at = holder.pop(c.name)
            if items[at][0] == "b" and re.match(r"<[uo]l\b", items[at][1]):
                placed = _attach_note(items[at][1], c.name, html_, c.line)
                if placed is not None:
                    items[at] = ("b", placed)
                    continue
            items.append(("c", html_))
            origin.append(c)
            continue
        if c.kind == "range":
            if pending:
                raise block_between()
            html_, carried = _render_range(md, c, counts)
            for name, roles in carried.items():
                pending.setdefault(name, {}).update(roles)
                holder[name] = len(items)
            if _holds_panel(c):
                # A range over a framing or synthesis belongs to its part, as the panel does; the prompts before it
                # move with it.
                k = len(items) - 1
                while k >= 0 and _is_review_row(origin[k]):
                    items[k] = ("part", items[k][1])
                    k -= 1
            items.append(("part" if _holds_panel(c) else "c", html_))
            origin.append(c)
            continue
        html_ = _render_node(md, c, counts)
        if pending and not carry and not (c.kind == "note" or c.kind == "annotate" and not _reviews(c)):
            raise heading_between() if re.search(r"<h[1-6][\s>]", html_) else block_between()
        items.append(("part", html_) if c.kind in PANELS
                     else ("c", html_) if c.kind in ("banner", "annotate", "note") else ("b", html_))
        origin.append(c)
    if carry:
        return items, pending
    if pending:
        line, name = _first_pending(pending)
        raise BuildError("line %d: the passage mark naming note %r has no :::note %s after it in %s"
                         % (line, name, name, _label(node)))
    return items


def _render_range(md, node, counts):
    """A :::range: div.doc-group.doc-annotation-range.surface-labeled-range, its row first, naming its one review
    judgment, then the blocks it covers, runs of blocks in a prose run and a panel directly (design-system-ASK
    review-semantics.md, "Annotation range"). Returns the html and the marks inside it still waiting for their note,
    which follows the range."""
    counts["annotation_ranges"] += 1
    items, carried = _items(md, node, counts, carry=True)
    out, run = ['<div class="%s">' % RANGE_DIV, items[0][1]], []
    for item in items[1:]:
        if item[0] == "b":
            run.append(item[1])
            continue
        if run:
            out.append('<div class="doc-prose">\n%s\n</div>' % "\n".join(run))
            run = []
        out.append(item[1])
    if run:
        out.append('<div class="doc-prose">\n%s\n</div>' % "\n".join(run))
    out.append("</div>")
    return "\n".join(out), carried


def _blocks_only(items, node, allowed):
    """A container that holds no heading: its items as HTML, each a block whose element is in allowed."""
    out = []
    for item in items:
        if item[0] == "h":
            raise BuildError("line %d: %s holds a heading; it is never a heading's container" % (node.line, _label(node)))
        tag = re.match(r"<([a-z0-9]+)", item[1]).group(1)
        if tag not in allowed:
            raise BuildError("line %d: %s holds a <%s> block; it holds %s only" % (node.line, _label(node), tag, ", ".join(allowed)))
        out.append(item[1])
    return "\n".join(out)


def _render_structure(node):
    """A structured block (design-system-ASK PREFORMATTED AND STRUCTURED TEXT): each source line is a
    pre.doc-pre-part; two spaces of indentation are one level, and the lines beneath a line sit in a
    div.doc-hierarchy, one per level. Blank source lines before a line are recorded as data-lead-lines.
    Declared peer groups (:::group) are the block's only children when present: each opens on its label,
    its first line, and sets nothing apart inside it."""
    groups = [c for c in node.children if isinstance(c, Node)]
    loose = [c for c in node.children if isinstance(c, Text) and c.nonblank()]
    if groups and loose:
        raise BuildError("line %d: a :::structure that declares groups holds only :::group containers, not text at line %d"
                         % (node.line, loose[0].first_nonblank_line()))
    if groups:
        inner = "\n".join('<div class="doc-pre-group">%s</div>' % _structure_lines(g, grouped=True) for g in groups)
    else:
        inner = _structure_lines(node, grouped=False)
    return '<div class="%s">%s</div>' % (_classes("doc-pre doc-pre--structured", node), inner)


def _structure_lines(node, grouped):
    lines = [(n, t) for c in node.children if isinstance(c, Text) for n, t in c.lines]
    while lines and not lines[0][1].strip():
        lines.pop(0)
    while lines and not lines[-1][1].strip():
        lines.pop()
    out, depth, blanks, prev = [], 0, 0, None
    for n, t in lines:
        if "\t" in t:
            raise BuildError("line %d: a structure line is indented with spaces, two per level, never a tab" % n)
        if not t.strip():
            if grouped:
                raise BuildError("line %d: a blank line inside a :::group; a peer group sets nothing apart inside it" % n)
            blanks += 1
            continue
        indent = len(t) - len(t.lstrip(" "))
        if indent % 2:
            raise BuildError("line %d: a structure line's indentation is two spaces per level (found %d)" % (n, indent))
        level = indent // 2
        if prev is None and level:
            raise BuildError("line %d: a structure's first line sits at the first level" % n)
        if prev is not None and level > prev + 1:
            raise BuildError("line %d: a structure line is more than one level beneath the line before it" % n)
        if blanks > MAX_LEAD_LINES:
            raise BuildError("line %d: %d blank lines before a structure line; at most %d are recorded"
                             % (n, blanks, MAX_LEAD_LINES))
        lead = ' data-lead-lines="%d"' % blanks if blanks else ""
        while depth > level:
            out.append("</div>")
            depth -= 1
        if level > depth:
            out.append('<div class="doc-hierarchy"%s>' % lead)
            depth += 1
            lead = ""
        out.append('<pre class="doc-pre-part"%s>%s</pre>' % (lead, _esc(t[indent:])))
        blanks, prev = 0, level
    out.extend("</div>" for _ in range(depth))
    return "".join(out)


def _render_annotations(node):
    """An annotation row, div.doc-annotations, its items in order; or an annotation list, dl.doc-annotation-list:
    its Item line first where it names one, then one dt.doc-label key per axis present, each followed by one dd
    holding that axis's marks and metadata (design-system-ASK review-semantics.html, "One item, several
    questions")."""
    if not node.listed:
        return '<div class="doc-annotations">\n%s\n</div>' % "\n".join(item_html(a, w, v) for a, w, v, _ in node.items)
    axes = []
    for a, w, v, _ in node.items:
        if not axes or axes[-1][0] != a:
            axes.append((a, []))
        axes[-1][1].append((w, v))
    lines = []
    for a, entries in axes:
        dd = "".join(meta_html(v) if a in ("item", "basis", "check") else mark_html(a, w) + (meta_html(v) if v is not None else "")
                     for w, v in entries)
        lines.append('<dt class="doc-label">%s</dt>\n<dd>%s</dd>' % (AXIS_KEYS[a], dd))
    return '<dl class="doc-annotation-list">\n%s\n</dl>' % "\n".join(lines)


def _render_node(md, node, counts):
    if node.kind == "table":
        counts["tables"] += 1
        out = _render_table(md, node)
        if node.parent.kind == "range" and 'data-review="' in out:
            # design-system-ASK review-semantics.md, rule 2: a whole-table range holds no independently judged cells.
            raise BuildError("line %d: a :::table whose cells carry review items cannot sit in a :::range: a range carries "
                             "one judgment, and a judgment on a whole table whose cells carry judgments of their own is "
                             "raised with the owner. Keep the cells' review items and leave the table outside a range, or "
                             "keep the range and move the cells' judgments out of the table" % node.line)
        counts["authored_case"] += out.count('<span class="uo-authored-case">')
        counts["cell_items"] += out.count('<span class="doc-annotation-item">')
        return out
    if node.kind == "annotate":
        counts["annotation_lists" if node.listed else "annotation_rows"] += 1
        return _render_annotations(node)
    if node.kind == "note":
        # The record a passage mark points to: a .doc-hierarchy group carrying its id; the not-yet-testable evidence
        # note draws that role's dashed rail instead, and no passage mark names it.
        counts["annotation_notes"] += 1
        items = _items(md, node, counts)
        body = _blocks_only(items[1:], node, ("p", "ul", "ol"))
        if node.name is None:
            head = '<div class="doc-group doc-annotation-note" data-evidence="%s">' % NYT_NOTE
        else:
            head = '<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-%s">' % node.name
        return "\n".join(x for x in (head, items[0][1], body, "</div>") if x)
    if node.kind == "structure":
        counts["structures"] += 1
        return _render_structure(node)
    if node.kind == "quote":
        counts["quotations"] += 1
        body = _blocks_only(_items(md, node, counts, in_quote=True), node, ("p", "pre", "ul", "ol", "blockquote"))
        footer = "\n<footer>%s</footer>" % _esc(node.attribution) if node.attribution is not None else ""
        return '<blockquote class="%s">\n%s%s\n</blockquote>' % (_classes("doc-quote", node), body, footer)
    items = _items(md, node, counts)
    if node.kind == "question":
        counts["questions"] += 1
        central = ' data-uo-central="true"' if node.central else ""
        return compose(items, '<div data-uo-role="question"%s class="%s">' % (central, _classes("doc-section", node)), "</div>")
    if node.kind == "finding":
        counts["findings"] += 1
        return compose(items, '<div data-uo-role="finding" class="%s">' % _classes("doc-section", node), "</div>")
    if node.kind == "callout":
        counts["callouts"] += 1
        body = _blocks_only(items, node, ("p", "ul", "ol", "blockquote", "pre", "div"))
        if not node.local and len(items) == 1 and items[0][1].startswith('<p class="doc-body">'):
            return '<p class="doc-body surface-emphasis-rail" data-uo-role="callout">' + items[0][1][len('<p class="doc-body">'):]
        return '<div data-uo-role="callout" class="%s">\n%s\n</div>' % (_classes("surface-emphasis-rail doc-group", node), body)
    if node.kind in ("framing", "synthesis"):
        counts[node.kind] += 1
        word = FRAMING_WORDS[node.word] if node.kind == "framing" else SYNTHESIS_WORD
        body = _blocks_only(items, node, ("p", "ul", "ol"))
        return ('<div data-uo-role="%s" class="%s">\n<p class="surface-emphasis-chip surface-emphasis--magenta">%s</p>\n%s\n</div>'
                % (node.kind, _classes(FLAT_PANEL, node), word, body))
    if node.kind == "banner":
        inner = "\n".join(i[-1] for i in items)
        if re.search(r"<blockquote\b", inner):
            raise BuildError("line %d: %s holds a quotation; its rule would draw a second edge inside the banner's "
                             "ruled frame, so it sits outside the banner" % (node.line, _label(node)))
        if re.search(r"<h[1-6]\b", inner):
            raise BuildError("line %d: %s holds a heading; a banner carries its flag and title only" % (node.line, _label(node)))
        cls, flag = BANNERS[node.banner]
        body = _blocks_only(items, node, ("p", "ul", "ol", "pre", "hr"))
        accent = "cyan" if node.banner == "review-status" else "violet"
        out = ['<div class="%s %s">' % (cls, EMPHASIS_PANEL % accent),
               '<p class="%s__flag surface-emphasis-chip">%s</p>' % (cls, flag)]
        if node.title is not None:
            out.append('<p class="uo-proof__title doc-subsection-title">%s</p>' % _esc(node.title))
        out += ['<div class="%s__body doc-prose">\n%s\n</div>' % (cls, body), "</div>"]
        return "\n".join(out)
    if node.kind == "disclose":
        counts["disclosures"] += 1
        body = compose(items, '<div class="uo-details__body surface-disclosure-body doc-section">', "</div>")
        if node.disclose == "detail" and re.search(r'<(?:span|mark) class="[^"<>]*" data-review="(?:%s)"'
                                                   % "|".join(ASKING_ROLES), body):
            # What the reviewer is asked to judge stays visible (README, "What stays visible"): a closed detail holds
            # no request for a judgment, in a row, list, range, note, cell, item host or passage mark.
            raise BuildError("line %d: an Open question, Proposed or Correction requested review item sits inside %s, "
                             "which is closed: what the reviewer is asked to judge stays in the visible reading. A "
                             "detail's review items are Accepted, Declined or No decision recorded"
                             % (_asking_line(node), _label(node)))
        return ('<details data-uo-disclose="%s" class="%s"><summary><span class="surface-disclosure-label">%s</span>'
                '<span class="surface-disclosure-indicator" aria-hidden="true">&#9660;</span></summary>\n%s\n</details>') % (
            node.disclose, _classes("uo-details " + DISCLOSURE, node), _esc(node.summary), body)
    raise BuildError("internal: unexpected node %r" % node.kind)


# The review roles that ask for a judgment rather than record one: Open question, and Proposed (Correction requested
# shares its role). A guided review's detail disclosure holds none of them.
ASKING_ROLES = ("open", "proposed")
ASKING_SOURCE = re.compile(r"\{\{(?:review +(?:%s)|mark +(?:%s))\b" % (
    "|".join(w for w, (role, _) in REVIEW_WORDS.items() if role in ASKING_ROLES), "|".join(ASKING_ROLES)))


def _asking_line(node):
    """The first source line inside node that holds a review item or passage mark asking for a judgment."""
    for c in node.children:
        if isinstance(c, Text):
            for n, t in c.lines:
                if ASKING_SOURCE.search(CODE_SPAN.sub("", t)):
                    return n
        elif c.kind == "annotate" and c.items:
            for a, w, v, n in c.items:
                if a == "review" and REVIEW_WORDS[w][0] in ASKING_ROLES:
                    return n
        else:
            found = _asking_line(c)
            if found:
                return found
    return node.line if node.kind == "disclose" else None


def render_body(meta, root, seal_footer, mark):
    """Returns (body inner HTML, counts, part numbers in order). Each section carries its part's id, and
    the masthead's section index links to every section the document holds."""
    md = new_markdown()
    counts = {"questions": 0, "findings": 0, "disclosures": 0, "tables": 0, "quotations": 0, "callouts": 0,
              "framing": 0, "synthesis": 0, "structures": 0, "authored_case": 0, "annotation_rows": 0,
              "annotation_lists": 0, "annotation_notes": 0, "passage_marks": 0, "cell_items": 0,
              "annotation_ranges": 0, "item_hosts": 0, "document_records": 0}
    parts = [c for c in root.children if isinstance(c, Node) and c.kind == "part"]
    record = next((c for c in root.children if isinstance(c, Node) and c.kind == "annotate"), None)
    numbers = [p.number for p in parts]
    sections = []
    if "01" not in numbers:
        parts.insert(0, Node("part", 0))
        parts[0].number = "01"
    if "10" not in numbers:
        tail = Node("part", 0)
        tail.number = "10"
        parts.append(tail)
    index, seen = [], {}
    for p in parts:
        seen[p.number] = seen.get(p.number, 0) + 1
        k = seen[p.number]
        suffix = "" if k == 1 else "-%d" % k
        index.append(("uo-part-%s%s" % (p.number, suffix), "%s %s%s" % (p.number, PART_NAMES[p.number],
                                                                        "" if k == 1 else " %d" % k)))
    for p, (sid, _) in zip(parts, index):
        items = _items(md, p, counts)
        framing = [i for i, c in enumerate(p.children) if isinstance(c, Node) and (c.kind == "framing" or (
            c.kind == "range" and any(isinstance(k, Node) and k.kind == "framing" for k in c.children)))]
        if framing:
            before = [x for c in p.children[:framing[0]]
                      for x in (_text_items(md, c, _inline_context(p)) if isinstance(c, Text) and c.nonblank() else [])]
            if any(x[0] == "h" and x[1] > 2 for x in before):
                raise BuildError("line %d: a :::framing opens its part, before the part's first ### or #### section"
                                 % p.children[framing[0]].line)
        if p.number == "01":
            record_html = None
            if record is not None:
                counts["document_records"] += 1
                record_html = _render_annotations(record)
            items = [("c", _masthead(meta, mark, index, record_html))] + items
        if p.number == "10":
            items = items + [("c", seal_footer)]
        sections.append(compose(items, '<section data-uo-part="%s" id="%s" class="%s">' % (p.number, sid, _classes("doc-section", p)),
                                "</section>", title=True))
    return "\n\n".join(sections), counts, [p.number for p in parts]


def _masthead(meta, mark, index, record_html=None):
    """The status rail, and the masthead: the section index (the contents role inside the disclosure
    treatment, opened by the assigned wordmark), the document title, the document's own review record where the
    source gives one (:::annotate document: a row under the title, which draws no rail), and its identity."""
    rail_items = [meta["classification"], meta["audience"], meta["kind"], meta["round"]]
    rail = ['<span class="doc-label"><strong>%s</strong></span>' % _esc(rail_items[0])]
    for item in rail_items[1:]:
        rail.append('<span class="uo-status-rail__sep"></span><span class="doc-label">%s</span>' % _esc(item))
    dl = "".join('<dt class="doc-label">%s</dt><dd class="doc-meta">%s</dd>' % (k, _esc(meta[k])) for k in ("id", "kind", "round"))
    items = "".join('<li><a class="doc-toc-link surface-text-link" href="#%s">%s</a></li>' % (sid, _esc(label))
                    for sid, label in index)
    mark_slot = ('<details class="uo-index %s"><summary class="uo-index__mark"><span class="surface-disclosure-label">%s'
                 'sections</span><span class="surface-disclosure-indicator" aria-hidden="true">&#9660;</span></summary>\n'
                 '<nav class="uo-index__list surface-disclosure-body" aria-label="Sections"><ol class="doc-toc-list">%s</ol>'
                 '</nav>\n</details>' % (DISCLOSURE, mark, items))
    record = record_html + "\n" if record_html else ""
    return ('<div class="uo-status-rail">%s</div>\n'
            '<header class="uo-head doc-titled">\n%s\n<h1 class="doc-title">%s</h1>\n%s<dl class="uo-head__meta">%s</dl>\n'
            '</header>' % ("".join(rail), mark_slot, _esc(meta["title"]), record, dl))


def wordmark_svg(data):
    """The vendored wordmark as masthead chrome: its viewBox and path data unchanged, in the one svg the
    allowlist admits, in the mark slot. Anything but one svg of path elements, with a numeric viewBox and
    fill="currentColor", fails the build."""
    text = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", data.decode("utf-8"))
    m = re.fullmatch(r'<svg\b([^>]*)>\s*((?:<path d="[^"<>]*"\s*/>\s*)+)</svg>\s*', text)
    if not m:
        raise BuildError("the vendored wordmark _dsa-tokens/%s is not one svg of path elements" % WORDMARK)
    attr = r'\s+([A-Za-z_:][-A-Za-z0-9_:.]*)="([^"<>]*)"'
    pairs = re.findall(attr, m.group(1))
    names = [k for k, _ in pairs]
    if re.sub(attr, "", m.group(1)).strip() or len(set(names)) != len(names) \
            or not set(names) <= {"id", "xmlns", "viewBox", "fill"}:
        raise BuildError("the vendored wordmark _dsa-tokens/%s carries svg attributes other than id, xmlns, viewBox "
                         "and fill, each once" % WORDMARK)
    a = dict(pairs)
    if not re.fullmatch(r"[0-9. ]+", a.get("viewBox", "")) or a.get("fill") != "currentColor":
        raise BuildError("the vendored wordmark _dsa-tokens/%s lacks a numeric viewBox or fill=\"currentColor\"" % WORDMARK)
    paths = re.findall(r'<path d="([^"<>]*)"\s*/>', m.group(2))
    return ('<svg class="uo-mark" viewBox="%s" fill="currentColor" role="img" aria-label="ASK">%s</svg>'
            % (a["viewBox"], "".join('<path d="%s"/>' % d for d in paths)))


# ---------------------------------------------------------------------------
# Dependency bytes: verified against _dsa-tokens/MANIFEST.md before sealing

def _manifest_fields(path, label):
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except OSError as e:
        raise BuildError("%s manifest unreadable: %s" % (label, e))
    fields = {}
    for m in re.finditer(r"^\|\s*([^|`]+?)\s*\|\s*`([^`]*)`\s*\|\s*$", text, flags=re.M):
        if m.group(1) in fields:
            raise BuildError("%s manifest: field %r repeated" % (label, m.group(1)))
        fields[m.group(1)] = m.group(2)
    commit = fields.get("commit")
    if commit is None:
        raise BuildError("%s manifest: no commit row" % label)
    if not re.match(r"^[0-9a-f]{40}$", commit):
        raise BuildError("%s manifest: commit %r is not 40 lowercase hex" % (label, commit))
    if "short" in fields and fields["short"] != commit[:7]:
        raise BuildError("%s manifest: short %r is not the commit's first 7 characters" % (label, fields["short"]))
    return fields, commit


def _verified(directory, rel, fields, label):
    expected = fields.get("%s sha256" % rel)
    if expected is None:
        raise BuildError("%s manifest: no sha256 row for %s" % (label, rel))
    path = os.path.join(HERE, directory, *rel.split("/"))
    try:
        with open(path, "rb") as f:
            data = f.read()
    except OSError:
        raise BuildError("dependency file missing: %s/%s" % (directory, rel))
    actual = hashlib.sha256(data).hexdigest()
    if actual != expected:
        raise BuildError("dependency bytes do not match the manifest: %s/%s sha256 %s, manifest %s"
                         % (directory, rel, actual, expected))
    return {"path": "%s/%s" % (directory, rel), "bytes": len(data), "sha256": actual, "data": data}


def verify_dependencies():
    """Reads both vendored manifests and every vendored file, and verifies each
    file's sha256 over the bytes actually read. The two manifests must name the
    same design-system commit: the register is never sealed against a foundation
    from another design-system state. Returns the verified record, including those
    bytes, tokens first, then the fonts, the wordmark, the register modules in
    their sealed-use order and the three semantic-state modules in theirs. All
    seven _dsa-surface/ files are verified on every build, whether or not the
    document annotates. Any gap fails.

    Stated limit: this binds the embedded bytes to the committed manifests' hash
    rows. That a manifest's commit row names the design-system commit those bytes
    came from is established when the snapshot is re-synced and reviewed; the
    renderer has no design-system clone and does not re-check it."""
    fields, commit = _manifest_fields(MANIFEST, "dependency")
    sfields, scommit = _manifest_fields(SURFACE_MANIFEST, "register")
    if scommit != commit:
        raise BuildError("the register manifest's commit %s differs from the token manifest's %s; both snapshots are "
                         "re-synced together, at one design-system commit" % (scommit, commit))
    record = {"commit": commit, "short": commit[:7], "files": []}
    for rel in ["colors_and_type.css"] + ["fonts/" + fn for fn in FONTS] + [WORDMARK]:
        record["files"].append(_verified("_dsa-tokens", rel, fields, "dependency"))
    for rel in MODULES + STATE_MODULES:
        record["files"].append(_verified("_dsa-surface", rel, sfields, "register"))
    return record


def dependency(dep, path):
    return next(f for f in dep["files"] if f["path"] == path)


def inlined_modules(annotated):
    """The _dsa-surface/ modules a render inlines, in order: the four register modules, then, in a document that
    annotates, the three semantic-state modules (design-system-ASK review-semantics.md, "How to use it")."""
    return MODULES + (STATE_MODULES if annotated else [])


def seal_tokens(dep, annotated=False):
    """The token CSS with its fonts embedded as data: URIs, then each inlined module verbatim, in the owner's
    sealed-use order."""
    css = dependency(dep, "_dsa-tokens/colors_and_type.css")["data"].decode("utf-8")
    for fn in FONTS:
        uri = "data:font/woff2;base64," + base64.b64encode(dependency(dep, "_dsa-tokens/fonts/" + fn)["data"]).decode("ascii")
        pattern = r"src:[^;]*fonts/" + re.escape(fn) + r"[^;]*;"
        css, n = re.subn(pattern, lambda _m: "src: url('" + uri + "') format('woff2');", css, flags=re.S)
        if n != 1:
            raise BuildError("expected exactly 1 src match for %s, got %d" % (fn, n))
    if re.findall(r"url\('fonts/[^']+'\)", css):
        raise BuildError("un-inlined font url() remain")
    out = ["/* === SEALED design-system-ASK tokens (upstream %s per the vendored manifest; file bytes verified "
           "against its sha256 rows) + base64 fonts === */\n%s" % (dep["short"], css)]
    for rel in inlined_modules(annotated):
        manifest = "the register manifest" if rel in MODULES else "the _dsa-surface manifest"
        out.append("/* === SEALED design-system-ASK %s (upstream %s, verbatim; bytes verified against %s) === */\n%s"
                   % (rel, dep["short"], manifest, dependency(dep, "_dsa-surface/" + rel)["data"].decode("utf-8")))
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Payload-local CSS

def load_local_css(path, used_names):
    try:
        with open(path, "rb") as f:
            raw = f.read()
    except OSError as e:
        raise BuildError("--local-css unreadable: %s" % e)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise BuildError("--local-css is not UTF-8")
    if "/*" in text or "*/" in text:
        raise BuildError("--local-css: comments are not allowed ('/*' or '*/'); the file is embedded byte for byte")
    css = text
    if "@" in css:
        raise BuildError("--local-css: at-rules are not allowed (found '@')")
    if re.search(r"url\(", css, flags=re.I):
        raise BuildError("--local-css: url( is not allowed")
    if "</" in css:
        raise BuildError("--local-css: '</' is not allowed")
    if "\\" in css:
        raise BuildError("--local-css: backslash escapes are not allowed")
    if re.search(r"!\s*important", css, flags=re.I):
        raise BuildError("--local-css: !important is not allowed")
    m = RESOURCE_FUNCTION.search(css)
    if m:
        raise BuildError("--local-css: %s( is not allowed (it can load a resource)" % m.group(1))
    referenced = set()
    chunks = css.split("}")
    if chunks[-1].strip():
        raise BuildError("--local-css: text after the last rule")
    for chunk in chunks[:-1]:
        if chunk.count("{") != 1:
            raise BuildError("--local-css: malformed or nested rule near %r" % chunk.strip()[:60])
        selectors, decls = chunk.split("{")
        if re.search(r"(^|;)\s*--", decls):
            raise BuildError("--local-css: custom property declarations are not allowed")
        _check_declaration_strings(decls)
        for sel in _split_selectors(selectors):
            sel = " ".join(sel.split())
            if _top_level_chars(sel) & set("~+|"):
                raise BuildError("--local-css: selector %r uses a sibling or column combinator; it would style "
                                 "elements outside the scoped container" % sel)
            m = re.match(r"^main\.uo-md \.uo-local-([a-z][a-z0-9-]{0,31})(?![a-z0-9-])", sel)
            if not m:
                raise BuildError("--local-css: selector %r is not scoped under 'main.uo-md .uo-local-<name>'" % sel)
            rest = sel[m.end():]
            if re.search(r"(?<![A-Za-z0-9_-])uo-(?!local-)", rest, flags=re.I):
                raise BuildError("--local-css: selector %r names a renderer hook; it may name only its uo-local-<name> scope" % sel)
            if re.search(r"\[\s*(?:[\w*-]*\|)?\s*class\b", rest, flags=re.I):
                raise BuildError("--local-css: selector %r selects by the class attribute; after its scope it may not" % sel)
            referenced.add(m.group(1))
    unused = sorted(referenced - set(used_names))
    if unused:
        raise BuildError("--local-css: scope names not used by the source: %s" % ", ".join(unused))
    return raw, css


def _check_declaration_strings(decls):
    """Fails on an unterminated string, or a quoted string inside any function
    argument list, where it could name a resource."""
    depth, quote = 0, None
    for ch in decls:
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            if depth > 0:
                raise BuildError("--local-css: a quoted string inside a function is not allowed")
            quote = ch
        elif ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
    if quote:
        raise BuildError("--local-css: unterminated string")


def _top_level_chars(selector):
    """Characters of a selector outside [attribute] brackets and (arguments). Only
    called on a selector _split_selectors accepted: no quotes, balanced depth."""
    out, depth = set(), 0
    for ch in selector:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        elif depth == 0:
            out.add(ch)
    return out


def _split_selectors(selectors):
    """Splits a selector list at top-level commas. A quote character anywhere in
    the prelude fails (backslash and comments are refused for the whole file),
    so every bracket and parenthesis is structural; depth that goes negative or
    ends non-zero fails."""
    if '"' in selectors or "'" in selectors:
        raise BuildError("--local-css: a quote character in a selector is not allowed (write an attribute value "
                         "unquoted): %r" % " ".join(selectors.split()))
    out, depth, cur = [], 0, []
    for ch in selectors:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
            if depth < 0:
                break
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    if depth != 0:
        raise BuildError("--local-css: unbalanced brackets or parentheses in selector %r" % " ".join(selectors.split()))
    out.append("".join(cur))
    if any(not s.strip() for s in out):
        raise BuildError("--local-css: empty selector")
    return out


def _local_names(node, acc):
    for c in node.children:
        if isinstance(c, Node):
            if c.local:
                acc.add(c.local)
            _local_names(c, acc)
    return acc


# ---------------------------------------------------------------------------
# Final-HTML allowlist

def _class_set(v):
    return frozenset((v or "").split())


COMPOSITION = frozenset(("doc-annotations", "doc-annotation-item", "doc-annotation-list", "doc-annotation-note", "doc-mark",
                         "doc-annotation-range"))
RANGE_DIV_SET = _class_set(RANGE_DIV)
RANGE_LI_SET = _class_set(RANGE_CLASS)
FLAT_PANEL_SET = _class_set(FLAT_PANEL)
PROMPT_ERROR = ("a review row outside a range is an explicit-target prompt, immediately before the range whose content it "
                "asks about")


class _Allowlist(HTMLParser):
    def __init__(self, n_styles):
        super().__init__(convert_charrefs=True)
        self.errors = []
        self.stack = []           # (tag, frozenset of class tokens)
        self.counts = {}
        self.class_counts = {}    # (tag, class token) -> count
        self.n_styles = n_styles
        self.styles = []
        self.in_style = False
        self.h1_ok = 0
        self.tables = []          # per open <table>: header labels, current column, header text being read, dense
        self.ids = set()          # section ids
        self.id_order = []        # section ids, in document order
        self.index_hrefs = []     # the section index's link targets, in order; checked against id_order
        self.part = None          # the open section's part
        self.note_ids = []        # annotation notes' ids, in document order
        self.described = []       # passage marks' aria-describedby targets, in document order
        self.words = []           # open annotation words being read: a mark's label, a key, a list key, a passage mark
        self.groups = []          # open annotation items and lists: the kinds of their direct children
        self.passages = []        # (data-review, aria-describedby) of every passage mark
        self.note = None          # the open named note: its id, depth, first row and the review roles that row records
        self.note_roles = {}      # a named note's id -> the review roles its first row records
        self.rows = []            # open annotation rows (div): depth, place, the axis each item names, review items
        self.ranges = []          # open annotation ranges (div or li): depth, tag, direct children seen, row open
        self.prompt = None        # the depth where a review row outside a range waits for the range it precedes
        self.record = None        # the depth of the document's record row while it is open
        self.head_kids = []       # the masthead's direct children, in order

    def err(self, msg):
        self.errors.append("%s (output line %d)" % (msg, self.getpos()[0]))

    def tags(self):
        return [t for t, _ in self.stack]

    def top(self, n=1):
        return self.stack[-n] if len(self.stack) >= n else (None, frozenset())

    def within(self, tag, cls):
        return any(t == tag and cls in c for t, c in self.stack)

    def handle_decl(self, decl):
        if decl.lower() != "doctype html":
            self.err("declaration %r not allowed" % decl)

    def unknown_decl(self, data):
        self.err("declaration not allowed")

    def handle_pi(self, data):
        self.err("processing instruction not allowed")

    def handle_comment(self, data):
        self.err("HTML comment not allowed in output")

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_starttag(self, tag, attrs):
        tags = self.tags()
        parent = tags[-1] if tags else None
        self.counts[tag] = self.counts.get(tag, 0) + 1
        a = {}
        for k, v in attrs:
            if k in a:
                self.err("<%s> repeats attribute %s" % (tag, k))
            a[k] = v if v is not None else ""
        cls = _class_set(a.get("class"))
        for c in cls:
            self.class_counts[(tag, c)] = self.class_counts.get((tag, c), 0) + 1
        if tag == "html":
            if parent is not None or set(a) != {"lang"}:
                self.err("<html> must be the root and carry lang only (got %s)" % sorted(a))
        elif tag in ("head", "body"):
            if parent != "html" or a:
                self.err("<%s> must sit directly in <html> with no attributes" % tag)
        elif "head" in tags:
            if tag not in HEAD_ELEMENTS or parent != "head":
                self.err("<%s> not allowed in <head>" % tag)
            elif tag == "meta":
                if not (set(a) == {"charset"} or (set(a) == {"name", "content"} and a["name"] == "viewport")):
                    self.err("<meta> must be charset or name=viewport content")
            elif a:
                self.err("<%s> in <head> takes no attributes" % tag)
        elif "body" in tags:
            if tag not in BODY_ELEMENTS:
                self.err("element <%s> not allowed" % tag)
            self._check_attrs(tag, a, parent)
            if "class" not in a:
                self._check_class(tag, None, parent)
            self._prompt_sibling(tag, cls)
            self._check_place(tag, cls, a)
            self._track_annotation_start(tag, cls, a)
        else:
            self.err("<%s> outside head and body" % tag)
        if tag == "h1":
            if self.top()[0] == "header" and "uo-head" in self.top()[1]:
                self.h1_ok += 1
            else:
                self.err("<h1> is the renderer's masthead title only; authored headings use ## to ####")
        if tag == "style":
            self.in_style = True
            self.styles.append("")
        if "body" in tags:
            self._track_table_start(tag, a, cls)
        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, cls))

    def handle_endtag(self, tag):
        if tag in VOID_ELEMENTS:
            return
        tags = self.tags()
        if not tags or tags[-1] != tag:
            self.err("unbalanced </%s> (open: %s)" % (tag, "/".join(tags)))
            if tag not in tags:
                return
            while self.stack and self.stack[-1][0] != tag:
                self.stack.pop()
        self.stack.pop()
        self._track_annotation_end(tag)
        if self.prompt is not None and len(self.stack) < self.prompt:
            self.err(PROMPT_ERROR)
            self.prompt = None
        if tag == "style":
            self.in_style = False
        if (self.tables and tag == "span" and self.tables[-1]["label"] is not None
                and len(self.stack) == self.tables[-1]["label"]["depth"]):
            lab = self.tables[-1]["label"]
            self.tables[-1]["label"] = None
            if cell_label(lab["text"]) != lab["expected"]:
                self.err("<span class=\'uo-cell-label\'> text %r does not equal its column's header text %r"
                         % (cell_label(lab["text"]), lab["expected"]))
        if self.tables and tag == "td" and self.tables[-1]["td"] in self.tables[-1]["cased"] \
                and not self.tables[-1]["label_cased"]:
            self.err("a cell label in an authored-case column lacks its authored-case span")
        if self.tables and tag == "td" and not self.tables[-1].get("cell_seen_label", True):
            self.err("<td> without its <span class='uo-cell-label'>: the visible narrow-width label "
                     "is the operable header representation and may not be dropped")
        if self.tables and tag == "th" and self.tables[-1]["text"] is not None:
            self.tables[-1]["labels"].append(cell_label(self.tables[-1]["text"]))
            self.tables[-1]["text"] = None
        if tag == "table" and self.tables:
            self.tables.pop()

    def handle_data(self, data):
        if self.stack and self.stack[-1][0] in ("svg", "path") and data.strip():
            self.err("text inside the wordmark")
        for w in self.words:
            w["text"] += data
        top_tag, top_cls = self.top()
        if data.strip() and (top_cls & {"doc-annotations", "doc-annotation-item", "doc-annotation-list", "doc-annotation-note",
                                        "doc-annotation-range"} or (top_tag == "dd" and not top_cls)):
            self.err("annotation text sits in a mark, a key or a metadata span, not directly in <%s>" % top_tag)
        if self.in_style:
            self.styles[-1] += data
        if self.tables and self.tables[-1]["text"] is not None:
            self.tables[-1]["text"] += data
        if self.tables and self.tables[-1]["label"] is not None:
            self.tables[-1]["label"]["text"] += data

    def _track_table_start(self, tag, a, cls):
        """Every body cell carries data-uo-label equal to its column's header text."""
        if tag == "table":
            self.tables.append({"labels": [], "column": 0, "text": None, "label": None,
                                "cell_seen_label": True, "dense": "doc-dense-table" in cls,
                                "cased": set(), "th": None, "td": None, "label_cased": False})
            return
        if not self.tables:
            return
        t = self.tables[-1]
        if tag == "tr":
            t["column"] = 0
        elif tag == "th":
            if "thead" in self.tags():
                t["text"] = ""
            t["th"] = t["column"]
            t["column"] += 1
        elif tag == "td":
            column = t["column"]
            t["column"] += 1
            t["td"], t["label_cased"] = column, False
            expected = t["labels"][column] if column < len(t["labels"]) else None
            t["cell_seen_label"] = False
            if "data-uo-label" not in a:
                self.err("<td> without data-uo-label")
            elif a["data-uo-label"] != expected:
                self.err("<td data-uo-label=%r> does not equal its column's header text %r" % (a["data-uo-label"], expected))
        elif tag == "span" and "uo-authored-case" in cls:
            parent_tag, parent_cls = self.top()
            if parent_tag == "th":
                t["cased"].add(t["th"])
            elif "uo-cell-label" in parent_cls:
                t["label_cased"] = True
                if t["td"] not in t["cased"]:
                    self.err("an authored-case cell label in a column whose header is not authored-case")
        elif tag == "span" and "uo-cell-label" in cls and t["label"] is None:
            t["cell_seen_label"] = True
            t["label"] = {"text": "", "depth": len(self.stack),
                          "expected": t["labels"][t["column"] - 1] if 0 < t["column"] <= len(t["labels"]) else None}

    # The words each annotation key may show, and the order of an annotation list's keys.
    ITEM_SHAPES = (("mark",), ("mark", "meta"), ("key", "meta"))
    LIST_KEYS = tuple(AXIS_KEYS[a] for a in ("item",) + ANNOTATION_AXES)

    def _prompt_sibling(self, tag, cls):
        """The element after a review row outside a range: the range the row asks about, or another prompt to it."""
        if self.prompt is None or len(self.stack) != self.prompt:
            return
        if tag == "div" and cls == RANGE_DIV_SET:
            self.prompt = None
        elif not (tag == "div" and cls == {"doc-annotations"}):
            self.err(PROMPT_ERROR)
            self.prompt = None

    def _track_annotation_start(self, tag, cls, a):
        """Reads an annotation's words and its items' and lists' shapes: a mark shows its role's words, an item is
        a mark, a mark and its metadata, or a key and its value, and a list keys each axis once, in order. Reads each
        row's items and each range's opening row."""
        depth = len(self.stack)
        top_tag, top_cls = self.top()
        if self.groups and depth == self.groups[-1]["depth"] + 1:
            kind = (tag if tag in ("dt", "dd") else "mark" if "doc-mark" in cls else "key" if cls == {"doc-label"}
                    else "meta" if cls == {"doc-meta"} else "other")
            self.groups[-1]["children"].append(kind)
        if tag == "span" and "doc-annotation-item" in cls or tag == "dl" and "doc-annotation-list" in cls:
            self.groups.append({"tag": tag, "depth": depth, "children": [], "keys": []})
        if self.note and depth == self.note["depth"] + 1 and not self.note["children"]:
            # a note's first child element is its row
            self.note["children"] = True
            if tag == "div" and cls == {"doc-annotations"}:
                self.note.update(row=depth, row_open=True)
            else:
                self.err("an annotation note holds its row first, not <%s>" % tag)
        if tag == "div" and cls in ({"doc-hierarchy", "doc-group", "doc-annotation-note"}, {"doc-group", "doc-annotation-note"}):
            self.note = {"id": a.get("id"), "nyt": "doc-hierarchy" not in cls, "depth": depth, "children": False, "row": None,
                         "row_open": False, "roles": set(), "nyt_mark": False}
        elif tag == "span" and "doc-mark" in cls and self.note and self.note["row_open"]:
            if "data-review" in a:
                self.note["roles"].add(a["data-review"])
            if a.get("data-evidence") == NYT_NOTE:
                self.note["nyt_mark"] = True
        if (tag == "div" and cls == RANGE_DIV_SET) or (tag == "li" and cls == RANGE_LI_SET):
            self.ranges.append({"depth": depth, "tag": tag, "kids": 0, "row_open": False})
        if tag == "div" and cls == {"doc-annotations"}:
            r = self.ranges[-1] if self.ranges else None
            place = ("record" if top_tag == "header" else "note" if "doc-annotation-note" in top_cls
                     else "range" if r is not None and depth == r["depth"] + 1 and r["kids"] == 1 else "section")
            if place == "range":
                r["row_open"] = True
            if place == "record":
                self.record = depth
            self.rows.append({"depth": depth, "place": place, "axes": [], "reviews": 0})
        if self.rows and tag == "span" and "doc-annotation-item" in cls and depth == self.rows[-1]["depth"] + 1:
            self.rows[-1]["axes"].append("key")
        if tag == "span" and "doc-mark" in cls:
            facets = [k[5:] for k in FACET_VALUES if k in a]
            if self.rows and depth == self.rows[-1]["depth"] + 2 and self.rows[-1]["axes"] and facets:
                self.rows[-1]["axes"][-1] = facets[0]
                self.rows[-1]["reviews"] += facets[0] == "review"
            if "data-review" in a and self.ranges and not self.ranges[-1]["row_open"]:
                self.err("an annotation range carries one judgment: no review mark sits inside it but the one its row "
                         "names (blocks judged otherwise are a sibling range; a table whose cells carry review items "
                         "takes no range)")
            if top_tag == "dd" and self.groups and self.groups[-1]["tag"] == "dl" and self.groups[-1]["keys"][-1:] == ["Item"]:
                self.err("an annotation list's Item line holds the name of the item it judges, as metadata only")
        if tag == "mark":
            self.passages.append((a.get("data-review"), a.get("aria-describedby")))
        expected = None
        if tag == "mark":
            expected = ()                     # any words: a passage mark is never empty
        elif tag == "span" and "doc-mark" in cls:
            facets = [(k, a[k]) for k in FACET_VALUES if k in a]
            expected = MARK_LABELS.get(facets[0], set()) if len(facets) == 1 else set()
        elif tag == "span" and cls == {"doc-label"} and top_cls & {"doc-annotation-item"}:
            expected = {AXIS_KEYS["basis"], AXIS_KEYS["check"]}
        elif tag == "dt" and "doc-annotation-list" in top_cls:
            expected = set(self.LIST_KEYS)
        if expected is not None:
            self.words.append({"tag": tag, "depth": depth, "text": "", "expected": expected,
                               "list": self.groups[-1] if tag == "dt" else None})

    def _track_annotation_end(self, tag):
        depth = len(self.stack)
        if self.note and tag == "div" and depth == self.note["row"]:
            self.note["row_open"] = False
        if self.note and tag == "div" and depth == self.note["depth"]:
            if self.note["row"] is None and not self.note["children"]:
                self.err("an annotation note holds its row first; this one holds nothing")
            if self.note["nyt"] and not self.note["nyt_mark"]:
                self.err("a not-yet-testable note's row carries a Not yet testable evidence mark")
            if not self.note["nyt"]:
                self.note_roles[self.note["id"]] = self.note["roles"]
            self.note = None
        if self.rows and tag == "div" and depth == self.rows[-1]["depth"]:
            row = self.rows.pop()
            lead = row["axes"][:1] == ["review"]
            if row["place"] == "range":
                self.ranges[-1]["row_open"] = False
                if row["reviews"] != 1 or not lead:
                    self.err("an annotation range opens with its row, which names its one review judgment first")
            elif row["place"] == "record":
                self.record = None
            elif row["place"] == "section":
                if row["reviews"]:
                    if row["reviews"] != 1 or not lead:
                        self.err("a review row outside a range is an explicit-target prompt: it names one review "
                                 "judgment, first")
                    self.prompt = row["depth"]
                elif self.prompt == row["depth"]:
                    self.err(PROMPT_ERROR)
                    self.prompt = None
        if self.ranges and tag == self.ranges[-1]["tag"] and depth == self.ranges[-1]["depth"]:
            if self.ranges.pop()["kids"] < 2:
                self.err("an annotation range covers at least one block after its row")
        if self.words and self.words[-1]["depth"] == depth and self.words[-1]["tag"] == tag and self.words[-1]["expected"] == ():
            if not has_visible_text(self.words.pop()["text"]):
                self.err("a passage mark shows the words it marks; it is never empty")
        elif self.words and self.words[-1]["depth"] == depth and self.words[-1]["tag"] == tag:
            w = self.words.pop()
            if w["text"] not in w["expected"]:
                self.err("annotation words %r are not their role's or key's words (%s)"
                         % (w["text"], " or ".join(sorted(w["expected"])) or "no valid facet"))
            if w["list"] is not None:
                w["list"]["keys"].append(w["text"])
        if self.groups and self.groups[-1]["depth"] == depth and self.groups[-1]["tag"] == tag:
            g = self.groups.pop()
            if tag == "span" and tuple(g["children"]) not in self.ITEM_SHAPES:
                self.err("an annotation item is a mark, a mark and its metadata, or a key and its value (got %s)"
                         % " ".join(g["children"]))
            if tag == "dl":
                pairs = g["children"]
                ranks = [self.LIST_KEYS.index(k) if k in self.LIST_KEYS else -1 for k in g["keys"]]
                if not pairs or pairs != ["dt", "dd"] * (len(pairs) // 2) or any(b <= a for a, b in zip(ranks, ranks[1:])):
                    self.err("an annotation list keys each axis once, in order, each key followed by its value")
                if "Review" in g["keys"] and g["keys"][:1] != ["Item"]:
                    self.err("an annotation list with a Review line names the item it judges first, in an Item line")

    def _check_place(self, tag, cls, a):
        """Where each emitted element may sit: the masthead's mark slot and wordmark, the contents list, the
        banners, table cells, the structured block, and the unclassed elements."""
        top_tag, top_cls = self.top()

        def need(ok, msg):
            if not ok:
                self.err(msg)
        if tag == "details" and "uo-index" in cls:
            need(top_tag == "header" and "uo-head" in top_cls, "<details class='uo-index'> is the masthead's section index only")
        if tag == "summary" and "uo-index__mark" in cls:
            need(top_tag == "details" and "uo-index" in top_cls, "<summary class='uo-index__mark'> sits only in the section index")
        if tag == "summary" and not cls:
            need(top_tag == "details" and "uo-details" in top_cls, "an unclassed <summary> is an authored disclosure's only")
        if tag == "nav":
            need(top_tag == "details" and "uo-index" in top_cls, "<nav> is the section index's list only")
        if tag == "span" and cls & {"surface-disclosure-label", "surface-disclosure-indicator"}:
            need(top_tag == "summary", "a disclosure's label and indicator sit only directly in its <summary>")
        if tag == "svg":
            need(top_tag == "span" and "surface-disclosure-label" in top_cls and self.top(2)[0] == "summary"
                 and "uo-index__mark" in self.top(2)[1], "<svg> is the masthead's wordmark only, in the mark slot")
        if self.top()[0] == "svg" and tag != "path":
            self.err("the wordmark holds path elements only")
        if tag == "path" and top_tag != "svg":
            self.err("<path> outside the wordmark")
        if top_tag == "path":
            self.err("<path> holds nothing")
        for banner, _ in BANNERS.values():
            if tag == "div" and banner in cls:
                need(top_tag == "section" and self.part == "01", "<div class='%s'> sits only directly in part 01" % banner)
            for c in (banner + "__flag", banner + "__body", banner + "__title"):
                if c in cls:
                    need(top_tag == "div" and banner in top_cls, "class '%s' sits only directly in its <div class='%s'>"
                         % (c, banner))
        if tag == "div" and "uo-details__body" in cls:
            need(top_tag == "details", "class 'uo-details__body' allowed only on a <div> directly inside <details>")
        if tag == "span" and "uo-cell-label" in cls:
            need(top_tag == "td", "class 'uo-cell-label' allowed only on a <span> directly inside <td>")
        if tag == "span" and "uo-authored-case" in cls:
            need(top_tag == "th" or (top_tag == "span" and "uo-cell-label" in top_cls),
                 "class 'uo-authored-case' allowed only directly in a header cell or in a cell's label")
        if any("uo-authored-case" in c for _, c in self.stack) and tag not in ("strong", "em"):
            self.err("an authored-case header holds text and inline emphasis only, not <%s>" % tag)
        if tag == "span" and cls == {"doc-label"}:
            need(top_tag == "div" and "uo-status-rail" in top_cls or top_tag == "span" and "doc-annotation-item" in top_cls,
                 "a status-rail item sits only in the status rail; an annotation key only in its item")
        if tag == "span" and "uo-status-rail__sep" in cls:
            need(top_tag == "div" and "uo-status-rail" in top_cls, "a status-rail item sits only in the status rail")
        if tag in ("div", "header") and cls & {"uo-status-rail", "uo-head"}:
            need(top_tag == "section" and self.part == "01", "the status rail and the masthead sit only in part 01")
        if tag == "dt" or tag == "dd" and cls:
            need(top_tag == "dl" and ("uo-head__meta" in top_cls or tag == "dt" and "doc-annotation-list" in top_cls),
                 "<%s> sits only in the masthead's identity list or an annotation list" % tag)
        if tag == "dd" and not cls:
            need(top_tag == "dl" and "doc-annotation-list" in top_cls, "an unclassed <dd> is an annotation list's value only")
        self._check_annotation_place(tag, cls, top_tag, top_cls, need)
        if tag == "ol" and "doc-toc-list" in cls:
            need(top_tag == "nav", "the contents list sits only in the section index")
        if tag == "li":
            in_toc = top_tag == "ol" and "doc-toc-list" in top_cls
            need(in_toc == (not cls), "a contents entry is an unclassed <li> in the contents list; every other <li> is document body")
        if tag == "a" and "doc-toc-link" in cls:
            need(top_tag == "li" and self.top(2)[0] == "ol" and "doc-toc-list" in self.top(2)[1],
                 "a contents link sits only in a contents entry")
        if tag == "a" and self.within("ol", "doc-toc-list"):
            need("doc-toc-link" in cls, "every link in the contents list is a contents link")
        if tag == "p" and not cls:
            need(top_tag == "blockquote", "an unclassed <p> is a quotation's paragraph only")
        if tag == "p" and "doc-body" in cls:
            need(top_tag != "blockquote", "a quotation's paragraph takes the quotation's rule, not document body")
        if tag == "p" and "surface-emphasis--magenta" in cls:
            need(top_tag == "div" and frozenset(FLAT_PANEL.split()) <= top_cls, "a framing or synthesis chip sits only in its panel")
        if tag == "footer":
            if cls:
                need(top_tag == "section" and self.part == "10", "the seal line sits only in part 10")
            else:
                need(top_tag == "blockquote", "an unclassed <footer> is a quotation's attribution only")
        if tag in ("td", "th") and self.tables:
            if tag == "td":
                need(("doc-table-cell" in cls) == self.tables[-1]["dense"],
                     "a dense table's cell is .doc-table-cell and a narrative table's is .doc-body")
        if tag == "pre" and "doc-pre-part" in cls:
            need(top_tag == "div" and top_cls & {"doc-pre--structured", "doc-hierarchy", "doc-pre-group"}
                 and self.within("div", "doc-pre--structured"), "a structured line sits only in a structured block")
        if tag == "div" and cls & {"doc-hierarchy", "doc-pre-group"} and "doc-annotation-note" not in cls:
            need(self.within("div", "doc-pre--structured"), "a hierarchy rail or peer group sits only in a structured block")
        if tag == "div" and "doc-pre-group" in cls:
            need(top_tag == "div" and "doc-pre--structured" in top_cls, "a peer group sits directly in its structured block")
        if tag == "code":
            need("pre" not in self.tags(), "a preformatted block carries its text directly")
        if tag == "section":
            need(top_tag == "main", "a part's <section> sits directly in <main>")
        if top_tag == "header" and "uo-head" in top_cls:
            self.head_kids.append(tag)

    def _check_annotation_place(self, tag, cls, top_tag, top_cls, need):
        """Review annotations (README, "Review annotations"): none in part 01 or 10 (a provenance disclosure is in
        10) but the document's record, directly under the masthead title; a row directly in a section, first in a note
        or a range, or as that record; a list, a range or a note directly in a section, a note also in a plain list
        item; an item host as an item of a top-level list; no range or note inside a range; a cell's row directly in
        its cell, an item only in a row, a mark or metadata only in an item or a list's value, words as text only, and
        a passage mark in document body text only, holding its words and any link inside them."""
        record = self.record is not None or (tag == "div" and cls == {"doc-annotations"} and top_tag == "header"
                                             and "uo-head" in top_cls)
        if self.part in CHROME_PARTS and (tag == "mark" or cls & COMPOSITION) and not record:
            self.err("no annotation sits in part 01 or 10 or in a provenance disclosure (<%s class='%s'>)"
                     % (tag, " ".join(sorted(cls))))
        if top_tag == "span" and ("doc-mark" in top_cls or top_cls == {"doc-meta"} or top_cls == {"doc-label"}
                                  and "doc-annotation-item" in self.top(2)[1]):
            self.err("an annotation's words are text only, not <%s>" % tag)
        section = top_tag in ("section", "div") and "doc-section" in top_cls
        r = self.ranges[-1] if self.ranges else None
        kid = None
        if r is not None and len(self.stack) == r["depth"] + 1:
            kid = r["kids"]
            r["kids"] += 1
            if kid == 0:
                need(tag == "div" and cls == {"doc-annotations"}, "an annotation range opens with its annotation row")
            elif r["tag"] == "li":
                need(tag == "p" and cls == {"doc-body"} or kid > 1 and tag in ("ul", "ol") and not cls,
                     "an item host holds its row, then its words in a p.doc-body, then only further paragraphs or a "
                     "nested list")
            else:
                need(tag == "div" and cls in ({"doc-prose"}, FLAT_PANEL_SET),
                     "an annotation range holds its row, then the blocks it covers in prose runs, and a panel")
        if tag == "div" and "doc-annotations" in cls:
            if top_tag == "header":
                need(self.head_kids[-1:] == ["h1"] and "div" not in self.head_kids,
                     "the document's review record sits once, directly under the masthead title")
            else:
                need(section or top_tag == "div" and "doc-annotation-note" in top_cls or kid == 0,
                     "an annotation row sits directly in a section, first in a note or a range, or under the masthead "
                     "title as the document's record")
        if tag == "dl" and "doc-annotation-list" in cls:
            need(section, "an annotation list sits directly in a section")
        if tag == "div" and "doc-annotation-note" in cls:
            need(section or top_tag == "li" and top_cls == {"doc-body"},
                 "an annotation note sits directly in a section, or in a plain list item after its text")
            need(not self.ranges, "an annotation note never sits inside an annotation range: it follows the range")
        if tag == "div" and "doc-annotation-range" in cls:
            need(section, "an annotation range sits directly in a section")
            need(not self.ranges, "annotation ranges never nest")
        if tag == "li" and "doc-annotation-range" in cls:
            need(top_tag in ("ul", "ol") and not top_cls and not self.ranges and "li" not in self.tags(),
                 "an item host is an item of a top-level list in the flow, never inside another list item or a range")
        if tag == "span" and "doc-annotations" in cls:
            need(top_tag == "td", "a cell's annotation row sits directly in its table cell")
        if tag == "span" and "doc-annotation-item" in cls:
            need(top_tag in ("div", "span") and "doc-annotations" in top_cls, "an annotation item sits only in an annotation row")
        if tag == "span" and ("doc-mark" in cls or cls == {"doc-meta"}):
            need(top_tag == "span" and "doc-annotation-item" in top_cls or top_tag == "dd" and not top_cls,
                 "a mark or its metadata sits only in an annotation item or an annotation list's value")
        if top_tag == "mark":
            need(tag == "a" and cls == {"surface-text-link"},
                 "a passage mark holds its words as text, and a link inside them, only")
        if top_tag == "a" and self.top(2)[0] == "mark":
            self.err("a link inside marked words holds plain text only, not <%s>" % tag)
        if tag == "mark":
            host = next(((t, c) for t, c in reversed(self.stack) if t not in ("strong", "em")), (None, frozenset()))
            need(host[0] in ("p", "li") and host[1] == {"doc-body"} and self.part not in CHROME_PARTS
                 and not any(t in ("blockquote", "table") or c & {"surface-emphasis-rail", "surface-separate",
                                                                  "doc-annotation-note"} for t, c in self.stack),
                 "a passage mark sits in document body text: a paragraph or list item outside a quotation, callout, "
                 "panel, banner, note or table")

    def _check_attrs(self, tag, a, parent):
        for k, v in a.items():
            if k == "href" and tag == "a":
                if v.startswith("#") and any(t == "nav" and "uo-index__list" in c for t, c in self.stack):
                    # the renderer's section index; authored Markdown cannot reach a nav
                    if SECTION_ID.match(v[1:]):
                        self.index_hrefs.append(v[1:])
                    else:
                        self.err("<a href=%r>: a section-index link names a section id, #uo-part-NN" % v)
                elif not re.match(r"^https?://", v):
                    self.err("<a href=%r>: only https:// and http:// links are allowed" % v)
            elif k == "id" and tag == "section":
                pass                  # checked below against the section's part
            elif k in ("viewbox", "fill", "role", "aria-label") and tag == "svg":
                pass                  # checked below
            elif k == "d" and tag == "path":
                pass
            elif k == "aria-label" and tag == "nav":
                pass
            elif k == "aria-hidden" and tag == "span" and v == "true" and "surface-disclosure-indicator" in _class_set(a.get("class")):
                pass
            elif k == "title" and tag == "a":
                pass
            elif k == "start" and tag == "ol":
                if not re.match(r"^[0-9]{1,6}$", v):
                    self.err("<ol start=%r> must be a number" % v)
            elif k in DATA_VALUES and v in DATA_VALUES[k] and (tag, k) in (
                    ("section", "data-uo-part"), ("div", "data-uo-role"), ("details", "data-uo-disclose"),
                    ("th", "data-uo-cell"), ("td", "data-uo-cell"), ("pre", "data-lead-lines"), ("div", "data-lead-lines")):
                pass
            elif k == "data-uo-role" and tag == "p" and v == "callout":
                pass
            elif k == "data-uo-central" and tag == "div" and v == "true" and a.get("data-uo-role") == "question":
                pass
            elif k == "data-uo-label" and tag == "td":
                pass                  # value checked against the column's header text (_track_table_start)
            elif k in FACET_VALUES and tag in ("span", "mark", "div") or k == "aria-describedby" and tag == "mark" \
                    or k == "id" and tag == "div":
                pass                  # an annotation's attributes: checked below (_check_annotation_attrs)
            elif k == "class":
                self._check_class(tag, v, parent)
            else:
                self.err("attribute %s=%r not allowed on <%s>" % (k, v, tag))
        if tag in ("th", "td") and "data-uo-cell" not in a:
            self.err("<%s> without a table role" % tag)
        if tag == "section" and "data-uo-part" not in a:
            self.err("<section> without data-uo-part")
        if tag == "section":
            sid = a.get("id")
            if sid is None:
                self.err("<section> without its id")
            elif not SECTION_ID.match(sid) or sid[8:10] != a.get("data-uo-part"):
                self.err("<section id=%r> does not name its part %r" % (sid, a.get("data-uo-part")))
            elif sid in self.ids:
                self.err("section id %r repeated" % sid)
            else:
                self.ids.add(sid)
                self.id_order.append(sid)
            self.part = a.get("data-uo-part")
        if tag == "svg" and not (a.get("class") == "uo-mark" and a.get("fill") == "currentColor" and a.get("role") == "img"
                                 and a.get("aria-label") == "ASK" and re.match(r"^[0-9. ]+$", a.get("viewbox", ""))):
            self.err("<svg> carries the wordmark's attributes only: class uo-mark, a numeric viewBox, "
                     "fill currentColor, role img, aria-label ASK")
        if tag == "nav" and a.get("aria-label") != "Sections":
            self.err("<nav> carries aria-label Sections")
        if tag == "details" and "uo-index" in _class_set(a.get("class")):
            if "data-uo-disclose" in a:
                self.err("the section index is not an authored disclosure")
        else:
            if tag == "details" and "data-uo-disclose" not in a:
                self.err("<details> without data-uo-disclose")
            if tag == "details" and "uo-details" not in _class_set(a.get("class")):
                self.err("<details> without class uo-details")
        if tag == "caption" and parent != "table":
            self.err("<caption> outside <table>")
        if tag in ("span", "mark", "div"):
            self._check_annotation_attrs(tag, a)

    def _check_annotation_attrs(self, tag, a):
        """A facet attribute sits on a mark, a passage mark or the not-yet-testable note, each with a value from
        its vocabulary; a mark carries exactly one, and only a review mark is the bordered label; a passage mark names
        the judgment its words take, pending or decided, and its note; a named note carries its id."""
        cls = _class_set(a.get("class"))
        facets = [k for k in FACET_VALUES if k in a]
        for k in facets:
            if a[k] not in FACET_VALUES[k]:
                self.err("%s=%r is outside the %s vocabulary" % (k, a[k], k[5:]))
        if tag == "span":
            if "doc-mark" in cls:
                if len(facets) != 1:
                    self.err("a mark carries exactly one of %s" % ", ".join(FACET_VALUES))
                elif (facets == ["data-review"]) != ("surface-bordered-label" in cls):
                    self.err("a review mark is the bordered label, class %s; an evidence or state mark is %s"
                             % (REVIEW_MARK, PLAIN_MARK))
            elif facets:
                self.err("a facet attribute sits on a mark, a passage mark or the not-yet-testable note only")
        elif tag == "mark":
            if facets != ["data-review"] or a.get("data-review") not in PASSAGE_ROLES:
                self.err("a passage mark carries data-review, the judgment its words take: %s" % ", ".join(PASSAGE_ROLES))
            target = a.get("aria-describedby", "")
            if not NOTE_ID.match(target):
                self.err("a passage mark names its note, aria-describedby=\"uo-note-<name>\" (got %r)" % target)
            self.described.append(target)
        else:
            nyt = cls == {"doc-group", "doc-annotation-note"}
            named = cls == {"doc-hierarchy", "doc-group", "doc-annotation-note"}
            if facets != (["data-evidence"] if nyt else []) or nyt and a.get("data-evidence") != NYT_NOTE:
                self.err("a facet attribute sits on a mark, a passage mark or the not-yet-testable note only")
            if named != ("id" in a):
                self.err("an annotation note carries its id, and only a note carries one")
            elif named:
                if not NOTE_ID.match(a["id"]) or a["id"] in self.note_ids:
                    self.err("a note's id is a unique uo-note-<name> (got %r)" % a["id"])
                self.note_ids.append(a["id"])

    def _check_class(self, tag, v, parent):
        """The class attribute is exactly one emitted set for its element, in its emitted order, plus at most
        one uo-local-<name> last where that set takes one; an element with no class is one of the named
        unclassed elements."""
        if v is None:
            if tag in CLASS_SETS and tag not in UNCLASSED:
                self.err("<%s> carries no role class" % tag)
            return
        tokens = v.split(" ")
        local = tokens[-1] if tokens[-1].startswith("uo-local-") else None
        base = " ".join(tokens[:-1]) if local else v
        if (len(set(tokens)) != len(tokens) or "" in tokens
                or (local and not re.match(r"^uo-local-[a-z][a-z0-9-]{0,31}$", local))):
            self.err("class %r not allowed on <%s>" % (v, tag))
        elif local:
            if (tag, base) not in LOCAL_SETS:
                self.err("class %r not allowed on <%s>" % (v, tag))
        elif base not in CLASS_SETS.get(tag, ()):
            self.err("class %r not allowed on <%s>" % (v, tag))


def check_final_html(doc, n_styles):
    p = _Allowlist(n_styles)
    p.feed(doc)
    p.close()
    errors = list(p.errors)
    for tag in ("html", "head", "body", "title", "main"):
        if p.counts.get(tag, 0) != 1:
            errors.append("exactly one <%s> required (found %d)" % (tag, p.counts.get(tag, 0)))
    if p.counts.get("meta", 0) != 2:
        errors.append("exactly two <meta> required (charset, viewport)")
    if p.counts.get("style", 0) != n_styles:
        errors.append("expected %d <style> elements, found %d" % (n_styles, p.counts.get("style", 0)))
    if p.h1_ok != 1 or p.counts.get("h1", 0) != 1:
        errors.append("exactly one <h1>, the masthead title, required")
    for tag, what in (("svg", "the masthead's wordmark"), ("nav", "the masthead's section index")):
        if p.counts.get(tag, 0) != 1:
            errors.append("exactly one <%s>, %s, required (found %d)" % (tag, what, p.counts.get(tag, 0)))
    for tag, cls, what in (("details", "uo-index", "section index"), ("summary", "uo-index__mark", "mark slot")):
        n = p.class_counts.get((tag, cls), 0)
        if n != 1:
            errors.append("exactly one %s, <%s class='%s'>, required (found %d)" % (what, tag, cls, n))
    if p.prompt is not None:
        errors.append(PROMPT_ERROR)
    if set(p.note_ids) != set(p.described):
        errors.append("each annotation note is named by a passage mark and each passage mark names a note: notes %s, "
                      "named %s" % (" ".join(p.note_ids) or "none", " ".join(sorted(set(p.described))) or "none"))
    for role, target in p.passages:
        if target in p.note_roles and role not in p.note_roles[target]:
            errors.append("a passage mark showing %s names %s, whose first row records no review %s mark"
                          % (role, target, role))
    if p.index_hrefs != p.id_order:
        errors.append("the section index must link every section, in order: %s, not %s"
                      % (" ".join(p.id_order), " ".join(p.index_hrefs)))
    if p.stack:
        errors.append("unclosed elements at end of output: %s" % "/".join(p.tags()))
    for css in p.styles:
        if "@import" in css:
            errors.append("CSS contains @import")
        if "</" in css:
            errors.append("CSS contains '</'")
        for m in re.finditer(r"url\(\s*(['\"]?)([^'\")]{0,40})", css):
            if not m.group(2).startswith("data:font/woff2;base64,"):
                errors.append("CSS url( is not an embedded woff2 font: %r" % m.group(2))
        for m in RESOURCE_FUNCTION.finditer(css):
            errors.append("CSS contains %s(, which can load a resource" % m.group(1))
    if errors:
        raise BuildError("final-HTML allowlist: " + "; ".join(errors[:12]))


# ---------------------------------------------------------------------------
# Seal

def content_sha256(doc):
    """SHA-256 of the bytes from <body> through </body>, with the footer.uo-foot
    seal-line element removed (it carries the render time)."""
    start = doc.index("<body>")
    end = doc.index("</body>") + len("</body>")
    body = doc[start:end]
    f0 = body.index('<footer class="uo-foot">')
    f1 = body.index("</footer>", f0) + len("</footer>")
    return hashlib.sha256((body[:f0] + body[f1:]).encode("utf-8")).hexdigest()


def render(source_md, out_html, manifest_path, uo_commit, local_css=None, now=None):
    check_markdown_pin()
    if not re.match(r"^[0-9a-f]{40}$", uo_commit or ""):
        raise BuildError("--uo-commit must be 40 lowercase hex characters")
    paths = [os.path.abspath(p) for p in (source_md, out_html, manifest_path)]
    if len(set(paths)) != 3:
        raise BuildError("--source, --out and --manifest must be three different paths")
    for label, p in (("--out", out_html), ("--manifest", manifest_path)):
        if os.path.lexists(p):
            raise BuildError("%s already exists: %s (a regenerated render is a new artifact)" % (label, p))

    with open(source_md, "rb") as f:
        source_bytes = f.read()
    try:
        source_text = source_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise BuildError("source is not UTF-8")
    source_sha = hashlib.sha256(source_bytes).hexdigest()

    with open(TEMPLATE, "rb") as f:
        template_bytes = f.read()
    with open(BUILD_PY, "rb") as f:
        build_bytes = f.read()
    shell = template_bytes.decode("utf-8")
    if shell.count("</head>") != 1:
        raise BuildError("expected exactly one </head> in template")
    head = shell.split("</head>", 1)[0]

    meta, root = parse_source(source_text)
    used = _local_names(root, set())
    local = None
    if local_css is not None:
        local = load_local_css(local_css, used)

    dep = verify_dependencies()
    try:
        owner_digest = tree_digest(HERE)
    except PinCheckError as e:
        raise BuildError(str(e))

    now = now or datetime.now(timezone.utc)
    render_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    footer = (
        '<footer class="uo-foot">\n'
        '<p class="doc-meta">Rendered <code class="doc-code">%s</code> · urban-observatory <code class="doc-code">%s</code> '
        '(declared) · design-system-ASK ' + SEAL_PARTS + ' <code class="doc-code">%s</code> (bytes verified '
        'against the vendored manifests)</p>\n'
        '<p class="doc-meta">Sealed single-file render from canonical Markdown. Fonts embedded (woff2), no sidecar.</p>\n'
        '<p class="doc-meta">Source: <code class="doc-code">%s</code> · source sha256 <code class="doc-code">%s</code></p>\n'
        "</footer>"
    ) % (render_ts, uo_commit[:7], dep["short"], _esc(os.path.basename(source_md)), source_sha)

    mark = wordmark_svg(dependency(dep, "_dsa-tokens/" + WORDMARK)["data"])
    body_html, counts, part_order = render_body(meta, root, footer, mark)
    # The three semantic-state modules, and the passage buffer, are inlined only when the document annotates; the body
    # decides, so the head is assembled after it, and the seal line names what was sealed.
    annotated = annotation_count(counts) > 0
    if body_html.count(SEAL_PARTS) != 1:
        raise BuildError("internal: the seal line's placeholder is not in the body exactly once")
    body_html = body_html.replace(SEAL_PARTS, seal_parts(annotated), 1)

    if head.count("<title>") != 1:
        raise BuildError("expected exactly one <title> in template")
    title = _esc(meta["title"])
    head = re.sub(r"<title>.*?</title>", lambda _m: "<title>%s</title>" % title, head, count=1, flags=re.S)
    if head.count("/*@@SEALED_TOKENS@@*/") != 1:
        raise BuildError("sealed-tokens marker not found exactly once in template")
    head = head.replace("/*@@SEALED_TOKENS@@*/", seal_tokens(dep, annotated), 1)
    head = head + "<style>" + md_css(annotated) + "</style>\n"
    if local is not None:
        head = head + "<style>" + local[1] + "</style>\n"
    head = head + "</head>"

    # head-only guards (the author body is governed by the allowlist instead)
    leftover = re.findall(r"@@[A-Z_]+@@", head)
    if leftover:
        raise BuildError("unreplaced markers: %r" % sorted(set(leftover)))
    if re.search(r"url\(['\"]?fonts/", head):
        raise BuildError("relative font ref present")
    if "<link" in head or "@import" in head:
        raise BuildError("external stylesheet reference present")

    doc = (
        head
        + '\n<body>\n<div class="uo-shell">\n\n'
        + '<main class="uo-md doc-flow">\n\n'
        + body_html
        + "\n\n</main>\n</div>\n</body>\n</html>\n"
    )
    check_final_html(doc, 3 if local is not None else 2)

    doc_bytes = doc.encode("utf-8")
    manifest_text = _package_manifest(
        meta=meta, dep=dep, uo_commit=uo_commit, owner_digest=owner_digest,
        build_bytes=build_bytes, template_bytes=template_bytes,
        source_md=source_md, source_bytes=source_bytes, source_sha=source_sha,
        local_css=local_css, local_raw=local[0] if local else None,
        part_order=part_order, counts=counts, out_html=out_html, doc_bytes=doc_bytes,
        content_sha=content_sha256(doc), render_ts=render_ts, inlined=inlined_modules(annotated))
    _write_new_files([(out_html, doc_bytes), (manifest_path, manifest_text.encode("utf-8"))])
    return {"out": out_html, "manifest": manifest_path, "output_sha256": hashlib.sha256(doc_bytes).hexdigest(),
            "content_sha256": content_sha256(doc), "dsa_commit": dep["commit"], "counts": counts,
            "parts": part_order, "inlined": inlined_modules(annotated)}


ANNOTATION_COUNTS = ("annotation_rows", "annotation_lists", "annotation_notes", "passage_marks", "cell_items",
                     "annotation_ranges", "item_hosts", "document_records")
# The seal line names the sealed design-system parts; the body is rendered before it is known whether the document
# annotates, so the footer carries this placeholder, replaced exactly once (render).
SEAL_PARTS = "\x00uo-seal-parts\x00"


def seal_parts(annotated):
    return "tokens, document register and semantic-state modules" if annotated else "tokens and document register"


def annotation_count(counts):
    """How many annotation constructs the document holds: rows, lists, notes, passage marks, cell items, ranges, item
    hosts and the document record."""
    return sum(counts[k] for k in ANNOTATION_COUNTS)


def role_profiles(counts):
    """The document's UO-owned roles, as design-system-ASK rendered-check profile declarations (C10): one per
    role present, with its exact count. An authored disclosure's summary keeps the case its author wrote, a
    UO value on the disclosure treatment, so it is declared rather than exempted ad hoc."""
    profiles = []
    if counts["disclosures"]:
        profiles.append({"name": "authored-case disclosure summary",
                         "selector": ".uo-details > summary > .surface-disclosure-label",
                         "owner": "urban-observatory tools/artifact-template",
                         "reason": "a disclosure summary carries authored payload text whose case can carry meaning (mW, pH), "
                                   "so it keeps the author's case: text-transform none, and no other value of the treatment",
                         "expected_count": counts["disclosures"]})
    if counts.get("authored_case"):
        profiles.append({"name": "authored-case table header",
                         "selector": ".uo-md .uo-authored-case",
                         "owner": "urban-observatory tools/artifact-template",
                         "reason": "a column declared authored-case carries header text whose case carries meaning (mW is not "
                                   "MW), so its header and each cell's label keep the author's case: text-transform none, "
                                   "and no other value of the label role",
                         "expected_count": counts["authored_case"]})
    return profiles


def _package_manifest(**k):
    dep = k["dep"]
    rows = [
        "# Package MANIFEST // sealed UO review document",
        "",
        "Written by `tools/artifact-template/build.py` after a successful seal. Pin checks are not performed by",
        "the renderer; run them from the clone (README, \"Pinned extraction and pin checks\").",
        "",
        "## design-system-ASK tokens, document register and semantic-state modules",
        "",
        "Each file below was hashed from the vendored bytes the render read and matched its sha256 row in the",
        "vendored `_dsa-tokens/MANIFEST.md` or `_dsa-surface/MANIFEST.md`; the two manifests name the same commit.",
        "The fonts are embedded as base64 of those same bytes. The token CSS is embedded with its font `src`",
        "declarations rewritten to `data:` URIs, so its embedded text is not byte-equal to the hashed file. The",
        "wordmark is embedded as the masthead's inline svg, carrying the file's viewBox and path data unchanged,",
        "so its embedded text is not byte-equal to the hashed file either. The four register modules are",
        "embedded byte for byte, in the order listed, after the token CSS. In a document that annotates, the three",
        "semantic-state modules (`spectral-state.css`, `evidence-state.css`, `review-semantics.css`) follow them,",
        "byte for byte, in the order listed; in any other document they are verified and not embedded. The row",
        "\"modules inlined, in order\" names the modules this render embedded. The commit is the manifests' commit",
        "row. The mapping from the commit to these bytes is established when the snapshots are re-synced and",
        "reviewed; the renderer does not re-check it against design-system-ASK.",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| repo | `https://github.com/apexSolarKiss/design-system-ASK` |",
        "| commit | `%s` |" % dep["commit"],
        "| short | `%s` |" % dep["short"],
        "| modules inlined, in order | `%s` |" % " ".join(k["inlined"]),
        "",
        "| File | Bytes | sha256 |",
        "| --- | --- | --- |",
    ]
    for f in dep["files"]:
        rows.append("| `%s` | %d | `%s` |" % (f["path"], f["bytes"], f["sha256"]))
    lc_raw = k["local_raw"]
    rows += [
        "",
        "## urban-observatory owner",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| commit (declared, not verified by the renderer) | `%s` |" % k["uo_commit"],
        "| extracted tree digest | `%s` |" % k["owner_digest"],
        "| build.py sha256 | `%s` |" % hashlib.sha256(k["build_bytes"]).hexdigest(),
        "| artifact.template.html sha256 | `%s` |" % hashlib.sha256(k["template_bytes"]).hexdigest(),
        "",
        "Tree digest: SHA-256 of the lines `<sha256>  ./<relpath>\\n` for every regular file under the renderer's",
        "directory, paths in byte order; a `__pycache__` directory or `.pyc` file fails the build. The renderer",
        "records this digest; `pin_check.py --extracted`, run from the clone on the final extraction, verifies it.",
        "",
        "## Toolchain",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| python | `%s` |" % sys.version.split()[0],
        "| markdown | `%s` |" % markdown.__version__,
        "",
        "## Source",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| file | `%s` |" % os.path.basename(k["source_md"]),
        "| bytes | `%d` |" % len(k["source_bytes"]),
        "| sha256 | `%s` |" % k["source_sha"],
        "",
        "## Local CSS",
        "",
        "| Field | Value |",
        "| --- | --- |",
    ]
    if lc_raw is None:
        rows.append("| local CSS | `none` |")
    else:
        rows += ["| file | `%s` |" % os.path.basename(k["local_css"]),
                 "| bytes | `%d` |" % len(lc_raw),
                 "| sha256 | `%s` |" % hashlib.sha256(lc_raw).hexdigest()]
    c = k["counts"]
    rows += [
        "",
        "## Document",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| kind | `%s` |" % k["meta"]["kind"],
        "| parts, in order | `%s` |" % " ".join(k["part_order"]),
        "| questions | `%d` |" % c["questions"],
        "| findings | `%d` |" % c["findings"],
        "| disclosures | `%d` |" % c["disclosures"],
        "| tables | `%d` |" % c["tables"],
        "| quotations (:::quote) | `%d` |" % c["quotations"],
        "| authorial callouts | `%d` |" % c["callouts"],
        "| section framings | `%d` |" % c["framing"],
        "| section syntheses | `%d` |" % c["synthesis"],
        "| structured blocks | `%d` |" % c["structures"],
        "| authored-case spans (headers and cell labels) | `%d` |" % c["authored_case"],
        "| annotation rows (:::annotate) | `%d` |" % c["annotation_rows"],
        "| annotation lists (:::annotate list) | `%d` |" % c["annotation_lists"],
        "| annotation notes (:::note) | `%d` |" % c["annotation_notes"],
        "| passage marks | `%d` |" % c["passage_marks"],
        "| annotation items in table cells | `%d` |" % c["cell_items"],
        "| annotation ranges (:::range) | `%d` |" % c["annotation_ranges"],
        "| item hosts (whole list items) | `%d` |" % c["item_hosts"],
        "| document record (:::annotate document) | `%d` |" % c["document_records"],
        "",
        "## Rendered-check profiles",
        "",
        "Package review runs design-system-ASK `tools/check-role-conformance.mjs` on the sealed file, at the",
        "owner commit above, with `--profiles` naming a file that holds exactly the JSON below. It declares the",
        "document's UO-owned roles, each with its exact count; an empty array declares none.",
        "",
        "```json",
        json.dumps(role_profiles(c), indent=1),
        "```",
        "",
        "## Output",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| file | `%s` |" % os.path.basename(k["out_html"]),
        "| bytes | `%d` |" % len(k["doc_bytes"]),
        "| sha256 | `%s` |" % hashlib.sha256(k["doc_bytes"]).hexdigest(),
        "| content sha256 | `%s` |" % k["content_sha"],
        "",
        "Content sha256: SHA-256 of the bytes from `<body>` through `</body>` with the `footer.uo-foot` seal-line",
        "element removed.",
        "",
        "## Render",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| rendered (UTC) | `%s` |" % k["render_ts"],
        "| pin checks | `not performed by the renderer; run from the clone` |",
        "",
    ]
    return "\n".join(rows)


def _write_new_files(items):
    """Writes each file to a temporary name in its own directory, then links it
    into place without overwriting. On any failure nothing is left behind."""
    temps = []
    placed = []
    try:
        for path, data in items:
            d = os.path.dirname(os.path.abspath(path))
            os.makedirs(d, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=d, prefix=".uo-render-", suffix=".tmp")
            temps.append(tmp)
            with os.fdopen(fd, "wb") as f:
                f.write(data)
        for (path, _), tmp in zip(items, temps):
            try:
                os.link(tmp, path)
            except FileExistsError:
                raise BuildError("output appeared during the render: %s" % path)
            placed.append(path)
    except BaseException:
        for p in placed:
            try:
                os.unlink(p)
            except OSError:
                pass
        raise
    finally:
        for t in temps:
            try:
                os.unlink(t)
            except OSError:
                pass


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render a UO human-readable artifact to sealed single-file HTML.")
    ap.add_argument("--source", required=True, help="canonical Markdown source path (meta + container grammar)")
    ap.add_argument("--out", required=True, help="output HTML path; must not exist")
    ap.add_argument("--manifest", required=True, help="package MANIFEST path; must not exist")
    ap.add_argument("--uo-commit", required=True, help="40-hex urban-observatory commit that was extracted")
    ap.add_argument("--local-css", default=None, help="optional payload-local CSS file")
    args = ap.parse_args(argv)
    try:
        result = render(args.source, args.out, args.manifest, args.uo_commit, args.local_css)
    except BuildError as e:
        print("ERROR: %s" % e, file=sys.stderr)
        return 1
    print("OK")
    print("output sha256  :", result["output_sha256"])
    print("content sha256 :", result["content_sha256"])
    print("dsa verified   :", result["dsa_commit"])
    print("out            :", result["out"])
    print("manifest       :", result["manifest"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
