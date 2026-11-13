"""Fast grid: K_f by generalized least squares under the reference's noise model at fixed noise, with e (nearly
circular, truth) and f (circular, truth) held, for a grid of f's period and phase after e's dip. Only the planets'
amplitudes are solved, so each point costs one factorization. Prints the K_f offset in m/s and percent.

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/probe_kgrid.py TASK_DIR DIAG.json K_F
    "P1 P2 ..." "PH1 PH2 ..." """
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
K_F = float(sys.argv[3])
periods = [float(x) for x in sys.argv[4].split()]
phases = [float(x) for x in sys.argv[5].split()]
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
circ = lambda t, P, K, tc: -K * np.sin(2 * math.pi * (t - tc) / P)
e_true = [115.3, TC_DIP, math.sqrt(0.04) * math.cos(1.2), math.sqrt(0.04) * math.sin(1.2)]
print("K_f %.2f; rows: period; columns: phase %s" % (K_F, " ".join("%5.3f" % p for p in phases)), flush=True)
for P_f in periods:
    row = []
    for ph in phases:
        tc_f = TC_DIP + ph * P_f
        rv.y = y0 - circ(rv.t, *F_OLD) + circ(rv.t, P_f, K_F, tc_f)
        _, beta, cov, _ = rv.solve(inner + [e_true, [P_f, tc_f, 0.0, 0.0]], rv.factor(noise))
        row.append("%+5.2f(%+3.0f%%)" % (beta[6] - K_F, 100 * (beta[6] - K_F) / K_F))
    print("%6.2f d: %s   (sigma %.2f)" % (P_f, " ".join(row), math.sqrt(cov[6, 6])), flush=True)
