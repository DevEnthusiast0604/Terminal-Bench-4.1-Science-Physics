"""2026-11-12: the poller's exit 2 (status time-outs) and its restart; v11 still queued. Adds only."""
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
state = ("- **%s**: the poller started 18:57 exited 2 at 02:10 after three status calls in a row timed out (the task "
         "page did not finish loading within 30 s; earlier 502 gateway errors 19:04-19:07 and 21:58-22:01). Not a "
         "sign-out: the debug Chrome was up, the site answered a plain request at once, and a direct "
         "`supertasker.py status T-1383` at 02:17-02:20 worked (about 170 s). v11's quick check is still queued (since "
         "2026-11-11 18:57), no unseen card. Poller restarted.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
