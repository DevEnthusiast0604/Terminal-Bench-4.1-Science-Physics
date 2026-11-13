import math, numpy as np
G = 9.79184
L = 1.00003
# rod from s=-0.15 to s=1.15 (1.30 m), fixed bob near A, slider between the edges
ROD_M, ROD_A, ROD_B = 2.40, -0.15, 1.15
BOB_M, BOB_S, BOB_I = 2.60, 0.06, 0.0020
SL_M, SL_I = 1.10, 0.0012

def body(x):
    parts = [(ROD_M, 0.5 * (ROD_A + ROD_B), ROD_M * (ROD_B - ROD_A) ** 2 / 12),
             (BOB_M, BOB_S, BOB_I), (SL_M, x, SL_I)]
    M = sum(p[0] for p in parts)
    s = sum(p[0] * p[1] for p in parts) / M
    I = sum(p[2] + p[0] * (p[1] - s) ** 2 for p in parts)
    return M, s, I / M

def periods(x):
    M, s, k2 = body(x)
    ha, hb = s, L - s
    ta = 2 * math.pi * math.sqrt((k2 + ha * ha) / (G * ha))
    tb = 2 * math.pi * math.sqrt((k2 + hb * hb) / (G * hb))
    return ta, tb, ha, hb, k2

xs = np.linspace(0.30, 0.98, 69)
prev = None
for x in xs:
    ta, tb, ha, hb, k2 = periods(x)
    d = ta - tb
    if prev is not None and prev * d < 0:
        print("crossing between", round(x - 0.01, 3), round(x, 3), "ha", round(ha, 4), "hb", round(hb, 4), "k2", round(k2, 4), "ha*hb", round(ha * hb, 4))
    prev = d
for x in (0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85):
    ta, tb, ha, hb, k2 = periods(x)
    print("x %.2f  Ta %.5f  Tb %.5f  diff %+.2e  ha %.4f hb %.4f k2 %.4f hahb %.4f" % (x, ta, tb, (ta - tb) / ta, ha, hb, k2, ha * hb))
print("2pi sqrt(L/g) =", 2 * math.pi * math.sqrt(L / G))
