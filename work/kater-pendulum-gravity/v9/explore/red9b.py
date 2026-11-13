"""v9 exploration: oracle and variants for the oblique-camera design."""
import json
import math
import os
import sys

import numpy as np

COUNTER_MOD = 65536
WINDOW = 8
PEAK_WINDOW = 0.20
STEP_FRAMES = 1.5


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


def clock(idx, c0, gps, sctr, mode="steps"):
    n = len(idx)
    if mode == "nominal":
        return idx / 240.0, np.ones(n, dtype=bool), []
    f = ((sctr - c0) % COUNTER_MOD).astype(float)
    s = (gps - gps.min()).astype(float)
    o = np.argsort(s)
    s, f = s[o], f[o]
    if mode == "line":
        slope, icpt = np.polyfit(s, f, 1)
        return (idx - icpt) / slope, np.ones(n, dtype=bool), []
    r0 = np.median(np.diff(f) / np.diff(s))
    cut = np.flatnonzero(np.diff(f) - r0 * np.diff(s) < -STEP_FRAMES)
    groups = np.split(np.arange(len(s)), cut + 1)
    num = den = 0.0
    for g in groups:
        if len(g) >= 2:
            ss, ff = s[g] - s[g].mean(), f[g] - f[g].mean()
            num += float((ss * ff).sum())
            den += float((ss * ss).sum())
    rate = num / den
    icpts = [float(f[g].mean() - rate * s[g].mean()) for g in groups]
    t = np.empty(n)
    valid = np.ones(n, dtype=bool)
    steps = []
    for gi, (g, icpt) in enumerate(zip(groups, icpts)):
        lo = -np.inf if gi == 0 else f[groups[gi - 1][-1]]
        hi = np.inf if gi == len(groups) - 1 else f[groups[gi + 1][0]]
        sel = (idx >= lo) & (idx < hi)
        t[sel] = (idx[sel] - icpt) / rate
        if gi > 0:
            steps.append(icpts[gi - 1] - icpt)
    for a, b in zip(groups[:-1], groups[1:]):
        valid &= ~((idx >= f[a[-1]] - 1) & (idx <= f[b[0]] + 1))
    return t, valid, steps


def agm(a, b):
    for _ in range(40):
        a, b = 0.5 * (a + b), math.sqrt(a * b)
    return a


def law(A, kind="exact"):
    if kind == "exact":
        return agm(1.0, math.cos(A / 2.0))
    if kind == "series1":
        return 1.0 / (1.0 + A * A / 16.0)
    if kind == "series2":
        return 1.0 / (1.0 + A * A / 16.0 + 11 * A ** 4 / 3072.0)
    raise ValueError(kind)


def to_true(phi, a, s, rho):
    d = phi - rho
    return np.arctan2(np.sin(d), a * np.cos(d) + s * np.sin(d))


def golden(fn, lo, hi, n=60):
    for _ in range(n):
        m1, m2 = lo + 0.382 * (hi - lo), lo + 0.618 * (hi - lo)
        if fn(m1) < fn(m2):
            hi = m2
        else:
            lo = m1
    return 0.5 * (lo + hi)


