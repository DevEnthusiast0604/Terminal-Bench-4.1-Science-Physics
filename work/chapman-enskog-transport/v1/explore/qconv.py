"""Convergence of Q^(l)(E) with the panel counts (author's prototype)."""
import sys, time
import numpy as np
import scatter as S
A = float(sys.argv[1])
sc = S.Scatter(S.Kihara(A))
for E in (0.01, 0.3, 0.79, 0.8001, 0.81, 3.0, 50.0, 500.0):
    t0 = time.time()
    q1 = S.Q_all(sc, E, 6, 40, 30)
    t1 = time.time()
    q2 = S.Q_all(sc, E, 6, 80, 60)
    q3 = S.Q_all(sc, E, 6, 160, 120)
    print("E=%-8g Q1..6 %s | rel diff 40/80: %.1e 80/160: %.1e (%.2f s per call)" % (
        E, " ".join("%.9f" % x for x in q3), np.abs(q1 / q3 - 1).max(), np.abs(q2 / q3 - 1).max(), t1 - t0), flush=True)
