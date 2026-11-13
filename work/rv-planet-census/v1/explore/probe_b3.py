"""Probe 2: planet b's chi-square against impact parameter without optimizer trouble.

For each fixed b: a grid in the mid-time offset (period fixed at the photometric one), the depth scale solved
linearly at each grid point (one refinement of k), the minimum over the grid. Circular orbit and run 3's e, w.
Also the same for planet e's single transit with run 3's orbit (e 0.419, w 0.890) and the true one (e 0.31)."""
import importlib.util
import math

import numpy as np

TASK = "tasks/active/rv-planet-census"
spec = importlib.util.spec_from_file_location("solve", TASK + "/solution/solve.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)

lc = S.table(TASK + "/environment/data/lightcurve.txt")
t, f = lc[:, 0], lc[:, 1]
star = S.notes(TASK + "/environment/data/NOTES.md")
fdil = 10 ** (-0.4 * 1.20)
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
R_E = star["radius"] * S.R_SUN / S.R_EARTH


def scan(P0, tc0, e, w, k0, bs, dts, R_true, label, half=0.6):
    aR = S.a_over_r(P0, star)
    win = (np.abs(((t - tc0) / P0 + 0.5) % 1.0 - 0.5) * P0 < half) & ~excl
    tt, yy = t[win], (1 + fdil) * r[win]
    sig = (1 + fdil) * sigma
    print(label, "a/R* %.3f, points %d, sigma %.1f ppm" % (aR, len(tt), 1e6 * sigma))
    rows = []
    for b in bs:
        best = None
        for dt in dts:
            k = k0
            for _ in range(2):
                m = S.transit_model(tt, P0, tc0 + dt, e, w, aR, k, b, star["u1"], star["u2"])
                if np.any(np.isnan(m)) or not np.any(m > 0):
                    break
                A = -float(np.dot(yy, m) / np.dot(m, m))
                k = k * math.sqrt(max(A, 1e-6))
            else:
                m = S.transit_model(tt, P0, tc0 + dt, e, w, aR, k, b, star["u1"], star["u2"])
                c = float(np.sum(((yy + m) / sig) ** 2))
                if best is None or c < best[0]:
                    best = (c, k, dt)
        rows.append((b,) + best)
    cmin = min(x[1] for x in rows)
    for b, c, k, dt in rows:
        print("   b %.2f  k %.5f  R %.3f (%+.1f%%)  dt %+.1f min  chi2-min %.2f"
              % (b, k, k * R_E, 100 * (k * R_E / R_true - 1), dt * 1440, c - cmin))


P0, tc_ref = 2.87623, 2460289.0082
tc0 = tc_ref + round((float(np.median(t)) - tc_ref) / P0) * P0
bs = (0.0, 0.2, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8)
dts = np.arange(-18.0, -4.99, 0.5) / 1440
scan(P0, tc0, 0.0, 0.0, 0.0212, bs, dts, 1.62, "planet b, circular")
scan(P0, tc0, 0.042, -0.566, 0.0212, bs, dts, 1.62, "planet b, e 0.042 w -0.566")

raise SystemExit
# planet e: the single dip, the orbit's period from the velocities
dts_e = np.arange(-20.0, 20.01, 1.0) / 1440
bs_e = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
scan(114.29274, 2460270.8375, 0.419, 0.890, 0.039, bs_e, dts_e, 2.95, "planet e, run 3 orbit (e 0.419 w 0.890)")
