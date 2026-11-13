"""Under the reference's own noise model (solve.py's RV class, built exactly as main() builds it from the draft's data
files), compare the single eccentric reading of e with the true configuration (e nearly circular plus f).

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/probe_gp.py TASK_DIR DIAG.json
TASK_DIR is the draft task folder (its environment/data and solution/solve.py are used); DIAG.json is the reference's
diagnostics from the same data (for its planets and noise). Nothing here is the oracle."""
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

vis = S.table(S.DATA / "rv_vis.txt")
nir = S.table(S.DATA / "rv_nir.txt")
tv, yv, ev = vis[:, 0], vis[:, 1], vis[:, 2]
tn, yn, en = nir[:, 0], nir[:, 1], nir[:, 2]
ha, eha = vis[:, 7], vis[:, 8]
rot = diag["rotation"]
P_rot, lam_ha, w_ha = rot["P_rot_halpha_gp"], rot["lam_halpha"], rot["w_halpha"]
lam, wq = rot["lam_dlw"], rot["w_dlw"]
# the Halpha process's amplitude and jitter are not in the diagnostics: refit them at the reported shape
_, P_rot2, lam_ha2, w_ha2, amp_ha, jit_ha = S.gp_fit_series(tv, ha, eha, [P_rot])
ha_nir = S.gp_predict(tv, ha, eha, (P_rot2, lam_ha2, w_ha2, amp_ha, jit_ha), tn)
reg = np.zeros((len(tv) + len(tn), 2))
reg[:len(tv), 0] = ha - np.mean(ha)
reg[len(tv):, 1] = ha_nir - np.mean(ha)
rv = S.RV(tv, yv, ev, tn, yn, en, (P_rot, lam, wq), regressors=reg)
nz = diag["noise"]
rv.noise = np.log([nz["jit_vis"], nz["jit_nir"], nz["h_vis"], nz["h_nir"], max(nz["h_slow"], 1e-3)])


def planet(P, tc, e, w):
    return [P, tc, math.sqrt(e) * math.cos(w), math.sqrt(e) * math.sin(w)]


def show(name, planets, lnl):
    fac = rv.factor(rv.noise)
    _, beta, cov, _ = rv.solve(planets, fac)
    parts = []
    for k, (P, tc, sc, ss) in enumerate(planets):
        parts.append("%.3f d K %.2f+-%.2f e %.2f w %+.0f" % (P, beta[2 + k], math.sqrt(cov[2 + k, 2 + k]),
                                                             sc * sc + ss * ss, math.degrees(math.atan2(ss, sc))))
    print("%-44s lnL %.2f | %s" % (name, lnl, "; ".join(parts)), flush=True)


ref = [planet(p["period"], p["tc"], p["e"], p["omega"]) for p in diag["planets"]]
inner = [q for q in ref if q[0] < 100]
e_true = planet(115.3, 2460270.842, 0.04, 1.2)
f_true = planet(56.9, 2460300.430, 0.0, 0.0)

saved = rv.noise.copy()
pl, lnl = rv.fit([list(q) for q in ref])
show("reference's four planets, refitted", pl, lnl)
single_lnl = lnl

# true nonlinear parameters for e and f, the other three as the reference has them; K solved, noise fitted
rv.noise = saved.copy()
truth = [list(q) for q in inner] + [e_true, f_true]
lnl_fixed = rv.fit_noise(truth)
show("truth for e and f held (noise fitted)", truth, lnl_fixed)

# from the truth, every planet free
pl2, lnl2 = rv.fit([list(q) for q in truth])
show("from the truth, all free", pl2, lnl2)

# e held circular at the truth's period and phase, f free: fit f alone at fixed noise, then the noise
rv.noise = saved.copy()
fac = rv.factor(rv.noise)
trial = [list(q) for q in inner] + [planet(115.3, 2460270.842, 0.0, 0.0), f_true]
trial = rv.fit_planets(trial, fac, free=[len(trial) - 1])
lnl3 = rv.fit_noise(trial)
show("e circular at the truth, f free", trial, lnl3)

# the single eccentric reading with e's eccentricity forced near zero (circular e, no f)
rv.noise = saved.copy()
circ = [list(q) for q in inner] + [planet(115.3, 2460270.842, 0.0, 0.0)]
lnl4 = rv.fit_noise(circ)
show("e circular at the truth, no f", circ, lnl4)
print("dlnL truth-held minus single eccentric: %+.2f; all-free from truth minus single: %+.2f"
      % (lnl_fixed - single_lnl, lnl2 - single_lnl))
