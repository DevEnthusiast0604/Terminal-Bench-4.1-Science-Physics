#!/usr/bin/env python3
"""spec-alignment: static rules for what the instruction promises against what the grader enforces.

The report's P2 items (conclusion-v2.md 8 to 12): a permissive modal the grader makes mandatory, a limit the grader
applies that the instruction does not state, a timer that leaves out the setup the agent controls, and three of the
customer's 10/16 grader findings no other gate covers. It reads instruction.md, task.toml and tests/ (the emitter,
the judge, test.sh, grading.json and the JSON answers tests/ ships). It never runs the task.

  M1  the instruction makes a key optional ("`note` may be omitted", "an optional `note`") and the judge requires
      it: the answers hold the key and the judge compares whole objects exactly, or reads it with obj["note"].
  M2  (advisory) the instruction lets a value be written in more than one form ("may be written as `1.50` or
      `1.5`") and the answers hold only one of them, compared as a string.
  L1  a resource cap on the solution's run (RLIMIT_AS, RLIMIT_NPROC, ulimit -u/-v/-t/-n, ...) that the instruction
      does not state and that is below what task.toml gives the container.
  L2  a time cap on the solution's run shorter than the time the instruction gives it.
  L3  (advisory) a time cap on the solution's run (CASE_TIMEOUT_SEC, RUN_TIMEOUT_SEC, ...) and no time limit in the
      instruction. Most of these never fail a correct solution: the advisory says to state the limit.
  L4  (advisory) the instruction says only one file is read, and the grader rejects the whole collected output on a
      size cap or a link the instruction does not state (disk-fleet-replacement f0001).
  D1  the instruction gives each call N seconds and the case's deadline is the same N, measured around a child
      process that also starts the interpreter, imports the code and does the harness's own work (hashing,
      serializing): a call that returns in time can miss it (charge-session-settlement f0002).
  T1  the instruction promises a speed (a speedup, a latency, a throughput) and the grader's timer starts after
      setup the submission does (an object it builds, a module it imports): the setup is not timed.
  E1  the judge passes on Python equality, `got == want`, where the answers hold booleans and no strict type check
      gates the pass: 0 and 1 equal false and true, so a Go or Rust repository's wrong type is accepted
      (namespace-sleep-wake f0002). Only for a repository that is not Python: a Python repository's returned types
      are the api-types control's.
  E2  the instruction says the repository's existing tests keep passing and the grader runs only part of them (an
      explicit package list, --ignore, -k "not ...", a comment saying the end-to-end ones are not run)
      (vendir-lazy-lock f0006).

Not checked here, and why:
  - instruction cases never exercised (p1-billing-reads f0005: no-gas billing exercised only for G2). Telling which
    combinations of the instruction's rules the fixtures cover needs the rules' meaning; the requirements gate maps
    each sentence to a test, not each combination. contract-generality and the probes are the controls for it.
  - fields omitted from the observation (namespace-sleep-wake f0001: the snapshot drops status and most metadata).
    Which fields a promise protects is a reading of the instruction; grader-hygiene B9 points at lossy emitter
    idioms, and a mutation control (change an omitted field, the judge must fail) is the check that proves it.

Severity: a finding is FAIL-PENDING-DISPOSITION (a reviewer fixes the grader or the instruction, or disposes the item
with what was checked); the advisory rules are warnings and never block. Every finding is evidence level
"reported": a reading of the files, nothing was run.

Stdlib only, Python 3.11+.
"""
from __future__ import annotations

import ast
import json
import re
import tomllib
from pathlib import Path

ANSWER_SKIP = ("grading.json", "budget.json", "requirements.json")
TRAILER = re.compile(r"to complete this task|do not cheat", re.I)

# ------------------------------------------------------------------ instruction text

