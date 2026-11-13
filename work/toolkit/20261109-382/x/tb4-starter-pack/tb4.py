#!/usr/bin/env python3
"""tb4: start a Terminal-Bench 4.0 task from the template, check its structure, and package it for the review platform.

  tb4 new <repo-fix|output-task> <slug> [--dir DIR]
        Copy the template to DIR/<slug>, set the task name to terminal-bench/<slug>,
        and list the placeholders left to fill.
  tb4 lint <task>
        The structure check: every file-level rule, with file:line for each problem.
        No Docker, no model, a few seconds. Exit 0 only when nothing fails.
  tb4 package <task> [--out DIR]
        Run the lint and, when nothing fails, zip the task folder: <slug>-<date>.zip, the file you upload
        on the review platform with the task's DAS Task ID. The platform runs everything else in the cloud:
        the controls, the quick check, pass@3 and the full review.
  tb4 --version
        The kit's version.
  tb4 help
        This text.
"""
import argparse
import re
import shlex
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LINT_DIR = HERE / "lint"
sys.path.insert(0, str(LINT_DIR))
TEMPLATES = {"repo-fix": "repo-fix-task", "repo-fix-task": "repo-fix-task", "output-task": "output-task"}
SLUG_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+){0,2}")

def version():
    try:
        return (HERE / "VERSION").read_text(encoding="utf-8").strip()
    except OSError:
        return "unknown"



# ---------------------------------------------------------------- tb4 new

def slug_error(slug):
    """None when SLUG is valid, else the reason it is not."""
    if not isinstance(slug, str) or not slug:
        return "the slug is empty"
    if SLUG_RE.fullmatch(slug):
        return None
    why = []
    if re.search(r"[A-Z]", slug):
        why.append("uppercase letters")
    if "_" in slug:
        why.append("underscores")
    if re.search(r"\s", slug):
        why.append("spaces")
    elif re.search(r"[^A-Za-z0-9_-]", slug):
        why.append("characters other than letters, digits and hyphens")
    if slug.startswith("-") or slug.endswith("-"):
        why.append("a leading or trailing hyphen")
    if "--" in slug:
        why.append("a double hyphen")
    if len([w for w in slug.split("-") if w]) > 3:
        why.append("more than three words")
    if not why:
        why.append("it is not lowercase letters, digits and hyphens")
    return "slug %r has %s; use lowercase letters, digits and hyphens, at most three words" % (slug, ", ".join(why))


def placeholders(task):
    """[(relative path, line number, token)] for every template placeholder still in TASK: the same list
    `tb4 lint` fails on."""
    import content_rules
    return list(content_rules.placeholder_hits(Path(task)))


def cmd_new(a):
    tpl = TEMPLATES.get(a.kind)
    if tpl is None:
        print("tb4 new: the kind must be repo-fix or output-task, not %r" % a.kind, file=sys.stderr)
        return 2
    err = slug_error(a.slug)
    if err:
        print("tb4 new: " + err, file=sys.stderr)
        return 2
    src = HERE / "template" / tpl
    if not src.is_dir():
        print("tb4 new: no template at %s" % src, file=sys.stderr)
        return 3
    dest = Path(a.dir)
    target = dest / a.slug
    if target.exists():
        print("tb4 new: %s already exists; refusing to overwrite it" % target, file=sys.stderr)
        return 2
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    toml = target / "task.toml"
    text = toml.read_text(encoding="utf-8")
    toml.write_text(re.sub(r'(?m)^name = "terminal-bench/[^"]*"', 'name = "terminal-bench/%s"' % a.slug, text, count=1),
                    encoding="utf-8")
    print("created %s from template/%s (task name terminal-bench/%s)" % (target, tpl, a.slug))
    left = placeholders(target)
    if left:
        print("%d placeholder(s) left to fill:" % len(left))
        for rel, n, tok in left:
            print("  %s/%s:%d: %s" % (target, rel, n, tok))
    else:
        print("no placeholders left")
    q = shlex.quote(str(target))
    print("\nnext: fill them, run  tb4 lint %s  until it passes, then  tb4 package %s  and upload the zip on the"
          " review platform" % (q, q))
    return 0




def task_fingerprint(task):
    """The task's content hash (sha256 over every file's path and bytes, Harbor's digest): any edit changes it."""
    import gatelib
    return gatelib.task_digest(task)




# ---------------------------------------------------------------- tb4 lint

LINT_CHECKS = ("placeholders", "requirements", "budget", "readme-claims", "readme-code", "structure", "lint")


def run_lint(task):
    """[(check, status, details, findings, warnings)] for every structure check on TASK."""
    import gates_static
    out = []
    for name in LINT_CHECKS:
        try:
            r = gates_static.GATES[name](Path(task).resolve())
            out.append((name, r.status, r.details, r.findings or [], r.warnings or []))
        except Exception as e:  # a crash of a check is an ERROR, never a pass
            out.append((name, "ERROR", "%s: %s" % (type(e).__name__, e), [], []))
    return out


