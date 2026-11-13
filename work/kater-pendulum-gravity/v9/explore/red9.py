"""v9 exploration: reductions with switchable clock / camera / amplitude-law handling."""
import json
import math
import os
import sys

import numpy as np

COUNTER_MOD = 65536
WINDOW = 8
PEAK_WINDOW = 0.20


def read_run(path):
    meta, rows, header = {}, [], None
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                key, _, val = line[1:].partition(":")
                meta[key.strip()] = val.strip()
            elif header is None:
                header = line.split(",")
            else:
                rows.append(line.split(","))
    col = {name: i for i, name in enumerate(header)}
    counter = np.array([int(r[col["frame_counter"]]) for r in rows])
    theta = np.array([float(r[col["theta"]]) for r in rows])
    ok = np.array([int(r[col["tracker_ok"]]) for r in rows]) == 1
    if meta["unit"] == "deg":
        theta = np.radians(theta)
    return meta, counter, theta, ok


def read_sync(path):
    gps, ctr = [], []
    with open(path, encoding="utf-8") as fh:
        next(fh)
        for line in fh:
            if line.strip():
                a, b = line.split(",")
                gps.append(int(a))
                ctr.append(int(b))
    return np.array(gps), np.array(ctr)


def unwrap(counter):
    step = np.diff(counter) % COUNTER_MOD
    return np.concatenate([[0], np.cumsum(step)])


def clock(idx, c0, gps, sctr, mode):
    """Seconds per tracker row and a validity mask. mode: nominal | line | steps | smooth."""
    n = len(idx)
    if mode == "nominal":
        return idx / 240.0, np.ones(n, dtype=bool), {}
    f = ((sctr - c0) % COUNTER_MOD).astype(float)
    S = (gps - gps.min()).astype(float)
    o = np.argsort(S)
    S, f = S[o], f[o]
    deg = {"line": 1, "steps": 1, "smooth": 3}[mode]
    scale = f[-1]
    steps = []

    def design(x, steps, use):
        cols = [(x / scale) ** p for p in range(deg + 1)]
        for j in steps:
            cols.append((x >= f[j + 1]).astype(float))
        return np.column_stack(cols)

    for _ in range(4):
        X = design(f, steps, None)
        coef, *_ = np.linalg.lstsq(X, S, rcond=None)
        poly = coef[:deg + 1]
        dpoly = np.array([p * poly[p] for p in range(1, deg + 1)])
        fm = 0.5 * (f[:-1] + f[1:])
        spf = sum(dpoly[p - 1] * (fm / scale) ** (p - 1) for p in range(1, deg + 1)) / scale   # s per frame
        D = np.diff(f) - np.diff(S) / spf
        if mode == "line":
            break
        new = [int(i) for i in np.flatnonzero(D < -1.5)]
        if new == steps:
            break
        steps = new
    # integer step sizes, then refit
    info = {"steps": [], "resid_rms_frames": None}
    if steps:
        X = design(f, steps, None)
        coef, *_ = np.linalg.lstsq(X, S, rcond=None)
        poly = coef[:deg + 1]
        dpoly = np.array([p * poly[p] for p in range(1, deg + 1)])
        heights = []
        for j, hgt in zip(steps, coef[deg + 1:]):
            fj = 0.5 * (f[j] + f[j + 1])
            spf_j = sum(dpoly[p - 1] * (fj / scale) ** (p - 1) for p in range(1, deg + 1)) / scale
            k = round(hgt / spf_j)
            heights.append(k * spf_j)
            info["steps"].append(k)
        Xp = design(f, [], None)
        target = S - sum(h * (f >= f[j + 1]) for j, h in zip(steps, heights))
        poly, *_ = np.linalg.lstsq(Xp, target, rcond=None)
    else:
        heights = []
    def tmap(x):
        t = sum(poly[p] * (x / scale) ** p for p in range(deg + 1))
        for j, h in zip(steps, heights):
            t = t + h * (x >= f[j + 1])
        return t
    t = tmap(idx.astype(float))
    valid = np.ones(n, dtype=bool)
    for j in steps:
        valid &= ~((idx >= f[j] - 1) & (idx <= f[j + 1] + 1))
    res = S - tmap(f)
    info["resid_rms_frames"] = float(np.std(res) * 240)
    return t, valid, info


def agm(a, b):
    for _ in range(40):
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return a


def to_true(phi, a, s, rho):
    d = phi - rho
    return np.arctan2(np.sin(d), a * np.cos(d) + s * np.sin(d))


