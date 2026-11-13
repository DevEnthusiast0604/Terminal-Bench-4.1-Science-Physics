"""v4: when no scheme fits, the reference says which single line keeps every scheme out (search again without it).
Only runs on that failure. Run from the folder root."""
from pathlib import Path

p = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
s = p.read_text(encoding="utf-8")
old = '''    if not solutions:
        raise SystemExit("no scheme agrees with the data")
'''
new = '''    if not solutions:
        # Which single line keeps every scheme out: the search again without each line in turn.
        for i in range(len(lines)):
            keep = [k for k in range(len(lines)) if k != i]
            pos = {k: x for x, k in enumerate(keep)}
            try:
                found = search([lines[k] for k in keep], [[flags[a][b] for b in keep] for a in keep],
                               [[ceiling[a][b] for b in keep] for a in keep], [pos[k] for k in order if k != i], 17)
            except RuntimeError:
                found = None
            if found:
                l = lines[i]
                print("a scheme fits without %.2f keV (I %.2f, share %.2f, member %s); seen with: %s; not seen with: %s"
                      % (l["E"], l["I"], l.get("share", 1.0), l["member"],
                         " ".join("%.1f" % lines[k]["E"] for k in range(len(lines)) if flags[i][k] == 1),
                         " ".join("%.1f" % lines[k]["E"] for k in range(len(lines)) if flags[i][k] == 0)), file=sys.stderr)
        raise SystemExit("no scheme agrees with the data")
'''
assert s.count(old) == 1
p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
print("edited", p)
