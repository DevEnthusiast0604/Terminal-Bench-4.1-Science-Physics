"""v13 design, audit: the generator's own design audit on the changed scheme (v11's X dropped, Y added), plus the
precision of the ways to measure the hidden line, with Poisson noise. Imports tests/generate.py read-only; writes
nothing. Run from the folder root. Arguments: Y beta feeding, branch to B, branch to A, Monte Carlo trials."""
import importlib.util
import math
import sys

import numpy as np
from scipy.optimize import least_squares

spec = importlib.util.spec_from_file_location("gen", "tasks/active/gamma-decay-scheme/tests/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

FEED = float(sys.argv[1]) if len(sys.argv) > 1 else 1.75
WB = float(sys.argv[2]) if len(sys.argv) > 2 else 50.0
WA = float(sys.argv[3]) if len(sys.argv) > 3 else 50.0
TRIALS = int(sys.argv[4]) if len(sys.argv) > 4 else 200
EH = 1081.4
EY = round(318.4 + EH, 1)

T = {}
for k, v in gen.TARGET.items():
    if k == "X":
        continue
    T[k] = v
    if k == "C":
        T["Y"] = (EY, FEED, [("B", WB), ("A", WA)])
gen.TARGET.clear()
gen.TARGET.update(T)
w = gen.Walk(gen.TARGET, gen.ISOMER_LEVEL)
strongest = max(w.intensity.values())
rel = {round(w.lines[i][0], 1): 100.0 * p / strongest for i, p in w.intensity.items()}
gen.audit(w, w.lines, rel)

# The singles of the whole run near 1082 keV, with every component, and a Poisson draw per trial.
fp, fd, fc, phi = gen.cycle_fractions()
parent = gen.singles_of(w, gen.N_PARENT, gen.EDGES_RUN)
mid = 0.5 * (gen.EDGES_RUN[:-1] + gen.EDGES_RUN[1:])
brems = np.exp(-mid / 220.0) * np.diff(gen.EDGES_RUN) * gen.threshold_cut(gen.EDGES_RUN)
parent = parent + 0.02 * gen.N_PARENT * brems / brems.sum()
daughter = gen.singles_of(gen.Walk(gen.GRANDDAUGHTER), gen.N_PARENT * phi, gen.EDGES_RUN)
isobar = gen.singles_of(gen.Walk(gen.ISOBAR), gen.N_PARENT * gen.ISOBAR_DECAYS_PER_PARENT, gen.EDGES_RUN)
room = gen.room_singles(gen.T_RUN, gen.EDGES_RUN)
expect = parent + daughter + isobar + room
idx = {(a, b): i for i, (e, a, b) in enumerate(w.lines)}
s, h = idx[("E", "B")], idx[("Y", "A")]
es, eh = w.lines[s][0], w.lines[h][0]
n_s = gen.N_PARENT * w.intensity[s] * float(gen.eps_pp(es))
n_h = gen.N_PARENT * w.intensity[h] * float(gen.eps_pp(eh))
print("\nhidden %.1f I %.2f (photopeak %.0f), strong %.1f I %.2f (photopeak %.0f)" % (eh, rel[round(eh, 1)], n_h, es,
                                                                                    rel[round(es, 1)], n_s))
edges = gen.EDGES_RUN
win = np.where((mid > es - 10.0) & (mid < es + 8.0))[0]
x = mid[win]
dx = np.diff(edges)[win]
iso_e = 1011.4            # an isolated strong line near by, for the tail parameters
iwin = np.where((mid > iso_e - 10.0) & (mid < iso_e + 8.0))[0]
ix = mid[iwin]


def tailed(xx, ed, e, area, sig, frac, tau_k):
    from scipy.special import erf, erfc
    g = np.diff(0.5 * (1.0 + erf((ed - e) / (sig * math.sqrt(2.0))))) * (1.0 - frac)
    tau = tau_k * sig
    z = xx - e
    t = np.exp(np.clip(z / tau + sig * sig / (2.0 * tau * tau), -700, 700)) * erfc((z / sig + sig / tau) / math.sqrt(2.0)) \
        * np.diff(ed) / (2.0 * tau)
    return area * (g + frac * t)


def gauss(xx, ed, e, area, sig):
    from scipy.special import erf
    return area * np.diff(0.5 * (1.0 + erf((ed - e) / (sig * math.sqrt(2.0)))))


ed = edges[win[0]:win[-1] + 2]
ied = edges[iwin[0]:iwin[-1] + 2]
rng = np.random.default_rng(7)
res = {"tail": [], "gauss_fixed": [], "gauss_free": []}
for trial in range(TRIALS):
    y = rng.poisson(expect[win]).astype(float)
    iy = rng.poisson(expect[iwin]).astype(float)
    # Tail parameters from the isolated line: Gaussian plus exponential tail on a straight background.
    def r_iso(q):
        return (tailed(ix, ied, q[0], q[1], q[2], q[3], q[4]) + q[5] + q[6] * (ix - iso_e) - iy) / np.sqrt(np.maximum(iy, 1.0))
    qi = least_squares(r_iso, [iso_e, iy.sum(), 0.8, 0.05, 1.0, iy[:5].mean(), 0.0],
                       bounds=([iso_e - 2, 0, 0.3, 0.0, 0.3, -np.inf, -np.inf], [iso_e + 2, np.inf, 3.0, 0.5, 5.0, np.inf, np.inf])).x
    sig_scale = qi[2] / (gen.fwhm(iso_e) / 2.3548)
    sig = sig_scale * gen.fwhm(es) / 2.3548
    frac, tauk = qi[3], qi[4]
    if trial == 0:
        print("isolated-line fit: sigma x%.3f, tail fraction %.3f, tau %.2f sigma" % (sig_scale, frac, tauk))

    def r_tail(q):
        m = tailed(x, ed, es, q[0], sig, frac, tauk) + tailed(x, ed, eh, q[1], sig, frac, tauk) + q[2] + q[3] * (x - es)
        return (m - y) / np.sqrt(np.maximum(y, 1.0))
    q = least_squares(r_tail, [n_s, n_h, y[:5].mean(), 0.0]).x
    res["tail"].append(q[1] / n_h - 1.0)

    def r_gf(q):
        m = gauss(x, ed, es, q[0], sig) + gauss(x, ed, eh, q[1], sig) + q[2] + q[3] * (x - es)
        return (m - y) / np.sqrt(np.maximum(y, 1.0))
    q = least_squares(r_gf, [n_s, n_h, y[:5].mean(), 0.0]).x
    res["gauss_fixed"].append(q[1] / n_h - 1.0)

    def r_gw(q):
        m = gauss(x, ed, es, q[0], q[4]) + gauss(x, ed, eh, q[1], q[4]) + q[2] + q[3] * (x - es)
        return (m - y) / np.sqrt(np.maximum(y, 1.0))
    q = least_squares(r_gw, [n_s, n_h, y[:5].mean(), 0.0, sig], bounds=([0, -np.inf, -np.inf, -np.inf, 0.3],
                                                                         [np.inf, np.inf, np.inf, np.inf, 3.0])).x
    res["gauss_free"].append(q[1] / n_h - 1.0)
for k, v in res.items():
    v = np.array(v)
    print("%-12s hidden area: mean %+.1f%%, sd %.1f%%, within 25%%: %.0f%% of trials"
          % (k, 100.0 * v.mean(), 100.0 * v.std(), 100.0 * np.mean(np.abs(v) < 0.25)))
