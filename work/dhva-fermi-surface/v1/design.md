# dhva-fermi-surface v1: design (2026-11-10)

DAS task ID 4034278 (user, 2026-11-10: "build high difficult science/physics task and submit with DAS task id
4034278"). Built after reading the briefing and the logs.

## Why this shape

The logs say forward-model fits and fully stated computations go 3/3 (chapman, kater), and the designs that qualified
(gamma-decay-scheme, rv-planet-census) are data-only inference tasks (RUN_PROGRAM=0) where the answer depends on
identifying what each feature of the data is, with several independent traps, each a standard expert check. The model's
weakness there: it dismisses a real signal that coincides with a known artifact, and it checks what it produced, not
what it left out.

This task carries that to quantum oscillations: de Haas-van Alphen magnetization sweeps of an invented metal, B || c,
5-35 T, twelve temperatures 0.35-18 K. Deliverable: every extremal orbit's frequency (0.5%) and cyclotron mass (10%),
nothing for harmonics or other frequencies, fewest orbits when the set is not unique.

## The Fermi surface (tests/generate.py ORBITS, invented)

| orbit | F (T) | m* | T_D (K) | g | trap |
|---|---|---|---|---|---|
| alpha | 461.30 | 0.660 | 1.30 | 2.08 | strong; its harmonics up to 7 alpha are in the data |
| gamma | 927.60 | 0.270 | 2.60 | 1.94 | 5.0 T above 2 alpha: one blended peak in every cold spectrum; light, so it alone survives at 9-18 K |
| epsilon | 1186.40 | 0.480 | 1.00 | 2.00 | spin factor cos(0.48 pi) = 0.063: weak fundamental, 2 epsilon stronger than it |
| beta_neck | 2641.00 | 1.210 | 1.10 | 2.10 | neck and belly of one sheet, 61.6 T apart: both are orbits |
| beta_belly | 2702.60 | 1.290 | 1.10 | 2.10 | |
| delta | 7415.00 | 3.350 | 0.80 | 1.90 | heavy: seen only in a high-field window at the lowest temperatures |

Signal: Lifshitz-Kosevich, 3D prefactor B^(1/2) p^(-3/2), R_T, R_D, R_S, harmonics to p = 8. Background: smooth
paramagnetic slope, small B^2 and B^3 terms, slow drift; white noise 2.0 per reading; single-point transients.

## Reference (solution/solve.py)

Spectra (Blackman-Harris, cubic background) of the coldest sweep over 6-35 T and 22-35 T; harmonic bookkeeping in
ascending frequency; amplitudes against temperature by linear least squares over 14-35 T with a Lifshitz-Kosevich
envelope for every column (fundamentals and harmonics); masses and Dingle temperatures refitted until they settle; a
harmonic column that its orbit's mass cannot explain (chi-square per degree of freedom above 10 at p m) is searched in
the sweeps where the harmonic has died away, which finds gamma.

## Changes during the build (2026-11-10)

- Audit 1: polynomial envelopes in the regression were ill-conditioned for close pairs (gamma's amplitude 1.5e9).
  Replaced by Lifshitz-Kosevich envelopes from the current mass and Dingle temperature.
- Audit 2: the anomaly test also asked for the harmonic's own mass to be 30% off, which kept the 2 alpha column (chi2
  2857, 21% off) from being flagged; dropped. The Dingle search's parabola through a sqrt(2) grid was biased; replaced
  by a bounded search.
- Audit 3: the reference found gamma (then at 936.50) and every mass within 5%. But a Hann spectrum of a whole cold
  sweep resolved gamma from 2 alpha (935.4 and 922.6 T), so the trap was weak: gamma moved to 2 alpha + 5.0 T = 927.60 T,
  inside every window's resolution. delta's amplitude 1.26 -> 2.0: its mass was -6% +- 2% on the shipped draw.
  The alternating mass/Dingle fit now runs until it settles (it had not after 4 rounds from a cold start: alpha +1.8%).
- Generator run 1 (22:44): AGREES, but delta's mass scattered -0.5/+4.8/+7.0% over three further noise draws, and the
  textbook Fourier peak-height route is off by up to 8.5% in a 22-35 T window. Mass band 10% -> 15%; frequencies of
  every orbit standing 10 sigma out are refined (delta's had stayed at its spectral value).
- Generator runs 2 and 3 (23:05, 23:14; run 3 only adds the Fourier-resolution line): AGREES. Frequencies within
  0.005%, masses within 0.6% except delta -4.0%; further draws within 1.3% except delta (-1.6, +2.8, +2.5%). Routes:
  the 6-35 T inventory alone has no peak near gamma or delta; frequency-only classification drops gamma; every peak
  as an orbit adds seven harmonics; gamma's mass from the blended peak +212 to +282%, from >= 4.5 K +7.4%, from
  >= 6.5 K -1.4%; arithmetic-mean field over 14-35 T +13 to +22%.

## What pass@3 should show

- 3 of 3: the traps are routine for the target model. Harder evidence next: gamma closer to 2 alpha or weaker, a
  second hidden orbit, magnetic-interaction combination frequencies that are not orbits.
- 0 of 3: check first whether gamma was found and dropped for a stated reason, whether delta was seen at all, and
  whether masses failed on precision (compare with checks.txt [4] and [5]) before easing through the evidence.