def crossings(t, y, usable):
    out = []
    idx = np.flatnonzero((y[:-1] * y[1:] < 0) & usable[:-1] & usable[1:])
    n = len(y)
    for i in idx:
        lo, hi = i - WINDOW + 1, i + WINDOW + 1
        if lo < 0 or hi > n or not usable[lo:hi].all() or t[hi - 1] - t[lo] > 0.2:
            continue
        a, b = np.polyfit(t[lo:hi] - t[i], y[lo:hi], 1)
        out.append((t[i] - b / a, 1 if a > 0 else -1, abs(a)))
    return out


def extremum(t, y, usable, t_ext, sign):
    sel = usable & (np.abs(t - t_ext) < PEAK_WINDOW)
    if sel.sum() < 40:
        return None
    x = t[sel] - t_ext
    c = np.polyfit(x, y[sel], 4)
    xs = np.linspace(x.min(), x.max(), 2001)
    ys = np.polyval(c, xs)
    j = int(np.argmax(sign * ys))
    return ys[j], xs[j] + t_ext


class Run:
    def __init__(self, data_dir, rid, clock_mode):
        self.rid = rid
        meta, counter, phi, ok = read_run(os.path.join(data_dir, "runs", rid + ".csv"))
        gps, sctr = read_sync(os.path.join(data_dir, "sync", rid + ".csv"))
        idx = unwrap(counter)
        self.t, valid, self.clock_info = clock(idx, int(counter[0]), gps, sctr, clock_mode)
        self.phi = phi
        self.usable = ok & valid

    def cycles(self, a, s, rho):
        """(period, image extreme of first half, image extreme of second half, direction) per same-direction
        crossing pair, plus crossing records."""
        th = to_true(self.phi, a, s, rho)
        cr = crossings(self.t, th, self.usable)
        out = []
        for direction in (1, -1):
            times = [(c, sl) for c, d, sl in cr if d == direction]
            for (t0, _), (t1, _) in zip(times[:-1], times[1:]):
                if not 1.0 < t1 - t0 < 3.0:
                    continue
                sel = self.usable & (self.t >= t0) & (self.t <= t1)
                if sel.sum() < 0.9 * (t1 - t0) * 240:
                    continue
                e1 = extremum(self.t, self.phi, self.usable, 0.5 * (t0 + t1) - (t1 - t0) / 4, direction)
                e2 = extremum(self.t, self.phi, self.usable, 0.5 * (t0 + t1) + (t1 - t0) / 4, -direction)
                if e1 is None or e2 is None:
                    continue
                hi = e1[0] if direction > 0 else e2[0]
                lo = e2[0] if direction > 0 else e1[0]
                out.append((t1 - t0, hi, lo, direction, t0))
        return out, cr

    def half_asym(self, a, s, rho):
        """Mean of (time above - time below) per cycle and mean |slope| (true-angle units)."""
        th = to_true(self.phi, a, s, rho)
        cr = crossings(self.t, th, self.usable)
        vals, slopes = [], []
        for k in range(1, len(cr) - 1):
            (t0, d0, s0), (t1, d1, s1), (t2, d2, s2) = cr[k - 1], cr[k], cr[k + 1]
            if d0 == d1 or d1 == d2 or t2 - t0 > 3.0:
                continue
            h1, h2 = t1 - t0, t2 - t1
            above = h1 if d0 > 0 else h2
            below = h2 if d0 > 0 else h1
            vals.append(above - below)
            slopes.append(s1)
        return vals, slopes


def amp_true(hi, lo, a, s, rho):
    up = math.atan2(math.sin(hi - rho), a * math.cos(hi - rho) + s * math.sin(hi - rho))
    dn = -math.atan2(math.sin(lo - rho), a * math.cos(lo - rho) + s * math.sin(lo - rho))
    return up, dn


def law(A, kind):
    if kind == "exact":
        return agm(1.0, math.cos(A / 2.0))
    if kind == "series1":
        return 1.0 / (1.0 + A * A / 16.0)
    raise ValueError(kind)


def golden(fn, lo, hi, n=50):
    for _ in range(n):
        m1, m2 = lo + 0.382 * (hi - lo), lo + 0.618 * (hi - lo)
        if fn(m1) < fn(m2):
            hi = m2
        else:
            lo = m1
    return 0.5 * (lo + hi)


