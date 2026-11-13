"""2026-11-12: v11 pass@3 QUALIFIED (1 of 3, 05:53), P3 ID P3-8546-0E6F-2BCD; full review queued as v12. Card logged
as unseen. Adds only."""
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


row = ("| 2026-11-12 05:53 | in review (T-1383 v11 pass@3 OK, 2 of 3 failed) | \"IN REVIEW / the full review is "
       "running. Submit the task in DAS now if you haven't yet, but don't upload a new version ... pass@3 is OK: 2 of 3 "
       "attempts failed. The full review has started on these exact files ... P3 ID P3-8546-0E6F-2BCD / this revision "
       "only ... Never reuse an earlier P3 ID for a revised task.\" Status: Queued; version row v12 (= v11's files): "
       "Full review queued 05:53; \"Download pass@3 (.zip, optional)\". Poller exit 0. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
