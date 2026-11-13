"""Fill the template files and add the independent-route evidence."""
import re
import shutil
from pathlib import Path

S = Path("tasks/active/gamma-decay-scheme")

# --- task.toml
t = (S / "task.toml").read_text(encoding="utf-8")
t = t.replace('description = "<one line, what the agent must produce>"',
              'description = "Build the level scheme of a daughter nucleus from the singles and gamma-gamma coincidence data of a moving-tape beta-decay run and write it to /app/output/decay_scheme.json."')
t = t.replace('authors = [{ name = "<Name>", email = "<email>" }]', 'authors = [{ name = "Arnulfo Lujan", email = "arnulfo.lujan@outlook.com" }]')
t = t.replace('keywords = ["<domain>", "<tool>", "<skill>"]',
              'keywords = ["nuclear-spectroscopy", "beta-decay", "gamma-gamma-coincidence", "level-scheme", "hpge", "isomer", "true-coincidence-summing"]')
t = t.replace('author_name = "<Name>"', 'author_name = "Arnulfo Lujan"')
t = t.replace('author_email = "<email>"', 'author_email = "arnulfo.lujan@outlook.com"')
t = t.replace('author_github = "<github-username>"', 'author_github = "arnulfo"')
t = t.replace('author_organization = "<optional>"\n', '')
t = t.replace('category = "Software"', 'category = "Science"')
t = t.replace('subcategory = "<subdomain>"', 'subcategory = "Physics"')
t = t.replace('tags = ["<specific>", "<specific>", "<specific>"]',
              'tags = ["nuclear-spectroscopy", "decay-scheme", "gamma-gamma-coincidence", "true-coincidence-summing", "isomer", "energy-calibration"]')
t = t.replace('expert_time_estimate_hours = 3', 'expert_time_estimate_hours = 7')
assert "<" not in re.sub(r"<<<|<<|<\(|< \"|<\s*\"\$f\"|<<", "", t.split("[[verifier.collect]]")[0]), "placeholder left in task.toml head"
(S / "task.toml").write_text(t, encoding="utf-8", newline="\n")

# --- environment/Dockerfile
d = (S / "environment" / "Dockerfile").read_text(encoding="utf-8")
old = "WORKDIR /app\n# <COPY the task inputs, never the expected outputs, e.g. COPY data/ /app/data/>\n"
new = ("# Numerical libraries for the analysis.\n"
       "RUN pip install --no-cache-dir numpy==2.3.3 scipy==1.18.1\n\n"
       "WORKDIR /app\n"
       "# The run's data files and the station's notes.\n"
       "COPY data/ /app/data/\n")
assert old in d
d = d.replace(old, new)
(S / "environment" / "Dockerfile").write_text(d, encoding="utf-8", newline="\n")

# --- solution/solve.sh
sh = (S / "solution" / "solve.sh").read_text(encoding="utf-8")
sh = sh.replace('python3 "$(dirname "$0")/solve.py" "<input-path>" /app/output', 'python3 "$(dirname "$0")/solve.py" /app/data /app/output')
sh = sh.replace('test -s "/app/output/<deliverable-file>"', 'test -s "/app/output/decay_scheme.json"')
(S / "solution" / "solve.sh").write_text(sh, encoding="utf-8", newline="\n")

# --- cheat: a data task keeps symlink-answers only
c = (S / "cheat" / "symlink-answers" / "solve.sh").read_text(encoding="utf-8")
c = c.replace('TARGET="/app/output/<deliverable-file>"', 'TARGET="/app/output/decay_scheme.json"')
(S / "cheat" / "symlink-answers" / "solve.sh").write_text(c, encoding="utf-8", newline="\n")
shutil.rmtree(S / "cheat" / "forge-reward", ignore_errors=True)
(S / "tests" / "emit.py").unlink(missing_ok=True)

