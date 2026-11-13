"""Compare each pass@3 answer with tests/expected.json the way the grader's tolerances do: levels within 0.5 keV,
transitions matched by both levels within 0.5 keV, energies within 0.5 keV, intensities within 25%. Reads JSON only.
Run from the folder root: python -X utf8 -I -B <this> OUTPUT_DIR"""
import json
import sys
from pathlib import Path

exp = json.loads(Path("tasks/active/gamma-decay-scheme/tests/expected.json").read_text(encoding="utf-8"))
out_dir = Path(sys.argv[1])
for f in sorted(out_dir.glob("a*.json")):
    a = json.loads(f.read_text(encoding="utf-8"))
    print("== %s: %d levels (want %d), %d transitions (want %d), T1/2 %.4f s (want %.3f), isomer %s"
          % (f.name, len(a["levels_keV"]), len(exp["levels_keV"]), len(a["transitions"]), len(exp["transitions"]),
             a["parent_half_life_s"], exp["parent_half_life_s"], a["isomer"]))
    miss_lev = [x for x in exp["levels_keV"] if not any(abs(x - y) <= 0.5 for y in a["levels_keV"])]
    extra_lev = [y for y in a["levels_keV"] if not any(abs(x - y) <= 0.5 for x in exp["levels_keV"])]
    print("  levels missing %s, extra %s" % (miss_lev, extra_lev))
    used = set()
    worst = []
    for t in sorted(exp["transitions"], key=lambda r: r["energy_keV"]):
        hits = [k for k, r in enumerate(a["transitions"]) if k not in used and abs(r["from_keV"] - t["from_keV"]) <= 0.5
                and abs(r["to_keV"] - t["to_keV"]) <= 0.5]
        if not hits:
            print("  MISSING %.2f keV %.1f -> %.1f (I %.3f)" % (t["energy_keV"], t["from_keV"], t["to_keV"],
                                                               t["relative_intensity"]))
            continue
        k = hits[0]
        used.add(k)
        r = a["transitions"][k]
        de = r["energy_keV"] - t["energy_keV"]
        di = r["relative_intensity"] / t["relative_intensity"] - 1.0
        worst.append((abs(di), t["energy_keV"], di))
        flag = []
        if abs(de) > 0.5:
            flag.append("ENERGY %+.2f" % de)
        if abs(di) > 0.25:
            flag.append("INTENSITY %+.1f%%" % (100 * di))
        if flag or t["energy_keV"] in (1081.4, 1082.3, 557.1, 551.8, 647.8, 646.9):
            print("  %8.2f %7.1f->%-7.1f got E %8.2f I %7.3f (want %7.3f, %+.1f%%) %s"
                  % (t["energy_keV"], t["from_keV"], t["to_keV"], r["energy_keV"], r["relative_intensity"],
                     t["relative_intensity"], 100 * di, " ".join(flag)))
    for k, r in enumerate(a["transitions"]):
        if k not in used:
            print("  EXTRA %.2f keV %.1f -> %.1f I %.3f" % (r["energy_keV"], r["from_keV"], r["to_keV"],
                                                           r["relative_intensity"]))
    worst.sort(reverse=True)
    print("  worst intensity errors: %s" % ", ".join("%.1f %+.1f%%" % (e, 100 * d) for _, e, d in worst[:4]))
