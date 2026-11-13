"""v4, second pass: keep M -> H (511.0 keV, on the annihilation line), drop M -> J (403.4 keV): the reference's own
403.4 keV intensity came out 28 percent low (summing-out at the top of a six-step cascade plus a minority time share),
and the stronger 551.8 keV line raised the 870.2 keV sum peak into a false doublet with 867.5 keV. The annihilation
split now asks for a 6-sigma narrow part with the parent's time profile (the parent/ramp/daughter shapes are too
correlated for a 6-sigma parent coefficient). Run from the folder root."""
from pathlib import Path

T = Path("tasks/active/gamma-decay-scheme")


def edit(path, pairs):
    p = T / path
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, (path, n, old[:80])
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="\n")
    print("edited", p)


edit("tests/generate.py", [
    ("# M -> J (403.4 keV) lies on the daughter's own 403.4 keV line, and M -> H (511.0 keV) on the annihilation line.\n",
     "# M -> H (511.0 keV) lies on the annihilation line.\n"),
    ('    "M": (3092.6, 12.0, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("J", 36), ("H", 6)]),\n',
     '    "M": (3092.6, 9.5, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("H", 6)]),\n'),
])
edit("solution/solve.py", [
    ('    if split["narrow"] > 6.0 * split["narrow_err"] and split["parent_area"] > 6.0 * split["parent_err"]:\n',
     '    if split["narrow"] > 6.0 * split["narrow_err"] and split["parent_share"] >= 0.5:\n'),
    ("        for l in lines:\n"
     '            print("line %8.2f  I %7.2f  share %.2f  member %s" % (l["E"], l["I"], l.get("share", 1.0), l["member"]),\n'
     "                  file=sys.stderr)\n",
     '        print("annihilation split:", DIAG.get("annihilation_split"), file=sys.stderr)\n'
     "        for l in lines:\n"
     '            print("line %8.2f  I %7.2f  share %.2f  member %s" % (l["E"], l["I"], l.get("share", 1.0), l["member"]),\n'
     "                  file=sys.stderr)\n"),
])
