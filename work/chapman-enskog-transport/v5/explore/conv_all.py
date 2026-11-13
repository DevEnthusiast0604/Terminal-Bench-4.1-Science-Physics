"""Summary of every generated case: tail size at P = 64, local exponent, raw P needed for 2e-5, the largest
four-index increment beyond P = 32 (late drift), and the tail-limit spread estimated at P = 48, 56, 64."""
import math
import sys

sys.path.insert(0, "../../../../tasks/active/chapman-enskog-transport/tests")
import ce_mix as M  # noqa: E402
import generate as G  # noqa: E402

for name, (a, r, x, t) in G.CASES.items():
    acc = M.load_blocks("../cache/blk-A%s-R%s-T%s-P64.npz" % (a, r, t))
    m2, x1, T = float(r), float(x), float(t)
    v = {P: M.coefficients(acc, m2, x1, T, P) for P in range(8, 65, 4)}
    out = []
    for q in M.QUANTITIES[1:]:
        lim = M.with_tail(64, v[56][q], v[60][q], v[64][q])
        tol = max(abs(lim) * 2e-5, 1e-6 if q == "thermal_diffusion_factor" else 0.0)
        need = next((P for P in range(8, 65, 4) if all(abs(v[p][q] - lim) <= tol for p in range(P, 65, 4))), None)
        tails = [M.with_tail(P, v[P - 8][q], v[P - 4][q], v[P][q]) for P in (48, 56, 64)]
        spread = (max(tails) - min(tails)) / max(abs(lim), 1e-300)
        late = max(abs(v[P][q] - v[P - 4][q]) for P in range(36, 65, 4)) / max(abs(lim), 1e-300)
        out.append("%s tail %.1e need P%s late %.1e spread %.1e" % (q[:6], abs(lim / v[64][q] - 1) if lim else 0.0,
                                                                     need, late, spread))
    print("%s (%s): %s" % (name, ", ".join(G.CASES[name]), " | ".join(out)), flush=True)
