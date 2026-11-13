"""Candidate survey with the fast pipeline (qs2 / qmix2): for each (A, R, Lambda, T), the resonances, the base cross
sections, the product-integration correction, and the brackets with and without it (the naive grid); then the
naive error in tolerances (2e-5 relative) at several x1, and the stage times.

    QS_LNUM_C=6 QS_RM_FLOOR=6 QS_TOL_LO=1e-5 QS_TOL_HI=1e-4 python -B run3.py workers P kfac tag A,R,Lam,T ...
Caches in v8/cache/<case>-<tag>/ (resonances, base Q, PI Q, brackets), so a killed run resumes.
"""
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qmix2 as qm  # noqa: E402

XS = (0.05, 0.3, 0.6, 0.95)


def run(A, R, Lam, T, P, workers, kfac, tag, log):
    L = P + 4
    case = "A%g_R%g_L%g_T%g" % (A, R, Lam, T)
    cdir = os.path.join(HERE, "..", "cache", case + "-" + tag)
    os.makedirs(cdir, exist_ok=True)
    f = lambda name: os.path.join(cdir, name)
    prs = qm.pairs(A, R, Lam)
    edges = qm.base_edges(T, P)
    U, W = qm.base_nodes(edges)
    times, Qb, Qe, allres = {}, {}, {}, {}
    for pk, pr in prs.items():
        if os.path.exists(f("pair%s.pkl" % pk)):
            allres[pk], Qb[pk], Qe[pk], times[pk] = pickle.load(open(f("pair%s.pkl" % pk), "rb"))
            continue
        t0 = time.time()
        res = qm.resonances(pr, kfac=kfac)
        t1 = time.time()
        Q, ph = qm.base_Q(pr, U, L, kfac=kfac, workers=workers, log=lambda s: None)
        t2 = time.time()
        q = qm.pi_correct(pr, res, edges, U, W, Q, ph, L, T, kfac=kfac, workers=workers, log=lambda s: None)
        t3 = time.time()
        allres[pk], Qb[pk], Qe[pk], times[pk] = res, Q, q, (t1 - t0, t2 - t1, t3 - t2)
        pickle.dump((res, Q, q, times[pk]), open(f("pair%s.pkl" % pk), "wb"))
    accs = {}
    for name, Qs in (("brk", Qe), ("naive", Qb)):
        fn = f("%s%d.pkl" % (name, P))
        if os.path.exists(fn):
            accs[name], tb = pickle.load(open(fn, "rb"))
        else:
            t0 = time.time()
            accs[name] = qm.brackets(R, T, P, U, W, Qs, workers=workers, log=lambda s: None)
            tb = time.time() - t0
            pickle.dump((accs[name], tb), open(fn, "wb"))
        times[name] = tb
    log("%s (P %d, %d nodes): pairs kappa^2 %s" % (case, P, U.size, " ".join(
        "%s %.0f" % (pk, pr.kap2) for pk, pr in prs.items())))
    for pk in prs:
        rs = sorted(allres[pk], key=lambda r: r["Gamma"] / r["E"])
        log("  %s: %d resonances, Gamma/E %s; scan/base/PI %s s" % (
            pk, len(rs), " ".join("l%d@%.3g:%.0e" % (r["l"], r["E"], r["Gamma"] / r["E"]) for r in rs),
            "/".join("%.0f" % t for t in times[pk])))
    log("  brackets %.0f s; total %.0f s" % (times["brk"], sum(sum(times[pk]) for pk in prs) + times["brk"]))
    for x1 in XS:
        c, n = qm.coefficients(accs["brk"], R, x1, T, P), qm.coefficients(accs["naive"], R, x1, T, P)
        log("  x1 %.2f naive-PI in tol: " % x1 + "  ".join("%s %+.2f" % (q[:6], (n[q] / c[q] - 1) / 2e-5) for q in c)
            + "  | " + " ".join("%.6g" % c[q] for q in c))


def main():
    workers, P, kfac, tag = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
    log = lambda s: print(s, flush=True)
    for spec in sys.argv[5:]:
        A, R, Lam, T = (float(v) for v in spec.split(","))
        run(A, R, Lam, T, P, workers, kfac, tag, log)


if __name__ == "__main__":
    main()
