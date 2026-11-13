from pathlib import Path
sol = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
t = sol.read_text(encoding="utf-8")


def sub(old, new):
    global t
    assert t.count(old) >= 1, old
    t = t.replace(old, new, 1)


# Remove the development counters.
sub("DEPTHS = {}\nREJECTS = []\n\n\n", "")
sub("        DEPTHS[pos] = DEPTHS.get(pos, 0) + 1\n", "")
sub("""                if flags[i][k] == 1 and not p:
                    REJECTS.append(("flag 1 without a path", lines[i]["E"], lines[k]["E"]))
                    return
                if flags[i][k] == 0 and p:
                    REJECTS.append(("flag 0 with a path", lines[i]["E"], lines[k]["E"]))
                    return
""", """                if flags[i][k] == 1 and not p:
                    return
                if flags[i][k] == 0 and p:
                    return
""")
sub("""            if into > 1.2 * outof + 0.5:
                REJECTS.append(("balance", levels[a], into, outof))
                return
""", """            if into > 1.2 * outof + 0.5:
                return
""")
sub("""                if not below:
                    REJECTS.append(("no decay", levels[a]))
                    return
""", """                if not below:
                    return
""")
sub("WINDOW_NS = 100.0\n", "")
sub("""    final = [p for p in keep if p["I"] >= 0.35]
    # The strongest line sets the scale of the coincidence strengths.
    return final, scale
""", """    # A line must clear the reporting floor within what its peak's corrections leave uncertain.
    return [p for p in keep if p["I"] >= 0.7 * FLOOR]
""")
sub("    lines, scale = classify(peaks, coin, eff, ratios)\n",
    "    lines = classify(peaks, coin, eff, ratios)\n"
    "    DIAG[\"mixed_peaks\"] = [{\"E\": p[\"E\"], \"I_parent\": p[\"I\"], \"I_whole_peak\": p[\"I\"] / p[\"share\"], \"share\": p[\"share\"]}\n"
    "                            for p in lines if p[\"share\"] < 0.9]\n")
sub("""    all_e = [p["E"] for p in peaks.items]
    coin.set_windows(all_e)
""", """    coin.set_windows([p["E"] for p in peaks.items])
""")

# main: count the schemes with one level more, keep the agreement of the final scheme with the coincidences.
a = t.index("    solutions = []\n    for max_levels in range(2, 24):")
b = t.index("    lines = split_intensities(lines, sol)\n")
new = """    solutions = []
    for max_levels in range(2, 24):
        solutions = search(lines, flags, ceiling, order, max_levels)
        DIAG.setdefault("search_counts", []).append((max_levels, len(solutions)))
        if solutions:
            break
    if not solutions:
        raise SystemExit("no scheme agrees with the data")
    DIAG["search_counts"].append((max_levels + 1, len(search(lines, flags, ceiling, order, max_levels + 1))))

    def disagreement(candidate):
        pred = predicted_strength(lines, candidate)
        return sum((strength[i][j] - pred[i][j]) ** 2 for i in range(len(lines)) for j in range(i + 1, len(lines))
                   if lines[i]["peak"] != lines[j]["peak"])

    sol = min(solutions, key=disagreement)
"""
t = t[:a] + new + t[b:]
sub("    flags, strength, upper, delayed_pairs = coincidence_flags(lines, coin, eff, k_scale)\n",
    "    flags, strength, ceiling, delayed_pairs = coincidence_flags(lines, coin, eff, k_scale)\n")
sub("def search(lines, flags, upper, order, max_levels, limit=400000):",
    "def search(lines, flags, ceiling, order, max_levels, limit=400000):")
sub("if 0.25 * ig * frac / min(ig, ik) > upper[g][k]:", "if 0.25 * ig * frac / min(ig, ik) > ceiling[g][k]:")

# After the final intensities: how well the scheme predicts the measured strengths.
sub("""    level_values = refine_levels(lines, sol)
""", """    level_values = refine_levels(lines, sol)
    pred = predicted_strength(lines, sol)
    DIAG["strengths"] = [(lines[i]["E"], lines[j]["E"], strength[i][j], pred[i][j]) for i in range(len(lines))
                         for j in range(i + 1, len(lines)) if lines[i]["peak"] != lines[j]["peak"] and pred[i][j] > 0.3
                         and not lines[i]["member"] and not lines[j]["member"]]
""")
sol.write_text(t, encoding="utf-8", newline="\n")

