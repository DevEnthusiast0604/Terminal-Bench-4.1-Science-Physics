"""Exploration (v5): binary mixture of identical Kihara molecules (core ratio A) with masses 1 and m2.
One pass over the energy nodes: Legendre transport cross sections Qt^(l)(E) = 2 pi int (1 - P_l(cos chi)) b db and
the quadrature kernels at x = E / T, summed into composition-independent blocks; then any x1 is cheap.
    python -B kihara_mix.py TESTS_DIR A m2 T P x1[,x1...] [width n_uni Xmax]"""
import os
import sys
import time

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"                # before numpy/scipy load: inherited by the spawned workers
import numpy as np

sys.path.insert(0, sys.argv[1])
import ce_ref as R                      # noqa: E402  (scattering and energy grid from the v4 reference)
from mixq import Kernel, rules, types   # noqa: E402
from survey import props                # noqa: E402

_G = {}


def leg_one_minus(s, L):
    """D[..., l] = 1 - P_l(1 - s) for l = 0..L-1, s = 1 - cos chi in [0, 2], without cancellation."""
    D = np.zeros(s.shape + (L,))
    if L > 1:
        D[..., 1] = s
    for l in range(1, L - 1):
        D[..., l + 1] = ((2 * l + 1) * (s + D[..., l] - s * D[..., l]) - l * D[..., l - 1]) / (l + 1)
    return D


def Qleg(sc, E, L, rel=1e-10, smax=30.0):
    """Qt^(l)(E) in units of sigma^2 for l = 0..L-1."""
    def integrand_b(bv):
        ch = sc.chi(bv, E)
        s = 2.0 * np.sin(0.5 * ch) ** 2
        return leg_one_minus(s, L) * bv[:, None]
    bs = sc.b_star(E)
    inner = lambda sv: integrand_b(bs * (-np.expm1(-sv))) * (bs * np.exp(-sv))[:, None]
    outer = lambda sv: integrand_b(bs * (1.0 + np.exp(-sv))) * (bs * np.exp(-sv))[:, None]
    far = lambda vv: integrand_b(2.0 * bs / vv) * (2.0 * bs / vv ** 2)[:, None]
    return 2.0 * np.pi * R.adaptive_pieces([(inner, 0.0, smax), (outer, 0.0, smax), (far, 1e-6, 1.0)], rel)


def _init(A, m2, P, tw):
    for v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[v] = "1"
    _G["sc"] = R.Scatter(R.Kihara(A), de_h=1.0 / 32)
    _G["K"] = {kind: {name: Kernel(*prm, P, kind, tw) for name, prm in types(1.0, m2).items()}
               for kind in ("vector", "tensor")}


def _node(args):
    """W_i sum_l Qt_l c_l(x_i) per kind and type (like: even l only; l = 0 dropped)."""
    i, E, x, W = args
    out = {}
    Lmax = max(K.Lout for d in _G["K"].values() for K in d.values())
    Q = Qleg(_G["sc"], E, Lmax)
    for kind, d in _G["K"].items():
        for name, K in d.items():
            c = K.c(x)
            ql = Q[:K.Lout].copy()
            ql[0] = 0.0
            if name == "like":
                ql[1::2] = 0.0
            out[(kind, name)] = W * np.tensordot(ql, c, axes=(0, 0))
    return i, out, Q


def blocks(A, m2, T, P, width=1.0, n_uni=16, Xmax=None, workers=6, log=print):
    from concurrent.futures import ProcessPoolExecutor
    pot = R.Kihara(A)
    Xmax = Xmax or max(150.0, 4.0 * P + 40.0)
    E, w = R.e_nodes(pot.E_c, 1e-4 * T, Xmax * T, width=width, n_uni=n_uni, K=10, n_gr=8)
    x = E / T
    W = w * np.exp(-x) * x * x                    # int e^-x x f dx = int e^-x x^2 f d(ln x)
    log("A %g m2 %g T %g P %d: %d energies, x up to %g, E_c %.6f" % (A, m2, T, P, len(E), Xmax, pot.E_c))
    acc = {}
    t0 = time.time()
    tw = tuple(np.asarray(v) for v in rules(P))
    with ProcessPoolExecutor(workers, initializer=_init, initargs=(A, m2, P, tw)) as ex:
        for n, (i, out, Q) in enumerate(ex.map(_node, [(i, float(E[i]), float(x[i]), float(W[i]))
                                                       for i in range(len(E))], chunksize=2)):
            for k, v in out.items():
                acc[k] = acc.get(k, 0.0) + v
            if n % 100 == 99:
                log("  %d / %d nodes (%.0f s)" % (n + 1, len(E), time.time() - t0))
    log("  nodes done in %.0f s" % (time.time() - t0))
    return acc


def H_from_blocks(acc, kind, m2, x1, T):
    m1, x2 = 1.0, 1.0 - x1
    mu = {"11": m1 / 2, "22": m2 / 2, "12": m1 * m2 / (m1 + m2)}
    f = {k: np.sqrt(T / (2 * np.pi * v)) / 2 for k, v in mu.items()}
    H11 = 16 * x1 * x1 * f["11"] * acc[(kind, "like")] + 8 * x1 * x2 * f["12"] * acc[(kind, "11")]
    H22 = 16 * x2 * x2 * f["22"] * acc[(kind, "like")] + 8 * x1 * x2 * f["12"] * acc[(kind, "22")]
    H12 = 8 * x1 * x2 * f["12"] * acc[(kind, "12")]
    return np.block([[H11, H12], [H12.T, H22]])


def report(acc, m2, T, P, x1s, Ps=None):
    Ps = Ps or [p for p in range(2, P + 1, 2)]
    for x1 in x1s:
        Ht, Hv = H_from_blocks(acc, "tensor", m2, x1, T), H_from_blocks(acc, "vector", m2, x1, T)
        res = {Pm: props(Ht, Hv, 1.0, m2, x1, T, Pm) for Pm in Ps}
        ref = res[Ps[-1]]
        print("  x1 %g: P=%d " % (x1, Ps[-1]) + " ".join("%s %.10g" % (k, float(v)) for k, v in ref.items()))
        for Pm in Ps[:-1]:
            print("     P=%2d err " % Pm + " ".join("%s %.1e" % (k, abs(float(res[Pm][k] / ref[k] - 1))) for k in ref))
        sys.stdout.flush()


if __name__ == "__main__":
    A, m2, T, P = float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), int(sys.argv[5])
    x1s = [float(v) for v in sys.argv[6].split(",")]
    extra = sys.argv[7:]
    width = float(extra[0]) if extra else 1.0
    n_uni = int(extra[1]) if len(extra) > 1 else 16
    Xmax = float(extra[2]) if len(extra) > 2 else None
    acc = blocks(A, m2, T, P, width, n_uni, Xmax)
    np.savez(os.path.join(os.path.dirname(os.path.abspath(__file__)), "cache",
                          "blk_A%g_m%g_T%g_P%d_w%g_n%d.npz" % (A, m2, T, P, width, n_uni)),
             **{"%s|%s" % k: v for k, v in acc.items()})
    report(acc, m2, T, P, x1s)
