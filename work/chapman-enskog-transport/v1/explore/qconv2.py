"""Q^(l)(E) with the adaptive rule at two tolerances (author's prototype)."""
import sys, time
import numpy as np
import scatter as S
sc = S.Scatter(S.Kihara(float(sys.argv[1])))
for E in (0.01, 0.3, 0.79, 0.8001, 0.81, 0.9, 3.0, 50.0, 500.0):
    t0 = time.time(); q1 = S.Q_all(sc, E, 6, 1e-9); t1 = time.time(); q2 = S.Q_all(sc, E, 6, 1e-12); t2 = time.time()
    print("E=%-8g Q %s | 1e-9 vs 1e-12: %.1e (%.2f s, %.2f s)" % (E, " ".join("%.10f" % x for x in q2),
          np.abs(q1 / q2 - 1).max(), t1 - t0, t2 - t1), flush=True)