FENCE = re.compile(r"```.*?```", re.S)
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z`(\[])")


def sentences(instr: str) -> list[tuple[int, str]]:
    """[(line, sentence)] of instruction.md outside code fences; the task trailer is left out."""
    text = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), instr)
    out = []
    for lno, line in enumerate(text.splitlines(), 1):
        for s in SENT_SPLIT.split(line.strip()):
            if s and not TRAILER.search(s):
                out.append((lno, s))
    return out


WORDS = {"a": 1, "an": 1, "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
         "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "fifteen": 15, "twenty": 20, "thirty": 30,
         "forty-five": 45, "sixty": 60, "ninety": 90}
UNIT = {"ms": 0.001, "millisecond": 0.001, "milliseconds": 0.001, "s": 1, "sec": 1, "secs": 1, "second": 1,
        "seconds": 1, "min": 60, "mins": 60, "minute": 60, "minutes": 60, "hour": 3600, "hours": 3600}
DURATION = re.compile(r"\b(\d[\d,_]*(?:\.\d+)?|%s)[ -]?(milliseconds?|ms|seconds?|secs?|s|minutes?|mins?|min|hours?)\b"
                      % "|".join(sorted(map(re.escape, WORDS), key=len, reverse=True)), re.I)
LIMIT_CUE = re.compile(r"\b(has|have|had|within|finish(es)?|return(s)?|under|at most|limit|takes?|stops?|allowed|"
                       r"timeout|time out|no more than|deadline)\b", re.I)
RUN_CUE = re.compile(r"\b(run|runs|call|calls|called|process|program|function|case|scenario|import(ed)?|per|each|"
                     r"sync|request|query|invocation)\b", re.I)
# a duration written as an adjective of the data (a hyphenated singular unit before a noun: "a 15-minute record",
# "5-second samples"), never a time budget (sonde-qc-migration: "15-minute record" was read as 900 s)
ADJECTIVAL = re.compile(r"(?:\d[\d,_]*(?:\.\d+)?|[A-Za-z-]+)-(?:millisecond|second|sec|minute|min|hour)\s+"
                        r"(?!or\b|and\b|limit|time\s*limit|timeout|time-out|deadline|cap\b|budget|window|run\b|maximum)[a-z]",
                        re.I)
AGGREGATE = re.compile(r"\b(whole run|whole suite|for the whole|in total|all together)\b", re.I)
CALL_CUE = re.compile(r"\b(each call|per call|a call|the call|the function|function must return|must return within|"
                      r"returns? within)\b", re.I)


def _num(tok: str) -> float | None:
    t = tok.lower().replace(",", "").replace("_", "")
    if t in WORDS:
        return float(WORDS[t])
    try:
        return float(t)
    except ValueError:
        return None


def time_limits(instr: str) -> list[dict]:
    """The time limits the instruction states for a run or a call: [{line, seconds, sentence, call}]."""
    out = []
    for lno, s in sentences(instr):
        if not LIMIT_CUE.search(s) or not RUN_CUE.search(s) or AGGREGATE.search(s):
            continue
        for m in DURATION.finditer(s):
            n = _num(m.group(1))
            if n is None or (m.group(2).lower() == "s" and not m.group(1)[0].isdigit()):
                continue
            if ADJECTIVAL.match(s, m.start()):
                continue                 # "15-minute record", "5-second samples": the data's spacing, not a time limit
            out.append({"line": lno, "seconds": n * UNIT[m.group(2).lower()], "sentence": s,
                        "call": bool(CALL_CUE.search(s))})
    return out


# ------------------------------------------------------------------ the task's files

def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


def _json(p: Path):
    try:
        return json.loads(_read(p))
    except ValueError:
        return None


def answers(task: Path) -> list:
    """The JSON documents tests/ ships at its top level (the expected answers)."""
    out = []
    for p in sorted((task / "tests").glob("*.json")):
        if p.name in ANSWER_SKIP or p.stat().st_size > 5_000_000:
            continue
        d = _json(p)
        if d is not None:
            out.append(d)
    return out


def walk_json(doc):
    stack = [doc]
    while stack:
        v = stack.pop()
        yield v
        if isinstance(v, dict):
            stack.extend(v.values())
        elif isinstance(v, list):
            stack.extend(v)


def judge_paths(task: Path) -> list[Path]:
    """tests/test_outputs.py and the tests/*.py modules it imports (not the emitter)."""
    tests = task / "tests"
    out, queue = [], [tests / "test_outputs.py"]
    while queue:
        p = queue.pop(0)
        if p in out or not p.is_file():
            continue
        out.append(p)
        try:
            tree = ast.parse(_read(p))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            names = [a.name.split(".")[0] for a in node.names] if isinstance(node, ast.Import) else \
                [node.module.split(".")[0]] if isinstance(node, ast.ImportFrom) and node.module and not node.level \
                else []
            queue += [tests / (n + ".py") for n in names if n != "emit" and (tests / (n + ".py")).is_file()]
    return out


def repo_language(task: Path) -> str:
    """"none" for a task with no repository (a program or a file is graded), else python, go, rust, js or other."""
    g = _json(task / "tests" / "grading.json")
    if not isinstance(g, dict) or not g.get("repo"):
        return "none"
    env = " ".join(map(str, (g.get("env") or {}).keys()))
    emit = _read(task / "tests" / "emit.py")
    if "GO" in env or re.search(r"[\"']go[\"']\s*,|shutil\.which\([\"']go[\"']\)|\bgo (test|build)\b", emit):
        return "go"
    if "CARGO" in env or re.search(r"\bcargo\b", emit):
        return "rust"
    if re.search(r"[\"'](npm|pnpm|yarn|node|npx|jest)[\"']", emit + json.dumps(g.get("suite") or {})):
        return "js"
    if g.get("python") or "pytest" in json.dumps(g.get("suite") or {}):
        return "python"
    return "other"


def _rel(task: Path, p: Path) -> str:
    return p.relative_to(task).as_posix()


# ------------------------------------------------------------------ M1, M2: permissive modals

OPTIONAL_KEY = [
    re.compile(r"`([A-Za-z_][\w.-]*)`\s+(?:is|are)\s+optional\b", re.I),
    re.compile(r"\boptional(?:ly)?\s+(?:an?\s+|the\s+)?(?:key\s+|field\s+|member\s+)?`([A-Za-z_][\w.-]*)`", re.I),
    re.compile(r"`([A-Za-z_][\w.-]*)`\s+(?:key\s+|field\s+)?(?:may|can)\s+(?:also\s+)?be\s+(?:omitted|absent|left out|"
               r"missing|dropped|skipped)", re.I),
    re.compile(r"\b(?:may|can)\s+(?:also\s+)?(?:include|contain|carry|have|add)\s+(?:an?\s+|the\s+)?"
               r"(?:key\s+|field\s+)?`([A-Za-z_][\w.-]*)`", re.I),
    re.compile(r"`([A-Za-z_][\w.-]*)`\s+(?:need not|does not have to|do not have to)\s+(?:be\s+)?(?:present|appear|"
               r"given|included)", re.I),
]
FORMS = re.compile(r"\b(?:may|can)\s+(?:also\s+)?be\s+(?:written|given|reported|spelled|formatted|returned|printed|"
                   r"encoded|expressed|represented)\s+(?:either\s+)?as\s+((?:`[^`]+`(?:\s*,\s*|\s+or\s+|,?\s+or\s+)?)+)",
                   re.I)