# The generator: run the reduction at the end and write the evidence.
gen = Path("work/gamma-decay-scheme/v1/generate_draft.py")
g = gen.read_text(encoding="utf-8")
old = """    with open(TASK / "tests" / "expected.json", "w", newline="\\n") as fh:
        json.dump(expected, fh, indent=1)
        fh.write("\\n")
    return
"""
new = """    with open(TASK / "tests" / "expected.json", "w", newline="\\n") as fh:
        json.dump(expected, fh, indent=1)
        fh.write("\\n")
    with tempfile.TemporaryDirectory() as tmp:
        diag_path = Path(tmp) / "diag.json"
        subprocess.run([sys.executable, "-X", "utf8", "-I", "-B", str(TASK / "solution" / "solve.py"), str(DATA), tmp,
                        "--diag", str(diag_path)], check=True)
        result = json.load(open(Path(tmp) / "decay_scheme.json"))
        diag = json.load(open(diag_path))
    write_checks(expected, result, diag, phi, fw, n1, n2, len(rows))
"""
assert old in g
g = g.replace(old, new)
old = "def main():\n    rng = np.random.default_rng(SEED)\n"
new = '''def write_checks(expected, result, diag, phi, fw, n1, n2, n3):
    """tests/checks.txt: the reference reduction's result on the shipped data against the scheme, and what each
    wrong route would give, every number measured from those files."""
    out = ["# %s" % CANARY,
           "# Written by tests/generate.py. The reference reduction (solution/solve.py) reads only the files in",
           "# environment/data, and its result is compared here with the scheme in tests/expected.json.", ""]
    level_dev = [abs(a - b) for a, b in zip(result["levels_keV"], expected["levels_keV"])]
    assert len(result["levels_keV"]) == len(expected["levels_keV"]) and max(level_dev) <= 0.5
    rows = []
    for t in expected["transitions"]:
        hits = [r for r in result["transitions"] if abs(r["from_keV"] - t["from_keV"]) <= 0.5
                and abs(r["to_keV"] - t["to_keV"]) <= 0.5]
        assert len(hits) == 1, t
        rows.append((t, hits[0]))
    assert len(result["transitions"]) == len(expected["transitions"])
    e_dev = max(abs(r["energy_keV"] - t["energy_keV"]) for t, r in rows)
    i_dev = max(abs(r["relative_intensity"] - t["relative_intensity"]) / t["relative_intensity"] for t, r in rows)
    hl = abs(result["parent_half_life_s"] - expected["parent_half_life_s"]) / expected["parent_half_life_s"]
    iso = abs(result["isomer"]["half_life_ns"] - expected["isomer"]["half_life_ns"]) / expected["isomer"]["half_life_ns"]
    iso_e = abs(result["isomer"]["level_keV"] - expected["isomer"]["level_keV"])
    assert e_dev <= 0.5 and i_dev <= 0.25 and hl <= 0.02 and iso <= 0.08 and iso_e <= 0.5
    out += ["[reference against the scheme]",
            "levels: %d in both, largest difference %.3f keV, tolerance 0.5 keV" % (len(level_dev), max(level_dev)),
            "transitions: %d in both, every one between the same two levels" % len(rows),
            "gamma-ray energies: largest difference %.3f keV, tolerance 0.5 keV" % e_dev,
            "relative intensities: largest difference %.1f percent, tolerance 25 percent" % (100.0 * i_dev),
            "parent half-life: %.3f s against %.3f s, %.2f percent, tolerance 2 percent"
            % (result["parent_half_life_s"], expected["parent_half_life_s"], 100.0 * hl),
            "isomer level: %.2f keV against %.2f keV, tolerance 0.5 keV" % (result["isomer"]["level_keV"], expected["isomer"]["level_keV"]),
            "isomer half-life: %.1f ns against %.1f ns, %.1f percent, tolerance 8 percent"
            % (result["isomer"]["half_life_ns"], expected["isomer"]["half_life_ns"], 100.0 * iso), ""]
    out += ["  from_keV    to_keV   E_scheme  E_reference   I_scheme  I_reference"]
    for t, r in rows:
        out.append("%9.2f %9.2f %10.2f %12.2f %10.2f %12.2f" % (t["from_keV"], t["to_keV"], t["energy_keV"], r["energy_keV"],
                                                               t["relative_intensity"], r["relative_intensity"]))
    off = diag["gain_offset_keV_at"]
    out += ["", "[gain of the production run]",
            "source-run gain against the source tables: rms %.3f keV" % diag["source_gain_rms_keV"],
            "room lines read with the source-run gain lie off by %.2f keV at 500 keV, %.2f keV at 1500 keV, %.2f keV at 2500 keV"
            % (off["500.0"], off["1500.0"], off["2500.0"]),
            "room lines after the correction: rms %.3f keV" % diag["gain_rms_keV"], ""]
    out += ["[placement search]"]
    for m, n in diag["search_counts"][-3:]:
        out.append("schemes with at most %d levels, ground state included: %d" % (m, n))
    out += ["", "[sum peaks: area of the peak against the coincidence count of the cascade divided by 7]",
            "    E_keV  I_whole_peak  I_after_subtraction  cascade"]
    for s in diag["sum_candidates"]:
        if s["I_before"] - s["I_after"] > 0.15:
            parts = " ".join("%.1f+%.1f" % (a, b) for a, b, n in s["parts"] if n > 50.0)
            out.append("%9.2f %13.2f %20.2f  %s" % (s["E"], s["I_before"], s["I_after"], parts))
    out += ["", "[other peaks of the parent's time profile that are not transitions]"]
    for kind, e, i in sorted(diag["excluded"], key=lambda r: r[1]):
        if kind.startswith("escape") and i > 0.2:
            out.append("%9.2f  I %.2f  %s peak" % (e, i, kind.split()[1].upper()))
    out += ["", "[peaks that are two transitions]", "    E_keV  width/resolution  self_coincidence_count  centroid_by_gate"]
    for r in diag["doublet_tests"]:
        if r["moved"]:
            gates = " ".join("%.1f:%.2f" % (g, c) for g, c, err in r["gates"] if err < 0.12)
            out.append("%9.2f %17.2f %23.0f  %s" % (r["E"], r["width"], r["self_net"], gates))
    widths = [r["width"] for r in diag["doublet_tests"] if not r["moved"]]
    out += ["other candidate lines: width/resolution from %.2f to %.2f, largest self-coincidence strength %.3f"
            % (min(widths), max(widths), max(abs(r["self_strength"]) for r in diag["doublet_tests"] if not r["moved"])), ""]
    out += ["[peak shared with the daughter's own decay]"]
    for m in diag["mixed_peaks"]:
        near = min(expected["transitions"], key=lambda t: abs(t["energy_keV"] - m["E"]))
        out.append("%.2f keV: parent's share %.2f; I from the parent's share %.2f, from the whole peak %.2f, scheme %.2f"
                   % (m["E"], m["share"], m["I_parent"], m["I_whole_peak"], near["relative_intensity"]))
    t = diag["isomer_time_spectrum"]
    out += ["", "[isomer]", "fraction of the pairs across the isomer inside the prompt window: %.3f" % fw,
            "delayed pairs of the lines across it, by delay in ns: delay, later line second, later line first"]
    for a, b, c in zip(t["t_ns"], t["plus"], t["minus"]):
        out.append("%6.0f %7.0f %7.0f" % (a, b, c))
    good = [(m, p) for _, _, m, p in diag["strengths"]]
    ratio = np.array([m / p for m, p in good])
    out += ["", "[coincidences against the final scheme]",
            "pairs the scheme predicts at a strength above 0.3: %d; measured over predicted: mean %.3f, rms %.3f"
            % (len(good), float(ratio.mean()), float(ratio.std())), "",
            "[files]", "cells in gg_prompt.txt %d, gg_random.txt %d, lines in gg_delayed.txt %d" % (n1, n2, n3),
            "daughter decays per parent decay within a cycle: %.3f" % phi]
    with open(TASK / "tests" / "checks.txt", "w", newline="\\n") as fh:
        fh.write("\\n".join(out) + "\\n")


def main():
    rng = np.random.default_rng(SEED)
'''
assert old in g
g = g.replace(old, new)
# Quiet by default: the audit prints only with --audit.
old = '''    print("daughter decays per parent decay in a cycle: %.3f" % phi)
    audit(w, w.lines, rel)
    if design_only:
'''
new = '''    if design_only:
        audit(w, w.lines, rel)
'''
assert old in g
g = g.replace(old, new)
old = '''    candidates = [(e, "line") for e in energies] + [(e, "other") for e in others]
    for _, _, _ in []:
        pass
'''
new = '''    candidates = [(e, "line") for e in energies] + [(e, "other") for e in others]
'''
assert old in g
g = g.replace(old, new)
old = '''python -X utf8 -I -B tests/generate.py

After writing the data it runs the reference reduction (solution/solve.py) on those files alone, compares its result
with the scheme by the judge's rules and writes the comparison to tests/checks.txt.
'''
new = '''python -X utf8 -I -B tests/generate.py            (--audit prints the design checks and writes nothing)

After writing the data it runs the reference reduction (solution/solve.py) on those files alone, compares its result
with the scheme by the judge's rules and writes the comparison to tests/checks.txt. It stops if they disagree.
'''
assert old in g
g = g.replace(old, new)
gen.write_text(g, encoding="utf-8", newline="\n")
Path("tasks/active/gamma-decay-scheme/tests/generate.py").write_text(g, encoding="utf-8", newline="\n")
print("edits applied")
