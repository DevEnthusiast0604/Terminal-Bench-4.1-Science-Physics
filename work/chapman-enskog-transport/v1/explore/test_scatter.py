"""Checks of scatter.py (author's prototype): Lennard-Jones orbiting constants, deflection angles against a direct
integration of the equations of motion, and LJ collision integrals at T* = 1 (tabulated Omega(1,1)* ~ 1.4398,
Omega(2,2)* ~ 1.5873)."""
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp

import scatter as S

A = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
pot = S.Kihara(A)
sc = S.Scatter(pot)
print("A=%.3f r_m=%.6f E_c=%.6f r_c=%.6f h_max=%.6f r_h=%.6f" % (A, pot.rm, pot.E_c, pot.r_c, pot.h_max, pot.r_h))


def chi_ode(b, E, X0=400.0):
    """Deflection from Newton's equations (reduced mass 1): cos chi from the outgoing velocity."""
    v = np.sqrt(2.0 * E)

    def rhs(t, y):
        x, yy, vx, vy = y
        r = np.hypot(x, yy)
        f = -pot.dV(r) / r
        return [vx, vy, f * x, f * yy]

    def leave(t, y):
        return np.hypot(y[0], y[1]) - X0 * 1.0001
    leave.terminal, leave.direction = True, 1
    y0 = [-np.sqrt(X0 ** 2 - b ** 2), b, v, 0.0]
    sol = solve_ivp(rhs, [0, 1e7], y0, method="DOP853", rtol=1e-12, atol=1e-12, events=leave)
    vx, vy = sol.y[2, -1], sol.y[3, -1]
    return vx / np.hypot(vx, vy)


for E, bs in ((0.3, [0.5, 1.2, None, 2.5]), (0.79, [0.9, 1.5, 1.9]), (2.0, [0.3, 1.0, 1.4]), (30.0, [0.2, 0.8])):
    if E < pot.E_c:
        bo, ro = sc.b_orb(E)
        bs = [b if b is not None else bo * (1 - 1e-4) for b in bs] + [bo * (1 + 1e-4)]
        print("E=%.3f b_orb=%.6f r_orb=%.6f" % (E, bo, ro))
    for b in bs:
        c1 = float(np.cos(sc.chi(np.array([b]), E))[0])
        c2 = chi_ode(b, E)
        print("  E=%-6g b=%-10.6f cos chi quad %.12f  ode %.12f  diff %.1e" % (E, b, c1, c2, c1 - c2))

t0 = time.time()
for E in (0.05, 0.5, 0.79, 0.81, 3.0, 50.0):
    q = S.Q_all(sc, E, 4)
    print("Q^(l)(E=%g)/pi sigma^2 = %s  (%.1f s)" % (E, " ".join("%.10f" % x for x in q), time.time() - t0))
