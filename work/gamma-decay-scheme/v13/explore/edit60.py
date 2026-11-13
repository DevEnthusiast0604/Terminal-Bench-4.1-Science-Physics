"""v13 README: the width range covers every kept line, not every peak. Run from the folder root."""
PATH = "tasks/active/gamma-decay-scheme/README.md"
s = open(PATH, encoding="utf-8", newline="").read()
old = "The singles do not flag it: every peak but the two doublets has a width"
assert s.count(old) == 1
s = s.replace(old, "The singles do not flag it: every line but the two doublets has a width")
open(PATH, "w", encoding="utf-8", newline="").write(s)
print("README.md edited")
