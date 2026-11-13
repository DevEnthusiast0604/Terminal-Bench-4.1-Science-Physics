"""Exploration (v5): first-order Chapman-Enskog coefficients of a binary mixture from Sonine brackets (mixgf.py).

Units: k = 1, sigma = 1. Inputs: masses m1, m2, mole fractions x1, x2 (n = 1), T, and omega(pair, l, s) giving
Omega_pair^(l,s) = sqrt(T / (2 pi mu)) int e^-g^2 g^(2s+3) Q^(l) dg, pair in ("11", "22", "12").
Basis per species: S_3/2^(p)(C^2) C (vector), S_5/2^(p)(C^2) C°C (tensor).
    eta = T sum_i n_i y_i0                                   (tensor problem, RHS 5/2 n_i delta_q0)
    lambda = -(5/4) sqrt(2T) sum_i n_i a_i1 / sqrt(m_i)       (thermal problem on p >= 1: zero diffusion)
    D12 = (x1 x2 n / 2) sqrt(2T) [d10 / sqrt(m1) - d20 / sqrt(m2)]   (diffusion problem, p >= 0, momentum constraint)
    D_T = (x1 x2 / 2) sqrt(2T) [a10 / sqrt(m1) - a20 / sqrt(m2)]      (thermal problem, p >= 0, momentum constraint)
    V1 - V2 = -(1 / (x1 x2)) [D12 d12 + D_T grad ln T],  k_T = D_T / D12,  alpha_T = k_T / (x1 x2).
"""
import mpmath as mp
import numpy as np

from mixgf import gf


class Brackets:
    def __init__(self, m1, m2, N):
        self.m1, self.m2, self.N = m1, m2, N
        M1, M2 = m1 / (m1 + m2), m2 / (m1 + m2)
        r = 1 / np.sqrt(2)
        s1, s2 = np.sqrt(M1), np.sqrt(M2)
        self.gf = {}
        for kind in ("vector", "tensor"):
            self.gf[kind] = {
                "like": gf(r, r, -r, -r, N, kind),
                "11": gf(s1, s1, -s2, -s2, N, kind),
                "22": gf(s2, s2, s1, s1, N, kind),
                "12": gf(s1, s2, -s2, s1, N, kind),
            }

    def H(self, kind, x1, x2, omega, idx, dps=30):
        """Bracket matrix on the basis [(1, p) for p in idx] + [(2, p) for p in idx]."""
        mp.mp.dps = dps
        G = self.gf[kind]
        n1, n2 = x1, x2
        K = len(idx)

        def block(g, pair, scale, even_only):
            B = mp.matrix(K, K)
            for (n, k), arr in g.items():
                if k == 0 or (even_only and k % 2):
                    continue
                om = mp.mpf(omega(pair, k, n))
                for a, p in enumerate(idx):
                    for b, q in enumerate(idx):
                        v = arr[p, q]
                        if v != 0.0:
                            B[a, b] += scale * mp.mpf(v) * om
            return B

        H11 = block(G["like"], "11", 16 * n1 * n1, True) + block(G["11"], "12", 8 * n1 * n2, False)
        H22 = block(G["like"], "22", 16 * n2 * n2, True) + block(G["22"], "12", 8 * n1 * n2, False)
        H12 = block(G["12"], "12", 8 * n1 * n2, False)
        H = mp.matrix(2 * K, 2 * K)
        for a in range(K):
            for b in range(K):
                H[a, b] = H11[a, b]
                H[K + a, K + b] = H22[a, b]
                H[a, K + b] = H12[a, b]
                H[K + b, a] = H12[a, b]
        return H


def solve_constrained(H, rhs, cvec):
    n = H.rows
    A = mp.matrix(n + 1, n + 1)
    for i in range(n):
        for j in range(n):
            A[i, j] = H[i, j]
        A[i, n] = cvec[i]
        A[n, i] = cvec[i]
    b = mp.matrix([rhs[i] for i in range(n)] + [0])
    x = mp.lu_solve(A, b)
    return [x[i] for i in range(n)]


def transport(br, x1, T, omega, P, dps=30):
    """dict of eta, lambda, D12 (n D12 with n = 1), D_T, k_T, alpha_T with Sonine indices up to P."""
    mp.mp.dps = dps
    m1, m2 = mp.mpf(br.m1), mp.mpf(br.m2)
    x1 = mp.mpf(x1)
    x2 = 1 - x1
    T = mp.mpf(T)
    out = {}
    # viscosity: p = 0..P
    idx = list(range(0, P + 1))
    K = len(idx)
    H = br.H("tensor", x1, x2, omega, idx, dps)
    rhs = mp.matrix(2 * K, 1)
    rhs[0] = mp.mpf(5) / 2 * x1
    rhs[K] = mp.mpf(5) / 2 * x2
    y = mp.lu_solve(H, rhs)
    out["eta"] = T * (x1 * y[0] + x2 * y[K])
    # thermal conductivity, zero diffusion: p = 1..P
    idx = list(range(1, P + 1))
    K = len(idx)
    H = br.H("vector", x1, x2, omega, idx, dps)
    rhs = mp.matrix(2 * K, 1)
    rhs[0] = -mp.mpf(15) / 4 * x1 * mp.sqrt(2 * T / m1)
    rhs[K] = -mp.mpf(15) / 4 * x2 * mp.sqrt(2 * T / m2)
    a = mp.lu_solve(H, rhs)
    out["lambda"] = -mp.mpf(5) / 4 * mp.sqrt(2 * T) * (x1 * a[0] / mp.sqrt(m1) + x2 * a[K] / mp.sqrt(m2))
    # diffusion and thermal diffusion: p = 0..P
    idx = list(range(0, P + 1))
    K = len(idx)
    H = br.H("vector", x1, x2, omega, idx, dps)
    c = [mp.mpf(0)] * (2 * K)
    c[0] = x1 * mp.sqrt(m1)
    c[K] = x2 * mp.sqrt(m2)
    rd = [mp.mpf(0)] * (2 * K)
    rd[0] = mp.mpf(3) / 2 * mp.sqrt(2 * T / m1)
    rd[K] = -mp.mpf(3) / 2 * mp.sqrt(2 * T / m2)
    d = solve_constrained(H, rd, c)
    rt = [mp.mpf(0)] * (2 * K)
    if K > 1:
        rt[1] = -mp.mpf(15) / 4 * x1 * mp.sqrt(2 * T / m1)
        rt[K + 1] = -mp.mpf(15) / 4 * x2 * mp.sqrt(2 * T / m2)
    at = solve_constrained(H, rt, c)
    D12 = x1 * x2 / 2 * mp.sqrt(2 * T) * (d[0] / mp.sqrt(m1) - d[K] / mp.sqrt(m2))
    DT = x1 * x2 / 2 * mp.sqrt(2 * T) * (at[0] / mp.sqrt(m1) - at[K] / mp.sqrt(m2))
    out["D12"] = D12
    out["D_T"] = DT
    out["k_T"] = DT / D12
    out["alpha_T"] = DT / D12 / (x1 * x2)
    return out


def rigid_omega(m1, m2, T):
    mu = {"11": m1 / 2, "22": m2 / 2, "12": m1 * m2 / (m1 + m2)}

    def om(pair, l, s):
        ql = 1 - (1 + (-1) ** l) / (2 * (1 + l))
        return np.sqrt(T / (2 * np.pi * mu[pair])) * np.pi * ql * float(mp.factorial(s + 1)) / 2
    return om
