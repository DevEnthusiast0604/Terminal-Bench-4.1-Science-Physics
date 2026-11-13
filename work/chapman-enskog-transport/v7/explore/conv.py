"""Convergence of a cached block set at several mole fractions: error of the raw truncation against the tail-corrected
limit at the highest P, increments over four indices, local power exponents, and the limit estimated at lower P.

    python -B conv.py BLOCKS.npz M2 T PMAX X1 [X1 ...]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "../../../../tasks/active/chapman-enskog-transport/tests")))
import ce_mix as M  # noqa: E402

REL, FLOOR = 2e-5, 1e-6


def tol(q, v):
    return max(REL * abs(v), FLOOR) if q == "thermal_diffusion_factor" else REL * abs(v)


def main():
    path, m2, T, pmax = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
    acc = M.load_blocks(path)
    for x1 in map(float, sys.argv[5:]):
        v = {P: M.coefficients(acc, m2, x1, T, P) for P in range(8, pmax + 1, 4)}
        print("== m2 %g x1 %g T %g (limit from P = %d)" % (m2, x1, T, pmax))
        for q in M.QUANTITIES:
            lim = M.with_tail(pmax, v[pmax - 8][q], v[pmax - 4][q], v[pmax][q])
            t = tol(q, lim)
            cells = []
            for P in range(24, pmax + 1, 8):
                d2, d1 = v[P][q] - v[P - 4][q], v[P - 4][q] - v[P - 8][q]
                k = math.log(d1 / d2) / math.log(P / (P - 4)) if d1 * d2 > 0 and abs(d2) < abs(d1) else float("nan")
                tl = M.with_tail(P, v[P - 8][q], v[P - 4][q], v[P][q])
                cells.append("P%d raw %.2g incr %.2g k %.2f tail %.2g" % (
                    P, abs(v[P][q] - lim) / t, abs(d2) / t, k, abs(tl - lim) / t))
            print("  %-25s limit %.12g  (shares of the tolerance)" % (q, lim))
            for c in cells:
                print("      " + c)


if __name__ == "__main__":
    main()
