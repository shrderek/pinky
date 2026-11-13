#!/usr/bin/env python3
"""Checks that an unpacked WebDriverAgent tree is the release Pinky builds.

Pinky's own check (internal/driver/ios/simwda.go, unpackSource/treeHash) hashes
the files, not the archive, so a different compression or top folder name does
not change it. One line per file, sorted by path: "<mode> <sha256> <path>".

Usage: wda-source-check.py <source tree> <expected tree hash>
"""
import hashlib
import os
import sys

FILES = ("644", "755")


def tree_hash(root):
    entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        for name in sorted(filenames):
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            if rel in (".", "") or rel.startswith("../"):
                sys.exit("unexpected path %r" % rel)
            digest = hashlib.sha256()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(1 << 20), b""):
                    digest.update(chunk)
            mode = "755" if os.stat(path).st_mode & 0o111 else "644"
            entries.append((rel, mode, digest.hexdigest()))
    if not entries:
        sys.exit("no files under %s" % root)
    h = hashlib.sha256()
    for rel, mode, digest in sorted(entries):
        h.update(("%s %s %s\n" % (mode, digest, rel)).encode())
    return h.hexdigest(), len(entries)


def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    root, want = sys.argv[1], sys.argv[2].strip().lower()
    got, count = tree_hash(root)
    print("%d files, treeHash %s" % (count, got))
    if got != want:
        sys.exit("this is not the WebDriverAgent release Pinky builds: want %s" % want)
    print("source matches the release")


if __name__ == "__main__":
    main()
