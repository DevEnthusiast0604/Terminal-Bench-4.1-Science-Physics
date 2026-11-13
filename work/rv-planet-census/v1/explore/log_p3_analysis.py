"""Append the pass@3 analysis of T-1519 v1 (job 20397) to logs/rv-planet-census.md and a BRIEFING point.

Adds only: the reviewed row under "Platform updates", a "### v1" block under "## pass@3 analyses", a State now line,
and a BRIEFING point. Times come from the clock (UTC)."""
import datetime as dt

hm = dt.datetime.now(dt.timezone.utc).strftime("%H:%M")
day = "2026-11-10"


def rd(p):
    return open(p, encoding="utf-8", newline="").read()


def wr(p, s):
    assert "\r" not in s
    open(p, "w", encoding="utf-8", newline="").write(s)


p = "logs/rv-planet-census.md"
s = rd(p)

# 1. the reviewed row, right after the 20:55 card's row
card = "Poller exit 0 at 20:55. | no |\n"
assert s.count(card) == 1
row = ("| 2026-11-10 20:55 | the same card, reviewed | Marked seen 21:01. pass@3 of v1 (job 20397): **2 of 3** solved, "
       "rewards [0, 1, 1]; a1 failed only `test_radii` (planet b 1.77 R_earth, +9.3% against the 8% band). The bundle's "
       "provenance digest is v1's (`sha256:527d1959…33c7`); the platform's v2 zip (`gate/task/20848.zip`) is "
       "byte-identical to `deliveries/rv-planet-census-20261110.zip` (sha256 `264e4446…400c`). Analysis under "
       "\"pass@3 analyses\" (v1). The user submits on DAS, so the P3 ID goes to the user, not to DAS. The full review "
       "runs as the platform's v2 (job 20848). Poller restarted for the review's decision. | yes |\n")
s = s.replace(card, card + row)

# 2. the analysis block
head = "## pass@3 analyses\n"
assert s.count(head) == 1
block = """
### v1 (T-1519 v1, job 20397, pass@3 ended 2026-11-10 20:46): 2 of 3 solved, QUALIFIES

- Sol 6.1 (`gpt-6.1-sol`), rewards [0, 1, 1]. Agent times 11, 8 and 11 min (35, 24 and 25 episodes), cost $0.46,
  $0.41 and $0.44. Bundle in `work/rv-planet-census/v1/pass3/` (`pass3.zip`, untrusted extraction under `x/`,
  `summary.md` from `tools/pass3_report.py`, which now skips the per-case table for a data task); answers copied to
  `work/rv-planet-census/v1/attempts/programs/aK/planets.json`, digests in `attempts/`, the comparison in
  `pass3/census.md` from the new `tools/census_report.py`.
- P3 ID **P3-DE0E-7F4D-56A1** ("this revision only"), task digest `sha256:527d1959…33c7`, the v1 files. Given to the
  user for DAS 4040198.
- Every attempt got every trap right: rotation 34.18, 33.5 and 33.67 d (within 2.3%); four planets and nothing
  else; d at 1.2195 d (the 5.48 d alias rejected by its phase disagreeing between the spectrographs); c at 17.67 d
  (kept: same amplitude and phase in both instruments and seasons); e at 113.6-113.9 d (-1.2 to -1.5%); the 6.047 d
  binary rejected by its secondary eclipse; the single dip assigned to e through the eccentric orbit's conjunction;
  the second star's light corrected. K within 12%, minimum masses within 11.7%, e's radius +0.7 to +3.4%.
- a1's only miss: b's radius 1.77 (+9.3%); a2 1.73 (+6.8%) and a3 1.72 (+6.2%) passed. All three fitted b's
  transits with local per-transit baselines, limb darkening from NOTES.md, a/R* from the stellar density (11.19, the
  true value) and the dilution applied correctly; impact parameters 0.44 (true 0.35), mid-times about 2.7 min late at
  their epoch. The reference (spline detrending, then the fit) has 1.606 (-0.9%). So the one failure is a precision
  edge of the radius of b, not one of the designed traps; the photometry has red noise (AR(1), 90 ppm, 0.05 d) on the
  transit's time scale. Fairness probe of the 8% band: see the State now entry after this one.
- Difficulty, honestly: the traps all fell in 8 to 11 minutes. Cross-instrument phase coherence, secondary-eclipse
  vetting, a single transit tied to an eccentric RV orbit and a stated dilution are standard moves for this model.
"""
s = s.replace(head, head + block)

# 3. a State now line
anchor = "\n\n## Current design (v1, 2026-11-10)\n"
assert s.count(anchor) == 1
entry = ("- **%s %s**: v1 QUALIFIED: pass@3 2 of 3 (job 20397, 20:46), P3 ID **P3-DE0E-7F4D-56A1**, given to the user\n"
         "  for DAS 4040198 (the user submits on DAS). The full review runs as the platform's v2 (job 20848, queued 20:55;\n"
         "  same zip). No upload while it runs. a1 failed only on b's radius (+9.3%% against 8%%); every designed trap fell in\n"
         "  all three attempts (see pass@3 analyses, v1). Next: probe whether the 8%% radius band is fair for b under the\n"
         "  light curve's red noise, and prepare for the review's likely points (b's radius band, the K/mass relation)."
         % (day, hm))
s = s.replace(anchor, "\n" + entry + anchor)
wr(p, s)

p = "logs/BRIEFING.md"
s = rd(p)
s = s.rstrip("\n") + "\n" + (
    "- (%s) rv-planet-census QUALIFIED: v1's pass@3 2 of 3 (job 20397), P3 ID P3-DE0E-7F4D-56A1, passed to the user for\n"
    "  DAS 4040198; the full review runs as the platform's v2 (job 20848). Every designed trap fell in all three\n"
    "  attempts (8 to 11 min): phase coherence between two spectrographs, secondary-eclipse vetting, one transit tied to\n"
    "  an eccentric orbit, a stated dilution. The one failure was a precision edge (b's radius +9.3%% against 8%%). For\n"
    "  Sol 6.1 these exoplanet moves are routine: a harder census needs evidence that standard steps get wrong.\n" % hm)
wr(p, s)
print("logged at", hm)
