"""One intensity band; the level differences that fall on peaks that are no transitions, written to checks.txt."""
from pathlib import Path

S = Path("tasks/active/gamma-decay-scheme")

# --- instruction.md and requirements.json: the absolute band never applies, the weakest transition is above 1
old_i = "is within 25% of the right value or within 0.15 of it, whichever allows more."
new_i = "is within 25% of the right value."
n = S / "instruction.md"
t = n.read_text(encoding="utf-8")
assert old_i in t
n.write_text(t.replace(old_i, new_i), encoding="utf-8", newline="\n")
n = S / "tests" / "requirements.json"
t = n.read_text(encoding="utf-8")
assert old_i in t
n.write_text(t.replace(old_i, new_i), encoding="utf-8", newline="\n")

# --- test_outputs.py
n = S / "tests" / "test_outputs.py"
t = n.read_text(encoding="utf-8")
old = '''INTENSITY = Decimal("0.25")          # instruction.md: a relative intensity within 25% of the right value ...
INTENSITY_ABS = Decimal("0.15")      # ... or within 0.15 of it, whichever allows more
'''
new = '''INTENSITY = Decimal("0.25")          # instruction.md: a relative intensity within 25% of the right value
'''
assert old in t
t = t.replace(old, new)
old = '''    """every relative intensity within 25% of the right value or 0.15 of it, whichever allows more."""
    for want, t in matched():
        right = Decimal(str(want["relative_intensity"]))
        tol = max(right * INTENSITY, INTENSITY_ABS)
        assert J.within(t["relative_intensity"], right, tol), \\
            "relative_intensity %r for the transition of %r keV, right value %s" % (t["relative_intensity"], want["energy_keV"], right)
'''
new = '''    """every relative intensity within 25% of the right value."""
    for want, t in matched():
        right = Decimal(str(want["relative_intensity"]))
        assert J.within(t["relative_intensity"], right, right * INTENSITY), \\
            "relative_intensity %r for the transition of %r keV, right value %s" % (t["relative_intensity"], want["energy_keV"], right)
'''
assert old in t
t = t.replace(old, new)
n.write_text(t, encoding="utf-8", newline="\n")

# --- generate.py: level differences that land on peaks of another origin
old = '''    good = [(m, p) for _, _, m, p in diag["strengths"]]
    ratio = np.array([m / p for m, p in good])
    shifts = []
'''
new = '''    energy = {name: v[0] for name, v in TARGET.items()}
    energy["g"] = 0.0
    direct = {(name, final) for name, v in TARGET.items() for final, _ in v[2]}
    origin = [(e, "room line") for e in ROOM] + [(511.0, "annihilation line")]
    origin += [(e, "line of the daughter's own decay") for e, _, _ in Walk(GRANDDAUGHTER).lines]
    origin += [(e, "line of the isobar") for e, _, _ in Walk(ISOBAR).lines]
    for t in expected["transitions"]:
        if t["energy_keV"] > 1300.0:
            origin += [(t["energy_keV"] - 511.0, "single-escape peak of %.1f" % t["energy_keV"]),
                       (t["energy_keV"] - 1022.0, "double-escape peak of %.1f" % t["energy_keV"])]
    out += ["", "[differences of two levels with no transition between them that fall on a peak of another origin]",
            "    upper     lower  difference      peak  what the peak is"]
    for a in energy:
        for b in energy:
            d = energy[a] - energy[b]
            if d > 0.0 and (a, b) not in direct:
                for e, what in sorted(origin):
                    if e - 0.5 <= d <= e + 0.5:
                        out.append("%9.1f %9.1f  %10.1f %9.2f  %s" % (energy[a], energy[b], d, e, what))
    good = [(m, p) for _, _, m, p in diag["strengths"]]
    ratio = np.array([m / p for m, p in good])
    shifts = []
'''
for gen in (S / "tests" / "generate.py", Path("work/gamma-decay-scheme/v1/generate_draft.py")):
    g = gen.read_text(encoding="utf-8")
    assert old in g
    gen.write_text(g.replace(old, new), encoding="utf-8", newline="\n")
print("done")
