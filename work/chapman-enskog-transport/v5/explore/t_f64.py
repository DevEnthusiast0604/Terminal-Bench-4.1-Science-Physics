"""Check: float64 linear solves against 30-digit ones on the P = 64 blocks of the hardest corner."""
import sys, time
import numpy as np
sys.path.insert(0, "../../../../tasks/active/chapman-enskog-transport/tests")
import ce_mix as M

def coef64(acc, m2, x1, T, P):
    Ht, Hv = M.H_from_blocks(acc, "tensor", m2, x1, T), M.H_from_blocks(acc, "vector", m2, x1, T)
    Kb, K = Ht.shape[0] // 2, P + 1
    x2, sT, s2 = 1 - x1, np.sqrt(2 * T), np.sqrt(m2)
    def sub(H, lo):
        idx = list(range(lo, K)) + [Kb + i for i in range(lo, K)]
        return H[np.ix_(idx, idx)]
    r = np.zeros(2 * K); r[0], r[K] = 2.5 * x1, 2.5 * x2
    y = np.linalg.solve(sub(Ht, 0), r); eta = T * (x1 * y[0] + x2 * y[K])
    k1 = K - 1
    r = np.zeros(2 * k1); r[0], r[k1] = -3.75 * x1 * sT, -3.75 * x2 * sT / s2
    a = np.linalg.solve(sub(Hv, 1), r); lam = -1.25 * sT * (x1 * a[0] + x2 * a[k1] / s2)
    n = 2 * K
    B = np.zeros((n + 1, n + 1)); B[:n, :n] = sub(Hv, 0)
    B[0, n] = B[n, 0] = x1; B[K, n] = B[n, K] = x2 * s2
    r = np.zeros(n + 1); r[0], r[K] = 1.5 * sT, -1.5 * sT / s2
    d = np.linalg.solve(B, r)
    r = np.zeros(n + 1); r[1], r[K + 1] = -3.75 * x1 * sT, -3.75 * x2 * sT / s2
    t = np.linalg.solve(B, r)
    D12 = x1 * x2 / 2 * sT * (d[0] - d[K] / s2); DT = x1 * x2 / 2 * sT * (t[0] - t[K] / s2)
    return {"viscosity": eta, "thermal_conductivity": lam, "binary_diffusion": D12,
            "thermal_diffusion_factor": DT / D12 / (x1 * x2)}

acc = M.load_blocks("cache/cm_A0.8_m40_T50_P64.npz")
for x1 in (0.05, 0.5, 0.95):
    for P in (32, 64):
        t0 = time.time(); f = coef64(acc, 40.0, x1, 50.0, P); tf = time.time() - t0
        t0 = time.time(); m = M.coefficients(acc, 40.0, x1, 50.0, P, dps=30); tm = time.time() - t0
        print("x1 %g P %d: " % (x1, P) + " ".join("%s %.1e" % (k[:10], abs(f[k] / m[k] - 1)) for k in m),
              "(f64 %.3f s, mp %.1f s)" % (tf, tm), flush=True)
