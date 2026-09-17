"""Tests for pin_check.py against a throwaway git repository the test creates in
a temporary directory. No real clone is touched.

Run from the repo root:
    python3 -B -m unittest discover -s tools/artifact-template/tests
"""
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
import pin_check  # noqa: E402

GIT = ["git", "-c", "user.name=pin-check-test", "-c", "user.email=pin-check-test@invalid",
       "-c", "commit.gpgsign=false", "-c", "init.defaultBranch=main"]


def git(cwd, *args):
    r = subprocess.run(GIT + ["-C", cwd] + list(args), capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError("git %s failed: %s" % (" ".join(args), r.stderr))
    return r.stdout.strip()


class PinCheck(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="uo-pin-check-test-")
        origin = os.path.join(cls.tmp, "origin.git")
        clone = os.path.join(cls.tmp, "clone")
        subprocess.run(GIT + ["init", "-q", "--bare", origin], check=True)
        subprocess.run(GIT + ["init", "-q", clone], check=True)
        git(clone, "remote", "add", "origin", origin)
        tdir = os.path.join(clone, "tools", "artifact-template")
        os.makedirs(tdir)

        def commit(name, text):
            with open(os.path.join(tdir, name), "w") as f:
                f.write(text)
            git(clone, "add", "-A")
            git(clone, "commit", "-q", "-m", name + " " + text[:8])
            return git(clone, "rev-parse", "HEAD")

        commit("build.py", "print('synthetic A')\n")
        cls.a = git(clone, "rev-parse", "HEAD")
        cls.b = commit("README.md", "synthetic B\n")
        git(clone, "push", "-q", "origin", "HEAD:refs/heads/main")
        git(clone, "checkout", "-q", "-b", "side", cls.a)
        cls.c = commit("side.txt", "synthetic side commit C\n")
        git(clone, "push", "-q", "origin", "HEAD:refs/heads/side")
        git(clone, "fetch", "-q", "origin", "--prune")
        cls.clone = clone

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def extract(self, commit):
        dest = tempfile.mkdtemp(prefix="extract-", dir=self.tmp)
        tar = os.path.join(dest, "a.tar")
        with open(tar, "wb") as f:
            subprocess.run(["git", "-C", self.clone, "archive", "--format=tar", commit, "tools/artifact-template"],
                           stdout=f, check=True)
        with tarfile.open(tar) as tf:
            tf.extractall(dest)
        os.unlink(tar)
        return os.path.join(dest, "tools", "artifact-template")

    def assert_fails(self, pattern, **kw):
        with self.assertRaises(pin_check.PinCheckError) as cm:
            pin_check.check(self.clone, **kw)
        self.assertRegex(str(cm.exception), pattern)

    def test_N73_clean_extraction_passes(self):
        results = pin_check.check(self.clone, self.b, extracted=self.extract(self.b), descends_from=self.a)
        self.assertEqual(len(results), 3)
        self.assertIn("ancestor of origin/main", results[0])
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(pin_check.main(["--clone", self.clone, "--commit", self.b]), 0)
        self.assertIn("PASS commit", out.getvalue())

    def test_older_ancestor_passes(self):
        pin_check.check(self.clone, self.a)

    def test_N69_non_ancestor_commit_fails(self):
        self.assert_fails(r"commit is not an ancestor of origin/main: " + self.c, commit=self.c)
        err = StringIO()
        with redirect_stderr(err):
            self.assertEqual(pin_check.main(["--clone", self.clone, "--commit", self.c]), 1)
        self.assertIn("FAIL commit is not an ancestor of origin/main", err.getvalue())

    def test_N70_nonexistent_commit_fails(self):
        self.assert_fails(r"commit does not exist in the clone", commit="ab" * 20)

    def test_N70b_short_commit_fails(self):
        self.assert_fails(r"--commit must be 40 lowercase hex", commit=self.b[:7])

    def test_N71_tampered_extraction_fails(self):
        ext = self.extract(self.b)
        with open(os.path.join(ext, "build.py"), "a") as f:
            f.write("# tampered\n")
        self.assert_fails(r"extracted tree digest [0-9a-f]{64} does not equal git archive", commit=self.b, extracted=ext)

    def test_N71b_extra_file_in_extraction_fails(self):
        ext = self.extract(self.b)
        with open(os.path.join(ext, "extra.txt"), "w") as f:
            f.write("x\n")
        self.assert_fails(r"does not equal git archive", commit=self.b, extracted=ext)

    def test_N71c_extraction_of_other_commit_fails(self):
        self.assert_fails(r"does not equal git archive", commit=self.b, extracted=self.extract(self.a))

    def test_F6_pycache_in_extraction_fails(self):
        ext = self.extract(self.b)
        os.makedirs(os.path.join(ext, "__pycache__"))
        with open(os.path.join(ext, "__pycache__", "build.cpython-311.pyc"), "wb") as f:
            f.write(b"\x00")
        self.assert_fails(r"tree digest: __pycache__ directory not allowed", commit=self.b, extracted=ext)

    def test_F6_empty_pycache_in_extraction_fails(self):
        ext = self.extract(self.b)
        os.makedirs(os.path.join(ext, "sub", "__pycache__"))
        self.assert_fails(r"tree digest: __pycache__ directory not allowed", commit=self.b, extracted=ext)

    def test_F6_loose_pyc_in_extraction_fails(self):
        ext = self.extract(self.b)
        with open(os.path.join(ext, "pin_check.pyc"), "wb") as f:
            f.write(b"\x00")
        self.assert_fails(r"tree digest: compiled Python file not allowed", commit=self.b, extracted=ext)
        err = StringIO()
        with redirect_stderr(err):
            self.assertEqual(pin_check.main(["--clone", self.clone, "--commit", self.b, "--extracted", ext]), 1)
        self.assertIn("FAIL tree digest: compiled Python file not allowed", err.getvalue())

    def test_N72_descends_from_non_ancestor_fails(self):
        self.assert_fails(r"commit %s does not descend from %s" % (self.b, self.c), commit=self.b, descends_from=self.c)

    def test_no_fetch_performed(self):
        before = git(self.clone, "rev-parse", "refs/remotes/origin/main")
        fetch_head = os.path.join(self.clone, ".git", "FETCH_HEAD")
        mtime = os.path.getmtime(fetch_head)
        pin_check.check(self.clone, self.b, extracted=self.extract(self.b))
        self.assertEqual(git(self.clone, "rev-parse", "refs/remotes/origin/main"), before)
        self.assertEqual(os.path.getmtime(fetch_head), mtime)


if __name__ == "__main__":
    unittest.main()
