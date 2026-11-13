"""v14 README: every figure from the v14 checks.txt; the hidden line now I 2.44 with its share from the gates; the
doublet rule in the flags; a single scheme with 17 levels again. Exact-match replacements; run from the folder root."""
PATH = "tasks/active/gamma-decay-scheme/README.md"
s = open(PATH, encoding="utf-8", newline="").read()


def rep(old, new, count=1):
    global s
    assert s.count(old) == count, (s.count(old), old[:80])
    s = s.replace(old, new)


rep("lie off by 0.61 keV at 500 keV, 1.13 keV at 1500 keV and 1.65 keV at",
    "lie off by 0.62 keV at 500 keV, 1.13 keV at 1500 keV and 1.65 keV at")
rep("escape peaks at 1507.65, 1752.20 and 2263.19 keV", "escape peaks at 1507.59, 1752.22 and 2263.21 keV")
rep("""The peak at 1171.51 keV has a
  relative intensity of 0.79 as read and -0.01 once the sum is removed;""", """The peak at 1171.50 keV has a
  relative intensity of 0.78 as read and 0.00 once the sum is removed;""")
rep("""The peak at 842.71 keV is a real crossover
  under a sum, 4.11 as read and 2.74 after""", """The peak at 842.69 keV is a real crossover
  under a sum, 4.11 as read and 2.75 after""")
rep("""The peak at 647.22 keV is in coincidence with itself (13450 counts) and its
  width is 1.19 times the resolution""", """The peak at 647.21 keV is in coincidence with itself (13605 counts) and its
  width is 1.16 times the resolution""")
rep("""The peak at 1322.48 keV has no self-coincidence (0 counts net) but a
  width of 1.28 times the resolution, and its centroid moves from 1321.80 to 1323.24 keV with the gate""",
    """The peak at 1322.47 keV has no self-coincidence (-2 counts net) but a
  width of 1.24 times the resolution, and its centroid moves from 1321.81 to 1323.19 keV with the gate""")
rep("""  318.40 keV by a 1081.40 keV transition of relative intensity 1.61 (`TARGET` in `tests/generate.py`,
  `tests/expected.json`). That lies 0.9 keV under the 1082.30 keV transition from the level at 1925.00 keV, eight
  times stronger. The singles do not flag it: every line but the two doublets has a width of 0.97 to 1.05 times the
  resolution and a self-coincidence strength of at most 0.007, the 1082.2 keV peak among them (`[peaks that are two
  transitions]`).""", """  318.40 keV by a 1081.40 keV transition of relative intensity 2.44 (`TARGET` in `tests/generate.py`,
  `tests/expected.json`). That lies 0.9 keV under the 1082.30 keV transition from the level at 1925.00 keV, five
  times stronger. The singles do not flag it: every line but the two doublets has a width of 0.90 to 1.05 times the
  resolution and a self-coincidence strength of at most 0.012, the 1082.1 keV peak among them (`[peaks that are two
  transitions]`).""")
rep("""  0.96 and none. What points to it is a level difference, 1081.42 keV, 0.78 keV under the peak's centroid. A fit of
  the peak with a second member there, with the low-energy tail that lines standing alone show (0.073 of the area,
  slope 1.53 σ), gives that member a share of 0.1245 ± 0.0191, where made-up members beside lines standing alone take
  an rms share of 0.0144; at the three other level differences near strong peaks the same fit gives -0.0105 ± 0.0146,
  0.0006 ± 0.0151 and -0.0303 ± 0.0888. The proportions of the two gates give 0.1102 ± 0.0128, against 0.1104 in the
  scheme, and Gaussians without the tail give 0.1489: the weak member's I is then 1.78, 1.57 and 2.12 for 1.61, the
  last outside 25% (`[a weak transition under a strong line]`). A peak list matched to level differences finds one
  line at 1082.2 keV and places it once, and the scheme then lacks a transition; read as one line, the peak gives
  14.27 for 12.99, inside the band, so only the missing transition fails.""", """  0.96 and none. What points to it is a level difference, 1081.41 keV, 0.74 keV under the peak's centroid. A fit of
  the peak with a second member there, with the low-energy tail that lines standing alone show (0.092 of the area,
  slope 1.30 σ), finds that member at a share of 0.2149 ± 0.0225, where made-up members beside lines standing alone
  take an rms share of 0.0086; at the three other level differences near strong peaks the same fit gives
  -0.0017 ± 0.0087, -0.0059 ± 0.0095 and -0.0337 ± 0.0846. The fit's share is not good to 25%, though: it follows
  where the peak's centroid sits between the two energies, so an error of 0.05 keV in the energy scale moves it by
  about 0.06. With the tail it gives I 3.15 for 2.44, outside the band, and with Gaussians alone 2.38. The
  proportions of the two gates depend neither on the shape nor on the scale: they give a share of 0.1757 ± 0.0117,
  against 0.1613 in the scheme, and I 2.58 (`[a weak transition under a strong line]`). A peak list matched to level
  differences finds one line at 1082.1 keV and places it once, and the scheme then lacks a transition; read as one
  line, the peak gives 14.67 for 12.66, inside the band, so only the missing transition fails.""")
