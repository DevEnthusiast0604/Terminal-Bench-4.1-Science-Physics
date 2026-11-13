from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
review = ("| 2026-11-12 01:36 | the same card, reviewed | Marked seen 01:50. pass@3 of v2 (job 21778): **0 of 3** solved, "
          "rewards [0, 0, 0]; each attempt reported the five lighter orbits within 0.15% and 4% and left out delta "
          "(7415 T). Every attempt converted the field axis. Analysis under \"pass@3 analyses\" (v2). Status REWORK: "
          "v3 moves delta clear of the accidental coincidences two attempts used to drop it. | yes |")
marker = "\n\n## pass@3 analyses"
i = t.index(marker)
t = t[:i] + "\n" + review + t[i:]
analysis = """
### v2 (T-1563 v2, job 21778, pass@3 ended 2026-11-12 01:36): 0 of 3 solved, TOO HARD

- Sol 6.1, rewards [0, 0, 0]; each failed `test_orbits_found` and `test_masses`. Agent times 21, 11 and 10 min (50,
  30 and 28 episodes), cost $0.89, $0.38 and $0.40. Bundle in `work/dhva-fermi-surface/v2/pass3/` (`pass3.zip`,
  untrusted extraction under `x/`, `summary.md`); answers in `work/dhva-fermi-surface/v2/attempts/programs/aK/
  orbits.json`, digests in `attempts/attempt-K.txt`.
- Answers: five orbits each time, delta missing in all three. The five are right: a1 and a3 within 0.008% in
  frequency, a2 0.04-0.15% high (as with N = 0); masses within 1.5% (a1, a3) and 3.7% (a2).
- The internal field fell in every attempt, from the first steps: a1 noted the dimensions and the moment at once,
  inferred the induction correction from the oscillations and checked it against the bar's demagnetizing factor
  (0.06283, the same formula as the reference); a2 computed mu0 m / V and fitted the coefficient; a3 estimated N
  and compared spectra against mu0 H and against B. The magnetic-interaction combinations make K measurable from the
  data (they vanish only at the right K). So the v2 physics is routine for the model; it costs no attempt.
- Why delta was lost, each a different way:
  - a1 found it (fit 7414.75 T, m 3.20) and then dropped it as a composite, 4 x 1186.4 + (2641.0 + 2702.6) / 2 =
    7417.4 T with summed mass 3.17, "stronger evidence for a breakdown/composite oscillation than for an additional
    extremal orbit", and wrote the fewest-orbits set. The match is an accident of the orbit table: within 0.03% in
    frequency and 1% in mass.
  - a2 searched residuals over the whole sweep (1/B from 0.030 to 0.190, Hann taper, five coldest sweeps averaged)
    and never a high-field window; delta, damped below 20 T, sits at the tapered end and came out at the noise level
    (7417.74 T, 0.057 against a floor of about 0.06). This is the designed trap ("A heavy orbit seen only at high
    field").
  - a3 saw the high-frequency residual and put it down to omitted harmonics of gamma and epsilon, then fitted those
    with free amplitudes. gamma's eighth harmonic is 7420.8 T, 5.8 T from delta and unresolvable at high field; by
    Lifshitz-Kosevich it is 0.10 units at 30 T against delta's 2.34, so the reading is wrong, but the coincidence
    let a free-amplitude model absorb delta.
- Fairness: the instruction asks for every orbit the sweeps show; the fewest-orbits rule applies only to sets that
  account for every oscillation, and neither reading does by Lifshitz-Kosevich (a composite of a mean frequency is no
  orbit; 8 x gamma's amplitude is 24 times too small). But two of the three dismissals rest on coincidences nobody
  designed and the README never mentions: 8 x gamma 0.08% from delta, and a combination of the other orbits within
  0.03% and 1% in mass. v1's attempts met the same coincidences and rejected both by mass.
- A scan (`work/dhva-fermi-surface/v3/explore/delta_scan2.py`) over every integer combination of the other five
  orbits with sum |n| <= 10 (the depth a1 searched): at delta's 7415 T one lies within 0.1% in frequency and 15% in
  mass; at 7290-7310 T and 7560 T none does (the lightest within 0.1% at 7300 T weighs 5.23), and the nearest
  harmonic is 111-139 T away.
- Next (v3): delta at 7300 T, everything else as v2 (its mass 3.35, Dingle temperature, g and amplitude unchanged, so
  it is still seen only at high field and in the cold sweeps). The designed trap stays; the accidental readings go.
  Answers change (delta's frequency), so the generator runs again.
"""
marker2 = "\n## Pitfalls"
j = t.index(marker2)
t = t[:j].rstrip("\n") + "\n" + analysis + t[j:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
