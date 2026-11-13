"""Run 2 put f (truth: 56.90 d, K 2.00, circular) at 56.24 d, K 2.854, e 0.731. Under the reference's own noise model
(built as main() builds it), with e's conjunction held on the dip as the reference holds it, compare the likelihood of
the reference's final model with the same model refitted with f circular, with e and f circular, and with the true
orbits of e and f. Also prints, for each fitted pair (f, e), how close f's apoapsis comes to e's periapsis.

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/probe_ecc.py TASK_DIR DIAG.json
Nothing here is the oracle: it imports the reference's model classes and fits them to the draft's data."""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

task = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("solve", task / "solution" / "solve.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
S.DATA = task / "environment" / "data"
diag = json.load(open(sys.argv[2]))
DIP = 2460270.8412
MSTAR = None

vis = S.table(S.DATA / "rv_vis.txt")
nir = S.table(S.DATA / "rv_nir.txt")
tv, yv, ev = vis[:, 0], vis[:, 1], vis[:, 2]
tn, yn, en = nir[:, 0], nir[:, 1], nir[:, 2]
ha, eha = vis[:, 7], vis[:, 8]
rot = diag["rotation"]
_, P2, l2, w2, amp_ha, jit_ha = S.gp_fit_series(tv, ha, eha, [rot["P_rot_halpha_gp"]])
ha_nir = S.gp_predict(tv, ha, eha, (P2, l2, w2, amp_ha, jit_ha), tn)
reg = np.zeros((len(tv) + len(tn), 2))
reg[:len(tv), 0] = ha - np.mean(ha)
reg[len(tv):, 1] = ha_nir - np.mean(ha)
rv = S.RV(tv, yv, ev, tn, yn, en, (rot["P_rot_halpha_gp"], rot["lam_dlw"], rot["w_dlw"]), regressors=reg)
nz = diag["noise"]
start_noise = np.log([nz["jit_vis"], nz["jit_nir"], nz["h_vis"], nz["h_nir"], max(nz["h_slow"], 1e-3)])


def planet(P, tc, e, w):
    return [P, tc, math.sqrt(e) * math.cos(w), math.sqrt(e) * math.sin(w)]


def fit_mixed(planets, fac, circular, pin):
    """fit_planets with the planets in `circular` held at e = 0 (their P and phase still free)."""
    base = [list(p) for p in planets]
    for k in circular:
        base[k][2] = base[k][3] = 0.0
    x0, bounds = [], []
    for k in range(len(base)):
        P = base[k][0]
        dl = P / rv.span
        x0 += list(S.to_fit(base[k], rv.tmid))
        eb = (0.0, 0.0) if k in circular else (-0.9, 0.9)
        bounds += [(math.log(P) - dl, math.log(P) + dl), (None, None), eb, eb]

    def unpack(x):
        pl, pen = [], 0.0
        for k in range(len(base)):
            p, extra = S.from_fit(x[4 * k:4 * k + 4], rv.tmid)
            pl.append(p)
            pen += extra
        return pl, pen

    def cost(x):
        pl, pen = unpack(x)
        return rv.solve(pl, fac)[0] + pen + S.pin_penalty(pl, pin)

    x = np.array(x0)
    for _ in range(2):
        x = minimize(cost, x, method="L-BFGS-B", bounds=bounds, options={"maxiter": 3000}).x
    out, _ = unpack(x)
    _, beta, _, _ = rv.solve(out, fac)
    for k in range(len(out)):
        if beta[2 + k] < 0:
            out[k] = S.flipped(*out[k])
    return out


def fit(planets, circular, pin, rounds=4):
    rv.noise = start_noise.copy()
    lnl = None
    for _ in range(rounds):
        planets = fit_mixed(planets, rv.factor(rv.noise), circular, pin)
        new = rv.fit_noise(planets)
        if lnl is not None and abs(new - lnl) < 0.1:
            return planets, new
        lnl = new
    return planets, lnl


def show(name, planets, lnl):
    fac = rv.factor(rv.noise)
    _, beta, cov, _ = rv.solve(planets, fac)
    parts = []
    for k, (P, tc, sc, ss) in enumerate(planets):
        parts.append("%.3f K %.2f+-%.2f e %.2f w %+.0f" % (P, beta[2 + k], math.sqrt(cov[2 + k, 2 + k]),
                                                           sc * sc + ss * ss, math.degrees(math.atan2(ss, sc))))
    ef = [p for p in planets if 40 < p[0] < 80]
    ee = [p for p in planets if p[0] > 100]
    gap = ""
    if ef and ee:
        Pf, Pe = ef[0][0], ee[0][0]
        e_f = ef[0][2] ** 2 + ef[0][3] ** 2
        e_e = ee[0][2] ** 2 + ee[0][3] ** 2
        ratio = (Pe / Pf) ** (2.0 / 3.0)
        gap = " | f apoapsis %.3f, e periapsis %.3f (units of f's a)" % (1 + e_f, ratio * (1 - e_e))
    print("%-34s lnL %.2f | %s%s" % (name, lnl, "; ".join(parts), gap), flush=True)


ref = [planet(p["period"], p["tc"], p["e"], p["omega"]) for p in diag["planets"]]
ke = max(range(len(ref)), key=lambda k: ref[k][0])
kf = [k for k in range(len(ref)) if 40 < ref[k][0] < 80][0]
pin = (ke, DIP, S.PIN_SIGMA_D)
print("e is planet %d, f is planet %d; pin %s" % (ke, kf, pin), flush=True)

pl, lnl = fit(ref, set(), pin)
show("reference's final model, refitted", pl, lnl)
lnl_free = lnl

pl, lnl = fit(ref, {kf}, pin)
show("f circular", pl, lnl)
pl, lnl = fit(ref, {kf, ke}, pin)
show("f and e circular", pl, lnl)

truth = [list(q) for q in ref]
truth[ke] = planet(115.3, 2460270.842, 0.04, 1.2)
truth[kf] = planet(56.9, 2460313.517, 0.0, 0.0)
pl, lnl = fit(truth, {kf}, pin)
show("from the truth, f circular", pl, lnl)
pl, lnl = fit(truth, set(), pin)
show("from the truth, all free", pl, lnl)
rv.noise = start_noise.copy()
lnl = rv.fit_noise(truth)
show("truth for e and f held", truth, lnl)
