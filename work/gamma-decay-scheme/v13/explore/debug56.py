"""Temporary: in solve.py's failure branch, print the flags, strengths and ceilings of every pair. Reverted after."""
PATH = "tasks/active/gamma-decay-scheme/solution/solve.py"
s = open(PATH, encoding="utf-8", newline="").read()
old = """        # Which single line keeps every scheme out: the search again without each line in turn.
"""
new = """        # DEBUG56
        for i in range(len(lines)):
            for k in range(len(lines)):
                if k != i:
                    print("DBG %8.2f %8.2f flag %s strength %.4f ceiling %.4f" % (lines[i]["E"], lines[k]["E"], flags[i][k],
                          strength[i][k], ceiling[i][k]), file=sys.stderr)
        # Which single line keeps every scheme out: the search again without each line in turn.
"""
assert s.count(old) == 1
s = s.replace(old, new)
open(PATH, "w", encoding="utf-8", newline="").write(s)
print("debug in")
