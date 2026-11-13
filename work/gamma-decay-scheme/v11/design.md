# gamma-decay-scheme v11 design (2026-11-11)

## Why

v10 (= v9's files) went 8 of 8 on pass@8 (Astra 6, job 21495): every attempt exact, worst intensity error 7-10%
against 25%. v9 had gone 1 of 3 on pass@3 (Sol 6.1). Both v9 traps (the 511 keV line among annihilation radiation, the
sub-threshold step out of the isomer) are routine for Astra 6. The task must now land at 1-2 of 3 on Sol 6.1 and
1-6 of 8 on Astra 6.

## What the pass@8 attempts skip (from `v10/pass8/attempts/`)

- a4's audit `UNASSIGNED GATED PEAKS` drops any gated peak within 4 keV of a peak already on its list.
- a4's `LEVEL DIFFERENCES UNASSIGNED` tests only peaks not yet placed against level differences.
- a4's check for "unexpected high coincidences" skips every pair that involves the 647 or 1322 keV doublet.
- a8 lists level differences within 0.7 keV of each peak, and checks gated centroids of the peaks it already calls
  unresolved.

A weak transition under a strong peak that is already placed, whose only clean gate is a doublet, passes all of these.

## The change

- New level X at 2721.70 keV, fed only by β decay (1.75 per 100 decays), branches 55 to B (1879.00 keV, I 1.49,
  clean) and 45 to Da (1081.40 keV, I 1.22).
- The 1081.40 keV line lies 0.9 keV under E->B (1082.30 keV, I 13.02). In the shipped singles, the 1082.22 keV peak has a
  width of 1.02 times the resolution (single lines 0.94 to 1.03) and no self-coincidence. Only the gate on the 1322 keV
  doublet shows it (centroid 1081.44 keV); the 1082.2 keV gate shows the doublet at 1321.91 keV (Da, not Db).
- X - Da = 1081.40 keV lies 0.82 keV from the singles centroid, outside a 0.5 or 0.7 keV level-difference match.
- No feeder of X (M->X was considered): a gate from above would show the weak line in a clean gate and break a4's
  blind spot.
- 511 keV line back to v8 (H β 2.75, M β 11.75, M->H 31, pair-production annihilation 3.0e-4 per decay; I 4.30, inside
  the band even read whole). v8 gave Sol 6.1 3 of 3, so the new trap carries the difficulty for both models.
- Reference (`solution/solve.py`): a moved doublet whose member holds under a quarter of the peak (by the singles
  centroid) takes that as its first share; a gate whose centroid sits on the strong member leaves the weak member's
  flag undecided (it would otherwise be "absent", and the 318.4 keV gate, which sees both, would forbid the true
  placement); `split_moved` sets the shares from the gates below each member (1322 keV for the weak one, 524.3 keV
  for the strong one), whose ratio cancels the coincidence scale.

## Result of the generator run (18:4x UTC, `tests/checks.txt`)

17 levels and 33 transitions, both matched; energies within 0.030 keV; intensities within 9.1% (the weak member, 1.11
for 1.22); `[placement search]` 0 schemes at 16 levels, 1 at 17, 2 at 18. Reference run time 26 s.

## Expected outcome and the next knob

Guess: Sol 6.1 finds the weak line in perhaps a quarter to a third of attempts, Astra 6 in about half to two thirds.
If pass@3 is 0 of 3 because every attempt misses the weak line, ease it: raise X->Da toward I 1.6, or add a weak
feeder M->X (370.8 keV) whose gate shows the weak line cleanly. If pass@8 is 7-8 of 8, lower X->Da or move it closer
under E->B.
