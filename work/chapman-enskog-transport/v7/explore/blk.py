"""Bracket blocks of one (A, m2, T, P) in N parts, cached in ../cache, within a time budget per run.

    python -B blk.py A M2 T P N [BUDGET_S] [WIDTH]      (from anywhere; re-run until it prints "complete")

A part does not start once BUDGET_S seconds (default 480) have passed since the run began. WIDTH (default 1.0, the
reference grid) is the width in ln E of the energy panels; another width is cached under its own name (-W<width>).
WIDTH s<w> is the split grid: the reference panels (width 1) below E_split = max(T / 2, 1.6 E_c), where the Sonine
polynomials oscillate slowly, and panels of width w in ln E above it (16 nodes each).
"""
import os
import sys
import time

import numpy as np
from numpy.polynomial.legendre import leggauss

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "../../../../tasks/active/chapman-enskog-transport/tests")))
import ce_mix as M  # noqa: E402
import ce_ref as R  # noqa: E402

CACHE = os.path.normpath(os.path.join(HERE, "../cache"))


def split_grid(A, T, P, w_hi, n=16):
    Ec = R.Kihara(A).E_c
    E_split, E_max = max(0.5 * T, 1.6 * Ec), max(150.0, 4.0 * P + 40.0) * T
    E1, w1 = R.e_nodes(Ec, 1e-4 * T, E_split, **M.GRID)
    a, b = np.log(E_split), np.log(E_max)
    edges = np.linspace(a, b, int(np.ceil((b - a) / w_hi)) + 1)
    xg, wg = leggauss(n)
    u = np.concatenate([0.5 * (lo + hi) + 0.5 * (hi - lo) * xg for lo, hi in zip(edges[:-1], edges[1:])])
    w2 = np.concatenate([0.5 * (hi - lo) * wg for lo, hi in zip(edges[:-1], edges[1:])])
    E, w = np.concatenate([E1, np.exp(u)]), np.concatenate([w1, w2])
    x = E / T
    return E, x, w * np.exp(-x) * x * x


def base_name(a, r, t, p, width="1.0"):
    tag = "" if width == "1.0" else "-W%s" % width
    return os.path.join(CACHE, "blk-A%s-R%s-T%s-P%s%s" % (a, r, t, p, tag))


def main():
    a, r, t, p, n = sys.argv[1:6]
    budget = float(sys.argv[6]) if len(sys.argv) > 6 else 480.0
    width = sys.argv[7] if len(sys.argv) > 7 else "1.0"
    if width.startswith("s"):
        w_hi = float(width[1:])
        M.energy_grid = lambda A, T, P, grid: split_grid(A, T, P, w_hi)
        grid = M.GRID
    else:
        grid = dict(M.GRID, width=float(width))
    os.makedirs(CACHE, exist_ok=True)
    base, start = base_name(a, r, t, p, width), time.time()
    if os.path.exists(base + ".npz"):
        print("complete (cached)", base + ".npz")
        return
    acc, done = {}, 0
    for i in range(int(n)):
        path = "%s-part%dof%s.npz" % (base, i + 1, n)
        if not os.path.exists(path):
            if time.time() - start > budget:
                print("budget used: %d of %s parts done; run again" % (done, n))
                return
            part = M.blocks(float(a), float(r), float(t), int(p), grid=grid, part=(i, int(n)),
                            log=lambda *m: print(*m, flush=True))
            M.save_blocks(path, part)
        done += 1
        for k, v in M.load_blocks(path).items():
            acc[k] = acc.get(k, 0.0) + v
    M.save_blocks(base + ".npz", acc)
    print("complete", base + ".npz", "%.0f s" % (time.time() - start))


if __name__ == "__main__":
    main()
