"""v13 README: the hidden transition now sits under 1082.3 keV with no gate that isolates it, and every figure follows
the new tests/checks.txt. Exact-match replacements; run from the folder root."""
PATH = "tasks/active/gamma-decay-scheme/README.md"
s = open(PATH, encoding="utf-8", newline="").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


rep("strong peak hides a weak transition that only a gate shows, and the evidence",
    "strong peak hides a weak transition that no gate isolates, and the evidence")
rep("1.13 keV at 1500 keV and 1.64 keV at\n", "1.13 keV at 1500 keV and 1.65 keV at\n")
rep("escape peaks at 1507.72, 1752.25 and 2263.22 keV", "escape peaks at 1507.65, 1752.20 and 2263.19 keV")
rep("""The peak at 1171.48 keV has a
  relative intensity of 0.80 as read and -0.01 once the sum is removed; it matches a real energy difference within
  0.3 keV and has no transition behind it. The peak at 842.70 keV is a real crossover under a sum, 4.08 as read and
  2.70 after (`[sum peaks: ...]`).""", """The peak at 1171.51 keV has a
  relative intensity of 0.79 as read and -0.01 once the sum is removed; it matches the difference of the levels at
  1489.60 and 318.40 keV within 0.35 keV and has no transition behind it. The peak at 842.71 keV is a real crossover
  under a sum, 4.11 as read and 2.74 after (`[sum peaks: ...]`).""")
rep("""The peak at 647.22 keV is in coincidence with itself (13663 counts) and its
  width is 1.17 times the resolution""", """The peak at 647.22 keV is in coincidence with itself (13450 counts) and its
  width is 1.19 times the resolution""")
rep("""The peak at 1322.43 keV has no self-coincidence (6 counts net) but a
  width of 1.25 times the resolution, and its centroid moves from 1321.75 to 1323.19 keV with the gate""",
    """The peak at 1322.48 keV has no self-coincidence (0 counts net) but a
  width of 1.28 times the resolution, and its centroid moves from 1321.80 to 1323.24 keV with the gate""")
rep("""- **A strong peak hides a weak transition.** The level at 2721.70 keV, which its 1879.00 keV line places above the
  level at 842.70 keV, also decays to the level at 1640.30 keV by a 1081.40 keV transition of relative intensity
  1.22 (`tests/expected.json`). That lies 0.9 keV under the 1082.30 keV transition from the level at 1925.00 keV,
  ten times stronger. The singles do not show it: the peak at 1082.22 keV has a width of 1.02 times the resolution,
  inside the 0.94 to 1.03 of single lines, and no self-coincidence (4 counts). A gate on a line below the weak member
  does: gated on the 1322 keV doublet the peak sits at 1081.44 keV, where the gates on 524.3, 708.0 and 867.5 keV
  put it at 1082.30 to 1082.32 keV, and the 1082.2 keV gate puts the doublet at 1321.91 keV, the line of the level at
  1640.30 keV (`[peaks that are two transitions]`). A peak list matched to level differences finds one line at
  1082.22 keV and places it once, since the level difference of 1081.40 keV lies 0.82 keV from the peak, and the
  scheme then lacks a transition. The gates on the lines below each member also give the shares: 0.080 for the
  weak member, against 0.059 from the singles centroid, and I 1.11 and 12.75 for 1.22 and 13.02 (the same section).
""", """- **A strong peak hides a weak transition that no gate isolates.** The level at 1399.80 keV, which its 557.10 keV
  line places above the level at 842.70 keV and which nothing but the β decay feeds, also decays to the level at
  318.40 keV by a 1081.40 keV transition of relative intensity 1.61 (`TARGET` in `tests/generate.py`,
  `tests/expected.json`). That lies 0.9 keV under the 1082.30 keV transition from the level at 1925.00 keV, eight
  times stronger. The singles do not flag it: every peak but the two doublets has a width of 0.97 to 1.05 times the
  resolution and a self-coincidence strength of at most 0.007, the 1082.2 keV peak among them (`[peaks that are two
  transitions]`). No gate shows it alone either, since the one line below it, 318.4 keV, also lies below the strong
  one: the 318.4 keV gate holds 0.96 of the strong member's cascade and all of the weak one's, the 524.3 keV gate
  0.96 and none. What points to it is a level difference, 1081.42 keV, 0.78 keV under the peak's centroid. A fit of
  the peak with a second member there, with the low-energy tail that lines standing alone show (0.073 of the area,
  slope 1.53 σ), gives that member a share of 0.1245 ± 0.0191, where made-up members beside lines standing alone take
  an rms share of 0.0144; at the three other level differences near strong peaks the same fit gives -0.0105 ± 0.0146,
  0.0006 ± 0.0151 and -0.0303 ± 0.0888. The proportions of the two gates give 0.1102 ± 0.0128, against 0.1104 in the
  scheme, and Gaussians without the tail give 0.1489: the weak member's I is then 1.78, 1.57 and 2.12 for 1.61, the
  last outside 25% (`[a weak transition under a strong line]`). A peak list matched to level differences finds one
  line at 1082.2 keV and places it once, and the scheme then lacks a transition; read as one line, the peak gives
  14.27 for 12.99, inside the band, so only the missing transition fails.
""")
rep("Whole-peak intensity is 4.74 where the scheme has 3.15", "Whole-peak intensity is 4.74 where the scheme has 3.14")
rep("with a relative intensity of 4.30: it feeds about half", "with a relative intensity of 4.29: it feeds about half")
rep("gives a σ of 1.53 keV where a line has 0.68 keV", "gives a σ of 1.50 keV where a line has 0.67 keV")
rep("scaled from the background run, 3557 counts,", "scaled from the background run, 3403 counts,")
rep("the peak gives 5.06 whole and 4.82 less that room share, inside 25% of 4.30;",
    "the peak gives 5.00 whole and 4.78 less that room share, inside 25% of 4.29;")
