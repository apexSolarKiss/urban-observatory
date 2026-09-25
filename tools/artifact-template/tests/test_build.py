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

TABLE = """:::table key text num status
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
        self.assertIn('<section data-uo-part="03" id="uo-part-03">', h)
        self.assertIn('<div data-uo-role="question" data-uo-central="true">', h)
        self.assertIn('<div data-uo-role="finding">', h)
        for cls in ("question-detail", "evidence", "provenance"):
            self.assertIn('<details data-uo-disclose="%s" class="uo-details"><summary>' % cls, h)
        self.assertEqual(r["counts"], {"questions": 2, "findings": 1, "disclosures": 3, "tables": 1})

    def test_confirmation_baseline_generates_01_and_10(self):
        r = self.render(CONFIRMATION)
        self.assertEqual(r["parts"], ["01", "02", "07", "10"])
        h = r["html"]
        self.assertIn('<section data-uo-part="01" id="uo-part-01">\n<div class="uo-status-rail">', h)
        self.assertRegex(h, r'<section data-uo-part="10" id="uo-part-10">\n<footer class="uo-foot">')

    def test_all_ten_parts_render_in_order(self):
        src = GUIDED
        src = mutate(src, ":::part 06\n", ":::part 05\nSynthetic finding index.\n:::\n\n:::part 06\n")
        src = mutate(src, ":::part 08\n", ":::part 06\n:::finding\nA second finding.\n:::\n:::\n\n"
                                             ":::part 07\nSynthetic prior-position delta.\n:::\n\n:::part 08\n")
        src = mutate(src, ":::part 10\n", ":::part 09\nSynthetic response format.\n:::\n\n:::part 10\n")
        r = self.render(src)
        self.assertEqual(r["parts"], ["01", "02", "03", "04", "05", "06", "06", "07", "08", "09", "10"])
        self.assertEqual(re.findall(r'<section data-uo-part="(\d\d)" id="uo-part-\d\d(?:-\d+)?">', r["html"]), r["parts"])
        self.assertEqual(re.findall(r'<section data-uo-part="\d\d" id="([a-z0-9-]+)">', r["html"]),
                         ["uo-part-01", "uo-part-02", "uo-part-03", "uo-part-04", "uo-part-05", "uo-part-06",
                          "uo-part-06-2", "uo-part-07", "uo-part-08", "uo-part-09", "uo-part-10"])
        self.assertEqual(r["counts"]["findings"], 2)

    def test_ordered_list_start_and_link_title_allowed(self):
        src = mutate(GUIDED, "The synthetic executive result.\n",
                     "The synthetic executive result.\n\n3. third\n4. fourth\n\n"
                     "[a link](https://example.org/x \"Synthetic title\")\n")
        h = self.render(src)["html"]
        self.assertIn('<ol start="3">', h)
        self.assertIn('<a href="https://example.org/x" title="Synthetic title">a link</a>', h)

    def test_N48_roles_applied_to_every_cell(self):
        h = self.render(with_table())["html"]
        cells = re.findall(r"<(th|td)( [^>]*)?>", h)
        self.assertEqual(len(cells), 12)
        roles = re.findall(r'<t[hd] data-uo-cell="([a-z]+)"[ >]', h)
        self.assertEqual(roles, ["key", "text", "num", "status"] * 3)

    def test_N18_repeated_06_allowed(self):
        src = mutate(GUIDED, ":::part 08\n", ":::part 06\n:::finding\nA second finding.\n:::\n:::\n\n:::part 08\n")
        r = self.render(src)
        self.assertEqual(r["parts"].count("06"), 2)

    def test_N6_colons_inside_fenced_code_are_code(self):
        src = mutate(GUIDED, "The synthetic executive result.\n",
                     "The synthetic executive result.\n\n```text\n:::part 09\n:::\n```\n")
        h = self.render(src)["html"]
        self.assertIn("<pre><code class=\"language-text\">:::part 09\n:::\n</code></pre>", h)

    def test_N35_tags_in_code_pass(self):
        src = mutate(GUIDED, "The synthetic executive result.\n",
                     "The synthetic executive result, `<div>` in a span.\n\n```\n<div>x</div>\n```\n\n"
                     "Indented:\n\n    <span>y</span>\n")
        h = self.render(src)["html"]
        self.assertIn("<code>&lt;div&gt;</code>", h)
        self.assertIn("&lt;div&gt;x&lt;/div&gt;", h)
        self.assertIn("&lt;span&gt;y&lt;/span&gt;", h)

    def test_N68_import_and_marker_text_in_body_render(self):
        src = mutate(GUIDED, "The synthetic executive result.\n",
                     "The synthetic executive result: `@import` and `@@X@@` and `<link>`.\n")
        h = self.render(src)["html"]
        self.assertIn("<code>@import</code>", h)
        self.assertIn("<code>@@X@@</code>", h)

    def test_meta_header_drives_masthead_rail_and_title(self):
        h = self.render(GUIDED)["html"]
        self.assertIn("<title>Synthetic guided review</title>", h)
        self.assertIn('<span class="uo-status-rail__primary">synthetic fixture</span>'
                      '<span class="uo-status-rail__sep"></span><span>renderer test</span>'
                      '<span class="uo-status-rail__sep"></span><span>guided-review</span>'
                      '<span class="uo-status-rail__sep"></span><span>R1</span>', h)
        self.assertIn("<h1>Synthetic guided review</h1>", h)
        self.assertIn("<dt>id</dt><dd>SYN-GR-001</dd><dt>kind</dt><dd>guided-review</dd><dt>round</dt><dd>R1</dd>", h)
        self.assertNotIn("approv", h.split("<body>")[1].lower())

    def test_N66_title_escaped_and_literal(self):
        src = mutate(GUIDED, "title: Synthetic guided review\n", "title: A <b> & \\1 \\g<0> title\n")
        h = self.render(src)["html"]
        self.assertIn("<title>A &lt;b&gt; &amp; \\1 \\g&lt;0&gt; title</title>", h)
        self.assertIn("<h1>A &lt;b&gt; &amp; \\1 \\g&lt;0&gt; title</h1>", h)

    def test_N67_seal_line_verified_and_never_unknown(self):
        r = self.render(GUIDED)
        foot = re.search(r'<footer class="uo-foot">.*?</footer>', r["html"], flags=re.S).group(0)
        self.assertNotIn("unknown", foot)
        dep = build.verify_dependencies()
        self.assertIn("design-system-ASK tokens <code>%s</code>" % dep["commit"][:7], foot)
        self.assertIn("urban-observatory <code>%s</code> (declared)" % UO_COMMIT[:7], foot)

    def test_local_css_hook_and_emission(self):
        src = mutate(GUIDED, ":::finding\n", ":::finding local=ctl\n")
        css = "main.uo-md .uo-local-ctl p,\nmain.uo-md .uo-local-ctl li { color: var(--fg-2); }\n"
        r = self.render(src, local_css=css)
        h = r["html"]
        self.assertIn('<div data-uo-role="finding" class="uo-local-ctl">', h)
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
        self.assertIn('<section data-uo-part="02" id="uo-part-02" class="uo-local-wide-a">', h)
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

    def test_N43_chrome_classes_exist_in_template_or_md_css(self):
        with open(build.TEMPLATE, encoding="utf-8") as f:
            css = f.read().split("</head>")[0] + build.MD_CSS

        def missing(table):
            return sorted(c for classes in table.values() for c in classes
                          if not re.search(r"\." + re.escape(c) + r"(?![A-Za-z0-9_-])", css))
        self.assertEqual(missing(build.CHROME_CLASSES), [])
        self.assertEqual(missing({"div": ("uo-unstyled-role",)}), ["uo-unstyled-role"])

    def test_allowlist_rejects_injected_output(self):
        h = self.render(GUIDED)["html"]
        bad = [
            (h.replace('<html lang="en">', '<html lang="en" data-theme="dark">'), r"<html> must be the root and carry lang only"),
            (h.replace("</head>", "<script></script></head>"), r"<script> not allowed in <head>"),
            (h.replace('<main class="uo-md">', '<main class="uo-md" id="x">'), r"attribute id='x' not allowed on <main>"),
            (h.replace("<p>Synthetic locator line.</p>", '<p onclick="x()">Synthetic locator line.</p>'), r"attribute onclick"),
            (h.replace("</style>", "@import url(x.css);</style>", 1), r"CSS contains @import"),
            (h.replace("</style>", 'p { background-image: image-set("https://x.invalid/a.png" 1x); }</style>', 1),
             r"CSS contains image-set\(, which can load a resource"),
            (h.replace("<p>Synthetic locator line.</p>", '<p class="caption">Synthetic locator line.</p>'),
             r"class 'caption' not allowed on <p>"),
        ]
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                with self.assertRaises(build.BuildError) as cm:
                    build.check_final_html(doc, 2)
                self.assertRegex(str(cm.exception), pattern)


class Tables(RenderCase):
    def test_N44_table_without_container(self):
        self.fails(with_table(table=TABLE.replace(":::table key text num status\n", "").replace("| closed |\n:::\n", "| closed |\n")),
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
        self.assertIn('<td data-uo-cell="text" data-uo-label="Claim">'
                      '<span class="uo-cell-label">Claim</span>a | b and <code>x|y</code></td>', h)


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
            if prelude.startswith("@media"):
                depth, k = 1, j + 1
                while depth:
                    depth += {"{": 1, "}": -1}.get(text[k], 0)
                    k += 1
                block(text[j + 1:k - 1], prelude[len("@media"):].strip())
                i = k
                continue
            k = text.index("}", j)
            decls = {}
            for d in text[j + 1:k].split(";"):
                if ":" in d:
                    name, _, value = d.partition(":")
                    decls[name.strip()] = " ".join(value.split())
            rules.append((media, tuple(" ".join(x.split()) for x in prelude.split(",")), decls))
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


U2_TABLE = """:::table key text num status "A <b> & caption"
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
    """U2: the template's disclosure, numeric, key and caption roles are reachable from the renderer."""

    def test_U2_disclosure_role_emitted(self):
        src = mutate(GUIDED, ':::disclose evidence "Field-level evidence"\n', ':::disclose evidence local=ev "Field-level evidence"\n')
        h = self.render(src)["html"]
        self.assertIn('<details data-uo-disclose="question-detail" class="uo-details"><summary>Question detail</summary>\n'
                      '<div class="uo-details__body">\n<p>The non-central question\'s detail.</p>\n</div>\n</details>', h)
        self.assertIn('<details data-uo-disclose="evidence" class="uo-details uo-local-ev"><summary>', h)
        self.assertEqual(len(re.findall(r'<details [^>]*class="uo-details[ "]', h)), 3)
        self.assertEqual(len(re.findall(r'<div class="uo-details__body">', h)), 3)

    def test_U2_code_block_in_disclosure_emitted_in_the_body(self):
        src = mutate(GUIDED, "Field-level listing.\n", "Field-level listing.\n\n```text\nline\n```\n\n    indented line\n")
        h = self.render(src)["html"]
        self.assertIn('<div class="uo-details__body">\n<p>Field-level listing.</p>\n'
                      '<pre><code class="language-text">line\n</code></pre>\n<pre><code>indented line\n</code></pre>\n</div>', h)

    def test_U2_caption_emitted_and_escaped(self):
        h = self.render(with_table(table=U2_TABLE))["html"]
        self.assertIn('<table>\n<caption>A &lt;b&gt; &amp; caption</caption>\n<thead>', h)
        h = self.render(with_table(table=U2_TABLE.replace(":::table ", ":::table local=w ")), name="local")["html"]
        self.assertIn('<table class="uo-local-w">\n<caption>A &lt;b&gt; &amp; caption</caption>', h)
        h = self.render(with_table(), name="nocap")["html"]
        self.assertNotIn("<caption", h)

    def test_U2_every_body_cell_carries_its_header_text(self):
        h = self.render(with_table(table=U2_TABLE))["html"]
        self.assertIn('<th data-uo-cell="key">Row <code>id</code></th>', h)
        self.assertIn('<td data-uo-cell="key" data-uo-label="Row id">'
                      '<span class="uo-cell-label">Row <code>id</code></span>a</td>', h)
        self.assertIn('<td data-uo-cell="text" data-uo-label="Claim &amp; limit">'
                      '<span class="uo-cell-label">Claim &amp; <em>limit</em></span>first claim</td>', h)
        self.assertIn('<td data-uo-cell="num" data-uo-label="Count">'
                      '<span class="uo-cell-label">Count</span>12</td>', h)
        self.assertIn('<td data-uo-cell="status" data-uo-label="State">'
                      '<span class="uo-cell-label">State</span>closed</td>', h)
        self.assertEqual(len(re.findall(r"<td [^>]*data-uo-label=", h)), 8)
        self.assertNotRegex(h, r"<th [^>]*data-uo-label=")

    def test_U2_R2_visible_label_element_keeps_header_links_and_code(self):
        # U2-R2: the label a reader actually sees at narrow widths is an element carrying the header
        # cell's own inline markup, not generated plain text, so a header's link stays an operable link
        # and its inline code stays code. One label element per body cell, each directly inside its <td>.
        h = self.render(with_table(table=LINK_HEADER_TABLE))["html"]
        self.assertIn('<span class="uo-cell-label">Row <a href="https://example.com/spec">spec</a></span>', h)
        self.assertIn('<span class="uo-cell-label">Claim <code>x|y</code></span>', h)
        self.assertEqual(len(re.findall(r'<span class="uo-cell-label">', h)), 4)
        self.assertEqual(len(re.findall(r'<td [^>]*><span class="uo-cell-label">', h)), 4)
        # the operable link is reproduced in the body, not only in the header row
        self.assertEqual(len(re.findall(r'href="https://example\.com/spec"', h)), 3)
        build.check_final_html(h, 2)

    def test_U2_R2_a_dropped_visible_label_fails_the_build(self):
        # The visible label IS the U2-R2 guarantee, so its ABSENCE must fail the check, not only a wrong
        # label's text. Validating the span's text only when a span happens to be present leaves the
        # guarantee unenforced against the one regression that would actually remove the operation.
        h = self.render(with_table(table=LINK_HEADER_TABLE))["html"]
        build.check_final_html(h, 2)                                    # control: the real render passes
        one = re.search(r'<span class="uo-cell-label">.*?</span>', h, re.S)
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
        one = '<td data-uo-cell="num" data-uo-label="Count"><span class="uo-cell-label">Count</span>12</td>'
        bad = [
            (h.replace(one, '<td data-uo-cell="num"><span class="uo-cell-label">Count</span>12</td>'),
             r"<td> without data-uo-label"),
            (h.replace(one, '<td data-uo-cell="num" data-uo-label="State"><span class="uo-cell-label">Count</span>12</td>'),
             r"<td data-uo-label='State'> does not equal its column's header text 'Count'"),
            (h.replace(one, '<td data-uo-cell="num" data-uo-label="Count "><span class="uo-cell-label">Count</span>12</td>'),
             r"does not equal its column's header text"),
            (h.replace(one, '<td data-uo-cell="num" data-uo-label="Count"><span class="uo-cell-label">State</span>12</td>'),
             r"<span class='uo-cell-label'> text 'State' does not equal its column's header text 'Count'"),
            (h.replace('<p>Synthetic locator line.</p>', '<span class="uo-cell-label">x</span>'),
             r"class 'uo-cell-label' allowed only on a <span> directly inside <td>"),
            (h.replace('<th data-uo-cell="num">', '<th data-uo-cell="num" data-uo-label="Count">'),
             r"attribute data-uo-label='Count' not allowed on <th>"),
            (h.replace('class="uo-details"><summary>Question detail', '><summary>Question detail'),
             r"<details> without class uo-details"),
            (h.replace('<p>Synthetic locator line.</p>', '<div class="uo-details__body">x</div>'),
             r"class 'uo-details__body' allowed only on a <div> directly inside <details>"),
            (h.replace('<p>Synthetic locator line.</p>', '<caption>x</caption>'), r"<caption> outside <table>"),
            (h.replace('<div class="uo-shell">', '<div class="uo-shell uo-local-x">'), r"class 'uo-shell uo-local-x' not allowed on <div>"),
            (h.replace('class="uo-details"><summary>Question detail', 'class="uo-details uo-details"><summary>Question detail'),
             r"class 'uo-details uo-details' not allowed on <details>"),
            (h.replace('class="uo-details"><summary>Question detail', 'class="uo-local-x uo-details"><summary>Question detail'),
             r"class 'uo-local-x uo-details' not allowed on <details>"),
            (h.replace('<table>', '<table class="caption">'), r"class 'caption' not allowed on <table>"),
        ]
        for doc, pattern in bad:
            with self.subTest(pattern=pattern):
                self.assertNotEqual(doc, h)
                with self.assertRaises(build.BuildError) as cm:
                    build.check_final_html(doc, 2)
                self.assertRegex(str(cm.exception), pattern)
        build.check_final_html(h, 2)