def _keys_in_answers(docs) -> set:
    return {k for d in docs for v in walk_json(d) if isinstance(v, dict) for k in v}


def _strings_in_answers(docs) -> set:
    return {v for d in docs for v in walk_json(d) if isinstance(v, str)}


EXACT = re.compile(r"\bassert\s+[\w\[\]\"'.()]+\s*==\s*[\w\[\]\"'.()]+|\bassert\s+set\(|\bsorted\([^)]*\)\s*==")


def rule_modals(task, instr, docs, judge) -> tuple[list, list]:
    findings, warnings = [], []
    keys = _keys_in_answers(docs)
    jtext = "\n".join(t for _, t in judge)
    exact = bool(EXACT.search(jtext))
    for lno, s in sentences(instr):
        for rx in OPTIONAL_KEY:
            for m in rx.finditer(s):
                k = m.group(1).split(".")[-1]
                sub = re.search(r"\[\s*[\"']%s[\"']\s*\]" % re.escape(k), jtext)
                soft = re.search(r"\.get\(\s*[\"']%s[\"']|[\"']%s[\"']\s+(?:not\s+)?in\b|setdefault\(\s*[\"']%s[\"']"
                                 % ((re.escape(k),) * 3), jtext)
                if sub and not soft:
                    why = "the judge reads it as obj[%r], a KeyError when it is left out" % k
                elif k in keys and exact and not re.search(r"[\"']%s[\"']" % re.escape(k), jtext):
                    why = "the answers hold `%s` and the judge compares whole objects exactly" % k
                else:
                    continue
                findings.append(("instruction.md", lno, "M1",
                                 "the instruction makes `%s` optional (%r) but %s: a submission that leaves it out "
                                 "fails. Fix: accept the object without it, or make the key required in the "
                                 "instruction" % (k, s[:160], why)))
        m = FORMS.search(s)
        if m:
            forms = re.findall(r"`([^`]+)`", m.group(1))
            held = [f for f in forms if f in _strings_in_answers(docs)]
            if len(forms) >= 2 and len(held) == 1 and exact:
                warnings.append(("instruction.md", lno, "M2",
                                 "the instruction allows %s (%r) but the answers hold only %r, compared exactly: "
                                 "check that the judge normalizes the other forms" % (
                                     " or ".join(map(repr, forms)), s[:160], held[0])))
    return findings, warnings


