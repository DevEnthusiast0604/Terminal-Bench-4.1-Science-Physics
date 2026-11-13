"""2026-11-11: v9's pass@3 (job 21129, 1 of 3 solved: QUALIFIED) analysed and marked seen; full review as v10. Adds only."""
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


def insert_at_slug_end(text, slug, entry):
    i = text.index("| Slug | `%s` |" % slug)
    m = re.compile(r"^# ", re.M).search(text, i)
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


row = ("| 2026-11-11 06:26 | the same card, reviewed | Marked seen 06:36. P3 ID P3-4DCE-3D5C-5E63 given to the user for "
       "DAS 4011092 (the user submits on DAS). The v10 zip (`gate/task/21495.zip`) is byte-identical to the v9 delivery "
       "(sha256 b81f8481…809a). pass@3 bundle `gate/full/21129.zip`: README rewards [0, 1, 0], task digest f9413828…b47a. "
       "Analysis under \"pass@3 analyses\" (v9). Poller restarted for the full review. | yes |\n")
analysis = """### v9 (T-1383 v9, job 21129, pass@3 ended 2026-11-11 06:26): 1 of 3 solved, QUALIFIED

- Sol 6.1 (`gpt-6.1-sol`), rewards [0, 1, 0]; P3 ID **P3-4DCE-3D5C-5E63** (bundle README and the card agree). Agent times
  12.9, 15.7 and 17.4 min (33, 27 and 39 steps); input tokens 1.26, 0.99 and 1.52 M. Bundle in
  `work/gamma-decay-scheme/v9/pass3/` (untrusted extraction under `x/`, answers in `outputs/`, digests in `attempts/`,
  `summary.md`).
- a1 (0): 16 of 16 levels, 30 of 31 transitions: the 511.00 keV line (I 2.99) not placed. It used 510.999 keV as a room
  line for its gain, listed the 510.99 keV peak among the parent-profile peaks at I 4.006 (whole peak), and finally
  excluded it with the room lines. Worst intensity error otherwise 21.7 percent (708.0 keV, inside the band).
- a2 (1): exact. The 511 keV peak decomposed into the line and broad annihilation radiation (narrow part about 41,000
  counts): -6.0 percent. Worst intensity error 10.8 percent (1323.2 keV).
- a3 (0): the 511 keV line found and separated the same way (narrow part about 44,000 counts): +0.4 percent. It failed
  the isomer: it put the isomer at 1925.0 keV and, explicitly rejecting "a hidden low-energy ground-state step" for the
  sub-threshold 38.1 keV transition, built three extra levels 38.1 keV low (2594.9, 2823.3, 3054.5 keV) for 669.9,
  898.3, 231.2 and 459.6 keV: 18 levels where 16 do, 708.0 keV left out, 231.2 and 459.6 keV split between two
  placements (intensities -44 and -63 percent). That placement contradicts the prompt partners of 231.2 and 459.6 keV
  (2018.7, 1219.8; 1143.4, 992.7) and the instruction's fewest-levels rule: a reasoning slip, not a task defect.
- Reading: at I 2.99 among doubled pair-production annihilation, the attempts that noticed the line also separated its
  shape (a2, a3); the shape trap did not catch them, the noticing trap caught a1. The isomer trap, passed by every v8
  attempt, caught a3. Both failures are fair: the evidence is in the shipped files (README bullets "The annihilation
  peak holds a line" and "One level has no visible exit").
- The full review started as v10 (06:26) on the same files.
"""
state = ("- **%s**: v9 QUALIFIED: pass@3 1 of 3 (job 21129, 06:26; card seen 06:36). P3 ID **P3-4DCE-3D5C-5E63**, given "
         "to the user, who submits on DAS 4011092 (never by this session). The full review runs as v10 (byte-identical to "
         "the v9 zip), queued 06:26. Don't upload while it runs.\n") % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

event = ("- **%s**: v9 pass@3 1/3 (job 21129): QUALIFIED, P3 ID P3-4DCE-3D5C-5E63 (to the user for DAS 4011092). a1 left "
         "the 511.00 keV line out (set aside with the room lines); a3 rejected the sub-threshold 38.1 keV step (isomer at "
         "1925.0, three extra levels); a2 exact. Full review as v10 (= v9's files) from 06:26.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", insert_at_slug_end(s, "gamma-decay-scheme", event))

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v10 = v9's files "
         "(`gamma-decay-scheme-20261111.zip`, digest `f9413828…b47a`) | IN REVIEW: v9 pass@3 1 of 3, QUALIFIED, P3 ID "
         "P3-4DCE-3D5C-5E63 (given to the user for DAS 4011092); full review queued as v10 06:26 | %s | Wait for the "
         "full review (poller); no upload meanwhile; the user submits on DAS | [log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))

point = ("- (%s) gamma-decay-scheme v9 qualified at 1 of 3 with two different traps: one attempt set the 511 keV line "
         "aside with the room lines (I 2.99), one rejected the sub-threshold isomer step. The attempts that noticed the "
         "511 keV line all separated it from the broad annihilation radiation, so its shape trap adds little on its own; "
         "the noticing and the isomer traps carry the difficulty.\n") % HM
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)
print("done", NOW)
