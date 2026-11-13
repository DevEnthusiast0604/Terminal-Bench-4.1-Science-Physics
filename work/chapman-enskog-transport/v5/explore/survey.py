"""Convergence survey (v5 exploration): rigid-sphere binary mixtures, Sonine index up to P, float64 brackets,
mpmath solves. Also reports the cancellation in the bracket sums (sum |terms| / |sum|) of the largest index.
    python -B survey.py m1 m2 x1 Pmax [T]"""
import sys
import time

import mpmath as mp
import numpy as np

from mixgf import gf


def full_blocks(m1, m2, N):
    M1, M2 = m1 / (m1 + m2), m2 / (m1 + m2)
    r = 1 / np.sqrt(2)
    s1, s2 = np.sqrt(M1), np.sqrt(M2)
    out = {}
    for kind in ("vector", "tensor"):
        out[kind] = {"like": gf(r, r, -r, -r, N, kind), "11": gf(s1, s1, -s2, -s2, N, kind),
                     "22": gf(s2, s2, s1, s1, N, kind), "12": gf(s1, s2, -s2, s1, N, kind)}
    return out


def assemble(G, x1, x2, omega, P):
    """float64 H on [(1, 0..P)] + [(2, 0..P)] and the cancellation ratio matrix."""
    K = P + 1

    def block(g, pair, scale, even_only):
        B = np.zeros((K, K))
        A = np.zeros((K, K))
        for (n, k), arr in g.items():
            if k == 0 or (even_only and k % 2):
                continue
            t = scale * arr[:K, :K] * omega(pair, k, n)
            B += t
            A += np.abs(t)
        return B, A

    b11a, a11a = block(G["like"], "11", 16 * x1 * x1, True)
    b11b, a11b = block(G["11"], "12", 8 * x1 * x2, False)
    b22a, a22a = block(G["like"], "22", 16 * x2 * x2, True)
    b22b, a22b = block(G["22"], "12", 8 * x1 * x2, False)
    b12, a12 = block(G["12"], "12", 8 * x1 * x2, False)
    H = np.block([[b11a + b11b, b12], [b12.T, b22a + b22b]])
    Aabs = np.block([[a11a + a11b, a12], [a12.T, a22a + a22b]])
    return H, Aabs


def props(Ht, Hv, m1, m2, x1, T, P, dps=40):
    """eta, lambda, D12, alpha_T from the leading sub-blocks with Sonine indices up to P."""
    mp.mp.dps = dps
    x2 = 1 - x1
    Kt = Ht.shape[0] // 2
    K = P + 1

    def sub(H, lo):
        rows = list(range(lo, K)) + [Kt + i for i in range(lo, K)]
        return mp.matrix([[mp.mpf(H[i, j]) for j in rows] for i in rows])
    sT = mp.sqrt(2 * mp.mpf(T))
    sm1, sm2 = mp.sqrt(mp.mpf(m1)), mp.sqrt(mp.mpf(m2))
    # viscosity
    H = sub(Ht, 0)
    rhs = mp.matrix(2 * K, 1)
    rhs[0], rhs[K] = mp.mpf(5) / 2 * x1, mp.mpf(5) / 2 * x2
    y = mp.lu_solve(H, rhs)
    eta = T * (x1 * y[0] + x2 * y[K])
    # conductivity (p >= 1)
    H = sub(Hv, 1)
    k1 = K - 1
    rhs = mp.matrix(2 * k1, 1)
    rhs[0], rhs[k1] = -mp.mpf(15) / 4 * x1 * sT / sm1, -mp.mpf(15) / 4 * x2 * sT / sm2
    a = mp.lu_solve(H, rhs)
    lam = -mp.mpf(5) / 4 * sT * (x1 * a[0] / sm1 + x2 * a[k1] / sm2)
    # diffusion / thermal diffusion (p >= 0), bordered with the momentum constraint
    H = sub(Hv, 0)
    n = 2 * K
    A = mp.matrix(n + 1, n + 1)
    for i in range(n):
        for j in range(n):
            A[i, j] = H[i, j]
    A[0, n] = A[n, 0] = x1 * sm1
    A[K, n] = A[n, K] = x2 * sm2
    rd = mp.matrix(n + 1, 1)
    rd[0], rd[K] = mp.mpf(3) / 2 * sT / sm1, -mp.mpf(3) / 2 * sT / sm2
    d = mp.lu_solve(A, rd)
    rt = mp.matrix(n + 1, 1)
    rt[1], rt[K + 1] = -mp.mpf(15) / 4 * x1 * sT / sm1, -mp.mpf(15) / 4 * x2 * sT / sm2
    at = mp.lu_solve(A, rt)
    D12 = x1 * x2 / 2 * sT * (d[0] / sm1 - d[K] / sm2)
    DT = x1 * x2 / 2 * sT * (at[0] / sm1 - at[K] / sm2)
    return {"eta": eta, "lambda": lam, "D12": D12, "alpha_T": DT / D12 / (x1 * x2)}


def rigid_omega(m1, m2, T):
    mu = {"11": m1 / 2, "22": m2 / 2, "12": m1 * m2 / (m1 + m2)}
    fac = [float(mp.factorial(s + 1)) for s in range(200)]

    def om(pair, l, s):
        ql = 1 - (1 + (-1) ** l) / (2 * (1 + l))
        return np.sqrt(T / (2 * np.pi * mu[pair])) * np.pi * ql * fac[s] / 2
    return om


if __name__ == "__main__":
    m1, m2, x1, Pmax = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4])
    T = float(sys.argv[5]) if len(sys.argv) > 5 else 1.0
    t0 = time.time()
    G = full_blocks(m1, m2, Pmax + 2)
    t1 = time.time()
    om = rigid_omega(m1, m2, T)
    Ht, At = assemble(G["tensor"], x1, 1 - x1, om, Pmax)
    Hv, Av = assemble(G["vector"], x1, 1 - x1, om, Pmax)
    canc = np.max(Av / np.maximum(np.abs(Hv), 1e-300) * (np.abs(Hv) > 1e-12 * np.abs(Hv).max()))
    print("m1 %g m2 %g x1 %g T %g: gf %.1f s; worst cancellation (vector) %.1e" % (m1, m2, x1, T, t1 - t0, canc))
    prev = None
    for P in range(1, Pmax + 1):
        r = props(Ht, Hv, m1, m2, x1, T, P)
        line = "P=%2d " % P + " ".join("%s %.10f" % (k, float(v)) for k, v in r.items())
        if prev:
            line += "  | rel.incr " + " ".join("%.1e" % abs(float(r[k] / prev[k] - 1)) for k in r)
        print(line, flush=True)
        prev = r