# --- solve.py: the half-life line by line, and the isomer's by the line above it
p = S / "solution" / "solve.py"
s = p.read_text(encoding="utf-8")
old = """    t_parent = best[1]
    shapes = cycle_shapes(t_parent)
    base = np.column_stack([shapes["parent"], shapes["ramp"], shapes["flat"]])
"""
new = """    t_parent = best[1]
    DIAG["half_life_by_line"] = [(p["E"], half_life_of([p], off)) for p in items]
    shapes = cycle_shapes(t_parent)
    base = np.column_stack([shapes["parent"], shapes["ramp"], shapes["flat"]])
"""
assert old in s
s = s.replace(old, new)
old = """    items = sorted(peaks.items, key=lambda p: -p["area"])[:4]
    off = np.arange(N_BINS // 3, N_BINS)
    best = None
    for t in np.arange(1.0, 20.0, 0.005):
        shapes = cycle_shapes_cached(round(float(t), 3))
        total = 0.0
        for p in items:
            y, e = p["curve"][off], p["curve_err"][off]
            a = np.column_stack([shapes["parent"][off], np.ones(len(off))]) / e[:, None]
            beta = np.linalg.lstsq(a, y / e, rcond=None)[0]
            total += float(np.sum((y / e - a @ beta) ** 2))
        if best is None or total < best[0]:
            best = (total, float(t))
"""
new = """    items = sorted(peaks.items, key=lambda p: -p["area"])[:4]
    off = np.arange(N_BINS // 3, N_BINS)
    best = (None, half_life_of(items, off))
"""
assert old in s
s = s.replace(old, new)
old = 'def separate_activities(peaks):\n'
new = '''def half_life_of(items, off):
    """The half-life that fits the beam-off time curves of these peaks best, each on its own flat background."""
    best = None
    for t in np.arange(1.0, 20.0, 0.005):
        shapes = cycle_shapes_cached(round(float(t), 3))
        total = 0.0
        for p in items:
            y, e = p["curve"][off], p["curve_err"][off]
            a = np.column_stack([shapes["parent"][off], np.ones(len(off))]) / e[:, None]
            beta = np.linalg.lstsq(a, y / e, rcond=None)[0]
            total += float(np.sum((y / e - a @ beta) ** 2))
        if best is None or total < best[0]:
            best = (total, float(t))
    return best[1]


def separate_activities(peaks):
'''
assert old in s
s = s.replace(old, new)
a = s.index("    ev = coin.ev\n    pairs = [(a, b) for a, b, _ in delayed_pairs]\n")
b = s.index("    return levels[lev], best_t[1], lev\n")
new = '''    t = 60.0 + 20.0 * (np.arange(32) + 0.5)

    def delay_spectrum(pairs):
        ev = coin.ev
        plus = np.zeros(32)
        minus = np.zeros(32)
        for first, last in pairs:
            sa, sb = coin.windows[first][0], coin.windows[last][0]
            lo, hi, sign = (sa, sb, 1) if first < last else (sb, sa, -1)
            mask = (ev[:, 0] >= lo[0]) & (ev[:, 0] <= lo[-1]) & (ev[:, 1] >= hi[0]) & (ev[:, 1] <= hi[-1])
            for i, j, d, c in ev[mask]:
                k = int((abs(d) - 60) // 20)
                if d * sign > 0:
                    plus[k] += c
                else:
                    minus[k] += c
        return plus, minus

    def fit(plus, minus):
        # The other side of zero holds only chance pairs, so its mean is the background.
        base = minus.mean()
        w = 1.0 / np.sqrt(np.maximum(plus, 1.0))
        best = None
        for tt in np.arange(20.0, 600.0, 0.5):
            a = 2.0 ** (-t / tt) * w
            amp = float(np.sum(a * (plus - base) * w) / np.sum(a * a))
            chi = float(np.sum(((plus - base) * w - amp * a) ** 2))
            if best is None or chi < best[0]:
                best = (chi, float(tt))
        return best[1]

    pairs = sorted({(a, b) for a, b, _ in delayed_pairs})
    plus, minus = delay_spectrum(pairs)
    half = fit(plus, minus)
    DIAG["isomer_time_spectrum"] = {"t_ns": t.tolist(), "plus": plus.tolist(), "minus": minus.tolist()}
    DIAG["isomer_by_line_above"] = [(f, fit(*delay_spectrum([q for q in pairs if q[0] == f])))
                                    for f in sorted({q[0] for q in pairs})]
'''
s = s[:a] + new + s[b:]
s = s.replace("    return levels[lev], best_t[1], lev\n", "    return levels[lev], half, lev\n")
p.write_text(s, encoding="utf-8", newline="\n")

# --- generate: the independent-route lines
gen = Path("work/gamma-decay-scheme/v1/generate_draft.py")
g = gen.read_text(encoding="utf-8")
old = """    good = [(m, p) for _, _, m, p in diag["strengths"]]
    ratio = np.array([m / p for m, p in good])
    out += ["", "[coincidences against the final scheme]",
            "pairs the scheme predicts at a strength above 0.3: %d; measured over predicted: mean %.3f, rms %.3f"
            % (len(good), float(ratio.mean()), float(ratio.std())), "",
"""
new = """    good = [(m, p) for _, _, m, p in diag["strengths"]]
    ratio = np.array([m / p for m, p in good])
    shifts = []
    for r in diag["doublet_tests"]:
        if not r["moved"]:
            shifts += [c - r["E"] for _, c, err in r["gates"] if err < 0.12]
    shifts = np.array(shifts)
    out += ["", "[other routes to the same numbers]",
            "intensities from coincidences instead of singles: %d pairs the scheme predicts at a strength above 0.3,"
            % len(good),
            "measured over predicted: mean %.3f, rms %.3f, furthest from 1 by %.3f"
            % (float(ratio.mean()), float(ratio.std()), float(np.abs(ratio - 1.0).max())),
            "energies from gated spectra instead of singles: %d gates, offset %.3f keV, rms about it %.3f keV, largest %.3f keV"
            % (len(shifts), float(shifts.mean()), float(shifts.std()), float(np.abs(shifts - shifts.mean()).max())),
            "parent half-life line by line: " + ", ".join("%.1f keV %.3f s" % (e, v) for e, v in diag["half_life_by_line"]),
            "isomer half-life by the line above it: " + ", ".join("%.1f keV %.1f ns" % (e, v) for e, v in diag["isomer_by_line_above"]),
            "",
"""
assert old in g
g = g.replace(old, new)
gen.write_text(g, encoding="utf-8", newline="\n")
(S / "tests" / "generate.py").write_text(g, encoding="utf-8", newline="\n")
print("done")
