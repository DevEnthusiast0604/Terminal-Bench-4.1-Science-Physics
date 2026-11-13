"""Classical scattering and collision integrals for a spherical-core (Kihara) potential (author's prototype).

Reduced units: lengths in sigma, energies in epsilon. Core diameter ratio A = a / sigma:
    V(r) = 4 [ (d/rho)^12 - (d/rho)^6 ],  rho = r - A,  d = 1 - A   (r > A; infinite below)
Deflection chi(b, E) = pi - 2 b int_{r0}^inf dr / (r^2 sqrt(F)),  F = 1 - b^2/r^2 - V(r)/E,
r0 the outermost root of F. Orbiting: h(r) = r^3 V'(r) / 2 is the E b^2 at which V_eff = V + E b^2/r^2 is
stationary; beyond its maximum h_max (at r_h) the stationary point is the barrier r_bar(b). The integral is split at
r_bar whenever the particle passes over the barrier (F(r_bar) > 0), so the slow passage is an endpoint of a
double-exponential rule.
Q^(l)(E) = 2 pi int (1 - cos^l chi) b db, with meshes graded logarithmically toward the orbiting b.
"""
import numpy as np
from numpy.polynomial.legendre import leggauss


class Kihara:
    def __init__(self, A):
        self.A, self.d = A, 1.0 - A
        self.rm = A + self.d * 2.0 ** (1 / 6)
        rs = np.linspace(self.rm, 60.0, 400001)
        h = self.h(rs)
        i = int(np.argmax(h))
        self.r_h = self._golden(lambda r: -self.h(r), rs[max(i - 1, 0)], rs[i + 1])
        self.h_max = float(self.h(self.r_h))
        eo = self.V(rs) + 0.5 * rs * self.dV(rs)
        i = int(np.argmax(eo))
        self.r_c = self._golden(lambda r: -(self.V(r) + 0.5 * r * self.dV(r)), rs[max(i - 1, 0)], rs[i + 1])
        self.E_c = float(self.V(self.r_c) + 0.5 * self.r_c * self.dV(self.r_c))

    @staticmethod
    def _golden(f, a, b):
        g = (np.sqrt(5) - 1) / 2
        c, d = b - g * (b - a), a + g * (b - a)
        for _ in range(200):
            if f(c) < f(d):
                b = d
            else:
                a = c
            c, d = b - g * (b - a), a + g * (b - a)
        return 0.5 * (a + b)

    def V(self, r):
        x = self.d / (r - self.A)
        x6 = x ** 6
        return 4.0 * (x6 * x6 - x6)

    def dV(self, r):
        rho = r - self.A
        x = self.d / rho
        x6 = x ** 6
        return 4.0 * (-12.0 * x6 * x6 + 6.0 * x6) / rho

    def h(self, r):
        return 0.5 * r ** 3 * self.dV(r)

    def dV_diff(self, r0, delta):
        """V(r0 + delta) - V(r0), accurate when delta is small."""
        rho0 = r0 - self.A
        lg = np.log1p(delta / rho0)
        x6 = (self.d / rho0) ** 6
        return 4.0 * (x6 * x6 * np.expm1(-12.0 * lg) - x6 * np.expm1(-6.0 * lg))


def bisect(f, lo, hi, it=80):
    """Vectorised bisection; f(lo) and f(hi) have opposite signs elementwise."""
    flo = f(lo)
    for _ in range(it):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        same = np.sign(fm) == np.sign(flo)
        lo = np.where(same, mid, lo)
        flo = np.where(same, fm, flo)
        hi = np.where(same, hi, mid)
    return 0.5 * (lo + hi)


def de_rule(h=1.0 / 64, tmax=3.4):
    """tanh-sinh nodes on (0, 1): returns (x, 1 - x, weight)."""
    t = np.arange(-tmax, tmax + h / 2, h)
    s = 0.5 * np.pi * np.sinh(t)
    x = 1.0 / (1.0 + np.exp(-2.0 * s))
    xc = 1.0 / (1.0 + np.exp(2.0 * s))
    wgt = h * 0.5 * np.pi * np.cosh(t) / (2.0 * np.cosh(s) ** 2)
    return x, xc, wgt


