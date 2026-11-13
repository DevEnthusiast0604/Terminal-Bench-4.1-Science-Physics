"""Limits from a least-squares power law a(P) = L + C P^-s fitted to the values over a window of P, against the
with_tail limit at the highest P, in shares of the tolerance.

    python -B conv3.py BLOCKS.npz M2 T X1 [X1 ...]

For each window [P1 - W, P1] (every index, W = 24, 32 or 48) the exponent s is found by a scan with L and C by linear
least squares at each s; the ripple of single increments averages out over the window.
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "../../../../tasks/active/chapman-enskog-transport/tests")))
import ce_mix as M  # noqa: E402

REL, FLOOR = 2e-5, 1e-6


def tol(q, v):
    return max(REL * abs(v), FLOOR) if q == "thermal_diffusion_factor" else REL * abs(v)


def fit(Ps, vals):
    Ps, vals = np.asarray(Ps, float), np.asarray(vals, float)
    best = None
    for s in np.arange(0.5, 12.0, 0.005):
        A = np.vstack([np.ones_like(Ps), Ps ** -s]).T
        coef, res, *_ = np.linalg.lstsq(A, vals, rcond=None)
        r = float(np.sum((A @ coef - vals) ** 2))
        if best is None or r < best[0]:
            best = (r, s, coef[0], np.sqrt(r / len(Ps)))
    return best[1], best[2], best[3]


def main():
    path, m2, T = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
    acc = M.load_blocks(path)
    pmax = acc[("vector", "like")].shape[0] - 1
    for x1 in map(float, sys.argv[4:]):
        v = {P: M.coefficients(acc, m2, x1, T, P) for P in range(16, pmax + 1)}
        print("== m2 %g x1 %g T %g (blocks to P = %d)" % (m2, x1, T, pmax))
        for q in M.QUANTITIES:
            a = {P: v[P][q] for P in v}
            ref = M.with_tail(pmax, a[pmax - 8], a[pmax - 4], a[pmax])
            t = tol(q, ref)
            print("  %-25s with_tail(%d) %.12g; raw(%d) %.3g tol off it" % (q, pmax, ref, pmax, abs(a[pmax] - ref) / t))
            for W in (24, 32, 48):
                cells = []
                for P1 in range(64, pmax + 1, 16):
                    if P1 - W < 16:
                        continue
                    Ps = list(range(P1 - W, P1 + 1))
                    s, L, rms = fit(Ps, [a[P] for P in Ps])
                    cells.append("P%d s %.2f L-ref %+.3f rms %.2g" % (P1, s, (L - ref) / t, rms / t))
                print("      W%-3d " % W + " | ".join(cells))


if __name__ == "__main__":
    main()
