"""v11 design, second pass: v8's 511 keV line (H beta 2.75, M beta 11.75, M->H 31) and a new level X fed only by beta
decay, decaying to B (a clean line) and to Da (a weak line under the strong E->B line). Imports tests/generate.py for
TARGET, Walk and the efficiencies only; changes TARGET in memory, writes nothing. Run from the folder root.
Arguments: X energy, X beta feeding, branch to B, branch to Da."""
import importlib.util
import math
import sys
from collections import defaultdict

spec = importlib.util.spec_from_file_location("gen", "tasks/active/gamma-decay-scheme/tests/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

EX = float(sys.argv[1]) if len(sys.argv) > 1 else 2721.7
FEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.2
WB = float(sys.argv[3]) if len(sys.argv) > 3 else 55.0
WD = float(sys.argv[4]) if len(sys.argv) > 4 else 45.0

T = {}
for k, v in gen.TARGET.items():
    T[k] = v
    if k == "J":
        T["X"] = (EX, FEED, [("B", WB), ("Da", WD)])
T["H"] = (2581.6, 2.75, [("Da", 50), ("B", 35), ("C", 15)])
T["M"] = (3092.6, 11.75, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("H", 31)])
NEW = {("X", "B"), ("X", "Da")}

w = gen.Walk(T, isomer=gen.ISOMER_LEVEL)
strongest = max(w.intensity.values())
rel = {i: 100.0 * w.intensity[i] / strongest for i in range(len(w.lines))}
print("total beta feeding %.2f" % sum(v[1] for v in T.values()))
for i, (e, a, b) in sorted(enumerate(w.lines), key=lambda t: t[1][0]):
    print("%8.1f  %2s->%-2s  I %6.2f%s" % (e, a, b, rel[i], "   NEW" if (a, b) in NEW else ""))

idx = {(a, b): i for i, (e, a, b) in enumerate(w.lines)}
s, x = idx[("E", "B")], idx[("X", "Da")]
es, ex = w.lines[s][0], w.lines[x][0]
p = rel[x] / (rel[x] + rel[s])
sig = gen.fwhm(es) / 2.3548
print("1082 keV peak: E->B %.1f I %.2f, X->Da %.1f I %.2f, X->Da share %.3f, separation %.2f keV = %.2f sigma, "
      "width x%.3f, centroid shift %.3f keV"
      % (es, rel[s], ex, rel[x], p, es - ex, (es - ex) / sig, math.sqrt(1 + p * (1 - p) * ((es - ex) / sig) ** 2),
         -p * (es - ex)))

# Photopeak-photopeak pairs in two different crystals, prompt (the isomer is not between any of these).
both = defaultdict(float)
for table in (w.pairs,):
    for k, v in table.items():
        both[k] += v


def pair(l1, l2):
    i, j = idx[l1], idx[l2]
    v = both.get((min(i, j), max(i, j)), 0.0)
    return gen.N_PARENT * v * gen.OTHER * float(gen.eps_pp(w.lines[i][0]) * gen.eps_pp(w.lines[j][0]))


singles_1082 = gen.N_PARENT * (w.intensity[s] * float(gen.eps_pp(es)) + w.intensity[x] * float(gen.eps_pp(ex)))
print("singles photopeak counts in the 1082 keV peak: %.0f (X->Da %.0f)" % (singles_1082, gen.N_PARENT * w.intensity[x] * float(gen.eps_pp(ex))))
for name, l1, l2 in (("X->Da with Da->A (1322 gate)", ("X", "Da"), ("Da", "A")),
                     ("H->Da with Da->A", ("H", "Da"), ("Da", "A")),
                     ("I->Da with Da->A", ("I", "Da"), ("Da", "A")),
                     ("E->B with B->A (524 gate)", ("E", "B"), ("B", "A")),
                     ("X->B with B->A", ("X", "B"), ("B", "A")),
                     ("X->Da with A->g", ("X", "Da"), ("A", "g")),
                     ("E->B with A->g", ("E", "B"), ("A", "g"))):
    print("  %-30s %8.0f photopeak pairs" % (name, pair(l1, l2)))

# Peaks of any origin within 3 keV of a new line, and level differences of X that fall on a peak.
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
    close = sorted((abs(q - e), q, what) for q, what in peaks if abs(q - e) < 3.0 and not what.endswith("%s->%s" % (a, b)))
    print("new %s->%s %.1f keV: within 3 keV: %s" % (a, b, e, ["%.1f %s" % (q, what) for _, q, what in close]))
levels = dict((k, v[0]) for k, v in T.items())
levels["g"] = 0.0
print("level differences of X within 1.5 keV of a peak:")
for k, v in sorted(levels.items(), key=lambda t: t[1]):
    if k == "X":
        continue
    d = abs(EX - v)
    if d >= 60.0:
        hit = [(q, what) for q, what in peaks if abs(q - d) < 1.5]
        if hit:
            print("  X-%s %.1f: %s" % (k, d, ["%.1f %s" % h for h in hit]))
