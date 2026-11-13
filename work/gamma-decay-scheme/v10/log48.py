"""2026-11-11: log the full-review card (v10, 08:23, one item for a person) as unseen. Adds only."""
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


row = ("| 2026-11-11 08:23 | in review (T-1383 v10 full review finished) | \"IN REVIEW, DECIDING / the full review has "
       "finished and the review team is deciding. ... don't upload a new version: you get an update with the decision. / "
       "The review left 1 item(s) that a person has to settle. ... Nothing to upload for now.\" TO CHECK: Contract "
       "generality: waits for a decision (\"Contract-generality FAIL-PENDING-DISPOSITION: 3 generator assumption(s) "
       "traced (0 dropped): 1 settled by a quoted rule, 2 not\"). Status: Waiting for a reviewer; v10 \"under evaluation "
       "by the review team\". P3 ID unchanged (P3-4DCE-3D5C-5E63). The poller started 06:37 had stopped with the earlier "
       "session; seen by `supertasker.py status` at 10:31. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
