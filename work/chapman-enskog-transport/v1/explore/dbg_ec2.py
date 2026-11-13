import numpy as np, scatter as S
sc = S.Scatter(S.Kihara(0.0))
E = 0.81
ref = S.Q_all(sc, E, 4, 640, 240)
for ns, nv in ((40, 30), (80, 30), (40, 240), (160, 30), (320, 30), (320, 240)):
    q = S.Q_all(sc, E, 4, ns, nv)
    print(ns, nv, "%.2e" % np.abs(q / ref - 1).max())
# integrand along the inner and outer pieces
bs = S.b_star(sc, E)
for s in (0.5, 1, 2, 3, 4, 5, 6, 8, 10, 15, 20):
    bi, bo = bs * (1 - np.exp(-s)), bs * (1 + np.exp(-s))
    print("s=%5.1f chi_in %9.4f chi_out %9.4f" % (s, sc.chi(np.array([bi]), E)[0], sc.chi(np.array([bo]), E)[0]))
