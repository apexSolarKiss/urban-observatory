#!/usr/bin/env python3
"""
Render a urban-observatory human-readable artifact to a sealed, single-file HTML.

Takes a canonical Markdown source and produces one self-contained HTML file:
design-system-ASK token CSS + UO artifact-template overlay + a token-based prose
stylesheet + base64-embedded fonts, all inlined. The output has no external
dependencies — it opens with full styling from any location (local file, email
attachment, copied folder) with no network and no sidecar.

This is the REUSABLE rendering machinery for the UO artifact class. Specific
review packages (e.g. TMK guided-review packages, with their own banners and
review-orchestration files) are assembled operator-side from this template; they
are not part of this repo.

Design-system inheritance
-------------------------
The visual language is inherited from design-system-ASK by reference. This repo
vendors a PINNED token snapshot under `_dsa-tokens/` (a reproducible build input,
NOT a fork and NOT a second source of truth) — see `_dsa-tokens/MANIFEST.md` for
the upstream commit SHA. Foundational tokens (`colors_and_type.css`) are used
verbatim and never edited here. The foreground values are the foundation's: the
template's copied dark block repeats them without changing them, and its only
artifact-layer value override is line intensity (`--artifact-line` /
`--artifact-line-soft`, in `artifact.template.html`). See README.md, "Light /
dark contract (Class B v2)", for the contract.

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
BUILD_PY = os.path.abspath(__file__)

MARKDOWN_PIN = "3.4.1"

FONTS = [
    "InterVariable.woff2", "InterVariable-Italic.woff2",
    "JetBrainsMono.woff2", "JetBrainsMono-Italic.woff2",
]

# Token-based prose stylesheet for the Markdown-rendered body. All values are
# design tokens; text resolves through --fg-*, whose values are the foundation's
# (the template's copied dark block repeats them unchanged), so base-element and
# class rules stay consistent.
MD_CSS = """
.uo-shell { max-width: 1120px; margin: 0 auto; padding: var(--space-7) var(--space-6) var(--space-10); }
.uo-md { max-width: 80ch; margin: 0 auto; font-size: var(--fs-small); font-weight: var(--fw-extralight); line-height: 1.6; color: var(--fg-1); }
.uo-md > :first-child { margin-top: 0; }
.uo-md h1 { font-size: var(--fs-h2); font-weight: var(--fw-regular); line-height: var(--lh-heading); letter-spacing: var(--tracking-tight); margin: var(--space-6) 0 var(--space-4); color: var(--fg-1); }
.uo-md h2 { font-size: var(--fs-h3); font-weight: var(--fw-regular); line-height: var(--lh-heading); letter-spacing: var(--tracking-tight); margin: var(--space-8) 0 var(--space-4); padding-top: var(--space-4); border-top: 1px solid var(--artifact-line); color: var(--fg-1); }
.uo-md h3 { font-size: var(--fs-body); font-weight: var(--fw-light); line-height: var(--lh-tight); margin: var(--space-6) 0 var(--space-3); color: var(--fg-1); }
.uo-md p { font-size: var(--fs-small); font-weight: var(--fw-extralight); line-height: 1.6; margin: 0 0 var(--space-4); color: var(--fg-1); text-wrap: pretty; }
.uo-md ul, .uo-md ol { margin: 0 0 var(--space-4); padding-left: var(--space-5); }
.uo-md li { margin: 0 0 var(--space-2); }
.uo-md strong { font-weight: var(--fw-medium); color: var(--fg-1); }
.uo-md em { font-style: italic; color: var(--fg-2); }
.uo-md a { color: inherit; border-bottom: 1px solid var(--artifact-line); }
.uo-md hr { border: 0; border-top: 1px solid var(--artifact-line-soft); margin: var(--space-7) 0; }
.uo-md blockquote { margin: 0 0 var(--space-4); padding: var(--space-1) 0 var(--space-1) var(--space-5); border-left: 3px solid var(--ask-emphasis-violet); color: var(--fg-2); }
.uo-md blockquote p { color: var(--fg-2); margin-bottom: var(--space-2); }
.uo-md code { font-family: var(--font-mono); font-size: 0.86em; font-weight: var(--fw-light); background: var(--uo-code-bg); padding: 0.08em 0.34em; border-radius: var(--radius-xs); }
.uo-md pre { background: var(--uo-soft-bg); padding: var(--space-4); border-radius: var(--radius-sm); overflow-x: auto; border: 1px solid var(--artifact-line-soft); margin: 0 0 var(--space-4); }
.uo-md pre code { background: none; padding: 0; font-size: var(--fs-caption); line-height: 1.55; }
.uo-md table { width: 100%; border-collapse: collapse; margin: 0 0 var(--space-5); font-family: var(--font-mono); font-size: var(--fs-caption); }
.uo-md th, .uo-md td { border: 1px solid var(--artifact-line); padding: var(--space-2) var(--space-3); text-align: left; vertical-align: top; }
.uo-md th, .uo-md td { overflow-wrap: anywhere; }
.uo-md thead th { font-weight: var(--fw-medium); border-bottom: 2px solid var(--artifact-line); }
.uo-md .uo-foot { margin-top: var(--space-8); padding-top: var(--space-5); border-top: 1px solid var(--artifact-line); font-family: var(--font-mono); font-size: var(--fs-caption); color: var(--fg-2); }
.uo-md .uo-foot p { font-family: var(--font-mono); font-size: var(--fs-caption); color: var(--fg-2); margin: 0 0 var(--space-2); }
"""


class BuildError(Exception):
    """A fail-closed rule rejected the source, its inputs or the output."""


# ---------------------------------------------------------------------------
# Closed vocabularies. README.md is the contract; tests assert these tables
# equal the README's.

PART_NUMBERS = tuple("%02d" % n for n in range(1, 11))
BASE_REQUIRED_PARTS = ("01", "02", "10")
KIND_PROFILES = {
    "guided-review": ("04", "06", "08"),
    "confirmation": ("07",),
}
GENERATED_PARTS = ("01", "10")          # the renderer generates their chrome

META_KEYS = ("kind", "title", "id", "round", "classification", "audience")
TITLE_MAX = 200

CONTAINER_KINDS = ("part", "question", "finding", "disclose", "table")
DISCLOSE_CLASSES = ("question-detail", "evidence", "provenance")
TABLE_ROLES = ("key", "text", "num", "status")
LOCAL_NAME = re.compile(r"^[a-z][a-z0-9-]{0,31}$")
CHROME_PARTS = ("01", "10")             # carry generated identity and seal chrome; no local= hook
# CSS functions that can load a resource from a string argument (url( is rejected separately).
RESOURCE_FUNCTION = re.compile(r"(?<![\w-])(-webkit-image-set|image-set|image|cross-fade|element|src|paint)\s*\(", re.I)

# Final-HTML allowlist.
BODY_ELEMENTS = frozenset(
    "div section header main footer h1 h2 h3 h4 p ul ol li blockquote pre code em strong a hr br "
    "table thead tbody tr th td details summary dl dt dd span".split()
)
HEAD_ELEMENTS = frozenset(("meta", "title", "style"))
VOID_ELEMENTS = frozenset(("meta", "br", "hr"))
# Renderer chrome classes, by the element that may carry each. Every one must
# exist in artifact.template.html or MD_CSS (a test asserts it).
CHROME_CLASSES = {
    "div": ("uo-shell", "uo-status-rail"),
    "main": ("uo-md",),
    "header": ("uo-head",),
    "dl": ("uo-head__meta",),
    "span": ("uo-status-rail__primary", "uo-status-rail__sep"),
    "footer": ("uo-foot",),
}
LOCAL_CLASS_ELEMENTS = ("section", "div", "details", "table")
DATA_VALUES = {
    "data-uo-part": PART_NUMBERS,
    "data-uo-role": ("question", "finding"),
    "data-uo-disclose": DISCLOSE_CLASSES,
    "data-uo-cell": TABLE_ROLES,
}


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


def new_markdown():
    return markdown.Markdown(extensions=["tables", "fenced_code", "sane_lists", NoRawHtml()])


_PROBE = []


def _probe_markdown():
    if not _PROBE:
        _PROBE.append(new_markdown())
    return _PROBE[0]


# ---------------------------------------------------------------------------
# Source model: one meta block plus a container tree

# The opening-fence shape python-markdown's fenced_code accepts (3.4.1), so a
# ":::" line is code text exactly where python-markdown renders code.
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
        self.local = None

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
                if c.kind == "table" or c.has_content():
                    return True
            elif c.renders_text():
                return True
        return False


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
        rendered = _render_markdown(_probe_markdown(), self)
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


def _open_container(kind, tokens, lineno, parent, root):
    if kind == "meta":
        raise BuildError("line %d: :::meta is not allowed here; it must be the first non-blank line" % lineno)
    if kind not in CONTAINER_KINDS:
        raise BuildError("line %d: unknown container kind %r (closed set: %s)" % (lineno, kind, ", ".join(CONTAINER_KINDS)))
    node = Node(kind, lineno, parent)
    seen = set()
    positional = []
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
        roles = []
        for typ, val in positional:
            if typ != "word" or val not in TABLE_ROLES:
                raise BuildError("line %d: table role %r outside the closed set %s" % (lineno, val, ", ".join(TABLE_ROLES)))
            roles.append(val)
        if not roles:
            raise BuildError("line %d: :::table takes one role per column" % lineno)
        node.roles = roles

    _check_position(node, parent, root)
    return node


def _check_position(node, parent, root):
    at = _label(None if parent is root else parent)
    if node.kind != "table" and parent is not root and parent.kind == "disclose":
        raise BuildError("K7: :::%s at line %d sits inside %s; ALWAYS VISIBLE content cannot be disclosed"
                         % (node.kind, node.line, _label(parent)))
    if node.kind == "part":
        if parent is not root:
            raise BuildError("line %d: :::part is allowed at top level only, not inside %s" % (node.line, at))
    elif node.kind == "question":
        if parent is root or parent.kind != "part" or parent.number != "03":
            raise BuildError("line %d: :::question is allowed directly inside :::part 03 only, not %s" % (node.line, at))
    elif node.kind == "finding":
        if parent is root or parent.kind != "part" or parent.number != "06":
            raise BuildError("line %d: :::finding is allowed directly inside :::part 06 only, not %s" % (node.line, at))
    elif node.kind == "table":
        if parent is root:
            raise BuildError("line %d: :::table is allowed inside a part only, not at top level" % node.line)
    elif node.kind == "disclose":
        chain = [] if parent is root else [parent] + list(parent.ancestors())
        if any(a is not root and a.kind == "part" and a.number == "08" for a in chain):
            raise BuildError("K7: :::disclose at line %d is inside part 08; the register stays whole and visible"
                             % node.line)
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
        elif node.disclose == "provenance":
            if parent is root or parent.kind != "part" or parent.number != "10":
                raise BuildError("line %d: :::disclose provenance is allowed directly inside :::part 10 only, not %s"
                                 % (node.line, at))
            if any(isinstance(c, Node) and c.kind == "disclose" for c in parent.children):
                raise BuildError("line %d: part 10 carries at most one provenance disclosure" % node.line)


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
        if FENCE_START.match(t):
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
                if node.kind in ("question", "finding", "disclose") and not node.has_content():
                    raise BuildError("line %d: %s is empty" % (lineno, _label(node)))
                continue
            m = re.match(r"^([a-z]+)(?:[ ]+(.*))?$", rest)
            if not m:
                raise BuildError("line %d: malformed container line %r" % (lineno, t))
            node = _open_container(m.group(1), _tokenize(m.group(2) or "", lineno), lineno, stack[-1], root)
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
    return meta, root


def _append_text(node, lineno, t):
    if not node.children or not isinstance(node.children[-1], Text):
        node.children.append(Text())
    node.children[-1].lines.append((lineno, t))


def _check_parts(meta, root):
    parts = [c for c in root.children if isinstance(c, Node)]
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
    required = BASE_REQUIRED_PARTS + KIND_PROFILES[meta["kind"]]
    for number in required:
        if number not in GENERATED_PARTS and number not in seen:
            raise BuildError("K2: kind %s requires part %s, which is missing" % (meta["kind"], number))


# ---------------------------------------------------------------------------
# Rendering

def _render_markdown(md, text_node):
    source = "\n".join(t for _, t in text_node.lines)
    md.reset()
    try:
        return md.convert(source)
    except BuildError as e:
        raise BuildError("line %d: %s" % (text_node.first_nonblank_line(), e))


TABLE_CELL = re.compile(r"<(th|td)((?:\s[^>]*)?)>")


def _render_table(md, node):
    texts = [c for c in node.children if isinstance(c, Text) and c.nonblank()]
    if any(isinstance(c, Node) for c in node.children) or len(texts) != 1:
        raise BuildError("line %d: a :::table container holds exactly one pipe table and nothing else" % node.line)
    out = _render_markdown(md, texts[0])
    n_tables = out.count("<table")
    stripped = re.sub(r"<table>.*?</table>", "", out, flags=re.S).strip() if n_tables == 1 else out
    if n_tables != 1 or stripped:
        raise BuildError("line %d: a :::table container holds exactly one pipe table and nothing else (found %d tables)"
                         % (node.line, n_tables))
    _check_row_cells(texts[0])
    rows = re.findall(r"<tr>(.*?)</tr>", out, flags=re.S)
    columns = len(TABLE_CELL.findall(rows[0])) if rows else 0
    if columns != len(node.roles):
        raise BuildError("line %d: :::table declares %d roles for %d columns" % (node.line, len(node.roles), columns))

    def fix_row(m):
        i = [0]

        def cell(cm):
            role = node.roles[i[0]] if i[0] < len(node.roles) else None
            i[0] += 1
            if role is None:
                raise BuildError("line %d: a table row has more cells than declared roles" % node.line)
            return '<%s data-uo-cell="%s"%s>' % (cm.group(1), role, cm.group(2))
        return "<tr>" + TABLE_CELL.sub(cell, m.group(1)) + "</tr>"

    out = re.sub(r"<tr>(.*?)</tr>", fix_row, out, flags=re.S)
    if node.local:
        out = out.replace("<table>", '<table class="uo-local-%s">' % node.local, 1)
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


def _local_attr(node):
    return ' class="uo-local-%s"' % node.local if node.local else ""


def _render_children(md, node, counts):
    out = []
    for c in node.children:
        if isinstance(c, Text):
            if not c.nonblank():
                continue
            rendered = _render_markdown(md, c)
            if "<table" in rendered:
                raise BuildError("line %d: a pipe table must be wrapped in :::table with its column roles"
                                 % c.first_nonblank_line())
            out.append(rendered)
        else:
            out.append(_render_node(md, c, counts))
    return "\n".join(out)


def _render_node(md, node, counts):
    if node.kind == "table":
        counts["tables"] += 1
        return _render_table(md, node)
    inner = _render_children(md, node, counts)
    if node.kind == "question":
        counts["questions"] += 1
        central = ' data-uo-central="true"' if node.central else ""
        return '<div data-uo-role="question"%s%s>\n%s\n</div>' % (central, _local_attr(node), inner)
    if node.kind == "finding":
        counts["findings"] += 1
        return '<div data-uo-role="finding"%s>\n%s\n</div>' % (_local_attr(node), inner)
    if node.kind == "disclose":
        counts["disclosures"] += 1
        return '<details data-uo-disclose="%s"%s><summary>%s</summary>\n%s\n</details>' % (
            node.disclose, _local_attr(node), _esc(node.summary), inner)
    raise BuildError("internal: unexpected node %r" % node.kind)


def render_body(meta, root, seal_footer):
    """Returns (body inner HTML, counts, part numbers in order)."""
    md = new_markdown()
    counts = {"questions": 0, "findings": 0, "disclosures": 0, "tables": 0}
    parts = [c for c in root.children if isinstance(c, Node)]
    numbers = [p.number for p in parts]
    sections = []
    if "01" not in numbers:
        parts.insert(0, Node("part", 0))
        parts[0].number = "01"
    if "10" not in numbers:
        tail = Node("part", 0)
        tail.number = "10"
        parts.append(tail)
    for p in parts:
        inner = _render_children(md, p, counts)
        chunks = []
        if p.number == "01":
            chunks.append(_masthead(meta))
        if inner:
            chunks.append(inner)
        if p.number == "10":
            chunks.append(seal_footer)
        sections.append('<section data-uo-part="%s"%s>\n%s\n</section>' % (p.number, _local_attr(p), "\n".join(chunks)))
    return "\n\n".join(sections), counts, [p.number for p in parts]


def _masthead(meta):
    rail_items = [meta["classification"], meta["audience"], meta["kind"], meta["round"]]
    rail = ['<span class="uo-status-rail__primary">%s</span>' % _esc(rail_items[0])]
    for item in rail_items[1:]:
        rail.append('<span class="uo-status-rail__sep"></span><span>%s</span>' % _esc(item))
    dl = "".join("<dt>%s</dt><dd>%s</dd>" % (k, _esc(meta[k])) for k in ("id", "kind", "round"))
    return ('<div class="uo-status-rail">%s</div>\n'
            '<header class="uo-head">\n<h1>%s</h1>\n<dl class="uo-head__meta">%s</dl>\n</header>'
            % ("".join(rail), _esc(meta["title"]), dl))


# ---------------------------------------------------------------------------
# Dependency bytes: verified against _dsa-tokens/MANIFEST.md before sealing

def verify_dependencies():
    """Reads the MANIFEST field table and every vendored file, and verifies each
    file's sha256 over the bytes actually read. Returns the verified record,
    including those bytes. Any gap fails.

    Stated limit: this binds the embedded bytes to the committed manifest's hash
    rows. That the manifest's commit row names the design-system commit those
    bytes came from is established when the snapshot is re-synced and reviewed;
    the renderer has no design-system clone and does not re-check it."""
    try:
        with open(MANIFEST, "r", encoding="utf-8") as f:
            manifest_text = f.read()
    except OSError as e:
        raise BuildError("dependency manifest unreadable: %s" % e)
    fields = {}
    for m in re.finditer(r"^\|\s*([^|`]+?)\s*\|\s*`([^`]*)`\s*\|\s*$", manifest_text, flags=re.M):
        if m.group(1) in fields:
            raise BuildError("dependency manifest: field %r repeated" % m.group(1))
        fields[m.group(1)] = m.group(2)
    commit = fields.get("commit")
    if commit is None:
        raise BuildError("dependency manifest: no commit row")
    if not re.match(r"^[0-9a-f]{40}$", commit):
        raise BuildError("dependency manifest: commit %r is not 40 lowercase hex" % commit)
    if "short" in fields and fields["short"] != commit[:7]:
        raise BuildError("dependency manifest: short %r is not the commit's first 7 characters" % fields["short"])
    record = {"commit": commit, "short": commit[:7], "files": []}
    for rel in ["colors_and_type.css"] + ["fonts/" + fn for fn in FONTS]:
        expected = fields.get("%s sha256" % rel)
        if expected is None:
            raise BuildError("dependency manifest: no sha256 row for %s" % rel)
        path = os.path.join(HERE, "_dsa-tokens", *rel.split("/"))
        try:
            with open(path, "rb") as f:
                data = f.read()
        except OSError:
            raise BuildError("dependency file missing: _dsa-tokens/%s" % rel)
        actual = hashlib.sha256(data).hexdigest()
        if actual != expected:
            raise BuildError("dependency bytes do not match the manifest: _dsa-tokens/%s sha256 %s, manifest %s"
                             % (rel, actual, expected))
        record["files"].append({"path": "_dsa-tokens/" + rel, "bytes": len(data), "sha256": actual, "data": data})
    return record


def seal_tokens(dep):
    css = dep["files"][0]["data"].decode("utf-8")
    for entry, fn in zip(dep["files"][1:], FONTS):
        uri = "data:font/woff2;base64," + base64.b64encode(entry["data"]).decode("ascii")
        pattern = r"src:[^;]*fonts/" + re.escape(fn) + r"[^;]*;"
        css, n = re.subn(pattern, lambda _m: "src: url('" + uri + "') format('woff2');", css, flags=re.S)
        if n != 1:
            raise BuildError("expected exactly 1 src match for %s, got %d" % (fn, n))
    if re.findall(r"url\('fonts/[^']+'\)", css):
        raise BuildError("un-inlined font url() remain")
    return ("/* === SEALED design-system-ASK tokens (upstream %s per the vendored manifest; file bytes verified "
            "against its sha256 rows) + base64 fonts === */\n%s" % (dep["short"], css))


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

class _Allowlist(HTMLParser):
    def __init__(self, n_styles):
        super().__init__(convert_charrefs=True)
        self.errors = []
        self.stack = []           # (tag, class attribute or None)
        self.counts = {}
        self.n_styles = n_styles
        self.styles = []
        self.in_style = False
        self.h1_ok = 0

    def err(self, msg):
        self.errors.append("%s (output line %d)" % (msg, self.getpos()[0]))

    def tags(self):
        return [t for t, _ in self.stack]

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
        else:
            self.err("<%s> outside head and body" % tag)
        if tag == "h1":
            if self.stack and self.stack[-1] == ("header", "uo-head"):
                self.h1_ok += 1
            else:
                self.err("<h1> is the renderer's masthead title only; authored headings use ## to ####")
        if tag == "style":
            self.in_style = True
            self.styles.append("")
        if tag not in VOID_ELEMENTS:
            self.stack.append((tag, a.get("class")))

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
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            self.styles[-1] += data

    def _check_attrs(self, tag, a, parent):
        for k, v in a.items():
            if k == "href" and tag == "a":
                if not re.match(r"^https?://", v):
                    self.err("<a href=%r>: only https:// and http:// links are allowed" % v)
            elif k == "title" and tag == "a":
                pass
            elif k == "start" and tag == "ol":
                if not re.match(r"^[0-9]{1,6}$", v):
                    self.err("<ol start=%r> must be a number" % v)
            elif k in DATA_VALUES and v in DATA_VALUES[k] and (tag, k) in (
                    ("section", "data-uo-part"), ("div", "data-uo-role"),
                    ("details", "data-uo-disclose"), ("th", "data-uo-cell"), ("td", "data-uo-cell")):
                pass
            elif k == "data-uo-central" and tag == "div" and v == "true" and a.get("data-uo-role") == "question":
                pass
            elif k == "class":
                self._check_class(tag, v, parent)
            else:
                self.err("attribute %s=%r not allowed on <%s>" % (k, v, tag))
        if tag in ("th", "td") and "data-uo-cell" not in a:
            self.err("<%s> without a table role" % tag)
        if tag == "section" and "data-uo-part" not in a:
            self.err("<section> without data-uo-part")
        if tag == "details" and "data-uo-disclose" not in a:
            self.err("<details> without data-uo-disclose")

    def _check_class(self, tag, v, parent):
        if tag == "code" and parent == "pre" and re.match(r"^language-[a-z0-9+-]+$", v):
            return
        if v in CHROME_CLASSES.get(tag, ()):
            return
        m = re.match(r"^uo-local-([a-z][a-z0-9-]{0,31})$", v)
        if m and tag in LOCAL_CLASS_ELEMENTS:
            return
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

    if head.count("<title>") != 1:
        raise BuildError("expected exactly one <title> in template")
    title = _esc(meta["title"])
    head = re.sub(r"<title>.*?</title>", lambda _m: "<title>%s</title>" % title, head, count=1, flags=re.S)
    if head.count("/*@@SEALED_TOKENS@@*/") != 1:
        raise BuildError("sealed-tokens marker not found exactly once in template")
    head = head.replace("/*@@SEALED_TOKENS@@*/", seal_tokens(dep), 1)
    head = head + "<style>" + MD_CSS + "</style>\n"
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

    now = now or datetime.now(timezone.utc)
    render_ts = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    footer = (
        '<footer class="uo-foot">\n'
        "<p>Rendered <code>%s</code> · urban-observatory <code>%s</code> (declared) · "
        "design-system-ASK tokens <code>%s</code> (bytes verified against the vendored manifest)</p>\n"
        "<p>Sealed single-file render from canonical Markdown. Fonts embedded (woff2), no sidecar.</p>\n"
        "<p>Source: <code>%s</code> · source sha256 <code>%s</code></p>\n"
        "</footer>"
    ) % (render_ts, uo_commit[:7], dep["short"], _esc(os.path.basename(source_md)), source_sha)

    body_html, counts, part_order = render_body(meta, root, footer)
    doc = (
        head
        + '\n<body>\n<div class="uo-shell">\n\n'
        + '<main class="uo-md">\n\n'
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
        content_sha=content_sha256(doc), render_ts=render_ts)
    _write_new_files([(out_html, doc_bytes), (manifest_path, manifest_text.encode("utf-8"))])
    return {"out": out_html, "manifest": manifest_path, "output_sha256": hashlib.sha256(doc_bytes).hexdigest(),
            "content_sha256": content_sha256(doc), "dsa_commit": dep["commit"], "counts": counts,
            "parts": part_order}


def _package_manifest(**k):
    dep = k["dep"]
    rows = [
        "# Package MANIFEST // sealed UO review document",
        "",
        "Written by `tools/artifact-template/build.py` after a successful seal. Pin checks are not performed by",
        "the renderer; run them from the clone (README, \"Pinned extraction and pin checks\").",
        "",
        "## design-system-ASK tokens",
        "",
        "Each file below was hashed from the vendored bytes the render read and matched its sha256 row in the",
        "vendored `_dsa-tokens/MANIFEST.md`. The fonts are embedded as base64 of those same bytes. The token",
        "CSS is embedded with its font `src` declarations rewritten to `data:` URIs, so its embedded text is not",
        "byte-equal to the hashed file. The commit is that manifest's commit row. The mapping from the commit",
        "to these bytes is established when the snapshot is re-synced and reviewed; the renderer does not",
        "re-check it against design-system-ASK.",
        "",
        "| Field | Value |",
        "| --- | --- |",
        "| repo | `https://github.com/apexSolarKiss/design-system-ASK` |",
        "| commit | `%s` |" % dep["commit"],
        "| short | `%s` |" % dep["short"],
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
