"""v14 design: more beta feeding to Y (1399.8 keV) so that 557.1 keV is a regular line, and a somewhat stronger hidden
1081.4 keV line. For each candidate (feeding, branch to B, branch to A): the intensities, how 557.1 keV stands in the
singles next to 551.8 keV and against other weak lines, how much the 1082 keV peak widens, and what an agent's ways of
measuring the hidden line give, on Poisson draws of the whole run's singles. Imports tests/generate.py read-only and
writes nothing. Run from the folder root. Argument: trials per candidate."""
import importlib.util
import math
import sys

import numpy as np
from scipy.optimize import least_squares
from scipy.special import erf, erfc, erfcx

spec = importlib.util.spec_from_file_location("gen", "tasks/active/gamma-decay-scheme/tests/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

TRIALS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
CANDIDATES = [(1.9, 45, 55), (3.0, 55, 45), (3.4, 50, 50), (3.6, 55, 45), (4.0, 50, 50)]
SQ2 = math.sqrt(2.0)
edges = gen.EDGES_RUN
mid_all = 0.5 * (edges[:-1] + edges[1:])
fp, fd, fc, phi = gen.cycle_fractions()
brems = np.exp(-mid_all / 220.0) * np.diff(edges) * gen.threshold_cut(edges)
other = gen.singles_of(gen.Walk(gen.GRANDDAUGHTER), gen.N_PARENT * phi, edges) \
    + gen.singles_of(gen.Walk(gen.ISOBAR), gen.N_PARENT * gen.ISOBAR_DECAYS_PER_PARENT, edges) + gen.room_singles(gen.T_RUN, edges)


def fwhm_g(e):
    return 1.05 * float(gen.fwhm(e))


def tailed(ed, c, s, frac, tau_k):
    g = 0.5 * np.diff(erf((ed - c) / (s * SQ2)))
    mid = 0.5 * (ed[:-1] + ed[1:])
    tau = tau_k * s
    z = mid - c
    b = (z / s + s / tau) / SQ2
    t = np.where(b > 0.0, np.exp(-0.5 * (z / s) ** 2) * erfcx(np.maximum(b, 0.0)),
                 np.exp(np.minimum(z / tau + 0.5 * (s / tau) ** 2, 700.0)) * erfc(np.minimum(b, 0.0)))
    return (1.0 - frac) * g + frac * t * np.diff(ed) / (2.0 * tau)


def gauss(ed, c, s):
    return 0.5 * np.diff(erf((ed - c) / (s * SQ2)))


def window(total, lo_e, hi_e):
    lo = int(np.searchsorted(edges, lo_e))
    hi = int(np.searchsorted(edges, hi_e))
    ed = edges[lo:hi + 1]
    return ed, 0.5 * (ed[:-1] + ed[1:]), total[lo:hi].astype(float)


ISOLATED = [318.4, 435.4, 1011.4, 1302.9, 1489.6, 2018.7, 2774.2, 898.3]


def fit_single(total, e, shape="gauss", frac=0.0, tau_k=1.0):
    """One line, free centroid, area and width, on a straight background: the width over the resolution."""
    s0 = fwhm_g(e) / 2.3548
    ed, mid, y = window(total, e - 10.0 * s0, e + 7.0 * s0)
    wt = 1.0 / np.sqrt(np.maximum(y, 1.0))
    t = (mid - e) / (mid.max() - mid.min())

    def resid(q):
        f = gauss(ed, q[0], q[2]) if shape == "gauss" else tailed(ed, q[0], q[2], frac, tau_k)
        return (q[1] * f + q[3] + q[4] * t - y) * wt
    r = least_squares(resid, [e, y.sum(), s0, max(float(np.median(y[:4])), 0.0), 0.0],
                      bounds=([e - 2.0, 0.0, 0.3 * s0, -np.inf, -np.inf], [e + 2.0, np.inf, 3.0 * s0, np.inf, np.inf]))
    return float(r.x[0]), float(r.x[2] / s0)


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
        rows.append((float(r.x[3]), float(r.x[4]), float(r.x[2] / s0)))
    return tuple(float(np.median([r[k] for r in rows])) for k in range(3))


def fit_two(total, e_main, e_other, model, frac=0.0, tau_k=1.0, s_ratio=1.0, width_free=False):
    s = s_ratio * fwhm_g(e_main) / 2.3548
    ed, mid, y = window(total, min(e_main, e_other) - 12.0 * s, max(e_main, e_other) + 7.0 * s)
    wt = 1.0 / np.sqrt(np.maximum(y, 1.0))
    t = (mid - e_main) / (mid.max() - mid.min())
    if width_free:
        def resid(q):
            return (q[0] * gauss(ed, e_main, q[4]) + q[1] * gauss(ed, e_other, q[4]) + q[2] + q[3] * t - y) * wt
        r = least_squares(resid, [y.sum() * 0.85, y.sum() * 0.15, float(np.median(y[:4])), 0.0, s],
                          bounds=([0.0, -np.inf, -np.inf, -np.inf, 0.3 * s], [np.inf, np.inf, np.inf, np.inf, 3.0 * s]))
        return float(r.x[1] / (r.x[0] + r.x[1])), float(r.x[4] / s)

    def solve(dl):
        f = (lambda c: tailed(ed, c, s, frac, tau_k)) if model == "tail" else (lambda c: gauss(ed, c, s))
        d = np.column_stack([f(e_main + dl), f(e_other + dl), np.ones_like(mid), t])
        a = d * wt[:, None]
        beta = np.linalg.lstsq(a, y * wt, rcond=None)[0]
        return float(np.sum((y * wt - a @ beta) ** 2)), beta
    grid = np.arange(-0.3, 0.3001, 0.01)
    k = int(np.argmin([solve(dl)[0] for dl in grid]))
    beta = solve(float(grid[k]))[1]
    return float(beta[1] / (beta[0] + beta[1])), float(grid[k])


for feed, wb, wa in CANDIDATES:
    T = {}
    for k, v in gen.TARGET.items():
        if k == "Y":
            continue
        T[k] = v
        if k == "C":
            T["Y"] = (1399.8, feed, [("B", wb), ("A", wa)])
    w = gen.Walk(T, gen.ISOMER_LEVEL)
    top = max(w.intensity.values())
    rel = {(a, b): 100.0 * w.intensity[i] / top for i, (e, a, b) in enumerate(w.lines)}
    parent = gen.singles_of(w, gen.N_PARENT, edges)
    parent = parent + 0.02 * gen.N_PARENT * brems / brems.sum() + gen.N_PARENT * 3.0e-4 * gen.peak(edges, 511.0, 1.3)
    expect = parent + other
    truth = rel[("Y", "A")] / (rel[("Y", "A")] + rel[("E", "B")])
    # 557.1 keV against the singles beneath it, and the same for other weak lines.
    vis = {}
    for e, key in ((557.1, ("Y", "B")), (1092.0, ("H", "C")), (992.7, ("I", "Da")), (1606.6, ("E", "A")),
                   (867.5, ("K", "E"))):
        if key not in rel:
            continue
        s0 = float(gen.fwhm(e)) / 2.3548
        n_peak = gen.N_PARENT * w.intensity[[i for i, l in enumerate(w.lines) if (l[1], l[2]) == key][0]] * float(gen.eps_pp(e))
        lo, hi = int(np.searchsorted(edges, e - 1.5 * s0)), int(np.searchsorted(edges, e + 1.5 * s0))
        under = float(expect[lo:hi].sum()) - 0.87 * n_peak
        vis[e] = (rel[key], n_peak / math.sqrt(max(under, 1.0)))
    rng = np.random.default_rng(23)
    res = {"tail": [], "gauss_fixed": [], "gauss_free": [], "width_free": [], "single_width": [], "iso_width": []}
    for trial in range(TRIALS):
        total = rng.poisson(expect).astype(float)
        frac, tau_k, s_ratio = line_shape(total)
        res["tail"].append(fit_two(total, 1082.3, 1081.4, "tail", frac, tau_k, s_ratio)[0])
        res["gauss_fixed"].append(fit_two(total, 1082.3, 1081.4, "gauss", s_ratio=s_ratio)[0])
        sh, wr = fit_two(total, 1082.3, 1081.4, "gauss", width_free=True)
        res["gauss_free"].append(sh)
        res["width_free"].append(wr)
        res["single_width"].append(fit_single(total, 1082.2)[1])
        res["iso_width"].append(np.median([fit_single(total, e)[1] for e in (1011.4, 1150.9, 941.3, 1302.9)]))
    print("feed %.1f, B %d / A %d: 557.1 I %.2f, hidden I %.2f under E->B I %.2f, true share %.4f; 551.8 I %.2f"
          % (feed, wb, wa, rel[("Y", "B")], rel[("Y", "A")], rel[("E", "B")], truth, rel[("J", "G")]))
    print("  peak counts over sqrt(counts beneath): %s" % ", ".join("%.1f keV (I %.2f) %.0f" % (e, v[0], v[1])
                                                                  for e, v in sorted(vis.items())))
    for k in ("tail", "gauss_fixed", "gauss_free"):
        v = np.array(res[k])
        print("  share by %-11s mean %.4f sd %.4f -> I bias %+.1f%%, within 25%% in %.0f%% of trials"
              % (k, v.mean(), v.std(), 100.0 * (v.mean() / truth - 1.0), 100.0 * np.mean(np.abs(v / truth - 1.0) < 0.25)))
    print("  one Gaussian on the 1082 peak: width %.3f of the resolution (lines standing alone %.3f); two-Gaussian free "
          "width %.3f" % (np.mean(res["single_width"]), np.mean(res["iso_width"]), np.mean(res["width_free"])))
