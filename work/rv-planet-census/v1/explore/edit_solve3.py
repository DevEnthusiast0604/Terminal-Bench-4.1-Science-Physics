"""solve.py: fit eccentricity as (e cos w, e sin w), whose gradient is not zero at e = 0 (sqrt(e) cos w and
sqrt(e) sin w left circular starts stuck at e = 0); the radius without the second star's light at the fitted impact
parameter; the no-transit box search with every known dip masked."""
from pathlib import Path

p = Path("tasks/active/rv-planet-census/solution/solve.py")
s = p.read_bytes().decode("utf-8")


def sub(old, new):
    global s
    assert s.count(old) == 1, old[:90]
    s = s.replace(old, new)


# --- the orbit fit in (ln P, phase, e cos w, e sin w)
sub('''        def unpack(x):
            pl = [list(p) for p in base]
            pen = 0.0
            for j, k in enumerate(free):
                lp, ph, sc, ss = x[4 * j:4 * j + 4]
                P = math.exp(lp)
                e = sc * sc + ss * ss
                if e > 0.85:
                    pen += 1e6 * (e - 0.85) ** 2
                    s = math.sqrt(0.85 / e)
                    sc, ss = sc * s, ss * s
                pl[k] = [P, self.tmid + ph * P / (2 * math.pi), sc, ss]
            return pl, pen
''', '''        def unpack(x):
            pl = [list(p) for p in base]
            pen = 0.0
            for j, k in enumerate(free):
                pl[k], extra = from_fit(x[4 * j:4 * j + 4], self.tmid)
                pen += extra
            return pl, pen
''')

sub('''        x0, bounds = [], []
        for k in free:
            P, tc, sc, ss = base[k]
            dl = P / self.span                          # a frequency change of 1/span
            x0 += [math.log(P), 2 * math.pi * (tc - self.tmid) / P, sc, ss]
            bounds += [(math.log(P) - dl, math.log(P) + dl), (None, None), (-0.95, 0.95), (-0.95, 0.95)]
''', '''        x0, bounds = [], []
        for k in free:
            P = base[k][0]
            dl = P / self.span                          # a frequency change of 1/span
            x0 += list(to_fit(base[k], self.tmid))
            bounds += [(math.log(P) - dl, math.log(P) + dl), (None, None), (-0.9, 0.9), (-0.9, 0.9)]
''')

sub('''    def ephemeris(self, planets, k, fac):
        """(ln P, phase, sqrt(e) cos w, sqrt(e) sin w) of planet k, phase = 2 pi (tc - tmid) / P, and their covariance
        from the curvature of the chi-square, the other planets and the noise held fixed. A weak prior (0.5) on the
        two eccentricity terms keeps the curvature finite for a circular orbit."""
        P, tc, sc, ss = planets[k]
        x0 = np.array([math.log(P), 2 * math.pi * (tc - self.tmid) / P, sc, ss])

        def cost(x):
            pl = [list(q) for q in planets]
            Pk = math.exp(x[0])
            pl[k] = [Pk, self.tmid + x[1] * Pk / (2 * math.pi), x[2], x[3]]
            return self.solve(pl, fac)[0]
''', '''    def ephemeris(self, planets, k, fac):
        """(ln P, phase, e cos w, e sin w) of planet k, phase = 2 pi (tc - tmid) / P, and their covariance from the
        curvature of the chi-square, the other planets and the noise held fixed. A weak prior (0.5) on the two
        eccentricity terms keeps the curvature finite."""
        P = planets[k][0]
        x0 = to_fit(planets[k], self.tmid)

        def cost(x):
            pl = [list(q) for q in planets]
            pl[k] = from_fit(x, self.tmid)[0]
            return self.solve(pl, fac)[0]
''')

sub('''def aliases(P):''', '''def to_fit(planet, tmid):
    """[P, tc, sqrt(e) cos w, sqrt(e) sin w] -> (ln P, 2 pi (tc - tmid) / P, e cos w, e sin w)."""
    P, tc, sc, ss = planet
    e, w = sc * sc + ss * ss, math.atan2(ss, sc)
    return np.array([math.log(P), 2 * math.pi * (tc - tmid) / P, e * math.cos(w), e * math.sin(w)])


def from_fit(x, tmid):
    """The inverse of to_fit, with e held below 0.85 and a penalty for the excess."""
    lp, ph, h, q = x
    P = math.exp(lp)
    e = math.hypot(h, q)
    pen = 0.0
    if e > 0.85:
        pen = 1e6 * (e - 0.85) ** 2
        h, q, e = h * 0.85 / e, q * 0.85 / e, 0.85
    w = math.atan2(q, h)
    return [P, tmid + ph * P / (2 * math.pi), math.sqrt(e) * math.cos(w), math.sqrt(e) * math.sin(w)], pen


def aliases(P):''')

