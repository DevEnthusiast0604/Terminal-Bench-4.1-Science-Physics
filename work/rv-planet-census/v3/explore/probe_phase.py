"""v3 feasibility probe: an inner planet f near 2:1 inside e, with e nearly circular.

pass@8 (Astra 6, 4 of 4 solved) and pass@3 (Sol 6.1) all read the ~57 d power as e's eccentric harmonic without testing
a second planet. If the 57 d power is a planet and e is nearly circular, a single eccentric orbit for e is the tempting
wrong census. This probe measures, on the generator's own visits, activity and noise, how strongly the velocities
prefer the right model (e + f) over the tempting one (e eccentric alone), and where the tempting orbit puts e's
conjunction and transit duration against the single dip. The activity is either removed exactly (the planets'
evidence alone) or left in and regressed on the Halpha index (a crude activity model). Nothing here is the oracle.

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/probe_phase.py P_f K_f PHASE [PHASE ...]
The same as probe_pair.py at chosen phases of f (fractions of its period after the dip)."""
import importlib.util
import math
import sys

import numpy as np
from scipy.optimize import least_squares

spec = importlib.util.spec_from_file_location("gen", "tasks/active/rv-planet-census/tests/generate.py")
G = importlib.util.module_from_spec(spec)
spec.loader.exec_module(G)

P_F = float(sys.argv[1]) if len(sys.argv) > 1 else 56.9
K_F = float(sys.argv[2]) if len(sys.argv) > 2 else 1.6
E_E = 0.04
TC_DIP = 2460270.842

rng = np.random.default_rng(G.SEED)
d = G.build(rng)                       # the v1 system: its visits, activity and noise draws
tv, tn = d["tv"], d["tn"]
old_v = sum(G.rv_planet(tv, p) for p in G.PLANETS)
old_n = sum(G.rv_planet(tn, p) for p in G.PLANETS)
sig_v = np.sqrt(d["ev"] ** 2 + G.VIS_JITTER ** 2)
sig_n = np.sqrt(d["en"] ** 2 + G.NIR_JITTER ** 2)
t = np.r_[tv, tn]
inst = np.r_[np.zeros(len(tv)), np.ones(len(tn))]
sig = np.r_[sig_v, sig_n]
ha = np.r_[d["ha"] - d["ha"].mean(), np.zeros(len(tn))]

base = {p["name"]: dict(p) for p in G.PLANETS}


def system(tc_f):
    ps = [dict(base["d"]), dict(base["b"]), dict(base["c"]), dict(base["e"])]
    ps[3]["e"], ps[3]["w"] = E_E, 1.2
    ps.append({"name": "f", "P": P_F, "K": K_F, "e": 0.0, "w": 0.0, "tc": tc_f, "R": None, "b": None})
    return ps


def rv_circ(tt, P, K, tc):
    return -K * np.sin(2 * math.pi * (tt - tc) / P)


def rv_ecc(tt, P, K, tc, ec, es):
    e = math.hypot(ec, es)
    w = math.atan2(es, ec)
    return G.rv_planet(tt, {"P": P, "K": K, "e": e, "w": w, "tc": tc})


def model(v, n_f):
    """v: offsets (2), Halpha slope, d b c circular (P K tc each), e eccentric (P K tc ec es), f circular if n_f."""
    out = np.where(inst == 0, v[0], v[1]) + v[2] * ha
    k = 3
    for _ in range(3):
        out = out + rv_circ(t, *v[k:k + 3])
        k += 3
    out = out + rv_ecc(t, *v[k:k + 5])
    k += 5
    if n_f:
        out = out + rv_circ(t, *v[k:k + 3])
    return out


def fit(y, start, n_f):
    lo = np.full(len(start), -np.inf)
    hi = np.full(len(start), np.inf)
    lo[3 + 9 + 3:3 + 9 + 5], hi[3 + 9 + 3:3 + 9 + 5] = -0.9, 0.9
    r = least_squares(lambda v: (y - model(v, n_f)) / sig, start, bounds=(lo, hi), x_scale="jac", max_nfev=4000)
    return r


