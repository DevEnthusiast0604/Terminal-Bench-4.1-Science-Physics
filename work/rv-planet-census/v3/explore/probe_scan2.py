"""probe_scan.py, extended: for each configuration of f (period, K, phase after e's dip), under the reference's noise
model at fixed noise (generalized chi-square, the inner three planets as a reference run has them):

  held      e and f at the truth (f circular), K solved: K_f and chi2
  pair_c    e free (P, tc, e, w), f circular (P, tc free)
  single    e free alone (eight eccentric starts): chi2, e, w, K_e, conjunction offset from the dip, duration factor
  single_tc e alone with its conjunction held on the dip (P, e, w free): chi2, e, w, K_e

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/probe_scan2.py TASK_DIR DIAG.json
    "P_f,K_f,phase ..." """
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
configs = [tuple(float(x) for x in c.split(",")) for c in sys.argv[3].split()]

TC_DIP = 2460270.842
F_OLD = (56.9, 1.8, 2460300.430)

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
noise = np.log([nz["jit_vis"], nz["jit_nir"], nz["h_vis"], nz["h_nir"], max(nz["h_slow"], 1e-3)])
y0 = rv.y.copy()
inner = [[p["period"], p["tc"], math.sqrt(p["e"]) * math.cos(p["omega"]), math.sqrt(p["e"]) * math.sin(p["omega"])]
         for p in diag["planets"] if p["period"] < 100]
rho = lambda e, w: math.sqrt(1 - e * e) / (1 + e * math.sin(w))


def circ(t, P, K, tc):
    return -K * np.sin(2 * math.pi * (t - tc) / P)


def ecc_from(h, q):
    e = math.hypot(h, q)
    if e > 0.85:
        h, q, e = h * 0.85 / e, q * 0.85 / e, 0.85
    w = math.atan2(q, h)
    return math.sqrt(e) * math.cos(w), math.sqrt(e) * math.sin(w), e


def best_of(cost, starts):
    best = None
    for x0 in starts:
        r = minimize(cost, np.array(x0, float), method="Nelder-Mead",
                     options={"maxiter": 3000, "xatol": 1e-6, "fatol": 1e-4})
        r = minimize(cost, r.x, method="Nelder-Mead", options={"maxiter": 3000, "xatol": 1e-7, "fatol": 1e-5})
        if best is None or r.fun < best.fun:
            best = r
    return best


for P_f, K_f, phase in configs:
    tc_f = TC_DIP + phase * P_f
    rv.y = y0 - circ(rv.t, *F_OLD) + circ(rv.t, P_f, K_f, tc_f)
    fac = rv.factor(noise)
    se, ce = math.sqrt(0.04), 1.2
    held = inner + [[115.3, TC_DIP, se * math.cos(ce), se * math.sin(ce)], [P_f, tc_f, 0.0, 0.0]]
    c_held, beta, cov, _ = rv.solve(held, fac)
    kf, skf = beta[6], math.sqrt(cov[6, 6])

    def cost_pair(x):    # e: dlnP, dtc, h, q ; f: dlnP, dtc (circular)
        sc, ss, _ = ecc_from(x[2], x[3])
        pl = inner + [[115.3 * math.exp(x[0]), TC_DIP + x[1], sc, ss], [P_f * math.exp(x[4]), tc_f + x[5], 0.0, 0.0]]
        return rv.solve(pl, fac)[0]
    rp = best_of(cost_pair, [[0, 0, 0.04 * math.cos(1.2), 0.04 * math.sin(1.2), 0, 0]])
    sc, ss, e_pc = ecc_from(rp.x[2], rp.x[3])
    pl_pc = inner + [[115.3 * math.exp(rp.x[0]), TC_DIP + rp.x[1], sc, ss],
                     [P_f * math.exp(rp.x[4]), tc_f + rp.x[5], 0.0, 0.0]]
    kf_pc = rv.solve(pl_pc, fac)[1][6]

    def cost_single(x):  # e: dlnP, dtc, h, q
        sc, ss, _ = ecc_from(x[2], x[3])
        return rv.solve(inner + [[115.3 * math.exp(x[0]), TC_DIP + x[1], sc, ss]], fac)[0]
    starts = [[0, 0, 0.3 * math.cos(w), 0.3 * math.sin(w)] for w in np.linspace(-math.pi, math.pi, 8, endpoint=False)]
    r1 = best_of(cost_single, starts)
    sc1, ss1, e1 = ecc_from(r1.x[2], r1.x[3])
    w1 = math.atan2(ss1, sc1)
    P1, tc1 = 115.3 * math.exp(r1.x[0]), TC_DIP + r1.x[1]
    n = round((TC_DIP - tc1) / P1)
    off = tc1 + n * P1 - TC_DIP
    ke1 = rv.solve(inner + [[P1, tc1, sc1, ss1]], fac)[1][5]

    def cost_tc(x):      # e with its conjunction on the dip: dlnP, h, q
        sc, ss, _ = ecc_from(x[1], x[2])
        return rv.solve(inner + [[115.3 * math.exp(x[0]), TC_DIP, sc, ss]], fac)[0]
    r2 = best_of(cost_tc, [[0, 0.3 * math.cos(w), 0.3 * math.sin(w)] for w in np.linspace(-math.pi, math.pi, 8,
                                                                                            endpoint=False)])
    sc2, ss2, e2 = ecc_from(r2.x[1], r2.x[2])
    w2_ = math.atan2(ss2, sc2)
    print("P_f %.2f K_f %.2f ph %.3f | held K_f %.2f+-%.2f (%+.0f%%) | pair_c K_f %.2f e_e %.2f: chi2 held-pair_c %+.1f"
          " | single e %.2f w %+.0f K_e %.2f conj %+.1f d dur x%.2f: single-pair_c %+.1f | conj on dip: e %.2f w %+.0f,"
          " single_tc-pair_c %+.1f"
          % (P_f, K_f, phase, kf, skf, 100 * (kf - K_f) / K_f, kf_pc, e_pc, c_held - rp.fun, e1, math.degrees(w1), ke1,
             off, rho(e1, w1) / rho(0.04, 1.2), r1.fun - rp.fun, e2, math.degrees(w2_), r2.fun - rp.fun), flush=True)
