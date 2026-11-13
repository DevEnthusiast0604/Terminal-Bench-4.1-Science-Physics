"""v10 design: size of each pin / centre-of-mass effect on g, k and the per-run periods (noise-free)."""
import math
import numpy as np

G, K, L = 9.79184, 0.3517, 1.00003
H_BAL, M_BAR, M_W, DX = 0.20346, 4.862, 0.815, 0.0200
H_A = H_BAL - M_W * DX / M_BAR
H_B = L - H_A
C1, C2 = 1.0 / 45.0, 0.02
GL = np.polynomial.legendre.leggauss(64)


def law(A, beta):
    """T(A)/T0 for a pivot rolling on a flat: (2/pi) int sqrt(1+2 beta k^2 s^2)/sqrt(1-k^2 s^2) dphi."""
    k2 = math.sin(A / 2) ** 2
    x, w = GL
    phi = (x + 1) * math.pi / 4
    s2 = np.sin(phi) ** 2
    return float(np.sum(w * np.sqrt(1 + 2 * beta * k2 * s2) / np.sqrt(1 - k2 * s2)) * (math.pi / 4) * 2 / math.pi)


def t0(h, r):
    return 2 * math.pi * math.sqrt((K ** 2 + h ** 2) / (G * (h + r)))


def kater(ta, tb, ha, hb, ra):
    g = 4 * math.pi ** 2 * (ha ** 2 - hb ** 2) / (ta ** 2 * (ha + ra) - tb ** 2 * hb)
    k = math.sqrt(g * ta ** 2 * (ha + ra) / (4 * math.pi ** 2) - ha ** 2)
    return g, k


def run_bias(amp, r, rate=240.0, sub=8, dur=90.0):
    """Mean over cycles of (exact-law T0, elliptic-law T0) / true T0 - 1 for a noise-free rolling run."""
    h, c = H_A, H_A + r
    dt = 1 / (rate * sub)

    def acc(th, om):
        j = K ** 2 + c ** 2 + r ** 2 - 2 * c * r * math.cos(th)
        return -(G * c * math.sin(th) + c * r * math.sin(th) * om * om) / j - C1 * om - C2 * abs(om) * om

    th, om, t = amp, 0.0, 0.0
    ts, xs = [0.0], [th]
    n = int(dur / dt)
    for _ in range(n):
        k1t, k1o = om, acc(th, om)
        k2t, k2o = om + 0.5 * dt * k1o, acc(th + 0.5 * dt * k1t, om + 0.5 * dt * k1o)
        k3t, k3o = om + 0.5 * dt * k2o, acc(th + 0.5 * dt * k2t, om + 0.5 * dt * k2o)
        k4t, k4o = om + dt * k3o, acc(th + dt * k3t, om + dt * k3o)
        th += dt * (k1t + 2 * k2t + 2 * k3t + k4t) / 6
        om += dt * (k1o + 2 * k2o + 2 * k3o + k4o) / 6
        t += dt
        ts.append(t); xs.append(th)
    ts, xs = np.array(ts), np.array(xs)
    up = np.flatnonzero((xs[:-1] < 0) & (xs[1:] >= 0))
    tz = ts[up] - xs[up] * dt / (xs[up + 1] - xs[up])
    beta = 2 * c * r / (K ** 2 + h ** 2)
    true = t0(h, r)
    ex, el = [], []
    for i in range(len(tz) - 1):
        seg = (ts >= tz[i]) & (ts < tz[i + 1])
        A = 0.5 * (xs[seg].max() - xs[seg].min())
        T = tz[i + 1] - tz[i]
        ex.append(T / law(A, beta) / true - 1)
        el.append(T / law(A, 0.0) / true - 1)
    return float(np.mean(ex)), float(np.mean(el))


print("session h_a = %.7f m (balance %.5f, shift %.4f mm)" % (H_A, H_BAL, 1e3 * M_W * DX / M_BAR))
for r in (1.0e-3, 1.5e-3, 2.0e-3, 2.5e-3):
    ta, tb = t0(H_A, r), t0(H_B, 0.0)
    g0, k0 = kater(ta, tb, H_A, H_B, r)
    out = {"pin ignored": kater(ta, tb, H_A, H_B, 0.0),
           "pin as axle": kater(ta, tb, H_A + r, H_B, 0.0),
           "stale CM": kater(ta, tb, H_BAL, L - H_BAL, r),
           "CM moved wrong way": kater(ta, tb, 2 * H_A - H_BAL, L - (2 * H_A - H_BAL), r),
           "CM shift over M - m_w": kater(ta, tb, H_BAL - M_W * DX / (M_BAR - M_W), L - H_BAL + M_W * DX / (M_BAR - M_W), r),
           "pin ignored + stale CM": kater(ta, tb, H_BAL, L - H_BAL, 0.0)}
    print("r = %.1f mm: T_a %.9f T_b %.9f  beta %.2e  (check g %.1e k %.1e)" % (
        1e3 * r, ta, tb, 2 * (H_A + r) * r / (K ** 2 + H_A ** 2), g0 / G - 1, k0 / K - 1))
    for name, (g, k) in out.items():
        print("    %-24s g %+.2e  k %+.2e" % (name, g / G - 1, k / K - 1))
    for amp in (0.95, 0.7812, 0.62, 0.5537, 0.45, 0.3194):
        ex, el = run_bias(amp, r)
        print("    run amp %.4f: exact law %+.1e, knife-edge law %+.1e" % (amp, ex, el))
