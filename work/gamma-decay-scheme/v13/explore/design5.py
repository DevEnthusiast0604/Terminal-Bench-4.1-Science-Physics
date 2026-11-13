"""v13 design, the reference's planned hidden-member test on simulated singles: tail parameters from isolated lines,
then each level difference near a strong line fitted as a second member (common shift free), and made-up members
next to isolated lines for the systematic floor. Imports tests/generate.py read-only; writes nothing. Run from the
folder root. Arguments: trials, Y beta feeding, branch to B, branch to A."""
import importlib.util
import math
import sys

import numpy as np
from scipy.optimize import least_squares
from scipy.special import erf, erfc, erfcx

spec = importlib.util.spec_from_file_location("gen", "tasks/active/gamma-decay-scheme/tests/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 20
FEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.9
WB = float(sys.argv[3]) if len(sys.argv) > 3 else 45.0
WA = float(sys.argv[4]) if len(sys.argv) > 4 else 55.0
SQ2 = math.sqrt(2.0)

T = {}
for k, v in gen.TARGET.items():
    if k == "X":
        continue
    T[k] = v
    if k == "C":
        T["Y"] = (1399.8, FEED, [("B", WB), ("A", WA)])
w = gen.Walk(T, gen.ISOMER_LEVEL)
top = max(w.intensity.values())
rel = {(a, b): 100.0 * w.intensity[i] / top for i, (e, a, b) in enumerate(w.lines)}
fp, fd, fc, phi = gen.cycle_fractions()
edges = gen.EDGES_RUN
mid_all = 0.5 * (edges[:-1] + edges[1:])
parent = gen.singles_of(w, gen.N_PARENT, edges)
brems = np.exp(-mid_all / 220.0) * np.diff(edges) * gen.threshold_cut(edges)
parent = parent + 0.02 * gen.N_PARENT * brems / brems.sum() + gen.N_PARENT * 3.0e-4 * gen.peak(edges, 511.0, 1.3)
expect = parent + gen.singles_of(gen.Walk(gen.GRANDDAUGHTER), gen.N_PARENT * phi, edges) \
    + gen.singles_of(gen.Walk(gen.ISOBAR), gen.N_PARENT * gen.ISOBAR_DECAYS_PER_PARENT, edges) + gen.room_singles(gen.T_RUN, edges)


def fwhm_g(e):
    return 1.05 * float(gen.fwhm(e))      # what Gaussian fits to the room lines give


def tailed(ed, c, s, frac, tau_k):
    g = 0.5 * np.diff(erf((ed - c) / (s * SQ2)))
    mid = 0.5 * (ed[:-1] + ed[1:])
    tau = tau_k * s
    z = mid - c
    b = (z / s + s / tau) / SQ2
    t = np.where(b > 0.0, np.exp(-0.5 * (z / s) ** 2) * erfcx(np.maximum(b, 0.0)),
                 np.exp(np.minimum(z / tau + 0.5 * (s / tau) ** 2, 700.0)) * erfc(np.minimum(b, 0.0)))
    return (1.0 - frac) * g + frac * t * np.diff(ed) / (2.0 * tau)


def window(total, lo_e, hi_e):
    lo = int(np.searchsorted(edges, lo_e))
    hi = int(np.searchsorted(edges, hi_e))
    ed = edges[lo:hi + 1]
    return ed, 0.5 * (ed[:-1] + ed[1:]), total[lo:hi].astype(float)


ISOLATED = [318.4, 435.4, 1011.4, 1302.9, 1489.6, 2018.7, 2774.2, 898.3]


def line_shape(total):
    rows = []
    for e in ISOLATED:
        s0 = fwhm_g(e) / 2.3548
        ed, mid, y = window(total, e - 12.0 * s0, e + 7.0 * s0)
        wt = 1.0 / np.sqrt(np.maximum(y, 1.0))
        t = (mid - e) / (mid.max() - mid.min())

        def resid(q):
            return (q[1] * tailed(ed, q[0], q[2], q[3], q[4]) + q[5] + q[6] * t - y) * wt
        r = least_squares(resid, [e, y.sum(), s0, 0.05, 1.5, max(float(np.median(y[:4])), 0.0), 0.0],
                          bounds=([e - 1.0, 0.0, 0.5 * s0, 0.0, 0.3, -np.inf, -np.inf],
                                  [e + 1.0, np.inf, 2.0 * s0, 0.4, 6.0, np.inf, np.inf]))
        rows.append((float(r.x[0]), float(r.x[3]), float(r.x[4]), float(r.x[2] / s0)))
    return (float(np.median([r[1] for r in rows])), float(np.median([r[2] for r in rows])),
            float(np.median([r[3] for r in rows])), rows)


def fit_two(total, e_main, e_other, frac, tau_k, s_ratio, shift_free=True):
    s = s_ratio * fwhm_g(e_main) / 2.3548
    ed, mid, y = window(total, min(e_main, e_other) - 12.0 * s, max(e_main, e_other) + 7.0 * s)
    wt = 1.0 / np.sqrt(np.maximum(y, 1.0))
    t = (mid - e_main) / (mid.max() - mid.min())

    def solve(dl):
        d = np.column_stack([tailed(ed, e_main + dl, s, frac, tau_k), tailed(ed, e_other + dl, s, frac, tau_k),
                             np.ones_like(mid), t])
        a = d * wt[:, None]
        beta = np.linalg.lstsq(a, y * wt, rcond=None)[0]
        return float(np.sum((y * wt - a @ beta) ** 2)), beta, a
    if shift_free:
        grid = np.arange(-0.3, 0.3001, 0.005)
        chis = [solve(dl)[0] for dl in grid]
        k = int(np.argmin(chis))
        dl = float(grid[k])
        # Error of the second area with the shift free: profile over the shift.
        chi0, beta, a = solve(dl)
        inside = [solve(g)[1][1] for g, c in zip(grid, chis) if c < chis[k] + 1.0 * max(chi0 / (len(y) - 5), 1.0)]
        prof = 0.5 * (max(inside) - min(inside)) if len(inside) > 1 else 0.0
    else:
        dl, prof = 0.0, 0.0
        chi0, beta, a = solve(0.0)
    cov = np.linalg.pinv(a.T @ a) * max(chi0 / max(len(y) - 5, 1), 1.0)
    err = math.hypot(math.sqrt(max(cov[1, 1], 0.0)), prof)
    return float(beta[0]), float(beta[1]), err, dl


CANDS = [("Y-A", 1081.4, 1082.3), ("E-Y", 525.2, 524.3), ("H-Db", 940.0, 941.3), ("K-Da", 1152.2, 1150.9)]
rng = np.random.default_rng(11)
res = {c[0]: [] for c in CANDS}
res_fixed = []
phant = []
for trial in range(TRIALS):
    total = rng.poisson(expect).astype(float)
    frac, tau_k, s_ratio, rows = line_shape(total)
    if trial == 0:
        print("tail fraction %.3f (0.08), slope %.2f sigma (1.3), sigma x%.3f; per line: %s"
              % (frac, tau_k, s_ratio, " ".join("%.0f:%.3f/%.2f" % (r[0], r[1], r[2]) for r in rows)))
    for name, d, e_main in CANDS:
        a_m, a_c, err, dl = fit_two(total, e_main, d, frac, tau_k, s_ratio)
        res[name].append((a_c / (a_m + a_c), err / (a_m + a_c), dl))
    a_m, a_c, err, dl = fit_two(total, 1082.3, 1081.4, frac, tau_k, s_ratio, shift_free=False)
    res_fixed.append(a_c / (a_m + a_c))
    for (c, _, _, _) in rows:
        for off in (-1.3, -0.9, 0.9, 1.3):
            a_m, a_c, err, dl = fit_two(total, c, c + off, frac, tau_k, s_ratio)
            phant.append(a_c / (a_m + a_c))
truth = rel[("Y", "A")] / (rel[("Y", "A")] + rel[("E", "B")])
print("true hidden share %.4f (I %.2f under I %.2f)" % (truth, rel[("Y", "A")], rel[("E", "B")]))
for name, v in res.items():
    v = np.array(v)
    print("%-5s share mean %.4f sd %.4f; quoted error mean %.4f; shift mean %+.3f; significance mean %.1f"
          % (name, v[:, 0].mean(), v[:, 0].std(), v[:, 1].mean(), v[:, 2].mean(), (v[:, 0] / v[:, 1]).mean()))
print("Y-A with the energies fixed: share mean %.4f sd %.4f" % (np.mean(res_fixed), np.std(res_fixed)))
phant = np.array(phant)
print("made-up members next to isolated lines: rms share %.4f, largest %.4f" % (np.sqrt(np.mean(phant ** 2)), np.abs(phant).max()))
