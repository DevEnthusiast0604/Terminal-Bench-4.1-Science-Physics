import math, numpy as np
G, L = 9.79184, 1.00003
ROD = (1.40, -0.18, 1.18)
BOBS = [(2.6, -0.14, 0.0025), (0.6, 1.12, 0.0010)]
SL_M, SL_I = 2.2, 0.0010

def body(x):
    parts = [(ROD[0], 0.5 * (ROD[1] + ROD[2]), ROD[0] * (ROD[2] - ROD[1]) ** 2 / 12)] + BOBS + [(SL_M, x, SL_I)]
    M = sum(p[0] for p in parts); s = sum(p[0] * p[1] for p in parts) / M
    I = sum(p[2] + p[0] * (p[1] - s) ** 2 for p in parts)
    return s, I / M

def periods(x):
    s, k2 = body(x); ha, hb = s, L - s
    return 2 * math.pi * math.sqrt((k2 + ha * ha) / (G * ha)), 2 * math.pi * math.sqrt((k2 + hb * hb) / (G * hb)), ha, hb, k2

# exact crossing
lo, hi = 0.75, 0.84
for _ in range(80):
    mid = 0.5 * (lo + hi); d = periods(mid)[0] - periods(mid)[1]
    if (periods(lo)[0] - periods(lo)[1]) * d <= 0: hi = mid
    else: lo = mid
xs_true = 0.5 * (lo + hi); Tstar = periods(xs_true)[0]
print("x* %.5f  T* %.7f  2pi sqrt(L/g) %.7f" % (xs_true, Tstar, 2 * math.pi * math.sqrt(L / G)))
for X in ([0.70, 0.75, 0.84], [0.71, 0.76, 0.83], [0.72, 0.765, 0.82]):
    Ta = np.array([periods(x)[0] for x in X]); Tb = np.array([periods(x)[1] for x in X])
    ha = np.array([periods(x)[2] for x in X])
    print("positions", X, "rel diffs", np.round((Ta - Tb) / Ta * 100, 3), "% ; ha", np.round(ha, 4))
    # quadratic through 3 points for each
    pa, pb = np.polyfit(X, Ta, 2), np.polyfit(X, Tb, 2)
    r = np.roots(pa - pb); r = [v.real for v in r if abs(v.imag) < 1e-12 and X[0] - 0.05 < v.real < X[-1] + 0.05]
    xq = r[0]; Tq = np.polyval(pa, xq)
    # linear between bracketing two
    i = 1 if (Ta[1] - Tb[1]) * (Ta[2] - Tb[2]) < 0 else 0
    da, db = Ta[i + 1] - Ta[i], Tb[i + 1] - Tb[i]
    f = (Tb[i] - Ta[i]) / (da - db); xl = X[i] + f * (X[i + 1] - X[i]); Tl = Ta[i] + f * da
    # linear fit of diff over all three, then quadratic Ta at that x
    print("  quadratic: x* err %.2e m, T* rel err %.1e ; linear(bracket): x* err %.2e m, T* rel err %.1e" % (xq - xs_true, Tq / Tstar - 1, xl - xs_true, Tl / Tstar - 1))
    # naive exact formula per config with balance error +-1.5 mm
    for dh in (0.0015, -0.0015):
        gs = []
        for x, ta, tb in zip(X, Ta, Tb):
            h1 = periods(x)[2] + dh; h2 = L - h1
            gs.append(4 * math.pi ** 2 * (h1 ** 2 - h2 ** 2) / (ta ** 2 * h1 - tb ** 2 * h2))
        print("  exact formula with dh=%+.1f mm: g rel errors" % (dh * 1000), np.round(np.array(gs) / G - 1, 6))
