"""Probe: how well does the shipped light curve pin planet b's impact parameter, and so its radius?

Uses the reference's own functions (solution/solve.py) on environment/data: the detrended light curve with the box
search's families masked, then the transit fit's chi-square at a fixed impact parameter, for a circular orbit and for
run 3's e = 0.042, w = -0.566. Prints b, k, R (Earth radii), chi-square above the best. Exploration only."""
import importlib.util
import math
import sys

import numpy as np
from scipy.optimize import least_squares

TASK = "tasks/active/rv-planet-census"
spec = importlib.util.spec_from_file_location("solve", TASK + "/solution/solve.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)

lc = S.table(TASK + "/environment/data/lightcurve.txt")
t, f = lc[:, 0], lc[:, 1]
star = S.notes(TASK + "/environment/data/NOTES.md")
fdil = 10 ** (-0.4 * 1.20)
print("star", {k: star[k] for k in sorted(star)})

fams = [
    {"kind": "binary", "P": 6.04485, "t0": 2460266.0191, "dur": 2.0 / 24},
    {"kind": "single", "t0": 2460270.8342, "dur": 5.0 / 24},
    {"kind": "planet", "P": 2.87532, "t0": 2460263.126, "dur": 1.66 / 24},
]
pre = np.zeros(len(t), bool)
excl = np.zeros(len(t), bool)
for fm in fams:
    pre |= S.family_mask(t, fm, pad=0.03)
    if fm["kind"] == "binary":
        excl |= S.family_mask(t, fm, pad=0.03)
r = S.detrend(t, f, pre)
sigma = float(1.4826 * np.median(np.abs(r[~pre] - np.median(r[~pre]))))
print("sigma ppm %.1f" % (1e6 * sigma))

P0, tc_ref = 2.87623, 2460289.0082
tc0 = tc_ref + round((float(np.median(t)) - tc_ref) / P0) * P0
R_E = star["radius"] * S.R_SUN / S.R_EARTH


def profile(e, w, label):
    aR = S.a_over_r(P0, star)
    win = (np.abs(((t - tc0) / P0 + 0.5) % 1.0 - 0.5) * P0 < 0.6) & ~excl
    tt, yy = t[win], (1 + fdil) * r[win]
    sig = (1 + fdil) * sigma
    rows = []
    for b in (0.0, 0.2, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85):
        def resid(x):
            m = S.transit_model(tt, P0 + x[2], tc0 + x[1], e, w, aR, x[0], b, star["u1"], star["u2"])
            if np.any(np.isnan(m)):
                return np.full(len(tt), 1e3)
            return (yy + m) / sig
        res = least_squares(resid, [0.022, 0.0, 0.0], bounds=([0.002, -0.05, -0.003], [0.3, 0.05, 0.003]),
                            x_scale=[0.005, 0.002, 1e-4])
        rows.append((b, res.x[0], 2 * res.cost))
    best = min(c for _, _, c in rows)
    print(label, "a/R* %.3f" % aR)
    for b, k, c in rows:
        print("   b %.2f  k %.5f  R %.3f (%+.1f%%)  chi2-min %.2f" % (b, k, k * R_E, 100 * (k * R_E / 1.62 - 1), c - best))


profile(0.0, 0.0, "circular")
profile(0.042, -0.566, "e 0.042 w -0.566")
sys.stdout.flush()