def lint_report(task, results):
    """(text, ok): the printable result of run_lint."""
    lines, bad = [], 0
    for name, status, details, fs, ws in results:
        lines.append("%-5s %s: %s" % (status, name, details))
        for f in fs:
            lines.append("      %s/%s:%s: %s" % (task, f.get("path", "."), f.get("line", 0), f.get("message", "")))
        for w in ws:
            lines.append("      warning %s/%s:%s: %s" % (task, w.get("path", "."), w.get("line", 0), w.get("message", "")))
        if status == "FAIL-PENDING-DISPOSITION":
            # only findings a person settles (e.g. a README claim backed by a file outside the task): the review
            # decides them, so they never block lint or packaging here
            lines.append("      (left to the review: these findings need a reviewer's decision, not a fix from you)")
        bad += status not in ("PASS", "N/A", "SKIP", "FAIL-PENDING-DISPOSITION")
    lines.append("")
    lines.append("lint: %s" % ("PASS, every structure check passes" if not bad else
                                "%d of %d checks FAIL: fix each file:line above and run tb4 lint again" % (bad, len(results))))
    return "\n".join(lines), not bad


def cmd_lint(a):
    task = Path(a.task)
    if not (task / "task.toml").is_file():
        print("tb4 lint: no task.toml in %s" % task, file=sys.stderr)
        return 2
    text, ok = lint_report(task, run_lint(task))
    print(text)
    return 0 if ok else 1




# ---------------------------------------------------------------- tb4 package

def cmd_package(a):
    """The zip you upload: the task folder alone, once tb4 lint passes. No review report, no runs, no attempts:
    the platform makes them in the cloud (controls, quick check, pass@3, full review)."""
    import datetime
    task = Path(a.task)
    if not (task / "task.toml").is_file():
        print("tb4 package: no task.toml in %s" % task, file=sys.stderr)
        return 2
    task = task.resolve()
    slug = task.name
    err = slug_error(slug)
    if err:
        print("tb4 package: the task folder's name is its slug: " + err, file=sys.stderr)
        return 2
    text, ok = lint_report(task, run_lint(task))
    if not ok:
        print(text)
        print("\nREFUSING TO PACKAGE %s: tb4 lint fails. Fix each file:line above and run tb4 package again." % slug,
              file=sys.stderr)
        return 1
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    z = out / ("%s-%s.zip" % (slug, datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")))
    if z.exists():
        print("tb4 package: %s already exists: move it away (or remove it) and package again" % z, file=sys.stderr)
        return 1
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        copy = Path(td) / slug
        dropped = _copytree(task, copy)
        write_zip(copy, z)
    if dropped:
        print("note: %d symbolic link(s) were left out of the zip (it holds files only)" % dropped)
    print("lint: PASS")
    print("task digest: %s" % task_fingerprint(task))
    print("zip: %s" % z)
    print("\nnext: upload it on the review platform with the task's DAS Task ID. The quick check runs there;"
          " a pass starts pass@3, and its P3 ID goes in the DAS task.")
    return 0


def _copytree(src, dst):
    shutil.copytree(src, dst, symlinks=True, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
    links = [p for p in Path(dst).rglob("*") if p.is_symlink()]
    for p in links:            # a delivery holds files only
        p.unlink()
    return len(links)


def write_zip(folder, zpath):
    import zipfile
    folder = Path(folder)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(folder.rglob("*")):
            if p.is_file() and not p.is_symlink():
                info = zipfile.ZipInfo.from_file(p, (folder.name / p.relative_to(folder)).as_posix())
                info.compress_type = zipfile.ZIP_DEFLATED
                with p.open("rb") as fh:
                    z.writestr(info, fh.read())



# ---------------------------------------------------------------- CLI

COMMANDS = ("new", "lint", "package")
GONE = {"attempt": "model attempts run on the review platform now (the quick check, pass@3 and the full review): "
                   "upload the zip from  tb4 package"}


def parser():
    ap = argparse.ArgumentParser(prog="tb4", add_help=False, allow_abbrev=False)
    sub = ap.add_subparsers(dest="cmd")
    n = sub.add_parser("new", prog="tb4 new", allow_abbrev=False)
    n.add_argument("kind", help="repo-fix or output-task")
    n.add_argument("slug", help="lowercase letters, digits and hyphens, at most three words")
    n.add_argument("--dir", default=".", help="where to create the task folder (default: here)")
    li = sub.add_parser("lint", prog="tb4 lint", allow_abbrev=False)
    li.add_argument("task", help="the task folder")
    pk = sub.add_parser("package", prog="tb4 package", allow_abbrev=False)
    pk.add_argument("task", help="the task folder")
    pk.add_argument("--out", default="deliveries", help="where the zip goes (default: ./deliveries)")
    return ap


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("help", "-h", "--help"):
        print(__doc__.strip())
        return 0
    if argv[0] in ("--version", "-V", "version"):
        print("tb4 %s" % version())
        return 0
    if argv[0] in GONE:
        print("tb4 %s: %s" % (argv[0], GONE[argv[0]]), file=sys.stderr)
        return 2
    if argv[0] not in COMMANDS:
        print("tb4: unknown command %r\n" % argv[0], file=sys.stderr)
        print(__doc__.strip(), file=sys.stderr)
        return 2
    a = parser().parse_args(argv)
    if a.cmd == "new":
        return cmd_new(a)
    if a.cmd == "lint":
        return cmd_lint(a)
    return cmd_package(a)


if __name__ == "__main__":
    sys.exit(main())
