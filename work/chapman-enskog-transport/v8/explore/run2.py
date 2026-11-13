"""Timed run of the fast pipeline (qs2 / qmix2) for one (A, R, Lambda, T) at P, compared with run1's reference.

    QS_LNUM_C=6 QS_RM_FLOOR=6 QS_TOL_LO=1e-5 QS_TOL_HI=1e-4 python -B run2.py A R Lam T P workers kfac tag [x1 ...]
Stages are cached in v8/cache/<case>-<tag>/ so a killed run resumes; the reference is run1's brk<P>.pkl.
"""
import math
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qmix2 as qm  # noqa: E402


def main():
    A, R, Lam, T = (float(v) for v in sys.argv[1:5])
    P, workers, kfac, tag = int(sys.argv[5]), int(sys.argv[6]), float(sys.argv[7]), sys.argv[8]
    xs = [float(v) for v in sys.argv[9:]] or [0.1, 0.5, 0.9]
    L = P + 4
    case = "A%g_R%g_L%g_T%g" % (A, R, Lam, T)
    cdir = os.path.join(HERE, "..", "cache", case + "-" + tag)
    os.makedirs(cdir, exist_ok=True)
    f = lambda name: os.path.join(cdir, name)
    log = lambda s: print(s, flush=True)
    prs = qm.pairs(A, R, Lam)
    edges = qm.base_edges(T, P)
    U, W = qm.base_nodes(edges)
    log("%s %s: %d base nodes, L %d, kfac %g, %d workers; env %s" % (case, tag, U.size, L, kfac, workers, {
        k: v for k, v in os.environ.items() if k.startswith("QS_")}))
    tt = time.time()
    Qe = {}
    for pk, pr in prs.items():
        if os.path.exists(f("qe%s.npy" % pk)):
            Qe[pk] = np.load(f("qe%s.npy" % pk))
            log("pair %s: cached" % pk)
            continue
        t0 = time.time()
        res = qm.resonances(pr, kfac=kfac)
        t1 = time.time()
        Q, ph = qm.base_Q(pr, U, L, kfac=kfac, workers=workers, log=log)
        t2 = time.time()
        Qe[pk] = qm.pi_correct(pr, res, edges, U, W, Q, ph, L, T, kfac=kfac, workers=workers, log=log)
        t3 = time.time()
        np.save(f("qe%s.npy" % pk), Qe[pk])
        log("pair %s kappa^2 %.1f: %d resonances; scan %.0f s, base %.0f s, PI %.0f s" % (
            pk, pr.kap2, len(res), t1 - t0, t2 - t1, t3 - t2))
    if os.path.exists(f("brk%d.pkl" % P)):
        acc = pickle.load(open(f("brk%d.pkl" % P), "rb"))
    else:
        acc = qm.brackets(R, T, P, U, W, Qe, workers=workers, log=log)
        pickle.dump(acc, open(f("brk%d.pkl" % P), "wb"))
    log("total %.0f s (this run)" % (time.time() - tt))
    ref = os.path.join(HERE, "..", "cache", case, "brk%d.pkl" % P)
    if os.path.exists(ref):
        aref = pickle.load(open(ref, "rb"))
        for x1 in xs:
            c, r = qm.coefficients(acc, R, x1, T, P), qm.coefficients(aref, R, x1, T, P)
            log("  x1 %.2f  " % x1 + "  ".join("%s %+.3f tol" % (q[:8], (c[q] / r[q] - 1) / 2e-5) for q in c))


if __name__ == "__main__":
    main()
