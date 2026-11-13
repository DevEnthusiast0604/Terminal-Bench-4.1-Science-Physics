import math, numpy as np
def agm(a, b):
    for _ in range(40):
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return a
def F(A):  # T/T0 for amplitude A
    return 1.0 / agm(1.0, math.cos(A / 2))
for beta, alpha in ((26, 17), (30, 20), (22, 14)):
    b, al = math.radians(beta), math.radians(alpha)
    a = math.cos(b) / math.cos(al); s = math.tan(al) * math.sin(b)
    print("pan %d tilt %d: a=%.4f s=%.4f" % (beta, alpha, a, s))
    for A in (0.3, 0.5, 0.75, 0.85):
        up = math.atan2(a * math.sin(A), math.cos(A) - s * math.sin(A))
        dn = -math.atan2(a * math.sin(-A), math.cos(-A) - s * math.sin(-A))
        half = 0.5 * (up + dn)
        # camera ignored: use half-amplitude as the true amplitude in the exact law
        e_ign = F(A) / F(half) - 1
        # gain-only: fit a from small amplitude (a) and use atan(tan(half)/a)
        Ag = math.atan(math.tan(half) / a)
        e_gain = F(A) / F(Ag) - 1
        print("  A=%.2f image +%.4f -%.4f half %.4f  T0 bias ignore %.1e  gain-only(a known) %.1e" % (A, up, dn, half, e_ign, e_gain))
