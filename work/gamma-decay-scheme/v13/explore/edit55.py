"""v13: the scheme drops v11's level at 2721.7 keV and gains one at 1399.8 keV, fed by the beta decay only, that
decays to 842.7 keV by a clean 557.1 keV line and to 318.4 keV by 1081.4 keV, 0.9 keV under E->B. The only line below
the weak one, 318.4 keV, lies below E->B as well, so no gate shows it alone. checks.txt gains the hidden-member test.
Exact-match replacements in tests/generate.py; run from the folder root."""
PATH = "tasks/active/gamma-decay-scheme/tests/generate.py"
s = open(PATH, encoding="utf-8", newline="").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)


rep("""# M -> H (511.0 keV) lies on the annihilation line and feeds about half of H. X -> Da (1081.4 keV) lies 0.9 keV
# under E -> B (1082.3 keV) with a tenth of its intensity: only the gates on the lines below each one tell them apart.
""", """# M -> H (511.0 keV) lies on the annihilation line and feeds about half of H. Y -> A (1081.4 keV) lies 0.9 keV
# under E -> B (1082.3 keV) with an eighth of its intensity, and the only line below it, A -> g, lies below E -> B as
# well: no gate shows it alone, and only the peak's shape and the gates' proportions tell the two apart.
""")
rep("""    "C": (1489.6, 3.0, [("B", 88), ("g", 12)]),
""", """    "C": (1489.6, 3.0, [("B", 88), ("g", 12)]),
    "Y": (1399.8, 1.9, [("B", 45), ("A", 55)]),
""")
rep("""    "X": (2721.7, 1.75, [("B", 55), ("Da", 45)]),
""", "")

rep("""    out += [""]
    out += ["[peaks shared with the daughter's own decay]"]
""", """    out += [""]
    shape = diag["line_shape"]
    out += ["[a weak transition under a strong line]",
            "line shape from %d lines standing alone (%s keV): tail %.3f of the area with a slope of %.2f sigma, width "
            "%.3f of the room lines' Gaussian width" % (len(shape["lines"]), " ".join("%.1f" % r["E"] for r in shape["lines"]),
                                                        shape["frac"], shape["tau_k"], shape["s_ratio"]),
            "a second member made up 0.9 or 1.3 keV from each of those lines takes an rms share of %.4f of the peak, "
            "at most %.4f" % (shape["phantom_rms"], shape["phantom_max"]),
            "differences of two levels with no transition between them, 0.4 to 1.6 keV from the centroid of a peak of "
            "I >= 4, and the share of a second member there:",
            "    upper     lower  difference      peak  offset  share_with_tail   error  share_Gaussians_alone  kept"]
    for t in diag["hidden_tests"]:
        out.append("%9.2f %9.2f %11.2f %9.2f %+7.2f %16.4f %7.4f %22.4f  %s"
                   % (t["upper"], t["lower"], t["E"], t["peak"], t["offset"], t["share"], t["sd"], t["share_gauss"],
                      "yes" if t["accepted"] else "no"))
    for t in diag["hidden_tests"]:
        if not t["accepted"]:
            continue
        hid = min(expected["transitions"], key=lambda r: abs(r["from_keV"] - t["upper"]) + abs(r["to_keV"] - t["lower"]))
        main = min((r for r in expected["transitions"] if r is not hid), key=lambda r: abs(r["energy_keV"] - t["line_E"]))
        out.append("kept %.2f -> %.2f keV: I %.2f, scheme %.2f; the %.2f keV line then I %.2f, scheme %.2f; the whole "
                   "peak read as that line alone %.2f" % (t["upper"], t["lower"], t["I"], hid["relative_intensity"],
                                                          main["energy_keV"], t["I_main"], main["relative_intensity"],
                                                          t["I_whole"]))
        out.append("the weak member's share of the peak: %.4f with the tail, %.4f with Gaussians alone, %.4f in the scheme"
                   % (t["share"], t["share_gauss"], hid["relative_intensity"] / (hid["relative_intensity"]
                                                                                 + main["relative_intensity"])))
        if "gate_share" in t:
            out.append("the gates on the lines below the two members, %s, give a share of %.4f +- %.4f"
                       % (", ".join("%.1f keV (%.2f of the strong member's cascade, %.2f of the weak one's)"
                                    % (g[0], g[3], g[4]) for g in t["gates"]), t["gate_share"], t["gate_err"]))
    out += [""]
    out += ["[peaks shared with the daughter's own decay]"]
""")

open(PATH, "w", encoding="utf-8", newline="").write(s)
print("generate.py edited")
