"""Increments of one quantity over single and four-index steps, with local exponents, for one cached block set.

    python -B incr.py BLOCKS.npz M2 T X1 QUANTITY [PMIN] [STEP]
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "../../../../tasks/active/chapman-enskog-transport/tests")))
import ce_mix as M  # noqa: E402


def main():
    path, m2, T, x1, q = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
    pmin = int(sys.argv[6]) if len(sys.argv) > 6 else 24
    step = int(sys.argv[7]) if len(sys.argv) > 7 else 1
    acc = M.load_blocks(path)
    pmax = acc[("vector", "like")].shape[0] - 1
    a = {P: M.coefficients(acc, m2, x1, T, P)[q] for P in range(pmin - 2 * step, pmax + 1, step)}
    tol = max(2e-5 * abs(a[pmax]), 1e-6) if q == "thermal_diffusion_factor" else 2e-5 * abs(a[pmax])
    print("%s m2 %g x1 %g T %g: value at P %d = %.12g, tolerance %.3g" % (q, m2, x1, T, pmax, a[pmax], tol))
    for P in range(pmin, pmax + 1, step):
        d, dp = a[P] - a[P - step], a[P - step] - a[P - 2 * step]
        k = math.log(dp / d) / math.log(P / (P - step)) if d * dp > 0 else float("nan")
        print("  P %3d  a %.12g  d %+.3e  (%.4f tol)  k %.2f" % (P, a[P], d, d / tol, k))


if __name__ == "__main__":
    main()
