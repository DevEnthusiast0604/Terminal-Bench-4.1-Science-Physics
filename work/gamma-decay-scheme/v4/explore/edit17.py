"""v4: the generator prints the reference's 511 keV split after each run. Run from the folder root."""
from pathlib import Path

p = Path("tasks/active/gamma-decay-scheme/tests/generate.py")
s = p.read_text(encoding="utf-8")
old = "        diag = json.load(open(diag_path))\n"
new = ("        diag = json.load(open(diag_path))\n"
       '    print("511 keV split:", {k: round(v, 3) for k, v in (diag.get("annihilation_split") or {}).items()})\n')
assert s.count(old) == 1
p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
print("edited", p)
