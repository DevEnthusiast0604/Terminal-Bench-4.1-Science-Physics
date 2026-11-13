"""The oracle's computation for one graded case in two calls, for cases that take longer than one call allows
(author self-check). The brackets are the program's own functions over half of its energies each; combining them
and the rest of main() follow solution/transport.py.

    python -B run_parts.py PROGRAM CASE 0|1        brackets over the energies i::2 (saved next to this file)
    python -B run_parts.py PROGRAM CASE combine    coefficients, tail, and the errors against tests/expected.json
"""
import importlib
import json
import multiprocessing
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = os.path.normpath(os.path.join(HERE, "../../../../tasks/active/chapman-enskog-transport/tests"))
sys.path.insert(0, TESTS)
import emit  # noqa: E402


def load(prog):
    """The program as a module named after its file, so that spawned workers can import it from this folder."""
    sys.path.insert(0, HERE)
    return importlib.import_module(os.path.splitext(prog)[0])


def half(T, a, m2, T_star, P, which):
    Ec = T.Kihara(a).E_c
    E, w = T.split_nodes(Ec, 1e-4 * T_star, (4.0 * P + 40.0) * T_star, max(0.5 * T_star, 1.6 * Ec))
    x = E / T_star
    W = w * np.exp(-x) * x * x
    nodes = [(float(E[i]), float(x[i]), float(W[i])) for i in range(which, len(E), 2)]
    n_chunks = 8 * T.WORKERS
    chunks = [nodes[k::n_chunks] for k in range(n_chunks)]
    tw = T.laguerre_rule(P + 4)
    ctx = multiprocessing.get_context("spawn")
    with ctx.Pool(T.WORKERS, initializer=T._init, initargs=(a, m2, P, tw)) as pool:
        parts = pool.map(T._chunk, chunks, chunksize=1)
    acc = {}
    for part in parts:
        for k, v in part.items():
            acc[k] = acc.get(k, 0.0) + v
    return acc


if __name__ == "__main__":
    prog, case, what = sys.argv[1:4]
    T = load(prog)
    a, m2, x1, T_star = (float(v) for v in emit.CASES[case][1:])
    out = os.path.join(HERE, "parts-%s-%s.npz" % (case, "%s"))
    t0 = time.time()
    if what in ("0", "1"):
        acc = half(T, a, m2, T_star, T.TERMS, int(what))
        np.savez(out % what, **{"%s|%s" % k: v for k, v in acc.items()})
        print("%s half %s: %.0f s" % (case, what, time.time() - t0))
    else:
        acc = {}
        for h in ("0", "1"):
            with np.load(out % h) as d:
                for k in d.files:
                    key = tuple(k.split("|"))
                    acc[key] = acc.get(key, 0.0) + d[k]
        P = T.TERMS
        v = {p: T.coefficients(acc, m2, x1, T_star, p) for p in (P - 8, P - 4, P)}
        res = {k: T.with_tail(P, v[P - 8][k], v[P - 4][k], v[P][k]) for k in v[P]}
        expected = json.load(open(os.path.join(TESTS, "expected.json")))[case]
        cells = []
        for q, e in expected.items():
            tol = max(abs(e) * 2e-5, 1e-6 if q == "thermal_diffusion_factor" else 0.0)
            cells.append("%s %.1e (%.0f%% of tol)" % (q[:12], abs(res[q] - e) / max(abs(e), 1e-300),
                                                      100 * abs(res[q] - e) / tol))
        print("%s %s (two halves): %s" % (case, " ".join(emit.CASES[case][1:]), "  ".join(cells)))
