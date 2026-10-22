"""Tests for build.py. Synthetic Markdown only.

Run from the repo root:
    python3 -B -m unittest discover -s tools/artifact-template/tests

Control discipline: each negative test applies ONE mutation to a passing
baseline source and asserts the specific error message.
"""
import hashlib
import importlib._bootstrap_external as bootstrap_external
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from unittest import mock

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import build  # noqa: E402

UO_COMMIT = "0" * 39 + "1"

GUIDED = """:::meta
kind: guided-review
title: Synthetic guided review
id: SYN-GR-001
round: R1
classification: synthetic fixture
audience: renderer test
:::

:::part 01
Synthetic locator line.
:::

:::part 02
What this synthetic document tests, and what not to judge.
:::

:::part 03
The bounded question set.

:::question central
The central question prompt.

The central question's detail, visible.
:::

:::question
A non-central question prompt.

:::disclose question-detail "Question detail"
The non-central question's detail.
:::
:::
:::

:::part 04
The synthetic executive result.
:::

:::part 06
:::finding
**Status:** open. Finding, significance and limit.

:::disclose evidence "Field-level evidence"
Field-level listing.
:::
:::
:::

:::part 08
The whole synthetic register.
:::

:::part 10
:::disclose provenance "Provenance"
Synthetic provenance block.
:::
:::
"""

CONFIRMATION = """:::meta
kind: confirmation
title: Synthetic confirmation
id: SYN-CF-001
round: R2
classification: synthetic fixture
audience: renderer test
:::

:::part 02
What this synthetic confirmation tests.
:::

:::part 07
What changed against the synthetic earlier position.
:::
"""

TABLE = """:::table dense key text num status
| Row | Claim | Count | State |
|---|---|---|---|
| a | first claim | 12 | open |
| b | second claim | 3 | closed |
:::
"""


def mutate(src, old, new, count=1):
    assert src.count(old) == count, "mutation anchor %r occurs %d times" % (old, src.count(old))
    return src.replace(old, new)


def with_table(src=GUIDED, table=TABLE):
    return mutate(src, "The synthetic executive result.\n", "The synthetic executive result.\n\n" + table)


class RenderCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="uo-build-test-")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def reset_tmp(self):
        """Gives each subtest an empty directory, so one subtest's output cannot
        decide the next one's result."""
        shutil.rmtree(self.tmp)
        os.makedirs(self.tmp)

    def render(self, src, local_css=None, name="doc"):
        path = os.path.join(self.tmp, name + ".md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(src)
        css_path = None
        if local_css is not None:
            css_path = os.path.join(self.tmp, name + ".local.css")
            with open(css_path, "w", encoding="utf-8") as f:
                f.write(local_css)
        out = os.path.join(self.tmp, name + ".html")
        man = os.path.join(self.tmp, name + ".MANIFEST.md")
        result = build.render(path, out, man, UO_COMMIT, css_path)
        with open(out, encoding="utf-8") as f:
            result["html"] = f.read()
        with open(man, encoding="utf-8") as f:
            result["manifest_text"] = f.read()
        return result

    def fails(self, src, pattern, local_css=None):
        with self.assertRaises(build.BuildError) as cm:
            self.render(src, local_css=local_css, name="neg")
        self.assertRegex(str(cm.exception), pattern)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "neg.html")))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "neg.MANIFEST.md")))
        return str(cm.exception)


class Positives(RenderCase):
    def test_guided_review_baseline(self):
        r = self.render(with_table())
        h = r["html"]
        self.assertEqual(r["parts"], ["01", "02", "03", "04", "06", "08", "10"])
        self.assertIn('<section data-uo-part="03" id="uo-part-03" class="doc-section">', h)
        self.assertIn('<div data-uo-role="question" data-uo-central="true" class="doc-section">', h)
        self.assertIn('<div data-uo-role="finding" class="doc-section">', h)
        for cls in ("question-detail", "evidence", "provenance"):
            self.assertIn('<details data-uo-disclose="%s" class="uo-details %s"><summary><span class="surface-disclosure-label">'
                          % (cls, build.DISCLOSURE), h)
        self.assertEqual(r["counts"], {"questions": 2, "findings": 1, "disclosures": 3, "tables": 1, "quotations": 0,
                                       "callouts": 0, "framing": 0, "synthesis": 0, "structures": 0,
                                       "authored_case": 0, "annotation_rows": 0, "annotation_lists": 0,
                                       "annotation_notes": 0, "passage_marks": 0, "cell_items": 0,
                                       "annotation_ranges": 0, "item_hosts": 0, "document_records": 0})

    def test_confirmation_baseline_generates_01_and_10(self):
        r = self.render(CONFIRMATION)
        self.assertEqual(r["parts"], ["01", "02", "07", "10"])
        h = r["html"]
        self.assertIn('<section data-uo-part="01" id="uo-part-01" class="doc-section">\n<div class="uo-status-rail">', h)
        self.assertRegex(h, r'<section data-uo-part="10" id="uo-part-10" class="doc-section">\n<footer class="uo-foot">')

    def test_all_ten_parts_render_in_order(self):
        src = GUIDED
        src = mutate(src, ":::part 06\n", ":::part 05\nSynthetic finding index.\n:::\n\n:::part 06\n")
        src = mutate(src, ":::part 08\n", ":::part 06\n:::finding\nA second finding.\n:::\n:::\n\n"
                                             ":::part 07\nSynthetic prior-position delta.\n:::\n\n:::part 08\n")
        src = mutate(src, ":::part 10\n", ":::part 09\nSynthetic response format.\n:::\n\n:::part 10\n")
        r = self.render(src)
        self.assertEqual(r["parts"], ["01", "02", "03", "04", "05", "06", "06", "07", "08", "09", "10"])
        self.assertEqual(re.findall(r'<section data-uo-part="(\d\d)" id="uo-part-\d\d(?:-\d+)?" class="doc-section">', r["html"]),
                         r["parts"])
        self.assertEqual(re.findall(r'<section data-uo-part="\d\d" id="([a-z0-9-]+)" class="doc-section">', r["html"]),
                         ["uo-part-01", "uo-part-02", "uo-part-03", "uo-part-04", "uo-part-05", "uo-part-06",
                          "uo-part-06-2", "uo-part-07", "uo-part-08", "uo-part-09", "uo-part-10"])
        self.assertEqual(r["counts"]["findings"], 2)

    def test_ordered_list_start_and_link_title_allowed(self):
        src = mutate(GUIDED, "The synthetic executive result.\n",
                     "The synthetic executive result.\n\n3. third\n4. fourth\n\n"
                     "[a link](https://example.org/x \"Synthetic title\")\n")
        h = self.render(src)["html"]
        self.assertIn('<ol start="3">', h)
        self.assertIn('<a class="surface-text-link" href="https://example.org/x" title="Synthetic title">a link</a>', h)

    def test_N48_roles_applied_to_every_cell(self):
        h = self.render(with_table())["html"]
        cells = re.findall(r"<(th|td)( [^>]*)?>", h)
        self.assertEqual(len(cells), 12)
        roles = re.findall(r'<t[hd] class="[a-z- ]+" data-uo-cell="([a-z]+)"[ >]', h)
        self.assertEqual(roles, ["key", "text", "num", "status"] * 3)

    def test_N18_repeated_06_allowed(self):
        src = mutate(GUIDED, ":::part 08\n", ":::part 06\n:::finding\nA second finding.\n:::\n:::\n\n:::part 08\n")
        r = self.render(src)
        self.assertEqual(r["parts"].count("06"), 2)

    def test_N6_colons_inside_fenced_code_are_code(self):
        src = mutate(GUIDED, "The synthetic executive result.\n",
                     "The synthetic executive result.\n\n```text\n:::part 09\n:::\n```\n")
        h = self.render(src)["html"]
        self.assertIn('<pre class="doc-pre">:::part 09\n:::\n</pre>', h)

    def test_N35_tags_in_code_pass(self):
        src = mutate(GUIDED, "The synthetic executive result.\n",
                     "The synthetic executive result, `<div>` in a span.\n\n```\n<div>x</div>\n```\n\n"
                     "Indented:\n\n    <span>y</span>\n")
        h = self.render(src)["html"]
        self.assertIn('<code class="doc-code">&lt;div&gt;</code>', h)
        self.assertIn("&lt;div&gt;x&lt;/div&gt;", h)
        self.assertIn("&lt;span&gt;y&lt;/span&gt;", h)

    def test_N68_import_and_marker_text_in_body_render(self):
        src = mutate(GUIDED, "The synthetic executive result.\n",
                     "The synthetic executive result: `@import` and `@@X@@` and `<link>`.\n")
        h = self.render(src)["html"]
        self.assertIn('<code class="doc-code">@import</code>', h)
        self.assertIn('<code class="doc-code">@@X@@</code>', h)

    def test_meta_header_drives_masthead_rail_and_title(self):
        h = self.render(GUIDED)["html"]
        self.assertIn("<title>Synthetic guided review</title>", h)
        self.assertIn('<span class="doc-label"><strong>synthetic fixture</strong></span>'
                      '<span class="uo-status-rail__sep"></span><span class="doc-label">renderer test</span>'
                      '<span class="uo-status-rail__sep"></span><span class="doc-label">guided-review</span>'
                      '<span class="uo-status-rail__sep"></span><span class="doc-label">R1</span>', h)
        self.assertIn('<h1 class="doc-title">Synthetic guided review</h1>', h)
        self.assertIn('<dt class="doc-label">id</dt><dd class="doc-meta">SYN-GR-001</dd><dt class="doc-label">kind</dt>'
                      '<dd class="doc-meta">guided-review</dd><dt class="doc-label">round</dt><dd class="doc-meta">R1</dd>', h)
        self.assertNotIn("approv", h.split("<body>")[1].lower())

    def test_N66_title_escaped_and_literal(self):
        src = mutate(GUIDED, "title: Synthetic guided review\n", "title: A <b> & \\1 \\g<0> title\n")
        h = self.render(src)["html"]
        self.assertIn("<title>A &lt;b&gt; &amp; \\1 \\g&lt;0&gt; title</title>", h)
        self.assertIn('<h1 class="doc-title">A &lt;b&gt; &amp; \\1 \\g&lt;0&gt; title</h1>', h)

    def test_N67_seal_line_verified_and_never_unknown(self):
        r = self.render(GUIDED)
        foot = re.search(r'<footer class="uo-foot">.*?</footer>', r["html"], flags=re.S).group(0)
        self.assertNotIn("unknown", foot)
        dep = build.verify_dependencies()
        self.assertIn('design-system-ASK tokens and document register <code class="doc-code">%s</code>' % dep["commit"][:7], foot)
        self.assertIn('urban-observatory <code class="doc-code">%s</code> (declared)' % UO_COMMIT[:7], foot)

    def test_local_css_hook_and_emission(self):
        src = mutate(GUIDED, ":::finding\n", ":::finding local=ctl\n")
        css = "main.uo-md .uo-local-ctl p,\nmain.uo-md .uo-local-ctl li { color: var(--fg-2); }\n"
        r = self.render(src, local_css=css)
        h = r["html"]
        self.assertIn('<div data-uo-role="finding" class="doc-section uo-local-ctl">', h)
        styles = re.findall(r"<style>(.*?)</style>", h, flags=re.S)
        self.assertEqual(len(styles), 3)
        self.assertEqual(styles[2], css)
        self.assertIn(hashlib.sha256(css.encode()).hexdigest(), r["manifest_text"])

    def test_F7_embedded_local_css_block_hashes_to_the_manifest_row(self):
        src = mutate(GUIDED, ":::finding\n", ":::finding local=ctl\n")
        css = "main.uo-md .uo-local-ctl p { color: var(--fg-2); }\r\nmain.uo-md .uo-local-ctl li { color: var(--fg-2); }"
        r = self.render(src, local_css=css)
        with open(r["out"], "rb") as f:
            out_bytes = f.read()
        blocks = re.findall(rb"<style>(.*?)</style>", out_bytes, flags=re.S)
        self.assertEqual(len(blocks), 3)
        row = re.search(r"## Local CSS\n\n\| Field \| Value \|\n\| --- \| --- \|\n\| file \| `[^`]+` \|\n"
                        r"\| bytes \| `\d+` \|\n\| sha256 \| `([0-9a-f]{64})` \|", r["manifest_text"])
        self.assertIsNotNone(row)
        self.assertEqual(hashlib.sha256(blocks[2]).hexdigest(), row.group(1))

    def test_local_hook_without_css_allowed(self):
        src = mutate(GUIDED, ":::part 02\n", ":::part 02 local=wide-a\n")
        h = self.render(src)["html"]
        self.assertIn('<section data-uo-part="02" id="uo-part-02" class="doc-section uo-local-wide-a">', h)
        self.assertEqual(len(re.findall(r"<style>", h)), 2)

    def test_manifest_emission(self):
        r = self.render(with_table())
        m = r["manifest_text"]
        with open(r["out"], "rb") as f:
            out_bytes = f.read()
        dep = build.verify_dependencies()
        self.assertIn("| commit | `%s` |" % dep["commit"], m)
        for entry in dep["files"]:
            self.assertIn("| `%s` | %d | `%s` |" % (entry["path"], entry["bytes"], entry["sha256"]), m)
        self.assertIn("| sha256 | `%s` |" % hashlib.sha256(out_bytes).hexdigest(), m)
        self.assertIn("| content sha256 | `%s` |" % r["content_sha256"], m)
        self.assertIn("| markdown | `3.8.2` |", m)
        self.assertIn("| commit (declared, not verified by the renderer) | `%s` |" % UO_COMMIT, m)
        self.assertIn("| extracted tree digest | `%s` |" % build.tree_digest(HERE), m)
        self.assertIn("| parts, in order | `01 02 03 04 06 08 10` |", m)
        self.assertIn("| local CSS | `none` |", m)
        self.assertIn("| pin checks | `not performed by the renderer; run from the clone` |", m)
        prose = " ".join(m.split())
        self.assertNotIn("hashed from the bytes embedded in the output", prose)
        self.assertIn("hashed from the vendored bytes the render read", prose)
        self.assertIn("The fonts are embedded as base64 of those same bytes.", prose)
        self.assertIn("its font `src` declarations rewritten to `data:` URIs, so its embedded text is not byte-equal "
                      "to the hashed file", prose)

    def test_content_sha_excludes_only_the_seal_line(self):
        a = self.render(GUIDED, name="a")
        with mock.patch.object(build, "datetime") as dt:
            import datetime as real
            dt.now.return_value = real.datetime(2030, 1, 1, tzinfo=real.timezone.utc)
            b = self.render(GUIDED, name="b")
        self.assertEqual(a["content_sha256"], b["content_sha256"])
        c = self.render(mutate(GUIDED, "The whole synthetic register.", "The whole synthetic register!"), name="c")
        self.assertNotEqual(a["content_sha256"], c["content_sha256"])

    def test_output_passes_allowlist_and_is_self_contained(self):
        h = self.render(with_table())["html"]
        build.check_final_html(h, 2)
        self.assertNotIn("<link", h)
        self.assertEqual(re.findall(r"url\(['\"]?fonts/", h), [])
        self.assertEqual(len(re.findall(r"url\('data:font/woff2;base64,", h)), 4)
        self.assertNotIn("data-theme", h.split("</head>")[1])
        self.assertIn('<html lang="en">', h)


class Grammar(RenderCase):
    def test_N1_unclosed_container(self):
        self.fails(mutate(GUIDED, "Synthetic provenance block.\n:::\n:::\n", "Synthetic provenance block.\n:::\n"),
                   r"unclosed container :::part 10 \(line \d+\) at end of file")

    def test_N1b_unclosed_fence(self):
        self.fails(mutate(GUIDED, "The synthetic executive result.\n", "The synthetic executive result.\n\n```\ncode\n"),
                   r"line \d+: unclosed fenced code block")

    def test_N2_stray_close(self):
        self.fails(mutate(GUIDED, ":::part 02\n", ":::\n:::part 02\n"), r"line \d+: stray ':::' closes nothing")

    def test_N3_unknown_kind(self):
        self.fails(mutate(GUIDED, ":::finding\n", ":::card\n"), r"unknown container kind 'card'")

    def test_N4_unknown_token(self):
        self.fails(mutate(GUIDED, ":::finding\n", ":::finding status=open\n"), r"unknown token 'status=open' on :::finding")

    def test_N5_repeated_token(self):
        self.fails(mutate(GUIDED, ":::question central\n", ":::question central central\n"),
                   r"repeated token 'central' on :::question")

    def test_N7_meta_not_first(self):
        self.fails("Intro line.\n\n" + GUIDED, r"line 1: the source must begin with a :::meta block")

    def test_N7b_meta_elsewhere(self):
        self.fails(mutate(GUIDED, ":::part 02\n", ":::meta\n:::\n:::part 02\n"), r":::meta is not allowed here")

    def test_N8_unknown_meta_key_status(self):
        self.fails(mutate(GUIDED, "round: R1\n", "round: R1\nstatus: open\n"), r"unknown meta key 'status'")

    def test_N9_unknown_meta_key_approval(self):
        self.fails(mutate(GUIDED, "round: R1\n", "round: R1\napproval: granted\n"), r"unknown meta key 'approval'")

    def test_N10_repeated_meta_key(self):
        self.fails(mutate(GUIDED, "round: R1\n", "round: R1\nround: R2\n"), r"meta key 'round' repeated")

    def test_N11_empty_meta_value(self):
        self.fails(mutate(GUIDED, "round: R1\n", "round: \n"), r"meta key 'round' has an empty value")

    def test_N11e_invisible_meta_value(self):
        values = {
            "title": "Synthetic guided review",
            "id": "SYN-GR-001",
            "round": "R1",
            "classification": "synthetic fixture",
            "audience": "renderer test",
        }
        for key, original in values.items():
            for value in ("\u200b", "\u2060", "\u3164", "\u2800", "\u0301"):
                with self.subTest(key=key, value=repr(value)):
                    self.reset_tmp()
                    source = mutate(
                        GUIDED, "%s: %s\n" % (key, original),
                        "%s: %s\n" % (key, value))
                    self.fails(source, r"meta key '%s' has no visible text" % key)

    def test_N11b_multiline_meta_value(self):
        self.fails(mutate(GUIDED, "round: R1\n", "round: R1\n  continued\n"), r"is not 'key: value' on one line")

    def test_N11c_missing_meta_key(self):
        self.fails(mutate(GUIDED, "audience: renderer test\n", ""), r"meta key 'audience' is required")

    def test_N11d_title_too_long(self):
        self.fails(mutate(GUIDED, "title: Synthetic guided review\n", "title: " + "x" * 201 + "\n"),
                   r"meta title is longer than 200")

    def test_malformed_fence_opening(self):
        self.fails(mutate(GUIDED, "The synthetic executive result.\n",
                          "The synthetic executive result.\n\n```two words\nx\n```\n"),
                   r"malformed fenced-code opening line")

    def test_unterminated_quote(self):
        self.fails(mutate(GUIDED, '"Field-level evidence"', '"Field-level evidence'), r"malformed container token")


class Parts(RenderCase):
    def test_N12_no_kind(self):
        self.fails(mutate(GUIDED, "kind: guided-review\n", ""), r"K1: the document declares no kind")

    def test_N13_kind_outside_set(self):
        self.fails(mutate(GUIDED, "kind: guided-review\n", "kind: blind-baseline\n"), r"K1: kind 'blind-baseline' has no profile")

    def test_N14_required_part_missing_guided_review(self):
        for number in ("02", "04", "08"):
            with self.subTest(part=number):
                start = GUIDED.index(":::part %s\n" % number)
                end = GUIDED.index(":::part ", start + 1)
                src = GUIDED[:start] + GUIDED[end:]
                self.fails(src, r"K2: kind guided-review requires part %s, which is missing" % number)

    def test_N14_required_part_missing_confirmation(self):
        start = CONFIRMATION.index(":::part 07\n")
        self.fails(CONFIRMATION[:start], r"K2: kind confirmation requires part 07, which is missing")

    def test_N15_empty_part(self):
        self.fails(mutate(GUIDED, "The synthetic executive result.\n", "\n"), r"K3: part 04 at line \d+ is empty")

    def test_N15b_empty_role_container(self):
        self.fails(mutate(GUIDED, "A non-central question prompt.\n\n:::disclose question-detail \"Question detail\"\n"
                                  "The non-central question's detail.\n:::\n", ""),
                   r":::question \(line \d+\) is empty")

    def test_N16_out_of_order_historical_order(self):
        start03 = GUIDED.index(":::part 03\n")
        start04 = GUIDED.index(":::part 04\n")
        start06 = GUIDED.index(":::part 06\n")
        src = GUIDED[:start03] + GUIDED[start04:start06] + GUIDED[start03:start04] + GUIDED[start06:]
        self.fails(src, r"K4: part 03 at line \d+ is out of order \(after part 04\)")

    def test_N17_repeated_part_02(self):
        self.fails(mutate(GUIDED, ":::part 03\n", ":::part 02\nAgain.\n:::\n\n:::part 03\n"),
                   r"K5: part 02 repeated at line \d+; only 06 may repeat")

    def test_N19_text_outside_parts(self):
        self.fails(mutate(GUIDED, ":::part 02\n", "Loose text.\n\n:::part 02\n"),
                   r"K8: line \d+ is content outside the ten parts")

    def test_N19b_fenced_block_before_parts(self):
        self.fails(mutate(GUIDED, ":::part 01\n", "~~~\nDROPPED :::part 99\n~~~\n\n:::part 01\n"),
                   r"K8: line \d+ is content outside the ten parts \(a fenced code block\)")

    def test_N19c_fenced_block_after_parts(self):
        self.fails(GUIDED + "\n```text\nDROPPED-AFTER-PARTS\n```\n",
                   r"K8: line \d+ is content outside the ten parts \(a fenced code block\)")

    def test_N15c_part_with_only_a_reference_definition(self):
        self.fails(mutate(GUIDED, "The synthetic executive result.\n", "[r]: https://a.example\n"),
                   r"K3: part 04 at line \d+ is empty")

    INVISIBLE = [
        ("U+200B zero width space", "\u200b"),
        ("&#8203; entity", "&#8203;"),
        ("U+3164 hangul filler", "\u3164"),
        ("U+2800 braille pattern blank", "\u2800"),
        ("U+FEFF zero width no-break space", "\ufeff"),
        ("U+2060 word joiner", "\u2060"),
        ("**U+200B** emphasis", "**\u200b**"),
        ("U+0301 combining mark alone", "\u0301"),
    ]

    def test_F3_invisible_only_part_is_empty(self):
        for label, text in self.INVISIBLE:
            with self.subTest(text=label):
                self.reset_tmp()
                self.fails(mutate(GUIDED, "The synthetic executive result.\n", text + "\n"),
                           r"K3: part 04 at line \d+ is empty")

    def test_F3_invisible_only_finding_is_empty(self):
        self.fails(mutate(GUIDED, ":::part 08\n", ":::part 06\n:::finding\n\u200b\n:::\n:::\n\n:::part 08\n"),
                   r":::finding \(line \d+\) is empty")

    def test_F3_visible_text_controls_pass(self):
        for label, text in (("letter", "a"), ("digit", "7"), ("punctuation only", "\u2014"),
                            ("letter with combining mark", "e\u0301")):
            with self.subTest(text=label):
                self.reset_tmp()
                self.render(mutate(GUIDED, "The synthetic executive result.\n", text + "\n"), name="ctl")

    def test_F3_invisible_disclose_summary(self):
        self.fails(mutate(GUIDED, '"Field-level evidence"', '"\u200b"'),
                   r":::disclose takes one non-empty quoted summary")

    def test_part_name_not_accepted(self):
        self.fails(mutate(GUIDED, ":::part 02\n", ":::part reviewer-brief\n"), r"unknown token 'reviewer-brief' on :::part")


class Roles(RenderCase):
    def test_N20_03_without_central(self):
        self.fails(mutate(GUIDED, ":::question central\n", ":::question\n"), r"K6: part 03 at line \d+ has 0 central questions")

    def test_N21_03_with_two_central(self):
        self.fails(mutate(GUIDED, ":::question\nA non-central", ":::question central\nA non-central"),
                   r"K7: :::disclose at line \d+ is inside the central question")
        src = mutate(GUIDED, "The bounded question set.\n",
                     "The bounded question set.\n\n:::question central\nA second central prompt.\n:::\n")
        self.fails(src, r"K6: part 03 at line \d+ has 2 central questions")

    def test_N22_question_outside_03(self):
        self.fails(mutate(GUIDED, "The synthetic executive result.\n",
                          "The synthetic executive result.\n\n:::question\nStray.\n:::\n"),
                   r":::question is allowed directly inside :::part 03 only")

    def test_N23_finding_outside_06(self):
        self.fails(mutate(GUIDED, "The synthetic executive result.\n",
                          "The synthetic executive result.\n\n:::finding\nStray.\n:::\n"),
                   r":::finding is allowed directly inside :::part 06 only")

    def test_N24_disclose_inside_central_question(self):
        src = mutate(GUIDED, "The central question's detail, visible.\n",
                     "The central question's detail, visible.\n\n:::disclose question-detail \"Hidden\"\nHidden detail.\n:::\n")
        self.fails(src, r"K7: :::disclose at line \d+ is inside the central question")

    def test_N25_disclose_first_child_of_finding(self):
        self.fails(mutate(GUIDED, "**Status:** open. Finding, significance and limit.\n\n", ""),
                   r"K7: :::disclose at line \d+ is the first child of :::finding")

    def test_N25c_disclose_after_only_a_reference_definition(self):
        self.fails(mutate(GUIDED, "**Status:** open. Finding, significance and limit.\n",
                          "[r]: https://a.example\n"),
                   r"K7: :::disclose at line \d+ is the first child of :::finding")

    def test_F3_disclose_after_only_an_invisible_line(self):
        self.fails(mutate(GUIDED, "**Status:** open. Finding, significance and limit.\n", "\u200b\n"),
                   r"K7: :::disclose at line \d+ is the first child of :::finding")

    def test_N25b_disclose_first_child_of_question(self):
        self.fails(mutate(GUIDED, "A non-central question prompt.\n\n", ""),
                   r"K7: :::disclose at line \d+ is the first child of :::question")

    def test_N26_disclose_evidence_outside_finding(self):
        self.fails(mutate(GUIDED, "The synthetic executive result.\n",
                          "The synthetic executive result.\n\n:::disclose evidence \"E\"\nEvidence.\n:::\n"),
                   r":::disclose evidence is allowed inside :::finding only")

    def test_N27_finding_inside_disclose(self):
        self.fails(mutate(GUIDED, "Field-level listing.\n", "Field-level listing.\n\n:::finding\nNested.\n:::\n"),
                   r"K7: :::finding at line \d+ sits inside :::disclose evidence")

    def test_N28_disclose_in_08(self):
        self.fails(mutate(GUIDED, "The whole synthetic register.\n",
                          "The whole synthetic register.\n\n:::disclose evidence \"More\"\nReduced.\n:::\n"),
                   r"K7: :::disclose at line \d+ is inside part 08")

    def test_N29_two_provenance_disclosures(self):
        self.fails(mutate(GUIDED, "Synthetic provenance block.\n:::\n",
                          "Synthetic provenance block.\n:::\n:::disclose provenance \"Again\"\nSecond.\n:::\n"),
                   r"part 10 carries at most one provenance disclosure")


DETAIL = (':::disclose detail "Optional detail"\n### A detail heading\n\nA detail paragraph.\n\n' + TABLE
          + "\n> A quoted passage.\n:::\n")


def without_part(src, number):
    start = src.index(":::part %s\n" % number)
    return src[:start] + src[src.index(":::part ", start + 1):]