# ------------------------------------------------------------------ L1-L4, D1: limits

TIMEOUT_CONST = re.compile(r"^\s*([A-Z][A-Z0-9_]*TIMEOUT[A-Z0-9_]*)\s*=\s*([\d_]+(?:\.\d+)?)\b", re.M)
SOLUTION_TIMEOUT = re.compile(r"CASE|RUN|CALL|BUILD|SUITE|TEST|PROGRAM|PROBE|SCENARIO|IMPORT")
HARNESS_TIMEOUT = re.compile(r"GIT|DRAIN|POLL|WAIT|KILL|GRACE|EXTRACT|APPLY|UNPACK|JUDGE")
RLIMIT = re.compile(r"setrlimit\(\s*(?:resource\.)?RLIMIT_([A-Z]+)\s*,\s*\(?\s*([^,)]+)")
ULIMIT = re.compile(r"\bulimit\s+-([vmutnsdf])\s+(\S+)")
TEMPLATE_FSIZE = 64 << 20   # test.sh's ulimit -f 65536 in the v2 template
RES_KIND = {"AS": "memory", "DATA": "memory", "RSS": "memory", "v": "memory", "m": "memory", "d": "memory",
            "NPROC": "processes", "u": "processes", "CPU": "cpu", "t": "cpu", "NOFILE": "files", "n": "files",
            "STACK": "stack", "s": "stack", "FSIZE": "filesize", "f": "filesize"}
STATED = {
    "memory": re.compile(r"\b(memory|RAM|address space)\b", re.I),
    "processes": re.compile(r"\b(processes|threads)\b", re.I),
    "cpu": re.compile(r"\bCPU (time|seconds)|seconds of CPU\b", re.I),
    "files": re.compile(r"\b(file descriptors|open files)\b", re.I),
    "stack": re.compile(r"\bstack\b", re.I),
    "filesize": re.compile(r"\bfile[^.]{0,40}\b(above|over|larger|more than|at most|bigger)\b|\bany one file\b", re.I),
}


def _const_value(text: str, expr: str) -> float | None:
    """A literal or a NAME = literal / NAME = a << b constant of the same file."""
    expr = expr.strip()
    try:
        return float(ast.literal_eval(expr))
    except (ValueError, SyntaxError, TypeError):
        pass
    m = re.search(r"^\s*%s\s*=\s*(.+?)(?:#.*)?$" % re.escape(expr), text, re.M)
    if not m:
        return None
    try:
        node = ast.parse(m.group(1).strip(), mode="eval").body
        return float(eval(compile(ast.Expression(node), "<const>", "eval"), {"__builtins__": {}}))  # noqa: S307
    except Exception:  # noqa: BLE001
        return None


