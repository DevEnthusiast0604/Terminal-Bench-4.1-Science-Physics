"""2026-11-15 22:2x: still signed out after a second 12 h window; one status call per round while signed out; poller
restarted. Adds only. Run from the folder root."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    assert "\r" not in text
    open(path, "w", encoding="utf-8", newline="").write(text)


def insert_at_section_end(text, header, entry):
    i = text.index(header)
    m = re.compile(r"^## ", re.M).search(text, i + len(header))
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


b = read("logs/BRIEFING.md")
point = ("- (%s) `tools/poll_pipeline.py` with `wait-sign-in` now makes one status call per round while signed out (the "
         "first task's) instead of one per task: the other tasks show the same sign-in page, and every call leaves a "
         "utility world in each tab the user keeps open (the CDP stall of 2026-11-13). When a status answers, the round "
         "goes on to the other tasks as before.\n" % NOW[11:])
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)

entry = ("- **%s**: still signed out: the combined poller (`b6npr2efg`, started 10:23) saw only the sign-in page and "
         "reached its 12 h limit at 22:24:25 (exit 1). Signed out since about 2026-11-14 21:56; nothing seen on any task "
         "since the good status of 11-14 09:08. Poller restarted with `wait-sign-in`, now one status call per round "
         "while signed out (BRIEFING point of this time).\n" % NOW)
for slug in ("gamma-decay-scheme", "dhva-fermi-surface", "rv-planet-census"):
    s = read("logs/%s.md" % slug)
    write("logs/%s.md" % slug, insert_at_section_end(s, "## State now", entry))
print("logged at", NOW)
