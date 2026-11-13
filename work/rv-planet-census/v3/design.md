# rv-planet-census v3 design (2026-11-11)

## Why v3

pass@8 on Astra 6 (job 20848, 2026-11-11 19:28) solved 4 of 4 and ended "out of range": too easy. Every designed trap of
v1 fell in every attempt of both models (pass@3 Sol 6.1, pass@8 Astra 6). One step none of the 7 attempts took: each
saw power near 57 d, called it the first harmonic of e's eccentric 115 d orbit ("An eccentric roughly 113.5-day orbit
accounts for the 57-day harmonic, so that harmonic should not be counted separately", pass@8 a2) and never tested a
second planet. In v1 that reading was right (e had e = 0.31).

The briefing's lesson from gamma-decay-scheme (2026-11-11 18:34): against Astra 6 a trap that only decides whether a
signal gets noticed does not hold; the task needs a step where careful, standard analysis still has to make a judgement
that the data settle.

## The change

A planet f, not transiting, just inside half of e's period, and e made nearly circular. The tempting census (e
eccentric, no f) is the one every attempt produced. This is the degeneracy of Anglada-Escude, Lopez-Morales and
Chambers (2010, ApJ 709, 168, "How eccentric orbital solutions can hide planetary systems in 2:1 resonant orbits"); see
also Wittenmyer et al. (2013, ApJS 208, 2), who refit single eccentric planets as 2:1 pairs.

