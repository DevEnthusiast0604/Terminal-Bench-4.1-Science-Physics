#!/usr/bin/env python3
"""grader-hygiene: static rules for the grader mechanisms behind the customer's 10/16 grader findings.

The gate reads only the code that reads the deliverable or emits observations:
  - tests/test_outputs.py and tests/emit.py, plus the tests/*.py modules they import (never tests/gen, a generator
    or data);
  - tests/test.sh;
  - tests/grading.json.

It never runs the task. One rule, B2, runs the task's own tolerance arithmetic on numbers to show a real boundary
failure. Every finding is path:line, names the mechanism, and ends with the fix.

  B1  a JSON deliverable is loaded without rejecting duplicate keys. Python keeps the last value of a repeated key,
      so `{"cause": "lightning", "cause": "line"}` reads as the second value. Fix: tb4judge.load_json, an
      object_pairs_hook that raises on a repeated key.
  B2  a tolerance is compared in binary floats, `abs(got - want) <= TOL`. A value exactly TOL away (2820.00 against
      2820.05) can fail. The finding states a pair that fails under the judge's own arithmetic. Fix:
      tb4judge.within, which compares in Decimal.
  B3  a CSV deliverable's rows are split on commas. A valid CSV that quotes a field fails. Fix: tb4judge.read_csv,
      which uses csv.reader.
  B4  key order is asserted (`list(obj) == KEYS`) for an object whose keys instruction.md does not order. An order
      counts as stated only when the list of keys that follows the word "keys" is introduced by "in this order" or
      ends in ", in that order". Only an object counts: a list compared to a list is an array in order, and a CSV
      header is column order unless instruction.md calls those names keys. Fix: tb4judge.keys(obj, KEYS,
      ordered=False), or state the order.
  B5  a test run (pytest, jest, `npm test`, `cargo test`, `go test`, `make test`, ...) whose exit status is never
      read. A suite that fails after its assertions pass (a teardown error, a crash at exit) still counts. An install
      or build step (`npm ci`, `cargo build`, `pip install`) is not a test run. Fix: fail unless the exit status is
      the one expected.
  B6  what the code under test returned is serialized with a converting default (json.dumps(default=str), float,
      list, vars, a function that returns a value): an object of the wrong type becomes the JSON value the
      instruction asks for (a Decimal or a Path its text, a set a list), so the judge accepts it. default=repr is not
      a finding: its text names the type, so the judge rejects it. json writes a tuple as a list with or without a
      default; the api-types control and template v2.1's plain() check catch that. Fix: no default; fail the case on
      a non-JSON type.
  B7  tests/grading.json test_globs names a project file (package.json, pyproject.toml, ...) that instruction.md
      does not freeze. The verifier discards the agent's edits to it. Fix: remove it from test_globs, or freeze it
      in the instruction.
  B8  inputs are not isolated:
      - the program's environment names the folder that holds every case (TB4_CASES);
      - every case is staged in one folder the runner can read, and the program runs once per case;
      - the runner owns the inputs or can write to them.
      Fix: stage one case per run, root:root a+rX,go-w.
  B9  (advisory warning, never a finding) the emitter discards information: .strip(), set(), case folding,
      sorting. It points at what to check by hand.
  B10 an item no pattern reads is dropped without an error: a loop over patterns with a `break` on a match and no
      `else`, a `continue` when nothing matched, or an emitter that keeps only the items a pattern matches. A
      contradictory sentence beside the right one is never seen (alaska-metar-remarks). Fix: fail on an item no
      pattern reads, or collect such items where the judge requires none.
  B11 a stream cap the instruction states is checked on the final size of the file the program's stdout or stderr
      went to: a program writes past it, seeks back and truncates (survey-wave-estimates). Fix: read through pipes
      and count every byte (template v2.1 tests/emit.py).
  B12 an unchanged check hashes a tree's paths and contents but no file mode, where the instruction promises the
      inputs stay unchanged: a chmod is invisible (survey-wave-estimates). Fix: hash each entry's mode too.
  B13 the judge decides with == between the observed value and an answer that holds booleans: 0/1 passes for
      false/true (namespace-sleep-wake). Members the emitter fills with a real boolean itself do not count. Fix:
      tb4judge.same, or check the JSON types first.
  B14 the collect hook packs all of /app/output, test.sh caps the whole archive or refuses a link anywhere in it,
      and the instruction says only the named file is read (without saying the folder is collected whole): an
      unrelated scratch file or link fails a correct deliverable (disk-fleet-replacement). Fix: declared
      deliverables and template v2.1's unpack.
  B15 the per-case process deadline is the instruction's own time limit for the graded call: start-up, the import
      and the serialization around the call count against it (charge-session-settlement). Fix: time the call
      itself and give the process a margin.
  B16 the instruction promises an agent-side path stays as delivered and nothing the verifier sees records it (a
      separate verifier whose collect hook leaves it out, or a shared one no check reads it in): only the
      verifier's fresh copy is compared (ranch-backpay-load). Fix: grading.json "protected" (template v2.1).

Severity:
  - Mechanical findings FAIL on any template. A finding on a line the v2 template ships verbatim (tests/test.sh,
    tests/emit.py; data/template-v2-lines.json) is the template's, fixed by `tb4 upgrade-verifier` (template v2.1).
    A B1 is the JSON loader every task copied, fixed by tb4judge.load_json in the task's own judge. Neither is
    disposed task by task.
  - B10-B13 and B15 on a line the v2 template ships verbatim are advisory warnings (one batch upgrade fixes every
    task made from it); B14 and B16 rest on the task's own promise and count as findings even on template lines.
  - The task's own findings: on the v2 template, when they are the only ones, the gate is FAIL-PENDING-DISPOSITION
    and a reviewer fixes each or settles it with `tb4 gate dispose <task> <key> accept|waive --reason .. --by ..`.
    On template v2.1 (it ships tests/tb4judge.py) they FAIL.
  - A FAIL is never disposed. The author can dispute a finding (`tb4 gate dispute`); the record stays FAIL, and a
    reviewer who is not an author settles each disputed item with `tb4 gate dispose`. The gate counts as met once
    every finding is disputed and settled.

Stdlib only, Python 3.11+.
"""
from __future__ import annotations

import ast
import json
import re
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path

JUDGE_FILES = ("tests/test_outputs.py", "tests/emit.py")
SKIP_PARTS = {"gen", "data", "fixtures", "static", "records", "calibration", "solver", "derive", "golden"}
V21_MARKER = "tests/tb4judge.py"

# What a value is, from the names and strings it is built from (resolve()). The task's own files are never a
# deliverable: the answer key, expected.json, budget.json, grading.json and requirements.json.
OWN_TOKENS = {"expected", "tb4_expected", "pointer", "pointer_path", "answer", "answers", "key", "truth", "budget",
              "grading", "requirements", "calibration", "golden", "fixture", "fixtures", "key_path", "keyfile",
              "answer_key", "expected_path"}
DELIVERABLE_TOKENS = {"tb4_output", "out", "output", "outdir", "out_dir", "output_dir", "deliverable",
                      "deliverables", "submission", "stdout", "observed", "plan", "produced", "written", "got",
                      "have", "result_file", "out_file", "report_path", "out_path"}
HARNESS_TOKENS = {"observations", "observation", "jsonl", "obs_file", "tb4_obs"}
# B5 counts a command that runs tests, never an install or a build step (npm ci, cargo build, pip install, go build,
# make with no test target): a test runner named in the command, or a tool's own test entry point
TEST_RUNNERS = ("pytest", "py.test", "jest", "vitest", "mocha", "rspec", "phpunit", "ctest", "tox", "nox", "unittest",
                "nextest")
TEST_RUNNER_RE = re.compile(r"(?:^|[/\s'\"=])(" + "|".join(re.escape(r) for r in TEST_RUNNERS) +
                            r")(?=$|[\s'\"/.:;&|)])")
TOOL_TEST_RE = re.compile(
    r"\b(?:npm|yarn|pnpm|bun|deno)\s+(?:run\s+|run-script\s+)?(?:test|t)(?=$|[\s:'\";&|)])"
    r"|\bnpx\s+(?:jest|vitest|mocha)\b|\bcargo\s+(?:\+\S+\s+)?(?:test|nextest)\b|\bgo\s+test\b"
    r"|\bdotnet\s+test\b|\bmix\s+test\b|\b(?:mvn|mvnw|gradle|gradlew)\b[^;&|]*?\s(?:test|verify|check)\b"
    r"|\bsbt\b[^;&|]*?\s(?:test|testOnly)\b|\bmake\b[^;&|]*?\s(?:test|check)\b", re.I)
# the same tools, read from the command's words in any order (an argv built in pieces): the tool and its test word
TOOL_TEST_WORDS = {"npm": {"test", "t"}, "yarn": {"test"}, "pnpm": {"test"}, "bun": {"test"}, "deno": {"test"},
                   "cargo": {"test", "nextest"}, "go": {"test"}, "dotnet": {"test"}, "mix": {"test"},
                   "mvn": {"test", "verify"}, "gradle": {"test", "check"}, "gradlew": {"test", "check"},
                   "sbt": {"test"}, "make": {"test", "check"}}
# project metadata a repair may legitimately edit (a configuration key, a script): a finding. Lockfiles and compiler
# settings are left out (discarding them is what a "no new dependencies" task wants); pyproject.toml, setup.cfg and
# setup.py usually also carry the test runner's own configuration, which test_globs rightly keeps: an advisory warning.
MANIFESTS = re.compile(r"^(?:package\.json|go\.mod|Cargo\.toml|Gemfile|pom\.xml|build\.gradle(?:\.kts)?|"
                       r"composer\.json)$")
TEST_CONFIG_MANIFESTS = re.compile(r"^(?:pyproject\.toml|setup\.cfg|setup\.py)$")
# the instruction says the file stays as it is: a prohibition on changing it, or that the checker restores it
FREEZE_WORDS = re.compile(r"\b(?:must not|do not|don't|never|may not|cannot|can't|not allowed to)\b[^.;]{0,60}?"
                          r"\b(?:change|modify|edit|touch|alter|update|rewrite)|\b(?:unchanged|untouched|frozen|"
                          r"read-only|restored|reset|reverted|discarded|kept as (?:it is|is))\b", re.I)
ORDER_PHRASE = re.compile(r"\bin (?:this|that|the following|the same|exactly this) order\b|\bin order\b|"
                          r"\bordered as\b", re.I)
BACKTICK = re.compile(r"`([^`\n]+)`")
SENTENCE_END = re.compile(r"[.!?](?=\s+[A-Z`(\[*_]|\s*$)")
KEYS_WORD = re.compile(r"\bkeys?\b", re.I)


# ------------------------------------------------------------------ reading the grader

def _rel(task: Path, p: Path) -> str:
    return p.relative_to(task).as_posix()


def judge_files(task: Path) -> list[Path]:
    """tests/test_outputs.py, tests/emit.py and the tests/*.py modules they import, once each."""
    tests = task / "tests"
    out, seen = [], set()
    queue = [task / f for f in JUDGE_FILES]
    while queue:
        p = queue.pop(0)
        if p in seen or not p.is_file() or any(part in SKIP_PARTS for part in p.relative_to(task).parts[1:-1]):
            continue
        seen.add(p)
        out.append(p)
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and not node.level:
                names = [node.module.split(".")[0]]
            for n in names:
                q = tests / (n + ".py")
                if q.is_file() and not n.startswith("generate") and q not in seen:
                    queue.append(q)
    return out


