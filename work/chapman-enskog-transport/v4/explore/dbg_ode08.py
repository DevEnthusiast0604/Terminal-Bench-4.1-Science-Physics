"""Which (E, b) pairs disagree at a = 0.8 between the quadrature chi and Newton's equations?"""
import os
import sys

import numpy as np
from scipy.integrate import solve_ivp

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "tasks", "active",
                                "chapman-enskog-transport", "tests"))
import ce_ref as R  # noqa: E402

A = float(sys.argv[1]) if len(sys.argv) > 1 else 0.8
pot = R.Kihara(A)
sc = R.Scatter(pot, de_h=1 / 32)


def chi_ode(b, E, X0=400.0, rtol=1e-13):
    v = np.sqrt(2.0 * E)

    def rhs(t, y):
        r = np.hypot(y[0], y[1])
        f = -pot.dV(r) / r
        return [y[2], y[3], f * y[0], f * y[1]]

    def leave(t, y):
        return np.hypot(y[0], y[1]) - X0 * 1.0001
    leave.terminal, leave.direction = True, 1
    sol = solve_ivp(rhs, [0, 1e9], [-np.sqrt(X0 ** 2 - b ** 2), b, v, 0.0], method="DOP853", rtol=rtol,
                    atol=rtol, events=leave)
    rmin = np.hypot(sol.y[0], sol.y[1]).min()
    return sol.y[2, -1] / np.hypot(sol.y[2, -1], sol.y[3, -1]), sol.status, sol.t[-1], rmin, sol.nfev


print("E_c", pot.E_c, "h_max", pot.h_max, "r_h", pot.r_h)
for E in (0.03, 0.9 * pot.E_c, 1.1 * pot.E_c, 60.0):
    bs = sc.b_star(E)
    for frac in (0.2, 0.7, 0.99, 1.01, 1.4, 2.5):
        b = frac * bs
        cq = float(np.cos(sc.chi(np.array([b]), E))[0])
        co, st, tend, rmin, nfev = chi_ode(b, E)
        flag = "  <<<" if abs(cq - co) > 1e-8 else ""
        print("E=%-8.4g b=%-9.5g (%.2f b*): cos chi quad %+.12f ode %+.12f diff %.1e  status %d t %.3g rmin %.5f nfev %d%s"
              % (E, b, frac, cq, co, abs(cq - co), st, tend, rmin, nfev, flag), flush=True)