def container_memory_bytes(task: Path) -> float | None:
    try:
        t = tomllib.loads(_read(task / "task.toml"))
    except tomllib.TOMLDecodeError:
        return None
    vals = [v.get("memory_mb") for v in t.values() if isinstance(v, dict) and isinstance(v.get("memory_mb"), int)]
    return max(vals) * (1 << 20) if vals else None


def _template_line(line: str, tmpl: dict, name: str) -> bool:
    return line.strip() in tmpl.get(name, set())


def emit_runs_child(emit: str) -> bool:
    """The emitter runs each case in a child process (itself with --case, or the submitted program)."""
    return bool(re.search(r"subprocess\.(Popen|run)\(", emit))


def rule_limits(task, instr, tmpl) -> tuple[list, list]:
    findings, warnings = [], []
    limits = time_limits(instr)
    emit_p, sh_p = task / "tests" / "emit.py", task / "tests" / "test.sh"
    emit, sh = _read(emit_p), _read(sh_p)
    # time caps
    for m in TIMEOUT_CONST.finditer(emit):
        name, val = m.group(1), float(m.group(2).replace("_", ""))
        if not SOLUTION_TIMEOUT.search(name) or HARNESS_TIMEOUT.search(name):
            continue
        lno = emit.count("\n", 0, m.start()) + 1
        if not limits:
            warnings.append(("tests/emit.py", lno, "L3",
                             "%s = %g s caps the solution's run and the instruction states no time limit: a correct "
                             "solution slower than that fails. State the limit in the instruction, or confirm the "
                             "reference finishes far inside it" % (name, val)))
            continue
        longest = max(limits, key=lambda x: x["seconds"])
        if val < longest["seconds"]:
            findings.append(("tests/emit.py", lno, "L2",
                             "%s = %g s is shorter than the %g s the instruction gives (line %d: %r): a correct "
                             "solution that uses the time it was given fails. Fix: give the case at least the stated "
                             "time" % (name, val, longest["seconds"], longest["line"], longest["sentence"][:140])))
            continue
        calls = [x for x in limits if x["call"] and x["seconds"] >= val]
        if calls and "CASE" in name and emit_runs_child(emit):
            c = calls[0]
            findings.append(("tests/emit.py", lno, "D1",
                             "the instruction gives each call %g s (line %d: %r) and %s is the same %g s, measured "
                             "around the whole case process: interpreter start, the import of the submission and the "
                             "harness's own work in the case (hashing, serializing the result) count against it, so a "
                             "call that returns just in time misses the deadline. Fix: time the call itself inside "
                             "the case, or give the case a margin over the stated time" % (
                                 c["seconds"], c["line"], c["sentence"][:140], name, val)))
    # resource caps
    mem = container_memory_bytes(task)
    sources = [("tests/emit.py", emit, "emit.py", RLIMIT), ("tests/test.sh", sh, "test.sh", ULIMIT)]
    for rel, text, tname, rx in sources:
        for lno, line in enumerate(text.splitlines(), 1):
            if line.lstrip().startswith("#") or _template_line(line, tmpl, tname):
                continue
            for m in rx.finditer(line):
                kind = RES_KIND.get(m.group(1))
                if kind is None or STATED[kind].search(instr):
                    continue
                val = _const_value(text, m.group(2))
                if rx is ULIMIT and val is not None and m.group(1) in "vmdf":
                    val *= 1024   # bash counts these in 1,024-byte blocks
                if kind == "memory" and mem and val and val >= mem:
                    continue   # no tighter than the container task.toml gives
                if kind == "filesize" and (val is None or val >= TEMPLATE_FSIZE):
                    continue   # the v2 template's 64 MiB on every task, or a wider one
                warnings.append((rel, lno, "L1",
                                 "%s caps the solution's %s%s and the instruction does not state it: a correct "
                                 "solution that needs more fails. Fix: state the cap in the instruction, or lift it" % (
                                     m.group(0).strip(), kind,
                                     " at %s" % _human(val, kind) if val is not None else "")))
    # the collected output: one file read, the whole archive judged
    only = re.search(r"\bOnly\s+`([^`]+)`\s+is\s+(read|graded|kept)\b", instr)
    caps_size = re.search(r"max_submission_mb", sh) and re.search(r"MAX_MB", sh)
    states_size = re.search(r"\b\d[\d,.]*\s?(KiB|MiB|GiB|KB|MB|GB|kB|bytes)\b", instr)
    if only and caps_size and not states_size:
        lno = next((i for i, ln in enumerate(sh.splitlines(), 1) if "max_submission_mb" in ln and "MAX_MB" in ln), 0)
        lno = lno or next((i for i, ln in enumerate(sh.splitlines(), 1) if "MAX_MB" in ln), 0)
        warnings.append(("tests/test.sh", lno, "L4",
                         "the instruction says only `%s` is read, and the grader scores 0 when the collected output "
                         "is over max_submission_mb (tests/budget.json), a size the instruction does not state: a "
                         "scratch file next to a correct answer fails it. State the cap, or judge only the file that "
                         "is read" % only.group(1)))
    return findings, warnings


