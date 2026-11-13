"""v8 (the reviewer's send-back of 2026-11-10 17:56, on v7 = v6's files):
1. instruction.md loses the proviso "A transition can share its peak with radiation of another origin, whatever the
   peak's energy." (an answer leak: it states the README's key realization).
2. A stated, tested consistency rule: each entry's energy_keV within 0.5 keV of its from_keV minus its to_keV, as its
   own sentence so that R9's quote stays whole; new test test_transition_consistency; R13 now quotes it (and R1, R5
   list the test too).
3. Easing through the data, not words: the 511 keV line M -> H made about five times stronger (M's beta feeding
   9.5 -> 11.75, its branch to H 6 -> 31; H's beta feeding 5.0 -> 2.75, so every other line keeps its intensity and the
   line feeds about half of H). tests/generate.py also records and asserts the reference's largest
   |from_keV - to_keV - energy_keV| in tests/checks.txt.
The README follows once the generator has written the new checks.txt (edit33.py). Run from the folder root."""
import json
from pathlib import Path

T = Path("tasks/active/gamma-decay-scheme")
PROVISO = "A transition can share its peak with radiation of another origin, whatever the peak's energy."
RULE = "The `energy_keV` of each entry must also be within 0.5 keV of its `from_keV` minus its `to_keV`."


def edit(path, pairs):
    p = T / path
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, (path, n, old[:80])
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="\n")
    print("edited", p)
    return s


s = edit("instruction.md", [
    (" %s Each object has exactly" % PROVISO, " Each object has exactly"),
    ("and whose `relative_intensity` is within 25% of the right value. `parent_half_life_s` must be within 2%",
     "and whose `relative_intensity` is within 25%% of the right value. %s `parent_half_life_s` must be within 2%%" % RULE),
])
assert PROVISO not in s and s.count(RULE) == 1

s = edit("tests/requirements.json", [
    ('"test_transition_energies", "test_relative_intensities", "test_isomer"]\n',
     '"test_transition_energies", "test_relative_intensities", "test_transition_consistency", "test_isomer"]\n'),
    ('      "tests": ["test_file_and_members", "test_transitions_placed", "test_transition_energies", "test_relative_intensities"]\n',
     '      "tests": ["test_file_and_members", "test_transitions_placed", "test_transition_energies", "test_relative_intensities", '
     '"test_transition_consistency"]\n'),
    ('      "quote": "%s",\n'
     '      "tests": ["test_transitions_placed", "test_transition_energies", "test_relative_intensities"]\n' % PROVISO,
     '      "quote": "%s",\n'
     '      "tests": ["test_transition_consistency"]\n' % RULE),
])
req = json.loads(s)["requirements"]
assert [r["id"] for r in req].count("R13") == 1 and len(req) == 13
assert next(r for r in req if r["id"] == "R13")["quote"] == RULE

edit("tests/test_outputs.py", [
    ('''def number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)
''',
     '''def number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def dec(x):
    """A JSON number as the decimal it prints as, the way tb4judge reads a float."""
    return Decimal(repr(x)) if isinstance(x, float) else Decimal(x)
'''),
    ('''def test_isomer():
''',
     '''def test_transition_consistency():
    """every entry's energy_keV within 0.5 keV of its own from_keV minus its own to_keV."""
    for t in scheme()["transitions"]:
        span = dec(t["from_keV"]) - dec(t["to_keV"])
        assert J.within(t["energy_keV"], span, KEV), \\
            "energy_keV %r for the entry from %r to %r keV, whose levels are %s keV apart" % (
                t["energy_keV"], t["from_keV"], t["to_keV"], span)


def test_isomer():
'''),
])

edit("tests/generate.py", [
    ('# M -> H (511.0 keV) lies on the annihilation line.\n',
     '# M -> H (511.0 keV) lies on the annihilation line and feeds about half of H.\n'),
    ('    "H": (2581.6, 5.0, [("Da", 50), ("B", 35), ("C", 15)]),\n',
     '    "H": (2581.6, 2.75, [("Da", 50), ("B", 35), ("C", 15)]),\n'),
    ('    "M": (3092.6, 9.5, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("H", 6)]),\n',
     '    "M": (3092.6, 11.75, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("H", 31)]),\n'),
    ('    iso_e = abs(result["isomer"]["level_keV"] - expected["isomer"]["level_keV"])\n'
     '    assert e_dev <= 0.5 and i_dev <= 0.25 and hl <= 0.02 and iso <= 0.08 and iso_e <= 0.5\n',
     '    iso_e = abs(result["isomer"]["level_keV"] - expected["isomer"]["level_keV"])\n'
     '    gap = max(abs(r["from_keV"] - r["to_keV"] - r["energy_keV"]) for r in result["transitions"])\n'
     '    assert e_dev <= 0.5 and i_dev <= 0.25 and hl <= 0.02 and iso <= 0.08 and iso_e <= 0.5 and gap <= 0.5\n'),
    ('            "gamma-ray energies: largest difference %.3f keV, tolerance 0.5 keV" % e_dev,\n',
     '            "gamma-ray energies: largest difference %.3f keV, tolerance 0.5 keV" % e_dev,\n'
     '            "each gamma-ray energy against its own two levels: largest |from_keV - to_keV - energy_keV| %.3f keV, "\n'
     '            "tolerance 0.5 keV" % gap,\n'),
])
