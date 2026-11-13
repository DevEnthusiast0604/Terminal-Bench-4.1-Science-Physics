import math, numpy as np
exec(open(__file__.replace("design6.py", "design5.py")).read().split("# exact crossing")[0])
rng = np.random.default_rng(1)
for X in ([0.70, 0.75, 0.84], [0.72, 0.765, 0.82], [0.66, 0.77, 0.88]):
    X = np.array(X)
    Ta = np.array([periods(x)[0] for x in X]); Tb = np.array([periods(x)[1] for x in X])
    def g_edge_a(Ta, X):
        # P Ta^2 + Q Ta^2 x - A0 = x^2 ; g = 4 pi^2 Q
        M = np.column_stack([Ta ** 2, Ta ** 2 * X, -np.ones_like(X)])
        P, Q, A0 = np.linalg.solve(M, X ** 2)
        return 4 * math.pi ** 2 * Q
    def g_edge_b(Tb, X):
        y = L - X
        M = np.column_stack([Tb ** 2, Tb ** 2 * y, -np.ones_like(y)])
        P, Q, C0 = np.linalg.solve(M, y ** 2)
        return 4 * math.pi ** 2 * Q
    def g_joint(Ta, Tb, X):
        # both edges, shared Q=g/4pi^2 ; a: P_a Ta^2 + Q Ta^2 x - A0 = x^2 ; b: P_b Tb^2 + Q Tb^2 y - C0 = y^2
        y = L - X
        M = np.zeros((6, 5)); rhs = np.concatenate([X ** 2, y ** 2])
        M[:3, 0] = Ta ** 2; M[:3, 2] = Ta ** 2 * X; M[:3, 3] = -1
        M[3:, 1] = Tb ** 2; M[3:, 2] = Tb ** 2 * y; M[3:, 4] = -1
        sol, *_ = np.linalg.lstsq(M, rhs, rcond=None)
        return 4 * math.pi ** 2 * sol[2]
    print("positions", X, "exact: g_a %.7f g_b %.7f joint %.7f" % (g_edge_a(Ta, X), g_edge_b(Tb, X), g_joint(Ta, Tb, X)))
    errs = {"a": [], "b": [], "joint": [], "crossq": []}
    for _ in range(400):
        ta = Ta * (1 + rng.normal(0, 1.5e-5, 3)); tb = Tb * (1 + rng.normal(0, 1.5e-5, 3))
        errs["a"].append(g_edge_a(ta, X) / G - 1); errs["b"].append(g_edge_b(tb, X) / G - 1); errs["joint"].append(g_joint(ta, tb, X) / G - 1)
    for k, v in errs.items():
        if v:
            print("   period noise 1.5e-5 -> %s g rms err %.1e" % (k, np.std(v)))
