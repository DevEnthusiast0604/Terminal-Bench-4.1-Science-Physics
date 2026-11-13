"""Exact bracket-integral coefficients for the Chapman-Enskog Sonine expansions of a simple gas (author's prototype).

Reduced velocities C = c sqrt(m / 2kT). Two molecules: C1 = G - g/2, C2 = G + g/2, |g|^2 = 2 gamma^2, G ~ N(0, I/4).
X = G + u, Y = G + v with |u| = |v| = gamma/sqrt(2), u.v = kappa gamma^2 / 2.
M(t1, t2, t3) = E[exp(t1 X^2 + t2 Y^2 + t3 X.Y)] = (1 - tau/2)^(-3/2) exp(gamma^2 Phi / (2 - tau)),
    tau = t1 + t2 + t3, Phi = t1 + t2 + kappa t3 + (kappa - 1)(t1 t2 - t3^2 / 4),
so  M = sum_n gamma^2n 2^-n / n! Phi^n (1 - tau/2)^(-3/2 - n), expanded multinomially below (exact rationals).

W_pq(kappa, gamma^2) = E[F_p(X) . F_q(Y)]:
    viscosity     F_p = S_5/2^(p)(C^2) C°C     (X°X : Y°Y = (X.Y)^2 - X^2 Y^2 / 3)
    conductivity  F_p = S_3/2^(p)(C^2) C       p >= 1
    diffusion     F_p = S_3/2^(p)(C^2) C       tracer (only molecule 1's function changes), p >= 0
Single-gas bracket: A = 4 [W(1) + W(-1) - W(c) - W(-c)] = 8 sum_{j, k even} w_jk gamma^2j (1 - c^k), c = cos chi.
Tracer bracket:     A = 2 [W(1) - W(c)]              = 2 sum_{j, k} w_jk gamma^2j (1 - c^k).
H_pq is then proportional to sum coef_ls Omega^(l, s), Omega^(l,s) = int exp(-g^2) g^(2s+3) Q^(l)(g) dg.
"""
import json
import sys
import time
from fractions import Fraction
from math import comb, factorial

HALF = Fraction(1, 2)


def rising(x, r):
    out = Fraction(1)
    for s in range(r):
        out *= x + s
    return out


def moment(i, j, m):
    """E[(X^2)^i (Y^2)^j (X.Y)^m] as {(n, e): coef} meaning coef gamma^(2n) kappa^e."""
    out = {}
    pre = factorial(i) * factorial(j) * factorial(m)
    for n4 in range(min(i, j) + 1):
        for n1 in range(i - n4 + 1):
            for n2 in range(j - n4 + 1):
                for n3, n5 in ((0, 0), (1, 0), (2, 0), (0, 1)):
                    c = m - n3 - 2 * n5
                    if c < 0:
                        continue
                    a, b = i - n1 - n4, j - n2 - n4
                    n = n1 + n2 + n3 + n4 + n5
                    r = a + b + c
                    coef = (Fraction(pre, factorial(n1) * factorial(n2) * factorial(n3) * factorial(n4) * factorial(n5))
                            * HALF ** n * Fraction(-1, 4) ** n5
                            * rising(Fraction(3, 2) + n, r) * HALF ** r / (factorial(a) * factorial(b) * factorial(c)))
                    e = n4 + n5
                    for t in range(e + 1):
                        key = (n, n3 + t)
                        out[key] = out.get(key, 0) + coef * comb(e, t) * (-1) ** (e - t)
    return {key: v for key, v in out.items() if v != 0}


def sonine(nu, p):
    """Coefficients alpha_i of S_nu^(p)(x) = sum_i alpha_i x^i (Chapman-Cowling normalisation, S^(0) = 1)."""
    return [Fraction((-1) ** i, factorial(i) * factorial(p - i)) * rising(nu + i + 1, p - i) for i in range(p + 1)]


def add(acc, poly, scale):
    for key, v in poly.items():
        acc[key] = acc.get(key, 0) + scale * v


def w_matrix(prop, P):
    """{(p, q): {(j, k): coef}} for p, q = 0..P."""
    nu = Fraction(5, 2) if prop == "visc" else Fraction(3, 2)
    alphas = [sonine(nu, p) for p in range(P + 1)]
    cache = {}

    def mom(i, j, m):
        if (i, j, m) not in cache:
            cache[(i, j, m)] = moment(i, j, m)
        return cache[(i, j, m)]

    out = {}
    for p in range(P + 1):
        for q in range(p, P + 1):
            acc = {}
            for i, ai in enumerate(alphas[p]):
                for l, al in enumerate(alphas[q]):
                    if prop == "visc":
                        add(acc, mom(i, l, 2), ai * al)
                        add(acc, mom(i + 1, l + 1, 0), -ai * al / 3)
                    else:
                        add(acc, mom(i, l, 1), ai * al)
            out[(p, q)] = {key: v for key, v in acc.items() if v != 0}
    return out


def omega_coefs(W, prop):
    """{(j, k): w} for one (p, q) -> {(l, s): coef} with H_pq ~ sum coef * Omega^(l, s)."""
    out = {}
    for (j, kk), c in W.items():
        if kk == 0:
            continue
        if prop in ("visc", "cond"):
            if kk % 2:
                continue
            fac = 8
        else:
            fac = 2
        out[(kk, j)] = out.get((kk, j), 0) + fac * c
    return {key: v for key, v in out.items() if v != 0}


def all_coefs(P):
    res = {}
    for prop in ("visc", "cond", "diff"):
        Wm = w_matrix("cond" if prop == "diff" else prop, P)
        lo = 1 if prop == "cond" else 0
        res[prop] = {pq: omega_coefs(W, prop) for pq, W in Wm.items() if min(pq) >= lo}
    return res


if __name__ == "__main__":
    P = int(sys.argv[1])
    t0 = time.time()
    res = all_coefs(P)
    print("P=%d: %.1f s" % (P, time.time() - t0))
    if len(sys.argv) > 2:
        ser = {prop: {"%d,%d" % pq: [[l, s, str(c)] for (l, s), c in sorted(d.items())] for pq, d in v.items()}
               for prop, v in res.items()}
        with open(sys.argv[2], "w", newline="\n") as fh:
            json.dump(ser, fh)
