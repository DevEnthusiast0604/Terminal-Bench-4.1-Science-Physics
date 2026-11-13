"""v4 README: the line in the annihilation peak, the reference's new step, and every figure from the new
tests/checks.txt. Every old string must occur exactly once. Run from the folder root."""
from pathlib import Path

p = Path("tasks/active/gamma-decay-scheme/README.md")
s = p.read_text(encoding="utf-8")
pairs = [
    ("The key realization is that a peak in a spectrum is not yet a transition. An analyst who lists the peaks and fits\n"
     "energy differences gets a scheme that looks complete and is wrong, because several peaks are something else and the\n"
     "evidence that says so is in different files.",
     "The key realization is that a peak in a spectrum is not yet a transition, and a peak of another origin is not yet\n"
     "free of one. An analyst who lists the peaks and fits energy differences gets a scheme that looks complete and is\n"
     "wrong, because several peaks are something else, one peak that is always set aside holds a transition as well, and\n"
     "the evidence that says so is in different files."),
    ("lie off by 0.61 keV at 500 keV, 1.14 keV at 1500 keV and 1.66 keV at\n  2500 keV",
     "lie off by 0.61 keV at 500 keV, 1.13 keV at 1500 keV and 1.65 keV at\n  2500 keV"),
    ("add escape peaks at 1507.76, 1752.21 and 2263.19 keV", "add escape peaks at 1507.73, 1752.21 and 2263.19 keV"),
    ("The peak at 1171.46 keV has a\n  relative intensity of 0.82 as read and -0.01 once the sum is removed",
     "The peak at 1171.49 keV has a\n  relative intensity of 0.82 as read and 0.00 once the sum is removed"),
    ("a real crossover under a sum, 4.09 as read and 2.71\n  after", "a real crossover under a sum, 4.11 as read and 2.73\n  after"),
    ("in coincidence with itself (13506 counts) and its\n  width is 1.19 times the resolution",
     "in coincidence with itself (13501 counts) and its\n  width is 1.18 times the resolution"),
    ("The peak at 1322.48 keV has almost no self-coincidence (6 counts) but a\n"
     "  width of 1.24 times the resolution, and its centroid moves from 1321.88 to 1323.18 keV with the gate",
     "The peak at 1322.47 keV has no self-coincidence (-1 counts net) but a\n"
     "  width of 1.28 times the resolution, and its centroid moves from 1321.85 to 1323.21 keV with the gate"),
    ("Of the peak at 707.96 keV only a share of 0.64 is the parent's; the\n"
     "  rest is a line of the daughter's own decay. Whole-peak intensity is 4.96 where the scheme has 3.26\n"
     "  (`[peak shared with the daughter's own decay]`).\n",
     "Of the peak at 707.97 keV only a share of 0.63 is the parent's; the\n"
     "  rest is a line of the daughter's own decay. Whole-peak intensity is 4.87 where the scheme has 3.23\n"
     "  (`[peaks shared with the daughter's own decay]`).\n"
     "- **The annihilation peak holds a line.** Every run has a peak at 511 keV from annihilation radiation, and it is\n"
     "  usually set aside. Here it also holds the parent's transition of 511.00 keV from the level at 3092.60 keV to the one\n"
     "  at 2581.60 keV, with a relative intensity of 0.85 against the floor of 0.5. Annihilation radiation is wider than the\n"
     "  detector's resolution: the background run, which holds it alone, gives a σ of 1.50 keV where a line has 0.67 keV.\n"
     "  Fitted with both shapes, the production peak has a broad part of 12792 counts and a narrow part of 11967 ± 482\n"
     "  counts, 0.98 of which follows the parent's time profile (`[the peak at 511 keV: ...]`). Its prompt coincidences\n"
     "  place it: 941.3, 1092.0 and 1738.9 keV, the three lines that leave the level at 2581.60 keV, and the lines below\n"
     "  them (`[lines on shared peaks: ...]`). The energy difference alone does not decide it, since five other differences\n"
     "  of two levels fall on peaks of another origin and hold no transition, the daughter's own 403.40 keV line among them.\n"),
    ("3. `classify` keeps the peaks with a parent share and drops the annihilation line, peaks too broad to be a line,\n"
     "   escape peaks (a parent line 511 or 1022 keV above at the ratio the source gave), and sum peaks.",
     "3. `annihilation_split` fits the production peak at 511 keV with the broad shape the background run gives\n"
     "   annihilation radiation and with the shape of a line, and keeps the narrow part as a line when it stands above six\n"
     "   standard deviations and follows the parent's time profile. `classify` keeps the peaks with a parent share and\n"
     "   drops the annihilation radiation, peaks too broad to be a line, escape peaks (a parent line 511 or 1022 keV above\n"
     "   at the ratio the source gave), and sum peaks."),
    ("been clear, or as undecided where it would be too weak. Pairs in the delayed matrix count as seen together.\n",
     "been clear, or as undecided where it would be too weak. Pairs in the delayed matrix count as seen together. A pair\n"
     "   whose two peaks both hold another activity stays undecided, since that activity's own cascade can make it.\n"),
    ("The reference is within 0.040 keV on levels and 0.020 keV on γ-ray energies. Energies read\n"
     "  from gated spectra instead of singles, over 147 gates, scatter by an rms of 0.042 keV with a largest departure of\n"
     "  0.267 keV. The room lines after the gain correction scatter by 0.032 keV.",
     "The reference is within 0.020 keV on levels and 0.020 keV on γ-ray energies. Energies read\n"
     "  from gated spectra instead of singles, over 153 gates, scatter by an rms of 0.040 keV with a largest departure of\n"
     "  0.178 keV. The room lines after the gain correction scatter by 0.025 keV."),
    ("- **25% on intensities.** The reference is within 7.7 percent. Intensities tested through coincidences instead of\n"
     "  singles, over 47 pairs, come out at measured over predicted of mean 1.015, rms 0.051 and at most 0.120 from 1. The\n"
     "  band is about twice that, because a different efficiency fit, a different way of sharing a doublet or a different\n"
     "  handling of the sum can reasonably move a line that far. It still rejects the whole-peak readings of 842.70 keV\n"
     "  (4.09 for 2.71) and 707.96 keV (4.96 for 3.26).",
     "- **25% on intensities.** The reference is within 10.4 percent. Intensities tested through coincidences instead of\n"
     "  singles, over 50 pairs, come out at measured over predicted of mean 1.017, rms 0.052 and at most 0.213 from 1. The\n"
     "  band is wider than both, because a different efficiency fit, a different way of sharing a doublet or a different\n"
     "  handling of the sum can reasonably move a line that far. It still rejects the whole-peak readings of 842.70 keV\n"
     "  (4.11 for 2.71) and 707.97 keV (4.87 for 3.23)."),
    ("- **2% on the parent's half-life.** The reference is within 0.11 percent. Fitted line by line, the four strongest\n"
     "  lines that die away give 4.335, 4.375, 4.390 and 4.435 s against 4.370 s,",
     "- **2% on the parent's half-life.** The reference gives 4.370 s, 0.00 percent off. Fitted line by line, the four\n"
     "  strongest lines that die away give 4.360, 4.380, 4.385 and 4.380 s against 4.370 s,"),
    ("The reference is within 2.1 percent. Fitted by the line above the isomer, the four\n"
     "  feeders give 158.5 to 166.0 ns against 168.0 ns,",
     "The reference is within 1.5 percent. Fitted by the line above the isomer, the four\n"
     "  feeders give 158.5 to 167.5 ns against 168.0 ns,"),
    ("which adds a level at\n2917.5 keV", "which adds a level at\n2917.6 keV"),
    ("floor of 0.5 excludes nothing the run could show: the weakest right transition in\n`tests/expected.json` is above 1.",
     "floor of 0.5 excludes nothing the scheme holds: the weakest right transition in\n`tests/expected.json` is the "
     "511.00 keV line at 0.853, and the next is above 1."),
]
for old, new in pairs:
    n = s.count(old)
    assert n == 1, (n, old[:70])
    s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline="\n")
print("edited", p, len(pairs), "replacements")
