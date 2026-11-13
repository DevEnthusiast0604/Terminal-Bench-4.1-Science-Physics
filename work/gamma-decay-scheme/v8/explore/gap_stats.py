"""For expected.json and earlier pass@3 answers (JSON copied out of the bundles), the largest |from_keV - to_keV -
energy_keV| of any transition: how close honest answers keep the three fields together. Reads JSON only; runs nothing
from the bundles. Run from the folder root: python -X utf8 -I -B <this> NAME=PATH ..."""
import json
import sys

for arg in sys.argv[1:]:
    name, path = arg.split("=", 1)
    d = json.load(open(path, encoding="utf-8"))
    gaps = sorted(((t["from_keV"] - t["to_keV"] - t["energy_keV"]), t["energy_keV"]) for t in d["transitions"])
    worst = max(gaps, key=lambda g: abs(g[0]))
    big = [(round(g, 3), round(e, 1)) for g, e in gaps if abs(g) > 0.2]
    print("%-12s n=%2d  worst gap %+.3f keV at %.1f keV  |gap|>0.2: %s" % (name, len(gaps), worst[0], worst[1], big))
