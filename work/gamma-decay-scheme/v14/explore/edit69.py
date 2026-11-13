"""v14: the reference keeps a hidden member on the fit of the peak's shape, but takes its share from the gates on the
lines below the two members when they give one: their proportions depend neither on the line shape nor on the energy
scale, and the fit's share moves with both (a common shift of 0.05 keV moves it by about 0.055). checks.txt says which
share set the intensity. Exact-match replacements in solution/solve.py and tests/generate.py; run from the folder root."""
SOLVE = "tasks/active/gamma-decay-scheme/solution/solve.py"
GEN = "tasks/active/gamma-decay-scheme/tests/generate.py"


def edit(path, pairs):
    s = open(path, encoding="utf-8", newline="").read()
    for old, new in pairs:
        assert s.count(old) == 1, (path, s.count(old), old[:80])
        s = s.replace(old, new)
    assert "\r" not in s
    open(path, "w", encoding="utf-8", newline="").write(s)
    print(path, "edited")


edit(SOLVE, [
    ("""    when it clears the reporting floor and stands five standard errors above zero, the error counting how far a member
    made up next to a line that stands alone strays. The gates on the lines below the two members check its share:
    they see the two in different proportions.
    \"\"\"""", """    when it clears the reporting floor and stands five standard errors above zero, the error counting how far a member
    made up next to a line that stands alone strays. Its share then comes from the gates on the lines below the two
    members, which see the two in different proportions: that ratio depends neither on the line shape nor on the
    energy scale, while the fit's share moves with both (a common shift of 0.05 keV moves it by about 0.055).
    \"\"\""""),
    ("""            t["gate_share"] = float(kh / (km + kh))
            t["gate_err"] = float(math.sqrt(max(jac @ cov @ jac, 0.0)))
""", """            t["gate_share"] = float(kh / (km + kh))
            t["gate_err"] = float(math.sqrt(max(jac @ cov @ jac, 0.0)))
        t["share_from"] = "fit"
        if 0.0 < t.get("gate_share", -1.0) < 0.5:
            whole = t["I_whole"]
            lines[k]["I"] = t["gate_share"] * whole
            lines[i]["I"] = whole - lines[k]["I"]
            t.update({"I": lines[k]["I"], "I_main": lines[i]["I"], "share_from": "gates"})
"""),
])

edit(GEN, [
    ("""        out.append("kept %.2f -> %.2f keV: I %.2f, scheme %.2f; the %.2f keV line then I %.2f, scheme %.2f; the whole "
                   "peak read as that line alone %.2f" % (t["upper"], t["lower"], t["I"], hid["relative_intensity"],
                                                          main["energy_keV"], t["I_main"], main["relative_intensity"],
                                                          t["I_whole"]))
""", """        out.append("kept %.2f -> %.2f keV, with the %s share: I %.2f, scheme %.2f; the %.2f keV line then I %.2f, scheme "
                   "%.2f; the whole peak read as that line alone %.2f"
                   % (t["upper"], t["lower"], "gates'" if t.get("share_from") == "gates" else "fit's", t["I"],
                      hid["relative_intensity"], main["energy_keV"], t["I_main"], main["relative_intensity"],
                      t["I_whole"]))
"""),
])
