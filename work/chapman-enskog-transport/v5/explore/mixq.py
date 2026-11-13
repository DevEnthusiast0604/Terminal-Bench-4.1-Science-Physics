"""Exploration (v5): numerically stable mixture bracket kernels by Gauss quadrature over the centre-of-mass
velocity, with Legendre components in kappa = cos(chi).

Type (a, alpha; b, beta): X = a G + alpha gamma u1, Y = b G + beta gamma u2 (unit u1, u2, u1.u2 = kappa),
G ~ N(0, I/2), gamma^2 = x. W_pq(x, kappa) = E_G[psi_p(X) . psi_q(Y)] = sum_l c[l, p, q](x) P_l(kappa), with
psi_p = S_3/2^(p)(X^2) X (vector) or S_5/2^(p)(X^2) X°X (tensor).
With G = rho G^, mu1 = G^.u1, mu2 = G^.u2:  <A(mu1) B(mu2)>_{G^} = sum_L A_L B_L P_L(kappa) / (2L + 1).
"""
import numpy as np
from numpy.polynomial.legendre import leggauss, legvander


def rules(P):
    """(t, wt) Gauss-Laguerre alpha = 1/2 with P + 4 nodes (scipy, imported here only: the process-pool workers
    get the arrays and never import scipy, which crashes them on Windows)."""
    from scipy.special import roots_genlaguerre
    return roots_genlaguerre(P + 4, 0.5)


def sonine_table(nu, P, z):
    out = np.empty(z.shape + (P + 1,))
    out[..., 0] = 1.0
    if P >= 1:
        out[..., 1] = 1.0 + nu - z
    for p in range(1, P):
        out[..., p + 1] = ((2 * p + 1 + nu - z) * out[..., p] - (p + nu) * out[..., p - 1]) / (p + 1)
    return out


def kappa_times(c):
    """Legendre coefficients (axis 0) of kappa * sum_l c_l P_l."""
    L = c.shape[0]
    d = np.zeros_like(c)
    for l in range(L):
        if l >= 1:
            d[l] += c[l - 1] * l / (2 * l - 1)
        if l + 1 < L:
            d[l] += c[l + 1] * (l + 1) / (2 * l + 3)
    return d


class Kernel:
    def __init__(self, a, al, b, be, P, kind, tw=None):
        self.a, self.al, self.b, self.be, self.P, self.kind = a, al, b, be, P, kind
        self.nu = 1.5 if kind == "vector" else 2.5
        self.Lout = P + (1 if kind == "vector" else 2) + 1          # l = 0 .. Lout-1
        self.Lint = self.Lout + 2
        t, wt = tw if tw is not None else rules(P)
        self.t, self.wt = np.asarray(t), np.asarray(wt) * 2.0 / np.sqrt(np.pi)   # E_G = (2/sqrt(pi)) sum w f
        mu, wmu = leggauss(P + 4)
        self.mu = mu
        Ls = np.arange(self.Lint)
        self.PLw = (wmu[:, None] * (2 * Ls[None, :] + 1) / 2.0) * legvander(mu, self.Lint - 1)

    def _proj(self, s, m, xg, scale_fn):
        """Legendre projections of f(mu) * S(Z) for the side with coefficients (s, m) at gamma = xg."""
        rho = np.sqrt(self.t)[:, None]
        Z = (s * rho) ** 2 + (m * xg) ** 2 + 2 * s * m * rho * xg * self.mu[None, :]
        S = sonine_table(self.nu, self.P, Z)                          # (Nt, Nmu, P+1)
        Nt, Nmu, Np = S.shape
        out = {}
        for key, f in scale_fn(Z).items():
            G = (S * f[:, :, None]).transpose(0, 2, 1).reshape(Nt * Np, Nmu)
            out[key] = (G @ self.PLw).reshape(Nt, Np, -1).transpose(2, 0, 1)   # (Lint, Nt, P+1)
        return out

    def c(self, x):
        """c[l, p, q] at x = gamma^2."""
        a, al, b, be = self.a, self.al, self.b, self.be
        g = np.sqrt(x)
        rho = np.sqrt(self.t)
        mu = self.mu[None, :]
        one = np.ones((len(self.t), len(self.mu)))
        if self.kind == "vector":
            fx = lambda Z: {"0": one, "1": one * mu}
        else:
            fx = lambda Z: {"0": one, "1": one * mu, "2": one * mu * mu, "Z": Z}
        A = self._proj(a, al, g, fx)
        B = self._proj(b, be, g, fx)
        Ls = np.arange(self.Lint)[:, None, None]

        w = self.wt[None, :, None]
        inv = 1.0 / (2 * Ls + 1)

        def lin(*terms):
            # sum of coef_k * A[L, k, p] over the terms, with the t-node weights, as (L, p, k)
            acc = 0.0
            for Ak, ck in terms:
                acc = acc + Ak * (ck[None, :, None] if np.ndim(ck) else ck)
            return (acc * w).transpose(0, 2, 1)

        def prod(Al, Bk):
            # sum_k Al[L, p, k] B[L, k, q] / (2L + 1)
            return np.matmul(Al, Bk) * inv
        c0 = a * b * rho ** 2          # X.Y = c0 + c1 mu1 + c2 mu2 + c3 kappa (c3 independent of rho)
        c1 = b * al * rho * g
        c2 = a * be * rho * g
        c3 = al * be * x
        if self.kind == "vector":
            base = prod(lin((A["0"], c0), (A["1"], c1)), B["0"]) + prod(lin((A["0"], c2)), B["1"])
            res = base + c3 * kappa_times(prod(lin((A["0"], 1.0)), B["0"]))
        else:
            base = (prod(lin((A["0"], c0 * c0), (A["2"], c1 * c1), (A["1"], 2 * c0 * c1)), B["0"])
                    + prod(lin((A["0"], 2 * c0 * c2), (A["1"], 2 * c1 * c2)), B["1"])
                    + prod(lin((A["0"], c2 * c2)), B["2"]) - prod(lin((A["Z"], 1.0)), B["Z"]) / 3.0)
            kap = c3 * (prod(lin((A["0"], 2 * c0), (A["1"], 2 * c1)), B["0"]) + prod(lin((A["0"], 2 * c2)), B["1"]))
            kap2 = c3 * c3 * prod(lin((A["0"], 1.0)), B["0"])
            res = base + kappa_times(kap) + kappa_times(kappa_times(kap2))
        return res[:self.Lout]


def types(m1, m2):
    M1, M2 = m1 / (m1 + m2), m2 / (m1 + m2)
    r = 1 / np.sqrt(2)
    s1, s2 = np.sqrt(M1), np.sqrt(M2)
    return {"like": (r, -r, r, -r), "11": (s1, -s2, s1, -s2), "22": (s2, s1, s2, s1), "12": (s1, -s2, s2, s1)}