class Presentation(unittest.TestCase):
    """U2: the CSS behaviors behind the profile roles, wrapping, narrow screens, theme and print.
    Values are not asserted beyond the behavior each rule exists for."""

    def setUp(self):
        self.md = css_rules(build.MD_CSS)
        self.tpl = css_rules(template_css())

    def test_U2_role_rules_reach_the_renderer_hooks(self):
        num = [d for m, sels, d in self.tpl if '.uo-md td[data-uo-cell="num"]' in sels]
        self.assertEqual(num, [{"text-align": "right", "font-variant-numeric": "tabular-nums"}])
        self.assertTrue(any('.uo-md th[data-uo-cell="num"]' in sels and ".uo-data-table td.num" in sels for m, sels, d in self.tpl))
        key = [d for m, sels, d in self.tpl if '.uo-md td[data-uo-cell="key"]' in sels]
        self.assertEqual(key, [{"color": "var(--fg-1)", "font-weight": "var(--fw-medium)"}])
        self.assertTrue(any(".uo-data-table tr.uo-row-key td" in sels and '.uo-md td[data-uo-cell="key"]' in sels for m, sels, d in self.tpl))
        cap = [(sels, d) for m, sels, d in self.tpl if ".uo-md table > caption" in sels]
        self.assertEqual(len(cap), 1)
        self.assertIn(".uo-data-table caption", cap[0][0])
        self.assertTrue(any("details.uo-details > summary" in sels for m, sels, d in self.tpl))
        self.assertTrue(any("details.uo-details > .uo-details__body" in sels for m, sels, d in self.tpl))

    def test_U2_R1_caption_and_summary_keep_the_authored_case(self):
        # U2-R1: the two roles that carry authored payload text must not transform its case. The override is
        # UO-local (the renderer's own stylesheet), it changes nothing else about either role, and the
        # template's own carrier rules are untouched.
        #
        # Each override must beat its template rule ON SPECIFICITY, never on emission order. The template
        # carries the identical selector `.uo-md table > caption`, so an equal-specificity override would win
        # only because MD_CSS happens to be emitted second — a silent revert if that order ever changed, and
        # nothing else in this suite pins it. `main.uo-md ...` adds a type selector and wins either way.
        for sel in ("main.uo-md table > caption", ".uo-md details.uo-details > summary"):
            got = [d for m, sels, d in self.md if m is None and sel in sels]
            self.assertEqual(got, [{"text-transform": "none"}], sel)
        for local_sel, tpl_sel in (("main.uo-md table > caption", ".uo-md table > caption"),
                                   (".uo-md details.uo-details > summary", "details.uo-details > summary")):
            self.assertGreater(specificity(local_sel), specificity(tpl_sel),
                               "%s must outrank %s on specificity, not on emission order" % (local_sel, tpl_sel))
        # the template still sets uppercase for both, so the override is doing real work
        cap = [d for m, sels, d in self.tpl if ".uo-md table > caption" in sels]
        self.assertEqual([d.get("text-transform") for d in cap], ["uppercase"])
        summ = [d for m, sels, d in self.tpl if "details.uo-details > summary" in sels and "text-transform" in d]
        self.assertEqual([d.get("text-transform") for d in summ], ["uppercase"])
        # the other governed metrics of both roles stay with the template and are not restated locally
        for d in cap + summ:
            for prop in ("font-family", "font-size", "font-weight", "letter-spacing", "color"):
                self.assertIn(prop, d)
        local = [d for m, sels, d in self.md if m is None
                 and ("main.uo-md table > caption" in sels or ".uo-md details.uo-details > summary" in sels)]
        self.assertEqual(sorted({k for d in local for k in d}), ["text-transform"])
        # the disclosure marker affordance is untouched
        self.assertTrue(any("details.uo-details > summary::before" in sels for m, sels, d in self.tpl))
        self.assertTrue(any("details.uo-details[open] > summary::before" in sels for m, sels, d in self.tpl))

    def test_U2_text_wraps_everywhere_in_the_document(self):
        self.assertEqual(rules_with(self.md, ".uo-md") [-1], {"overflow-wrap": "anywhere"})
        self.assertIn({"overflow-wrap": "anywhere"}, rules_with(self.md, ".uo-md td"))

    def test_U2_table_cells_fit_first_headers_included(self):
        # U1's fit-first wrap governs every cell. Checked in two stylesheets: no MD_CSS rule outside the narrow
        # block, and no template rule that can select the renderer's cells (every class its selector names is
        # one the renderer emits), gives a header or body cell another wrap, a white-space, a word-break, a
        # hyphens or a width setting. Other stylesheets (local CSS) and computed layout are not checked here.
        self.assertIn({"overflow-wrap": "anywhere"}, rules_with(self.md, ".uo-md th"))
        cell = re.compile(r"(^|[\s>+~])(th|td|thead|tbody|tr)([\s.:\[>+~]|$)")
        emitted = {c for classes in build.CHROME_CLASSES.values() for c in classes}

        def reachable(selector):
            return bool(cell.search(selector)) and set(re.findall(r"\.([\w-]+)", selector)) <= emitted

        matched = [("MD_CSS", sels, d) for m, sels, d in self.md if m is None and any(cell.search(s) for s in sels)]
        self.assertGreaterEqual(len(matched), 3)          # the MD_CSS check is not vacuous
        in_template = [("template", sels, d) for m, sels, d in self.tpl if any(reachable(s) for s in sels)]
        self.assertGreaterEqual(len(in_template), 2)      # the num and key role rules: the template check is not vacuous
        for sheet, sels, d in matched + in_template:
            with self.subTest(stylesheet=sheet, selectors=sels):
                self.assertEqual(d.get("overflow-wrap", "anywhere"), "anywhere")
                for prop in ("white-space", "word-break", "hyphens", "min-width", "width"):
                    self.assertNotIn(prop, d)
        # the template's own data-table header rule is left as it is; the renderer never emits its class
        self.assertEqual([d.get("white-space") for d in rules_with(self.tpl, ".uo-data-table th")], [None, "nowrap"])
        self.assertFalse(any("uo-data-table" in classes for classes in build.CHROME_CLASSES.values()))

    def test_U2_stacked_labels_align_left_in_every_column(self):
        before = [d for m, sels, d in self.md if m == "(max-width: 960px)" and ".uo-md .uo-cell-label" in sels]
        self.assertEqual(len(before), 1)
        self.assertEqual(before[0].get("text-align"), "left")
        # without it the label would inherit the num role's right alignment
        self.assertIn("right", [d.get("text-align") for m, sels, d in self.tpl if '.uo-md td[data-uo-cell="num"]' in sels])

    def test_U2_code_block_in_disclosure_renders_as_outside(self):
        body_code = [sels for m, sels, d in self.tpl for s in sels
                     if ".uo-details__body" in s and re.search(r"\bcode$", s)]
        self.assertEqual(body_code, [("details.uo-details > .uo-details__body :not(pre) > code",)])
        md_line_height = [d["line-height"] for m, sels, d in self.md if m is None and sels == (".uo-md",) and "line-height" in d]
        self.assertEqual(len(md_line_height), 1)
        self.assertEqual(rules_with(self.md, ".uo-md .uo-details__body pre"), [{"line-height": md_line_height[0]}])

    def test_U2_narrow_screens_stack_rows_without_display_none_visibility_or_font_size(self):
        # Checks the narrow block's declarations only: the stacked parts, the label rule, the header-row rules, and
        # no display: none, visibility or font-size in the block. It cannot tell whether content is visually
        # hidden: the header row is moved out of view with a clip, and the reader sees the header as the per-cell
        # label element instead. U2-R2 adds the focus reveal, checked by its own test below.
        media = "(max-width: 960px)"
        self.assertIn(media, [m for m, s, d in self.tpl if m])   # the template's existing threshold, same media
        narrow = [(sels, d) for m, sels, d in self.md if m == media]
        blocks = [s for sels, d in narrow if d.get("display") == "block" and "content" not in d for s in sels]
        self.assertEqual(sorted(blocks), sorted([".uo-md table", ".uo-md caption", ".uo-md tbody", ".uo-md tr", ".uo-md td",
                                                 ".uo-md .uo-cell-label",
                                                 ".uo-md thead:focus-within tr", ".uo-md thead:focus-within th"]))
        self.assertIn({"display": "block", "font-weight": "var(--fw-medium)", "text-align": "left"},
                      [d for sels, d in narrow if ".uo-md .uo-cell-label" in sels])
        head = [d for sels, d in narrow if ".uo-md thead" in sels]
        self.assertEqual(len(head), 1)
        for sels, d in narrow:
            self.assertNotIn(d.get("display"), ("none",))
            self.assertNotIn("visibility", d)
            self.assertNotIn("font-size", d)
        # no narrow-block rule uses generated content to carry payload text
        self.assertEqual([d for sels, d in narrow if "content" in d], [])
        self.assertNotIn(".uo-md th", [s for sels, d in narrow for s in sels])

    def test_U2_R2_focused_header_row_returns_to_view(self):
        # U2-R2: a link inside the out-of-view header row must not be focusable while invisible. The reveal
        # undoes every declaration that takes the row out of view, and stacks it so revealing cannot widen
        # the page. Checked as declarations; the browser measurement is the check for the effect.
        narrow = [(sels, d) for m, sels, d in self.md if m == "(max-width: 960px)"]
        hidden = [d for sels, d in narrow if sels == (".uo-md thead",)]
        self.assertEqual(len(hidden), 1)
        shown = [d for sels, d in narrow if sels == (".uo-md thead:focus-within",)]
        self.assertEqual(len(shown), 1)
        # every property that hides the row is reset by the reveal
        self.assertEqual(sorted(hidden[0]), sorted(shown[0]))
        self.assertEqual(shown[0], {"position": "static", "width": "auto", "height": "auto",
                                    "overflow": "visible", "clip-path": "none", "white-space": "normal"})
        self.assertIn({"display": "block"},
                      [d for sels, d in narrow if ".uo-md thead:focus-within th" in sels])

    def test_U2_theme_dark_resolves_the_template_tokens(self):
        dark = [(sels, d) for m, sels, d in self.tpl if m is None and ':root[data-theme="dark"]' in sels]
        declared = sorted(k for sels, d in dark for k in d)
        self.assertEqual(declared, ["--artifact-line", "--artifact-line-soft", "--uo-code-bg", "--uo-mark", "--uo-soft-bg"])
        for sels, d in dark:
            self.assertEqual(sels, (':root[data-theme="dark"]', ".theme-dark"))
        with open(os.path.join(HERE, "_dsa-tokens", "colors_and_type.css"), encoding="utf-8") as f:
            foundation = css_rules(f.read())
        self.assertTrue(any(sels == (':root[data-theme="dark"]', ".theme-dark") for m, sels, d in foundation))

    def test_U2_print_keeps_the_theme_ground_and_rebinds_no_token(self):
        self.assertIn({"-webkit-print-color-adjust": "exact", "print-color-adjust": "exact"}, rules_with(self.tpl, "html", "print"))
        self.assertIn({"white-space": "pre-wrap"}, rules_with(self.md, ".uo-md pre", "print"))
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
        head = re.search(r'<section data-uo-part="01" id="uo-part-01">\n(.*?)\n</section>', h, flags=re.S).group(1)
        self.assertRegex(head, r'^<div class="uo-status-rail">.*</div>\n<header class="uo-head">\n'
                               r'<details class="uo-index"><summary class="uo-index__mark"><svg class="uo-mark" [^>]*>.*</svg>'
                               r'<span class="uo-index__label">sections</span></summary>\n'
                               r'<nav class="uo-index__list" aria-label="Sections"><ol>.*</ol></nav>\n</details>\n'
                               r'<h1>Synthetic guided review</h1>\n<dl class="uo-head__meta">.*</dl>\n</header>\n'
                               r'<p>Synthetic locator line.</p>$')
        links = re.findall(r'<li><a href="#([a-z0-9-]+)">([^<]+)</a></li>', h)
        self.assertEqual(links, [("uo-part-01", "01 locator + masthead"), ("uo-part-02", "02 reviewer brief"),
                                 ("uo-part-03", "03 decision request"), ("uo-part-04", "04 executive result"),
                                 ("uo-part-06", "06 finding unit"), ("uo-part-08", "08 unresolved + later-check register"),
                                 ("uo-part-10", "10 seal + provenance")])
        self.assertEqual([sid for sid, _ in links], re.findall(r'<section data-uo-part="\d\d" id="([a-z0-9-]+)"', h))

    def test_U3_index_lists_only_the_sections_present(self):
        h = self.render(CONFIRMATION)["html"]
        self.assertEqual(re.findall(r'<li><a href="#([a-z0-9-]+)">', h), ["uo-part-01", "uo-part-02", "uo-part-07", "uo-part-10"])

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
        self.assertIn('<li><a href="#uo-part-06-2">06 finding unit 2</a></li>', h)
        self.assertIn('<li><a href="#uo-part-06-3">06 finding unit 3</a></li>', h)

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
        self.assertIn('</header>\n<div class="uo-reviewer-status">\n<p class="uo-reviewer-status__flag">review status</p>\n'
                      '<div class="uo-reviewer-status__body">\n<p>Synthetic status line.</p>\n</div>\n</div>\n'
                      '<div class="uo-proof">\n<p class="uo-proof__flag">proof of assembly</p>\n'
                      '<p class="uo-proof__title">Synthetic proof title</p>\n'
                      '<div class="uo-proof__body">\n<p>Synthetic proof line.</p>\n</div>\n</div>\n</section>', h)

    def test_U3_banners_keep_source_order(self):
        h = self.render(with_part_01(part=":::part 01\nA locator line.\n\n:::banner proof\nP.\n:::\n\n"
                                          ":::banner review-status\nR.\n:::\n:::\n\n"))["html"]
        self.assertLess(h.index("<p>A locator line.</p>"), h.index('<div class="uo-proof">'))
        self.assertLess(h.index('<div class="uo-proof">'), h.index('<div class="uo-reviewer-status">'))

    def test_U3_proof_without_title_and_title_escaped(self):
        h = self.render(with_part_01(part=':::part 01\n:::banner proof\nA line.\n:::\n:::\n\n'))["html"]
        self.assertNotIn('class="uo-proof__title"', h)
        self.reset_tmp()
        h = self.render(with_part_01(part=':::part 01\n:::banner proof "A <b> & title"\nA line.\n:::\n:::\n\n'))["html"]
        self.assertIn('<p class="uo-proof__title">A &lt;b&gt; &amp; title</p>', h)

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
        nav = re.search(r'<nav class="uo-index__list".*?</nav>', h, flags=re.S).group(0)
        brief = "<p>What this synthetic document tests, and what not to judge.</p>"
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
            (h.replace(brief, brief + '<p><a href="#uo-part-08">x</a></p>'), r"only https:// and http:// links are allowed"),
            (h.replace(brief, brief + svg), r"<svg> is the masthead's wordmark only, in the mark slot"),
            (h.replace(svg, svg + svg), r"exactly one <svg>, the masthead's wordmark, required \(found 2\)"),
            (h.replace(svg, ""), r"exactly one <svg>, the masthead's wordmark, required \(found 0\)"),
            (h.replace('aria-label="ASK"', 'aria-label="Other"'), r"<svg> carries the wordmark's attributes only"),
            (h.replace('role="img" aria-label="ASK">', 'role="img" aria-label="ASK">text'), r"text inside the wordmark"),
            (h.replace('role="img" aria-label="ASK">', 'role="img" aria-label="ASK"><span>x</span>'),
             r"the wordmark holds path elements only"),
            (h.replace(brief, brief + '<p><path d="M0"></path></p>'), r"<path> outside the wordmark"),
            (h.replace(brief, brief + nav), r"<nav> is the section index's list only"),
            (h.replace('aria-label="Sections"', 'aria-label="Parts"'), r"<nav> carries aria-label Sections"),
            (h.replace('<details class="uo-index">', '<details class="uo-index" data-uo-disclose="evidence">'),
             r"the section index is not an authored disclosure"),
            (h.replace(brief, brief + '<details class="uo-index"><summary>x</summary></details>'),
             r"<details class='uo-index'> is the masthead's section index only"),
            (h.replace(brief, brief + '<div class="uo-proof"><p class="uo-proof__flag">x</p></div>'),
             r"<div class='uo-proof'> sits only directly in part 01"),
            (h.replace(brief, brief + '<p class="uo-reviewer-status__flag">x</p>'),
             r"class 'uo-reviewer-status__flag' sits only directly in its <div class='uo-reviewer-status'>"),
            (h.replace('<p class="uo-proof__title">', '<p class="uo-reviewer-status__flag">'),
             r"class 'uo-reviewer-status__flag' sits only directly in its <div class='uo-reviewer-status'>"),
            (h.replace('<li><a href="#uo-part-08">08 unresolved + later-check register</a></li>', ''),
             r"the section index must link every section, in order"),
            (h.replace('<li><a href="#uo-part-02">02 reviewer brief</a></li><li><a href="#uo-part-03">03 decision request</a></li>',
                       '<li><a href="#uo-part-03">03 decision request</a></li><li><a href="#uo-part-02">02 reviewer brief</a></li>'),
             r"the section index must link every section, in order"),
            (h.replace(nav, '<nav class="uo-index__list" aria-label="Sections"><ol></ol></nav>'),
             r"the section index must link every section, in order"),
            (h.replace('<h1>', '<details class="uo-index"><summary>x</summary></details>\n<h1>'),
             r"exactly one section index, <details class='uo-index'>, required \(found 2\)"),
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
        self.assertEqual(rules_with(tpl, ".uo-md .uo-mark")[0]["color"], "var(--uo-mark)")

    def test_U3_banner_and_index_rules_outrank_the_prose_rules(self):
        """The banners and the index sit inside main.uo-md, where MD_CSS's element rules also match them."""
        tpl, md = css_rules(template_css()), css_rules(build.MD_CSS)
        pairs = [(".uo-md .uo-reviewer-status__flag", ".uo-md p"), (".uo-md .uo-proof__flag", ".uo-md p"),
                 (".uo-md .uo-proof__title", ".uo-md p"), (".uo-md .uo-reviewer-status__body p", ".uo-md p"),
                 (".uo-md .uo-proof__body p", ".uo-md p"), (".uo-md .uo-reviewer-status__body strong", ".uo-md strong"),
                 (".uo-md .uo-proof__body strong", ".uo-md strong"), (".uo-md .uo-proof__body em", ".uo-md em"),
                 (".uo-md .uo-index__list ol", ".uo-md ol"), (".uo-md .uo-index__list li", ".uo-md li"),
                 (".uo-md .uo-index__list a", ".uo-md a")]
        for ours, prose in pairs:
            with self.subTest(selector=ours):
                self.assertTrue(rules_with(tpl, ours), ours)
                self.assertTrue(rules_with(md, prose), prose)
                self.assertGreater(specificity(ours), specificity(prose))

    def test_U3_no_rule_hides_or_clips_the_focus_ring(self):
        """The mark slot and the index links keep the browser's own focus ring, measured in U3. No stylesheet
        here declares an outline or `all`, and none clips the index or its ancestors; a change to either
        reopens that measurement."""
        with open(os.path.join(HERE, "_dsa-tokens", "colors_and_type.css"), encoding="utf-8") as f:
            foundation = f.read()
        self.assertEqual(focus_ring_hazards(template_css()) + focus_ring_hazards(build.MD_CSS)
                         + focus_ring_hazards(foundation), [])
        for extra in (".uo-md .uo-index__list a:focus-visible { outline: 2px solid transparent; }",
                      "summary { all: unset; }",
                      ".uo-md .uo-index__mark { outline-color: rgba(0,0,0,0); }",
                      ".uo-md .uo-index { overflow: hidden; }",
                      "main.uo-md { overflow: hidden; }",
                      "A:FOCUS { OUTLINE: none; }",
                      ".uo-md .uo-index__mark:focus { outline: none; }"):
            with self.subTest(extra=extra):
                self.assertEqual(len(focus_ring_hazards(extra)), 1)
        self.assertEqual(focus_ring_hazards(".uo-md pre { overflow-x: auto; } .uo-md { overflow-wrap: anywhere; }"), [])

    def test_U3_manifest_states_the_wordmark_embedding(self):
        m = " ".join(self.render(GUIDED)["manifest_text"].split())
        self.assertIn("The wordmark is embedded as the masthead's inline svg, carrying the file's viewBox and path data "
                      "unchanged, so its embedded text is not byte-equal to the hashed file either.", m)
        dep = build.verify_dependencies()
        self.assertEqual(dep["files"][-1]["path"], "_dsa-tokens/" + build.WORDMARK)


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


