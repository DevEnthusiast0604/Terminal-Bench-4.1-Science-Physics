import sys
from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
stage = sys.argv[1]
if stage == "unseen":
    row = ("| 2026-11-13 10:14 | in review (T-1563 v4) | \"IN REVIEW, DECIDING. the full review has finished and the review "
           "team is deciding. Submit the task in DAS now if you haven't yet, but don't upload a new version: you get an "
           "update with the decision.\" \"The review left 2 item(s) that a person has to settle. A reviewer settles them "
           "and decides what comes next: you get an update when one decides. Nothing to upload for now.\" TO CHECK "
           "Contract generality: \"Contract-generality FAIL-PENDING-DISPOSITION: 1 generator assumption(s) traced (0 "
           "dropped): 0 settled by a quoted rule, 1 not\". TO CHECK Stated facts.facts consistent: \"README.md's "
           "frequency-tolerance discussion claims the reference is within 0.005% on every further noise draw\" (cut "
           "off). P3 ID P3-2F9B-5B0C-A1B0 shown again. Status \"Waiting for a reviewer\"; v4 \"Full review: under "
           "evaluation by the review team\". Seen by the poller at 10:31 (it started 01:38). | no |")
else:
    row = "| 2026-11-13 10:14 | the same card, reviewed | Marked seen %s. %s | yes |" % (sys.argv[2], sys.argv[3])
marker = "\n\n## pass@3 analyses"
i = t.index(marker)
t = t[:i] + "\n" + row + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok", stage)
