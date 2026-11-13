"""Rigid-sphere map: smallest Sonine index P with all four coefficients within TOL of the P = Pref values;
errors and two-step increments at P = 12, 16, 20, 24.   python -B survey2.py Pref R:x1 [R:x1 ...]"""
import sys, time
import numpy as np
from scipy.special import roots_genlaguerre
from mixsolve2 import kernels_at, assemble
from survey import props

TOL = 2e-5
Pref = int(sys.argv[1])
for spec in sys.argv[2:]:
    R, x1 = map(float, spec.split(":"))
    m1, m2 = 1.0, R
    t0 = time.time()
    xs, W = roots_genlaguerre(Pref + 4, 1.0)
    ker = kernels_at(m1, m2, Pref, xs)
    H = {}
    for kind in ("vector", "tensor"):
        L = ker[kind]["like"].shape[1]
        q = np.where(np.arange(L)[None, :] >= 1, np.pi, 0.0) * np.ones((len(xs), 1))
        H[kind] = assemble(ker[kind], W, {pr: q for pr in ("11", "22", "12")}, m1, m2, x1, 1.0, Pref)
    res = {P: props(H["tensor"], H["vector"], m1, m2, x1, 1.0, P) for P in range(2, Pref + 1, 2)}
    ref = res[Pref]
    err = {P: {k: abs(float(r[k] / ref[k] - 1)) for k in r} for P, r in res.items()}
    need = {k: min(P for P in res if all(err[Q][k] <= TOL for Q in res if Q >= P)) for k in ref}
    tail = {k: abs(float(res[Pref - 2][k] / ref[k] - 1)) for k in ref}
    print("R %g x1 %g (%.0f s): P needed %s; ref-increment %s" % (R, x1, time.time() - t0,
          {k: v for k, v in need.items()}, {k: "%.0e" % v for k, v in tail.items()}))
    for P in (12, 16, 20, 24):
        if P in res and P - 2 in res:
            inc = {k: abs(float(res[P][k] / res[P - 2][k] - 1)) for k in ref}
            print("   P=%d err %s | incr %s" % (P, " ".join("%s %.1e" % (k, err[P][k]) for k in ref),
                                              " ".join("%.1e" % inc[k] for k in ref)), flush=True)
