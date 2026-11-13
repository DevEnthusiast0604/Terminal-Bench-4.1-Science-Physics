#!/usr/bin/env python3
"""Static gates: checks that read the task (or its delivery) and never run it.

usage:
  gates_static.py <gate> <task-dir> [--gates-dir D] [--json]
  gates_static.py packaging <delivery-dir|delivery.zip|dir-of-zips> [--task T] [--gates-dir D] [--json]

gates:
  requirements   tests/requirements.json binds every instruction constraint to a test, and every test to one
  budget         tests/budget.json caps add up under [verifier].timeout_sec; literal timeouts agree with it; every
                 time or size limit the instruction or budget.json states is enforced (a timeout, ulimit, setrlimit
                 or a failing comparison fed by it), and one that is only mentioned under tests/ is a warning
  readme-claims  measured claims in README.md cite a file that exists
  readme-code    paths, scripts and name() identifiers in README.md exist; solution claims match solution/
  structure      the v2 file set: requirements, budget, /app/submission artifact, collect hook, locked /tests
                 plus verifier-code rules: X2.5 missing input read as empty, X3.2 pre-launch-only deadline
                 or uncounted kill grace, X3.4 captured output sliced to a suffix or prefix, X3.3 a bounded
                 read never checked for more data, X3.1 a reward path that leaves no ctrf.json, X4.2
                 submitted code built or run as root, PROC.4h9 subset key checks under an exact contract,
                 PROC.4h10 offset-tolerant parsing of Z timestamps
                 plus CRLF line endings in task shell and Python files
  lint           wraps checks/tb4-lint.py and records its FAIL rows
  placeholders   template placeholders left unfilled (<40-hex-sha>, /app/<repo>, <Task Title>, CHANGE_ME)
  content        the task-content rules `tb4 package` and `tb4 criteria` apply (content_rules.py): FROM digest
                 pins, lockfiles, D1 a Dockerfile RUN that masks a failed build, the task-file email scan,
                 README cite resolution, C1 signatures claimed with no verifier, C2 a no-survivor claim over a
                 killpg-only cleanup, the registered upstream checks, hygiene and tbench-assess's task rules
  grader-hygiene the grader code that reads the deliverable or emits observations (grader_hygiene.py): B1 duplicate
                 JSON keys accepted, B2 a float tolerance that fails at its own boundary (shown on a value), B3 a
                 CSV split on commas, B4 an object's key order the instruction does not state, B5 a test run's exit
                 status ignored, B6 a converting default= (str, float, list, ...) on what the code under test
                 returned, B7 a project manifest in test_globs, B8 cases or inputs not isolated, B9 (advisory) lossy
                 emitter idioms, B10 an item no pattern reads dropped, B11 a stated stream cap read from the final
                 file size, B12 an unchanged check that hashes no file mode, B13 an answer with booleans decided by
                 ==, B14 the whole output folder under one cap against an only-read promise, B15 the call's own
                 limit used as the case process deadline, B16 a protected agent-side path nothing records. Template
                 v2 code and the copied JSON loader (B1) are mechanical FAILs (B10-B13 and B15 on template lines
                 are advisory warnings), fixed by
                 `tb4 upgrade-verifier` and tb4judge.load_json; the task's own findings FAIL on template v2.1 and
                 are FAIL-PENDING-DISPOSITION on v2 when they are the only ones (a reviewer fixes or disposes each)
  spec-alignment what the instruction says against what the grader enforces (spec_checks.py): M1 an optional key
                 the judge requires, L2 a time cap shorter than the stated time, D1 a per-call deadline measured
                 around the whole case process, T1 a speed timer that leaves out the submission's setup, E1 booleans
                 judged with == for a repository that is not Python, E2 part of the repository's tests run while
                 the instruction says they keep passing; advisory: M2 alternative forms, L1 an unstated resource cap,
                 L3 an unstated case timeout, L4 an unstated archive cap; findings are FAIL-PENDING-DISPOSITION
  all            every task-level gate above
  packaging      delivery mode: one task.toml at any depth, safe zip entries, one zip per task id, attempt
                 counts, emails, cited paths

  gates_static.py ship-provenance <provenance-dir> <dest-dir>
                 package time: copy provenance by allowlist (PROVENANCE.json, NOVELTY.md, its named generators
                 and seeds, provenance-manifest.txt entries), never a nested task tree

Every gate writes <gates-dir>/<gate>.json through gatelib.write_gate, with
path:line findings. Exit 0 only when the gate (or every gate, for `all`) is
PASS; 1 on FAIL or FAIL-PENDING-DISPOSITION; 2 on ERROR. A gate that cannot run is ERROR, never PASS.
readme-claims and readme-code count only evidence inside the task root; a claim, path or generator that
resolves only in the wrapper (evidence/, provenance/) is a `receipt-only` finding that needs a disposition.

Stdlib only, Python 3.11+ (tomllib).
"""
from __future__ import annotations

import argparse
import ast
import fnmatch
import importlib.util
import json
import posixpath
import re
import stat
import sys
import tempfile
import tomllib
import unicodedata
import zipfile
from pathlib import Path, PurePosixPath

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import gatelib  # noqa: E402
import content_rules  # noqa: E402
from gatelib import finding  # noqa: E402

TASK_GATES = ("placeholders", "requirements", "budget", "readme-claims", "readme-code", "structure", "lint", "content",
              "grader-hygiene", "spec-alignment")
SUBMISSION = "/app/submission"
TEXT_EXT = {".py", ".sh", ".go", ".rs", ".js", ".mjs", ".cjs", ".ts", ".json", ".toml", ".md", ".txt",
            ".yaml", ".yml", ".cfg", ".ini", ".c", ".h", ".cpp", ".java", ".rb", ".php", ".patch", ".diff",
            ".csv", ".xml", ".html", ".sql", ".mod", ".sum", ""}
CODE_EXT = {".py", ".sh", ".go", ".rs", ".js", ".mjs", ".cjs", ".ts", ".c", ".h", ".cpp", ".java", ".rb",
            ".php", ".patch", ".diff", ".toml", ".mod", ".sum", ".lock"}
PERSONAL_MAIL = re.compile(r"@(gmail|googlemail|hotmail|outlook|live|yahoo|icloud|me|aol|proton|protonmail|gmx|"
                           r"yandex|mail)\.[a-z.]+$", re.I)
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
# RFC 2606 / RFC 6761 reserved names: synthetic data uses these, and no mail is ever delivered to them.
RESERVED_MAIL = re.compile(r"@(?:[a-z0-9-]+\.)*(?:example\.(?:com|org|net)|[a-z0-9-]+\.(?:test|example|invalid|localhost)"
                           r"|test|example|invalid|localhost)$", re.I)


def mask_email(e: str) -> str:
    """j***@gmail.com: enough to find the address, not enough to repeat it."""
    local, _, dom = e.partition("@")
    return (local[:1] + "***@" + dom) if local else e


def own_emails() -> set:
    """The operator's own addresses: $TB4_ATTEMPTER_EMAIL and git user.email. They never ship."""
    import os
    out = {x.strip().lower() for x in os.environ.get("TB4_ATTEMPTER_EMAIL", "").split(",") if "@" in x}
    try:
        import subprocess
        r = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and "@" in r.stdout:
            out.add(r.stdout.strip().lower())
    except Exception:
        pass
    return out


class GateResult:
    def __init__(self, status, details, findings=None, warnings=None, evidence=None, extra=None):
        self.status, self.details = status, details
        self.findings = list(findings or [])
        self.warnings = list(warnings or [])
        self.evidence = list(evidence or [])
        self.extra = dict(extra or {})


# ------------------------------------------------------------------ helpers

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace")


def norm(s: str) -> str:
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip()


def load_toml(task: Path) -> dict:
    return tomllib.loads(read(task / "task.toml"))


def artifact_sources(d: dict) -> list[str]:
    out = []
    for a in d.get("artifacts", []) or []:
        if isinstance(a, str):
            out.append(a)
        elif isinstance(a, dict) and "source" in a:
            out.append(str(a["source"]))
    return out


def is_v2(task: Path, d: dict | None = None) -> bool:
    if (task / "tests/requirements.json").is_file() or (task / "tests/budget.json").is_file():
        return True
    try:
        d = d if d is not None else load_toml(task)
    except Exception:
        return False
    return artifact_sources(d) == [SUBMISSION]


def line_of(text: str, needle: str, default: int = 0) -> int:
    i = text.find(needle)
    return text[:i].count("\n") + 1 if i >= 0 else default


def task_text_files(task: Path, subdirs=("environment", "solution", "tests"), skip_readme=True):
    files = []
    for f in ("task.toml", "instruction.md") + (() if skip_readme else ("README.md",)):
        if (task / f).is_file():
            files.append(task / f)
    for sd in subdirs:
        base = task / sd
        if base.is_dir():
            for p in sorted(base.rglob("*")):
                if p.is_file() and p.suffix.lower() in TEXT_EXT and p.stat().st_size < 4_000_000:
                    files.append(p)
    return files


def strip_fences(text: str) -> str:
    """Blank fenced code blocks and HTML comments, keeping line numbers."""
    out, fence = [], False
    for ln in text.splitlines():
        if ln.lstrip().startswith("```"):
            fence = not fence
            out.append("")
            continue
        out.append("" if fence else ln)
    t = "\n".join(out)
    return re.sub(r"<!--.*?-->", lambda m: "\n" * m.group().count("\n"), t, flags=re.S)


def paragraphs(text: str):
    """(start_line, text) for blank-line separated blocks; each table row is its own block."""
    blocks, cur, start = [], [], 0
    for n, ln in enumerate(text.splitlines(), 1):
        if ln.strip().startswith("|"):
            if cur:
                blocks.append((start, "\n".join(cur))); cur = []
            blocks.append((n, ln))
            continue
        if ln.strip():
            if not cur:
                start = n
            cur.append(ln)
        elif cur:
            blocks.append((start, "\n".join(cur))); cur = []
    if cur:
        blocks.append((start, "\n".join(cur)))
    return blocks


def sections(text: str):
    """Map line number -> lower-cased '## ' heading it sits under."""
    cur, out = "", {}
    for n, ln in enumerate(text.splitlines(), 1):
        m = re.match(r"^#{1,6}\s+(.*)$", ln)
        if m:
            cur = m.group(1).strip().lower()
        out[n] = cur
    return out


DELIVERY_OVERRIDE: list = []   # set by --delivery: the full extracted delivery the task gates may read


def _is_delivery(p: Path) -> bool:
    return (p / "DELIVERY.md").is_file() or (p / "MANIFEST.json").is_file()


def resolve_delivery(d: Path) -> Path | None:
    """The delivery root at d, or its single subdirectory that is one (an unzipped zip has one top folder)."""
    d = Path(d).resolve()
    if _is_delivery(d):
        return d
    subs = [x for x in d.iterdir() if x.is_dir() and _is_delivery(x)] if d.is_dir() else []
    return subs[0] if len(subs) == 1 else None


def delivery_root(task: Path) -> Path | None:
    if DELIVERY_OVERRIDE:
        return DELIVERY_OVERRIDE[0]
    p = task.parent
    return p if _is_delivery(p) else None


def relocated_in_delivery(s: str):
    """Where a task-relative cite may have been relocated when the delivery was assembled, as delivery-root-
    relative posix paths to try besides the literal one. The packager (package-delivery.sh) and finalize.build
    move a task's cheat/ to evidence/cheat/ and _provenance/ to a flat provenance/, so a README/REVISION
    reference to the task-relative path still resolves against its shipped location (matches llm_gates.Checker.
    resolve). A path that exists in neither the literal nor the relocated place is still dangling."""
    s = s.lstrip("./").rstrip("/")
    out = []
    if s.startswith("cheat/"):
        out.append("evidence/" + s)                                  # cheat/<rest> -> evidence/cheat/<rest>
    elif s.startswith("_provenance/"):
        rest = s[len("_provenance/"):]
        out.append("provenance/" + rest)                             # _provenance/<rest> -> provenance/<rest>
        if "/" in rest:
            out.append("provenance/" + rest.split("/", 1)[1])        # _provenance/<slug>/<f> -> provenance/<f>
    return out


# ------------------------------------------------------------------ requirements

TRAILER_RE = re.compile(r"^(You have \d+ seconds to complete this task|Do not cheat by using online)")
# A sentence is a requirement when it carries an obligation (a modal or a bound) or states a property of
# the deliverable declaratively ("`cuts` lists every interruption", "holds UTC", "standard library").
# Background prose ("The console logged every case to one file") has neither and stays out.
CONSTRAINT_RE = re.compile(r"\b(must|should|never|only if|exactly|at most|at least|within|may not|cannot|shall|"
                           r"has to|have to|needs? to)\b|\b(no|nothing|none)\b[^.;]{0,80}?\bmay\b", re.I)
# The obligations that make an opening-paragraph sentence a requirement whatever the paragraph around it says.
STRONG_OBLIGATION = re.compile(r"\b(must|never|only if|exactly|at most|at least|may not|shall)\b|"
                               r"\b(no|nothing|none)\b[^.;]{0,80}?\bmay\b", re.I)
SPEC_VERB = r"(?:is|are|has|have|holds?|lists?|maps?|gives?|names?|contains?|keeps?|returns?|prints?|stays?|" \
            r"counts?|behaves?|comes?|goes|does not|do not|is not|are not)"
DECLARATIVE_RES = [
    re.compile(r"^(?:[\w\s,]{0,30}?)`[^`]+`(?:\s*(?:,|and|or)\s*`[^`]+`)*\s+" + SPEC_VERB + r"\b"),  # `field` is/lists ...
    re.compile(r"\b(standard library|no network|without (?:a |any )?network|network access|no internet|offline|"
               r"read-only|no other package)\b", re.I),
    re.compile(r"\b(UTC|ISO 8601|time zone|timezone)\b"),
    re.compile(r"\bevery\s+(?:\d+|one|two|three|five|ten|fifteen|thirty|sixty)\s+(?:seconds?|minutes?|hours?|days?)\b",
               re.I),
    re.compile(r"\b\d[\d,.]*\s*(?:ms|s|seconds?|minutes?|hours?|MB|GB|KB|°C|degrees?|nm|nautical miles?|m2|m²|"
               r"percent|%|decimals?|bits?|bytes?)(?![\w])", re.I),
    re.compile(r"\b(several|a few)\s+(seconds|minutes|hours)\b|\b(?:are|is) (?:integers?|strings?|null|floats?|"
               r"numbers?|lowercase|uppercase|sorted)\b|\bin (?:degrees|decimal degrees|celsius|metres|meters|seconds|"
               r"minutes|hours|nautical miles|percent)\b", re.I),
    re.compile(r"\b(the same|as it was|as they are|unchanged|as today|byte for byte|in (?:the same|any) order|"
               r"in time order|in input order|one (?:row|entry|line|file|object) (?:per|for|every)|both|the only)\b", re.I),
    re.compile(r"\b(?:holds?|applies|hold) (?:for|on|under|wherever)\b|\b(?:is|are) (?:not )?(?:graded|kept|collected|"
               r"evaluated|compared|read|transferred)\b|\bcompares?\b|\bdo(?:es)? not (?:move|change)\b", re.I),
    re.compile(r"^(?:(?:please|now|then|also)\s+)?(?:write|add|make|keep|print|return|move|recover|attribute|rewrite|"
               r"work out|output|produce|emit|use|fix|implement|report|convert|record|list)\b", re.I),
    re.compile(r"[;:]\s+(?:write|use|keep|return|print)\b", re.I),
    re.compile(r"^(?:the|this|its|each|every)\s+(?:subset|format|output|deliverable|result|file|table|header|column|row|"
               r"report|schema|command|decoder|interpreter|program|resolver|tool)s?\b[^.;]*\b" + SPEC_VERB + r"\b", re.I),
]
WEAK_RES = DECLARATIVE_RES[2:8]   # UTC, units, "the same"...: not enough on their own in the opening paragraph


SCOPE_LINE = re.compile(r"^(?:fix|edit|change|modify|patch|work in|the fix (?:goes|lives) in)\s+`?/[\w./-]+`?\s*:?\s*"
                        r"(?:`?[\w./-]+`?(?:,\s*|\s+and\s+)?)*\.?$", re.I)
# "A turn that never boots stays launching forever": "never" inside a relative clause narrates a symptom
SYMPTOM_NEVER = re.compile(r"\b(?:that|which|who|where|when)\s+(?:never|cannot|can't)\b", re.I)
NOT_REQUIREMENT = re.compile(r"^(?:The grader\b|Grading\b|Your (?:work|implementation|solution|interpreter|program)\b"
                             r"[^.]*\b(?:is|will be) (?:graded|evaluated)|[^.]{0,40}\b(?:is|are) graded by\b)", re.I)


def is_requirement(sentence: str, opening: bool = False) -> bool:
    st = sentence.strip()
    if NOT_REQUIREMENT.match(st) and not re.search(r"\b(must|never|only)\b", st):
        return False  # grader procedure, not a property of the deliverable
    if st.startswith("`") and re.search(r"\s[—→]\s|\s->\s", st):
        return False  # an example row of a symptom list
    if (st.endswith(":") or re.search(r"\ball of the following\.?$", st)) and \
            not re.search(r"\b(never|exactly|at most|at least)\b", st):
        return False  # introduces a list; the items are the requirements
    if SCOPE_LINE.match(st):
        return False  # "Fix /app/pkg/: a.py, b.py." names where to work, not a property
    sentence = SYMPTOM_NEVER.sub(" ", sentence)
    if CONSTRAINT_RE.search(sentence):
        return True
    pats = [p for p in DECLARATIVE_RES if not (opening and p in WEAK_RES)]
    return any(p.search(sentence) for p in pats)


BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d{1,2}[.)])\s+")
ABBREV_RE = re.compile(r"(?:\b(?:e\.g|i\.e|etc|vs|cf|approx|incl|resp|fig|al)\.|(?<![\w.])[A-Z]\.)$", re.I)


def split_sentences(block: str):
    """(offset, sentence) pairs. Splits on . ! ? followed by whitespace and a capital, digit, quote or a
    lowercase identifier ("...from a file. trimesh's own tests"), but never after an abbreviation."""
    out, pos = [], 0
    for m in re.finditer(r"[.!?][\"')\]`]*\s+", block):
        nxt = block[m.end():m.end() + 1]
        if not nxt or not (nxt.isalnum() or nxt in "`\"'(*_"):
            continue
        if block[m.start()] == "." and ABBREV_RE.search(block[:m.start() + 1]):
            continue
        s = block[pos:m.end()]
        if s.strip():
            out.append((pos, s))
        pos = m.end()
    if block[pos:].strip():
        out.append((pos, block[pos:]))
    return out


def instruction_sentences(text: str):
    """(line, sentence) for prose sentences, without code fences, comments or the trailer. Markdown
    bullets are their own blocks, so two list items never merge into one "sentence"."""
    out, seen = [], set()
    for start, block in paragraphs(strip_fences(text)):
        if block.lstrip().startswith("|"):
            out.append((start, block.strip()))
            continue
        subs = []
        for i, ln in enumerate(block.split("\n")):
            if not subs or BULLET_RE.match(ln):
                subs.append([start + i, BULLET_RE.sub("", ln, count=1)])
            else:
                subs[-1][1] += "\n" + ln
        for sline, sub in subs:
            for off, s in split_sentences(sub):
                ns = norm(s)
                if ns and ns not in seen:
                    seen.add(ns)
                    out.append((sline + sub[:off].count("\n"), ns))
    return [(n, s) for n, s in out if not TRAILER_RE.match(s)]


def constraint_sentences(text: str, with_opening: bool = False):
    """One entry per sentence that states a requirement: an obligation, or a declarative property of the
    deliverable. Weak cues (UTC, units, "the same") do not count in the opening background paragraph, the
    first paragraph that is not only a scope line ("Fix /app/pkg/: a.py, b.py."). With WITH_OPENING the
    entries are (line, sentence, in the opening paragraph)."""
    blocks = [b for b in paragraphs(strip_fences(text)) if not TRAILER_RE.match(norm(b[1]))
              and not b[1].lstrip().startswith(("#", "<!--"))]
    prose = [b for b in blocks if not SCOPE_LINE.match(norm(b[1]))]
    first = (prose or blocks or [(0, "")])[0]
    first_end = first[0] + first[1].count("\n")
    out = [(n, s, first[0] <= n <= first_end) for n, s in instruction_sentences(text)]
    out = [(n, s, o) for n, s, o in out if is_requirement(s, opening=o)]
    return out if with_opening else [(n, s) for n, s, _ in out]


def _py_tests(p: Path, text: str):
    found = {}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        for m in re.finditer(r"^\s*(?:async\s+)?def\s+(test_\w+)", text, re.M):
            found.setdefault(m.group(1), (text[:m.start()].count("\n") + 1, None))
        return found
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            ids = set()
            opaque = False
            for dec in node.decorator_list:
                if isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") == "parametrize":
                    kw = {k.arg: k.value for k in dec.keywords}
                    if "ids" in kw and isinstance(kw["ids"], (ast.List, ast.Tuple)) and all(
                            isinstance(e, ast.Constant) and isinstance(e.value, str) for e in kw["ids"].elts):
                        ids |= {e.value for e in kw["ids"].elts}
                    else:
                        opaque = True
            found.setdefault(node.name, (node.lineno, None if opaque or not ids else ids))
    return found


def discover_tests(task: Path):
    """{name: (relpath, line, ids or None)} for every test function or case under tests/."""
    tests = {}
    tdir = task / "tests"
    if not tdir.is_dir():
        return tests
    for p in sorted(tdir.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(task).as_posix()
        name, suf = p.name, p.suffix
        if suf == ".py" and (name.startswith("test_") or name.endswith("_test.py")):
            text = read(p)
            for t, (ln, ids) in _py_tests(p, text).items():
                tests.setdefault(t, (rel, ln, ids))
        elif suf in (".js", ".mjs", ".cjs", ".ts"):
            text = read(p)
            for m in re.finditer(r"\b(?:test|it)\s*\(\s*(['\"`])(.+?)\1", text):
                tests.setdefault(m.group(2), (rel, text[:m.start()].count("\n") + 1, None))
        elif suf == ".go" and name.endswith("_test.go"):
            text = read(p)
            for m in re.finditer(r"^func\s+(Test\w+)\s*\(", text, re.M):
                tests.setdefault(m.group(1), (rel, text[:m.start()].count("\n") + 1, None))
        elif suf == ".rs":
            text = read(p)
            for m in re.finditer(r"#\[test\]\s*(?:#\[[^\]]*\]\s*)*fn\s+(\w+)", text):
                tests.setdefault(m.group(1), (rel, text[:m.start()].count("\n") + 1, None))
    return tests


def split_ref(ref: str):
    last = ref.split("::")[-1].strip()
    m = re.match(r"^(.*?)\[(.*)\]$", last)
    return (m.group(1), m.group(2)) if m else (last, None)


def vacuous_python_tests(task: Path, tests: dict) -> list:
    """Reject literal-only test bodies, without claiming other bodies verify their requirements."""
    findings = []
    for relative in sorted({location[0] for location in tests.values() if location[0].endswith(".py")}):
        try:
            tree = ast.parse(read(task / relative))
        except SyntaxError as error:
            findings.append(finding(relative, error.lineno or 0, "cannot inspect test assertions: invalid Python"))
            continue
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if tests.get(node.name, ())[:2] != (relative, node.lineno):
                continue
            for statement in node.body:
                if isinstance(statement, ast.Pass):
                    continue
                if isinstance(statement, ast.Expr) and isinstance(statement.value, ast.Constant):
                    continue
                if isinstance(statement, ast.Assert) and isinstance(statement.test, ast.Constant):
                    continue
                break
            else:
                statement = None
            if statement is None or (isinstance(statement, ast.Return) and (
                    statement.value is None or isinstance(statement.value, ast.Constant))):
                findings.append(finding(relative, node.lineno,
                                        f"{node.name}: vacuous test body; no behavior-dependent check runs"))
    return findings


# Words of an identifier (snake_case and camelCase split) that name a tolerance. Whole words only:
# N_STEPS, REPS, SHALLOW and BANDWIDTH are not tolerances.
TOL_WORDS = {"tol", "tols", "tolerance", "tolerances", "band", "bands", "eps", "epsilon", "margin", "margins",
             "slack", "atol", "rtol", "abstol", "reltol", "within", "allow", "allowed", "allowance"}


class _TolName:
    """TOL_NAME.search(identifier): true when one of the identifier's words is a tolerance word."""

    @staticmethod
    def search(name: str) -> bool:
        words = re.findall(r"[A-Z]+(?![a-z])|[A-Z]?[a-z]+|\d+", name)
        return any(w.lower() in TOL_WORDS for w in words)


TOL_NAME = _TolName()


def test_tolerances(task: Path):
    """{value: [(rel, line, name)]} for tolerance constants the tests compare with: constants named like a
    tolerance or band (dict values included), isclose/approx tolerances, and literals in abs(a - b) <= C."""
    out = {}
    tdir = task / "tests"
    for p in sorted(tdir.glob("*.py")) if tdir.is_dir() else []:
        rel = p.relative_to(task).as_posix()
        try:
            tree = ast.parse(read(p))
        except SyntaxError:
            continue

        def add(v, line, name):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 1e-4 or v in (0, 1):
                return
            out.setdefault(float(v), []).append((rel, line, name))
        for nd in ast.walk(tree):
            if isinstance(nd, ast.Assign) and len(nd.targets) == 1 and isinstance(nd.targets[0], ast.Name) \
                    and TOL_NAME.search(nd.targets[0].id):
                vals = [nd.value] if not isinstance(nd.value, ast.Dict) else nd.value.values
                for v in vals:
                    if isinstance(v, ast.Constant):
                        add(v.value, nd.lineno, nd.targets[0].id)
            elif isinstance(nd, ast.Call):
                fname = getattr(nd.func, "attr", getattr(nd.func, "id", ""))
                if fname in ("isclose", "approx", "allclose", "assert_allclose"):
                    for k in nd.keywords:
                        if k.arg in ("abs_tol", "rel_tol", "abs", "rel", "atol", "rtol") and isinstance(k.value, ast.Constant):
                            add(k.value.value, nd.lineno, f"{fname}({k.arg}=)")
            elif isinstance(nd, ast.Compare) and isinstance(nd.left, ast.Call) and \
                    getattr(nd.left.func, "id", "") == "abs" and len(nd.ops) == 1 and \
                    isinstance(nd.ops[0], (ast.Lt, ast.LtE)) and isinstance(nd.comparators[0], ast.Constant):
                add(nd.comparators[0].value, nd.lineno, "abs(a - b) bound")
    return out


# Number words an instruction may state a band in ("within four decimals", "to two decimal places").
TOL_NUMBER_WORDS = dict({"half": 0.5}, **{w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen "
    "seventeen eighteen nineteen twenty".split())},
    thirty=30, forty=40, fifty=50, sixty=60, seventy=70, eighty=80, ninety=90, hundred=100)


def unstated_tolerances(task: Path, instr: str):
    """Tolerances the tests apply that instruction.md never states (value, or value x100 as a percentage)."""
    nums = {float(x.replace(",", "")) for x in re.findall(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)", instr)}
    nums |= {float(v) for w, v in TOL_NUMBER_WORDS.items() if re.search(r"\b" + w + r"\b", instr, re.I)}
    out = {}
    for v, where in test_tolerances(task).items():
        if any(abs(v - n) < 1e-9 or abs(v * 100 - n) < 1e-9 for n in nums):
            continue
        for rel, line, name in where:
            out.setdefault(rel, []).append((line, f"{name} = {v:g}"))
    return out


def gate_requirements(task: Path) -> GateResult:
    instr_p, req_p = task / "instruction.md", task / "tests/requirements.json"
    if not instr_p.is_file():
        return GateResult("ERROR", "instruction.md is missing, nothing to bind requirements to")
    instr = read(instr_p)
    constraints = constraint_sentences(instr, with_opening=True)
    tol_fs = []
    for rel, items in unstated_tolerances(task, instr).items():
        ln0, msg = _collapse(items, "the tests compare with tolerances the instruction never states ({where}): "
                                    "an agent cannot aim for a band it is not told; state each band or its scale in "
                                    "instruction.md")
        tol_fs.append(finding(rel, ln0, msg))
    if not req_p.is_file():
        fs = [finding("tests/requirements.json", 0, "missing: no instruction sentence is bound to a test")] + tol_fs
        fs += [finding("instruction.md", n, f"constraint sentence with no requirement: \"{s[:160]}\"")
               for n, s, _ in constraints]
        if is_v2(task):
            return GateResult("ERROR", "v2 task without tests/requirements.json: the gate cannot run", fs)
        return GateResult("FAIL", "legacy task: tests/requirements.json is missing. Migrate to v2 and give every "
                          f"constraint sentence below ({len(constraints)}) a requirement id bound to a test.", fs)
    raw = read(req_p)
    try:
        data = json.loads(raw)
        reqs = data["requirements"]
        assert isinstance(reqs, list)
    except Exception as e:
        return GateResult("ERROR", f"tests/requirements.json does not parse as {{\"requirements\": [...]}}: {e}")
    unstated = [str(x) for x in data.get("unstated_ok", []) or []]
    tests = discover_tests(task)
    fs = list(tol_fs) + vacuous_python_tests(task, tests)
    warns = []
    instr_norm = norm(strip_fences(instr) + "\n" + instr)
    # context_ok: instruction sentences the author declares background, not requirements ("operators have to
    # restart the runner" narrates the symptom). Each must be quoted verbatim, and the gate details list every
    # one, so contract review sees what was taken out of the traceability check.
    context = data.get("context_ok", []) or []
    if not isinstance(context, list):
        fs.append(finding("tests/requirements.json", line_of(raw, "context_ok"), "context_ok is not a list of quotes"))
        context = []
    context_ok = []
    for c in context:
        if not isinstance(c, str) or not c.strip():
            fs.append(finding("tests/requirements.json", line_of(raw, "context_ok"),
                              f"context_ok entry {c!r} is not a non-empty quote"))
        elif norm(c) not in instr_norm:
            fs.append(finding("tests/requirements.json", line_of(raw, c[:40]),
                              f"context_ok quote does not appear verbatim in instruction.md: \"{c[:120]}\""))
        else:
            context_ok.append(norm(c))
    referenced = set()
    quotes = []
    for i, r in enumerate(reqs):
        if not isinstance(r, dict):
            fs.append(finding("tests/requirements.json", 0, f"requirement #{i + 1} is not an object")); continue
        rid = str(r.get("id", f"#{i + 1}"))
        ln = line_of(raw, f'"{rid}"')
        q, tl = r.get("quote"), r.get("tests")
        if not isinstance(q, str) or not q.strip():
            fs.append(finding("tests/requirements.json", ln, f"{rid}: no quote"))
        else:
            quotes.append(norm(q))
            if norm(q) not in instr_norm:
                fs.append(finding("tests/requirements.json", ln,
                                  f"{rid}: quote does not appear verbatim in instruction.md: \"{q[:120]}\""))
        if not isinstance(tl, list) or not tl:
            fs.append(finding("tests/requirements.json", ln, f"{rid}: lists no test, so nothing adjudicates it"))
            continue
        for ref in tl:
            base, pid = split_ref(str(ref))
            if base not in tests:
                fs.append(finding("tests/requirements.json", ln, f"{rid}: test {ref!r} does not exist under tests/"))
                continue
            ids = tests[base][2]
            if pid is not None and ids is not None and pid not in ids:
                fs.append(finding("tests/requirements.json", ln,
                                  f"{rid}: {ref!r} names a parametrize id that {base} does not declare"))
            referenced.add(base)
    ok_bases = {split_ref(u)[0] for u in unstated}
    for u in unstated:
        if split_ref(u)[0] not in tests:
            fs.append(finding("tests/requirements.json", line_of(raw, u), f"unstated_ok {u!r} is not a test"))
    for t, (rel, ln, _ids) in sorted(tests.items()):
        if t not in referenced and t not in ok_bases:
            fs.append(finding(rel, ln, f"graded test {t} is not bound to any requirement (nor listed in unstated_ok)"))
    for c in context_ok:
        if any(c == q for q in quotes):
            fs.append(finding("tests/requirements.json", line_of(raw, c[:40]),
                              f"context_ok quote is also a requirement quote: \"{c[:120]}\""))
    n_context = 0
    # the opening paragraph narrates the symptom when later paragraphs carry the requirements
    symptom_para = any(not o for _, _, o in constraints)
    for n, s, opening in constraints:
        ns = norm(s)
        if any(q in ns or ns in q or (len(q) > 25 and q[:40] in ns) for q in quotes):
            continue
        if any(c == ns or (len(c) > 25 and (c in ns or ns in c)) for c in context_ok):
            n_context += 1
            continue
        f = finding("instruction.md", n, f"constraint sentence no requirement quotes: \"{s[:160]}\"")
        if opening and symptom_para and not STRONG_OBLIGATION.search(SYMPTOM_NEVER.sub(" ", s)):
            # the opening paragraph narrates the symptom; a weak obligation word there ("operators have to restart
            # the runner") is usually background. A signal for the contract review, not a verdict: bind it or list
            # it in context_ok to silence it. "must", "never", "exactly" there still need a requirement.
            f["message"] += " (opening paragraph: background or a requirement? bind it, or list it in context_ok)"
            warns.append(f)
        else:
            fs.append(f)
    shown = "; ".join(f"\"{c[:80]}\"" for c in context_ok)
    return GateResult("FAIL" if fs else "PASS",
                 f"syntactic traceability: {len(reqs)} requirements, {len(tests)} graded tests, "
                 f"{len(constraints)} constraint sentences"
                 + (f"; {len(fs)} findings" if fs else "; every quote, test and constraint is bound")
                 + (f"; {len(context_ok)} context_ok sentence(s) declared background by the author, not graded "
                    f"(contract review: confirm each is not a requirement): {shown}" if context_ok else "")
                 + (f"; {len(warns)} unbound opening-paragraph sentence(s) (warning)" if warns else "")
                 + "; semantic assertion coverage is not evaluated", fs, warns,
                 extra={"tests_found": sorted(tests), "coverage_kind": "syntactic_traceability",
                     "semantic_coverage": "not_evaluated", "context_ok": context,
                     "context_ok_matched": n_context})


# ------------------------------------------------------------------ budget

UNIT = {"": 1, "s": 1, "m": 60, "h": 3600, "d": 86400}
SH_TIMEOUT = re.compile(r"(?<![\w-])timeout\s+((?:-{1,2}[A-Za-z][\w-]*(?:[ =][\w.]+)?\s+)*)"
                        r"(?:\$\{\w+:-)?[\"']?(\d+(?:\.\d+)?)([smhd]?)\b")
KW_TIMEOUT = re.compile(r"\btimeout\s*=\s*(.*)$")
PROC_CALL = re.compile(r"\bsubprocess\b|\bPopen\b|check_output|check_call|\.communicate\(|\.wait\(\s*timeout|"
                       r"(?<![\w.])run\(")
FLAG_TIMEOUT = re.compile(r"(?<![\w])-{1,2}timeout[= ](\d+(?:\.\d+)?)([smh]?)\b")
LIST_TIMEOUT = re.compile(r"[\"']timeout[\"']\s*,\s*(?:[\"']-k[\"']\s*,\s*[\"']\d+[\"']\s*,\s*)?[\"'](\d+)[\"']")
TIME_WORDS = re.compile(r"(\d+(?:\.\d+)?)\s*(seconds?|secs?|s|minutes?|mins?|hours?|hrs?|h)\b", re.I)
LIMIT_CUE = re.compile(r"(within|under|has|have|gets|given|at most|no more than|less than|limit|timeout|time out|budget|cap|"
                       r"must (?:finish|complete|return|respond)|takes? no more|in no more)\W+(?:\w+\W+){0,4}$", re.I)
# A stated time limit is a limit on the run (and must be enforced) when its sentence names the run, the agent, the
# verifier or the deliverable's own runtime; otherwise it describes the product ("waited at most 20 minutes").
RUN_LIMIT = re.compile(r"\b(?:you|your|the (?:whole |entire )?run|(?:each|every|the) (?:build|run|test|case|step|attempt)s?|"
                       r"per (?:run|test|case|attempt|build|step)|agent|verifier|"
                       r"grader|checker|test suite|the tests?|wall[- ]?clock|time limit|time budget|"
                       r"must (?:finish|complete|terminate|return|respond|run|exit)|(?:finish|complete)s? (?:in|within)|"
                       r"(?:program|script|solution|command|tool|build)s? (?:must|should|has|gets|may))\b", re.I)
# "has", "have", "gets" and "given" state a time limit only with limit wording after the quantity: "you have
# 10 minutes to respond", "is given 30 s for the build"; "the feed has 24 hours of late postings" is data.
WEAK_LIMIT_CUES = {"has", "have", "gets", "given"}
LIMIT_AFTER = re.compile(r"^\s*(?:to|for|before|until|in which|per (?:run|request|call|attempt|case|test)|"
                         r"(?:of|in) (?:wall[- ]?clock|cpu|run ?time|compute)|(?:time )?(?:limit|budget|timeout)\b)",
                         re.I)


def logical_lines(text: str):
    out, buf, start = [], "", 0
    for n, ln in enumerate(text.splitlines(), 1):
        if not buf:
            start = n
        if ln.rstrip().endswith("\\"):
            buf += ln.rstrip()[:-1] + " "
            continue
        out.append((start, buf + ln))
        buf = ""
    if buf:
        out.append((start, buf))
    return out


# Test data folders under tests/: a log or fixture that records a product's own --timeout flag is data, not a
# verifier step.
DATA_DIR_NAMES = {"fixtures", "fixture", "data", "testdata", "test_data", "golden", "samples", "expected", "logs"}


def _py_code_views(text: str):
    """(without comments, without comments or string literals), line for line, for a Python file. A comment
    ("# upstream CI runs this with timeout 45") or a string ("--timeout=3" as expected product output) is not a
    process wait; a file that does not tokenize keeps its text in both."""
    import io
    import tokenize
    lines = text.splitlines()
    nocom, nostr = [list(ln) for ln in lines], [list(ln) for ln in lines]
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, SyntaxError, IndentationError):
        return text, text
    for t in toks:
        if t.type not in (tokenize.COMMENT, tokenize.STRING) and not (
                t.type == getattr(tokenize, "FSTRING_MIDDLE", -1)):
            continue
        (r0, c0), (r1, c1) = t.start, t.end
        views = (nocom, nostr) if t.type == tokenize.COMMENT else (nostr,)
        for view in views:
            for r in range(r0, r1 + 1):
                if r - 1 >= len(view):
                    break
                a = c0 if r == r0 else 0
                b = c1 if r == r1 else len(view[r - 1])
                for i in range(a, min(b, len(view[r - 1]))):
                    view[r - 1][i] = " "
    return "\n".join("".join(x) for x in nocom), "\n".join("".join(x) for x in nostr)


