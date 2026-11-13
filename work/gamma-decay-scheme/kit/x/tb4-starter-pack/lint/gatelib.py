#!/usr/bin/env python3
"""Shared record format for every validation gate.

A gate is one check (a lint, a control run, a review). Every gate writes one
JSON file, and every file has the same shape, so GATES.json, the dashboard and
DELIVERY.md are built from records rather than written by hand:

    {"schema": 1, "gate": "<name>",
     "status": "PASS" | "FAIL" | "ERROR" | "FAIL-PENDING-DISPOSITION" | "DISPUTED",
     "task": "<slug>", "task_digest": "sha256:<hex>", "created_utc": "...",
     "details": "<one paragraph>", "findings": [{"path": "...", "line": N,
     "message": "..."}], "evidence": ["<relative path>", ...]}

Rules the records enforce:
  * FAIL-CLOSED. A gate that could not run is ERROR, never PASS. A gate with
    no record counts as missing, and missing blocks packaging.
  * ONE DIGEST. Every record carries the digest of the task it judged, computed
    exactly as Harbor 0.25.0 (and 0.23.0, the same hash) computes a task's
    content hash, so a record made on another version of the task is detected
    and refused.
  * OUTSIDE THE TASK. Records live in a sibling directory, never inside the
    task (the linter flags extraneous files and edits change the digest).
  * APPEND-ONLY HISTORY. <gate>.json is the latest run; every run is also kept
    as history/<gate>/<utc>-<status>.json and never replaced, so a FAIL or an
    ERROR survives a later PASS (rerunning a control until it is green leaves
    the failures on disk, and gates.py summary reports them).
  * PENDING IS NOT PASS. FAIL-PENDING-DISPOSITION and DISPUTED block until a
    person records a disposition for each item (gates.py dispose).

Stdlib only, Python 3.9+.
"""
import datetime as _dt
import fnmatch
import hashlib
import json
import os
import sys
from pathlib import Path

SCHEMA = 1
STATUSES = ("PASS", "FAIL", "ERROR", "FAIL-PENDING-DISPOSITION", "DISPUTED")
# Statuses a recorded disposition (gates.py dispose) can resolve. FAIL and ERROR cannot.
DISPOSABLE = ("FAIL-PENDING-DISPOSITION", "DISPUTED")
HISTORY_DIR = "history"

# How each finding was established, the customer's own distinctions (conclusion-v2.md item 11):
#   reported          a reading of the files or a model's judgment; nothing was run
#   reproduced-local  the task's own code (its judge, its arithmetic) was run on a constructed input and failed
#   reproduced-e2e    the whole verifier ran in its container on a submission and gave the wrong result
#   conditional       it holds only if a condition the check could not establish holds (an advisory warning)
EVIDENCE_LEVELS = ("reported", "reproduced-local", "reproduced-e2e", "conditional")
EVIDENCE_TEXT = {"reported": "reported: read from the files, not run",
                 "reproduced-local": "reproduced locally: the task's own code was run on a constructed input",
                 "reproduced-e2e": "reproduced end to end: the verifier ran in its container",
                 "conditional": "conditional: holds only if a condition the check did not establish holds"}
# the gates that run the whole verifier on a submission (the Docker controls and the robustness controls)
E2E_GATES = frozenset(("oracle", "oracle-determinism", "verifier-repeat", "nop", "tamper", "tamper-delivery",
                       "wrong-answers", "missing-artifact", "partial-artifact", "readable-answers", "valid-variants",
                       "strict-parsing", "isolation", "suite-exit", "api-types"))


def default_evidence_level(gate):
    """A finding's evidence level when the gate that wrote it did not set one."""
    return "reproduced-e2e" if gate in E2E_GATES else "reported"


def with_evidence_levels(gate, findings, warnings=None):
    """FINDINGS with evidence_level set where missing (the gate's default), and WARNINGS (dicts) as conditional."""
    out = []
    for f in findings or []:
        if isinstance(f, dict) and f.get("evidence_level") not in EVIDENCE_LEVELS:
            f = dict(f, evidence_level=default_evidence_level(gate))
        out.append(f)
    if warnings is None:
        return out
    ws = [dict(w, evidence_level="conditional") if isinstance(w, dict) and w.get("evidence_level") not in
          EVIDENCE_LEVELS else w for w in warnings]
    return out, ws

