"""v8 README: follows edit32.py and the generator's new tests/checks.txt (2026-11-10 18:11). The proviso's mention goes,
the 511 keV bullet describes the stronger line, every figure cited from checks.txt takes its new value, the test table
gains test_transition_consistency (R13 is now the consistency rule), a band bullet explains that rule, and the
placement paragraph answers the reviewer's optional tie point. Run from the folder root."""
import re
from pathlib import Path

P = Path("tasks/active/gamma-decay-scheme/README.md")
s = P.read_text(encoding="utf-8")


def sub(old, new):
    global s
    n = s.count(old)
    assert n == 1, (n, old[:90])
    s = s.replace(old, new)


# The proviso is gone from the instruction.
sub("the evidence that says so is in different files. The instruction says only that a transition can share its peak with\n"
    "radiation of another origin, whatever the peak's energy, and names no case. `environment/data/NOTES.md` states\n",
    "the evidence that says so is in different files. The instruction names none of this. `environment/data/NOTES.md` states\n")

# Difficulty bullets: new figures from checks.txt.
sub("0.61 keV at 500 keV, 1.13 keV at 1500 keV and 1.65 keV at", "0.62 keV at 500 keV, 1.14 keV at 1500 keV and 1.66 keV at")
sub("escape peaks at 1507.73, 1752.21 and 2263.19 keV", "escape peaks at 1507.71, 1752.17 and 2263.18 keV")
sub("relative intensity of 0.82 as read and 0.00 once the sum is removed", "relative intensity of 0.83 as read and 0.00 once the sum is removed")
sub("under a sum, 4.11 as read and 2.73", "under a sum, 4.14 as read and 2.76")
sub("(13501 counts) and its\n  width is 1.18 times", "(13679 counts) and its\n  width is 1.16 times")
sub("(-1 counts net) but a\n  width of 1.28 times the resolution, and its centroid moves from 1321.85 to 1323.21 keV",
    "(1 count net) but a\n  width of 1.26 times the resolution, and its centroid moves from 1321.73 to 1323.23 keV")
sub("Of the peak at 707.97 keV", "Of the peak at 707.95 keV")
sub("Whole-peak intensity is 4.87 where", "Whole-peak intensity is 4.88 where")

NEW_511 = """- **The annihilation peak holds a line.** Every run has a peak at 511 keV from annihilation radiation, and it is
  usually set aside. Here it also holds the parent's transition of 511.00 keV from the level at 3092.60 keV to the one
  at 2581.60 keV, with a relative intensity of 4.41, as strong as the 941.30 keV line that leaves the same level: it
  feeds about half of that level (`TARGET` in `tests/generate.py`). Annihilation radiation is wider than the
  detector's resolution: the background run, which holds it alone, gives a σ of 1.45 keV where a line has 0.68 keV.
  Pair production by the parent's own lines above 1022 keV adds annihilation radiation with the parent's time profile,
  so the cycle's time bins do not separate the two; the two shapes do. Fitted with both, the production peak has a
  broad part of 11142 ± 1249 counts and a narrow part of 63967 ± 1023 counts, a share of 1.00 of which follows the
  parent's time profile (`[the peak at 511 keV: ...]`). Its prompt coincidences place it: 941.3 keV (1552 counts),
  1092.0 keV (415) and 1738.9 keV (576), the three lines that leave the level at 2581.60 keV, and the lines below them
  (`[lines on shared peaks: ...]`). The energy difference alone does not decide it, since five other differences of
  two levels fall on peaks of another origin and hold no transition, the daughter's own 403.40 keV line among them.
"""
m = list(re.finditer(r"- \*\*The annihilation peak holds a line\.\*\*.*?403\.40 keV line among them\.\n", s, re.S))
assert len(m) == 1, len(m)
s = s[:m[0].start()] + NEW_511 + s[m[0].end():]

# Verification: the test table and the bands.
sub("runs seven tests against the scheme", "runs eight tests against the scheme")
sub("| `test_transitions_placed` | R1, R4, R5, R9, R11, R12, R13 |", "| `test_transitions_placed` | R1, R4, R5, R9, R11, R12 |")
sub("| `test_transition_energies` | R1, R4, R5, R9, R13 |", "| `test_transition_energies` | R1, R4, R5, R9 |")
sub("| `test_relative_intensities` | R1, R4, R5, R9, R13 | every `relative_intensity` within 25% |\n",
    "| `test_relative_intensities` | R1, R4, R5, R9 | every `relative_intensity` within 25% |\n"
    "| `test_transition_consistency` | R1, R5, R13 | every entry's `energy_keV` within 0.5 keV of its own `from_keV` minus its own `to_keV` |\n")
sub("The reference is within 0.020 keV on levels and 0.020 keV on γ-ray energies.",
    "The reference is within 0.090 keV on levels and 0.060 keV on γ-ray energies.")
sub("over 153 gates, scatter by an rms of 0.040 keV with a largest departure of\n  0.178 keV. The room lines after the gain correction scatter by 0.025 keV.",
    "over 158 gates, scatter by an rms of 0.045 keV with a largest departure of\n  0.300 keV. The room lines after the gain correction scatter by 0.034 keV.")
sub("off by 0.61 keV already at 500 keV", "off by 0.62 keV already at 500 keV")
sub("- **25% on intensities.**",
    "- **0.5 keV between an entry's γ-ray energy and its two levels.** The reference's γ-ray energies and the differences\n"
    "  of its levels agree within 0.010 keV (`[reference against the scheme]`): an answer that fits its levels to its own\n"
    "  line energies keeps the two within its fit residuals. The rule rejects an entry whose three fields each stay inside\n"
    "  their own band while together describing no single transition, such as 843.19 to 317.91 keV with 524.30 keV, whose\n"
    "  levels lie 0.98 keV further apart than its γ-ray energy.\n"
    "- **25% on intensities.**")
sub("The reference is within 10.4 percent.", "The reference is within 7.1 percent.")
sub("over 50 pairs, come out at measured over predicted of mean 1.017, rms 0.052 and at most 0.213 from 1.",
    "over 52 pairs, come out at measured over predicted of mean 1.004, rms 0.056 and at most 0.176 from 1.")
sub("(4.11 for 2.71) and 707.97 keV (4.87 for 3.23)", "(4.14 for 2.71) and 707.95 keV (4.88 for 3.23)")
sub("give 4.360, 4.380, 4.385 and 4.380 s against 4.370 s", "give 4.365, 4.390, 4.370 and 4.370 s against 4.370 s")
sub("The reference is within 1.5 percent.", "The reference is within 0.6 percent.")
sub("feeders give 158.5 to 167.5 ns against 168.0 ns", "feeders give 165.0 to 168.0 ns against 168.0 ns")
sub("2917.6 keV and a second unseen transition", "2917.5 keV and a second unseen transition")
sub("The rule selects the 16.", "The rule selects the 16, and it leaves no tie to break: the search finds a single scheme with 16 levels.")
sub("`tests/expected.json` is the 511.00 keV line at 0.853, and the next is above 1.",
    "`tests/expected.json` is the 1606.60 keV line at 1.028, twice the floor.")

P.write_text(s, encoding="utf-8", newline="\n")
print("edited", P)
