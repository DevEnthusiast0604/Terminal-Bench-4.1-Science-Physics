"""Exploration (v5): mixture transport from the stable quadrature kernels (mixq.py).
H blocks = factor * sum_l sum_i W_i c[l](x_i) Qt_pair^(l)(x_i), where sum_i W_i f(x_i) ~ int_0^inf e^-x x f(x) dx and
Qt^(l) = 2 pi int (1 - P_l(cos chi)) b db (units sigma^2). Omega-like factor sqrt(T / (2 pi mu)) / 2.
    python -B mixsolve2.py rigid|maxwell m1 m2 x1 P [T]"""
import sys
import time

import numpy as np
from scipy.special import roots_genlaguerre

from mixq import Kernel, types
from survey import props


def kernels_at(m1, m2, P, xs):
    """{kind: {type: array (Nx, Lout, P+1, P+1)}}"""
    out = {}
    for kind in ("vector", "tensor"):
        out[kind] = {}
        for name, prm in types(m1, m2).items():
            K = Kernel(*prm, P, kind)
            out[kind][name] = np.array([K.c(x) for x in xs])
    return out


def assemble(ker, W, Qt, m1, m2, x1, T, P):
    """Full (2(P+1))^2 H for one kind; Qt[pair] = array (Nx, Lout) of Qt^(l)(x_i)."""
    x2 = 1 - x1
    mu = {"11": m1 / 2, "22": m2 / 2, "12": m1 * m2 / (m1 + m2)}
    fac = {k: np.sqrt(T / (2 * np.pi * v)) / 2 for k, v in mu.items()}

    def block(c, pair, even_only):
        Lout = c.shape[1]
        wl = W[:, None] * Qt[pair][:, :Lout]
        if even_only:
            wl = wl * (np.arange(Lout) % 2 == 0)[None, :]
        wl[:, 0] = 0.0
        return fac[pair] * np.einsum("il,ilpq->pq", wl, c)

    H11 = 16 * x1 * x1 * block(ker["like"], "11", True) + 8 * x1 * x2 * block(ker["11"], "12", False)
    H22 = 16 * x2 * x2 * block(ker["like"], "22", True) + 8 * x1 * x2 * block(ker["22"], "12", False)
    H12 = 8 * x1 * x2 * block(ker["12"], "12", False)
    return np.block([[H11, H12], [H12.T, H22]])


if __name__ == "__main__":
    model, m1, m2, x1, P = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
    T = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
    if model == "rigid":
        xs, W = roots_genlaguerre(P + 4, 1.0)          # exact: Qt constant
        q = lambda x, L: np.where(np.arange(L)[None, :] >= 1, np.pi, 0.0) * np.ones((len(x), 1))
    else:                                              # Maxwell molecules: g Qt const -> Qt ~ 1/sqrt(x)
        xs, W = roots_genlaguerre(P + 4, 0.5)          # int e^-x x^(1/2) (...) exact
        W = W * np.sqrt(xs)                            # so that sum W f = int e^-x x f
        q = lambda x, L: (np.where(np.arange(L)[None, :] >= 1, 1.0 + 0.3 * np.arange(L)[None, :] ** 0.5, 0.0)
                          / np.sqrt(x)[:, None])
    t0 = time.time()
    ker = kernels_at(m1, m2, P, xs)
    t1 = time.time()
    H = {}
    for kind in ("vector", "tensor"):
        L = ker[kind]["like"].shape[1]
        Qt = {pr: q(xs, L) for pr in ("11", "22", "12")}
        H[kind] = assemble(ker[kind], W, Qt, m1, m2, x1, T, P)
    print("%s m1 %g m2 %g x1 %g T %g P %d: kernels %.1f s" % (model, m1, m2, x1, T, P, t1 - t0))
    prev = None
    for Pm in list(range(1, min(P, 8) + 1)) + list(range(10, P + 1, 2)):
        r = props(H["tensor"], H["vector"], m1, m2, x1, T, Pm)
        line = "P=%2d " % Pm + " ".join("%s %.10f" % (k, float(v)) for k, v in r.items())
        if prev:
            line += "  | incr " + " ".join("%.1e" % abs(float(r[k] / prev[k] - 1)) if prev[k] != 0 else "-" for k in r)
        print(line, flush=True)
        prev = r
