"""2026-11-12: v11 pass@3 (job 22164) reviewed: 1 of 3, QUALIFIED, P3 ID P3-8546-0E6F-2BCD; analysis; card seen.
Adds only."""
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


row = ("| 2026-11-12 05:53 | the same card, reviewed | Marked seen 06:02 (`mark-seen` printed NOT CONFIRMED on the slow "
       "page; `updates` then listed it as seen). pass@3 bundle `gate/full/22164.zip` in "
       "`work/gamma-decay-scheme/v11/pass3/` (x/ untrusted; outputs/a1-a3.json, summary.md, intensity_errors.txt, "
       "attempts/). Rewards [0, 1, 0]; see pass@3 analyses (v11). P3 ID P3-8546-0E6F-2BCD given to the user for DAS "
       "4011092. Nothing uploaded; poller restarted for the full review. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)

analysis = """### v11 (T-1383 v11, job 22164, pass@3 on Sol 6.1 ended 2026-11-12 05:53): 1 of 3 solved, QUALIFIED

- P3 ID **P3-8546-0E6F-2BCD** (this revision only), given to the user for DAS 4011092. The full review runs as v12
  (= v11's files, `gate/task/22785.zip`), queued 05:53.
- Rewards [0, 1, 0]. a1 and a3 are exact apart from one thing: both leave out the 1081.40 keV transition from
  2721.70 to 1640.30 keV (I 1.22) and keep the whole 1082 keV peak as E->B (+9.0% and +8.2%). Both found the level at
  2721.70 keV through the 1879.0 keV line. a2 is exact: its weak-peak search flagged "an unresolved component near
  1081.4 keV" next to the 1879.0 keV level, and it took the weak line's intensity from "its exclusive 1322-keV
  coincidence" (-5.5%), E->B -2.7%.
- Every other part held in all three: 17 levels, the 511 keV line (-17.6%, -5.2%, -2.3%), the isomer at 1963.1 keV
  (168.5-172.0 ns), the parent at 4.3625-4.3734 s. Worst intensity errors 18.1%, 14.4%, 11.5% against 25% (a1:
  1092.0 keV -18.1%, 511.0 keV -17.6%).
- The trap works as designed on Sol 6.1, and it is the only one that caught an attempt. Whether Astra 6 misses it
  (pass@8 needs 1-6 of 8) is the open question.
"""
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
state = ("- **%s**: v11 QUALIFIED: pass@3 1 of 3 on Sol 6.1 (job 22164, 05:53; card seen 06:02). P3 ID "
         "**P3-8546-0E6F-2BCD**, given to the user, who submits on DAS 4011092 (never by this session). a1 and a3 missed "
         "only the 1081.40 keV transition under E->B; a2 exact. The full review runs as v12 (= v11's files), queued "
         "05:53. Don't upload while it runs; then pass@8 on Astra 6.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

event = ("- **%s**: v11 pass@3 1/3 (job 22164, 05:53): QUALIFIED, P3 ID P3-8546-0E6F-2BCD (to the user for DAS "
         "4011092). a1 and a3 missed only the weak 1081.40 keV line under E->B; a2 exact. Full review as v12 from 05:53.\n"
         % NOW)
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", insert_at_slug_end(s, "gamma-decay-scheme", event))

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v12 = v11's files "
         "(`gamma-decay-scheme-20261111.zip`, digest `ebda2428…eaea`) | IN REVIEW: v11 pass@3 1 of 3, QUALIFIED, P3 ID "
         "P3-8546-0E6F-2BCD (given to the user for DAS 4011092); full review queued as v12 05:53 | %s | Wait for the "
         "full review and pass@8 (poller); no upload meanwhile; the user submits on DAS | [log](gamma-decay-scheme.md) |"
         % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))

point = ("- (%s) gamma-decay-scheme v11 qualified at 1 of 3 on Sol 6.1 through one trap only: a weak transition (I 1.22) "
         "0.9 keV under a strong placed line (I 13.0), whose only clean gate is a doublet. The two failed attempts were "
         "otherwise exact; the one that passed found it with a weak-peak search and took its intensity from the clean "
         "gate. A single trap aimed at a specific blind spot gave a cleaner result than stacking noticing traps.\n"
         % NOW[11:])
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)
print("done", NOW)