def scan_timeouts(task: Path):
    """Every literal timeout under tests/: dicts with file, line, sec, text, order. Only verifier code: test data
    (a fixtures/ or data/ folder, an extensionless file without a shebang) is skipped, and in Python only code
    counts: comments never, and string literals only where a process is started (a command line in a string)."""
    found = []
    tdir = task / "tests"
    if not tdir.is_dir():
        return found
    for p in sorted(tdir.rglob("*")):
        if not p.is_file() or p.suffix not in (".sh", ".py", ".bash", "") or p.name == "Dockerfile":
            continue
        if any(part.lower() in DATA_DIR_NAMES for part in p.relative_to(tdir).parts[:-1]):
            continue
        if p.suffix == "" and not read(p).startswith("#!"):
            continue   # an extensionless log or sample, not a script
        rel = p.relative_to(task).as_posix()
        depth = 0
        text = read(p)
        phys = text.splitlines()
        if p.suffix == ".py":
            nocom_text, nostr_text = _py_code_views(text)
            nocom, nostr = dict(logical_lines(nocom_text)), dict(logical_lines(nostr_text))
        for n, ln in logical_lines(text):
            code = ln.split("#", 1)[0] if p.suffix in (".sh", ".bash", "") else ln
            raw_code = code
            if p.suffix == ".py":
                raw_code = nocom.get(n, "")
                ctx = "\n".join(phys[max(0, n - 4):n])
                # a string holds a command line only where a process is started ("timeout 30 cmd" for shell=True)
                code = raw_code if PROC_CALL.search(ctx) else nostr.get(n, "")
            if p.suffix in (".sh", ".bash", ""):
                if re.search(r"\b(for|while|until)\b.*\bdo\b|^\s*(for|while|until)\b", code):
                    depth += 1
                if re.search(r"^\s*done\b|;\s*done\b", code):
                    depth = max(0, depth - 1)
            hits = []
            for m in SH_TIMEOUT.finditer(code):
                hits.append((m.start(), float(m.group(2)) * UNIT[m.group(3)]))
            for m in FLAG_TIMEOUT.finditer(code):
                hits.append((m.start(), float(m.group(1)) * UNIT[m.group(2)]))
            for m in LIST_TIMEOUT.finditer(raw_code):   # argv ["timeout", "30", ...]: a process wait wherever it is
                hits.append((m.start(), float(m.group(1))))
            if p.suffix == ".py":
                m = KW_TIMEOUT.search(raw_code)
                # a process wait only: product parameters (timeout_s=180.0) and in-process waits
                # (asyncio.wait_for(..., timeout=5.0)) are not verifier steps
                ctx = "\n".join(phys[max(0, n - 4):n])
                if m and (not PROC_CALL.search(ctx) or "asyncio" in code or "wait_for" in code):
                    m = None
                if m:
                    rest = re.sub(r"([\"'])(?!\d+(?:\.\d+)?\1)[^\"']*\1", "", m.group(1))
                    num = re.search(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])", rest)
                    if num:
                        hits.append((m.start(), float(num.group(1))))
            for order, (pos, sec) in enumerate(sorted(hits)):
                found.append({"file": rel, "line": n, "sec": sec, "text": raw_code.strip()[:160], "full": raw_code,
                              "order": order, "loop": depth > 0 and p.suffix != ".py"})
    return found


# ------------------------------------------------------------------ shell reading helpers

HEREDOC_RE = re.compile(r"(?<!<)<<-?\s*(['\"]?)([A-Za-z_]\w*)\1")
VAR_RE = re.compile(r"\$\{(\w+)(?:[:#%/][^}]*)?\}|\$(\w+)")


def _strip_comment(s: str) -> str:
    q, prev = None, " "
    for i, ch in enumerate(s):
        if q:
            if ch == q and (q == "'" or s[i - 1] != "\\"):
                q = None
        elif ch in "'\"" and (i == 0 or s[i - 1] != "\\"):
            q = ch
        elif ch == "#" and prev.isspace():
            return s[:i]
        prev = ch
    return s


def _quote_open(s: str) -> bool:
    q = None
    for i, ch in enumerate(s):
        if q:
            if ch == q and (q == "'" or s[i - 1] != "\\"):
                q = None
        elif ch in "'\"" and (i == 0 or s[i - 1] != "\\"):
            q = ch
    return q is not None


def sh_logical(text: str):
    """(line, code) for a shell script: continuations and multi-line quoted strings joined, comments
    stripped, heredoc bodies skipped (their python is not shell)."""
    lines, out, i = text.splitlines(), [], 0
    while i < len(lines):
        start, buf = i + 1, lines[i]
        i += 1
        joins = 0
        while i < len(lines) and joins < 60:
            code = _strip_comment(buf)
            if code.rstrip().endswith("\\"):
                buf = code.rstrip()[:-1] + " " + lines[i]
            elif _quote_open(code):
                buf = code + "\n" + lines[i]
            else:
                break
            i += 1
            joins += 1
        code = _strip_comment(buf)
        out.append((start, code))
        for m in HEREDOC_RE.finditer(code):
            tag, strip_tabs = m.group(2), "<<-" in m.group(0)
            while i < len(lines) and (lines[i].strip() if strip_tabs else lines[i].rstrip()) != tag:
                i += 1
            i += 1
    return out


def split_cmds(code: str):
    """Simple commands of one logical line, split on ; && || | & and newlines outside quotes and $( )."""
    segs, cur, q, depth, i = [], "", None, 0, 0
    while i < len(code):
        ch = code[i]
        if q:
            cur += ch
            if ch == q and (q == "'" or code[i - 1] != "\\"):
                q = None
        elif ch in "'\"":
            q = ch
            cur += ch
        elif code.startswith("$(", i):
            depth += 1
            cur += "$("
            i += 2
            continue
        elif ch == ")" and depth:
            depth -= 1
            cur += ch
        elif depth == 0 and (ch in ";\n|" or (ch == "&" and not code.startswith("&>", i)
                                             and not cur.rstrip().endswith((">", "<")))):
            if ch == "&" and code.startswith("&&", i) or ch == "|" and code.startswith("||", i):
                i += 1
            if cur.strip():
                segs.append(cur.strip())
            cur = ""
        else:
            cur += ch
        i += 1
    if cur.strip():
        segs.append(cur.strip())
    return segs


def sh_words(seg: str):
    """(words, redirects) of one simple command; redirects are (op, target). Quotes are kept on words."""
    words, redirs, cur, q, depth, i = [], [], "", None, 0, 0
    pending = None

    def flush():
        nonlocal cur, pending
        if cur:
            if pending:
                if not (pending.endswith("&") and cur.isdigit()) and not cur.startswith("&"):
                    redirs.append((pending, cur))
                pending = None
            else:
                words.append(cur)
        cur = ""

    while i < len(seg):
        ch = seg[i]
        if q:
            cur += ch
            if ch == q and (q == "'" or seg[i - 1] != "\\"):
                q = None
        elif ch in "'\"":
            q = ch
            cur += ch
        elif seg.startswith("$(", i):
            depth += 1
            cur += "$("
            i += 2
            continue
        elif ch == ")" and depth:
            depth -= 1
            cur += ch
        elif depth == 0 and ch in "<>":
            if cur and not (cur.isdigit() or cur == "&"):
                flush()
            cur = ""
            op = ch
            while i + 1 < len(seg) and seg[i + 1] in "<>&|":
                i += 1
                op += seg[i]
            if op.startswith("<<"):
                op = "<<"
            pending = op
        elif depth == 0 and ch.isspace():
            flush()
        else:
            cur += ch
        i += 1
    flush()
    return [w for w in words if w not in ("(", ")", "{", "}", "((", "))")], redirs


def unquote(w: str) -> str:
    return w.replace('"', "").replace("'", "")


class ShEnv:
    """Straight-line shell variable values: literal or built from other variables. $(...) values are
    opaque and stay as $NAME, so "$RUNS/x" expands to "$TMP/runs/x" when RUNS="$TMP/runs"."""

    def __init__(self):
        self.v = {}

    def learn(self, seg: str):
        words, _ = sh_words(seg)
        if not words or not all(re.match(r"^(?:export\s+)?[A-Za-z_]\w*=", w) for w in words):
            if words and words[0] in ("export", "local", "readonly", "declare"):
                words = [w for w in words[1:] if "=" in w and not w.startswith("-")]
                if not words:
                    return
            else:
                return
        for w in words:
            name, _, val = w.partition("=")
            val = val.strip()
            if val.startswith("$(") or val.startswith("`") or val.startswith('"$(') or val.startswith("("):
                self.v[name] = None
            else:
                self.v[name] = unquote(val)

    def expand(self, s: str, extra=None, depth=0) -> str:
        env = dict(self.v)
        if extra:
            env.update(extra)

        def rep(m):
            name = m.group(1) or m.group(2)
            val = env.get(name)
            if val is None or depth > 6:
                return "$" + name
            return self.expand(val, extra, depth + 1)
        return VAR_RE.sub(rep, unquote(s))

    def number(self, s: str):
        e = self.expand(s).strip()
        return float(e) if re.fullmatch(r"\d+(?:\.\d+)?", e) else None


def sh_functions(lines):
    """{name: (first_line, last_line, body_text)} for shell function definitions."""
    funcs, i = {}, 0
    while i < len(lines):
        n, code = lines[i]
        m = re.match(r"^\s*(?:function\s+)?([A-Za-z_][\w-]*)\s*\(\)\s*\{?(.*)$", code)
        if m:
            depth = code.count("{") - code.count("}")
            body, last = [m.group(2)], n
            j = i
            while depth > 0 and j + 1 < len(lines):
                j += 1
                last, c = lines[j]
                body.append(c)
                depth += c.count("{") - c.count("}")
            funcs[m.group(1)] = (n, last, "\n".join(body))
            i = j + 1
            continue
        i += 1
    return funcs


def loop_head(code: str):
    """None when the line opens no loop, else ('for', var, words_text) / ('while', None, None) / ('cfor', N)."""
    s = code.strip()
    m = re.match(r"^(?:\w+=\S*\s+)*for\s+\(\((.*?)\)\)", s)
    if m:
        lim = re.search(r"<=?\s*(\d+)", m.group(1))
        return ("cfor", None, int(lim.group(1)) + (1 if "<=" in m.group(1) else 0) if lim else None)
    m = re.match(r"^for\s+(\w+)\s+in\s+(.*?)(?:;\s*do\b.*|\s+do\b.*)?$", s, re.S)
    if m:
        return ("for", m.group(1), m.group(2))
    m = re.match(r"^for\s+(\w+)\s*(?:;\s*do\b|$)", s)
    if m:
        return ("for", m.group(1), '"$@"')
    if re.match(r"^(while|until)\b", s):
        return ("while", None, None)
    return None


def loop_items(task: Path, head, env: ShEnv):
    """The literal item list of a for loop, or None when the gate cannot count it."""
    kind, _var, words = head
    if kind == "cfor":
        return [None] * words if isinstance(words, int) else None
    if kind == "while":
        return None
    items = []
    for w, _ in [(w, None) for w in sh_words(words)[0]]:
        if w.startswith("$(") or w.startswith("`") or w.startswith('"$('):
            inner = w.strip('"`$()')
            ms = re.fullmatch(r"\s*seq\s+(?:(\d+)\s+)?(\d+)\s*", inner)
            if ms:
                items += [None] * (int(ms.group(2)) - int(ms.group(1) or 1) + 1)
                continue
            f = re.search(r"(?:/tests/|\btests/)([\w./-]+)", inner)
            if f and (task / "tests" / f.group(1)).is_file() and re.match(r"\s*(cat|grep|sed|awk|cut|sort|tail|head)\b", inner):
                items += [ln for ln in read(task / "tests" / f.group(1)).splitlines()
                          if ln.strip() and not ln.lstrip().startswith("#")]
                continue
            return None
        mb = re.fullmatch(r"\{(\d+)\.\.(\d+)\}", w)
        if mb:
            items += list(range(int(mb.group(1)), int(mb.group(2)) + 1))
            continue
        if any(c in w for c in "*?[") or w in ('"$@"', "$@", '"$*"'):
            return None
        if w.startswith('"') and "$" in w:
            e = env.expand(w)
            if "$" in e:
                return None
            items.append(e)
            continue
        if "$" in w:
            e = env.expand(w)
            if "$" in e or any(c in e for c in "*?["):
                return None
            items += e.split()
            continue
        items.append(unquote(w))
    return items


# ------------------------------------------------------------------ worst-case time budget

SH_TIMEOUT_VAR = re.compile(r"(?<![\w-])timeout\s+((?:-{1,2}[A-Za-z][\w-]*(?:[ =][\w.]+)?\s+)*)"
                            r"[\"']?\$\{?(\w+)\}?[\"']?(?=\s)")
UNCAPPED_RE = re.compile(r"\b(go\s+(?:build|test|vet)|cargo\s+(?:build|test)|npm\s+(?:test|run|ci|install)|"
                         r"python3?\s+-m\s+pytest|pytest|mocha|make)\b")


def sh_worst_case(task: Path, rel: str, text: str):
    """Worst-case seconds of the outermost timeouts in one shell file, loops multiplied by their item
    count. Returns (total, parts, unbounded, uncapped, covered_files)."""
    lines = sh_logical(text)
    env = ShEnv()
    funcs = sh_functions(lines)
    in_func = {n for a, b, _ in funcs.values() for n in range(a, b + 1)}
    tests_names = [p.name for p in (task / "tests").rglob("*") if p.is_file()] if (task / "tests").is_dir() else []
    stack, parts, unbounded, uncapped, covered = [], [], [], 0, set()
    total = 0.0
    for n, code in lines:
        for seg in split_cmds(code):
            env.learn(seg)
        head = loop_head(code)
        if head:
            items = loop_items(task, head, env)
            stack.append((n, None if items is None else len(items)))
        sec = 0.0
        for seg in split_cmds(code):
            hits = [(m.start(), float(m.group(2)) * UNIT[m.group(3)]) for m in SH_TIMEOUT.finditer(seg)]
            for m in SH_TIMEOUT_VAR.finditer(seg):
                v = env.number("$" + m.group(2))
                if v is not None:
                    hits.append((m.start(), v))
            if hits:
                sec += sorted(hits)[0][1]  # the outermost timeout of each simple command
        if sec and n not in in_func:
            mult, unb = 1, None
            for ln, cnt in stack:
                if cnt is None:
                    unb = ln
                else:
                    mult *= cnt
            total += sec * mult
            parts.append((n, sec, mult))
            if unb:
                unbounded.append((unb, n, sec))
            for name in tests_names:
                if re.search(r"(?<![\w.-])" + re.escape(name) + r"\b", code):
                    covered.add(name)
        elif not sec and n not in in_func and UNCAPPED_RE.search(code) and not code.strip().startswith(("#", "echo")):
            uncapped += 1
        if re.search(r"(^|;|\s)done\b", code) and stack:
            stack.pop()
    return total, parts, unbounded, uncapped, covered


PROCESS_CALLS = {"run", "call", "check_call", "check_output", "communicate", "wait", "Popen", "join", "result",
                 "wait_for", "run_until_complete", "getoutput"}


class PyBudget:
    """Worst-case seconds of the timeouts one python file passes, following parameters and module
    constants within the file, loops multiplied by their item count, parametrize cases counted."""

    def __init__(self, task: Path, rel: str, text: str):
        self.task, self.rel = task, rel
        self.tree = ast.parse(text)
        self.funcs = {}
        for node in ast.walk(self.tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.funcs.setdefault(node.name, node)
        self.assign = {}
        for st in self.tree.body:
            if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name):
                self.assign[st.targets[0].id] = st.value
        self.unbounded = []
        self.once, self.once_total = set(), 0.0

    def num(self, e, env, depth=0):
        if depth > 8 or e is None:
            return None
        if isinstance(e, ast.Constant) and isinstance(e.value, (int, float)) and not isinstance(e.value, bool):
            return float(e.value)
        if isinstance(e, ast.Constant) and isinstance(e.value, str) and re.fullmatch(r"\d+(\.\d+)?", e.value):
            return float(e.value)
        if isinstance(e, ast.Name):
            if e.id in env:
                return env[e.id]
            return self.num(self.assign.get(e.id), {}, depth + 1)
        if isinstance(e, ast.BinOp):
            a, b = self.num(e.left, env, depth + 1), self.num(e.right, env, depth + 1)
            if a is None or b is None:
                return None
            ops = {ast.Mult: lambda: a * b, ast.Add: lambda: a + b, ast.Sub: lambda: a - b,
                   ast.Div: lambda: a / b if b else None, ast.FloorDiv: lambda: a // b if b else None}
            f = ops.get(type(e.op))
            return f() if f else None
        if isinstance(e, ast.Call):
            fn = e.func
            if isinstance(fn, ast.Name) and fn.id in ("int", "float") and e.args:
                return self.num(e.args[0], env, depth + 1)
            if isinstance(fn, ast.Attribute) and fn.attr in ("get", "getenv") and len(e.args) >= 2:
                return self.num(e.args[1], env, depth + 1)
        return None

    def count(self, it, env, depth=0):
        if depth > 6:
            return None
        if isinstance(it, (ast.List, ast.Tuple, ast.Set)):
            return None if any(isinstance(x, ast.Starred) for x in it.elts) else len(it.elts)
        if isinstance(it, ast.Dict):
            return len(it.keys)
        if isinstance(it, ast.Name):
            return self.count(self.assign.get(it.id), env, depth + 1) if it.id in self.assign else None
        if isinstance(it, ast.Call):
            fn = it.func
            if isinstance(fn, ast.Name) and fn.id == "range":
                vals = [self.num(a, env) for a in it.args]
                if vals and all(v is not None for v in vals):
                    try:
                        return len(range(*[int(v) for v in vals]))
                    except (TypeError, ValueError):
                        return None
                return None
            if isinstance(fn, ast.Name) and fn.id in ("sorted", "list", "tuple", "set", "reversed", "enumerate") and it.args:
                return self.count(it.args[0], env, depth + 1)
            if isinstance(fn, ast.Attribute) and fn.attr in ("items", "keys", "values"):
                return self.count(fn.value, env, depth + 1)
            if isinstance(fn, ast.Attribute) and fn.attr in ("glob", "rglob") and it.args and \
                    isinstance(it.args[0], ast.Constant) and isinstance(it.args[0].value, str):
                parts = [c.value for c in ast.walk(fn.value) if isinstance(c, ast.Constant) and isinstance(c.value, str)]
                base = self.task / "tests"
                for p in parts:
                    base = base / p.strip("/")
                if base.is_dir():
                    g = base.rglob if fn.attr == "rglob" else base.glob
                    return sum(1 for _ in g(it.args[0].value))
        return None

    def calls_cost(self, node, env, stack):
        total = 0.0
        todo = [node]
        while todo:
            x = todo.pop()
            if isinstance(x, (ast.Lambda, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and x is not node:
                continue
            if isinstance(x, ast.Call):
                total += self.call_cost(x, env, stack)
            todo.extend(ast.iter_child_nodes(x))
        return total

    def call_cost(self, c, env, stack):
        sec = 0.0
        name = None
        if isinstance(c.func, ast.Name):
            name = c.func.id
        elif isinstance(c.func, ast.Attribute) and isinstance(c.func.value, ast.Name) and c.func.value.id in ("self", "cls"):
            name = c.func.attr
        fn = self.funcs.get(name) if name else None
        callee = c.func.attr if isinstance(c.func, ast.Attribute) else getattr(c.func, "id", "")
        if fn is None and callee in PROCESS_CALLS:
            # only process and thread waits are verifier steps; HTTP and socket timeouts are per request
            for kw in c.keywords:
                if kw.arg in ("timeout", "timeout_sec", "timeout_s"):
                    sec += self.num(kw.value, env) or 0.0
        if fn is None or name in stack or len(stack) > 12:
            return sec
        params = [a.arg for a in fn.args.posonlyargs + fn.args.args]
        if params and params[0] in ("self", "cls"):
            params = params[1:]
        if not params and not fn.args.kwonlyargs:
            # a zero-argument helper is usually a cached build: counted once per file, not per call
            if name not in self.once:
                self.once.add(name)
                self.once_total += self.body_cost(fn.body, {}, stack + (name,))
            return sec
        env2 = {}
        defaults = fn.args.defaults
        for p, d in zip(params[len(params) - len(defaults):], defaults):
            v = self.num(d, {})
            if v is not None:
                env2[p] = v
        for p, d in zip([a.arg for a in fn.args.kwonlyargs], fn.args.kw_defaults):
            v = self.num(d, {}) if d is not None else None
            if v is not None:
                env2[p] = v
        for p, a in zip(params, c.args):
            if isinstance(a, ast.Starred):
                break
            v = self.num(a, env)
            if v is not None:
                env2[p] = v
        for kw in c.keywords:
            if kw.arg:
                v = self.num(kw.value, env)
                if v is not None:
                    env2[kw.arg] = v
        return sec + self.body_cost(fn.body, env2, stack + (name,))

    def body_cost(self, stmts, env, stack):
        total = 0.0
        for st in stmts:
            if isinstance(st, (ast.For, ast.AsyncFor)):
                inner = self.body_cost(st.body, env, stack)
                if inner:
                    n = self.count(st.iter, env)
                    if n is None:
                        self.unbounded.append((st.lineno, inner))
                        total += inner
                    else:
                        total += n * inner
                total += self.calls_cost(st.iter, env, stack) + self.body_cost(st.orelse, env, stack)
            elif isinstance(st, ast.While):
                inner = self.body_cost(st.body, env, stack)
                if inner:
                    self.unbounded.append((st.lineno, inner))
                    total += inner
            elif isinstance(st, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if stack:  # a nested def is usually returned and run: count it once
                    total += self.body_cost(st.body, env, stack + (st.name,))
            elif isinstance(st, ast.ClassDef):
                continue
            elif isinstance(st, ast.If):
                total += self.calls_cost(st.test, env, stack) + max(self.body_cost(st.body, env, stack),
                                                                     self.body_cost(st.orelse, env, stack))
            elif isinstance(st, (ast.With, ast.AsyncWith)):
                for it in st.items:
                    total += self.calls_cost(it.context_expr, env, stack)
                total += self.body_cost(st.body, env, stack)
            elif isinstance(st, ast.Try):
                total += self.body_cost(st.body, env, stack) + self.body_cost(st.finalbody, env, stack) + \
                    max([self.body_cost(h.body, env, stack) for h in st.handlers] + [self.body_cost(st.orelse, env, stack)])
            else:
                total += self.calls_cost(st, env, stack)
        return total

    def param_count(self, fn):
        n = 1
        for dec in fn.decorator_list:
            if isinstance(dec, ast.Call) and getattr(dec.func, "attr", "") == "parametrize" and len(dec.args) >= 2:
                c = self.count(dec.args[1], {})
                if c is None:
                    return None
                n *= c
        return n

    def fixture_cost(self, fn, seen) -> float:
        """Cost of the pytest fixtures a test (or fixture) requests: wide-scope fixtures once per
        file, function-scope fixtures on every use."""
        per_use = 0.0
        for a in fn.args.args:
            fx = self.funcs.get(a.arg)
            if fx is None or a.arg in seen or not any(
                    "fixture" in ast.unparse(d) for d in fx.decorator_list):
                continue
            seen = seen | {a.arg}
            scope = next((ast.unparse(k.value).strip("'\"") for d in fx.decorator_list if isinstance(d, ast.Call)
                          for k in d.keywords if k.arg == "scope"), "function")
            cost = self.body_cost(fx.body, {}, (a.arg,)) + self.fixture_cost(fx, seen)
            if scope == "function":
                per_use += cost
            elif a.arg not in self.once:
                self.once.add(a.arg)
                self.once_total += cost
        return per_use

    def file_cost(self, is_test: bool) -> float:
        total = self.body_cost(self.tree.body, {}, ())
        if is_test:
            tests = [s for s in self.tree.body if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))]
            for cls in (s for s in self.tree.body if isinstance(s, ast.ClassDef) and s.name.startswith("Test")):
                tests += [s for s in cls.body if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef))]
            for fn in tests:
                if not fn.name.startswith("test"):
                    continue
                c = self.body_cost(fn.body, {}, (fn.name,)) + self.fixture_cost(fn, set())
                if not c:
                    continue
                n = self.param_count(fn)
                if n is None:
                    self.unbounded.append((fn.lineno, c))
                    total += c
                else:
                    total += n * c
        return total + self.once_total


def worst_case_budget(task: Path):
    """(total_sec, parts, unbounded, uncapped) over tests/: shell files first, then the python files the
    verifier runs without an outer timeout around them."""
    tdir = task / "tests"
    total, parts, unbounded, uncapped, covered = 0.0, [], [], 0, set()
    if not tdir.is_dir():
        return total, parts, unbounded, uncapped
    shells = [p for p in sorted(tdir.rglob("*")) if p.is_file() and p.suffix in (".sh", ".bash")]
    sh_text = ""
    for p in shells:
        rel = p.relative_to(task).as_posix()
        text = read(p)
        sh_text += text + "\n"
        t, ps, ub, unc, cov = sh_worst_case(task, rel, text)
        total += t
        uncapped += unc
        covered |= cov
        parts += [(f"{rel}:{n}", sec, mult) for n, sec, mult in ps]
        unbounded += [(rel, loop_line, f"{rel}:{hit} caps each iteration at {sec:g} s") for loop_line, hit, sec in ub]
    for p in sorted(tdir.rglob("*.py")):
        if p.name in covered or p.stat().st_size > 2_000_000:
            continue
        is_test = p.name.startswith("test_") or p.name.endswith("_test.py")
        if not is_test and not re.search(r"(?<![\w.-])" + re.escape(p.name) + r"\b", sh_text):
            continue
        rel = p.relative_to(task).as_posix()
        try:
            pb = PyBudget(task, rel, read(p))
            t = pb.file_cost(is_test)
        except (SyntaxError, RecursionError, ValueError):
            continue
        if t:
            total += t
            parts.append((rel, t, 1))
        unbounded += [(rel, ln, f"each pass costs {sec:g} s") for ln, sec in pb.unbounded]
    return total, parts, unbounded, uncapped


def numbers_in_tests(task: Path) -> set[float]:
    nums = set()
    tdir = task / "tests"
    if tdir.is_dir():
        for p in tdir.rglob("*"):
            if p.is_file() and p.suffix in (".sh", ".py", ".json", ".bash", ""):
                if p.stat().st_size > 2_000_000:
                    continue
                nums |= {float(x) for x in re.findall(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])", read(p))}
    return nums


# ------------------------------------------------------------------ is a limit enforced?
# A number that appears somewhere under tests/ is not evidence that the limit is enforced: it may be a data value,
# a message or a comment. A limit counts as enforced when that number, or a name that carries it (a constant, a
# budget.json key and every variable read from it), reaches an enforcing construct: a timeout (shell `timeout N`,
# `timeout=` on a process call or wait, `--timeout`), `ulimit`/`prlimit`/`setrlimit`/`signal.alarm`, or a comparison
# in a condition or assert (the elapsed time or a size checked against it), or it is a task.toml limit Harbor applies.
NUM_TOKEN = re.compile(r"(?<![\w.])(\d+(?:\.\d+)?)(?![\w.])")
SH_TIMEOUT_CMD = re.compile(r"(?<![\w-])timeout\s|--timeout\b")
PY_TIMEOUT_CALL = re.compile(r"[(,]\s*timeout\s*=(?!=)|\.wait\(|signal\.alarm|[\"']timeout[\"']\s*,")
RLIMIT = re.compile(r"(?<![\w-])(?:ulimit|prlimit)\s|setrlimit|RLIMIT_")
SH_CMP = re.compile(r"\s-(?:gt|ge|lt|le)\s|\(\(.*[<>]")
# a comparison enforces a limit of its kind only when the line is about that quantity
CMP_HINT = {"time": re.compile(r"time|elapsed|duration|deadline|monotonic|perf_counter|second|_s\b|_sec|start|cap|"
                               r"budget|limit", re.I),
            "size": re.compile(r"size|bytes|len\(|_mb|_kb|\bmb\b|stat|cap|budget|limit|max", re.I)}
LIMIT_JSON = re.compile(r"budget|limit|caps?\b|config|grading", re.I)
PY_CMP = re.compile(r"(?<![<>=!-])(?:<=|>=|<|>)(?![<>=])")
PY_COND = re.compile(r"^\s*(?:assert|if|elif|while)\b|\bif\b")
PY_ASSIGN = re.compile(r"^\s*((?:[A-Za-z_]\w*\s*,\s*)*[A-Za-z_]\w*)\s*(?::[^=]*)?=(?!=)")
SH_ASSIGN = re.compile(r"^\s*(?:(?:local|export|readonly|declare(?:\s+-\w+)*)\s+)?([A-Za-z_]\w*)=")
SH_READ = re.compile(r"\bread\s+(?:-\w+\s+)*((?:[A-Za-z_]\w*\s*)+?)\s*<<<(.*)$")
SH_HEREDOC = re.compile(r"<<-?\s*['\"]?([A-Za-z_]\w*)['\"]?")
STRINGS = re.compile(r"(\"(?:[^\"\\]|\\.)*\"|'(?:[^'\\]|\\.)*')")
TOML_TIME_LIMITS = (("agent", "timeout_sec"), ("verifier", "timeout_sec"), ("environment", "build_timeout_sec"))
TOML_SIZE_LIMITS = (("environment", "memory_mb"), ("environment", "storage_mb"))


def _code_units(task: Path):
    """(file, line, kind, text, block) for every logical line of the code under tests/: shell with its continuations
    (a heredoc body also counts as the opening line's block, so `caps=$(python3 - <<'PY' ... PY)` carries what the
    body reads), Python joined over open brackets. kind is "sh" or "py"; a heredoc body run by python is "py"."""
    tdir = task / "tests"
    if not tdir.is_dir():
        return []
    units = []
    for p in sorted(tdir.rglob("*")):
        if not p.is_file() or p.suffix not in (".sh", ".py", ".bash", "") or p.name == "Dockerfile":
            continue
        if p.stat().st_size > 2_000_000:
            continue
        rel, text = p.relative_to(task).as_posix(), read(p)
        if p.suffix == ".py":
            units += [(rel, n, "py", ln, "") for n, ln in _py_logical(text)]
            continue
        lines = text.splitlines()
        i = 0
        while i < len(lines):
            start, ln = i + 1, lines[i]
            while ln.rstrip().endswith("\\") and i + 1 < len(lines):
                i += 1
                ln = ln.rstrip()[:-1] + " " + lines[i]
            m = SH_HEREDOC.search(ln.split("#", 1)[0]) if "<<<" not in ln else None
            body = []
            if m:
                tag = m.group(1)
                while i + 1 < len(lines) and lines[i + 1].strip() != tag:
                    i += 1
                    body.append((i + 1, lines[i]))
                i += 1  # the terminator
            units.append((rel, start, "sh", ln, "\n".join(b for _, b in body)))
            kind = "py" if re.search(r"python|RPY|\bPY\b", ln) else "sh"
            if kind == "py":
                joined = _py_logical("\n".join(b for _, b in body))
                first = body[0][0] if body else start
                units += [(rel, first + n - 1, "py", t, "") for n, t in joined]
            else:
                units += [(rel, n, "sh", b, "") for n, b in body]
            i += 1
    return units


def _py_logical(text: str):
    """Python logical lines: physical lines joined while a bracket is open (strings and comments ignored)."""
    out, buf, start, depth = [], [], 0, 0
    for n, ln in enumerate(text.splitlines(), 1):
        if not buf:
            start = n
        buf.append(ln)
        code = STRINGS.sub("''", ln).split("#", 1)[0]
        depth = max(0, depth + sum(code.count(c) for c in "([{") - sum(code.count(c) for c in ")]}"))
        if depth == 0 or len(buf) >= 60:
            out.append((start, " ".join(s.strip() for s in buf)))
            buf, depth = [], 0
    if buf:
        out.append((start, " ".join(s.strip() for s in buf)))
    return out


def _enforcing(kind: str, text: str, what: str) -> int:
    """2: a timeout or rlimit construct; 1: a comparison in a condition, on a line about this kind of quantity; 0."""
    if kind == "sh":
        code = re.sub(r"'[^']*'", "''", text.split(" #", 1)[0])
        if RLIMIT.search(code) or (what == "time" and SH_TIMEOUT_CMD.search(code)):
            return 2
        return int(bool(SH_CMP.search(code) and CMP_HINT[what].search(code)))
    if RLIMIT.search(text) or (what == "time" and PY_TIMEOUT_CALL.search(text)):
        return 2
    code = STRINGS.sub("''", text).split("#", 1)[0]
    return int(bool(PY_CMP.search(code) and PY_COND.search(code) and "->" not in code
                    and CMP_HINT[what].search(text)))


def _json_keys(task: Path, values: set[float]) -> set[str]:
    """Keys of the limit files under tests/ (budget.json, a grading or config file) whose value is one of `values`
    (e.g. max_submission_mb, cap_sec). Data files (expected outputs, fixtures) are not read: their keys name values."""
    keys = set()

    def walk(v, key=None):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, k)
        elif isinstance(v, list):
            for x in v:
                walk(x, key)
        elif isinstance(v, (int, float)) and not isinstance(v, bool) and key and float(v) in values:
            keys.add(str(key))
    tdir = task / "tests"
    for p in sorted(tdir.rglob("*.json")) if tdir.is_dir() else []:
        if LIMIT_JSON.search(p.stem) and p.stat().st_size <= 200_000:
            try:
                walk(json.loads(read(p)))
            except ValueError:
                pass
    return keys


