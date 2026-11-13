"""Scan planet f's period, phase and K under the reference's own noise model at fixed noise (solve.py's RV class,
built as main() builds it, noise parameters from a reference run's diagnostics). The draft data hold f at
(56.9 d, 1.8 m/s, tc 2460300.430); each configuration swaps that signal for another in the velocities, which is exact
because f adds no random draw.

For each configuration: K_f by generalized least squares with e and f held at the truth; the pair (e and f free from
the truth) against the single eccentric reading (e free from eight eccentric starts), as generalized chi-square at
fixed noise; and where the single reading puts e's conjunction and how long its transit lasts.

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/probe_scan.py TASK_DIR DIAG.json
    "P_f,K_f,phase P_f,K_f,phase ..."   (phase: fraction of P_f after e's dip at 2460270.842)"""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

task = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("solve", task / "solution" / "solve.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
S.DATA = task / "environment" / "data"
diag = json.load(open(sys.argv[2]))
configs = [tuple(float(x) for x in c.split(",")) for c in sys.argv[3].split()]

TC_DIP = 2460270.842
F_OLD = (56.9, 1.8, 2460300.430)
E_TRUE = (115.3, 2460270.842, 0.04, 1.2)

vis = S.table(S.DATA / "rv_vis.txt")
nir = S.table(S.DATA / "rv_nir.txt")
tv, yv, ev = vis[:, 0], vis[:, 1], vis[:, 2]
tn, yn, en = nir[:, 0], nir[:, 1], nir[:, 2]
ha, eha = vis[:, 7], vis[:, 8]
rot = diag["rotation"]
_, P_rot2, lam_ha2, w_ha2, amp_ha, jit_ha = S.gp_fit_series(tv, ha, eha, [rot["P_rot_halpha_gp"]])
ha_nir = S.gp_predict(tv, ha, eha, (P_rot2, lam_ha2, w_ha2, amp_ha, jit_ha), tn)
reg = np.zeros((len(tv) + len(tn), 2))
reg[:len(tv), 0] = ha - np.mean(ha)
reg[len(tv):, 1] = ha_nir - np.mean(ha)
rv = S.RV(tv, yv, ev, tn, yn, en, (rot["P_rot_halpha_gp"], rot["lam_dlw"], rot["w_dlw"]), regressors=reg)
nz = diag["noise"]
noise = np.log([nz["jit_vis"], nz["jit_nir"], nz["h_vis"], nz["h_nir"], max(nz["h_slow"], 1e-3)])
y0 = rv.y.copy()


def circ(t, P, K, tc):
    return -K * np.sin(2 * math.pi * (t - tc) / P)


def planet(P, tc, e, w):
    return [P, tc, math.sqrt(e) * math.cos(w), math.sqrt(e) * math.sin(w)]


inner = [planet(p["period"], p["tc"], p["e"], p["omega"]) for p in diag["planets"] if p["period"] < 100]
star = {"mass": 0.690, "radius": 0.672}
print("noise", nz, flush=True)
for P_f, K_f, phase in configs:
    tc_f = TC_DIP + phase * P_f
    rv.y = y0 - circ(rv.t, *F_OLD) + circ(rv.t, P_f, K_f, tc_f)
    fac = rv.factor(noise)
    e0 = planet(*E_TRUE)
    f0 = planet(P_f, tc_f, 0.0, 0.0)
    held = inner + [e0, f0]
    c_held, beta, cov, _ = rv.solve(held, fac)
    kf, skf = beta[2 + 4], math.sqrt(cov[2 + 4, 2 + 4])
    pair = S.RV.fit_planets(rv, [list(q) for q in held], fac, free=[3, 4])
    c_pair, bp, cp, _ = rv.solve(pair, fac)
    best = None
    for w0 in np.linspace(0, 2 * math.pi, 8, endpoint=False):
        start = inner + [planet(115.3, TC_DIP, 0.25, w0)]
        sol = rv.fit_planets(start, fac, free=[3])
        c1 = rv.solve(sol, fac)[0]
        if best is None or c1 < best[0]:
            best = (c1, sol)
    c_single, single = best
    P1, tc1, sc1, ss1 = single[3]
    e1, w1 = sc1 * sc1 + ss1 * ss1, math.atan2(ss1, sc1)
    n = round((TC_DIP - tc1) / P1)
    off = tc1 + n * P1 - TC_DIP
    rho = lambda e, w: math.sqrt(1 - e * e) / (1 + e * math.sin(w))
    Pp, tcp, scp, ssp = pair[4]
    print("P_f %.2f K_f %.2f phase %.3f: K_f held %.2f +- %.2f (%+.0f%%); pair K_f %.2f e_f %.2f e_e %.2f; "
          "chi2 single - pair %+.1f, held - pair %+.1f | single: e %.2f w %+.0f K %.2f, conj %+.1f d, duration x%.2f"
          % (P_f, K_f, phase, kf, skf, 100 * (kf - K_f) / K_f, bp[6], scp ** 2 + ssp ** 2,
             pair[3][2] ** 2 + pair[3][3] ** 2, c_single - c_pair, c_held - c_pair, e1, math.degrees(w1),
             rv.solve(single, fac)[1][5], off, rho(e1, w1) / rho(0.04, 1.2)), flush=True)