def _human(v: float, kind: str) -> str:
    if kind in ("memory", "filesize", "stack"):
        for u, n in (("GiB", 1 << 30), ("MiB", 1 << 20), ("KiB", 1 << 10)):
            if v >= n:
                return "%g %s" % (v / n, u)
        return "%g bytes" % v
    return "%g" % v


# ------------------------------------------------------------------ T1: the timer

SPEED = re.compile(r"\bspeed ?up\b|\bfaster\b|\btimes as fast\b|\blatency\b|\bthroughput\b|\bper second\b|"
                   r"\bwithin \d+ ?(ms|milliseconds?)\b|\bin under \d+ ?(ms|milliseconds?)\b", re.I)
CLOCKS = ("perf_counter", "perf_counter_ns", "monotonic", "monotonic_ns", "time", "process_time", "time_ns")


def _is_clock(node) -> bool:
    return (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in CLOCKS
            and isinstance(node.func.value, ast.Name) and node.func.value.id == "time") or (
        isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in ("perf_counter",
                                                                                            "monotonic"))


def _call_bases(nodes) -> set:
    out = set()
    for n in nodes:
        for c in ast.walk(n):
            if isinstance(c, ast.Call):
                f = c.func
                while isinstance(f, ast.Attribute):
                    f = f.value
                if isinstance(f, ast.Name):
                    out.add(f.id)
    return out


def rule_timer(task, instr, files) -> list:
    if not SPEED.search(instr):
        return []
    out = []
    for rel, text in files:
        try:
            tree = ast.parse(text)
        except SyntaxError:
            continue
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Module)):
                continue
            body = fn.body
            for i, st in enumerate(body):
                if not (isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name)
                        and _is_clock(st.value)):
                    continue
                start = st.targets[0].id
                stop = next((j for j in range(i + 1, len(body)) if any(
                    isinstance(c, ast.BinOp) and isinstance(c.op, ast.Sub) and isinstance(c.right, ast.Name)
                    and c.right.id == start for c in ast.walk(body[j]))), None)
                if stop is None:
                    continue
                built = {}
                for b in body[:i]:   # names bound before the clock starts, from a call: setup the submission did
                    if isinstance(b, ast.Assign) and isinstance(b.value, (ast.Call, ast.Await)):
                        for t in b.targets:
                            if isinstance(t, ast.Name):
                                built[t.id] = b.lineno
                    elif isinstance(b, (ast.Import, ast.ImportFrom)):
                        for a in b.names:
                            built[(a.asname or a.name).split(".")[0]] = b.lineno
                used = _call_bases(body[i + 1:stop + 1]) & set(built)
                used -= {"time", "json", "os", "sys", "subprocess", "math", "re"}
                if used:
                    n = sorted(used)[0]
                    out.append((rel, st.lineno, "T1",
                                "the instruction promises a speed and this timer starts after `%s` was built (line "
                                "%d), outside the timed interval: work the submission moves into that setup is not "
                                "measured. Fix: start the timer before the submission's setup, or time a fresh "
                                "process end to end" % (n, built[n])))
    return out


