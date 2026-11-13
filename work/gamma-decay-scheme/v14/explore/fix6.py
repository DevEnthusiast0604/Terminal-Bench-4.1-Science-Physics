"""Correct the level names in design6.py. Run from the folder root."""
P = "work/gamma-decay-scheme/v14/explore/design6.py"
s = open(P, encoding="utf-8", newline="").read()
for old, new in [('(1092.0, ("M", "Da")), (992.7, ("K", "Da")), (1606.6, ("E", "A")),\n                   (867.5, ("L", "E"))',
                  '(1092.0, ("H", "C")), (992.7, ("I", "Da")), (1606.6, ("E", "A")),\n                   (867.5, ("K", "E"))'),
                 ('rel[("Jb", "F")]\n             if ("Jb", "F") in rel else float("nan")', 'rel[("J", "G")]')]:
    assert s.count(old) == 1, old[:40]
    s = s.replace(old, new)
open(P, "w", encoding="utf-8", newline="").write(s)
print("fixed")
