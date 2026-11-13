"""Tail models against a high-order limit, in shares of the tolerance, for one cached block set.

    python -B conv2.py BLOCKS.npz M2 T PMAX X1 [X1 ...]

For each quantity: the limit L from PMAX (ce_mix.with_tail), the spread of the with_tail limits from PMAX - 24 ..
PMAX, the raw error at several P, the error of with_tail (three values, constant exponent) at several P, and the
error of a drifting-exponent tail (four values: k(P) = k_inf + c / P from the last two local exponents).
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "../../../../tasks/active/chapman-enskog-transport/tests")))
import ce_mix as M  # noqa: E402

REL, FLOOR = 2e-5, 1e-6


def tol(q, v):
    return max(REL * abs(v), FLOOR) if q == "thermal_diffusion_factor" else REL * abs(v)


def drift_tail(P, a12, a8, a4, a0, jmax=200000):
    """a(P) plus the tail with k(Q) = k_inf + c / Q fitted to the local exponents at P - 4 and P."""
    d0, d1, d2 = a8 - a12, a4 - a8, a0 - a4
    if not (d0 * d1 > 0 and d1 * d2 > 0 and abs(d2) < abs(d1) < abs(d0)):
        return M.with_tail(P, a8, a4, a0)
    kA = math.log(d0 / d1) / math.log((P - 4.0) / (P - 8.0))      # local exponent near P - 6
    kB = math.log(d1 / d2) / math.log(P / (P - 4.0))              # near P - 2
    qa, qb = P - 6.0, P - 2.0
    c = (kA - kB) / (1.0 / qa - 1.0 / qb)
    kinf = kB - c / qb
    Q = P + 4.0 * np.arange(1, jmax + 1)
    k = np.maximum(kinf + c / (Q - 2.0), 1.01)
    ratio = np.exp(-k * np.log(Q / (Q - 4.0)))
    return a0 + d2 * float(np.sum(np.cumprod(ratio)))


def main():
    path, m2, T, pmax = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
    acc = M.load_blocks(path)
    show = [p for p in (48, 64, 72, 80, 96, 112, 128, 144, 160) if p <= pmax]
    for x1 in map(float, sys.argv[5:]):
        v = {P: M.coefficients(acc, m2, x1, T, P) for P in range(8, pmax + 1, 4)}
        print("== m2 %g x1 %g T %g (limit from P = %d)" % (m2, x1, T, pmax))
        for q in M.QUANTITIES:
            a = {P: v[P][q] for P in v}
            lim = M.with_tail(pmax, a[pmax - 8], a[pmax - 4], a[pmax])
            t = tol(q, lim)
            lims = [M.with_tail(P, a[P - 8], a[P - 4], a[P]) for P in range(pmax - 24, pmax + 1, 8)]
            dl = [drift_tail(P, a[P - 12], a[P - 8], a[P - 4], a[P]) for P in range(pmax - 24, pmax + 1, 8)]
            d2, d1 = a[pmax] - a[pmax - 4], a[pmax - 4] - a[pmax - 8]
            k = math.log(d1 / d2) / math.log(pmax / (pmax - 4.0)) if d1 * d2 > 0 and abs(d2) < abs(d1) else float("nan")
            print("  %-25s L %.12g  k(PMAX) %.2f  tail(PMAX) %.3g  spread3 %.3g  spread4 %.3g  drift-vs-3 %.3g" % (
                q, lim, k, abs(lim - a[pmax]) / t, (max(lims) - min(lims)) / t, (max(dl) - min(dl)) / t,
                abs(dl[-1] - lim) / t))
            print("      raw   " + "  ".join("P%d %.3g" % (P, abs(a[P] - lim) / t) for P in show))
            print("      tail3 " + "  ".join("P%d %.3g" % (P, abs(M.with_tail(P, a[P - 8], a[P - 4], a[P]) - lim) / t)
                                         for P in show))
            print("      tail4 " + "  ".join("P%d %.3g" % (
                P, abs(drift_tail(P, a[P - 12], a[P - 8], a[P - 4], a[P]) - lim) / t) for P in show))


if __name__ == "__main__":
    main()
