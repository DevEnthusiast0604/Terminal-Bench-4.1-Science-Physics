from pathlib import Path
p = Path("logs/BRIEFING.md")
t = p.read_text(encoding="utf-8").rstrip("\n")
t += """
- (2026-11-12 02:05) dhva-fermi-surface v2 (internal field B = mu0 H + mu0 (1 - N) M, magnetic interaction) went
  0 of 3 on Sol 6.1, but not on the new physics: every attempt converted the field axis from its first steps (NOTES
  gave the bar's size and called the moment the sample's own; the magnetic-interaction combinations let them fit K
  from the data). All three lost the heavy orbit delta instead, two of them through coincidences nobody designed:
  gamma's eighth harmonic 5.8 T away (absorbed by a free-amplitude harmonic) and a combination of the other orbits
  matching delta in frequency (0.03%) and mass (1%), read as a "composite" and dropped by the fewest-orbits rule. Before
  a generator run, test every planted signal against harmonics up to the generated order and against integer
  combinations of the others as deep as attempts search (sum |n| <= 10), in frequency and in mass:
  `combinations_near` in dhva's `tests/generate.py` does it and writes the result to checks.txt [1].
"""
p.write_text(t + "\n", encoding="utf-8", newline="\n")
print("ok")
