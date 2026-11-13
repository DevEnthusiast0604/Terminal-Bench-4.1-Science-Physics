"""Check: kernel accuracy at high P with isotropic pseudo-Maxwell molecules (Qt^(l)(E) = E^-1/2 for l >= 1), whose
brackets are exactly block-diagonal in the Sonine index, so alpha_T = 0 and every coefficient is exact at the lowest
order. The x integral is Gauss-Laguerre (alpha = 1/2), exact for these polynomials.
    python -B t_maxwell_hiP.py P m2"""
import os
import sys
import time

os.environ["OPENBLAS_NUM_THREADS"] = "1"
import numpy as np  # noqa: E402
from scipy.special import roots_genlaguerre  # noqa: E402

sys.path.insert(0, "../../../../tasks/active/chapman-enskog-transport/tests")
import ce_mix as M  # noqa: E402

if __name__ == "__main__":
    P, m2, T = int(sys.argv[1]), float(sys.argv[2]), 2.0
    tw = M.rules(P)
    Ks = {kind: M.Kernels(m2, P, kind, tw) for kind in ("vector", "tensor")}
    xs, ws = roots_genlaguerre(P + 6, 0.5)
    acc = {}
    t0 = time.time()
    for x, w in zip(xs, ws):
        for kind, K in Ks.items():
            for name, c in K.c(x).items():
                ql = np.ones(K.Lout) / np.sqrt(T)        # x^-1/2 is in the weight; Qt = (x T)^-1/2
                ql[0] = 0.0
                if name == "like":
                    ql[1::2] = 0.0
                acc[(kind, name)] = acc.get((kind, name), 0.0) + w * np.tensordot(ql, c, axes=(0, 0))
    print("kernels at %d nodes in %.0f s" % (len(xs), time.time() - t0))
    for kind in ("vector", "tensor"):
        for name in ("like", "11", "22", "12"):
            B = acc[(kind, name)]
            off = np.abs(B - np.diag(np.diag(B)))
            print("%s %-4s  max |off-diagonal| / max |diagonal| = %.1e" % (kind, name, off.max() / np.abs(np.diag(B)).max()))
    for x1 in (0.05, 0.5):
        rows = []
        r1 = M.coefficients(acc, m2, x1, T, 1)
        for p in (8, 16, 32, 48, P):
            r = M.coefficients(acc, m2, x1, T, p)
            rows.append("P%d: aT %.1e, max rel dev from P=1 %.1e" % (p, r["thermal_diffusion_factor"], max(
                abs(r[q] / r1[q] - 1) for q in ("viscosity", "thermal_conductivity", "binary_diffusion"))))
        print("x1 %g  " % x1 + "; ".join(rows))
