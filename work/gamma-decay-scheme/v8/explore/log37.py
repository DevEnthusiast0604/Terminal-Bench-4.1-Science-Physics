"""2026-11-11: log v8's pass@3 card (3 of 3, 00:00) as unseen. Adds only."""
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


row = ("| 2026-11-11 00:00 | pass@3 solved 3 of 3 (T-1383 v8) | \"The model solved all three attempts: the task is too "
       "easy. Make it harder, lint, and upload it again for a new review.\" Version row: pass@3 TOO EASY, 0 of 3 failed "
       "(Sol 6.1); Platform: sent back (SBQ) 00:00; task REWORK, status Sent back. Poller exit 0 at 00:02. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
