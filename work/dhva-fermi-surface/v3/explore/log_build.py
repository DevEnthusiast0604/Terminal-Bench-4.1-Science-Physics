from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
entry = """- **2026-11-12 01:40-02:50**: v2's pass@3 card (0 of 3, 01:36) logged, analysed and marked seen 01:50 (analysis under
  "pass@3 analyses", v2). v3 built in the active folder (design `work/dhva-fermi-surface/v3/design.md`): delta
  7415 -> 7300 T, its mass, Dingle temperature, g and amplitude unchanged; everything else as v2. `tests/generate.py`:
  ORBITS, the harmonic coincidences up to p = 8 (was 6) and `combinations_near` (integer combinations of the other
  orbits, sum |n| <= 10, in frequency and mass), both written to checks.txt [1]. README: delta's bullet (7300 T, the
  coincidence check), the bands from the new checks, the reference's time.
  - Generator run (01:55-02:44, 2913 s, exit 0; the user was told it runs): AGREES. Frequencies within 0.002% (draws
    0.005%); masses within 1.6% but delta -3.7% (+-0.037, against +-0.17 in v2 with 8 x gamma 5.8 T away); draws
    delta -0.01, +2.8, -4.4%. Reference 1850 s on one CPU, against 838 s in v2: seven processes on six cores and
    probably another session's work at the same time. Output `work/dhva-fermi-surface/v3/explore/gen1.out`; v2's
    hashes in `hashes_v2.txt`.
  - [1]: delta's nearest harmonic is 8 x gamma, +120.8 T; 6 combinations within 0.1%, none within 15% in mass (the
    lightest 5.23). [2]: delta 7299.9 T, signal to noise 23 over 22-35 T, absent from 6-35 T and whole sweeps.
  - `release.sh --check`: scan 0 problems, canary, every .py parses, lint PASS.
  - BRIEFING point (02:05): test planted signals against harmonics and against mass-matching combinations before a
    generator run.
"""
marker = "\n## Version history"
i = t.index(marker)
t = t[:i].rstrip("\n") + "\n" + entry + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
