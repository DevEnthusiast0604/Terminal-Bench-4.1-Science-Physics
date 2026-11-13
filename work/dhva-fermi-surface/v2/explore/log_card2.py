import sys
from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
stage = sys.argv[1]
if stage == "unseen":
    row = ("| 2026-11-12 01:36 | pass@3 solved 0 of 3 (T-1563 v2) | \"pass@3 solved 0 of 3: the target model failed all "
           "three attempts, so the task comes back to you. A task must be solved in some but not all attempts. If they "
           "fail on something the instruction never states, or on an environment problem, fix that; if they fail at the "
           "stated difficulty, make the task somewhat easier. Then lint and upload the new version.\" Version row: "
           "pass@3 \"TOO HARD, 3 of 3 failed\" (01:36), Platform \"sent back (SBQ)\"; task status REWORK, \"pass@3 ran "
           "on Sol 6.1\". Job 21778. Seen by the poller at 01:39. | no |")
else:
    row = ("| 2026-11-12 01:36 | the same card, reviewed | Marked seen %s. %s | yes |" % (sys.argv[2], sys.argv[3]))
marker = "\n\n## pass@3 analyses"
i = t.index(marker)
t = t[:i] + "\n" + row + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok", stage)
