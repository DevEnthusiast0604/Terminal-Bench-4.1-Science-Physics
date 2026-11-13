"""2026-11-10: the reviewer's send-back (17:56) reviewed and marked seen; the v8 plan. Adds only."""
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


row = ("| 2026-11-10 17:56 | the same card, reviewed | Marked seen 18:08. Both problems accepted as stated (the user's "
       "standing mandate: fix and resubmit). v8 plan: (1) drop the proviso; (2) a stated consistency rule, `energy_keV` "
       "within 0.5 keV of `from_keV` minus `to_keV`, as its own sentence (R9's quote stays whole), with a new test "
       "`test_transition_consistency` bound to a new R13 (and R1, R5); every honest answer so far keeps the gap within "
       "0.10 keV (`v8/explore/gap_stats.py` over expected.json and the nine pass@3 answers of v3, v5 and v6), the "
       "reviewer's case has 0.98 keV; (3) ease through the data instead of words, since v5 (no proviso) gave 0 of 3: "
       "the 511 keV line made about five times stronger; (4) the optional tie point answered in the README (the search "
       "finds one scheme at the fewest levels, so no tie arises). | yes |\n")
state = ("- **%s**: SENT BACK 17:56 (REWORK). Fixing as v8 (the platform's next version; v7 was v6's files): no proviso; "
         "a stated and tested consistency rule; the 511 keV line strengthened in the data (TARGET: M's β feeding 9.5 -> "
         "11.75 and its branch to H 6 -> 31, H's β feeding 5.0 -> 2.75, so every other line keeps its intensity and the "
         "511 keV line feeds about half of H, I about 4.4). New data and answers: the generator runs after telling the "
         "user.\n") % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

point = ("- (%s) A full review sent T-1383 back: (1) an instruction sentence that states the task's central realization "
         "is an answer leak even when it names no case; (2) a grader that checks `from_keV`, `to_keV` and `energy_keV` "
         "each on its own accepts an entry whose fields disagree with each other by up to three tolerances; test the "
         "relations between reported fields, not only each field. Easing after a 0 of 3 must go through the data's "
         "evidence, never the instruction's words.\n") % HM
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)

event = ("- **%s**: v7 (= v6) SENT BACK by the reviewer: the proviso leaks the key realization; the grader lacks a "
         "from/to/energy consistency check. v8 in progress: proviso out, consistency rule in, the 511 keV line "
         "strengthened about fivefold in the data (new generator run).\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v6 (the platform's v7 is the "
         "same files) | REWORK: sent back 17:56 (answer leak in the v6 proviso; no from/to/energy consistency check). "
         "P3-6AEE-4ACB-FA2A is spent with this revision | %s | Build v8 (proviso out, consistency rule and test, 511 "
         "keV line strengthened in the data), regenerate, `release.sh gamma-decay-scheme T-1383 8` | "
         "[log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))
print("done", NOW)
