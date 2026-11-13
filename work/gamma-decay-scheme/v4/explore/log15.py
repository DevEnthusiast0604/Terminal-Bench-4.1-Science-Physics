"""2026-11-10: log v4's quick-check card (did not finish, 01:50) as unseen. Adds only."""
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


row = ("| 2026-11-10 01:50 | the quick check did not finish (T-1383 v4) | \"The quick check stopped before it had a result "
       "(a platform fault, not your task). Upload the task again; if it stops again, tell your team lead.\" The card "
       "also lists a FIX: \"README.md author metadata omits the email address specified in task.toml. Set the author "
       "metadata in README.md to '<name> (<email>)' so it matches task.toml exactly.\" Version row: quick check failed, "
       "View report; task status Did not finish (REWORK). Queued 18:02, running from about 01:48, ended 01:50. Poller "
       "exit 0 at 01:51. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
