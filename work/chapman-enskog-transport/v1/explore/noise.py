"""Sensitivity of the correction factors to relative noise in the collision integrals (author's check)."""
import sys
import numpy as np
import omega as O

I = np.load(sys.argv[1])
P = int(sys.argv[2])
t = int(sys.argv[3])
coefs = O.load_coefs(P, "coefs_P%d.json" % P)
base = O.factors(coefs, I[t], P)
rng = np.random.default_rng(1)
for eps in (1e-12, 1e-10, 1e-8):
    worst = {k: np.zeros(P) for k in base}
    for trial in range(5):
        Ip = I[t] * (1 + eps * rng.standard_normal(I[t].shape))
        f = O.factors(coefs, Ip, P)
        for k in base:
            worst[k] = np.maximum(worst[k], np.abs(np.array(f[k]) - np.array(base[k])))
    for k in base:
        print("eps=%.0e %s max |df| over M=1..%d: %s" % (eps, k, P, " ".join("%.1e" % v for v in worst[k])))
