"""Thermal collision integrals and exact Chapman-Enskog transport coefficients (author's prototype).

Q^(l)(E) is sampled once on Gauss-Legendre panels in u = ln E (split at the critical orbiting energy E_c and graded
geometrically toward it); every temperature reuses the same samples:
    I(l, s; T*) = int_0^inf exp(-x) x^(s+1) Q^(l)(x T*) dx = int exp(-x) x^(s+2) Q^(l)(E) du,   x = E / T*
with Q in units of pi sigma^2. Omega^(l,s) of brackets.py is (pi sigma^2 / 2) I(l, s).
"""
import json
import os
import sys
import time
from fractions import Fraction

import mpmath as mp
import numpy as np
from numpy.polynomial.legendre import leggauss

import scatter as S


def e_nodes(Ec, Elo, Ehi, width=0.5, n_uni=16, K=14, n_gr=10):
    """Nodes E and weights w for int g(E) d(ln E) over (Elo, Ehi), with E_c a panel boundary and panels graded toward
    it: delta = E / E_c - 1 in +-[2^-(k+1), 2^-k], k = 1..K, plus the two innermost panels touching E_c."""
    uc = np.log(Ec)
    edges_lo = [uc + np.log1p(-2.0 ** -k) for k in range(1, K + 1)] + [uc]
    edges_hi = [uc] + [uc + np.log1p(2.0 ** -k) for k in range(K, 0, -1)]
    graded = sorted(set(edges_lo + edges_hi))
    a, b = np.log(Elo), np.log(Ehi)
    left = np.linspace(a, graded[0], max(1, int(np.ceil((graded[0] - a) / width))) + 1)
    right = np.linspace(graded[-1], b, max(1, int(np.ceil((b - graded[-1]) / width))) + 1)
    us, ws = [], []
    for edges, n in ((left, n_uni), (np.array(graded), n_gr), (right, n_uni)):
        xg, wg = leggauss(n)
        for lo, hi in zip(edges[:-1], edges[1:]):
            us.append(0.5 * (lo + hi) + 0.5 * (hi - lo) * xg)
            ws.append(0.5 * (hi - lo) * wg)
    u = np.concatenate(us)
    return np.exp(u), np.concatenate(ws)


_SC = None


def _init(A, h):
    global _SC
    _SC = S.Scatter(S.Kihara(A), de_h=h)


def _work(args):
    i, e, L, rel = args
    return i, S.Q_all(_SC, e, L, rel)


def sample_Q(A, h, E, L, rel, cache, workers=6, budget=520.0):
    """Q^(l)(E) for l = 1..L at every node, in a process pool; progress is kept in the cache file so that a run cut
    short (budget seconds) resumes where it stopped. Returns None while incomplete."""
    from concurrent.futures import ProcessPoolExecutor, wait, FIRST_COMPLETED
    Q = np.full((len(E), L), np.nan)
    if os.path.exists(cache):
        z = np.load(cache)
        if z["E"].shape == E.shape and np.array_equal(z["E"], E) and z["Q"].shape[1] >= L:
            Q = z["Q"][:, :L].copy()
    todo = [int(i) for i in np.where(np.isnan(Q[:, 0]))[0]]
    if not todo:
        return Q
    t0, last = time.time(), time.time()
    print("  %d of %d energies to sample" % (len(todo), len(E)), flush=True)
    with ProcessPoolExecutor(workers, initializer=_init, initargs=(A, h)) as ex:
        pending = {ex.submit(_work, (i, float(E[i]), L, rel)) for i in todo}
        while pending:
            done, pending = wait(pending, timeout=5.0, return_when=FIRST_COMPLETED)
            for f in done:
                i, q = f.result()
                Q[i] = q
            if time.time() - last > 30 or not pending:
                np.savez(cache, E=E, Q=Q)
                last = time.time()
                print("  %d / %d sampled (%.0f s)" % (int(np.sum(~np.isnan(Q[:, 0]))), len(E), time.time() - t0),
                      flush=True)
            if time.time() - t0 > budget and pending:
                for f in pending:
                    f.cancel()
                break
    np.savez(cache, E=E, Q=Q)
    return None if np.isnan(Q[:, 0]).any() else Q


def thermal(Ts, E, w, Q, smax):
    """I[t, l-1, s] for s = 0..smax."""
    out = np.zeros((len(Ts), Q.shape[1], smax + 1))
    for t, T in enumerate(Ts):
        x = E / T
        lx = np.log(x)
        for s in range(smax + 1):
            k = w * np.exp(-x + (s + 2) * lx)
            out[t, :, s] = k @ Q
    return out


