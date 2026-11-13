"""2026-11-12: the poller's exit 2 at 19:18 (slow task page) and its restart; still waiting for a reviewer. Adds only."""
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


s = read("logs/gamma-decay-scheme.md")
state = ("- **%s**: the poller started 07:37 saw \"Waiting for a reviewer\" all day (one slow call at 12:41) and exited 2 "
         "at 19:18 after three status calls in a row timed out (the task page did not load within 30 s). Not a "
         "sign-out: the debug Chrome was up and the site answered a plain request at once; a direct status at 19:21 "
         "timed out the same way. No new card seen. Poller restarted.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
