"""The judge (tests/test_outputs.py) on observations made like tests/emit.py makes them (author's check).

    python -B judge_check.py <task_dir> <scratch_dir> [oracle|trust|empty|nopivotb ...]

oracle    solution/reduce.py run on each graded session as the checker runs it (a folder holding only a
          copy of reduce.py as its working directory, a bare environment), its rc and stdout recorded
trust     the same program with the logbook's pivots trusted (assign_pivots skipped)
empty     no program: python3 reduce.py exits 2 with nothing on stdout
For each variant the judge runs under pytest with TB4_OUTPUT, TB4_OBSERVATIONS and TB4_EXPECTED set, in a
scratch copy of tests/ (nothing is written under the task).
"""
import json
import os
import shutil
import subprocess
import sys

task, scratch = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
variants = sys.argv[3:] or ["oracle", "trust", "empty"]
CASES = ["h1", "h2", "h3", "h4"]
TRUST = """
import runpy, sys
mod = runpy.run_path(sys.argv[1], run_name="reduce_mod")
""".strip()


def run_program(workdir, case_dir, variant):
    env = {"HOME": workdir, "TMPDIR": workdir, "PATH": os.environ["PATH"], "LANG": "C.UTF-8",
           "SYSTEMROOT": os.environ.get("SYSTEMROOT", "")}
    if variant == "empty":
        return {"rc": 2, "stdout": ""}
    if variant == "oracle":
        cmd = [sys.executable, "-B", "reduce.py", case_dir]
    else:
        cmd = [sys.executable, "-B", "-c",
               "import importlib.util, json, sys\n"
               "spec = importlib.util.spec_from_file_location('r', 'reduce.py')\n"
               "R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)\n"
               "R.assign_pivots = lambda runs, geo: ({r: r[0] for r in runs}, {r: 0.0 for r in runs}, (0.0, 0.0))\n"
               "sys.stdout.write(json.dumps(R.reduce_session(sys.argv[1]), sort_keys=True) + '\\n')\n",
               case_dir]
    p = subprocess.run(cmd, cwd=workdir, env=env, capture_output=True, text=True)
    return {"rc": p.returncode, "stdout": p.stdout}


for variant in variants:
    vdir = os.path.join(scratch, "judge-" + variant)
    shutil.rmtree(vdir, ignore_errors=True)
    os.makedirs(os.path.join(vdir, "out"))
    os.makedirs(os.path.join(vdir, "judge"))
    if variant != "empty":
        shutil.copy(os.path.join(task, "solution", "reduce.py"), os.path.join(vdir, "out", "reduce.py"))
    with open(os.path.join(vdir, "observations.jsonl"), "w", newline="\n") as fh:
        for case in CASES:
            value = run_program(os.path.join(vdir, "out"), os.path.join(task, "tests", "cases", case), variant)
            fh.write("TB4-OBS " + json.dumps({"case": case, "ok": True, "value": value}, sort_keys=True) + "\n")
    for f in ("test_outputs.py", "tb4judge.py"):
        shutil.copy(os.path.join(task, "tests", f), os.path.join(vdir, "judge", f))
    env = dict(os.environ, TB4_OUTPUT=os.path.join(vdir, "out"), TB4_OBSERVATIONS=os.path.join(vdir, "observations.jsonl"),
               TB4_EXPECTED=os.path.join(task, "tests", "expected.json"), PYTHONDONTWRITEBYTECODE="1")
    p = subprocess.run([sys.executable, "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--tb=line",
                        os.path.join(vdir, "judge", "test_outputs.py")], cwd=os.path.join(vdir, "judge"),
                       env=env, capture_output=True, text=True)
    print("=== %s" % variant)
    print("\n".join(line[:300] for line in p.stdout.strip().splitlines()[-14:]))
