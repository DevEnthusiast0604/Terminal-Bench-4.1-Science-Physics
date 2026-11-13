"""Adds the [bulk] section to the v15 draft's tests/checks.py. Not shipped."""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:90]
    s = s.replace(old, new)


rep('''  [gap]        the gap conductivity of combine against a numerical solution of the layer's boundary-value problem;
and the convergence of the reference's own truncations,
  [P]          the convergence in the Sonine index of each of the 24 graded values, from the reference brackets;''',
    '''  [gap]        the gap conductivity of combine against a numerical solution of the layer's boundary-value problem;
  [bulk]       the bulk viscosity of combine against a numerical integration of the uniform expansion itself;
and the convergence of the reference's own truncations,
  [P]          the convergence in the Sonine index of each of the 32 graded values, from the reference brackets;''')
rep('''    say("[gap] worst |numerical solution of the layer / combine - 1| over the eight sets: %.1e" % worst)
''', '''    say("[gap] worst |numerical solution of the layer / combine - 1| over the eight sets: %.1e" % worst)


def expansion(gas, B, T0, N0, TAU, rate):
    """(p_e - p) / div v at the end of a uniform expansion at div v = rate / TAU from equilibrium at T0 and N0, run for
    30 TAU by scipy DOP853 on the full nonlinear equations as stated, nothing linearized: the energy per molecule
    e = 3/2 T + theta x2 falls as de/dt = -T div v (p = n T, no heat exchanged) and dx2/dt = (x2e(T) - x2) / TAU;
    p_e from the equilibrium state of the same n and e (brentq). Also returns the end state (T, n)."""
    from scipy.integrate import solve_ivp
    from scipy.optimize import brentq
    theta = G.equilibrium(gas, B, T0)[1]

    def x2e(T):
        return 1.0 - G.equilibrium(gas, B, T)[0]

    D = rate / TAU

    def f(t, y):
        T, x2 = y
        dx2 = (x2e(T) - x2) / TAU
        return [(-T * D - theta * dx2) / 1.5, dx2]

    t_end = 30.0 * TAU
    sol = solve_ivp(f, (0.0, t_end), [T0, x2e(T0)], method="DOP853", rtol=1e-13, atol=1e-18)
    assert sol.success, sol.message
    T, x2 = sol.y[0, -1], sol.y[1, -1]
    n = N0 * math.exp(-D * t_end)
    e = 1.5 * T + theta * x2
    Te = brentq(lambda u: 1.5 * u + theta * x2e(u) - e, 0.5 * T, 2.0 * T, xtol=1e-17, rtol=1e-15)
    return n * (Te - T) / D, T, n


def bulk_check():
    """For each graded set: eta_b from the integrated expansion at three rates, extrapolated to rate 0 (Richardson,
    rates tau div v = 1e-3, 2e-3 and 4e-3), against combine at each run's end state; and what eta_b would be with
    tau taken as the relaxation time at fixed energy, or with the frozen heat capacity 5/2 of a rotating molecule."""
    worst = 0.0
    for name in G.CASES:
        gas, B, T = G.CASES[name][0], float(G.CASES[name][3]), float(G.CASES[name][4])
        N, W, TAU = G.gap_inputs(name)
        ratio = []
        for rate in (1e-3, 2e-3, 4e-3):
            eb, Tn, n = expansion(gas, B, T, N, TAU, rate)
            x1n, theta = G.equilibrium(gas, B, Tn)
            ratio.append(eb / G.bulk(x1n, theta, Tn, n, TAU))
        r0 = (8.0 * ratio[0] - 6.0 * ratio[1] + ratio[2]) / 3.0
        worst = max(worst, abs(r0 - 1.0))
        x1, theta = G.equilibrium(gas, B, T)
        cR = x1 * (1.0 - x1) * (theta / T) ** 2
        ref = G.bulk(x1, theta, T, N, TAU)
        fixed_e = N * T * TAU * cR / (1.5 * (1.5 + cR))
        rot = N * T * TAU * cR / (2.5 + cR) ** 2
        say("[bulk] %s: c_R %.5g, eta_b %.6g (%.4g times the shear viscosity); integrated expansion / combine - 1: "
            "%+.1e at tau div v = 1e-3, extrapolated to 0 %+.1e; tau taken at fixed energy would be off by %+.1f "
            "tolerances, a frozen heat capacity 5/2 by %+.1f" % (
                label(name), cR, ref, ref / G.compute(name)[0]["viscosity"], ratio[0] - 1.0, r0 - 1.0,
                (fixed_e / ref - 1.0) / TOL, (rot / ref - 1.0) / TOL))
    say("[bulk] worst |integrated expansion / combine - 1| extrapolated to rate 0 over the eight sets: %.1e" % worst)
''')
rep('''    gap()
    sonine()''', '''    gap()
    bulk_check()
    sonine()''')
rep('''    say("[P] worst |P = p minus P = %d| over the 24 graded values''',
    '''    say("[P] worst |P = p minus P = %d| over the 32 graded values''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