def limit_enforcement(task: Path, values, *, what: str = "time", keys=(), toml_limits=(), units=None,
                      construct_only: bool = False) -> tuple[str, str]:
    """("enforced", where) when one of `values` (or a name that carries it) reaches an enforcing construct under
    tests/, or is a task.toml limit in `toml_limits`; ("mentioned", where) when it only appears there; ("absent", "").
    construct_only: a comparison is not enough (a budget.json cap is fed to a timeout, not only checked)."""
    values = {float(v) for v in values}
    try:
        d = load_toml(task)
    except Exception:
        d = {}
    for sect, key in toml_limits:
        v = (d.get(sect) or {}).get(key)
        if isinstance(v, (int, float)) and float(v) in values:
            return "enforced", f"task.toml [{sect}].{key} = {v:g}"
    units = _code_units(task) if units is None else units
    seeds = set(keys) | _json_keys(task, values)

    def carries(text: str, names) -> bool:
        if any(float(x) in values for x in NUM_TOKEN.findall(text)):
            return True
        return any(re.search(r"(?<![\w])" + re.escape(n) + r"(?![\w])", text) for n in names)
    by_file = {}
    for u in units:
        by_file.setdefault(u[0], []).append(u)
    mention = ""
    for rel, file_units in by_file.items():
        names = set(seeds)  # a name carries the limit within its own file: `cap` in one file is not `cap` in another
        for _ in range(8):  # names propagate through assignments until nothing new is found
            grown = set(names)
            for _rel, _n, kind, text, block in file_units:
                if kind == "py":
                    m = PY_ASSIGN.match(text)
                    if m and carries(text[m.end():], names):
                        grown |= {x.strip() for x in m.group(1).split(",")}
                    continue
                m = SH_READ.search(text)
                if m and carries(m.group(2), names):
                    grown |= set(m.group(1).split())
                m = SH_ASSIGN.match(text)
                if m and (carries(text[m.end():], names) or (block and carries(block, names))):
                    grown.add(m.group(1))
            grown = {n for n in grown if len(n) > 1}
            if grown == names:
                break
            names = grown
        for _rel, n, kind, text, _block in file_units:
            if not carries(text, names):
                continue
            if _enforcing(kind, text, what) >= (2 if construct_only else 1):
                return "enforced", f"{rel}:{n}"
            mention = mention or f"{rel}:{n}"
    if mention or values & numbers_in_tests(task):
        return "mentioned", mention or "a number under tests/"
    return "absent", ""


SIZE_WORDS = re.compile(r"(\d+(?:\.\d+)?)\s*(KiB|MiB|GiB|KB|kB|MB|GB)\b")
SIZE_CUE = re.compile(r"(at most|no more than|not more than|up to|under|below|above|over|larger than|bigger than|"
                      r"exceed(?:s|ing)?|limit(?:ed)?(?: to)?|capped at|cap of|maximum(?: of)?|max\.?)\W+(?:\w+\W+){0,3}$",
                      re.I)


def size_values(num: float, unit: str) -> set[float]:
    """The number as written and in bytes (binary and decimal), the forms a test may compare against."""
    k = {"k": 1, "m": 2, "g": 3}[unit[0].lower()]
    return {num, num * 1024 ** k, num * 1000 ** k}


def gate_budget(task: Path) -> GateResult:
    try:
        d = load_toml(task)
    except Exception as e:
        return GateResult("ERROR", f"task.toml does not parse: {e}")
    vt = (d.get("verifier") or {}).get("timeout_sec")
    if not isinstance(vt, (int, float)):
        return GateResult("ERROR", "[verifier].timeout_sec is not set, so no budget can be checked")
    toml_text = read(task / "task.toml")
    vt_line = line_of(toml_text, "timeout_sec")
    fs, caps, margin = [], [], 0.0
    step_expected = []  # (name, cap_sec, expected_sec | None): a step's declared typical/expected duration
    bud_p = task / "tests/budget.json"
    legacy_missing = False
    if bud_p.is_file():
        braw = read(bud_p)
        try:
            b = json.loads(braw)
            caps = [(str(s["name"]), float(s["cap_sec"])) for s in b["steps"]]
            margin = float(b.get("margin_sec", 0))
            for s in b["steps"]:
                exp = s.get("expected_sec", s.get("typical_sec"))
                step_expected.append((str(s["name"]), float(s["cap_sec"]),
                                      float(exp) if isinstance(exp, (int, float)) and not isinstance(exp, bool)
                                      else None))
        except Exception as e:
            return GateResult("ERROR", f"tests/budget.json does not parse as the v2 budget: {e}")
        if "verifier_timeout_sec" in b and float(b["verifier_timeout_sec"]) != float(vt):
            fs.append(finding("tests/budget.json", line_of(braw, "verifier_timeout_sec"),
                              f"verifier_timeout_sec {b['verifier_timeout_sec']} disagrees with task.toml "
                              f"[verifier].timeout_sec {vt}"))
        total = sum(c for _, c in caps) + margin
        if total > vt:
            fs.append(finding("tests/budget.json", 1, f"caps {' + '.join('%g' % c for _, c in caps)} + margin "
                              f"{margin:g} = {total:g} s exceed [verifier].timeout_sec {vt:g} s"))
    elif is_v2(task, d):
        return GateResult("ERROR", "v2 task without tests/budget.json: the gate cannot run")
    else:
        legacy_missing = True
        fs.append(finding("tests/budget.json", 0, "missing: the verifier's time budget is not written down"))

    tos = scan_timeouts(task)
    cap_vals = {c for _, c in caps}
    if caps:
        for t in tos:
            if t["sec"] not in cap_vals:
                fs.append(finding(t["file"], t["line"], f"literal timeout {t['sec']:g} s is not a cap in "
                                  f"tests/budget.json (test.sh must read caps from the budget): {t['text']}"))
    # nesting: a shell timeout wraps the test files named on its line, and later timeouts on the same line
    tests_files = {p.name: p.relative_to(task).as_posix() for p in (task / "tests").rglob("*")
                   if p.is_file()} if (task / "tests").is_dir() else {}
    covered_files = set()
    for t in tos:
        if not t["file"].endswith((".sh", ".bash")) and "." in PurePosixPath(t["file"]).name:
            continue
        for other in tos:
            if other["file"] == t["file"] and other["line"] == t["line"] and other["order"] > t["order"]:
                if other["sec"] >= t["sec"]:
                    fs.append(finding(t["file"], t["line"], f"inner timeout {other['sec']:g} s >= its outer "
                                      f"{t['sec']:g} s on the same command"))
        for name, rel in tests_files.items():
            if rel == t["file"] or not re.search(r"(?<![\w.-])" + re.escape(name) + r"\b", t["full"]):
                continue
            covered_files.add(rel)
            for inner in (x for x in tos if x["file"] == rel):
                if inner["sec"] >= t["sec"]:
                    fs.append(finding(inner["file"], inner["line"],
                                      f"inner timeout {inner['sec']:g} s >= the outer timeout {t['sec']:g} s at "
                                      f"{t['file']}:{t['line']} that wraps it; the outer kill leaves no report"))
    # emit.py's per-case deadline (CASE_TIMEOUT_SEC, a time.monotonic() budget, not a timeout= literal) runs
    # inside the emit step: one case that may take the whole emit cap leaves the others no time and the outer
    # kill leaves no observations to judge
    emit_cap = next((c for name, c in caps if name == "emit"), None)
    if (task / "tests").is_dir():
        for p in sorted((task / "tests").rglob("*.py")):
            ptxt = read(p)
            m = re.search(r"^CASE_TIMEOUT_SEC\s*=\s*(\d+(?:\.\d+)?)\b", ptxt, re.M)
            if not m:
                continue
            sec, prel = float(m.group(1)), p.relative_to(task).as_posix()
            bound = [(emit_cap, "the emit cap in tests/budget.json")] if emit_cap is not None else []
            bound.append((float(vt), "[verifier].timeout_sec"))
            for cap, what in bound:
                if sec >= cap:
                    fs.append(finding(prel, line_of(ptxt, m.group(0)), f"CASE_TIMEOUT_SEC {sec:g} s (one case) is "
                                      f"not below {what} {cap:g} s that bounds the whole emit phase: lower it"))
                    break
    # worst case: loops multiplied by their item count, parameters and constants followed, in legacy
    # mode too (without budget.json this sum is the only budget the task has)
    worst, parts, unbounded, uncapped = worst_case_budget(task)
    if worst + margin > vt:
        where = ", ".join(f"{w}={s:g}" + (f"x{m}" if m != 1 else "") for w, s, m in parts[:10])
        more = f", +{len(parts) - 10} more" if len(parts) > 10 else ""
        unc = f"; plus {uncapped} uncapped build or test step(s) not counted" if uncapped else ""
        fs.append(finding("task.toml", vt_line, f"worst-case timeouts add up to {worst:g} s (loops multiplied by "
                          f"their item count) against [verifier].timeout_sec {vt:g} s: {where}{more}{unc}"))
    seen_loops = set()
    for rel, ln, why in unbounded:
        if (rel, ln) in seen_loops:
            continue
        seen_loops.add((rel, ln))
        fs.append(finding(rel, ln, f"unbounded loop of capped steps: the gate cannot count this loop's items, "
                          f"so the budget has no worst case ({why})"))
    for t in tos:
        if t["sec"] >= vt:
            fs.append(finding(t["file"], t["line"], f"a single timeout of {t['sec']:g} s is not below "
                              f"[verifier].timeout_sec {vt:g} s"))
    # instruction numbers that read as time or size limits: each must be enforced (limit_enforcement), not only
    # appear as a number under tests/. A literal timeout is enforcing by itself; a budget.json cap is when test.sh
    # feeds it to one. Mentioned only: a warning. Nowhere: a finding.
    instr_p = task / "instruction.md"
    units = _code_units(task)
    warns = []

    def limit_check(n, text, values, keys=(), toml_limits=TOML_TIME_LIMITS, what="time limit", sentence=""):
        if what == "time limit" and set(values) & {t["sec"] for t in tos}:
            return
        state, where = limit_enforcement(task, values, what=what.split()[0], keys=keys, toml_limits=toml_limits,
                                         units=units)
        if state == "mentioned":
            warns.append(finding("instruction.md", n, f"the instruction's {what} of {text} is mentioned under "
                                 f"tests/ ({where}) but no enforcing construct was found (a timeout, ulimit, "
                                 "setrlimit or a comparison that fails the run)"))
        elif state == "absent" and what == "time limit" and not RUN_LIMIT.search(sentence):
            # "the runner clamps the wait to at most 20 minutes" describes the product, not a limit on the run
            warns.append(finding("instruction.md", n, f"the instruction states a {what} of {text} that no budget "
                                 "cap or test uses; the sentence does not name the run, the agent or the verifier, "
                                 "so it reads as product behaviour (warning): if it limits the run, enforce it"))
        elif state == "absent":
            fs.append(finding("instruction.md", n, f"the instruction states a {what} of {text} that no budget "
                              "cap or test uses"))

    def sentence_at(line, pos):
        for off, snt in split_sentences(line):
            if off <= pos < off + len(snt):
                return snt
        return line
    if instr_p.is_file():
        for n, ln in enumerate(strip_fences(read(instr_p)).splitlines(), 1):
            if TRAILER_RE.match(ln.strip()):
                continue
            for m in TIME_WORDS.finditer(ln):
                cue = LIMIT_CUE.search(ln[:m.start()])
                if not cue:
                    continue
                if cue.group(1).lower() in WEAK_LIMIT_CUES and not LIMIT_AFTER.match(ln[m.end():]):
                    continue
                # "every crossing time within 4 minutes" is a tolerance on an answer, not a run limit
                if cue.group(1).lower() == "within" and (re.search(
                        r"\b(every|each|error|tolerance|band|off by|accurate)\b[^.;]{0,40}$", ln[:cue.start()], re.I)
                        or re.search(r"\bcompared\b[^.;]{0,80}$", ln[:cue.start()], re.I)):
                    continue
                u = m.group(2).lower()
                mult = 3600 if u.startswith("h") else 60 if u.startswith("m") else 1
                sec = float(m.group(1)) * mult
                limit_check(n, f"{m.group(0)} ({sec:g} s)", {sec}, sentence=sentence_at(ln, m.start()))
            for m in SIZE_WORDS.finditer(ln):
                if SIZE_CUE.search(ln[:m.start()]):
                    limit_check(n, m.group(0), size_values(float(m.group(1)), m.group(2)),
                                toml_limits=TOML_SIZE_LIMITS, what="size limit")
    # the limits tests/budget.json declares are read by an enforcing construct (test.sh feeds each cap to a timeout
    # and compares the submission with max_submission_mb), not only written down
    if bud_p.is_file():
        declared = [("steps[].cap_sec", {c for _, c in caps}, ("cap_sec",), "time")] if caps else []
        if isinstance(b.get("max_submission_mb"), (int, float)):
            declared.append(("max_submission_mb", {float(b["max_submission_mb"])}, ("max_submission_mb",), "size"))
        for key, values, keys, what in declared:
            state, where = limit_enforcement(task, values, what=what, keys=keys, units=units,
                                             construct_only=what == "time")
            if state != "enforced":
                warns.append(finding("tests/budget.json", line_of(braw, key.split("[")[0]),
                                     f"{key} is declared but no enforcing construct under tests/ reads it (a timeout "
                                     "fed from the budget, or a size comparison that fails the run)"))
    # Headroom declaration (static, no runtime measurement). An enforced limit is only meaningful when the task
    # also declares the value it expects and leaves a margin above it: without a declared expected/typical value
    # and a positive margin, a cap is a number nobody has justified. These are WARNs (a task may still be sound),
    # never FAILs, so a budget that predates the convention is not blocked.
    if bud_p.is_file() and caps:
        if margin <= 0:
            warns.append(finding("tests/budget.json", line_of(braw, "margin_sec") or 1,
                                 f"margin_sec is {margin:g}: the budget declares no headroom between the step caps "
                                 f"({sum(c for _, c in caps):g} s) and [verifier].timeout_sec {vt:g} s; set a "
                                 "positive margin_sec so the caps + margin relationship is a real declared budget"))
        for name, cap, exp in step_expected:
            if exp is None:
                continue
            if cap <= exp:
                warns.append(finding("tests/budget.json", line_of(braw, f'"{name}"') or 1,
                                     f"step {name}: cap_sec {cap:g} s does not exceed its declared expected_sec "
                                     f"{exp:g} s, so there is no headroom above the typical duration"))
        if isinstance(b.get("max_submission_mb"), (int, float)) and not isinstance(b.get("max_submission_mb"), bool):
            exp_mb = b.get("expected_submission_mb", b.get("typical_submission_mb"))
            if isinstance(exp_mb, (int, float)) and not isinstance(exp_mb, bool) and float(b["max_submission_mb"]) <= float(exp_mb):
                warns.append(finding("tests/budget.json", line_of(braw, "max_submission_mb") or 1,
                                     f"max_submission_mb {b['max_submission_mb']:g} does not exceed the declared "
                                     f"expected_submission_mb {exp_mb:g}: no headroom above the expected size"))

    status = "FAIL" if fs else "PASS"
    if caps:
        worst = max(worst, sum(c for _, c in caps) + margin)
    det = (f"verifier timeout {vt:g} s; {len(caps)} budget steps; {len(tos)} literal timeouts under tests/; "
           f"worst case {worst:g} s" + ("; legacy task without tests/budget.json" if legacy_missing else "")
           + (f"; {len(warns)} limit warning(s) (not enforced or no declared headroom)" if warns else ""))
    return GateResult(status, det, fs, warns,
                      extra={"timeouts": [{k: v for k, v in t.items() if k != "full"} for t in tos],
                             "worst_case_sec": worst,
                             "headroom_declared": bool(bud_p.is_file() and caps and margin > 0)})


# ------------------------------------------------------------------ README helpers

MODEL_RE = r"(gpt-[\w.-]+|claude[\w.-]*|opus[\w.-]*|sonnet[\w.-]*|haiku[\w.-]*|gemini[\w.-]*|astra|fable|" \
           r"deepseek[\w.-]*|qwen[\w.-]*|llama[\w.-]*|grok[\w.-]*|terminus[\w.-]*)"
CLAIM_RE = re.compile(r"(\d+(?:\.\d+)?\s?%|\bpass(?:es|ed)\b|\bscored?\b|\bmeasured\b|\bcalibrated\b|\bk\s*=\s*\d|"
                      r"\bpass@\d|\b\d+\s+(?:of\s+\d+\s+)?(?:attempts?|trials?|runs?)\b|\battempts\b|\btrials\b|\b"
                      + MODEL_RE + r"\b)", re.I)
PATH_TOKEN = re.compile(r"(?<![\w/.$<>@-])((?:\.{0,2}/)?(?:[\w.-]+/)+[\w.-]*[\w]|[\w-]+\.(?:py|sh|go|rs|js|mjs|ts|json|"
                        r"toml|patch|diff|csv|yaml|yml|txt|pdf|md|log|cast|xml|html))\b")
IDENT_TOKEN = re.compile(r"(?<![\w.])([A-Za-z_][\w]*(?:\.[A-Za-z_]\w*)*)\(\)")
# Common dotted framework/library names tokenize as nonexistent ".js" file paths (Node.js, Vue.js).
# They are technology names in prose, not files in the task, so they are not checked for existence.
TECH_DOTTED = {"node.js", "express.js", "vue.js", "nuxt.js", "next.js", "nest.js", "react.js", "angular.js",
               "backbone.js", "ember.js", "d3.js", "chart.js", "three.js", "jquery.js", "socket.js",
               "babel.js", "webpack.js", "discord.js", "p5.js", "meteor.js", "knockout.js", "require.js"}


def readme_tokens(line: str):
    """Paths and identifiers on one README line: (kind, token)."""
    line = re.sub(r"https?://\S+", " ", line)
    out = []
    spans = re.findall(r"`([^`]+)`", line)
    rest = re.sub(r"`[^`]+`", " ", line)
    for s in spans:
        s = s.strip()
        m = re.fullmatch(r"([A-Za-z_][\w.]*)\(\)", s)
        if m:
            out.append(("ident", m.group(1)))
        elif " " not in s and ("/" in s or re.search(r"\.[A-Za-z][A-Za-z0-9]{0,4}$", s)):
            out.append(("path", s))
        else:
            out += [("ident", x) for x in IDENT_TOKEN.findall(s)]
    for m in PATH_TOKEN.finditer(rest):
        out.append(("path", m.group(1)))
    for m in IDENT_TOKEN.finditer(rest):
        out.append(("ident", m.group(1)))
    good = []
    for kind, t in out:
        t = t.rstrip(".,;:)")
        if kind == "path" and t.lower() in TECH_DOTTED:
            continue  # "Node.js", "Vue.js": technology names in prose, not files in the task
        if kind == "path" and not t.endswith("/") and "." not in PurePosixPath(t).name:
            continue  # "openrouter/openai/model", "owner/repo": identifiers, not files
        if not t or any(c in t for c in "<>*${}|[]") or "..." in t or t.startswith(("-", "~")) or \
                re.fullmatch(r"\.[\w.-]+", t):
            continue
        if kind == "path" and (re.fullmatch(r"[\d./]+", t) or re.fullmatch(r"\w+/\w+", t) and "." not in t
                               and not t.startswith(("tests", "solution", "environment", "evidence", "provenance"))):
            continue  # "and/or", "3/4", "km/h": prose, not paths
        good.append((kind, t))
    return good


class TaskIndex:
    def __init__(self, task: Path):
        self.task = task
        self.root = delivery_root(task)
        self.files = [p for p in task.rglob("*") if p.is_file()]
        self.rels = {p.relative_to(task).as_posix() for p in self.files}
        self.names = {p.name for p in self.files}
        self.texts = {p.relative_to(task).as_posix(): read(p) for p in task_text_files(task)}
        self.sol = {k: v for k, v in self.texts.items() if k.startswith("solution/")}
        self._made = None

    def where(self, t: str) -> str | None:
        """Where a cited path resolves: "task" (inside the task root, the only place the customer judges),
        "receipt" (only in the wrapper around the task: the delivery's evidence/ or provenance/), or None.
        X8: a wrapper receipt is never task-root evidence; callers report it separately."""
        t = t.lstrip("./") if not t.startswith("/") else t
        if t.startswith("/app/") or t == "/app":
            # an agent-image path: it lives in the environment's cloned repo unless environment/ ships it
            return "task"
        if t.startswith("/"):
            name = PurePosixPath(t).name
            hit = name in self.names or any(t in v for v in self.texts.values()) or \
                any(t.rstrip("/") in v for v in self.texts.values())
            if not hit:
                # a path the verifier or the image makes at run time: tests/test.sh writes "$LOG/write-probe.txt"
                # with LOG=/logs/verifier, so /logs/verifier/write-probe.txt is in no file as written
                if self._made is None:
                    self._made = made_at_run_time(Tree(self.task), "")[0]
                hit = t.strip("/") in self._made
            return "task" if hit else None
        t2 = t.rstrip("/")
        if (self.task / t2).exists():
            return "task"
        if any(r == t2 or r.endswith("/" + t2) or r.startswith(t2 + "/") for r in self.rels):
            return "task"
        if "/" not in t2 and t2 in self.names:
            return "task"
        if self.root and (self.root / t2).exists():
            try:
                (self.root / t2).resolve().relative_to(self.task.resolve())
                return "task"
            except ValueError:
                return "receipt"
        if self.root:
            # the packager relocates cheat/ -> evidence/cheat/ and _provenance/ -> a flat provenance/ when it
            # assembles a delivery; a task-relative cite of a shipped cheat/provenance file is still valid
            for rel in relocated_in_delivery(t2):
                if (self.root / rel).exists():
                    return "task"
        if any(re.search(r"(?<![\w-])" + re.escape(t2) + r"(?![\w-])", v) for v in self.texts.values()):
            return "task"
        return None

    def path_exists(self, t: str) -> bool:
        return self.where(t) is not None

    def ident_in(self, name: str, texts) -> bool:
        last = name.split(".")[-1]
        return any(re.search(r"(?<![\w])" + re.escape(last) + r"(?![\w])", v) for v in texts.values())


# ------------------------------------------------------------------ readme-claims

MEASURE_VERB = re.compile(r"\b(measured|scored|passed|solved|failed|ran|calibrated|validated)\b", re.I)
PASS_RATE = re.compile(r"(?<![\w/.:-])\d+/\d+(?![\w/:-]|\.\d)|(?<![\w.])\d+(?:\.\d+)?\s?%|\bpass@(?:\d+|k)\b", re.I)
TOLERANCE_PCT = re.compile(r"(?:within|under|below|above|±|\+/-|\+-|bands?(?: of)?|tolerances?(?: of)?|noise(?: of)?|"
                           r"errors?(?: of)?|up to|about|around|roughly|approximately|~|cv(?: of)?)\s*(?:±\s*)?"
                           r"\d+(?:\.\d+)?(?:\s*(?:-|to)\s*\d+(?:\.\d+)?)?\s?%", re.I)
CLAIM_SKIP_SECTION = re.compile(r"experience|author|expertise|\bbio\b|about (?:me|the author)|metadata|contributor", re.I)


NUM_WORDS = r"(?:one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|" \
            r"sixteen|twenty|thirty|forty|fifty|hundred|thousand)"
PRESENT_VERB = re.compile(r"\b(pass(?:es)?|fail(?:s)?|scores?|solves?|reproduces?)\b", re.I)
COUNT_NOUN = re.compile(r"\b(tests?|checks?|attempts?|runs?|cases?|trials?|instruments?|samples?|observations?|logs?|"
                        r"strategies|variants?|repairs?|recoveries|methods?|installations?|seeds?|subtests?)\b", re.I)
OUTCOME_VERB = re.compile(r"(passed|failed|solved)$", re.I)
DESIGN_PHRASE = re.compile(r"\bmust (?:all )?(?:pass|fail)\b|\bfor a reward(?: of \d)?\b|\bsolve\.sh\b[^.;]*", re.I)
HAS_NUMBER = re.compile(r"\d|\b" + NUM_WORDS + r"\b", re.I)


def claim_hits(sentence: str, intro: bool = False, table: bool = False):
    """Measured claims in one sentence: a number plus a measurement verb (past tense, or present tense
    with a count noun: "16 checks fail and 10 pass"), or a pass rate (k/N, N%, pass@k). A sentence that
    introduces a table or list ("were calibrated against partial repairs:") counts without a number.
    Tolerance percentages ("within 5%") are specifications, not measurements."""
    s = TOLERANCE_PCT.sub(" ", sentence)
    # "outcome" words mark a measurement/scoring sentence. They include the scoring subjects and idioms a
    # pass-rate uses ("the oracle gets 33/33", "the model achieves 8/10") so a real rate still counts, while
    # bare prose ratios ("16/9", "24/7") do not.
    outcome = re.search(r"\b(pass\w*|fail\w*|solv\w*|scor\w*|attempt\w*|trials?|worst|measured|accuracy|"
                        r"success|oracle|gets?|got|achiev\w*)\b", s, re.I)
    # a bare percentage is a claim only in an outcome sentence ("worst error was 15.8%"), not biology or spec prose;
    # likewise a bare N/M ("16/9", "24/7") is a pass-rate claim only beside an outcome word, else it is prose
    # (a ratio, a date, a version). pass@k is self-labelled and always counts.
    hits = [m.group(0) for m in PASS_RATE.finditer(s)
            if m.group(0).lower().startswith("pass@") or outcome]
    if table:
        return hits

    def near(m):  # a number within 60 characters of the verb, so "the measured demand (7)" is not a claim
        return HAS_NUMBER.search(s[max(0, m.start() - 60):m.end() + 60])
    s = DESIGN_PHRASE.sub(" ", s)
    counted = bool(re.search(r"\d", s) and COUNT_NOUN.search(s))
    past = [m for m in MEASURE_VERB.finditer(s)]
    # passed/failed/solved read as outcomes only next to a digit and a count noun ("16 checks fail")
    hits += [m.group(0) for m in past if near(m) and counted]
    if counted:
        hits += [m.group(0) for m in PRESENT_VERB.finditer(s) if near(m)]
    if intro and past and not hits:
        hits += [m.group(0) for m in past]
    return hits


def claim_numbers(sentences):
    """Numbers a receipt must contain: every figure of two or more digits, or with a decimal point."""
    out = set()
    for s in sentences:
        for m in re.finditer(r"(?<![\w.])(\d[\d,]*(?:\.\d+)?)(?![\w])", TOLERANCE_PCT.sub(" ", s)):
            v = m.group(1).replace(",", "").rstrip(".")
            if len(v.replace(".", "")) >= 2:
                out.add(v)
    return out


def cited_texts(idx, p: str, limit=200, scope="task"):
    """Texts of the file (or the files under the directory) a README path names. scope "task" reads the
    task root only; scope "receipt" reads the wrapper (delivery root) only."""
    t = p.lstrip("./").rstrip("/")
    roots = [idx.task] if scope == "task" else ([idx.root] if idx.root else [])
    out = []
    for r in roots:
        q = r / t
        files = [q] if q.is_file() else sorted(x for x in q.rglob("*") if x.is_file())[:limit] if q.is_dir() else []
        for f in files:
            if f.stat().st_size < 3_000_000:
                out.append(read(f))
        if out:
            break
    return out


RECEIPT_ONLY = "receipt-only"


def receipt_only(path, line, message):
    """A claim, cited path or generator that resolves only in the wrapper (evidence/, provenance/) around the
    task. The customer judges each task root alone (X8), so it is reported apart from FAIL findings and blocks
    until a reviewer dispositions it (gates.py dispose)."""
    f = finding(path, line, "receipt-only: " + message)
    f["kind"] = RECEIPT_ONLY
    f["needs_disposition"] = True
    return f


def evidence_status(fs) -> str:
    """FAIL when any finding is a real defect; FAIL-PENDING-DISPOSITION when every finding is receipt-only."""
    if any(f.get("kind") != RECEIPT_ONLY for f in fs):
        return "FAIL"
    return "FAIL-PENDING-DISPOSITION" if fs else "PASS"


def gate_readme_claims(task: Path) -> GateResult:
    rp = task / "README.md"
    if not rp.is_file():
        return GateResult("ERROR", "README.md is missing")
    text = strip_fences(read(rp))
    sec = sections(text)
    idx = TaskIndex(task)
    fs, nclaims = [], 0
    for start, block in paragraphs(text):
        if CLAIM_SKIP_SECTION.search(sec.get(start, "")) or block.lstrip().startswith("#") or \
                re.match(r"\s*(This is the work of|I am|I have been|I'm)\b", block):
            continue  # author bio
        sents = [s for _, s in split_sentences(block.replace("\n", " "))]
        table = block.lstrip().startswith("|")
        hits = [(s, claim_hits(s, intro=s.rstrip().endswith(":") and i == len(sents) - 1, table=table))
                for i, s in enumerate(sents)]
        claims = [h for _, hs in hits for h in hs]
        if not claims:
            continue
        nclaims += 1
        claim_sents = [s for s, hs in hits if hs]
        nums = claim_numbers(claim_sents)
        paths = [t for k, t in readme_tokens(block.replace("\n", " ")) if k == "path" and not t.startswith("/")]
        where = {p: idx.where(p) for p in paths}
        existing = [p for p in paths if where[p]]

        def holds(cands, scope):
            ok = False
            for p in cands:
                texts = cited_texts(idx, p, scope=scope)
                if not nums or not texts:
                    ok = ok or not nums
                    continue
                if any(re.search(r"(?<![\d.])" + re.escape(n) + r"(?![\d])", t.replace(",", ""))
                       for t in texts for n in nums):
                    return True
            return ok
        in_task = [p for p in existing if where[p] == "task"]
        receipts = [p for p in existing if where[p] == "receipt"]
        if holds(in_task, "task"):
            continue
        snippet = norm(block)[:140]
        label = ", ".join(dict.fromkeys(c.strip() for c in claims[:4]))
        if receipts and holds(receipts, "receipt"):
            fs.append(receipt_only("README.md", start, f"measured claim ({label}) is backed only by "
                                   f"{', '.join(receipts[:3])}, outside the task root; a reviewer judging the task "
                                   f"alone cannot check it: move the receipt into the task, drop the claim, or "
                                   f"record a disposition: \"{snippet}\""))
            continue
        if existing:
            why = f"; cited {', '.join(existing[:3])} exist but hold none of the claimed numbers ({', '.join(sorted(nums)[:4])})"
        else:
            why = f"; cited {', '.join(paths[:3])} not found" if paths else ""
        fs.append(finding("README.md", start, f"measured claim ({label})"
                          f" cites no file that exists in the task root and holds the claim{why}: \"{snippet}\""))
    nrec = sum(1 for f in fs if f.get("kind") == RECEIPT_ONLY)
    return GateResult(evidence_status(fs),
                      f"{nclaims} README blocks carry measured claims; {len(fs) - nrec} have no receipt holding the "
                      f"claim in the task root; {nrec} are receipt-only (wrapper evidence, needs a disposition)", fs)


# ------------------------------------------------------------------ readme-code

EVERY_DOC = re.compile(r"\b(every|all|each)\s+(?:of\s+the\s+)?(document|record|file|log|input)s?\b", re.I)


def doc_phrase(stem: str) -> str | None:
    words = [w for w in re.split(r"[_\-\s]+", stem.lower()) if w]
    if not words or len(words) > 4 or any(re.search(r"\d", w) for w in words):
        return None
    if not any(len(w) >= 3 for w in words):
        return None
    return " ".join(words)


TASK_TOPS = {"tests", "solution", "environment", "cheat", "_provenance", "evidence", "provenance", "steps"}


def repo_task(task: Path) -> bool:
    """The environment holds a repository at a pinned commit: tests/grading.json names a base_commit, or the
    environment Dockerfile clones or fetches one."""
    g = task / "tests" / "grading.json"
    try:
        if g.is_file() and json.loads(read(g)).get("base_commit"):
            return True
    except (ValueError, AttributeError):
        pass
    df = task / "environment" / "Dockerfile"
    return df.is_file() and bool(re.search(r"\bgit\s+(?:clone|fetch|checkout)\b", read(df)))


def repo_relative(task: Path, t: str) -> bool:
    """A README path relative to the root of the repository the environment holds (a repo task only): relative,
    with a directory, and not under the task's own top-level names (tests/, solution/, environment/, ...) or
    anything else that sits in the task folder."""
    if t.startswith(("/", "./", "../")) or "/" not in t.strip("/") or not repo_task(task):
        return False
    top = t.split("/", 1)[0]
    own = {p.name for p in task.iterdir()} if task.is_dir() else set()
    return top not in TASK_TOPS and top not in own


def gate_readme_code(task: Path) -> GateResult:
    rp = task / "README.md"
    if not rp.is_file():
        return GateResult("ERROR", "README.md is missing")
    raw = read(rp)
    text = strip_fences(raw)
    sec = sections(text)
    idx = TaskIndex(task)
    fs, warns, seen = [], [], set()
    ntok = 0
    for n, ln in enumerate(text.splitlines(), 1):
        in_sol = "solution" in sec.get(n, "")
        for kind, t in readme_tokens(ln):
            ntok += 1
            key = (kind, t, in_sol)
            if key in seen:
                continue
            seen.add(key)
            if kind == "path":
                w = idx.where(t)
                if w is None and repo_relative(task, t):
                    # "omnigent/scheduler/dispatch.py": a file of the repository the image clones, cited relative
                    # to its root. Like an /app path, it lives in the environment, not in the task folder.
                    warns.append(finding("README.md", n, f"path {t!r} is not in the task; read as a path in the "
                                         "environment's repository (like /app/...), not checked"))
                elif w is None:
                    fs.append(finding("README.md", n, f"path {t!r} does not exist in the task"
                                      + (" or its delivery" if idx.root else "")))
                elif w == "receipt":
                    fs.append(receipt_only("README.md", n, f"path {t!r} exists only in the delivery wrapper, outside "
                                           f"the task root; cite it as a receipt only, or move it into the task"))
                continue
            pool = idx.sol if in_sol else idx.texts
            if not idx.ident_in(t, pool):
                where = "solution/" if in_sol else "the task (README excluded)"
                fs.append(finding("README.md", n, f"identifier {t}() is not found in {where}"))
            elif in_sol:
                last = t.split(".")[-1]
                allsol = "\n".join(idx.sol.values())
                defs = len(re.findall(r"\b(?:def|func|function|fn)\s+" + re.escape(last) + r"\s*\(", allsol))
                uses = len(re.findall(r"(?<![\w.])" + re.escape(last) + r"\s*\(", allsol)) - defs
                if defs and uses <= 0:
                    # a public helper the tests call, or the instruction names, is used: the checker is its caller
                    called = re.compile(r"(?<![\w.])" + re.escape(last) + r"\s*\(")
                    named = re.compile(r"(?<![\w])" + re.escape(last) + r"(?![\w])")
                    instr_text = read(task / "instruction.md") if (task / "instruction.md").is_file() else ""
                    used = any(called.search(v) for k, v in idx.texts.items() if k.startswith("tests/")) \
                        or bool(named.search(instr_text))
                    if not used:
                        fs.append(finding("README.md", n, f"{t}() is defined in solution/ but never called"))
    # input documents the README or solution_explanation says the solution reads
    env = task / "environment"
    docs = {}
    if env.is_dir():
        for p in env.rglob("*"):
            if p.is_file() and p.name != "Dockerfile" and p.suffix.lower() not in CODE_EXT:
                ph = doc_phrase(p.stem)
                if ph:
                    docs.setdefault(ph, (p.stem, p.relative_to(task).as_posix()))
    sol_all = "\n".join(idx.sol.values()).lower()
    if docs and sol_all:
        used = {ph for ph, (stem, _) in docs.items() if stem.lower() in sol_all}
        if used:  # a document-reading solution
            try:
                se = str((load_toml(task).get("metadata") or {}).get("solution_explanation", ""))
            except Exception:
                se = ""
            toml_raw = read(task / "task.toml") if (task / "task.toml").is_file() else ""
            se_line = line_of(toml_raw, "solution_explanation")
            claims_all = bool(EVERY_DOC.search(se)) or any(
                EVERY_DOC.search(l) for i, l in enumerate(text.splitlines(), 1) if "solution" in sec.get(i, ""))
            low = lambda s: re.sub(r"['’]s\b", "s", s.lower()).replace("_", " ").replace("-", " ")
            for ph, (stem, rel) in sorted(docs.items()):
                if ph in used:
                    continue
                pat = re.compile(r"\b" + re.escape(ph) + r"s?\b")
                hit_sol = [i for i, l in enumerate(text.splitlines(), 1)
                           if "solution" in sec.get(i, "") and pat.search(low(l))]
                hit_any = [i for i, l in enumerate(text.splitlines(), 1) if pat.search(low(l))]
                msg = f"README describes the {ph} ({rel}) but no file in solution/ references {stem}"
                if hit_sol:
                    fs.append(finding("README.md", hit_sol[0], msg))
                elif claims_all:
                    fs.append(finding("task.toml" if EVERY_DOC.search(se) else "README.md",
                                      se_line if EVERY_DOC.search(se) else (hit_any[0] if hit_any else 0),
                                      f"the solution is said to read every document, but no file in solution/ "
                                      f"references {rel}" + (f" (README mentions the {ph} at line {hit_any[0]})"
                                                             if hit_any else "")))
                elif hit_any:
                    warns.append(finding("README.md", hit_any[0], msg))
    fs += number_crosscheck(task, idx)
    gfs, gwarns = generator_shipped(task, idx)
    fs += gfs
    warns += gwarns
    fs += tolerance_crosscheck(task)
    nrec = sum(1 for f in fs if f.get("kind") == RECEIPT_ONLY)
    return GateResult(evidence_status(fs),
                      f"{ntok} README references checked; {len(fs) - nrec} dangling, unbacked or inconsistent; "
                      f"{nrec} receipt-only (wrapper evidence, needs a disposition)", fs, warns)


