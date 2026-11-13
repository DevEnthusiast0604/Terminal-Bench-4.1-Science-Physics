"""Clock-only check of every stall in tests/generate.py's SESSIONS (author's design script, not shipped).

For each stall: the GPS interval that holds it, its counted frames minus the exact rate (in (-1-n, 1-n) for a
stall of n frames), and whether a detector that compares counts with the median count and a 1.5-frame
threshold misses it. Also checks the rules NOTES.md states: no stall covers the first lit frame of an onset,
stalls lie 5 s after the release and 5 s before the end of the log.

    python -B stalls.py <tests_dir>
"""
import math
import sys

import numpy as np

sys.path.insert(0, sys.argv[1])
import generate as G  # noqa: E402

for name, sess in G.SESSIONS.items():
    for rid, (pivot, amp, eps, c0, held, stalls, unit, gps0, frac) in sess["runs"].items():
        rate = G.NOMINAL_FPS * (1.0 + eps)
        n_raw = int(sess["duration"] * rate)
        first = int(round(held * rate))
        t_rel = (np.arange(n_raw) - first) / rate
        delivered = np.ones(n_raw, dtype=bool)
        lost_before = np.zeros(n_raw, dtype=int)
        where = []
        for lost, ts in stalls:
            k0 = int(np.searchsorted(t_rel, ts))
            delivered[k0:k0 + lost] = False
            lost_before[k0 + lost:] += lost
            where.append((lost, ts, k0))
        t_frame = frac + np.arange(n_raw) / rate
        onsets = []
        for n in range(1, int(t_frame[-1]) + 1):
            k = int(np.searchsorted(t_frame, n))
            if not delivered[k]:
                print("%s %s: STALL COVERS ONSET at second %d" % (name, rid, n))
            onsets.append((n, k, k - lost_before[k]))
        counts = np.diff([c for _, _, c in onsets])
        med = np.median(counts)
        log_len = (n_raw - first) / rate
        for lost, ts, k0 in where:
            j = next(i for i in range(len(onsets) - 1) if onsets[i][1] <= k0 < onsets[i + 1][1])
            deficit = counts[j] - rate
            naive = counts[j] - med
            flags = []
            if naive > -1.5:
                flags.append("MISSED by median+1.5")
            if ts < 5 or ts > log_len - 5:
                flags.append("TOO CLOSE TO AN END")
            print("%s %s stall %2d at %6.2f s: interval %3d, count-rate %+.3f, count-median %+.0f  %s" % (
                name, rid, lost, ts, j, deficit, naive, " ".join(flags)))
