"""Check: the like-type generating function reproduces v4's exact single-gas W coefficients."""
import sys, time
sys.path.insert(0, sys.argv[1])          # tests/ of the task (ce_ref.py)
import numpy as np
from ce_ref import w_matrix
from mixgf import gf

P = 5
N = P + 2
r = 1 / np.sqrt(2)
for kind, k4 in (("vector", "vec"), ("tensor", "visc")):
    t0 = time.time()
    G = gf(r, r, -r, -r, N, kind)
    t1 = time.time()
    W = w_matrix(k4, P)
    worst = 0.0
    for (p, q), d in W.items():
        for (n, e), c in d.items():
            got = G.get((n, e))
            g = 0.0 if got is None else got[p, q]
            worst = max(worst, abs(g - float(c)) / max(1.0, abs(float(c))))
        # and nothing extra
        for (n, e), arr in G.items():
            if (n, e) not in d and abs(arr[p, q]) > 1e-12:
                worst = max(worst, abs(arr[p, q]))
    print(kind, "gf %.2f s" % (t1 - t0), "worst diff vs exact %.2e" % worst)
