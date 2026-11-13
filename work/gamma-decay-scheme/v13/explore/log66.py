"""2026-11-13: v13's pass@3 card (0 of 3) reviewed and marked seen; the analysis. Adds only."""
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


def insert_at_slug_end(text, slug, entry):
    i = text.index("| Slug | `%s` |" % slug)
    m = re.compile(r"^# ", re.M).search(text, i)
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


row = ("| 2026-11-13 07:23 | the same card, reviewed | Marked seen about 07:31 (`mark-seen` printed NOT CONFIRMED on the "
       "slow page; `updates` then listed it as seen). pass@3 bundle `gate/full/23827.zip` in "
       "`work/gamma-decay-scheme/v13/pass3/` (x/ untrusted; outputs/a1-a3.json pulled with "
       "`v10/explore/pull_outputs8.py`, compared by `v13/explore/compare13.py`; digests in `v13/attempts/`). All three "
       "missed the hidden 1081.40 keV line and nothing else; see pass@3 analyses (v13). Next: v14, somewhat easier at that "
       "trap. | yes |\n")
analysis = """### v13 (T-1383 v13, job 23827, pass@3 on Sol 6.1 ended 2026-11-13 07:23): 0 of 3 solved, TOO HARD

- Rewards [0, 0, 0], each failing test_transitions_placed, test_transition_energies and test_relative_intensities on
  one thing: the missing 1081.40 keV transition from 1399.8 to 318.4 keV (I 1.61). All three have the 17 levels
  exact, the 1399.8 keV level among them, the other 32 transitions within the bands (worst 1606.6 keV +20.1%, +20.3%,
  and 1082.3 keV read whole +10.5% to +12.3%), the parent at 4.368-4.372 s and the isomer at 1963.1 keV (165-167 ns).
  Agent time 15, 21 (29 with the verifier) and 15 min.
- All three found the level at 1399.8 keV through 557.1 keV (I 1.32, 5.3 keV above 551.8 keV at I 7.7), and late: a1
  about two thirds through ("The 557.1 keV peak is a genuine weak candidate with strong 318/524 coincidences and may
  require an additional level near 1399.8 keV"), a2 about two thirds through, a3 near its end ("one previously missed
  transition ... It therefore adds a minimally necessary level near 1399.8 keV"). Their matching of level differences
  to peaks came before that (a3: "1082.219 [(1924.9, 842.7, 1082.2)]") and none repeated it with the new level. a2
  tested 1399.8 keV to the ground state (the 1400.6 keV sum peak) but not to 318.4 keV.
- None flagged the 1082 keV peak itself: a2 compared its singles and gated centroids (1082.21 and 1082.25 keV) and
  went on.
- So the trap failed at its trigger, not at the measurement. In v11 (Sol 1 of 3) the hidden line's upper level was
  placed early by an isolated clean line (1879.0 keV), and the one success also took the intensity from a gate that
  isolated the weak line, which v13 removed.
- v14 plan: make 557.1 keV a regular line (more beta feeding to 1399.8 keV), so the level stands from the start, and
  the hidden line somewhat stronger, so a plain two-Gaussian fit lands nearer the band; still no gate isolates it.
"""
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
s = insert_at_section_end(s, "## State now",
                          "- **%s**: v13 pass@3 card reviewed and marked seen. All three attempts missed only the hidden "
                          "1081.40 keV line: they placed 1399.8 keV late, by its weak 557.1 keV line, after matching level "
                          "differences to peaks. Next: v14 with 557.1 keV a regular line and a somewhat stronger hidden "
                          "line (draft in `work/gamma-decay-scheme/v14/`).\n" % NOW)
write("logs/gamma-decay-scheme.md", s)

ps = read("work/physics-task-state.md")
ps = insert_at_slug_end(ps, "gamma-decay-scheme",
                        "- %s: v13 pass@3 analysed: all three missed only the hidden 1081.40 keV line (the 1399.8 keV level "
                        "came late, by its weak 557.1 keV line). v14: stronger 557.1 keV and hidden line.\n" % NOW)
write("work/physics-task-state.md", ps)

b = read("logs/BRIEFING.md")
point = ("- (%s) gamma-decay-scheme v13 (0 of 3 on Sol 6.1): a trap that needs a level difference only works when the "
         "upper level is placed early. Sol 6.1 matches level differences to peaks once, before it adds levels from weak "
         "lines, and does not repeat it.\n" % NOW[11:])
write("logs/BRIEFING.md", b if b.endswith("\n") else b + "\n")
write("logs/BRIEFING.md", read("logs/BRIEFING.md") + point)
print("logged at", NOW)
