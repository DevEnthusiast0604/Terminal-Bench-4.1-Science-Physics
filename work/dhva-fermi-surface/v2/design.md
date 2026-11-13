# dhva-fermi-surface v2: design (2026-11-11)

T-1563, DAS 4034278. v1 came back 3 of 3 (job 21089, Sol 6.1): every trap fell to a direct least-squares fit of the
exact Lifshitz-Kosevich model in field space. Approved order, step 3 (new physics), since the attempts handled the
current challenge cleanly.

## What v1 shows about the model

- It reads NOTES, despikes, takes spectra of several sweeps over several windows, then fits the LK model (harmonics
  with p F, p m, spin factors) to every sweep and drives the residual to the noise. Anything built from that model
  falls: a blend (gamma), a spin zero (epsilon), a heavy orbit (delta), a close pair (beta), harmonics.
- None of the three attempts turned the moment into a magnetization. v1's own background (1500 units per T on a
  0.045 mm^3 sample) means mu0 M = 4.2% of the field: a real sample like that has oscillations periodic in
  1/B with B = mu0 H + mu0 (1 - N) M, not in 1/(mu0 H). v1's generator ignored this, and so did the attempts.

## v2: the field the electrons feel

Landau quantization follows the flux density inside the sample, B = mu0 H_a + mu0 (1 - N) M (uniform-magnetization
approximation; H_a the applied field, N the demagnetizing factor along the field, M the sample's whole
magnetization). An expert analysing a strongly magnetized sample converts the field axis before any spectrum.

- The sample: a bar 0.250 x 0.200 x 1.600 mm, field along its length (c). N = 0.0628 (Aharoni 1998, rectangular
  prism; checked: cube 1/3, three axes sum to 1). V = 0.0800 mm^3. K = mu0 (1 - N) 1e-9 / V = 1.47e-5 T per moment
  unit (1e-9 A m^2).
- The sample's steady magnetization: van Vleck-like, nearly linear (S1 B + S3 B^3), so B exceeds mu0 H by about 2%:
  every frequency read against the applied field is about 2% low, four times the 0.5% band. No other symptom: a pure
  scale cannot be fitted away (it is degenerate with F).
- The oscillatory magnetization feeds back too (magnetic interaction, Shoenberg ch. 6): alpha made stronger so that
  a = K dm~/dB reaches about 0.2 in the coldest sweep. Against the applied field this adds harmonics whose damping
  is not that of an LK harmonic and combination frequencies (2 epsilon +- alpha, gamma +- alpha, beta +- alpha) that are
  not orbits. Against B they vanish exactly: M is a function of B.
- The answers are unchanged (ORBITS' F and m). What changes: the data (built through the self-consistent B(H)), NOTES
  (bar dimensions, the moment is the sample's own after the empty-cell run, the field column is the magnet's field),
  the instruction (frequency defined as F = hbar A / (2 pi e), so it is a property of the Fermi surface), the
  reference (converts with the measured moment first), checks.txt and the README.
- Routes for checks.txt: the reference against the applied field (no conversion) and with the oscillatory part only
  (the textbook MI correction without the steady magnetization): both put every frequency about 2% low.

## Fairness

- Every input of the conversion is in the files: the moment (the sample's own), the bar's dimensions (V and N), the
  applied field. N's formula hardly matters: N = 0 instead of 0.0628 moves every frequency by 0.14%; an ellipsoid
  estimate (0.03) by 0.07%.
- The instruction defines the frequency through the orbit's area, so the right value does not depend on the field
  variable an analysis happens to use.

## What pass@3 should show

- 1 or 2 of 3: the attempts that convert pass, the others fail every frequency.
- 0 of 3: check whether any attempt computed the magnetization at all; then the dial is a sentence of fact in NOTES
  (the sample's mu0 M at 35 T), or stronger magnetic interaction.
- 3 of 3: the conversion is routine for the model; harder evidence next.
