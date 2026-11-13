"""2026-11-10: log the "in review" card (12:33; pass@3 of v6: 2 of 3, P3 ID issued) as unseen. Adds only."""
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


row = ("| 2026-11-10 12:33 | in review (T-1383, pass@3 of v6) | \"IN REVIEW. the full review is running. Submit the task "
       "in DAS now if you haven't yet, but don't upload a new version: you get an update when the review team has "
       "decided. pass@3 is OK: 1 of 3 attempts failed. The full review has started on these exact files: you get an "
       "update when it ends. Your pass@3 is done on these files: copy its P3 ID below and paste it into the same DAS "
       "task to submit it.\" P3 ID **P3-6AEE-4ACB-FA2A** (\"this revision only\"; \"Open the same task in DAS, paste the "
       "P3 ID and submit the task for review. There is no zip to upload to DAS. Never reuse an earlier P3 ID for a "
       "revised task.\"). Task row: IN REVIEW, 7 versions, last change 12:33, status Queued; newest version row "
       "\"T-1383 · v7\" (12:33) with Full review queued and \"Download pass@3 (.zip, optional)\". pass@3 ran on Sol 6.1 "
       "from 12:03. Poller exit 0 at 12:35. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