# --- transit fit with an optional fixed impact parameter
sub('''def fit_transit(t, r, sigma, excl, P, tc0, e, w, star, fdil, free_P):
    """Radius ratio, impact parameter, mid-time and period from the light corrected for the second star: the target's
    own relative flux change is (1 + F) times the observed one, F being the second star's light over the target's."""
    und = (1.0 + fdil) * r
    aR = a_over_r(P, star)
    win = (np.abs(((t - tc0) / P + 0.5) % 1.0 - 0.5) * P < 0.6) & ~excl
    tt, yy = t[win], und[win]
    sig = (1.0 + fdil) * sigma

    def resid(x):
        Pf = P + (x[3] if free_P else 0.0)
        m = transit_model(tt, Pf, tc0 + x[2], e, w, aR, x[0], x[1], star["u1"], star["u2"])
        if np.any(np.isnan(m)):
            return np.full(len(tt), 1e3)
        return (yy + m) / sig

    sm = np.convolve(yy, np.ones(15) / 15, "same")
    k0 = math.sqrt(max(1e-6, -float(np.min(sm))))
    lo, hi, scale = [0.002, 0.0, -0.05], [0.3, 1.2, 0.05], [0.005, 0.1, 0.002]
    if free_P:
        lo, hi, scale = lo + [-0.003], hi + [0.003], scale + [1e-4]
    best = None
    for b0 in (0.1, 0.4, 0.7):
        x0 = [k0, b0, 0.0] + ([0.0] if free_P else [])
        res = least_squares(resid, x0, bounds=(lo, hi), x_scale=scale)
        if best is None or res.cost < best.cost:
            best = res
    x = best.x
    return float(x[0]), float(x[1]), float(tc0 + x[2]), float(P + (x[3] if free_P else 0.0))
''', '''def fit_transit(t, r, sigma, excl, P, tc0, e, w, star, fdil, free_P, fix_b=None):
    """Radius ratio, impact parameter, mid-time and period from the light corrected for the second star: the target's
    own relative flux change is (1 + F) times the observed one, F being the second star's light over the target's.
    With fix_b the impact parameter is held at that value."""
    und = (1.0 + fdil) * r
    aR = a_over_r(P, star)
    win = (np.abs(((t - tc0) / P + 0.5) % 1.0 - 0.5) * P < 0.6) & ~excl
    tt, yy = t[win], und[win]
    sig = (1.0 + fdil) * sigma

    def unpack(x):
        x = list(x)
        k = x.pop(0)
        b = x.pop(0) if fix_b is None else fix_b
        dt = x.pop(0)
        return k, b, dt, (x.pop(0) if free_P else 0.0)

    def resid(x):
        k, b, dt, dP = unpack(x)
        m = transit_model(tt, P + dP, tc0 + dt, e, w, aR, k, b, star["u1"], star["u2"])
        if np.any(np.isnan(m)):
            return np.full(len(tt), 1e3)
        return (yy + m) / sig

    sm = np.convolve(yy, np.ones(15) / 15, "same")
    k0 = math.sqrt(max(1e-6, -float(np.min(sm))))
    lo, hi, scale = [0.002, -0.05], [0.3, 0.05], [0.005, 0.002]
    if fix_b is None:
        lo, hi, scale = lo[:1] + [0.0] + lo[1:], hi[:1] + [1.2] + hi[1:], scale[:1] + [0.1] + scale[1:]
    if free_P:
        lo, hi, scale = lo + [-0.003], hi + [0.003], scale + [1e-4]
    best = None
    for b0 in ((0.1, 0.4, 0.7) if fix_b is None else (None,)):
        x0 = [k0] + ([b0] if fix_b is None else []) + [0.0] + ([0.0] if free_P else [])
        res = least_squares(resid, x0, bounds=(lo, hi), x_scale=scale)
        if best is None or res.cost < best.cost:
            best = res
    k, b, dt, dP = unpack(best.x)
    return float(k), float(b), float(tc0 + dt), float(P + dP)
''')

sub('''        k_raw = fit_transit(t, r, sigma, excl, Pf, tcf, e, w, star, 0.0, False)[0]
''', '''        k_raw = fit_transit(t, r, sigma, excl, Pf, tcf, e, w, star, 0.0, False, fix_b=bb)[0]
        k_free, b_free = fit_transit(t, r, sigma, excl, Pf, tcf, e, w, star, 0.0, False)[:2]
''')

sub('''            "radius_earth_without_the_second_star": round(k_raw * star["radius"] * R_SUN / R_EARTH, 3)})
''', '''            "radius_earth_without_the_second_star": round(k_raw * star["radius"] * R_SUN / R_EARTH, 3),
            "radius_earth_without_the_second_star_b_free": round(k_free * star["radius"] * R_SUN / R_EARTH, 3),
            "impact_parameter_without_the_second_star_b_free": round(b_free, 3)})
''')

# --- generate.py: both dilution diagnostics in [other routes]
g = Path("tasks/active/rv-planet-census/tests/generate.py")
gs = g.read_bytes().decode("utf-8")
old = '''            out.append("radius of the planet at %.4f d without the second star's light: %.3f, %+.1f percent from %.2f"
                       % (want["P"], s["radius_earth_without_the_second_star"],
                          pct(s["radius_earth_without_the_second_star"], want["R"]), want["R"]))
'''
new = '''            out.append("radius of the planet at %.4f d without the second star's light, impact parameter as fitted: "
                       "%.3f, %+.1f percent from %.2f; impact parameter free (b %.2f): %.3f, %+.1f percent"
                       % (want["P"], s["radius_earth_without_the_second_star"],
                          pct(s["radius_earth_without_the_second_star"], want["R"]), want["R"],
                          s["impact_parameter_without_the_second_star_b_free"],
                          s["radius_earth_without_the_second_star_b_free"],
                          pct(s["radius_earth_without_the_second_star_b_free"], want["R"])))
'''
assert gs.count(old) == 1
g.write_bytes(gs.replace(old, new).encode("utf-8"))
print("generate.py edited")

# --- no-transit search with every known dip masked
sub('''    w2 = nb2 / sigma ** 2
    for fm in fams:
        if fm["kind"] == "binary":
            w2 = np.where(family_mask(tb2, fm, pad=0.03), 0.0, w2)
''', '''    w2 = nb2 / sigma ** 2
    for fm in fams:
        w2 = np.where(family_mask(tb2, fm, pad=0.03), 0.0, w2)
''')

p.write_bytes(s.encode("utf-8"))
print("solve.py edited")
