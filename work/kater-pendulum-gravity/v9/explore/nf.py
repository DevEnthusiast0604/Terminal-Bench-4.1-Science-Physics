import sys, math, numpy as np
sys.path.insert(0, ".")
import gen9b as G
import red9b as R
G.SIGMA = 0.0
real_int = G.np.random.default_rng
# no dropouts: monkeypatch build so bursts have zero length
orig = G.build_run
def build(rid, rng):
    c, m, ok, sync = orig(rid, rng)
    return c, m, ok, sync
G.main("dnf", "dnf/expected.json")
