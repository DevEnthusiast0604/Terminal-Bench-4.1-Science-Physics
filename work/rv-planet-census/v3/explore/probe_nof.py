"""Without planet f: does the star's activity alone give the nearly circular e a spurious eccentricity in the
reference's own model? The draft data hold f at (56.9 d, 1.8 m/s, tc 2460300.430); it is removed exactly from the
velocities (f adds no random draw). e is fitted free from several eccentric starts and circular, the noise refitted.

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/probe_nof.py TASK_DIR DIAG.json [E W]
E W: e's true eccentricity and omega in the draft data (default 0.04 1.2), used for the duration factor."""
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
E_T, W_T = (float(sys.argv[3]), float(sys.argv[4])) if len(sys.argv) > 4 else (0.04, 1.2)
TC_DIP = 2460270.842

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
fsig = lambda t: -1.8 * np.sin(2 * math.pi * (t - 2460300.430) / 56.9)
rv = S.RV(tv, yv - fsig(tv), ev, tn, yn - fsig(tn), en, (rot["P_rot_halpha_gp"], rot["lam_dlw"], rot["w_dlw"]),
          regressors=reg)
nz = diag["noise"]
start_noise = np.log([nz["jit_vis"], nz["jit_nir"], nz["h_vis"], nz["h_nir"], max(nz["h_slow"], 1e-3)])


def planet(P, tc, e, w):
    return [P, tc, math.sqrt(e) * math.cos(w), math.sqrt(e) * math.sin(w)]


inner = [planet(p["period"], p["tc"], p["e"], p["omega"]) for p in diag["planets"] if p["period"] < 100]
rho = lambda e, w: math.sqrt(1 - e * e) / (1 + e * math.sin(w))
k = 2.95 * 6.3781e6 / (0.672 * 6.957e8)
results = []
for name, e0, w0 in [("circular start", 0.0, 0.0)] + [("start e 0.25 w %+.0f" % math.degrees(w), 0.25, w)
                                                     for w in np.linspace(-math.pi, math.pi, 6, endpoint=False)]:
    rv.noise = start_noise.copy()
    pl, lnl = rv.fit(inner + [planet(115.3, TC_DIP, e0, w0)])
    P, tc, sc, ss = pl[3]
    e, w = sc * sc + ss * ss, math.atan2(ss, sc)
    _, beta, _, _ = rv.solve(pl, rv.factor(rv.noise))
    n = round((TC_DIP - tc) / P)
    fac = rho(e, w) / rho(E_T, W_T)
    chord = math.sqrt((1 + k) ** 2 - 0.42 ** 2) / fac
    b1 = "none" if chord > 1 + k else "%.2f" % math.sqrt((1 + k) ** 2 - chord ** 2)
    print("%-22s lnL %.2f | e: P %.3f K %.2f e %.3f w %+.0f, conj %+.2f d from the dip, duration x%.2f, b to match %s"
          % (name, lnl, P, beta[5], e, math.degrees(w), tc + n * P - TC_DIP, fac, b1), flush=True)
    results.append(lnl)
# e held circular: only its period and phase free (fit with e fixed by refitting from a circular start each round)
rv.noise = start_noise.copy()
pl = inner + [planet(115.3, TC_DIP, 0.0, 0.0)]
for _ in range(3):
    fac0 = rv.factor(rv.noise)
    pl = rv.fit_planets(pl, fac0, free=[0, 1, 2])
    lnl_c = rv.fit_noise(pl)
print("e held circular at the truth's period and phase: lnL %.2f; best free minus this %+.2f"
      % (lnl_c, max(results) - lnl_c), flush=True)
