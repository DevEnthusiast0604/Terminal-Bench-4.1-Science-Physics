#!/usr/bin/env python3
"""Task-content rules shared by `tb4 check` (the static `content` gate), `tb4 package` and `tb4 criteria`.

One implementation per rule, so the three places that judge a task's files agree. Before this module
the rules below ran only at `tb4 criteria` (tbench-assess's deterministic tier) or at `tb4 package`,
after the Docker controls and the paid pass@1 had already run on a digest the fix would then change.

  unpinned_from(text)        FROM lines without an @sha256 digest (packaging's dockerfile_findings and
                             tb4-lint.py both call it: one rule, a tag-only FROM is a FAIL everywhere)
  upstream_findings(task)    the registered upstream checks, through run-upstream-checks.sh (the same
                             runner packaging and the criteria tier run)
  hygiene_findings(task)     checks/hygiene.py with the test-data exemptions (hygiene.data_paths)
  task_rules_findings(task)  tbench-assess's task_rules.structure/parameters, when tbench-assess is
                             next to the pack (TB4_ASSESS_DIR, <pack>/tbench-assess, <pack>/../tbench-assess)
  placeholder_findings(task) template placeholders left unfilled (<40-hex-sha>, /app/<repo>, <Task Title>)
  crlf_findings(task)        CRLF line endings in task shell and Python files

The packaging-side rules (FROM digest pins, lockfiles, the task-file email scan, README cite resolution)
live in gates_static.py (dockerfile_findings, email_findings, doc_cite_findings) and are called from both
check_delivery (packaging) and gate_content (tb4 check).

Every finding carries the file, the line when there is one, and the fix. Stdlib only, Python 3.11+.
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACK = HERE.parent
TEMPLATE_DIR = PACK / "template"
sys.path.insert(0, str(HERE))
from gatelib import finding  # noqa: E402
import winbash  # noqa: E402


# Test-data / fixtures folders: a file here holds sample inputs (a config template with CHANGE_ME, an
# intentionally CRLF-terminated file for a dos2unix task, an angle-bracket phrase in sample prose), not the
# task's own template to fill or scripts to run, so the placeholder and CRLF rules do not apply to it.
DATA_DIR_NAMES = {"fixtures", "fixture", "data", "testdata", "test_data", "golden", "samples", "expected", "logs"}


def in_data_dir(rel: str) -> bool:
    parts = rel.replace(os.sep, "/").split("/")[:-1]
    return any(part in DATA_DIR_NAMES for part in parts)


# ------------------------------------------------------------------ base-image pinning (one rule)

FROM_RE = re.compile(r"(?i)^\s*FROM\s+(?:--\S+\s+)*(\S+)(?:\s+AS\s+(\S+))?")
FROM_FIX = "pin it by digest: FROM {img}@sha256:<digest> (the digest: `docker buildx imagetools inspect {img}`)"


def unpinned_from(text: str):
    """[(line, image)] for every FROM whose image has no @sha256 digest. A tag (python:3.12) is not a pin:
    the tag can move under the task. Earlier build stages (FROM builder), scratch and ${ARG} images are
    skipped, exactly as packaging always did."""
    stages, out = set(), []
    lines = text.splitlines()
    for n, ln in enumerate(lines, 1):
        m = FROM_RE.match(ln)
        if not m:
            continue
        img = m.group(1)
        if img.lower() not in stages and img != "scratch" and "$" not in img and "@sha256:" not in img:
            out.append((n, img))
        if m.group(2):
            stages.add(m.group(2).lower())
    return out


def from_fix(img: str) -> str:
    base = img.split("@", 1)[0]
    return FROM_FIX.format(img=base)


# ------------------------------------------------------------------ upstream checks

UPSTREAM_RUNNER = HERE / "run-upstream-checks.sh"


def run_upstream(task: Path, changelog_base: str | None = None, timeout: int = 900):
    """(exit code, output, parsed json or None): run-upstream-checks.sh --json on the task, with the
    changelog baseline packaging uses (TB4_CHANGELOG_BASE, else `new`). The vendored scripts' bare
    `python3` is this interpreter (TB4_PYTHON), which has tomllib, whatever python3 is first on PATH."""
    cl = changelog_base or os.environ.get("TB4_CHANGELOG_BASE") or "new"
    with tempfile.TemporaryDirectory(prefix="tb4-upstream-") as td:
        out = Path(td) / "upstream.json"
        argv = [winbash.bash(), str(UPSTREAM_RUNNER), "--changelog-base", cl, "--json", str(out), str(task)]
        try:
            p = subprocess.run(argv, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=timeout,
                               env=dict(os.environ, PYTHONUTF8="1",
                                        TB4_PYTHON=os.environ.get("TB4_PYTHON") or sys.executable))
        except (OSError, subprocess.TimeoutExpired) as e:
            return 127, str(e), None
        try:
            doc = json.loads(out.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            doc = None
        return p.returncode, (p.stdout or "") + (p.stderr or ""), doc


def upstream_findings(task: Path, changelog_base: str | None = None):
    """(findings, error or None). One finding per registered upstream check that FAILs, with the check's
    own message (the text `tb4 package` prints)."""
    rc, text, doc = run_upstream(task, changelog_base)
    if doc is None:
        tail = " ".join(text.strip().splitlines()[-3:])[:300]
        return [], f"run-upstream-checks.sh wrote no result (exit {rc}): {tail}"
    fs, errors = [], []
    for row in doc.get("checks") or []:
        if not isinstance(row, dict) or row.get("status") == "PASS":
            continue
        if row.get("status") == "ERROR":   # the interpreter could not run the check: not a task finding
            errors.append(f"{row.get('check') or '?'}: {row.get('detail') or 'ERROR'}")
            continue
        script = str(row.get("check") or "?")
        detail = str(row.get("detail") or "").strip()
        m = re.match(r"^(?:FAIL\s+)?([\w./-]+\.(?:py|sh|md|toml|json)|[\w./-]*Dockerfile)(?::(\d+))?\s*:?\s*(.*)$", detail)
        path, line = (m.group(1), int(m.group(2) or 0)) if m else (".", 0)
        fs.append(finding(path, line, f"[upstream {script}] {detail or 'FAIL'} (fix the file, then rerun "
                                      f"`tb4 checks <task>`: the same check `tb4 package` and `tb4 criteria` run)"))
    if errors:
        return fs, (f"{len(errors)} upstream check(s) could not run on this machine's python3 (install Python "
                    f"3.11+ or set TB4_PYTHON; not a task failure): " + "; ".join(errors[:3]))
    return fs, None


# ------------------------------------------------------------------ hygiene

def _hygiene():
    spec = importlib.util.spec_from_file_location("tb4_hygiene", HERE / "hygiene.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


HYGIENE_FIX = {
    "abs-path-users": "use a path relative to the task root (or the container path the task defines)",
    "abs-path-home": "this is your own home directory on this machine: use a path relative to the task root "
                     "(or the container path the task defines, such as /app)",
    "abs-path-win": "use a path relative to the task root (or the container path the task defines)",
    "abs-path-host": "use a path relative to the task root: this is a path on the machine that ran the check",
    "non-english": "write the file in English; test data that pins Unicode behaviour belongs in a data "
                   "folder (fixtures/, data/, ...) or a data file (.json, .csv, ...), which is exempt",
    "non-english-code": "a warning: comments or strings of a code file read as Spanish; translate them when the "
                        "file is the task's own, leave vendored upstream code as it is",
}


def hygiene_findings(task: Path, with_warnings: bool = False):
    """checks/hygiene.py over the task with the same test-data exemptions tbench-assess passes. Rules hygiene
    only warns on (hygiene.WARN_RULES: Spanish comments in a code file) are left out, or returned second with
    WITH_WARNINGS: (findings, warnings)."""
    hy = _hygiene()
    fs, warns = [], []
    for rel, line, rid, detail in hy.scan(str(task), hy.data_paths(str(task))):
        f = finding(rel.replace(os.sep, "/"), line, f"[hygiene {rid}] {detail}: {HYGIENE_FIX.get(rid, '')}")
        (warns if rid in getattr(hy, "WARN_RULES", ()) else fs).append(f)
    return (fs, warns) if with_warnings else fs


# ------------------------------------------------------------------ tbench-assess task rules

def assess_dir() -> Path | None:
    """Where tbench-assess is, in checks/find-assess.sh's order."""
    env = os.environ.get("TB4_ASSESS_DIR")
    cands = [Path(env)] if env else [PACK / "tbench-assess", PACK.parent / "tbench-assess"]
    for c in cands:
        if (c / "src" / "tbench_assess" / "task_rules.py").is_file():
            return c.resolve()
    return None


