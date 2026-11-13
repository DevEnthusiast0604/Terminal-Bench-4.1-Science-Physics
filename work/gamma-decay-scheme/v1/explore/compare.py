import json, sys
exp = json.load(open("tasks/active/gamma-decay-scheme/tests/expected.json"))
got = json.load(open("work/gamma-decay-scheme/v1/explore/out/decay_scheme.json"))
print("half-life", got["parent_half_life_s"], exp["parent_half_life_s"])
print("isomer", got["isomer"], exp["isomer"])
print("levels", len(got["levels_keV"]), len(exp["levels_keV"]), "max dev %.3f" % max(abs(a-b) for a, b in zip(got["levels_keV"], exp["levels_keV"])))
def find(t, rows):
    hits = [r for r in rows if abs(r["from_keV"]-t["from_keV"]) <= 0.5 and abs(r["to_keV"]-t["to_keV"]) <= 0.5]
    return hits[0] if len(hits) == 1 else None
worst = 0
for t in exp["transitions"]:
    r = find(t, got["transitions"])
    if r is None:
        print("MISSING", t); continue
    dev = r["relative_intensity"]/t["relative_intensity"]-1
    worst = max(worst, abs(dev))
    print("%8.1f -> %8.1f  E %8.2f %8.2f  I %7.2f %7.2f  %+.1f%%" % (t["from_keV"], t["to_keV"], t["energy_keV"], r["energy_keV"], t["relative_intensity"], r["relative_intensity"], 100*dev))
print("worst intensity dev %.1f%%; transitions %d vs %d" % (100*worst, len(got["transitions"]), len(exp["transitions"])))