TRUTH_SOURCE = re.compile(
    r"\b(?:truth|expected (?:output|outcomes?|rows|values|answers|files|results)|answer key|reference (?:data|output|"
    r"values)|graded (?:data|values|rows|inputs|batch|worklist))\b[^.;]{0,120}?\b(?:generated|simulated|synthesi[sz]ed|"
    r"computed|produced|converted|derived|(?:is|are) the (?:actual )?output of)\b"
    r"|\b(?:data|documents?|inputs?|fixtures?|cases?|records?|logs?|texts?|files?)\b[^.;]{0,60}?\b(?:(?:is|are|was|were) "
    r"(?:\w+ )?(?:generated|simulated|synthesi[sz]ed)|(?:is|are) (?:all )?synthetic)\b", re.I)
GEN_NAME = re.compile(r"(gen|generat|sim|synth|make_|build_|truth|render|convert|world|degrade|fixture)", re.I)
CODE_SUFFIX = (".py", ".sh", ".js", ".mjs", ".ts", ".go", ".rs", ".r", ".jl", ".ipynb", ".pl", ".rb", ".c", ".cpp")


def tolerance_crosscheck(task: Path) -> list:
    """A tolerance the README states that no test uses, when a test uses a different one of the same scale
    ("0.03 for a reported estimate" in the README, 0.05 in the code)."""
    if not (task / "README.md").is_file():
        return []
    tols = set(test_tolerances(task))
    if not tols:
        return []
    fs, seen = [], set()
    for n, ln in enumerate(strip_fences(read(task / "README.md")).splitlines(), 1):
        for m in re.finditer(r"\b(?:tolerances?|bands?)\b(?:\s+(?:is|of|=|are|at))?\s+(?:±\s*)?(\d+\.\d+)(?![\w.])", ln, re.I):
            r = float(m.group(1))
            dec = len(m.group(1).split(".")[1])
            if r in tols or r * 0.01 in tols or r in seen or r <= 0:
                continue
            close = [t for t in tols if 0.25 <= r / t <= 4 and len(repr(t).split(".")[-1]) == dec and t != r]
            if close:
                seen.add(r)
                fs.append(finding("README.md", n, f"states a tolerance of {m.group(1)}, but the tests compare with "
                                  f"{', '.join(f'{t:g}' for t in sorted(close))}"))
    return fs


def generator_shipped(task: Path, idx):
    """README, task.toml or PROVENANCE.json say the truth or the data come from a generator, simulation or
    conversion: the generator must ship INSIDE the task root (a generator-named script under tests/), where the
    customer can run it (X8). Returns (findings, warnings). Generator code only in the wrapper's provenance/ is
    a receipt-only finding; a task-root generator nothing in tests/ consumes (tests/Dockerfile RUN line,
    test.sh or a test file) is a warning."""
    root = idx.root
    srcs = []
    if (task / "README.md").is_file():
        srcs.append(("README.md", strip_fences(read(task / "README.md"))))
    if (task / "task.toml").is_file():
        srcs.append(("task.toml", read(task / "task.toml")))
    if root:
        for pj in root.glob("provenance/**/PROVENANCE.json"):
            srcs.append((pj.relative_to(root).as_posix(), read(pj)))
    hit = None
    for rel, txt in srcs:
        for n, ln in enumerate(txt.splitlines(), 1):
            m = TRUTH_SOURCE.search(ln)
            if m and not re.search(r"\b(not|never|no)\b", m.group(0), re.I) and not re.search(
                    r"\bby (?:the (?:library|program|code under test|engine|package)|\w+ itself)|\bitself\b|\bis real\b",
                    ln[m.start():m.end() + 60], re.I):
                hit = (rel, n, ln.strip()[:160])
                break
        if hit:
            break
    if not hit:
        return [], []
    tdir = task / "tests"
    in_task = sorted(p.relative_to(task).as_posix() for p in (tdir.rglob("*") if tdir.is_dir() else [])
                     if p.is_file() and p.suffix.lower() in CODE_SUFFIX and GEN_NAME.search(p.stem)
                     and not re.search(r"test|check", p.stem, re.I))
    readme = read(task / "README.md") if (task / "README.md").is_file() else ""
    if in_task:
        dirs = {str(PurePosixPath(x).parent) for x in in_task}
        if not any(x in readme or PurePosixPath(x).name in readme for x in in_task) and \
                not any(d in readme for d in dirs if d not in ("tests", ".")):
            return [finding("README.md", 0, f"the task ships generator code ({', '.join(in_task[:3])}) but the README "
                            f"never names its path: point the verification section at it")], []
        consumers = ""
        for q in (tdir.rglob("*") if tdir.is_dir() else []):
            if q.is_file() and q.relative_to(task).as_posix() not in in_task and q.stat().st_size < 2_000_000:
                txt = read(q)
                if q.name == "Dockerfile":
                    txt = "\n".join(ln for _, ln in logical_lines(txt) if re.match(r"\s*RUN\s", ln, re.I))
                consumers += txt + "\n"
        unused = [x for x in in_task if PurePosixPath(x).name not in consumers]
        if len(unused) == len(in_task):
            return [], [finding(in_task[0], 0, f"generator code ships in tests/ ({', '.join(in_task[:3])}) but nothing "
                                "in tests/ runs it (no RUN line in tests/Dockerfile, no call from test.sh or a test "
                                "file): the hardcoded truth is not regenerated or validated through a consumed path")]
        return [], []
    receipts = []
    if root:
        for p in root.rglob("*"):
            if not p.is_file() or p.suffix.lower() not in CODE_SUFFIX:
                continue
            r = p.relative_to(root).as_posix()
            if r.startswith("provenance/") and "/controls/" not in r and "/artifacts/" not in r and "/agent/" not in r:
                receipts.append(r)
    if receipts:
        return [receipt_only(hit[0], hit[1], f"says the truth or data come from a generator (\"{hit[2]}\"), but the "
                             f"generator code ships only in the wrapper ({', '.join(sorted(receipts)[:3])}), outside the "
                             f"task root: move it under tests/ and run it from tests/Dockerfile, or disposition it")], []
    # The computation may live in solution/ (a generator-named script a reviewer can read even though the
    # agent never sees it): the answers are then auditable, so this is a disposition, not a hard FAIL.
    # "data is synthetic" / "values are computed from the formula" is a routine clarifier when the generator
    # ships in solution/. A plain solve.sh is NOT a truth generator; only a generator-named script counts,
    # exactly as the tests/ scan above decides. A task with no generator anywhere stays the real FAIL.
    sdir = task / "solution"
    sol_gen = sorted(p.relative_to(task).as_posix() for p in (sdir.rglob("*") if sdir.is_dir() else [])
                     if p.is_file() and p.suffix.lower() in CODE_SUFFIX
                     and GEN_NAME.search(p.stem) and not re.search(r"test|check", p.stem, re.I))
    if sol_gen:
        return [receipt_only(hit[0], hit[1], f"says the truth or data come from a generator, simulation or "
                             f"computation (\"{hit[2]}\"); no generator ships under tests/, but solution/ carries the "
                             f"computation ({', '.join(sol_gen[:3])}): move it under tests/ so the customer can "
                             f"regenerate it, or disposition it")], []
    return [finding(hit[0], hit[1], f"says the truth or data come from a generator, simulation or conversion "
                    f"(\"{hit[2]}\"), but the task ships no generator code (a generator script under tests/): nobody "
                    f"can regenerate or audit the answers")], []


COUNT_STATED = re.compile(r"(?<![\w.,/-])(\d{1,3}(?:,\d{3})+|\d+)\s+(?:graded\s+|named\s+|parametri[sz]ed\s+|behaviour\s+|"
                          r"per-\w+\s+)?(tests|checks|test cases|subtests|graded checks)\b", re.I)
FLOOR_STATED = re.compile(r"\bfloors?\b(?:\s+(?:of|is|=|at))?\s+(\d[\d,]*)", re.I)
# a line that counts the task's own data ("18 joints, 18 tests and 567 readings": bridge load tests), not verifier tests
DATA_COUNT = re.compile(r"\b\d[\d,]*\s+(?:[a-z][a-z-]*\s+)?([a-z][a-z-]*s)\b", re.I)
NOT_DATA = {"tests", "checks", "subtests", "cases", "those", "these", "others", "items", "runs", "attempts", "is", "was"}
# a count a shipped record states ("tests: 229" in solution/records/...): measured, so not a stale number
RECORDED_COUNT = re.compile(r"\btests?\b[\"']?\s*[:=]\s*(\d[\d,]*)", re.I)


def counts_data(ln: str) -> bool:
    return sum(1 for m in DATA_COUNT.finditer(ln) if m.group(1).lower() not in NOT_DATA) >= 2


def recorded_counts(task: Path) -> set[int]:
    out: set[int] = set()
    for sub in ("solution", "tests"):
        d = task / sub
        for p in sorted(d.rglob("*"))[:2000] if d.is_dir() else []:
            if p.is_file() and p.suffix.lower() in (".txt", ".md", ".json", ".csv", ".log") and p.stat().st_size < 2_000_000:
                out |= {int(m.group(1).replace(",", "")) for m in RECORDED_COUNT.finditer(read(p))}
    return out


def grading_floor(task: Path) -> int | None:
    """The v2 template keeps the verifier's floor in tests/grading.json (suite.floor), not in a FLOOR= line."""
    try:
        f = (json.loads(read(task / "tests/grading.json")).get("suite") or {}).get("floor")
        return int(f) if f is not None else None
    except Exception:
        return None


def graded_receipt(ctrf: Path) -> int:
    """The graded test count of an oracle's ctrf.json. A verifier that publishes the repository suite's per-test
    statuses after the judge's graded tests (suite-ctrf.json beside it, appended to the published report:
    mysql-session-parity, union-reads-old) holds its floor to the judge's tests alone, so those appended entries
    are not counted. They are left out only when they are exactly the tail of the report: the entries of a
    suite-ctrf.json beside it (a ctrf report or a bare list of tests), or a trailing block named
    "repository-suite::..." (regional-meter-settlement keeps its suite file inside the verifier's work folder)."""
    tests = json.loads(read(ctrf))["results"]
    n = int(tests["summary"]["tests"])
    names = [t.get("name") if isinstance(t, dict) else None for t in tests.get("tests") or []]
    if len(names) != n:
        return n
    side = ctrf.parent / "suite-ctrf.json"
    if side.is_file():
        try:
            doc = json.loads(read(side))
            suite = [t.get("name") for t in (doc if isinstance(doc, list) else doc["results"]["tests"])]
        except Exception:
            suite = []
        if suite and len(suite) < n and names[-len(suite):] == suite:
            return n - len(suite)
    tail = 0
    while tail < n and str(names[n - 1 - tail] or "").startswith("repository-suite::"):
        tail += 1
    return n - tail if tail < n else n


