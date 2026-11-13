"""v4: on the no-scheme failure the reference also prints its line table. Run from the folder root."""
from pathlib import Path

p = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
s = p.read_text(encoding="utf-8")
old = '''        # Which single line keeps every scheme out: the search again without each line in turn.
'''
new = '''        for l in lines:
            print("line %8.2f  I %7.2f  share %.2f  member %s" % (l["E"], l["I"], l.get("share", 1.0), l["member"]),
                  file=sys.stderr)
        # Which single line keeps every scheme out: the search again without each line in turn.
'''
assert s.count(old) == 1
p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
print("edited", p)
