import sys, os, json, shutil, subprocess
sys.path.insert(0, "C:/Users/Administrator/Documents/Tango-arunufo/tasks/kater-pendulum-gravity/tests")
sys.path.insert(0, "C:/Users/Administrator/Documents/Tango-arunufo/tasks/kater-pendulum-gravity/solution")
import generate as G, solve as S, numpy as np
for seed in (1, 2, 3, 4, 5):
    G.SEED = seed
    d = f"seed{seed}"; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    G.main(d, d + "/exp.json")
    shutil.copy("data2/NOTES.md", d)
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()):
        S.main(d, d + "/out")
    r = json.load(open(d + "/out/result.json")); e = json.load(open(d + "/exp.json"))
    errs = {k: v / e["run_periods_s"][k] - 1 for k, v in r["run_periods_s"].items()}
    print(seed, "g %+.1e" % (r["g_m_s2"] / e["g_m_s2"] - 1), "k %+.1e" % (r["radius_of_gyration_m"] / e["radius_of_gyration_m"] - 1), "maxT %.1e" % max(abs(x) for x in errs.values()))