def number_crosscheck(task: Path, idx) -> list:
    """Counts the prose states (README, DELIVERY, test docstrings) against the verifier's FLOOR and the
    oracle's receipt: a stale or rounded number is a claim nobody re-measured."""
    fs = []
    sh = read(task / "tests/test.sh") if (task / "tests/test.sh").is_file() else ""
    floors = {int(m.group(1)) for m in re.finditer(r"(?m)^\s*(?:export\s+)?\w*FLOOR\w*=[\"']?(\d+)", sh)}
    for p in (task / "tests").glob("*.txt") if (task / "tests").is_dir() else []:
        floors |= {int(x) for x in re.findall(r"(?m)^#\s*floor\s+(\d+)\s*$", read(p))}
    receipt = None
    root = idx.root
    if root:
        for c in sorted(root.glob("evidence/oracle*/**/ctrf.json")):
            try:
                receipt = graded_receipt(c)
                break
            except Exception:
                continue
        if receipt is None and (root / "MANIFEST.json").is_file():
            try:
                receipt = int(json.loads(read(root / "MANIFEST.json"))["controls"]["oracle"]["ctrf"]["tests"])
            except Exception:
                pass
    if floors and receipt is not None and receipt not in floors:
        fl = re.search(r"(?m)^\s*(?:export\s+)?\w*FLOOR\w*=", sh)
        fs.append(finding("tests/test.sh", sh[:fl.start()].count("\n") + 1 if fl else 0, f"FLOOR {', '.join(map(str, sorted(floors)))} but the "
                          f"oracle receipt reports {receipt} tests: a floor below the real count lets graded tests "
                          f"go missing silently, one above it fails the oracle"))
    known = floors | ({receipt} if receipt is not None else set())
    if not known:                                   # nothing measured to compare with (a bare task, no receipt)
        return fs
    gfloor = grading_floor(task)
    if gfloor is not None:
        known.add(gfloor)
    recorded = recorded_counts(task)
    texts = [("README.md", read(task / "README.md"))] if (task / "README.md").is_file() else []
    if root and (root / "DELIVERY.md").is_file():
        texts.append(("DELIVERY.md", read(root / "DELIVERY.md")))
    for p in sorted((task / "tests").glob("*.py")) if (task / "tests").is_dir() else []:
        try:
            tree = ast.parse(read(p))
        except SyntaxError:
            continue
        for nd in ast.walk(tree):
            if isinstance(nd, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                ds = ast.get_docstring(nd, clean=False)
                if ds:
                    texts.append((p.relative_to(task).as_posix(), ds))
    top = max(known)
    seen = set()
    for rel, txt in texts:
        for n, ln in enumerate(strip_fences(txt).splitlines(), 1):
            for m in FLOOR_STATED.finditer(ln):
                ctx = ln[max(0, m.start() - 50):m.end() + 50]
                if not re.search(r"FLOOR|\b(tests?|checks?|collected|verifier|ctrf|graded)\b", ctx):
                    continue  # "the balcony of floor 49"
                v = int(m.group(1).replace(",", ""))
                if floors and v not in floors and (rel, v) not in seen:
                    seen.add((rel, v))
                    fs.append(finding(rel, n, f"states a floor of {v}, but test.sh FLOOR is "
                                      f"{', '.join(map(str, sorted(floors)))}"))
            for m in COUNT_STATED.finditer(ln):
                v = int(m.group(1).replace(",", ""))
                if v in known or v in recorded or (rel, v) in seen or not (0.8 * top <= v <= 1.25 * top) or v < 10 or counts_data(ln):
                    continue
                seen.add((rel, v))
                fs.append(finding(rel, n, f"states {m.group(0)!r}, but the verifier's floor is "
                                  f"{', '.join(map(str, sorted(floors))) or 'unset'}"
                                  + (f" and the oracle receipt reports {receipt}" if receipt is not None else "")))
    # prose against prose and receipts: two counts of the same thing that differ by a few are a stale number
    stmts = []
    for rel, txt in texts:
        for n, ln in enumerate(strip_fences(txt).splitlines(), 1):
            for m in COUNT_STATED.finditer(ln):
                if not counts_data(ln) and int(m.group(1).replace(",", "")) not in recorded:
                    stmts.append((int(m.group(1).replace(",", "")), rel, n, m.group(0)))
    if root:
        for rp in sorted(list(root.glob("provenance/**/*.txt")) + list(root.glob("provenance/**/*.md"))
                         + list(root.glob("evidence/**/*.txt")))[:400]:
            if "/attempt" in rp.as_posix() or "/agent/" in rp.as_posix() or rp.stat().st_size > 500_000:
                continue
            rrel = rp.relative_to(root).as_posix()
            for n, ln in enumerate(read(rp).splitlines()[:400], 1):
                for m in re.finditer(r"(?<![\w.])(\d+)\s*(?:/|of)\s*(\d+)\s+(tests|checks|subtests|cases)\b|"
                                     r"(?<![\w.])(\d+)/(\d+)(?![\w/])", ln):
                    v = int(m.group(2) or m.group(5))
                    stmts.append((v, rrel, n, m.group(0).strip()))
        if (root / "MANIFEST.json").is_file():
            try:
                mo = json.loads(read(root / "MANIFEST.json"))["controls"]["oracle"]["ctrf"]["tests"]
                stmts.append((int(mo), "MANIFEST.json", 0, f"controls.oracle.ctrf.tests = {mo}"))
            except Exception:
                pass
    prose = [x for x in stmts if not x[1].startswith(("provenance/", "evidence/", "MANIFEST"))]
    for v, rel, n, txt in prose:
        if v < 20 or (rel, v) in seen:
            continue
        near_ = [w for w in stmts if w[1] != rel and w[0] != v and abs(w[0] - v) <= max(3, 0.02 * v)]
        if near_:
            w = near_[0]
            seen.add((rel, v))
            fs.append(finding(rel, n, f"states {txt!r}, but {w[1]}" + (f":{w[2]}" if w[2] else "")
                              + f" says {w[3]!r}: one of the two counts is stale"))
    return fs


# ------------------------------------------------------------------ structure

def runner_wrappers(sh: str) -> set[str]:
    names = set()
    for m in re.finditer(r"^\s*(?:function\s+)?(\w+)\s*\(\)\s*\{(.*?)^\s*\}", sh, re.M | re.S):
        if re.search(r"\b(setpriv|runuser|gosu|su-exec|sudo\s+-u|su\s)", m.group(2)):
            names.add(m.group(1))
    for m in re.finditer(r"^\s*(?:function\s+)?(\w+)\s*\(\)\s*\{([^\n}]*)\}", sh, re.M):
        if re.search(r"\b(setpriv|runuser|gosu|su-exec|sudo\s+-u|su\s)", m.group(2)):
            names.add(m.group(1))
    return names


WRAP_RE = re.compile(r"\b(setpriv|runuser|gosu|su-exec)\b|\bsudo\s+-u\b|\bsu\s+(?:-\s+)?\w+\s+-c\b")
RUNNER_DEFAULT = {"nobody", "runner", "1500", "65534"}
SETUP_CMDS = {"mkdir", "chown", "chmod", "rm", "rmdir", "mktemp", "cd", "pushd", "popd", "ln", "touch", "export",
              "local", "readonly", "declare", "[", "[[", "test", "echo", "printf", "true", "false", ":", "command",
              "pkill", "pgrep", "kill", "killall", "sleep", "wait", "for", "while", "until", "if", "then", "elif",
              "else", "fi", "do", "done", "case", "esac", "return", "exit", "set", "unset", "trap", "umask", "id",
              "stat", "ls", "find", "shift", "break", "continue", "read", "type", "hash", "ulimit", "!", "time",
              "infra", "finish", "write_reward", "seq"}
DATA_ART = re.compile(r"(^|/)(output|outputs|results?|out)(/|$)|\.(json|jsonl|ndjson|csv|tsv|txt|xml|ya?ml|npz|parquet)$",
                      re.I)
CODE_RUN_RE = re.compile(r"\b(subprocess|Popen|os\.system|os\.exec\w*|runpy|importlib|exec\()")
WORKTREE_ROOTS = ("/app", "/pristine", "/opt/pristine", "/tests")


# What counts as ENFORCING a promise (X5; pipeline doc s2.2: "a venv and -I -S are not adversarial sandboxes").
# Network: an actual network-off mechanism around the submitted program (a new network namespace, a container
# without a network, a firewall, a downed interface) or a connect probe the verifier expects to fail.
# allow_internet = false and an in-process socket monkeypatch no longer count. Standard library: a NEGATIVE
# probe (importing a representative non-stdlib package fails in the runtime the submission uses) or a runtime
# whose site-packages path is proven empty; python -S, -I, --no-site-packages or an empty venv alone do not count.
NET_MECHANISM = re.compile(r"unshare\s+[^|;&\n]*(?:-\w*n\b|--net)|--net(?:work)?[= ]none|network_mode:?\s*=?\s*[\"']?none|"
                           r"\biptables\b|\bnft\s|ip\s+link\s+set\s+\S+\s+down", re.I)
NET_PROBE = re.compile(
    r"pytest\.raises\(\s*\(?\s*(?:OSError|ConnectionError|ConnectionRefusedError|TimeoutError|socket\.\w+|"
    r"urllib\.error\.URLError)[\s\S]{0,400}?(?:create_connection|\.connect(?:_ex)?\(|urlopen|getaddrinfo)"
    r"|connect_ex\([^)\n]*\)\s*!=\s*0"
    r"|(?:\bcurl\b|\bwget\b|\bnc\b|/dev/tcp/)[^\n]*(?:&&|\bthen\b)[^\n]*(?:exit\s+[1-9]|\bfail)", re.I)
STDLIB_PROBE = re.compile(
    r"pytest\.raises\(\s*\(?\s*(?:ModuleNotFoundError|ImportError)[\s\S]{0,300}?(?:\bimport\b|import_module|__import__)"
    r"|find_spec\(\s*[\"'][\w.]+[\"']\s*\)\s+is\s+None"
    r"|[\"']-c[\"']\s*,\s*[\"']\s*import\s+[\w.]+[\s\S]{0,300}?returncode\s*(?:!=\s*0|==\s*1|>\s*0)"
    r"|-c\s+[\"']\s*import\s+[\w.]+[^\n]*(?:&&|\bthen\b)[^\n]*(?:exit\s+[1-9]|\bfail)"
    r"|assert\s+not\s+[^\n]*(?:site-packages|getsitepackages|getusersitepackages)"
    r"|assert\s+[^\n]*(?:site-packages|getsitepackages)[^\n]*==\s*(?:\[\]|0|set\(\)|\(\))"
    r"|(?:\[\s+|\btest\s+)-z\s+\"\$\((?:ls|find)\b[^\n]*site-packages", re.I)
WEAK_STDLIB = re.compile(r"\bpython[\d.]*\s+(?:-[A-Za-z]*\s+)*-[A-Za-z]*[SI]\b|--no-site-packages|-m\s+venv\b")
# A promise is worded as one: a negation or an obligation ("no network", "without network access", "only the
# standard library", "must not use"). A bare mention ("the standard library's monotonic clock", "network access
# errors", "an offline replica") describes the product and promises nothing.
NET_SAID = re.compile(r"\b(no network|without (?:a |any )?network|no internet|(?:no|without|not|never|cannot|"
                      r"can't|must not|may not)\b[^.;]{0,40}\b(?:network|internet) access|"
                      r"(?:works?|runs?|operates?|must (?:work|run|operate)|is|are|stays?) (?:fully |entirely )?"
                      r"offline|offline[- ]only)\b", re.I)
STDLIB_SAID = re.compile(r"\b(?:only|just|nothing (?:but|beyond|except)|no more than|limited to|restricted to)\b"
                         r"[^.;]{0,30}\bstandard library\b|\bstandard library\b[^.;]{0,15}\bonly\b|"
                         # the runtime the submission gets: "runs with Python 3.12 and its standard library"
                         r"\b(?:runs?|running|executes?|is available|are available|installed|provided)\b"
                         r"(?:[^.;]|\.(?=\d)){0,40}"
                         r"\b(?:its|the) standard library\b(?!['’])|"
                         r"\bno other packages?\b|\b(?:must not|may not|cannot|do not|does not|never|without)\s+"
                         r"(?:use|install|import|add|need|require|rely on|using|installing)\b[^.;]{0,50}"
                         r"\b(?:third[- ]party|external|non[- ]standard|pip|packages?|libraries|dependencies)\b|"
                         r"\bno (?:third[- ]party|external|non[- ]standard) (?:packages?|libraries|dependencies|modules)\b",
                         re.I)
PROMISES = {
    "network": (NET_SAID,
                None,
                "a network-off mechanism around the submitted program (unshare -n, --network none, network_mode "
                "none, iptables) or a connect probe the verifier expects to fail; allow_internet = false or a "
                "socket monkeypatch is not enforcement"),
    "standard library": (STDLIB_SAID,
                         None,
                         "a negative probe in the verifier (importing a representative non-stdlib package fails in "
                         "the runtime the submission uses) or a runtime whose site-packages path is proven empty; "
                         "python -S, -I or an empty venv alone is not enforcement"),
    "no writes": (re.compile(r"\bread-only\b|\bno writes?\b|\bmust not (?:write|modify|change)\b|\bnever writes?\b|"
                             r"\b(?:nothing|no file)\b[^.;]{0,60}\bmay be (?:modified|changed|written)", re.I),
                  re.compile(r"chmod\s+(?:-R\s+)?(?:[augo]*-w|0?[45][0-7][0-7])\b|:ro\b|mount\s+-o\s+ro|read_only:\s*true|"
                             r"chattr\s+\+i|sha256sum|hashlib|\bcmp\s|diff\s+-r|chown\s+-R\s+root", re.I),
                  "a read-only mount, chmod a-w on the protected paths, or a checksum comparison"),
}


def promise_enforced(kind: str, blob: str) -> bool:
    if kind == "network":
        return bool(NET_MECHANISM.search(blob) or NET_PROBE.search(blob))
    if kind == "standard library":
        return bool(STDLIB_PROBE.search(blob))
    return bool(PROMISES[kind][1].search(blob))


# "Python 3.12 with numpy 2.3.3, scipy 1.16.2 and the standard library" allows packages: no -S demand then
ALLOWED_DEPS = re.compile(r"\b(numpy|scipy|pandas|requests|lxml|pillow|matplotlib|scikit-learn|sklearn|pyyaml|"
                          r"networkx|sympy|torch)\b|\b(?!python\b|cpython\b)[a-z][\w-]+ \d+\.\d+(?:\.\d+)?\s*(?:,|and)", re.I)
OFFLINE_TOOLS = re.compile(r"--offline|CARGO_NET_OFFLINE|GOPROXY=off|PIP_NO_INDEX|HF_HUB_OFFLINE|npm_config_offline", re.I)


def promise_findings(task: Path) -> list:
    """Environment promises in instruction.md (no network, standard library only, no writes) that no
    verifier file enforces."""
    ip = task / "instruction.md"
    if not ip.is_file():
        return []
    blob = ""
    for p in sorted((task / "tests").rglob("*")) if (task / "tests").is_dir() else []:
        if p.is_file() and p.suffix in (".sh", ".py", ".yaml", ".yml", ".toml", ".json", "") and p.stat().st_size < 2_000_000:
            blob += read(p) + "\n"
    if (task / "task.toml").is_file():
        blob += read(task / "task.toml")
    out = []
    for kind, (said, enforced, how) in PROMISES.items():
        cands = [(n, sn) for n, sn in instruction_sentences(read(ip)) if said.search(sn)]
        strong = [c for c in cands if not re.search(r"\boffline\b", c[1], re.I) or
                  re.search(r"no network|network access|no internet", c[1], re.I)]
        if kind == "standard library":
            cands = [c for c in cands if not ALLOWED_DEPS.search(c[1])]
        hit = (strong or cands or [None])[0] if kind != "standard library" else (cands or [None])[0]
        if not hit:
            continue
        paths = re.findall(r"`(/[^`\s]+)`", hit[1]) if kind == "no writes" else []
        if paths:  # the protection must name the protected path, not any checksum in the verifier
            ok = any(enforced.search(ln) and any(p.rstrip("/") in ln for p in paths) for ln in blob.splitlines())
        else:
            ok = promise_enforced(kind, blob)
        ok = ok or (kind == "network" and re.search(r"\boffline\b", hit[1], re.I)
                                        and not re.search(r"no network|network access|no internet", hit[1], re.I)
                                        and OFFLINE_TOOLS.search(blob))
        if not ok:
            weak = ""
            if kind == "standard library":
                m = WEAK_STDLIB.search(blob)
                weak = f" (found {m.group(0).strip()!r}, which only limits accidental imports)" if m else ""
            out.append(finding("instruction.md", hit[0], f"the instruction promises {kind} (\"{hit[1][:140]}\") but no "
                               f"verifier file enforces it{weak}: expected {how}"))
    return out


def runs_submitted_code(task: Path, d: dict) -> bool:
    """False only for a legacy output task whose verifier reads data files and never runs submitted code
    (every artifact is an output file or directory and no test starts a process)."""
    arts = artifact_sources(d)
    if not arts or arts == [SUBMISSION] or not all(DATA_ART.search(a) for a in arts):
        return True
    tdir = task / "tests"
    for p in (tdir.rglob("*.py") if tdir.is_dir() else []):
        if CODE_RUN_RE.search(read(p)):
            return True
    sh = read(tdir / "test.sh") if (tdir / "test.sh").is_file() else ""
    for _, code in sh_logical(sh):
        # a runner phase that starts a program which is not one of the verifier's own test files
        for m in re.finditer(r"\b(?:python[\d.]*|node|bash|sh|ruby|php)\s+(?:-\S+\s+)*[\"']?([^\s\"';|&]+\.(?:py|m?js|sh|rb|php))",
                             code):
            if WRAP_RE.search(code) and "/tests/" not in m.group(1) and not PurePosixPath(m.group(1)).name.startswith("test_"):
                return True
    return False


def _world_writable(mode: str) -> bool:
    if re.fullmatch(r"0?[0-7]{3,4}", mode):
        return int(mode[-1]) & 2 == 2
    return bool(re.search(r"(^|,)[ugo]*[ao][ugoa]*[+=][rwxXst]*w", mode))


def _under(p: str, prefix: str) -> bool:
    prefix = prefix.rstrip("/")
    return bool(prefix) and (p.rstrip("/") == prefix or p.startswith(prefix + "/"))


def _collapse(items, rule_msg):
    """items: [(line, detail)] for one rule; one finding at the first line listing every occurrence."""
    items = sorted(dict.fromkeys(items))
    where = ", ".join(f"line {n}" + (f" ({d})" if d else "") for n, d in items[:6])
    if len(items) > 6:
        where += f", +{len(items) - 6} more"
    return items[0][0], rule_msg.format(where=where)


class ShScan:
    """One pass over a verifier shell script: runner phases, kills, runner-writable paths and root touches."""

    def __init__(self, task: Path, sh: str, runner_extra=()):
        self.task = task
        self.lines = sh_logical(sh)
        self.funcs = sh_functions(self.lines)
        self.in_func = {n for a, b, _ in self.funcs.values() for n in range(a + 1, b + 1)} | \
            {a for a, b, _ in self.funcs.values()}
        self.wrappers = {k for k, (_, _, body) in self.funcs.items() if WRAP_RE.search(body)}
        # arrays used as wrappers: AS_NOBODY=(setpriv --reuid nobody ...) then "${AS_NOBODY[@]}" cmd
        self.arrays = set(re.findall(r"(?m)^\s*(\w+)=\(\s*(?:setpriv|runuser|gosu|su-exec|sudo)\b", sh))
        self.killfns = {}
        for k, (_, _, body) in self.funcs.items():
            if re.search(r"\b(pkill|killall)\b[^\n]*\s-u\b", body):
                self.killfns[k] = bool(re.search(r"\b(pgrep|ps)\b", body) and
                                       re.search(r"\b(exit|infra|raise|return\s+1)\b", body))
        self.livefns = {k for k, (_, _, body) in self.funcs.items() if re.search(r"\b(pgrep|ps)\s", body)}
        env = ShEnv()
        for _, code in self.lines:
            for seg in split_cmds(code):
                env.learn(seg)
        users = set()
        for _, code in self.lines:
            for m in re.finditer(r"\b(?:pkill|killall)\b[^;&|\n]*?\s-u\s+(\S+)", code):
                users.add(env.expand(m.group(1)))
        if not users:
            for _, code in self.lines:
                for m in re.finditer(r"(?:--reuid[= ]|runuser\s+-u\s+|gosu\s+|su-exec\s+|sudo\s+-u\s+)(\S+)", code):
                    users.add(env.expand(m.group(1)))
        self.runners = (users | RUNNER_DEFAULT | set(runner_extra)) - {"root", "0", ""}
        self.scan()

    def is_runner(self, user: str) -> bool:
        u = user.split(":")[0].split(".")[0]
        return u in self.runners

    def scan(self):
        env = ShEnv()
        self.registry = []          # (prefix, line)
        self.chowned = []           # (path, line) chown to the runner, for the work-tree rule
        self.info = {}              # line -> dict(phase, kill, events, loops, phase_paths)
        loops, stack, loopvars = [], [], {}
        for n, code in self.lines:
            if n in self.in_func:
                continue
            head = loop_head(code)
            if head:
                items = loop_items(self.task, head, env)
                loops.append({"start": n, "end": None, "phase": False, "kill": False})
                stack.append(len(loops) - 1)
                if head[0] == "for" and items is not None:
                    loopvars[head[1]] = [str(x) for x in items if x is not None]
            rec = {"phase": False, "kill": None, "events": [], "loops": tuple(stack), "touch": []}
            for seg in split_cmds(code):
                env.learn(seg)
                words, redirs = sh_words(seg)
                if not words and not redirs:
                    continue
                body = [w for w in words if not re.match(r"^[A-Za-z_]\w*=", w)]
                lead = [w for w in words[:len(words) - len(body)]] if body else words
                cmd = unquote(body[0]) if body else ""
                phase = bool(WRAP_RE.search(seg)) or any(unquote(w) in self.wrappers for w in body[:6]) or \
                    any(re.search(r"\$\{?" + re.escape(a) + r"\b", seg) for a in self.arrays)
                if re.search(r"\b(pkill|killall)\b[^;&|]*\s-u\b", seg):
                    rec["kill"] = "unasserted"
                elif cmd in self.killfns:
                    rec["kill"] = "asserted" if self.killfns[cmd] else "unasserted"

                def expand_all(w):
                    names = [m.group(1) or m.group(2) for m in VAR_RE.finditer(w)]
                    lv = [v for v in names if v in loopvars]
                    if not lv:
                        return [env.expand(w)]
                    return [env.expand(w, {lv[0]: it}) for it in loopvars[lv[0]]] or [env.expand(w)]
                args = [w for w in body[1:] if not w.startswith("-")]
                if cmd == "chown" and args:
                    if self.is_runner(unquote(env.expand(args[0]))):
                        for t in args[1:]:
                            for p in expand_all(t):
                                self.registry.append((p, n))
                                self.chowned.append((p, n))
                elif cmd == "chmod" and len(args) >= 2 and _world_writable(unquote(args[0])):
                    for t in args[1:]:
                        for p in expand_all(t):
                            self.registry.append((p, n))
                elif cmd == "mkdir":
                    m = re.search(r"(?:-m\s*|--mode[= ])(\S+)", seg)
                    if m and _world_writable(unquote(m.group(1))):
                        for t in args:
                            if t != unquote(m.group(1)):
                                for p in expand_all(t):
                                    self.registry.append((p, n))
                for op, tgt in redirs:
                    if op == "<<":
                        continue
                    rec["events"].append(("write" if ">" in op else "read", env.expand(tgt)))
                if phase:
                    rec["phase"] = True
                    rec["touch"] += [env.expand(w) for w in body] + [env.expand(t) for _, t in redirs]
                    continue
                if cmd in SETUP_CMDS or not cmd:
                    continue
                for w in lead:
                    rec["events"].append(("read", env.expand(w.partition("=")[2])))
                vals = [env.expand(w.split("=", 1)[1] if w.startswith("-") and "=" in w else w)
                        for w in body[1:] if not (w.startswith("-") and "=" not in w)]
                if cmd in ("cp", "mv", "install", "rsync") and len(vals) >= 2:
                    rec["events"] += [("read", v) for v in vals[:-1]] + [("write", vals[-1])]
                elif cmd == "tee":
                    rec["events"] += [("write", v) for v in vals]
                else:
                    rec["events"] += [("read", v) for v in vals]
                    if cmd.startswith(("/", "$", ".")):
                        rec["events"].append(("read", env.expand(cmd)))
            for li in stack:
                if rec["phase"]:
                    loops[li]["phase"] = True
                if rec["kill"]:
                    loops[li]["kill"] = True
            self.info[n] = rec
            if re.search(r"(^|;|\s)done\b", code) and stack:
                loops[stack.pop()]["end"] = n
        for lp in loops:
            if lp["end"] is None:
                lp["end"] = self.lines[-1][0] if self.lines else lp["start"]
        self.loops = loops
        # a kill counts as asserted when a survivor check that exits follows within a few lines
        order = [n for n, _ in self.lines if n in self.info]
        for i, n in enumerate(order):
            if self.info[n]["kill"] == "unasserted":
                bodies = dict(self.lines)
                window = "\n".join(bodies[m] for m in order[i:i + 7])
                if re.search(r"\b(exit|infra|raise)\b", window) and (
                        re.search(r"\b(pgrep|ps)\s", window) or any(f in window for f in self.livefns)):
                    self.info[n]["kill"] = "asserted"

    def writable(self, p: str, n: int):
        """The registry prefix that makes path p runner-writable at line n, or None."""
        for prefix, rl in self.registry:
            if prefix.rstrip("/") in ("", "/tmp") or re.search(r"/.*\$", prefix):
                continue  # too broad, or a variable the gate could not resolve
            if _under(p, prefix):
                same_loop = any(self.loops[li]["start"] <= rl <= self.loops[li]["end"] for li in self.info[n]["loops"])
                if rl < n or same_loop:
                    return prefix, rl
        return None

    def findings(self):
        out = {"write": [], "read-before-kill": [], "read-unasserted-kill": [], "no-kill-between-phases": []}
        phases = [n for n in sorted(self.info) if self.info[n]["phase"]]
        last_phase, kill_state, kill_line = None, None, None
        for n in sorted(self.info):
            rec = self.info[n]
            loop_live = any(self.loops[li]["phase"] and not self.loops[li]["kill"] for li in rec["loops"])
            for kind, p in rec["events"]:
                w = self.writable(p, n)
                if not w:
                    continue
                prefix, rl = w
                if kind == "write":
                    after = any(rl < pl < n for pl in phases) or any(
                        self.loops[li]["phase"] and rl <= self.loops[li]["end"] for li in rec["loops"])
                    if after:
                        out["write"].append((n, p))
                elif (last_phase is not None and kill_state is None) or loop_live:
                    out["read-before-kill"].append((n, p))
                elif last_phase is not None and kill_state == "unasserted":
                    out["read-unasserted-kill"].append((n, f"{p}; kill at line {kill_line}"))
            if rec["phase"]:
                if last_phase is not None and kill_state is None and not (
                        set(rec["loops"]) & set(self.info[last_phase]["loops"])):
                    # only when a later root read takes what the earlier phase left in a runner-writable dir
                    later = [p for m in sorted(self.info) if m > n for k, p in self.info[m]["events"] if k == "read"]
                    touched = []
                    for t in self.info[last_phase]["touch"]:
                        w = self.writable(t, last_phase)
                        if w and any(_under(r, w[0]) for r in later):
                            touched.append(t)
                    if touched:
                        out["no-kill-between-phases"].append((n, f"after the phase at line {last_phase}, "
                                                                  f"which writes {touched[0]}"))
                last_phase, kill_state = n, None
            if rec["kill"] and last_phase is not None:
                kill_state, kill_line = rec["kill"], n
        return out


SH_RULES = {
    "write": "root writes into a runner-writable directory after the runner has run there ({where}): a planted "
             "symlink or a pre-created runner-owned file turns the write into a root write primitive or a "
             "forgeable verdict; write into a root-only directory (spec rule 7)",
    "read-before-kill": "root reads runner-writable paths before the runner's processes are killed ({where}): a "
                        "surviving daemon can rewrite them; pkill -u <runner>, wait, assert none survive, then read "
                        "(spec rule 7)",
    "read-unasserted-kill": "root reads runner-writable paths after a pkill with no survivor assertion ({where}): "
                            "assert that no runner process survived before reading (spec rule 7)",
    "no-kill-between-phases": "a runner phase starts while the previous one may still run ({where}): no pkill -u "
                              "<runner> plus survivor assertion between runner phases (spec rule 7)",
}

PY_WRITE_METHODS = ("write_text", "write_bytes")


def _py_root(e):
    if isinstance(e, ast.JoinedStr) and e.values and isinstance(e.values[0], ast.FormattedValue):
        return ast.unparse(e.values[0].value)
    if isinstance(e, ast.Call):
        f = e.func
        if isinstance(f, ast.Attribute) and f.attr == "join" and e.args:
            return _py_root(e.args[0])
        if isinstance(f, ast.Name) and f.id in ("Path", "PurePath", "str") and e.args:
            return _py_root(e.args[0])
    if isinstance(e, ast.BinOp) and isinstance(e.op, ast.Div):
        return _py_root(e.left)
    if isinstance(e, (ast.Name, ast.Attribute)):
        return ast.unparse(e)
    return None


def py_root_opens(rel: str, text: str, runners):
    """(line, detail) for opens-for-writing by root inside a directory the file chowns to the runner (or
    chmods world-writable), without O_NOFOLLOW."""
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    parents = {}
    for node in ast.walk(tree):
        for ch in ast.iter_child_nodes(node):
            parents[ch] = node
    owned = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        name = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", "")
        if name in ("chown", "lchown") and len(node.args) >= 2 or name == "chown" and node.keywords:
            owner = node.args[1] if len(node.args) >= 2 else next((k.value for k in node.keywords if k.arg == "user"), None)
            if isinstance(owner, ast.Constant) and owner.value in (0, "root"):
                continue
        elif name == "chmod" and len(node.args) >= 2:
            mode = node.args[1]
            if not (isinstance(mode, ast.Constant) and isinstance(mode.value, int) and mode.value & 0o002):
                continue
        else:
            continue
        tgt = node.args[0] if node.args else None
        targets = [tgt]
        if isinstance(tgt, ast.Name):
            p = parents.get(node)
            while p is not None:
                if isinstance(p, (ast.For, ast.comprehension)) and isinstance(p.target, ast.Name) and \
                        p.target.id == tgt.id and isinstance(p.iter, (ast.Tuple, ast.List)):
                    targets = p.iter.elts
                    break
                p = parents.get(p)
        for t in targets:
            if isinstance(t, (ast.Name, ast.Attribute)):
                owned.setdefault(ast.unparse(t), node.lineno)
    if not owned:
        return []
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        f = node.func
        path, write = None, False
        if isinstance(f, ast.Name) and f.id == "open" and node.args:
            path = node.args[0]
            mode = node.args[1] if len(node.args) > 1 else next((k.value for k in node.keywords if k.arg == "mode"), None)
            write = isinstance(mode, ast.Constant) and isinstance(mode.value, str) and bool(set(mode.value) & set("wax+"))
        elif isinstance(f, ast.Attribute) and f.attr == "open" and isinstance(f.value, ast.Name) and f.value.id == "os" \
                and len(node.args) >= 2:
            flags = ast.unparse(node.args[1])
            path = node.args[0]
            write = "O_NOFOLLOW" not in flags and bool(re.search(r"O_(WRONLY|RDWR|CREAT|APPEND|TRUNC)", flags))
        elif isinstance(f, ast.Attribute) and f.attr in PY_WRITE_METHODS:
            path, write = f.value, True
        elif isinstance(f, ast.Attribute) and f.attr == "open" and node.args and isinstance(node.args[0], ast.Constant) \
                and isinstance(node.args[0].value, str) and set(node.args[0].value) & set("wax+"):
            path, write = f.value, True
        elif isinstance(f, ast.Attribute) and f.attr in ("copy", "copyfile", "copy2", "move") and len(node.args) >= 2 \
                and isinstance(f.value, ast.Name) and f.value.id == "shutil":
            path, write = node.args[1], True
        if not write or path is None:
            continue
        root = _py_root(path)
        if root in owned and ast.unparse(path) != root:
            out.append((node.lineno, f"{ast.unparse(path)[:60]} in {root}, runner-owned since line {owned[root]}"))
    return out


def dockerfile_runner_chowns(df: str, runners):
    """(line, path) for chown to the runner and COPY --chown=<runner> in a Dockerfile."""
    out = []
    for n, ln in logical_lines(df):
        s = ln.strip()
        m = re.match(r"(?i)(?:COPY|ADD)\s+.*--chown=(\S+)\s+.*\s(\S+)$", s)
        if m and m.group(1).split(":")[0] in runners:
            out.append((n, m.group(2)))
        for m in re.finditer(r"\bchown\s+((?:-\S+\s+)*)(\S+)\s+([^&;|]+)", s):
            if m.group(2).split(":")[0] in runners:
                out += [(n, p) for p in m.group(3).split() if p.startswith("/")]
    return out


GRADING_STEP = re.compile(r"(?:\bpython[\d.]*\s+(?:-\S+\s+)*(?:-m\s+pytest|\S*/tests/\S+\.py)|\bpytest\s|"
                          r"\bgo\s+test\b|\bcargo\s+test\b|\bnode\s+\S*/tests/)")


def fail_closed_findings(task: Path, sh: str, scan, watch, runs_code: bool) -> list:
    """Shell steps that fail open: truncated graded output, a copy or grading step whose exit status is
    swallowed, and root copies of submission or runner output that follow symlinks."""
    trunc, swallow, follow = [], [], []
    env = ShEnv()
    for n, code in scan.lines:
        for seg in split_cmds(code):
            env.learn(seg)
        c = code.strip()
        for m in re.finditer(r"\bhead\s+-c\s*\S+\s+(\S+)(?:\s*>\s*(\S+))?|\bdd\b[^|;&]*\bif=(\S+)[^|;&]*\bcount=", c):
            src = env.expand(m.group(1) or m.group(3) or "").strip("\"'()")
            dst = env.expand(m.group(2) or "").strip("\"'()")
            if re.search(r"\.(log|err|rc|txt|stderr|stdout)$", src) or dst.startswith("/logs/") \
                    or "urandom" in src or c[max(0, m.start() - 2):m.start()] == "$(":
                continue
            trunc.append((n, src.strip('"')))
        if re.search(r"\|\|\s*(true|:|echo\b)", c):
            head = re.split(r"\|\|\s*(?:true|:|echo\b)", c)[0]
            if re.search(r"\b(pkill|kill|rm|chmod|chown|mkdir|rmdir|umount|pgrep|command -v)\b", head):
                continue
            eh = env.expand(head)
            is_copy = re.match(r"\s*\(?\s*cp\b", head) and any(a in eh for a in watch) and "/logs/" not in eh
            is_grade = not re.match(r"\s*\(?\s*(cp|head|cat|tail|mv)\b", head) and GRADING_STEP.search(head)
            if is_copy or is_grade:
                swallow.append((n, "copy" if is_copy else "grading step"))
        if runs_code and not (scan.info.get(n) or {}).get("phase"):
            for seg in split_cmds(code):
                words, _ = sh_words(seg)
                if not words or unquote(words[0]) != "cp":
                    continue
                flags = "".join(w.lstrip("-") for w in words[1:] if w.startswith("-") and not w.startswith("--"))
                if set(flags) & set("Pda") or "--no-dereference" in seg:
                    continue
                args = [env.expand(w) for w in words[1:] if not w.startswith("-")]
                srcs = args[:-1]
                if not args or args[-1].startswith("/logs/"):
                    continue  # a log copy for reviewers, not the graded input
                raw_srcs = [w for w in words[1:] if not w.startswith("-")][:-1]
                vars_ = {v for w in raw_srcs for v in re.findall(r"\$\{?(\w+)", w)}
                if vars_ and any(re.search(r"-L\s+[\"']?\$\{?" + v + r"\b", sh) for v in vars_):
                    continue  # symlinks are refused before this copy
                if any(scan.writable(x, n) or any(_under(x, a) for a in watch) for x in srcs):
                    follow.append((n, srcs[0]))
    lines = scan.lines
    ignored = []
    if not re.search(r"(?m)^\s*set\s+-\w*e", sh):
        for i, (n, code) in enumerate(lines):
            c = code.strip()
            if not re.search(r"\bpython[\d.]*\s+(?:-\S+\s+)*\S*/tests/(?!test_)\w+\.py\b", c) or "pytest" in c \
                    or re.search(r"\|\||&&|^\s*if\b|^\s*!|\$\(", c) or (scan.info.get(n) or {}).get("phase") is None:
                continue
            nxt = " ".join(x for _, x in lines[i + 1:i + 3])
            if "$?" not in nxt:
                ignored.append((n, re.search(r"\S*/tests/\w+\.py", c).group(0)))
    out = []
    if ignored:
        ln0, msg = _collapse(ignored, "a verifier driver's exit status is never checked ({where}): a driver crash "
                                      "grades as the submission's 0 instead of an infrastructure error")
        out.append(finding("tests/test.sh", ln0, msg))
    if trunc:
        ln0, msg = _collapse(trunc, "graded output is truncated before grading ({where}): the tail of a submission "
                                    "is silently dropped; refuse an oversize output instead")
        out.append(finding("tests/test.sh", ln0, msg))
    if swallow:
        ln0, msg = _collapse(swallow, "a copy or grading step's exit status is swallowed with `|| true` or `|| echo` "
                                      "({where}): a crash or a failed copy grades as an ordinary 0 or passes unseen; "
                                      "fail closed with an infrastructure error")
        out.append(finding("tests/test.sh", ln0, msg))
    if follow:
        ln0, msg = _collapse(follow, "root copies submission or runner output without -P ({where}): a planted symlink "
                                     "makes root read any file (answers included) into the graded copy; use cp -P or "
                                     "reject symlinks")
        out.append(finding("tests/test.sh", ln0, msg))
    out += ctrf_fallback_findings(scan)
    return out


REWARD_WRITE = re.compile(r"(?:>>?|\btee\s+(?:-a\s+)?)\s*[\"']?[^\s;&|<>]*reward\.(?:txt|json)\b")


def ctrf_fallback_findings(scan) -> list:
    """X3.1 (customer F03): a reward written on a path that leaves no ctrf.json. Applies when the script
    deletes or produces ctrf.json (it names it outside comments). Fires on
      * a function that writes reward.txt/reward.json (finish-like) and neither writes nor stubs ctrf.json,
        directly or through a function it calls, when one of its call sites is not covered: a call with
        reward 1, a call inside a function that writes ctrf, or a call that a ctrf write precedes on the
        same or the previous logical line (`{ ctrf_stub; finish 0 ...; }`) is covered. A function that only
        removes the reward (infra) is not a reward writer;
      * a top-level `echo 0 > .../reward.txt` followed by `exit` on the same or the next two top-level
        lines, before the pytest --ctrf step, with no ctrf write in between.
    A ctrf "write" is any non-`rm` command that names ctrf (ctrf_stub, cp .../ctrf.json, a heredoc
    writer whose argument is ctrf.json)."""
    if scan is None:
        return []
    lines = scan.lines
    if not any(re.search(r"ctrf", c, re.I) for _, c in lines):
        return []
    funcs = scan.funcs
    owner = {}
    for name, (a, b, _) in funcs.items():
        for n in range(a, b + 1):
            owner.setdefault(n, name)
    bodies = {name: [(n, c) for n, c in lines if a <= n <= b] for name, (a, b, _) in funcs.items()}

    def cmds(code):
        for seg in split_cmds(code):
            words, _ = sh_words(seg)
            body = [unquote(w) for w in words if not re.match(r"^[A-Za-z_]\w*=", w)]
            yield seg, body

    def writes_ctrf(code) -> bool:
        return any(re.search(r"ctrf", seg, re.I) and not (body and body[0] == "rm") for seg, body in cmds(code))

    calls = {name: {b[0] for _, c in body for _, b in cmds(c) if b and b[0] in funcs and b[0] != name}
             for name, body in bodies.items()}
    ctrf_fns = {name for name, body in bodies.items() if any(writes_ctrf(c) for _, c in body)}
    grew = True
    while grew:
        grew = False
        for name in funcs:
            if name not in ctrf_fns and calls[name] & ctrf_fns:
                ctrf_fns.add(name)
                grew = True
    def covered(i, name) -> bool:
        """The call of `name` on logical line i: reward 1, inside a function that writes ctrf, or preceded on
        the same or the previous logical line by a ctrf write ({ ctrf_stub; finish 0 ...; })."""
        n, code = lines[i]
        if owner.get(n) in ctrf_fns:
            return True
        segs = list(cmds(code))
        at = next(k for k, (_, b) in enumerate(segs) if b and b[0] == name)
        if segs[at][1][1:2] == ["1"]:
            return True
        before = [seg for seg, _ in segs[:at]] + ([lines[i - 1][1]] if i else [])
        return any(writes_ctrf(x) or any(b and b[0] in ctrf_fns for _, b in cmds(x)) for x in before)

    items = []
    for name, body in bodies.items():
        if name in ctrf_fns or not any(REWARD_WRITE.search(c) for _, c in body):
            continue
        sites = [i for i, (n, c) in enumerate(lines)
                 if owner.get(n) != name and any(b and b[0] == name for _, b in cmds(c))]
        bare = [lines[i][0] for i in sites if not covered(i, name)]
        if bare:
            items.append((funcs[name][0], f"{name}() writes the reward and never ctrf.json; called without one "
                                          f"at line {bare[0]}" + (f" and {len(bare) - 1} more" if len(bare) > 1 else "")))
    top = [(n, c) for n, c in lines if n not in owner]
    judge = next((n for n, c in top if "--ctrf" in c or GRADING_STEP.search(c)), None)
    for i, (n, c) in enumerate(top):
        if judge is not None and n >= judge:
            break
        if not REWARD_WRITE.search(c):
            continue
        window = [x for _, x in top[i:i + 3]]
        if any(re.search(r"(?:^|[;&|{(\s])exit\b", x) for x in window) and not any(
                writes_ctrf(x) or any(b and b[0] in ctrf_fns for _, b in cmds(x)) for x in window):
            items.append((n, "reward written, then exit"))
    if not items:
        return []
    ln0, msg = _collapse(items, "X3.1: a path that writes the reward leaves no ctrf.json ({where}): an early exit "
                                "(oversized or refused submission, a patch that does not apply, a judge that crashed) "
                                "scores 0 with no structured test report; write a fallback ctrf.json (every graded "
                                "test failed) inside the function that writes the reward")
    return [finding("tests/test.sh", ln0, msg)]


# ------------------------------------------------------------------ verifier-code rules
# Static rules over the verifier's own code (tests/**). They are part of the structure gate and
# each finding names its rule id, so a disposition can target one rule.
#   X2.5       a reader that turns a missing input into empty data
#   X3.1       a reward-writing path in test.sh that leaves no ctrf.json (customer F03; fail_closed_findings)
#   X3.2       a suite deadline checked only before a step starts, or a kill grace outside the stated limit;
#              and captured output sliced to a suffix or prefix before grading (customer F01)
#   X3.3       a bounded read (f.read(N), os.read(fd, N)) never checked for more data (customer F02)
#   X4.2       submitted code built, installed, imported or run as root
#   PROC.4h9   key checks written as >=, <=, issubset or issuperset where the contract says exact keys
#   PROC.4h10  offset-tolerant timestamp parsing where the instruction shows Z timestamps

READ_ERRORS = {"OSError", "IOError", "EnvironmentError", "FileNotFoundError", "PermissionError", "Exception",
               "BaseException", "IsADirectoryError", "NotADirectoryError"}
READ_CALLS = {"open", "read", "read_text", "read_bytes", "load", "loads", "readlines", "readline", "fromfile",
              "loadtxt", "read_csv", "read_json", "safe_load", "check_output"}
PARSE_CALLS = {"load", "loads", "safe_load", "full_load", "DictReader", "reader", "read_json", "parse", "fromstring"}
REFERENCE_HINT = re.compile(r"expect|golden|reference|truth|answer|groups|suite|spec|budget|requirements|grading|"
                            r"__file__|/tests\b|\bHERE\b|\bSUITE\b|\bDATA(?:_DIR)?\b|\bROOT\b|\bTESTS?_DIR\b|\bREF_\w+|fixture", re.I)
KEY_NOUN = r"(?:keys|fields|properties|members|columns|attributes)"
EXACT_KEYS = re.compile(r"\bexactly (?:the |these |those |the following )?(?:[\w`-]+ )?" + KEY_NOUN + r"\b|"
                        r"\b" + KEY_NOUN + r" (?:are|is|must be|should be) exactly\b|"
                        r"\bno (?:other|extra|additional|unknown|further) (?:top-level )?" + KEY_NOUN + r"\b|"
                        r"\b(?:only|nothing but) (?:these|the following|those) (?:[\w`-]+ )?" + KEY_NOUN + r"\b|"
                        r"\badditionalProperties\b", re.I)
LOGISH = re.compile(r"log|tail|stderr|diag|debug|trace", re.I)
Z_TIMESTAMP = re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?Z\b")
Z_ASSERTED = re.compile(r"endswith\(\s*\(?\s*[\"']Z[\"']|Z\$|Z\\Z|\[\"']Z[\"']\]|==\s*[\"']Z[\"']|"
                        r"strftime\([^)]*Z[\"']\)\s*==|isoformat\(\)\.replace\([^)]*\)\s*==", re.I)
BUILD_WORDS = {"npm", "pnpm", "yarn", "npx", "pip", "pip3", "cargo", "go", "make", "cmake", "node", "bun", "deno",
               "gradle", "mvn", "rustc", "gcc", "g++", "cc", "clang", "javac", "dotnet", "uv", "poetry"}
BUILD_SUB = {"npm": r"(?:install|i|ci|build|run|test|exec|rebuild|start|pack)", "pnpm": r".", "yarn": r".", "npx": r".",
             "pip": r"install", "pip3": r"install", "cargo": r"(?:build|test|run|install|check|bench|b|t|r)",
             "go": r"(?:build|test|run|install|generate|vet)", "uv": r"(?:pip|run|sync)", "poetry": r"(?:install|run)",
             "gradle": r".", "mvn": r".", "dotnet": r"(?:build|test|run)", "bun": r".", "deno": r"."}
DROP_KW = {"user", "preexec_fn", "group", "extra_groups", "process_group"}
PY_STDLIB = set(getattr(sys, "stdlib_module_names", ())) | {"pytest", "yaml", "numpy", "_pytest"}


def verifier_py_files(task: Path):
    tdir = task / "tests"
    if not tdir.is_dir():
        return []
    return [p for p in sorted(tdir.rglob("*.py")) if p.is_file() and p.stat().st_size < 2_000_000]


def _call_name(node) -> str:
    f = node.func if isinstance(node, ast.Call) else node
    if isinstance(f, ast.Attribute):
        return f.attr
    return getattr(f, "id", "")


def _empty_literal(e) -> str | None:
    """'' / b'' / [] / {} / () / set() / str() / bytes() / list() / dict(): the text, or None."""
    if isinstance(e, ast.Constant) and e.value in ("", b""):
        return repr(e.value)
    if isinstance(e, (ast.List, ast.Tuple, ast.Set)) and not e.elts:
        return ast.unparse(e)
    if isinstance(e, ast.Dict) and not e.keys:
        return "{}"
    if isinstance(e, ast.Call) and isinstance(e.func, ast.Name) and e.func.id in ("str", "bytes", "list", "dict",
                                                                                    "set", "tuple") and not e.args:
        return ast.unparse(e)
    return None


def _handler_types(h) -> set:
    if h.type is None:
        return {"BaseException"}
    elts = h.type.elts if isinstance(h.type, ast.Tuple) else [h.type]
    return {(e.attr if isinstance(e, ast.Attribute) else getattr(e, "id", "")) for e in elts}


def _parents(tree):
    par = {}
    for node in ast.walk(tree):
        for ch in ast.iter_child_nodes(node):
            par[ch] = node
    return par


def rule_empty_reader(rel: str, tree) -> list:
    """X2.5: a read wrapped in try whose OSError/FileNotFoundError handler returns, assigns or leaves empty
    data (or passes), and .get(key, '') on data parsed from a deliverable."""
    out = []
    par = _parents(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Try):
            continue
        reads = [c for s in node.body for c in ast.walk(s) if isinstance(c, ast.Call) and _call_name(c) in READ_CALLS]
        if not reads:
            continue
        fn = par.get(node)
        while fn is not None and not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            fn = par.get(fn)
        where = (fn.name + " " if fn is not None else "") + " ".join(
            _resolve_arg(a, fn or tree) for c in reads for a in list(c.args[:1]) + [getattr(c.func, "value", None)]
            if a is not None)
        if REFERENCE_HINT.search(where) or LOGISH.search(where):
            continue
        for h in node.handlers:
            if not (_handler_types(h) & READ_ERRORS):
                continue
            body = [s for s in h.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant))]
            what = None
            if not body or all(isinstance(s, ast.Pass) for s in body):
                what = "pass"
            elif len(body) == 1 and isinstance(body[0], ast.Return) and body[0].value is not None \
                    and _empty_literal(body[0].value):
                what = "return " + _empty_literal(body[0].value)
            elif len(body) == 1 and isinstance(body[0], ast.Assign) and _empty_literal(body[0].value):
                what = ast.unparse(body[0].targets[0]) + " = " + _empty_literal(body[0].value)
            if what:
                out.append((h.lineno, f"except {'/'.join(sorted(_handler_types(h)))}: {what}"))
    # names bound to parsed data that is not the verifier's own reference
    parsed = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and isinstance(node.value, ast.Call) \
                and _call_name(node.value) in PARSE_CALLS and not REFERENCE_HINT.search(ast.unparse(node.value)):
            tg = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in tg:
                if isinstance(t, ast.Name) and not REFERENCE_HINT.search(t.id):
                    parsed.add(t.id)
    changed = True
    while changed:   # values taken from parsed data: row = data["rows"][0]; for rec in data: ...
        changed = False
        for node in ast.walk(tree):
            src, tgts = None, []
            if isinstance(node, ast.Assign):
                src, tgts = node.value, node.targets
            elif isinstance(node, (ast.For, ast.comprehension)):
                src, tgts = node.iter, [node.target]
            if src is None:
                continue
            roots = {n.id for n in ast.walk(src) if isinstance(n, ast.Name)}
            if roots & parsed:
                for t in tgts:
                    for n in ast.walk(t):
                        if isinstance(n, ast.Name) and n.id not in parsed and not REFERENCE_HINT.search(n.id):
                            parsed.add(n.id)
                            changed = True
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "get" \
                and len(node.args) == 2 and _empty_literal(node.args[1]):
            recv = node.func.value
            root = recv
            while isinstance(root, (ast.Attribute, ast.Subscript, ast.Call)):
                root = root.value if not isinstance(root, ast.Call) else root.func
            if isinstance(root, ast.Name) and root.id in parsed and not re.search(r"ctrf|junit|report|summary",
                                                                                  ast.unparse(recv), re.I):
                tgt = par.get(node)
                while isinstance(tgt, (ast.Call, ast.Attribute)) and not isinstance(tgt, ast.Assign):
                    tgt = par.get(tgt)
                name = tgt.targets[0].id if isinstance(tgt, ast.Assign) and isinstance(tgt.targets[0], ast.Name) else None
                if name and re.search(r"(?m)^\s*(?:assert\s+(?:len\()?" + re.escape(name) + r"\b(?!\s*(?:==|in\b|is\b))|"
                                      r"if\s+not\s+" + re.escape(name) + r"\b)", ast.unparse(tree)):
                    continue   # a missing value is caught as empty right after
                out.append((node.lineno, ast.unparse(node)[:60]))
    if not out:
        return []
    ln0, msg = _collapse(out, "X2.5: a verifier reader turns a missing input into empty data ({where}): a missing "
                              "capture or field then compares equal to an expected empty value and passes; keep "
                              "missing distinct (let the error propagate, return None, or fail the check)")
    return [finding(rel, ln0, msg)]


def _resolve_arg(a, scope) -> str:
    """The source text of a read's path argument, following one simple assignment of a bare name."""
    txt = ast.unparse(a)
    if isinstance(a, ast.Name):
        for n in ast.walk(scope):
            if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == a.id for t in n.targets):
                return txt + " " + ast.unparse(n.value)
    return txt


def _docstring_lines(tree) -> set:
    lines = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
            lines |= set(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    return lines


def _is_clock(e) -> bool:
    return any(isinstance(c, ast.Call) and _call_name(c) in ("time", "monotonic", "perf_counter", "now")
               and ast.unparse(c.func).split(".")[0] in ("time", "datetime", "_time", "clock", "dt")
               for c in ast.walk(e))


def rule_prelaunch_deadline(rel: str, tree) -> list:
    """X3.2 (python): a clock check that skips or stops before starting a process, while the process it
    starts is bounded only by a fixed per-step timeout and nothing kills it at the suite deadline."""
    par = _parents(tree)
    checks = []
    for node in ast.walk(tree):
        if isinstance(node, ast.If) and isinstance(node.test, ast.Compare) and _is_clock(node.test) and \
                any(isinstance(s, (ast.Return, ast.Break, ast.Continue, ast.Raise)) for s in node.body):
            checks.append(node)
    if not checks:
        return []
    out = []
    for chk in checks:
        fn = chk
        while fn is not None and not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.For, ast.While)):
            fn = par.get(fn)
        scope = fn if fn is not None else tree
        launches = [c for c in ast.walk(scope) if isinstance(c, ast.Call) and _call_name(c) in
                    ("run", "Popen", "call", "check_call", "check_output") and
                    ast.unparse(c.func).split(".")[0] in ("subprocess", "sp", "run", "Popen")]
        for c in launches:
            to = next((k.value for k in c.keywords if k.arg == "timeout"), None)
            bounded = to is not None and (_is_clock(to) or re.search(r"remain|left|deadline|until", ast.unparse(to), re.I))
            if not bounded:
                out.append((chk.lineno, f"then {ast.unparse(c.func)} at line {c.lineno} with "
                                        f"{'timeout=' + ast.unparse(to) if to is not None else 'no timeout'}"))
    if not out:
        return []
    # a kill at the deadline elsewhere in the file (a watchdog) makes the check a scheduling hint only
    text = ast.unparse(tree)
    if re.search(r"\b(killpg|\.kill\(\)|\.terminate\(\)|pkill|Timer\()", text) and \
            re.search(r"remain|deadline|BUDGET|budget", text) and re.search(r"Timer\(|watchdog|threading", text):
        return []
    ln0, msg = _collapse(out, "X3.2: the suite deadline is checked only before a step starts ({where}): a step "
                              "started just before the deadline runs its full per-step limit past it and nothing "
                              "kills it; bound each step by the remaining budget or kill running steps at the "
                              "deadline")
    return [finding(rel, ln0, msg)]


def stated_seconds(task: Path) -> set:
    ip = task / "instruction.md"
    out = set()
    if not ip.is_file():
        return out
    for ln in strip_fences(read(ip)).splitlines():
        if TRAILER_RE.match(ln.strip()):
            continue
        for m in TIME_WORDS.finditer(ln):
            u = m.group(2).lower()
            out.add(float(m.group(1)) * (3600 if u.startswith("h") else 60 if u.startswith("m") else 1))
    return out


KILL_GRACE_SH = re.compile(r"(?<![\w-])timeout\s+(?:-{1,2}[A-Za-z][\w-]*(?:[ =][\w.$\"{}]+)?\s+)*?"
                           r"(?:-k\s*|--kill-after[= ])[\"']?(\d+(?:\.\d+)?)([smh]?)[\"']?\s+"
                           r"(?:-{1,2}[A-Za-z][\w-]*(?:[ =][\w.]+)?\s+)*[\"']?(\d+(?:\.\d+)?)([smh]?)\b")
KILL_GRACE_LIST = re.compile(r"[\"']timeout[\"']\s*,\s*[\"'](?:-k|--kill-after)[\"']\s*,\s*[\"'](\d+(?:\.\d+)?)[\"']\s*,"
                             r"\s*(?:str\(\s*(\w+)\s*\)|[\"'](\d+(?:\.\d+)?)[\"']|(\d+(?:\.\d+)?))")


def rule_kill_grace(task: Path) -> list:
    """X3.2: `timeout -k G N` where the instruction states N as the limit and never N + G."""
    stated = stated_seconds(task)
    if not stated:
        return []
    out = []
    tdir = task / "tests"
    for p in sorted(tdir.rglob("*")) if tdir.is_dir() else []:
        if not p.is_file() or p.suffix not in (".sh", ".py", ".bash", "") or p.name == "Dockerfile":
            continue
        text = read(p)
        consts = {m.group(1): float(m.group(2)) for m in re.finditer(r"(?m)^\s*([A-Z_][A-Z0-9_]*)\s*=\s*(\d+(?:\.\d+)?)\s*$",
                                                                     text)}
        rel = p.relative_to(task).as_posix()
        hits = []
        skip = set()
        if p.suffix == ".py":
            try:
                skip = _docstring_lines(ast.parse(text))
            except SyntaxError:
                pass
        for n, ln in logical_lines(text):
            if n in skip:
                continue
            for m in KILL_GRACE_SH.finditer(ln):
                g, lim = float(m.group(1)) * UNIT[m.group(2)], float(m.group(3)) * UNIT[m.group(4)]
                hits.append((n, g, lim))
            for m in KILL_GRACE_LIST.finditer(ln):
                lim = consts.get(m.group(2)) if m.group(2) else float(m.group(3) or m.group(4))
                if lim is not None:
                    hits.append((n, float(m.group(1)), lim))
        for n, g, lim in hits:
            if g > 0 and lim in stated and (lim + g) not in stated:
                out.append((rel, n, g, lim))
    if not out:
        return []
    items = {}
    for rel, n, g, lim in out:
        items.setdefault(rel, []).append((n, f"-k {g:g} on a {lim:g} s limit"))
    fs = []
    for rel, its in items.items():
        ln0, msg = _collapse(its, "X3.2: a kill grace is not counted in the stated limit ({where}): the instruction "
                                  "states the limit without the grace, so a step can run the grace longer than "
                                  "stated; state limit + grace, or put the grace inside the stated limit")
        fs.append(finding(rel, ln0, msg))
    return fs


def rule_sh_prelaunch_deadline(rel: str, sh: str) -> list:
    """X3.2 (shell): a loop that breaks on a clock check and starts commands bounded by a fixed timeout."""
    out = []
    lines = sh_logical(sh)
    depth, loop_start, has_check, check_line = 0, None, False, 0
    body = []
    for n, code in lines:
        if loop_head(code):
            depth += 1
            if depth == 1:
                loop_start, has_check, body = n, False, []
        if depth:
            body.append((n, code))
            if re.search(r"date\s+\+%s|\$SECONDS\b|\bSECONDS\b", code) and re.search(r"\b(break|exit|continue|return)\b",
                                                                                       code):
                has_check, check_line = True, n
        if re.search(r"(^|;|\s)done\b", code) and depth:
            depth -= 1
            if depth == 0 and has_check:
                runs = [m for m, c in body if re.search(r"(?<![\w-])timeout\s", c)]
                bounded = any(re.search(r"(?<![\w-])timeout\s+[^|;&]*\$\{?\w*(?:REMAIN|LEFT|DEADLINE)", c, re.I)
                              for _, c in body)
                if runs and not bounded:
                    out.append((check_line, f"then a fixed timeout at line {runs[0]}"))
    if not out:
        return []
    ln0, msg = _collapse(out, "X3.2: the suite deadline is checked only before a step starts ({where}): a step "
                              "started just before the deadline runs its full per-step limit past it; bound each "
                              "step by the remaining budget or kill running steps at the deadline")
    return [finding(rel, ln0, msg)]


def _dropped(seg: str, scan) -> bool:
    words, _ = sh_words(seg)
    body = [unquote(w) for w in words if not re.match(r"^[A-Za-z_]\w*=", w)]
    return bool(WRAP_RE.search(seg)) or any(w in scan.wrappers for w in body[:6]) or \
        any(re.search(r"\$\{?" + re.escape(a) + r"\b", seg) for a in scan.arrays)


