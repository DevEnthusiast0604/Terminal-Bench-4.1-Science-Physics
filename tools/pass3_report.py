"""One-command pass@3 report. Extracts a downloaded full pass@3 zip, digests every attempt's trajectory, copies each
attempt's final /app/output files (never runs them) and prints one summary: rewards, tests, times, cost, the worst
error of every graded case as a fraction of the tolerance, the controls, the provenance digest and keyword counts in
each final program.

    python -X utf8 -I -B tools/pass3_report.py work/<slug>/v<N> [--job J] [--rtol 2e-5] [--atol NAME=1e-6 ...]
        [--keywords word,word,...]

--job J first fetches gate/full/J.zip through tools/supertasker.py into work/<slug>/v<N>/pass3/pass3.zip (the job
number is in `tools/supertasker.py links T-ID v<N>`). The zip is untrusted data: it is extracted into pass3/x/
(members with absolute paths, '..' or links are refused), nothing in it runs, and this script runs with -I from the
folder root. Errors are judged as the graders do for numbers: |got - expected| / max(rtol |expected|, atol[name]).
Writes pass3/summary.md, attempts/attempt-K.txt and attempts/programs/aK/.
"""
import argparse
import datetime as dt
import json
import math
import re
import stat
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path, PurePosixPath


def safe_name(name):
    p = PurePosixPath(name.replace("\\", "/"))
    if p.is_absolute() or ".." in p.parts or (p.parts and ":" in p.parts[0]):
        return None
    return p


def longpath(p):
    """Absolute path, with the \\\\?\\ prefix on Windows so deep members stay under the 260-character limit."""
    s = str(Path(p).resolve())
    if sys.platform == "win32" and not s.startswith("\\\\?\\"):
        s = "\\\\?\\" + s
    return Path(s)


def extract_zip(zpath, dest):
    with zipfile.ZipFile(zpath) as z:
        for info in z.infolist():
            p = safe_name(info.filename)
            mode = info.external_attr >> 16
            if p is None or stat.S_ISLNK(mode):
                print("refused member:", info.filename)
                continue
            out = dest.joinpath(*p.parts)
            if info.is_dir():
                out.mkdir(parents=True, exist_ok=True)
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            with z.open(info) as src, open(out, "wb") as fh:
                fh.write(src.read())


def extract_tar(tpath, dest):
    files = []
    with tarfile.open(tpath) as t:
        for m in t.getmembers():
            p = safe_name(m.name)
            if p is None or not m.isfile() or not p.parts or p.parts == (".",):
                continue
            out = dest.joinpath(*[x for x in p.parts if x != "."])
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(t.extractfile(m).read())
            files.append(out)
    return files


def stamp(s):
    return dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None


def minutes(block):
    a, b = stamp((block or {}).get("started_at")), stamp((block or {}).get("finished_at"))
    return (b - a).total_seconds() / 60 if a and b else None


def observations(path):
    got = {}
    if not path.exists():
        return got
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.startswith("TB4-OBS "):
            continue
        rec = json.loads(line[8:])
        val = rec.get("value") or {}
        try:
            got[rec["case"]] = json.loads(val.get("stdout") or "")
        except (ValueError, TypeError):
            got[rec["case"]] = None          # no JSON: timeout, crash or bad output
    return got


