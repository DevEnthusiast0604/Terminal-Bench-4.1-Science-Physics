import numpy as np, scatter as S
from test_scatter import chi_ode
pot = S.Kihara(0.0); sc = S.Scatter(pot)
E = 0.8001
bs = S.b_star(sc, E)
print("b* =", bs, "1 - Ec/E =", 1 - pot.E_c / E)
for f in (-3e-2, -1e-2, -3e-3, -1e-3, -1e-4, -1e-6, 1e-6, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2):
    b = bs * (1 + f)
    c1 = float(np.cos(sc.chi(np.array([b]), E))[0]); ch = float(sc.chi(np.array([b]), E)[0])
    c2 = chi_ode(b, E)
    print("f=%+.0e chi=%10.5f cos quad %.10f ode %.10f diff %.1e" % (f, ch, c1, c2, c1 - c2))
