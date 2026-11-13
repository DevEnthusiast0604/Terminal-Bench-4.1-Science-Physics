"""v11 design check: a new level X fed from M and decaying to B (clean) and to Da (hidden 0.8 keV under E->B), with the
511 keV line back at v8's strength. Imports tests/generate.py for TARGET, Walk and the efficiencies only; changes TARGET
in memory. Prints every line's relative intensity, the width the 1082 keV peak would show, and every peak of any
origin within 3 keV of a new line. Run from the folder root."""
import importlib.util
import math
from collections import defaultdict

spec = importlib.util.spec_from_file_location("gen", "tasks/active/gamma-decay-scheme/tests/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

T = dict(gen.TARGET)
EX = 1640.3 + 1081.5
T["H"] = (2581.6, 2.75, [("Da", 50), ("B", 35), ("C", 15)])
T["M"] = (3092.6, 11.75, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("H", 31), ("X", 12)])
T["X"] = (EX, 1.0, [("B", 60), ("Da", 40)])
NEW = {("M", "X"), ("X", "B"), ("X", "Da")}

w = gen.Walk(T, isomer=gen.ISOMER_LEVEL)
strongest = max(w.intensity.values())
rel = {i: 100.0 * w.intensity[i] / strongest for i in range(len(w.lines))}
for i, (e, a, b) in sorted(enumerate(w.lines), key=lambda t: t[1][0]):
    print("%8.1f  %2s->%-2s  I %6.2f%s" % (e, a, b, rel[i], "   NEW" if (a, b) in NEW else ""))

idx = {(a, b): i for i, (e, a, b) in enumerate(w.lines)}
s, x = idx[("E", "B")], idx[("X", "Da")]
es, ex = w.lines[s][0], w.lines[x][0]
p = rel[x] / (rel[x] + rel[s])
sig = gen.fwhm(es) / 2.3548
print("1082 keV peak: S %.1f I %.2f, W %.1f I %.2f, W share %.3f, separation %.2f keV = %.2f sigma, width x%.3f"
      % (es, rel[s], ex, rel[x], p, es - ex, (es - ex) / sig, math.sqrt(1 + p * (1 - p) * ((es - ex) / sig) ** 2)))

# Peaks of any origin: lines, cascade sums (I >= 0.05), escapes of lines above 1022 keV, room, daughter, isobar.
peaks = [(e, "line %s->%s" % (a, b)) for e, a, b in w.lines]
both = defaultdict(float)
for table in (w.pairs, w.straddle):
    for k, v in table.items():
        both[k] += v
for (i, j), v in both.items():
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
print("level differences of X within 1.5 keV of a peak (decoys):")
for k, v in sorted(levels.items(), key=lambda t: t[1]):
    if k == "X":
        continue
    d = abs(EX - v)
    if d >= 60.0:
        hit = [(q, what) for q, what in peaks if abs(q - d) < 1.5]
        if hit:
            print("  X-%s %.1f: %s" % (k, d, ["%.1f %s" % h for h in hit]))
