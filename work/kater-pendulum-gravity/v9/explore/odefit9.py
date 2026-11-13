"""Joint least-squares fit of the damped pendulum equation + oblique-camera map to all six runs."""
import json
import math
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import red9b as R  # file readers only

DT = 1.0 / 480.0


def clock_map(idx, c0, gps, sync_ctr):
    f = ((sync_ctr - c0) % 65536).astype(float)
    s = (gps - gps.min()).astype(float)
    o = np.argsort(s)
    s, f = s[o], f[o]
    r = np.median(np.diff(f) / np.diff(s))
    cut = np.flatnonzero(np.diff(f) - r * np.diff(s) < -1.5) + 1
    groups = np.split(np.arange(len(s)), cut)
    t = np.full(len(idx), np.nan)
    for g, members in enumerate(groups):
        lo = -np.inf if g == 0 else 0.5 * (f[groups[g - 1][-1]] + f[members[0]])
        hi = np.inf if g == len(groups) - 1 else 0.5 * (f[members[-1]] + f[groups[g + 1][0]])
        slope, icpt = np.polyfit(s[members], f[members], 1)
        sel = (idx >= lo) & (idx < hi)
        t[sel] = (idx[sel] - icpt) / slope
    for a, b in zip(groups[:-1], groups[1:]):
        t[(idx > f[a[-1]] - 1) & (idx < f[b[0]] + 1)] = np.nan
    return t


def integrate(w2, c1, c2, x0, n):
    """RK4 from rest at x0 for arrays of parameter sets; returns X, V of shape (n, m)."""
    x = np.array(x0, dtype=float)
    v = np.zeros_like(x)
    X = np.empty((n, len(x)))
    V = np.empty((n, len(x)))

    def acc(x, v):
        return -w2 * np.sin(x) - c1 * v - c2 * np.abs(v) * v

    h = DT
    for i in range(n):
        X[i], V[i] = x, v
        a1 = acc(x, v)
        x2, v2 = x + 0.5 * h * v, v + 0.5 * h * a1
        a2 = acc(x2, v2)
        x3, v3 = x + 0.5 * h * v2, v + 0.5 * h * a2
        a3 = acc(x3, v3)
        x4, v4 = x + h * v3, v + h * a3
        a4 = acc(x4, v4)
        x = x + h * (v + 2 * v2 + 2 * v3 + v4) / 6.0
        v = v + h * (a1 + 2 * a2 + 2 * a3 + a4) / 6.0
    return X, V


def hermite(X, V, tau):
    """Values and derivatives at times tau >= 0 from grid samples (columns are trajectories)."""
    u = tau / DT
    i = np.minimum(u.astype(int), X.shape[0] - 2)
    s = (u - i)[:, None]
    h00, h10, h01, h11 = 2 * s**3 - 3 * s**2 + 1, s**3 - 2 * s**2 + s, -2 * s**3 + 3 * s**2, s**3 - s**2
    x = h00 * X[i] + h10 * DT * V[i] + h01 * X[i + 1] + h11 * DT * V[i + 1]
    d00, d10, d01, d11 = 6 * s**2 - 6 * s, 3 * s**2 - 4 * s + 1, -6 * s**2 + 6 * s, 3 * s**2 - 2 * s
    v = (d00 * X[i] + d10 * DT * V[i] + d01 * X[i + 1] + d11 * DT * V[i + 1]) / DT
    return x, v


def cam(theta, a, s, rho):
    N, D = a * np.sin(theta), np.cos(theta) - s * np.sin(theta)
    q = N * N + D * D
    phi = rho + np.arctan2(N, D)
    dth = (D * a * np.cos(theta) + N * (np.sin(theta) + s * np.cos(theta))) / q
    da = D * np.sin(theta) / q
    ds = N * np.sin(theta) / q
    return phi, dth, da, ds


class Obs:
    def __init__(self, data_dir, rid):
        meta, counter, phi, ok = R.read_run(os.path.join(data_dir, "runs", rid + ".csv"))
        gps, sctr = R.read_sync(os.path.join(data_dir, "sync", rid + ".csv"))
        t = clock_map(R.unwrap(counter), int(counter[0]), gps, sctr)
        start = np.median(phi[:40])
        moved = int(np.flatnonzero(np.abs(phi - start) > 0.004)[0])
        self.held = phi[:max(moved - 12, 20)]
        keep = ok & np.isfinite(t) & (np.arange(len(phi)) >= moved - 6)
        self.t, self.phi = t[keep], phi[keep]
        self.t_release_guess = float(t[moved - 1])
        self.pivot = rid[0]