rep("""broad part of 12112 ± 1026 counts and a narrow part of 64351 ± 829 counts, a share of
  1.00 of which follows the parent's time profile, and the narrow part gives 4.26""",
    """broad part of 11854 ± 1088 counts and a narrow part of 64249 ± 879 counts, a share of
  0.99 of which follows the parent's time profile, and the narrow part gives 4.22""")
rep("""with 941.3 keV (1613 counts),
  1092.0 keV (378) and 1738.9 keV (628)""", """with 941.3 keV (1498 counts),
  1092.0 keV (392) and 1738.9 keV (593)""")
rep("since six other differences", "since five other differences")
rep("""the
   898.3 keV gate reads the 647.22 keV peak at 646.82 keV, under the 646.88 to 646.94 keV of the other gates that
   see the lower member alone (`[peaks that are two transitions]`). When one member holds under a quarter of a peak,
   as the 1081.40 keV member does, the singles centroid gives its first share, since a fit of two shapes cannot hold
   so small a part, and a gate whose centroid sits on the strong member leaves the weak one undecided.""", """the
   708.0 keV gate reads the 647.22 keV peak at 646.82 keV, under the 646.88 to 647.08 keV of the other gates on
   lines that reach the lower member alone (`[peaks that are two transitions]`). When one member holds under a
   quarter of a peak, the singles centroid gives its first share, since a fit of two shapes at free energies cannot
   hold so small a part, and a gate whose centroid sits on the strong member leaves the weak one undecided.""")
rep("""   since the instruction wants the scheme with the fewest levels.
   A placement must agree with the flags, the energy sums within 0.35 keV (`RITZ_KEV`), the measured coincidence
   strengths and the intensity balance at each level. A level with no line out may leave through one unseen transition
   under the 60 keV threshold. That search finds one scheme at 17 levels, the ground state included, and none below
   (`[placement search]`).
7. `refine_levels` fits the level energies to all the line energies by weighted least squares, `split_intensities` shares
   a doublet in one cascade between the members from what the scheme predicts, `split_moved` shares a doublet that the
   gates tell apart from the gates on the lines below each member, whose ratio leaves the scale of the coincidences
   out, and `isomer_half_life` finds the level with
   every pair across it delayed and fits the exponential of the delay spectrum, using the opposite side of zero as the
   chance background.""", """   since the instruction wants the scheme with the fewest levels. It places the clean lines first, strongest first,
   then the lines on peaks shared with something else, then the lines in delayed coincidence.
   A placement must agree with the flags, the energy sums within 0.35 keV (`RITZ_KEV`), the measured coincidence
   strengths and the intensity balance at each level. A level with no line out may leave through one unseen transition
   under the 60 keV threshold. That search finds two schemes at 17 levels, the ground state included, and none below,
   and keeps the one whose predicted coincidence strengths lie closest to the measured ones. The other places
   551.8 keV from a level at 2041.4 keV to 1489.6 keV, beside 647.8 keV rather than above it: it predicts a strength
   of 0.847 for 551.8 keV with the 647.2 keV peak, where the run gives 1.948 ± 0.017 and the scheme kept 1.847
   (`[placement search]`).
7. `split_intensities` shares a doublet in one cascade between the members from what the scheme predicts, and
   `split_moved` shares a doublet that the gates tell apart from the gates on the lines below each member, whose ratio
   leaves the scale of the coincidences out.
8. `hidden_members` looks under strong peaks for a transition the singles cannot show. For each difference of two
   levels with no transition between them that lies 0.4 to 1.6 keV from the centroid of a peak of I ≥ 4, it fits the
   peak with two members at those two energies under one common shift, with the line shape measured on up to eight
   lines that stand alone (a Gaussian with an exponential tail on its low-energy side), and keeps the second member
   as a transition when its share stands above five times its error, which includes the rms share that made-up
   members beside those lines take. The gates on the lines below the two members check the share
   (`[a weak transition under a strong line]`).
9. `refine_levels` fits the level energies to all the line energies by weighted least squares, and `isomer_half_life`
   finds the level with every pair across it delayed and fits the exponential of the delay spectrum, using the
   opposite side of zero as the chance background.""")
