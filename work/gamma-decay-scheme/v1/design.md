# gamma-decay-scheme v1 design

Goal: a data-reduction task whose difficulty is inference from messy evidence, not a fully specified computation,
because every fully specified computation so far was solved 3 of 3. The only earlier failure came from trusting a wrong
record, and it was judged unfair because NOTES promised the variations were listed. So NOTES here states the station's
facts and promises nothing about the records.

## Scheme (`TARGET` in `tests/generate.py`)

Level: energy keV, β feed, branches.

- A 318.4, 6, g
- B 842.7, 9, A96 g4
- C 1489.6, 3, B88 g12
- Da 1640.3, 1, A
- Db 1641.6, 1, A
- E 1925.0, 2, B65 C30 A5
- F 1963.1, 2, E (38.1 keV, unseen; isomer, 168 ns)
- G 2137.4, 2, C
- H 2581.6, 5, Da50 B35 C15
- I 2633.0, 5, F40 E30 C20 Da10
- J 2689.2, 5, G
- K 2792.5, 6, Db50 C35 E15
- L 2861.4, 6, F45 B40 Db15
- M 3092.6, 9, A45 Da20 I20 L15
- N 3148.8, 5, G

Daughter's own decay: a 403.4 (18), b 1111.3 (12; a15 g85), c 1326.5 (10; b60 a40), so 707.9 sits under the real 708.0.
Isobar: a 471.8 (60), b 1539.3 (25; a70 g30).

## Reference route (`solution/solve.py`)

Source gain, efficiency, escape ratios. Production gain from the room lines. Time-in-cycle shares. Escape peaks by
ratio, sums by S = C / (N − 1). Doublets by self-coincidence and gate centroids. Flags for every pair. Exhaustive
placement with fewest levels. Refined levels, split intensities, isomer from the delayed spectra.

## Bands and why

0.5 keV, 25%, 2%, 8%: see the README's Verification explanation and `tests/checks.txt`. Each sits outside the spread of
the other routes and inside the wrong readings that matter.

## Dials

- Harder: smaller doublet gaps, more shared lines, weaker coincidence statistics, a hidden-data program mode.
- Easier, only if the failure is unfair: wider doublets, stronger delayed statistics.
