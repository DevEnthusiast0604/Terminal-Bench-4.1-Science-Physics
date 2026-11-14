"""2026-11-14: the combined poller's 12 h window ended with no new card; toolkit 3.8.8 installed; poller restarted.
Adds only. Run from the folder root."""
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
point = ("- (%s) The platform offered kit 3.8.8; `tools/kit_update.py` installed it (`~/tb4/tb4-starter-pack`, 3.8.7 "
         "kept as `~/tb4/tb4-starter-pack-3.8.7`, download in `work/toolkit/20261114-388/`, exit 0). Only VERSION and "
         "`lint/gates_static.py` changed: README lines that contain `/path/to/` placeholders are example commands, and "
         "their path tokens are no longer checked. A relaxation only, the template is unchanged, so nothing that passed "
         "under 3.8.7 can fail under it.\n" % NOW)
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)

entry = ("- **%s**: the combined poller (`bdq9mh8vy`, started 2026-11-13 21:17:55) reached its 12 h limit at 09:07:56 "
         "with no new card on T-1383, T-1563 or T-1519 (exit 1; the only changes it printed, at 00:04, were \"last "
         "change\" turning into a date at midnight). Kit 3.8.8 installed (BRIEFING point of this time); the combined "
         "poller restarted (`b6a0li6cv`, T-1383,T-1563,T-1519 at 600 s).\n" % NOW)
for slug in ("gamma-decay-scheme", "dhva-fermi-surface", "rv-planet-census"):
    s = read("logs/%s.md" % slug)
    write("logs/%s.md" % slug, insert_at_section_end(s, "## State now", entry))
print("logged at", NOW)
