"""Lint fixes and the half-life line selection."""
from pathlib import Path

S = Path("tasks/active/gamma-decay-scheme")

# --- solve.py: only lines that die away while the beam is off date the parent
p = S / "solution" / "solve.py"
s = p.read_text(encoding="utf-8")
old = """    items = sorted(peaks.items, key=lambda p: -p["area"])[:4]
    off = np.arange(N_BINS // 3, N_BINS)
    best = (None, half_life_of(items, off))
    t_parent = best[1]
"""
new = """    off = np.arange(N_BINS // 3, N_BINS)
    # A line of a longer-lived activity on the tape, or of the room, does not fall by half over the beam-off time.
    falling = [p for p in peaks.items if p["curve"][off[0]] > 2.0 * p["curve"][off[-1]]]
    items = sorted(falling, key=lambda p: -p["area"])[:4]
    t_parent = half_life_of(items, off)
"""
assert old in s
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline="\n")

# --- generate.py: the audit's closeness test, in a form that is no tolerance of the judge's
old = 'print("near non-parent lines (<6 keV):", [(a, b) for a in energies for b in others if abs(a - b) < 6.0])'
new = 'print("near non-parent lines (<6 keV):", [(a, b) for a in energies for b in others if b - 6.0 < a < b + 6.0])'
for gen in (S / "tests" / "generate.py", Path("work/gamma-decay-scheme/v1/generate_draft.py")):
    g = gen.read_text(encoding="utf-8")
    assert old in g
    gen.write_text(g.replace(old, new), encoding="utf-8", newline="\n")

# --- NOTES.md
n = S / "environment" / "data" / "NOTES.md"
t = n.read_text(encoding="utf-8")
old = "Lines starting with `#` are comments. The first comment of each data file repeats nothing you need; the second and third say what the columns are.\n"
new = "Lines starting with `#` are comments.\n"
assert old in t
n.write_text(t.replace(old, new), encoding="utf-8", newline="\n")

# --- instruction.md
n = S / "instruction.md"
t = n.read_text(encoding="utf-8")
old = "The checker compares the file with the correct scheme. `levels_keV` must"
new = "`levels_keV` must"
assert old in t
n.write_text(t.replace(old, new), encoding="utf-8", newline="\n")

# --- requirements.json
n = S / "tests" / "requirements.json"
t = n.read_text(encoding="utf-8")
old = """    {
      "id": "R10",
"""
new = """    {
      "id": "R11",
      "quote": "The parent β⁻ decays to a daughter nucleus whose excited levels have never been measured, and we need the daughter's level scheme from this run.",
      "tests": ["test_levels", "test_transitions_placed"]
    },
    {
      "id": "R10",
"""
assert old in t
n.write_text(t.replace(old, new), encoding="utf-8", newline="\n")

# --- test_outputs.py: requirement numbers live in requirements.json only
n = S / "tests" / "test_outputs.py"
t = n.read_text(encoding="utf-8")
for tag in ("R1, R5, R7: ", "R2, R8: ", "R3, R8: ", "R4, R8: ", "R5, R8: ", "R6, R8: "):
    assert tag in t
    t = t.replace(tag, "")
n.write_text(t, encoding="utf-8", newline="\n")
print("done")
