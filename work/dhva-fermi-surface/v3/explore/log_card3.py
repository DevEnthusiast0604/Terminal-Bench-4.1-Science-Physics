import sys
from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
stage = sys.argv[1]
if stage == "unseen":
    row = ("| 2026-11-12 19:40 | the quick check passed (T-1563 v3) | \"All 40 criteria pass. pass@3 has started: three "
           "attempts by the target model on these exact files. You get another update when it ends. Do not change the "
           "task meanwhile: any edit needs a new check.\" Version row: quick check PASS, 36 of 40 pass; pass@3 queued "
           "19:40, on Sol 6.1. Queued 02:44, running from about 12:31, passed about 19:34 (status calls timed out "
           "19:01-19:27). Seen by the poller at 19:43. | no |")
else:
    row = "| 2026-11-12 19:40 | the same card, reviewed | Marked seen %s. %s | yes |" % (sys.argv[2], sys.argv[3])
marker = "\n\n## pass@3 analyses"
i = t.index(marker)
t = t[:i] + "\n" + row + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok", stage)
