from pathlib import Path
gen = Path("work/gamma-decay-scheme/v1/generate_draft.py")
t = gen.read_text(encoding="utf-8")
old = "    width = max(1, int(round(float(fwhm(e)) / 2.3548 / 0.5)))\n"
new = "    width = 8      # multiple scattering and electron binding round the Compton edge over about 4 keV\n"
assert old in t
gen.write_text(t.replace(old, new), encoding="utf-8", newline="\n")
Path("tasks/active/gamma-decay-scheme/tests/generate.py").write_text(gen.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")

sol = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
t = sol.read_text(encoding="utf-8")

# Width filter in classify.
old = """        if abs(p["E"] - 511.0) < 2.5:
            excluded.append(("annihilation", p["E"], p["I"]))
"""
new = """        if abs(p["E"] - 511.0) < 2.5:
            excluded.append(("annihilation", p["E"], p["I"]))
        elif p["width"] > 1.6:
            excluded.append(("too broad for a line", p["E"], p["I"]))
"""
assert old in t
t = t.replace(old, new)

# Doublet membership from the gated centroids.
a = t.index("        clusters = []\n        if len(partners) >= 2:")
b = t.index("    DIAG[\"doublet_tests\"] = report")
new = """        firm = [r for r in partners if r["err"] < 0.12]
        moved, low, high = False, None, None
        if len(firm) >= 2:
            cmin = min(r["centroid"] for r in firm)
            cmax = max(r["centroid"] for r in firm)
            def mean_of(rows):
                w = np.array([1.0 / r["err"] ** 2 for r in rows])
                return float(np.sum(w * np.array([r["centroid"] for r in rows])) / w.sum())
            low = mean_of([r for r in firm if r["centroid"] <= cmin + 0.15])
            high = mean_of([r for r in firm if r["centroid"] >= cmax - 0.15])
            spread = np.array([r["centroid"] for r in firm])
            chi = float(np.sum(((spread - mean_of(firm)) / np.array([r["err"] for r in firm])) ** 2)) / (len(firm) - 1)
            moved = high - low > 0.6 and chi > 4.0
        report.append({"E": e, "width": p["width"], "self_net": self_n, "self_strength": self_strength,
                       "gates": [(r["gate"], r["centroid"], r["err"]) for r in partners], "moved": moved,
                       "low": low, "high": high})
        if not (moved or self_flag):
            q = dict(p)
            q["peak"] = e
            q["member"] = None
            out.append(q)
            continue
        # A gate sees the lower member only, the upper one only, or both (a centroid between the two).
        span = high - low
        sees = {}
        for r in partners:
            margin = 2.0 * r["err"]
            if r["centroid"] + margin < low + 0.3 * span:
                sees[r["gate"]] = "low"
            elif r["centroid"] - margin > high - 0.3 * span:
                sees[r["gate"]] = "high"
            elif r["centroid"] - margin > low + 0.3 * span and r["centroid"] + margin < high - 0.3 * span:
                sees[r["gate"]] = "both"
        for name, value in (("low", low), ("high", high)):
            q = dict(p)
            q["peak"] = e
            q["member"] = name
            q["E"] = value
            q["err"] = 0.08
            q["sees"] = sees
            q["I"] = 0.5 * p["I"]
            q["self"] = self_flag
            out.append(q)
"""
t = t[:a] + new + t[b:]

old = t[t.index("            # A centroid in a gate says which member of a doublet the gate belongs to.\n"):t.index("            flags[i][j] = flags[j][i] = f\n    return flags, strength, delayed_pairs")]
new = """            # For a member of a doublet only a centroid in a gate says which of the two a partner goes with.
            for x, y in ((a, b), (b, a)):
                if x["member"] and f == 1:
                    seen = x["sees"].get(y["peak"])
                    f = None if seen is None else (1 if seen in (x["member"], "both") else 0)
"""
t = t.replace(old, new)
sol.write_text(t, encoding="utf-8", newline="\n")