# ------------------------------------------------------------------ E1: booleans compared with ==

def _strict_funcs(trees) -> set:
    """Local functions whose body checks a value's type: type(a) is type(b), isinstance(x, bool)."""
    out = set()
    for tree in trees:
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.FunctionDef):
                continue
            for c in ast.walk(fn):
                if isinstance(c, ast.Compare) and any(isinstance(o, (ast.Is, ast.IsNot, ast.Eq, ast.NotEq))
                                                       for o in c.ops):
                    sides = [c.left] + list(c.comparators)
                    if sum(isinstance(s, ast.Call) and isinstance(s.func, ast.Name) and s.func.id == "type"
                           for s in sides) >= 2:
                        out.add(fn.name)
                if isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id == "isinstance" \
                        and len(c.args) == 2 and "bool" in ast.dump(c.args[1]):
                    out.add(fn.name)
    return out


def _called_names(node) -> set:
    out = set()
    for c in ast.walk(node):
        if isinstance(c, ast.Call):
            f = c.func
            out.add(f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else "")
    return out


def rule_bool_equality(task, docs, judge) -> list:
    if repo_language(task) in ("none", "python"):
        return []
    if not any(isinstance(v, bool) for d in docs for v in walk_json(d)):
        return []
    trees = []
    for rel, text in judge:
        try:
            trees.append((rel, ast.parse(text)))
        except SyntaxError:
            pass
    strict = _strict_funcs(t for _, t in trees)
    gated = False
    plain = []
    for rel, tree in trees:
        for a in ast.walk(tree):
            if not isinstance(a, ast.Assert):
                continue
            if _called_names(a.test) & (strict | {"same", "strict_equal", "plain", "typed_equal"}):
                gated = True
            t = a.test
            if isinstance(t, ast.Compare) and len(t.ops) == 1 and isinstance(t.ops[0], ast.Eq) and not any(
                    isinstance(s, ast.Constant) for s in (t.left, t.comparators[0])):
                plain.append((rel, a.lineno, ast.unparse(t)[:80],
                              bool(a.msg is not None and _called_names(a.msg) & strict)))
    if gated or not plain:
        return []
    rel, lno, expr, msg_only = plain[0]
    return [(rel, lno, "E1",
             "`assert %s` passes on Python equality and the answers hold booleans: 0 and 1 equal false and true, so a "
             "%s repository that emits a number where a boolean is required passes%s. Fix: compare with a strict type "
             "check in the assertion itself (type(got) is type(want) at every level)" % (
                 expr, repo_language(task).capitalize(),
                 " (the type check is only in the failure message, which runs after the comparison failed)"
                 if msg_only else ""))]


# ------------------------------------------------------------------ E2: part of the repository's tests

KEEP_PASSING = re.compile(r"(existing|repository's|library's|project's|their own|its own)[^.]{0,80}\btests?\b"
                          r"[^.]{0,100}\b(keep|still|continue)[^.]{0,30}\bpass", re.I)
SUBSET = [
    (re.compile(r"[\"']\./[\w/-]+/\.\.\.[\"']"), "an explicit package list instead of ./..."),
    (re.compile(r"--ignore(?:-glob)?[= ]"), "--ignore"),
    (re.compile(r"--deselect\b"), "--deselect"),
    (re.compile(r"[\"']-k[\"']\s*,\s*[\"']not\b|-k\s+[\"']not\b"), "-k \"not ...\""),
    (re.compile(r"[\"']-m[\"']\s*,\s*[\"']not\b|-m\s+[\"']not\b"), "-m \"not ...\""),
    (re.compile(r"--testPathIgnorePatterns\b|[\"']-skip[\"']"), "an exclusion flag"),
]
# an explicit package list is weaker evidence than a note or an exclusion: the packages it leaves out may hold no
# tests (image-cache-purge ./pkg/... ./cmd/..., accepted); it is advisory
PACKAGE_LIST = "an explicit package list instead of ./..."
NOT_RUN = re.compile(r"(end-to-end|e2e|integration)[^\n]{0,80}\b(not run|are skipped|is skipped|omitted|excluded|left out)",
                     re.I)


