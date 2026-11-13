"""v13 design: drop v11's level X (2721.7 keV) and add a level Y fed only by beta decay that decays to B by a clean line
and to A by a weak line hidden under E->B (1082.3 keV). The weak line's only coincidence partner is 318.4 keV, which
E->B shares, so no gate shows it alone. Imports tests/generate.py read-only; changes TARGET in memory, writes nothing.
Run from the folder root. Arguments: hidden energy (keV), Y beta feeding, branch to B, branch to A."""
import importlib.util
import math
import sys
from collections import defaultdict

import numpy as np
from scipy.optimize import least_squares

spec = importlib.util.spec_from_file_location("gen", "tasks/active/gamma-decay-scheme/tests/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

EH = float(sys.argv[1]) if len(sys.argv) > 1 else 1081.4
FEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.75
WB = float(sys.argv[3]) if len(sys.argv) > 3 else 50.0
WA = float(sys.argv[4]) if len(sys.argv) > 4 else 50.0
EY = round(318.4 + EH, 1)

T = {}
for k, v in gen.TARGET.items():
    if k == "X":
        continue
    T[k] = v
    if k == "C":
        T["Y"] = (EY, FEED, [("B", WB), ("A", WA)])
NEW = {("Y", "B"), ("Y", "A")}

w = gen.Walk(T, isomer=gen.ISOMER_LEVEL)
strongest = max(w.intensity.values())
rel = {i: 100.0 * w.intensity[i] / strongest for i in range(len(w.lines))}
print("Y at %.1f keV; total beta feeding %.2f; %d levels, %d lines" % (EY, sum(v[1] for v in T.values()), len(T) + 1, len(w.lines)))
for i, (e, a, b) in sorted(enumerate(w.lines), key=lambda t: t[1][0]):
    print("%8.1f  %2s->%-2s  I %6.2f%s" % (e, a, b, rel[i], "   NEW" if (a, b) in NEW else ""))

idx = {(a, b): i for i, (e, a, b) in enumerate(w.lines)}
s, h = idx[("E", "B")], idx[("Y", "A")]
es, eh = w.lines[s][0], w.lines[h][0]
p = rel[h] / (rel[h] + rel[s])
sig = gen.fwhm(es) / 2.3548
print("\n1082 keV peak: E->B %.1f I %.2f, Y->A %.1f I %.2f; hidden share %.3f; separation %.2f keV = %.2f sigma; "
      "Gaussian width x%.3f; centroid shift %.3f keV; E->B read as the whole peak: %+.1f%%"
      % (es, rel[s], eh, rel[h], p, es - eh, (es - eh) / sig, math.sqrt(1 + p * (1 - p) * ((es - eh) / sig) ** 2),
         -p * (es - eh), 100.0 * rel[h] / rel[s]))

# Singles around the peak with the generator's own line shape, no noise: what a fit of two members gives.
edges = gen.EDGES_RUN
mid = 0.5 * (edges[:-1] + edges[1:])
win = (mid > es - 9.0) & (mid < es + 7.0)
n_s = gen.N_PARENT * w.intensity[s] * float(gen.eps_pp(es))
n_h = gen.N_PARENT * w.intensity[h] * float(gen.eps_pp(eh))
y = n_s * gen.peak(edges, es)[win] + n_h * gen.peak(edges, eh)[win]
x = mid[win]
dx = np.diff(edges)[win]


def gauss(e, area, sigma):
    return area * dx * np.exp(-0.5 * ((x - e) / sigma) ** 2) / (sigma * math.sqrt(2.0 * math.pi))


def shape(e, area):
    return area * gen.peak(edges, e)[win]


fit = least_squares(lambda q: (gauss(es, q[0], q[2]) + gauss(eh, q[1], q[2]) - y) / np.sqrt(y + 50.0),
                    [n_s, n_h, sig], bounds=([0, 0, 0.3], [np.inf, np.inf, 3.0]))
print("two Gaussians at fixed energies, common width free: hidden area %+.1f%%, strong %+.1f%%, width %.3f (sigma %.3f)"
      % (100.0 * (fit.x[1] / n_h - 1.0), 100.0 * (fit.x[0] / n_s - 1.0), fit.x[2], sig))
iso = [e for e in (941.3, 1150.9, 1219.8, 1302.9) if True]
fit = least_squares(lambda q: (gauss(es, q[0], sig) + gauss(eh, q[1], sig) - y) / np.sqrt(y + 50.0), [n_s, n_h],
                    bounds=([0, 0], [np.inf, np.inf]))
print("two Gaussians at fixed energies, width fixed at the resolution: hidden area %+.1f%%, strong %+.1f%%"
      % (100.0 * (fit.x[1] / n_h - 1.0), 100.0 * (fit.x[0] / n_s - 1.0)))
fit = least_squares(lambda q: (shape(es, q[0]) + shape(eh, q[1]) - y) / np.sqrt(y + 50.0), [n_s, n_h],
                    bounds=([0, 0], [np.inf, np.inf]))
print("two members with the true line shape: hidden area %+.1f%%" % (100.0 * (fit.x[1] / n_h - 1.0)))
one = least_squares(lambda q: (gauss(q[0], q[1], q[2]) - y) / np.sqrt(y + 50.0), [es, n_s + n_h, sig])
single = least_squares(lambda q: (gauss(q[0], q[1], q[2]) - n_s * gen.peak(edges, es)[win]) / np.sqrt(y + 50.0),
                       [es, n_s, sig])
print("one Gaussian: centroid %.3f, width %.3f; the same fit to E->B alone: width %.3f; ratio %.3f"
      % (one.x[0], one.x[2], single.x[2], one.x[2] / single.x[2]))
print("singles photopeak counts: E->B %.0f, Y->A %.0f" % (n_s, n_h))

# Coincidences of the 1082 keV peak with 318.4 and 524.3 keV, photopeak pairs in two crystals.
both = defaultdict(float)
for k, v in w.pairs.items():
    both[k] += v


def pair(l1, l2):
    i, j = idx[l1], idx[l2]
    v = both.get((min(i, j), max(i, j)), 0.0)
    return gen.N_PARENT * v * gen.OTHER * float(gen.eps_pp(w.lines[i][0]) * gen.eps_pp(w.lines[j][0]))


a318 = pair(("E", "B"), ("A", "g")) + pair(("Y", "A"), ("A", "g"))
a524 = pair(("E", "B"), ("B", "A"))
r_other = []
for feeder in (("C", "B"), ("H", "B"), ("L", "B"), ("Y", "B")):
    r_other.append(pair(feeder, ("A", "g")) / pair(feeder, ("B", "A")))
print("\n1082 peak in the 318.4 gate %.0f pairs (Y->A %.0f), in the 524.3 gate %.0f" % (a318, pair(("Y", "A"), ("A", "g")), a524))
print("ratio 318/524 for the 1082 peak %.4f; for the other feeders of B %s; excess %.1f%%"
      % (a318 / a524, " ".join("%.4f" % r for r in r_other), 100.0 * (a318 / a524 / r_other[0] - 1.0)))
sh = pair(("Y", "A"), ("A", "g")) / a318
print("1082 centroid in the 318.4 gate shifts by %.3f keV against the 524.3 gate; statistical error about %.3f keV"
      % (-sh * (es - eh), sig * math.sqrt(1.0 / a318 + 1.0 / a524)))
print("Y->B with B->A %.0f pairs; Y->B with A->g %.0f" % (pair(("Y", "B"), ("B", "A")), pair(("Y", "B"), ("A", "g"))))

# Every level difference that falls within 1.5 keV of a peak of any origin.
peaks = [(e, "line %s->%s" % (a, b)) for e, a, b in w.lines]
allp = defaultdict(float)
for table in (w.pairs, w.straddle):
    for k, v in table.items():
        allp[k] += v
for (i, j), v in allp.items():
    e = w.lines[i][0] + w.lines[j][0]
    size = 100.0 * v / strongest * float(gen.eps_pp(w.lines[i][0]) * gen.eps_pp(w.lines[j][0])) * gen.SAME / float(gen.eps_pp(e))
    if size >= 0.05:
        peaks.append((e, "sum %.1f+%.1f (I %.2f)" % (w.lines[i][0], w.lines[j][0], size)))
for e, a, b in w.lines:
    if e > 1022.0:
        peaks += [(e - 511.0, "SE of %.1f" % e), (e - 1022.0, "DE of %.1f" % e)]
peaks += [(e, "room") for e in gen.ROOM] + [(511.0, "annihilation")]
for table, name in ((gen.GRANDDAUGHTER, "daughter"), (gen.ISOBAR, "isobar")):
    en = {k: v[0] for k, v in table.items()}
    en["g"] = 0.0
    for k, (e0, _, br) in table.items():
        for f, _ in br:
            peaks.append((e0 - en[f], name))
for a, b in sorted(NEW):
    e = w.lines[idx[(a, b)]][0]
    close = sorted((abs(q - e), q, what) for q, what in peaks if abs(q - e) < 6.0 and not what.endswith("%s->%s" % (a, b)))
    print("new %s->%s %.1f keV: within 6 keV: %s" % (a, b, e, ["%.1f %s" % (q, what) for _, q, what in close]))
levels = dict((k, v[0]) for k, v in T.items())
levels["g"] = 0.0
real = {(a, b) for _, a, b in w.lines}
print("level differences without a transition within 1.0 keV of a peak:")
names = sorted(levels, key=levels.get)
for i, a in enumerate(names):
    for b in names[:i]:
        if (a, b) in real:
            continue
        d = levels[a] - levels[b]
        if d < 60.0:
            continue
        hit = [(q, what) for q, what in peaks if abs(q - d) < 1.0]
        if hit and ("Y" in (a, b)):
            print("  %s-%s %.1f: %s" % (a, b, d, ["%.1f %s" % hh for hh in hit]))