def _task_rules():
    d = assess_dir()
    if d is None:
        return None
    spec = importlib.util.spec_from_file_location("tb4_task_rules", d / "src" / "tbench_assess" / "task_rules.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def task_rules_findings(task: Path):
    """(findings, warnings, note). tbench-assess's structure and parameters rules (the criteria tier's
    first checks); a rule the release itself breaks is a warning there and a warning here."""
    tr = _task_rules()
    if tr is None:
        return [], [], "tbench-assess not found (TB4_ASSESS_DIR, <pack>/tbench-assess, <pack>/../tbench-assess): " \
                       "its task rules run at `tb4 criteria`"
    fs, warns = [], []
    for group, fn in (("structure", tr.structure), ("parameters", tr.parameters)):
        for rid, title, status, detail in fn(task).rows:
            if status not in ("fail", "warn"):
                continue
            path = "task.toml" if group == "parameters" else "."
            m = re.search(r"\b([\w./-]+\.(?:md|toml|sh|py)|[\w./-]*Dockerfile)\b", detail or title)
            if group == "structure" and m and (task / m.group(1)).exists():
                path = m.group(1)
            f = finding(path, 0, f"[tbench-assess {group}.{rid}] {title}: {detail}")
            (fs if status == "fail" else warns).append(f)
    return fs, warns, None


# ------------------------------------------------------------------ placeholders

# <word>, <two words>, <40-hex-sha>, <one line, what the agent must achieve>. Not HTML comments (<!--),
# closing tags, heredocs (<<), shell redirects (< file), process substitution (<(...)), generics (List<String>)
# or comparisons (a<b and c>d).
PLACEHOLDER_RE = re.compile(r"(?<![\w<])<(?![!/?=%<\s(])([A-Za-z0-9][A-Za-z0-9 _./:,|'+-]{0,160}?)(?<!\s)>(?!\w)")
HTML_TAGS = {"a", "b", "i", "u", "p", "br", "hr", "em", "strong", "code", "pre", "div", "span", "sup", "sub", "img",
             "table", "tr", "td", "th", "li", "ul", "ol", "details", "summary", "kbd", "small", "tt", "del", "ins"}
# Single generic words that a finished task may use as documentation (`usage: tool <path>`); they count as
# unfilled only when the whole template line is still there.
GENERIC = {"path", "file", "arg", "args", "module", "function", "package", "params", "trial", "status", "mode",
           "sha256", "sha256|-", "behavior", "behaviour", "input", "output", "name", "value", "key", "id", "n"}
# A Markdown line that is (or opens) an angle-bracket placeholder paragraph: "<What is intrinsically hard, ..."
MD_BLOCK = re.compile(r"^\s{0,3}(?:#{1,6}\s+)?<(?![!/?])([A-Za-z][^<>]*?)(?:>\s*)?$")
CHANGE_ME = re.compile(r"\bCHANGE_ME\w*")
COMMENT_KINDS = {".sh", ".bash", ".py", ".toml", ".yml", ".yaml", "Dockerfile"}
SCAN_SUFFIX = {".md", ".toml", ".sh", ".bash", ".py", ".json", ".yml", ".yaml", ".txt", ".patch", ""}
_TEMPLATE_CACHE: dict = {}


def _kind(p: Path) -> str:
    return "Dockerfile" if p.name == "Dockerfile" or p.name.endswith(".Dockerfile") else p.suffix.lower()


def _is_comment(kind: str, line: str) -> bool:
    return kind in COMMENT_KINDS and line.lstrip().startswith("#")


def _tokens(line: str):
    for m in PLACEHOLDER_RE.finditer(line):
        tok = m.group(1)
        if tok.lower() in HTML_TAGS or re.fullmatch(r"[\d.,\s]+", tok) or "@" in tok or "://" in tok:
            continue
        yield m.group(0), tok


def template_placeholders(template_dir: Path = TEMPLATE_DIR):
    """(tokens, lines): every placeholder token in the shipped templates, outside comments, and every
    stripped template line that carries one. A task line identical to one of those lines is unfilled."""
    key = str(template_dir)
    if key in _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE[key]
    toks, lines = set(), set()
    for p in sorted(template_dir.rglob("*")) if template_dir.is_dir() else []:
        if not p.is_file():
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        kind = _kind(p)
        for ln in text.splitlines():
            if _is_comment(kind, ln):
                continue
            found = [t for _, t in _tokens(ln)]
            if found:
                toks.update(found)
                lines.add(ln.strip())
    _TEMPLATE_CACHE[key] = (toks, lines)
    return toks, lines


def template_files(template_dir: Path = TEMPLATE_DIR) -> set:
    """Task-relative paths of the files the templates ship (instruction.md, tests/test.sh, ...): relative to each
    template variant's root (the folder holding its task.toml or instruction.md), or to the template folder."""
    key = ("files", str(template_dir))
    if key in _TEMPLATE_CACHE:
        return _TEMPLATE_CACHE[key]
    roots = sorted({p.parent for p in template_dir.rglob("*") if p.name in ("task.toml", "instruction.md")},
                   key=lambda r: -len(r.parts)) if template_dir.is_dir() else []
    out = set()
    for p in sorted(template_dir.rglob("*")) if template_dir.is_dir() else []:
        if p.is_file():
            root = next((r for r in roots if r == p.parent or r in p.parents), template_dir)
            out.add(p.relative_to(root).as_posix())
    _TEMPLATE_CACHE[key] = out
    return out


def _md_code_spans(line: str):
    return [(m.start(), m.end()) for m in re.finditer(r"`[^`]*`", line)]


def placeholder_hits(task: Path, template_dir: Path = TEMPLATE_DIR):
    """[(rel, line, token)] for template placeholders still in the task. A line still identical to a
    template placeholder line always counts; otherwise, in a file the template ships (instruction.md,
    tests/test.sh, ...), a placeholder token of the template counts outside comments (single generic words
    such as <path> only through the identical-line rule), and in Markdown any angle-bracket phrase with a
    space outside code (<Task Title>). A file the template does not ship (a fixture, a usage text: "usage:
    mirror <repo> <domain>") is checked by the identical-line rule and CHANGE_ME only."""
    toks, tlines = template_placeholders(template_dir)
    shipped = template_files(template_dir)
    out = []
    for p in sorted(task.rglob("*")):
        if not p.is_file() or any(s in ("__pycache__", ".git", "node_modules") for s in p.parts):
            continue
        kind = _kind(p)
        if kind not in SCAN_SUFFIX and kind != "Dockerfile":
            continue
        if p.stat().st_size > 2_000_000:
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = p.relative_to(task).as_posix()
        from_template = rel in shipped
        # Fixtures/data hold sample content: a config template's CHANGE_ME, an angle-bracket phrase in sample
        # prose. Those are exempt here. A line still IDENTICAL to a shipped template line (a real leftover copied
        # in) is flagged everywhere, fixtures included, through the `same` rule below.
        fixture = in_data_dir(rel)
        fence = False
        for n, ln in enumerate(text.splitlines(), 1):
            if kind == ".md" and ln.lstrip().startswith("```"):
                fence = not fence
                continue
            if _is_comment(kind, ln) or (kind == ".md" and fence):
                continue
            if not fixture:
                for m in CHANGE_ME.finditer(ln):
                    out.append((rel, n, m.group(0)))
            if kind == ".md" and from_template and not fixture:
                m = MD_BLOCK.match(ln)
                if m and " " in m.group(1).strip() and m.group(1).split()[0].lower() not in HTML_TAGS:
                    text = ln.strip().lstrip("#").strip()
                    out.append((rel, n, text if len(text) <= 60 else text[:60].rstrip() + " ..."))
                    continue
            same = ln.strip() in tlines
            spans = _md_code_spans(ln) if kind == ".md" else []
            for whole, tok in _tokens(ln):
                start = ln.find(whole)
                in_code = any(a <= start < b for a, b in spans)
                if same or (from_template and not fixture and
                            ((tok in toks and tok.lower() not in GENERIC) or
                             (kind == ".md" and not in_code and " " in tok.strip()))):
                    out.append((rel, n, whole))
    return out


def placeholder_findings(task: Path, template_dir: Path = TEMPLATE_DIR):
    by_line = {}
    for rel, n, whole in placeholder_hits(task, template_dir):
        by_line.setdefault((rel, n), []).append(whole)
    out = []
    for (rel, n), ws in by_line.items():
        msg = f"template placeholder {', '.join(dict.fromkeys(ws))} left unfilled: fill the placeholder with the " \
              f"task's real value"
        if rel.startswith("cheat/"):
            msg += f" (or delete {'/'.join(rel.split('/')[:2])}/ if that cheat does not apply to this task)"
        out.append(finding(rel, n, msg))
    return out


# ------------------------------------------------------------------ line endings

CRLF_SUFFIX = {".sh", ".bash", ".py"}


def crlf_findings(task: Path):
    """Task shell and Python files with CRLF line endings: bash reads `set -e\\r` and python3\\r shebangs
    as different commands inside the Linux container, so the task behaves differently from what was
    checked. Typical cause: a Windows checkout with core.autocrlf=true."""
    fs = []
    for p in sorted(task.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in CRLF_SUFFIX or "__pycache__" in p.parts:
            continue
        rel = p.relative_to(task).as_posix()
        if in_data_dir(rel):
            continue  # an intentional CRLF fixture (a dos2unix task's input) is sample data, not a task script
        try:
            data = p.read_bytes()
        except OSError:
            continue
        if b"\r\n" not in data:
            continue
        first = data[:data.index(b"\r\n")].count(b"\n") + 1
        n_crlf = data.count(b"\r\n")
        fs.append(finding(rel, first, f"CRLF line endings ({n_crlf} lines): convert to LF with `dos2unix {rel}` (or `sed -i 's/\\r$//' {rel}`), "
                                      f"and keep them LF with a .gitattributes line `*.sh text eol=lf` / "
                                      f"`*.py text eol=lf`"))
    return fs
