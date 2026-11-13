"""Exploration (v5): blocks of one (A, m2, T) at Sonine index P with the shipped tests/ce_mix.py, cached, then the
convergence of the four coefficients at the given mole fractions.
    python -B run_case.py A m2 T P x1[,x1...] [Plist]"""
import os
import sys
import time

sys.path.insert(0, "../../../../tasks/active/chapman-enskog-transport/tests")
import ce_mix as M  # noqa: E402

if __name__ == "__main__":
    A, m2, T, P = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
    x1s = [float(v) for v in sys.argv[5].split(",")]
    Ps = [int(v) for v in sys.argv[6].split(",")] if len(sys.argv) > 6 else list(range(16, P + 1, 8))
    path = "cache/cm_A%g_m%g_T%g_P%d.npz" % (A, m2, T, P)
    if os.path.exists(path):
        acc = M.load_blocks(path)
    else:
        acc = M.blocks(A, m2, T, P)
        M.save_blocks(path, acc)
    for x1 in x1s:
        t0 = time.time()
        res = {p: M.coefficients(acc, m2, x1, T, p, dps=30) for p in Ps}
        ref = res[Ps[-1]]
        print("x1 %g: P=%d " % (x1, Ps[-1]) + " ".join("%s %.10g" % (k[:12], v) for k, v in ref.items())
              + "  (%.0f s)" % (time.time() - t0))
        for p in Ps[:-1]:
            print("    P=%2d " % p + " ".join("%s %.1e" % (k[:12], abs(res[p][k] / ref[k] - 1)) for k in ref))
        sys.stdout.flush()