def conj_and_rho(P, tc, ec, es):
    e = math.hypot(ec, es)
    w = math.atan2(es, ec)
    rho = math.sqrt(1 - e * e) / (1 + e * math.sin(w))
    n = round((TC_DIP - tc) / P)
    return tc + n * P, e, w, rho


def run(tc_f, with_activity):
    ps = system(tc_f)
    new_v = sum(G.rv_planet(tv, p) for p in ps)
    new_n = sum(G.rv_planet(tn, p) for p in ps)
    yv = d["rv_v"] - old_v + new_v
    yn = d["rv_n"] - old_n + new_n
    if not with_activity:
        yv = yv - d["act_v"]["rv_vis"]
        yn = yn - d["act_n"]["rv_nir"]
    y = np.r_[yv, yn]
    pv = []
    for nm in ("d", "b", "c"):
        p = base[nm]
        pv += [p["P"], p["K"], p["tc"] if nm != "c" else p["tc"]]
    pe = base["e"]
    start_pair = [G.VIS_OFFSET, G.NIR_OFFSET, 0.0] + pv + [pe["P"], pe["K"], pe["tc"], 0.0, 0.0] + [P_F, K_F, tc_f]
    r2 = fit(y, start_pair, True)
    best1 = None
    for w0 in np.linspace(0, 2 * math.pi, 8, endpoint=False):
        start = [G.VIS_OFFSET, G.NIR_OFFSET, 0.0] + pv + [pe["P"], pe["K"], pe["tc"], 0.45 * math.cos(w0), 0.45 * math.sin(w0)]
        r1 = fit(y, start, False)
        if best1 is None or r1.cost < best1.cost:
            best1 = r1
    c1, c2 = 2 * best1.cost, 2 * r2.cost
    v1 = best1.x
    tcx, e1, w1, rho = conj_and_rho(v1[12], v1[14], v1[15], v1[16])
    # the conjunction's spread from the Jacobian (one planet's tc)
    J = best1.jac
    try:
        cov = np.linalg.inv(J.T @ J)
        stc = math.sqrt(cov[14, 14])
    except np.linalg.LinAlgError:
        stc = float("nan")
    v2 = r2.x
    tc2, e2, w2, rho2 = conj_and_rho(v2[12], v2[14], v2[15], v2[16])
    return dict(c1=c1, c2=c2, e1=e1, w1=w1, rho1=rho, tc1=tcx, stc1=stc, K1=v1[13], P1=v1[12],
                e2=e2, rho2=rho2, tc2=tc2, Kf=v2[18], Pf=v2[17], Ke2=v2[13], P2=v2[12])


print("f at %.3f d (e's half period %.3f d), K_f %.2f m/s; e circular-ish (e %.2f)" % (P_F, base["e"]["P"] / 2, K_F, E_E))
rho_true = math.sqrt(1 - E_E ** 2) / (1 + E_E * math.sin(1.2))
need = rho_true * math.sqrt((1 + 0.0402) ** 2 - 0.42 ** 2)   # the dip's chord times speed factor (truth)
for with_act in (False, True):
    print("activity %s:" % ("left in, Halpha regressed" if with_act else "removed exactly"))
    for frac in [float(x) for x in sys.argv[3:]]:
        tc_f = TC_DIP + frac * P_F
        r = run(tc_f, with_act)
        bmax = "none" if r["rho1"] * 1.0402 < need else "%.2f" % math.sqrt(max(0.0, 1.0402 ** 2 - (need / r["rho1"]) ** 2))
        print("  f phase %.3f: chi2 single-eccentric %.1f, pair %.1f, delta %.1f | single: P %.2f K %.2f e %.2f w %+4.0f deg,"
              " conjunction %+.1f +- %.1f d from the dip, duration factor %.2f (b to match: %s) | pair: P_f %.2f K_f %.2f, e's e %.2f,"
              " conjunction %+.1f d" % (frac, r["c1"], r["c2"], r["c1"] - r["c2"], r["P1"], r["K1"], r["e1"],
                                         math.degrees(r["w1"]), r["tc1"] - TC_DIP, r["stc1"], r["rho1"], bmax,
                                         r["Pf"], r["Kf"], r["e2"], r["tc2"] - TC_DIP), flush=True)
