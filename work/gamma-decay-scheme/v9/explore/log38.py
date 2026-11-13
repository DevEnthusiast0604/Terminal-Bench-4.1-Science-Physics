"""2026-11-11: v8's pass@3 (job 20645, 3 of 3) analysed and marked seen; the v9 decision. Adds only."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
HM = NOW[11:]


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    open(path, "w", encoding="utf-8", newline="").write(text)


def insert_at_section_end(text, header, entry):
    i = text.index(header)
    m = re.compile(r"^## ", re.M).search(text, i + len(header))
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


row = ("| 2026-11-11 00:00 | the same card, reviewed | Marked seen 00:09. Analysis under \"pass@3 analyses\" (v8): all "
       "three exact, the 511 keV line found by coincidences in each. v9 hardens the intensity of that line, not its "
       "noticing. | yes |\n")
analysis = """### v8 (T-1383 v8, job 20645, pass@3 ended 2026-11-11 00:00): 3 of 3 solved, TOO EASY

- Sol 6.1 (`gpt-6.1-sol`), rewards [1, 1, 1]. Agent times 9.7, 10.3 and 9.4 min (25, 24 and 27 steps); input tokens
  0.65, 0.75 and 0.88 M. Bundle in `work/gamma-decay-scheme/v8/pass3/` (untrusted extraction under `x/`, answers in
  `outputs/`, digests in `attempts/`, `summary.md`). The bundle's README carries P3-4C55-BFAB-2B18 with rewards
  [1, 1, 1]: not a qualifying result, not for DAS.
- All three: 16 of 16 levels, 31 of 31 transitions, half-life 4.379, 4.37 and 4.375 s, isomer 1963.1 keV with 169.0,
  168.0 and 169.0 ns. Worst intensity errors 12.9, 15.4 and 19.6 percent (1323.2, 992.7 and 1606.6 keV).
- The 511 keV line (I 4.41): +8.2, -1.9 and +6.3 percent. Against each attempt's median error on the other lines
  (-1.5, -2.1, -0.9) that is +9.7, +0.2 and +7.2: a2 isolated the line (coincidences); a1 and a3 kept part of the
  broad annihilation part (a3 took the production peak's area with no annihilation correction).
- How it was found: no attempt set 511 keV aside by energy this time (a1's room list for the gain had no 511; a2 took
  511 out of its gain anchors). The strong narrow peak entered the line list, and the coincidences of 941.3, 1092.0
  and 1738.9 keV placed it ("The network also supports a real transition at approximately 511 keV, overlapping
  annihilation radiation", a2; "it cannot simply be discarded as annihilation radiation", a3).
- Reading: the line's strength decides whether the model looks at the peak at all: I 0.853 -> 0 of 3 (v5), 4.41 ->
  3 of 3 (v8); with the proviso at 0.853 all three looked (v6) and measured it within 9 percent.
- v9 (harden, within the approved order: the same physics made to decide the grade): keep the line easy to notice
  (I about 3.0, still a third of the feeding of 2581.6 keV) and make its intensity depend on separating the line from
  the parent's own annihilation radiation: pair production of the parent's lines raised from 3.0e-4 to 6.0e-4 detected
  annihilation photons per parent decay. Then the whole peak, the peak less the background run's annihilation, and a
  parent-time-profile share all read about 40 to 50 percent high; the two shapes or the coincidences give the line.
  `tests/checks.txt` will record those readings (new lines in `write_checks`).
"""
state = ("- **%s**: v8's pass@3 3 of 3 (job 20645, 00:00; card seen 00:09). Building v9: the 511 keV line at I about "
         "3.0 (TARGET: M's beta feeding 10.85, its branch to H 21; H's beta feeding 3.65) and the parent's pair-production "
         "annihilation doubled (6.0e-4 per decay), so the line's intensity needs the two shapes or coincidences; new data "
         "from the generator after telling the user.\n") % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

point = ("- (%s) The 511 keV line's strength switches whether Sol 6.1 looks at the annihilation peak at all: I 0.853 gave "
         "0 of 3 (the peak set aside by energy), 4.41 gave 3 of 3 (found by coincidences). Harden through what the "
         "attempts then do with the peak, its intensity, rather than through whether they notice it.\n") % HM
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)

event = ("- **%s**: v8 pass@3 3/3 (job 20645): all exact; the 511 keV line found by coincidences. v9: line at I about "
         "3.0 and pair-production annihilation doubled, so its intensity needs the shapes or coincidences.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done", NOW)
