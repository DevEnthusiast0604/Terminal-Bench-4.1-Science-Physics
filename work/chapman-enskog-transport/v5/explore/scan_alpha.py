"""Exploration (v5): sign and size of alpha_T at low T* over the core ratio (low Sonine order is enough there).
    python -B scan_alpha.py TESTS_DIR P m2 A:T[,A:T...] x1[,x1...]"""
import sys
import time

import kihara_mix as K
from survey import props

if __name__ == "__main__":
    P, m2 = int(sys.argv[2]), float(sys.argv[3])
    pairs = [tuple(float(v) for v in s.split(":")) for s in sys.argv[4].split(",")]
    x1s = [float(v) for v in sys.argv[5].split(",")]
    for A, T in pairs:
        t0 = time.time()
        acc = K.blocks(A, m2, T, P, log=lambda *a: None)
        row = []
        for x1 in x1s:
            Ht, Hv = K.H_from_blocks(acc, "tensor", m2, x1, T), K.H_from_blocks(acc, "vector", m2, x1, T)
            r = props(Ht, Hv, 1.0, m2, x1, T, P)
            row.append("x1 %g aT %+.5f" % (x1, float(r["alpha_T"])))
        print("A %.2f T %5.2f (%3.0f s): %s" % (A, T, time.time() - t0, "  ".join(row)), flush=True)
