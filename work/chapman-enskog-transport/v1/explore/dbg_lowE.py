import sys, numpy as np, scatter as S
pot = S.Kihara(0.5)
sc = S.Scatter(pot, de_h=1/32)
E, L, rel = float(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
orig = S.gl16
log = []
def gl16(f, lo, hi):
    log.append((len(lo), float(lo.min()), float(hi.max())))
    return orig(f, lo, hi)
S.gl16 = gl16
orig_ap = S.adaptive_pieces
def ap(pieces, rel=1e-11, n0=24, min_width=1e-5, max_rounds=30):
    lo = np.concatenate([np.linspace(a, b, n0 + 1)[:-1] for f, a, b in pieces])
    hi = np.concatenate([np.linspace(a, b, n0 + 1)[1:] for f, a, b in pieces])
    owner = np.repeat(np.arange(len(pieces)), n0)
    width = sum(b - a for f, a, b in pieces)
    total, est = 0.0, None
    for rnd in range(max_rounds):
        mid = 0.5 * (lo + hi)
        W = np.zeros((len(lo), L)); Hh = np.zeros_like(W)
        for k, (f, a, b) in enumerate(pieces):
            sel = owner == k
            if sel.any():
                W[sel] = orig(f, lo[sel], hi[sel]); Hh[sel] = orig(f, lo[sel], mid[sel]) + orig(f, mid[sel], hi[sel])
        if est is None:
            est = np.maximum(np.abs(Hh.sum(0)), 1e-300)
        err = (np.abs(Hh - W) / est[None, :]).max(1)
        ok = (err <= rel * (hi - lo) / width) | ((hi - lo) < min_width)
        bad = ~ok
        print("round %d: panels %d, bad %d by piece %s; bad s-range %s; worst l %s" % (
            rnd, len(lo), bad.sum(), np.bincount(owner[bad], minlength=3),
            [(round(float(lo[bad & (owner == k)].min()), 4), round(float(hi[bad & (owner == k)].max()), 4)) if (bad & (owner == k)).any() else None for k in range(3)],
            np.bincount((np.abs(Hh - W) / est[None, :])[bad].argmax(1), minlength=L) if bad.any() else None), flush=True)
        total = total + Hh[ok].sum(0)
        if ok.all() or len(lo) > 200000:
            return total
        lo, hi, owner = (np.concatenate([lo[bad], mid[bad]]), np.concatenate([mid[bad], hi[bad]]), np.concatenate([owner[bad], owner[bad]]))
S.adaptive_pieces = ap
q = S.Q_all(sc, E, L, rel)
print(q)