def reduce_all(data_dir, clock_mode="smooth", camera="full", lawkind="exact", verbose=False):
    ids = ["a1", "a2", "a3", "b1", "b2", "b3"]
    runs = {rid: Run(data_dir, rid, clock_mode) for rid in ids}
    a, s, rho = 1.0, 0.0, 0.0
    # first level: mean of extreme percentiles over all runs
    rho = float(np.median([0.5 * (np.percentile(r.phi[r.usable], 99.5) + np.percentile(r.phi[r.usable], 0.5)) for r in runs.values()]))
    for it in range(6):
        # level from half-period symmetry
        if camera != "none" or True:
            v, sl = [], []
            for r in runs.values():
                vv, ss = r.half_asym(a, s, rho)
                v += vv
                sl += ss
            # time above - below = -4 delta / |theta'|  =>  delta(true) = -(above-below)|theta'|/4
            dth = -float(np.median(np.array(v) * np.array(sl))) / 4.0
            rho -= a * dth
        cyc = {rid: r.cycles(a, s, rho)[0] for rid, r in runs.items()}
        if camera == "full":
            # s/a from extreme asymmetry: 1/u_minus - 1/u_plus = 2 s/a  (decay interpolated)
            sig = []
            for rid, cl in cyc.items():
                for per, hi, lo, d, t0 in cl:
                    up, dn = math.tan(hi - rho), math.tan(rho - lo)
                    sig.append(0.5 * (1.0 / dn - 1.0 / up))
            sigma = float(np.median(sig))
        else:
            sigma = 0.0
        if camera in ("full", "gain"):
            def cost(aa):
                ss = sigma * aa
                res = []
                for piv in "ab":
                    est = []
                    for rid, cl in cyc.items():
                        if rid[0] != piv:
                            continue
                        for per, hi, lo, d, t0 in cl:
                            up, dn = amp_true(hi, lo, aa, ss, rho)
                            est.append(per * law(0.5 * (up + dn), lawkind))
                    est = np.array(est)
                    res.append(((est - est.mean()) ** 2).sum())
                return sum(res)
            a = golden(cost, 0.80, 1.10, 60)
            s = sigma * a
        if verbose:
            print("iter %d: rho %.5f a %.5f s %.5f" % (it, rho, a, s))
    per_run = {}
    for rid, cl in cyc.items():
        est = []
        for per, hi, lo, d, t0 in cl:
            up, dn = amp_true(hi, lo, a, s, rho)
            est.append(per * law(0.5 * (up + dn), lawkind))
        per_run[rid] = float(np.mean(est))
    return per_run, (a, s, rho), {rid: r.clock_info for rid, r in runs.items()}


def pivots(per_run, ha=0.20011, sep=1.00003):
    hb = sep - ha
    ta = float(np.mean([v for r, v in per_run.items() if r[0] == "a"]))
    tb = float(np.mean([v for r, v in per_run.items() if r[0] == "b"]))
    g = 4 * math.pi ** 2 * (ha ** 2 - hb ** 2) / (ta ** 2 * ha - tb ** 2 * hb)
    k2 = 0.5 * (g * ha * ta ** 2 + g * hb * tb ** 2) / (4 * math.pi ** 2) - 0.5 * (ha ** 2 + hb ** 2)
    return g, ta, tb, math.sqrt(k2)


def report(data_dir, label, **kw):
    exp = json.load(open(os.path.join(data_dir, "expected.json")))
    per_run, cam, ci = reduce_all(data_dir, **kw)
    g, ta, tb, k = pivots(per_run)
    errs = {r: v / exp["run_periods_s"][r] - 1 for r, v in per_run.items()}
    print("%-28s cam a=%.4f s=%.4f rho=%.5f | runs %s | Ta %+.1e Tb %+.1e g %+.1e k %+.1e" % (
        label, cam[0], cam[1], cam[2], " ".join("%+.1e" % errs[r] for r in sorted(errs)),
        ta / exp["small_amplitude_period_s"]["a"] - 1, tb / exp["small_amplitude_period_s"]["b"] - 1,
        g / exp["g_m_s2"] - 1, k / exp["radius_of_gyration_m"] - 1))
    return ci


if __name__ == "__main__":
    d = sys.argv[1]
    ci = report(d, "oracle smooth/full/exact", verbose=False)
    print({k: v for k, v in ci.items()})
    for label, kw in [("clock line", dict(clock_mode="line")),
                      ("clock steps (linear)", dict(clock_mode="steps")),
                      ("camera none", dict(camera="none")),
                      ("camera gain only", dict(camera="gain")),
                      ("series1 law", dict(lawkind="series1")),
                      ("camera none + steps clock", dict(camera="none", clock_mode="steps"))]:
        report(d, label, **kw)
