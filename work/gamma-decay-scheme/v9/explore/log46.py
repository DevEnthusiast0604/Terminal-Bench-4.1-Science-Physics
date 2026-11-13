"""2026-11-11: log v9's pass@3 card (qualified, 1 of 3 solved; full review started as v10, 06:26) as unseen. Adds only."""
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


row = ("| 2026-11-11 06:26 | in review (T-1383 v9 pass@3 QUALIFIED; full review as v10) | \"IN REVIEW / the full review "
       "is running. Submit the task in DAS now if you haven't yet, but don't upload a new version: you get an update when "
       "the review team has decided. / pass@3 is OK: 2 of 3 attempts failed. The full review has started on these exact "
       "files: you get an update when it ends. / Your pass@3 is done on these files: copy its P3 ID below and paste it "
       "into the same DAS task to submit it.\" P3 ID **P3-4DCE-3D5C-5E63** (this revision only). pass@3 on Sol 6.1 from "
       "06:09: 1 of 3 ended 06:22, 2 of 3 06:25. Newest version v10 (06:26), full review queued, \"Download pass@3 (.zip, "
       "optional)\". Poller exit 0 at 06:29. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
