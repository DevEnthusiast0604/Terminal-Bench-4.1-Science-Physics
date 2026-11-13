"""2026-11-11: v10's pass@8 card (8 of 8 on Astra 6, TOO EASY, 18:12) reviewed and marked seen; the analysis. Adds only."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


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


def insert_at_slug_end(text, slug, entry):
    i = text.index("| Slug | `%s` |" % slug)
    m = re.compile(r"^# ", re.M).search(text, i)
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


row = ("| 2026-11-11 18:12 | the same card, reviewed | Marked seen 18:33. No reviewer note beyond the card. pass@8 bundle "
       "`gate/passk/21495.zip` in `work/gamma-decay-scheme/v10/pass8/` (x/ untrusted; outputs/a1-a8.json, summary.md, "
       "intensity_errors.txt, attempts/). Astra 6 got the whole scheme in all 8 attempts; see pass@3 analyses (v10 pass@8). "
       "Next: v11, harder for Astra 6 while Sol 6.1 keeps 1-2 of 3. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)

analysis = """### v10 pass@8 (T-1383 v10 = v9's files, job 21495, pass@8 on Astra 6 ended 2026-11-11 18:12): 8 of 8 solved, TOO EASY

- The card: "The target model solved all 8 of its attempts, so the task is too easy and comes back to you. ... Make the
  task harder there, without changing what the instruction asks for". pass@8 runs on Astra 6 and must land at 1-6 of 8;
  pass@3 runs on Sol 6.1 and must land at 1-2 of 3. v8 gave Sol 3/3, v9 1/3; v10 (same files as v9) gave Astra 8/8.
- Attempts 17:50-18:12, 11-19 min and 15-26 steps each. All 8 exact on structure: 16/16 levels, 31/31 transitions,
  isomer at 1963.1 with 164.3-168.0 ns (168.0), parent 4.361-4.370 s (4.37), every energy within 0.1 keV.
- Intensities (grader: 25%): worst error per attempt 7.2-10.0%. 992.7 keV is -7.2 to -10.0% in all 8 (the reference
  itself -8.3%); 511.0 keV -1.3 to -6.0%; the 647 keV doublet members within 6%. Nothing came near the limit.
- What Astra 6 did, in every attempt: gain recalibration on the room lines; time-profile fits of every peak; doublets
  from width, self-coincidence and gated centroids; quantitative sum (coincidences over 7) and escape checks; the 708
  keV mixed peak by its timing; the 511 keV line by coincidences with H's three other exits plus a narrow/broad shape
  fit; the isomer by signed delayed coincidences; an audit of weak peaks; coincidence checks of second placements
  (459.6 = N-J considered and rejected). The two traps that caught Sol 6.1 in v9 (the 511 keV line set aside, the
  sub-threshold isomer step) are routine for Astra 6.
- Design notes so far (`work/gamma-decay-scheme/v11/explore/`): `candidates.py` finds no existing level pair 0.5-1.3
  keV from a line except pairs through the Da/Db doublet, whose gates can't be told apart; `summing_out.py` shows the
  generator's summing-out costs at most -5.2% uncorrected and would need an unrealistic array to matter.
"""
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
state = ("- **%s**: v10 SENT BACK: pass@8 on Astra 6 solved 8 of 8 (18:12, TOO EASY; card seen 18:33). Every attempt "
         "exact (16 levels, 31 transitions, isomer), worst intensity error 7-10%% against 25%%. Next: v11, harder for Astra 6 "
         "without changing what the instruction asks, while Sol 6.1 keeps at least 1 of 3. The P3 ID P3-4DCE-3D5C-5E63 "
         "stays spent; a qualifying v11 pass@3 gives a new one.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

event = ("- **%s**: v10 pass@8 on Astra 6: 8/8 (job 21495, 18:12), TOO EASY, sent back. All 8 exact; worst intensity "
         "error 7-10%% (limit 25%%). Astra 6 handles both v9 traps (511 keV line, sub-threshold isomer step) routinely. "
         "v11: harden for Astra 6, keep Sol 6.1 at 1-2 of 3.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", insert_at_slug_end(s, "gamma-decay-scheme", event))

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v10 = v9's files "
         "(`gamma-decay-scheme-20261111.zip`, digest `f9413828…b47a`) | SENT BACK: pass@8 on Astra 6 8 of 8 (job 21495, "
         "18:12), TOO EASY | %s | Harden as v11 (draft in `work/gamma-decay-scheme/v11/`), upload with release.sh, "
         "watch quick check, pass@3, full review, pass@8 | [log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))

point = ("- (%s) pass@8 runs on Astra 6 and is far stronger than Sol 6.1 on pass@3: gamma-decay-scheme v10 (Sol 1 of 3) "
         "went 8 of 8 there, every attempt exact. Astra 6 runs a full spectroscopy playbook unprompted (gain "
         "recalibration, time profiles of every peak, gated centroids for doublets, quantitative sum and escape checks, "
         "signed delayed coincidences, an audit of weak peaks). A trap that only decides whether a peak gets noticed won't "
         "hold it; the task needs a step where careful, standard analysis still has to make a judgement the data settle.\n"
         % NOW[11:])
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)
print("done", NOW)