class Run:
    def __init__(self, data_dir, rid, clock_mode="steps"):
        self.rid = rid
        meta, counter, phi, ok = read_run(os.path.join(data_dir, "runs", rid + ".csv"))
        gps, sctr = read_sync(os.path.join(data_dir, "sync", rid + ".csv"))
        idx = unwrap(counter)
        self.t, valid, self.steps = clock(idx, int(counter[0]), gps, sctr, clock_mode)
        self.phi = phi
        # the held stretch: the angle stays at its first value until the catch lets go
        start = np.median(phi[:40])
        moved = np.flatnonzero(np.abs(phi - start) > 0.004)[0]
        self.held = float(np.median(phi[:max(moved - 12, 20)]))
        self.release_t = float(self.t[moved])
        self.usable = ok & valid & (np.arange(len(phi)) >= moved)
        self.extremes = self._extremes()

    def _extremes(self):
        """(time, image angle, sign) of every turning point after release, by a quartic fit."""
        t, y, u = self.t, self.phi, self.usable
        mid = 0.5 * (np.percentile(y[u], 99) + np.percentile(y[u], 1))
        d = y - mid
        idx = np.flatnonzero((d[:-1] * d[1:] < 0) & u[:-1] & u[1:])
        cr = t[idx]
        out = []
        for t0, t1 in zip(cr[:-1], cr[1:]):
            if t1 - t0 < 0.4:
                continue
            tm = 0.5 * (t0 + t1)
            sign = 1 if np.median(d[(t > t0) & (t < t1)]) > 0 else -1
            sel = u & (np.abs(t - tm) < PEAK_WINDOW)
            if sel.sum() < 60:
                continue
            x = t[sel] - tm
            c = np.polyfit(x, y[sel], 4)
            xs = np.linspace(x.min(), x.max(), 4001)
            ys = np.polyval(c, xs)
            j = int(np.argmax(sign * ys))
            if j in (0, len(xs) - 1):
                continue
            out.append((tm + xs[j], ys[j], sign))
        return out

    def crossings(self, a, s, rho):
        th = to_true(self.phi, a, s, rho)
        t, u = self.t, self.usable
        idx = np.flatnonzero((th[:-1] * th[1:] < 0) & u[:-1] & u[1:])
        out = []
        n = len(th)
        for i in idx:
            lo, hi = i - WINDOW + 1, i + WINDOW + 1
            if lo < 0 or hi > n or not u[lo:hi].all() or t[hi - 1] - t[lo] > 0.2:
                continue
            sl, b = np.polyfit(t[lo:hi] - t[i], th[lo:hi], 1)
            out.append((t[i] - b / sl, 1 if sl > 0 else -1, abs(sl)))
        return out


def cycles(run, cr):
    """Same-direction crossing pairs with the extremes between them."""
    ex = run.extremes
    et = np.array([e[0] for e in ex])
    out = []
    for direction in (1, -1):
        times = [c for c, d, _ in cr if d == direction]
        for t0, t1 in zip(times[:-1], times[1:]):
            if not 1.0 < t1 - t0 < 3.0:
                continue
            sel = run.usable & (run.t >= t0) & (run.t <= t1)
            if sel.sum() < 0.9 * (t1 - t0) * 240:
                continue
            inside = [ex[j] for j in np.flatnonzero((et > t0) & (et < t1))]
            if len(inside) != 2:
                continue
            hi = [e[1] for e in inside if e[2] > 0]
            lo = [e[1] for e in inside if e[2] < 0]
            if len(hi) != 1 or len(lo) != 1:
                continue
            out.append((t1 - t0, hi[0], lo[0]))
    return out


def true_amp(hi, lo, a, s, rho):
    up = math.atan2(math.sin(hi - rho), a * math.cos(hi - rho) + s * math.sin(hi - rho))
    dn = -math.atan2(math.sin(lo - rho), a * math.cos(lo - rho) + s * math.sin(lo - rho))
    return 0.5 * (up + dn)


def sigma_from_extremes(runs, rho, order=3):
    vals, wts = [], []
    for r in runs.values():
        ex = r.extremes
        for k in range(3, len(ex) - 3):
            nb = [ex[k - 3], ex[k - 1], ex[k + 1], ex[k + 3]] if order == 3 else [ex[k - 1], ex[k + 1]]
            t1, y1, s1 = ex[k]
            if any(e[2] != -s1 for e in nb) or nb[-1][0] - nb[0][0] > (6.0 if order == 3 else 2.5):
                continue
            tt = np.array([e[0] for e in nb]) - t1
            vv = np.array([1.0 / math.tan(abs(e[1] - rho)) for e in nb])
            inv_opp = float(np.polyval(np.polyfit(tt, vv, len(nb) - 1), 0.0))
            inv_mid = 1.0 / math.tan(abs(y1 - rho))
            # 1/u_minus - 1/u_plus = 2 s / a
            vals.append(0.5 * (inv_opp - inv_mid) if s1 > 0 else 0.5 * (inv_mid - inv_opp))
            wts.append(math.tan(abs(y1 - rho)) ** 4)       # the error of 1/u grows as 1/u^2
    return float(np.average(vals, weights=wts)), vals


