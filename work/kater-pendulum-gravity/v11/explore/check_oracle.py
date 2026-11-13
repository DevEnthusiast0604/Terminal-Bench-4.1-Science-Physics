"""Run the oracle reduce.py on every session and compare with generate.truth (author's check, not shipped).

    python -B check_oracle.py <task_dir> [session ...]

Prints each quantity's relative error as a fraction of its tolerance (|err| / tol; above 1 fails) and the
wall time per session.
"""
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.join(sys.argv[1], "tests"))
import generate as G  # noqa: E402
import json  # noqa: E402

TOL = {"g_m_s2": 4e-4, "period": 1e-4, "radius_of_gyration_m": 1e-3, "amp": 2e-3}
task = sys.argv[1]
names = sys.argv[2:] or list(G.SESSIONS)
worst = 0.0
for name in names:
    folder = os.path.join(task, "environment/data/sessions" if name in G.EXAMPLES else "tests/cases", name)
    t0 = time.time()
    proc = subprocess.run([sys.executable, "-B", os.path.join(task, "solution", "reduce.py"), folder],
                          capture_output=True, text=True)
    dt = time.time() - t0
    if proc.returncode != 0:
        print(name, "FAILED rc", proc.returncode, proc.stderr[-2000:])
        continue
    got = json.loads(proc.stdout)
    want = G.truth(name)
    rows = [("g", got["g_m_s2"], want["g_m_s2"], TOL["g_m_s2"]),
            ("k", got["radius_of_gyration_m"], want["radius_of_gyration_m"], TOL["radius_of_gyration_m"])]
    rows += [("T_" + p, got["small_amplitude_period_s"][p], want["small_amplitude_period_s"][p], TOL["period"]) for p in "ab"]
    rows += [("P_" + r, got["run_periods_s"][r], want["run_periods_s"][r], TOL["period"]) for r in sorted(want["run_periods_s"])]
    rows += [("A_" + r, got["release_amplitude_rad"][r], want["release_amplitude_rad"][r], TOL["amp"]) for r in sorted(want["release_amplitude_rad"])]
    fr = [(lab, (h - w) / w / tol) for lab, h, w, tol in rows]
    worst_here = max(abs(f) for _, f in fr)
    worst = max(worst, worst_here) if name not in G.EXAMPLES else worst
    print("%s  %.1f s  worst %.3f of tolerance" % (name, dt, worst_here))
    print("   " + "  ".join("%s %+.3f" % (lab, f) for lab, f in fr))
    for line in proc.stderr.strip().splitlines():
        if line.startswith("camera"):
            print("   " + line)
print("worst over graded sessions: %.3f of tolerance" % worst)
