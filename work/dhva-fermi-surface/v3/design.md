# dhva-fermi-surface v3: design (2026-11-12)

T-1563, DAS 4034278. v2 came back 0 of 3 (job 21778, Sol 6.1). The platform's rule for 0 of 3: fix anything the
instruction never states; if the attempts fail at the stated difficulty, make the task somewhat easier.

## What v2 shows

- The internal field (v2's new physics) is routine for the model once NOTES gives the bar and calls the moment the
  sample's own: all three attempts converted from their first steps, and the magnetic-interaction combinations let
  them fit K from the data (they vanish only at the right K). Every attempt got the five lighter orbits right.
- All three lost delta, each a different way (analysis in `logs/dhva-fermi-surface.md`, "pass@3 analyses", v2):
  1. a composite reading, 4 x 1186.4 + (2641.0 + 2702.6) / 2 = 7417.4 T with summed mass 3.17, matching delta's
     7415 T and 3.35 within 0.03% and 6% (its own fit gave 3.20, within 1%);
  2. no high-field window: a whole-sweep Hann residual, where delta sits at the tapered end (the designed trap);
  3. gamma's eighth harmonic, 7420.8 T, 5.8 T from delta, absorbed it in a free-amplitude harmonic model, though by
     Lifshitz-Kosevich it is 0.10 units at 30 T against delta's 2.34.
- Readings 1 and 3 rest on coincidences in the orbit table that were never designed and that the README never
  mentions. v1's attempts met them too and rejected both by mass; v2's did not.

## v3: delta clear of accidental readings

- delta moves from 7415 T to 7300 T. Nothing else changes: its mass 3.35, Dingle temperature 0.80 K, g 1.90 and
  amplitude 2.0 stay, so it is still damped below 20 T and above 2 K and seen only in a high-field spectrum of the
  cold sweeps. The internal field, the magnetic interaction and every other orbit stay as in v2.
- At 7300 T (`work/dhva-fermi-surface/v3/explore/delta_scan2.py`, and `combinations_near` in the generator):
  the nearest harmonic p <= 8 of another orbit is 8 x gamma = 7420.8 T, 120.8 T away (five resolution elements over
  14-35 T, two over 22-35 T); of the integer combinations of the other orbits with sum |n| <= 10 (the depth attempt 1
  searched), 6 lie within 0.1% and none within 15% of delta's mass (the lightest weighs 5.23).
- The reference's first classification still calls delta an orbit: the nearest harmonic of an orbit it has then
  (6 x epsilon, 7118.4 T) is 181.6 T away, beyond the high-field tolerance of 118 T; gamma joins later and nothing is
  classified again.
- checks.txt [1] reports the harmonic coincidences up to p = 8 (was 6) and the combination count for delta.

## What pass@3 should show

- 1 or 2 of 3: attempts that look at a high-field window keep delta; one that searches only whole sweeps misses it.
- 3 of 3: the high-field trap alone does not hold; next lever is delta's strength (amplitude or Dingle temperature),
  not new coincidences.
- 0 of 3: read each attempt for delta again; if it is found and dropped on some other reading, check that reading's
  Lifshitz-Kosevich consistency before anything else.
