import sys, numpy as np, scatter as S
sc = S.Scatter(S.Kihara(float(sys.argv[1])))
Ec = sc.p.E_c
print("E_c =", Ec)
rows = []
for d in (-3e-1, -1e-1, -3e-2, -1e-2, -3e-3, -1e-3, -1e-4, -1e-5, 0.0, 1e-5, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1):
    E = Ec * (1 + d) if d != 0 else Ec * (1 - 1e-9)
    q = S.Q_all(sc, E, 2, 1e-10)
    rows.append((d, q))
    print("d=%+.0e  Q1 %.11f  Q2 %.11f" % (d, q[0], q[1]), flush=True)