class Scatter:
    def __init__(self, pot, de_h=1.0 / 64):
        self.p = pot
        self.x, self.xc, self.w = de_rule(de_h)

    def F(self, r, b, E):
        return 1.0 - b * b / (r * r) - self.p.V(r) / E

    def F_near(self, r0, delta, b, E):
        """F(r0 + delta) with F(r0) = 0 exactly, from differences (delta given, never formed as r - r0)."""
        r = r0 + delta
        return b * b * delta * (r + r0) / (r0 * r0 * r * r) - self.p.dV_diff(r0, delta) / E

    def chi(self, b, E):
        b = np.atleast_1d(np.asarray(b, float))
        p = self.p
        Eb2 = E * b * b
        has_bar = Eb2 < p.h_max
        # r_bar: the barrier (V_eff maximum) when there is one, else the inflection r_h of the flattest crossing
        r_bar = np.full_like(b, p.r_h)
        if has_bar.any():
            hb = Eb2[has_bar]
            lo = np.full_like(hb, p.r_h)
            hi = np.full_like(hb, 1e4)
            r_bar[has_bar] = bisect(lambda r: p.h(r) - hb, lo, hi)
        Fbar = self.F(r_bar, b, E)
        outer = Fbar <= 0                      # turning point outside the barrier (or beyond r_h)
        split = (Fbar > 0) & (Fbar < 0.5)      # slow passage over the barrier or the inflection: split there
        r0 = np.empty_like(b)
        if outer.any():
            bo = b[outer]
            lo = r_bar[outer]
            hi = np.maximum(bo, lo) * 2.0 + 10.0
            r0[outer] = bisect(lambda r: self.F(r, bo, E), lo, hi)
        inner = ~outer
        if inner.any():
            bi = b[inner]
            lo = np.full_like(bi, p.A + 1e-9 * p.d)
            r0[inner] = bisect(lambda r: self.F(r, bi, E), lo, r_bar[inner])
        x, xc, w = self.x[None, :], self.xc[None, :], self.w[None, :]
        out = np.empty_like(b)
        ns = ~split
        if ns.any():
            # one piece, u = r0 / r in (0, 1) (u = x, 1 - u = xc), as a difference from free motion so that weak
            # deflections keep their digits: chi = 2 int [1/sqrt(1-u^2) - beta/sqrt(F)] du, beta = b/r0, and
            # F = beta^2 (1-u^2)(1+g) with g = (F(r0) + v(1) - v(u)) / (beta^2 (1-u^2)), v = V/E.
            # F(r0) is dropped near r0 (it is only F'(r0) ulp(r0), large at low energy, and F(r0) = 0 there is the
            # consistent choice) and kept elsewhere, where the true b matters more than the exact root.
            R0 = r0[ns][:, None]
            bn = b[ns][:, None]
            beta2 = (bn / R0) ** 2
            one_m_u2 = xc * (1.0 + x)
            dv = -self.p.dV_diff(R0, R0 * xc / x) / E
            eps0 = self.F(R0, bn, E)
            g = np.where(x >= 0.5, dv, eps0 + dv) / (beta2 * one_m_u2)
            sq = np.sqrt(1.0 + g)
            term = g / (sq * (1.0 + sq)) / np.sqrt(one_m_u2)
            out[ns] = 2.0 * (w * term).sum(1)
        if split.any():
            R0, RB = r0[split][:, None], r_bar[split][:, None]
            bs = b[split][:, None]
            dl = (RB - R0) * x
            near0 = x < 0.5           # from the turning point's side F by differences; near r_bar F itself,
            r = np.where(near0, R0 + dl, RB - (RB - R0) * xc)   # since F(r0) = 0 is only good to F'(r0) dr0
            Fv = np.where(near0, self.F_near(R0, dl, bs, E), self.F(r, bs, E))
            part1 = ((RB - R0) * w / (r * r * np.sqrt(Fv))).sum(1)
            u = x
            r = RB / u
            Fv = self.F(r, bs, E)
            part2 = (w / np.sqrt(Fv)).sum(1) / RB[:, 0]
            out[split] = np.pi - 2.0 * b[split] * (part1 + part2)
        if not np.all(np.isfinite(out)):
            raise FloatingPointError("chi not finite at E=%r, b=%r" % (E, b[~np.isfinite(out)][:5]))
        return out

    def b_orb(self, E):
        """(b, r) of orbiting at energy E < E_c: outer solution of V + r V'/2 = E."""
        p = self.p
        f = lambda r: p.V(r) + 0.5 * r * p.dV(r) - E
        r = float(bisect(f, np.array([p.r_c]), np.array([1e4]), 200)[0])
        return np.sqrt(p.h(r) / E), r


GL = {n: leggauss(n) for n in (8, 16, 32)}


