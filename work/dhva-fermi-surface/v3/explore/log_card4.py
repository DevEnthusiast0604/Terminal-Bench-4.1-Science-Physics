import sys
from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
stage = sys.argv[1]
if stage == "unseen":
    row = ("| 2026-11-13 01:28 | in review (T-1563 v3 -> v4) | \"IN REVIEW. the full review is running. Submit the task in DAS "
           "now if you haven't yet, but don't upload a new version: you get an update when the review team has decided.\" "
           "\"pass@3 is OK: 1 of 3 attempts failed. The full review has started on these exact files: you get an update when "
           "it ends.\" **P3 ID P3-2F9B-5B0C-A1B0** (\"this revision only\"). Version row: v4 (v3's files), Full review "
           "running 01:28. pass@3 queued 19:40, running from about 00:00, 2 of 3 ended by 01:25. Seen by the poller at "
           "01:31. | no |")
else:
    row = "| 2026-11-13 01:28 | the same card, reviewed | Marked seen %s. %s | yes |" % (sys.argv[2], sys.argv[3])
marker = "\n\n## pass@3 analyses"
i = t.index(marker)
t = t[:i] + "\n" + row + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok", stage)
