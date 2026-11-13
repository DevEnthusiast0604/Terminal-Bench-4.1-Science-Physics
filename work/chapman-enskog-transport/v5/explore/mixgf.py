"""Exploration (v5): Sonine bracket coefficients for a binary mixture with unequal masses, from the Gaussian
moment generating function, as truncated 2D power series in the Sonine generating variables (w1, w2).

Collision pair (k, l), reduced velocities C = c sqrt(m / 2kT):
    C_k = sqrt(M_k) G - sqrt(M_l) g,   C_l = sqrt(M_l) G + sqrt(M_k) g,   M_k = m_k / (m_k + m_l),
G and g independent N(0, I/2); after the collision g -> g' (|g'| = |g|, angle chi).
A "type" is X = a G + alpha u1, Y = b G + beta u2 with |u1| = |u2| = gamma, u1.u2 = kappa gamma^2:
    like (k = l):          a = b = 1/sqrt2,  alpha = beta = -1/sqrt2
    "kk" (both on k):      a = b = sqrt(M_k), alpha = beta = -sqrt(M_l)
    "kl" (k and l):        a = sqrt(M_k), alpha = -sqrt(M_l), b = sqrt(M_l), beta = sqrt(M_k)
W_pq(x = gamma^2, kappa) = E_G[psi_p(X) . psi_q(Y)] with psi_p = S_3/2^(p)(X^2) X (vector) or
S_5/2^(p)(X^2) X°X (tensor). GF[n][k] is the (N, N) array of the coefficient of x^n kappa^k, indexed [p, q].
"""
import numpy as np
from math import factorial, comb


_IDX = {}


def _index(N):
    if N not in _IDX:
        i = np.arange(N)[:, None, None]
        k = np.arange(N)[None, :, None]
        l = np.arange(N)[None, None, :]
        bi = np.where(i >= k, i - k, N)              # Bs[i, k, l] = B[i - k, l] (row N = zeros)
        kk = np.arange(N)[:, None, None]
        ll = np.arange(N)[None, :, None]
        j = np.arange(N)[None, None, :]
        uj = np.where(j >= ll, j - ll, N)            # U[k, l, j] = A[k, j - l] (column N = zeros)
        _IDX[N] = (np.broadcast_to(bi, (N, N, N)), np.broadcast_to(l, (N, N, N)),
                   np.broadcast_to(kk, (N, N, N)), np.broadcast_to(uj, (N, N, N)))
    return _IDX[N]


def mul(A, B):
    """Truncated 2D series product: C[i, j] = sum_{k<=i, m<=j} A[k, m] B[i-k, j-m]."""
    N = A.shape[0]
    bi, bl, uk, uj = _index(N)
    Bp = np.zeros((N + 1, N))
    Bp[:N] = B
    Ap = np.zeros((N, N + 1))
    Ap[:, :N] = A
    Bs = Bp[bi, bl]                                  # (i, k, l)
    U = Ap[uk, uj]                                   # (k, l, j)
    return Bs.reshape(N, N * N) @ U.reshape(N * N, N)


def one(N):
    S = np.zeros((N, N))
    S[0, 0] = 1.0
    return S


def powr(S, nu, N):
    """S^nu for S[0,0] > 0 (binomial series in S/s0 - 1)."""
    s0 = S[0, 0]
    D = S / s0
    D[0, 0] = 0.0
    out = one(N)
    term = one(N)
    c = 1.0
    for k in range(1, 2 * N):
        term = mul(term, D)
        if not term.any():
            break
        c *= (nu - k + 1) / k
        out = out + c * term
    return out * s0 ** nu


def series_1d(N, coef_fn, axis):
    S = np.zeros((N, N))
    for k in range(N):
        if axis == 0:
            S[k, 0] = coef_fn(k)
        else:
            S[0, k] = coef_fn(k)
    return S


