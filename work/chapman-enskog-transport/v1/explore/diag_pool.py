import os, sys, time, traceback
import numpy as np
sys.path.insert(0, os.path.abspath("../../../../tasks/active/chapman-enskog-transport/tests"))
import ce_ref as R

_SC = None
def init():
    global _SC
    _SC = R.Scatter(R.Kihara(0.5), de_h=1/32)

def work(a):
    i, e = a
    with open("diag/w%d.txt" % os.getpid(), "a") as fh:
        fh.write("start %d %.17g %.0f\n" % (i, e, time.time()))
    try:
        q = R.Q_all(_SC, e, 14, 1e-11)
        out = (i, q, None)
    except BaseException as exc:
        out = (i, None, "%s: %s" % (type(exc).__name__, exc))
    with open("diag/w%d.txt" % os.getpid(), "a") as fh:
        fh.write("done %d %.0f %s\n" % (i, time.time(), out[2]))
    return out

if __name__ == "__main__":
    from concurrent.futures import ProcessPoolExecutor
    pot = R.Kihara(0.5)
    E, w = R.e_nodes(pot.E_c, 3e-5 * 1.0067, 1.5e4 * 0.9933, width=0.5, n_uni=16, K=14, n_gr=12)
    E, w = R.e_nodes(pot.E_c, 1e-4 * 0.3, 150.0 * 100, width=0.5, n_uni=16, K=14, n_gr=12)
    lo, hi = int(sys.argv[1]), int(sys.argv[2])
    t0 = time.time()
    errs = []
    with ProcessPoolExecutor(6, initializer=init) as ex:
        for i, q, err in ex.map(work, [(i, float(E[i])) for i in range(lo, min(hi, len(E)))], chunksize=4):
            if err:
                errs.append((i, E[i], err))
    print("energies %d..%d of %d: %.0f s, errors %s" % (lo, hi, len(E), time.time() - t0, errs[:5]))
