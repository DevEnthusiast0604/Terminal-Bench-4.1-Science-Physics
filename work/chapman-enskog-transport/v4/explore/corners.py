"""Reference behaviour at the corners of a (core ratio, T*) domain: E_c(a), the 18-value machinery at single
(a, T*) points, Sonine convergence, run time, and the change on a finer grid with a tighter b-tolerance.

    python -B work/chapman-enskog-transport/v4/explore/corners.py ec
    python -B work/chapman-enskog-transport/v4/explore/corners.py run 0.0:0.1 0.8:0.2 ...
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "tasks", "active",
                                "chapman-enskog-transport", "tests"))
import ce_ref as R  # noqa: E402

GRID = dict(width=1.0, n_uni=16, K=10, n_gr=8)
GRID2 = dict(width=0.5, n_uni=16, K=14, n_gr=12)
Q = ["viscosity", "thermal_conductivity", "self_diffusion"]


def ec():
    for A in (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.85, 0.9):
        p = R.Kihara(A)
        print("a = %.2f  E_c = %.6f at r_c = %.5f   h_max = %.6f at r_h = %.5f   r_m = %.5f"
              % (A, p.E_c, p.r_c, p.h_max, p.r_h, p.rm), flush=True)


def run(cases, fine):
    for case in cases:
        A, T = map(float, case.split(":"))
        t0 = time.time()
        r1 = R.transport(A, [T], 12, GRID, 1 / 32, 1e-10, log=lambda *a: None)["results"][0]
        t1 = time.time() - t0
        line = "a=%.3f T*=%-6g (%.0f s): " % (A, T, t1) + "  ".join("%s %.10f" % (q[:4], r1["exact"][q]) for q in Q)
        fs = r1["f"]
        conv = "  ".join("%s M4 %.1e M5 %.1e M11 %.1e" % (q[:4], abs(fs[q][3] / fs[q][-1] - 1), abs(fs[q][4] / fs[q][-1] - 1),
                                                       abs(fs[q][10] / fs[q][-1] - 1)) for q in Q)
        print(line, flush=True)
        print("    sonine:", conv, "  Omega11* %.6f Omega22* %.6f" % tuple(r1["omega_star"]), flush=True)
        if fine:
            t0 = time.time()
            r2 = R.transport(A, [T], 12, GRID2, 1 / 32, 1e-11, log=lambda *a: None)["results"][0]
            print("    finer grid (%.0f s): max rel diff %.1e" % (time.time() - t0, max(abs(r2["exact"][q] / r1["exact"][q] - 1)
                                                                                for q in Q)), flush=True)


if __name__ == "__main__":
    if sys.argv[1] == "ec":
        ec()
    else:
        run(sys.argv[2:], fine=sys.argv[1] == "runfine")
