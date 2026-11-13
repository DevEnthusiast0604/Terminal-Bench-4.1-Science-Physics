import sys
from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
stage = sys.argv[1]
if stage == "unseen":
    row = ("| 2026-11-12 01:13 | the quick check passed (T-1563 v2) | \"All 40 criteria pass. pass@3 has started: three "
           "attempts by the target model on these exact files. You get another update when it ends. Do not change the "
           "task meanwhile: any edit needs a new check.\" Version row: quick check PASS, 36 of 40 pass; pass@3 running, "
           "0 of 3 ended, on Sol 6.1. Queued 12:11, running from about 20:31, passed about 00:55. Seen by the restarted "
           "poller at 01:17. | no |")
else:
    row = ("| 2026-11-12 01:13 | the same card, reviewed | Marked seen %s. Job 21778 (reviewer astra, gpt-6.1-sol): 35 "
           "criteria 31 pass, 0 fail, 3 N/A, `novel` NOT_PROVIDED (deferred to the full review); 5 extra pass. The "
           "reviewer's notes name the internal-field conversion (`solution_quality`, `oracle_investigates`: \"corrects "
           "the field using sample dimensions supplied in NOTES.md\") and magnetic feedback (`difficult`). Reports in "
           "`work/dhva-fermi-surface/v2/criteria-35.md` and `criteria-extra.md`. pass@3 running. | yes |" % sys.argv[2])
marker = "\n\n## pass@3 analyses"
assert t.count(marker) == 1
i = t.index(marker)
t = t[:i] + "\n" + row + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok", stage)