def load_coefs(P, path):
    if os.path.exists(path):
        with open(path) as fh:
            ser = json.load(fh)
        res = {prop: {tuple(map(int, pq.split(","))): {(l, s): Fraction(c) for l, s, c in v} for pq, v in d.items()}
               for prop, d in ser.items()}
        if max(p for p, q in res["visc"]) >= P:
            return res
    import brackets as B
    res = B.all_coefs(P)
    ser = {prop: {"%d,%d" % pq: [[l, s, str(c)] for (l, s), c in sorted(d.items())] for pq, d in v.items()}
           for prop, v in res.items()}
    with open(path, "w", newline="\n") as fh:
        json.dump(ser, fh)
    return res


def factors(coefs, I, P, dps=40):
    """f^(M) for M = 1..P (M Sonine terms) per property, from I[l-1, s] (one temperature); mpmath linear algebra."""
    mp.mp.dps = dps
    om = lambda l, s: mp.mpf(float(I[l - 1, s])) / 2
    out = {}
    for prop, lo in (("visc", 0), ("cond", 1), ("diff", 0)):
        d = coefs[prop]
        n = P
        idx = list(range(lo, lo + n))
        H = mp.matrix(n, n)
        for a, p in enumerate(idx):
            for b, q in enumerate(idx):
                key = (min(p, q), max(p, q))
                H[a, b] = mp.fsum(mp.mpf(c.numerator) / c.denominator * om(l, s) for (l, s), c in d[key].items())
        fs = []
        for M in range(1, n + 1):
            sub = H[:M, :M]
            e0 = mp.matrix([1] + [0] * (M - 1))
            x = mp.lu_solve(sub, e0)
            fs.append(float(H[0, 0] * x[0]))
        out[prop] = fs
    return out


def first_approx(I, T):
    """Reduced first approximations: eta* = eta sigma^2 / sqrt(m eps), lambda* = lambda sigma^2 sqrt(m/eps) / k,
    (nD)* = n D sigma^2 sqrt(m / eps)."""
    J7 = np.pi * I[1, 2] / 2      # int exp(-g^2) g^7 Q^(2) dg / sigma^2
    J5 = np.pi * I[0, 1] / 2      # int exp(-g^2) g^5 Q^(1) dg / sigma^2
    eta1 = 5.0 / 8.0 * np.sqrt(np.pi * T) / J7
    return {"visc": eta1, "cond": 15.0 / 4.0 * eta1, "diff": 3.0 / 8.0 * np.sqrt(np.pi * T) / J5}


def omega_star(I):
    """Omega^(1,1)* and Omega^(2,2)* (rigid-sphere reduced)."""
    return I[0, 1] / 2.0, I[1, 2] / (6.0 * 2.0 / 3.0)


if __name__ == "__main__":
    opt = dict(A="0", T="1", P="8", rel="1e-10", width="0.5", K="14", ngr="10", nuni="16", h="0.015625", tag="base")
    opt.update(a.split("=", 1) for a in sys.argv[1:])
    A, P, rel = float(opt["A"]), int(opt["P"]), float(opt["rel"])
    Ts = [float(t) for t in opt["T"].split(",")]
    pot = S.Kihara(A)
    sc = S.Scatter(pot, de_h=float(opt["h"]))
    print("A=%.3f E_c=%.6f r_c=%.6f h_max=%.6f  options %s" % (A, pot.E_c, pot.r_c, pot.h_max, opt))
    coefs = load_coefs(P, "coefs_P%d.json" % P)
    L = max(l for d in coefs.values() for v in d.values() for l, s in v)
    smax = max(s for d in coefs.values() for v in d.values() for l, s in v)
    E, w = e_nodes(pot.E_c, 1e-4 * min(Ts), 150.0 * max(Ts), float(opt["width"]), int(opt["nuni"]), int(opt["K"]),
                   int(opt["ngr"]))
    print("P=%d needs l<=%d s<=%d; %d energies" % (P, L, smax, len(E)), flush=True)
    t0 = time.time()
    Q = sample_Q(A, float(opt["h"]), E, L, rel, "Q_A%.3f_%s.npz" % (A, opt["tag"]))
    print("Q sampling %.0f s" % (time.time() - t0))
    if Q is None:
        print("INCOMPLETE: run again with the same options to resume")
        sys.exit(3)
    I = thermal(Ts, E, w, Q, smax)
    for t, T in enumerate(Ts):
        o11, o22 = omega_star(I[t])
        fa = first_approx(I[t], T)
        fs = factors(coefs, I[t], P)
        print("T*=%-7g Omega11*=%.10f Omega22*=%.10f" % (T, o11, o22))
        for prop in ("visc", "cond", "diff"):
            f = fs[prop]
            print("   %s first=%.10f  f(M=1..%d): %s" % (prop, fa[prop], len(f), " ".join("%.9f" % v for v in f)))
    np.save("I_A%.3f_%s.npy" % (A, opt["tag"]), I)