class Scope:
    """Assignments of a module and of each function: name -> [(line, expression)] (assign, with ... as, for)."""

    def __init__(self, tree: ast.Module):
        self.tree = tree
        self.module = self._assigns(tree.body, top=True)
        self.funcs = {}
        self.owner = {}
        self.params = {}
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self.funcs[node] = self._assigns([node], top=False)
                self.params[node] = [a.arg for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs]
                for sub in ast.walk(node):
                    if hasattr(sub, "lineno") and sub is not node:
                        self.owner.setdefault(id(sub), node)

    @staticmethod
    def _assigns(body, top: bool) -> dict:
        out: dict = {}

        def add(target, value, line):
            if isinstance(target, ast.Name):
                out.setdefault(target.id, []).append((line, value))
            elif isinstance(target, (ast.Tuple, ast.List)):
                for t in target.elts:
                    add(t, value, line)

        nodes = []
        for b in body:
            if top and isinstance(b, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            nodes.extend(ast.walk(b))
        for n in nodes:
            if top and isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if isinstance(n, ast.Assign):
                for t in n.targets:
                    add(t, n.value, n.lineno)
            elif isinstance(n, ast.AnnAssign) and n.value is not None:
                add(n.target, n.value, n.lineno)
            elif isinstance(n, (ast.With, ast.AsyncWith)):
                for it in n.items:
                    if it.optional_vars is not None:
                        add(it.optional_vars, it.context_expr, n.lineno)
            elif isinstance(n, (ast.For, ast.AsyncFor)):
                add(n.target, n.iter, n.lineno)
            elif isinstance(n, ast.comprehension):
                add(n.target, n.iter, getattr(n.iter, "lineno", 0))
        return out

    def func_of(self, node):
        return self.owner.get(id(node))

    def lookup(self, name: str, node, line: int | None = None) -> list:
        """The assignments of NAME that reach NODE (or LINE): in a function, the latest one at or before that line (a
        name reused for the deliverable and then for the answer key is two different values); else the module's."""
        f = self.func_of(node)
        if f is not None and name in self.funcs.get(f, {}):
            cands = self.funcs[f][name]
            line = getattr(node, "lineno", None) if line is None else line
            before = [c for c in cands if line is not None and c[0] <= line]
            if before:
                last = max(c[0] for c in before)
                return [c for c in before if c[0] == last]
            return [] if line is not None and f is not None else cands
        return self.module.get(name, [])


def _tokens(expr) -> tuple[set, set]:
    """(identifier tokens, string constants) used in EXPR."""
    ids, strs = set(), set()
    for n in ast.walk(expr):
        if isinstance(n, ast.Name):
            ids.add(n.id)
        elif isinstance(n, ast.Attribute):
            ids.add(n.attr)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str):
            strs.add(n.value)
        elif isinstance(n, ast.arg):
            ids.add(n.arg)
    return ids, strs


def resolve(expr, scope: Scope, at, depth: int = 0, seen=None, line: int | None = None) -> tuple[set, set]:
    """Every identifier and string EXPR is built from, following the names it uses through the assignments that
    reach them (in the enclosing function, then the module), at most 6 levels deep. The names of an assignment's
    right-hand side resolve before that assignment, so `lines = [x for x in lines]` reaches the earlier `lines`."""
    seen = set() if seen is None else seen
    ids, strs = _tokens(expr)
    if depth >= 6:
        return ids, strs
    for name in list(ids):
        for l, value in scope.lookup(name, at, line):
            if (name, l) in seen:
                continue
            seen.add((name, l))
            i2, s2 = resolve(value, scope, at, depth + 1, seen, line=l - 1)
            ids |= i2
            strs |= s2
    return ids, strs


def _classify(ids: set, strs: set) -> str:
    low = {i.lower() for i in ids}
    text = " ".join(s.lower() for s in strs)
    if low & OWN_TOKENS or "/tests/" in text or "expected" in text:
        return "own"
    if any(s.startswith("TB4-") for s in strs):
        return "harness"           # a TB4-OBS / TB4-LINT protocol line the harness's own code printed
    keys = {s.lower() for s in strs}           # a subscript key reads the same as a name: v["stdout"] is the program's
    if "stdout" in low or "stdout" in keys or "/app/output" in text or "/app/submission" in text or \
            low & DELIVERABLE_TOKENS:
        return "deliverable"
    if low & HARNESS_TOKENS or ".jsonl" in text:
        return "harness"
    return "unknown"


def kind_of(expr, scope: Scope, at, depth: int = 0) -> str:
    """'own' (the task's own files), 'harness' (the observations emit.py wrote), 'deliverable' or 'unknown'. A value
    that comes in as a parameter of the enclosing function is what its callers pass (a helper `_load(path)` reads the
    deliverable when a caller passes OUT / DELIVERABLE)."""
    ids, strs = resolve(expr, scope, at)
    kind = _classify(ids, strs)
    if kind != "unknown" or depth >= 3:
        return kind
    f = scope.func_of(at)
    params = [p for p in scope.params.get(f, []) if p in ids] if f is not None else []
    kinds = set()
    for name in params:
        idx = scope.params[f].index(name)
        for call in ast.walk(scope.tree):
            if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == f.name:
                arg = call.args[idx] if idx < len(call.args) else _kw(call, name)
                if arg is not None:
                    kinds.add(kind_of(arg, scope, call, depth + 1))
    for k in ("deliverable", "own", "harness"):
        if k in kinds:
            return k
    return "unknown"


def _is_json_call(node, attr: tuple) -> bool:
    if not isinstance(node, ast.Call):
        return False
    f = node.func
    return isinstance(f, ast.Attribute) and f.attr in attr and isinstance(f.value, ast.Name) and f.value.id == "json"


def _kw(node, name):
    return next((k.value for k in node.keywords if k.arg == name), None)


# ------------------------------------------------------------------ B1 duplicate keys

def rule_dup_keys(rel: str, tree, scope: Scope) -> list:
    out = []
    for node in ast.walk(tree):
        if not _is_json_call(node, ("load", "loads")) or not node.args or _kw(node, "object_pairs_hook") is not None:
            continue
        if kind_of(node.args[0], scope, node) != "deliverable":
            continue
        out.append((rel, node.lineno, "B1",
                    "reads the deliverable with json.%s(), which keeps only the last of two duplicate keys: an object "
                    "holding a wrong value and then the right one under the same key passes as the right one. Load it "
                    "with tb4judge.load_json (an object_pairs_hook that raises on a repeated key)" % node.func.attr))
    return out


# ------------------------------------------------------------------ B2 float tolerance at its boundary

def _num(x):
    if isinstance(x, bool):
        return None
    if isinstance(x, (int, float)):
        return x
    return None


def _const_values(expr, scope: Scope, at, depth=0) -> list:
    """[(field or None, number)] a tolerance expression stands for: a number, a name bound to one, or an item of a
    dict of numbers (every item, with its key)."""
    if depth > 4:
        return []
    if isinstance(expr, ast.Constant):
        v = _num(expr.value)
        return [(None, v)] if v is not None else []
    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.USub):
        return [(f, -v) for f, v in _const_values(expr.operand, scope, at, depth + 1)]
    if isinstance(expr, ast.Name):
        out = []
        for _, value in scope.lookup(expr.id, at):
            out += _const_values(value, scope, at, depth + 1)
        return out
    if isinstance(expr, ast.Dict):
        out = []
        for k, v in zip(expr.keys, expr.values):
            if isinstance(k, ast.Constant) and isinstance(v, ast.Constant) and _num(v.value) is not None:
                out.append((str(k.value), v.value))
        return out
    if isinstance(expr, ast.Subscript):
        base = _const_values(expr.value, scope, at, depth + 1)
        sl = expr.slice
        if isinstance(sl, ast.Constant):
            return [(f, v) for f, v in base if f == str(sl.value)] or base
        return base
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id == "float" and expr.args:
        return _const_values(expr.args[0], scope, at, depth + 1)
    return []


def _exact(expr) -> bool:
    """The compared values are converted to exact arithmetic first (Decimal, Fraction) or rounded."""
    for n in ast.walk(expr):
        if isinstance(n, ast.Call):
            name = n.func.id if isinstance(n.func, ast.Name) else n.func.attr if isinstance(n.func, ast.Attribute) else ""
            if name in ("Decimal", "Fraction", "round", "quantize", "isclose_decimal"):
                return True
    return False


def _tolerance_compares(tree, scope: Scope):
    """(node, tolerance expression) for abs(a - b) <= T, T >= abs(a - b), abs(a - b) > T (a fail test),
    math.isclose(..., abs_tol=T) and pytest.approx(..., abs=T), when the operands are not made exact first."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            left, op, right = node.left, node.ops[0], node.comparators[0]
            for diff, tol, ops in ((left, right, (ast.LtE, ast.Gt)), (right, left, (ast.GtE, ast.Lt))):
                if isinstance(op, ops) and isinstance(diff, ast.Call) and isinstance(diff.func, ast.Name) \
                        and diff.func.id == "abs" and diff.args and isinstance(diff.args[0], ast.BinOp) \
                        and isinstance(diff.args[0].op, ast.Sub) and not _exact(diff):
                    yield node, tol
        elif isinstance(node, ast.Call):
            f = node.func
            name = f.attr if isinstance(f, ast.Attribute) else f.id if isinstance(f, ast.Name) else ""
            if name == "isclose" and not (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                                          and f.value.id not in ("math",)) and not _exact(node):
                t = _kw(node, "abs_tol")
                if t is not None:
                    yield node, t
            elif name == "approx" and not _exact(node):
                t = _kw(node, "abs")
                if t is not None:
                    yield node, t


def _json_numbers(task: Path) -> list:
    """[(key, number)] in the JSON files tests/ ships at its top level (expected values), in file order."""
    out = []
    tests = task / "tests"
    for p in sorted(tests.glob("*.json")):
        if p.name in ("grading.json", "budget.json", "requirements.json") or p.stat().st_size > 2_000_000:
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except ValueError:
            continue
        stack = [(None, doc)]
        while stack:
            k, v = stack.pop(0)
            if isinstance(v, dict):
                stack.extend(v.items())
            elif isinstance(v, list):
                stack.extend((k, x) for x in v)
            elif _num(v) is not None:
                out.append((k, v))
    return out


def _boundary_pair(v, tol):
    """(want, got, |got - want|) where got is exactly TOL from WANT in decimal but abs(got - want) <= tol is False in
    binary floats, or None."""
    try:
        dv, dt = Decimal(repr(float(v))), Decimal(repr(float(tol)))
    except (InvalidOperation, ValueError, OverflowError):
        return None
    for got in (float(dv + dt), float(dv - dt)):
        diff = abs(got - float(v))
        if not diff <= tol:
            return float(v), got, diff
    return None


def boundary_evidence(task: Path, fields_tols: list, shipped: list):
    """The first boundary failure for a tolerance: on a value the tests ship (under the tolerance's own field when
    it has one), else on a value with the tolerance's precision. (want, got, diff, tol, source) or None."""
    for field, tol in fields_tols:
        if not isinstance(tol, float) or tol <= 0 or float(tol).is_integer():
            continue
        values = [v for k, v in shipped if field is None or k == field]
        for v in values:
            pair = _boundary_pair(v, tol)
            if pair:
                return pair + (tol, "a value tests/ ships" + (" under %r" % field if field else ""))
    for field, tol in fields_tols:
        if not isinstance(tol, float) or tol <= 0 or float(tol).is_integer():
            continue
        places = max(0, -Decimal(repr(tol)).normalize().as_tuple().exponent)
        step = Decimal(1).scaleb(-places)
        for k in range(1, 200_000):
            pair = _boundary_pair(float(step * k), tol)
            if pair:
                return pair + (tol, "a value with the tolerance's precision")
    return None


NUMBER_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
                "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8}
STATED_DECIMALS = re.compile(r"\b(\d|one|two|three|four|five|six|seven|eight|first|second|third|fourth|fifth|sixth|"
                             r"seventh|eighth)(?:\s+|-)decimals?\b|\bnearest (cent|0\.01|0\.001|0\.0001)\b", re.I)


def stated_decimals(instr: str) -> set:
    """The numbers of decimals instruction.md asks values to be written with ("four decimal places", "the fourth
    decimal", "to the nearest cent")."""
    out = set()
    for m in STATED_DECIMALS.finditer(instr):
        if m.group(1):
            w = m.group(1).lower()
            out.add(int(w) if w.isdigit() else NUMBER_WORDS[w])
        else:
            out.add({"cent": 2, "0.01": 2, "0.001": 3, "0.0001": 4}[m.group(2).lower()])
    return out