# Harbor's Packager.DEFAULT_IGNORES, used when the task has no .gitignore.
_DEFAULT_IGNORES = ["__pycache__/", "*.pyc", ".DS_Store", "*.swp", "*.swo", "*~"]
_SINGLE_FILES = ("task.toml", "instruction.md", "README.md", "trajectory.json")
_DIRS = ("environment", "tests", "solution", "steps")


def _ignored(rel, patterns):
    """A small subset of gitignore matching: enough for Harbor's defaults and
    for the plain patterns task authors write (name, *.ext, dir/)."""
    parts = rel.split("/")
    for raw in patterns:
        pat = raw.strip()
        if not pat or pat.startswith("#") or pat.startswith("!"):
            continue
        anchored = pat.startswith("/")
        pat = pat.lstrip("/")
        if pat.endswith("/"):
            name = pat[:-1]
            if any(fnmatch.fnmatch(p, name) for p in parts[:-1]):
                return True
            continue
        if "/" in pat or anchored:
            if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(rel, pat + "/*"):
                return True
        elif any(fnmatch.fnmatch(p, pat) for p in parts):
            return True
    return False


def task_files(task):
    """The files Harbor hashes, in Harbor's order (cheat/ and _provenance are not among them)."""
    task = Path(task).resolve()
    files = [task / f for f in _SINGLE_FILES if (task / f).is_file()]
    for d in _DIRS:
        if (task / d).is_dir():
            files += [p for p in (task / d).rglob("*") if p.is_file()]
    gi = task / ".gitignore"
    patterns = gi.read_text().splitlines() if gi.is_file() else _DEFAULT_IGNORES
    files = [f for f in files if not _ignored(f.relative_to(task).as_posix(), patterns)]
    files.sort(key=lambda p: p.relative_to(task).as_posix())
    return files


def task_digest(task, overrides=None):
    """Harbor's content hash: sha256 over "<rel>\\0<sha256(file)>\\n" in path order.
    OVERRIDES, {rel: bytes}, hashes those bytes in place of an existing file's (equivalence.py
    recomputes the digest of an earlier version from the delivered tree and its recorded README)."""
    task = Path(task).resolve()
    overrides = overrides or {}
    outer = hashlib.sha256()
    for f in task_files(task):
        rel = f.relative_to(task).as_posix()
        if rel in overrides:
            digest = hashlib.sha256(overrides[rel]).hexdigest()
        else:
            h = hashlib.sha256()
            with f.open("rb") as fh:
                for chunk in iter(lambda: fh.read(1 << 20), b""):
                    h.update(chunk)
            digest = h.hexdigest()
        outer.update(("%s\0%s\n" % (rel, digest)).encode())
    return "sha256:" + outer.hexdigest()


def gates_dir(task, override=None):
    """Where records live: <parent>/<slug>-gates/, next to the task, never inside it."""
    task = Path(task).resolve()
    d = Path(override).resolve() if override else task.parent / (task.name + "-gates")
    if task == d or task in d.parents:
        raise SystemExit("gates directory %s is inside the task %s" % (d, task))
    d.mkdir(parents=True, exist_ok=True)
    return d


def _utc_now():
    return _dt.datetime.now(_dt.timezone.utc)


def write_gate(task, gate, status, details="", findings=None, evidence=None, out_dir=None, extra=None):
    """Write <gates-dir>/<gate>.json (the latest run) and append the same record to
    <gates-dir>/history/<gate>/<utc>-<status>.json; return the latest record's path."""
    if status not in STATUSES:
        raise ValueError("status must be one of %s, got %r" % (STATUSES, status))
    task = Path(task).resolve()
    now = _utc_now()
    rec = {
        "schema": SCHEMA,
        "gate": gate,
        "status": status,
        "task": task.name,
        "task_digest": task_digest(task),
        "created_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "details": details,
        "findings": with_evidence_levels(gate, findings),
        "evidence": [str(e) for e in (evidence or [])],
    }
    if extra:
        rec.update(extra)
        if isinstance(rec.get("warnings"), list):
            rec["warnings"] = with_evidence_levels(gate, [], rec["warnings"])[1]
    gdir = gates_dir(task, out_dir)
    text = json.dumps(rec, indent=2, sort_keys=True) + "\n"
    hdir = gdir / HISTORY_DIR / gate
    hdir.mkdir(parents=True, exist_ok=True)
    stem = "%s-%s" % (now.strftime("%Y%m%dT%H%M%S.%fZ"), status)
    n = 0
    while True:   # exclusive create: a history entry is never overwritten
        hp = hdir / ("%s%s.json" % (stem, "" if n == 0 else "-%d" % n))
        try:
            with open(hp, "x") as fh:
                fh.write(text)
            break
        except FileExistsError:
            n += 1
    rec["history_file"] = hp.relative_to(gdir).as_posix()
    path = gdir / (gate + ".json")
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
    os.replace(tmp, path)
    return path


