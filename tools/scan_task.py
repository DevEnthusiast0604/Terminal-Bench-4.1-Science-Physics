"""Byte-level pre-package scan of a task folder (not a task file, never shipped).

    python -I -B tools/scan_task.py tasks/active/<slug>

Reports every file holding a CR byte (lint fails CRLF scripts, and grep -I can miss CRs), a host path or
this machine's folder names, or an email address outside task.toml whose domain is not a reserved one
(example.com/.org/.net, *.test, *.example, *.invalid), plus any symlink (tb4 package drops them) and any
__pycache__ or .pytest_cache folder. Exit status 1 when anything is found. One exception: task.toml's own
author_email on the README's `- **Author:**` line, which TB 4.1 requires as `Name (email)` (user, 2026-11-10).
"""
import pathlib
import re
import sys
import tomllib

HOST = [b"c:\\", b"c:/", b"/c/users", b"administrator", b"appdata", b"tango-arunufo", b".supertasker-profile"]
EMAIL = re.compile(rb"[A-Za-z0-9._%+-]+@([A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,})")
RESERVED = re.compile(rb"(^|\.)(example\.(com|org|net)|[a-z0-9-]+\.(test|example|invalid))$|(^|\.)(test|example|invalid)$")


def author_emails(root):
    """task.toml's author_email values, the only addresses the README's Author line may hold."""
    try:
        md = tomllib.loads((root / "task.toml").read_text(encoding="utf-8")).get("metadata", {})
    except (OSError, tomllib.TOMLDecodeError):
        return set()
    v = md.get("author_email", [])
    return {e.encode() for e in ([v] if isinstance(v, str) else v)}


def on_author_line(data, pos):
    return data[data.rfind(b"\n", 0, pos) + 1:].startswith(b"- **Author:** ")


def scan(root):
    problems, n_files = [], 0
    allowed = author_emails(root)
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if p.is_symlink():
            problems.append(("symlink", rel))
            continue
        if p.is_dir():
            if p.name in ("__pycache__", ".pytest_cache"):
                problems.append(("cache folder", rel))
            continue
        n_files += 1
        data = p.read_bytes()
        if b"\r" in data:
            problems.append(("CR byte", rel))
        low = data.lower()
        for pat in HOST:
            if pat in low:
                problems.append(("host text %r" % pat.decode(), rel))
        if p.name != "task.toml":
            for m in EMAIL.finditer(data):
                if RESERVED.search(m.group(1).lower()):
                    continue
                if rel == "README.md" and m.group(0) in allowed and on_author_line(data, m.start()):
                    continue
                problems.append(("email %s" % m.group(0).decode(errors="replace"), rel))
    return n_files, problems


def main(path):
    n_files, problems = scan(pathlib.Path(path))
    print("files scanned: %d" % n_files)
    for kind, rel in problems:
        print("  %s: %s" % (kind, rel))
    print("problems: %d" % len(problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