def fraction(g, e, rtol, atol):
    if not isinstance(g, (int, float)) or isinstance(g, bool) or not math.isfinite(g):
        return math.inf
    scale = max(rtol * abs(e), atol)
    d = abs(g - e)
    return d / scale if scale > 0 else (0.0 if d == 0 else math.inf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vdir")
    ap.add_argument("--job")
    ap.add_argument("--rtol", type=float, default=2e-5)
    ap.add_argument("--atol", action="append", default=[])
    ap.add_argument("--keywords", default="")
    a = ap.parse_args()
    vdir = Path(a.vdir)
    slug = vdir.parent.name
    atol = {k: float(v) for k, v in (s.split("=", 1) for s in a.atol)}
    keys = [k for k in a.keywords.split(",") if k]
    zpath, xdir = vdir / "pass3" / "pass3.zip", longpath(vdir / "pass3" / "x")

    if a.job:
        if zpath.exists():
            sys.exit("%s exists: move it aside or leave out --job" % zpath)
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", "-B", "tools/supertasker.py", "fetch",
                            "gate/full/%s.zip" % a.job, str(zpath)])
        if r.returncode:
            sys.exit("fetch failed")
    if not zpath.exists():
        sys.exit("no %s (give --job J to fetch it)" % zpath)
    if not xdir.exists() or not any(xdir.iterdir()):
        xdir.mkdir(parents=True, exist_ok=True)
        extract_zip(zpath, xdir)
    roots = [p for p in xdir.iterdir() if p.is_dir()]
    if len(roots) != 1:
        sys.exit("expected one top folder in %s, found %d" % (xdir, len(roots)))
    root = roots[0]
    expected = json.loads((root / slug / "tests" / "expected.json").read_text(encoding="utf-8"))
    if not all(isinstance(v, dict) for v in expected.values()):
        # A data task (RUN_PROGRAM=0) has one answer object, not {case: {quantity: value}}: skip the per-case errors
        # and compare the copied outputs (attempts/programs/aK/) with the task's own report tool.
        print("expected.json is not {case: {quantity: value}}: a data task; per-case errors skipped")
        expected = {}
    prov = root / "provenance" / "PROVENANCE.json"
    digest = json.loads(prov.read_text(encoding="utf-8")).get("task_digest") if prov.exists() else "?"

    out = ["# pass@3 report: %s %s" % (slug, vdir.name), "",
           "Zip `%s`; provenance task digest `%s`. Tolerance: rtol %g%s." % (
               zpath.as_posix(), digest, a.rtol,
               "".join(", %s atol %g" % kv for kv in atol.items())), ""]
    adir = vdir / "attempts"
    adir.mkdir(exist_ok=True)
    attempts = sorted((root / "evidence" / "attempts").glob("*/attempt-*"))
    rows, per_case, kw = [], {}, {}
    for k, at in enumerate(attempts, 1):
        res = json.loads((at / "result.json").read_text(encoding="utf-8"))
        reward = ((res.get("verifier_result") or {}).get("rewards") or {}).get("reward")
        ctrf = at / "verifier" / "ctrf.json"
        tests = json.loads(ctrf.read_text(encoding="utf-8"))["results"]["tests"] if ctrf.exists() else []
        failed = [t["name"].split("::")[-1] for t in tests if t.get("status") != "passed"]
        ag = res.get("agent_result") or {}
        exc = (res.get("exception_info") or {}).get("exception_type") if res.get("exception_info") else None
        got = observations(at / "verifier" / "observations.jsonl")
        worst = (0.0, "-", "-")
        for case, exp in expected.items():
            g = got.get(case)
            fr = {q: (fraction(g.get(q), e, a.rtol, atol.get(q, 0.0)) if isinstance(g, dict) else math.inf)
                  for q, e in exp.items()}
            q = max(fr, key=fr.get)
            per_case.setdefault(case, {})[k] = (fr[q], q)
            if fr[q] > worst[0]:
                worst = (fr[q], case, q)
        traj = at / "agent" / "trajectory.json"
        if traj.exists():
            r = subprocess.run([sys.executable, "-X", "utf8", "-I", "-B", "tools/trajectory_digest.py", str(traj)],
                               capture_output=True, text=True, encoding="utf-8")
            (adir / ("attempt-%d.txt" % k)).write_text(r.stdout, encoding="utf-8", newline="\n")
        pdir = longpath(adir / "programs" / ("a%d" % k))
        tar = at / "artifacts" / "app" / "submission" / "output.tar"
        files = extract_tar(tar, pdir) if tar.exists() else []
        text = "\n".join(f.read_text(encoding="utf-8", errors="replace") for f in files if f.suffix == ".py")
        kw[k] = {w: len(re.findall(re.escape(w), text, re.I)) for w in keys}
        rows.append("| %d | %s | %s | %s | %s | %s | %s | %s | %.3g at %s %s | %d lines |" % (
            k, reward, "all passed" if tests and not failed else ("failed " + ", ".join(failed) if failed else "none"),
            ((res.get("agent_execution") or {}).get("started_at") or "")[11:16],
            "%.0f min" % minutes(res.get("agent_execution")) if minutes(res.get("agent_execution")) else "?",
            "%.1f min" % minutes(res.get("verifier")) if minutes(res.get("verifier")) else "?",
            (ag.get("metadata") or {}).get("n_episodes", "?"),
            ("$%.2f" % ag["cost_usd"]) if ag.get("cost_usd") else "?",
            worst[0], worst[1], worst[2], text.count("\n") + (1 if text else 0)) + (" %s" % exc if exc else ""))
    out += ["| attempt | reward | tests | agent start | agent | verifier | episodes | cost | worst error / tolerance |"
            " program |", "|---|---|---|---|---|---|---|---|---|---|"] + rows + [""]
    out += ["Worst error per case as a fraction of the tolerance (quantity in brackets):", "",
            "| case | " + " | ".join("a%d" % k for k in range(1, len(attempts) + 1)) + " |",
            "|---|" + "---|" * len(attempts)]
    for case in expected:
        out.append("| %s | " % case + " | ".join("%.3g (%s)" % per_case[case][k] for k in range(1, len(attempts) + 1))
                   + " |")
    out.append("")
    if keys:
        out += ["Keyword counts in each final program:", "", "| keyword | " + " | ".join(
            "a%d" % k for k in kw) + " |", "|---|" + "---|" * len(kw)]
        out += ["| %s | " % w + " | ".join(str(kw[k][w]) for k in kw) + " |" for w in keys]
        out.append("")
    ctl = []
    for rt in sorted((root / "evidence").glob("controls/*/verifier/reward.txt")):
        ctl.append("%s %s" % (rt.parent.parent.name, rt.read_text(encoding="utf-8").strip()))
    out += ["Controls: " + (", ".join(ctl) if ctl else "none in the zip"), "",
            "Digests: `%s/attempt-K.txt`; programs (copied, not run): `%s/programs/aK/`." % (
                adir.as_posix(), adir.as_posix())]
    text = "\n".join(out) + "\n"
    (vdir / "pass3" / "summary.md").write_text(text, encoding="utf-8", newline="\n")
    print(text)


if __name__ == "__main__":
    main()