- f: P 56.90 d (e's half period is 57.65 d; ratio 2.026, just wide of 2:1 like many Kepler pairs), K 1.80 m/s, e 0,
  tc 2460300.430 = e's dip + 0.52 P_f. m sin i 8.45 Earth masses. No transit (a/R* about 82; f's conjunction falls on
  data 1.2 d from the binary's secondary eclipse and 1.9 d from its primary).
- e: e 0.31 -> 0.04, w 0.95 -> 1.20 rad; P, K, tc, R, b unchanged. m sin i 19.60 (was 18.65). Its transit now lasts
  6.16 h (was 4.9 h).
- Photometry: white 680 -> 520 ppm, red 90 -> 60 ppm. Sol's pass@3 a1 failed only on b's radius (+9.3% against the 8%
  band), partly from noise (probe `v1/explore/probe_b4.py`: sd 3.6 to 4.0% on 200 synthetic curves). Lower noise keeps
  the radius band a test of method (dilution, detrending) rather than of luck.
- Same seed and draws: f adds no random draw, the noise scales only multiply draws, so visits, activity and noise
  realizations are v1's.

## What settles it (probes, before the generator run)

`v3/explore/probe_phase.py P_f K_f PHASE...` on the generator's own visits, activity and noise, with the activity either
removed exactly (the planets' evidence alone) or left in and regressed on Halpha (a crude activity model):

| K_f | phase | chi2 single - pair, exact | crude Halpha | single reading of e | conjunction vs dip | duration x | b to match | pair K_f |
|---|---|---|---|---|---|---|---|---|
| 1.6 | 0.52 | 51.4 | 26.1 | e 0.32, w -91 | +1.2 +- 1.9 d | 1.39 | 0.80 | 1.30 |
| 1.8 | 0.52 | 69.6 | 32.7 | e 0.34, w -91 | +1.3 +- 1.9 d | 1.43 | 0.82 | 1.50 |
| 2.0 | 0.52 | 92.0 | 42.8 | e 0.37, w -91 | +1.4 +- 1.9 d | 1.47 | 0.83 | 1.70 |
| 2.2 | 0.52 | 119.1 | 57.0 | e 0.39, w -91 | +1.5 +- 1.9 d | 1.51 | 0.84 | 1.90 |

Phase choice: near 0.52 the single eccentric reading puts e's conjunction on the dip, so the transit timing does not
expose it (at phases 0.25 and 0.75 it misses the dip by 12 to 14 d, at 0.0 its transit would be too short for any b).
Phase 0.50 was dropped because f's conjunction fell 0.02 d from the binary's secondary eclipse.

What the eccentric reading costs: f is missing (test_planets_found), and e's transit at that eccentricity is about 1.4
times as long as the true orbit's at the same chord, so with the stated stellar density the dip needs b about 0.82
(true 0.42), where the limb is darker: e's radius comes out about 10% large (test_radii). A reading that adds f but
keeps e eccentric splits f's signal with e's harmonic and puts K_f low.

## Risk: f's K

f's sinusoid and e's first harmonic drift apart by only 0.21 cycles over the 917 d span (correlation about 0.9), so the
split between K_f and e's eccentricity is the least certain number in the census: about +-0.27 m/s. In this noise
realization the exact-activity pair fit puts K_f 0.30 m/s low at every K_f tried (phase 0.52); across phases the offset
ran from -0.40 to +0.36 m/s. The 25% band is 0.45 m/s at K_f 1.8 and 0.55 at 2.2. Choose K_f from the reference's GP
result in `tests/checks.txt`, keeping the reference well inside the band.

## Mutual perturbation

Near 2:1 the planets perturb each other. Near-resonant timing variations (Lithwick, Xie and Wu 2012) for these masses:
about 0.09 d for f and 0.03 d for e over a super-period of about 4400 d, which moves the velocities by about 0.02 m/s,
far below the noise. The generator sums Keplerian orbits.

## 20:45: generator run 1 and the GP probes (the 2:1 design at phase 0.52 is unfair)

Run 1 (K_f 1.8, phase 0.52): the reference read e as one eccentric orbit (e 0.326, w -77 deg), missed f and put e's
radius at 3.211 (+8.8%). Under its own noise model (`probe_gp.py`, `probe_gp_run1.out`) the true configuration scores
the same as the eccentric reading (lnL -607.70 against -607.53), and K_f comes out 1.29 +- 0.26 (-28%).

`probe_kgrid.py` (`probe_kgrid_a.out`): with e and f held at the truth, the reference's model pulls K_f by about
0.5 cos(2 pi phase) m/s, phase after e's dip, for every P_f from 55.5 to 57.4 d: a broad residual of the activity,
phased on e's dip in this realization. Phases 0.0 and 0.5, the only ones where the eccentric reading puts e's
conjunction on the dip, are exactly where K_f is pulled 28 to 31% off. A fair hidden version would need e's dip
moved by about P_f / 4.

`probe_nof.py` (`probe_nof.out`): without f, the activity alone gives e only e 0.17 at w +95 deg, dlnL 2.2 over
circular, a transit 0.87 times as long: no radius trap of its own.

`probe_scan2.py` (`probe_scan2_a.out`), fixed noise, chi2 differences:

| K_f | phase | K_f held | K_f pair (f circular) | single - pair | single e, w, K_e | single conj vs dip | single, conj held on dip - pair |
|---|---|---|---|---|---|---|---|
| 1.8 | 0.75 | 1.70 (-6%) | 1.85 | 13.4 | 0.41, +17, 4.07 | -12.1 d | 35.1 |
| 2.0 | 0.75 | 1.90 (-5%) | 2.01 | 17.1 | 0.43, +12, 4.21 | -13.0 d | 40.4 |
| 1.8 | 0.80 | 1.86 (+4%) | 2.16 | 14.9 | 0.48, +42, 4.34 | -9.9 d | 43.7 |
| 1.8 | 0.70 | 1.54 (-14%) | 1.48 | 9.3 | 0.40, -7, 3.96 | -14.0 d | 24.0 |
| 1.8 | 0.25 | 1.90 (+6%) | 2.71 | 8.2 | 0.44, +168, 4.28 | +13.6 d | 35.6 |
| 1.8 | 0.52 | 1.29 (-28%) | 1.75 | 2.3 | 0.33, -76, 3.54 | -4.3 d | 2.7 |

## v3c: f at phase 0.75, K_f 2.0 (the transit time settles it)

f: P 56.90 d, K 2.00 m/s, circular, tc 2460313.517 (0.75 P_f after e's dip; on data, 0.87 d from the binary's
primary eclipse). e nearly circular as before. The velocities alone prefer the pair only mildly (dlnL about 8.6,
below the 15 any search asks of a new planet), so the eccentric reading stays the natural one; it puts e's conjunction
about 13 d before the dip. The single dip is e's (no other planet can make it: the only one with no other transit on
the data; its duration matches e's circular orbit at b 0.42 with the stated density). Held there, the eccentric reading
loses dlnL about 20 to the pair, and the residual then shows f. So the data settle it for an analysis that uses the
transit time in the velocity fit, which is standard for single transits (joint fits), and only Astra's a4 did it in v1.

Reference change: once a single dip is assigned to a planet, the velocities are refitted with that planet's conjunction
held at the dip and the planet search continues from there (then the 2:1 test). The assignment itself becomes a test:
each planet with no other transit on the data and a circular duration within 0.5 to 1.6 of the dip's is held at the dip
in turn; the best is kept if its likelihood is within 2 of the unheld model's or better.

## 21:23: run 2 and f's eccentricity

Run 2 (v3c data, reference with the hold) found all five planets, rejected the eccentric reading of e after the hold
and put e's radius +5.5%, but fitted f with e 0.731 and K 2.854 (+42.7%; minimum mass -3.0%). Under the reference's
noise model with the hold (`probe_ecc.py`, `probe_ecc_run2.out`):

| model | lnL | f: P, K, e | e: P, K, e |
|---|---|---|---|
| reference's final, refitted | -605.68 | 56.247, 2.84, 0.73 | 114.873, 3.20, 0.14 |
| f circular | -607.47 | 56.769, 2.01, 0 | 114.725, 3.25, 0.12 |
| f and e circular | -606.96 | 56.754, 2.08, 0 | 114.868, 3.19, 0 |
| from the truth, f circular | -607.21 | 56.753, 2.03, 0 | 114.782, 3.21, 0.07 |
| from the truth, all free | -607.18 | 56.720, 2.06, 0.06 | 114.827, 3.20, 0.04 |
| truth for e and f held | -610.15 | 56.900, 1.88, 0 | 115.300, 3.23, 0.04 |

f's eccentricity buys dlnL 1.8 for two parameters (Lucy and Sweeney 1971 at 5%: chi-square 5.99, dlnL 3.0; BIC
would ask about 6), and the e 0.73 orbit's apoapsis (1.726 a_f) lies beyond e's periapsis (1.392 a_f): crossing
orbits of 9 and 19 Earth masses. Two standard arguments, each enough, make f circular, and then K_f is 2.01 to 2.08.

Reference (run 3): `crossing_penalty` in every fit; the pair in `pair_test` stays circular (Anglada-Escude et al.
compare one eccentric orbit with two circular ones); `eccentricity_test` after the single dips refits each orbit
circular (least significant K first) and keeps it circular unless the eccentricity raises lnL by 3.0.

For the solver this is a second judgement after the 2:1 one: an eccentricity fitted freely to a 2 m/s planet among
the activity runs to 0.73 and inflates K by 40%; it is neither significant nor physical.

## 21:47: run 3 agrees

Reference 1072 s. All five planets, all circular after `eccentricity_test` (eccentricity gains: c 1.28, f 0.16,
e 0.01, d 0.80, b 0.48; 3.0 needed). Errors: f P -0.26%, K +3.2%; e P -0.39%, K -3.1%, R +2.0%; c K -6.7%; b R -0.7%;
rotation +0.1%. Unheld: e eccentric (0.43), pair dlnL 7.91 < 15 (the velocities alone do not settle it, as designed).
Held on the dip: -10.0 for the eccentric reading, f found at dlnL +18.00, five planets 8.0 above the eccentric four.
Other noise models: f's K 1.90 to 2.12, e's 2.99 to 3.18, c's 2.62 to 2.89. Without the second star's light the radii
come out 10.6 to 13.5% small. Kept eccentric (e 0.22, w -1.54), e's transit would last 1.30 times as long and need
b 0.74, radius about +7%.
