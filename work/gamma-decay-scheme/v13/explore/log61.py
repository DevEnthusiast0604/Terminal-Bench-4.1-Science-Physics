"""2026-11-12: v12's pass@8 card (7 of 8 on Astra 6, TOO EASY, 21:09) reviewed and marked seen; the analysis. Adds only."""
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


row = ("| 2026-11-12 21:09 | the same card, reviewed | Marked seen about 21:28 (`mark-seen` printed NOT CONFIRMED on the "
       "slow page; `updates` then listed it as seen). No reviewer note beyond the card. pass@8 bundle "
       "`gate/passk/22785.zip` in `work/gamma-decay-scheme/v12/pass8/` (x/ untrusted; outputs/a1-a8.json, summary.md, "
       "intensity_errors.txt, attempts/). Astra 6 found the hidden 1081.40 keV line in 7 of 8; see pass@3 analyses (v12 "
       "pass@8). Next: v13, harder for Astra 6 while Sol 6.1 keeps 1-2 of 3. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)

analysis = """### v12 pass@8 (T-1383 v12 = v11's files, job 22785, pass@8 on Astra 6 ended 2026-11-12 21:09): 7 of 8 solved, TOO EASY

- The card: "This version added the weak 1081.4 keV transition hidden under the stronger 1082.3 keV line, which only
  gated spectra reveal; most attempts still found it, so that one transition does not make the task hard enough on its
  own." pass@8 must land at 1-6 of 8.
- Attempts 20:17-21:00, 15-21 min each. a4 failed, on that line alone: it kept the whole 1082 keV peak as E->B (+7.8%)
  and its weak-peak search "found no overlooked transition". Everything else in a4 was exact.
- The other seven listed 1081.40 keV (errors -13.7% to +6.0%); worst intensity error per attempt 9.2-13.7% (limit
  25%). All 8: 17 levels, the isomer at 1963.1 keV, the parent half-life within 0.2%.
- Two routes found it, either one enough:
  - The level difference. Once 1879.0 keV places 2721.7 keV, 2721.7 - 1640.3 falls on the 1082 keV peak (a2: "The
    existing 2721.7-keV level would also produce a 1081.4-keV transition to 1640.3 keV, unresolved beneath the
    stronger 1082.3-keV line. This must be tested before writing the output."; a3 planned to "test for an additional
    1081.4/1082.3 keV doublet"; a5 and a7 the same).
  - The gate on 1321.9 keV, a member of the 1322 keV doublet that every attempt gates on anyway (a6: "The 1322-gated
    spectrum reveals a second 1082-region transition at about 1081.5 keV"; a8: "A previously hidden approximately
    1081.4 keV branch appears in the 1321.9 keV gate"; a1 used it to rule out the low-energy tail).
  A fit of the 1082 keV peak with two members at fixed energies (several with a low-energy tail in the line shape) or
  the gate's own area then gave the intensity.
- Sol 6.1 found the line in 1 of 3 (v11), by the level difference only. Astra 6 found it in 7 of 8, by either route.
"""
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
state = ("- **%s**: v12 SENT BACK: pass@8 on Astra 6 solved 7 of 8 (21:09, TOO EASY; card seen). a4 alone missed the "
         "1081.40 keV line; the other seven found it by the level difference 2721.7 - 1640.3 or in the 1321.9 keV gate. "
         "Next: v13 (draft in `work/gamma-decay-scheme/v13/`), harder for Astra 6 without changing what the instruction "
         "asks, while Sol 6.1 keeps at least 1 of 3. P3-8546-0E6F-2BCD is spent; a qualifying v13 pass@3 gives a new P3 ID "
         "for DAS 4011092.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

event = ("- **%s**: v12 pass@8 on Astra 6: 7/8 (job 22785, 21:09), TOO EASY, sent back. Only a4 missed the hidden "
         "1081.40 keV line; the rest found it by the level difference 2721.7 - 1640.3 or in the 1321.9 keV gate. v13: "
         "harden for Astra 6, keep Sol 6.1 at 1-2 of 3.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", insert_at_slug_end(s, "gamma-decay-scheme", event))

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v12 = v11's files "
         "(`gamma-decay-scheme-20261111.zip`, digest `ebda2428…eaea`) | SENT BACK: pass@8 on Astra 6 7 of 8 (job 22785, "
         "21:09), TOO EASY | %s | Harden as v13 (draft in `work/gamma-decay-scheme/v13/`), upload with release.sh, "
         "watch quick check, pass@3, full review, pass@8 | [log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))

point = ("- (%s) gamma-decay-scheme v11/v12: one weak line hidden under a strong one gave Sol 6.1 1 of 3 but Astra 6 7 of "
         "8. Astra 6 found it two ways: by checking every difference of two placed levels against the peaks (the line's "
         "upper level was placed by a clean line) and in the gate on a doublet member that it examines anyway. Sol 6.1 "
         "used only the first. A hidden line holds Astra 6 only if no cheap check points straight at it.\n" % NOW[11:])
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)
print("done", NOW)
