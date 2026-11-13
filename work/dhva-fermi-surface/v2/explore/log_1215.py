from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
entry = """- **2026-11-11 11:15-12:20**: v2 built in the active folder (design `work/dhva-fermi-surface/v2/design.md`). The
  electrons feel the flux density inside the sample, B = mu0 H + mu0 (1 - N) M, not the field column. The bar
  (0.250 x 0.200 x 1.600 mm, field along its length, now in NOTES.md) gives N = 0.0628 (Aharoni 1998) and
  K = 1.4721e-5 T per moment unit; the steady moment 1430 B - 0.10 B^3 puts B 1.9-2.2% above the field column, so every
  frequency read against the field column is 2.2-2.4% low (four times the band). alpha's amplitude 201 -> 900 makes
  the magnetic interaction a = K dm~/dB reach 0.209 at 0.35 K: against the field column the coldest 6-35 T spectrum
  has 14 peaks (combinations 2eps-alpha, 2eps+alpha, beta+alpha, ...), against B 8. Answers unchanged
  (`expected.json` byte-identical). Changes: `solution/solve.py` (step 0 converts the field axis; `--frame` for the
  routes), `tests/generate.py` (self-consistent B(H), STEADY, DRIFT, the routes, peak labels), NOTES.md (bar size,
  the moment as the sample's own after the empty-cell run, the field column as the magnet's field), instruction R5
  (F = hbar A / (2 pi e) with A the orbit's k-space area; `requirements.json` quote updated), `task.toml` and README
  tags (`magnetic-interaction`), README rewritten from the v2 checks.
  - Generator run 1 (11:20-11:42, 1318 s, exit 0): AGREES; frequencies within 0.009% (draws 0.024%), masses within
    1.7% but delta -6.6% (draws -8.3/-7.0/-2.3%, inside the 15% band); the reference against the field column and
    with the oscillatory magnetization only both DISAGREE (five of six orbits missed; the beta neck matched only by
    the beta belly's shifted entry). Output `work/dhva-fermi-surface/v2/explore/gen1.out`.
  - Generator run 2 (11:46-12:08, 1320 s, exit 0) after making the applied-field peak labels list both readings
    ("3 x alpha or gamma + alpha") and naming each route entry: data and `expected.json` sha256-identical to run 1,
    only `checks.txt` changed (reference 838 s). Output `gen2.out`, hashes `hashes_run1.txt`, `hashes_run2.txt`.
  - lint FAIL once on readme-claims ("worst" made "-2.3%" a measured claim in a block with no file path); reworded.
    Then `release.sh --check`: scan 0 problems, canary, every .py parses, lint PASS.
"""
marker = "\n## Version history"
assert t.count(marker) == 1
i = t.index(marker)
t = t[:i].rstrip("\n") + "\n" + entry + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
