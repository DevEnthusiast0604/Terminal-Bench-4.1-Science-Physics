"""The card of 02:52 reviewed and marked seen; the lesson goes to the briefing. Adds only."""
s = open("logs/gamma-decay-scheme.md", encoding="utf-8", newline="").read()
row_old = "| no |\n"
assert s.count(row_old) == 1
row = ("| 2026-11-06 02:52 | the same card, reviewed | Marked seen 02:57. Fixed in v2: the instruction states the rule of the "
       "fewest levels. | yes |\n")
s = s.replace(row_old, row_old + row)
open("logs/gamma-decay-scheme.md", "w", encoding="utf-8", newline="").write(s)

line = ("- (02:59) `discoverable` and `oracle_investigates` read the task's own evidence: gamma-decay-scheme v1 failed because "
        "`tests/checks.txt` and the README documented a 17-level scheme the data do not exclude, while the instruction said "
        "only \"every level\". When an inverse problem's solution is not unique, state the selection rule in the instruction "
        "(v2: \"the one with the fewest levels\"). A quick check on this data task took 50 min.\n")
s = open("logs/BRIEFING.md", encoding="utf-8", newline="").read()
open("logs/BRIEFING.md", "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + line)
print("done")