def _root_build(words, cwd: str | None, seg: str) -> str | None:
    """A description when this simple command builds, installs, imports or runs code that is not the
    verifier's own; None otherwise."""
    body = [unquote(w) for w in words if not re.match(r"^[A-Za-z_]\w*=", w)]
    while body and body[0] in ("env", "exec", "nice", "nohup", "command", "stdbuf", "time") or \
            body and body[0] == "timeout":
        if body[0] == "timeout":
            body = body[1:]
            while body and body[0].startswith("-"):
                body = body[2:] if body[0] in ("-k", "-s", "--signal", "--kill-after") else body[1:]
            body = body[1:]
        else:
            body = [w for w in body[1:] if not re.match(r"^[A-Za-z_]\w*=", w)]
            while body and body[0].startswith("-") and body[0] != "-":
                body = body[1:]
    if not body:
        return None
    cmd = PurePosixPath(body[0]).name
    rest = body[1:]
    verifier_side = (cwd or "").startswith("/tests") or re.search(r"(?<![\w-])/tests/|\$\{?TESTS?_?DIR", seg)
    pyname = re.fullmatch(r"python[\d.]*", cmd)
    if pyname:
        if "-c" in rest:
            code = rest[rest.index("-c") + 1] if rest.index("-c") + 1 < len(rest) else ""
            mods = {m.split(".")[0] for m in re.findall(r"(?:^|[;\s])(?:import|from)\s+([\w.]+)", code)}
            sub = re.search(r"PYTHONPATH=\S*(?:/app|submission)|sys\.path\.\w+\([^)]*(?:/app|submission)", seg) or \
                (cwd or "").startswith(("/app", SUBMISSION))
            foreign = {m for m in mods if m not in PY_STDLIB}
            if foreign and sub:
                return f"python -c import {sorted(foreign)[0]}"
            return None
        if rest[:2] == ["-m", "pip"] and "install" in rest:
            if verifier_side and not re.search(r"(?:/app|submission)", seg):
                return None
            return "python -m pip install"
        return None
    if cmd not in BUILD_WORDS:
        return None
    if cmd == "node":
        if rest and rest[0] in ("-e", "-p", "--eval", "--print"):
            code = " ".join(rest[1:])
            if re.search(r"/app\b|submission|require\(\s*[\"']\.", code) or (cwd or "").startswith("/app"):
                return "node -e (loads submitted code)"
            return None
        tgt = next((w for w in rest if not w.startswith("-")), "")
        if "/tests/" in tgt or PurePosixPath(tgt).name.startswith("test_") and verifier_side:
            return None
        return "node " + tgt
    if cmd in ("make", "cmake", "gcc", "g++", "cc", "clang", "rustc", "javac"):
        if verifier_side and not re.search(r"(?:/app|submission)", seg):
            return None
        return cmd
    sub = BUILD_SUB.get(cmd)
    first = next((w for w in rest if not w.startswith("-")), "")
    if sub and not re.fullmatch(sub, first):
        return None
    if verifier_side and not re.search(r"(?:/app|submission)", seg):
        return None
    if cmd in ("pip", "pip3") and not re.search(r"\s(?:-e|--editable|-r|\.|/app\S*|\S*submission\S*)(?:\s|$)", " " + " ".join(rest)):
        return None   # a pinned verifier dependency from an index, not the submission
    return f"{cmd} {first}".strip()


def rule_root_build_sh(rel: str, sh: str, scan) -> list:
    """X4.2 (shell): a root step outside any runner phase that builds, installs, imports or runs submitted code."""
    out = []
    env = ShEnv()
    cwd = None
    for n, code in scan.lines:
        if n in scan.in_func:
            continue
        for seg in split_cmds(code):
            env.learn(seg)
            words, _ = sh_words(seg)
            if not words:
                continue
            if unquote(words[0]) in ("cd", "pushd") and len(words) > 1:
                cwd = env.expand(words[1])
                continue
            if _dropped(seg, scan):
                continue
            what = _root_build(words, cwd, env.expand(seg))
            if what:
                out.append((n, what))
    if not out:
        return []
    ln0, msg = _collapse(out, "X4.2: submitted code is built, installed, imported or run as root ({where}): "
                              "package hooks, build scripts and import-time code then run with root's rights; run "
                              "the step through setpriv/runuser/su as the runner")
    return [finding(rel, ln0, msg)]


def rule_root_build_py(rel: str, tree) -> list:
    """X4.2 (python run as root): subprocess argv lists that build or run submitted code with no privilege drop."""
    out = []
    for c in ast.walk(tree):
        if not (isinstance(c, ast.Call) and _call_name(c) in ("run", "Popen", "call", "check_call", "check_output")):
            continue
        if not c.args or not isinstance(c.args[0], (ast.List, ast.Tuple)):
            continue
        argv = [e.value if isinstance(e, ast.Constant) and isinstance(e.value, str) else "$X" for e in c.args[0].elts]
        if not argv or argv[0] == "$X":
            continue
        if any(PurePosixPath(a).name in ("setpriv", "runuser", "su", "sudo", "gosu", "su-exec") for a in argv[:3]):
            continue
        if any(k.arg in DROP_KW for k in c.keywords):
            continue
        cwd = next((ast.unparse(k.value) for k in c.keywords if k.arg == "cwd"), "")
        cwd = cwd.strip("\"'") if cwd.startswith(("'", '"')) else ("/app" if re.search(r"app|sub|work|repo", cwd, re.I) else "")
        what = _root_build([shlex_quote(a) for a in argv], cwd or None, " ".join(argv))
        if what:
            out.append((c.lineno, what))
    if not out:
        return []
    ln0, msg = _collapse(out, "X4.2: verifier Python run as root starts a build, install or run of submitted code "
                              "with no privilege drop ({where}): pass user=/preexec_fn or wrap the argv in setpriv "
                              "to the runner")
    return [finding(rel, ln0, msg)]


def shlex_quote(s: str) -> str:
    return s if re.fullmatch(r"[\w@%+=:,./-]+", s) else "'" + s.replace("'", "") + "'"


def _keyish(e) -> bool:
    s = ast.unparse(e)
    if isinstance(e, ast.Set) and all(isinstance(x, ast.Constant) and isinstance(x.value, str) for x in e.elts):
        return True
    return bool(re.search(r"\.keys\(\)|\bset\(|\bfrozenset\(|\b\w*(?:keys|fields|columns|props|properties|required|"
                          r"expected_names|allowed)\w*\b", s, re.I))


def rule_subset_keys(rel: str, tree) -> list:
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], (ast.GtE, ast.LtE)):
            if _keyish(node.left) and _keyish(node.comparators[0]) and \
                    not any(isinstance(x, ast.Constant) and isinstance(x.value, (int, float)) for x in
                            (node.left, node.comparators[0])) and \
                    not re.search(r"\blen\(", ast.unparse(node)):
                out.append((node.lineno, ast.unparse(node)[:60]))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and \
                node.func.attr in ("issubset", "issuperset") and (_keyish(node.func.value) or
                                                                  any(_keyish(a) for a in node.args)):
            out.append((node.lineno, ast.unparse(node)[:60]))
    return out


def exact_keys_contract(task: Path) -> str | None:
    """Where the contract says the key set is exact: instruction.md sentence or a schema file."""
    ip = task / "instruction.md"
    if ip.is_file():
        m = EXACT_KEYS.search(strip_fences(read(ip)))
        if m:
            return "instruction.md: " + m.group(0)[:60]
    for sd in ("tests", "environment"):
        base = task / sd
        for p in sorted(base.rglob("*.json")) if base.is_dir() else []:
            if p.stat().st_size < 2_000_000 and re.search(r"[\"']additionalProperties[\"']\s*:\s*false", read(p)):
                return p.relative_to(task).as_posix() + ": additionalProperties false"
    return None


def rule_offset_tolerant(rel: str, tree, text: str) -> list:
    out = []
    iso_names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call) and \
                _call_name(node.value) in ("fromisoformat", "isoparse", "strptime"):
            iso_names |= {t.id for t in node.targets if isinstance(t, ast.Name)}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        nm = _call_name(node)
        if nm == "astimezone" and isinstance(node.func, ast.Attribute):
            v = node.func.value
            if isinstance(v, ast.Call) and _call_name(v) in ("fromisoformat", "isoparse", "strptime") or \
                    isinstance(v, ast.Name) and v.id in iso_names:
                out.append((node.lineno, ast.unparse(node)[:60]))
        elif nm == "fromisoformat" and node.args and re.search(r"\.replace\(\s*[\"']Z[\"']\s*,\s*[\"']\+00:?00[\"']",
                                                                ast.unparse(node.args[0])):
            out.append((node.lineno, "Z replaced by +00:00, then any offset parses"))
        elif nm in ("isoparse",) or nm == "parse" and ast.unparse(node.func).startswith(("parser.", "dateutil")):
            out.append((node.lineno, ast.unparse(node.func)))
        elif nm == "strptime" and any(isinstance(a, ast.Constant) and isinstance(a.value, str) and "%z" in a.value
                                      for a in node.args):
            out.append((node.lineno, "strptime with %z"))
    return out


CAP_NAME = re.compile(r"(?i)(?:^|_)(?:max|limit|cap)")
LOG_NAME = re.compile(r"(?i)(?:^|_)(?:err|errs|stderr|log|logs|diag|debug|trace|tail|excerpt|snippet|preview|msg|"
                      r"message|reason|detail|details)(?:_|$)")
READ_ATTRS = {"read", "decode", "read_bytes", "read_text", "getvalue", "readall"}
STRIP_ATTRS = {"strip", "rstrip", "lstrip"}
LOOP_NODES = (ast.For, ast.AsyncFor, ast.While, ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp, ast.Lambda)


def _const_int(e):
    """The integer a constant expression (literal, unary minus, + - * << ** of literals) evaluates to, or None."""
    if isinstance(e, ast.Constant) and isinstance(e.value, int) and not isinstance(e.value, bool):
        return e.value
    if isinstance(e, ast.UnaryOp) and isinstance(e.op, ast.USub):
        v = _const_int(e.operand)
        return None if v is None else -v
    if isinstance(e, ast.BinOp):
        a, b = _const_int(e.left), _const_int(e.right)
        if a is None or b is None:
            return None
        ops = {ast.Add: lambda: a + b, ast.Sub: lambda: a - b, ast.Mult: lambda: a * b,
               ast.LShift: lambda: a << b if 0 <= b < 64 else None, ast.Pow: lambda: a ** b if 0 <= b < 64 else None}
        f = ops.get(type(e.op))
        return f() if f else None
    return None


def _cap_bound(e) -> bool:
    """A size bound: a constant, or an expression over MAX*/LIMIT*/CAP* names (MAX_BYTES + 1, cfg.MAX_OUT)."""
    if _const_int(e) is not None:
        return True
    names = [n.id if isinstance(n, ast.Name) else n.attr for n in ast.walk(e) if isinstance(n, (ast.Name, ast.Attribute))]
    return bool(names) and any(CAP_NAME.search(x) for x in names) and not any(
        isinstance(n, ast.Call) for n in ast.walk(e))


def _readish(e) -> bool:
    """A .read()/.decode()/.read_text()/.getvalue() result, through .strip()-like calls."""
    while isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute):
        if e.func.attr in READ_ATTRS:
            return True
        if e.func.attr not in STRIP_ATTRS:
            return False
        e = e.func.value
    return False


def _read_receiver(e) -> str:
    """The base name a read chain starts from (`err` in err.read().decode()), or ''."""
    while isinstance(e, (ast.Call, ast.Attribute, ast.Subscript)):
        e = e.func if isinstance(e, ast.Call) else e.value
    return e.id if isinstance(e, ast.Name) else ""


def _scopes(tree):
    """(scope node, its nodes without nested function bodies) for the module and every function."""
    out = []
    for sc in [tree] + [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        nodes, todo = [], list(ast.iter_child_nodes(sc))
        while todo:
            n = todo.pop()
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            nodes.append(n)
            todo.extend(ast.iter_child_nodes(n))
        out.append((sc, nodes))
    return out


def _diagnostic_use(node, par) -> bool:
    """The value only feeds a message: print or a write of the bare text (not a dict, list or json.dumps
    record, which is how an emitter prints an observation), logging, an f-string or % format, a raise or an
    assert message, or a dict key / keyword / name that says log."""
    child, p = node, par.get(node)
    structured = False
    while p is not None and not isinstance(p, ast.stmt):
        if isinstance(p, (ast.Dict, ast.List, ast.Tuple)):
            structured = True
        if isinstance(p, ast.JoinedStr) and not structured:
            return True
        if isinstance(p, ast.BinOp) and isinstance(p.op, ast.Mod) and isinstance(p.left, ast.Constant) \
                and isinstance(p.left.value, str) and not structured:
            return True
        if isinstance(p, ast.Call):
            fn = _call_name(p)
            recv = ast.unparse(p.func.value) if isinstance(p.func, ast.Attribute) else ""
            if fn in ("dumps", "dump", "emit"):
                structured = True
            if fn in ("warn", "warning", "info", "debug", "error", "exception", "critical") \
                    or re.match(r"(?:logging|log|logger)\b", recv) \
                    or (fn == "write" and re.search(r"stderr|log", recv, re.I)) \
                    or (fn in ("print", "write", "format") and not structured):
                return True
        if isinstance(p, ast.keyword) and p.arg and LOG_NAME.search(p.arg):
            return True
        if isinstance(p, ast.Dict) and child in p.values:
            k = p.keys[p.values.index(child)]
            if isinstance(k, ast.Constant) and isinstance(k.value, str) and LOG_NAME.search(k.value):
                return True
        child, p = p, par.get(p)
    if isinstance(p, (ast.Raise, ast.Assert)) and not (isinstance(p, ast.Assert) and child is p.test):
        return True
    if isinstance(p, (ast.Assign, ast.AnnAssign)):
        ts = p.targets if isinstance(p, ast.Assign) else [p.target]
        if any(isinstance(t, ast.Name) and LOG_NAME.search(t.id) for t in ts):
            return True
    return False


def rule_truncated_capture(rel: str, tree) -> list:
    """X3.4 (customer F01): captured output cut to a suffix or prefix before grading. A slice [-N:] or [:N]
    (N a constant or a MAX*/LIMIT*/CAP* bound) applied to a .read()/.decode() result, or to a name assigned
    from one in the same scope. Not flagged: a slice whose value only feeds a message (_diagnostic_use), a
    read whose receiver or target name says it is a log or stderr tail, constant bounds under 64 (a newline or
    magic-number sniff) and [:-1]-style trims."""
    out = []
    par = _parents(tree)
    for sc, nodes in _scopes(tree):
        readvars = {}
        for n in nodes:
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) \
                    and _readish(n.value):
                readvars[n.targets[0].id] = _read_receiver(n.value)
        for n in nodes:
            if not (isinstance(n, ast.Subscript) and isinstance(n.slice, ast.Slice) and n.slice.step is None):
                continue
            lo, hi = n.slice.lower, n.slice.upper
            suffix = hi is None and lo is not None and (
                (isinstance(lo, ast.UnaryOp) and isinstance(lo.op, ast.USub) and _cap_bound(lo.operand))
                or ((_const_int(lo) or 0) < 0))
            prefix = (lo is None or _const_int(lo) == 0) and hi is not None and _cap_bound(hi) and \
                (_const_int(hi) is None or _const_int(hi) > 0)
            bound = _const_int(lo if suffix else hi)
            if not (suffix or prefix) or (bound is not None and abs(bound) < 64):
                continue    # [-1:], [:4]: a newline or magic-number sniff, not a capture cap
            v = n.value
            if _readish(v):
                recv = _read_receiver(v)
            elif isinstance(v, ast.Name) and v.id in readvars:
                recv = readvars[v.id]
                if LOG_NAME.search(v.id):
                    continue
            else:
                continue
            if LOG_NAME.search(recv) or _diagnostic_use(n, par):
                continue
            out.append((n.lineno, ast.unparse(n)[:80]))
    if not out:
        return []
    ln0, msg = _collapse(out, "X3.4: captured output is truncated to a suffix or prefix before grading ({where}): "
                              "a malformed beginning or end outside the slice is never judged; reject an oversized "
                              "capture instead (fstat or a len() check against the cap) and grade it whole")
    return [finding(rel, ln0, msg)]


def rule_bounded_read(rel: str, tree) -> list:
    """X3.3 (customer F02): a bounded read with no rejection. `x = f.read(N)` / `os.read(fd, N)` outside any
    loop (an accumulate loop that compares len(data) is the template's pattern) whose result is never
    length-checked later in the same function: no Compare holds len(x), and the receiver is not read
    again (`if fh.read(1):` probes for excess). Also an unassigned bounded read (json.loads(f.read(N))).
    N must look like a size cap (a constant of 1024 or more, or a MAX*/LIMIT*/CAP* expression): small
    literal reads are magic-number sniffs and length-header reads (rfile.read(length)) are exact."""
    out = []
    par = _parents(tree)
    for sc, nodes in _scopes(tree):
        nodeset = set(nodes)
        for n in nodes:
            if not (isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "read"):
                continue
            is_os = isinstance(n.func.value, ast.Name) and n.func.value.id == "os"
            args = list(n.args) + [k.value for k in n.keywords if k.arg in ("size", "n", "length")]
            if len(args) != (2 if is_os else 1):
                continue
            size = args[-1]
            c = _const_int(size)
            if (c is not None and (c < 1024)) or not _cap_bound(size):
                continue
            p, looped = par.get(n), False
            while p is not None and p is not sc:
                if isinstance(p, LOOP_NODES):
                    looped = True
                    break
                p = par.get(p)
            if looped:
                continue
            recv = ast.unparse(n.args[0] if is_os else n.func.value)
            # the statement holding the read, and the name it is assigned to through a .decode() chain
            stmt, child = par.get(n), n
            while stmt is not None and not isinstance(stmt, ast.stmt):
                child, stmt = stmt, par.get(stmt)
            name = None
            if isinstance(stmt, (ast.Assign, ast.AnnAssign)) and (stmt.value is child):
                ts = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
                e = child
                while e is not n and isinstance(e, ast.Call) and isinstance(e.func, ast.Attribute):
                    e = e.func.value
                if e is n and len(ts) == 1 and isinstance(ts[0], ast.Name):
                    name = ts[0].id
            later = [m for m in nodeset if getattr(m, "lineno", 0) >= n.lineno and m is not n]
            checked = any(isinstance(m, ast.Compare) and any(
                isinstance(x, ast.Call) and _call_name(x) == "len" and x.args and isinstance(x.args[0], ast.Name)
                and x.args[0].id == name for x in ast.walk(m)) for m in later) if name else False
            probed = any(isinstance(m, ast.Call) and isinstance(m.func, ast.Attribute) and m.func.attr == "read"
                         and (ast.unparse(m.args[0]) if is_os and m.args else ast.unparse(m.func.value)) == recv
                         and m.lineno > n.lineno for m in later)
            if checked or probed:
                continue
            out.append((n.lineno, ast.unparse(n)[:80]))
    if not out:
        return []
    ln0, msg = _collapse(out, "X3.3: a bounded read is never checked for more data ({where}): only the first N "
                              "bytes are graded and whatever follows (invalid trailing text included) is ignored; "
                              "read N+1 and reject when len() is above the cap, or fstat the file first")
    return [finding(rel, ln0, msg)]


def verifier_code_findings(task: Path, sh: str = "", scan=None, runs_code: bool = True) -> list:
    fs = []
    exact = exact_keys_contract(task)
    ip = task / "instruction.md"
    z_shown = bool(ip.is_file() and Z_TIMESTAMP.search(read(ip)))
    root_text = "\n".join(c for n, c in scan.lines if not (scan.info.get(n) or {}).get("phase")) if scan else ""
    for p in verifier_py_files(task):
        rel = p.relative_to(task).as_posix()
        text = read(p)
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        fs += rule_empty_reader(rel, tree)
        fs += rule_prelaunch_deadline(rel, tree)
        fs += rule_truncated_capture(rel, tree)
        fs += rule_bounded_read(rel, tree)
        if runs_code and not (sh and not re.search(r"(?<![\w.-])" + re.escape(p.name) + r"\b", root_text)
                              and re.search(r"(?<![\w.-])" + re.escape(p.name) + r"\b", sh)):
            fs += rule_root_build_py(rel, tree)
        if exact:
            items = rule_subset_keys(rel, tree)
            if items:
                ln0, msg = _collapse(items, "PROC.4h9: key checks written as a subset or superset ({where}) while "
                                            f"the contract says the keys are exact ({exact}): an extra or missing key "
                                            "passes; compare the key sets with ==")
                fs.append(finding(rel, ln0, msg))
        if z_shown and not Z_ASSERTED.search(text):
            items = rule_offset_tolerant(rel, tree, text)
            if items:
                ln0, msg = _collapse(items, "PROC.4h10: timestamps are parsed offset-tolerantly ({where}) while the "
                                            "instruction shows Z timestamps: 2024-01-01T02:00:00+02:00 grades equal to "
                                            "2024-01-01T00:00:00Z; assert the literal Z form or compare the text")
                fs.append(finding(rel, ln0, msg))
    fs += rule_kill_grace(task)
    if sh:
        fs += rule_sh_prelaunch_deadline("tests/test.sh", sh)
        if scan and runs_code:
            fs += rule_root_build_sh("tests/test.sh", sh, scan)
    return fs



def declared_bar(task: Path) -> bool:
    try:
        g = json.loads(read(task / "tests/grading.json")) if (task / "tests/grading.json").is_file() else {}
    except Exception:
        g = {}
    if isinstance(g, dict) and g.get("difficulty_bar"):
        return True
    rd = read(task / "README.md") if (task / "README.md").is_file() else ""
    return bool(re.search(r"difficulty bar|\bbar\b[^.\n]{0,40}\b(\d+\s*(?:of|/)\s*\d+|max_solved|solved)", rd, re.I))


# ------------------------------------------------------------------ cheat wiring (warnings only)

_CHEAT_TARGET = re.compile(r"""(?m)^\s*TARGET=(["']?)([^"'\s#]+)\1""")
_CHEAT_KIND_LINE = re.compile(r"(?m)^#\s*tb4-cheat-kind:\s*([A-Za-z, -]+?)\s*$")
_COLLECT_REPO = re.compile(r"(?m)^\s*R=(/\S+)\s*$")


def _cheats(task: Path) -> dict:
    """{name: solve.sh path} for cheat/<name>/solve.sh, plus a legacy cheat/solve.sh named 'cheat'."""
    cdir, out = task / "cheat", {}
    if (cdir / "solve.sh").is_file():
        out["cheat"] = cdir / "solve.sh"
    if cdir.is_dir():
        for p in sorted(cdir.iterdir()):
            if (p / "solve.sh").is_file():
                out[p.name] = p / "solve.sh"
    return out


def _read_or_empty(p: Path) -> str:
    try:
        return read(p) if p.is_file() else ""
    except OSError:
        return ""


def _verifier_text(task: Path) -> str:
    """Every text file under tests/ and solution/, and instruction.md: what could name a cheat's TARGET."""
    parts = [_read_or_empty(task / "instruction.md")]
    for sub in ("tests", "solution"):
        root = task / sub
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*")):
            if p.is_file() and p.stat().st_size <= 2_000_000:
                try:
                    parts.append(p.read_text(errors="replace"))
                except OSError:
                    pass
    return "\n".join(parts)


def cheat_wiring_warnings(task: Path, d: dict | None = None) -> list:
    """Warnings (never blocking) for a cheat that may never fire, so its 0 would prove nothing.

    The tamper control passes any cheat that scores 0, and a cheat scores 0 just as surely when it never ran.
    Two cases are visible in the task itself: TARGET lies outside what the collect hook ships to the verifier
    (or, for a repo-fix task, in a test glob the verifier restores from pristine), and nothing in tests/,
    solution/ or instruction.md names TARGET, so no graded step is shown to import, run or read it. Unfilled
    or dynamic TARGETs are left to the tamper control (it ERRORs on them); a task whose collect hook names no
    root this check can read is skipped."""
    out = []
    cheats = _cheats(task)
    if not cheats:
        return out
    toml_raw = _read_or_empty(task / "task.toml")
    roots = _COLLECT_REPO.findall(toml_raw)
    if "/app/output" in toml_raw:
        roots.append("/app/output")
    roots = [r.rstrip("/") for r in roots if "<" not in r]
    if not roots:
        return out
    grading = {}
    try:
        grading = json.loads(_read_or_empty(task / "tests" / "grading.json") or "{}")
    except ValueError:
        pass
    if not isinstance(grading, dict):
        grading = {}
    globs = [g for g in (grading.get("test_globs") or []) if isinstance(g, str)]
    text = None
    for name, sh in cheats.items():
        body = _read_or_empty(sh)
        m = _CHEAT_TARGET.search(body)
        if not m:
            continue
        target = m.group(2)
        if "CHANGE_ME" in target or "<" in target or "$" in target or not target.startswith("/"):
            continue
        rel_sh = sh.relative_to(task).as_posix()
        line = body[:m.start()].count("\n") + 1
        root = next((r for r in roots if target == r or target.startswith(r + "/")), None)
        if root is None:
            out.append(finding(rel_sh, line, f"cheat {name}: TARGET {target} is outside what the collect hook ships "
                               f"({', '.join(roots)}), so the payload never reaches the verifier and its 0 proves nothing"))
            continue
        rel = target[len(root) + 1:]
        if rel and any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(PurePosixPath(rel).name, g) for g in globs):
            out.append(finding(rel_sh, line, f"cheat {name}: TARGET {target} matches a test glob the verifier restores "
                               "from pristine, so the payload is wiped before the tests run and its 0 proves nothing"))
            continue
        if text is None:
            text = _verifier_text(task)
        p = PurePosixPath(rel or target)
        names = {p.as_posix(), p.name}
        if p.suffix == ".py":
            names |= {p.with_suffix("").as_posix().replace("/", "."), p.stem}
        if not any(n and n in text for n in names):
            out.append(finding(rel_sh, line, f"cheat {name}: nothing in tests/, solution/ or instruction.md names "
                               f"TARGET {target}, so no graded step is shown to import, run or read it; point TARGET "
                               "at a file the graded tests import (repo-fix) or the verifier runs or reads (output "
                               "task), or the cheat may never fire"))
    return out


def gate_structure(task: Path) -> GateResult:
    try:
        d = load_toml(task)
    except Exception as e:
        return GateResult("ERROR", f"task.toml does not parse: {e}")
    toml_raw = read(task / "task.toml")
    v2 = is_v2(task, d)
    fs = []
    legacy = []                       # (short, long) v2 file-set items, one finding on legacy tasks
    for f in ("tests/requirements.json", "tests/budget.json"):
        if not (task / f).is_file():
            legacy.append((f"{f} missing", finding(f, 0, f"{f} missing (v2 file set)")))
    arts = artifact_sources(d)
    aline = line_of(toml_raw, "artifacts")
    if arts != [SUBMISSION]:
        legacy.append((f"artifacts = {arts} (v2 requires exactly [\"{SUBMISSION}\"])",
                       finding("task.toml", aline, f"artifacts = {arts} (v2 requires exactly [\"{SUBMISSION}\"])")))
    hooks = (d.get("verifier") or {}).get("collect") or []
    hline = line_of(toml_raw, "[[verifier.collect]]")
    mv_re = re.compile(r"\bmv\s+(?:-\S+\s+)*\S+\s+[\"']?" + re.escape(SUBMISSION) + r"/?[\"']?\s*;?\s*$")
    good_hook = False
    for h in hooks:
        cmd = str(h.get("command", "")) if isinstance(h, dict) else ""
        segs = [s.strip() for s in re.split(r"&&|;|\n|\|\|", cmd) if s.strip() and not s.strip().startswith("#")]
        if segs and mv_re.search(segs[-1]):
            good_hook = True
            continue
        for tok in re.findall(r"[\w./-]+\.sh", cmd):
            cand = [p for p in (task / "environment").rglob(PurePosixPath(tok).name)] if (task / "environment").is_dir() else []
            for c in cand:
                lines = [l.strip() for l in read(c).splitlines() if l.strip() and not l.strip().startswith("#")]
                if lines and mv_re.search(lines[-1]):
                    good_hook = True
    if not good_hook:
        msg = ("no [[verifier.collect]] hook whose last command is an `mv` into "
               f"{SUBMISSION} (a failed hook must leave nothing behind)" if hooks else
               "no [[verifier.collect]] hook: the submission is not captured atomically")
        legacy.append((msg.split(" (")[0], finding("task.toml", hline, msg)))
    if v2:
        fs += [f for _, f in legacy]
    elif legacy:
        fs.append(finding("task.toml", aline or hline, "legacy task, not on the v2 file set: "
                          + "; ".join(s for s, _ in legacy)))
    runs_code = runs_submitted_code(task, d)
    if runs_code:
        fs += promise_findings(task)
    tsh = task / "tests/test.sh"
    sh = read(tsh) if tsh.is_file() else ""
    scan = ShScan(task, sh) if sh else None
    runners = scan.runners if scan else RUNNER_DEFAULT
    vdf = task / "tests/Dockerfile"
    watch = [a.rstrip("/") for a in arts] + [SUBMISSION]
    if not vdf.is_file():
        fs.append(finding("tests/Dockerfile", 0, "missing: the verifier image is not defined"))
    else:
        df = read(vdf)
        chmod_ok = re.search(r"chmod\s+(?:-R\s+)?0?700\s+/tests\b|chmod\s+(?:-R\s+)?go-rwx\s+/tests\b", df)
        if not chmod_ok and runs_code:
            fs.append(finding("tests/Dockerfile", 0, "/tests is not locked with chmod 700 (the runner can read answers)"))
        workdir = None
        rules = {"mkdir": [], "copy": [], "checkout": []}
        checkout_at = set()
        for n, ln in logical_lines(df):
            s = ln.strip()
            m = re.match(r"(?i)WORKDIR\s+(\S+)", s)
            if m:
                workdir = m.group(1).rstrip("/")
            for a in watch:
                ap = PurePosixPath(a)
                if re.search(r"mkdir[^&;]*\s" + re.escape(a) + r"(/|\s|$)", s) or re.match(
                        r"(?i)WORKDIR\s+" + re.escape(a) + r"/?$", s):
                    rules["mkdir"].append((n, a))
                m2 = re.match(r"(?i)(COPY|ADD)\s+(?:--\S+\s+)*.+\s(\S+)$", s)
                if m2:
                    dest = PurePosixPath(m2.group(2).rstrip("/") or "/")
                    if str(dest) not in ("/", "/app", "/tests") and (dest == ap or dest in ap.parents or ap in dest.parents):
                        rules["copy"].append((n, f"{dest} around {a}"))
                if re.search(r"\bgit\s+(clone|checkout|fetch|init)\b|pip install\s+(-e|--editable)", s):
                    tgt = workdir
                    mc = re.search(r"git\s+clone\s+(?:-\S+\s+(?:\S+\s+)?)*\S+\s+(/\S+)", s)
                    if mc:
                        tgt = mc.group(1).rstrip("/")
                    if tgt and tgt not in ("/", "/app") and (PurePosixPath(tgt) == ap or PurePosixPath(tgt) in ap.parents):
                        rules["checkout"].append((n, a))
                        checkout_at.add(tgt)
        msgs = {"mkdir": "creates the artifact path(s) in the verifier image ({where}): a missing submission is "
                         "graded as this empty or pristine path",
                "copy": "copies files at or around the artifact path ({where}): a missing submission would grade "
                        "this copy",
                "checkout": "puts a code checkout at {at}, over the artifact path(s) ({where}); the pristine "
                            "copy belongs at /pristine/<repo>"}
        for k, items in rules.items():
            if items:
                ln0, msg = _collapse(items, msgs[k].replace("{at}", ", ".join(sorted(checkout_at))))
                fs.append(finding("tests/Dockerfile", ln0, msg))
        # spec rule 5: the work tree is root-owned and read-only to the runner
        wt = [(n, p) for n, p in dockerfile_runner_chowns(df, runners)
              if p.startswith(WORKTREE_ROOTS) or any(_under(p, a) for a in watch)]
        if wt:
            ln0, msg = _collapse(wt, "the runner owns the work tree ({where}): it can rewrite graded code, tests "
                                     "or build outputs between phases; keep it root-owned and read-only (spec rule 5)")
            fs.append(finding("tests/Dockerfile", ln0, msg))
    if tsh.is_file():
        wr = runner_wrappers(sh) | {"setpriv", "runuser", "gosu", "su-exec"}
        py_lines = []
        for n, ln in logical_lines(sh):
            code = ln.split("#", 1)[0]
            if "pytest" in code and re.search(r"(?<![\w-])/tests/", code) and (
                    any(re.search(r"(?<![\w-])" + re.escape(w) + r"\b", code) for w in wr)
                    or re.search(r"sudo\s+-u|\bsu\s+\w+\s+-c", code)):
                py_lines.append((n, ""))
        if py_lines:
            ln0, msg = _collapse(py_lines, "pytest runs as the runner user on /tests ({where}): the submission's "
                                           "user then reads the graded tests and writes the report")
            fs.append(finding("tests/test.sh", ln0, msg))
        fs += fail_closed_findings(task, sh, scan, watch, runs_code)
        fl = re.search(r"(?m)^\s*(?:export\s+)?(\w*FLOOR\w*)=[\"']?(\d+)", sh)
        if fl and not re.search(r"\bwant\s*[-=|]|\bmissing\s*=|[\"']missing[\"']|by name|names?_in\b|expected[-_ ]?names|"
                                r"\bnames\s*=|\bgraded[-_]\w+\.txt|\btest[-_]?ids\b|\.split\(\"::\"\)", sh):
            fs.append(finding("tests/test.sh", sh[:fl.start()].count("\n") + 1,
                              f"{fl.group(1)}={fl.group(2)} is a bare count: no list of expected test names is checked, so "
                              f"a run that swaps or duplicates tests still reaches the floor; assert the names"))
        wt = [(n, p) for p, n in scan.chowned
              if p.startswith(WORKTREE_ROOTS) or any(_under(p, a) for a in watch)]
        if wt:
            ln0, msg = _collapse(wt, "the runner owns the work tree ({where}): it can rewrite graded code, tests "
                                     "or build outputs between phases; keep it root-owned and read-only (spec rule 5)")
            fs.append(finding("tests/test.sh", ln0, msg))
        if runs_code:
            for rule, items in scan.findings().items():
                if items:
                    ln0, msg = _collapse(items, SH_RULES[rule])
                    fs.append(finding("tests/test.sh", ln0, msg))
            # python the verifier runs as root: every tests/*.py not started only by a runner phase
            root_text = "\n".join(c for n, c in scan.lines if not (scan.info.get(n) or {}).get("phase"))
            for p in sorted((task / "tests").rglob("*.py")):
                if not re.search(r"(?<![\w.-])" + re.escape(p.name) + r"\b", root_text) and \
                        re.search(r"(?<![\w.-])" + re.escape(p.name) + r"\b", sh):
                    continue  # started only by a runner phase
                rel = p.relative_to(task).as_posix()
                items = py_root_opens(rel, read(p), runners)
                if items:
                    ln0, msg = _collapse(items, "root opens a path for writing inside a runner-owned directory "
                                                "without O_NOFOLLOW ({where}): a planted symlink turns it into a root "
                                                "write primitive (spec rule 7)")
                    fs.append(finding(rel, ln0, msg))
    else:
        fs.append(finding("tests/test.sh", 0, "missing"))
    fs += verifier_code_findings(task, sh, scan, runs_code)
    fs += content_rules.crlf_findings(task)
    warns = [] if declared_bar(task) else [finding("tests/grading.json", 0, "no difficulty bar declared "
                                                   "(grading.json difficulty_bar.max_solved or a README 'difficulty "
                                                   "bar'); the attempts gate falls back to the pack floor: at least 2 of k must fail")]
    warns += cheat_wiring_warnings(task, d)
    return GateResult("FAIL" if fs else "PASS",
                      ("v2 file set complete" if not fs else
                       ("v2 task with structural defects" if v2 else
                        "legacy task: migrate to the v2 template; missing or wrong: ")
                       + ("" if v2 else "; ".join(f["message"].split(" (")[0].split(": ", 1)[-1][:120]
                                                  for f in fs[:6])))
                      + ("" if runs_code else "; the verifier runs no submitted code, so the /tests lock and "
                                              "root-touch rules do not apply"), fs, warns)


# ------------------------------------------------------------------ lint