def _decimals(x) -> int:
    return max(0, -Decimal(repr(float(x))).normalize().as_tuple().exponent)


def rule_float_tolerance(task: Path, rel: str, tree, scope: Scope, shipped: list,
                         instr: str = "") -> tuple[list, list]:
    """B2. A tolerance finer than the precision instruction.md asks for (5e-05 for values written to four decimals:
    half a unit of the last place) has a boundary no correctly written value can reach: no finding."""
    out, warns = [], []
    stated = stated_decimals(instr)
    for node, tol in _tolerance_compares(tree, scope):
        values = _const_values(tol, scope, node)
        if stated:
            reach = [(f, t) for f, t in values if not (isinstance(t, float) and _decimals(t) > max(stated))]
            if values and not reach:
                warns.append((rel, node.lineno, "B2", "compares a tolerance in binary floats, but the tolerance is "
                              "finer than the %d decimal(s) instruction.md asks for, so a correctly written value never "
                              "sits on its boundary" % max(stated)))
                continue
            values = reach
        if not values:
            continue
        ev = boundary_evidence(task, values, shipped)
        if ev is None:
            if any(isinstance(t, float) and not float(t).is_integer() for _, t in values):
                warns.append((rel, node.lineno, "B2",
                              "compares a tolerance in binary floats; no boundary failure was found on the values "
                              "tried, but tb4judge.within (Decimal) removes the risk"))
            continue
        want, got, diff, t, source = ev
        out.append((rel, node.lineno, "B2",
                    "compares abs(got - want) against the tolerance %r in binary floats, so a value exactly %r away "
                    "can be rejected: want %r and got %r (%s) give a difference of %r, above %r. Compare in Decimal "
                    "with tb4judge.within(have, want, tol)" % (t, t, want, got, source, diff, t)))
    return out, warns


# ------------------------------------------------------------------ B3 CSV split on commas

NO_QUOTES = re.compile(r"\b(?:not|never|no|without)\b[^.;]{0,40}\bquot|\bunquoted\b", re.I)


def rule_csv_split(task: Path, rel: str, tree, scope: Scope, csv_task: bool, instr: str = "") -> list:
    """A CSV deliverable split on commas, unless instruction.md itself rules quoting out (then the strictness is
    stated)."""
    if not csv_task or NO_QUOTES.search(instr):
        return []
    out = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "split"
                and node.args and isinstance(node.args[0], ast.Constant) and node.args[0].value in (",", ", ")):
            continue
        recv = node.func.value
        if isinstance(recv, ast.Constant):
            continue
        if isinstance(recv, ast.Name) and all(isinstance(v, ast.Constant)
                                              for _, v in scope.lookup(recv.id, node)) \
                and scope.lookup(recv.id, node):
            continue
        if kind_of(recv, scope, node) != "deliverable":
            continue
        out.append((rel, node.lineno, "B3",
                    "splits the CSV deliverable's rows on commas: a valid CSV that quotes a field (\"a,b\" or "
                    "\"x\") keeps its quotes or splits inside them, and fails. Parse it with tb4judge.read_csv "
                    "(csv.reader)"))
    return out


# ------------------------------------------------------------------ B4 key order the instruction does not state

def _str_list(expr) -> list | None:
    if isinstance(expr, (ast.List, ast.Tuple)) and expr.elts and all(
            isinstance(e, ast.Constant) and isinstance(e.value, str) for e in expr.elts):
        return [e.value for e in expr.elts]
    return None


def _keys_lists(expr, scope: Scope, at) -> list:
    """The constant key lists EXPR stands for: a literal, a name bound to one, or a parameter of the enclosing
    function, followed to the literal lists its callers pass."""
    lit = _str_list(expr)
    if lit:
        return [lit]
    if not isinstance(expr, ast.Name):
        return []
    found = []
    for _, value in scope.lookup(expr.id, at):
        lit = _str_list(value)
        if lit:
            found.append(lit)
    if found:
        return found
    f = scope.func_of(at)
    if f is None or expr.id not in scope.params.get(f, []):
        return []
    idx = scope.params[f].index(expr.id)
    for call in ast.walk(scope.tree):
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == f.name:
            arg = call.args[idx] if idx < len(call.args) else _kw(call, expr.id)
            if arg is not None:
                found += [k for k in _keys_lists(arg, scope, call)]
    return found


def _ordered_obj(expr):
    """(X, keys_call) when EXPR is list(X), list(X.keys()), tuple(X) or [*X]; keys_call is True for X.keys(). (None,
    False) otherwise."""
    if isinstance(expr, ast.Call) and isinstance(expr.func, ast.Name) and expr.func.id in ("list", "tuple") \
            and len(expr.args) == 1:
        a = expr.args[0]
        if isinstance(a, ast.Call) and isinstance(a.func, ast.Attribute) and a.func.attr == "keys" and not a.args:
            return a.func.value, True
        return a, False
    if isinstance(expr, ast.List) and len(expr.elts) == 1 and isinstance(expr.elts[0], ast.Starred):
        return expr.elts[0].value, False
    return None, False


# list(X) == [...] asserts an order. It is key order only when X is an object (a dict): a list compared to a list is
# an array in order, and a CSV header is column order.
TABLE_TOKENS = {"csv", "reader", "dictreader", "fieldnames", "header", "headers", "columns", "cols", "heading",
                "headings", "row", "rows", "line", "lines", "split", "splitlines"}
DICT_USE = ("keys", "items", "values", "get", "setdefault")
FIELD_WORDS = re.compile(r"\b(?:fields?|members?|propert(?:y|ies)|attributes?)\b", re.I)
OBJECT_WORDS = re.compile(r"\b(?:objects?|JSON|dict(?:ionary|ionaries|s)?|mappings?)\b", re.I)
TABLE_WORDS = re.compile(r"\b(?:CSV|TSV|columns?|headers?|header row|spreadsheet|table)\b", re.I)


def _same(a, b) -> bool:
    return ast.dump(a) == ast.dump(b)


def _used_as_dict(obj, scope: Scope, at) -> bool:
    """OBJ is checked or used as a dict where it is compared: isinstance(OBJ, dict), OBJ.items(), OBJ.get(...)."""
    f = scope.func_of(at)
    for n in ast.walk(f if f is not None else scope.tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "isinstance" \
                and len(n.args) == 2 and _same(n.args[0], obj):
            t = n.args[1]
            names = [t] if not isinstance(t, ast.Tuple) else t.elts
            if any(isinstance(x, (ast.Name, ast.Attribute)) and (getattr(x, "id", None) or getattr(x, "attr", ""))
                   in ("dict", "Mapping", "MutableMapping", "OrderedDict") for x in names):
                return True
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in DICT_USE \
                and _same(n.func.value, obj):
            return True
    return False


def instruction_calls_keys(instr: str, keys: list, strict: bool = False) -> bool:
    """instruction.md names KEYS (two of them, or the one) as an object's keys: backticked after a "key(s)" word in
    the same sentence, or (unless STRICT) after "fields", "members" or "properties" of an object or JSON document that
    is not a CSV or a table."""
    text = re.sub(r"\s+", " ", instr)
    need = min(2, len(keys))
    words = [(m, True) for m in KEYS_WORD.finditer(text)] + ([] if strict else [(m, False) for m in
                                                                               FIELD_WORDS.finditer(text)])
    for m, is_key in words:
        span = text[m.end(): m.end() + 1500]
        end = SENTENCE_END.search(span)
        span = span[:end.start() + 1] if end else span
        named = {t.group(1).strip() for t in BACKTICK.finditer(span)}
        if len(named & set(keys)) < need:
            continue
        if is_key:
            return True
        around = text[max(0, m.start() - 200): m.end()] + span
        if OBJECT_WORDS.search(around) and not TABLE_WORDS.search(around):
            return True
    return False


def _shipped_shapes(task: Path) -> tuple[list, list]:
    """([key lists of the objects], [string lists of the arrays]) in the JSON files tests/ ships at its top level."""
    objs, arrays = [], []
    tests = task / "tests"
    for p in sorted(tests.glob("*.json")):
        if p.name in ("grading.json", "budget.json", "requirements.json") or p.stat().st_size > 2_000_000:
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except ValueError:
            continue
        stack = [doc]
        while stack:
            v = stack.pop()
            if isinstance(v, dict):
                objs.append(list(v))
                stack.extend(v.values())
            elif isinstance(v, list):
                if v and all(isinstance(x, str) for x in v):
                    arrays.append(v)
                stack.extend(v)
    return objs, arrays


def key_order_shape(obj, keys_call: bool, keys: list, scope: Scope, at, instr: str, shipped: tuple) -> str:
    """'dict' when the compared X is an object, so the order asserted is key order; 'table' for a CSV header or a
    split line (column order); 'array' for a list of values; 'unknown' when nothing shows which."""
    if keys_call or _used_as_dict(obj, scope, at):
        return "dict"
    ids, strs = resolve(obj, scope, at)
    if {i.lower() for i in ids} & TABLE_TOKENS or any(s in (",", "\t", ";") for s in strs):
        return "dict" if instruction_calls_keys(instr, keys, strict=True) else "table"
    objs, arrays = shipped
    if any(set(o) == set(keys) for o in objs):
        return "dict"
    if any(set(a) == set(keys) for a in arrays):
        return "array"
    return "dict" if instruction_calls_keys(instr, keys) else "unknown"


def instruction_orders(instr: str, keys: list) -> str | None:
    """The instruction's own words when it orders KEYS: the list of backticked keys that follows a "keys" word
    starts with KEYS[0] and holds every key in this order, and an order phrase stands between that word and the first
    key ("keys, in this order: `a`") or right after the last key ("`a` and `b`, in that order"). None otherwise."""
    text = re.sub(r"\s+", " ", instr)
    for m in KEYS_WORD.finditer(text):
        span = text[m.end(): m.end() + 2500]
        end = SENTENCE_END.search(span)            # the list belongs to this sentence only
        span = span[:end.start() + 1] if end else span
        toks = list(BACKTICK.finditer(span))
        if not toks or toks[0].group(1).strip() != keys[0] or toks[0].start() > 60:
            continue
        pos, ends = 0, []
        for k in keys:
            while pos < len(toks) and toks[pos].group(1).strip() != k:
                pos += 1
            if pos == len(toks):
                break
            ends.append(toks[pos].end())
            pos += 1
        if len(ends) != len(keys):
            continue
        lead = span[:toks[0].start()]
        after = span[ends[-1]: ends[-1] + 20]
        if ORDER_PHRASE.search(lead) or re.match(r"^[\s,;)]{0,3}(?:" + ORDER_PHRASE.pattern + ")", after, re.I):
            return text[m.start(): m.end() + ends[-1] + (len(after) if ORDER_PHRASE.search(after) else 0)][:300]
    return None


def rule_key_order(rel: str, tree, scope: Scope, instr: str, shipped: tuple = ([], [])) -> tuple[list, list]:
    """B4: the keys of an object compared in order (list(obj) == KEYS) where instruction.md does not order them. Only
    an object counts: a list compared to a list is an array in order, a CSV header is column order (unless the
    instruction calls those names keys)."""
    out, ordered = [], []
    seen = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Compare) and len(node.ops) == 1 and isinstance(node.ops[0], (ast.Eq, ast.NotEq))):
            continue
        for obj_side, keys_side in ((node.left, node.comparators[0]), (node.comparators[0], node.left)):
            obj, keys_call = _ordered_obj(obj_side)
            if obj is None or kind_of(obj, scope, node) in ("own", "harness"):
                continue
            for keys in _keys_lists(keys_side, scope, node):
                if len(keys) < 2 or (node.lineno, tuple(keys)) in seen:
                    continue
                seen.add((node.lineno, tuple(keys)))
                quote = instruction_orders(instr, keys)
                if quote:
                    ordered.append((rel, node.lineno, keys, quote))
                    continue
                if key_order_shape(obj, keys_call, keys, scope, node, instr, shipped) != "dict":
                    continue
                out.append((rel, node.lineno, "B4",
                            "requires the keys %s in this order, but instruction.md does not order them (no \"in "
                            "this order\" at their list): an output with the same keys in another order fails. Compare "
                            "them unordered with tb4judge.keys(obj, KEYS, ordered=False), or state the order in "
                            "instruction.md" % ", ".join(keys)))
    return out, ordered


