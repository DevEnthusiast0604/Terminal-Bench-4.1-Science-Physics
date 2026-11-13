# dhva-fermi-surface v3: dials prepared while v2 waits (2026-11-11 12:15 UTC)

v2 went up at 12:11 (T-1563, digest `34941787…7604`). These are prepared moves for each pass@3 outcome; nothing
here is applied until v2's result arrives.

## Evidence before v2

- v1's three attempts (digests in `work/dhva-fermi-surface/v1/attempts/`) never mention the sample's volume,
  dimensions, magnetization, demagnetization, internal field or magnetic interaction (grep, 12:13). v1's NOTES gave
  "about 0.6 x 0.5 x 0.15 mm" and put the background on "the sample and the cell", so there was no cue.
- v2's cues: a bar measured to 1% with the field along its length; the empty cell subtracted, "so the moment is the
  sample's own"; the field column named as the magnet's field; F defined by the orbit's k-space area; combination
  peaks (2eps - alpha, 2eps + alpha, beta + alpha) against the field column that no orbit set explains.

## If 0 of 3

1. Read every attempt for: a computed magnetization or B; the textbook magnetic-interaction correction with the
   oscillatory part only (the `oscillatory` route in checks.txt [4]); combination peaks reported as orbits.
2. Fairness first: confirm the failures are the conversion (every frequency 2.2-2.4% low), not another check.
3. Dial: one sentence of fact in NOTES.md, Sample section, e.g. "The metal is strongly paramagnetic: at 35 T its
   magnetization mu0 M is about 0.7 T." Data and answers unchanged, so no generator run is needed unless the README
   quotes NOTES; README gets one line on the cue. If attempts converted with the oscillatory part only, the sentence
   should rather name the steady magnetization.

## If 3 of 3

The conversion is routine for the model. Candidates, each to be checked against the approved hardening order:
- the field column's own calibration (the pickup coil reads a known fraction off, fixed by an independent marker in
  the data), which ties to the author's experience of calibrating an instrument against a reference;
- a temperature-dependent (Curie-Weiss) steady magnetization, so B / mu0 H differs per sweep and a mass from
  amplitudes read against the field column is biased per temperature;
- magnetic-breakdown combinations that are not extremal cross-sections, told apart from magnetic-interaction
  combinations only by their temperature dependence.

## If 1 or 2 of 3

Tell the user the P3 ID and DAS 4034278. No upload meanwhile.
