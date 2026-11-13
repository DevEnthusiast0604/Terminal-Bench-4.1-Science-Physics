"""Run an oracle copy on graded cases and compare with tests/expected.json (author self-check).
    python -B run_cases.py PROGRAM k01 [k02 ...]"""
import json
import subprocess
import sys
import time
from decimal import Decimal

TESTS = "../../../../tasks/active/chapman-enskog-transport/tests"
sys.path.insert(0, TESTS)
import emit  # noqa: E402

expected = json.load(open(TESTS + "/expected.json"))
prog = sys.argv[1]
for case in sys.argv[2:]:
    args = emit.CASES[case][1:]
    t0 = time.time()
    p = subprocess.run([sys.executable, "-B", prog, *args], capture_output=True, text=True)
    dt = time.time() - t0
    got = json.loads(p.stdout)
    worst = []
    for q, e in expected[case].items():
        tol = max(abs(e) * 2e-5, 1e-6 if q == "thermal_diffusion_factor" else 0.0)
        worst.append("%s %.1e (%.0f%% of tol)" % (q[:12], abs(got[q] - e) / max(abs(e), 1e-300), 100 * abs(got[q] - e) / tol))
    print("%s %s: %.0f s  %s" % (case, " ".join(args), dt, "  ".join(worst)), flush=True)
