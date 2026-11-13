"""2026-11-10: log the "in review" card of 14:05 (full review finished, the review team deciding) as unseen. Adds only."""
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


row = ("| 2026-11-10 14:05 | in review (T-1383 v7, full review finished) | \"IN REVIEW, DECIDING. the full review has "
       "finished and the review team is deciding. Submit the task in DAS now if you haven't yet, but don't upload a new "
       "version: you get an update with the decision. The review left 2 item(s) that a person has to settle. A reviewer "
       "settles them and decides what comes next: you get an update when one decides. Nothing to upload for now.\" TO "
       "CHECK: \"Contract generality: waits for a decision. Contract-generality FAIL-PENDING-DISPOSITION: 2 generator "
       "assumption(s) traced (0 dropped): 1 settled by a quoted rule, 1 not\"; TO CHECK: \"Answer leak. no answer leak. "
       "The difficulty README identifies the key realization as a peak of another origin not necessarily being free of "
       "a genuine transition\". P3 ID P3-6AEE-4ACB-FA2A shown again. Task row: status Waiting for a reviewer (\"Next: "
       "pass@3 is done on these files: a reviewer decides what comes next.\"), last change 14:04; v7's Full review "
       "\"under evaluation by the review team\" with View report. Poller exit 0 at 14:08. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
