"""The oracle with the stall detectors of the v10 pass@3 attempts swapped in (author's check, not shipped).

    python -B wrong_stalls.py <task_dir> [session ...]

D1 (attempt 1): per-second rate below its median by 1.5 frames/s.  D2 (attempt 2): interval count below
median rate x interval by 1.5 frames.  D3 (attempt 3): round(count - rate x interval) < -1.  Each is
followed by the oracle's own piecewise clock fit, without re-detection. Prints each graded quantity that
leaves its tolerance (|err| / tol > 1), and the stalls each detector misses.
"""
import importlib.util
import os
import sys

import numpy as np

task = sys.argv[1]
sys.path.insert(0, os.path.join(task, "tests"))
import generate as G  # noqa: E402

spec = importlib.util.spec_from_file_location("reduce", os.path.join(task, "solution", "reduce.py"))
R = importlib.util.module_from_spec(spec)
spec.loader.exec_module(R)
ORIGINAL = R.time_map


def detector(kind):
    def cuts_of(s, f):
        ds, df = np.diff(s), np.diff(f)
        if kind == "D1":
            rates = df / ds
            return np.flatnonzero(rates < np.median(rates) - 1.5) + 1
        rate = float(np.median(df / ds))
        if kind == "D2":
            return np.flatnonzero(df - rate * ds < -1.5) + 1
        rough = np.flatnonzero(df - rate * ds < -2.5) + 1
        rate, _, _ = R.fit_clock(s, f, rough)
        return np.flatnonzero(np.round(df - rate * ds) < -1) + 1

    def time_map(frame_idx, c0, gps, sync_ctr):
        f = ((sync_ctr - c0) % R.COUNTER_MOD).astype(float)
        order = np.argsort(gps)
        s = (gps - gps[order[0]]).astype(float)[order]
        f = f[order]
        cuts = cuts_of(s, f)
        rate, groups, intercepts = R.fit_clock(s, f, cuts)
        t = np.empty(len(frame_idx))
        valid = np.ones(len(frame_idx), dtype=bool)
        edges = [(f[a[-1]], f[b[0]]) for a, b in zip(groups[:-1], groups[1:])]
        bounds = [-np.inf] + [0.5 * (lo + hi) for lo, hi in edges] + [np.inf]
        for g, icpt in enumerate(intercepts):
            sel = (frame_idx >= bounds[g]) & (frame_idx < bounds[g + 1])
            t[sel] = (frame_idx[sel] - icpt) / rate
        for lo, hi in edges:
            valid &= ~((frame_idx >= lo - 1) & (frame_idx <= hi + 1))
        time_map.ncuts.append(len(cuts))
        return t, valid
    time_map.ncuts = []
    return time_map


TOL = {"g_m_s2": 4e-4, "period": 1e-4, "radius_of_gyration_m": 1e-3, "amp": 2e-3}
names = sys.argv[2:] or [n for n in G.SESSIONS if n not in G.EXAMPLES]
for name in names:
    folder = os.path.join(task, "environment/data/sessions" if name in G.EXAMPLES else "tests/cases", name)
    want = G.truth(name)
    nstall = [len(spec_[5]) for _, spec_ in sorted(G.SESSIONS[name]["runs"].items())]
    for kind in ("D1", "D2", "D3"):
        R.time_map = detector(kind)
        got = R.reduce_session(folder)
        ncuts = R.time_map.ncuts
        R.time_map = ORIGINAL
        bad = []
        if abs(got["g_m_s2"] / want["g_m_s2"] - 1) > TOL["g_m_s2"]:
            bad.append("g %.2f" % ((got["g_m_s2"] / want["g_m_s2"] - 1) / TOL["g_m_s2"]))
        if abs(got["radius_of_gyration_m"] / want["radius_of_gyration_m"] - 1) > TOL["radius_of_gyration_m"]:
            bad.append("k")
        for p in "ab":
            e = (got["small_amplitude_period_s"][p] / want["small_amplitude_period_s"][p] - 1) / TOL["period"]
            if abs(e) > 1:
                bad.append("T_%s %.2f" % (p, e))
        for r in sorted(want["run_periods_s"]):
            e = (got["run_periods_s"][r] / want["run_periods_s"][r] - 1) / TOL["period"]
            if abs(e) > 1:
                bad.append("P_%s %.2f" % (r, e))
        for r in sorted(want["release_amplitude_rad"]):
            e = (got["release_amplitude_rad"][r] / want["release_amplitude_rad"][r] - 1) / TOL["amp"]
            if abs(e) > 1:
                bad.append("A_%s %.2f" % (r, e))
        print("%s %s cuts per run %s (stalls %s): %s" % (name, kind, ncuts[-len(nstall):], nstall,
                                                        "FAILS " + ", ".join(bad) if bad else "passes"))
        print("    run periods / tol: " + "  ".join("%s %+.2f" % (r, (got["run_periods_s"][r] / want["run_periods_s"][r] - 1) / TOL["period"])
                                                 for r in sorted(want["run_periods_s"])))
