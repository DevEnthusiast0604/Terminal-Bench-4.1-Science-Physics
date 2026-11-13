"""Per-transition relative-intensity and energy errors of each pass@3 answer against expected.json (JSON only).
python -X utf8 -I -B <this> EXPECTED.json a1=PATH a2=PATH ..."""
import json
import sys

exp = json.load(open(sys.argv[1], encoding="utf-8"))
runs = [a.split("=", 1) for a in sys.argv[2:]]
docs = {n: json.load(open(p, encoding="utf-8")) for n, p in runs}
print("%-8s %-17s %8s " % ("E_keV", "from->to", "I_true") + " ".join("%14s" % n for n, _ in runs))
worst = {n: 0.0 for n, _ in runs}
for w in sorted(exp["transitions"], key=lambda t: t["energy_keV"]):
    cells = []
    for n, _ in runs:
        hit = [t for t in docs[n]["transitions"]
               if abs(t["from_keV"] - w["from_keV"]) <= 0.5 and abs(t["to_keV"] - w["to_keV"]) <= 0.5]
        if len(hit) != 1:
            cells.append("%14s" % "-")
            continue
        r = hit[0]["relative_intensity"] / w["relative_intensity"] - 1
        worst[n] = max(worst[n], abs(r))
        cells.append("%+6.1f%% %+5.2f" % (100 * r, hit[0]["energy_keV"] - w["energy_keV"]))
    print("%-8.1f %-17s %8.2f " % (w["energy_keV"], "%.1f->%.1f" % (w["from_keV"], w["to_keV"]), w["relative_intensity"])
          + " ".join(cells))
print("worst |dI/I|:", {n: round(100 * v, 1) for n, v in worst.items()})
for n, _ in runs:
    errs = []
    for w in exp["transitions"]:
        hit = [t for t in docs[n]["transitions"]
               if abs(t["from_keV"] - w["from_keV"]) <= 0.5 and abs(t["to_keV"] - w["to_keV"]) <= 0.5]
        if len(hit) == 1:
            errs.append(abs(hit[0]["relative_intensity"] / w["relative_intensity"] - 1))
    for tol in (0.05, 0.10, 0.15, 0.20):
        print(n, "transitions outside %2d%%: %d" % (100 * tol, sum(e > tol for e in errs)))
