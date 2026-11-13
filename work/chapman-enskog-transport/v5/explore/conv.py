"""Convergence of one cached case: increments over four indices, local power exponents and tail estimates.
    python -B conv.py blocks.npz m2 x1 T [quantity]"""
import math
import sys

sys.path.insert(0, "../../../../tasks/active/chapman-enskog-transport/tests")
import ce_mix as M  # noqa: E402

path, m2, x1, T = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
qs = sys.argv[5:] or M.QUANTITIES[1:]
acc = M.load_blocks(path)
v = {P: M.coefficients(acc, m2, x1, T, P) for P in range(8, 65, 4)}
for q in qs:
    lim = M.with_tail(64, v[56][q], v[60][q], v[64][q])
    print("%s: P64 %.12g  limit %.12g" % (q, v[64][q], lim))
    for P in range(16, 65, 4):
        d2, d1 = v[P][q] - v[P - 4][q], v[P - 4][q] - v[P - 8][q]
        k = math.log(d1 / d2) / math.log(P / (P - 4)) if d1 * d2 > 0 and abs(d2) < abs(d1) else float("nan")
        print("  P %2d err %+.2e  incr %+.2e  k %5.2f  tail-limit %+.2e" % (
            P, v[P][q] / lim - 1, d2 / abs(lim), k, M.with_tail(P, v[P - 8][q], v[P - 4][q], v[P][q]) / lim - 1))