def gate_history(gdir, gate):
    """Every recorded run of GATE, oldest first: [(path, record or None when unreadable)]."""
    hdir = Path(gdir) / HISTORY_DIR / gate
    out = []
    if not hdir.is_dir():
        return out
    for p in sorted(hdir.glob("*.json"), key=lambda q: (q.name[:24], len(q.name), q.name)):
        try:
            out.append((p, read_gate(p)))
        except (ValueError, OSError):
            out.append((p, None))
    return out


def history_gates(gdir):
    d = Path(gdir) / HISTORY_DIR
    return sorted(p.name for p in d.iterdir() if p.is_dir()) if d.is_dir() else []


def read_gate(path):
    """Load a record and check its shape. Raises ValueError on a malformed record."""
    rec = json.loads(Path(path).read_text())
    for k in ("schema", "gate", "status", "task", "task_digest"):
        if k not in rec:
            raise ValueError("%s: missing %s" % (path, k))
    if rec["status"] not in STATUSES:
        raise ValueError("%s: bad status %r" % (path, rec["status"]))
    return rec


def newer_task_files(task, stamp):
    """Task files modified after `stamp` (epoch seconds), among the files the task digest covers
    (task_files): cheat/, _provenance, interpreter caches and Finder litter are not task content.
    Used only for a criteria record without a task_digest."""
    task = Path(task).resolve()
    return [p.relative_to(task).as_posix() for p in task_files(task) if p.stat().st_mtime > stamp]


def criteria_staleness(task, criteria, rec):
    """Why the criteria record REC (read from the file CRITERIA) is not current for TASK: [] when it is.
    A record with a task_digest is current exactly when it equals the digest now (equal content is
    proven, file mtimes are not read); only one without a digest falls back to file times: a task file
    newer than the record file, or than its generated_utc (which survives a copy that resets mtimes).
    gates.py import-criteria and package-delivery.sh both apply it."""
    recorded = rec.get("task_digest")
    if recorded:
        return [] if recorded == task_digest(task) else [
            "stale: the record's task_digest %s is not the current one" % recorded]
    newer = newer_task_files(task, Path(criteria).stat().st_mtime)
    try:
        stamp = _dt.datetime.strptime(rec.get("generated_utc"), "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=_dt.timezone.utc).timestamp()
    except (TypeError, ValueError):
        stamp = None
    if stamp is not None:
        newer = sorted(set(newer) | set(newer_task_files(task, stamp + 1)))
    return ["stale: task file(s) changed after the review: %s" % ", ".join(newer[:5])] if newer else []


def finding(path, line, message, evidence_level=None):
    f = {"path": str(path), "line": int(line or 0), "message": message}
    if evidence_level is not None:
        if evidence_level not in EVIDENCE_LEVELS:
            raise ValueError("evidence_level must be one of %s, got %r" % (EVIDENCE_LEVELS, evidence_level))
        f["evidence_level"] = evidence_level
    return f


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: gatelib.py <task-dir>   (prints the task digest)")
    print(task_digest(sys.argv[1]))


def extract_zip_member(zf, info, dest):
    """Extract one zip entry the way `unzip` does: with its stored Unix permission bits (rwx only, never
    setuid/setgid/sticky). zipfile.extract drops them, so an executable verifier helper (tests/harness/bin/...)
    came out 0644 and a replayed oracle scored 0 on "Permission denied" (stale-order-figures, 2026-09-30)."""
    path = zf.extract(info, dest)
    mode = (info.external_attr >> 16) & 0o777
    if mode and info.create_system == 3 and not info.is_dir():     # 3 = Unix: the attributes carry a mode
        os.chmod(path, mode | 0o400)                                 # always readable by the owner
    return path


def extract_zip(zf, dest, skip=()):
    """Every entry of ZF under DEST with its permission bits (extract_zip_member); names starting with SKIP are left."""
    for info in zf.infolist():
        if skip and info.filename.startswith(tuple(skip)):
            continue
        extract_zip_member(zf, info, dest)