def readme_chrome_classes(readme):
    block = re.search(r"```text\nelement +renderer chrome classes\n(.*?)```", readme, flags=re.S)
    if block is None:
        return None
    table = {}
    for line in block.group(1).strip().splitlines():
        m = re.match(r"^([a-z0-9]+) +([a-z_-]+(?: · [a-z_-]+)*)$", line)
        if m is None:
            return None
        table[m.group(1)] = tuple(m.group(2).split(" · "))
    return table


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

    def test_U2_chrome_class_table_equals_readme(self):
        readme = self.readme()
        self.assertEqual(readme_chrome_classes(readme), {k: tuple(v) for k, v in build.CHROME_CLASSES.items()})

    def test_U2_drifted_chrome_class_table_detected(self):
        readme = self.readme()
        drifted = readme.replace("details   uo-details · uo-index\n", "details   uo-details · uo-index · uo-card\n")
        self.assertNotEqual(drifted, readme)
        self.assertNotEqual(readme_chrome_classes(drifted), build.CHROME_CLASSES)

    def test_N75_requirements_pin_equals_constant(self):
        with open(os.path.join(HERE, "requirements.txt"), encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
        self.assertEqual(lines, ["Markdown==%s" % build.MARKDOWN_PIN])


if __name__ == "__main__":
    unittest.main()
