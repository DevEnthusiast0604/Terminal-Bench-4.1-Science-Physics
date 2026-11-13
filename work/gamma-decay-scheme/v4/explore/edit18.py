"""v4: the 511 keV split window stops short of the strong 524.3 keV line (501 to 518 keV). Run from the folder root."""
from pathlib import Path

p = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
s = p.read_text(encoding="utf-8")
pairs = [("    lo = max(int(np.searchsorted(peaks.edges, 511.0 - 14.0)) - 1, 0)\n    hi = int(np.searchsorted(peaks.edges, 511.0 + 14.0))\n",
          "    # The window stops short of the strong 524.3 keV line above it.\n"
          "    lo = max(int(np.searchsorted(peaks.edges, 511.0 - 10.0)) - 1, 0)\n    hi = int(np.searchsorted(peaks.edges, 511.0 + 7.0))\n")]
for old, new in pairs:
    assert s.count(old) == 1, old
    s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline="\n")
print("edited", p)