rep("Of the peak at 707.97 keV only a share of 0.63", "Of the peak at 707.96 keV only a share of 0.63")
rep("Whole-peak intensity is 4.74 where the scheme has 3.14", "Whole-peak intensity is 4.60 where the scheme has 3.06")
rep("with a relative intensity of 4.29: it feeds about half", "with a relative intensity of 4.18: it feeds about half")
rep("gives a σ of 1.50 keV where a line has 0.67 keV", "gives a σ of 1.48 keV where a line has 0.69 keV")
rep("scaled from the background run, 3403 counts,", "scaled from the background run, 3346 counts,")
rep("the peak gives 5.00 whole and 4.78 less that room share, inside 25% of 4.29;",
    "the peak gives 4.75 whole and 4.54 less that room share, inside 25% of 4.18;")
rep("""broad part of 11854 ± 1088 counts and a narrow part of 64249 ± 879 counts, a share of
  0.99 of which follows the parent's time profile, and the narrow part gives 4.22""",
    """broad part of 9955 ± 1300 counts and a narrow part of 65085 ± 1058 counts, a share of
  0.99 of which follows the parent's time profile, and the narrow part gives 4.12""")
rep("""with 941.3 keV (1498 counts),
  1092.0 keV (392) and 1738.9 keV (593)""", """with 941.3 keV (1533 counts),
  1092.0 keV (389) and 1738.9 keV (626)""")
rep("""the
   708.0 keV gate reads the 647.22 keV peak at 646.82 keV, under the 646.88 to 647.08 keV of the other gates on
   lines that reach the lower member alone""", """the
   511.0 keV gate reads the 647.21 keV peak at 646.81 keV, under the 646.85 to 647.01 keV of the other gates on
   lines that reach the lower member alone""")
rep("""   whose two peaks both hold another activity stays undecided, since that activity's own cascade can make it.
""", """   whose two peaks both hold another activity stays undecided, since that activity's own cascade can make it. Each
   member of a doublet in one cascade adds at most one of its γ rays per γ ray of a weaker partner, so a partner that
   comes with more than 1.15 of them, by three standard errors, sees both members whatever its gated centroid says.
""")
rep("""under the 60 keV threshold. That search finds two schemes at 17 levels, the ground state included, and none below,
   and keeps the one whose predicted coincidence strengths lie closest to the measured ones. The other places
   551.8 keV from a level at 2041.4 keV to 1489.6 keV, beside 647.8 keV rather than above it: it predicts a strength
   of 0.847 for 551.8 keV with the 647.2 keV peak, where the run gives 1.948 ± 0.017 and the scheme kept 1.847
   (`[placement search]`).""", """under the 60 keV threshold. That search finds one scheme at 17 levels, the ground state included, and none below
   (`[placement search]`). Were several to fit, it would keep the one whose predicted coincidence strengths lie
   closest to the measured ones.""")
rep("""   members beside those lines take. The gates on the lines below the two members check the share
   (`[a weak transition under a strong line]`).""", """   members beside those lines take. The share it keeps comes from the gates on the lines below the two members,
   which see the two in different proportions and depend neither on the line shape nor on the energy scale
   (`[a weak transition under a strong line]`).""")
rep("""The reference is within 0.070 keV on levels and 0.060 keV on γ-ray energies. Energies read
  from gated spectra instead of singles, over 162 gates, scatter by an rms of 0.054 keV with a largest departure of
  0.420 keV. The room lines after the gain correction scatter by 0.025 keV.""",
    """The reference is within 0.090 keV on levels and 0.070 keV on γ-ray energies. Energies read
  from gated spectra instead of singles, over 160 gates, scatter by an rms of 0.049 keV with a largest departure of
  0.211 keV. The room lines after the gain correction scatter by 0.032 keV.""")
