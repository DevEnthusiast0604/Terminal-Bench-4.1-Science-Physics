"""Checks of brackets.py (author's prototype): first-approximation structure, Maxwell molecules (Sonine polynomials are
eigenfunctions, so every off-diagonal bracket vanishes for any angular law), and rigid spheres (exact rationals:
CC second approximations 1 + 3/202 for viscosity and 1 + 1/44 for conductivity; limits 1.016034 and 1.025218)."""
import sys
import time
from fractions import Fraction
from math import factorial

import brackets as B


def omega_hs(l, s):
    return Fraction(factorial(s + 1), 2) * (1 - Fraction(1 + (-1) ** l, 2 * (l + 1)))


def matrix(coefs, omega, idx):
    return [[sum(c * omega(l, s) for (l, s), c in coefs[(min(p, q), max(p, q))].items()) for q in idx] for p in idx]


def inv00(H):
    """(H^-1)_00 by exact Gaussian elimination."""
    n = len(H)
    A = [row[:] + [Fraction(int(i == 0))] for i, row in enumerate(H)]
    for col in range(n):
        piv = next(r for r in range(col, n) if A[r][col] != 0)
        A[col], A[piv] = A[piv], A[col]
        for r in range(n):
            if r != col and A[r][col] != 0:
                f = A[r][col] / A[col][col]
                A[r] = [x - f * y for x, y in zip(A[r], A[col])]
    return A[0][n] / A[0][0]


P = int(sys.argv[1])
t0 = time.time()
res = B.all_coefs(P)
print("coefficients up to p = %d in %.1f s" % (P, time.time() - t0))
print("H_00 visc:", res["visc"][(0, 0)])
print("H_11 cond:", res["cond"][(1, 1)])
print("H_00 diff:", res["diff"][(0, 0)])
# Maxwell molecules: Omega^(l,s) = A_l Gamma(s + 3/2) / 2 for any A_l, so each l must cancel on its own
bad = 0
for prop in res:
    for (p, q), d in res[prop].items():
        if p == q:
            continue
        for l in {l for l, _ in d}:
            tot = sum(c * B.rising(Fraction(3, 2), s) for (ll, s), c in d.items() if ll == l)
            if tot != 0:
                bad += 1
print("Maxwell off-diagonal brackets that do not vanish:", bad)
for prop, lo in (("visc", 0), ("cond", 1), ("diff", 0)):
    fs = []
    for Mord in range(1, P + 2 - lo):
        idx = list(range(lo, lo + Mord))
        H = matrix(res[prop], omega_hs, idx)
        fs.append(H[0][0] * inv00(H))
    print(prop, "rigid spheres f^(M), M = 1..%d:" % len(fs), " ".join("%.7f" % float(f) for f in fs))
    if len(fs) > 1:
        print("   second approximation exactly", fs[1], "=", "1 + %s" % (fs[1] - 1))
