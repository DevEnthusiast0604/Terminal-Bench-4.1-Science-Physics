"""Stand flexure: how much it shifts the small-amplitude period and how much it changes the period's growth
with amplitude, for the rig's geometry. 2-DOF Lagrangian: bar angle theta, plates' sideways shift u with
u = -c F (c compliance m/N, F the bar's sideways force on the plates). Pin of radius r rolling on the plates,
D = h + r from the pin axis to the centre of mass:
    [1   X ] [u'']   [ D sin(th) th'^2 - u / (c m) ]
    [X   J ] [th''] = [ -(g + r th'^2) D sin(th)    ],  X = D cos(th) - r,  J = k^2 + D^2 + r^2 - 2 D r cos(th)
No damping here. Usage: python -I -B flexure.py"""
import math

import numpy as np
from scipy.special import ellipk

G, K, M = 9.80, 0.3517, 4.862


def acc(state, h, r, c):
    th, om, u, v = state
    D = h + r
    X = D * math.cos(th) - r
    J = K * K + D * D + r * r - 2 * D * r * math.cos(th)
    b1 = D * math.sin(th) * om * om - (u / (c * M) if c else 0.0)
    b2 = -(G + r * om * om) * D * math.sin(th)
    if c == 0.0:
        return np.array([om, b2 / J, 0.0, 0.0])
    det = J - X * X
    udd = (b1 * J - X * b2) / det
    thdd = (b2 - X * b1) / det
    return np.array([om, thdd, v, udd])


def period(amp, h, r, c, dt=2.5e-4, cycles=4):
    """Mean period over `cycles` swings from rest at amp, u started at its quasi-static value."""
    # quasi-static start: u'' = 0 at t = 0 with th' = 0  ->  u = -c M X th''  and  J th'' + X u'' = b2
    D = h + r
    X = D * math.cos(amp) - r
    J = K * K + D * D + r * r - 2 * D * r * math.cos(amp)
    thdd0 = -(G) * D * math.sin(amp) / J
    s = np.array([amp, 0.0, -c * M * X * thdd0, 0.0])
    t, prev, crosses = 0.0, s[0], []
    while len(crosses) < 2 * cycles + 1:
        k1 = acc(s, h, r, c)
        k2 = acc(s + 0.5 * dt * k1, h, r, c)
        k3 = acc(s + 0.5 * dt * k2, h, r, c)
        k4 = acc(s + dt * k3, h, r, c)
        s = s + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0
        t += dt
        if prev * s[0] < 0:
            crosses.append(t - dt * s[0] / (s[0] - prev))
        prev = s[0]
    return (crosses[-1] - crosses[0]) / cycles


def linear_period(h, r, c):
    """Slow root of  c M k^2 x^2 - (k^2 + h^2 + g D c M) x + g D = 0,  x = omega^2."""
    D = h + r
    if c == 0.0:
        return 2 * math.pi * math.sqrt((K * K + h * h) / (G * D))
    A, B, C = c * M * K * K, K * K + h * h + G * D * c * M, G * D
    x = (B - math.sqrt(B * B - 4 * A * C)) / (2 * A)
    return 2 * math.pi / math.sqrt(x)


for c in (1.0e-5, 2.0e-5):
    print("compliance %.1e m/N" % c)
    for h, r in ((0.2001, 0.0015), (0.7999, 0.0)):
        T0f, T00 = linear_period(h, r, c), linear_period(h, r, 0.0)
        print("  h %.4f r %.4f: T0 shift by flexure %.3e" % (h, r, T0f / T00 - 1))
        for amp in (0.2, 0.5, 0.9):
            Tf, T0 = period(amp, h, r, c), period(amp, h, r, 0.0)
            # growth with amplitude, flexure vs none: the part a no-flexure amplitude law gets wrong
            print("    amp %.1f: T/T0 flex %.7f none %.7f  -> mismatch %.2e" % (
                amp, Tf / T0f, T0 / T00, (Tf / T0f) / (T0 / T00) - 1))
