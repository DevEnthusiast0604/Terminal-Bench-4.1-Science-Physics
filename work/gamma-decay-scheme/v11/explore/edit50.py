"""v11 edit 1 of 2: tests/generate.py. v8's 511 keV line (H beta 2.75, M beta 11.75, M->H 31, pair-production
annihilation 3.0e-4 per decay) and a new level at 2721.7 keV, fed only by beta decay, that decays to B by a clean
1879.0 keV line and to Da by a 1081.4 keV line 0.9 keV under E->B (1082.3 keV). Every replacement must match once."""
from pathlib import Path

P = Path("tasks/active/gamma-decay-scheme/tests/generate.py")
s = P.read_bytes().decode("utf-8")
assert "\r" not in s

EDITS = [
    ("# M -> H (511.0 keV) lies on the annihilation line and feeds about a third of H.\n",
     "# M -> H (511.0 keV) lies on the annihilation line and feeds about half of H. X -> Da (1081.4 keV) lies 0.9 keV\n"
     "# under E -> B (1082.3 keV) with a tenth of its intensity: only the gates on the lines below each one tell them apart.\n"),
    ('    "H": (2581.6, 3.65, [("Da", 50), ("B", 35), ("C", 15)]),\n',
     '    "H": (2581.6, 2.75, [("Da", 50), ("B", 35), ("C", 15)]),\n'),
    ('    "J": (2689.2, 5.0, [("G", 1)]),\n',
     '    "J": (2689.2, 5.0, [("G", 1)]),\n'
     '    "X": (2721.7, 1.75, [("B", 55), ("Da", 45)]),\n'),
    ('    "M": (3092.6, 10.85, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("H", 21)]),\n',
     '    "M": (3092.6, 11.75, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("H", 31)]),\n'),
    ("    parent = parent + N_PARENT * 6.0e-4 * peak(EDGES_RUN, 511.0, 1.3)\n",
     "    parent = parent + N_PARENT * 3.0e-4 * peak(EDGES_RUN, 511.0, 1.3)\n"),
]
for old, new in EDITS:
    n = s.count(old)
    assert n == 1, (n, old)
    s = s.replace(old, new)
P.write_bytes(s.encode("utf-8"))
print("generate.py: %d edits" % len(EDITS))
