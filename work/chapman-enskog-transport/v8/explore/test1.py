"""Checks of qs.phases: an independent DOP853 integration, step convergence, matching-radius convergence."""
import math
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0])
import qs  # noqa: E402

A, Lam, mu = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3])
P = qs.Pair(A, Lam, mu)
print("kappa^2 = %.4f" % P.kap2)


def ref_phase(E, l, rm, r0):
    k2 = P.kap2 * E

    def f(r, y):
        return [y[1], (l * (l + 1) / r ** 2 + P.U(r) - k2) * y[0]]
    s = solve_ivp(f, (r0, rm), [0.0, 1.0], method="DOP853", rtol=1e-13, atol=1e-300)
    u, up = s.y[0, -1], s.y[1, -1]
    k = math.sqrt(k2)
    jh, nh, jd, nd = qs.ricbes(l, k * rm)
    d = math.atan((k * u * jd - up * jh) / (k * u * nd - up * nh))
    return d


for E in (1e-3, 0.05, 0.5, 3.0, 30.0):
    k = math.sqrt(P.kap2 * E)
    lnum = max(int(k * qs.r_match(P, k)) + 5, 25)
    t0 = time.time()
    res = {}
    for kf in (1.0, 0.5, 0.25):
        res[kf] = qs.phases(P, np.array([E]), lnum, kfac=kf)[0]
    t1 = time.time() - t0
    ed = qs.make_grid(P, E, E)
    rm, r0 = ed[-1], ed[0]
    ls = [0, 1, 2, 5, min(10, lnum), min(25, lnum)]
    print("E %g  k %.3f  rm %.2f  r0 %.4f  steps %d  lnum %d  (%.1f s for 3 runs)" % (E, k, rm, r0, len(ed) - 1,
                                                                                  lnum, t1))
    for l in ls:
        dref = ref_phase(E, l, rm, r0)
        dm = res[0.25][l]
        dmod = (dm + math.pi / 2) % math.pi - math.pi / 2
        # compare without the tail: recompute tail separately
        tl = qs.tail(P, np.array([k]), np.array([l]), np.array([dm]), rm)[0]
        print("  l %3d  abs %+.12f  kf1-kf.25 %+.2e  kf.5-kf.25 %+.2e  (mod pi, no tail) - DOP853 %+.2e  tail %+.3e"
              % (l, dm, res[1.0][l] - dm, res[0.5][l] - dm,
                 ((dmod - tl - dref + math.pi / 2) % math.pi - math.pi / 2), tl))
