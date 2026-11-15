"""2026-11-15: still signed out after the poller's 12 h window; poller restarted with wait-sign-in. Adds only. Run from
the folder root."""
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


entry = ("- **%s**: the debug Chrome is still signed out: the combined poller with `wait-sign-in` (`b9vnwb72x`, started "
         "2026-11-14 22:22) saw only the sign-in page and reached its 12 h limit at 10:22:54 (exit 1, no status, so no "
         "card could be seen). The user was asked on 11-14 at 22:22 to sign in again. Combined poller restarted with "
         "`wait-sign-in`. No task has been seen since the good status of 2026-11-14 09:08.\n" % NOW)
for slug in ("gamma-decay-scheme", "dhva-fermi-surface", "rv-planet-census"):
    s = read("logs/%s.md" % slug)
    write("logs/%s.md" % slug, insert_at_section_end(s, "## State now", entry))
print("logged at", NOW)