def b_star(sc, E):
    """The impact parameter of the slowest passage: orbiting below E_c, the flattest barrier crossing above it."""
    if E < sc.p.E_c:
        return sc.b_orb(E)[0]
    return float(np.sqrt(sc.p.h_max / E))


def gl16(f, lo, hi):
    xg, wg = GL[16]
    pts = (0.5 * (lo + hi)[:, None] + 0.5 * (hi - lo)[:, None] * xg[None, :]).ravel()
    wts = (0.5 * (hi - lo)[:, None] * wg[None, :]).ravel()
    return (f(pts) * wts[:, None]).reshape(len(lo), 16, -1).sum(1)


def adaptive_pieces(pieces, rel=1e-11, n0=24, min_width=1e-5, max_rounds=30, floor=1e-11, max_panels=20000):
    """Sum over pieces (f, a, b) of the integral of the vector-valued f. Panels are halved until the 16-point rule on
    the two halves and on the whole agree, per component, within rel * |total| * width / total width (absolute, so
    noise near a singular point stops the halving) or within floor * |panel value| (the noise floor of the deflection
    angles: such panels add at most floor * total), or the panel is narrower than min_width."""
    lo = np.concatenate([np.linspace(a, b, n0 + 1)[:-1] for f, a, b in pieces])
    hi = np.concatenate([np.linspace(a, b, n0 + 1)[1:] for f, a, b in pieces])
    owner = np.repeat(np.arange(len(pieces)), n0)
    width = sum(b - a for f, a, b in pieces)
    total, est = 0.0, None
    for rnd in range(max_rounds):
        mid = 0.5 * (lo + hi)
        whole, halves = [], []
        for k, (f, a, b) in enumerate(pieces):
            sel = owner == k
            if sel.any():
                whole.append((sel, gl16(f, lo[sel], hi[sel])))
                halves.append(gl16(f, lo[sel], mid[sel]) + gl16(f, mid[sel], hi[sel]))
        W = np.zeros((len(lo), whole[0][1].shape[1]))
        Hh = np.zeros_like(W)
        for (sel, wv), hv in zip(whole, halves):
            W[sel], Hh[sel] = wv, hv
        if est is None:
            est = np.maximum(np.abs(Hh.sum(0)), 1e-300)
        tol = np.maximum(rel * est[None, :] * ((hi - lo) / width)[:, None], floor * np.abs(Hh))
        ok = (np.abs(Hh - W) <= tol).all(1) | ((hi - lo) < min_width)
        total = total + Hh[ok].sum(0)
        if ok.all():
            return total
        bad = ~ok
        if 2 * bad.sum() > max_panels:
            raise RuntimeError("adaptive_pieces: %d panels would be needed in round %d" % (2 * bad.sum(), rnd + 1))
        lo, hi, owner = (np.concatenate([lo[bad], mid[bad]]), np.concatenate([mid[bad], hi[bad]]),
                         np.concatenate([owner[bad], owner[bad]]))
    raise RuntimeError("adaptive_pieces: %d panels left after %d rounds" % (len(lo), max_rounds))


def Q_all(sc, E, L, rel=1e-11, smax=30.0):
    """Q^(l)(E) / (pi sigma^2) for l = 1..L: b graded logarithmically toward b* on both sides
    (b = b* (1 -+ exp(-s)), s in (0, smax)), then b = 2 b* / v for v in (1e-6, 1); adaptive panels."""
    ls = np.arange(1, L + 1)

    def integrand_b(bv):
        ch = sc.chi(bv, E)
        c = np.cos(ch)[:, None]
        small = c > 0.5                                 # 1 - cos^l chi = -expm1(l log1p(-2 sin^2(chi/2))) there
        s2 = np.where(small, -2.0 * np.sin(0.5 * ch)[:, None] ** 2, 0.0)
        val = np.where(small, -np.expm1(ls[None, :] * np.log1p(s2)), 1.0 - c ** ls[None, :])
        return val * bv[:, None]

    bs = b_star(sc, E)
    inner = lambda sv: integrand_b(bs * (-np.expm1(-sv))) * (bs * np.exp(-sv))[:, None]
    outer = lambda sv: integrand_b(bs * (1.0 + np.exp(-sv))) * (bs * np.exp(-sv))[:, None]
    far = lambda vv: integrand_b(2.0 * bs / vv) * (2.0 * bs / vv ** 2)[:, None]
    return 2.0 * adaptive_pieces([(inner, 0.0, smax), (outer, 0.0, smax), (far, 1e-6, 1.0)], rel)
