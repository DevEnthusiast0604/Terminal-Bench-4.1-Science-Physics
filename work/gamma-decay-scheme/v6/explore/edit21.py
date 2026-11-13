"""v6 (pass@3 of v5: 0 of 3, job 19705; the platform: "make the task somewhat easier"): all three attempts set the
511 keV peak aside by its energy before any analysis, so the instruction now says that a transition can share its
peak with radiation of another origin, whatever the peak's energy. It names no peak. Requirement R13 binds the
sentence to the transition tests; the README follows. Data, expected.json, checks.txt, generate.py and solve.py are
unchanged. Run from the folder root."""
import json
from pathlib import Path

T = Path("tasks/active/gamma-decay-scheme")
SENTENCE = "A transition can share its peak with radiation of another origin, whatever the peak's energy."


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


edit("instruction.md", [
    ("and nothing for any other peak in the data. Each object has exactly",
     "and nothing for any other peak in the data. %s Each object has exactly" % SENTENCE),
])

s = edit("tests/requirements.json", [
    ('      "tests": ["test_parent_half_life", "test_isomer"]\n'
     "    }\n"
     "  ],\n",
     '      "tests": ["test_parent_half_life", "test_isomer"]\n'
     "    },\n"
     "    {\n"
     '      "id": "R13",\n'
     '      "quote": "%s",\n'
     '      "tests": ["test_transitions_placed", "test_transition_energies", "test_relative_intensities"]\n'
     "    }\n"
     "  ],\n" % SENTENCE),
])
ids = [r["id"] for r in json.loads(s)["requirements"]]
assert ids.count("R13") == 1 and len(ids) == 13, ids

edit("README.md", [
    ("the evidence that says so is in different files. The instruction names none of this. `environment/data/NOTES.md` states\n",
     "the evidence that says so is in different files. The instruction says only that a transition can share its peak with\n"
     "radiation of another origin, whatever the peak's energy, and names no case. `environment/data/NOTES.md` states\n"),
    ("  detector's resolution: the background run, which holds it alone, gives a σ of 1.50 keV where a line has 0.67 keV.\n"
     "  Fitted with both shapes, the production peak has a broad part of 12792 counts and a narrow part of 11967 ± 482\n"
     "  counts, 0.98 of which follows the parent's time profile (`[the peak at 511 keV: ...]`). Its prompt coincidences\n",
     "  detector's resolution: the background run, which holds it alone, gives a σ of 1.50 keV where a line has 0.67 keV.\n"
     "  The broad part is not the room's alone: pair production by the parent's own lines above 1022 keV adds annihilation\n"
     "  radiation with the parent's time profile, so neither the background run's rate nor the cycle's time bins take it\n"
     "  off the line; the two shapes do. Fitted with both, the production peak has a broad part of 12792 counts and a\n"
     "  narrow part of 11967 ± 482 counts, 0.98 of which follows the parent's time profile (`[the peak at 511 keV: ...]`).\n"
     "  Its prompt coincidences\n"),
    ("| `test_transitions_placed` | R1, R4, R5, R9, R11, R12 |", "| `test_transitions_placed` | R1, R4, R5, R9, R11, R12, R13 |"),
    ("| `test_transition_energies` | R1, R4, R5, R9 |", "| `test_transition_energies` | R1, R4, R5, R9, R13 |"),
    ("| `test_relative_intensities` | R1, R4, R5, R9 |", "| `test_relative_intensities` | R1, R4, R5, R9, R13 |"),
])
