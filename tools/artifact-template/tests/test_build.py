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
                                       "authored_case": 0})

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
        self.assertIn("| markdown | `3.4.1` |", m)
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
        for number in ("02", "04", "06", "08"):
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
            uo_css = f.read().split("</head>")[0] + build.MD_CSS
        register_css = ""
        for rel in build.MODULES:
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


class Atomicity(RenderCase):
    def test_N62_markdown_version_not_pin(self):
        with mock.patch.object(build.markdown, "__version__", "3.5.0"):
            self.fails(GUIDED, r"markdown 3.5.0 is installed; this renderer is pinned to markdown==3.4.1")

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
        rules = [(sels, d) for m, sels, d in css_rules(build.MD_CSS) + css_rules(template_css())
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
        self.md = css_rules(build.MD_CSS)
        self.tpl = css_rules(template_css())

    @staticmethod
    def zero_specificity(sel):
        return re.fullmatch(r"(?::where\((?:[^()]|\([^()]*(?:\([^()]*\))*[^()]*\))*\)\s*(?:>\s*)?)+", sel) is not None

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
        for sheet, rules in (("template", css_rules(template_css())), ("MD_CSS", css_rules(build.MD_CSS))):
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
        self.assertEqual(focus_ring_hazards(template_css()) + focus_ring_hazards(build.MD_CSS)
                         + focus_ring_hazards(foundation), [])
        self.assertNotIn("outline", build.MD_CSS + template_css())
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
        self.assertEqual([f["path"] for f in dep["files"]][-len(build.MODULES):], ["_dsa-surface/" + x for x in build.MODULES])
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
            (reg(":::quote\n:::callout\nx\n:::\n:::\n"), r":::callout is allowed inside :::part, :::question, :::finding, :::disclose only"),
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


if __name__ == "__main__":
    unittest.main()
