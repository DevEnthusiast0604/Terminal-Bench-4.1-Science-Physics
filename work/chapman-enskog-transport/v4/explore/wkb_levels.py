"""WKB survey of the quasi-bound (shape-resonance) levels of the Kihara a = sigma/2 potential for a quantum gas.

Reduced units sigma = eps = m = 1, so mu = 1/2 and the radial equation is u'' = [l(l+1)/r^2 + (V - E)/hb^2] u.
For each hbar* = hbar / (sigma sqrt(m eps)), list per l the levels between 0 and the barrier top, with WKB widths,
and an estimate of how much each narrow resonance adds to Omega(2,2) at several T*.

    python -B wkb_levels.py 0.05 0.08 0.12
"""
import sys

import numpy as np
from scipy.optimize import brentq, minimize_scalar
from scipy.integrate import quad

A = 0.5


def V(r):
    y = (1 - A) / (r - A)
    return 4 * (y ** 12 - y ** 6)


def veff(r, l, hb):
    return V(r) + hb * hb * l * (l + 1) / (r * r)


def survey(hb, temps=(0.3, 0.75, 2.0)):
    print("hbar* = %.4f (Lambda* = %.4f)" % (hb, 2 * np.pi * hb))
    total = {}
    allv = []
    l = 0
    while True:
        f = lambda r: -veff(r, l, hb)
        rs = np.linspace(0.9, 6, 20001)
        v = veff(rs, l, hb)
        i_min = np.argmin(v)
        if i_min == len(rs) - 1:
            break
        j = i_min + np.argmax(v[i_min:])
        if l > 0 and (j == len(rs) - 1 or v[j] <= v[i_min] + 1e-12):
            break
        top = v[j] if l > 0 else 0.0
        r_top = rs[j]
        if top <= 0 and l > 0:
            l += 1
            continue
        levels = []

        def action(E):
            r1 = brentq(lambda r: veff(r, l, hb) - E, 0.7, rs[i_min])
            r2 = brentq(lambda r: veff(r, l, hb) - E, rs[i_min], r_top) if l > 0 else \
                brentq(lambda r: veff(r, l, hb) - E, rs[i_min], 50)
            return quad(lambda r: np.sqrt(max(E - veff(r, l, hb), 0)), r1, r2, limit=200)[0] / hb, r1, r2

        Emax = top - 1e-9
        Emin = v[i_min] + 1e-9
        n_top = action(Emax)[0] / np.pi - 0.5
        n_lo = action(Emin)[0] / np.pi - 0.5
        for n in range(int(np.ceil(n_lo)), int(np.floor(n_top)) + 1):
            if n < 0:
                continue
            En = brentq(lambda E: action(E)[0] / np.pi - 0.5 - n, Emin, Emax)
            if En <= 0:
                continue
            # Gamow width
            _, r1, r2 = action(En)
            r3 = brentq(lambda r: veff(r, l, hb) - En, r_top, 200)
            theta = quad(lambda r: np.sqrt(max(veff(r, l, hb) - En, 0)), r2, r3, limit=200)[0] / hb
            # classical period of the well motion, mu = 1/2: v = sqrt(2 (E - Veff)/mu) = 2 sqrt(E - Veff)
            period = 2 * quad(lambda r: 1 / (2 * np.sqrt(max(En - veff(r, l, hb), 1e-300))), r1, r2, limit=200)[0]
            hw = 2 * np.pi * hb / period
            gam = hw / (2 * np.pi) * np.exp(-2 * theta)
            levels.append((n, En, gam))
        for n, En, gam in levels:
            # resonance adds about (pi Gamma / 2) * (4 pi / k^2) (2 l + 1) * c to the area under Q2;
            # Bose: only even l, doubled amplitude; use weight ~ 2 (2l+1) * 4 pi / k^2 * 1/2 (crude)
            k2 = En / hb ** 2
            area = np.pi * gam / 2 * 4 * np.pi / k2 * (l + 1) * (l + 2) / (2 * l + 3) * 2
            for T in temps:
                w = (En / T) ** 2 * np.exp(-En / T) / (2 * T)  # Omega(2,2) weight per unit E, normalised to Q-bar
                rel = area * w / 5.0
                if l % 2 == 0:
                    for cut in (1e-2, 1e-3, 1e-4, 1e-5):
                        if gam < cut * T:
                            total[(T, cut)] = total.get((T, cut), 0.0) + rel
            allv.append((l, n, En, gam))
        l += 1
        if l > 400:
            break
    print("  %d levels with 0 < E < barrier top, l = 0..%d; widths %s" % (
        len(allv), l - 1, np.histogram(np.log10([g for *_, g in allv] or [1]), bins=range(-30, 2, 4))[0]))
    for T in temps:
        print("  T*=%-5g crude Omega22 share of even-l levels narrower than 1e-2/1e-3/1e-4/1e-5 kT: %s" % (
            T, " ".join("%.1e" % total.get((T, c), 0.0) for c in (1e-2, 1e-3, 1e-4, 1e-5))))
    narrow = sorted(allv, key=lambda t: -t[3])
    print("  levels (l, n, E, Gamma), broadest first:", "; ".join("%d %d %.4f %.1e" % t for t in narrow[:60]))


for hb in map(float, sys.argv[1:]):
    survey(hb)
