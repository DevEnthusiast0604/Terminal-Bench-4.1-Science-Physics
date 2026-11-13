"""2026-11-10: log v5's pass@3 card (0 of 3, 07:59) as unseen. Adds only."""
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


row = ("| 2026-11-10 07:59 | pass@3 solved 0 of 3 (T-1383 v5) | \"pass@3 solved 0 of 3: the target model failed all "
       "three attempts, so the task comes back to you. A task must be solved in some but not all attempts. If they fail "
       "on something the instruction never states, or on an environment problem, fix that; if they fail at the stated "
       "difficulty, make the task somewhat easier. Then lint and upload the new version.\" Version row: pass@3 TOO HARD, "
       "3 of 3 failed (Sol 6.1); Platform: sent back (SBQ) 07:59; task status Sent back. Poller exit 0 at 08:01. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
