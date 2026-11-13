"""v2 probe: internal field, magnetic-interaction strength, spectra against H and against B (no reference run)."""
import importlib.util, math, sys, time
from pathlib import Path
import numpy as np
TASK = Path("tasks/active/dhva-fermi-surface")
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod); return mod
G = load("gen", TASK / "tests" / "generate.py")
S = G.load_solver()
print("N %.5f  V %.4e m3  K %.5e T/unit" % (S.DEMAG, S.VOLUME, S.K_FIELD))
H = G.field_grid()
for T in (0.35, 2.4, 9.0):
    t0 = time.time()
    B = G.internal_field(H, T, S.K_FIELD)
    osc = sum(G.lk_moment(B, T, o) for o in G.ORBITS)
    a = S.K_FIELD * np.gradient(osc, B)
    k = int(np.argmax(np.abs(a)))
    print("T %5.2f: B/H at 5, 20, 35 T: %.5f %.5f %.5f; max K dm~/dB %.3f at %.1f T (%.2f s)"
          % (T, B[0] / H[0], B[7500] / H[7500], B[-1] / H[-1], abs(a[k]), H[k], time.time() - t0))
    for lo, hi in ((6, 14), (14, 22), (22, 35)):
        sel = (H >= lo) & (H <= hi)
        print("     max |a| over %d-%d T: %.3f" % (lo, hi, np.max(np.abs(a[sel]))))
sw = G.build(np.random.default_rng(G.SEED))
for frame in ("internal", "applied", "oscillatory"):
    rd = G.as_read(sw, S, frame)
    for k, win in ((0, S.W_SEARCH), (0, S.W_HIGH), (9, S.W_HOT)):
        pk = S.peaks_of(rd[k], win)
        print("%-11s %5.2f K %s: %s" % (frame, rd[k]["T"], win, ", ".join("%.1f (%.0f)" % (p["f"], p["snr"]) for p in pk)))