# ------------------------------------------------------------------ B5 the test runner's exit status ignored

def _argv_text(expr, scope: Scope, at) -> str:
    ids, strs = resolve(expr, scope, at)
    return " ".join(sorted(strs) + sorted(ids))


def _argv_words(expr, scope: Scope, at, depth: int = 0) -> list:
    """The words of a command in their order: a list or tuple literal, a string (split on spaces), a name bound to one
    (its latest assignment before AT), list or string concatenation, an f-string's literal parts, or the arguments of
    a call (shlex.split("...")). A word that is not a string literal is its name."""
    if depth > 5:
        return []
    if isinstance(expr, (ast.List, ast.Tuple)):
        out = []
        for e in expr.elts:
            out += _argv_words(e.value if isinstance(e, ast.Starred) else e, scope, at, depth + 1)
        return out
    if isinstance(expr, ast.Constant):
        return expr.value.split() if isinstance(expr.value, str) else []
    if isinstance(expr, ast.JoinedStr):
        return " ".join(v.value if isinstance(v, ast.Constant) else " " for v in expr.values
                        if isinstance(v, (ast.Constant, ast.FormattedValue))).split()
    if isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add):
        return _argv_words(expr.left, scope, at, depth + 1) + _argv_words(expr.right, scope, at, depth + 1)
    if isinstance(expr, ast.Name):
        found = scope.lookup(expr.id, at)
        return _argv_words(found[-1][1], scope, at, depth + 1) if found else [expr.id]
    if isinstance(expr, ast.Attribute):
        return [expr.attr]
    if isinstance(expr, ast.Call):
        out = []
        for a in expr.args:
            out += _argv_words(a, scope, at, depth + 1)
        return out
    return []


def test_command(expr, scope: Scope, at) -> str | None:
    """The test command EXPR runs ("jest", "npm test", "cargo test"), or None for anything else (an install, a
    build, a script that is not a test runner)."""
    text = " " + " ".join(_argv_words(expr, scope, at)) + " "
    m = TEST_RUNNER_RE.search(text) or TOOL_TEST_RE.search(text)
    if m:
        return m.group(1) if m.re is TEST_RUNNER_RE else re.sub(r"\s+", " ", m.group(0).strip())
    loose = _argv_text(expr, scope, at)               # an argv built in pieces: the words in any order
    m = TEST_RUNNER_RE.search(" " + loose + " ")
    if m:
        return m.group(1)
    words = set(loose.split())
    for tool, tests in TOOL_TEST_WORDS.items():
        if tool in words and words & tests:
            return "%s %s" % (tool, sorted(words & tests)[0])
    return None


def rule_runner_rc_py(rel: str, tree, scope: Scope) -> list:
    out = []
    parents = {}
    for p in ast.walk(tree):
        for c in ast.iter_child_nodes(p):
            parents[id(c)] = p
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess"
                and node.func.attr in ("run", "call", "Popen") and node.args):
            continue
        runner = test_command(node.args[0], scope, node)
        if not runner:
            continue
        check = _kw(node, "check")
        if isinstance(check, ast.Constant) and check.value is True:
            continue
        parent = parents.get(id(node))
        used = False
        if isinstance(parent, (ast.Assign, ast.AnnAssign, ast.withitem, ast.NamedExpr)):
            targets = parent.targets if isinstance(parent, ast.Assign) else [getattr(parent, "target", None)
                                                                             or getattr(parent, "optional_vars", None)]
            names = {t.id for t in targets if isinstance(t, ast.Name)}
            fn = scope.func_of(node) or tree
            for n in ast.walk(fn):
                if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id in names \
                        and n.attr in ("returncode", "wait", "poll", "check_returncode", "communicate"):
                    used = True
        elif not isinstance(parent, ast.Expr):
            used = True                       # passed on or returned: its caller may read it
        if used:
            continue
        out.append((rel, node.lineno, "B5",
                    "runs the repository's tests (%s) and never reads the exit status: a suite that fails after its "
                    "assertions pass (a teardown error, a crash at exit, a suite Jest marks failed) still counts as "
                    "passing. Fail it unless the exit status is the expected one, and put the status in the "
                    "observation" % runner))
    return out


def rule_runner_rc_sh(rel: str, sh: str, has_suite: bool) -> list:
    if not has_suite:
        return []
    out = []
    lines = sh.split("\n")
    for i, ln in enumerate(lines):
        code = ln.split("#", 1)[0]
        if "SUITE_CMD[@]" not in code or "mapfile" in code or "readarray" in code:
            continue
        if re.search(r"\$\?|PIPESTATUS|\|\||\bif\b|&&\s*\w+=", code):
            continue
        nxt = next((l.split("#", 1)[0].strip() for l in lines[i + 1:] if l.split("#", 1)[0].strip()), "")
        if re.search(r"\$\?|PIPESTATUS", nxt):
            continue
        out.append((rel, i + 1, "B5",
                    "runs the repository suite and never captures its exit status (no $? after this line): the "
                    "verdict reads only the printed PASSED/FAILED lines, so a suite that crashes or errors at exit "
                    "after printing them passes. Capture the status and fail unless it is the expected one (pytest: "
                    "1 with the canary as the only failure; Jest: no failed suite but the canary's)"))
    return out


# ------------------------------------------------------------------ B6 a converting default on the code's own objects

# json.dumps never calls default= for a JSON type (dict, list, tuple, str, int, float, bool, None, or a subclass of
# one): a tuple is written as a list with or without it. default= decides only what happens to any other object.
# repr names the type (Decimal('1.5'), PosixPath('/a'), {1, 2}, <Foo object at 0x...>), so the judge sees a string
# it rejects: nothing is hidden. A converting default turns an object the code under test returned into a JSON value
# the instruction may ask for, so a wrong type passes.
SAFE_DEFAULTS = ("repr",)
CONVERTS = {"str": "a Decimal, UUID, Path, date or enum becomes its text, so it passes where a string is asked for",
            "float": "a Decimal or a numpy number becomes a JSON number", "int": "a Decimal or a numpy number becomes "
            "a JSON number", "list": "a set or another iterable becomes a list", "sorted": "a set becomes a list",
            "tuple": "a set or another iterable becomes a list", "dict": "an object becomes a dict",
            "vars": "an object becomes a dict of its attributes", "asdict": "a dataclass becomes a dict",
            "isoformat": "a date becomes its ISO text, so it passes where a string is asked for",
            "tolist": "a numpy array becomes a list", "item": "a numpy scalar becomes a JSON number",
            "__dict__": "an object becomes a dict of its attributes"}
# what loads code at run time: a case that imports the submission, or a helper that does
LOADS_CODE = ("import_module", "__import__", "spec_from_file_location", "module_from_spec", "exec_module", "run_path",
              "run_module", "exec", "load_module", "load_source")
# libraries an emitter imports for its own work: their objects are the emitter's, not the submission's
EMITTER_LIBS = {"numpy", "pandas", "scipy", "yaml", "requests", "pytest", "_pytest", "jsonschema", "dateutil", "pytz",
                "toml", "tomli", "lxml", "bs4", "PIL", "psutil", "packaging", "simplejson", "ujson", "orjson",
                "regex", "chardet", "tb4judge"}


def _call_name(node) -> str:
    f = node.func
    return f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""


def _converting_default(d, funcs: dict) -> str | None:
    """What a default= converts (a CONVERTS key, or "" for a function that returns some other value), or None for
    repr (and a lambda or function that returns repr(...) only)."""
    if isinstance(d, ast.Name) and d.id in SAFE_DEFAULTS:
        return None
    body = None
    if isinstance(d, ast.Lambda):
        body = [d.body]
    elif isinstance(d, ast.Name) and d.id in funcs:
        body = [r.value for r in ast.walk(funcs[d.id]) if isinstance(r, ast.Return) and r.value is not None]
    if body is None:
        name = d.id if isinstance(d, ast.Name) else d.attr if isinstance(d, ast.Attribute) else ""
        return name if name in CONVERTS else ""
    if body and all(isinstance(b, ast.Call) and _call_name(b) in SAFE_DEFAULTS for b in body):
        return None
    for b in body:
        for n in ast.walk(b):
            if isinstance(n, ast.Call) and _call_name(n) in CONVERTS:
                return _call_name(n)
            if isinstance(n, ast.Attribute) and n.attr in CONVERTS:
                return n.attr
    return ""


def submitted_code_reach(tree, local: set) -> tuple[set, bool]:
    """(the functions that run submitted code, whether the module's own statements do). A function runs it when it
    loads code (importlib, runpy, exec, or an import of a module that is neither the standard library nor one of
    tests/*.py), uses a module the file imported that way, calls a function that does, or calls a case through a
    table of functions (CASES[name]())."""
    stdlib = set(getattr(sys, "stdlib_module_names", ())) | {"__future__"}
    # the graded package the template names (TARGET_MODULE = "pkg.mod") is submitted code even when it is a library
    # an emitter could also use for itself
    target = {n.value.value.split(".")[0] for n in tree.body if isinstance(n, ast.Assign)
              and isinstance(n.value, ast.Constant) and isinstance(n.value.value, str)
              and any(isinstance(t, ast.Name) and t.id == "TARGET_MODULE" for t in n.targets)}

    def foreign(module: str | None) -> bool:
        top_name = (module or "").split(".")[0]
        return bool(top_name) and top_name not in stdlib | local and (top_name not in EMITTER_LIBS
                                                                        or top_name in target)

    def loads(nodes) -> bool:
        for n in nodes:
            if isinstance(n, ast.Call) and _call_name(n) in LOADS_CODE:
                return True
            if isinstance(n, ast.Import) and any(foreign(a.name) for a in n.names):
                return True
            if isinstance(n, ast.ImportFrom) and not n.level and foreign(n.module):
                return True
        return False

    top = [n for stmt in tree.body if not isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
           for n in ast.walk(stmt)]
    # the names the module's own imports of submitted code bind (sys.path.insert(0, OUT); import solution)
    imported = set()
    for n in top:
        if isinstance(n, ast.Import):
            imported |= {(a.asname or a.name).split(".")[0] for a in n.names if foreign(a.name)}
        elif isinstance(n, ast.ImportFrom) and not n.level and foreign(n.module):
            imported |= {a.asname or a.name for a in n.names}
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    # NAME = {"case": func or lambda, ...}: a table of cases, called as NAME[case]()
    tables = {}
    for n in tree.body:
        if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict):
            for t in n.targets:
                if isinstance(t, ast.Name):
                    tables[t.id] = n.value.values

    def direct(nodes) -> bool:
        nodes = list(nodes)
        return loads(nodes) or any(isinstance(x, ast.Name) and x.id in imported for x in nodes)

    reach = {name for name, f in funcs.items() if direct(ast.walk(f))}

    def table_runs(values) -> bool:
        for v in values:
            if isinstance(v, ast.Name) and v.id in reach:
                return True
            if isinstance(v, ast.Lambda) and (direct(ast.walk(v.body)) or any(
                    isinstance(c, ast.Call) and isinstance(c.func, ast.Name) and c.func.id in reach
                    for c in ast.walk(v.body))):
                return True
        return False

    changed = True
    while changed:
        changed = False
        for name, f in funcs.items():
            if name in reach:
                continue
            for n in ast.walk(f):
                if not isinstance(n, ast.Call):
                    continue
                callee = n.func.id if isinstance(n.func, ast.Name) else None
                via = n.func.value.id if isinstance(n.func, ast.Subscript) and isinstance(n.func.value, ast.Name) \
                    else None
                if callee in reach or (via in tables and table_runs(tables[via])):
                    reach.add(name)
                    changed = True
                    break
    module_runs = direct(top) or any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in reach
                                     for n in top)
    return {funcs[n] for n in reach}, module_runs