rep("It rejects the uncorrected gain, off by 0.61 keV already at 500 keV", "It rejects the uncorrected gain, off by 0.62 keV already at 500 keV")
rep("""- **25% on intensities.** The reference is within 10.3 percent, on the weak 1081.40 keV member (1.78 for 1.61).
  Intensities tested through coincidences instead of singles, over 53 pairs, come out at measured over predicted of
  mean 1.005 and rms 0.065, and none lies further from 1 than the band. The furthest, 318.4 keV with 1606.6 keV at
  1.208, has a reason: the 1606.6 keV peak also holds the sum of 524.3 and 1082.2 keV (1.19 as read, 1.00 once the
  sum is removed, `[sum peaks: ...]`)""", """- **25% on intensities.** The reference is within 10.0 percent, on the weak 992.70 keV line (0.92 for 1.02).
  Intensities tested through coincidences instead of singles, over 54 pairs, come out at measured over predicted of
  mean 0.998 and rms 0.051, and none lies further from 1 than the band. The furthest, 318.4 keV with 1606.6 keV at
  1.157, has a reason: the 1606.6 keV peak also holds the sum of 524.3 and 1082.1 keV (1.16 as read, 0.96 once the
  sum is removed, `[sum peaks: ...]`)""")
rep("""different handling of the sum can reasonably move a line that far: the weak member's I is 1.78 from a fit with the
  line's tail and 1.57 from the gates, against 1.61 in the scheme. It still rejects the whole-peak readings of
  842.71 keV (4.11 for 2.69) and 707.97 keV (4.74 for 3.14), and the weak member fitted with Gaussians that leave out
  the tail (2.12 for 1.61).""", """different handling of the sum can reasonably move a line that far: the weak member's I is 2.58 from the gates and
  2.38 from a fit with Gaussians alone, against 2.44 in the scheme. It still rejects the whole-peak readings of
  842.69 keV (4.11 for 2.69) and 707.96 keV (4.60 for 3.06), and a share of the weak member that the energy scale
  has moved (3.15 for 2.44 from the fit with the tail in this run).""")
rep("""The reference gives 4.365 s, 0.11 percent off. Fitted line by line, the four
  strongest lines that die away give 4.370, 4.365, 4.370 and 4.310 s against 4.370 s,""",
    """The reference gives 4.375 s, 0.11 percent off. Fitted line by line, the four
  strongest lines that die away give 4.375, 4.355, 4.395 and 4.405 s against 4.370 s,""")
rep("""The reference is within 0.9 percent. Fitted by the line above the isomer, the four
  feeders give 163.5 to 170.0 ns against 168.0 ns""", """The reference is within 0.6 percent. Fitted by the line above the isomer, the four
  feeders give 165.5 to 171.0 ns against 168.0 ns""")
rep("""search finds no scheme with 16 levels or fewer and two with 17. The second places 551.8 keV from a level at 2041.4 keV
to 1489.6 keV, beside 647.8 keV rather than above it, and the coincidences exclude it: it predicts a strength of 0.847
for 551.8 keV with the 647.2 keV peak, where the run gives 1.948 ± 0.017 and the scheme kept 1.847. With 18 levels the
search finds three more, each with a second unseen transition that no peak calls for: one adds a level at 2917.6 keV,
and two hold the excluded level at 2041.4 keV (`[placement search]`). The data do not exclude the level at
2917.6 keV, so the instruction states the rule that decides: of the schemes that agree with the data, the one with the
fewest levels, which is how spectroscopists adopt a level, only when the data call for it. The rule selects the 17,
and it leaves no tie to break: the only other scheme with 17 levels disagrees with the coincidences. The
`relative_intensity` floor of 0.5 excludes nothing the scheme holds: the weakest right transition in
`tests/expected.json` is the 1606.60 keV line at 0.999, twice the floor.""", """search finds no scheme with 16 levels or fewer and one with 17, and with 18 it finds one more, which adds a level at
2917.5 keV and a second unseen transition that no peak calls for (`[placement search]`). The data do not exclude that
extra level, so the instruction states the rule that decides: of the schemes that agree with the data, the one with the
fewest levels, which is how spectroscopists adopt a level, only when the data call for it. The rule selects the 17,
and it leaves no tie to break: the search finds a single scheme with 17 levels. The `relative_intensity` floor of 0.5
excludes nothing the scheme holds: the weakest right transition in `tests/expected.json` is the 1606.60 keV line at
0.974, about twice the floor.""")
rep("The reference takes under a minute on one CPU (43 s, `[files]`)", "The reference takes under a minute on one CPU (22 s, `[files]`)")

assert "\r" not in s
open(PATH, "w", encoding="utf-8", newline="").write(s)
print("README.md edited")