def rule_test_subset(task, instr, tmpl) -> tuple[list, list]:
    m = KEEP_PASSING.search(instr)
    # the instruction itself names the part that counts ("apart from its integration folder", "not marked ...")
    if not m or re.search(r"\b(apart from|except|other than|not marked|excluding)\b", m.group(0), re.I):
        return [], []
    said = m.group(0)
    findings, warnings = [], []
    for rel in ("tests/emit.py", "tests/test.sh"):
        text = _read(task / rel)
        for lno, line in enumerate(text.splitlines(), 1):
            if _template_line(line, tmpl, Path(rel).name):
                continue
            why = None if line.lstrip().startswith("#") else next((w for rx, w in SUBSET if rx.search(line)), None)
            if why is None and NOT_RUN.search(line):
                why = "a note that some of them are not run"
            if why is None:
                continue
            msg = ("the instruction says %r, and the grader runs part of them (%s): a regression confined to the "
                   "tests it leaves out is not graded. Fix: run them all, or say in the instruction which ones count"
                   % (said[:120], why))
            (warnings if why == PACKAGE_LIST else findings).append((rel, lno, "E2", msg))
    return findings[:1], ([] if findings else warnings[:1])


# ------------------------------------------------------------------ the gate

def check(task: Path) -> dict:
    """{"status", "details", "findings": [(path, line, rule, message)], "warnings": [...]}."""
    task = Path(task)
    if not (task / "tests").is_dir() or not (task / "instruction.md").is_file():
        return {"status": "ERROR", "details": "no tests/ folder or instruction.md: nothing to align",
                "findings": [], "warnings": []}
    instr = _read(task / "instruction.md")
    docs = answers(task)
    judge = [(_rel(task, p), _read(p)) for p in judge_paths(task)]
    try:
        import grader_hygiene
        tmpl = {} if (task / grader_hygiene.V21_MARKER).is_file() else grader_hygiene.template_lines()
    except Exception:  # noqa: BLE001
        tmpl = {}
    findings, warnings = [], []
    f, w = rule_modals(task, instr, docs, judge)
    findings += f
    warnings += w
    f, w = rule_limits(task, instr, tmpl)
    findings += f
    warnings += w
    grader = judge + [("tests/emit.py", _read(task / "tests" / "emit.py"))]
    findings += rule_timer(task, instr, grader)
    findings += rule_bool_equality(task, docs, judge)
    f, w = rule_test_subset(task, instr, tmpl)
    findings += f
    warnings += w
    findings = sorted(set(findings), key=lambda x: (x[0], x[1], x[2]))
    warnings = sorted(set(warnings), key=lambda x: (x[0], x[1], x[2]))
    if findings:
        rules = sorted({x[2] for x in findings})
        status = "FAIL-PENDING-DISPOSITION"
        details = ("%d finding(s) (%s) where the grader enforces what the instruction does not say: a reviewer fixes "
                   "the grader or the instruction, or disposes each item with what was checked (`tb4 gate dispose`)"
                   % (len(findings), ", ".join(rules)))
    else:
        status = "PASS"
        details = "no modal, limit, deadline, timer, boolean-equality or test-subset finding"
    if warnings:
        details += "; %d advisory warning(s) (%s)" % (len(warnings), ", ".join(sorted({x[2] for x in warnings})))
    return {"status": status, "details": details, "findings": findings, "warnings": warnings}


if __name__ == "__main__":
    import sys
    for arg in sys.argv[1:]:
        r = check(Path(arg))
        print("%s: %s  %s" % (Path(arg).name, r["status"], r["details"]))
        for p, n, rule, msg in r["findings"]:
            print("  %s %s:%d  %s" % (rule, p, n, msg))
        for p, n, rule, msg in r["warnings"]:
            print("  (warning) %s %s:%d  %s" % (rule, p, n, msg))
