import importlib.util, time
from pathlib import Path
spec = importlib.util.spec_from_file_location("gen", Path("tasks/active/dhva-fermi-surface/tests/generate.py"))
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
t0 = time.time()
print("delta", G.ORBITS[-1][:3], G.combinations_near("delta"), "%.1f s" % (time.time() - t0))
print("coincidences p <= 8:", G.coincidences())
dF = G.ORBITS[-1][1]
print(min(((p * o[1], p, o[0]) for o in G.ORBITS[:-1] for p in range(1, 9)), key=lambda h: abs(h[0] - dF)))
