"""Design probe: periodograms of the generated activity and RVs (imports the generator; writes nothing)."""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
import generate as G  # noqa: E402


def gls(t, y, e, freqs):
    w = 1 / e ** 2
    w = w / w.sum()
    y = y - np.sum(w * y)
    out = np.empty(len(freqs))
    yy = np.sum(w * y * y)
    for i, f in enumerate(freqs):
        x = 2 * np.pi * f * t
        c, s = np.cos(x), np.sin(x)
        C, S = np.sum(w * c), np.sum(w * s)
        YC, YS = np.sum(w * y * c), np.sum(w * y * s)
        CC = np.sum(w * c * c) - C * C
        SS = np.sum(w * s * s) - S * S
        CS = np.sum(w * c * s) - C * S
        D = CC * SS - CS * CS
        out[i] = (SS * YC ** 2 + CC * YS ** 2 - 2 * CS * YC * YS) / (yy * D)
    return out


def peaks(freqs, p, n=8):
    idx = [i for i in range(1, len(p) - 1) if p[i] > p[i - 1] and p[i] >= p[i + 1]]
    idx.sort(key=lambda i: -p[i])
    return [(1 / freqs[i], p[i]) for i in idx[:n]]


rng = np.random.default_rng(G.SEED)
d = G.build(rng)
tv, tn = d["tv"], d["tn"]
freqs = np.linspace(1 / 400, 1 / 1.05, 120000)
sel = (freqs > 1 / 40) & (freqs < 1 / 12)
for name, t, y, e in [("rot_vis (noiseless)", tv, d["act_v"]["rot_vis"], np.ones(len(tv))),
                      ("conv (noiseless)", tv, d["act_v"]["conv"], np.ones(len(tv))),
                      ("dlw", tv, d["dlw"], d["e_dlw"]), ("halpha", tv, d["ha"], d["e_ha"]),
                      ("crx", tv, d["crx"], d["e_crx"]),
                      ("rv_vis", tv, d["rv_v"], d["ev"]), ("rv_nir", tn, d["rv_n"], d["en"])]:
    p = gls(t, y, e, freqs[sel])
    print("%-20s" % name, " ".join("%.3f:%.3f" % pk for pk in peaks(freqs[sel], p, 6)))
# whole range for the RVs
for name, t, y, e in [("rv_vis all", tv, d["rv_v"], d["ev"]), ("rv_nir all", tn, d["rv_n"], d["en"]),
                      ("rv both all", np.r_[tv, tn], np.r_[d["rv_v"] - np.mean(d["rv_v"]), d["rv_n"] - np.mean(d["rv_n"])],
                       np.r_[d["ev"], d["en"]])]:
    p = gls(t, y, e, freqs)
    print("%-20s" % name, " ".join("%.4f:%.3f" % pk for pk in peaks(freqs, p, 10)))
# residuals after the true planets
kep_v = sum(G.rv_planet(tv, q) for q in G.PLANETS)
kep_n = sum(G.rv_planet(tn, q) for q in G.PLANETS)
for name, t, y, e in [("vis minus planets", tv, d["rv_v"] - kep_v, d["ev"]),
                      ("vis minus act", tv, d["rv_v"] - d["act_v"]["rv_vis"], d["ev"]),
                      ("nir minus act", tn, d["rv_n"] - d["act_n"]["rv_nir"], d["en"])]:
    p = gls(t, y, e, freqs)
    print("%-20s" % name, " ".join("%.4f:%.3f" % pk for pk in peaks(freqs, p, 10)))