def reduce_all(data_dir, clock_mode="steps", camera="full", lawkind="exact", verbose=False, runs=None):
    ids = ["a1", "a2", "a3", "b1", "b2", "b3"]
    if runs is None:
        runs = {rid: Run(data_dir, rid, clock_mode) for rid in ids}
    rho = float(np.median([np.mean([e[1] for e in r.extremes]) for r in runs.values()]))
    a, s = 1.0, 0.0
    for it in range(6):
        v = []
        for r in runs.values():
            cr = r.crossings(a, s, rho)
            for k in range(1, len(cr) - 1):
                (t0, d0, _), (t1, d1, sl), (t2, d2, _) = cr[k - 1], cr[k], cr[k + 1]
                if d0 == d1 or d1 == d2 or t2 - t0 > 3.0:
                    continue
                h1, h2 = t1 - t0, t2 - t1
                above, below = (h1, h2) if d0 > 0 else (h2, h1)
                v.append((above - below) * sl)
        rho += a * float(np.median(v)) / 4.0       # level too high by delta => above - below = -4 delta/|theta'|
        sigma = sigma_from_extremes(runs, rho)[0] if camera == "full" else 0.0
        cyc = {rid: cycles(r, r.crossings(a, s, rho)) for rid, r in runs.items()}
        if camera in ("full", "gain"):
            def cost(aa):
                total = 0.0
                for piv in "ab":
                    est = np.array([per * law(true_amp(hi, lo, aa, sigma * aa, rho), lawkind)
                                    for rid, cl in cyc.items() if rid[0] == piv for per, hi, lo in cl])
                    total += float(((est - est.mean()) ** 2).sum())
                return total
            a = golden(cost, 0.80, 1.10)
            s = sigma * a
        if verbose:
            print("iter %d: rho %.6f a %.6f s %.6f" % (it, rho, a, s))
    per_run, release = {}, {}
    for rid, cl in cyc.items():
        per_run[rid] = float(np.mean([per * law(true_amp(hi, lo, a, s, rho), lawkind) for per, hi, lo in cl]))
        release[rid] = abs(float(to_true(np.array([runs[rid].held]), a, s, rho)[0]))
    return per_run, release, (a, s, rho), runs


def pivots(per_run, ha=0.20011, sep=1.00003):
    hb = sep - ha
    ta = float(np.mean([v for r, v in per_run.items() if r[0] == "a"]))
    tb = float(np.mean([v for r, v in per_run.items() if r[0] == "b"]))
    g = 4 * math.pi ** 2 * (ha ** 2 - hb ** 2) / (ta ** 2 * ha - tb ** 2 * hb)
    k2 = 0.5 * (g * ha * ta ** 2 + g * hb * tb ** 2) / (4 * math.pi ** 2) - 0.5 * (ha ** 2 + hb ** 2)
    return g, ta, tb, math.sqrt(k2)


def report(data_dir, label, **kw):
    exp = json.load(open(os.path.join(data_dir, "expected.json")))
    per_run, release, cam, runs = reduce_all(data_dir, **kw)
    g, ta, tb, k = pivots(per_run)
    errs = {r: v / exp["run_periods_s"][r] - 1 for r, v in per_run.items()}
    aerr = {r: v - exp["release_amplitude_rad"][r] for r, v in release.items()}
    print("%-22s a=%.5f s=%.5f rho=%.5f | T %s | A %s | g %+.1e k %+.1e" % (
        label, cam[0], cam[1], cam[2], " ".join("%+.1e" % errs[r] for r in sorted(errs)),
        " ".join("%+.1e" % aerr[r] for r in sorted(aerr)), g / exp["g_m_s2"] - 1, k / exp["radius_of_gyration_m"] - 1))
    return runs


if __name__ == "__main__":
    d = sys.argv[1]
    runs = report(d, "oracle", verbose=True)
    print({rid: [round(x * 240, 2) for x in r.steps] for rid, r in runs.items()})
    report(d, "gain only", camera="gain", runs=runs)
    report(d, "camera none", camera="none", runs=runs)
    report(d, "series1", lawkind="series1", runs=runs)
    report(d, "series2", lawkind="series2", runs=runs)
    report(d, "clock line", clock_mode="line")
