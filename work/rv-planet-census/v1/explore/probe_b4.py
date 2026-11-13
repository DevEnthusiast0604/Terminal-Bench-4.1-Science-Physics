"""Probe 4 (after pass@3, 2026-11-10): is the 8% radius band fair for planet b?

pass@3 a1 fitted b's transits with a quadratic baseline per transit (+-0.22 d windows), limb darkening from NOTES.md,
a/R* from the stellar density and the stated dilution, and got 1.77 R_earth (+9.3%); a2 and a3 got +6.8% and +6.2%;
the reference (spline detrending, then the fit) has 1.606 (-0.9%). This probe fits the shipped light curve both ways
with one fast model (small-planet approximation, the same for both), then repeats both fits on synthetic light curves
with the generator's photometric noise (white 680 ppm, AR(1) red 90 ppm with 0.05 d) and b's true transit, to see
how often a correct method lands outside 8%. Nothing here is the oracle or the verifier."""
import importlib.util
import math
import sys

import numpy as np
from scipy.optimize import least_squares

TASK = "tasks/active/rv-planet-census"
spec = importlib.util.spec_from_file_location("solve", TASK + "/solution/solve.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)

lc = S.table(TASK + "/environment/data/lightcurve.txt")
T, F = lc[:, 0], lc[:, 1]
star = S.notes(TASK + "/environment/data/NOTES.md")
U1, U2 = star["u1"], star["u2"]
FD = 10 ** (-0.4 * 1.20)
R_E = star["radius"] * S.R_SUN / S.R_EARTH
NORM = 1 - U1 / 3 - U2 / 6
R_TRUE, B_TRUE, P_TRUE, TC_TRUE = 1.62, 0.35, 2.876314, 2460263.1137
K_TRUE = R_TRUE / R_E
AR = S.a_over_r(P_TRUE, star)
N_MC = int(sys.argv[1]) if len(sys.argv) > 1 else 60


def deficit(t, P, tc, k, b):
    ph = 2 * math.pi * (t - tc) / P
    x, y = AR * np.sin(ph), b * np.cos(ph)
    z = np.sqrt(x * x + y * y)
    out = np.zeros(len(t))
    m = (np.cos(ph) > 0) & (z < 1 + k)
    zz = z[m]
    area = np.full(len(zz), math.pi * k * k)
    edge = zz > 1 - k
    if edge.any():
        ze = zz[edge]
        k0 = np.arccos(np.clip((k * k + ze * ze - 1) / (2 * k * ze), -1, 1))
        k1 = np.arccos(np.clip((1 - k * k + ze * ze) / (2 * ze), -1, 1))
        area[edge] = k * k * k0 + k1 - 0.5 * np.sqrt(np.clip(4 * ze * ze - (1 + ze * ze - k * k) ** 2, 0, None))
    reff = np.where(edge, np.clip((zz - k + 1) / 2, 0, 1), np.clip(zz, 0, 1))
    mu = np.sqrt(np.clip(1 - reff ** 2, 0, 1))
    inten = (1 - U1 * (1 - mu) - U2 * (1 - mu) ** 2) / NORM
    out[m] = area / math.pi * inten
    return out


def phase_dist(t, P, tc):
    return np.abs(((t - tc) / P + 0.5) % 1.0 - 0.5) * P


def fit_spline(t, f, P0, tc0, excl):
    """Reference style: spline detrending with the transits masked, then the transit fit on the residual."""
    pre = (phase_dist(t, P0, tc0) < 0.75 * 0.0692 + 0.05) | excl
    r = S.detrend(t, f, pre)
    win = (phase_dist(t, P0, tc0) < 0.3) & ~excl
    tt, yy = t[win], (1 + FD) * r[win]

    def res(v):
        P, tc, k, b = v
        return yy + deficit(tt, P, tc, k, b)
    v = least_squares(res, [P0, tc0, K_TRUE * 0.98, 0.3], bounds=([P0 - 2e-3, tc0 - 0.02, 0.01, 0], [P0 + 2e-3, tc0 + 0.02, 0.04, 0.95]),
                      x_scale=[1e-4, 1e-3, 1e-3, 0.1]).x
    return v[2] * R_E, v[3]


def fit_local(t, f, P0, tc0, excl, half=0.22, order=2):
    """a1 style: a polynomial baseline per transit window, solved linearly, times the diluted transit."""
    win = (phase_dist(t, P0, tc0) < half) & ~excl
    tt, ff = t[win], f[win]
    ev = np.rint((tt - tc0) / P0).astype(int)
    groups = [np.where(ev == e)[0] for e in np.unique(ev)]

    def res(v):
        P, tc, k, b = v
        tr = 1 - deficit(tt, P, tc, k, b) / (1 + FD)
        out = np.empty(len(tt))
        for g in groups:
            d = tt[g] - (tc0 + ev[g[0]] * P0)
            X = np.column_stack([d ** j for j in range(order + 1)]) * tr[g, None]
            beta = np.linalg.lstsq(X, ff[g], rcond=None)[0]
            out[g] = ff[g] - X @ beta
        return out
    v = least_squares(res, [P0, tc0, K_TRUE * 0.98, 0.3], bounds=([P0 - 2e-3, tc0 - 0.02, 0.01, 0], [P0 + 2e-3, tc0 + 0.02, 0.04, 0.95]),
                      x_scale=[1e-4, 1e-3, 1e-3, 0.1]).x
    return v[2] * R_E, v[3]


# the shipped light curve: mask the binary's eclipses and e's single transit
excl = (phase_dist(T, 6.04485, 2460266.0191) < 0.0692 + 0.05) | (phase_dist(T, 6.04485, 2460266.0191 + 3.022425) < 0.0692 + 0.05)
excl |= np.abs(T - 2460270.8342) < 0.75 * 5.0 / 24 + 0.05
P0, tc0 = 2.87624, 2460288.9999
print("shipped light curve, planet b (true R 1.62, b 0.35):")
for name, fn in (("spline then fit", lambda: fit_spline(T, F, P0, tc0, excl)),
                 ("quadratic per transit +-0.22 d", lambda: fit_local(T, F, P0, tc0, excl)),
                 ("quadratic per transit +-0.30 d", lambda: fit_local(T, F, P0, tc0, excl, half=0.30)),
                 ("linear per transit +-0.22 d", lambda: fit_local(T, F, P0, tc0, excl, order=1))):
    R, b = fn()
    print("  %-32s R %.3f (%+.1f%%)  b %.2f" % (name, R, 100 * (R / R_TRUE - 1), b), flush=True)

# synthetic light curves on the same time stamps
gen = importlib.util.spec_from_file_location("gen", TASK + "/tests/generate.py")
rng = np.random.default_rng(20261110)
cad = 2.0 / 1440
phi = math.exp(-cad / 0.05)
sector = (T - 2460262.30) > 27.5
clean = 1 - deficit(T, P_TRUE, TC_TRUE, K_TRUE, B_TRUE) / (1 + FD)
rows = {"spline": [], "quad22": [], "quad30": [], "lin22": []}
for i in range(N_MC):
    kick = rng.normal(0, 90e-6 * math.sqrt(1 - phi ** 2), len(T))
    red = np.empty(len(T))
    red[0] = rng.normal(0, 90e-6)
    for j in range(1, len(T)):
        red[j] = (phi * red[j - 1] if T[j] - T[j - 1] < 2 * cad else rng.normal(0, 90e-6)) + kick[j]
    spots = 0.004 * np.sin(2 * math.pi * T / 34.28 + rng.uniform(0, 6.3)) + 0.0015 * np.sin(2 * math.pi * T / 17.1 + rng.uniform(0, 6.3))
    f = clean * (1 - spots / (1 + FD)) + red + rng.normal(0, 680e-6, len(T))
    for s in (False, True):
        f[sector == s] /= np.median(f[sector == s])
    tcr = TC_TRUE + 9 * P_TRUE
    none = np.zeros(len(T), bool)
    rows["spline"].append(fit_spline(T, f, P_TRUE, tcr, none)[0] / R_TRUE - 1)
    rows["quad22"].append(fit_local(T, f, P_TRUE, tcr, none)[0] / R_TRUE - 1)
    rows["quad30"].append(fit_local(T, f, P_TRUE, tcr, none, half=0.30)[0] / R_TRUE - 1)
    rows["lin22"].append(fit_local(T, f, P_TRUE, tcr, none, order=1)[0] / R_TRUE - 1)
    if (i + 1) % 10 == 0:
        print("  %d realizations done" % (i + 1), flush=True)

print("synthetic light curves (%d realizations; b's true transit, white 680 ppm, red 90 ppm / 0.05 d, slow spots):" % N_MC)
for name, v in rows.items():
    v = np.array(v)
    print("  %-7s mean %+.2f%%  sd %.2f%%  outside 8%%: %d of %d  outside 5%%: %d  max |dev| %.1f%%"
          % (name, 100 * v.mean(), 100 * v.std(ddof=1), int(np.sum(np.abs(v) > 0.08)), len(v),
             int(np.sum(np.abs(v) > 0.05)), 100 * np.abs(v).max()))
