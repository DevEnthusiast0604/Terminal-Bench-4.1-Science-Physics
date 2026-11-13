"""Sonine convergence of the light-tracer problem in the Lorentz limit (m2 -> inf, x1 -> 0), for one (A, T*).

    python -B lorentz.py A T [PMAX]

In that limit a light molecule only turns: the vector collision operator is multiplication by
nu(x) = sqrt(x) Qt^(1)(x T*), so the exact solutions are src / nu and the Sonine (Galerkin) solutions use the moment
matrix of nu. Prints, for P = 8 .. PMAX, the errors of D and alpha_T (= D_T / D) in units of 2e-5 relative.
Q is sampled once on a log grid and interpolated, which is consistent for both the exact and the Galerkin values.
"""
import math
import os
import sys
import time

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import CubicSpline

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "../../../../tasks/active/chapman-enskog-transport/tests")))
import ce_ref as R  # noqa: E402

A, T = float(sys.argv[1]), float(sys.argv[2])
PMAX = int(sys.argv[3]) if len(sys.argv) > 3 else 512
t0 = time.time()
pot = R.Kihara(A)
sc = R.Scatter(pot, de_h=1.0 / 32)
Ec = pot.E_c
xmax = 4.0 * PMAX + 200.0
lnE = np.unique(np.concatenate([np.linspace(math.log(1e-6 * T), math.log(xmax * T), 700),
                                np.log(Ec * (1 + np.array([-1, 1])[:, None] * np.geomspace(1e-6, 0.5, 40)).ravel())]))
Q = np.array([R.Q_all(sc, math.exp(u), 1, rel=1e-11)[0] for u in lnE])
spl = CubicSpline(lnE, np.log(Q))
print("Q sampled at %d energies in %.0f s (E_c = %.4f, x_c = %.5f)" % (len(lnE), time.time() - t0, Ec, Ec / T))

# composite Gauss-Legendre in u = sqrt(x), u_c = sqrt(x_c) a panel boundary, graded toward 0 and toward u_c
uc, umax = math.sqrt(Ec / T), math.sqrt(xmax)
edges = np.unique(np.concatenate([[0.0], uc * np.geomspace(1e-4, 1, 30), uc * (1 + np.geomspace(1e-5, 0.3, 25)),
                                  np.arange(0.0, umax, 0.08), [umax]]))
xg, wg = leggauss(20)
u = np.concatenate([0.5 * (a + b) + 0.5 * (b - a) * xg for a, b in zip(edges[:-1], edges[1:])])
wu = np.concatenate([0.5 * (b - a) * wg for a, b in zip(edges[:-1], edges[1:])])
x = u * u
dx = 2 * u * wu
nu = np.sqrt(x) * np.exp(spl(np.log(np.maximum(x, 1e-300) * T)))

al = 1.5
F = np.empty((PMAX + 1, len(x)))
with np.errstate(divide="ignore"):
    F[0] = np.exp(0.5 * (al * np.log(x) - x - math.lgamma(al + 1)))
F[1] = (al + 1 - x) / math.sqrt(al + 1) * F[0]
for q in range(1, PMAX):
    F[q + 1] = ((2 * q + al + 1 - x) * F[q] - math.sqrt(q * (q + al)) * F[q - 1]) / math.sqrt((q + 1) * (q + al + 1))
sw = np.exp(0.5 * (al * np.log(x) - x))           # sqrt of the weight x^3/2 e^-x
Amat = (F * (nu * dx)) @ F.T
bD = F @ (sw * dx)
bT = F @ (sw * (x - 2.5) * dx)
w = sw * sw * dx
D_ex = np.sum(w / nu)
DT_ex = np.sum(w * (x - 2.5) / nu)
aT_ex = DT_ex / D_ex
print("exact Lorentz: D %.10g, alpha_T %.10g" % (D_ex, aT_ex))
rows = []
for P in [8, 16, 24, 32, 48, 64, 80, 96, 128, 160, 192, 256, 320, 384, 448, 512, 640, 768, 896, 1024]:
    if P > PMAX:
        break
    n = P + 1
    sol = np.linalg.solve(Amat[:n, :n], np.stack([bD[:n], bT[:n]], axis=1))
    D = bD[:n] @ sol[:, 0]
    DT = bD[:n] @ sol[:, 1]
    aT = DT / D
    rows.append((P, (D_ex - D) / (2e-5 * D_ex), (aT - aT_ex) / max(2e-5 * abs(aT_ex), 1e-6)))
    print("P %4d  D err %10.3f tol   alpha_T err %10.3f tol" % rows[-1])
print("done in %.0f s" % (time.time() - t0))
