"""Rewrite TASK_DIR/tests/checks.txt from a kept reference run (RUN_DIR/planets.json and diag.json, written by
`tests/generate.py --keep RUN_DIR`) after a change to write_checks only. It uses the generator's own build (same seed,
so the same data the kept run reduced), expected and write_checks; nothing here runs the reference or the grader.
It also checks that the shipped data files still match what build produces, byte for byte.

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/checks_from_run.py TASK_DIR RUN_DIR SECONDS
"""
import importlib.util
import json
import sys
import tempfile
from pathlib import Path

import numpy as np

task, run, seconds = Path(sys.argv[1]).resolve(), Path(sys.argv[2]), float(sys.argv[3])
spec = importlib.util.spec_from_file_location("generate", task / "tests" / "generate.py")
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

d = G.build(np.random.default_rng(G.SEED))
exp = G.expected()
shipped = json.load(open(task / "tests" / "expected.json"))
assert exp == shipped, "expected.json differs from what the generator computes"

# the data files: write them to a scratch folder with the generator's own writer and compare
with tempfile.TemporaryDirectory() as tmp:
    real = G.DATA
    G.DATA = Path(tmp)
    try:
        for f in real.iterdir():
            if f.is_file():
                (Path(tmp) / f.name).write_bytes(f.read_bytes())    # NOTES.md and anything not generated
        G.write_data(d)
        for f in sorted(real.iterdir()):
            if f.is_file():
                same = (Path(tmp) / f.name).read_bytes() == f.read_bytes()
                print("%-20s %s" % (f.name, "same" if same else "DIFFERS"))
                assert same, f.name
    finally:
        G.DATA = real

res = json.load(open(run / "planets.json"))
diag = json.load(open(run / "diag.json"))
ok, notes = G.write_checks(exp, res, diag, d, seconds)
print("checks.txt rewritten; %s" % ("agrees with the system" if ok else "DISAGREES: " + "; ".join(notes)))
