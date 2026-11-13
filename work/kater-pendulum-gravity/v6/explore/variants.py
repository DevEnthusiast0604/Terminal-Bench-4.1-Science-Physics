import sys, math, numpy as np
sys.path.insert(0, "C:/Users/Administrator/Documents/Tango-arunufo/tasks/kater-pendulum-gravity/solution")
import solve as S
D = sys.argv[1]
truth = {"a": 1.8162959008808408, "b": 1.9617669495331866}
def run(label, patch=None, flag_ok=True):
    orig = (S.time_map, S.agm)
    if patch == "nostall":
        def tm(idx, c0, gps, sc):
            f = ((sc - c0) % 65536).astype(float); s = (gps - gps[0]).astype(float)
            A = np.vstack([s, np.ones_like(s)]).T; r, b = np.linalg.lstsq(A, f, rcond=None)[0]
            return (idx - b) / r, np.ones(len(idx), bool), r
        S.time_map = tm
    elif patch == "nominal":
        S.time_map = lambda idx, c0, gps, sc: (idx / 240.0, np.ones(len(idx), bool), 240.0)
    elif patch == "noamp":
        S.agm = lambda a, b: 1.0
    res = {}
    for rid in "a1 a2 a3 b1 b2 b3".split():
        meta, c, th, ok = S.read_run(f"{D}/runs/{rid}.csv")
        if not flag_ok: ok = np.ones_like(ok)
        gps, sc = S.read_sync(f"{D}/sync/{rid}.csv")
        res[rid] = S.analyse_run(meta, c, th, ok, gps, sc)[0]
    S.time_map, S.agm = orig
    print(label, " ".join("%s:%+.1e" % (r, v / truth[r[0]] - 1) for r, v in res.items()))
run("oracle    ")
run("no stall  ", "nostall")
run("ignore ok ", None, False)
run("no ampcorr", "noamp")
run("nominal   ", "nominal")
