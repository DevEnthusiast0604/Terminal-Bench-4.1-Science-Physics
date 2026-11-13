"""Level pairs of the v13 scheme with no transition whose difference falls 0.3-2.0 keV from a line (any intensity).
Imports tests/generate.py read-only. Run from the folder root."""
import importlib.util
spec = importlib.util.spec_from_file_location("gen", "tasks/active/gamma-decay-scheme/tests/generate.py")
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
T = {}
for k, v in gen.TARGET.items():
    if k == "X":
        continue
    T[k] = v
    if k == "C":
        T["Y"] = (1399.8, 1.9, [("B", 45), ("A", 55)])
w = gen.Walk(T, gen.ISOMER_LEVEL)
top = max(w.intensity.values())
lines = [(e, a, b, 100.0 * w.intensity[i] / top) for i, (e, a, b) in enumerate(w.lines)]
lev = {k: v[0] for k, v in T.items()}
lev["g"] = 0.0
real = {(a, b) for _, a, b, _ in lines}
for a in lev:
    for b in lev:
        d = lev[a] - lev[b]
        if d < 60.0 or (a, b) in real:
            continue
        for e, x, y, i in lines:
            if 0.3 <= abs(d - e) <= 2.0:
                print("%-2s-%-2s %8.1f  vs %8.1f %s->%s I %6.2f  offset %+.1f" % (a, b, d, e, x, y, i, d - e))