def rule_repr_fallback(rel: str, tree, local: set = frozenset()) -> list:
    """B6: json.dump(s) with a converting default (str, float, list, vars, a function that returns a value) where the
    value can hold the objects the code under test returned: in a function that runs submitted code (or calls one
    that does). default=repr, and the parent that only re-prints what a case process wrote as JSON, are not
    findings."""
    out = []
    funcs = {n.name: n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    reach, module_runs = submitted_code_reach(tree, set(local))
    owner = {}
    for f in funcs.values():
        for sub in ast.walk(f):
            if sub is not f:
                owner.setdefault(id(sub), f)
    for node in ast.walk(tree):
        if not _is_json_call(node, ("dumps", "dump")):
            continue
        d = _kw(node, "default")
        if d is None:
            continue
        what = _converting_default(d, funcs)
        if what is None:
            continue
        f = owner.get(id(node))
        if not (f in reach if f is not None else module_runs):
            continue
        name = d.id if isinstance(d, ast.Name) else "a lambda" if isinstance(d, ast.Lambda) else \
            d.attr if isinstance(d, ast.Attribute) else "a function"
        out.append((rel, node.lineno, "B6",
                    "serializes what the code under test returned with json.%s(default=%s): %s, so the judge sees "
                    "the type the instruction asks for even when the code returned another. Drop the default and fail "
                    "the case on a non-JSON type (template v2.1 emit.py, plain())"
                    % (node.func.attr, name, CONVERTS.get(what) or "any other object becomes what that function "
                       "returns")))
    return out


# ------------------------------------------------------------------ B7 project files in test_globs

def rule_test_globs(task: Path, rel: str, text: str, instr: str) -> tuple[list, list]:
    """(findings, warnings): a project manifest in test_globs that instruction.md does not freeze is a finding; a
    Python manifest (pyproject.toml, setup.cfg, setup.py) that usually also carries the test runner's configuration
    is a warning."""
    try:
        doc = json.loads(text)
    except ValueError:
        return [], []
    globs = doc.get("test_globs") if isinstance(doc, dict) else None
    out, warns = [], []
    for g in globs or []:
        if not isinstance(g, str):
            continue
        base = g.rstrip("/").split("/")[-1]
        manifest, test_config = bool(MANIFESTS.match(base)), bool(TEST_CONFIG_MANIFESTS.match(base))
        if not (manifest or test_config):
            continue
        frozen = False
        for sent in re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", instr)):
            if base in sent and FREEZE_WORDS.search(sent):
                frozen = True
                break
        if frozen:
            continue
        line = next((i + 1 for i, ln in enumerate(text.split("\n")) if json.dumps(g) in ln), 1)
        if test_config:
            warns.append((rel, line, "B7", "lists %s in test_globs: the agent's edits to it are discarded. It usually "
                          "holds the test runner's configuration too; check that a repair never needs to change "
                          "anything else in it" % g))
            continue
        out.append((rel, line, "B7",
                    "lists %s in test_globs, so the verifier discards every change the agent makes to it (applied "
                    "with --exclude, then restored from the pristine tree), although instruction.md does not freeze "
                    "it: a repair that legitimately edits %s fails. Remove it from test_globs, or say in "
                    "instruction.md that it must not change" % (g, base)))
    return out, warns


# ------------------------------------------------------------------ B8 cases and inputs not isolated

CASE_DIR = re.compile(r"\$\{?VW\}?/(?:harness/)?([A-Za-z_]*(?:case|incident|lake|storefront|site|store|well|"
                      r"plant|month|folder)s?)\b", re.I)


# the root judge's own command (pytest on tests/test_outputs.py): its environment is never the program's
JUDGE_CMD = re.compile(r"\bpytest\b|\btest_outputs\.py\b")


def _command_at(lines: list, i: int) -> str:
    """The shell command line I belongs to, its backslash continuations joined (comments dropped)."""
    j = i
    while j > 0 and lines[j - 1].split("#", 1)[0].rstrip().endswith("\\"):
        j -= 1
    parts = []
    while j < len(lines):
        code = lines[j].split("#", 1)[0].rstrip()
        parts.append(code.rstrip("\\"))
        if not code.endswith("\\"):
            break
        j += 1
    return " ".join(parts)


def rule_isolation(task: Path, rel: str, sh: str, emit_text: str) -> list:
    out = []
    lines = sh.split("\n")
    per_case = bool(re.search(r"--case\b|case_dir|for\s+\w+\s+in\s+.*(?:CASES|cases)|iterdir\(\)|os\.listdir|"
                              r"sorted\(os\.listdir", emit_text))
    runner_cases = False             # TB4_CASES handed to something other than the judge (the runner, the emitter)
    for i, ln in enumerate(lines):
        code = ln.split("#", 1)[0]
        m = re.search(r"\bTB4_CASES=(\S+)", code)
        if m and JUDGE_CMD.search(_command_at(lines, i)):
            continue                 # the judge's pytest reads the cases; the program never gets this environment
        runner_cases = runner_cases or bool(m)
        if m and per_case:
            out.append((rel, i + 1, "B8",
                        "hands the program's environment TB4_CASES=%s, the folder of every graded case: a run for one "
                        "case can read the other cases' inputs. Stage one case per run and keep the cases folder out "
                        "of the program's environment" % m.group(1).strip("\"'")))
    staged = {}
    for i, ln in enumerate(lines):
        code = ln.split("#", 1)[0]
        if re.search(r"\b(?:cp|tar|install|rsync|mv)\b", code):
            for m in CASE_DIR.finditer(code):
                staged.setdefault(m.group(1), m.group(0).replace("${VW}", "$VW"))
    for i, ln in enumerate(lines):
        code = ln.split("#", 1)[0]
        for name, where in staged.items():
            if not re.search(r"\$\{?VW\}?/(?:harness/)?" + re.escape(name) + r"\b", code):
                continue
            name = where[len("$VW/"):] if where.startswith("$VW/") else where
            if re.search(r"\bchown\b[^;&|]*\$\{?RUNNER_UID\}?|chown\b[^;&|]*\brunner\b", code):
                out.append((rel, i + 1, "B8",
                            "gives the runner ownership of the staged inputs ($VW/%s): a program can write into them "
                            "and restore the bytes before any check, and nothing sees it. Stage the inputs root:root "
                            "a+rX,go-w so any write fails" % name))
            elif re.search(r"\bchmod\b[^;&|]*(?:a\+w|o\+w|go\+w|\b777\b|\b666\b)", code):
                out.append((rel, i + 1, "B8",
                            "makes the staged inputs ($VW/%s) writable for everyone: a program can change them. Stage "
                            "them root:root a+rX,go-w" % name))
            elif per_case and re.search(r"\bchmod\b[^;&|]*(?:a\+rX|go=rX|a\+r\b|o\+r|755|644)", code) \
                    and runner_cases:
                out.append((rel, i + 1, "B8",
                            "stages every graded case in one folder the runner can read ($VW/%s) and runs the program "
                            "once per case: a run for one case can read the other cases' inputs. Stage one case per "
                            "run (copy in, run, kill the runner, remove)" % name))
    return out


# ------------------------------------------------------------------ B9 lossy idioms in the emitter (advisory)

def rule_lossy(rel: str, tree) -> list:
    """Advisory: idioms by which an emitter (or a helper it imports) drops what it observes. Each is a place to check
    by hand, never a finding: a set or a sort is often harmless."""
    out = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            a = node.func.attr
            recv = node.func.value
            if a == "strip" and isinstance(recv, ast.Call) and isinstance(recv.func, ast.Attribute) \
                    and recv.func.attr in ("read", "read_text", "decode"):
                out.append((rel, node.lineno, "B9", "strips what it read before observing it: whitespace and "
                            "newline changes become invisible (observe the raw value or its sha256)"))
            elif a in ("lower", "casefold"):
                out.append((rel, node.lineno, "B9", "folds case before observing: a value in the wrong case "
                            "becomes invisible"))
            elif a == "join" and node.args and isinstance(node.args[0], ast.Call) \
                    and isinstance(node.args[0].func, ast.Attribute) and node.args[0].func.attr == "split" \
                    and not node.args[0].args:
                out.append((rel, node.lineno, "B9", "collapses whitespace before observing: spacing changes become "
                            "invisible"))
            elif a == "sub" and isinstance(recv, ast.Name) and recv.id == "re" and node.args \
                    and isinstance(node.args[0], ast.Constant) and str(node.args[0].value) in (r"\s+", r"\s*"):
                out.append((rel, node.lineno, "B9", "collapses whitespace before observing: spacing changes become "
                            "invisible"))
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == "re" \
                and node.attr in ("I", "IGNORECASE"):
            out.append((rel, node.lineno, "B9", "matches case-insensitively: a value in the wrong case is observed "
                        "as the right one"))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "set":
            out.append((rel, node.lineno, "B9", "collects observed items in a set: repeats and order become "
                        "invisible (observe a list)"))
        elif isinstance(node, ast.SetComp):
            out.append((rel, node.lineno, "B9", "collects observed items in a set: repeats and order become "
                        "invisible (observe a list)"))
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sorted":
            out.append((rel, node.lineno, "B9", "sorts observed items: an output in the wrong order is observed as "
                        "the right one (when order is part of the contract)"))
    return sorted(set(out), key=lambda w: w[1])[:12]


# ------------------------------------------------------------------ B10 an item no pattern reads is dropped

MATCH_ATTRS = ("match", "fullmatch", "search")
FAIL_CALLS = ("fail", "exit", "abort")


def _is_match_call(node) -> bool:
    return isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in MATCH_ATTRS


def _match_names(stmts) -> set:
    """Names bound to a regex match in STMTS (m = pat.match(s), (m := pat.match(s)))."""
    out = set()
    for st in stmts:
        for n in ast.walk(st):
            if isinstance(n, ast.Assign) and _is_match_call(n.value):
                out |= {t.id for t in n.targets if isinstance(t, ast.Name)}
            elif isinstance(n, ast.NamedExpr) and _is_match_call(n.value):
                out.add(n.target.id)
    return out


def _matched(test, names) -> bool:
    """TEST holds when a regex matched: `m`, `pat.match(s)`, `(m := ...)`, `m is not None`, `x and m`."""
    if isinstance(test, ast.Name):
        return test.id in names
    if _is_match_call(test) or (isinstance(test, ast.NamedExpr) and _is_match_call(test.value)):
        return True
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.IsNot) \
            and isinstance(test.comparators[0], ast.Constant) and test.comparators[0].value is None:
        return _matched(test.left, names)
    if isinstance(test, ast.BoolOp) and isinstance(test.op, ast.And):
        return any(_matched(v, names) for v in test.values)
    return False


def _unmatched(test, names) -> bool:
    """TEST holds when a regex did not match: `not m`, `not pat.match(s)`, `m is None`."""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return _matched(test.operand, names)
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Is) \
            and isinstance(test.comparators[0], ast.Constant) and test.comparators[0].value is None:
        return _matched(test.left, names)
    return False


def _harness_pattern(node, scope: Scope) -> bool:
    """A match against the harness's own protocol (a TB4-OBS / TB4-LINT line): never a deliverable's content."""
    calls = [n for n in ast.walk(node) if _is_match_call(n)]
    for c in calls:
        _, strs = resolve(c, scope, c)
        if any("TB4-" in s for s in strs):
            return True
    return False


def _checked_after(stmts, names: set) -> bool:
    """A statement in STMTS that fails, or tests a name the match branch set (found = ...; if not found: ...)."""
    for st in stmts:
        for n in ast.walk(st):
            if isinstance(n, (ast.Raise, ast.Assert)):
                return True
            if isinstance(n, ast.Call) and _call_name(n) in FAIL_CALLS:
                return True
            if isinstance(n, (ast.If, ast.While, ast.IfExp)) and \
                    names & {x.id for x in ast.walk(n.test) if isinstance(x, ast.Name)}:
                return True
    return False


