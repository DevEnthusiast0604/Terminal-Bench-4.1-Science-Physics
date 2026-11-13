"""v13: record every other scheme with as few levels as the one kept (the lines it places elsewhere and the peaks whose
coincidences tell the two apart), and print it in checks.txt with the weak member's I from each way of sharing the
peak. Exact-match replacements in solution/solve.py and tests/generate.py; run from the folder root."""
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


edit(SOLVE, [("""    sol = min(solutions, key=disagreement)
""", """    sol = min(solutions, key=disagreement)
    # Any other scheme with as few levels: the lines it places elsewhere, and the peaks whose coincidences with them
    # tell it from the one kept, measured and predicted per gamma ray of the line that moves.
    DIAG["minimal_schemes"] = []
    pred_sol = predicted_strength(lines, sol)
    for cand in solutions:
        if cand is sol:
            continue
        pred = predicted_strength(lines, cand)
        moved = [i for i in range(len(lines))
                 if any(abs(cand[0][cand[1][i][s]] - sol[0][sol[1][i][s]]) > 0.5 for s in (0, 1))]
        rows = []
        for m in moved:
            lm = lines[m]
            for pk in sorted({l["peak"] for l in lines} - {lm["peak"]}):
                on = [k for k in range(len(lines)) if lines[k]["peak"] == pk]
                kept = sum(pred_sol[m][k] * min(lm["I"], lines[k]["I"]) for k in on) / lm["I"]
                other = sum(pred[m][k] * min(lm["I"], lines[k]["I"]) for k in on) / lm["I"]
                if abs(kept - other) < 0.05:
                    continue
                net, var = coin.net(lm["peak"], pk)
                dn, dv, _, _ = coin.delayed(lm["peak"], pk)
                if abs(dn) > 6.0 * math.sqrt(max(dv, 1.0)) and abs(dn) > 25.0:
                    net, var = net + abs(dn), var + dv
                full = k_scale * float(eff(lm["peak"])) * float(eff(pk)) * lm["I"]
                rows.append({"E": lm["E"], "peak": pk, "measured": net / full, "err": math.sqrt(max(var, 1.0)) / full,
                             "kept": kept, "other": other})
        DIAG["minimal_schemes"].append({
            "levels": sorted(cand[0]), "disagreement": disagreement(cand), "disagreement_kept": disagreement(sol),
            "moved": [{"E": lines[m]["E"], "kept": [sol[0][sol[1][m][0]], sol[0][sol[1][m][1]]],
                       "other": [cand[0][cand[1][m][0]], cand[0][cand[1][m][1]]]} for m in moved],
            "pairs": sorted(rows, key=lambda r: -abs(r["kept"] - r["other"]) / r["err"])})
""")])

edit(GEN, [("""    out.append("instruction.md asks for the scheme with the fewest levels: the one with %d" % len(expected["levels_keV"]))
""", """    out.append("instruction.md asks for the scheme with the fewest levels: the one with %d" % len(expected["levels_keV"]))
    for alt in diag["minimal_schemes"]:
        out.append("another scheme with %d levels places %s" % (len(alt["levels"]), "; ".join(
            "%.1f keV from %.1f to %.1f keV, where the one kept has it from %.1f to %.1f keV"
            % (m["E"], m["other"][0], m["other"][1], m["kept"][0], m["kept"][1]) for m in alt["moved"])))
        out.append("  coincidence strengths, measured against predicted, squared differences summed over the pairs: %.2f for "
                   "the scheme kept, %.2f for this one" % (alt["disagreement_kept"], alt["disagreement"]))
        for r in alt["pairs"][:4]:
            out.append("  %.1f keV with the peak at %.1f keV, per %.1f keV gamma ray: measured %.3f +- %.3f, the scheme "
                       "kept predicts %.3f, this one %.3f" % (r["E"], r["peak"], r["E"], r["measured"], r["err"],
                                                              r["kept"], r["other"]))
"""), ("""        if "gate_share" in t:
            out.append("the gates on the lines below the two members, %s, give a share of %.4f +- %.4f"
                       % (", ".join("%.1f keV (%.2f of the strong member's cascade, %.2f of the weak one's)"
                                    % (g[0], g[3], g[4]) for g in t["gates"]), t["gate_share"], t["gate_err"]))
""", """        if "gate_share" in t:
            out.append("the gates on the lines below the two members, %s, give a share of %.4f +- %.4f"
                       % (", ".join("%.1f keV (%.2f of the strong member's cascade, %.2f of the weak one's)"
                                    % (g[0], g[3], g[4]) for g in t["gates"]), t["gate_share"], t["gate_err"]))
        out.append("the weak member's I from each share of the whole peak's %.2f: %.2f with the tail, %.2f with Gaussians "
                   "alone%s; scheme %.2f" % (t["I_whole"], t["share"] * t["I_whole"], t["share_gauss"] * t["I_whole"],
                                             ", %.2f from the gates" % (t["gate_share"] * t["I_whole"])
                                             if "gate_share" in t else "", hid["relative_intensity"]))
""")])