def rough(o, rho):
    d = o.phi - rho
    up = np.flatnonzero((d[:-1] < 0) & (d[1:] >= 0))
    return (o.t[up[-1]] - o.t[up[0]]) / (len(up) - 1)


def fit(data_dir, verbose=False):
    ids = ["a1", "a2", "a3", "b1", "b2", "b3"]
    obs = [Obs(data_dir, rid) for rid in ids]
    rho0 = float(np.median(np.concatenate([o.phi for o in obs])))
    p = [1.0, 0.0, rho0]
    for o in obs:
        T = rough(o, rho0)
        p += [(2 * math.pi / T) ** 2, 0.02, 0.01, float(np.median(o.held)) - rho0, o.t_release_guess]
    p = np.array(p)
    hstep = np.array([1e-5, 1e-6, 1e-6, 1e-7])     # w2, c1, c2, x0 finite-difference steps

    def evaluate(p, span):
        a, s, rho = p[:3]
        W2, C1, C2, X0 = [], [], [], []
        for k in range(len(obs)):
            base = list(p[3 + 5 * k:7 + 5 * k])
            for j in range(5):
                q = list(base)
                if j > 0:
                    q[j - 1] += hstep[j - 1]
                W2.append(q[0]); C1.append(q[1]); C2.append(q[2]); X0.append(q[3])
        tmax = max(min(o.t[-1], o.t[0] + span) - p[7 + 5 * k] for k, o in enumerate(obs)) + 0.1
        X, V = integrate(np.array(W2), np.array(C1), np.array(C2), np.array(X0), int(tmax / DT) + 3)
        rows_r, rows_J = [], []
        for k, o in enumerate(obs):
            tr = p[7 + 5 * k]
            sel = (o.t >= tr) & (o.t <= o.t[0] + span)
            xs, vs = hermite(X[:, 5 * k:5 * k + 5], V[:, 5 * k:5 * k + 5], o.t[sel] - tr)
            phi_m, dth, da, ds = cam(xs[:, 0], a, s, rho)
            J = np.zeros((int(sel.sum()), len(p)))
            J[:, 0], J[:, 1], J[:, 2] = da, ds, 1.0
            for j in range(4):
                J[:, 3 + 5 * k + j] = dth * (xs[:, j + 1] - xs[:, 0]) / hstep[j]
            J[:, 7 + 5 * k] = -dth * vs[:, 0]
            ph0, dth0, da0, ds0 = cam(np.array([p[6 + 5 * k]]), a, s, rho)
            Jh = np.zeros((len(o.held), len(p)))
            Jh[:, 0], Jh[:, 1], Jh[:, 2], Jh[:, 6 + 5 * k] = da0[0], ds0[0], 1.0, dth0[0]
            rows_r += [o.phi[sel] - phi_m, o.held - ph0[0]]
            rows_J += [J, Jh]
        r = np.concatenate(rows_r)
        return r, np.vstack(rows_J), float(r @ r)

    for span in (6.0, 15.0, 35.0, 60.0, 200.0):
        lam = 1e-3
        r, J, cost = evaluate(p, span)
        for it in range(25):
            A, g = J.T @ J, J.T @ r
            accepted = False
            for _ in range(8):
                delta = np.linalg.solve(A + lam * np.diag(np.diag(A)), g)
                r2, J2, c2 = evaluate(p + delta, span)
                if c2 < cost:
                    p, r, J, cost, accepted = p + delta, r2, J2, c2, True
                    lam = max(lam / 3, 1e-9)
                    break
                lam *= 10
            if verbose:
                print("span %5.1f it %2d rms %.3e a %.6f s %.6f rho %.6f" % (span, it, math.sqrt(cost / len(r)), p[0], p[1], p[2]))
            if not accepted or np.max(np.abs(delta[3::5] / p[3::5])) < 1e-10:
                break
    out = {}
    for k, rid in enumerate(ids):
        out[rid] = (2 * math.pi / math.sqrt(p[3 + 5 * k]), abs(p[6 + 5 * k]))
    return out, p[:3]


if __name__ == "__main__":
    d = sys.argv[1]
    res, camp = fit(d, verbose=True)
    exp = json.load(open(os.path.join(d, "expected.json")))
    print("camera", camp)
    for rid, (T0, A0) in res.items():
        print(rid, "T0 err %+.2e  A0 err %+.2e" % (T0 / exp["run_periods_s"][rid] - 1, A0 - exp["release_amplitude_rad"][rid]))
