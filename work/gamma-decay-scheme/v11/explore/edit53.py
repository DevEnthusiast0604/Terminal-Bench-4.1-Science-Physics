"""v11: README.md figures from the new tests/checks.txt and tests/expected.json, the hidden 1081.40 keV transition,
v8's 511 keV line (I 4.30, inside the band when read whole) and the reference's new doublet steps.
Every replacement must match once."""
from pathlib import Path

P = Path("tasks/active/gamma-decay-scheme/README.md")
s = P.read_bytes().decode("utf-8")
assert "\r" not in s

EDITS = [
    # Key realization.
    ("wrong, because several peaks are something else, one peak that is always set aside holds a transition as well, and\n"
     "the evidence that says so is in different files.",
     "wrong, because several peaks are something else, one peak that is always set aside holds a transition as well, one\n"
     "strong peak hides a weak transition that only a gate shows, and the evidence that says so is in different files."),
    # Gain.
    ("background run, taken straight after it, lie off by 0.62 keV at 500 keV, 1.14 keV at 1500 keV and 1.66 keV at\n"
     "  2500 keV when read",
     "background run, taken straight after it, lie off by 0.61 keV at 500 keV, 1.13 keV at 1500 keV and 1.64 keV at\n"
     "  2500 keV when read"),
    # Escape peaks.
    ("its lines and the annihilation line; strong high-energy lines add escape peaks at 1507.75, 1752.16 and 2263.18 keV",
     "its lines and the annihilation line; strong high-energy lines add escape peaks at 1507.72, 1752.25 and 2263.22 keV"),
    # Sum peaks.
    ("two γ rays of one cascade sometimes land in the same crystal and read as their sum. The peak at 1171.46 keV has a\n"
     "  relative intensity of 0.85 as read and 0.02 once the sum is removed; it matches a real energy difference within\n"
     "  0.3 keV and has no transition behind it. The peak at 842.69 keV is a real crossover under a sum, 4.11 as read and\n"
     "  2.73 after (`[sum peaks: ...]`).",
     "two γ rays of one cascade sometimes land in the same crystal and read as their sum. The peak at 1171.48 keV has a\n"
     "  relative intensity of 0.80 as read and -0.01 once the sum is removed; it matches a real energy difference within\n"
     "  0.3 keV and has no transition behind it. The peak at 842.70 keV is a real crossover under a sum, 4.08 as read and\n"
     "  2.70 after (`[sum peaks: ...]`)."),
    # Doublets.
    ("- **Some peaks are two transitions.** The peak at 647.21 keV is in coincidence with itself (13418 counts) and its\n"
     "  width is 1.18 times the resolution:",
     "- **Some peaks are two transitions.** The peak at 647.22 keV is in coincidence with itself (13663 counts) and its\n"
     "  width is 1.17 times the resolution:"),
    ("one misplaces the levels fed through them. The peak at 1322.47 keV has no self-coincidence (-2 counts net) but a\n"
     "  width of 1.25 times the resolution, and its centroid moves from 1321.73 to 1323.23 keV with the gate: two nearly\n"
     "  degenerate levels at 1640.30 and 1641.60 keV (`[peaks that are two transitions]`). Merged, they miss the 0.5 keV\n"
     "  tolerance, and their feeders land on the wrong one.\n",
     "one misplaces the levels fed through them. The peak at 1322.43 keV has no self-coincidence (6 counts net) but a\n"
     "  width of 1.25 times the resolution, and its centroid moves from 1321.75 to 1323.19 keV with the gate: two nearly\n"
     "  degenerate levels at 1640.30 and 1641.60 keV (`[peaks that are two transitions]`). Merged, they miss the 0.5 keV\n"
     "  tolerance, and their feeders land on the wrong one.\n"
     "- **A strong peak hides a weak transition.** The level at 2721.70 keV, which its 1879.00 keV line places above the\n"
     "  level at 842.70 keV, also decays to the level at 1640.30 keV by a 1081.40 keV transition of relative intensity\n"
     "  1.22 (`tests/expected.json`). That lies 0.9 keV under the 1082.30 keV transition from the level at 1925.00 keV,\n"
     "  ten times stronger. The singles do not show it: the peak at 1082.22 keV has a width of 1.02 times the resolution,\n"
     "  inside the 0.94 to 1.03 of single lines, and no self-coincidence (4 counts). A gate on a line below the weak member\n"
     "  does: gated on the 1322 keV doublet the peak sits at 1081.44 keV, where the gates on 524.3, 708.0 and 867.5 keV\n"
     "  put it at 1082.30 to 1082.32 keV, and the 1082.2 keV gate puts the doublet at 1321.91 keV, the line of the level at\n"
     "  1640.30 keV (`[peaks that are two transitions]`). A peak list matched to level differences finds one line at\n"
     "  1082.22 keV and places it once, since the level difference of 1081.40 keV lies 0.82 keV from the peak, and the\n"
     "  scheme then lacks a transition. The gates on the lines below each member also give the shares: 0.080 for the\n"
     "  weak member, against 0.059 from the singles centroid, and I 1.11 and 12.75 for 1.22 and 13.02 (the same line).\n"),
    # Shared peak.
    ("- **One peak is shared with another activity.** Of the peak at 707.96 keV only a share of 0.64 is the parent's; the\n"
     "  rest is a line of the daughter's own decay. Whole-peak intensity is 4.90 where the scheme has 3.23",
     "- **One peak is shared with another activity.** Of the peak at 707.97 keV only a share of 0.63 is the parent's; the\n"
     "  rest is a line of the daughter's own decay. Whole-peak intensity is 4.74 where the scheme has 3.15"),
    # Annihilation.
    ("at 2581.60 keV, with a relative intensity of 2.99: it feeds about a third of that level (`TARGET` in\n"
     "  `tests/generate.py`). Annihilation radiation is wider than the detector's resolution: the background run, which\n"
     "  holds it alone, gives a σ of 1.46 keV where a line has 0.67 keV. Pair production by the parent's own lines above\n"
     "  1022 keV adds annihilation radiation with the parent's time profile, so the cycle's time bins do not separate the\n"
     "  two, and the room's share scaled from the background run, 3516 counts, is only part of the broad radiation. Read as\n"
     "  one line, the peak gives 4.34 whole and 4.10 less that room share, both outside 25% of 2.99. The two shapes\n"
     "  separate it: fitted with both, the production peak has a broad part of 22175 ± 861 counts and a narrow part of\n"
     "  41831 ± 660 counts, a share of 1.00 of which follows the parent's time profile, and the narrow part gives 2.83\n"
     "  (`[the peak at 511 keV: ...]`). Its prompt coincidences place it: 941.3 keV (1029 counts), 1092.0 keV (246) and\n"
     "  1738.9 keV (431), the three lines that leave the level at 2581.60 keV, and the lines below them (`[lines on shared\n"
     "  peaks: ...]`). The energy difference alone does not decide it, since five other differences of two levels fall on\n"
     "  peaks of another origin and hold no transition, the daughter's own 403.40 keV line among them.",
     "at 2581.60 keV, with a relative intensity of 4.30: it feeds about half of that level (`TARGET` in\n"
     "  `tests/generate.py`). Annihilation radiation is wider than the detector's resolution: the background run, which\n"
     "  holds it alone, gives a σ of 1.53 keV where a line has 0.68 keV. Pair production by the parent's own lines above\n"
     "  1022 keV adds annihilation radiation with the parent's time profile, so the cycle's time bins do not separate the\n"
     "  two, and the room's share scaled from the background run, 3557 counts, is only part of the broad radiation. Read as\n"
     "  one line, the peak gives 5.06 whole and 4.82 less that room share, inside 25% of 4.30; fitted with both shapes,\n"
     "  the production peak has a broad part of 12112 ± 1026 counts and a narrow part of 64351 ± 829 counts, a share of\n"
     "  1.00 of which follows the parent's time profile, and the narrow part gives 4.26 (`[the peak at 511 keV: ...]`).\n"
     "  What decides it is whether the peak is looked at: its prompt coincidences place it, with 941.3 keV (1613 counts),\n"
     "  1092.0 keV (378) and 1738.9 keV (628), the three lines that leave the level at 2581.60 keV, and the lines below\n"
     "  them (`[lines on shared peaks: ...]`). The energy difference alone does not decide it, since six other differences\n"
     "  of two levels fall on peaks of another origin and hold no transition, the daughter's own 403.40 keV line among them."),
    # Solution: split_doublets.
    ("   the upper member, the highest) centroid that holds to two standard errors, so one stray gate cannot set it: the\n"
     "   898.3 keV gate reads the 647.21 keV peak at 646.69 keV, 0.2 keV under the other gates that see the lower member\n"
     "   alone (`[peaks that are two transitions]`).\n",
     "   the upper member, the highest) centroid that holds to two standard errors, so one stray gate cannot set it: the\n"
     "   898.3 keV gate reads the 647.22 keV peak at 646.82 keV, under the 646.88 to 646.94 keV of the other gates that\n"
     "   see the lower member alone (`[peaks that are two transitions]`). When one member holds under a quarter of a peak,\n"
     "   as the 1081.40 keV member does, the singles centroid gives its first share, since a fit of two shapes cannot hold\n"
     "   so small a part, and a gate whose centroid sits on the strong member leaves the weak one undecided.\n"),
    # Solution: search count.
    ("   under the 60 keV threshold. That search finds one scheme at 16 levels, the ground state included, and none below\n",
     "   under the 60 keV threshold. That search finds one scheme at 17 levels, the ground state included, and none below\n"),
    # Solution: intensities.
    ("7. `refine_levels` fits the level energies to all the line energies by weighted least squares, `split_intensities` shares\n"
     "   a doublet's intensity between the members from what the scheme predicts, and `isomer_half_life` finds the level with\n",
     "7. `refine_levels` fits the level energies to all the line energies by weighted least squares, `split_intensities` shares\n"
     "   a doublet in one cascade between the members from what the scheme predicts, `split_moved` shares a doublet that the\n"
     "   gates tell apart from the gates on the lines below each member, whose ratio leaves the scale of the coincidences\n"
     "   out, and `isomer_half_life` finds the level with\n"),
    # Verification: energies.
    ("- **0.5 keV on energies.** The reference is within 0.030 keV on levels and 0.030 keV on γ-ray energies. Energies read\n"
     "  from gated spectra instead of singles, over 159 gates, scatter by an rms of 0.047 keV with a largest departure of\n"
     "  0.198 keV. The room lines after the gain correction scatter by 0.027 keV. The band therefore holds any sound\n"
     "  centroid method. It rejects the uncorrected gain, off by 0.62 keV already at 500 keV,",
     "- **0.5 keV on energies.** The reference is within 0.020 keV on levels and 0.030 keV on γ-ray energies. Energies read\n"
     "  from gated spectra instead of singles, over 154 gates, scatter by an rms of 0.043 keV with a largest departure of\n"
     "  0.288 keV. The room lines after the gain correction scatter by 0.016 keV. The band therefore holds any sound\n"
     "  centroid method. It rejects the uncorrected gain, off by 0.61 keV already at 500 keV,"),
    # Verification: intensities.
    ("- **25% on intensities.** The reference is within 8.4 percent. Intensities tested through coincidences instead of\n"
     "  singles, over 52 pairs, come out at measured over predicted of mean 1.020 and rms 0.076. One pair lies further\n"
     "  from 1 than the band, 318.4 keV with 1606.6 keV at 1.337: the 1606.6 keV peak also holds the sum of 524.3 and\n"
     "  1082.3 keV (1.21 as read, 1.01 once the sum is removed, `[sum peaks: ...]`), and that cascade ends in 318.4 keV as\n"
     "  well. The band is wider than the reference's error and that rms, because a different efficiency fit, a different\n"
     "  way of sharing a doublet or a different handling of the sum can reasonably move a line that far. It still rejects\n"
     "  the whole-peak readings of 842.69 keV (4.11 for 2.71), 707.96 keV (4.90 for 3.23) and 511 keV (4.34 for 2.99, and\n"
     "  4.10 less the room's annihilation radiation).",
     "- **25% on intensities.** The reference is within 9.1 percent, on the weak 1081.40 keV member (1.11 for 1.22).\n"
     "  Intensities tested through coincidences instead of singles, over 47 pairs, come out at measured over predicted of\n"
     "  mean 1.016 and rms 0.061. One pair lies further from 1 than the band, 318.4 keV with 1606.6 keV at 1.261: the\n"
     "  1606.6 keV peak also holds the sum of 524.3 and 1082.2 keV (1.16 as read, 0.96 once the sum is removed, `[sum\n"
     "  peaks: ...]`), and that cascade ends in 318.4 keV as well. The band is wider than the reference's error and that\n"
     "  rms, because a different efficiency fit, a different way of sharing a doublet or a different handling of the sum\n"
     "  can reasonably move a line that far: the weak member's share is 0.059 from the singles centroid and 0.080 from the\n"
     "  gates, against 0.086 in the scheme. It still rejects the whole-peak readings of 842.70 keV (4.08 for 2.70) and\n"
     "  707.97 keV (4.74 for 3.15)."),
    # Verification: half-lives.
    ("strongest lines that die away give 4.365, 4.370, 4.395 and 4.345 s against 4.370 s, so a fit to one strong line stays inside.",
     "strongest lines that die away give 4.355, 4.390, 4.375 and 4.430 s against 4.370 s, so a fit to one strong line stays inside."),
    ("- **8% on the isomer's half-life.** The reference is within 0.3 percent. Fitted by the line above the isomer, the four\n"
     "  feeders give 164.0 to 176.0 ns against 168.0 ns, so a fit to one feeder stays inside.",
     "- **8% on the isomer's half-life.** The reference is within 0.9 percent. Fitted by the line above the isomer, the four\n"
     "  feeders give 158.5 to 171.0 ns against 168.0 ns, so a fit to one feeder stays inside."),
    # Verification: level count.
    ("calibrated on it and the margins above are stated rather than a spread over seeds. The level count has no band: the\n"
     "search finds no scheme with 15 levels or fewer and one with 16, and with 17 it finds one more,",
     "calibrated on it and the margins above are stated rather than a spread over seeds. The level count has no band: the\n"
     "search finds no scheme with 16 levels or fewer and one with 17, and with 18 it finds one more,"),
    ("fewest levels, which is how spectroscopists adopt a level, only when the data call for it. The rule selects the 16, and it leaves no tie to break: the search finds a single scheme with 16 levels. The\n"
     "`relative_intensity` floor of 0.5 excludes nothing the scheme holds: the weakest right transition in\n"
     "`tests/expected.json` is the 1606.60 keV line at 1.028, twice the floor.",
     "fewest levels, which is how spectroscopists adopt a level, only when the data call for it. The rule selects the 17, and it leaves no tie to break: the search finds a single scheme with 17 levels. The\n"
     "`relative_intensity` floor of 0.5 excludes nothing the scheme holds: the weakest right transition in\n"
     "`tests/expected.json` is the 1606.60 keV line at 1.001, twice the floor."),
]
for old, new in EDITS:
    n = s.count(old)
    assert n == 1, (n, old[:90])
    s = s.replace(old, new)
P.write_bytes(s.encode("utf-8"))
print("README.md: %d edits" % len(EDITS))