def _positive_match(expr, targets: set) -> bool:
    """EXPR (a comprehension's condition) keeps an item only when a regex matches it (not under a `not`)."""
    if isinstance(expr, ast.UnaryOp) and isinstance(expr.op, ast.Not):
        return False
    if isinstance(expr, ast.BoolOp):
        return any(_positive_match(v, targets) for v in expr.values)
    if isinstance(expr, ast.Compare) and len(expr.ops) == 1 and isinstance(expr.ops[0], ast.IsNot):
        return _positive_match(expr.left, targets)
    if _is_match_call(expr):
        used = {n.id for a in list(expr.args) + [expr.func.value] for n in ast.walk(a) if isinstance(n, ast.Name)}
        return bool(used & targets)
    return False


def rule_silent_drop(rel: str, tree, scope: Scope, emitter: bool) -> list:
    """B10: a parse or emit step that drops an item no pattern reads, with no error and no record of it."""
    out = []
    parents = {}
    for p in ast.walk(tree):
        for field, value in ast.iter_fields(p):
            if isinstance(value, list):
                for c in value:
                    if isinstance(c, ast.AST):
                        parents[id(c)] = (p, value)
    loops = (ast.For, ast.AsyncFor, ast.While)

    def in_loop(node):
        p = parents.get(id(node))
        while p is not None:
            if isinstance(p[0], loops):
                return p[0]
            if isinstance(p[0], (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                return None
            p = parents.get(id(p[0]))
        return None

    def ours(loop) -> bool:
        it = getattr(loop, "iter", None)
        return it is None or kind_of(it, scope, loop) not in ("own", "harness")

    for node in ast.walk(tree):
        # an inner loop over patterns: `for pat, fn in PATTERNS: m = pat.match(s); if m: ...; break`, no else
        if isinstance(node, (ast.For, ast.AsyncFor)) and not node.orelse:
            outer = in_loop(node)
            names = _match_names(node.body)
            branch = next((st for st in node.body if isinstance(st, ast.If) and _matched(st.test, names)
                           and any(isinstance(b, ast.Break) for b in st.body)), None)
            if outer is None or branch is None or _harness_pattern(node, scope) or not ours(outer):
                continue
            set_in_branch = {t.id for b in branch.body for n in ast.walk(b) if isinstance(n, ast.Assign)
                             for t in n.targets if isinstance(t, ast.Name)}
            block = parents.get(id(node), (None, []))[1]
            after = block[block.index(node) + 1:] if node in block else []
            if _checked_after(after, set_in_branch):
                continue
            out.append((rel, node.lineno, "B10",
                        "an item that no pattern in this loop matches falls through with no fact, no error and no "
                        "record: a wrong extra item (a contradictory sentence or field beside the right ones) is "
                        "dropped and the judge never sees it. Fail the case on an item no pattern reads (for ... "
                        "else: raise), or collect such items where the judge requires none"))
        # an explicit skip: `m = PAT.match(line); if not m: continue`
        elif isinstance(node, ast.If) and len(node.body) == 1 and isinstance(node.body[0], ast.Continue):
            loop = in_loop(node)
            if loop is None:
                continue
            names = _match_names(loop.body)
            if not _unmatched(node.test, names) or not ours(loop):
                continue
            if _harness_pattern(node.test, scope) or any(
                    _harness_pattern(st, scope) for st in loop.body if isinstance(st, ast.Assign)
                    and {t.id for t in st.targets if isinstance(t, ast.Name)} & names):
                continue
            out.append((rel, node.lineno, "B10",
                        "skips an item no pattern matches (`continue`): a wrong extra line or field beside the right "
                        "ones is dropped without an error and the judge never sees it. Fail on an item that cannot be "
                        "read, or collect it where the judge requires none"))
        # an emitter that keeps only what a pattern matches: `[r for r in remarks if GRADED.match(r)]`
        elif emitter and isinstance(node, (ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)):
            for gen in node.generators:
                targets = {n.id for n in ast.walk(gen.target) if isinstance(n, ast.Name)}
                if any(_positive_match(c, targets) for c in gen.ifs) and not _harness_pattern(gen, scope) \
                        and kind_of(gen.iter, scope, node) not in ("own", "harness"):
                    out.append((rel, node.lineno, "B10",
                                "keeps only the items a pattern matches before observing them: an item of another "
                                "kind (a wrong extra sentence beside the right ones) is discarded, so the judge "
                                "never sees it. Observe every item and let the judge fail what it does not read, or "
                                "observe the discarded items in a field the judge requires empty"))
                    break
    return out


# ------------------------------------------------------------------ B11 a stream cap read from the final file size

SIZE_ATTRS = {"getsize", "st_size"}
CAP_NAME = re.compile(r"MAX|CAP|LIMIT", re.I)
SUBPROCESS_CALLS = ("Popen", "run", "call", "check_call", "check_output")
_SIZE = r"at most\s+[\d,.]+\s*(?:bytes?|[KMG]i?B)\b"
STREAM_CAP_SAID = re.compile(r"\b(?:stdout|standard output|stderr|standard error|print(?:s|ing)?)\b[^.\n]{0,80}?\b%s"
                             r"|\b%s[^.\n]{0,40}?\b(?:stdout|standard output|stderr|standard error)\b" % (_SIZE, _SIZE),
                             re.I)
FILE_OPENERS = ("open", "TemporaryFile", "NamedTemporaryFile", "SpooledTemporaryFile", "fdopen", "mkstemp")


def rule_stream_cap(rel: str, tree, scope: Scope, instr: str) -> list:
    """B11: the program's stdout or stderr goes to a file and its size is checked against a cap after the run. Only
    where instruction.md states the cap: otherwise it is the harness's own guard and an evasion breaks no promise."""
    if not STREAM_CAP_SAID.search(instr):
        return []
    out = []
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        streams = {}
        for n in ast.walk(fn):
            if isinstance(n, ast.Call) and _call_name(n) in SUBPROCESS_CALLS:
                for k in n.keywords:
                    if k.arg in ("stdout", "stderr") and isinstance(k.value, ast.Name) and any(
                            isinstance(v, ast.Call) and _call_name(v) in FILE_OPENERS
                            for _, v in scope.lookup(k.value.id, n)):
                        streams.setdefault(k.arg, k.value.id)
        if not streams:
            continue
        for n in ast.walk(fn):
            if not (isinstance(n, ast.Compare) and len(n.ops) == 1
                    and isinstance(n.ops[0], (ast.Lt, ast.LtE, ast.Gt, ast.GtE))):
                continue
            sides = [n.left, n.comparators[0]]
            measured = [s for s in sides if SIZE_ATTRS & resolve(s, scope, n)[0]]
            capped = [s for s in sides if s not in measured and (
                any(CAP_NAME.search(i) for i in resolve(s, scope, n)[0])
                or (isinstance(s, ast.Constant) and isinstance(s.value, int) and s.value >= 1024))]
            if measured and capped:
                out.append((rel, n.lineno, "B11",
                            "checks the program's %s against its cap by the size of the file it was written to, "
                            "after the run: a program can write past the cap, seek back and truncate, and the final "
                            "size passes. Read stdout and stderr through pipes and count every byte as it arrives "
                            "(template v2.1 tests/emit.py run())" % " and ".join(sorted(streams))))
                break
    return out


# ------------------------------------------------------------------ B12 an unchanged check that hashes no file mode

WALK_ATTRS = {"walk", "rglob", "glob", "listdir", "iterdir", "scandir"}
HASH_ATTRS = {"sha256", "sha1", "md5", "blake2b", "blake2s", "sha512", "new", "file_digest"}
MODE_ATTRS = {"st_mode", "S_IMODE", "filemode", "X_OK", "W_OK", "S_IXUSR"}


def rule_tree_hash(rel: str, tree, scope: Scope, instr: str) -> list:
    """B12: a function that hashes a tree's paths and contents for an `unchanged` check without any file mode, where
    instruction.md promises the inputs stay unchanged."""
    if not PROTECT_WORDS.search(instr):
        return []
    out = []
    compared = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Compare) and any(isinstance(o, (ast.Eq, ast.NotEq)) for o in n.ops):
            compared.append(n)
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        attrs = {n.attr for n in ast.walk(fn) if isinstance(n, ast.Attribute)}
        hashes = any(isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name) and n.value.id == "hashlib"
                     and n.attr in HASH_ATTRS for n in ast.walk(fn))
        reads = attrs & {"read", "read_bytes", "read_text"} or any(
            isinstance(n, ast.Call) and _call_name(n) == "open" for n in ast.walk(fn))
        if not (attrs & WALK_ATTRS and hashes and reads) or attrs & MODE_ATTRS:
            continue
        if not any(fn.name in resolve(side, scope, c)[0] for c in compared for side in [c.left] + c.comparators):
            continue
        out.append((rel, fn.lineno, "B12",
                    "%s() hashes a tree's paths and contents for an unchanged check but no file mode: a program can "
                    "change an input's permissions (0644 to 0600, or add +x) and the check still matches. Hash each "
                    "entry's mode too (os.lstat(p).st_mode), as template v2.1's per-case input check compares paths, "
                    "modes, links and contents" % fn.name))
    return out


# ------------------------------------------------------------------ B13 a JSON value compared with == alone

TYPE_FREE_CALLS = {"int", "float", "str", "len", "round", "sorted", "set", "frozenset", "tuple", "list", "abs",
                   "Decimal", "bool", "repr", "sum", "min", "max", "dumps", "type", "isinstance", "same",
                   "difference", "keys", "within"}
ANSWER_FILE = re.compile(r"expected|answer|truth|golden", re.I)


def _has_bool(doc) -> bool:
    stack = [doc]
    while stack:
        x = stack.pop()
        if isinstance(x, bool):
            return True
        if isinstance(x, dict):
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
    return False


def answer_bools(task: Path) -> list:
    """[(path, document, member names)] of the task's own answer files (tests/expected.json, ...) that hold a boolean."""
    tests = task / "tests"
    out = []
    for p in sorted(tests.rglob("*.json")):
        rel = p.relative_to(tests)
        if len(rel.parts) > 3 or not ANSWER_FILE.search(p.name) or p.stat().st_size > 20_000_000:
            continue
        try:
            doc = json.loads(p.read_text(encoding="utf-8", errors="replace"))
        except ValueError:
            continue
        if _has_bool(doc):
            out.append((_rel(task, p), doc, _keys_of(doc)))
    return out


def _bool_members(doc) -> set:
    """The member names in DOC that hold a boolean (directly, or a list of them)."""
    out, stack = set(), [doc]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            for k, v in x.items():
                if isinstance(v, bool) or (isinstance(v, list) and any(isinstance(y, bool) for y in v)):
                    out.add(k)
                stack.append(v)
        elif isinstance(x, list):
            stack.extend(x)
    return out


def _bool_under(doc, keys: set, typed: set = frozenset()) -> bool:
    """A boolean under the innermost of KEYS that is compared (want["reports"][case]["sql"]: under sql, not
    anywhere in reports); with no KEYS (the whole value is compared), anywhere in DOC. A member the emitter computes
    as a real boolean itself (TYPED: inbox.empty(), a comparison) cannot come back as 0/1 and does not count."""
    if not keys:
        return bool(_bool_members(doc) - typed) or (isinstance(doc, list) and _has_bool(doc) and not typed)
    values: dict = {}
    stack = [doc]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            for k, v in x.items():
                if k in keys:
                    values.setdefault(k, []).append(v)
                stack.append(v)
        elif isinstance(x, list):
            stack.extend(x)
    inner = [k for k in values if not any(keys - {k} & _keys_of(v) for v in values[k])]
    return any(isinstance(v, bool) and k not in typed or bool(_bool_members(v) - typed)
               for k in inner for v in values[k])


