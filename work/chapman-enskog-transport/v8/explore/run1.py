"""Staged exploration run for one (A, R, Lambda, T): resonances, base Q, product integration, brackets, coefficients.

    python -B run1.py A R Lam T P stage [x1 ...]
stage: res | base<pair> | pi<pair> | brk | brknaive | coef. Caches in v8/cache/<tag>/; the base grid and the
cross sections (Legendre orders 0..LQ-1) are those of P_GRID, so every P <= P_GRID reuses them.
"""
import math
import os
import pickle
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import qmix  # noqa: E402


def main():
    A, R, Lam, T, P = (float(v) for v in sys.argv[1:5]) + (int(sys.argv[5]),) if False else (
        float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5]))
    stage = sys.argv[6]
    P_GRID, LQ = 32, 36
    tag = "A%g_R%g_L%g_T%g" % (A, R, Lam, T)
    cdir = os.path.join(HERE, "..", "cache", tag)
    os.makedirs(cdir, exist_ok=True)
    f = lambda name: os.path.join(cdir, name)
    prs = qmix.pairs(A, R, Lam)
    L = LQ
    edges = qmix.base_edges(T, P_GRID)
    U, W = qmix.base_nodes(edges)
    t0 = time.time()
    if stage == "res":
        out = {}
        for pk, pr in prs.items():
            t1 = time.time()
            out[pk] = qmix.resonances(pr)
            print("pair %s kappa^2 %.2f: %d resonances (%.0f s)" % (pk, pr.kap2, len(out[pk]), time.time() - t1), flush=True)
            for r in out[pk]:
                print("    l %3d E %.6f Gamma %.3e Gamma/T %.2e" % (r["l"], r["E"], r["Gamma"], r["Gamma"] / T))
        pickle.dump(out, open(f("res.pkl"), "wb"))
    elif stage.startswith("base"):
        pk = stage[4:]
        Q, ph = qmix.base_Q(prs[pk], U, L)
        pickle.dump((Q, ph), open(f("base%s.pkl" % pk), "wb"))
    elif stage.startswith("pi"):
        pk = stage[2:]
        res = pickle.load(open(f("res.pkl"), "rb"))[pk]
        Q, ph = pickle.load(open(f("base%s.pkl" % pk), "rb"))
        Qe = qmix.pi_correct(prs[pk], res, edges, U, W, Q, ph, L, T)
        np.save(f("qe%s.npy" % pk), Qe)
    elif stage in ("brk", "brknaive"):
        Qs = {}
        for pk in prs:
            Qs[pk] = (np.load(f("qe%s.npy" % pk)) if stage == "brk" else pickle.load(open(f("base%s.pkl" % pk), "rb"))[0])
        acc = qmix.brackets(R, T, P, U, W, Qs)
        pickle.dump(acc, open(f("%s%d.pkl" % (stage, P)), "wb"))
    elif stage == "direct":
        jobs = []
        allres = pickle.load(open(f("res.pkl"), "rb"))
        for pk in prs:
            Q, ph = pickle.load(open(f("base%s.pkl" % pk), "rb"))
            jobs += qmix.direct_jobs(prs[pk], pk, allres[pk], edges, U, W, Q, ph, L, T)
        acc = qmix.brackets_jobs(R, P, jobs)
        pickle.dump(acc, open(f("direct%d.pkl" % P), "wb"))
    elif stage == "coef":
        xs = [float(v) for v in sys.argv[7:]] or [0.5]
        for name in ("brk", "brknaive", "direct"):
            if not os.path.exists(f("%s%d.pkl" % (name, P))):
                continue
            acc = pickle.load(open(f("%s%d.pkl" % (name, P)), "rb"))
            print(name)
            for x1 in xs:
                rows = {p: qmix.coefficients(acc, R, x1, T, p) for p in range(4, P + 1, 4)}
                for q in qmix.QUANTITIES:
                    ref = rows[P][q]
                    print("  x1 %.3f %-26s P%d %.10g | rel diff of P-4k:" % (x1, q, P, ref),
                          " ".join("%+.1e" % ((rows[p][q] - ref) / ref) for p in range(4, P, 4)))
    print("stage %s done in %.0f s" % (stage, time.time() - t0))


if __name__ == "__main__":
    main()
