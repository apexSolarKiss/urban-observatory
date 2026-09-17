#!/usr/bin/env python3
"""
Clone-side pin checks for a pinned extraction of tools/artifact-template/.

Run this from a urban-observatory clone's own working tree, never from an
extraction: an extracted build.py cannot vouch for its own descent. The git
objects in the clone are what vouch; this script only asks git. It performs
no fetch. Run `git -C <clone> fetch origin --prune` first (README, "Pinned
extraction and pin checks").

    python3 -B tools/artifact-template/pin_check.py --clone PATH --commit SHA \
        [--extracted DIR] [--descends-from SHA]

Checks, each fail-closed (exit status 1, message on stderr):

- --commit is 40-hex, exists in the clone, and is an ancestor of origin/main;
- with --extracted DIR (the directory holding the extracted build.py), the
  tree digest of DIR equals the digest of a fresh `git archive <commit>
  tools/artifact-template`;
- with --descends-from SHA, SHA is an ancestor of --commit.

Stated limit: this script runs from the clone's mutable working tree. The
git objects vouch, not this file's bytes.
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
import tarfile
import tempfile

TEMPLATE_PATH = "tools/artifact-template"
HEX40 = re.compile(r"^[0-9a-f]{40}$")


class PinCheckError(Exception):
    pass


def tree_digest(root):
    """SHA-256 over lines "<sha256>  ./<relpath>\\n" for every regular file under
    root, paths in byte order. A __pycache__ directory or a .pyc file fails: a
    compiled file can be imported in place of the source it shadows, so it is
    refused rather than skipped. A symlink or any other non-regular entry fails,
    because it cannot be hashed as bytes."""
    root = os.path.abspath(root)
    entries = []
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        for d in list(dirnames):
            full = os.path.join(dirpath, d)
            if os.path.islink(full):
                raise PinCheckError("tree digest: symlink not allowed: %s" % full)
            if d == "__pycache__":
                raise PinCheckError("tree digest: __pycache__ directory not allowed (run with python3 -B): %s" % full)
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if fn.endswith(".pyc"):
                raise PinCheckError("tree digest: compiled Python file not allowed: %s" % full)
            if os.path.islink(full) or not os.path.isfile(full):
                raise PinCheckError("tree digest: not a regular file: %s" % full)
            rel = os.path.relpath(full, root).replace(os.sep, "/")
            with open(full, "rb") as f:
                entries.append((rel.encode("utf-8"), hashlib.sha256(f.read()).hexdigest()))
    entries.sort(key=lambda e: e[0])
    h = hashlib.sha256()
    for rel, sha in entries:
        h.update(sha.encode("ascii") + b"  ./" + rel + b"\n")
    return h.hexdigest()


def _git(clone, *args):
    return subprocess.run(["git", "-C", clone] + list(args), capture_output=True)


def check(clone, commit, extracted=None, descends_from=None):
    if not HEX40.match(commit or ""):
        raise PinCheckError("--commit must be 40 lowercase hex characters: %r" % commit)
    if descends_from is not None and not HEX40.match(descends_from):
        raise PinCheckError("--descends-from must be 40 lowercase hex characters: %r" % descends_from)
    if _git(clone, "rev-parse", "--git-dir").returncode != 0:
        raise PinCheckError("not a git clone: %s" % clone)
    if _git(clone, "cat-file", "-e", commit + "^{commit}").returncode != 0:
        raise PinCheckError("commit does not exist in the clone: %s" % commit)
    if _git(clone, "rev-parse", "--verify", "--quiet", "refs/remotes/origin/main").returncode != 0:
        raise PinCheckError("the clone has no origin/main ref")
    r = _git(clone, "merge-base", "--is-ancestor", commit, "refs/remotes/origin/main")
    if r.returncode == 1:
        raise PinCheckError("commit is not an ancestor of origin/main: %s" % commit)
    if r.returncode != 0:
        raise PinCheckError("git merge-base failed (%d): %s" % (r.returncode, r.stderr.decode("utf-8", "replace").strip()))
    results = ["commit %s exists and is an ancestor of origin/main" % commit]

    if descends_from is not None:
        if _git(clone, "cat-file", "-e", descends_from + "^{commit}").returncode != 0:
            raise PinCheckError("--descends-from commit does not exist in the clone: %s" % descends_from)
        r = _git(clone, "merge-base", "--is-ancestor", descends_from, commit)
        if r.returncode == 1:
            raise PinCheckError("commit %s does not descend from %s" % (commit, descends_from))
        if r.returncode != 0:
            raise PinCheckError("git merge-base failed (%d)" % r.returncode)
        results.append("commit descends from %s" % descends_from)

    if extracted is not None:
        if not os.path.isfile(os.path.join(extracted, "build.py")):
            raise PinCheckError("--extracted must be the directory holding the extracted build.py: %s" % extracted)
        with tempfile.TemporaryDirectory(prefix="uo-pin-check-") as tmp:
            tar_path = os.path.join(tmp, "archive.tar")
            with open(tar_path, "wb") as out:
                r = subprocess.run(["git", "-C", clone, "archive", "--format=tar", commit, TEMPLATE_PATH],
                                   stdout=out, stderr=subprocess.PIPE)
            if r.returncode != 0:
                raise PinCheckError("git archive failed: %s" % r.stderr.decode("utf-8", "replace").strip())
            fresh = os.path.join(tmp, "fresh")
            os.mkdir(fresh)
            with tarfile.open(tar_path) as tf:
                for member in tf.getmembers():
                    if member.name.startswith("/") or ".." in member.name.split("/"):
                        raise PinCheckError("unsafe path in archive: %s" % member.name)
                tf.extractall(fresh)
            expected = tree_digest(os.path.join(fresh, TEMPLATE_PATH))
        actual = tree_digest(extracted)
        if actual != expected:
            raise PinCheckError("extracted tree digest %s does not equal git archive %s digest %s"
                                % (actual, commit, expected))
        results.append("extracted tree digest %s equals git archive of the commit" % actual)
    return results


def main(argv=None):
    ap = argparse.ArgumentParser(description="Clone-side pin checks for a pinned artifact-template extraction.")
    ap.add_argument("--clone", required=True, help="path to a urban-observatory clone (fetched beforehand)")
    ap.add_argument("--commit", required=True, help="the 40-hex commit that was extracted")
    ap.add_argument("--extracted", default=None, help="directory holding the extracted build.py")
    ap.add_argument("--descends-from", default=None, help="a commit --commit must descend from")
    args = ap.parse_args(argv)
    try:
        for line in check(args.clone, args.commit, args.extracted, args.descends_from):
            print("PASS", line)
    except PinCheckError as e:
        print("FAIL", e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