def gf(a, b, al, be, N, kind):
    """{(n, k): (N, N) array}: coefficient of x^n kappa^k of sum_pq w1^p w2^q W_pq."""
    I = one(N)
    T1 = series_1d(N, lambda k: -1.0 if k >= 1 else 0.0, 0)
    T2 = series_1d(N, lambda k: -1.0 if k >= 1 else 0.0, 1)
    OMA = I - a * a * T1 - b * b * T2                      # 1 - A0
    inv = powr(OMA, -1.0, N)
    inv2 = mul(inv, inv)
    T11, T22, T12 = mul(T1, T1), mul(T2, T2), mul(T1, T2)
    P0 = al * al * T1 + be * be * T2 + mul(a * a * al * al * T11 + b * b * be * be * T22, inv)
    P1 = 2.0 * a * b * al * be * mul(T12, inv)
    Q0 = a * b * mul(al * al * T1 + be * be * T2, inv) + a * b * mul(a * a * al * al * T11 + b * b * be * be * T22, inv2)
    Q1 = al * be * I + al * be * mul(a * a * T1 + b * b * T2, inv) + 2.0 * a * a * b * b * al * be * mul(T12, inv2)
    c1 = 1.5 * a * b * inv
    R0 = powr(OMA, -1.5, N)
    # powers
    P0p = [I]
    for j in range(1, 2 * N):
        P0p.append(mul(P0p[-1], P0) / j)
    P1p = [I]
    for k in range(1, N):
        P1p.append(mul(P1p[-1], P1) / k)
    E = {}
    for k in range(N):
        if not P1p[k].any():
            break
        for j in range(2 * N):
            if not P0p[j].any():
                break
            Enk = mul(P0p[j], P1p[k])
            if Enk.any():
                E[(j + k, k)] = mul(R0, Enk)            # M0_{n,k}
    get = lambda n, k: E.get((n, k))
    out = {}
    keys = set(E) | {(n + 1, k) for n, k in E} | {(n + 1, k + 1) for n, k in E}
    if kind == "tensor":
        keys |= {(n + 2, k) for n, k in E} | {(n + 2, k + 1) for n, k in E} | {(n + 2, k + 2) for n, k in E}
    if kind == "vector":
        pre = mul(series_1d(N, lambda k: comb_half(2.5, k), 0), series_1d(N, lambda k: comb_half(2.5, k), 1))
        cR, Q0R, Q1R = c1, Q0, Q1
        for n, k in keys:
            acc = np.zeros((N, N))
            for coefS, key in ((cR, (n, k)), (Q0R, (n - 1, k)), (Q1R, (n - 1, k - 1))):
                M0 = get(*key)
                if M0 is not None:
                    acc += mul(coefS, M0)
            if acc.any():
                out[(n, k)] = mul(pre, acc)
        return out
    # tensor
    c11 = 1.5 * (a * b) ** 2 * inv2
    inv3 = mul(inv2, inv)
    Bq0_0 = 4.0 * (a * a * al * al * T11 + b * b * be * be * T22)
    Bq0_1 = 8.0 * a * b * al * be * T12
    Bqp_0 = 4.0 * a * b * (al * al * T1 + be * be * T2)
    Bqp_1 = 4.0 * al * be * (b * b * T2 + a * a * T1)
    Bqpp_0 = (2.0 * b * b * al * al + 2.0 * a * a * be * be) * I
    Bqpp_1 = 4.0 * a * b * al * be * I
    F33_0 = 0.25 * mul(Bqpp_0, inv) + 0.5 * a * b * mul(Bqp_0, inv2) + 0.5 * (a * b) ** 2 * mul(Bq0_0, inv3)
    F33_1 = 0.25 * mul(Bqpp_1, inv) + 0.5 * a * b * mul(Bqp_1, inv2) + 0.5 * (a * b) ** 2 * mul(Bq0_1, inv3)
    A00 = mul(c1, c1) + c11
    A10 = 2.0 * mul(c1, Q0) + F33_0
    A11 = 2.0 * mul(c1, Q1) + F33_1
    A20, A21, A22 = mul(Q0, Q0), 2.0 * mul(Q0, Q1), mul(Q1, Q1)
    pre = mul(series_1d(N, lambda k: comb_half(3.5, k), 0), series_1d(N, lambda k: comb_half(3.5, k), 1))
    sq = mul(series_1d(N, lambda k: (1.0, -2.0, 1.0)[k] if k < 3 else 0.0, 0),
             series_1d(N, lambda k: (1.0, -2.0, 1.0)[k] if k < 3 else 0.0, 1))   # (1-w1)^2 (1-w2)^2
    for n, k in keys:
        acc = np.zeros((N, N))
        for coefS, key in ((A00, (n, k)), (A10, (n - 1, k)), (A11, (n - 1, k - 1)),
                           (A20, (n - 2, k)), (A21, (n - 2, k - 1)), (A22, (n - 2, k - 2))):
            M0 = get(*key)
            if M0 is not None:
                acc += mul(coefS, M0)
        M0 = get(n, k)
        if M0 is not None:
            d = np.zeros((N, N))
            ii, jj = np.arange(N), np.arange(N)
            d[:N - 1, :N - 1] = M0[1:, 1:] * (ii[1:, None] * jj[None, 1:])
            acc -= mul(sq, d) / 3.0
        if acc.any():
            out[(n, k)] = mul(pre, acc)
    return out


def comb_half(nu, k):
    """coefficient of w^k in (1 - w)^(-nu)."""
    c = 1.0
    for i in range(k):
        c *= (nu + i) / (i + 1)
    return c
