"""Append probe 4's result (the radius band for planet b) to logs/rv-planet-census.md State now and design.md."""
import datetime as dt

hm = dt.datetime.now(dt.timezone.utc).strftime("%H:%M")
p = "logs/rv-planet-census.md"
s = open(p, encoding="utf-8", newline="").read()
anchor = "\n\n## Current design (v1, 2026-11-10)\n"
assert s.count(anchor) == 1
entry = (
    "- **2026-11-10 %s**: radius-band probe for b (`work/rv-planet-census/v1/explore/probe_b4.py`, `.out`; analysis of\n"
    "  the shipped light curve and of synthetic ones, not the oracle or verifier). On the shipped light curve one fast\n"
    "  model gives: spline detrending then the fit 1.593 (-1.7%%), a quadratic baseline per transit in +-0.22 d windows\n"
    "  (a1's method) 1.730 (+6.8%%), +-0.30 d 1.700 (+4.9%%), a linear one 1.614 (-0.4%%). So the attempts' +6 to +9%% is the\n"
    "  quadratic-window method on this noise draw. On 200 synthetic light curves (b's true transit, white 680 ppm, red\n"
    "  90 ppm with 0.05 d, slow spots) every method is unbiased (mean -0.6 to +0.6%%) with sd 3.6 to 4.0%%, and 9 or 10 of\n"
    "  200 land outside 8%%: a correct analysis loses b's radius about 5%% of the time, and an uncorrected one (-13.3%%\n"
    "  expected) would pass now and then. The README's radius bullet rests on the reference's one fit and does not show\n"
    "  this scatter. Nothing changes during the full review. If it comes back, the fix goes through the data (less\n"
    "  photometric noise on the target, or a deeper transit for b, so a correct fit's scatter is about 2%%), with the\n"
    "  README showing the scatter, and harder evidence elsewhere, since every designed trap fell in pass@3.\n" % hm)
s = s.replace(anchor, "\n" + entry.rstrip("\n") + anchor)
open(p, "w", encoding="utf-8", newline="").write(s)

p = "work/rv-planet-census/v1/design.md"
s = open(p, encoding="utf-8", newline="").read()
s = s.rstrip("\n") + "\n" + (
    "\n## pass@3 of v1 and the radius band (2026-11-10 %s)\n\n"
    "pass@3 2 of 3 (job 20397, P3-DE0E-7F4D-56A1). Every designed trap fell in all three attempts; a1 failed only on b's\n"
    "radius (1.77, +9.3%%). Probe 4 (`explore/probe_b4.py`, `.out`): on 200 synthetic light curves with the generator's\n"
    "photometric noise, b's fitted radius has sd 3.6 to 4.0%% for every method (no bias), and about 5%% of correct fits\n"
    "land outside 8%%. On the shipped draw a quadratic baseline per +-0.22 d window gives +6.8%%, a linear one -0.4%%, the\n"
    "spline route -1.7%%. A v2, if one is needed: less photometric noise or a deeper transit for b, so that a correct fit's\n"
    "scatter is about 2%% and the uncorrected radius (-13.3%%) stays clearly outside; show that scatter in the README; and\n"
    "harder evidence, since the traps as built are routine for the target model.\n" % hm)
open(p, "w", encoding="utf-8", newline="").write(s)
print("logged at", hm)
