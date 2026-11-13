"""v14: more beta feeding to Y (1399.8 keV), 1.9 -> 3.6, branches B 55 / A 45, so that its 557.1 keV line is a regular
line (I about 3.0) and the hidden 1081.4 keV line somewhat stronger (I about 2.4, a fifth of E -> B). Exact-match
replacements in tests/generate.py; run from the folder root."""
PATH = "tasks/active/gamma-decay-scheme/tests/generate.py"
s = open(PATH, encoding="utf-8", newline="").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


rep("""# under E -> B (1082.3 keV) with an eighth of its intensity, and the only line below it, A -> g, lies below E -> B as
""", """# under E -> B (1082.3 keV) with a fifth of its intensity, and the only line below it, A -> g, lies below E -> B as
""")
rep("""    "Y": (1399.8, 1.9, [("B", 45), ("A", 55)]),
""", """    "Y": (1399.8, 3.6, [("B", 55), ("A", 45)]),
""")
assert "\r" not in s
open(PATH, "w", encoding="utf-8", newline="").write(s)
print("generate.py edited")
