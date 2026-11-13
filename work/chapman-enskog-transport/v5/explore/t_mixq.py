"""Check: quadrature kernels (mixq) = generating-function polynomials (mixgf) at low order."""
import time
import numpy as np
from numpy.polynomial import legendre as Lg
from mixgf import gf
from mixq import Kernel, types

P = 7
m1, m2 = 1.0, 6.5
T = types(m1, m2)
for kind in ("vector", "tensor"):
    for name, (a, al, b, be) in T.items():
        G = gf(a, b, al, be, P + 2, kind)
        K = Kernel(a, al, b, be, P, kind)
        worst = 0.0
        for x in (0.37, 2.9, 11.0):
            t0 = time.time()
            c = K.c(x)
            dt = time.time() - t0
            kmax = max(k for n, k in G) + 1
            # GF -> polynomial in kappa at this x -> Legendre
            for p in range(P + 1):
                for q in range(P + 1):
                    pk = np.zeros(kmax)
                    for (n, k), arr in G.items():
                        pk[k] += arr[p, q] * x ** n
                    leg = Lg.poly2leg(pk)
                    ref = np.zeros(c.shape[0])
                    ref[:min(len(leg), len(ref))] = leg[:len(ref)]
                    scale = max(1.0, np.abs(ref).max())
                    worst = max(worst, np.abs(c[:, p, q] - ref).max() / scale)
        print("%-6s %-4s worst rel diff %.1e  (%.3f s per x)" % (kind, name, worst, dt))
