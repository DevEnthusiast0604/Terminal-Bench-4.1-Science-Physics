import cProfile, pstats, numpy as np, scatter as S, time
sc = S.Scatter(S.Kihara(0.0))
orig = sc.chi
calls = {"n": 0, "pts": 0}
def counted(b, E):
    calls["n"] += 1; calls["pts"] += np.size(b)
    return orig(b, E)
sc.chi = counted
t0 = time.time(); S.Q_all(sc, 0.3, 20, 1e-9); print("Q_all E=0.3: %.2f s, chi calls %d, b points %d" % (time.time() - t0, calls["n"], calls["pts"]))
calls.update(n=0, pts=0)
t0 = time.time(); S.Q_all(sc, 3.0, 20, 1e-9); print("Q_all E=3: %.2f s, chi calls %d, b points %d" % (time.time() - t0, calls["n"], calls["pts"]))
for h in (1/16, 1/32, 1/64):
    sc2 = S.Scatter(S.Kihara(0.0), de_h=h)
    b = np.linspace(0.01, 4, 2000)
    ref = S.Scatter(S.Kihara(0.0), de_h=1/128).chi(b, 0.3)
    t0 = time.time(); c = sc2.chi(b, 0.3); dt = time.time() - t0
    print("DE h=1/%d: max |chi - chi(h=1/128)| = %.1e, %.3f s per 2000 b" % (round(1/h), np.abs(c - ref).max(), dt))
