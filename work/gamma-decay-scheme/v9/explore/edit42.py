"""v9: README figures from the v9 tests/checks.txt (the 511 keV line at 2.99 among pair-production annihilation
radiation; the reference's doublet members from the gates that agree; the coincidence route's one pair outside the
band). Run from the folder root."""
from pathlib import Path

T = Path("tasks/active/gamma-decay-scheme")


def edit(path, pairs):
    p = T / path
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, (path, n, old[:80])
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="\n")
    print("edited", p)


OLD_511 = """- **The annihilation peak holds a line.** Every run has a peak at 511 keV from annihilation radiation, and it is
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
NEW_511 = """- **The annihilation peak holds a line.** Every run has a peak at 511 keV from annihilation radiation, and it is
  usually set aside. Here it also holds the parent's transition of 511.00 keV from the level at 3092.60 keV to the one
  at 2581.60 keV, with a relative intensity of 2.99: it feeds about a third of that level (`TARGET` in
  `tests/generate.py`). Annihilation radiation is wider than the detector's resolution: the background run, which
  holds it alone, gives a σ of 1.46 keV where a line has 0.67 keV. Pair production by the parent's own lines above
  1022 keV adds annihilation radiation with the parent's time profile, so the cycle's time bins do not separate the
  two, and the room's share scaled from the background run, 3516 counts, is only part of the broad radiation. Read as
  one line, the peak gives 4.34 whole and 4.10 less that room share, both outside 25% of 2.99. The two shapes
  separate it: fitted with both, the production peak has a broad part of 22175 ± 861 counts and a narrow part of
  41831 ± 660 counts, a share of 1.00 of which follows the parent's time profile, and the narrow part gives 2.83
  (`[the peak at 511 keV: ...]`). Its prompt coincidences place it: 941.3 keV (1029 counts), 1092.0 keV (246) and
  1738.9 keV (431), the three lines that leave the level at 2581.60 keV, and the lines below them (`[lines on shared
  peaks: ...]`). The energy difference alone does not decide it, since five other differences of two levels fall on
  peaks of another origin and hold no transition, the daughter's own 403.40 keV line among them.
"""

edit("README.md", [
    ("strong high-energy lines add escape peaks at 1507.71, 1752.17 and 2263.18 keV",
     "strong high-energy lines add escape peaks at 1507.75, 1752.16 and 2263.18 keV"),
    ("The peak at 1171.49 keV has a\n"
     "  relative intensity of 0.83 as read and 0.00 once the sum is removed; it matches a real energy difference exactly\n"
     "  and has no transition behind it. The peak at 842.70 keV is a real crossover under a sum, 4.14 as read and 2.76\n"
     "  after",
     "The peak at 1171.46 keV has a\n"
     "  relative intensity of 0.85 as read and 0.02 once the sum is removed; it matches a real energy difference within\n"
     "  0.3 keV and has no transition behind it. The peak at 842.69 keV is a real crossover under a sum, 4.11 as read and\n"
     "  2.73 after"),
    ("The peak at 647.22 keV is in coincidence with itself (13679 counts) and its\n"
     "  width is 1.16 times the resolution",
     "The peak at 647.21 keV is in coincidence with itself (13418 counts) and its\n"
     "  width is 1.18 times the resolution"),
    ("The peak at 1322.47 keV has no self-coincidence (1 count net) but a\n"
     "  width of 1.26 times the resolution",
     "The peak at 1322.47 keV has no self-coincidence (-2 counts net) but a\n"
     "  width of 1.25 times the resolution"),
    ("Of the peak at 707.95 keV only a share of 0.63 is the parent's; the\n"
     "  rest is a line of the daughter's own decay. Whole-peak intensity is 4.88 where the scheme has 3.23",
     "Of the peak at 707.96 keV only a share of 0.64 is the parent's; the\n"
     "  rest is a line of the daughter's own decay. Whole-peak intensity is 4.90 where the scheme has 3.23"),
    (OLD_511, NEW_511),
    ("   gated spectra (`Coincidences.centroid_in_gate`) moves with the gate, and records which member each gate sees.\n",
     "   gated spectra (`Coincidences.centroid_in_gate`) moves with the gate, and records which member each gate sees. A\n"
     "   member's energy is the mean of the gates whose centroid agrees, within two standard errors, with the lowest (for\n"
     "   the upper member, the highest) centroid that holds to two standard errors, so one stray gate cannot set it: the\n"
     "   898.3 keV gate reads the 647.21 keV peak at 646.69 keV, 0.2 keV under the other gates that see the lower member\n"
     "   alone (`[peaks that are two transitions]`).\n"),
    ("The reference is within 0.090 keV on levels and 0.060 keV on γ-ray energies. Energies read\n"
     "  from gated spectra instead of singles, over 158 gates, scatter by an rms of 0.045 keV with a largest departure of\n"
     "  0.300 keV. The room lines after the gain correction scatter by 0.034 keV.",
     "The reference is within 0.030 keV on levels and 0.030 keV on γ-ray energies. Energies read\n"
     "  from gated spectra instead of singles, over 159 gates, scatter by an rms of 0.047 keV with a largest departure of\n"
     "  0.198 keV. The room lines after the gain correction scatter by 0.027 keV."),
    ("- **25% on intensities.** The reference is within 7.1 percent. Intensities tested through coincidences instead of\n"
     "  singles, over 52 pairs, come out at measured over predicted of mean 1.004, rms 0.056 and at most 0.176 from 1. The\n"
     "  band is wider than both, because a different efficiency fit, a different way of sharing a doublet or a different\n"
     "  handling of the sum can reasonably move a line that far. It still rejects the whole-peak readings of 842.70 keV\n"
     "  (4.14 for 2.71) and 707.95 keV (4.88 for 3.23).\n",
     "- **25% on intensities.** The reference is within 8.4 percent. Intensities tested through coincidences instead of\n"
     "  singles, over 52 pairs, come out at measured over predicted of mean 1.020 and rms 0.076. One pair lies further\n"
     "  from 1 than the band, 318.4 keV with 1606.6 keV at 1.337: the 1606.6 keV peak also holds the sum of 524.3 and\n"
     "  1082.3 keV (1.21 as read, 1.01 once the sum is removed, `[sum peaks: ...]`), and that cascade ends in 318.4 keV as\n"
     "  well. The band is wider than the reference's error and that rms, because a different efficiency fit, a different\n"
     "  way of sharing a doublet or a different handling of the sum can reasonably move a line that far. It still rejects\n"
     "  the whole-peak readings of 842.69 keV (4.11 for 2.71), 707.96 keV (4.90 for 3.23) and 511 keV (4.34 for 2.99, and\n"
     "  4.10 less the room's annihilation radiation).\n"),
    ("strongest lines that die away give 4.365, 4.390, 4.370 and 4.370 s against 4.370 s",
     "strongest lines that die away give 4.365, 4.370, 4.395 and 4.345 s against 4.370 s"),
    ("The reference is within 0.6 percent. Fitted by the line above the isomer, the four\n"
     "  feeders give 165.0 to 168.0 ns against 168.0 ns",
     "The reference is within 0.3 percent. Fitted by the line above the isomer, the four\n"
     "  feeders give 164.0 to 176.0 ns against 168.0 ns"),
    ("which adds a level at\n2917.5 keV", "which adds a level at\n2917.6 keV"),
])
