"""2026-11-10: v5's pass@3 (job 19705, 0 of 3) reviewed; the v6 decision. Adds only."""
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


row = ("| 2026-11-10 07:59 | the same card, reviewed | Marked seen 08:08. Analysis under \"pass@3 analyses\" (v5): all "
       "three missed the 511.00 keV line, set aside by energy as a room line; fair, so v6 eases the noticing step with "
       "one instruction sentence. | yes |\n")
analysis = """### v5 (T-1383 v5, job 19705, pass@3 ended 2026-11-10 07:59): 0 of 3 solved, TOO HARD

- Sol 6.1 (`gpt-6.1-sol`), rewards [0, 0, 0]. Agent times 13.7, 15.8 and 15.9 min (32, 23 and 21 steps); input tokens
  1.16, 0.73 and 0.58 M. Bundle in `work/gamma-decay-scheme/v5/pass3/` (`pass3.zip`, untrusted extraction under `x/`,
  answers in `outputs/`, digests in `attempts/`, `summary.md` from `tools/scheme_report.py`).
- Each attempt passed 4 of 7 tests (members, half-life, levels, isomer) and failed `test_transitions_placed`,
  `test_transition_energies` and `test_relative_intensities`. Levels 16 of 16 in all three; parent half-life 4.372,
  4.368 and 4.369 s; isomer 1963.1 keV with 158.3, 165.7 and 170.1 ns.
- a2 and a3: 30 of 31 transitions, missing only 3092.6 -> 2581.6 keV (511.00 keV, I 0.853); every other intensity
  within 11.2 and 13.7 percent. a1: 29 of 31, also missing 941.3 keV, which it read as the single-escape peak of
  1452.3 keV (1452.3 - 941.3 = 511.0: the triangle 3092.6 -> 2581.6 -> 1640.3 against 3092.6 -> 1640.3), and 1489.6
  keV at 4.41 for 3.26.
- Cause: all three put 511 keV in a list of room lines from general knowledge (a1 `bgE=[...,510.999,...]`, a2
  `bge=[...,511.,...]`, a3 `bglines=[...,511,...]`) and removed it before any analysis. a3's own coincidence table
  showed 511.0 keV in the gates of 1322.47 keV (232 counts) and 1738.9 keV (120), and a gated peak at 511.097 keV
  with sigma 0.64 keV; it did not follow them up.
- Fairness: instruction.md and NOTES.md say nothing of 511 keV or annihilation; the line is above the floor (0.853
  against 0.5); the data show it (narrow part 11967 +- 482 counts, parent share 0.98, gates of 941.3, 1092.0 and
  1738.9 keV); the reference reads 0.80. Only one pair of levels is 511 keV apart. No unstated requirement and no
  unfair check: the attempts failed at the stated difficulty.
- The bundle's README carries P3-3C8F-10C6-C3A0 with rewards [0, 0, 0]: not a qualifying result, not for DAS.
- v6 (the platform: "make the task somewhat easier"): one instruction sentence, "A transition can share its peak with
  radiation of another origin, whatever the peak's energy." It removes the shortcut (setting a peak aside by its
  energy) and names no peak. Still to decide: which of the six level differences on peaks of another origin hold a
  transition (511.0 keV only; 403.4, 1120.4, 2263.2, 300.1 and 1507.2 keV do not), and the 511 keV line's intensity.
  By the generator's constants about 9000 of the broad part's counts come from pair production of the parent's own
  lines (N_PARENT 3.0e7 times 3.0e-4), with the parent's time profile, and the room's share is about 3500 (0.8 per s
  over 4320 s): taking off only the room's share leaves about 1.75 times the line, outside 25 percent. The two
  shapes (sigma 1.50 against 0.67 keV) or coincidence intensities give it. Requirement R13 binds the sentence to the
  three transition tests; the README follows. Data, expected.json, checks.txt, generate.py and solve.py unchanged,
  so no generator run.
"""
pitfall = ("- (%s) A `cd` into `work/<slug>/v<N>/pass3/x/` in a Bash call persists, because the folder is inside the "
           "working directories: the next commands then run inside the untrusted tree. List and read it with paths "
           "from the folder root instead (happened at 08:03 on 11-10; nothing ran there, the next call went back).\n") % NOW
state = ("- **%s**: v5's pass@3: 0 of 3 (job 19705, 07:59; card seen 08:08). All three set the 511 keV peak aside "
         "by energy and missed the 511.00 keV line; a2 and a3 had everything else right. Fair, so v6 eases the "
         "noticing step: one instruction sentence (no peak named), R13, README. Next: `release.sh` v6.\n") % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
s = insert_at_section_end(s, "## Pitfalls", pitfall)
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

point = ("- (%s) v5 pass@3 (job 19705): 0 of 3. All three dropped 511 keV by energy as a room line before any analysis; "
         "a2 and a3 were otherwise exact. Judged fair (nothing unstated; the data show the line). v6 adds one sentence to "
         "the instruction, \"A transition can share its peak with radiation of another origin, whatever the peak's "
         "energy.\", bound as R13; the intensity (the broad part is mostly the parent's own pair production) and the "
         "five decoy differences still decide. Data and answers unchanged.\n") % HM
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)

event = ("- **%s**: v5 pass@3 0/3 (job 19705): the 511.00 keV line missed by all three (511 set aside as a room line). "
         "v6 = v5 plus one instruction sentence (a transition can share its peak with radiation of another origin, "
         "whatever the peak's energy), R13 and README; no new data.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done", NOW)
