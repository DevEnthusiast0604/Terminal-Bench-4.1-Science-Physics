"""v11 design: where could a weak transition hide 0.5-1.3 keV from an existing line? Imports tests/generate.py for
TARGET and Walk only (no data written, no reference run). Run from the folder root."""
import importlib.util
import itertools
import sys

spec = importlib.util.spec_from_file_location("gen", "tasks/active/gamma-decay-scheme/tests/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)

T = gen.TARGET
w = gen.Walk(T, isomer=gen.ISOMER_LEVEL)
strongest = max(w.intensity.values())
rel = {i: 100.0 * w.intensity[i] / strongest for i in range(len(w.lines))}
lines = [(e, a, b, rel[i], i) for i, (e, a, b) in enumerate(w.lines)]
energy = dict(w.energy)
direct = {(a, b) for _, a, b, _, _ in lines}


def partners(i):
    """Lines in prompt or delayed cascade with line i, with the pair probability relative to line i's intensity."""
    out = {}
    for (p, q), v in list(w.pairs.items()) + list(w.straddle.items()):
        if i in (p, q):
            j = q if p == i else p
            out[j] = out.get(j, 0.0) + v / w.intensity[i]
    return out


print("lines: %d" % len(lines))
for u, l in itertools.permutations(energy, 2):
    d = energy[u] - energy[l]
    if d < gen.THRESHOLD_KEV or (u, l) in direct:
        continue
    near = min(lines, key=lambda r: abs(r[0] - d))
    sep = d - near[0]
    if 0.5 <= abs(sep) <= 1.3 and near[3] >= 2.0:
        others = [r for r in lines if abs(r[0] - d) < 3.0 and r is not near]
        print("%s->%s %.1f keV: %+.1f from %.1f (%s->%s, I %.2f); other lines within 3 keV: %s"
              % (u, l, d, sep, near[0], near[1], near[2], near[3], [round(r[0], 1) for r in others]))
