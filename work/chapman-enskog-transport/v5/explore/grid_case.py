"""Blocks of one case at P with a modified energy grid or cross-section tolerance, cached; prints the alpha_T and D12
sequence next to the generator's P = 64 blocks.
    python -B grid_case.py A m2 x1 T P width n_uni rel ref.npz"""
import os
import sys

sys.path.insert(0, "../../../../tasks/active/chapman-enskog-transport/tests")
import ce_mix as M  # noqa: E402

if __name__ == "__main__":
    A, m2, x1, T, P = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
    width, n_uni, rel, ref = float(sys.argv[6]), int(sys.argv[7]), float(sys.argv[8]), sys.argv[9]
    path = "cache/g_A%g_m%g_T%g_P%d_w%g_n%d_r%g.npz" % (A, m2, T, P, width, n_uni, rel)
    if os.path.exists(path):
        acc = M.load_blocks(path)
    else:
        acc = M.blocks(A, m2, T, P, grid=dict(width=width, n_uni=n_uni, K=10, n_gr=8), rel=rel, log=lambda *a: None)
        M.save_blocks(path, acc)
    R = M.load_blocks(ref)
    for q in ("thermal_diffusion_factor", "binary_diffusion"):
        print(q)
        for p in range(24, P + 1, 4):
            a, b = M.coefficients(acc, m2, x1, T, p)[q], M.coefficients(R, m2, x1, T, p)[q]
            print("  P %2d  this %.12g  generator %.12g  rel diff %.1e" % (p, a, b, abs(a / b - 1)))
