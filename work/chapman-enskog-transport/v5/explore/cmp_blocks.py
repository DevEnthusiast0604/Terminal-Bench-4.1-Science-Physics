"""Compare transport results from two cached block files at a common Sonine index P (grid-convergence check).
    python -B cmp_blocks.py a.npz b.npz m2 T P x1[,x1...]"""
import sys

import numpy as np

sys.path.insert(0, "../../../../tasks/active/chapman-enskog-transport/tests")

from kihara_mix import H_from_blocks
from survey import props


def load(path, P):
    d = np.load(path)
    return {tuple(k.split("|")): d[k][:P + 1, :P + 1] for k in d.files}


fa, fb, m2, T, P = sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
x1s = [float(v) for v in sys.argv[6].split(",")]
A, B = load(fa, P), load(fb, P)
for x1 in x1s:
    ra = props(H_from_blocks(A, "tensor", m2, x1, T), H_from_blocks(A, "vector", m2, x1, T), 1.0, m2, x1, T, P)
    rb = props(H_from_blocks(B, "tensor", m2, x1, T), H_from_blocks(B, "vector", m2, x1, T), 1.0, m2, x1, T, P)
    print("x1 %g P %d: " % (x1, P) + " ".join("%s %.10g (rel diff %.1e)" % (k, float(rb[k]), abs(float(ra[k] / rb[k] - 1)))
                                          for k in ra))
