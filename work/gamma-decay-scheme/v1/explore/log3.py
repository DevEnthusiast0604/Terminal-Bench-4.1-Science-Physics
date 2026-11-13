"""The first quick-check card: logged with Seen = no. Adds only."""
s = open("logs/gamma-decay-scheme.md", encoding="utf-8", newline="").read()
row = ("| 2026-11-06 02:52 | the quick check found something to fix (job 18754) | v1: 34 of 39, 1 FAIL `discoverable`: the "
       "instruction asks for every level and does not exclude the 17-level scheme that `tests/checks.txt` documents. "
       "`oracle_investigates` FAIL-PENDING-DISPOSITION on the same point (1 of 3 draws, does not block). 35 criteria: 31 "
       "pass, 3 N/A, `novel` deferred. | no |\n")
head = "| Card time (UTC) | Title | Result | Seen |\n|---|---|---|---|\n"
assert head in s
s = s.replace(head, head + row)
open("logs/gamma-decay-scheme.md", "w", encoding="utf-8", newline="").write(s)
print("done")
