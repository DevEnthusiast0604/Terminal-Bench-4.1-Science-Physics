"""How much the shape resonances of one pair move the thermal averages I(l, s; T) = int e^-x x^(s+1) Q^(l)(xT) dx,
and how far composite Gauss grids of fixed panel width in ln E (8 nodes per panel) are from the resolved value.

    python -B res2.py A Lam mu like|unlike out.pkl
"""
import math
import os
import pickle
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import qs  # noqa: E402

A, Lam, mu, kind, out = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), sys.argv[4], sys.argv[5]
like = kind == "like"
P = qs.Pair(A, Lam, mu)
Lb = qs.barrier_lmax(P)
t0 = time.time()
data = qs.scan(P, 1e-6, 3.0, Lb + 2)
res = qs.find_resonances(data)
if like:
    res = [r for r in res if r["l"] % 2 == 0]
print("%d resonances (%.0f s)" % (len(res), time.time() - t0), flush=True)
L = 4
Ts = [0.25, 0.5, 1.0]
Elo, Emid, Ehi = 1e-5 * min(Ts), 3.0, 40.0 * max(Ts)
KEYS = ((1, 1), (2, 2), (1, 2), (2, 3))


def integrals(E, w, Q):
    rows = []
    for T in Ts:
        x = E / T
        for (l, s_) in KEYS:
            rows.append(np.sum(w * np.exp(-x) * x ** (s_ + 1) * Q[:, l]) / T)
    return np.array(rows)


def lin(a, b, width):
    return np.linspace(math.log(a), math.log(b), int(math.ceil(math.log(b / a) / width)) + 1)


t0 = time.time()
Eh, wh = qs.nodes_from(np.exp(lin(Emid, Ehi, 0.1)), 8)
Qh = qs.Q_at(P, Eh, L, like)
high = integrals(Eh, wh, Qh)
print("high part: %d nodes (%.0f s)" % (len(Eh), time.time() - t0), flush=True)
low = {}
for width in (0.2, 0.1, 0.05):
    t0 = time.time()
    E, w = qs.nodes_from(np.exp(lin(Elo, Emid, width)), 8)
    low[width] = integrals(E, w, qs.Q_at(P, E, L, like))
    print("naive width %.3f: %d nodes (%.0f s)" % (width, len(E), time.time() - t0), flush=True)
t0 = time.time()
E, w = qs.nodes_from(qs.panels(lin(Elo, Emid, 0.1), res, T=min(Ts)), 8)
Q = qs.Q_at(P, E, L, like)
ref = integrals(E, w, Q) + high
print("resolved: %d nodes (%.0f s)" % (len(E), time.time() - t0), flush=True)
for it, T in enumerate(Ts):
    print("T %.2f" % T)
    for j, (l, s_) in enumerate(KEYS):
        i = 4 * it + j
        print("  I(%d,%d) %.10f  naive rel err (width .2 .1 .05): %s" % (l, s_, ref[i], " ".join(
            "%+.2e" % ((low[wd][i] + high[i] - ref[i]) / ref[i]) for wd in (0.2, 0.1, 0.05))))
pickle.dump(dict(res=res, E=E, w=w, Q=Q, Eh=Eh, wh=wh, Qh=Qh), open(out, "wb"))