LINTER = HERE / "tb4-lint.py"


def toml_key_line(p: Path, msg: str) -> int:
    """The line of the first task.toml key or [table] a lint message names, or 0."""
    try:
        lines = read(p).splitlines()
    except OSError:
        return 0
    for m in re.finditer(r"\[([\w.]+)\]|\b([a-z][a-z0-9_]{2,})\b", msg):
        tbl, key = m.group(1), m.group(2)
        for n, ln in enumerate(lines, 1):
            if tbl and re.match(r"^\s*\[{1,2}" + re.escape(tbl) + r"\]{1,2}\s*$", ln):
                return n
            if key and re.match(r"^\s*" + re.escape(key) + r"\s*=", ln):
                return n
    return 0


def gate_lint(task: Path) -> GateResult:
    spec = importlib.util.spec_from_file_location("tb4lint", LINTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    r = mod.lint(task)
    fs, warns = [], []
    for crit, verdict, msg, evd in r.rows:
        path, line = str(evd or ""), 0
        m = re.match(r"^(?:inventory:)?(.*?)(?::(\d+))?$", path)
        if m:
            path, line = m.group(1), int(m.group(2) or 0)
        try:
            path = Path(path).resolve().relative_to(task).as_posix()
        except (ValueError, OSError):
            pass
        if not line and path.endswith(".toml"):
            line = toml_key_line(task / path, msg)
        f = finding(path or ".", line, f"[{crit}] {msg}")
        if verdict == "FAIL":
            fs.append(f)
        elif verdict == "WARN":
            warns.append(f)
    crits = sorted({f["message"].split("]")[0][1:] for f in fs})
    return GateResult("FAIL" if fs else "PASS",
                      f"tb4-lint: {len(r.rows)} rows, {len(fs)} FAIL" + (f" across {', '.join(crits)}" if crits else "")
                      + f", {len(warns)} WARN (warnings never block)", fs, warns, evidence=[str(LINTER)])


# ------------------------------------------------------------------ placeholders (tb4 check runs it first)

def gate_placeholders(task: Path) -> GateResult:
    """Template placeholders left in the task (<40-hex-sha>, /app/<repo>, <Task Title>, CHANGE_ME), file:line
    each. `tb4 new` prints the same list (content_rules.placeholder_findings)."""
    fs = content_rules.placeholder_findings(task)
    files = sorted({f["path"] for f in fs})
    return GateResult("FAIL" if fs else "PASS",
                      f"{len(fs)} line(s) with an unfilled template placeholder in {len(files)} file(s)" if fs
                      else "no template placeholder left", fs, evidence=[str(content_rules.TEMPLATE_DIR)])


# ------------------------------------------------------------------ content (the rules packaging and criteria run)

CRYPTO_CLAIM = re.compile(r"\b(?:Ed25519|ECDSA)\b|\bRSA[- ](?:PSS[- ])?(?:signatures?|signed|signing)\b|"
                          r"\bcryptographic(?:ally)?[- ](?:sign|signed|signing|signatures?)\b", re.I)
SIGN_WORD = re.compile(r"\bsign(?:s|ed|ing|er|ers|ature|atures)?\b", re.I)
CRYPTO_VERIFIER = re.compile(
    r"(?m)^\s*(?:from|import)\s+(?:cryptography|nacl|ed25519|ecdsa|Crypto|Cryptodome|pure25519|signify|jwt|jose)\b|"
    r"\bhmac\.compare_digest\b|\"crypto/(?:ed25519|ecdsa|rsa)\"|golang\.org/x/crypto/ed25519|\bed25519_dalek\b|"
    r"\bring::signature\b|\becdsa::|\bcrypto\.verify\(|\bcreateVerify\(|\bsubtle\.verify\(|tweetnacl|@noble/|"
    r"\bSignature\.getInstance\(|\bEVP_DigestVerify|\bEVP_PKEY_verify|\bcrypto_sign_(?:verify|open)|"
    r"\bopenssl\s+(?:verify|(?:dgst|pkeyutl|smime|cms|rsautl)\b[^\n]*\s-verify)\b|\bssh-keygen\b[^\n]*-Y\s+verify|"
    r"\bgpg2?\b[^\n]*--verify|\bminisign\b[^\n]*\s-V\b|\bsignify\b[^\n]*\s-V\b|\bcosign\s+verify")
SURVIVE_CLAIM = re.compile(
    r"\b(?:no|nothing|none)\b(?=[^.;:]{0,60}?\b(?:process|descendant|child|daemon|started|spawned|runner|"
    r"helper|orphan|leftover))[^.;:]{0,60}?\b(?:survives?|outlives?|outlasts?|lingers?)\b|"
    r"\bno (?:descendant|child|process|orphan|leftover)(?:es|s|ren)?\b[^.;:]{0,40}?\b(?:remains?|is left|"
    r"stays? alive|keeps? running)\b|"
    r"\b(?:every|all|each) (?:process(?:es)?|descendants?|child(?:ren)?)\b[^.;:]{0,60}?\bkilled\b|"
    r"\bkills? (?:every|all|each) (?:process(?:es)?|descendants?|child(?:ren)?)\b", re.I)
GROUP_KILL = re.compile(r"\bkillpg\b|\bkill\s+(?:-\S+\s+)*--\s+-|\bkill\s+-(?:9|KILL|SIGKILL|TERM)\s+-[$\d]")
UID_KILL = re.compile(r"\bkill\(\s*-1\b|\bkill\s+(?:-\S+\s+)*-1\b|\b(?:pkill|killall)\b[^\n]*\s-[uU]\b|"
                      r"cgroup\.kill|cgroup\.procs|\bkill_runner\b|\bsetrlimit\(\s*resource\.RLIMIT_NPROC|"
                      r"\bprctl\b[^\n]*PR_SET_CHILD_SUBREAPER")
CLAIM_EXT = {".md", ".txt", ".py", ".sh", ".go", ".rs", ".js", ".mjs", ".ts", ".json", ".toml", ".c", ".h", ".rb"}


def _claim_texts(task: Path, tops):
    """(rel, text) for README.md, instruction.md and the text files under the given task subdirs."""
    out = []
    for f in ("README.md", "instruction.md"):
        if (task / f).is_file():
            out.append((f, read(task / f)))
    for top in tops:
        d = task / top
        if not d.is_dir():
            continue
        for p in sorted(d.rglob("*")):
            if p.is_file() and (p.suffix in CLAIM_EXT or p.name == "Dockerfile") and p.stat().st_size < 1_000_000:
                out.append((p.relative_to(task).as_posix(), read(p)))
    return out


def _line_at(text: str, pos: int) -> int:
    return text.count("\n", 0, pos) + 1


def _code_only(rel: str, text: str) -> str:
    """The text with comments (and, for Python, string literals) blanked: what the file does, not says."""
    if rel.endswith(".py"):
        return _py_code_views(text)[1]
    if rel.endswith(".sh") or PurePosixPath(rel).name == "Dockerfile":
        return "\n".join(_strip_comment(ln) for ln in text.splitlines())
    if rel.endswith(".md") or rel.endswith(".txt") or rel.endswith(".json"):
        return ""
    return text


def claim_code_findings(task: Path) -> list:
    """Documentation that promises more than the code does.
      C1 (customer F05): the task text (README, instruction, environment/, tests/, solution/ files) names an
         Ed25519 / ECDSA / RSA signature or a cryptographic signature (Ed25519 and ECDSA count only within
         80 characters of sign*, so an "ssh-ed25519" key type is not a claim), while no task file imports or
         calls a real verifier (cryptography, nacl, ed25519, hmac.compare_digest, crypto/ed25519,
         openssl ... -verify, gpg --verify, ...). Mock hashes labelled as signatures fail here.
      C2 (customer F06): README, instruction or a verifier file (tests/) claims that no descendant or process
         survives, or that every process is killed, while the cleanup code behind the claim has killpg (or
         `kill -- -PGID`) and no uid-wide kill (kill(-1), pkill/killall -u, cgroup.kill, kill_runner). The
         code behind a claim in a tests/ file is that file plus the tests/ modules it imports; behind a
         README/instruction claim it is the tests/ files the claim's paragraph names, else every tests/ file."""
    fs = []
    texts = _claim_texts(task, ("environment", "tests", "solution"))
    code = [(rel, t) for rel, t in texts if rel not in ("README.md", "instruction.md")]
    # ---- C1
    claims = []
    for rel, t in texts:
        flat = t.replace("\n", " ")
        for m in CRYPTO_CLAIM.finditer(flat):
            near = flat[max(0, m.start() - 80):m.end() + 80]
            if m.group(0).lower() in ("ed25519", "ecdsa") and not SIGN_WORD.search(near):
                continue
            claims.append((rel, _line_at(t, m.start()), m.group(0)))
            break
    if claims and not any(CRYPTO_VERIFIER.search(t) for rel, t in code if not rel.endswith((".md", ".txt", ".json"))):
        where = ", ".join(f"{r}:{n} ({w})" for r, n, w in claims[:6]) + (
            f", +{len(claims) - 6} more" if len(claims) > 6 else "")
        fs.append(finding(claims[0][0], claims[0][1],
                          f"C1: the task describes cryptographic signatures ({where}) but no task file imports or "
                          "calls a real signature verifier (cryptography, nacl, crypto/ed25519, hmac.compare_digest, "
                          "openssl ... -verify): a hash or mock labelled as a signature proves nothing about "
                          "authenticity; verify it with a real library or describe it as the checksum it is"))
    # ---- C2
    tests = {rel: t for rel, t in texts if rel.startswith("tests/") and _code_only(rel, t)}
    for rel, t in texts:
        if not (rel in ("README.md", "instruction.md") or rel in tests):
            continue
        flat = t.replace("\n", " ")
        hits = list(SURVIVE_CLAIM.finditer(flat))
        if not hits:
            continue
        if rel in tests:
            scope = [rel] + [r for r in tests if r.endswith(".py") and r != rel and re.search(
                r"(?m)^\s*(?:from|import)\s+" + re.escape(PurePosixPath(r).stem) + r"\b", t)]
        else:
            named = set()
            for m in hits:
                a, b = t.rfind("\n\n", 0, m.start()), t.find("\n\n", m.end())
                para = t[max(a, 0):b if b >= 0 else len(t)]
                named |= {r for r in tests if re.search(r"(?<![\w.-])" + re.escape(PurePosixPath(r).name) + r"\b", para)}
            scope = sorted(named) or sorted(tests)
        body = "\n".join(_code_only(r, tests[r]) for r in scope)
        if GROUP_KILL.search(body) and not UID_KILL.search(body):
            items = [(_line_at(t, m.start()), m.group(0)[:60]) for m in hits]
            ln0, msg = _collapse(items, "C2: the text promises that no process outlives the cleanup ({where}), but "
                                        f"the cleanup in {', '.join(scope[:4])} kills only a process group "
                                        "(killpg): a descendant that calls setsid() leaves the group and survives; "
                                        "add a uid-wide kill (kill(-1) as the runner, pkill -u) with a survivor "
                                        "check, or narrow the claim to the process group")
            fs.append(finding(rel, ln0, msg))
    return fs


def gate_content(task: Path) -> GateResult:
    """The task-content rules `tb4 package` and `tb4 criteria` apply, run on the task before the controls:
    FROM digest pins, lockfiles and D1 masked build steps (dockerfile_findings), C1/C2 documentation that
    promises more than the code does (claim_code_findings), the email scan over the task's files
    (email_findings), README cite resolution (doc_cite_findings), the registered upstream checks
    (run-upstream-checks.sh), hygiene (hygiene.py with the test-data exemptions) and tbench-assess's
    structure and parameter rules. Same functions, same messages: a FAIL here is the FAIL packaging or the
    criteria tier would give later, after the Docker controls and the paid attempt."""
    fs, warns, notes = [], [], []
    counts = {}

    def add(kind, items):
        counts[kind] = counts.get(kind, 0) + len(items)
        fs.extend(items)

    tree = Tree(task)
    docker = [p for p in tree.paths if PurePosixPath(p).name == "Dockerfile" or p.endswith(".Dockerfile")]
    add("base image / lockfile / masked build", [f for p in docker for f in dockerfile_findings(tree, p)])
    add("claim vs code", claim_code_findings(task))
    mfs, mwarns = email_findings(tree, tree.paths, "task.toml", "task.toml")
    add("email", mfs)
    warns += mwarns
    if tree.exists("README.md"):
        root = delivery_root(task)
        rel = None
        if root is not None:
            try:
                rel = task.resolve().relative_to(Path(root).resolve()).as_posix()
            except ValueError:
                rel = None
        if rel:   # a delivery around the task: cites resolve against it, as packaging resolves them
            cites = doc_cite_findings(Tree(Path(root)), [rel + "/README.md"], rel)
            cites = [finding("README.md", f["line"], f["message"]) for f in cites]
        else:     # a bare task: evidence/ and provenance/ exist only once `tb4 package` assembles them
            cites = doc_cite_findings(tree, ["README.md"], "", skip_tops=PACKAGE_TIME_TOPS, skip_bare=True)
        add("README cite", cites)
    ufs, uerr = content_rules.upstream_findings(task)
    add("upstream check", ufs)
    hfs, hwarns = content_rules.hygiene_findings(task, with_warnings=True)
    add("hygiene", hfs)
    warns += hwarns
    tfs, twarns, tnote = content_rules.task_rules_findings(task)
    add("tbench-assess rule", tfs)
    warns += twarns
    if tnote:
        notes.append(tnote)
    for f in fs + warns:   # point at the key, never at task.toml:0
        if not f["line"] and f["path"].endswith(".toml"):
            f["line"] = toml_key_line(task / f["path"], f["message"])
    summary = ", ".join(f"{n} {k}" for k, n in counts.items() if n) or "0 findings"
    details = f"task-content rules shared with `tb4 package` and `tb4 criteria`: {summary}" + \
        (f"; {'; '.join(notes)}" if notes else "")
    if uerr:
        return GateResult("ERROR", details + f"; the upstream checks could not run: {uerr}", fs, warns,
                          evidence=[str(content_rules.UPSTREAM_RUNNER)])
    return GateResult("FAIL" if fs else "PASS", details, fs, warns,
                      evidence=[str(content_rules.UPSTREAM_RUNNER), str(HERE / "hygiene.py")])


# ------------------------------------------------------------------ packaging

NUMWORD = {w: i for i, w in enumerate("zero one two three four five six seven eight nine ten eleven twelve".split())}
COUNT_CLAIM = re.compile(r"(?<![\w.-])(\d+|" + "|".join(NUMWORD) + r")\s+(?:graded\s+|model\s+|real\s+|scored\s+|"
                         r"pass@k\s+)?(?:attempts?|runs?|trials?)\b|\bpass@(\d+)\b|\bk\s*=\s*(\d+)\b", re.I)
SHIP_CUE = re.compile(r"\b(ships?|shipped|shipping|deliver(?:y|ed|s|ing)?|attempts?\s+folders?|attempt\s+directories)\b",
                      re.I)
HISTORY_HEAD = re.compile(r"version|history|earlier|previous|superseded|changelog", re.I)
HISTORY_SEG = re.compile(r"^(history[\w.-]*|v\d+(?:\.\d+)*(?:-[\w-]+)?|superseded[\w.-]*|previous[\w.-]*|drafts?|"
                         r"old[-_][\w.-]*|[\w-]*-v\d+-task)$", re.I)
TRANSCRIPT_NAMES = {"trajectory.json", "recording.cast"}
TOOLKIT = {p.name for p in HERE.iterdir()} | {"report.schema.json", "tb4", "validate.sh", "package_task.py"}
PLACEHOLDER = re.compile(r"(^|[-_/])(N|K|X|NN|k|n)(/|$|[-_.])|\.\.|[<>{}*]")
KNOWN_EXT = {"py", "sh", "go", "rs", "js", "mjs", "cjs", "ts", "json", "jsonl", "toml", "patch", "diff", "csv", "tsv",
             "yaml", "yml", "txt", "pdf", "md", "log", "cast", "xml", "html", "npz", "png", "zip", "gz", "tar", "c",
             "h", "cpp", "rb", "php", "sql", "ipynb", "lock", "cfg", "ini", "svg", "jpg", "jpeg", "parquet", "db"}
# File names a Python toolchain gives a role: a README that writes one bare names the mechanism (python3 runs a folder that
# holds a __main__.py, a sitecustomize.py runs at start-up, the suite's excluded pyproject.toml/setup.py/setup.cfg/
# conftest.py), not a file of the delivery: import-entry-audit, kilnrun-restart, sqlglot-duckdb-sqlite. A cite with a
# folder (src/pkg/__main__.py) is still checked.
CONVENTION_NAMES = {"__main__.py", "__init__.py", "sitecustomize.py", "usercustomize.py", "conftest.py", "pyproject.toml",
                    "setup.py", "setup.cfg", "pytest.ini", "tox.ini"}
LOCKFILES = {"package-lock.json", "npm-shrinkwrap.json", "yarn.lock", "pnpm-lock.yaml", "uv.lock", "poetry.lock",
             "pdm.lock", "Pipfile.lock", "requirements.lock"}


def is_transcript(p: str) -> bool:
    """Agent transcripts and third-party artifacts: their emails are not the author's."""
    pp = PurePosixPath(p)
    return pp.name in TRANSCRIPT_NAMES or pp.suffix == ".pane" or any(s in ("agent", "artifacts") for s in pp.parts[:-1])


def cite_candidate(t: str) -> bool:
    """A token that names a file: not a placeholder, identifier, docker ref, URL or toolkit script."""
    t = t.strip()
    if not t or t.startswith(("/", "~", "$")) or ":" in t or PLACEHOLDER.search(t):
        return False
    name = PurePosixPath(t.rstrip("/")).name
    if name in TOOLKIT or t.rstrip("/") in TOOLKIT:
        return False
    if "/" not in t.rstrip("/"):
        ext = name.rsplit(".", 1)[-1] if "." in name else ""
        return ext in KNOWN_EXT  # "time.Time", "Scene.dump", "RDLOG.C" are identifiers
    return True


class Tree:
    """A delivery as a set of relative paths plus text access; a directory or a zip."""

    def __init__(self, src: Path):
        self.src = src
        self.zip = None
        if src.is_file():
            self.zip = zipfile.ZipFile(src)
            names = [n for n in self.zip.namelist() if not n.endswith("/")]
            tops = {n.split("/", 1)[0] for n in names}
            self.prefix = (tops.pop() + "/") if len(tops) == 1 and all("/" in n for n in names) else ""
            self.paths = [n[len(self.prefix):] for n in names]
        else:
            self.prefix = ""
            self.paths = [p.relative_to(src).as_posix() for p in src.rglob("*") if p.is_file()]
        self.pathset = set(self.paths)
        self.dirs = {str(PurePosixPath(p).parent) for p in self.paths}
        for p in list(self.dirs):
            q = PurePosixPath(p)
            self.dirs |= {str(x) for x in q.parents}

    def size(self, rel):
        return self.zip.getinfo(self.prefix + rel).file_size if self.zip else (self.src / rel).stat().st_size

    def text(self, rel, limit=3_000_000):
        if self.size(rel) > limit:
            return None
        data = self.zip.read(self.prefix + rel) if self.zip else (self.src / rel).read_bytes()
        if b"\0" in data[:4096]:
            return None
        return data.decode("utf-8", errors="replace")

    def exists(self, rel):
        rel = rel.strip("/")
        return rel in self.pathset or rel in self.dirs

    def extract_task(self, task_rel: str, dest: Path) -> Path:
        out = dest / PurePosixPath(task_rel).name
        for p in self.paths:
            if p == task_rel or p.startswith(task_rel + "/"):
                target = out / p[len(task_rel):].lstrip("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(self.zip.read(self.prefix + p) if self.zip else (self.src / p).read_bytes())
        return out


NONCANON_SEG = re.compile(r"^(_?provenance|history[\w.-]*|[\w.-]*superseded[\w.-]*|[\w.-]*previous[-_]versions?[\w.-]*)$",
                          re.I)


def noncanonical_reason(d: str) -> str | None:
    """Why a task directory (relative posix path) cannot be a canonical task root, or None."""
    for seg in PurePosixPath(d).parts:
        if NONCANON_SEG.match(seg):
            return f"under {seg}/"
        if HISTORY_SEG.match(seg):
            return f"under the history-named folder {seg}/"
    return None


def task_descriptors(paths):
    """Discover task.toml at ANY depth in a set of relative posix file paths. Returns (canonical, other):
    canonical task roots are directories holding task.toml AND instruction.md whose path has no provenance/,
    history, superseded or previous-version segment; `other` is every remaining descriptor as
    (task.toml path, reason)."""
    pathset = set(paths)
    canon, other = [], []
    for t in sorted(p for p in paths if PurePosixPath(p).name == "task.toml"):
        d = str(PurePosixPath(t).parent)
        d = "" if d == "." else d
        why = noncanonical_reason(d)
        if why is None and ((d + "/") if d else "") + "instruction.md" not in pathset:
            why = "no instruction.md beside it"
        if why is None:
            canon.append(d)
        else:
            other.append((t, why))
    return canon, other


def zip_entry_problems(zf) -> list:
    """Unsafe entries in an archive, as (entry name, reason): absolute paths, '..' components, symlinks,
    device or special files, and names that collide after normalisation (NFC, case-folded, ./ and // removed).
    A delivery holding any of them is rejected, never extracted around."""
    out, files, dirs = [], {}, set()
    for info in zf.infolist():
        n = info.filename
        parts = re.split(r"[\\/]", n)
        mode = (info.external_attr >> 16) & 0xFFFF
        why = None
        if n.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", n):
            why = "absolute path"
        elif ".." in parts:
            why = "'..' path component"
        elif mode and stat.S_ISLNK(mode):
            why = "symlink"
        elif mode and (stat.S_ISCHR(mode) or stat.S_ISBLK(mode) or stat.S_ISFIFO(mode) or stat.S_ISSOCK(mode)):
            why = "device or special file"
        if why:
            out.append((n, why))
            continue
        key = unicodedata.normalize("NFC", posixpath.normpath(n.replace("\\", "/"))).casefold()
        if n.endswith("/"):
            if key in files:
                out.append((n, f"directory collides with file {files[key]!r} after normalisation"))
            dirs.add(key)
            continue
        if key in files:
            out.append((n, f"duplicate of {files[key]!r} after normalisation"))
        elif key in dirs:
            out.append((n, "collides with a directory entry after normalisation"))
        else:
            files[key] = n
    return out


def task_id_of_zip(z: Path) -> str:
    try:
        with zipfile.ZipFile(z) as zf:
            names = [n for n in zf.namelist() if not n.endswith("/")]
            canon, _ = task_descriptors(names)
            if len(canon) == 1:
                rel = (canon[0] + "/") if canon[0] else ""
                name = tomllib.loads(zf.read(rel + "task.toml").decode("utf-8", "replace")).get("task", {}).get("name", "")
                if name:
                    return name.split("/")[-1]
    except Exception:
        pass
    return re.sub(r"(-\d{8}.*|-v\d+.*|-pass\d+.*|-gpt-.*)$", "", z.stem)


def _json_strings(x):
    if isinstance(x, str):
        yield x
    elif isinstance(x, dict):
        for k, v in x.items():
            yield from _json_strings(v)
    elif isinstance(x, list):
        for v in x:
            yield from _json_strings(v)


def _version(s) -> str | None:
    m = re.match(r"\s*v?(\d+(?:\.\d+)*)", str(s or ""))
    return m.group(1) if m else None


DELIVERY_TOPS = {"provenance", "evidence", "tests", "solution", "environment", "cheat", "_provenance"}


def container_path_tails(tokens):
    """The relative tails of every image/container path (/app, /pristine, /tests, ...) cited among TOKENS. A
    relative cite equal to one of these names a file of the container image, not the delivery -- the document
    gives its absolute container path (/app/...) alongside -- so it is not a missing delivery file."""
    tails = set()
    for t in tokens:
        t = t.strip().rstrip("/")
        if any(t == r or t.startswith(r + "/") for r in WORKTREE_ROOTS):
            parts = t.lstrip("/").split("/")
            for i in range(1, len(parts)):
                tails.add("/".join(parts[i:]))
    return tails


COMPRESSED = {".gz": r"gunzip|gzip\s+-\w*d|zcat", ".xz": r"unxz|xz\s+-\w*d|xzcat", ".bz2": r"bunzip2|bzip2\s+-\w*d|bzcat",
              ".zst": r"unzstd|zstd\s+-\w*d|zstdcat"}


def decompressed_in_image(tree: Tree, rel: str) -> bool:
    """REL is not shipped as is but as REL.gz (or .xz, .bz2, .zst), and a Dockerfile of the delivery decompresses that
    file at build (mysql-session-parity: tests/expected.json.gz, gunzipped into /tests/expected.json by
    tests/Dockerfile), so a cite of REL names a file the image holds."""
    for ext, tool in COMPRESSED.items():
        if not tree.exists(rel + ext):
            continue
        name = re.escape(PurePosixPath(rel).name + ext)
        for p in tree.paths:
            if PurePosixPath(p).name == "Dockerfile" or PurePosixPath(p).name.startswith("Dockerfile."):
                if re.search(r"(?:%s)\b[^\n]*%s" % (tool, name), tree.text(p) or ""):
                    return True
    return False


def _strict_missing(tree: Tree, tokens, bases, extra_tails=frozenset(), extra_dirs=frozenset()):
    """Cited paths that resolve against none of the bases (no basename-anywhere fallback). Bare file
    names are skipped: output names and upstream files are indistinguishable from cites. A cite the document
    also gives as an absolute container path (/app/...), and a cheat/ or _provenance/ path the packager
    relocated when the delivery was assembled, are resolved, not reported."""
    missing = []
    tails = container_path_tails(tokens) | set(extra_tails)
    for t in tokens:
        if not cite_candidate(t) or "/" not in t.rstrip("/"):
            continue
        t2 = t.lstrip("./").rstrip("/")
        if t2 in tails or str(PurePosixPath(t2).parent) in extra_dirs:
            continue    # a container-image path the document (or the instruction: its folders too) cites absolutely
        if any(tree.exists((b + "/" + t2) if b not in ("", ".") else t2) for b in bases):
            continue
        if any(tree.exists(rel) for rel in relocated_in_delivery(t2)):
            continue    # cheat/ -> evidence/cheat/, _provenance/ -> provenance/, at delivery-assembly time
        if any(decompressed_in_image(tree, (b + "/" + t2) if b not in ("", ".") else t2) for b in bases):
            continue    # shipped compressed (tests/expected.json.gz) and decompressed by a Dockerfile at build
        missing.append(t)
    return list(dict.fromkeys(missing))


def dockerfile_findings(tree: Tree, rel: str):
    """Digest pins on FROM, lockfiles behind npm/pip installs of a copied manifest, and D1: a RUN step whose
    build or install is masked by `|| true` (masked_build_steps). gate_content runs it on every Dockerfile of
    the task (environment/ and tests/), packaging on every Dockerfile of the delivery."""
    fs = []
    txt = tree.text(rel) or ""
    ctx = str(PurePosixPath(rel).parent)
    copied, runs, dests = [], [], {}
    for n, ln in logical_lines(txt):
        s = ln.strip()
        if content_rules.FROM_RE.match(s):
            continue
        m = re.match(r"(?i)(?:COPY|ADD)\s+((?:--\S+\s+)*)(.+)$", s)
        if m and "--from" not in m.group(1):
            parts = [x.strip('"[],') for x in m.group(2).split()]
            copied += [(n, x) for x in parts[:-1]]
            for x in parts[:-1]:
                dests[PurePosixPath(parts[-1]).name if not parts[-1].endswith("/") else PurePosixPath(x).name] = x
            continue
        if re.match(r"(?i)RUN\s", s):
            runs.append((n, s))
    unpinned = content_rules.unpinned_from(txt)   # one rule with tb4-lint.py: a tag is not a pin
    if unpinned:
        ln0, msg = _collapse(unpinned, "FROM without a digest pin (@sha256:...) ({where}): the base image can "
                                       "change under the task")
        fs.append(finding(rel, ln0, msg + "; " + content_rules.from_fix(unpinned[0][1])))
    names = {PurePosixPath(p).name for _, p in copied}
    ctx_has = lambda nm: any(tree.exists((ctx + "/" if ctx not in ("", ".") else "") + str(PurePosixPath(p).parent / nm))
                             for _, p in copied)
    for n, s in runs:
        if re.search(r"\bnpm\s+(?:install|i|add)\b[^&;|]*\s[@\w/.-]+@\d", s) and not names & LOCKFILES:
            fs.append(finding(rel, n, "npm install of pinned top-level packages with no lockfile: their transitive "
                                      "dependencies float between builds"))
        if re.search(r"\bnpm\s+(install|i|add)\b", s) and any(fnmatch.fnmatch("package.json", nm) for nm in names):
            if not (names & LOCKFILES or any(fnmatch.fnmatch("package-lock.json", nm) for nm in names)):
                fs.append(finding(rel, n, "npm install from a copied package.json with no lockfile copied (and not "
                                          "npm ci): transitive dependencies float between builds"))
        for req in re.findall(r"\bpip3?\s+install\b[^&;|]*?\s-r\s+(\S+)", s):
            rn = PurePosixPath(req).name
            src = dests.get(rn) or next((p for _, p in copied if PurePosixPath(p).name == rn), None)
            if src is None:
                continue
            body = tree.text((ctx + "/" if ctx not in ("", ".") else "") + src) or ""
            loose = [l.strip() for l in body.splitlines() if l.strip() and not l.strip().startswith(("#", "-"))
                     and "==" not in l and " @ " not in l]
            if loose and not names & LOCKFILES:
                fs.append(finding(rel, n, f"pip install -r {rn} with unpinned requirements ({', '.join(loose[:4])}) "
                                          "and no lockfile"))
        if re.search(r"\bpip3?\s+install\b[^&;|]*\s(\.|-e\s+\.)(\s|$)", s) and "pyproject.toml" in names \
                and not names & LOCKFILES:
            fs.append(finding(rel, n, "pip install . from a copied pyproject.toml with no lockfile: dependencies "
                                      "float between builds"))
    masked = [(n, h) for n, s in runs for h in masked_build_steps(s)]
    if masked:
        ln0, msg = _collapse(masked, "D1: a RUN step masks a failed build or install ({where}): a failed download, "
                                     "compile or install still produces a layer and the image ships broken; let the "
                                     "step fail (drop `|| true`), or guard only a command that may fail for a stated "
                                     "reason")
        fs.append(finding(rel, ln0, msg))
    return fs


DF_MASK = re.compile(r"\|\|\s*(?:true|:|/bin/true|exit\s+0)(?=\s*(?:$|[;&|)}]))|;\s*(?:true|:)\s*$")
DF_BUILD = re.compile(
    r"\bgo\s+(?:mod|build|vet|install|get|generate|test|run)\b|(?<![\w./-])make(?![\w.-])|\bcmake\b|\bninja\b|"
    r"\bcargo\s+(?:build|fetch|install|test|check|vendor)\b|\bpip3?\s+install\b|\bpython[\d.]*\s+-m\s+pip\s+install\b|"
    r"\buv\s+(?:pip\s+install|sync)\b|\bpoetry\s+install\b|\b(?:npm|pnpm|yarn)\s+(?:install|i|ci|add|run|build)\b|"
    r"\bapt-get\s+(?:-\S+\s+)*(?:install|build-dep|upgrade|dist-upgrade)\b|\bapt\s+install\b|\bapk\s+add\b|"
    r"\b(?:yum|dnf|microdnf)\s+install\b|(?<![\w./-])(?:gcc|g\+\+|clang|clang\+\+|cc|rustc|javac|tsc)\s|\bmvn\b|"
    r"\bgradlew?\b|\./configure\b|\bdotnet\s+(?:build|restore|publish)\b|\bbundle\s+install\b|\bgem\s+install\b|"
    r"\bcomposer\s+install\b|\bsetup\.py\b")


def masked_build_steps(run_line: str) -> list:
    """D1 (customer F04): the build or install commands a RUN line's `|| true`, `|| :`, `|| exit 0` or a
    trailing `; true` turns into a success. The masked part of `a && b || true` is the whole and-or list
    back to the previous `;` or the opening of the ( ) / { } group the mask sits in, so `(pkill x || true)`
    masks only pkill and `rm -rf d || true` masks no build step. A mask inside quotes is not one."""
    s = re.sub(r"(?i)^\s*RUN\s+(?:--\S+\s+)*", "", run_line)
    out = []
    for m in DF_MASK.finditer(s):
        if _quote_open(s[:m.start()]):
            continue
        i, oror = m.start(), s[m.start()] == "|"
        start, depth, j = 0, 0, i - 1
        while j >= 0:
            ch = s[j]
            if ch in ")}":
                depth += 1
            elif ch in "({":
                if depth == 0:
                    start = j + 1
                    break
                depth -= 1
            elif ch == ";" and depth == 0 and oror:
                start = j + 1
                break
            j -= 1
        head = s[start:i]
        if re.match(r"\s*(?:command\s+-v|which|type|test|\[)\s", head):
            continue
        b = DF_BUILD.search(head)
        if b:
            out.append(f"{b.group(0).strip()} ... {m.group(0).strip()}")
    return out


BINARY_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".gz", ".tar", ".whl", ".so", ".bin", ".min",
                   ".npy", ".parquet", ".sqlite", ".db")


def is_attempt_evidence(p: str) -> bool:
    """A file of a model attempt's evidence (evidence/attempts/<model>/<attempt>/...: its agent.patch, verifier
    output): what the agent wrote or read in the environment's repository, not the author's own text."""
    parts = PurePosixPath(p).parts
    return len(parts) > 2 and parts[0] == "evidence" and parts[1] == "attempts"


def upstream_patch_emails(tree: Tree, paths) -> set:
    """Addresses the environment's repository already held before any agent edit: those on a context line, a
    removed line or a hunk header of a unified diff in attempt evidence (agent.patch). A diff only shows such a
    line when the file it was taken from carries it, so the address is the upstream project's (a license header
    of the library the environment clones: transit-time-flow), not one the author or the model introduced. The
    same address on an added line of another attempt's patch (the model copying that header into a new file) is
    then the same public address; anywhere outside attempt evidence it is still reported."""
    out = set()
    for p in paths:
        if not is_attempt_evidence(p) or PurePosixPath(p).suffix.lower() not in (".patch", ".diff"):
            continue
        txt = tree.text(p)
        if not txt or "@" not in txt:
            continue
        for ln in txt.splitlines():
            if ln.startswith(("@@", " ")) or (ln.startswith("-") and not ln.startswith("---")):
                out |= {e.lower() for e in EMAIL_RE.findall(ln)}
    return out


def email_findings(tree: Tree, paths, toml_rel, main_toml):
    """(findings, warnings): personal addresses, the task.toml authors' own addresses and the operator's own
    addresses (git user.email / $TB4_ATTEMPTER_EMAIL), in any file of `paths` but the task's task.toml and agent
    transcripts; one finding per address. Own addresses fail even on a reserved domain; a consumer-domain
    address fails masked with the RFC 2606 fix; reserved domains (example.com/.org/.net, *.test, *.example,
    *.invalid, localhost) are allowed. In attempt evidence, an address the environment's repository already
    held (upstream_patch_emails) is the upstream project's and is not reported. Packaging passes the whole
    delivery, the content gate the task's files: the same rule, the same messages."""
    fs, warns = [], []
    author_mails = set()
    if toml_rel is not None and tree.exists(toml_rel):
        tt = tree.text(toml_rel) or ""
        author_mails = {e.lower() for e in EMAIL_RE.findall(tt)}
        for e in sorted(author_mails):
            if PERSONAL_MAIL.search(e):
                warns.append(finding(toml_rel, line_of(tt, e), "task.toml author email is at a personal mail domain"))
    own = own_emails()
    upstream = upstream_patch_emails(tree, paths)
    by_addr = {}
    for p in paths:
        if p == main_toml or is_transcript(p):
            continue
        if PurePosixPath(p).suffix.lower() in BINARY_SUFFIXES:
            continue
        txt = tree.text(p)
        if not txt or "@" not in txt:
            continue
        for n, ln in enumerate(txt.splitlines(), 1):
            for e in EMAIL_RE.findall(ln):
                el = e.lower()
                if el in upstream and is_attempt_evidence(p) and el not in author_mails and el not in own:
                    continue
                if el in author_mails or el in own or (PERSONAL_MAIL.search(el) and not RESERVED_MAIL.search(el)):
                    by_addr.setdefault(el, [])
                    if not by_addr[el] or by_addr[el][-1][0] != p:
                        by_addr[el].append((p, n))
    for el, where in by_addr.items():
        more = f" (the same address is also in {len(where) - 1} other file(s): " \
               f"{', '.join(w for w, _ in where[1:4])}{', ...' if len(where) > 4 else ''})" if len(where) > 1 else ""
        if el in author_mails or el in own:
            why = (f"{mask_email(el)} is {'the task author' + chr(39) + 's' if el in author_mails else 'your'} own address "
                   f"({'task.toml authors' if el in author_mails else 'git user.email / TB4_ATTEMPTER_EMAIL'}): remove it "
                   "from this file (review records ship it hashed; nowhere else may it appear)")
        else:
            local = el.partition("@")[0]
            why = (f"{mask_email(el)} is at a consumer mail domain ({el.partition('@')[2]}): if it is synthetic data, "
                   f"use a reserved RFC 2606 domain instead, e.g. {local[:1]}***@example.com (example.com/.org/.net, "
                   "*.test, *.example, *.invalid and localhost are allowed); if it is a real person's address, remove it")
        fs.append(finding(where[0][0], where[0][1], "personal email address outside task.toml authors: " + why + more))
    return fs, warns


PACKAGE_TIME_TOPS = ("evidence", "provenance", "_provenance")


# finalize's own wording in DELIVERY.md for review records not yet recorded ("... are absent: ...")
ABSENT_LINE = re.compile(r"\b(?:is|are)\s+absent\b", re.I)

OUTPUT_CITE = re.compile(r"/app/output/([\w.-]+(?:/[\w.-]+)*)")
ABS_IN_TEXT = re.compile(r"(?<![\w.$}/:-])(/[A-Za-z_][\w.-]*(?:/[\w.-]+)+)")
SHELL_ABS_VAR = re.compile(r"(?m)^\s*(?:export\s+|readonly\s+|local\s+)?([A-Za-z_]\w*)=[\"']?(/[\w./-]*[\w.-])[\"']?\s*(?:[;#].*)?$")
SHELL_VAR_PATH = re.compile(r"\$\{?([A-Za-z_]\w*)\}?((?:/[\w.-]+)+)")
# a line of solution or test code that writes a file: open(..., "w"), write_text/write_bytes, json.dump, a redirect
WRITE_CUE = re.compile(r"\bopen\(.*,\s*(?:mode\s*=\s*)?[\"'][wxa]b?\+?[\"']|\.write_(?:text|bytes)\(|\bjson\.dump\(|"
                       r"\.to_(?:csv|json)\(|(?<![<>&=-])>>?\s*[\"']?[\w$./{}-]")
QUOTED_FILE = re.compile(r"[\"']([\w.-]+\.[A-Za-z0-9]{1,8})[\"']")
# the files a solution patch edits (diff --git a/X b/X, --- a/X, +++ b/X): files of the repository in the image
PATCHED_FILE = re.compile(r"^(?:diff --git a/(\S+) b/\S+|(?:---|\+\+\+) [ab]/(\S+))", re.M)


def shell_paths(text: str) -> set:
    """Absolute paths a shell script names through a variable set to one: with LOG=/logs/verifier,
    "$LOG/write-probe.txt" is /logs/verifier/write-probe.txt."""
    roots = {}
    for m in SHELL_ABS_VAR.finditer(text):
        roots.setdefault(m.group(1), set()).add(m.group(2).rstrip("/"))
    return {r + m.group(2) for m in SHELL_VAR_PATH.finditer(text) for r in roots.get(m.group(1), ())}


def made_at_run_time(tree: Tree, task_rel: str):
    """(paths, names, stems) a document may cite although no file of the delivery holds them, because the task
    declares or makes them. Declared outputs: the /app/output/<path> of instruction.md and tests/grading.json's
    deliverables (rebate_claims.csv). Made at build or run time: every absolute path a RUN or WORKDIR step of a
    task Dockerfile names, except one it removes (the step reads or creates it, so the image holds it:
    /tests/cases), every path tests/*.sh names, its variables expanded ($LOG/write-probe.txt), and the file names
    solution/ or tests/ code writes (open(..., "w"), write_text, a redirect: facilities.json), and the files a
    solution/*.patch edits, which the repository in the image holds (geometry.py). paths holds each
    absolute path without its leading slash and each output relative to /app/output, names their basenames, stems
    the declared outputs without a suffix (a package directory, so `knotcalc.py` names the form of `knotcalc`
    the contract forbids, not a missing file)."""
    tp = (task_rel + "/") if task_rel else ""
    absp, outs, names = set(), set(), set()
    if tree.exists(tp + "instruction.md"):
        outs |= {o.rstrip(".") for o in OUTPUT_CITE.findall(tree.text(tp + "instruction.md") or "")}
    if tree.exists(tp + "tests/grading.json"):
        try:
            g = json.loads(tree.text(tp + "tests/grading.json") or "{}")
        except ValueError:
            g = {}
        dl = g.get("deliverables") if isinstance(g, dict) else None
        outs |= {x.strip().lstrip("./").rstrip("/") for x in dl if isinstance(x, str) and x.strip()} \
            if isinstance(dl, list) else set()
    for p in tree.paths:
        if not p.startswith(tp):
            continue
        rel, nm = p[len(tp):], PurePosixPath(p).name
        if nm == "Dockerfile" or nm.startswith("Dockerfile.") or nm.endswith(".Dockerfile"):
            for _, ln in logical_lines(tree.text(p) or ""):
                if re.match(r"\s*(?:RUN|WORKDIR)\s", ln, re.I):
                    for seg in re.split(r"&&|\|\||;", ln):
                        if not re.match(r"\s*(?:RUN\s+)?rm\s", seg, re.I):
                            absp |= set(ABS_IN_TEXT.findall(seg))
            continue
        if rel.startswith("tests/") and nm.endswith(".sh"):
            txt = tree.text(p) or ""
            absp |= shell_paths(txt) | set(ABS_IN_TEXT.findall(txt))
        if rel.startswith("solution/") and PurePosixPath(nm).suffix in (".patch", ".diff"):
            # fluids-without-scipy: README cites geometry.py, drag.py, ... that solution/solve.patch edits in /app/fluids
            names |= {PurePosixPath(a or b).name for a, b in PATCHED_FILE.findall(tree.text(p) or "")}
        if rel.startswith(("solution/", "tests/")) and PurePosixPath(nm).suffix in CODE_SUFFIX:
            names |= {f for ln in (tree.text(p) or "").splitlines() if WRITE_CUE.search(ln)
                      for f in QUOTED_FILE.findall(ln)}
    paths = {a.strip("/") for a in absp} | outs
    names |= {PurePosixPath(x).name for x in paths}
    stems = {PurePosixPath(o).name for o in outs if "." not in PurePosixPath(o).name}
    return paths, names, stems


def doc_cite_findings(tree: Tree, docs, task_rel, skip_tops=(), skip_bare=False):
    """Paths DELIVERY.md and README.md cite that the tree does not contain, one finding per cited token:
    resolved against the tree root, the document's folder and the task, then by basename, then as a suffix of
    any path. `skip_tops` leaves out cites into folders that only exist once the delivery is assembled
    (evidence/, provenance/) when the tree is a bare task, and `skip_bare` leaves out bare file names
    there: packaging accepts a bare name found anywhere in the delivery (evidence/ included), so on a bare task
    an output or runtime file name (error.txt) cannot be told from a cite; a cite with a folder is checked. A
    cite of what the task declares as output or makes at build or run time (made_at_run_time) is not missing."""
    fs, made = [], None
    tp = (task_rel + "/") if task_rel else ""
    for doc in docs:
        txt = strip_fences(tree.text(doc) or "")
        base = str(PurePosixPath(doc).parent)
        seen = set()
        # a cite the same document also gives by its absolute container path (/app/...) names a file of the image,
        # not of the delivery: the rule _strict_missing applies (gridsheet README: __utils.ts and /app/.../__utils.ts)
        tails = container_path_tails([t for ln in txt.splitlines() for k, t in readme_tokens(ln) if k == "path"])
        for n, ln in enumerate(txt.splitlines(), 1):
            # A line that says the paths it names are absent (finalize's own "evidence/rubric/ and evidence/gates/
            # are absent: ... review_records.pending") states a fact about the delivery; it cites nothing.
            absent = PurePosixPath(doc).name == "DELIVERY.md" and bool(ABSENT_LINE.search(ln))
            if PurePosixPath(doc).name == "DELIVERY.md":     # finalize's tables name tests by node id (suite::path::test),
                ln = re.sub(r"\S*::\S*", " ", ln)           # often of the repository in the image: not file cites
            for kind, t in readme_tokens(ln):
                if kind != "path" or t in seen or not cite_candidate(t):
                    continue
                if absent:
                    continue
                seen.add(t)
                t2 = t.lstrip("./").rstrip("/")
                if skip_tops and t2.split("/")[0] in skip_tops:
                    continue
                if skip_bare and "/" not in t2:
                    continue
                if t2 in CONVENTION_NAMES:
                    continue
                if t2 in tails:
                    continue
                cands = [t2, (base + "/" + t2) if base not in (".", "") else t2]
                if task_rel:
                    cands.append(tp + t2)
                if any(tree.exists(c) for c in cands):
                    continue
                if "/" not in t2 and any(PurePosixPath(p).name == t2 for p in tree.paths):
                    continue
                if any(p.endswith("/" + t2) or ("/" + t2 + "/") in ("/" + p) for p in tree.paths):
                    continue
                if made is None:
                    made = made_at_run_time(tree, task_rel) if task_rel is not None else (set(), set(), set())
                paths, names, stems = made
                if t2 in paths or ("/" not in t2 and (t2 in names or ("." in t2 and PurePosixPath(t2).stem in stems))):
                    continue    # an output the task declares, or a path its image, verifier or solution makes
                fs.append(finding(doc, n, f"cites {t!r}, which the delivery does not contain: correct the path, "
                                          f"ship the file, or, for a file of the repository in the image, cite "
                                          f"its absolute container path (/app/...)"))
    return fs


def check_delivery(tree: Tree):
    """Findings for one delivery. Returns (task_rel or None, findings, warnings)."""
    fs, warns = [], []
    tomls = [p for p in tree.paths if PurePosixPath(p).name == "task.toml"]
    canon, others = task_descriptors(tree.paths)
    main = [(d + "/task.toml") if d else "task.toml" for d in canon]
    task_rel = str(PurePosixPath(main[0]).parent) if len(main) == 1 else None
    if task_rel == ".":
        task_rel = ""
    tp = (task_rel + "/") if task_rel else ""
    in_task = lambda p: task_rel is not None and (task_rel == "" or p.startswith(tp))
    if not main:
        fs.append(finding(".", 0, "no canonical task directory (task.toml next to instruction.md, outside provenance/, "
                                  "history, superseded and previous-version folders) anywhere in the delivery"))
    elif len(main) > 1:
        fs.append(finding(".", 0, f"{len(main)} task directories in one delivery: {', '.join(main)}"))
    for t, why in others:   # X1: every descriptor outside the one task root is reported, at any depth
        fs.append(finding(t, 0, f"non-canonical task descriptor {t} ({why}): a package ships exactly one task.toml"))
    # history and draft trees: any extra task.toml, history-named folders, instruction drafts
    extra = [t for t in tomls if not (main and t == main[0])]
    hist = sorted(d for d in tree.dirs if d not in (".", "") and HISTORY_SEG.match(PurePosixPath(d).name)
                  and not (task_rel and (d == task_rel or d.startswith(tp))))
    hist = [d for d in hist if not any(d.startswith(h + "/") for h in hist)]
    under = lambda p: any(p.startswith(h + "/") for h in hist)
    drafts = [p for p in tree.paths if re.match(r"instruction[\w.-]*\.md$", PurePosixPath(p).name) and not in_task(p)]
    items = hist + [t for t in extra if not under(t)] + [p for p in drafts if not under(p) and p not in extra]
    if items:
        why = (f"{len(extra)} extra task.toml, a second task.toml: " if extra else "") + \
            "history or draft trees are refused; ship only the task and the evidence of this version"
        fs.append(finding(items[0], 0, f"history or draft material shipped ({len(items)}): {', '.join(items[:6])}"
                          + (f", +{len(items) - 6} more" if len(items) > 6 else "") + f" ({why})"))
    # attempts inventory
    folders = {}
    for p in tree.paths:
        m = re.match(r"^(evidence/(?:.*/)?[^/]+)/attempt-(\d+)/", p)
        if m and not any(HISTORY_SEG.match(s) for s in PurePosixPath(m.group(1)).parts):
            folders.setdefault(m.group(1), set()).add(int(m.group(2)))
    counts = {k[len("evidence/"):]: len(v) for k, v in folders.items()}
    total = sum(counts.values())
    manifest = None
    if tree.exists("MANIFEST.json"):
        try:
            manifest = json.loads(tree.text("MANIFEST.json") or "")
        except Exception as e:
            fs.append(finding("MANIFEST.json", 0, f"MANIFEST.json does not parse: {e}"))
    ks, voids = set(), {0}
    if isinstance(manifest, dict):
        pak = manifest.get("pass_at_k")
        if isinstance(pak, dict):
            for v in pak.values():
                if isinstance(v, dict) and isinstance(v.get("k"), int):
                    ks.add(v["k"])
                    if isinstance(v.get("voids"), int):
                        voids.add(v["voids"])
        if isinstance(manifest.get("k"), int):
            ks.add(manifest["k"])
    mz = re.search(r"-pass(\d+)\b", tree.src.name)
    if mz and int(mz.group(1)) > 1:
        ks.add(int(mz.group(1)))
    delivery_md = "DELIVERY.md" if tree.exists("DELIVERY.md") else None
    dtxt = strip_fences(tree.text(delivery_md) or "") if delivery_md else ""
    if not ks and dtxt:
        ks |= {int(k) for k in re.findall(r"(?i)\bpass@(\d+)\b", dtxt) if int(k) > 1}
    if ks:
        for folder, nums in sorted(folders.items()):
            n = len(nums)
            if n > 1 and not any(n == k + v for k in ks for v in voids):
                fs.append(finding(folder + "/", 0, f"{n} attempt folders, but the delivery declares pass@"
                                  f"{'/'.join(str(k) for k in sorted(ks))}: a pass@k set holds exactly k attempts"))
    if isinstance(manifest, dict) and isinstance(manifest.get("attempts"), dict):
        for model, v in manifest["attempts"].items():
            n = v.get("n") if isinstance(v, dict) else None
            key = f"evidence/attempts/{model}"
            if isinstance(n, int) and key in folders and len(folders[key]) != n:
                fs.append(finding("MANIFEST.json", line_of(tree.text("MANIFEST.json") or "", f'"{model}"'),
                                  f"attempts.{model}.n = {n}, but {key}/ holds {len(folders[key])} attempt folders"))
    # MANIFEST version == task.toml version
    if isinstance(manifest, dict) and task_rel is not None:
        mv = _version(manifest.get("version") or manifest.get("task_version"))
        try:
            td = tomllib.loads(tree.text(tp + "task.toml") or "")
        except Exception:
            td = {}
        tv = _version((td.get("task") or {}).get("version") or td.get("version"))
        if mv and tv and mv != tv:
            fs.append(finding("MANIFEST.json", 0, f"MANIFEST.json version {mv} differs from task.toml version {tv}"))
    # a DELIVERY that describes another version: digests or versions on the lines about what ships
    if delivery_md and task_rel is not None:
        cur_digest = str(manifest.get("task_digest", "")) if isinstance(manifest, dict) else ""
        cur_hex = cur_digest.split(":")[-1].lower()
        try:
            tdv = _version((tomllib.loads(tree.text(tp + "task.toml") or "").get("task") or {}).get("version"))
        except Exception:
            tdv = None
        sec_d = sections(dtxt)
        stale = []
        for n, ln in enumerate(dtxt.splitlines(), 1):
            if HISTORY_HEAD.search(sec_d.get(n, "")) or not SHIP_CUE.search(ln) or \
                    re.search(r"\b(earlier|previous|superseded|old|v\d+ was|former)\b", ln, re.I):
                continue
            for m in re.finditer(r"sha256:([0-9a-f]{8,64})", ln):
                h = m.group(1).lower()
                if cur_hex and not (cur_hex.startswith(h) or h.startswith(cur_hex)):
                    stale.append((n, f"digest {h[:12]} vs MANIFEST {cur_hex[:12]}"))
            for m in re.finditer(r"\b[Vv]ersion\s+(\d+\.\d+\.\d+)\b|\bv(\d+\.\d+\.\d+)\b", ln):
                v = m.group(1) or m.group(2)
                if tdv and v != tdv:
                    stale.append((n, f"version {v} vs task.toml {tdv}"))
        if stale:
            ln0, msg = _collapse(stale, "DELIVERY.md describes another version of the task on the lines about what "
                                        "ships ({where}): regenerate it from the records of this version")
            fs.append(finding(delivery_md, ln0, msg))
    # DELIVERY count claims, only where the text talks about what ships
    if delivery_md:
        sec = sections(dtxt)
        for n, ln in enumerate(dtxt.splitlines(), 1):
            if not SHIP_CUE.search(ln) or HISTORY_HEAD.search(sec.get(n, "")):
                continue
            for m in COUNT_CLAIM.finditer(ln):
                raw = m.group(1) or m.group(2) or m.group(3)
                val = NUMWORD.get(raw.lower(), None) if not raw.isdigit() else int(raw)
                if val is None:
                    continue
                if re.search(r"\b(control|oracle|nop|no-op|cheat)\b", ln[max(0, m.start() - 30):m.end() + 10], re.I) \
                        or re.search(r"\breward\s*$", ln[:m.start()], re.I):
                    continue
                if val != total and val not in counts.values():
                    fs.append(finding(delivery_md, n, f"DELIVERY.md states {m.group(0).strip()!r} but the delivery "
                                      f"ships {total} attempt folder(s)"
                                      + (f" ({', '.join(f'{k}: {v}' for k, v in sorted(counts.items()))})" if counts else "")))
    # emails: authored files only, one finding per address
    main_toml = main[0] if main else None
    mfs, mwarns = email_findings(tree, tree.paths, tp + "task.toml" if task_rel is not None else None, main_toml)
    fs += mfs
    warns += mwarns
    # cited paths: DELIVERY and README (existing resolution), one finding per cited token
    docs = [delivery_md] if delivery_md else []
    if task_rel is not None and tree.exists(tp + "README.md"):
        docs.append(tp + "README.md")
    fs += doc_cite_findings(tree, docs, task_rel)
    # cited paths in provenance and test docstrings: strict, relative to the delivery root, the document's
    # folder or the task; no basename-anywhere fallback
    strict_docs = []
    for p in tree.paths:
        if in_task(p) and not p.startswith(tp + "tests/"):
            continue
        name = PurePosixPath(p).name
        if name == "PROVENANCE.json":
            try:
                toks = [t for s in _json_strings(json.loads(tree.text(p) or "")) for k, t in readme_tokens(s)
                        if k == "path"]
            except Exception:
                toks = []
            strict_docs.append((p, toks))
        elif p.startswith("provenance/") and name.endswith(".md") and not any(
                HISTORY_SEG.match(s) for s in PurePosixPath(p).parts[:-1]):
            toks = [t for ln in strip_fences(tree.text(p) or "").splitlines() for k, t in readme_tokens(ln) if k == "path"]
            strict_docs.append((p, toks))
        elif in_task(p) and p.startswith(tp + "tests/") and name.endswith(".py"):
            try:
                tree_py = ast.parse(tree.text(p) or "")
            except SyntaxError:
                continue
            ds = [ast.get_docstring(nd) or "" for nd in ast.walk(tree_py)
                  if isinstance(nd, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
            # a docstring names upstream repository files too; only delivery-rooted cites are checked
            toks = [t for d in ds for ln in d.splitlines() for k, t in readme_tokens(ln) if k == "path"
                    and t.lstrip("./").split("/")[0] in DELIVERY_TOPS]
            strict_docs.append((p, toks))
    # the instruction's container paths (/app/<repo>/tests/...): their relative forms name files of the image,
    # which a test docstring may cite without repeating the absolute path
    itxt = tree.text(tp + "instruction.md") if task_rel is not None and tree.exists(tp + "instruction.md") else ""
    itails = container_path_tails([t for ln in (itxt or "").splitlines() for k, t in readme_tokens(ln) if k == "path"])
    idirs = {str(PurePosixPath(t).parent) for t in itails if "/" in t}
    for p, toks in strict_docs:
        bases = ["", str(PurePosixPath(p).parent), task_rel or "", "provenance"]
        if in_task(p):
            bases.append(tp + "tests")
        miss = _strict_missing(tree, toks, bases, itails, idirs)
        if miss:
            fs.append(finding(p, 0, f"cites {len(miss)} path(s) the delivery does not contain: "
                              f"{', '.join(miss[:6])}" + (f", +{len(miss) - 6} more" if len(miss) > 6 else "")))
    # delivery leftovers: file-count claims, the evidence set, cheat/ inside the task
    if task_rel is not None:
        tfiles = [p for p in tree.paths if in_task(p)]
        hashed = [p for p in tfiles if p[len(tp):] in ("task.toml", "instruction.md", "README.md")
                  or p[len(tp):].split("/")[0] in ("environment", "tests", "solution")]
        if dtxt:
            for n, ln in enumerate(dtxt.splitlines(), 1):
                for m in re.finditer(r"(?<![\w.-])(\d+|" + "|".join(NUMWORD) + r")\s+files\b", ln, re.I):
                    raw = m.group(1).lower()
                    val = int(raw) if raw.isdigit() else NUMWORD[raw]
                    near = ln[max(0, m.start() - 90):m.start()]
                    if not (re.search(r"\btask (?:package|folder|directory|dir)\b", near, re.I)
                            or (task_rel and task_rel + "/" in near)):
                        continue
                    if val not in (len(tfiles), len(hashed)):
                        fs.append(finding(delivery_md, n, f"DELIVERY.md says {m.group(0)!r} for the task, but it holds "
                                          f"{len(tfiles)} files ({len(hashed)} hashed by Harbor)"))
        cheats = sorted({p[len(tp):].split("/")[0] for p in tfiles if p[len(tp):].startswith("cheat/")})
        if cheats:
            fs.append(finding(tp + "cheat/", 0, "cheat/ ships inside the task folder: the agent image or a reviewer "
                              "reading the task sees the attack; move it to evidence/ at package time"))
        need = {"oracle": r"^evidence/(?:[^/]+/)?oracle", "nop": r"^evidence/(?:[^/]+/)?n(?:o-?)?op",
                "tamper or cheat": r"^evidence/(?:[^/]+/)?(?:cheat|tamper|controls/)"}
        miss = [k for k, rx in need.items() if not any(re.match(rx, d) for d in tree.dirs)]
        if miss:
            fs.append(finding("evidence/", 0, f"the delivery ships no {', '.join(miss)} receipts under evidence/: the "
                              f"controls the README and DELIVERY rely on cannot be checked"))
    # Dockerfiles: digest pins and lockfiles
    if task_rel is not None:
        for p in tree.paths:
            if in_task(p) and (PurePosixPath(p).name == "Dockerfile" or p.endswith(".Dockerfile")):
                fs += dockerfile_findings(tree, p)
    return task_rel, fs, warns


def gate_packaging(src: Path, task_override: Path | None, gates_dir: str | None):
    """Returns a list of (task_path_for_record, GateResult, tmpdir_holder). A folder of zips gives one record
    per zip (under <gates-dir>/<task>/ when --gates-dir is set) plus a duplicate-task-id check."""
    results = []
    if src.is_dir() and not (src / "DELIVERY.md").is_file() and not (src / "task.toml").is_file() and list(src.glob("*.zip")):
        zips = sorted(src.glob("*.zip"))
        by_id = {}
        for z in zips:
            by_id.setdefault(task_id_of_zip(z), []).append(z)
        for tid, zs in sorted(by_id.items()):
            extra_fs = []
            if len(zs) > 1:
                extra_fs.append(finding(".", 0, f"{len(zs)} zips for task id {tid}: {', '.join(z.name for z in zs)}"
                                        " (ship one zip per task id)"))
            for z in zs:
                for item in _package_one(z, task_override, gates_dir, per_task=True):
                    item[1].findings = extra_fs + item[1].findings
                    if extra_fs:
                        item[1].status = "FAIL" if item[1].status == "PASS" else item[1].status
                    results.append(item)
        return results
    return _package_one(src, task_override, gates_dir)


def _package_one(src: Path, task_override, gates_dir, per_task=False):
    holder = tempfile.TemporaryDirectory(prefix="pkg-gate-")
    if src.is_file():
        try:
            with zipfile.ZipFile(src) as zf:
                bad = zip_entry_problems(zf)
        except (zipfile.BadZipFile, OSError) as e:
            return [(None, GateResult("ERROR", f"{src.name}: not a readable zip: {e}"), holder)]
        if bad:
            fs = [finding(n, 0, f"unsafe zip entry {n!r}: {why}") for n, why in bad]
            res = GateResult("ERROR", f"{src.name}: {len(bad)} unsafe zip entr{'y' if len(bad) == 1 else 'ies'} "
                             f"(first: {bad[0][0]!r}, {bad[0][1]}); the zip is rejected, not extracted", fs,
                             evidence=[str(src)])
            if task_override:
                res.extra["gates_dir"] = gates_dir
                return [(Path(task_override).resolve(), res, holder)]
            return [(None, res, holder)]
    tree = Tree(src)
    task_rel, fs, warns = check_delivery(tree)
    if task_override:
        task = Path(task_override).resolve()
    elif task_rel is not None and src.is_dir():
        task = (src / task_rel).resolve() if task_rel else src.resolve()
    elif task_rel is not None:
        task = tree.extract_task(task_rel, Path(holder.name))
    else:
        return [(None, GateResult("ERROR", f"{src}: no task directory found, cannot key a record", fs, warns), holder)]
    gd = gates_dir
    if gd is not None and per_task:
        gd = str(Path(gd) / task.name)
    if gd is None and not task_override:
        gd = str(src.resolve().parent / (task.name + "-gates"))
    res = GateResult("FAIL" if fs else "PASS", f"{src.name}: {len(tree.paths)} files; {len(fs)} packaging findings",
                     fs, warns, evidence=[str(src)])
    res.extra["gates_dir"] = gd
    return [(task, res, holder)]


# ------------------------------------------------------------------ provenance allowlist (package time)

PROVENANCE_MANIFEST = "provenance-manifest.txt"


def ship_provenance(prov: Path, dest: Path):
    """Copy a task's provenance into a delivery by ALLOWLIST, never wholesale (X1): PROVENANCE.json, originality records,
    the generator code and seeds PROVENANCE.json names under "generators" and "seeds", and the files listed one
    per line in provenance-manifest.txt (relative to the provenance folder; a directory ships its files). An
    entry that is absolute, climbs out with '..', is a symlink, is or holds a task.toml, or sits under a
    history, superseded or previous-version folder is refused; a listed file that is missing is refused.
    Returns (copied relative paths, refusals, number of files left out)."""
    prov, dest = Path(prov), Path(dest)
    want, bad = {"PROVENANCE.json": "record", "NOVELTY.md": "record", "ORIGINALITY.json": "record",
                 "ORIGINALITY.md": "record", "EQUIVALENCE.json": "record"}, []
    pj = prov / "PROVENANCE.json"
    if pj.is_file():
        try:
            doc = json.loads(read(pj))
        except ValueError as e:
            doc = {}
            bad.append(f"PROVENANCE.json does not parse ({e})")
        for key in ("generators", "seeds"):
            v = doc.get(key) if isinstance(doc, dict) else None
            for item in ([v] if isinstance(v, str) else v if isinstance(v, list) else []):
                if isinstance(item, str) and item.strip():
                    want.setdefault(item.strip(), f"PROVENANCE.json {key}")
    if (prov / PROVENANCE_MANIFEST).is_file():
        want.setdefault(PROVENANCE_MANIFEST, "record")
        for ln in read(prov / PROVENANCE_MANIFEST).splitlines():
            ln = ln.split("#", 1)[0].strip()
            if ln:
                want.setdefault(ln, PROVENANCE_MANIFEST)
    copied = []
    for rel, why in want.items():
        parts = PurePosixPath(rel).parts
        src = prov / rel
        if rel.startswith(("/", "\\")) or re.match(r"^[A-Za-z]:", rel) or ".." in parts:
            bad.append(f"{rel} ({why}): absolute or '..' paths are refused")
            continue
        if any(noncanonical_reason(seg) for seg in parts):
            bad.append(f"{rel} ({why}): history, superseded or previous-version material stays internal")
            continue
        if not src.exists() and not src.is_symlink():
            if why != "record":
                bad.append(f"{rel} ({why}): listed but missing")
            continue
        files = sorted(src.rglob("*")) if src.is_dir() and not src.is_symlink() else [src]
        for f in files:
            r = f.relative_to(prov).as_posix()
            if f.is_symlink():
                bad.append(f"{r} ({why}): symlinks are refused")
            elif f.name == "task.toml":
                bad.append(f"{r} ({why}): a nested task tree is never shipped (one task.toml per package)")
            elif any(noncanonical_reason(seg) for seg in PurePosixPath(r).parts[:-1]):
                bad.append(f"{r} ({why}): history, superseded or previous-version material stays internal")
            elif f.is_file() and r not in copied:
                (dest / r).parent.mkdir(parents=True, exist_ok=True)
                (dest / r).write_bytes(f.read_bytes())
                copied.append(r)
    left = sum(1 for f in prov.rglob("*") if f.is_file() and f.relative_to(prov).as_posix() not in copied)
    return copied, bad, left


def main_ship_provenance(argv) -> int:
    if len(argv) != 2:
        print("usage: gates_static.py ship-provenance <provenance-dir> <dest-dir>", file=sys.stderr)
        return 2
    copied, bad, left = ship_provenance(Path(argv[0]), Path(argv[1]))
    print(f"provenance allowlist: {len(copied)} file(s) shipped, {left} left out")
    for r in copied:
        print(f"  shipped {r}")
    for b in bad:
        print(f"REFUSED {b}")
    return 1 if bad else 0


# ------------------------------------------------------------------ grader-hygiene

def gate_grader_hygiene(task: Path) -> GateResult:
    """The grader mechanisms behind the customer's 10/16 grader findings (grader_hygiene.py, rules B1-B16). The
    rules read only the code that reads the deliverable or emits observations. A finding in template v2 code, or a
    B1 (the JSON loader every task copied), is a mechanical FAIL: `tb4 upgrade-verifier` (template v2.1) and
    tb4judge.load_json fix it. The task's own findings FAIL on template v2.1 (it ships tests/tb4judge.py); on the v2
    template, when they are the only ones, the gate is FAIL-PENDING-DISPOSITION and a reviewer fixes the grader or
    disposes each item. A FAIL is never disposed: the author disputes a finding and a reviewer who is not an author
    settles it. B9 is advisory."""
    import grader_hygiene   # its own module: the rules and their benchmark tests live together
    r = grader_hygiene.check(task)
    # B2 runs the judge's own tolerance arithmetic on the pair it shows: reproduced locally, not only read
    fs = [finding(p, n, "%s: %s" % (rule, msg), "reproduced-local" if rule == "B2" else "reported")
          for p, n, rule, msg in r["findings"]]
    ws = [finding(p, n, "%s: %s" % (rule, msg), "conditional") for p, n, rule, msg in r["warnings"]]
    ordered = [{"path": p, "line": n, "keys": keys, "quote": quote} for p, n, keys, quote in r["ordered"]]
    return GateResult(r["status"], r["details"], fs, ws, extra={"ordered_keys": ordered} if ordered else None)


# ------------------------------------------------------------------ spec-alignment

def gate_spec_alignment(task: Path) -> GateResult:
    """What the instruction says against what the grader enforces (spec_checks.py): permissive modals, limits the
    instruction does not state, a per-call deadline that counts the harness's own work, a speed timer that leaves out
    setup, booleans judged with == outside Python, and part of the repository's tests run. A finding is
    FAIL-PENDING-DISPOSITION, evidence level reported; the advisory rules (M2, L1, L3, L4) never block."""
    import spec_checks   # its own module: the rules and their benchmark tests live together
    r = spec_checks.check(task)
    fs = [finding(p, n, "%s: %s" % (rule, msg), "reported") for p, n, rule, msg in r["findings"]]
    ws = [finding(p, n, "%s: %s" % (rule, msg), "conditional") for p, n, rule, msg in r["warnings"]]
    return GateResult(r["status"], r["details"], fs, ws)


# ------------------------------------------------------------------ CLI

GATES = {"requirements": gate_requirements, "budget": gate_budget, "readme-claims": gate_readme_claims,
         "readme-code": gate_readme_code, "structure": gate_structure, "lint": gate_lint,
         "placeholders": gate_placeholders, "content": gate_content, "grader-hygiene": gate_grader_hygiene,
         "spec-alignment": gate_spec_alignment}


def run_gate(name, task: Path) -> GateResult:
    try:
        if not task.is_dir():
            return GateResult("ERROR", f"{task} is not a directory")
        return GATES[name](task)
    except Exception as e:  # fail closed
        return GateResult("ERROR", f"{name} could not run: {type(e).__name__}: {e}")


def record(task: Path, gate: str, res: GateResult, gates_dir):
    extra = {"warnings": res.warnings, "warnings_advisory": True}   # heuristic signals: they never block
    for k, v in res.extra.items():
        if k not in ("gates_dir",):
            extra[k] = v
    return gatelib.write_gate(task, gate, res.status, res.details, res.findings, res.evidence,
                              out_dir=gates_dir, extra=extra)


def show(gate, res: GateResult, path, as_json):
    if as_json:
        print(Path(path).read_text() if path else json.dumps({"gate": gate, "status": res.status,
                                                              "details": res.details, "findings": res.findings}))
        return
    print(f"{gate:<14} {res.status:<5} {res.details}")
    for f in res.findings[:40]:
        print(f"    {f['path']}:{f['line']}  {f['message']}")
    if len(res.findings) > 40:
        print(f"    ... {len(res.findings) - 40} more in {path}")
    if path:
        print(f"    record: {path}")


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv[:1] == ["ship-provenance"]:
        return main_ship_provenance(argv[1:])
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("gate", choices=list(GATES) + ["all", "packaging"])
    ap.add_argument("target")
    ap.add_argument("--gates-dir")
    ap.add_argument("--task", help="packaging: the source task the record belongs to")
    ap.add_argument("--delivery", help="task gates: the full extracted delivery (provenance/, evidence/, DELIVERY.md)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    target = Path(a.target).resolve()
    worst = "PASS"
    rank = {"PASS": 0, "FAIL-PENDING-DISPOSITION": 1, "FAIL": 1, "ERROR": 2}
    if a.gate == "packaging":
        if not target.exists():
            print(f"packaging ERROR {target} does not exist", file=sys.stderr)
            return 2
        items = gate_packaging(target, Path(a.task) if a.task else None, a.gates_dir)
        for task, res, holder in items:
            path = None
            if task is not None:
                path = record(task, "packaging", res, res.extra.get("gates_dir") or a.gates_dir)
            show("packaging", res, path, a.json)
            holder.cleanup()
            worst = max(worst, res.status, key=rank.get)
        return rank[worst]
    DELIVERY_OVERRIDE[:] = []
    if a.delivery:
        root = resolve_delivery(Path(a.delivery))
        if root is None:
            print(f"--delivery {a.delivery}: no DELIVERY.md or MANIFEST.json there or in its single subfolder",
                  file=sys.stderr)
            return 2
        DELIVERY_OVERRIDE[:] = [root]
        full = root / target.name
        if full.is_dir() and (full / "task.toml").is_file() and full.resolve() != target:
            print(f"--delivery: gating the full task {full} (binaries included) instead of {target}", file=sys.stderr)
            target = full.resolve()
    names = TASK_GATES if a.gate == "all" else (a.gate,)
    for g in names:
        res = run_gate(g, target)
        path = record(target, g, res, a.gates_dir) if target.is_dir() else None
        show(g, res, path, a.json)
        worst = max(worst, res.status, key=rank.get)
    return rank[worst]


if __name__ == "__main__":
    sys.exit(main())
