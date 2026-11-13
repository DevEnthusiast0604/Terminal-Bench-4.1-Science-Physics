"""2026-11-13: v14 pass@3 analysis (job 24365, 1 of 3 solved) and the card marked seen. Adds only. Run from the folder
root."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    assert "\r" not in text
    open(path, "w", encoding="utf-8", newline="").write(text)


def insert_at_section_end(text, header, entry):
    i = text.index(header)
    m = re.compile(r"^## ", re.M).search(text, i + len(header))
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


analysis = """### v14 (T-1383 v14, job 24365, pass@3 on Sol 6.1 ended 2026-11-13 19:16): 1 of 3 solved, QUALIFIED

- P3 ID **P3-B911-F9F1-EDFA** (this revision only), given to the user for DAS 4011092. The full review runs as v15
  (= v14's files), queued 19:16. The run started 13:39 had a fault on the platform's side and was restarted at 18:44;
  the attempts' agents started 18:49 and took 15 to 18 min, the verifier 4.5 to 10.6 min.
- Rewards [1, 0, 0] (`work/gamma-decay-scheme/v14/pass3/summary.md`; outputs in `pass3/outputs/`, compared with
  `work/gamma-decay-scheme/v13/explore/compare13.py`). All three found 17 levels, the 1399.8 keV level and its
  557.1 keV line (I 2.90 to 3.00 for 2.98): the stronger feeding of v14 made that level easy to place.
- a1 is exact: 33 of 33 transitions; the hidden 1081.41 keV line at I 2.10 (-13.8%); worst other errors 647.8 keV
  +13.1%, 646.9 keV -7.4%; parent 4.380 s, isomer 1963.1 keV 170.5 ns.
- a2 leaves out the hidden 1081.40 keV line (the v13 failure) and keeps the whole 1082 keV peak as 1925.0 -> 842.7
  (+16.1%); 708.0 keV at -24.9% sits at the band's edge.
- a3 finds the hidden line (1081.38 keV, I 2.96, +21.6%) but never detects the weak 1092.00 keV line (2581.6 ->
  1489.6 keV, I 1.25; the reference measures 1.20 in `tests/checks.txt`): its trajectory digest
  (`attempts/attempt-3.txt`) never mentions 1092 keV. 511.0 keV at -23.4% is near the edge too.
- So two independent ways to fail: the hidden line (found by 2 of 3; their intensities 2.10 and 2.96 for 2.44, both
  inside 25%) and a missed weak line. The v12 pass@8 on Astra 6 solved 7 of 8 with a weaker hidden line (I 1.22); if
  this pass@8 comes back TOO EASY, the next hardening has to hide something Astra 6's level-difference check does not
  reach (BRIEFING 2026-11-12 21:45).
"""
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
s = insert_at_section_end(s, "## Platform updates",
                          "| 2026-11-13 19:16 | the same card, reviewed | Marked seen %s (`mark-seen` printed NOT CONFIRMED "
                          "on the slow page; `updates` then listed the card as seen). pass@3 bundle `gate/full/24365.zip` in "
                          "`work/gamma-decay-scheme/v14/pass3/` (x/ untrusted); analysis under pass@3 analyses. | yes |\n"
                          % NOW[11:])
s = insert_at_section_end(s, "## State now",
                          "- **%s**: the v14 pass@3 card is reviewed and marked seen; analysis under pass@3 analyses "
                          "(a1 exact; a2 missed the hidden 1081.40 keV line; a3 missed the weak 1092.00 keV line). The "
                          "full review (v15) is queued; poller at 600 s.\n" % NOW)
write("logs/gamma-decay-scheme.md", s)
print("logged at", NOW)