rep("""The reference is within 0.020 keV on levels and 0.030 keV on γ-ray energies. Energies read
  from gated spectra instead of singles, over 154 gates, scatter by an rms of 0.043 keV with a largest departure of
  0.288 keV. The room lines after the gain correction scatter by 0.016 keV.""",
    """The reference is within 0.070 keV on levels and 0.060 keV on γ-ray energies. Energies read
  from gated spectra instead of singles, over 162 gates, scatter by an rms of 0.054 keV with a largest departure of
  0.420 keV. The room lines after the gain correction scatter by 0.025 keV.""")
rep("""- **25% on intensities.** The reference is within 9.1 percent, on the weak 1081.40 keV member (1.11 for 1.22).
  Intensities tested through coincidences instead of singles, over 47 pairs, come out at measured over predicted of
  mean 1.016 and rms 0.061. One pair lies further from 1 than the band, 318.4 keV with 1606.6 keV at 1.261: the
  1606.6 keV peak also holds the sum of 524.3 and 1082.2 keV (1.16 as read, 0.96 once the sum is removed, `[sum
  peaks: ...]`), and that cascade ends in 318.4 keV as well. The band is wider than the reference's error and that
  rms, because a different efficiency fit, a different way of sharing a doublet or a different handling of the sum
  can reasonably move a line that far: the weak member's share is 0.059 from the singles centroid and 0.080 from the
  gates, against 0.086 in the scheme. It still rejects the whole-peak readings of 842.70 keV (4.08 for 2.70) and
  707.97 keV (4.74 for 3.15).""", """- **25% on intensities.** The reference is within 10.3 percent, on the weak 1081.40 keV member (1.78 for 1.61).
  Intensities tested through coincidences instead of singles, over 53 pairs, come out at measured over predicted of
  mean 1.005 and rms 0.065, and none lies further from 1 than the band. The furthest, 318.4 keV with 1606.6 keV at
  1.208, has a reason: the 1606.6 keV peak also holds the sum of 524.3 and 1082.2 keV (1.19 as read, 1.00 once the
  sum is removed, `[sum peaks: ...]`), and that cascade ends in 318.4 keV as well. The band is wider than the
  reference's error and that rms, because a different efficiency fit, a different way of sharing a doublet or a
  different handling of the sum can reasonably move a line that far: the weak member's I is 1.78 from a fit with the
  line's tail and 1.57 from the gates, against 1.61 in the scheme. It still rejects the whole-peak readings of
  842.71 keV (4.11 for 2.69) and 707.97 keV (4.74 for 3.14), and the weak member fitted with Gaussians that leave out
  the tail (2.12 for 1.61).""")
rep("""The reference gives 4.370 s, 0.00 percent off. Fitted line by line, the four
  strongest lines that die away give 4.355, 4.390, 4.375 and 4.430 s against 4.370 s,""",
    """The reference gives 4.365 s, 0.11 percent off. Fitted line by line, the four
  strongest lines that die away give 4.370, 4.365, 4.370 and 4.310 s against 4.370 s,""")
rep("feeders give 158.5 to 171.0 ns against 168.0 ns", "feeders give 163.5 to 170.0 ns against 168.0 ns")
rep("""The level count has no band: the
search finds no scheme with 16 levels or fewer and one with 17, and with 18 it finds one more, which adds a level at
2917.6 keV and a second unseen transition that no peak calls for (`[placement search]`). The data do not exclude that
extra level, so the instruction states the rule that decides: of the schemes that agree with the data, the one with the
fewest levels, which is how spectroscopists adopt a level, only when the data call for it. The rule selects the 17, and it leaves no tie to break: the search finds a single scheme with 17 levels. The
`relative_intensity` floor of 0.5 excludes nothing the scheme holds: the weakest right transition in
`tests/expected.json` is the 1606.60 keV line at 1.001, twice the floor.""", """The level count has no band: the
search finds no scheme with 16 levels or fewer and two with 17. The second places 551.8 keV from a level at 2041.4 keV
to 1489.6 keV, beside 647.8 keV rather than above it, and the coincidences exclude it: it predicts a strength of 0.847
for 551.8 keV with the 647.2 keV peak, where the run gives 1.948 ± 0.017 and the scheme kept 1.847. With 18 levels the
search finds three more, each with a second unseen transition that no peak calls for: one adds a level at 2917.6 keV,
and two hold the excluded level at 2041.4 keV (`[placement search]`). The data do not exclude the level at
2917.6 keV, so the instruction states the rule that decides: of the schemes that agree with the data, the one with the
fewest levels, which is how spectroscopists adopt a level, only when the data call for it. The rule selects the 17,
and it leaves no tie to break: the only other scheme with 17 levels disagrees with the coincidences. The
`relative_intensity` floor of 0.5 excludes nothing the scheme holds: the weakest right transition in
`tests/expected.json` is the 1606.60 keV line at 0.999, twice the floor.""")
rep("The reference takes well under a minute on one CPU (`[files]`)", "The reference takes under a minute on one CPU (43 s, `[files]`)")

assert "\r" not in s
open(PATH, "w", encoding="utf-8", newline="").write(s)
print("README.md edited")
