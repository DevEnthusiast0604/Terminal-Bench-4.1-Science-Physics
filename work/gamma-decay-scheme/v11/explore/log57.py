"""2026-11-12: v12's full review (= v11's files) finished 07:32, a reviewer decides. Card logged as unseen. Adds only."""
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


row = ("| 2026-11-12 07:32 | in review (T-1383 v12 full review finished) | \"IN REVIEW, DECIDING / the full review has "
       "finished and the review team is deciding. ... don't upload a new version: you get an update with the decision. / "
       "The review left 1 item(s) that a person has to settle. ... Nothing to upload for now.\" TO CHECK: Contract "
       "generality: waits for a decision (\"Contract-generality FAIL-PENDING-DISPOSITION: 1 generator assumption(s) "
       "traced (0 dropped): 1 settled by a quoted rule, 0 not\"). P3 ID unchanged (P3-8546-0E6F-2BCD). Poller exit 0. "
       "| no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