BOOL_CALLS = {"bool", "isinstance", "issubclass", "callable", "hasattr", "any", "all", "exists", "isfile", "isdir",
              "islink", "is_file", "is_dir", "is_symlink", "empty", "startswith", "endswith", "isdigit", "is_alive",
              "done", "cancelled", "issubset", "issuperset", "isdisjoint"}


def _bool_expr(v) -> bool:
    """V is always a real boolean: a comparison, a `not`, a predicate call (bool(), inbox.empty(), ...), True/False."""
    if isinstance(v, ast.Constant):
        return isinstance(v.value, bool)
    if isinstance(v, (ast.Compare,)) or (isinstance(v, ast.UnaryOp) and isinstance(v.op, ast.Not)):
        return True
    if isinstance(v, ast.BoolOp):
        return all(_bool_expr(x) for x in v.values)
    return isinstance(v, ast.Call) and _call_name(v) in BOOL_CALLS


def typed_bool_members(trees) -> set:
    """Member names the emitter fills with a real boolean of its own ({"inbox_empty": inbox.empty()})."""
    out = set()
    for tree in trees:
        for n in ast.walk(tree):
            if isinstance(n, ast.Dict):
                out |= {k.value for k, v in zip(n.keys, n.values) if isinstance(k, ast.Constant)
                        and isinstance(k.value, str) and _bool_expr(v)}
            elif isinstance(n, ast.Call) and _call_name(n) == "dict":
                out |= {k.arg for k in n.keywords if k.arg and _bool_expr(k.value)}
            elif isinstance(n, ast.Assign) and _bool_expr(n.value):
                out |= {t.slice.value for t in n.targets if isinstance(t, ast.Subscript)
                        and isinstance(t.slice, ast.Constant) and isinstance(t.slice.value, str)}
    return out


def _keys_of(doc) -> set:
    out, stack = set(), [doc]
    while stack:
        x = stack.pop()
        if isinstance(x, dict):
            out |= set(x)
            stack.extend(x.values())
        elif isinstance(x, list):
            stack.extend(x)
    return out


def _fails(body) -> bool:
    return any(isinstance(st, ast.Raise) or (isinstance(st, ast.Expr) and isinstance(st.value, ast.Call)
                                             and _call_name(st.value) in FAIL_CALLS) for st in body)


def rule_type_equality(rel: str, tree, scope: Scope, answers: list, typed: set = frozenset()) -> list:
    """B13: the judge decides with `got == want` (or `!=` then fail), which counts true as 1 and false as 0. Only
    where the answer holds a boolean under what is compared (want["early"]: the member early), or anywhere when the
    whole value is compared."""
    if not answers:
        return []
    lines, bools_in = [], ""
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            test, op = node.test, ast.Eq
        elif isinstance(node, ast.If) and _fails(node.body):
            test, op = node.test, ast.NotEq
        else:
            continue
        if not (isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], op)):
            continue
        sides = (test.left, test.comparators[0])
        if any(isinstance(s, (ast.Constant, ast.JoinedStr)) or (isinstance(s, ast.Call) and _call_name(s) in
                                                                 TYPE_FREE_CALLS) for s in sides):
            continue
        kinds = [kind_of(s, scope, node) for s in sides]
        if "own" not in kinds or not set(kinds) & {"deliverable", "harness"}:
            continue
        strs = resolve(sides[kinds.index("own")], scope, node)[1]
        hit = next((path for path, doc, keys in answers if _bool_under(doc, strs & keys, typed)), "")
        if hit:
            lines.append(node.lineno)
            bools_in = bools_in or hit
    if not lines:
        return []
    more = (" (%d places: lines %s)" % (len(lines), ", ".join(map(str, sorted(lines)[:8])))) if len(lines) > 1 else ""
    return [(rel, min(lines), "B13",
             "decides with == between the observed value and the expected one%s, which counts true as 1 and false as "
             "0 (and 1 as 1.0): an output that writes 0/1 where %s holds true/false passes. Compare with "
             "tb4judge.same (template v2.1, type-strict), or check the JSON types before ==" % (more, bools_in))]


# ------------------------------------------------------------------ B14 the whole output folder under one cap

WHOLE_OUTPUT_COLLECT = re.compile(r"cp\s+-a\s+/app/output/?\.?\s|tar\s+-C\s+/app/output\b")
_CLAUSE = r"(?:`[^`\n]*`|[^.;`\n])"        # a clause's text; a dot inside backticks (a file name) does not end it
ONLY_READ = re.compile(r"\bonly\b%s{0,120}?\b(?:is|are)\s+(?:read|graded|checked|scored|used)\b"
                       r"|\b(?:nothing else|no other files?)\b%s{0,80}?\b(?:read|graded|checked|scored)\b"
                       r"|\bother files\b%s{0,60}?\b(?:ignored|not (?:read|graded|checked))\b" % ((_CLAUSE,) * 3),
                       re.I)
# the instruction says the whole folder reaches the grader: "/app/output is collected", "the whole `/app/output` folder
# is collected" (carillon-drum-repin), "everything in `/app/output` is packed into one archive" (vr-session-credits)
COLLECT_SAID = re.compile(r"/app/output`?\s+(?:(?:folder|directory)\s+)?is\s+collected\b|\bcollected whole\b"
                          r"|\b(?:everything|all(?: files)?)\s+(?:in|under)\s+`?/app/output`?\s+is\s+(?:packed|collected|archived)\b"
                          r"|\b(?:holds?|hold|with) no (?:symbolic |hard )?links\b|\bregular files and directories\b", re.I)
ARCHIVE_CAP = re.compile(r"\$\{?size\}?\"?\s+-(?:le|lt|gt|ge)\s+\$\(\(\s*\$?\{?MAX_MB")
REFUSE_MEMBER = re.compile(r"\bif not \(m\.isfile\(\) or m\.isdir\(\)\)")


def _sentence_at(text: str, pos: int) -> str:
    """The sentence of TEXT around POS (a dot inside backticks does not end it)."""
    start = max([text.rfind("\n", 0, pos)] + [m.start() for m in SENTENCE_END.finditer(text, 0, pos)]) + 1
    m = SENTENCE_END.search(text, pos)
    nl = text.find("\n", pos)
    end = min([i for i in (m.end() if m else -1, nl) if i >= 0] or [len(text)])
    return " ".join(text[start:end].split())


def rule_whole_output_cap(rel: str, sh: str, toml_text: str, instr: str) -> list:
    """B14: the collect hook packs all of /app/output, test.sh holds the whole archive to one cap (or refuses a link
    anywhere in it), and the instruction says only the named file is read without saying the folder is collected
    whole (that sentence makes the cap and the no-link rule part of the contract)."""
    m = ONLY_READ.search(instr)
    if not m or COLLECT_SAID.search(instr) or "archive-cap" in sh or not WHOLE_OUTPUT_COLLECT.search(toml_text):
        return []
    said = _sentence_at(instr, m.start())[:160]
    out = []
    for i, ln in enumerate(sh.split("\n")):
        code = ln.split("#", 1)[0]
        if ARCHIVE_CAP.search(code):
            out.append((rel, i + 1, "B14",
                        "holds the whole archive of /app/output (the collect hook packs every file) to "
                        "max_submission_mb, though instruction.md says \"%s\": a scratch file the agent leaves beside "
                        "a correct deliverable can push it past the cap. Declare the deliverables in tests/grading.json "
                        "and move to template v2.1 (`tb4 upgrade-verifier`): its unpack grades only the declared paths "
                        "and gives the archive its own ceiling" % said))
        elif REFUSE_MEMBER.search(code):
            out.append((rel, i + 1, "B14",
                        "refuses the whole submission for one link or special file anywhere in /app/output, though "
                        "instruction.md says \"%s\": an unrelated link left beside a correct deliverable fails it. "
                        "Declare the deliverables in tests/grading.json and move to template v2.1 (`tb4 "
                        "upgrade-verifier`): its unpack lists the undeclared members and never extracts or follows "
                        "them" % said))
    return out


# ------------------------------------------------------------------ B15 a deadline that times more than the call

TIMEOUT_NAME = re.compile(r"TIMEOUT|DEADLINE|LIMIT", re.I)
# the limit is the graded call's own (each call has 60 seconds), not one for the whole case process
CALL_WORDS = re.compile(r"\b(?:call|calls|function|method|invocation)\b|`[A-Za-z_][\w.]*\(", re.I)
PROCESS_WORDS = re.compile(r"\b(?:process|in all|in total|altogether|including|start-?up|whole run|end to end)\b", re.I)


def _process_deadline(tree, name: str) -> bool:
    """NAME bounds a child process, in a function that starts one: `time.monotonic() + NAME`, `timeout=NAME`,
    signal.alarm(NAME). A limit checked on the call's own elapsed time inside the case is not one."""
    for fn in [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
        if not any(isinstance(n, ast.Call) and _call_name(n) in SUBPROCESS_CALLS for n in ast.walk(fn)):
            continue
        for n in ast.walk(fn):
            uses = lambda e: any(isinstance(x, ast.Name) and x.id == name for x in ast.walk(e))   # noqa: E731
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add) and uses(n) and any(
                    isinstance(x, ast.Call) and _call_name(x) in ("monotonic", "time", "perf_counter")
                    for x in ast.walk(n)):
                return True
            if isinstance(n, ast.Call) and (any(k.arg == "timeout" and uses(k.value) for k in n.keywords)
                                            or (_call_name(n) in ("alarm", "setitimer") and uses(n))):
                return True
    return False


def rule_case_deadline(rel: str, tree, scope: Scope, instr: str) -> list:
    """B15: the per-case deadline is the instruction's own time limit for the graded call, but it times the whole
    case process (start-up, the import of the submission, hashing and serialization around the call)."""
    imports_submission = any(isinstance(n, ast.Call) and _call_name(n) in ("import_module", "__import__")
                             for n in ast.walk(tree))
    reruns_itself = any(isinstance(n, ast.Call) and _call_name(n) in SUBPROCESS_CALLS and any(
        isinstance(x, ast.Name) and x.id == "__file__" for a in n.args for x in ast.walk(a)) for n in ast.walk(tree))
    if not (imports_submission and reruns_itself):
        return []
    out = []
    for name, assigns in scope.module.items():
        if not TIMEOUT_NAME.search(name):
            continue
        for line, value in assigns:
            v = value.value if isinstance(value, ast.Constant) else None
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v <= 0:
                continue
            num = ("%g" % v).replace(".", r"\.")
            said = next((s for s in re.finditer(r"[^.\n]*\b%s\s*(?:-\s*)?(?:s|sec|secs|seconds?)\b[^.\n]*" % num,
                                                instr) if CALL_WORDS.search(s.group(0))
                         and not PROCESS_WORDS.search(s.group(0))), None)
            if said and _process_deadline(tree, name):
                out.append((rel, line, "B15",
                            "%s = %g s is the instruction's own limit (\"%s\"), but it times the whole case process: "
                            "interpreter start-up, the import of the submission and the hashing and serialization "
                            "around the call count against it, so a correct call that returns just under %g s can "
                            "fail. Time only the graded call inside the case (time.perf_counter() around it, checked "
                            "against %g s) and give the process deadline a margin" % (
                                name, v, " ".join(said.group(0).split())[:140], v, v)))
    return out


# ------------------------------------------------------------------ B16 a protected tree the verifier never sees

PROTECT_WORDS = re.compile(FREEZE_WORDS.pattern + r"|\b(?:stay|stays|remain|remains)\s+(?:exactly\s+)?"
                           r"(?:as\b|the same\b|unchanged\b|untouched\b)|\bas (?:delivered|shipped)\b"
                           r"|\bas it found it\b|\bwithout (?:changing|modifying|altering|touching)\b", re.I)
RESTORE_WORDS = re.compile(r"\b(?:restored|reset|reverted|discarded|overwritten|put back)\b", re.I)
PROGRAM_SUBJECT = re.compile(r"\b(?:program|script|run|tool|command|code|it)s?\s+(?:must|should|has to|may)?\s*"
                             r"(?:not\s+)?(?:leave|leaves|change|modify|write)\b", re.I)
