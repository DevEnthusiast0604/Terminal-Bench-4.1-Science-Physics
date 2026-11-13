"""Deflection-angle checks (author's prototype): direct integration of Newton's equations, point-to-point noise,
quadrature-step convergence, and cross sections for three DE steps."""
import sys
import numpy as np
from scipy.integrate import solve_ivp
import scatter as S

A = float(sys.argv[1])
pot = S.Kihara(A)
sc = S.Scatter(pot)


def chi_ode(b, E, X0=400.0):
    v = np.sqrt(2.0 * E)

    def rhs(t, y):
        x, yy, vx, vy = y
        r = np.hypot(x, yy)
        f = -pot.dV(r) / r
        return [vx, vy, f * x, f * yy]

    def leave(t, y):
        return np.hypot(y[0], y[1]) - X0 * 1.0001
    leave.terminal, leave.direction = True, 1
    sol = solve_ivp(rhs, [0, 1e9], [-np.sqrt(X0 ** 2 - b ** 2), b, v, 0.0], method="DOP853", rtol=1e-13,
                    atol=1e-13, events=leave)
    vx, vy = sol.y[2, -1], sol.y[3, -1]
    return vx / np.hypot(vx, vy)


worst = 0.0
for E in (0.01, 0.3, 0.9 * pot.E_c, 1.1 * pot.E_c, 5.0, 100.0):
    bst = S.b_star(sc, E)
    for frac in (0.2, 0.7, 0.99, 1.01, 1.4, 2.5):
        b = frac * bst
        d = float(np.cos(sc.chi(np.array([b]), E))[0]) - chi_ode(b, E)
        worst = max(worst, abs(d))
print("ODE check: worst |cos chi quad - cos chi ode| = %.1e" % worst)
for E in (3e-5, 1e-3, 0.3, 1.9, 2.0, 30.0, 1.5e4):
    bst = S.b_star(sc, E)
    noise = 0.0
    for frac in (0.3, 0.6, 0.75, 0.99, 1.01, 1.5, 3.0, 10.0):
        b = frac * bst + np.arange(41) * 1e-9
        c = sc.chi(b, E)
        p = np.polyfit(b - b[0], c, 2)
        noise = max(noise, np.abs(c - np.polyval(p, b - b[0])).max())
    scs = {h: S.Scatter(pot, de_h=h) for h in (1 / 32, 1 / 64, 1 / 128)}
    bb = np.concatenate([np.linspace(0.01, 0.98, 200), np.linspace(1.02, 6, 200), [10, 30, 100, 1000]]) * bst
    c = {h: s.chi(bb, E) for h, s in scs.items()}
    print("E=%-8g noise %.1e   max|chi(h) - chi(1/128)|: h=1/32 %.1e, h=1/64 %.1e;  chi(1000 b*) = %.3e" % (
        E, noise, np.abs(c[1 / 32] - c[1 / 128]).max(), np.abs(c[1 / 64] - c[1 / 128]).max(), c[1 / 128][-1]))
for E in (3e-5, 1.9, 30.0):
    qs = {round(1 / h): S.Q_all(S.Scatter(pot, de_h=h), E, 14, 1e-11) for h in (1 / 32, 1 / 64, 1 / 128)}
    print("E=%-8g Q1: %s   max rel diff (1/32, 1/64) vs 1/128: %.1e %.1e" % (
        E, " ".join("%.13f" % q[0] for q in qs.values()), np.abs(qs[32] / qs[128] - 1).max(),
        np.abs(qs[64] / qs[128] - 1).max()))