class GuidedReviewDetail(RenderCase):
    """The guided-review profile, revised in place (README, "Kinds" and "What stays visible"): it requires 04 and 08,
    and its 04 may close per-claim detail after the visible reading. Synthetic sources only."""

    def test_GR1_profile_requires_04_and_08_only(self):
        self.assertEqual(build.KIND_PROFILES["guided-review"], ("04", "08"))
        r = self.render(without_part(without_part(GUIDED, "03"), "06"))
        self.assertEqual(r["parts"], ["01", "02", "04", "08", "10"])

    def test_GR2_detail_allowed_in_04_of_a_guided_review(self):
        src = in_04("## A short claim\n\nThe claim and the qualification it needs.\n\n" + DETAIL
                    + "\n## A second claim\n\n- The second claim, with its limit.\n\n"
                    + DETAIL.replace("Optional detail", "More detail"))
        r = self.render(src)
        h = r["html"]
        for summary in ("Optional detail", "More detail"):
            self.assertIn('<details data-uo-disclose="detail" class="uo-details %s"><summary><span '
                          'class="surface-disclosure-label">%s</span>' % (build.DISCLOSURE, summary), h)
        self.assertEqual(h.count('data-uo-disclose="detail"'), 2)
        self.assertNotRegex(h, r"<details[^>]* open")
        part = h[h.index('id="uo-part-04"'):h.index('id="uo-part-06"')]
        # the visible reading precedes its detail in the claim's own section; the detail's body is a section
        self.assertLess(part.index("The claim and the qualification it needs."), part.index('data-uo-disclose="detail"'))
        body = part[part.index('<div class="uo-details__body surface-disclosure-body doc-section">'):]
        self.assertIn('<div class="doc-section">\n<h3 class="doc-subsection-title">A detail heading</h3>', body)
        self.assertIn('<table class="doc-dense-table">', body)
        self.assertIn('<blockquote class="doc-quote">', body)
        self.assertEqual(r["counts"]["disclosures"], 5)
        build.check_final_html(h, 2)

    def test_GR2b_detail_after_its_sections_visible_block_and_without_finding_units(self):
        src = without_part(without_part(GUIDED, "03"), "06")
        for reading in ("The claim, as read.\n\n", TABLE + "\n", "> A quoted passage.\n\n",
                        ranged("review accepted: v1 · owner · this claim", "The claim, as read.") + "\n"):
            with self.subTest(reading=reading[:24]):
                self.reset_tmp()
                r = self.render(mutate(src, "The synthetic executive result.\n",
                                       "The synthetic executive result.\n\n## A claim\n\n" + reading + DETAIL))
                self.assertEqual(r["html"].count('data-uo-disclose="detail"'), 1)

    def test_GR2c_detail_takes_annotations(self):
        src = in_04("A claim.\n\n:::disclose detail \"Optional detail\"\nA record.\n\n:::annotate\nbasis: two copies\n:::\n\n"
                    + ranged("review declined: which reading · this record · owner", "A line {{mark accepted dn: as quoted}}.")
                    + "\n:::note dn\n:::annotate\nreview accepted: on “as quoted” · owner\n:::\n:::\n:::\n")
        r = self.render(src)
        detail = r["html"][r["html"].index('<details data-uo-disclose="detail"'):]
        detail = detail[:detail.index("</details>")]
        for piece in (RANGE_OPEN, passage("accepted", "dn", "as quoted"), 'id="uo-note-dn"', key_item("Basis", "two copies")):
            self.assertIn(piece, detail)

    def test_GR3_detail_refused_in_04_of_other_kinds(self):
        src = mutate(CONFIRMATION, ":::part 07\n", ":::part 04\nA result.\n\n" + DETAIL + ":::\n\n:::part 07\n")
        self.fails(src, r"line %d: :::disclose detail belongs to a guided-review document only; this document's kind "
                        r"is confirmation" % row_of(src, ":::disclose detail"))
        src = mutate(CONFIRMATION, "What changed against the synthetic earlier position.\n",
                     "What changed against the synthetic earlier position.\n\n" + DETAIL)
        self.fails(src, r"belongs to a guided-review document only; this document's kind is confirmation")

    def test_GR4_detail_refused_before_visible_content(self):
        for before in ("", "[r]: https://a.example\n\n", "\u200b\n\n"):
            with self.subTest(before=repr(before)):
                self.reset_tmp()
                src = mutate(GUIDED, "The synthetic executive result.\n", before + DETAIL)
                self.fails(src, r"K7: :::disclose at line %d is the first child of :::part 04 \(line \d+\); the visible "
                                r"reading it details must precede it" % row_of(src, ":::disclose detail"))

    def test_GR4b_detail_refused_after_a_heading_alone(self):
        # A heading is not the reading: the detail's own section, from its last heading, holds a visible block first.
        pattern = (r"K7: :::disclose at line %d follows no visible block in its own section of :::part 04 \(line \d+\); "
                   r"the visible reading it details, a paragraph, list, code block, table, quotation, callout, structure, "
                   r"range or panel after the section's heading, must precede it")
        part04 = ":::part 04\nThe synthetic executive result.\n"
        cases = [
            mutate(GUIDED, part04, ":::part 04\n## A claim\n\n" + DETAIL),
            in_04("## A claim\n\n" + DETAIL),
            in_04("## A claim\n\nThe claim, as read.\n\n### Its limit\n\n" + DETAIL),
            in_04("## A claim\n\n:::annotate\nbasis: owner-stated\n:::\n\n" + DETAIL),
            in_04("## A claim\n\n---\n\n" + DETAIL),
            in_04("## A claim\n\n" + DETAIL + "\n" + DETAIL.replace("Optional detail", "More detail")),
        ]
        for src in cases:
            with self.subTest(src=src[src.index(":::part 04"):][:90]):
                self.reset_tmp()
                self.fails(src, pattern % row_of(src, ":::disclose detail"))

    def test_GR8_detail_holds_no_request_for_a_judgment(self):
        # What the reviewer is asked to judge stays visible: Open question, Proposed and Correction requested never sit
        # in a guided review's closed detail, in a range, a prompt, a list, a note, a cell, an item host or a mark.
        def detail(body):
            return in_04("A claim.\n\n:::disclose detail \"Optional detail\"\nA record.\n\n" + body + ":::\n")
        cases = [
            (ranged("review open: which reading · this record · owner", "The record."), 2),
            (ranged("review proposed: a reading · this record · editor", "The record."), 2),
            (":::annotate\nreview open: the record below · owner\n:::\n\n"
             + ranged("review accepted: v1 · owner · this record", "The record."), 1),
            (":::annotate list\nitem: the record\nreview correction-requested: on its total · owner\n:::\n", 2),
            ("Words {{mark open dn: as quoted}}.\n\n:::note dn\n:::annotate\nreview open: whose copy · owner\n:::\n:::\n", 0),
            ("Words {{mark proposed dn: as quoted}}.\n\n:::note dn\n:::annotate\nreview proposed: a phrase · editor\n"
             ":::\n:::\n", 0),
            (CELL % "{{review open: carried · owner}}", 3),
            ("- {{review proposed: editor · this item}} A disclosed item.\n", 0),
        ]
        for body, k in cases:             # k: the asking line within body
            with self.subTest(body=body[:50]):
                self.reset_tmp()
                self.fails(detail(body), r"%s: an Open question, Proposed or Correction requested review item sits inside "
                                         r":::disclose detail \(%s\), which is closed" % (at(5 + k), at(2)))
        # Recorded judgments may sit there, and a request may sit in the visible reading before it.
        self.reset_tmp()
        h = self.render(in_04(ranged("review open: whether the record holds · the claim · owner", "A claim.")
                              + "\n:::disclose detail \"Optional detail\"\nA record.\n\n"
                              + ranged("review none: no production decision", "The record.") + "\n"
                              + CELL % "{{review declined: v1 · owner}}" + ":::\n"))["html"]
        self.assertEqual(h.count('data-uo-disclose="detail"'), 1)
        # Markup quoted in a code span is text, not a request.
        self.reset_tmp()
        self.render(in_04("A claim.\n\n:::disclose detail \"Optional detail\"\nA record citing "
                          "`<span class=\"doc-mark\" data-review=\"open\">` as markup.\n:::\n"))

    def test_GR5_detail_refused_in_08(self):
        src = mutate(GUIDED, "The whole synthetic register.\n", "The whole synthetic register.\n\n" + DETAIL)
        self.fails(src, r"K7: :::disclose at line %d is inside part 08" % row_of(src, ":::disclose detail"))

    def test_GR6_detail_refused_outside_04(self):
        cases = [
            (mutate(GUIDED, "What this synthetic document tests, and what not to judge.\n",
                    "What this synthetic document tests, and what not to judge.\n\n" + DETAIL), r"not :::part 02"),
            (mutate(GUIDED, "**Status:** open. Finding, significance and limit.\n",
                    "**Status:** open. Finding, significance and limit.\n\n" + DETAIL), r"not :::finding"),
            (in_04(":::callout\nA claim.\n\n" + DETAIL + ":::\n"), r"not :::callout"),
            (mutate(GUIDED, "Field-level listing.\n", "Field-level listing.\n\n" + DETAIL),
             r"K7: :::disclose at line \d+ sits inside :::disclose evidence"),
            (in_04(DETAIL.replace("A detail paragraph.\n", "A detail paragraph.\n\n" + DETAIL)),
             r"K7: :::disclose at line \d+ sits inside :::disclose detail"),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_GR7_disclosure_positions_follow_the_declared_parts(self):
        # The declared parts are the operative positions: moving one moves the rule (README, "What stays visible").
        with mock.patch.dict(build.DISCLOSE_PARTS, {"evidence": "05"}):
            self.fails(GUIDED, r"line %d: :::disclose evidence sits in part 05 only, not :::finding"
                       % row_of(GUIDED, ":::disclose evidence"))
        with mock.patch.dict(build.DISCLOSE_KINDS, {"detail": ("confirmation",)}):
            self.fails(in_04("A claim.\n\n" + DETAIL), r"belongs to a confirmation document only; this document's "
                                                         r"kind is guided-review")


class RawHtml(RenderCase):
    def neg(self, text, pattern):
        return self.fails(mutate(GUIDED, "The synthetic executive result.\n", text), pattern)

    def test_N30_block_tag(self):
        self.neg('<div class="x">block</div>\n', r"raw HTML block in source")

    def test_N31_inline_tag(self):
        self.neg("Result with <span>inline</span> tag.\n", r"raw inline HTML in source: '<span>'")

    def test_N32_comment(self):
        self.neg("<!-- hidden -->\n\nResult.\n", r"raw HTML block in source")

    def test_N32b_inline_comment(self):
        self.neg("Result <!-- c --> text.\n", r"raw inline HTML in source")

    def test_N33_html_in_table_cell(self):
        src = with_table(table=TABLE.replace("| a | first claim |", "| a | <b>first</b> claim |"))
        self.fails(src, r"raw inline HTML in source: '<b>'")

    def test_N34_backslash_lt(self):
        self.neg("\\<div> literal\n", r"raw (inline )?HTML")


class Allowlist(RenderCase):
    def neg(self, text, pattern):
        return self.fails(mutate(GUIDED, "The synthetic executive result.\n", text), pattern)

    def test_N36_image(self):
        self.neg("![alt](fig.png)\n", r"element <img> not allowed")

    def test_N37_relative_link(self):
        self.neg("[doc](other.html)\n", r"only https:// and http:// links are allowed")

    def test_N37b_fragment_link(self):
        self.neg("[doc](#part-02)\n", r"only https:// and http:// links are allowed")

    def test_N38_javascript_link(self):
        self.neg("[doc](javascript:alert(1))\n", r"only https:// and http:// links are allowed")

    def test_N38b_mailto_autolink(self):
        self.neg("<someone@example.org>\n", r"only https:// and http:// links are allowed")

    def test_N39_authored_h1(self):
        self.neg("# Authored heading\n", r"<h1> is the renderer's masthead title only")

    def test_N40_h5(self):
        self.neg("##### Deep heading\n", r"element <h5> not allowed")

    def test_N41_table_alignment_colons(self):
        src = with_table(table=TABLE.replace("|---|---|---|---|", "|---|---|--:|---|"))
        self.fails(src, r"attribute style='text-align: right;' not allowed on <th>")

    def test_N42_invalid_local_name_uppercase(self):
        self.fails(mutate(GUIDED, ":::finding\n", ":::finding local=Wide\n"), r"invalid local name 'Wide'")

    def test_N42b_injected_class_via_fence_attrs(self):
        self.neg("```{#x .uo-card}\ncode\n```\n", r"attribute id='x' not allowed on <pre>")

    def test_N43_emitted_classes_are_styled_or_declared_hooks(self):
        with open(build.TEMPLATE, encoding="utf-8") as f:
            uo_css = f.read().split("</head>")[0] + build.md_css(True)
        register_css = ""
        for rel in build.MODULES + build.STATE_MODULES:
            with open(os.path.join(HERE, "_dsa-surface", rel), encoding="utf-8") as f:
                register_css += f.read()

        def styled(c, css):
            return re.search(r"\." + re.escape(c) + r"(?![A-Za-z0-9_-])", css) is not None
        classes = sorted({c for sets in build.CLASS_SETS.values() for s in sets for c in s.split()})
        uo = [c for c in classes if c.startswith("uo-")]
        self.assertEqual(sorted(c for c in uo if not styled(c, uo_css)), sorted(build.STRUCTURAL_HOOKS))
        self.assertEqual([c for c in classes if not c.startswith("uo-") and not styled(c, register_css)], [])
        self.assertFalse(styled("uo-unstyled-role", uo_css))

    def test_allowlist_rejects_injected_output(self):
        h = self.render(GUIDED)["html"]
        bad = [
            (h.replace('<html lang="en">', '<html lang="en" data-theme="dark">'), r"<html> must be the root and carry lang only"),
            (h.replace("</head>", "<script></script></head>"), r"<script> not allowed in <head>"),
            (h.replace('<main class="uo-md doc-flow">', '<main class="uo-md doc-flow" id="x">'), r"attribute id='x' not allowed on <main>"),
            (h.replace('<p class="doc-body">Synthetic locator line.</p>', '<p class="doc-body" onclick="x()">Synthetic locator line.</p>'),
             r"attribute onclick"),
            (h.replace("</style>", "@import url(x.css);</style>", 1), r"CSS contains @import"),
            (h.replace("</style>", 'p { background-image: image-set("https://x.invalid/a.png" 1x); }</style>', 1),
             r"CSS contains image-set\(, which can load a resource"),
            (h.replace('<p class="doc-body">Synthetic locator line.</p>', '<p class="caption">Synthetic locator line.</p>'),
             r"class 'caption' not allowed on <p>"),
            (h.replace('<p class="doc-body">Synthetic locator line.</p>', '<p>Synthetic locator line.</p>'),
             r"an unclassed <p> is a quotation's paragraph only"),
        ]
        for doc, _ in bad:
            self.assertNotEqual(doc, h)
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                with self.assertRaises(build.BuildError) as cm:
                    build.check_final_html(doc, 2)
                self.assertRegex(str(cm.exception), pattern)


class Tables(RenderCase):
    def test_N44_table_without_container(self):
        self.fails(with_table(table=TABLE.replace(":::table dense key text num status\n", "").replace("| closed |\n:::\n", "| closed |\n")),
                   r"a pipe table must be wrapped in :::table")

    def test_N45_role_count_differs(self):
        self.fails(with_table(table=TABLE.replace("key text num status", "key text num")),
                   r":::table declares 3 roles for 4 columns")

    def test_N46_role_outside_set(self):
        self.fails(with_table(table=TABLE.replace("key text num status", "key text date status")),
                   r"table role 'date' outside the closed set")

    def test_N47_two_tables_in_one_container(self):
        two = TABLE.replace("| b | second claim | 3 | closed |\n",
                            "| b | second claim | 3 | closed |\n\n| X | Y | Z | W |\n|---|---|---|---|\n| 1 | 2 | 3 | 4 |\n")
        self.fails(with_table(table=two), r"holds exactly one pipe table and nothing else \(found 2 tables\)")

    def test_N47b_text_beside_table(self):
        self.fails(with_table(table=TABLE.replace("| b | second claim | 3 | closed |\n",
                                                  "| b | second claim | 3 | closed |\n\nA stray paragraph.\n")),
                   r"holds exactly one pipe table and nothing else")


    def test_F2_body_row_with_more_cells_fails(self):
        src = with_table(table=TABLE.replace("| b | second claim | 3 | closed |\n",
                                             "| b | second claim | 3 | closed | dropped |\n"))
        self.fails(src, r"line \d+: table row has 5 cells; the header row has 4")

    def test_F2_body_row_with_fewer_cells_fails(self):
        src = with_table(table=TABLE.replace("| b | second claim | 3 | closed |\n", "| b | second claim | 3 |\n"))
        self.fails(src, r"line \d+: table row has 3 cells; the header row has 4")

    def test_F2_row_with_borders_under_a_borderless_header_fails(self):
        src = with_table(table=":::table key text\nRow | Claim\n---|---\n| a | first |\n:::\n")
        self.fails(src, r"line \d+: table row has 4 cells; the header row has 2")

    def test_F2_escaped_pipe_and_code_span_pipe_pass(self):
        src = with_table(table=TABLE.replace("| b | second claim | 3 | closed |\n",
                                             "| b | a \\| b and `x|y` | 3 | closed |\n"))
        h = self.render(src)["html"]
        self.assertIn('<td class="doc-table-cell" data-uo-cell="text" data-uo-label="Claim">'
                      '<span class="uo-cell-label doc-label">Claim</span>a | b and <code class="doc-code">x|y</code></td>', h)


class LocalCss(RenderCase):
    SRC = mutate(GUIDED, ":::finding\n", ":::finding local=ctl\n")

    def neg(self, css, pattern, src=None):
        return self.fails(src or self.SRC, pattern, local_css=css)

    def test_N49_unscoped_selector(self):
        self.neg("main.uo-md .uo-local-ctl p, body { color: red; }", r"selector 'body' is not scoped")

    def test_N49b_prefix_lookalike(self):
        self.neg("main.uo-md .uo-local-ctlx p { color: red; }", r"scope names not used by the source: ctlx")

    def test_N50_unused_hook_name(self):
        self.neg("main.uo-md .uo-local-other p { color: red; }", r"scope names not used by the source: other")

    def test_N51_media(self):
        self.neg("@media print { main.uo-md .uo-local-ctl p { color: red; } }", r"at-rules are not allowed")

    def test_N52_import(self):
        self.neg("@import 'x.css';", r"at-rules are not allowed")

    def test_N49c_sibling_combinator(self):
        self.neg("main.uo-md .uo-local-ctl ~ section { display: none; }", r"uses a sibling or column combinator")

    def test_N49d_adjacent_sibling_combinator(self):
        self.neg("main.uo-md .uo-local-ctl + section { display: none; }", r"uses a sibling or column combinator")

    def test_combinator_characters_inside_arguments_and_brackets_pass(self):
        css = "main.uo-md .uo-local-ctl li:nth-child(2n+1), main.uo-md .uo-local-ctl p[title~=a] { color: var(--fg-2); }"
        h = self.render(self.SRC, local_css=css)["html"]
        self.assertIn("nth-child(2n+1)", h)
        self.assertIn("p[title~=a]", h)

    def test_F1_quote_in_selector_fails(self):
        p = "main.uo-md .uo-local-ctl"
        cases = [
            ("bracket string escape", p + '[title="]"], body { display: none; }'),
            ("paren string escape", p + ':not([title=")"]), body { display: none; }'),
            ("is() string escape", p + ':is(")"), main { display: none; }'),
            ("bracket single quote", p + "[title=']'], .uo-shell { display: none; }"),
            ("balanced quoted attribute", p + ' p[title~="a"] { color: var(--fg-2); }'),
        ]
        for label, css in cases:
            with self.subTest(css=label):
                self.reset_tmp()
                self.neg(css, r"--local-css: a quote character in a selector is not allowed")

    def test_F1_unbalanced_selector_fails(self):
        p = "main.uo-md .uo-local-ctl"
        cases = [
            ("extra ]", p + "[title=a]], body { display: none; }"),
            ("extra )", p + ":not(.x)), body { display: none; }"),
            ("unclosed [", p + "[title=a, body { display: none; }"),
            ("unclosed (", p + ":not(.x, body { display: none; }"),
        ]
        for label, css in cases:
            with self.subTest(css=label):
                self.reset_tmp()
                self.neg(css, r"--local-css: unbalanced brackets or parentheses in selector")

    def test_F7_comment_in_local_css_fails(self):
        p = "main.uo-md .uo-local-ctl"
        for label, css in (("comment", "/* c */ " + p + " { color: red; }"),
                           ("comment opener in a string", p + ' { content: "/*"; } body { display:none } ' + p + ' { content: "*/"; }'),
                           ("comment closer alone", p + " { color: red; } */")):
            with self.subTest(css=label):
                self.reset_tmp()
                self.neg(css, r"--local-css: comments are not allowed")

    def test_local_hook_on_chrome_parts_fails(self):
        self.fails(mutate(GUIDED, ":::part 10\n", ":::part 10 local=seal\n"),
                   r":::part 10 carries generated masthead or seal chrome and takes no local= hook")
        self.fails(mutate(GUIDED, ":::part 01\n", ":::part 01 local=head\n"),
                   r":::part 01 carries generated masthead or seal chrome and takes no local= hook")

    def test_N53b_image_set_string(self):
        self.neg('main.uo-md .uo-local-ctl { background-image: image-set("https://x.invalid/a.png" 1x); }',
                 r"image-set\( is not allowed \(it can load a resource\)")

    def test_N53c_webkit_image_set_on_cursor(self):
        self.neg("main.uo-md .uo-local-ctl { cursor: -webkit-image-set('sidecar.png' 1x), auto; }",
                 r"-webkit-image-set\( is not allowed")

    def test_N53d_string_inside_any_function(self):
        self.neg('main.uo-md .uo-local-ctl { background-image: linear-gradient("x", red); }',
                 r"a quoted string inside a function is not allowed")

    def test_N53e_unterminated_string(self):
        self.neg('main.uo-md .uo-local-ctl::before { content: "x; }', r"unterminated string")

    def test_string_outside_functions_passes(self):
        css = 'main.uo-md .uo-local-ctl p { font-family: "JetBrains Mono", monospace; }'
        h = self.render(self.SRC, local_css=css)["html"]
        self.assertIn('"JetBrains Mono"', h)

    def test_N53_url(self):
        self.neg("main.uo-md .uo-local-ctl { background: URL(x.png); }", r"url\( is not allowed")

    def test_N54_backslash(self):
        self.neg("main.uo-md .uo-local-ctl\\,p { color: red; }", r"backslash escapes are not allowed")

    def test_N55_second_local_on_container(self):
        self.fails(mutate(GUIDED, ":::finding\n", ":::finding local=a local=b\n"),
                   r"repeated token: a container carries at most one local= hook")

    def test_N56_invalid_name(self):
        self.fails(mutate(GUIDED, ":::finding\n", ":::finding local=9x\n"), r"invalid local name '9x'")

    def test_N57_custom_property(self):
        self.neg("main.uo-md .uo-local-ctl { --fg-1: red; }", r"custom property declarations are not allowed")

    def test_N58_important(self):
        self.neg("main.uo-md .uo-local-ctl p { color: red !important; }", r"!important is not allowed")

    def test_style_close_in_css(self):
        self.neg("main.uo-md .uo-local-ctl p { content: '</style>'; }", r"'</' is not allowed")


class Provenance(unittest.TestCase):
    """N59-N61 run the renderer from a copy of the owner directory, so vendored
    bytes can be changed without touching the real tree."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="uo-build-prov-")
        self.owner = os.path.join(self.tmp, "artifact-template")
        shutil.copytree(HERE, self.owner, ignore=shutil.ignore_patterns("__pycache__"))
        self.src = os.path.join(self.tmp, "doc.md")
        with open(self.src, "w", encoding="utf-8") as f:
            f.write(GUIDED)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def run_copy(self, *extra, out="doc.html", manifest="doc.MANIFEST.md"):
        cmd = [sys.executable, "-B", os.path.join(self.owner, "build.py"), "--source", self.src,
               "--out", os.path.join(self.tmp, out), "--manifest", os.path.join(self.tmp, manifest),
               "--uo-commit", UO_COMMIT] + list(extra)
        return subprocess.run(cmd, capture_output=True, text=True)

    def assert_fails(self, r, pattern):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertRegex(r.stderr, pattern)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "doc.html")))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "doc.MANIFEST.md")))

    def test_copy_baseline_passes(self):
        r = self.run_copy()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_N59_token_css_byte_changed(self):
        p = os.path.join(self.owner, "_dsa-tokens", "colors_and_type.css")
        with open(p, "ab") as f:
            f.write(b"\n")
        self.assert_fails(self.run_copy(), r"dependency bytes do not match the manifest: _dsa-tokens/colors_and_type.css")

    def test_N60_font_byte_changed(self):
        p = os.path.join(self.owner, "_dsa-tokens", "fonts", "JetBrainsMono.woff2")
        with open(p, "r+b") as f:
            b = f.read(1)
            f.seek(0)
            f.write(bytes([b[0] ^ 1]))
        self.assert_fails(self.run_copy(), r"dependency bytes do not match the manifest: _dsa-tokens/fonts/JetBrainsMono.woff2")

    def test_N61_manifest_commit_row_missing(self):
        p = os.path.join(self.owner, "_dsa-tokens", "MANIFEST.md")
        with open(p, encoding="utf-8") as f:
            text = f.read()
        new = re.sub(r"^\| commit \| `[0-9a-f]{40}` \|\n", "", text, flags=re.M)
        self.assertNotEqual(new, text)
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        self.assert_fails(self.run_copy(), r"dependency manifest: no commit row")

    def test_N61d_manifest_short_row_disagrees(self):
        p = os.path.join(self.owner, "_dsa-tokens", "MANIFEST.md")
        with open(p, encoding="utf-8") as f:
            text = f.read()
        new = re.sub(r"^\| short \| `[0-9a-f]{7}` \|$", "| short | `0000000` |", text, flags=re.M)
        self.assertNotEqual(new, text)
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        self.assert_fails(self.run_copy(), r"dependency manifest: short '0000000' is not the commit's first 7 characters")

    def test_N61b_manifest_font_row_missing(self):
        p = os.path.join(self.owner, "_dsa-tokens", "MANIFEST.md")
        with open(p, encoding="utf-8") as f:
            text = f.read()
        new = re.sub(r"^\| fonts/InterVariable-Italic.woff2 sha256 .*\n", "", text, flags=re.M)
        self.assertNotEqual(new, text)
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        self.assert_fails(self.run_copy(), r"no sha256 row for fonts/InterVariable-Italic.woff2")

    def test_N61c_font_file_missing(self):
        os.unlink(os.path.join(self.owner, "_dsa-tokens", "fonts", "InterVariable.woff2"))
        self.assert_fails(self.run_copy(), r"dependency file missing: _dsa-tokens/fonts/InterVariable.woff2")

    def test_U3_wordmark_byte_changed(self):
        p = os.path.join(self.owner, "_dsa-tokens", "assets", "logo-ASK.svg")
        with open(p, "ab") as f:
            f.write(b"\n")
        self.assert_fails(self.run_copy(), r"dependency bytes do not match the manifest: _dsa-tokens/assets/logo-ASK.svg")

    def test_U3_wordmark_manifest_row_missing(self):
        p = os.path.join(self.owner, "_dsa-tokens", "MANIFEST.md")
        with open(p, encoding="utf-8") as f:
            text = f.read()
        new = re.sub(r"^\| assets/logo-ASK.svg sha256 .*\n", "", text, flags=re.M)
        self.assertNotEqual(new, text)
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        self.assert_fails(self.run_copy(), r"no sha256 row for assets/logo-ASK.svg")

    def test_U3_wordmark_file_missing(self):
        os.unlink(os.path.join(self.owner, "_dsa-tokens", "assets", "logo-ASK.svg"))
        self.assert_fails(self.run_copy(), r"dependency file missing: _dsa-tokens/assets/logo-ASK.svg")

    def test_U6_register_module_byte_changed(self):
        with open(os.path.join(self.owner, "_dsa-surface", "surface-document.css"), "ab") as f:
            f.write(b"\n")
        self.assert_fails(self.run_copy(), r"dependency bytes do not match the manifest: _dsa-surface/surface-document.css")

    def test_U6_register_module_missing(self):
        os.unlink(os.path.join(self.owner, "_dsa-surface", "surface-treatments.css"))
        self.assert_fails(self.run_copy(), r"dependency file missing: _dsa-surface/surface-treatments.css")

    def test_U6_register_manifest_row_missing(self):
        p = os.path.join(self.owner, "_dsa-surface", "MANIFEST.md")
        with open(p, encoding="utf-8") as f:
            text = f.read()
        new = re.sub(r"^\| surface-panel.css sha256 .*\n", "", text, flags=re.M)
        self.assertNotEqual(new, text)
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        self.assert_fails(self.run_copy(), r"register manifest: no sha256 row for surface-panel.css")

    def test_U6_register_manifest_missing(self):
        os.unlink(os.path.join(self.owner, "_dsa-surface", "MANIFEST.md"))
        self.assert_fails(self.run_copy(), r"register manifest unreadable")

    def test_U6_two_pins_fail(self):
        p = os.path.join(self.owner, "_dsa-surface", "MANIFEST.md")
        with open(p, encoding="utf-8") as f:
            text = f.read()
        new = re.sub(r"^(\| commit \| `)[0-9a-f]{40}(` \|)$", r"\g<1>" + "1" * 40 + r"\g<2>", text, flags=re.M)
        new = re.sub(r"^\| short \| `[0-9a-f]{7}` \|$", "| short | `1111111` |", new, flags=re.M)
        self.assertNotEqual(new, text)
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        self.assert_fails(self.run_copy(), r"the register manifest's commit 1{40} differs from the token manifest's")

    def test_U6_modules_are_sealed_verbatim_in_order_after_the_tokens(self):
        self.assertEqual(self.run_copy().returncode, 0)
        with open(os.path.join(self.tmp, "doc.html"), encoding="utf-8") as f:
            head = f.read().split("</head>")[0]
        at = head.index("--tracking-caption")          # inside the token CSS
        for rel in build.MODULES:
            with open(os.path.join(self.owner, "_dsa-surface", rel), encoding="utf-8") as f:
                module = f.read()
            i = head.find(module)
            self.assertGreater(i, at, rel)
            self.assertEqual(head.count(module), 1, rel)
            at = i
        self.assertLess(at, head.index("urban-observatory // review-document overlay"))

    def test_F6_planted_pycache_fails_before_it_is_imported(self):
        real = os.path.join(self.owner, "pin_check.py")
        with open(real, encoding="utf-8") as f:
            forged_source = f.read() + "\n\ndef tree_digest(root):\n    return '5' * 64\n"
        st = os.stat(real)
        code = compile(forged_source, real, "exec")
        data = bootstrap_external._code_to_timestamp_pyc(code, int(st.st_mtime), st.st_size)
        os.makedirs(os.path.join(self.owner, "__pycache__"))
        tag = sys.implementation.cache_tag
        with open(os.path.join(self.owner, "__pycache__", "pin_check.%s.pyc" % tag), "wb") as f:
            f.write(data)
        self.assert_fails(self.run_copy(), r"__pycache__ directory not allowed")

    def test_F6_loose_pyc_fails(self):
        with open(os.path.join(self.owner, "tests", "stray.pyc"), "wb") as f:
            f.write(b"\x00")
        self.assert_fails(self.run_copy(), r"compiled Python file not allowed")

    def test_N63_out_exists(self):
        open(os.path.join(self.tmp, "doc.html"), "w").close()
        r = self.run_copy()
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stderr, r"--out already exists")
        self.assertEqual(os.path.getsize(os.path.join(self.tmp, "doc.html")), 0)
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "doc.MANIFEST.md")))

    def test_N64_manifest_exists(self):
        open(os.path.join(self.tmp, "doc.MANIFEST.md"), "w").close()
        r = self.run_copy()
        self.assertEqual(r.returncode, 1)
        self.assertRegex(r.stderr, r"--manifest already exists")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "doc.html")))

    def test_title_flag_removed(self):
        r = self.run_copy("--title", "x")
        self.assertEqual(r.returncode, 2)
        self.assertIn("unrecognized arguments: --title", r.stderr)

    def test_uo_commit_must_be_40_hex(self):
        cmd = [sys.executable, "-B", os.path.join(self.owner, "build.py"), "--source", self.src,
               "--out", os.path.join(self.tmp, "doc.html"), "--manifest", os.path.join(self.tmp, "doc.MANIFEST.md"),
               "--uo-commit", "9d674a3"]
        r = subprocess.run(cmd, capture_output=True, text=True)
        self.assert_fails(r, r"--uo-commit must be 40 lowercase hex")


    def test_RS_review_semantics_module_byte_changed_fails_an_unannotated_document(self):
        # All seven _dsa-surface/ files are verified on every build, whether or not the document annotates.
        with open(os.path.join(self.owner, "_dsa-surface", "review-semantics.css"), "ab") as f:
            f.write(b"\n")
        self.assert_fails(self.run_copy(), r"dependency bytes do not match the manifest: _dsa-surface/review-semantics.css")

    def test_RS_state_module_missing(self):
        os.unlink(os.path.join(self.owner, "_dsa-surface", "spectral-state.css"))
        self.assert_fails(self.run_copy(), r"dependency file missing: _dsa-surface/spectral-state.css")

    def test_RS_state_module_manifest_row_missing(self):
        p = os.path.join(self.owner, "_dsa-surface", "MANIFEST.md")
        with open(p, encoding="utf-8") as f:
            text = f.read()
        new = re.sub(r"^\| evidence-state.css sha256 .*\n", "", text, flags=re.M)
        self.assertNotEqual(new, text)
        with open(p, "w", encoding="utf-8") as f:
            f.write(new)
        self.assert_fails(self.run_copy(), r"register manifest: no sha256 row for evidence-state.css")

    def test_RS_vendored_bytes_match_both_manifests(self):
        dep = build.verify_dependencies()
        self.assertEqual([f["path"] for f in dep["files"]][-7:],
                         ["_dsa-surface/" + x for x in build.MODULES + build.STATE_MODULES])
        for name in ("_dsa-tokens", "_dsa-surface"):
            fields, commit = build._manifest_fields(os.path.join(HERE, name, "MANIFEST.md"), name)
            self.assertEqual(commit, dep["commit"])
        with open(os.path.join(HERE, "_dsa-surface", "MANIFEST.md"), encoding="utf-8") as f:
            text = f.read()
        for rel in build.STATE_MODULES:
            with open(os.path.join(HERE, "_dsa-surface", rel), "rb") as f:
                self.assertIn("| %s sha256 | `%s` |" % (rel, hashlib.sha256(f.read()).hexdigest()), text)


class Atomicity(RenderCase):
    def test_N62_markdown_version_not_pin(self):
        with mock.patch.object(build.markdown, "__version__", "3.5.0"):
            self.fails(GUIDED, r"markdown 3.5.0 is installed; this renderer is pinned to markdown==3.8.2")

    def test_N65_no_partial_output_after_failure(self):
        real_link = os.link
        calls = []

        def link(src, dst):
            calls.append(dst)
            if len(calls) == 2:
                raise OSError("simulated failure placing the manifest")
            return real_link(src, dst)
        with mock.patch.object(build.os, "link", side_effect=link):
            with self.assertRaises(OSError):
                self.render(GUIDED, name="partial")
        self.assertEqual(len(calls), 2)
        self.assertEqual(sorted(os.listdir(self.tmp)), ["partial.md"])

    def test_N65b_failed_build_leaves_no_temp(self):
        self.fails(mutate(GUIDED, "kind: guided-review\n", "kind: other\n"), r"K1")
        self.assertEqual(sorted(os.listdir(self.tmp)), ["neg.md"])


def top_level_split(selectors):
    """A selector list split at its top-level commas: a comma inside :where(), :is(), :not() or :has() stays."""
    out, depth, cur = [], 0, []
    for ch in selectors:
        depth += {"(": 1, ")": -1}.get(ch, 0)
        if ch == "," and depth == 0:
            out.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    out.append("".join(cur))
    return out


def css_rules(css):
    """Parses the template's and MD_CSS's plain CSS into (media, selectors, declarations) triples.
    media is None outside @media; selectors are whitespace-normalized; declaration values too."""
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    rules = []

    def block(text, media):
        i = 0
        while True:
            j = text.find("{", i)
            if j < 0:
                return
            prelude = " ".join(text[i:j].split())
            if prelude.startswith(("@media", "@container")):
                depth, k = 1, j + 1
                while depth:
                    depth += {"{": 1, "}": -1}.get(text[k], 0)
                    k += 1
                block(text[j + 1:k - 1], prelude[1:] if prelude.startswith("@container") else prelude[len("@media"):].strip())
                i = k
                continue
            k = text.index("}", j)
            decls = {}
            for d in text[j + 1:k].split(";"):
                if ":" in d:
                    name, _, value = d.partition(":")
                    decls[name.strip()] = " ".join(value.split())
            rules.append((media, tuple(" ".join(x.split()) for x in top_level_split(prelude)), decls))
            i = k + 1
    block(css, None)
    return rules


def template_css():
    with open(build.TEMPLATE, encoding="utf-8") as f:
        head = f.read().split("</head>")[0]
    return re.search(r"<style>(.*)</style>", head, flags=re.S).group(1)



def specificity(sel):
    """(ids, classes/attrs/pseudo-classes, types) for a simple compound-descendant selector."""
    ids = len(re.findall(r"#[\w-]+", sel))
    cls = len(re.findall(r"\.[\w-]+|\[[^\]]+\]|:(?!:)[\w-]+", sel))
    typ = len(re.findall(r"(?:^|[\s>+~])([a-zA-Z][\w-]*)", sel))
    return (ids, cls, typ)

def rules_with(rules, selector, media=None):
    return [d for m, sels, d in rules if selector in sels and m == media]


U2_TABLE = """:::table dense key text num status "A <b> & caption"
| Row `id` | Claim &amp; *limit* | Count | State |
|---|---|---|---|
| a | first claim | 12 | open |
| b | second claim | 3 | closed |
:::
"""

# U2-R2: a header carrying a link and a header carrying inline code.
LINK_HEADER_TABLE = """:::table key text
| Row [spec](https://example.com/spec) | Claim `x|y` |
|---|---|
| a | first claim |
| b | second claim |
:::
"""


class ProfileRoles(RenderCase):
    """U2, as U6 carries it: the disclosure, numeric, key and caption roles are reachable from the renderer,
    now on the design-system disclosure treatment and the register's table roles."""

    def test_U2_disclosure_role_emitted(self):
        src = mutate(GUIDED, ':::disclose evidence "Field-level evidence"\n', ':::disclose evidence local=ev "Field-level evidence"\n')
        h = self.render(src)["html"]
        self.assertIn('<details data-uo-disclose="question-detail" class="uo-details %s"><summary>'
                      '<span class="surface-disclosure-label">Question detail</span>'
                      '<span class="surface-disclosure-indicator" aria-hidden="true">&#9660;</span></summary>\n'
                      '<div class="uo-details__body surface-disclosure-body doc-section">\n<div class="doc-prose">\n'
                      '<p class="doc-body">The non-central question\'s detail.</p>\n</div>\n</div>\n</details>' % build.DISCLOSURE, h)
        self.assertIn('<details data-uo-disclose="evidence" class="uo-details %s uo-local-ev"><summary>' % build.DISCLOSURE, h)
        self.assertEqual(len(re.findall(r'<details [^>]*class="uo-details[ "]', h)), 3)
        self.assertEqual(len(re.findall(r'<div class="uo-details__body surface-disclosure-body doc-section">', h)), 3)

    def test_U2_code_block_in_disclosure_emitted_in_the_body(self):
        src = mutate(GUIDED, "Field-level listing.\n", "Field-level listing.\n\n```text\nline\n```\n\n    indented line\n")
        h = self.render(src)["html"]
        self.assertIn('<div class="uo-details__body surface-disclosure-body doc-section">\n<div class="doc-prose">\n'
                      '<p class="doc-body">Field-level listing.</p>\n'
                      '<pre class="doc-pre">line\n</pre>\n<pre class="doc-pre">indented line\n</pre>\n</div>\n</div>', h)

    def test_U2_caption_emitted_and_escaped(self):
        h = self.render(with_table(table=U2_TABLE))["html"]
        self.assertIn('<table class="doc-dense-table">\n<caption class="doc-meta">A &lt;b&gt; &amp; caption</caption>\n<thead>', h)
        h = self.render(with_table(table=U2_TABLE.replace(":::table ", ":::table local=w ")), name="local")["html"]
        self.assertIn('<table class="doc-dense-table uo-local-w">\n<caption class="doc-meta">A &lt;b&gt; &amp; caption</caption>', h)
        h = self.render(with_table(table=U2_TABLE.replace(":::table dense ", ":::table local=w ")), name="narrative")["html"]
        self.assertIn('<table class="uo-local-w">\n<caption class="doc-meta">A &lt;b&gt; &amp; caption</caption>', h)
        h = self.render(with_table(), name="nocap")["html"]
        self.assertNotIn("<caption", h)

    def test_U2_every_body_cell_carries_its_header_text(self):
        h = self.render(with_table(table=U2_TABLE))["html"]
        self.assertIn('<th class="doc-label" data-uo-cell="key">Row <code class="doc-code">id</code></th>', h)
        self.assertIn('<td class="doc-table-cell" data-uo-cell="key" data-uo-label="Row id">'
                      '<span class="uo-cell-label doc-label">Row <code class="doc-code">id</code></span><strong>a</strong></td>', h)
        self.assertIn('<td class="doc-table-cell" data-uo-cell="text" data-uo-label="Claim &amp; limit">'
                      '<span class="uo-cell-label doc-label">Claim &amp; <em>limit</em></span>first claim</td>', h)
        self.assertIn('<td class="doc-table-cell" data-uo-cell="num" data-uo-label="Count">'
                      '<span class="uo-cell-label doc-label">Count</span>12</td>', h)
        self.assertIn('<td class="doc-table-cell" data-uo-cell="status" data-uo-label="State">'
                      '<span class="uo-cell-label doc-label">State</span>closed</td>', h)
        self.assertEqual(len(re.findall(r"<td [^>]*data-uo-label=", h)), 8)
        self.assertNotRegex(h, r"<th [^>]*data-uo-label=")

    def test_U2_R2_visible_label_element_keeps_header_links_and_code(self):
        # U2-R2: the label a reader actually sees at narrow widths is an element carrying the header
        # cell's own inline markup, not generated plain text, so a header's link stays an operable link
        # and its inline code stays code. One label element per body cell, each directly inside its <td>.
        h = self.render(with_table(table=LINK_HEADER_TABLE))["html"]
        self.assertIn('<span class="uo-cell-label doc-label">Row <a class="surface-text-link" href="https://example.com/spec">spec</a></span>', h)
        self.assertIn('<span class="uo-cell-label doc-label">Claim <code class="doc-code">x|y</code></span>', h)
        self.assertEqual(len(re.findall(r'<span class="uo-cell-label doc-label">', h)), 4)
        self.assertEqual(len(re.findall(r'<td [^>]*><span class="uo-cell-label doc-label">', h)), 4)
        # the operable link is reproduced in the body, not only in the header row
        self.assertEqual(len(re.findall(r'href="https://example\.com/spec"', h)), 3)
        build.check_final_html(h, 2)

    def test_U2_R2_a_dropped_visible_label_fails_the_build(self):
        # The visible label IS the U2-R2 guarantee, so its ABSENCE must fail the check, not only a wrong
        # label's text. Validating the span's text only when a span happens to be present leaves the
        # guarantee unenforced against the one regression that would actually remove the operation.
        h = self.render(with_table(table=LINK_HEADER_TABLE))["html"]
        build.check_final_html(h, 2)                                    # control: the real render passes
        one = re.search(r'<span class="uo-cell-label doc-label">.*?</span>', h, re.S)
        self.assertIsNotNone(one)
        with self.assertRaises(build.BuildError) as cm:                 # the span deleted outright
            build.check_final_html(h.replace(one.group(0), "", 1), 2)
        self.assertIn("without its <span class='uo-cell-label'>", str(cm.exception))
        with self.assertRaises(build.BuildError):                       # and a wrong label still fails
            build.check_final_html(h.replace(">Row <a", ">Rowx <a", 1), 2)

    def test_U2_caption_must_follow_the_roles(self):
        self.fails(with_table(table=U2_TABLE.replace('key text num status "A <b> & caption"', 'key "Cap" text num status')),
                   r":::table takes at most one quoted caption, after its column roles")

    def test_U2_one_caption_only(self):
        self.fails(with_table(table=U2_TABLE.replace('"A <b> & caption"', '"One" "Two"')),
                   r":::table takes at most one quoted caption, after its column roles")

    def test_U2_caption_needs_visible_text(self):
        self.fails(with_table(table=U2_TABLE.replace('"A <b> & caption"', '"​⠀"')),
                   r"a :::table caption must contain visible text")

    def test_U2_allowlist_rejects_broken_role_markup(self):
        h = self.render(with_table(table=U2_TABLE))["html"]
        one = ('<td class="doc-table-cell" data-uo-cell="num" data-uo-label="Count">'
               '<span class="uo-cell-label doc-label">Count</span>12</td>')
        p = '<p class="doc-body">Synthetic locator line.</p>'
        qd = 'class="uo-details %s"><summary><span class="surface-disclosure-label">Question detail' % build.DISCLOSURE
        bad = [
            (h.replace(one, '<td class="doc-table-cell" data-uo-cell="num"><span class="uo-cell-label doc-label">Count</span>12</td>'),
             r"<td> without data-uo-label"),
            (h.replace(one, one.replace('data-uo-label="Count"', 'data-uo-label="State"')),
             r"<td data-uo-label='State'> does not equal its column's header text 'Count'"),
            (h.replace(one, one.replace('data-uo-label="Count"', 'data-uo-label="Count "')),
             r"does not equal its column's header text"),
            (h.replace(one, one.replace('doc-label">Count</span>', 'doc-label">State</span>')),
             r"<span class='uo-cell-label'> text 'State' does not equal its column's header text 'Count'"),
            (h.replace(p, '<span class="uo-cell-label doc-label">x</span>'),
             r"class 'uo-cell-label' allowed only on a <span> directly inside <td>"),
            (h.replace('<th class="doc-label" data-uo-cell="num">', '<th class="doc-label" data-uo-cell="num" data-uo-label="Count">'),
             r"attribute data-uo-label='Count' not allowed on <th>"),
            (h.replace(qd, qd.split("><summary>")[0].replace('class="uo-details %s"' % build.DISCLOSURE, "") + "><summary>"
                       + qd.split("><summary>")[1]),
             r"<details> without class uo-details"),
            (h.replace(p, '<div class="uo-details__body surface-disclosure-body doc-section">x</div>'),
             r"class 'uo-details__body' allowed only on a <div> directly inside <details>"),
            (h.replace(p, '<caption class="doc-meta">x</caption>'), r"<caption> outside <table>"),
            (h.replace('<div class="uo-shell">', '<div class="uo-shell uo-local-x">'), r"class 'uo-shell uo-local-x' not allowed on <div>"),
            (h.replace(qd, qd.replace('class="uo-details ', 'class="uo-details uo-details ')),
             r"class 'uo-details uo-details surface-disclosure[^']*' not allowed on <details>"),
            (h.replace(qd, qd.replace('class="uo-details ', 'class="uo-local-x uo-details ')),
             r"class 'uo-local-x uo-details surface-disclosure[^']*' not allowed on <details>"),
            (h.replace('<table class="doc-dense-table">', '<table class="caption">'), r"class 'caption' not allowed on <table>"),
            (h.replace(p, '<p class="doc-body doc-body">Synthetic locator line.</p>'), r"class 'doc-body doc-body' not allowed on <p>"),
            (h.replace(one, one.replace('class="doc-table-cell"', 'class="doc-body"')),
             r"a dense table's cell is .doc-table-cell and a narrative table's is .doc-body"),
            (h.replace(p, '<p class="doc-body surface-emphasis-rail doc-label">Synthetic locator line.</p>'),
             r"class 'doc-body surface-emphasis-rail doc-label' not allowed on <p>"),
        ]
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                self.assertNotEqual(doc, h)
                with self.assertRaises(build.BuildError) as cm:
                    build.check_final_html(doc, 2)
                self.assertRegex(str(cm.exception), pattern)
        build.check_final_html(h, 2)


CASED_TABLE = """:::table dense key text num:authored-case status "Loads"
| Row | Claim | Power (mW) | State |
|---|---|---|---|
| a | first claim | 12 | open |
| b | second claim | 3 | closed |
:::
"""


class AuthoredCase(RenderCase):
    """R2: a header whose case carries meaning (mW is not MW). A column role may carry the one modifier
    :authored-case; that column's header and each body cell's label keep the author's case in
    span.uo-authored-case, declared to the rendered check as a profile with its exact count."""

    def test_R2_only_the_declared_column_keeps_its_case(self):
        r = self.render(with_table(table=CASED_TABLE))
        h = r["html"]
        self.assertIn('<th class="doc-label" data-uo-cell="num"><span class="uo-authored-case">Power (mW)</span></th>', h)
        self.assertIn('<th class="doc-label" data-uo-cell="key">Row</th>', h)
        self.assertIn('<th class="doc-label" data-uo-cell="text">Claim</th>', h)
        self.assertIn('<td class="doc-table-cell" data-uo-cell="num" data-uo-label="Power (mW)"><span class="uo-cell-label doc-label">'
                      '<span class="uo-authored-case">Power (mW)</span></span>12</td>', h)
        self.assertIn('<td class="doc-table-cell" data-uo-cell="text" data-uo-label="Claim"><span class="uo-cell-label doc-label">'
                      'Claim</span>first claim</td>', h)
        self.assertEqual(h.count('<span class="uo-authored-case">'), 3)          # the header and two body labels
        self.assertEqual(r["counts"]["authored_case"], 3)
        self.assertIn("| authored-case spans (headers and cell labels) | `3` |", r["manifest_text"])
        profiles = build.role_profiles(r["counts"])
        self.assertEqual([p["name"] for p in profiles], ["authored-case disclosure summary", "authored-case table header"])
        self.assertEqual(profiles[1]["selector"], ".uo-md .uo-authored-case")
        self.assertEqual(profiles[1]["expected_count"], 3)
        self.assertEqual(build.role_profiles({"disclosures": 0, "authored_case": 2})[0]["name"], "authored-case table header")
        self.assertEqual(build.role_profiles({"disclosures": 0, "authored_case": 0}), [])

    def test_R2_the_one_declaration_is_case_and_nothing_else(self):
        rules = [(sels, d) for m, sels, d in css_rules(build.md_css(True)) + css_rules(template_css())
                 if any("uo-authored-case" in sel for sel in sels)]
        self.assertEqual([(list(sels), d) for sels, d in rules], [([":where(.uo-md) :where(.uo-authored-case)"], {"text-transform": "none"})])

    def test_R2_emphasis_is_allowed_inside_an_authored_case_header(self):
        h = self.render(with_table(table=CASED_TABLE.replace("| Power (mW) |", "| Power (*mW*) |")))["html"]
        self.assertIn('<span class="uo-authored-case">Power (<em>mW</em>)</span></th>', h)

    def test_R2_refusals(self):
        for table, pattern in (
                (CASED_TABLE.replace("num:authored-case", "num:caps"), r"table role modifier 'caps': the one modifier is 'authored-case'"),
                (CASED_TABLE.replace("num:authored-case", "num:"), r"table role modifier '': the one modifier is 'authored-case'"),
                (CASED_TABLE.replace("num:authored-case", "nums:authored-case"), r"table role 'nums' outside the closed set"),
                (CASED_TABLE.replace(":::table dense ", ":::table dense:authored-case "), r"'dense' takes no modifier"),
                (CASED_TABLE.replace("| Power (mW) |", "| Power (`mW`) |"), r"column 3's header is declared authored-case and holds text and inline emphasis only"),
                (CASED_TABLE.replace("| Power (mW) |", "| [mW](https://example.org/) |"), r"holds text and inline emphasis only"),
                (CASED_TABLE.replace("| Power (mW) |", "| &nbsp; |"), r"column 3's header is declared authored-case and must contain visible text")):
            with self.subTest(pattern=pattern):
                self.fails(with_table(table=table), pattern)

    def test_R2_allowlist_places_the_span_by_column(self):
        h = self.render(with_table(table=CASED_TABLE))["html"]
        cased_label = '<span class="uo-cell-label doc-label"><span class="uo-authored-case">Power (mW)</span></span>12</td>'
        plain_label = 'data-uo-label="Claim"><span class="uo-cell-label doc-label">Claim</span>first claim</td>'
        p = '<p class="doc-body">Synthetic locator line.</p>'
        bad = [
            (h.replace(cased_label, '<span class="uo-cell-label doc-label">Power (mW)</span>12</td>'),
             r"a cell label in an authored-case column lacks its authored-case span"),
            (h.replace(plain_label, 'data-uo-label="Claim"><span class="uo-cell-label doc-label"><span class="uo-authored-case">Claim</span>'
                                    '</span>first claim</td>'),
             r"an authored-case cell label in a column whose header is not authored-case"),
            (h.replace(p, '<p class="doc-body"><span class="uo-authored-case">Synthetic locator line.</span></p>'),
             r"class 'uo-authored-case' allowed only directly in a header cell or in a cell's label"),
            (h.replace('<span class="uo-authored-case">Power (mW)</span></th>',
                       '<span class="uo-authored-case"><code class="doc-code">mW</code></span></th>'),
             r"an authored-case header holds text and inline emphasis only, not <code>"),
            (h.replace('<span class="uo-authored-case">Power (mW)</span></th>',
                       '<span class="uo-authored-case">Power (<em><code class="doc-code">mW</code></em>)</span></th>'),
             r"an authored-case header holds text and inline emphasis only, not <code>"),
        ]
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                self.assertNotEqual(doc, h)
                with self.assertRaisesRegex(build.BuildError, pattern):
                    build.check_final_html(doc, 2)

    def test_R2_local_css_may_not_reach_a_renderer_hook(self):
        src = with_table(table=CASED_TABLE.replace(":::table dense ", ":::table local=ctl dense "))
        hook, attr = r"names a renderer hook; it may name only its uo-local-<name> scope", r"selects by the class attribute"
        for css, pattern in (("main.uo-md .uo-local-ctl .uo-authored-case { font-size: 30px; }\n", hook),
                             ("main.uo-md .uo-local-ctl td .uo-cell-label { display: block; }\n", hook),
                             ("main.uo-md .uo-local-ctl :is(.uo-authored-case) { font-size: 30px; }\n", hook),
                             ("main.uo-md .uo-local-ctl [title~=UO-authored-case] { font-size: 30px; }\n", hook),
                             ("main.uo-md .uo-local-ctl [class~=authored-case] { font-size: 30px; }\n", attr),
                             ("main.uo-md .uo-local-ctl [ CLASS*=authored] { font-size: 30px; }\n", attr),
                             ("main.uo-md .uo-local-ctl [*|class$=authored-case] { font-size: 30px; }\n", attr),
                             ("main.uo-md .uo-local-ctl [|class*=authored] { font-size: 30px; }\n", attr),
                             ("main.uo-md .uo-local-ctl :is([*|class^=uo]) { font-size: 30px; }\n", attr)):
            with self.subTest(css=css):
                self.fails(src, pattern, local_css=css)
        ok = self.render(src, local_css="main.uo-md .uo-local-ctl td { padding: 2px; }\n", name="ok")["html"]
        self.assertIn('<table class="doc-dense-table uo-local-ctl">', ok)          # the positive case reaches the table
        self.assertIn("main.uo-md .uo-local-ctl td { padding: 2px; }", ok)


class Presentation(unittest.TestCase):
    """U6: the UO stylesheets are geometry. Every text style is a design-system register role; the checks
    here are on the UO rules' declarations. Computed presentation is the rendered check's (README,
    "Rendered conformance check")."""

    TYPE = ("font-family", "font-size", "font-weight", "line-height", "letter-spacing", "color", "text-transform",
            "font", "font-style", "font-variant-numeric")
    FOUNDATION_TOKENS = re.compile(r"^--(fg|line|bg|surface|shadow|ask|fs|fw|lh|tracking|space|radius)-")
    ROWS_CONTEXTS = ("(max-width: 960px)", "container uo-body (max-width: 1119.98px)", None)

    def setUp(self):
        # The fullest UO stylesheet, an annotating document's: MD_CSS and the passage buffer (build.md_css).
        self.md = css_rules(build.md_css(True))
        self.tpl = css_rules(template_css())

    @staticmethod
    def zero_specificity(sel):
        """True when sel is :where() groups, each with balanced parentheses, joined only by combinators."""
        i, rest = 0, []
        while i < len(sel):
            if sel.startswith(":where(", i):
                depth, j = 0, i + len(":where")
                while j < len(sel):
                    depth += {"(": 1, ")": -1}.get(sel[j], 0)
                    j += 1
                    if depth == 0:
                        break
                if depth:
                    return False
                i = j
            else:
                rest.append(sel[i])
                i += 1
        return ":where(" in sel and re.fullmatch(r"[\s>+~]*", "".join(rest)) is not None

    def test_U6_the_uo_stylesheets_set_no_type_and_sit_at_zero_specificity(self):
        exceptions = {
            (None, ".uo-details > summary > .surface-disclosure-label"): {"text-transform": "none"},
            (None, ":where(.uo-md) :where(.uo-authored-case)"): {"text-transform": "none"},
            ("print", ".uo-md .doc-pre"): {"white-space": "pre-wrap"},
            ("print", ".uo-md .doc-pre-part"): {"white-space": "pre-wrap"},
            ("print", "html"): {"-webkit-print-color-adjust": "exact", "print-color-adjust": "exact"},
        }
        seen = set()
        for sheet, rules in (("template", self.tpl), ("MD_CSS", self.md)):
            for m, sels, d in rules:
                for sel in sels:
                    with self.subTest(sheet=sheet, media=m, selector=sel):
                        if sel.startswith(":root") or sel == ".theme-dark":
                            self.assertTrue(all(k.startswith("--") for k in d), "a token rule declares tokens only")
                            continue
                        if (m, sel) in exceptions:
                            self.assertEqual(d, exceptions[(m, sel)])
                            seen.add((m, sel))
                            continue
                        self.assertTrue(self.zero_specificity(sel), "not zero-specificity: %s" % sel)
                        type_props = [k for k in d if k in self.TYPE and not (sel == ":where(.uo-mark)" and k == "color")]
                        self.assertEqual(type_props, [], "a UO rule sets a type metric")
        self.assertEqual(seen, set(exceptions))

    def test_U6_no_foundation_token_is_redeclared(self):
        for sheet, rules in (("template", self.tpl), ("MD_CSS", self.md)):
            for m, sels, d in rules:
                for k in d:
                    with self.subTest(sheet=sheet, selectors=sels, token=k):
                        self.assertIsNone(self.FOUNDATION_TOKENS.match(k))

    def test_U2_theme_dark_resolves_the_template_tokens(self):
        dark = [(sels, d) for m, sels, d in self.tpl if m is None and ':root[data-theme="dark"]' in sels]
        self.assertEqual(sorted(k for sels, d in dark for k in d), ["--artifact-line", "--artifact-line-soft", "--uo-mark"])
        for sels, d in dark:
            self.assertEqual(sels, (':root[data-theme="dark"]', ".theme-dark"))
        auto = [d for m, sels, d in self.tpl if m == "(prefers-color-scheme: dark)"]
        self.assertEqual(auto, [dark[0][1]])
        with open(os.path.join(HERE, "_dsa-tokens", "colors_and_type.css"), encoding="utf-8") as f:
            foundation = css_rules(f.read())
        self.assertTrue(any(sels == (':root[data-theme="dark"]', ".theme-dark") for m, sels, d in foundation))
        self.assertTrue(any(m == "(prefers-color-scheme: dark)" for m, sels, d in foundation))

    def test_U6_caption_and_summary_keep_the_authored_case(self):
        # The caption takes the register's metadata role, which sets no case. The disclosure summary keeps the
        # author's case through one UO value on the treatment, and the package MANIFEST declares it as a profile
        # over exactly that selector.
        with open(os.path.join(HERE, "_dsa-surface", "surface-document.css"), encoding="utf-8") as f:
            reg = css_rules(f.read())
        meta = [d for m, sels, d in reg if ".doc-meta" in sels and "font-family" in d]
        self.assertEqual(len(meta), 1)
        self.assertNotIn("text-transform", meta[0])
        summary = [d for m, sels, d in self.md if ".uo-details > summary > .surface-disclosure-label" in sels]
        self.assertEqual(summary, [{"text-transform": "none"}])
        prof = build.role_profiles({"disclosures": 3})
        self.assertEqual([x["selector"] for x in prof], [".uo-details > summary > .surface-disclosure-label"])
        self.assertEqual(prof[0]["expected_count"], 3)
        self.assertEqual(sorted(prof[0]), ["expected_count", "name", "owner", "reason", "selector"])
        self.assertEqual(build.role_profiles({"disclosures": 0}), [])

    def test_U2_text_wraps_everywhere_in_the_document(self):
        self.assertIn("anywhere", [d.get("overflow-wrap") for m, sels, d in self.md if m is None and ":where(.uo-md)" in sels])

    def test_U6_cells_keep_words_and_values_whole(self):
        cells = [d for m, sels, d in self.md if m is None and ":where(.uo-md) :where(th, td)" in sels]
        self.assertEqual([d.get("overflow-wrap") for d in cells], ["break-word"])
        for m, sels, d in self.md + self.tpl:
            self.assertNotIn("hyphens", d)
        atomic = ':where(.uo-md) :where(td[data-uo-cell="key"], td[data-uo-cell="num"], td[data-uo-cell="status"])'
        self.assertEqual([d for m, sels, d in self.md if m is None and atomic in sels], [{"white-space": "nowrap"}])
        long = [d for m, sels, d in self.md if m is None and ":where(.uo-md) :where(th, td) :where(code, a)" in sels]
        self.assertEqual(long, [{"overflow-wrap": "anywhere"}])
        num = [d for m, sels, d in self.md if m is None
               and ':where(.uo-md) :where(th[data-uo-cell="num"], td[data-uo-cell="num"])' in sels]
        self.assertEqual(num, [{"text-align": "right"}])

    def rows_rules(self, ctx):
        """The rows-view rules of one context, found by the table selector each rule opens with."""
        table = {self.ROWS_CONTEXTS[0]: "table", self.ROWS_CONTEXTS[1]: build.WIDE_BELOW_CAP,
                 self.ROWS_CONTEXTS[2]: build.WIDE_ALWAYS}[ctx]
        prefix = ":where(.uo-md) :where(%s)" % table
        return [(sels, d) for m, sels, d in self.md if m == ctx and sels[0].startswith(prefix)]

    def test_U6_rows_view_applies_in_three_contexts_alike(self):
        per = {ctx: [d for sels, d in self.rows_rules(ctx)] for ctx in self.ROWS_CONTEXTS}
        self.assertEqual(len(per[self.ROWS_CONTEXTS[0]]), len(build.ROWS_VIEW))
        for ctx in self.ROWS_CONTEXTS[1:]:
            self.assertEqual(per[ctx], per[self.ROWS_CONTEXTS[0]], ctx)
        self.assertIn("th:nth-child(7)", build.WIDE_BELOW_CAP)
        self.assertIn("th:nth-child(6)", build.WIDE_BELOW_CAP)
        self.assertIn("th:nth-child(9)", build.WIDE_ALWAYS)
        self.assertIn("th:nth-child(8)", build.WIDE_ALWAYS)

    def test_U2_stacked_labels_align_left_in_every_column(self):
        for ctx in self.ROWS_CONTEXTS:
            labels = [d for sels, d in self.rows_rules(ctx) if sels[0].endswith(":where(.uo-cell-label)")]
            self.assertEqual(labels, [{"display": "block", "text-align": "left"}], ctx)
        grid = [d for m, sels, d in self.md if m is None and ":where(.uo-md) :where(.uo-cell-label)" in sels]
        self.assertEqual(grid, [{"display": "none"}])

    def test_U2_narrow_screens_stack_rows_without_display_none_visibility_or_font_size(self):
        for ctx in self.ROWS_CONTEXTS:
            for sels, d in self.rows_rules(ctx):
                with self.subTest(context=ctx, selectors=sels):
                    self.assertNotEqual(d.get("display"), "none")
                    self.assertNotIn("visibility", d)
                    self.assertNotIn("font-size", d)
                    self.assertNotIn("content", d)

    def test_U2_R2_focused_header_row_returns_to_view(self):
        for ctx in self.ROWS_CONTEXTS:
            narrow = self.rows_rules(ctx)
            hidden = [d for sels, d in narrow if sels[0].endswith("> :where(thead)")]
            shown = [d for sels, d in narrow if sels[0].endswith("> :where(thead:focus-within)")]
            self.assertEqual(len(hidden), 1, ctx)
            self.assertEqual(len(shown), 1, ctx)
            self.assertEqual(sorted(hidden[0]), sorted(shown[0]))
            self.assertEqual(shown[0], {"position": "static", "width": "auto", "height": "auto",
                                        "overflow": "visible", "clip-path": "none", "white-space": "normal"})

    def test_U6_code_block_in_disclosure_renders_as_outside(self):
        # A preformatted block is the register's .doc-pre wherever it sits; no UO rule reaches inside a disclosure body.
        for m, sels, d in self.md + self.tpl:
            for sel in sels:
                self.assertNotIn("uo-details__body", sel)

    def test_U2_print_keeps_the_theme_ground_and_rebinds_no_token(self):
        self.assertIn({"-webkit-print-color-adjust": "exact", "print-color-adjust": "exact"}, rules_with(self.tpl, "html", "print"))
        self.assertIn({"white-space": "pre-wrap"}, rules_with(self.md, ".uo-md .doc-pre", "print"))
        for m, sels, d in self.tpl + self.md:
            if m and "print" in m:
                self.assertEqual([k for k in d if k.startswith("--")], [])


BANNERS_01 = """:::part 01
:::banner review-status
Synthetic status line.
:::

:::banner proof "Synthetic proof title"
Synthetic proof line.
:::
:::

"""


def with_part_01(src=GUIDED, part=BANNERS_01):
    return mutate(src, ":::part 01\nSynthetic locator line.\n:::\n\n", part)


def vendored_wordmark():
    with open(os.path.join(HERE, "_dsa-tokens", build.WORDMARK), encoding="utf-8") as f:
        text = f.read()
    return (re.search(r'viewBox="([^"]+)"', text).group(1), re.findall(r'<path d="([^"]*)"\s*/>', text))


# The masthead's index and every element around it, by the subject of a selector.
FOCUS_RING_ANCESTORS = re.compile(r"(?:\.uo-(?:index|head|shell|md)\b|^(?::root|html|body|section|header|details|summary|nav|ol|li)\b)",
                                  re.I)


def focus_ring_hazards(css):
    """Declarations that could hide or clip the browser's own focus ring on the mark slot and the index
    links: any outline property or `all`, anywhere; overflow, clip or contain on the index or its ancestors."""
    found = []
    for m, sels, d in css_rules(css):
        for prop, value in d.items():
            name = prop.strip().lower()
            subjects = [re.split(r"[\s>+~]+", sel.strip())[-1] for sel in sels]
            if name.startswith("outline") or name == "all" or (
                    name in ("overflow", "overflow-x", "overflow-y", "clip", "clip-path", "contain")
                    and any(FOCUS_RING_ANCESTORS.search(x) for x in subjects)):
                found.append("%s { %s: %s }" % (", ".join(sels), name, value))
    return found


class Identity(RenderCase):
    """U3: the assigned wordmark, the section ids and the generated section index, and the part-01 banners."""

    def banner(self, body, pattern, head=":::banner proof"):
        return self.fails(with_part_01(part=":::part 01\n%s\n%s:::\n:::\n\n" % (head, body)), pattern)

    def test_U3_masthead_order_mark_slot_and_index(self):
        h = self.render(GUIDED)["html"]
        head = re.search(r'<section data-uo-part="01" id="uo-part-01" class="doc-section">\n(.*?)\n</section>', h, flags=re.S).group(1)
        self.assertRegex(head, r'^<div class="uo-status-rail">.*</div>\n<header class="uo-head doc-titled">\n'
                               r'<details class="uo-index surface-disclosure surface-material-panel surface-attach-free '
                               r'surface-elevation-flush"><summary class="uo-index__mark"><span class="surface-disclosure-label">'
                               r'<svg class="uo-mark" [^>]*>.*</svg>sections</span><span class="surface-disclosure-indicator" '
                               r'aria-hidden="true">&#9660;</span></summary>\n'
                               r'<nav class="uo-index__list surface-disclosure-body" aria-label="Sections"><ol class="doc-toc-list">'
                               r'.*</ol></nav>\n</details>\n'
                               r'<h1 class="doc-title">Synthetic guided review</h1>\n<dl class="uo-head__meta">.*</dl>\n</header>\n'
                               r'<div class="doc-prose">\n<p class="doc-body">Synthetic locator line.</p>\n</div>$')
        links = re.findall(r'<li><a class="doc-toc-link surface-text-link" href="#([a-z0-9-]+)">([^<]+)</a></li>', h)
        self.assertEqual(links, [("uo-part-01", "01 locator + masthead"), ("uo-part-02", "02 reviewer brief"),
                                 ("uo-part-03", "03 decision request"), ("uo-part-04", "04 executive result"),
                                 ("uo-part-06", "06 finding unit"), ("uo-part-08", "08 unresolved + later-check register"),
                                 ("uo-part-10", "10 seal + provenance")])
        self.assertEqual([sid for sid, _ in links], re.findall(r'<section data-uo-part="\d\d" id="([a-z0-9-]+)"', h))

    def test_U3_index_lists_only_the_sections_present(self):
        h = self.render(CONFIRMATION)["html"]
        self.assertEqual(re.findall(r'<li><a class="doc-toc-link surface-text-link" href="#([a-z0-9-]+)">', h),
                         ["uo-part-01", "uo-part-02", "uo-part-07", "uo-part-10"])

    def test_U3_wordmark_carries_the_vendored_geometry(self):
        h = self.render(GUIDED)["html"]
        svg = re.search(r'<svg class="uo-mark" viewBox="([^"]+)" fill="currentColor" role="img" aria-label="ASK">(.*?)</svg>',
                        h, flags=re.S)
        self.assertIsNotNone(svg)
        viewbox, paths = vendored_wordmark()
        self.assertEqual(svg.group(1), viewbox)
        self.assertEqual(re.findall(r'<path d="([^"]*)"/>', svg.group(2)), paths)
        self.assertEqual(len(paths), 3)
        self.assertEqual(h.count("<svg"), 1)

    def test_U3_repeated_06_ids_and_labels(self):
        src = mutate(GUIDED, ":::part 08\n", ":::part 06\n:::finding\nA second finding.\n:::\n:::\n\n"
                                             ":::part 06\n:::finding\nA third finding.\n:::\n:::\n\n:::part 08\n")
        h = self.render(src)["html"]
        self.assertEqual(re.findall(r'<section data-uo-part="06" id="([a-z0-9-]+)"', h),
                         ["uo-part-06", "uo-part-06-2", "uo-part-06-3"])
        self.assertIn('<li><a class="doc-toc-link surface-text-link" href="#uo-part-06-2">06 finding unit 2</a></li>', h)
        self.assertIn('<li><a class="doc-toc-link surface-text-link" href="#uo-part-06-3">06 finding unit 3</a></li>', h)

    def test_U3_authored_section_links_fail(self):
        """Only the renderer's section index links inside the document; a source link is http(s) only."""
        http_only = r"only https:// and http:// links are allowed"
        at_result = "The synthetic executive result.\n"
        cases = {
            "inline": mutate(GUIDED, at_result, "See [x](#uo-part-08).\n"),
            "inline, existing part 01": mutate(GUIDED, at_result, "See [x](#uo-part-01).\n"),
            "inline, titled": mutate(GUIDED, at_result, 'See [x](#uo-part-08 "t").\n'),
            "reference": mutate(GUIDED, at_result, "See [x][r].\n\n[r]: #uo-part-08\n"),
            "absent part": mutate(GUIDED, at_result, "See [x](#uo-part-05).\n"),
            "malformed": mutate(GUIDED, at_result, "See [x](#uo-part-11).\n"),
            "bare #": mutate(GUIDED, at_result, "See [x](#).\n"),
            "table cell": with_table(table=TABLE.replace("| first claim |", "| [x](#uo-part-08) |")),
            "table header": with_table(table=TABLE.replace("| Claim |", "| [x](#uo-part-08) |")),
            "disclosure body": mutate(GUIDED, "Field-level listing.\n", "Field-level listing, [x](#uo-part-08).\n"),
            "banner body": with_part_01(part=":::part 01\n:::banner proof\nSee [x](#uo-part-08).\n:::\n:::\n\n"),
        }
        for name, src in cases.items():
            with self.subTest(form=name):
                self.reset_tmp()
                self.fails(src, http_only)

    def test_U3_banners_render_with_generated_flags(self):
        h = self.render(with_part_01())["html"]
        self.assertIn('</header>\n<div class="uo-reviewer-status %s">\n'
                      '<p class="uo-reviewer-status__flag surface-emphasis-chip">review status</p>\n'
                      '<div class="uo-reviewer-status__body doc-prose">\n<p class="doc-body">Synthetic status line.</p>\n</div>\n</div>\n'
                      '<div class="uo-proof %s">\n<p class="uo-proof__flag surface-emphasis-chip">proof of assembly</p>\n'
                      '<p class="uo-proof__title doc-subsection-title">Synthetic proof title</p>\n'
                      '<div class="uo-proof__body doc-prose">\n<p class="doc-body">Synthetic proof line.</p>\n</div>\n</div>\n</section>'
                      % (build.EMPHASIS_PANEL % "cyan", build.EMPHASIS_PANEL % "violet"), h)

    def test_U3_banners_keep_source_order(self):
        h = self.render(with_part_01(part=":::part 01\nA locator line.\n\n:::banner proof\nP.\n:::\n\n"
                                          ":::banner review-status\nR.\n:::\n:::\n\n"))["html"]
        self.assertLess(h.index('<p class="doc-body">A locator line.</p>'), h.index('<div class="uo-proof '))
        self.assertLess(h.index('<div class="uo-proof '), h.index('<div class="uo-reviewer-status '))

    def test_U3_proof_without_title_and_title_escaped(self):
        h = self.render(with_part_01(part=':::part 01\n:::banner proof\nA line.\n:::\n:::\n\n'))["html"]
        self.assertNotIn('class="uo-proof__title"', h)
        self.reset_tmp()
        h = self.render(with_part_01(part=':::part 01\n:::banner proof "A <b> & title"\nA line.\n:::\n:::\n\n'))["html"]
        self.assertIn('<p class="uo-proof__title doc-subsection-title">A &lt;b&gt; &amp; title</p>', h)

    def test_U3_banner_outside_part_01_fails(self):
        self.fails(mutate(GUIDED, "What this synthetic document tests, and what not to judge.\n",
                          "What this synthetic document tests.\n\n:::banner proof\nA line.\n:::\n"),
                   r":::banner is allowed directly inside :::part 01 only, not :::part 02")

    def test_U3_banner_at_top_level_fails(self):
        self.fails(mutate(GUIDED, ":::part 02\n", ":::banner proof\nA line.\n:::\n\n:::part 02\n"),
                   r":::banner is allowed directly inside :::part 01 only")

    def test_U3_repeated_banner_fails(self):
        self.fails(with_part_01(part=":::part 01\n:::banner review-status\nA.\n:::\n:::banner review-status\nB.\n:::\n:::\n\n"),
                   r"part 01 carries at most one :::banner review-status")

    def test_U3_banner_kind_and_title_rules(self):
        cases = [
            (":::banner\n", r":::banner takes one kind from review-status, proof, first"),
            (":::banner approval\n", r":::banner takes one kind from review-status, proof, first"),
            (":::banner \"T\" proof\n", r":::banner takes one kind from review-status, proof, first"),
            (":::banner proof proof\n", r"repeated token|takes one kind"),
            (":::banner review-status \"T\"\n", r"only :::banner proof takes a quoted title"),
            (":::banner proof \"A\" \"B\"\n", r"at most one non-empty quoted title"),
            (":::banner proof \"\"\n", r"at most one non-empty quoted title"),
            (":::banner proof \"​\"\n", r"at most one non-empty quoted title"),
            (":::banner proof local=x\n", r"takes no local= hook"),
        ]
        for head, pattern in cases:
            with self.subTest(head=head):
                self.reset_tmp()
                self.fails(with_part_01(part=":::part 01\n%sA line.\n:::\n:::\n\n" % head), pattern)

    def test_U3_banner_holds_markdown_only(self):
        self.banner(TABLE, r":::table sits inside :::banner proof \(line \d+\); a banner holds Markdown only")
        self.reset_tmp()
        self.banner("> A quoted line.\n", r"holds a quotation; its rule would draw a second edge inside the banner's ruled frame")
        self.reset_tmp()
        self.fails(with_part_01(part=":::part 01\n:::banner review-status\n- a list item\n\n  > nested quote\n:::\n:::\n\n"),
                   r":::banner review-status \(line \d+\) holds a quotation")
        self.reset_tmp()
        self.banner("## A heading\n", r"holds a heading; a banner carries its flag and title only")

    def test_U3_empty_banner_fails(self):
        self.fails(with_part_01(part=":::part 01\n:::banner review-status\n​\n:::\n:::\n\n"),
                   r":::banner review-status \(line \d+\) is empty")

    def test_U3_banner_counts_as_part_01_content(self):
        r = self.render(with_part_01(part=":::part 01\n:::banner proof\nA line.\n:::\n:::\n\n"))
        self.assertEqual(r["parts"][0], "01")

    def test_U3_wordmark_svg_rejects_other_shapes(self):
        good = b'<?xml version="1.0"?>\n<svg viewBox="0 0 10 10" fill="currentColor"><path d="M0 0h1z"/></svg>\n'
        self.assertEqual(build.wordmark_svg(good), '<svg class="uo-mark" viewBox="0 0 10 10" fill="currentColor" '
                                                   'role="img" aria-label="ASK"><path d="M0 0h1z"/></svg>')
        bad = [
            (b'<svg viewBox="0 0 10 10" fill="currentColor"><g><path d="M0"/></g></svg>', r"not one svg of path elements"),
            (b'<svg viewBox="0 0 10 10" fill="currentColor"><path d="M0" onload="x()"/></svg>', r"not one svg of path elements"),
            (b'<svg viewBox="0 0 10 10" fill="currentColor"><script>x()</script></svg>', r"not one svg of path elements"),
            (b'<svg viewBox="0 0 10 10" fill="currentColor"></svg>', r"not one svg of path elements"),
            (b'<svg viewBox="0 0 10 10" fill="#fff"><path d="M0"/></svg>', r"numeric viewBox or fill=\"currentColor\""),
            (b'<svg viewBox="url(x)" fill="currentColor"><path d="M0"/></svg>', r"numeric viewBox or fill=\"currentColor\""),
            (b'<svg fill="currentColor"><path d="M0"/></svg>', r"numeric viewBox or fill=\"currentColor\""),
            (b'<svg viewBox="0 0 10 10" fill="currentColor" transform="scale(-1 1)"><path d="M0"/></svg>',
             r"carries svg attributes other than id, xmlns, viewBox and fill, each once"),
            (b'<svg viewBox="0 0 10 10" fill="currentColor" style="fill:red"><path d="M0"/></svg>',
             r"carries svg attributes other than id, xmlns, viewBox and fill, each once"),
            (b'<svg data-viewBox="0 0 10 10" viewBox="-5 0 10 10" fill="currentColor"><path d="M0"/></svg>',
             r"carries svg attributes other than id, xmlns, viewBox and fill, each once"),
            (b'<svg viewBox="0 0 10 10" fill="currentColor" fill="#000"><path d="M0"/></svg>',
             r"carries svg attributes other than id, xmlns, viewBox and fill, each once"),
            (b'<svg viewBox="0 0 10 10" fill=currentColor><path d="M0"/></svg>',
             r"carries svg attributes other than id, xmlns, viewBox and fill, each once"),
        ]
        for data, pattern in bad:
            with self.subTest(data=data):
                with self.assertRaises(build.BuildError) as cm:
                    build.wordmark_svg(data)
                self.assertRegex(str(cm.exception), pattern)

    def test_U3_allowlist_rejects_misplaced_identity_chrome(self):
        h = self.render(with_part_01())["html"]
        svg = re.search(r'<svg class="uo-mark".*?</svg>', h, flags=re.S).group(0)
        nav = re.search(r'<nav class="uo-index__list surface-disclosure-body".*?</nav>', h, flags=re.S).group(0)
        brief = '<p class="doc-body">What this synthetic document tests, and what not to judge.</p>'
        index = '<details class="uo-index %s">' % build.DISCLOSURE
        toc = '<li><a class="doc-toc-link surface-text-link" href="#%s">%s</a></li>'
        bad = [
            (h.replace(' id="uo-part-03"', ''), r"<section> without its id"),
            (h.replace(' id="uo-part-03"', ' id="uo-part-05"'), r"<section id='uo-part-05'> does not name its part '03'"),
            (h.replace(' id="uo-part-03"', ' id="x"'), r"<section id='x'> does not name its part '03'"),
            (h.replace('href="#uo-part-10"', 'href="#uo-part-09"'), r"the section index must link every section, in order"),
            (h.replace('href="#uo-part-01"', 'href="#top"'), r"a section-index link names a section id, #uo-part-NN"),
            (h.replace('href="#uo-part-01"', 'href="#uo-part-01-1"'), r"a section-index link names a section id, #uo-part-NN"),
            (h.replace('href="#uo-part-01"', 'href="#UO-PART-01"'), r"a section-index link names a section id, #uo-part-NN"),
            (h.replace(' id="uo-part-03"', ' id="uo-part-03-1"'), r"<section id='uo-part-03-1'> does not name its part '03'"),
            (h.replace(' id="uo-part-03"', ' id="uo-part-3"'), r"<section id='uo-part-3'> does not name its part '03'"),
            (h.replace(brief, brief + '<p class="doc-body"><a class="surface-text-link" href="#uo-part-08">x</a></p>'),
             r"only https:// and http:// links are allowed"),
            (h.replace(brief, brief + svg), r"<svg> is the masthead's wordmark only, in the mark slot"),
            (h.replace(svg, svg + svg), r"exactly one <svg>, the masthead's wordmark, required \(found 2\)"),
            (h.replace(svg, ""), r"exactly one <svg>, the masthead's wordmark, required \(found 0\)"),
            (h.replace('aria-label="ASK"', 'aria-label="Other"'), r"<svg> carries the wordmark's attributes only"),
            (h.replace('role="img" aria-label="ASK">', 'role="img" aria-label="ASK">text'), r"text inside the wordmark"),
            (h.replace('role="img" aria-label="ASK">', 'role="img" aria-label="ASK"><span>x</span>'),
             r"the wordmark holds path elements only"),
            (h.replace(brief, brief + '<p class="doc-body"><path d="M0"></path></p>'), r"<path> outside the wordmark"),
            (h.replace(brief, brief + nav), r"<nav> is the section index's list only"),
            (h.replace('aria-label="Sections"', 'aria-label="Parts"'), r"<nav> carries aria-label Sections"),
            (h.replace(index, index[:-1] + ' data-uo-disclose="evidence">'),
             r"the section index is not an authored disclosure"),
            (h.replace(brief, brief + index + '<summary class="uo-index__mark">x</summary></details>'),
             r"<details class='uo-index'> is the masthead's section index only"),
            (h.replace(brief, brief + '<div class="uo-proof %s"><p class="uo-proof__flag surface-emphasis-chip">x</p></div>'
                       % (build.EMPHASIS_PANEL % "violet")),
             r"<div class='uo-proof'> sits only directly in part 01"),
            (h.replace(brief, brief + '<p class="uo-reviewer-status__flag surface-emphasis-chip">x</p>'),
             r"class 'uo-reviewer-status__flag' sits only directly in its <div class='uo-reviewer-status'>"),
            (h.replace('<p class="uo-proof__title doc-subsection-title">', '<p class="uo-reviewer-status__flag surface-emphasis-chip">'),
             r"class 'uo-reviewer-status__flag' sits only directly in its <div class='uo-reviewer-status'>"),
            (h.replace(toc % ("uo-part-08", "08 unresolved + later-check register"), ''),
             r"the section index must link every section, in order"),
            (h.replace(toc % ("uo-part-02", "02 reviewer brief") + toc % ("uo-part-03", "03 decision request"),
                       toc % ("uo-part-03", "03 decision request") + toc % ("uo-part-02", "02 reviewer brief")),
             r"the section index must link every section, in order"),
            (h.replace(nav, '<nav class="uo-index__list surface-disclosure-body" aria-label="Sections"><ol class="doc-toc-list"></ol></nav>'),
             r"the section index must link every section, in order"),
            (h.replace('<h1 class="doc-title">', index + '<summary class="uo-index__mark">x</summary></details>\n<h1 class="doc-title">'),
             r"exactly one section index, <details class='uo-index'>, required \(found 2\)"),
            (h.replace(toc % ("uo-part-02", "02 reviewer brief"), '<li><a class="surface-text-link" href="#uo-part-02">02 reviewer brief</a></li>'),
             r"every link in the contents list is a contents link"),
            (h.replace(toc % ("uo-part-02", "02 reviewer brief"), '<li class="doc-body">' + toc[4:] % ("uo-part-02", "02 reviewer brief")),
             r"a contents entry is an unclassed <li> in the contents list"),
            (h.replace('</summary>\n<nav', '</summary><summary class="uo-index__mark">y</summary>\n<nav'),
             r"exactly one mark slot, <summary class='uo-index__mark'>, required \(found 2\)"),
        ]
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                self.assertNotEqual(doc, h)
                with self.assertRaises(build.BuildError) as cm:
                    build.check_final_html(doc, 2)
                self.assertRegex(str(cm.exception), pattern)

    def test_U3_repeated_section_id_fails(self):
        src = mutate(GUIDED, ":::part 08\n", ":::part 06\n:::finding\nA second finding.\n:::\n:::\n\n:::part 08\n")
        h = self.render(src)["html"]
        with self.assertRaises(build.BuildError) as cm:
            build.check_final_html(h.replace(' id="uo-part-06-2"', ' id="uo-part-06"'), 2)
        self.assertRegex(str(cm.exception), r"section id 'uo-part-06' repeated")

    def test_U3_wordmark_takes_the_design_system_pairing(self):
        tpl = css_rules(template_css())
        found = {(m, sels): d["--uo-mark"] for m, sels, d in tpl if "--uo-mark" in d}
        self.assertEqual(found, {
            (None, (":root",)): "var(--ask-white)",
            (None, (':root[data-theme="dark"]', ".theme-dark")): "var(--ask-lavender-ask)",
            ("(prefers-color-scheme: dark)", (':root:not([data-theme="light"]):not([data-theme="dark"])',)):
                "var(--ask-lavender-ask)",
        })
        self.assertEqual(rules_with(tpl, ":where(.uo-mark)")[0]["color"], "var(--uo-mark)")

    def test_U6_no_uo_element_rule_competes_with_a_role(self):
        """U3's banner and index rules had to outrank MD_CSS's prose rules. U6 retired both: the banners, the
        index and every text element take register roles, and no UO rule names a text element at all."""
        text = re.compile(r"(?:^|[\s>+~(])(p|li|h[1-6]|blockquote|code|pre|a|strong|em|th|td|caption|dt|dd|summary)(?=$|[\s.:\[>+~,)])")
        for sheet, rules in (("template", css_rules(template_css())), ("MD_CSS", css_rules(build.md_css(True)))):
            for m, sels, d in rules:
                for sel in sels:
                    if sel == ".uo-details > summary > .surface-disclosure-label":
                        self.assertEqual(d, {"text-transform": "none"})     # the one declared profile value
                        continue
                    if text.search(sel):
                        with self.subTest(sheet=sheet, selector=sel):
                            self.assertFalse([k for k in d if k in Presentation.TYPE], "a text-element rule sets type")

    def test_U6_focus_is_the_design_systems_and_nothing_here_clips_it(self):
        """U3's native ring was provisional. At U6 the mark slot is a design-system disclosure trigger, whose
        keyboard focus is the treatment's: a 2px --fg-1 outline around the trigger, --space-1 out, with the
        summary at --fg-1 and its indicator in the magenta. Every index link is a surface-text-link, whose
        focus is that module's own underline. No UO stylesheet declares an outline or `all`, and none clips the
        index or its ancestors; the rendered check (C9) and the keyboard measurement prove the effect."""
        with open(os.path.join(HERE, "_dsa-tokens", "colors_and_type.css"), encoding="utf-8") as f:
            foundation = f.read()
        self.assertEqual(focus_ring_hazards(template_css()) + focus_ring_hazards(build.md_css(True))
                         + focus_ring_hazards(foundation), [])
        self.assertNotIn("outline", build.md_css(True) + template_css())
        with open(os.path.join(HERE, "_dsa-surface", "surface-treatments.css"), encoding="utf-8") as f:
            treat = css_rules(f.read())
        self.assertIn({"color": "var(--fg-1)", "outline": "2px solid var(--fg-1)", "outline-offset": "var(--space-1)"},
                      rules_with(treat, ".surface-disclosure > summary:focus-visible"))
        self.assertIn({"color": "var(--ask-emphasis-magenta)"},
                      rules_with(treat, ".surface-disclosure > summary:focus-visible .surface-disclosure-indicator"))
        with open(os.path.join(HERE, "_dsa-surface", "surface-text-link.css"), encoding="utf-8") as f:
            link = f.read()
        self.assertRegex(link, r"\.surface-text-link:focus-visible")
        for extra in (".uo-md .uo-index__list a:focus-visible { outline: 2px solid transparent; }",
                      "summary { all: unset; }",
                      ".uo-md .uo-index__mark { outline-color: rgba(0,0,0,0); }",
                      ".uo-md .uo-index { overflow: hidden; }",
                      "main.uo-md { overflow: hidden; }",
                      "A:FOCUS { OUTLINE: none; }",
                      ".uo-md .uo-index__mark:focus { outline: none; }"):
            with self.subTest(extra=extra):
                self.assertEqual(len(focus_ring_hazards(extra)), 1)

    def test_U3_manifest_states_the_wordmark_embedding(self):
        m = " ".join(self.render(GUIDED)["manifest_text"].split())
        self.assertIn("The wordmark is embedded as the masthead's inline svg, carrying the file's viewBox and path data "
                      "unchanged, so its embedded text is not byte-equal to the hashed file either.", m)
        dep = build.verify_dependencies()
        self.assertEqual(build.dependency(dep, "_dsa-tokens/" + build.WORDMARK)["path"], "_dsa-tokens/" + build.WORDMARK)
        surface = build.MODULES + build.STATE_MODULES
        self.assertEqual([f["path"] for f in dep["files"]][-len(surface):], ["_dsa-surface/" + x for x in surface])
        self.assertIn("The four register modules are embedded byte for byte, in the order listed, after the token CSS.", m)


U6_SRC = mutate(GUIDED, "What this synthetic document tests, and what not to judge.\n", """## Reviewer brief

What this synthetic document tests, and what not to judge.

:::framing thesis
The part's thesis, framed before its sections.
:::

### What to judge

A paragraph with `code` and a [link](https://example.org/a).

- one item
- two items

#### A deep heading

> Someone's words.
>
>     quoted code

:::quote "A public source, page 2"
A quotation with its attribution.
:::

:::callout
A posed question of the document's own?
:::

:::callout
A lead-in to the structure below.

:::structure
:::group
LABEL
  a line beneath
:::
:::group
SECOND
  another line
:::
:::
:::

```
a fenced block
```

:::synthesis
What the part comes to.
:::
""")


class Register(RenderCase):
    """U6: every element takes a design-system document-register role, and the containers U6 adds."""

    def test_U6_roles_on_every_markdown_element(self):
        h = self.render(U6_SRC)["html"]
        body = h.split("<body>")[1]
        for fragment in ('<h2 class="doc-section-title">Reviewer brief</h2>',
                         '<h3 class="doc-subsection-title">What to judge</h3>',
                         '<h4 class="doc-deep-title">A deep heading</h4>',
                         '<p class="doc-body">A paragraph with <code class="doc-code">code</code> and a '
                         '<a class="surface-text-link" href="https://example.org/a">link</a>.</p>',
                         '<li class="doc-body">one item</li>',
                         '<blockquote class="doc-quote">\n<p>Someone\'s words.</p>\n<pre class="doc-pre">quoted code\n</pre>\n</blockquote>',
                         '<pre class="doc-pre">a fenced block\n</pre>'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, body)
        self.assertNotIn("<pre><code", body)
        self.assertEqual(len(re.findall(r"<p>", body)), 2)                     # the two quotations' own paragraphs
        self.assertEqual(len(re.findall(r'<blockquote class="doc-quote">\n<p>', body)), 2)

    def test_U6_headings_nest_sections(self):
        h = self.render(U6_SRC)["html"]
        part = re.search(r'<section data-uo-part="02" id="uo-part-02" class="doc-section">\n(.*?)\n</section>', h, re.S).group(1)
        self.assertTrue(part.startswith('<h2 class="doc-section-title">Reviewer brief</h2>'))
        self.assertIn('<div class="doc-section">\n<h3 class="doc-subsection-title">What to judge</h3>', part)
        self.assertIn('<div class="doc-section">\n<h4 class="doc-deep-title">A deep heading</h4>', part)
        self.assertLess(part.index('<h3 '), part.index('<h4 '))
        # the synthesis closes the part: it sits directly in the part's section, after every nested section
        self.assertTrue(part.endswith('<p class="doc-body">What the part comes to.</p>\n</div>'))
        self.assertIn('</div>\n</div>\n<div data-uo-role="synthesis"', part)

    def test_U6_every_heading_container_is_a_section_and_every_run_is_prose(self):
        # The register leads a section nested in a section (.doc-section > .doc-section). A container that
        # holds headings is therefore itself a section -- a part, a question, a finding, a disclosure's body --
        # so its first subsection is set apart as in a part; and a section's run of blocks is always a
        # .doc-prose, the last section's included.
        src = mutate(GUIDED, "**Status:** open. Finding, significance and limit.\n",
                     "**Status:** open. Finding, significance and limit.\n\n### First\n\nOne.\n\nTwo.\n\n#### Deep\n\nThree.\n\n"
                     "### Second\n\nFour.\n\n:::disclose evidence \"Heads\"\n#### Inside\n\nFive.\n\n#### Again\n\nSix.\n:::\n")
        h = self.render(src)["html"]
        self.assertIn('<div data-uo-role="finding" class="doc-section">', h)
        finding = h[h.index('<div data-uo-role="finding" class="doc-section">'):]
        self.assertTrue(finding.startswith('<div data-uo-role="finding" class="doc-section">\n<div class="doc-prose">\n'
                                           '<p class="doc-body"><strong>Status:</strong> open.'))
        self.assertIn('<div class="doc-section">\n<h3 class="doc-subsection-title">First</h3>\n<div class="doc-prose">\n'
                      '<p class="doc-body">One.</p>\n<p class="doc-body">Two.</p>\n</div>\n<div class="doc-section">\n'
                      '<h4 class="doc-deep-title">Deep</h4>\n<div class="doc-prose">\n<p class="doc-body">Three.</p>\n</div>\n</div>\n</div>',
                      finding)
        self.assertIn('<div class="uo-details__body surface-disclosure-body doc-section">\n<div class="doc-section">\n'
                      '<h4 class="doc-deep-title">Inside</h4>\n<div class="doc-prose">\n<p class="doc-body">Five.</p>\n</div>\n</div>\n'
                      '<div class="doc-section">\n<h4 class="doc-deep-title">Again</h4>\n<div class="doc-prose">\n'
                      '<p class="doc-body">Six.</p>\n</div>\n</div>\n</div>', h)
        # no heading is followed directly by a bare block, and no .doc-group or .doc-prose holds a heading
        self.assertIsNone(re.search(r'</h[2-4]>\n<(p|ul|ol|pre|table|blockquote|details)\b', h))
        for m in re.finditer(r'<div class="doc-(?:group|prose)">\n<h[2-4]\b', h):
            self.fail("a heading directly inside a group or prose run: %r" % m.group(0))
        self.assertNotIn('class="doc-group"', h)

    def test_U6_framing_synthesis_callout_quote_and_structure_markup(self):
        r = self.render(U6_SRC)
        h = r["html"]
        self.assertIn('<div data-uo-role="framing" class="%s">\n<p class="surface-emphasis-chip surface-emphasis--magenta">thesis</p>\n'
                      '<p class="doc-body">The part\'s thesis, framed before its sections.</p>\n</div>' % build.FLAT_PANEL, h)
        self.assertIn('<div data-uo-role="synthesis" class="%s">\n<p class="surface-emphasis-chip surface-emphasis--magenta">compression</p>'
                      % build.FLAT_PANEL, h)
        self.assertIn('<p class="doc-body surface-emphasis-rail" data-uo-role="callout">A posed question of the document\'s own?</p>', h)
        self.assertIn('<div data-uo-role="callout" class="surface-emphasis-rail doc-group">\n<p class="doc-body">A lead-in', h)
        self.assertIn('<blockquote class="doc-quote">\n<p>A quotation with its attribution.</p>\n<footer>A public source, page 2</footer>\n'
                      '</blockquote>', h)
        self.assertIn('<div class="doc-pre doc-pre--structured"><div class="doc-pre-group"><pre class="doc-pre-part">LABEL</pre>'
                      '<div class="doc-hierarchy"><pre class="doc-pre-part">a line beneath</pre></div></div>', h)
        self.assertEqual({k: r["counts"][k] for k in ("quotations", "callouts", "framing", "synthesis", "structures")},
                         {"quotations": 1, "callouts": 2, "framing": 1, "synthesis": 1, "structures": 1})
        build.check_final_html(h, 2)

    def test_U6_structure_levels_and_lead_lines(self):
        src = mutate(GUIDED, "The whole synthetic register.\n", "The whole synthetic register.\n\n:::structure\nA\n  b\n    c\n  d\n\n\nE\n:::\n")
        h = self.render(src)["html"]
        self.assertIn('<div class="doc-pre doc-pre--structured"><pre class="doc-pre-part">A</pre><div class="doc-hierarchy">'
                      '<pre class="doc-pre-part">b</pre><div class="doc-hierarchy"><pre class="doc-pre-part">c</pre></div>'
                      '<pre class="doc-pre-part">d</pre></div><pre class="doc-pre-part" data-lead-lines="2">E</pre></div>', h)

    def test_U6_container_refusals(self):
        at = "The whole synthetic register.\n"
        reg = lambda text: mutate(GUIDED, at, at + "\n" + text)
        cases = [
            (reg(":::structure\nA\n\tb\n:::\n"), r"never a tab"),
            (reg(":::structure\nA\n   b\n:::\n"), r"two spaces per level \(found 3\)"),
            (reg(":::structure\nA\n    b\n:::\n"), r"more than one level beneath"),
            (reg(":::structure\n  A\n:::\n"), r"first line sits at the first level"),
            (reg(":::structure\nA\n\n\n\n\nB\n:::\n"), r"4 blank lines before a structure line; at most 3"),
            (reg(":::structure\n:::group\nA\n\n  b\n:::\n:::\n"), r"a blank line inside a :::group"),
            (reg(":::structure\nloose\n:::group\nA\n:::\n:::\n"), r"holds only :::group containers"),
            (reg(":::group\nA\n:::\n"), r":::group is allowed inside :::structure only"),
            (reg(":::structure\n:::group\n​\n:::\n:::\n"), r":::group \(line \d+\) is empty"),
            (reg(":::structure local=x\n:::group local=y\nA\n:::\n:::\n"), r":::group takes no local= hook"),
            (reg(":::quote\n## A heading\n:::\n"), r"a quotation holds no heading"),
            (reg("> quoted\n>\n> ### heading\n"), r"a quotation holds no heading"),
            (reg(":::quote\n:::callout\nx\n:::\n:::\n"), r":::callout is allowed inside :::part, :::question, :::finding, :::disclose, "
                                                    r":::range only"),
            (reg(":::quote word\nx\n:::\n"), r":::quote takes at most one quoted attribution"),
            (reg(':::quote "​"\nx\n:::\n'), r"attribution must contain visible text"),
            (reg(":::callout\n#### A heading\n:::\n"), r"holds a heading"),
            (reg(":::callout\n:::callout\nx\n:::\n:::\n"), r":::callout is allowed inside"),
            (reg(":::framing verdict\nx\n:::\n"), r":::framing takes one of thesis, question"),
            (reg(":::synthesis\nWhat it comes to.\n:::\n\nA line after.\n"), r"a :::synthesis closes its part"),
            (reg(":::synthesis\n> quoted\n:::\n"), r"holds a <blockquote> block; it holds p, ul, ol only"),
            (reg(":::synthesis\nOne.\n:::\n:::synthesis\nTwo.\n:::\n"), r"part 08 carries at most one :::synthesis"),
            (reg(":::table dense key text dense\n| a | b |\n|---|---|\n| 1 | 2 |\n:::\n"), r"'dense' comes first on :::table, once"),
            (reg(":::structure\n:::table key\n| a |\n|---|\n| 1 |\n:::\n:::\n"), r":::table is allowed inside"),
            (mutate(GUIDED, ":::part 10\n", ":::part 10\n:::framing thesis\nx\n:::\n"),
             r":::framing is not allowed in part 10, which carries generated chrome"),
            (mutate(GUIDED, "What this synthetic document tests, and what not to judge.\n",
                    "What this synthetic document tests.\n\n### A section\n\nText.\n\n:::framing question\nx\n:::\n"),
             r"a :::framing opens its part, before the part's first ### or #### section"),
            (mutate(GUIDED, "What this synthetic document tests, and what not to judge.\n",
                    "What this synthetic document tests.\n\n:::synthesis\nx\n:::\n:::framing thesis\ny\n:::\n"),
             r"a :::framing opens a part and comes before its :::synthesis"),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_U6_allowlist_places_the_register(self):
        h = self.render(U6_SRC)["html"]
        para = '<p class="doc-body">A paragraph with'
        bad = [
            (h.replace(para, '<pre class="doc-pre-part">x</pre>' + para, 1), r"a structured line sits only in a structured block"),
            (h.replace(para, '<div class="doc-pre-group"><pre class="doc-pre">x</pre></div>' + para, 1),
             r"a hierarchy rail or peer group sits only in a structured block"),
            (h.replace('<pre class="doc-pre">a fenced block\n</pre>', '<pre class="doc-pre"><code class="doc-code">x</code></pre>', 1),
             r"a preformatted block carries its text directly"),
            (h.replace('<p class="surface-emphasis-chip surface-emphasis--magenta">thesis</p>', '', 1).replace(
                para, '<p class="surface-emphasis-chip surface-emphasis--magenta">thesis</p>' + para, 1),
             r"a framing or synthesis chip sits only in its panel"),
            (h.replace('<li class="doc-body">one item</li>', '<li>one item</li>', 1),
             r"a contents entry is an unclassed <li> in the contents list; every other <li> is document body"),
            (h.replace('<footer>A public source, page 2</footer>', '<footer class="uo-foot">A public source, page 2</footer>', 1),
             r"the seal line sits only in part 10"),
        ]
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                self.assertNotEqual(doc, h)
                with self.assertRaises(build.BuildError) as cm:
                    build.check_final_html(doc, 2)
                self.assertRegex(str(cm.exception), pattern)

    def test_U6_every_text_element_carries_a_role(self):
        """A static mirror of the rendered check's unmapped list: every element that holds text directly sits
        inside an element carrying a register role, a design-system treatment's text class or the quotation's
        own paragraph or attribution."""
        from html.parser import HTMLParser
        roles = {"doc-title", "doc-section-title", "doc-subsection-title", "doc-deep-title", "doc-body", "doc-lede",
                 "doc-label", "doc-meta", "doc-code", "doc-quote", "doc-pre", "doc-pre-part", "doc-toc-link",
                 "doc-table-cell", "doc-entry-title", "surface-emphasis-chip", "surface-disclosure-label",
                 "surface-disclosure-indicator"}
        h = self.render(mutate(U6_SRC, "The synthetic executive result.\n", "The synthetic executive result.\n\n" + TABLE))["html"]
        unmapped = []

        class P(HTMLParser):
            def __init__(self):
                super().__init__()
                self.stack, self.body = [], False

            def handle_starttag(self, tag, attrs):
                if tag == "body":
                    self.body = True
                if tag not in ("br", "hr", "meta", "path"):
                    self.stack.append((tag, set((dict(attrs).get("class") or "").split())))

            def handle_endtag(self, tag):
                if self.stack and self.stack[-1][0] == tag:
                    self.stack.pop()

            def handle_data(self, data):
                if not self.body or not data.strip() or any(t in ("style", "svg") for t, _ in self.stack):
                    return
                covered = any(c & roles for t, c in self.stack) or (
                    len(self.stack) > 1 and self.stack[-2][0] == "blockquote" and self.stack[-1][0] in ("p", "footer"))
                if not covered:
                    unmapped.append((self.stack[-1][0], data.strip()[:30]))
        P().feed(h)
        self.assertEqual(unmapped, [])

    def test_U6_manifest_declares_the_rendered_check_profiles(self):
        r = self.render(U6_SRC)
        block = re.search(r"## Rendered-check profiles\n.*?```json\n(.*?)\n```", r["manifest_text"], re.S)
        import json as _json
        self.assertEqual(_json.loads(block.group(1)), build.role_profiles(r["counts"]))
        self.assertEqual(_json.loads(block.group(1))[0]["expected_count"], 3)


def readme_profiles(readme):
    block = re.search(r"```text\nkind +requires, beyond 01 · 02 · 10 +status\n(.*?)```", readme, flags=re.S)
    if block is None:
        return None
    table = {}
    for line in block.group(1).strip().splitlines():
        m = re.match(r"^([a-z-]+) +((?:\d\d(?: · )?)+) +([A-Z]+)$", line)
        if m is None:
            return None
        table[m.group(1)] = tuple(m.group(2).split(" · "))
    return table


def readme_class_sets(readme):
    """README's "Emitted classes" table: one line per element and emitted class set, in order."""
    block = re.search(r"```text\nelement +emitted class set\n(.*?)```", readme, flags=re.S)
    if block is None:
        return None
    table = {}
    for line in block.group(1).strip().splitlines():
        m = re.match(r"^([a-z0-9]+) +([a-z_-]+(?: [a-z_-]+)*)$", line)
        if m is None:
            return None
        table.setdefault(m.group(1), []).append(m.group(2))
    return {k: tuple(v) for k, v in table.items()}


def readme_visibility(readme):
    """README's "What stays visible" tables: the parts ALWAYS VISIBLE lists, and the parts MAY DISCLOSE lists, each
    with the kinds its "(<kind> only)" qualifier limits it to (None: every kind), in order."""
    block = re.search(r"```text\nALWAYS VISIBLE, including\n(.*?)\nMAY DISCLOSE\n(.*?)```", readme, flags=re.S)
    if block is None:
        return None
    always = tuple(re.findall(r"^  (\d\d)   \S", block.group(1), flags=re.M))
    may = [(m.group(1), tuple(m.group(2).split(" or ")) if m.group(2) else None)
           for m in re.finditer(r"^  (\d\d)   (?:\(([a-z-]+(?: or [a-z-]+)*) only\) )?\S", block.group(2), flags=re.M)]
    return {"always": always, "may": may}


def code_visibility():
    """The same tables from the build's declarations: a part where a disclosure class may sit, with the kinds it is
    limited to; ALWAYS VISIBLE must list those parts (what precedes or surrounds a disclosure there stays visible) and
    the parts no disclosure enters. It may list other parts too: a part with no disclosure class is visible whole."""
    may = sorted((part, build.DISCLOSE_KINDS.get(cls)) for cls, part in build.DISCLOSE_PARTS.items())
    always = tuple(sorted(set(build.DISCLOSE_PARTS.values()) | set(build.NO_DISCLOSE_PARTS)))
    return {"always": always, "may": may}


def visibility_matches(readme_tables, code):
    """README's tables against the build's: MAY DISCLOSE equal, and ALWAYS VISIBLE holding every part that has a
    disclosure class or takes none; README's other ALWAYS VISIBLE lines are allowed."""
    return (readme_tables is not None and readme_tables["may"] == code["may"]
            and set(code["always"]) <= set(readme_tables["always"]))


class Consistency(unittest.TestCase):
    def readme(self):
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
            return f.read()

    def test_N74_profile_table_equals_readme(self):
        readme = self.readme()
        self.assertEqual(readme_profiles(readme), build.KIND_PROFILES)
        self.assertIn("Every kind requires 01, 02 and 10.", readme)
        self.assertEqual(build.BASE_REQUIRED_PARTS, ("01", "02", "10"))

    def test_N74b_drifted_readme_detected(self):
        readme = self.readme()
        drifted = readme.replace("confirmation    07                              PROVISIONAL",
                                 "confirmation    07 · 08                         PROVISIONAL")
        self.assertNotEqual(drifted, readme)
        self.assertNotEqual(readme_profiles(drifted), build.KIND_PROFILES)

    def test_N74c_visibility_tables_equal_disclosure_positions(self):
        readme = self.readme()
        self.assertEqual(set(build.DISCLOSE_PARTS), set(build.DISCLOSE_CLASSES))
        self.assertTrue(set(build.DISCLOSE_KINDS) <= set(build.DISCLOSE_CLASSES))
        self.assertTrue(all(set(k) <= set(build.KIND_PROFILES) for k in build.DISCLOSE_KINDS.values()))
        self.assertTrue(visibility_matches(readme_visibility(readme), code_visibility()))
        self.assertEqual(code_visibility(), {"always": ("03", "04", "06", "08", "10"),
                                             "may": [("03", None), ("04", ("guided-review",)), ("06", None),
                                                     ("10", None)]})
        # An ALWAYS VISIBLE line for a part with no disclosure class is allowed.
        widened = readme.replace("  03   every question's prompt;", "  02   the ask\n  03   every question's prompt;")
        self.assertNotEqual(widened, readme)
        self.assertTrue(visibility_matches(readme_visibility(widened), code_visibility()))

    def test_N74d_drifted_visibility_tables_detected(self):
        readme = self.readme()
        drifts = [
            ("  04   (guided-review only) per-finding", "  04   per-finding"),
            ("  04   (guided-review only) per-finding", "  05   (guided-review only) per-finding"),
            ("  04   every claim of the short reading", "       every claim of the short reading"),
            ("  10   the provenance table, as one block\n", "  10   the provenance table, as one block\n  08   x\n"),
        ]
        for old, new in drifts:
            with self.subTest(drift=new):
                drifted = readme.replace(old, new)
                self.assertNotEqual(drifted, readme)
                self.assertFalse(visibility_matches(readme_visibility(drifted), code_visibility()))

    def test_N74e_guided_review_contract_sentences(self):
        # The parity test compares part numbers and kind qualifiers; these pin the guided-review contract's words.
        readme = " ".join(self.readme().split())
        for sentence in (
            "04 every claim of the short reading and each qualification it needs",
            "04 (guided-review only) per-finding detail, quoted passages and locators, and supporting records, as "
            "closed detail after the visible reading; a disclosed finding or claim keeps its own status, limit and "
            "qualifications inside the same detail",
            "08 the whole register, never reduced to the limits each finding unit states (except as below for a "
            "guided review)",
            "In a guided review, unresolved items already stated visibly beside their claims in 04 are not repeated in "
            "08, and 08 carries the document-level non-claims.",
            "A guided review's dates stay visible in 02: when the sources it reports were observed, and when this copy "
            "was rendered, which re-checks nothing.",
            "A guided review requires no 06: a finding unit's significance field would have the author pre-answer the "
            "judgment the reviewer is asked to make.",
            "whether the visible reading states every claim and the qualifications each needs is a package-review "
            "check, which no build makes.",
            "A guided review's detail disclosure holds no request for a judgment:",
        ):
            with self.subTest(sentence=sentence[:40]):
                self.assertIn(sentence, readme)

    def test_U6_emitted_class_table_equals_readme(self):
        readme = self.readme()
        self.assertEqual(readme_class_sets(readme), {k: tuple(v) for k, v in build.CLASS_SETS.items()})

    def test_U6_drifted_emitted_class_table_detected(self):
        readme = self.readme()
        drifted = readme.replace("\nsummary   uo-index__mark\n", "\nsummary   uo-index__mark\nsummary   uo-card\n")
        self.assertNotEqual(drifted, readme)
        self.assertNotEqual(readme_class_sets(drifted), {k: tuple(v) for k, v in build.CLASS_SETS.items()})

    def test_U6_readme_states_the_rows_view_thresholds(self):
        readme = " ".join(self.readme().split())
        self.assertIn("a dense table of 7 or more columns or a narrative table of 6 or more while the column is below "
                      "its full 1120px, and a dense table of 9 or more or a narrative table of 8 or more at any width", readme)
        self.assertIn("th:nth-child(7)", build.WIDE_BELOW_CAP)
        self.assertIn("th:nth-child(9)", build.WIDE_ALWAYS)

    def test_N75_requirements_pin_equals_constant(self):
        with open(os.path.join(HERE, "requirements.txt"), encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
        self.assertEqual(lines, ["Markdown==%s" % build.MARKDOWN_PIN])


# Review annotations (README, "Review annotations"), design-system-ASK Review Semantics at 705a195: synthetic sources only.
ANNOTATED_02 = """## Reviewer brief

:::annotate
review open: on the frame rule below · whether it holds in every bay · decided by the owner
:::

:::range
:::annotate
review proposed: rev 3 · editor, round 2 · this paragraph
basis: editor draft
:::
The frame keeps {{mark proposed props: two props or fewer}} in each bay, and {{mark accepted bays: every [bay](https://example.org/bay)}} stays.
:::

:::note props
:::annotate
review correction-requested: on “two props or fewer” · owner, round 2
:::
The owner asked for a narrower phrase.
:::

:::note bays
:::annotate
review accepted: on “every bay” · owner, round 1
:::
:::

- {{review accepted: owner, round 1 · this item}}{{basis: owner-stated}} Each frame is printed once.
- Proofs reach the studio {{mark open month: before the end of each month}}, as [the plan](https://example.org/plan) says.
- {{review declined: owner, round 2 · this item}} Glossy stock is used.

:::note month
:::annotate
review open: on “before the end of each month” · awaiting the owner
:::
:::
"""

ANNOTATED_04 = """The synthetic executive result.

:::annotate
basis: owner-stated
evidence supported: 9 of 14, counted
:::

The method component, as described.

:::annotate list
item: the method component, version 0.3
state structural: schema-proven
basis: analyst synthesis
evidence partially-supported: tested in 2 of 5 cases
review accepted: version 0.3 · reviewer, round 2 · bounded trial
check: link check passed
:::

:::note not-yet-testable
:::annotate
evidence not-yet-testable: no readings until next season
:::
Readings cannot exist yet.
:::

:::range
:::annotate
review open: the reprint plan below · whether each frame is reprinted · owner
:::
:::table text text
| Frame | Basis |
|---|---|
| F-1 | {{basis: owner-stated}} |
:::
:::

:::table dense key text status
| Position | Claim | Decision |
|---|---|---|
| P-1 | first claim | {{review declined: reviewer, round 1 · replaced by P-2}} |
| P-2 | second claim | {{basis: owner-stated}} {{review accepted: reviewer, round 1}} |
:::

:::table text text
| Earlier position | Decision |
|---|---|
| P-3 | {{review open: carried to round 3}} |
:::
"""


def annotated(src=GUIDED):
    src = mutate(src, "What this synthetic document tests, and what not to judge.\n", ANNOTATED_02)
    return mutate(src, "The synthetic executive result.\n", ANNOTATED_04)


def in_04(text, src=GUIDED):
    """GUIDED with text added after part 04's first paragraph; the text's first line is line AT."""
    return mutate(src, "The synthetic executive result.\n", "The synthetic executive result.\n\n" + text)


AT = GUIDED.splitlines().index("The synthetic executive result.") + 3


def at(k=0):
    """The source line k lines into text added by in_04, as an error message names it."""
    return "line %d" % (AT + k)


def item(axis, role, label, meta=None):
    mark = '<span class="%s" data-%s="%s">%s</span>' % (build.REVIEW_MARK if axis == "review" else build.PLAIN_MARK,
                                                       axis, role, label)
    return '<span class="doc-annotation-item">%s%s</span>' % (mark, '<span class="doc-meta">%s</span>' % meta if meta else "")


def key_item(label, value):
    return '<span class="doc-annotation-item"><span class="doc-label">%s</span><span class="doc-meta">%s</span></span>' % (
        label, value)


def row(*items):
    return '<div class="doc-annotations">\n%s\n</div>' % "\n".join(items)


def passage(role, name, words):
    return '<mark class="doc-passage-mark surface-scope-underline" data-review="%s" aria-describedby="uo-note-%s">%s</mark>' % (
        role, name, words)


RANGE_OPEN = '<div class="doc-group doc-annotation-range surface-labeled-range">\n'
NOTE = ":::note n\n:::annotate\nreview open\n:::\n:::\n"


def ranged(review, text, extra=""):
    """A :::range whose row names one review item (and any further items), over text."""
    return ":::range\n:::annotate\n%s\n%s:::\n%s\n:::\n" % (review, extra, text)


def row_of(src, text):
    """The 1-based source line that holds text."""
    return next(i + 1 for i, line in enumerate(src.splitlines()) if text in line)


CELL = ":::table text text\n| A | B |\n|---|---|\n| x | %s |\n:::\n"


class ReviewAnnotations(RenderCase):
    def test_RS_leading_single_block_range(self):
        # A judgment on one paragraph opens a range: its row first, its review item leading, then the paragraph.
        h = self.render(in_04(ranged("review accepted: v3 · owner · this paragraph", "One judged paragraph.",
                                     "basis: owner-stated\n")))["html"]
        self.assertIn(RANGE_OPEN + row(item("review", "accepted", "Accepted", "v3 · owner · this paragraph"),
                                       key_item("Basis", "owner-stated"))
                      + '\n<div class="doc-prose">\n<p class="doc-body">One judged paragraph.</p>\n</div>\n</div>', h)
        # Several blocks, a lead-in and its list, sit in one range; a quotation and a callout keep their rails inside it.
        self.reset_tmp()
        h = self.render(in_04(ranged("review open: awaiting the owner · the lead-in and both items",
                                     "Two choices remain:\n\n- the square crop;\n- the winter set.\n\n> Quoted words.\n\n"
                                     ":::callout\nThe document's own point.\n:::")))["html"]
        self.assertIn(RANGE_OPEN + row(item("review", "open", "Open question", "awaiting the owner · the lead-in and both items"))
                      + '\n<div class="doc-prose">\n<p class="doc-body">Two choices remain:</p>\n<ul>\n'
                        '<li class="doc-body">the square crop;</li>\n<li class="doc-body">the winter set.</li>\n</ul>\n'
                        '<blockquote class="doc-quote">\n<p>Quoted words.</p>\n</blockquote>\n'
                        '<p class="doc-body surface-emphasis-rail" data-uo-role="callout">The document\'s own point.</p>\n'
                        '</div>\n</div>', h)

    def test_RS_trailing_review_row_fails(self):
        # The composition's first model (#178, never adopted here) put a review row after its block; a row after a block
        # is read as introducing what follows it.
        src = in_04("One paragraph.\n\n:::annotate\nreview accepted: v3 · owner · this copy\n:::\n")
        self.fails(src, r"%s: a review judgment on whole blocks opens a :::range, even over one paragraph" % at(2))
        # So does a row after a heading, and after a table.
        self.reset_tmp()
        self.fails(in_04("### A section\n\n:::annotate\nreview open: x\n:::\n\nWords.\n"),
                   r"%s: a review judgment on whole blocks opens a :::range" % at(2))
        self.reset_tmp()
        self.fails(in_04(TABLE + "\n:::annotate\nreview proposed: x\n:::\n"),
                   r"line \d+: a review judgment on whole blocks opens a :::range")

    def test_RS_one_paragraph_judgment_without_a_range_fails(self):
        # The withdrawn single-block exemption: a leading review row over one paragraph, without a range.
        self.fails(in_04(":::annotate\nreview proposed: rev 3 · editor · this paragraph\n:::\n\nOne paragraph.\n"),
                   r"%s: a review judgment on whole blocks opens a :::range, even over one paragraph: its :::annotate row "
                   r"is the range's first child" % at())

    def test_RS_nested_range_fails(self):
        inner = ranged("review accepted: x · y", "Inner.")
        self.fails(in_04(ranged("review proposed: a", "Outer.\n\n" + inner)),
                   r"%s: :::range sits inside :::range \(%s\); ranges never nest" % (at(6), at()))

    def test_RS_one_judgment_per_range(self):
        cases = [
            (in_04(":::range\n:::annotate\nreview proposed: a\nreview accepted: b\n:::\nWords.\n:::\n"),
             r"%s: one judgment per range: a second review item" % at(3)),
            (in_04(":::range\n:::annotate\nbasis: owner-stated\n:::\nWords.\n:::\n"),
             r"%s: a :::range's row names its one review judgment first; evidence and state never open a range" % at(1)),
            (in_04(":::range\n:::annotate\nbasis: owner-stated\nreview open: x\n:::\nWords.\n:::\n"),
             r"%s: a row holding a review item opens a :::range or stands as a prompt before one, and leads with its review "
             r"item" % at(3)),
            (in_04(":::range\n:::annotate\nreview open: x\n:::\nWords.\n\n:::annotate\nbasis: y\n:::\n:::\n"),
             r"%s: :::annotate \(%s\) sits inside :::range \(%s\), which holds one :::annotate row, as its first child"
             % (at(6), at(6), at())),
            (in_04(":::range\nWords first.\n\n:::annotate\nreview open: x\n:::\n:::\n"),
             r"%s: :::annotate \(%s\) sits inside :::range" % (at(3), at(3))),
            (in_04(":::range\n:::annotate list\nitem: a\nreview open: x\n:::\nWords.\n:::\n"),
             r"%s: a :::range opens with an :::annotate row naming its one judgment, not a list" % at(1)),
            (in_04(":::range\nWords without a row.\n:::\n"), r"%s: :::range \(%s\) opens with its :::annotate row" % (at(), at())),
            (in_04(":::range\n:::annotate\nreview open: x\n:::\n:::\n"), r"%s: :::range \(%s\) covers at least one block after "
                                                                          r"its row" % (at(), at())),
            (in_04(ranged("review open: x", "Words {{mark open n: here}}.\n\n" + NOTE)),
             r"%s: :::note n \(%s\) sits inside :::range \(%s\); a note on words a range holds follows the range"
             % (at(6), at(6), at())),
            (in_04(ranged("review open: x", "Words.\n\n### A heading\n\nMore.")),
             r"%s: :::range \(%s\) holds a heading: .* a range over a heading alone is a UO capability limit for now; raise "
             r"it with the owner" % (at(6), at())),
            (in_04(ranged("review open: x", ":::disclose evidence \"E\"\nDetail.\n:::")),
             r"%s: :::disclose sits inside :::range \(%s\); a range holds its :::annotate row, then the blocks it covers"
             % (at(4), at())),
            (in_04(":::callout\nA point.\n\n" + ranged("review open: x", "Words.") + ":::\n"),
             r":::range is allowed inside :::part, :::question, :::finding, :::disclose only, not :::callout"),
            (mutate(GUIDED, "Synthetic locator line.\n", "Synthetic locator line.\n\n" + ranged("review open: x", "W.")),
             r":::range \(line \d+\) is not allowed in part 01, which carries generated chrome"),
            (mutate(GUIDED, "Synthetic provenance block.\n", "Synthetic provenance block.\n\n" + ranged("review open: x", "W.")),
             r":::range \(line \d+\) is not allowed in a provenance disclosure"),
            (in_04(":::range local=x\n:::annotate\nreview open: x\n:::\nW.\n:::\n"), r"%s: :::range takes no local= hook" % at()),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)
        # Blocks judged otherwise are a sibling range, 24px apart by the shared rule.
        self.reset_tmp()
        h = self.render(in_04(ranged("review proposed: a", "First.") + "\n" + ranged("review accepted: b · owner", "Second.")))["html"]
        self.assertIn('<p class="doc-body">First.</p>\n</div>\n</div>\n' + RANGE_OPEN, h)

    def test_RS_explicit_target_prompt(self):
        prompt = ":::annotate\nreview open: for each frame in the range below, may it be printed again? · owner\n:::\n\n"
        second = ":::annotate\nreview proposed: a second question about the range below · editor\n:::\n\n"
        h = self.render(in_04(prompt + second + ranged("review proposed: editor, round 2 · the print plan", "The plan.")))["html"]
        self.assertIn(row(item("review", "open", "Open question", "for each frame in the range below, may it be printed again? · owner"))
                      + "\n" + row(item("review", "proposed", "Proposed", "a second question about the range below · editor"))
                      + "\n" + RANGE_OPEN + row(item("review", "proposed", "Proposed", "editor, round 2 · the print plan")), h)
        cases = [
            (in_04(prompt + "A paragraph, not a range.\n"), r"%s: a review judgment on whole blocks opens a :::range" % at()),
            (in_04(prompt + ":::annotate\nbasis: x\n:::\n\n" + ranged("review open: y", "W.")),
             r"%s: a review judgment on whole blocks opens a :::range" % at()),
            (in_04(prompt), r"%s: a review judgment on whole blocks opens a :::range" % at()),
            (in_04(":::annotate\nreview open: q1\nreview proposed: q2\n:::\n\n" + ranged("review open: y", "W.")),
             r"%s: one judgment per row: a second review item" % at(2)),
            (in_04(":::annotate\nstate held: s\nreview open: q\n:::\n\n" + ranged("review open: y", "W.")),
             r"%s: a row holding a review item .* leads with its review item" % at(2)),
            (in_04(":::annotate\nreview open: q\nevidence supported: e\nstate held: s\n:::\n\n" + ranged("review open: y", "W.")),
             r"%s: annotation items read in the order review, state, basis, evidence, check; evidence comes after state" % at(3)),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)
        # A prompt may open its container: it precedes the range it names.
        self.reset_tmp()
        self.render(mutate(GUIDED, ":::part 04\nThe synthetic executive result.\n",
                           ":::part 04\n" + prompt + ranged("review open: y", "The synthetic executive result.")))

    def test_RS_passage_marks_pending_and_decided(self):
        h = self.render(annotated())["html"]
        self.assertIn('The frame keeps %s in each bay, and %s stays.'
                      % (passage("proposed", "props", "two props or fewer"),
                         passage("accepted", "bays", 'every <a class="surface-text-link" href="https://example.org/bay">bay</a>')), h)
        self.assertIn('<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-props">\n%s\n'
                      '<p class="doc-body">The owner asked for a narrower phrase.</p>\n</div>'
                      % row(item("review", "proposed", "Correction requested", "on “two props or fewer” · owner, round 2")), h)
        for role, record in (("accepted", "review accepted: on “here” · owner"), ("declined", "review declined: on “here” · owner"),
                             ("open", "review open"), ("proposed", "review proposed: a narrower phrase")):
            with self.subTest(role=role):
                self.reset_tmp()
                h = self.render(in_04("Words {{mark %s n: here}}.\n\n:::note n\n:::annotate\n%s\n:::\n:::\n" % (role, record)))["html"]
                self.assertIn('<p class="doc-body">Words %s.</p>' % passage(role, "n", "here"), h)
        self.reset_tmp()
        self.fails(in_04("Words {{mark none n: here}}.\n\n" + NOTE),
                   r"%s: No decision recorded marks no words: a passage mark names the judgment its words take, proposed, "
                   r"open, accepted, declined, not 'none'" % at())

    def test_RS_passage_mark_without_a_note_fails(self):
        self.fails(in_04("Words {{mark accepted n: here}}.\n"),
                   r"%s: the passage mark naming note 'n' has no :::note n after it in :::part 04" % at())
        self.reset_tmp()
        self.fails(in_04(ranged("review open: x", "Words {{mark declined n: here}}.")),
                   r"%s: the passage mark naming note 'n' has no :::note n after it in :::part 04" % at(4))

    def test_RS_note_follows_the_range_holding_its_mark(self):
        src = in_04(ranged("review proposed: a · this paragraph", "Words {{mark accepted n: here}}.")
                    + "\n:::annotate\nbasis: owner-stated\n:::\n\n:::note n\n:::annotate\nreview accepted: on “here” · owner\n:::\n:::\n")
        h = self.render(src)["html"]
        self.assertIn('<p class="doc-body">Words %s.</p>\n</div>\n</div>\n%s\n'
                      '<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-n">'
                      % (passage("accepted", "n", "here"), row(key_item("Basis", "owner-stated"))), h)
        # A block or another range before the note separates it from its mark.
        for between in ("Another block.\n\n", ranged("review open: b", "Second.") + "\n"):
            with self.subTest(between=between[:12]):
                self.reset_tmp()
                self.fails(in_04(ranged("review proposed: a", "Words {{mark accepted n: here}}.") + "\n" + between + NOTE),
                           r"%s: the passage mark naming note 'n' is followed by another block or container before its note"
                           % at(4))

    def test_RS_a_mark_in_any_block_a_range_covers_has_its_note_after_the_range(self):
        # The range's later blocks follow a mark in an earlier one; its note waits for the whole range, then follows
        # it, and the final HTML passes the allowlist.
        h = self.render(in_04(ranged("review open: a · these paragraphs", "Words {{mark open n: here}}.\n\nSecond.")
                              + "\n" + NOTE))["html"]
        self.assertIn('%s%s\n<div class="doc-prose">\n<p class="doc-body">Words %s.</p>\n<p class="doc-body">Second.</p>\n'
                      '</div>\n</div>\n<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-n">'
                      % (RANGE_OPEN, row(item("review", "open", "Open question", "a · these paragraphs")),
                         passage("open", "n", "here")), h)
        build.check_final_html(h, 2)
        # Marks in a paragraph and a list item, then a callout, a structure and a whole table the range covers;
        # each mark's note follows the range, in either order.
        note_m = NOTE.replace(":::note n", ":::note m")
        blocks = ("Words {{mark open n: here}}.\n\n- an item with {{mark open m: there}}\n- another item\n\n"
                  ":::callout\nA point.\n:::\n\n:::structure\nA line\n  beneath it\n:::\n\n"
                  + CELL % "y" + "\nA closing paragraph.")
        for notes in (NOTE + "\n" + note_m, note_m + "\n" + NOTE):
            with self.subTest(first=notes[:10]):
                self.reset_tmp()
                r = self.render(in_04(ranged("review open: a", blocks) + "\n" + notes))
                h = r["html"]
                self.assertEqual((r["counts"]["passage_marks"], r["counts"]["annotation_notes"]), (2, 2))
                end = h.index("A closing paragraph.</p>\n</div>\n</div>\n")
                for mark in (passage("open", "n", "here"), passage("open", "m", "there")):
                    self.assertLess(h.index(RANGE_OPEN), h.index(mark))
                    self.assertLess(h.index(mark), end)
                for note in ("uo-note-n", "uo-note-m"):
                    self.assertGreater(h.index('id="%s"' % note), end)
                build.check_final_html(h, 2)
        # A synthesis is a block the range covers too: a mark in an earlier block has its note after the range, which
        # the synthesis's finality admits.
        self.reset_tmp()
        h = self.render(mutate(GUIDED, "The synthetic executive result.\n", "The synthetic executive result.\n\n"
                               + ranged("review open: a", "Words {{mark open n: here}}.\n\n:::synthesis\nWhat the part "
                                        "comes to.\n:::\n") + "\n" + NOTE))["html"]
        self.assertLess(h.index('data-uo-role="synthesis"'), h.index('id="uo-note-n"'))
        build.check_final_html(h, 2)

    def test_RS_a_ranges_note_still_follows_the_whole_range(self):
        # The range lets its own blocks follow a mark, and nothing else: a block or another range after the range
        # still separates the note from its mark, outside a range a block still does, and inside one a note, a
        # nested range or a heading still fails.
        two = ranged("review open: a", "Words {{mark open n: here}}.\n\nSecond.")
        for between in ("Another block.\n\n", ranged("review open: b", "Third.") + "\n"):
            with self.subTest(between=between[:12]):
                self.reset_tmp()
                self.fails(in_04(two + "\n" + between + NOTE),
                           r"%s: the passage mark naming note 'n' is followed by another block or container before its note"
                           % at(4))
        self.reset_tmp()
        self.fails(in_04("Words {{mark open n: here}}.\n\nSecond.\n\n" + NOTE),
                   r"%s: the passage mark naming note 'n' is followed by another block or container before its note" % at())
        inside = [
            ("Words {{mark open n: here}}.\n\n" + NOTE, r"%s: :::note n \(%s\) sits inside :::range \(%s\); a note on words "
                                                         r"a range holds follows the range" % (at(6), at(6), at())),
            ("Words {{mark open n: here}}.\n\n" + ranged("review open: b", "Third."),
             r"%s: :::range sits inside :::range \(%s\); ranges never nest" % (at(6), at())),
            ("Words {{mark open n: here}}.\n\n### A heading\n\nUnder it.",
             r"%s: :::range \(%s\) holds a heading" % (at(6), at())),
        ]
        for blocks, pattern in inside:
            with self.subTest(pattern=pattern[10:40]):
                self.reset_tmp()
                self.fails(in_04(ranged("review open: a", blocks) + "\n" + NOTE), pattern)
        # A note still records the words of one block: marks naming one note in two blocks of a range fail at the
        # later mark, while two marks in one block name one note.
        for second in ("B {{mark open n: y}}.", "- an item with {{mark open n: y}}\n- another item"):
            with self.subTest(second=second[:6]):
                self.reset_tmp()
                self.fails(in_04(ranged("review open: a", "A {{mark open n: x}}.\n\n" + second) + "\n" + NOTE),
                           r"%s: passage marks in two blocks name note 'n'; a note records the words of one block, as it "
                           r"does those of one list item" % at(6))
        self.reset_tmp()
        r = self.render(in_04(ranged("review open: a", "A {{mark open n: x}} and {{mark open n: y}}.\n\nB.") + "\n" + NOTE))
        self.assertEqual((r["counts"]["passage_marks"], r["counts"]["annotation_notes"]), (2, 1))

    def test_RS_note_attaches_inside_a_plain_list_item(self):
        h = self.render(annotated())["html"]
        note = ('<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-month">\n%s\n</div>'
                % row(item("review", "open", "Open question", "on “before the end of each month” · awaiting the owner")))
        self.assertIn('<li class="doc-body">Proofs reach the studio %s, as <a class="surface-text-link" '
                      'href="https://example.org/plan">the plan</a> says.\n%s</li>'
                      % (passage("open", "month", "before the end of each month"), note), h)
        self.assertEqual(h.count('id="uo-note-month"'), 1)
        # A loose item takes the note after its paragraphs; a tight item with a nested list, before that list; a second
        # note on one item follows the first.
        cases = [
            ("- First item.\n\n- Second {{mark open n: here}}.\n\n    More of the item.\n",
             '<li class="doc-body">\n<p class="doc-body">Second %s.</p>\n<p class="doc-body">More of the item.</p>\n'
             '<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-n">' % passage("open", "n", "here")),
            ("- Top {{mark open n: here}}.\n    - nested\n",
             '<li class="doc-body">Top %s.\n<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-n">\n%s\n</div>'
             '\n<ul>\n<li class="doc-body">nested</li>' % (passage("open", "n", "here"), row(item("review", "open", "Open question")))),
            ("- Nested parent\n    - inner {{mark open n: here}}.\n",
             '<li class="doc-body">inner %s.\n<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-n">'
             % passage("open", "n", "here")),
        ]
        for text, want in cases:
            with self.subTest(text=text[:20]):
                self.reset_tmp()
                self.assertIn(want, self.render(in_04(text + "\n" + NOTE))["html"])
        self.reset_tmp()
        h = self.render(in_04("- One {{mark open n: a}} and {{mark open m: b}}.\n\n" + NOTE
                              + "\n:::note m\n:::annotate\nreview open\n:::\n:::\n"))["html"]
        self.assertLess(h.index('id="uo-note-n"'), h.index('id="uo-note-m"'))
        self.assertLess(h.index('id="uo-note-m"'), h.index("</li>", h.index('id="uo-note-n"')))
        # Words in an item host keep their note after the list.
        self.reset_tmp()
        h = self.render(in_04("- {{review open: x · this item}} Words {{mark accepted n: here}}.\n\n"
                              ":::note n\n:::annotate\nreview accepted: on “here” · owner\n:::\n:::\n"))["html"]
        self.assertIn('</p></li>\n</ul>\n</div>\n<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-n">', h)

    def test_RS_item_host(self):
        h = self.render(annotated())["html"]
        self.assertIn('<ul>\n<li class="doc-annotation-range surface-labeled-range">%s<p class="doc-body">Each frame is printed '
                      'once.</p></li>\n<li class="doc-body">Proofs reach' % row(
                          item("review", "accepted", "Accepted", "owner, round 1 · this item"), key_item("Basis", "owner-stated")), h)
        self.assertIn('<li class="doc-annotation-range surface-labeled-range">%s<p class="doc-body">Glossy stock is used.</p></li>'
                      % row(item("review", "declined", "Declined", "owner, round 2 · this item")), h)
        # A loose item keeps its further paragraphs after its words; consecutive hosts are allowed.
        self.reset_tmp()
        h = self.render(in_04("- {{review open: a · this item}} First.\n\n    Its second paragraph.\n\n"
                              "- {{review proposed: b · this item}} Second.\n"))["html"]
        self.assertIn('<li class="doc-annotation-range surface-labeled-range">%s<p class="doc-body">First.</p>\n'
                      '<p class="doc-body">Its second paragraph.</p>\n</li>' % row(item("review", "open", "Open question",
                                                                                      "a · this item")), h)
        self.assertEqual(h.count('<li class="doc-annotation-range surface-labeled-range">'), 2)
        cases = [
            (in_04(ranged("review open: x", "- {{review accepted: y}} Words.")),
             r"%s: an item host never sits inside a :::range" % at(4)),
            (in_04("Words {{mark open n: x}}.\n\n:::note n\n:::annotate\nreview open\n:::\n- {{review open: y}} In a note.\n:::\n"),
             r"%s: an annotation item \{\{review \.\.\.\}\} sits in a :::table body cell, or opens a list item in body text "
             r"as an item host; not in :::note n" % at(6)),
            (in_04(":::quote\n- {{review open: y}} Quoted.\n:::\n"), r"not in :::quote"),
            (in_04(":::callout\n- {{review open: y}} Called out.\n:::\n"), r"not in :::callout"),
            (in_04("- Parent\n    - {{review open: y}} Nested.\n"), r"%s: an item host is an item of a top-level list, never of "
                                                                     r"a nested list" % at(1)),
            (in_04("- Words first {{review open: y}}.\n"), r"%s: an item host's row opens its list item: its items come first, "
                                                          r"before any of the item's words" % at()),
            (in_04("- {{review open: a}}{{review accepted: b}} Words.\n"),
             r"%s: an item host carries one review judgment; a second judgment on one whole list item is raised with the "
             r"owner" % at()),
            (in_04("- {{basis: owner}} Words.\n"), r"%s: an item host's row leads with its review item" % at()),
            (in_04("- {{review open: a}}{{evidence supported: e}}{{basis: b}} Words.\n"),
             r"%s: an item host's items read in the order review, state, basis, evidence, check; evidence comes after basis"
             % at()),
            (in_04("- {{review open: a}}\n"), r"%s: an item host's words follow its row" % at()),
            (in_04("- **{{review open: a}}** Words.\n"), r"%s: an item host's row opens its list item" % at()),
            (in_04("Words {{review open: x}}.\n"), r"%s: an annotation item \{\{review \.\.\.\}\} sits in a :::table body cell, "
                                                  r"or opens a list item as an item host" % at()),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_RS_annotation_list_names_its_item(self):
        h = self.render(annotated())["html"]
        self.assertIn('<dl class="doc-annotation-list">\n'
                      '<dt class="doc-label">Item</dt>\n<dd><span class="doc-meta">the method component, version 0.3</span></dd>\n'
                      '<dt class="doc-label">State</dt>\n<dd>%s</dd>\n'
                      '<dt class="doc-label">Basis</dt>\n<dd><span class="doc-meta">analyst synthesis</span></dd>\n'
                      '<dt class="doc-label">Evidence</dt>\n<dd>%s</dd>\n'
                      '<dt class="doc-label">Review</dt>\n<dd>%s</dd>\n'
                      '<dt class="doc-label">Check</dt>\n<dd><span class="doc-meta">link check passed</span></dd>\n</dl>'
                      % ('<span class="doc-mark doc-label" data-state="structural">Structural</span><span class="doc-meta">schema-proven</span>',
                         '<span class="doc-mark doc-label" data-evidence="partially-supported">Partially supported</span>'
                         '<span class="doc-meta">tested in 2 of 5 cases</span>',
                         '<span class="%s" data-review="accepted">Accepted</span>'
                         '<span class="doc-meta">version 0.3 · reviewer, round 2 · bounded trial</span>' % build.REVIEW_MARK), h)
        self.assertIn('<div class="doc-group doc-annotation-note" data-evidence="not-yet-testable">\n%s\n'
                      '<p class="doc-body">Readings cannot exist yet.</p>\n</div>'
                      % row(item("evidence", "not-yet-testable", "Not yet testable", "no readings until next season")), h)
        cases = [
            (in_04(":::annotate list\nevidence supported: e\nreview accepted: v1 · owner\n:::\n"),
             r"%s: an :::annotate list with a review line names the item it judges first, in an `item: <name>` line" % at()),
            (in_04(":::annotate list\nevidence supported: e\nitem: x\n:::\n"),
             r"%s: an annotation list names its item first, in one `item:` line" % at(2)),
            (in_04(":::annotate\nitem: x\nbasis: b\n:::\n"), r"%s: an `item:` line names the item an :::annotate list judges; "
                                                             r"a row takes none" % at(1)),
            (in_04(":::annotate list\nitem:  \nbasis: b\n:::\n"), r"%s: the item line's text after ':' must contain visible text"
                                                                  % at(1)),
            (in_04(":::annotate list\nitem: x\n:::\n"), r"%s: :::annotate list \(%s\) is empty; it holds at least one item line "
                                                        r"after its `item:` line" % (at(), at())),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)
        # Without a review line the Item line is optional.
        self.reset_tmp()
        self.assertNotIn('<dt class="doc-label">Item</dt>', self.render(in_04(":::annotate list\nbasis: b\ncheck: c\n:::\n"))["html"])

    def test_RS_document_record(self):
        record = ":::annotate document\nbasis: synthetic fixture\nreview open: on SYN-GR-001 as a whole · the reviewer decides\n:::\n\n"
        src = mutate(GUIDED, ":::part 01\n", record + ":::part 01\n")
        r = self.render(src)
        self.assertIn('<h1 class="doc-title">Synthetic guided review</h1>\n%s\n<dl class="uo-head__meta">' % row(
            key_item("Basis", "synthetic fixture"),
            item("review", "open", "Open question", "on SYN-GR-001 as a whole · the reviewer decides")), r["html"])
        self.assertEqual(r["counts"]["document_records"], 1)
        self.assertEqual(r["inlined"], build.MODULES + build.STATE_MODULES)
        self.assertIn("| document record (:::annotate document) | `1` |", r["manifest_text"])
        build.check_final_html(r["html"], 2)
        cases = [
            (mutate(GUIDED, ":::part 02\n", record + ":::part 02\n"), r"line \d+: :::annotate document comes before the first :::part"),
            (mutate(GUIDED, ":::part 01\n", record + record + ":::part 01\n"), r"line \d+: a document carries one :::annotate "
                                                                             r"document record"),
            (in_04(":::annotate document\nbasis: x\n:::\n"), r"%s: :::annotate document is the document's own record: it sits at "
                                                            r"top level" % at()),
            (mutate(GUIDED, ":::part 01\n", ":::annotate document\nreview open: a\nreview none: b\nbasis: c\n:::\n\n:::part 01\n"),
             r"line \d+: annotation items read in the order state, basis, evidence, review, check; review comes after basis"),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_RS_tables(self):
        h = self.render(annotated())["html"]
        self.assertIn('<td class="doc-table-cell" data-uo-cell="status" data-uo-label="Decision"><span class="uo-cell-label doc-label">'
                      'Decision</span><span class="doc-annotations">%s</span></td>'
                      % item("review", "declined", "Declined", "reviewer, round 1 · replaced by P-2"), h)
        self.assertIn('<span class="uo-cell-label doc-label">Decision</span><span class="doc-annotations">%s%s</span></td>'
                      % (key_item("Basis", "owner-stated"), item("review", "accepted", "Accepted", "reviewer, round 1")), h)
        # A whole-table range, its cells carrying no judgment of their own.
        self.assertIn(RANGE_OPEN + row(item("review", "open", "Open question", "the reprint plan below · whether each frame is "
                                            "reprinted · owner")) + '\n<div class="doc-prose">\n<table>\n', h)
        self.assertNotIn("doc-table-scroll", h.split("<body>")[1])
        cases = [
            (in_04(ranged("review proposed: the plan", CELL.rstrip("\n") % "{{review accepted: v1 · owner}}")),
             r"line %d: a :::table whose cells carry review items cannot sit in a :::range" % (AT + 4)),
            (in_04(":::table text text\n| A | B |\n|---|---|\n:::range\n:::annotate\nreview open: x\n:::\n| x | y |\n:::\n:::\n"),
             r"%s: :::range inside :::table \(%s\): a per-cell block range is a UO capability limit: .* raise it with the owner"
             % (at(3), at())),
            (in_04(CELL % "{{range open: x}}"), r"%s: a per-cell block range is a UO capability limit" % at(3)),
            (in_04("Words {{range open: x}}.\n"), r"%s: `\{\{range` is not an annotation: a judgment on whole blocks opens a "
                                                  r":::range container" % at()),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_RS_every_vocabulary_word_takes_its_role_and_label(self):
        marks = ["state %s" % w for w in build.STATE_WORDS] + ["evidence %s" % w for w in build.EVIDENCE_WORDS]
        table = ":::table text status\n| Claim | Decision |\n|---|---|\n%s\n:::\n" % "\n".join(
            "| c%d | {{review %s: x}} |" % (i, w) for i, w in enumerate(build.REVIEW_WORDS))
        h = self.render(in_04(":::annotate\n%s\n:::\n\nA second block.\n\n%s" % ("\n".join(marks), table)))["html"]
        for w, label in build.STATE_WORDS.items():
            self.assertIn(item("state", w, label), h)
        for w, label in build.EVIDENCE_WORDS.items():
            self.assertIn(item("evidence", w, label), h)
        for w, (role, label) in build.REVIEW_WORDS.items():
            self.assertIn(item("review", role, label, "x"), h)
        # the owner's checker vocabulary (role-conformance.js C12) is the renderer's
        self.assertEqual(build.FACET_VALUES, {"data-review": ("accepted", "declined", "none", "open", "proposed"),
                                              "data-evidence": ("supported", "partially-supported", "unresolved",
                                                                "weakened", "not-yet-testable"),
                                              "data-state": ("earned", "structural", "partial", "deflated", "held",
                                                             "external", "proposed", "neutral")})
        self.assertEqual(build.PASSAGE_ROLES, ("proposed", "open", "accepted", "declined"))

    def test_RS_meta_is_plain_text_and_escaped(self):
        h = self.render(in_04(":::annotate\nbasis: a <b> & *c* `d`\n:::\n"))["html"]
        self.assertIn(key_item("Basis", "a &lt;b&gt; &amp; *c* `d`"), h)

    def test_RS_annotations_in_question_finding_and_disclosure(self):
        # A question and a finding take ranges, rows, lists, passage marks and notes (prompts:
        # test_RS_prompts_in_a_question_a_finding_and_a_disclosure).
        src = mutate(GUIDED, "The central question prompt.\n",
                     ":::range\n:::annotate\nreview open: awaiting the reviewer · this question\n:::\nThe central question prompt.\n:::\n")
        src = mutate(src, "**Status:** open. Finding, significance and limit.\n",
                     "**Status:** open. Finding, {{mark open lst: significance}} and limit.\n\n:::annotate list\n"
                     "evidence unresolved: two readings disagree\n:::\n\n:::note lst\n:::annotate\nreview open: whose reading\n:::\n:::\n")
        r = self.render(src)
        self.assertIn('<div data-uo-role="question" data-uo-central="true" class="doc-section">\n' + RANGE_OPEN, r["html"])
        self.assertEqual({k: r["counts"][k] for k in build.ANNOTATION_COUNTS},
                         {"annotation_rows": 2, "annotation_lists": 1, "annotation_notes": 1, "passage_marks": 1,
                          "cell_items": 0, "annotation_ranges": 1, "item_hosts": 0, "document_records": 0})

    def test_RS_annotations_inside_an_authored_disclosure(self):
        # A question-detail or evidence disclosure takes what its container takes: ranges, rows, lists,
        # notes, passage marks, item hosts and cell items. A passage mark and its note sit in one disclosure.
        src = mutate(GUIDED, "Field-level listing.\n",
                     "Field-level listing.\n\n:::annotate\nstate held: until the second pass\nbasis: survey sheet\n"
                     "evidence supported: two sheets agree\n:::\n\n"
                     + ranged("review open: whose total · the second listing · owner", "A second listing, {{mark open lst: one "
                              "reading}} in question.")
                     + "\n:::note lst\n:::annotate\nreview open: which sheet\n:::\nOn “one reading”: which sheet holds it?\n:::\n\n"
                     ":::note not-yet-testable\n:::annotate\nevidence not-yet-testable: no readings until next season\n:::\n:::\n\n"
                     "- {{review accepted: v2 · owner · this line}} A disclosed line.\n\n"
                     + CELL % "{{review accepted: v2 · owner · this listing}}")
        src = mutate(src, "The non-central question's detail.\n",
                     "The non-central question's detail, {{mark proposed qd: as worded}}.\n\n:::annotate list\n"
                     "state external: the archive\nevidence unresolved: two readings\n:::\n\n"
                     ":::note qd\n:::annotate\nreview correction-requested: owner, round 2\n:::\n:::\n")
        r = self.render(src)
        h = r["html"]
        self.assertEqual({k: r["counts"][k] for k in build.ANNOTATION_COUNTS},
                         {"annotation_rows": 5, "annotation_lists": 1, "annotation_notes": 3, "passage_marks": 2,
                          "cell_items": 1, "annotation_ranges": 1, "item_hosts": 1, "document_records": 0})
        evidence = h[h.index('<details data-uo-disclose="evidence"'):]
        evidence = evidence[:evidence.index("</details>")]
        for piece in (item("state", "held", "Held", "until the second pass"), RANGE_OPEN,
                      passage("open", "lst", "one reading"), '<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-lst">',
                      '<div class="doc-group doc-annotation-note" data-evidence="not-yet-testable">',
                      '<li class="doc-annotation-range surface-labeled-range">',
                      item("review", "accepted", "Accepted", "v2 · owner · this listing")):
            self.assertIn(piece, evidence)
        detail = h[h.index('<details data-uo-disclose="question-detail"'):]
        detail = detail[:detail.index("</details>")]
        for piece in (passage("proposed", "qd", "as worded"), '<dl class="doc-annotation-list">',
                      '<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-qd">',
                      item("review", "proposed", "Correction requested", "owner, round 2")):
            self.assertIn(piece, detail)
        build.check_final_html(h, 2)
        # A mark and its record stay in one scope, and the provenance disclosure takes no annotation.
        out = mutate(GUIDED, "Field-level listing.\n:::\n",
                     "Field-level listing, {{mark open n: here}}.\n:::\n\n" + NOTE)
        into = mutate(mutate(GUIDED, "**Status:** open. Finding, significance and limit.\n",
                             "**Status:** open. Finding, {{mark open n: significance}} and limit.\n"),
                      "Field-level listing.\n", "Field-level listing.\n\n" + NOTE)
        provenance = [mutate(GUIDED, "Synthetic provenance block.\n", "Synthetic provenance block.\n\n" + extra) for extra in (
            ":::note not-yet-testable\n:::annotate\nevidence not-yet-testable: y\n:::\n:::\n",
            ranged("review open: x", "W."), ":::annotate\nbasis: x\n:::\n")]
        cases = [
            (out, r"line %d: the passage mark naming note 'n' has no :::note n after it in :::disclose evidence"
                  % row_of(out, "{{mark")),
            (into, r"line %d: :::note n \(line %d\) follows no passage mark naming it in :::disclose evidence"
                   % (row_of(into, ":::note n"), row_of(into, ":::note n"))),
        ] + [(src, r"line %d: :::(note not-yet-testable|range|annotate) \(line %d\) is not allowed in a provenance disclosure"
              % (row_of(src, "Synthetic provenance block.") + 2, row_of(src, "Synthetic provenance block.") + 2))
             for src in provenance]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_RS_code_spans_keep_braces_literal(self):
        h = self.render(in_04("Write `{{mark open x: y}}` and\n\n```\n{{ fenced }}\n```\n\n:::structure\n{{ structured }}\n:::\n"))["html"]
        self.assertIn('<code class="doc-code">{{mark open x: y}}</code>', h)
        self.assertIn("{{ fenced }}", h)
        self.assertIn('<pre class="doc-pre-part">{{ structured }}</pre>', h)
        self.assertNotIn("doc-passage-mark", h)

    def test_RS_review_semantics_modules_inline_only_when_a_document_annotates(self):
        modules = {}
        for rel in build.MODULES + build.STATE_MODULES:
            with open(os.path.join(HERE, "_dsa-surface", rel), encoding="utf-8") as f:
                modules[rel] = f.read()
        plain = self.render(GUIDED, name="plain")
        head = plain["html"].split("</head>")[0]
        for rel in build.STATE_MODULES:
            self.assertNotIn(modules[rel], head)
            self.assertNotIn("SEALED design-system-ASK %s" % rel, head)
        self.assertEqual(plain["inlined"], build.MODULES)
        self.assertIn("| modules inlined, in order | `%s` |" % " ".join(build.MODULES), plain["manifest_text"])
        rich = self.render(annotated(), name="rich")
        head = rich["html"].split("</head>")[0]
        at_ = head.index("--tracking-caption")          # inside the token CSS
        for rel in build.MODULES + build.STATE_MODULES:
            i = head.find(modules[rel])
            self.assertGreater(i, at_, rel)
            self.assertEqual(head.count(modules[rel]), 1, rel)
            at_ = i
        self.assertLess(at_, head.index("urban-observatory // review-document overlay"))
        self.assertEqual(rich["inlined"], build.MODULES + build.STATE_MODULES)
        self.assertIn("| modules inlined, in order | `%s` |" % " ".join(build.MODULES + build.STATE_MODULES),
                      rich["manifest_text"])
        for field, n in (("annotation rows (:::annotate)", 8), ("annotation lists (:::annotate list)", 1),
                         ("annotation notes (:::note)", 4), ("passage marks", 3), ("annotation items in table cells", 5),
                         ("annotation ranges (:::range)", 2), ("item hosts (whole list items)", 2),
                         ("document record (:::annotate document)", 0)):
            self.assertIn("| %s | `%d` |" % (field, n), rich["manifest_text"])
        self.assertEqual(build.role_profiles(rich["counts"]), build.role_profiles(plain["counts"]))
        # A range, an item host or a document record alone inlines the modules.
        for name, src in (("range", in_04(ranged("review open: x", "W."))), ("host", in_04("- {{review open: x}} W.\n")),
                          ("record", mutate(GUIDED, ":::part 01\n", ":::annotate document\nbasis: b\n:::\n\n:::part 01\n"))):
            with self.subTest(name=name):
                self.assertEqual(self.render(src, name=name)["inlined"], build.MODULES + build.STATE_MODULES)

    def test_RS_cell_items_alone_inline_the_modules(self):
        r = self.render(with_table(table=":::table text status\n| Claim | Decision |\n|---|---|\n| a | {{review open: round 2}} |\n:::\n"))
        self.assertEqual(r["inlined"], build.MODULES + build.STATE_MODULES)

    def test_RS_output_passes_the_allowlist(self):
        h = self.render(annotated())["html"]
        build.check_final_html(h, 2)

    def test_RS_source_refusals(self):
        row_ = ":::annotate\n%s\n:::\n"
        cases = [
            (in_04(row_ % "evidence supported: x\nbasis: y"), at(2) + r": annotation items read in the order state, basis, "
                                                                r"evidence, review, check; evidence comes after basis"),
            (in_04(row_ % "status open"), at(1) + r": 'status open' is not an annotation item"),
            (in_04(row_ % "review maybe: x"), at(1) + r": review 'maybe' is outside the closed set"),
            (in_04(row_ % "evidence proven"), at(1) + r": evidence 'proven' is outside the closed set"),
            (in_04(row_ % "state done"), at(1) + r": state 'done' is outside the closed set"),
            (in_04(row_ % "review accepted"), at(1) + r": review accepted shows a decision and needs its record"),
            (in_04(row_ % "review declined"), at(1) + r": review declined shows a decision"),
            (in_04(row_ % "review correction-requested"), at(1) + r": review correction-requested names a request to change "
                                                                r"existing words and needs its record after ':' \(on what, who asked\)"),
            (in_04(row_ % "basis:"), at(1) + r": the basis item's text after ':' must contain visible text"),
            (in_04(row_ % "check owner: x"), at(1) + r": a check item is 'check: <value>'"),
            (in_04(row_ % "basis"), at(1) + r": a basis item is 'basis: <value>'"),
            (in_04(row_ % "basis: a {{b}}"), at(1) + r": an annotation item is plain text and holds no `\{\{`"),
            (in_04(":::annotate\n\n:::\n"), at() + r": :::annotate \(%s\) is empty" % at()),
            (in_04(":::annotate foo\nbasis: x\n:::\n"), at() + r": :::annotate takes no token but an optional 'list' or 'document'"),
            (in_04(":::annotate local=x\nbasis: x\n:::\n"), at() + r": :::annotate takes no local= hook"),
            (in_04(":::range foo\n"), at() + r": unknown token 'foo' on :::range"),
            (in_04(":::note Bad\n"), at() + r": invalid note name 'Bad'"),
            (in_04(":::note x local=y\n"), at() + r": :::note takes no local= hook"),
            (in_04(":::annotate\n```\nbasis: x\n:::\n"), at(1) + r": '```' is not an annotation item"),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_RS_placement_refusals(self):
        basis = ":::annotate\nbasis: x\n:::\n"
        cases = [
            (mutate(GUIDED, ":::part 04\nThe synthetic executive result.\n", ":::part 04\n" + basis + "The synthetic executive result.\n"),
             r"%s: :::annotate \(%s\) is the first child of :::part 04 \(%s\); a row or list without a review item follows "
             r"the heading or block it qualifies" % (at(-2), at(-2), at(-3))),
            (in_04(basis + "\n" + basis), r"%s: :::annotate \(%s\) follows :::annotate \(%s\)" % (at(4), at(4), at())),
            (in_04(":::annotate list\nbasis: x\n:::\n" + basis), r"%s: :::annotate \(%s\) follows :::annotate list \(%s\)"
                                                               % (at(3), at(3), at())),
            (in_04("W {{mark open n: x}}.\n\n" + NOTE + basis), r":::annotate \(line \d+\) follows :::note n \(%s\)" % at(2)),
            (mutate(GUIDED, "Synthetic locator line.\n", "Synthetic locator line.\n" + basis),
             r"line 1\d: :::annotate \(line 1\d\) is not allowed in part 01, which carries generated chrome"),
            (mutate(GUIDED, "Synthetic provenance block.\n", "Synthetic provenance block.\n" + basis),
             r":::annotate \(line \d+\) is not allowed in a provenance disclosure"),
            (mutate(GUIDED, ":::part 10\n", ":::part 10\nSeal text.\n\n" + basis), r"is not allowed in part 10"),
            (in_04(":::callout\nA point.\n\n" + basis + ":::\n"), r":::annotate is allowed inside :::part, :::question, :::finding, "
                                                                r":::disclose, :::note, :::range only, not :::callout"),
            (in_04(":::quote\nWords.\n\n" + basis + ":::\n"), r"not :::quote"),
            (in_04(":::framing thesis\nA frame.\n\n" + basis + ":::\n"), r"not :::framing"),
            (mutate(GUIDED, "Synthetic locator line.\n", ":::banner review-status\nStatus.\n\n" + basis + ":::\n"),
             r"sits inside :::banner review-status \(line \d+\); a banner holds Markdown only"),
            (in_04("Words {{mark open n: here}}.\n\n:::note n\n:::annotate list\nreview open\n:::\n:::\n"),
             r"a :::note holds an annotation row, not a list"),
            (in_04("Words {{mark open n: here}}.\n\n:::note n\nText first.\n\n:::annotate\nreview open\n:::\n:::\n"),
             r"a :::note holds one :::annotate row, as its first child"),
            (in_04("Words {{mark open n: here}}.\n\n:::note n\n:::annotate\nreview open\n:::\n" + NOTE + ":::\n"),
             r":::note is allowed inside :::part, :::question, :::finding, :::disclose only, not :::note n"),
            (in_04("Words {{mark open n: here}}.\n\n:::note n\nOnly text.\n:::\n"), r":::note n \(%s\) holds an :::annotate row first" % at(2)),
            (in_04("Words.\n\n:::note not-yet-testable\n:::annotate\nevidence unresolved: x\n:::\n:::\n"),
             r"a :::note not-yet-testable row carries an 'evidence not-yet-testable' item"),
            (in_04("Words {{mark open n: here}}.\n\n:::note n\n:::annotate\nreview open\n:::\n### A heading\n:::\n"),
             r":::note n \(%s\) holds a heading" % at(2)),
            (in_04("Words.\n\n" + NOTE), r"%s: :::note n \(%s\) follows no passage mark naming it in :::part 04" % (at(2), at(2))),
            (in_04("Words {{mark open n: here}}.\n\n### Next\n\nMore.\n\n" + NOTE),
             at() + r": the passage mark naming note 'n' has no note before the next heading"),
            (in_04("Words {{mark open n: here}}.\n\n" + NOTE + "\nAgain {{mark open n: there}}.\n"),
             r"the passage mark naming note 'n' has no :::note n after it"),
            (mutate(in_04("Words {{mark open n: here}}.\n\n" + NOTE), "The whole synthetic register.\n",
                    "The whole synthetic register {{mark open n: again}}.\n\n" + NOTE),
             r"line \d+: note name 'n' is already used at %s" % at(2)),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_RS_inline_refusals(self):
        note = "\n" + NOTE
        cases = [
            (in_04("Open {{mark open n: words\n"), at() + r": `\{\{` opens no annotation"),
            (in_04("A {{foo}} here.\n"), at() + r": `\{\{foo` is not an annotation"),
            (in_04("A \\{{mark open n: x}} here.\n"), at() + r": `\{\{` outside a code span that is not an annotation"),
            (in_04("[x](https://example.org/{{b}})\n"), at() + r": `\{\{` outside a code span that is not an annotation"),
            (in_04("A {{mark open n: `code`}}.\n" + note), at() + r": a passage mark's words are plain text and may hold a "
                                                                r"link written \[text\]\(url\): no code span, escape or other "
                                                                r"construct inside `\{\{mark \.\.\.\}\}`"),
            (in_04("A {{mark maybe n: words}}.\n" + note), at() + r": a passage mark names the judgment its words take, "
                                                                r"proposed, open, accepted, declined, not 'maybe'"),
            (in_04("A {{mark open not-yet-testable: words}}.\n"), r"the not-yet-testable evidence note takes no passage mark"),
            (in_04("A {{mark open n:  }}.\n" + note), r"a passage mark's words after ':' must contain visible text"),
            (in_04("A {{mark open n: [](https://example.org/)}}.\n" + note), r"a passage mark's words after ':' must contain "
                                                                           r"visible text"),
            (in_04("A {{mark open N: x}}.\n"), r"invalid note name 'N' in a passage mark"),
            (in_04("### Heading {{mark open n: x}}\n" + note), at() + r": a passage mark sits in a paragraph or list item, not inside <h3>"),
            (in_04("> Quoted {{mark open n: x}}\n" + note), r"not inside <blockquote>"),
            (in_04("[A {{mark open n: x}}](https://example.org/a)\n" + note), r"not inside <a>"),
            (in_04(":::quote\nQuoted {{mark open n: x}}.\n:::\n" + note), r"a passage mark sits in body text directly inside a part "
                                                                            r"02 to 09, .* not in :::quote \(%s\)" % at()),
            (in_04(":::callout\nA {{mark open n: x}}.\n:::\n" + note), r"not in :::callout"),
            (in_04(":::framing thesis\nA {{mark open n: x}}.\n:::\n" + note), r"not in :::framing"),
            (in_04("Words {{mark open n: x}}.\n\n:::note n\n:::annotate\nreview open\n:::\nIn the note {{mark open m: y}}.\n:::\n"),
             r"not in :::note n"),
            (mutate(GUIDED, "Synthetic locator line.\n", "Synthetic {{mark open n: locator}} line.\n"), r"not in :::part 01"),
            (in_04(":::table text text\n| A | B |\n|---|---|\n| {{mark open n: x}} | y |\n:::\n" + note), r"not in a :::table"),
            (in_04(":::table text text\n| A {{review open}} | B |\n|---|---|\n| x | y |\n:::\n"),
             at(1) + r": an annotation item sits in a body cell, never in a header"),
            (in_04(":::table key text\n| A | B |\n|---|---|\n| {{review open}} | y |\n:::\n"),
             at(3) + r": column 1 is a key column; annotation items sit in a text or status column"),
            (in_04(":::table text num\n| A | B |\n|---|---|\n| x | {{review open}} |\n:::\n"), r"column 2 is a num column"),
            (in_04(":::table text text\n| A | B |\n|---|---|\n| x | y {{review open}} |\n:::\n"),
             at(3) + r": a cell holding annotation items holds them only \(column 2\)"),
            (in_04(":::table text text\n| A | B |\n|---|---|\n| x | **{{review open}}** |\n:::\n"), r"holds them only"),
            (in_04(":::table text text\n| A | B |\n|---|---|\n| x | {{review open}} {{basis: y}} |\n:::\n"),
             at(3) + r": annotation items read in the order state, basis, evidence, review, check; review comes after basis"),
            (in_04(":::table text text \"Cap {{x}}\"\n| A | B |\n|---|---|\n| x | y |\n:::\n"),
             at() + r": a container token holds `\{\{`"),
            (mutate(GUIDED, "title: Synthetic guided review\n", "title: Synthetic {{x}} review\n"),
             r"meta line 3: meta key 'title' holds `\{\{`"),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_RS_link_inside_marked_words(self):
        h = self.render(in_04("Each print follows {{mark accepted n: the [paper plan](https://example.org/p \"Plan\") agreed}}.\n\n"
                              ":::note n\n:::annotate\nreview accepted: on “the paper plan agreed” · owner\n:::\n:::\n"))["html"]
        self.assertIn('Each print follows %s.' % passage("accepted", "n", 'the <a class="surface-text-link" '
                                                         'href="https://example.org/p" title="Plan">paper plan</a> agreed'), h)
        build.check_final_html(h, 2)
        cases = [
            (in_04("A {{mark open n: the [*plan*](https://example.org/p)}}.\n" + "\n" + NOTE),
             at() + r": a link inside marked words holds plain text: no code span, escape or emphasis in its text"),
            (in_04("A {{mark open n: the [`plan`](https://example.org/p)}}.\n" + "\n" + NOTE), r"a link inside marked words holds "
                                                                                              r"plain text"),
            (in_04("A {{mark open n: a \\* b}}.\n" + "\n" + NOTE), r"a passage mark's words are plain text and may hold a link"),
            (in_04(CELL % "{{review open: a [l](https://example.org/) b}}"), r"an annotation is plain text: no code span, escape "
                                                                            r"or link inside `\{\{\.\.\.\}\}`; only a passage "
                                                                            r"mark's words may hold a link"),
            (in_04("A {{mark open n: [x](other.html)}}.\n" + "\n" + NOTE), r"only https:// and http:// links are allowed"),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_RS_allowlist_places_the_composition(self):
        h = self.render(annotated())["html"]
        accepted = item("review", "accepted", "Accepted", "on “every bay” · owner, round 1")
        para = '<p class="doc-body">The whole synthetic register.</p>'
        host = '<li class="doc-annotation-range surface-labeled-range">'
        range_row = row(item("review", "proposed", "Proposed", "rev 3 · editor, round 2 · this paragraph"),
                        key_item("Basis", "editor draft"))
        bad = [
            (h.replace('data-review="accepted">Accepted', 'data-review="maybe">Accepted', 1), r"data-review='maybe' is outside the review vocabulary"),
            (h.replace('data-review="accepted">Accepted', 'data-review="declined">Accepted', 1),
             r"annotation words 'Accepted' are not their role's or key's words \(Declined\)"),
            (h.replace('<span class="%s" data-review="accepted">' % build.REVIEW_MARK, '<span class="%s" data-review="accepted" '
                       'data-state="earned">' % build.REVIEW_MARK, 1), r"a mark carries exactly one of data-review, data-evidence, data-state"),
            (h.replace('<span class="%s" data-review="accepted">' % build.REVIEW_MARK, '<span class="doc-mark doc-label" '
                       'data-review="accepted">', 1), r"a review mark is the bordered label"),
            (h.replace('<span class="doc-mark doc-label" data-evidence', '<span class="%s" data-evidence' % build.REVIEW_MARK, 1),
             r"a review mark is the bordered label, class .*; an evidence or state mark is doc-mark doc-label"),
            (h.replace(' aria-describedby="uo-note-props"', "", 1), r"a passage mark names its note"),
            (h.replace(' aria-describedby="uo-note-props"', ' aria-describedby="uo-note-other"', 1),
             r"each annotation note is named by a passage mark and each passage mark names a note"),
            (h.replace('data-review="proposed" aria-describedby="uo-note-props"', 'data-review="none" aria-describedby="uo-note-props"', 1),
             r"a passage mark carries data-review, the judgment its words take"),
            (h.replace('<mark class="doc-passage-mark surface-scope-underline"', '<mark class="doc-passage-mark"', 1),
             r"class 'doc-passage-mark' not allowed on <mark>"),
            (h.replace('<div class="doc-annotations">', '<div class="doc-annotations" data-review="open">', 1),
             r"a facet attribute sits on a mark, a passage mark or the not-yet-testable note only"),
            (h.replace(para, para + accepted, 1), r"an annotation item sits only in an annotation row"),
            (h.replace(para, '<p class="doc-body">The whole synthetic register <span class="%s" data-review="open">Open '
                       'question</span></p>' % build.REVIEW_MARK, 1),
             r"a mark or its metadata sits only in an annotation item or an annotation list's value"),
            (h.replace('<dt class="doc-label">Basis</dt>', '<dt class="doc-label">Origin</dt>', 1),
             r"annotation words 'Origin' are not their role's or key's words"),
            (h.replace(para, '<blockquote class="doc-quote"><p>Quoted <mark class="doc-passage-mark surface-scope-underline" '
                       'data-review="open" aria-describedby="uo-note-month">x</mark></p></blockquote>', 1),
             r"a passage mark sits in document body text"),
            (h.replace('id="uo-note-month"', 'id="uo-note-month" data-evidence="unresolved"', 1),
             r"a facet attribute sits on a mark, a passage mark or the not-yet-testable note only"),
            # ranges
            (h.replace(RANGE_OPEN + range_row + "\n", RANGE_OPEN, 1), r"an annotation range opens with its annotation row"),
            (h.replace(range_row, row(key_item("Basis", "editor draft"), item("review", "proposed", "Proposed", "x")), 1),
             r"an annotation range opens with its row, which names its one review judgment first"),
            (h.replace(range_row, row(item("review", "proposed", "Proposed", "x"), item("review", "open", "Open question", "y")), 1),
             r"an annotation range opens with its row, which names its one review judgment first"),
            (h.replace('<p class="doc-body">The frame keeps', '<p class="doc-body"><span class="doc-annotations">x</span>The frame '
                       'keeps', 1), r"a cell's annotation row sits directly in its table cell"),
            (h.replace(' in each bay, and', ' in each bay <span class="doc-annotations"><span class="doc-annotation-item">%s'
                       '</span></span>, and' % item("review", "open", "Open question")[len('<span class="doc-annotation-item">'):-7], 1),
             r"an annotation range carries one judgment"),
            (h.replace(para, RANGE_OPEN + row(item("review", "open", "Open question")) + '\n<div class="doc-prose">\n' + para
                       + "\n</div>\n</div>", 1).replace(RANGE_OPEN + range_row, RANGE_OPEN + range_row + "\n" + RANGE_OPEN
                                                      + row(item("review", "open", "Open question")) + '\n<div class="doc-prose">'
                                                        '\n<p class="doc-body">x</p>\n</div>\n</div>', 1),
             r"annotation ranges never nest"),
            (h.replace('<div class="doc-prose">\n<p class="doc-body">The frame keeps',
                       '<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-zz">%s</div>\n<div class="doc-prose">\n'
                       '<p class="doc-body">The frame keeps' % row(item("review", "open", "Open question")), 1),
             r"an annotation note never sits inside an annotation range"),
            (h.replace(RANGE_OPEN + range_row + "\n", RANGE_OPEN + range_row + "\n" + '<p class="doc-body">bare</p>\n', 1),
             r"an annotation range holds its row, then the blocks it covers"),
            (h.replace(RANGE_OPEN, '<div class="doc-prose">' + RANGE_OPEN, 1).replace("stays.</p>\n</div>\n</div>",
                                                                                      "stays.</p>\n</div>\n</div>\n</div>", 1),
             r"an annotation range sits directly in a section"),
            # prompts
            (h.replace("\n" + RANGE_OPEN, '\n<div class="doc-prose"><p class="doc-body">between</p></div>\n' + RANGE_OPEN, 1),
             r"a review row outside a range is an explicit-target prompt, immediately before the range"),
            (h.replace(para, para + "\n</div>\n" + row(item("review", "open", "Open question", "x")) + '\n<div class="doc-prose">', 1),
             r"a review row outside a range is an explicit-target prompt"),
            # item hosts
            (h.replace(host + '<div class="doc-annotations">', host + '<p class="doc-body">w</p><div class="doc-annotations">', 1),
             r"an annotation range opens with its annotation row"),
            (h.replace('<li class="doc-body">Proofs reach the studio', '<li class="doc-body">Proofs <ul>' + host
                       + row(item("review", "open", "Open question", "x")) + '<p class="doc-body">n</p></li></ul> reach the studio', 1),
             r"an item host is an item of a top-level list in the flow"),
            (h.replace("</div><p class=\"doc-body\">Glossy stock is used.</p>", "</div>Glossy stock is used.", 1),
             r"annotation text sits in a mark, a key or a metadata span, not directly in <li>"),
            # notes in list items, links in marks
            (h.replace('<p class="doc-body">Glossy stock is used.</p></li>',
                       '<p class="doc-body">Glossy stock is used.</p><div class="doc-hierarchy doc-group doc-annotation-note" '
                       'id="uo-note-zz">%s</div></li>' % row(item("review", "open", "Open question")), 1),
             r"an annotation note sits directly in a section, or in a plain list item after its text"),
            (h.replace('href="https://example.org/bay">bay</a>', 'href="https://example.org/bay"><em>bay</em></a>', 1),
             r"a link inside marked words holds plain text only, not <em>"),
            (h.replace('aria-describedby="uo-note-bays">every ', 'aria-describedby="uo-note-bays"><em>every</em> ', 1),
             r"a passage mark holds its words as text, and a link inside them, only"),
            # the list's Item line, the document record
            (h.replace('<dt class="doc-label">Item</dt>\n<dd><span class="doc-meta">the method component, version 0.3</span></dd>\n', "", 1),
             r"an annotation list with a Review line names the item it judges first, in an Item line"),
            (h.replace('<dd><span class="doc-meta">the method component, version 0.3</span></dd>',
                       '<dd><span class="doc-meta">the method component</span>%s</dd>' % item("review", "open", "Open question")[
                           len('<span class="doc-annotation-item">'):-7], 1),
             r"an annotation list's Item line holds the name of the item it judges"),
            (h.replace('<h1 class="doc-title">', row(key_item("Basis", "x")) + '\n<h1 class="doc-title">', 1),
             r"the document's review record sits once, directly under the masthead title"),
        ]
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                self.assertNotEqual(doc, h)
                with self.assertRaises(build.BuildError) as cm:
                    build.check_final_html(doc, 2)
                self.assertRegex(str(cm.exception), pattern)


class ReviewAnnotationPlacementAndRecords(RenderCase):
    """Where no annotation sits (the chrome parts and the provenance disclosure), the note's record of the judgment its
    marks show, and the composition rules of README, "Review annotations", under design-system-ASK #185 (705a195)."""

    def test_no_annotation_in_chrome_parts_or_provenance(self):
        accepted = "{{review accepted: y · owner · this copy}}"
        basis, check = "{{basis: owner-stated}}", "{{check: re-summed}}"
        cases = [
            (mutate(GUIDED, "Synthetic locator line.\n", "Synthetic locator line.\n\n" + CELL % accepted), accepted, r":::part 01"),
            (with_part_01(part=":::part 01\n:::banner review-status\nStatus.\n:::\n\n" + CELL % accepted + ":::\n\n"), accepted,
             r":::part 01"),
            (mutate(GUIDED, ":::part 10\n", ":::part 10\nSeal text.\n\n" + CELL % basis), basis, r":::part 10"),
            (mutate(GUIDED, "Synthetic provenance block.\n", "Synthetic provenance block.\n\n" + CELL % basis), basis,
             r":::disclose provenance"),
            (mutate(GUIDED, "Synthetic provenance block.\n", "Synthetic provenance block.\n\n" + CELL % check), check,
             r":::disclose provenance"),
        ]
        for src, construct, where in cases:
            with self.subTest(where=where, construct=construct):
                self.reset_tmp()
                self.fails(src, r"line %d: no annotation sits in part 01 or 10 or in a provenance disclosure; this :::table "
                                r"is in %s \(line \d+\)" % (row_of(src, construct), where))
        self.reset_tmp()
        r = self.render(in_04(CELL % basis))                          # the positive control: part 04
        self.assertIn(key_item("Basis", "owner-stated"), r["html"])

    def test_allowlist_refuses_annotations_in_chrome_parts(self):
        h = self.render(GUIDED, name="a")["html"]
        row_ = '<div class="doc-annotations">%s</div>' % key_item("Basis", "x")
        doc = h.replace('<p class="doc-body">Synthetic locator line.</p>\n</div>', '<p class="doc-body">Synthetic locator line.</p>\n'
                        '</div>\n' + row_, 1)
        self.assertNotEqual(doc, h)
        with self.assertRaises(build.BuildError) as cm:
            build.check_final_html(doc, 2)
        self.assertRegex(str(cm.exception), r"no annotation sits in part 01 or 10 or in a provenance disclosure "
                                            r"\(<div class='doc-annotations'>\)")
        h = self.render(mutate(GUIDED, ":::part 10\n", ":::part 10\nSeal text.\n\n" + CELL % "plain"), name="b")["html"]
        doc = h.replace("</span>plain</td>", '</span><span class="doc-annotations">%s</span></td>' % key_item("Basis", "x"), 1)
        self.assertNotEqual(doc, h)
        with self.assertRaises(build.BuildError) as cm:
            build.check_final_html(doc, 2)
        self.assertRegex(str(cm.exception), r"no annotation sits in part 01 or 10 or in a provenance disclosure "
                                            r"\(<span class='doc-annotations'>\)")
        doc = h.replace('<p class="doc-body">Seal text.</p>', '<p class="doc-body">Seal text.</p>\n</div>\n' + RANGE_OPEN
                        + row(item("review", "open", "Open question")) + '\n<div class="doc-prose">\n<p class="doc-body">x</p>', 1)
        with self.assertRaises(build.BuildError) as cm:
            build.check_final_html(doc, 2)
        self.assertRegex(str(cm.exception), r"no annotation sits in part 01 or 10 or in a provenance disclosure "
                                            r"\(<div class='doc-annotation-range doc-group surface-labeled-range'>\)")

    def note_doc(self, mark_role, note_lines, words="here"):
        return in_04("Words {{mark %s n: %s}}.\n\n:::note n\n:::annotate\n%s\n:::\n:::\n" % (mark_role, words, note_lines))

    def test_a_note_records_the_judgment_its_marks_show(self):
        def msg(role, words):
            return r"%s: a passage mark showing %s names note 'n', whose row records no %s item" % (at(), role, words)
        proposed = msg("proposed", "review proposed or review correction-requested")
        cases = [
            (self.note_doc("proposed", "review accepted: v2 · owner · this copy"), proposed),
            (self.note_doc("proposed", "basis: owner-stated\ncheck: re-summed"), proposed),
            (self.note_doc("open", "review proposed: an answer"), msg("open", "review open")),
            (self.note_doc("accepted", "review declined: v2 · owner"), msg("accepted", "review accepted")),
            (self.note_doc("declined", "review open: who decides"), msg("declined", "review declined")),
            (in_04("A {{mark proposed n: one}} and {{mark open n: two}}.\n\n:::note n\n:::annotate\nreview proposed: x\n:::\n:::\n"),
             msg("open", "review open")),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern, src=src[-120:]):
                self.reset_tmp()
                self.fails(src, pattern)
        good = [
            self.note_doc("proposed", "review correction-requested: on “here” · owner, round 2"),
            self.note_doc("proposed", "review proposed: a narrower phrase · editor\nreview correction-requested: on “here” · "
                                      "owner"),
            self.note_doc("accepted", "review accepted: on “here” · owner, round 1"),
            self.note_doc("declined", "review declined: on “here” · owner, round 1"),
            in_04("A {{mark proposed n: one}} and {{mark open n: two}}.\n\n:::note n\n:::annotate\nreview proposed: x\n"
                  "review open: y\n:::\n:::\n"),
        ]
        for i, src in enumerate(good):
            with self.subTest(good=i):
                self.reset_tmp()
                self.render(src)

    def test_a_note_row_holds_no_review_item_its_marks_do_not_show(self):
        # A review item in a note's row that no mark naming the note shows would judge the blocks before the note from
        # a row placed after them: the trailing row a whole-block judgment never takes. A named note after a paragraph,
        # and the not-yet-testable evidence note, which no mark names, after a paragraph and after a synthesis. (A
        # named note follows a synthesis only where it follows the range around it, for a mark in that range's earlier
        # block: no mark sits in a panel.)
        def other(line, word, role):
            return (r"line %d: the row of note 'n' holds review %s, but no passage mark naming the note shows %s: a "
                    r"note's review items record only what its marks show" % (line, word, role))
        nyt = (":::note not-yet-testable\n:::annotate\nevidence not-yet-testable: no readings yet\n%s\n:::\n:::\n")
        synthesis = mutate(GUIDED, "The synthetic executive result.\n",
                           "The synthetic executive result.\n\n:::synthesis\nWhat the part comes to.\n:::\n\n%s")
        cases = [
            (self.note_doc("proposed", "review correction-requested: on “here” · owner\n"
                                       "review accepted: this whole paragraph · owner"),
             other(row_of(in_04(""), "The synthetic executive result.") + 7, "accepted", "accepted")),
            (self.note_doc("open", "review open: who decides\nreview declined: phase 1 · owner · phase 1 only"),
             other(row_of(in_04(""), "The synthetic executive result.") + 7, "declined", "declined")),
            (self.note_doc("open", "review open: who decides\nreview none: no production decision"),
             r"line %d: the row of note 'n' holds review none: No decision recorded marks no words"
             % (row_of(in_04(""), "The synthetic executive result.") + 7)),
        ]
        for text, after in (("Words.\n\n" + nyt, "a paragraph"), (nyt, "a synthesis")):
            src = in_04(text % "review declined: owner · this paragraph") if after == "a paragraph" else (
                synthesis % (nyt % "review accepted: synthesis v1 · owner · this document"))
            cases.append((src, r"line %d: a :::note not-yet-testable row carries no review item: it is an evidence note, "
                               r"and no passage mark names it" % (row_of(src, "evidence not-yet-testable:") + 1)))
        for src, pattern in cases:
            with self.subTest(pattern=pattern[:60], src=src[-100:]):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_allowlist_mirrors_the_note_roles(self):
        h = self.render(annotated())["html"]
        doc = h.replace('data-review="proposed">Correction requested</span>', 'data-review="accepted">Accepted</span>', 1)
        self.assertNotEqual(doc, h)
        with self.assertRaises(build.BuildError) as cm:
            build.check_final_html(doc, 2)
        self.assertRegex(str(cm.exception), r"a passage mark showing proposed names uo-note-props, whose first row records "
                                            r"no review proposed mark")

    def test_spectral_and_review_proposed_take_the_list(self):
        both = "state proposed: a candidate stage\nreview proposed: its adoption"
        cases = [
            (in_04(":::annotate\nreview proposed: its adoption\nstate proposed: a candidate stage\n:::\n\n" + ranged("review open: q", "W.")),
             r"%s: state proposed and review proposed on one item read as one word twice; an :::annotate list carries them, "
             r"one key each" % at(1)),
            (self.note_doc("proposed", both), r"%s: a note's row cannot carry both state proposed and review proposed; keep "
                                              r"the state item in the block's own row or list" % at(5)),
            (in_04(CELL % "{{state proposed: s}} {{review proposed: r}}"),
             r"%s: state proposed and review proposed in one cell read as one word twice; carry them in an :::annotate "
             r"list, one key each \(column 2\)" % at(3)),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)
        self.reset_tmp()
        h = self.render(in_04(":::annotate list\nitem: a candidate stage\n%s\n:::\n" % both))["html"]
        self.assertIn('<dt class="doc-label">State</dt>\n<dd><span class="doc-mark doc-label" data-state="proposed">Proposed</span>', h)
        self.assertIn('<dt class="doc-label">Review</dt>\n<dd><span class="%s" data-review="proposed">Proposed</span>'
                      % build.REVIEW_MARK, h)
        for src in (self.note_doc("proposed", "state proposed: s\nreview correction-requested: on “x” · owner"),
                    in_04(CELL % "{{state proposed: s}} {{review correction-requested: on x · owner}}")):
            with self.subTest(src=src[-80:]):
                self.reset_tmp()
                self.assertIn('data-review="proposed">Correction requested</span>', self.render(src)["html"])

    def test_a_status_cell_decision_record_wraps(self):
        md = css_rules(build.MD_CSS)
        rule = ':where(.uo-md) :where(td[data-uo-cell="status"]) > :where(.doc-annotations)'
        self.assertEqual(rules_with(md, rule), [{"white-space": "normal"}])
        nowrap = ':where(.uo-md) :where(td[data-uo-cell="key"], td[data-uo-cell="num"], td[data-uo-cell="status"])'
        order = [sels for m, sels, d in md if m is None]
        self.assertLess(order.index((nowrap,)), order.index((rule,)))
        self.assertTrue(Presentation.zero_specificity(rule))

    def test_a_heading_in_a_child_container_separates_a_mark_from_its_note(self):
        note = NOTE + "\n"
        mark = "Words {{mark open n: here}}.\n\n"
        finding = mutate(GUIDED, ":::part 06\n", ":::part 06\n" + mark + ":::finding\n### Inside\n\nA finding.\n:::\n\n" + note)
        deep = mutate(GUIDED, ":::part 06\n", ":::part 06\n" + mark + ":::finding\nA finding.\n\n:::disclose evidence \"E\"\n"
                      "#### Deep\n\nListing.\n:::\n:::\n\n" + note)
        question = mutate(GUIDED, "The bounded question set.\n", "The bounded question set.\n\n" + mark
                          + ":::question\n### A heading\n\nA prompt.\n:::\n\n" + note)
        for src in (finding, deep, question):
            with self.subTest(src=row_of(src, "{{mark")):
                self.reset_tmp()
                self.fails(src, r"line %d: the passage mark naming note 'n' has no note before the next heading" % row_of(src, "{{mark"))
        # Without a heading the container still separates block and note; before the container, the note builds.
        self.reset_tmp()
        self.fails(finding.replace("### Inside\n\n", ""), r"line %d: the passage mark naming note 'n' is followed by another "
                                                         r"block or container before its note" % row_of(finding, "{{mark"))
        self.reset_tmp()
        self.render(mutate(GUIDED, ":::part 06\n", ":::part 06\n" + mark + note + ":::finding\n### Inside\n\nA finding.\n:::\n\n"))

    def test_construct_text_is_plain_whichever_checks_reach_it(self):
        probed = []
        real = build.Text.renders_text

        def spy(text):
            if any("{{" in line for _, line in text.lines):
                probed.append(True)
            return real(text)
        with mock.patch.object(build.Text, "renders_text", spy):
            a = self.render(self.note_doc("open", "review open: x", words="a <b> c"), name="a")["html"]
        self.assertTrue(probed)                               # the flow check read the mark's paragraph
        probed.clear()
        with mock.patch.object(build.Text, "renders_text", spy):
            b = self.render(in_04(CELL % "{{review open: a <b> c}}"), name="b")["html"]
        self.assertFalse(probed)                              # no check reads a table's text
        self.assertIn('aria-describedby="uo-note-n">a &lt;b&gt; c</mark>', a)
        self.assertIn('<span class="doc-meta">a &lt;b&gt; c</span>', b)
        c = self.render(self.note_doc("open", "review open: x", words="x<y"), name="c")["html"]
        self.assertIn('aria-describedby="uo-note-n">x&lt;y</mark>', c)
        probe = build.Text()
        probe.lines = [(1, "Words {{mark open n: a <b> c}}.")]
        self.assertTrue(probe.renders_text())

    def test_seal_line_and_manifest_name_the_sealed_parts(self):
        short = build.verify_dependencies()["commit"][:7]
        heading = "## design-system-ASK tokens, document register and semantic-state modules"
        plain = self.render(GUIDED, name="plain")
        self.assertIn('design-system-ASK tokens and document register <code class="doc-code">%s</code>' % short, plain["html"])
        self.assertNotIn("semantic-state modules <code", plain["html"])
        rich = self.render(annotated(), name="rich")
        self.assertIn('design-system-ASK tokens, document register and semantic-state modules <code class="doc-code">%s</code>'
                      % short, rich["html"])
        for r in (plain, rich):
            self.assertIn(heading, r["manifest_text"])
            self.assertNotIn("\x00", r["html"])

    def test_a_list_answers_each_question_once(self):
        self.fails(in_04(":::annotate list\nitem: x\nreview accepted: v1 · owner · trial\nreview none: no production decision\n:::\n"),
                   r"%s: a list answers each question once; a second judgment at another scope is its own :::annotate "
                   r"list, naming its item in its `item:` line" % at(3))
        for axis, first, second in (("basis", "basis: owner-stated", "basis: analyst"),
                                    ("evidence", "evidence supported: owner", "evidence unresolved: analyst"),
                                    ("state", "state earned: v1", "state held: v2"),
                                    ("check", "check: owner", "check: analyst")):
            with self.subTest(axis=axis):
                self.reset_tmp()
                self.fails(in_04("Words.\n\n:::annotate list\nitem: x\n%s\n%s\n:::\n" % (first, second)),
                           r"%s: a list answers each question once, and this is a second %s record; two records of one "
                           r"axis at different scopes take one row, which may repeat that axis" % (at(5), axis))
                # The form the message names builds: one row after the block it qualifies, repeating that axis.
                self.reset_tmp()
                r = self.render(in_04("Words.\n\n:::annotate\n%s\n%s\n:::\n" % (first, second)))
                self.assertEqual((r["counts"]["annotation_rows"], r["counts"]["annotation_lists"]), (1, 0))
                self.assertEqual(r["html"].count('<span class="doc-annotation-item">'), 2)

    def test_only_notes_and_rows_without_a_review_item_sit_between_a_block_and_its_note(self):
        cases = [
            in_04("Words {{mark open n: here}}.\n\nAnother block.\n\n" + NOTE),
            in_04("Words {{mark open n: here}}.\n\n" + TABLE + "\n" + NOTE),
            in_04("Words {{mark open n: here}}.\n\n:::callout\nA point.\n:::\n\n" + NOTE),
            in_04("Words {{mark open n: here}}.\n\n:::annotate list\nitem: x\nreview accepted: v1 · owner\n:::\n\n" + NOTE),
        ]
        for src in cases:
            with self.subTest(src=src[-60:]):
                self.reset_tmp()
                self.fails(src, r"%s: the passage mark naming note 'n' is followed by another block or container before its "
                                r"note; a note follows the block or range holding its mark, with only other notes and rows "
                                r"or lists without a review item between" % at())
        self.reset_tmp()
        self.render(in_04("Words {{mark open n: here}} and {{mark open m: there}}.\n\n:::annotate\nbasis: x\n:::\n\n" + NOTE
                          + "\n:::note m\n:::annotate\nreview open\n:::\n:::\n\n:::note not-yet-testable\n:::annotate\n"
                          "evidence not-yet-testable: later\n:::\n:::\n\nA later block.\n"))

    def test_construct_source_refusals(self):
        cases = [
            (in_04("See <https://example.org/{{mark open n: x}}>\n"), r"%s: an annotation never sits inside an autolink" % at()),
            (in_04("Words {{mark open n: here}}.\n\n:::note n\n​\n\n:::annotate\nreview open\n:::\n:::\n"),
             r":::note n \(%s\) holds an :::annotate row first" % at(2)),
            (in_04("A `{{foo}}` span,\nthen {{foo}} here.\n"), r"%s: `\{\{foo` is not an annotation" % at(1)),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_allowlist_keeps_words_plain_and_marks_full(self):
        h = self.render(annotated())["html"]
        bad = [
            (h.replace('data-review="accepted">Accepted</span>', 'data-review="accepted"><em>Accepted</em></span>', 1),
             r"an annotation's words are text only, not <em>"),
            (h.replace('<span class="doc-meta">on “every bay” · owner, round 1</span>',
                       '<span class="doc-meta"><a class="surface-text-link" href="https://example.org/">v3</a></span>', 1),
             r"an annotation's words are text only, not <a>"),
            (h.replace('aria-describedby="uo-note-props">two props or fewer</mark>', 'aria-describedby="uo-note-props"></mark>', 1),
             r"a passage mark shows the words it marks; it is never empty"),
        ]
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                self.assertNotEqual(doc, h)
                with self.assertRaises(build.BuildError) as cm:
                    build.check_final_html(doc, 2)
                self.assertRegex(str(cm.exception), pattern)


class ReviewAnnotationRecordsAndEscapes(RenderCase):
    """A correction request's record, the sealed modules' comments, error lines and escapes inside a construct, and the
    allowlist's hold of each note to its row, under design-system-ASK #185 (705a195)."""

    def test_correction_requested_is_a_request_not_a_decision(self):
        msg = self.fails(in_04(":::annotate\nreview correction-requested\n:::\n"),
                         r"%s: review correction-requested names a request to change existing words and needs its record "
                         r"after ':' \(on what, who asked\)$" % at(1))
        self.assertNotIn("decision", msg)
        self.reset_tmp()
        self.fails(in_04(":::annotate\nreview accepted\n:::\n"),
                   r"%s: review accepted shows a decision and needs its record after ':' \(what, who, scope\)$" % at(1))

    def test_sealed_comments_name_each_modules_manifest(self):
        plain = self.render(GUIDED, name="plain")["html"].split("</head>")[0]
        rich = self.render(annotated(), name="rich")["html"].split("</head>")[0]
        for rel in build.MODULES:
            for head in (plain, rich):
                self.assertIn("SEALED design-system-ASK %s (upstream 705a195, verbatim; bytes verified against the register "
                              "manifest) === */" % rel, head)
        for rel in build.STATE_MODULES:
            self.assertIn("SEALED design-system-ASK %s (upstream 705a195, verbatim; bytes verified against the _dsa-surface "
                          "manifest) === */" % rel, rich)
            self.assertNotIn(rel, plain)

    def test_error_lines_skip_code_spans_and_count_identical_constructs(self):
        note = "\n" + NOTE
        cases = [
            # a code-span literal before a real construct in a heading: the heading's line
            (in_04("Write `{{mark open n: x}}` here.\n\n### Head {{mark open n: x}}\n" + note), at(2),
             r"a passage mark sits in a paragraph or list item, not inside <h3>"),
            # a code-span literal before a real mark whose note is missing: the mark's line
            (in_04("`{{mark open n: x}}`\n\nWords {{mark open n: x}}.\n"), at(2),
             r"the passage mark naming note 'n' has no :::note n after it"),
            # an identical valid construct before a bad one, with identical surrounding text: the bad one's line
            (in_04("{{mark open n: x}}\n\n### {{mark open n: x}}\n" + note), at(2),
             r"a passage mark sits in a paragraph or list item, not inside <h3>"),
            # an identical construct inside a code span on the same line as the bad one
            (in_04("A `{{foo}}` then {{foo}} here.\n"), at(), r"`\{\{foo` is not an annotation"),
        ]
        for src, line, pattern in cases:
            with self.subTest(line=line, pattern=pattern):
                self.reset_tmp()
                self.fails(src, r"^%s: %s" % (line, pattern))

    def test_escapes_and_code_fail_inside_a_construct_and_show_in_a_row(self):
        for text in ("a \\* b", "a `c` b"):
            for src in (in_04(CELL % ("{{review open: %s}}" % text)), in_04("Words {{mark open n: %s}}.\n\n" % text + NOTE),
                        in_04("- {{review open: %s}} Words.\n" % text)):
                with self.subTest(text=text, src=src[-40:]):
                    self.reset_tmp()
                    self.fails(src, r"(an annotation is plain text: no code span, escape or link inside|a passage mark's words "
                                    r"are plain text and may hold a link)")
        self.reset_tmp()
        h = self.render(in_04(":::annotate\nbasis: a \\* b `c` [l](https://example.org/)\n:::\n"))["html"]
        self.assertIn(key_item("Basis", "a \\* b `c` [l](https://example.org/)"), h)

    def test_allowlist_holds_each_note_to_its_row(self):
        h = self.render(annotated())["html"]
        nyt_mark = '<span class="doc-mark doc-label" data-evidence="not-yet-testable">Not yet testable</span>'
        nyt_row = row(item("evidence", "not-yet-testable", "Not yet testable", "no readings until next season")) + "\n"
        named_open = '<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-props">\n'
        self.assertEqual(h.count(nyt_mark), 1)
        self.assertEqual(h.count(nyt_row), 1)
        bad = [
            (h.replace(nyt_mark, '<span class="doc-mark doc-label" data-evidence="supported">Supported</span>', 1),
             r"a not-yet-testable note's row carries a Not yet testable evidence mark"),
            (h.replace(nyt_row, row(key_item("Check", "x")) + "\n", 1),
             r"a not-yet-testable note's row carries a Not yet testable evidence mark"),
            (h.replace(nyt_row, "", 1), r"an annotation note holds its row first, not <p>"),
            (h.replace(named_open, named_open + '<p class="doc-body">x</p>\n', 1), r"an annotation note holds its row first, not <p>"),
        ]
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                self.assertNotEqual(doc, h)
                with self.assertRaises(build.BuildError) as cm:
                    build.check_final_html(doc, 2)
                self.assertRegex(str(cm.exception), pattern)


class ReviewAnnotationSynthesisAndDisclosures(RenderCase):
    """A synthesis, or the range around it, is its part's last substantive content, and an authored disclosure takes
    annotations (README, "Disclosures and the synthesis"; test_RS_annotations_inside_an_authored_disclosure)."""

    SYNTHESIS = ":::synthesis\nThe finding is bounded to this survey.\n:::\n"
    PANEL = ('<div data-uo-role="synthesis" class="%s">\n<p class="surface-emphasis-chip surface-emphasis--magenta">compression'
             '</p>\n<p class="doc-body">The finding is bounded to this survey.</p>\n</div>' % build.FLAT_PANEL)

    def accepted(self, inner=None):
        return (":::range\n:::annotate\nreview accepted: synthesis v1 · reviewer · this document only\n"
                "basis: analyst synthesis\n:::\n" + (inner if inner is not None else self.SYNTHESIS) + ":::\n")

    def test_an_accepted_synthesis_takes_a_range(self):
        # The synthesis stays its part's last content and keeps its panel; the range around it carries its judgment,
        # and its origin survives the acceptance (review-semantics.md, "Origin survives adoption").
        h = self.render(in_04(self.accepted()))["html"]
        self.assertIn(RANGE_OPEN + row(item("review", "accepted", "Accepted", "synthesis v1 · reviewer · this document only"),
                                       key_item("Basis", "analyst synthesis")) + "\n" + self.PANEL + "\n</div>\n</section>", h)
        # A row or list without a review item, then a not-yet-testable note, may follow it outside the panel.
        self.reset_tmp()
        h = self.render(in_04(self.SYNTHESIS + "\n:::annotate list\nevidence partially-supported: one survey\n:::\n\n"
                              ":::note not-yet-testable\n:::annotate\nevidence not-yet-testable: the second season\n:::\n:::\n"))["html"]
        self.assertIn(self.PANEL + '\n<dl class="doc-annotation-list">', h)
        self.assertIn('<div class="doc-group doc-annotation-note" data-evidence="not-yet-testable">', h)
        # A range over a panel belongs to its part, and the prompt before it moves with it out of a ### section.
        self.reset_tmp()
        h = self.render(in_04("### A section\n\nIts text.\n\n:::annotate\nreview open: on the synthesis below · owner\n:::\n\n"
                              + self.accepted()))["html"]
        self.assertIn('<p class="doc-body">Its text.</p>\n</div>\n</div>\n' + row(item("review", "open", "Open question",
                                                                                     "on the synthesis below · owner"))
                      + "\n" + RANGE_OPEN, h)

    def test_prose_after_the_synthesis_fails(self):
        for holder in (self.SYNTHESIS, self.accepted()):
            cases = [
                ("A line after.\n", "A line after."),
                ("### A later section\n", "### A later section"),
                (":::callout\nA later callout.\n:::\n", ":::callout"),
                (TABLE, ":::table dense"),
                (":::quote\nA later quotation.\n:::\n", ":::quote"),
                (ranged("review open: x", "A later range."), ":::range"),
            ]
            for tail, first in cases:
                with self.subTest(holder=holder[:9], tail=first):
                    self.reset_tmp()
                    src = in_04(holder + "\n" + tail)
                    if holder != self.SYNTHESIS and first == ":::range":
                        first_line = [i + 1 for i, ln in enumerate(src.splitlines()) if ln == ":::range"][1]
                    else:
                        first_line = row_of(src, first) if first != ":::range" else row_of(src, ":::range")
                    self.fails(src, r"line %d: a :::synthesis closes its part; only notes, and rows or lists without a review "
                                    r"item, may follow it in part 04, and line %d does not" % (row_of(src, ":::synthesis"), first_line))
        # A review row or a review list after the synthesis fails: a judgment on it is a range around it.
        for tail in (":::annotate\nreview accepted: v1 · reviewer\n:::\n", ":::annotate list\nitem: the synthesis\n"
                                                                                  "review accepted: v1 · reviewer\n:::\n"):
            with self.subTest(tail=tail[:16]):
                self.reset_tmp()
                src = in_04(self.SYNTHESIS + "\n" + tail)
                self.fails(src, r"line %d: a :::synthesis closes its part, and a review judgment on it opens a :::range around "
                                r"it; the review row or list at line %d follows it" % (row_of(src, ":::synthesis"), row_of(src, ":::annotate")))
        # Inside its range, the synthesis is the last block.
        self.reset_tmp()
        src = in_04(self.accepted(self.SYNTHESIS + "\nAfter it.\n"))
        self.fails(src, r"line %d: a :::synthesis closes its part, and closes the :::range that holds it; line %d follows it"
                   % (row_of(src, ":::synthesis"), row_of(src, "After it.")))

    def test_panels_in_a_range_keep_their_rules(self):
        cases = [
            (mutate(GUIDED, "The non-central question's detail.\n:::\n:::\n",
                    "The non-central question's detail.\n:::\n\n" + self.accepted() + ":::\n"),
             r"a :::synthesis sits in a :::range only where that range sits directly in a part, not in :::question"),
            (in_04(self.accepted() + "\n" + self.accepted()), r"part 04 carries at most one :::synthesis"),
            (in_04("### A section\n\nText.\n\n" + ranged("review proposed: x", ":::framing thesis\nA frame.\n:::")),
             r"a :::framing opens its part, before the part's first ### or #### section"),
            (mutate(GUIDED, ":::part 10\n", ":::part 10\n" + ranged("review open: x", ":::framing thesis\nA frame.\n:::")),
             r":::range \(line \d+\) is not allowed in part 10"),
        ]
        for src, pattern in cases:
            with self.subTest(pattern=pattern):
                self.reset_tmp()
                self.fails(src, pattern)

    def test_ranges_over_a_quotation_a_callout_and_a_framing(self):
        # A whole-block judgment opens a range and leaves the block's document role alone: the quotation keeps its rail
        # and attribution, the callout its magenta rail, the framing its panel and chip (review-semantics.md, rule 1).
        src = mutate(GUIDED, "What this synthetic document tests, and what not to judge.\n",
                     "What this synthetic document tests, and what not to judge.\n\n"
                     + ranged("review proposed: owner, round 1", ":::framing thesis\nShaded streets stay cooler.\n:::"))
        src = in_04(ranged("review accepted: v1 · owner", ':::quote "Resident"\nLook used, not styled.\n:::',
                           "basis: interview transcript\n")
                    + "\n" + ranged("review open: does wear mean use", ":::callout\nWe read this as signs of use.\n:::"), src)
        h = self.render(src)["html"]
        self.assertIn(RANGE_OPEN + row(item("review", "accepted", "Accepted", "v1 · owner"), key_item("Basis", "interview transcript"))
                      + '\n<div class="doc-prose">\n<blockquote class="doc-quote">\n<p>Look used, not styled.</p>\n'
                        '<footer>Resident</footer>\n</blockquote>\n</div>\n</div>', h)
        self.assertIn(RANGE_OPEN + row(item("review", "open", "Open question", "does wear mean use"))
                      + '\n<div class="doc-prose">\n<p class="doc-body surface-emphasis-rail" data-uo-role="callout">We read this '
                        'as signs of use.</p>\n</div>\n</div>', h)
        self.assertIn(RANGE_OPEN + row(item("review", "proposed", "Proposed", "owner, round 1")) + '\n<div data-uo-role="framing" '
                      'class="%s">\n<p class="surface-emphasis-chip surface-emphasis--magenta">thesis</p>' % build.FLAT_PANEL, h)
        build.check_final_html(h, 2)



class _Tree(HTMLParser):
    """A rendered body as an element tree: (tag, class tokens, children), elements only."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = ("root", (), [])
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        el = (tag, tuple((dict(attrs).get("class") or "").split()), [])
        self.stack[-1][2].append(el)
        if tag not in build.VOID_ELEMENTS:
            self.stack.append(el)

    def handle_endtag(self, tag):
        if tag not in build.VOID_ELEMENTS:
            while self.stack[-1][0] != tag:
                self.stack.pop()
            self.stack.pop()


def rail_depth(el, edge):
    """How deep el reaches a scope rail at its first or last (edge) edge, as the renderer's buffer rule reads it: 0
    for a range or a list that opens or closes on an item host, n for a div.doc-section or div.doc-prose whose edge
    child reaches one at n - 1; None otherwise."""
    tag, cls, kids = el
    if tag == "div" and "surface-labeled-range" in cls:
        return 0
    k = kids[0 if edge == "first" else -1] if kids else None
    if tag in ("ul", "ol"):
        return 0 if k is not None and k[0] == "li" and "surface-labeled-range" in k[1] else None
    if tag == "div" and ("doc-section" in cls or "doc-prose" in cls) and k is not None:
        d = rail_depth(k, edge)
        return None if d is None else d + 1
    return None


def rail_pairs(html_):
    """Each pair of adjacent element siblings in the body where the first ends on a scope rail and the second starts
    on one: (depth at the end, depth at the start)."""
    t = _Tree()
    t.feed(html_[html_.index("<main"):html_.index("</main>") + len("</main>")])
    pairs = []

    def walk(el):
        kids = el[2]
        for a, b in zip(kids, kids[1:]):
            da, db = rail_depth(a, "last"), rail_depth(b, "first")
            if da is not None and db is not None:
                pairs.append((da, db))
        for k in kids:
            walk(k)
    walk(t.root)
    return pairs


class ReviewAnnotationBoundaries(RenderCase):
    """Records on prompts and ranges, one note per list item and per note role, the passage buffer across UO's
    wrappers, diagnostics that name the working form, and placements README states (README, "Review annotations").
    Synthetic sources only."""

    def test_passage_buffer_rule_is_zero_specificity_geometry(self):
        md = css_rules(build.md_css(True))
        rules = [(sels, d) for m, sels, d in md if m is None and any(".surface-labeled-range" in x for x in sels)]
        self.assertEqual(len(rules), 1)
        sels, decls = rules[0]
        self.assertEqual(decls, {"margin-top": "var(--space-5)"})
        self.assertEqual(len(sels), 1)
        self.assertTrue(Presentation.zero_specificity(sels[0]))
        self.assertEqual(build.RAIL_BUFFER, ":where(.uo-md :is(%s) + :is(%s)) { margin-top: var(--space-5); }"
                         % (build._rail_edge("last"), build._rail_edge("first")))
        # Each edge names a range and a host list at every depth from 0 to RAIL_DEPTH: two alternatives per depth.
        for edge in ("first", "last"):
            alts = top_level_split(build._rail_edge(edge))
            self.assertEqual(len(alts), 2 * (build.RAIL_DEPTH + 1))
            self.assertEqual(sorted(a.count(build.RAIL_WRAPPER) for a in alts),
                             sorted([0, 0] + [d for d in range(1, build.RAIL_DEPTH + 1) for _ in (0, 1)]))
            for a in alts:
                self.assertNotIn("padding", a)
        self.assertNotRegex(build.RAIL_BUFFER, r"margin-(left|right|inline)|padding|border|::before")

    def test_passage_buffer_reaches_ranges_across_uo_wrappers(self):
        # The shapes whose rails met at 4 to 10px before the rule: a range closing a heading's section, then a range
        # around a synthesis lifted to the part; a list closing on an item host, then that range; adjacent questions
        # and findings, the first closing on a range and the next opening on one. And the direct siblings the owner's
        # rule spaces. These are the block pairs the rule's selectors reach; no maintained check measures the rendered
        # gap (the rendered check's buffer rule counts siblings only).
        synth = ranged("review accepted: v1 · owner · this synthesis", ":::synthesis\nWhat the part comes to.\n:::")
        shapes = {
            "section then panel range": in_04("### A subsection\n\nText.\n\n" + ranged("review open: a · owner", "Last.")
                                              + "\n" + synth),
            "host list then panel range": in_04("### A subsection\n\n- A plain item.\n- {{review open: owner · this item}} "
                                                "The last item.\n\n" + synth),
            "adjacent questions": mutate(GUIDED, ":::question\nA non-central question prompt.\n",
                                         ":::question\n" + ranged("review accepted: owner · this question as posed",
                                                                  "A non-central question prompt.")),
            "direct siblings": in_04(ranged("review proposed: a · editor", "First.") + "\n"
                                     + ranged("review accepted: b · owner", "Second.")),
        }
        shapes["adjacent questions"] = mutate(shapes["adjacent questions"], "The central question's detail, visible.\n",
                                              ranged("review accepted: owner · this answer",
                                                     "The central question's detail, visible."))
        findings = mutate(GUIDED, ":::finding\n**Status:** open. Finding, significance and limit.\n",
                          ":::finding\n**Status:** open. A first finding.\n\n"
                          + ranged("review accepted: owner · this limit", "Its limit.") + ":::\n\n:::finding\n"
                          + ranged("review accepted: owner · this status", "**Status:** open. A second finding."))
        shapes["adjacent findings"] = findings
        want = {"section then panel range": (1, 0), "host list then panel range": (2, 0), "adjacent questions": (1, 1),
                "direct siblings": (0, 0), "adjacent findings": (1, 1)}
        for name, src in shapes.items():
            with self.subTest(shape=name):
                self.reset_tmp()
                pairs = rail_pairs(self.render(src)["html"])
                self.assertIn(want[name], pairs)
                self.assertTrue(all(max(p) <= build.RAIL_DEPTH for p in pairs))

    def test_passage_buffer_depth_covers_the_deepest_nesting(self):
        # Three heading levels in part 03, the last question in the deepest, three heading levels inside it and a list
        # closing on an item host, then a range around the part's synthesis: the deepest chain UO composes.
        src = mutate(GUIDED, "The bounded question set.\n",
                     "The bounded question set.\n\n## Two\n\nText.\n\n### Three\n\nText.\n\n#### Four\n\nText.\n")
        src = mutate(src, "A non-central question prompt.\n\n:::disclose question-detail \"Question detail\"\n"
                          "The non-central question's detail.\n:::\n:::\n:::\n",
                     "A non-central question prompt.\n\n## Two\n\nText.\n\n### Three\n\nText.\n\n#### Four\n\n"
                     "- A plain item.\n- {{review accepted: owner · this item}} The last item.\n:::\n\n"
                     + ranged("review accepted: v1 · owner · this synthesis", ":::synthesis\nWhat the set comes to.\n:::")
                     + ":::\n")
        pairs = rail_pairs(self.render(src)["html"])
        self.assertIn((9, 0), pairs)
        self.assertLessEqual(max(max(p) for p in pairs), build.RAIL_DEPTH)

    def test_prompt_and_range_rows_carry_their_record(self):
        # review-semantics.md, rule 2: a bare label that names no target is no prompt; a range's row names its judgment.
        for word in build.REVIEW_WORDS:
            with self.subTest(word=word, row="prompt"):
                self.reset_tmp()
                src = in_04(":::annotate\nreview %s\n:::\n\n" % word + ranged("review open: x · owner", "W."))
                self.fails(src, r"%s: (a prompt's review item carries its record after ':'|review %s (shows a decision|"
                                r"names a request))" % (at(1), word))
            with self.subTest(word=word, row="range"):
                self.reset_tmp()
                src = in_04(":::range\n:::annotate\nreview %s\n:::\nW.\n:::\n" % word)
                self.fails(src, r"%s: (the review item that opens a :::range carries its record after ':'|review %s "
                                r"(shows a decision|names a request))" % (at(2), word))
        self.reset_tmp()
        self.fails(in_04(":::annotate\nreview open\n:::\n\n" + ranged("review open: x · owner", "W.")),
                   r"%s: a prompt's review item carries its record after ':': the content below as its target, the scope "
                   r"of its question and who decides, as in `review open: <record>`; a bare label that names no target is "
                   r"no prompt" % at(1))
        self.reset_tmp()
        self.fails(in_04(":::range\n:::annotate\nreview none\n:::\nW.\n:::\n"),
                   r"%s: the review item that opens a :::range carries its record after ':': what the range holds, the "
                   r"scope of the judgment and who decides or asks, as in `review none: <record>`" % at(2))
        # A note's row keeps its bare label: its marks name what it records.
        self.reset_tmp()
        self.render(in_04("Words {{mark open n: here}}.\n\n" + NOTE))

    def test_a_note_records_the_words_of_one_list_item(self):
        note = ":::note n\n:::annotate\nreview proposed: a narrower phrase · editor\n:::\n:::\n"
        cases = [
            ("- {{mark proposed n: alpha}} first.\n- middle.\n- {{mark proposed n: omega}} last.\n", 2),
            ("- {{mark proposed n: alpha}} first.\n    - {{mark proposed n: omega}} nested.\n- last.\n", 1),
            ("- {{mark proposed n: alpha}} first.\n- {{review open: owner · this item}} host {{mark proposed n: omega}}.\n", 1),
            ("- {{review open: owner · this item}} {{mark proposed n: alpha}}.\n"
             "- {{review accepted: owner · this item}} {{mark proposed n: omega}}.\n", 1),
        ]
        for text, k in cases:
            with self.subTest(text=text[:40]):
                self.reset_tmp()
                self.fails(in_04(text + "\n" + note), r"%s: passage marks in 2 list items name note 'n'; a note records "
                                                      r"the words of one list item" % at(k))
        self.reset_tmp()
        self.fails(in_04(ranged("review open: x · owner", "- {{mark proposed n: alpha}}.\n- {{mark proposed n: omega}}.")
                         + "\n" + note), r"%s: passage marks in 2 list items name note 'n'" % at(5))
        # Two marks in one item share their note, inside that item.
        self.reset_tmp()
        h = self.render(in_04("- {{mark proposed n: alpha}} and {{mark proposed n: omega}}.\n- another.\n\n" + note))["html"]
        self.assertIn('%s and %s.\n<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-n">'
                      % (passage("proposed", "n", "alpha"), passage("proposed", "n", "omega")), h)

    def test_a_note_on_a_plain_item_a_range_holds_follows_the_range(self):
        h = self.render(in_04(ranged("review open: x · owner · the list", "- A plain {{mark accepted n: item}}.\n- Another.")
                              + "\n:::note n\n:::annotate\nreview accepted: on “item” · owner\n:::\n:::\n"))["html"]
        self.assertIn('<li class="doc-body">A plain %s.</li>\n<li class="doc-body">Another.</li>\n</ul>\n</div>\n</div>\n'
                      '<div class="doc-hierarchy doc-group doc-annotation-note" id="uo-note-n">'
                      % passage("accepted", "n", "item"), h)

    def test_a_range_over_a_structure(self):
        h = self.render(in_04(ranged("review accepted: v1 · owner · this outline", ":::structure\nTop\n  Child\n:::")))["html"]
        self.assertIn(RANGE_OPEN + row(item("review", "accepted", "Accepted", "v1 · owner · this outline"))
                      + '\n<div class="doc-prose">\n<div class="doc-pre doc-pre--structured"><pre class="doc-pre-part">Top'
                        '</pre><div class="doc-hierarchy"><pre class="doc-pre-part">Child</pre></div></div>\n</div>\n</div>', h)

    def test_RS_prompts_in_a_question_a_finding_and_a_disclosure(self):
        prompt = ":::annotate\nreview open: on the range below · whether it holds · owner\n:::\n\n"
        src = mutate(GUIDED, "The central question prompt.\n",
                     prompt + ranged("review accepted: owner · this prompt", "The central question prompt."))
        src = mutate(src, "**Status:** open. Finding, significance and limit.\n",
                     prompt + ranged("review declined: owner · this status line", "**Status:** open. Finding, significance "
                                                                                 "and limit."))
        src = mutate(src, "The non-central question's detail.\n",
                     "The non-central question's detail.\n\n" + prompt
                     + ranged("review accepted: owner · this detail", "A ranged line in the detail."))
        src = mutate(src, "Field-level listing.\n", "Field-level listing.\n\n" + prompt
                     + ranged("review none: no production decision", "A ranged listing."))
        r = self.render(src)
        h = r["html"]
        self.assertEqual(r["counts"]["annotation_rows"], 8)          # four prompts and the four ranges' rows
        self.assertEqual(r["counts"]["annotation_ranges"], 4)
        prompt_html = row(item("review", "open", "Open question", "on the range below · whether it holds · owner"))
        for where in ('<div data-uo-role="question" data-uo-central="true"', '<div data-uo-role="finding"',
                      '<details data-uo-disclose="question-detail"', '<details data-uo-disclose="evidence"'):
            with self.subTest(where=where):
                block = h[h.index(where):]
                self.assertIn(prompt_html + "\n" + RANGE_OPEN, block[:block.index("</details>" if "details" in where
                                                                                   else "</div>\n</div>\n</div>")])
        build.check_final_html(h, 2)

    def test_a_later_row_or_list_in_a_range_names_the_first_child_rule(self):
        for later in (":::annotate list\nitem: a\nbasis: b\n:::\n", ":::annotate\nbasis: b\n:::\n"):
            with self.subTest(later=later[:16]):
                self.reset_tmp()
                src = in_04(":::range\n:::annotate\nreview open: x · owner\n:::\nWords.\n\n" + later + ":::\n")
                what = ":::annotate list" if "list" in later else ":::annotate"
                self.fails(src, r"%s: %s \(%s\) sits inside :::range \(%s\), which holds one :::annotate row, as its first "
                                r"child: one judgment per range" % (at(6), what, at(6), at()))

    def test_document_record_refuses_the_proposed_pair(self):
        src = mutate(GUIDED, ":::part 01\n", ":::annotate document\nstate proposed: draft\nreview proposed: SYN-GR-001 as a "
                                             "whole · editor\n:::\n\n:::part 01\n")
        self.fails(src, r"line %d: the document's record cannot carry both state proposed and review proposed: they read "
                        r"as one word twice, and the record is a row, never a list" % row_of(src, "review proposed: SYN"))

    def test_an_item_host_carries_its_record(self):
        # An item host is its own range (README, "Review annotations"): its review item names its judgment after ':',
        # whatever its word, as a range's row and a prompt's do. A table cell's item keeps judging its cell.
        host = "- {{review %s}} The item's words.\n- A plain item.\n"

        def in_question(text):
            return mutate(GUIDED, "The central question's detail, visible.\n",
                          "The central question's detail, visible.\n\n" + text)
        places = (("part 04", in_04), ("question", in_question))
        for word in build.REVIEW_WORDS:
            for where, place in places:
                with self.subTest(word=word, where=where):
                    self.reset_tmp()
                    src = place(host % word)
                    self.fails(src, r"line %d: (the review item that opens an item host carries its record after ':'|"
                                    r"review %s (shows a decision|names a request))" % (row_of(src, "{{review"), word))
        for word in ("open", "proposed", "none"):
            for where, place in places:
                for text in (host % word, "- {{review %s}}{{basis: owner-stated}} The item's words.\n" % word):
                    with self.subTest(word=word, where=where, text=text[:30]):
                        self.reset_tmp()
                        src = place(text)
                        self.fails(src, r"line %d: the review item that opens an item host carries its record after "
                                        r"':': what the item holds, the scope of the judgment and who decides or asks, "
                                        r"as in \{\{review %s: <record>\}\}" % (row_of(src, "{{review"), word))
        for word in build.REVIEW_WORDS:
            for where, place in places:
                with self.subTest(word=word, where=where, record=True):
                    self.reset_tmp()
                    r = self.render(place("- {{review %s: owner · this item}} The item's words.\n" % word))
                    self.assertEqual(r["counts"]["item_hosts"], 1)
        self.reset_tmp()
        self.assertEqual(self.render(in_04(CELL % "{{review open}}"))["counts"]["cell_items"], 1)

    def test_passage_buffer_only_where_the_document_annotates(self):
        # The passage buffer is gated where the semantic-state modules are: an unannotated document's stylesheet is
        # MD_CSS alone, with no rule naming a range; an annotated one's is MD_CSS, then the buffer.
        self.assertEqual(build.md_css(False), build.MD_CSS)
        self.assertEqual(build.md_css(True), build.MD_CSS + build.RAIL_BUFFER + "\n")
        self.assertNotIn("surface-labeled-range", build.MD_CSS)
        self.assertNotIn(build.RAIL_BUFFER, build.MD_CSS)
        plain = self.render(GUIDED, name="plain")
        self.assertEqual(build.annotation_count(plain["counts"]), 0)
        self.assertEqual(plain["inlined"], build.MODULES)
        self.assertNotIn(build.RAIL_BUFFER, plain["html"])
        self.assertNotIn(":where(.uo-md :is(div.surface-labeled-range", plain["html"])
        self.assertEqual(plain["html"].count("<style>" + build.MD_CSS + "</style>"), 1)
        rich = self.render(in_04(ranged("review open: x · owner", "W.")), name="rich")
        self.assertGreater(build.annotation_count(rich["counts"]), 0)
        self.assertEqual(rich["inlined"], build.MODULES + build.STATE_MODULES)
        self.assertEqual(rich["html"].count(build.RAIL_BUFFER), 1)
        self.assertEqual(rich["html"].count("<style>" + build.md_css(True) + "</style>"), 1)


if __name__ == "__main__":
    unittest.main()
