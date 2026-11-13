"""v11 design: the photopeak loss of each line to same-crystal summing (summing-out), the generator's own formula, and
what it does to a relative intensity read without a correction. Imports tests/generate.py for TARGET, Walk and the
efficiencies only. Optional argument: a factor on the array efficiency (eps_pp), to see a closer geometry.
Run from the folder root."""
import importlib.util
import sys
from collections import defaultdict

spec = importlib.util.spec_from_file_location("gen", "tasks/active/gamma-decay-scheme/tests/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
scale = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0

w = gen.Walk(gen.TARGET, isomer=gen.ISOMER_LEVEL)
energies = [e for e, _, _ in w.lines]
both = defaultdict(float)
for table in (w.pairs, w.straddle):
    for key, p in table.items():
        both[key] += p
loss = {}
for i in range(len(energies)):
    s = 0.0
    for (a, b), p in both.items():
        if i in (a, b):
            other = energies[b if i == a else a]
            s += p / w.intensity[i] * scale * float(gen.eps_tot(other)) * gen.SAME
    loss[i] = s
ref = max(range(len(energies)), key=lambda i: w.intensity[i])
strongest = w.intensity[ref]
rows = []
for i, e in enumerate(energies):
    read = (1.0 - loss[i]) / (1.0 - loss[ref])
    rows.append((e, 100.0 * w.intensity[i] / strongest, loss[i], read - 1.0))
for e, rel, l, err in sorted(rows):
    print("%8.1f  I %7.2f  summing-out loss %5.1f%%  uncorrected relative intensity %+6.1f%%" % (e, rel, 100 * l, 100 * err))
print("scale %.2f: worst uncorrected error %+.1f%%; lines past 25%%: %d" %
      (scale, 100 * min(r[3] for r in rows), sum(1 for r in rows if abs(r[3]) > 0.25)))
