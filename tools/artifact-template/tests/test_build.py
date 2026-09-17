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
        self.assertIn('<section data-uo-part="03">', h)
        self.assertIn('<div data-uo-role="question" data-uo-central="true">', h)
        self.assertIn('<div data-uo-role="finding">', h)
        for cls in ("question-detail", "evidence", "provenance"):
            self.assertIn('<details data-uo-disclose="%s"><summary>' % cls, h)
        self.assertEqual(r["counts"], {"questions": 2, "findings": 1, "disclosures": 3, "tables": 1})

    def test_confirmation_baseline_generates_01_and_10(self):
        r = self.render(CONFIRMATION)
        self.assertEqual(r["parts"], ["01", "02", "07", "10"])
        h = r["html"]
        self.assertIn('<section data-uo-part="01">\n<div class="uo-status-rail">', h)
        self.assertRegex(h, r'<section data-uo-part="10">\n<footer class="uo-foot">')

    def test_all_ten_parts_render_in_order(self):
        src = GUIDED
        src = mutate(src, ":::part 06\n", ":::part 05\nSynthetic finding index.\n:::\n\n:::part 06\n")
        src = mutate(src, ":::part 08\n", ":::part 06\n:::finding\nA second finding.\n:::\n:::\n\n"
                                             ":::part 07\nSynthetic prior-position delta.\n:::\n\n:::part 08\n")
        src = mutate(src, ":::part 10\n", ":::part 09\nSynthetic response format.\n:::\n\n:::part 10\n")
        r = self.render(src)
        self.assertEqual(r["parts"], ["01", "02", "03", "04", "05", "06", "06", "07", "08", "09", "10"])
        self.assertEqual(re.findall(r'<section data-uo-part="(\d\d)">', r["html"]), r["parts"])
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
        roles = re.findall(r'<t[hd] data-uo-cell="([a-z]+)">', h)
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
        self.assertIn('<section data-uo-part="02" class="uo-local-wide-a">', h)
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
        self.assertIn('<td data-uo-cell="text">a | b and <code>x|y</code></td>', h)


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

    def test_N75_requirements_pin_equals_constant(self):
        with open(os.path.join(HERE, "requirements.txt"), encoding="utf-8") as f:
            lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
        self.assertEqual(lines, ["Markdown==%s" % build.MARKDOWN_PIN])


if __name__ == "__main__":
    unittest.main()