AGENT_PATH = re.compile(r"(?<![\w/])(/app/[A-Za-z0-9_.\-/]*[A-Za-z0-9_\-])")


def _collect_text(toml_text: str) -> str:
    out = []
    for m in re.finditer(r"\[\[verifier\.collect\]\](.*?)(?=\n\[(?!\[verifier\.collect)|\Z)", toml_text, re.S):
        out.append(m.group(1))
    return "\n".join(out)


def rule_protected_paths(task: Path, toml_text: str, sh: str, judge_text: str, grading, instr: str) -> list:
    """B16: instruction.md promises an agent-side path stays as delivered, and nothing the verifier sees records it:
    the collect hook leaves it out (separate verifier) or no check names it (shared one)."""
    separate = bool(re.search(r"environment_mode\s*=\s*\"separate\"", toml_text))
    collect = _collect_text(toml_text)
    arts = re.search(r"^\s*artifacts\s*=\s*\[([^\]]*)\]", toml_text, re.M)
    arts = arts.group(1) if arts else ""
    g = grading if isinstance(grading, dict) else {}
    prot = g.get("protected")
    prot = [str(x.get("path") if isinstance(x, dict) else x) for x in prot] if isinstance(prot, list) else \
        [str(k) for k in prot] if isinstance(prot, dict) else []
    repo = str(g.get("repo") or "")
    repo = repo if repo.startswith("/") else ("/app/" + repo if repo else "")
    seen, out = set(), []
    for s in re.split(r"(?<=[.!?])\s+|\n", instr):
        if not PROTECT_WORDS.search(s) or RESTORE_WORDS.search(s):
            continue
        for m in AGENT_PATH.finditer(s):
            if PROGRAM_SUBJECT.search(s[:m.start()]):
                continue                       # the program's runs leave it unchanged: checked on the verifier's copy
            p = m.group(1).rstrip("/.")
            if p in seen or re.match(r"/app/(?:output|submission)\b", p) or p == "/app":
                continue
            seen.add(p)
            if repo and (p == repo or p.startswith(repo.rstrip("/") + "/")):
                continue                       # inside the repository: the submitted patch carries any change
            covered = any(p == q.rstrip("/") or p.startswith(q.rstrip("/") + "/") or q.startswith(p + "/")
                          for q in prot if q)
            if covered or p in collect or p in arts or (not separate and (p in sh or p in judge_text)):
                continue
            where = next((i + 1 for i, ln in enumerate(toml_text.split("\n")) if "[[verifier.collect]]" in ln), 1)
            out.append(("task.toml", where, "B16",
                        "instruction.md promises %s stays as delivered (\"%s\"), but %s: changing the agent-side %s "
                        "costs nothing, since the verifier checks only its own fresh copy. List %s in tests/grading.json "
                        "\"protected\" (template v2.1's collect hook records it after the agent phase and tb4judge "
                        "compares it with the pristine digest), or drop the promise" % (
                            p, " ".join(s.split())[:140],
                            "the verifier runs in its own container and the collect hook never records it"
                            if separate else "no check in tests/ reads it", p, p)))
    return out


def emit_side(task: Path) -> set:
    """tests/emit.py and the tests/*.py modules it imports: the code that turns the program's output into
    observations."""
    tests = task / "tests"
    start = tests / "emit.py"
    out, queue = set(), [start]
    while queue:
        p = queue.pop()
        if p in out or not p.is_file():
            continue
        out.add(p)
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            names = [a.name.split(".")[0] for a in node.names] if isinstance(node, ast.Import) else \
                [node.module.split(".")[0]] if isinstance(node, ast.ImportFrom) and node.module and not node.level \
                else []
            queue += [tests / (n + ".py") for n in names if (tests / (n + ".py")).is_file()]
    return out


# ------------------------------------------------------------------ the gate

TEMPLATE_LINES = Path(__file__).resolve().parent / "data" / "template-v2-lines.json"
MECHANICAL_FIX = ("mechanical: the same loader is in nearly every task's judge; load the deliverable with "
                  "tb4judge.load_json (template v2.1), no disposition. ")
TEMPLATE_FIX = ("template v2 code, the same in every task made from it: `tb4 upgrade-verifier` moves the task to "
                "template v2.1, which fixes it (merge by hand where it reports a manual merge). ")
TEMPLATE_ADVISORY = {"B10", "B11", "B12", "B13", "B15"}


def template_lines() -> dict:
    """{"test.sh": set, "emit.py": set}: the v2 template's code lines (data/template-v2-lines.json); empty when the
    file is missing (a finding is then the task's own)."""
    try:
        return {k: set(v) for k, v in json.loads(TEMPLATE_LINES.read_text())["files"].items()}
    except (OSError, ValueError, KeyError):
        return {}


def template_owned(finding, text_of: dict, tmpl: dict) -> bool:
    """A finding on a line of tests/test.sh or tests/emit.py that the v2 template ships verbatim: the template's,
    fixed by its upgrade, not a defect the task's author wrote."""
    path, line = finding[0], finding[1]
    name = Path(path).name
    if path not in ("tests/test.sh", "tests/emit.py") or name not in tmpl:
        return False
    lines = (text_of.get(path) or "").splitlines()
    return 0 < line <= len(lines) and lines[line - 1].strip() in tmpl[name]


def check(task: Path) -> dict:
    """{"status", "details", "findings": [(path, line, rule, message)], "warnings": [...], "ordered": [...]}."""
    task = Path(task)
    if not (task / "tests").is_dir():
        return {"status": "ERROR", "details": "no tests/ folder: no grader to check", "findings": [], "warnings": [],
                "ordered": []}
    instr = (task / "instruction.md").read_text(encoding="utf-8", errors="replace") \
        if (task / "instruction.md").is_file() else ""
    grading_p = task / "tests" / "grading.json"
    grading_text = grading_p.read_text(encoding="utf-8", errors="replace") if grading_p.is_file() else ""
    try:
        grading = json.loads(grading_text) if grading_text else {}
    except ValueError:
        grading = {}
    has_suite = isinstance(grading, dict) and bool(grading.get("suite"))
    files = judge_files(task)
    texts = {p: p.read_text(encoding="utf-8", errors="replace") for p in files}
    csv_task = bool(re.search(r"\.csv\b|\bCSV\b", instr)) or any("csv" in t.lower() for t in texts.values())
    shipped = _json_numbers(task)
    shapes = _shipped_shapes(task)
    emitter = emit_side(task)
    local = {q.stem for q in (task / "tests").glob("*.py")}       # the grader's own helper modules
    answers = answer_bools(task)
    typed = set()
    for q in emitter:
        try:
            typed |= typed_bool_members([ast.parse(q.read_text(encoding="utf-8", errors="replace"))])
        except SyntaxError:
            pass
    findings, warnings, ordered = [], [], []
    for p in files:
        rel = _rel(task, p)
        try:
            tree = ast.parse(texts[p])
        except SyntaxError as e:
            warnings.append((rel, e.lineno or 0, "parse", "could not parse: %s" % e.msg))
            continue
        scope = Scope(tree)
        findings += rule_dup_keys(rel, tree, scope)
        f2, w2 = rule_float_tolerance(task, rel, tree, scope, shipped, instr)
        findings += f2
        warnings += w2
        findings += rule_csv_split(task, rel, tree, scope, csv_task, instr)
        f4, o4 = rule_key_order(rel, tree, scope, instr, shapes)
        findings += f4
        ordered += o4
        findings += rule_runner_rc_py(rel, tree, scope)
        findings += rule_silent_drop(rel, tree, scope, p in emitter)
        findings += rule_stream_cap(rel, tree, scope, instr)
        findings += rule_tree_hash(rel, tree, scope, instr)
        findings += rule_case_deadline(rel, tree, scope, instr)
        if p in emitter:
            findings += rule_repr_fallback(rel, tree, local)
            warnings += rule_lossy(rel, tree)
        else:
            findings += rule_type_equality(rel, tree, scope, answers, typed)
    toml_p = task / "task.toml"
    toml_text = toml_p.read_text(encoding="utf-8", errors="replace") if toml_p.is_file() else ""
    sh_p = task / "tests" / "test.sh"
    sh = ""
    if sh_p.is_file():
        sh = sh_p.read_text(encoding="utf-8", errors="replace")
        findings += rule_runner_rc_sh("tests/test.sh", sh, has_suite)
        emit_text = texts.get(task / "tests" / "emit.py", "")
        findings += rule_isolation(task, "tests/test.sh", sh, emit_text)
        findings += rule_whole_output_cap("tests/test.sh", sh, toml_text, instr)
    findings += rule_protected_paths(task, toml_text, sh, "\n".join(texts.values()), grading, instr)
    if grading_text:
        f7, w7 = rule_test_globs(task, "tests/grading.json", grading_text, instr)
        findings += f7
        warnings += w7
    v21 = (task / V21_MARKER).is_file()
    findings = sorted(set(findings), key=lambda f: (f[0], f[1], f[2]))
    text_of = {_rel(task, p): t for p, t in texts.items()}
    if sh_p.is_file():
        text_of["tests/test.sh"] = sh
    tmpl = {} if v21 else template_lines()
    # B10-B13 and B15 on a line the v2 template ships: the same code in every task made from it, fixed by one batch
    # upgrade, so an advisory warning rather than a FAIL on every v2 task. B14 and B16 always FAIL: each rests on the
    # task's own promise (only one file is read, a path stays as delivered).
    advisory = [f for f in findings if f[2] in TEMPLATE_ADVISORY and template_owned(f, text_of, tmpl)]
    findings = [f for f in findings if f not in advisory]
    warnings += [(f[0], f[1], f[2], TEMPLATE_FIX + f[3]) for f in advisory]
    ours = [f for f in findings if template_owned(f, text_of, tmpl)]
    # B1 is mechanical too: the loader authors copied from the template's test_outputs.py, in nearly every task (all
    # 60 delivered on 10/16); the fix is one call (tb4judge.load_json), never a judgment to dispose task by task
    ours += [f for f in findings if f not in ours and f[2] == "B1"]
    theirs = [f for f in findings if f not in ours]
    findings = theirs + [(f[0], f[1], f[2], (TEMPLATE_FIX if template_owned(f, text_of, tmpl) else MECHANICAL_FIX)
                          + f[3]) for f in ours]
    if findings:
        # the author's grader: a reviewer's judgment on v2 (fix or dispose), a FAIL on v2.1; the template's and the
        # copied loader's: a FAIL with one mechanical fix, never a disposition to argue task by task
        status = "FAIL" if (ours or v21) else "FAIL-PENDING-DISPOSITION"
        rules = sorted({f[2] for f in findings})
        if v21:
            how = "on template v2.1 (tests/tb4judge.py) each FAILs: fix it, or the author disputes it and a reviewer " \
                  "who is not an author settles it"
        elif ours:
            how = "the mechanical ones are fixed by the v2.1 upgrade (`tb4 upgrade-verifier`) and tb4judge.load_json; " \
                  "on v2.1 the task's own ones FAIL too, so fix them in the same pass"
        else:
            how = "on the v2 template a reviewer fixes each or disposes it with a reason (`tb4 gate dispose`)"
        details = ("%d grader finding(s) (%s): %d in the task's own grader, %d mechanical (template v2 code or the "
                   "copied JSON loader); %s" % (len(findings), ", ".join(rules), len(theirs), len(ours), how))
    else:
        status = "PASS"
        details = "%d grader file(s) checked: no duplicate-key, float-boundary, CSV, key-order, exit-status, " \
                  "serialization, test_globs, isolation, dropped-item, stream-cap, mode-hash, bool/int, " \
                  "output-folder-cap, deadline or protected-path finding" % (len(files) + bool(sh_p.is_file()))
    return {"status": status, "details": details, "findings": findings, "warnings": warnings, "ordered": ordered}
