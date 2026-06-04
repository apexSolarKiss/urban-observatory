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
verbatim and never edited here. The artifact template applies a LOCAL light-mode
foreground rebind (in `artifact.template.html`) so light-mode text is readable on
the lavender gradient; dark mode is unchanged. See README.md for the contract.

Usage
-----
    python3 build.py --source PATH.md --out PATH.html [--title "..."]

Requires: python3 + the `markdown` package (pip install markdown).
"""
import argparse
import base64
import hashlib
import os
import re
from datetime import datetime, timezone

import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
TOKENS_CSS = os.path.join(HERE, "_dsa-tokens", "colors_and_type.css")
FONTS_DIR = os.path.join(HERE, "_dsa-tokens", "fonts")
TEMPLATE = os.path.join(HERE, "artifact.template.html")
MANIFEST = os.path.join(HERE, "_dsa-tokens", "MANIFEST.md")

FONTS = [
    "InterVariable.woff2", "InterVariable-Italic.woff2",
    "JetBrainsMono.woff2", "JetBrainsMono-Italic.woff2",
]

# Token-based prose stylesheet for the Markdown-rendered body. All values are
# design tokens; text resolves through --fg-* (which the template rebinds for
# light-mode readability), so base-element and class rules stay consistent.
MD_CSS = """
.uo-shell { max-width: 1120px; margin: 0 auto; padding: var(--space-7) var(--space-6) var(--space-10); }
.uo-md { max-width: 80ch; margin: 0 auto; font-size: var(--fs-small); font-weight: var(--fw-extralight); line-height: 1.6; color: var(--fg-1); }
.uo-md > :first-child { margin-top: 0; }
.uo-md h1 { font-size: var(--fs-h2); font-weight: var(--fw-regular); line-height: var(--lh-heading); letter-spacing: var(--tracking-tight); margin: var(--space-6) 0 var(--space-4); color: var(--fg-1); }
.uo-md h2 { font-size: var(--fs-h3); font-weight: var(--fw-regular); line-height: var(--lh-heading); letter-spacing: var(--tracking-tight); margin: var(--space-8) 0 var(--space-4); padding-top: var(--space-4); border-top: 1px solid var(--line-1); color: var(--fg-1); }
.uo-md h3 { font-size: var(--fs-body); font-weight: var(--fw-light); line-height: var(--lh-tight); margin: var(--space-6) 0 var(--space-3); color: var(--fg-1); }
.uo-md p { font-size: var(--fs-small); font-weight: var(--fw-extralight); line-height: 1.6; margin: 0 0 var(--space-4); color: var(--fg-1); text-wrap: pretty; }
.uo-md ul, .uo-md ol { margin: 0 0 var(--space-4); padding-left: var(--space-5); }
.uo-md li { margin: 0 0 var(--space-2); }
.uo-md strong { font-weight: var(--fw-medium); color: var(--fg-1); }
.uo-md em { font-style: italic; color: var(--fg-2); }
.uo-md a { color: inherit; border-bottom: 1px solid var(--line-1); }
.uo-md hr { border: 0; border-top: 1px solid var(--line-2); margin: var(--space-7) 0; }
.uo-md blockquote { margin: 0 0 var(--space-4); padding: var(--space-1) 0 var(--space-1) var(--space-5); border-left: 3px solid var(--ask-emphasis-violet); color: var(--fg-2); }
.uo-md blockquote p { color: var(--fg-2); margin-bottom: var(--space-2); }
.uo-md code { font-family: var(--font-mono); font-size: 0.86em; font-weight: var(--fw-light); background: var(--uo-code-bg); padding: 0.08em 0.34em; border-radius: var(--radius-xs); }
.uo-md pre { background: var(--uo-soft-bg); padding: var(--space-4); border-radius: var(--radius-sm); overflow-x: auto; border: 1px solid var(--line-2); margin: 0 0 var(--space-4); }
.uo-md pre code { background: none; padding: 0; font-size: var(--fs-caption); line-height: 1.55; }
.uo-md table { width: 100%; border-collapse: collapse; margin: 0 0 var(--space-5); font-family: var(--font-mono); font-size: var(--fs-caption); }
.uo-md th, .uo-md td { border: 1px solid var(--line-1); padding: var(--space-2) var(--space-3); text-align: left; vertical-align: top; }
.uo-md thead th { font-weight: var(--fw-medium); border-bottom: 2px solid var(--line-1); }
.uo-md .uo-foot { margin-top: var(--space-8); padding-top: var(--space-5); border-top: 1px solid var(--line-1); font-family: var(--font-mono); font-size: var(--fs-caption); color: var(--fg-2); }
.uo-md .uo-foot p { font-family: var(--font-mono); font-size: var(--fs-caption); color: var(--fg-2); margin: 0 0 var(--space-2); }
"""


def _dsa_sha():
    """Read the pinned design-system commit SHA from the vendored MANIFEST."""
    try:
        with open(MANIFEST, "r", encoding="utf-8") as f:
            m = re.search(r"\|\s*commit\s*\|\s*`([0-9a-f]{40})`", f.read())
            return m.group(1) if m else "unknown"
    except OSError:
        return "unknown"


def seal_tokens():
    with open(TOKENS_CSS, "r", encoding="utf-8") as f:
        css = f.read()
    raw_total = enc_total = 0
    for fn in FONTS:
        with open(os.path.join(FONTS_DIR, fn), "rb") as f:
            raw = f.read()
        enc = base64.b64encode(raw).decode("ascii")
        raw_total += len(raw)
        enc_total += len(enc)
        uri = "data:font/woff2;base64," + enc
        pattern = r"src:[^;]*fonts/" + re.escape(fn) + r"[^;]*;"
        css, n = re.subn(pattern, "src: url('" + uri + "') format('woff2');", css, flags=re.S)
        if n != 1:
            raise SystemExit("ERROR: expected exactly 1 src match for %s, got %d" % (fn, n))
    if re.findall(r"url\('fonts/[^']+'\)", css):
        raise SystemExit("ERROR: un-inlined font url() remain")
    short = _dsa_sha()[:7]
    return "/* === SEALED design-system-ASK tokens (upstream %s) + base64 fonts === */\n%s" % (short, css)


def md_to_html(md_text):
    # Cosmetic: hard-break the leading metadata block (bold field lines) so they
    # don't collapse into one run-on paragraph. Canonical source is not modified.
    parts = md_text.split("\n---\n", 1)
    if len(parts) == 2:
        head, rest = parts
        head = head.replace("\n**", "  \n**")
        md_text = head + "\n---\n" + rest
    return markdown.markdown(md_text, extensions=["tables", "fenced_code", "sane_lists"])


def render(source_md, out_html, title=None):
    with open(TEMPLATE, "r", encoding="utf-8") as f:
        shell = f.read()
    if shell.count("</head>") != 1:
        raise SystemExit("ERROR: expected exactly one </head> in template")
    head = shell.split("</head>", 1)[0]
    if title:
        head = re.sub(r"<title>.*?</title>", "<title>%s</title>" % title, head, count=1, flags=re.S)

    with open(source_md, "r", encoding="utf-8") as f:
        md_text = f.read()
    md_sha = hashlib.sha256(md_text.encode("utf-8")).hexdigest()
    body_html = md_to_html(md_text)

    sealed = seal_tokens()
    if head.count("/*@@SEALED_TOKENS@@*/") != 1:
        raise SystemExit("ERROR: sealed-tokens marker not found exactly once in template")
    head = head.replace("/*@@SEALED_TOKENS@@*/", sealed, 1)
    head = head + "<style>" + MD_CSS + "</style>\n</head>"

    render_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    dsa_sha = _dsa_sha()
    footer = (
        '<footer class="uo-foot">\n'
        "  <p>Rendered <code>%s</code> · design-system-ASK tokens pinned <code>%s</code></p>\n"
        "  <p>Sealed single-file render from canonical Markdown. Fonts embedded (woff2), no sidecar.</p>\n"
        "  <p>Source: <code>%s</code> · source sha256 <code>%s</code></p>\n"
        "</footer>"
    ) % (render_ts, dsa_sha[:7], os.path.basename(source_md), md_sha)

    html = (
        head
        + '\n<body>\n<div class="uo-shell">\n\n'
        + '<main class="uo-md">\n\n'
        + body_html
        + "\n\n" + footer
        + "\n\n</main>\n</div>\n</body>\n</html>\n"
    )

    # self-contained + cleanliness guards
    leftover = re.findall(r"@@[A-Z_]+@@", html)
    if leftover:
        raise SystemExit("ERROR: unreplaced markers: %r" % set(leftover))
    if "/*@@SEALED_TOKENS@@*/" in html:
        raise SystemExit("ERROR: sealed-tokens marker not replaced")
    if re.search(r"url\(['\"]?fonts/", html):
        raise SystemExit("ERROR: relative font ref present")
    if "<link" in html or "@import" in html:
        raise SystemExit("ERROR: external stylesheet reference present")

    os.makedirs(os.path.dirname(os.path.abspath(out_html)) or ".", exist_ok=True)
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)

    print("OK")
    print("source sha256 :", md_sha)
    print("dsa pinned    :", dsa_sha)
    print("final bytes   : %d (%.2f MB)" % (os.path.getsize(out_html), os.path.getsize(out_html) / 1024 / 1024))
    print("out           :", out_html)


def main():
    ap = argparse.ArgumentParser(description="Render a UO human-readable artifact to sealed single-file HTML.")
    ap.add_argument("--source", required=True, help="canonical Markdown source path")
    ap.add_argument("--out", required=True, help="output HTML path")
    ap.add_argument("--title", default=None, help="optional <title> override")
    args = ap.parse_args()
    render(args.source, args.out, args.title)


if __name__ == "__main__":
    main()
