"""Development aid: run the reduction stage by stage and print each stage next to the generator's truth."""
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

TASK = Path("tasks/active/gamma-decay-scheme")
spec = importlib.util.spec_from_file_location("solve", TASK / "solution" / "solve.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
DATA = TASK / "environment" / "data"
truth = json.load(open(TASK / "tests" / "expected.json"))
true_lines = {round(t["energy_keV"], 1): t for t in truth["transitions"]}

stale, eff, ratios = S.calibrate(DATA)
print("source gain rms %.3f keV, efficiency rms %.4f" % (S.DIAG["source_gain_rms_keV"], S.DIAG["efficiency_rms"]))
print("escape ratios", {k: [(round(a), round(b, 3)) for a, b in v.tolist()] for k, v in ratios.items()})
a, b, widths = S.production_gain(DATA, stale)
print("production gain a %.3f b %.6f rms %.3f; widths %s" % (a, b, S.DIAG["gain_rms_keV"], widths))
print("offset", S.DIAG["gain_offset_keV_at"])
peaks = S.Peaks(DATA, stale, (a, b, widths), eff)
t_parent = S.separate_activities(peaks)
print("parent half-life %.3f, daughter %s; peaks found: %d" % (t_parent, S.DIAG["daughter_half_life_s"], len(peaks.items)))
coin = S.Coincidences(DATA, peaks)
lines, scale = S.classify(peaks, coin, eff, ratios)
print("\nexcluded:")
for kind, e, i in sorted(S.DIAG["excluded"], key=lambda t: t[1]):
    if i > 0.3:
        print("  %-18s %8.2f  I %.2f" % (kind, e, i))
print("\nsum candidates:")
for s in S.DIAG["sum_candidates"]:
    print("  %8.2f before %.2f after %.2f  parts %s" % (s["E"], s["I_before"], s["I_after"], [(round(x, 1), round(y, 1), round(n)) for x, y, n in s["parts"]]))
print("\ncandidate lines vs truth:")
got = []
for p in lines:
    near = min(true_lines, key=lambda e: abs(e - p["E"]))
    tag = "%8.1f I %.2f  dE %+.2f" % (near, true_lines[near]["relative_intensity"], p["E"] - near) if abs(near - p["E"]) < 2 else "--- NOT TRUE"
    print("  %8.2f +- %.2f width %.2f I %7.2f share %.2f | %s" % (p["E"], p["err"], p["width"], p["I"], p["share"], tag))
    got.append(near)
missing = [e for e in true_lines if e not in got and not any(abs(e - p["E"]) < 2 for p in lines)]
print("missing true lines:", missing)
lines2, k_scale = S.split_doublets(lines, coin, eff)
print("\nk_scale", k_scale)
for r in S.DIAG["doublet_tests"]:
    if r["moved"] or r["self_strength"] > 0.01 or r["width"] > 1.12:
        print("  %8.2f width %.2f self %.0f (%.3f) moved %s gates %s" % (r["E"], r["width"], r["self_net"], r["self_strength"], r["moved"], [(round(g, 1), round(c, 2), round(e, 2)) for g, c, e in r["gates"]]))
print("lines after split:", [(round(l["E"], 2), l["member"]) for l in lines2 if l["member"]])
flags, strength, upper, delayed = S.coincidence_flags(lines2, coin, eff, k_scale)
print("delayed pairs:", [(round(a, 1), round(b, 1), round(n)) for a, b, n in delayed])

# Compare the flags with the truth: path exists in the true scheme?
lev = {}
trans = []
for t in truth["transitions"]:
    trans.append((t["from_keV"], t["to_keV"], t["energy_keV"]))
hidden = [(1963.1, 1925.0)]
def reach_from(x):
    seen = {x}
    stack = [x]
    while stack:
        u = stack.pop()
        for a, b, _ in trans:
            if a == u and b not in seen:
                seen.add(b); stack.append(b)
        for a, b in hidden:
            if a == u and b not in seen:
                seen.add(b); stack.append(b)
    return seen
def true_line(e):
    best = min(trans, key=lambda t: abs(t[2] - e))
    return best if abs(best[2] - e) < 1.0 else None
wrong = 0
for i in range(len(lines2)):
    for j in range(i + 1, len(lines2)):
        A, B = true_line(lines2[i]["E"]), true_line(lines2[j]["E"])
        if A is None or B is None:
            print("no truth for", lines2[i]["E"], lines2[j]["E"]); continue
        p = A[1] in reach_from(B[0]) and False
        p = (B[0] in reach_from(A[1])) or (A[0] in reach_from(B[1]))
        f = flags[i][j]
        if (f == 1 and not p) or (f == 0 and p):
            wrong += 1
            print("  WRONG FLAG %.1f %.1f flag %s true path %s strength %.3f" % (A[2], B[2], f, p, strength[i][j]))
na = sum(1 for i in range(len(lines2)) for j in range(i + 1, len(lines2)) if flags[i][j] is None)
print("wrong flags: %d; unknown flags: %d of %d" % (wrong, na, len(lines2) * (len(lines2) - 1) // 2))
if "--search" in sys.argv:
    feeders = {p[0] for p in delayed}
    for l in lines2:
        l["delayed_feeder"] = l["peak"] in feeders
    order = sorted(range(len(lines2)), key=lambda i: (lines2[i]["delayed_feeder"], -lines2[i]["I"]))
    import time
    print("order:", [(round(lines2[i]["E"], 1), round(lines2[i]["I"], 1)) for i in order], flush=True)
    for m in range(14, 19):
        t0 = time.time()
        S.DEPTHS.clear()
        try:
            sols = S.search(lines2, flags, upper, order, m, limit=int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 400000)
            print("depths", sorted(S.DEPTHS.items()), flush=True)
            print("rejects", S.REJECTS[-8:], flush=True)
        except RuntimeError as ex:
            print("max levels", m, ex, "%.1f s" % (time.time() - t0))
            print("depths", sorted(S.DEPTHS.items()), flush=True)
            break
        print("max levels", m, "solutions", len(sols), "%.1f s" % (time.time() - t0))
        for levels, place, hid in sols[:6]:
            print("   ", sorted(round(v, 1) for v in levels), hid)
