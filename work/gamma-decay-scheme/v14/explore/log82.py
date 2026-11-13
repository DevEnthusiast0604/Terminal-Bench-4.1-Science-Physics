"""2026-11-13: correction to the State now entry of 21:18 (poller start time). Adds only. Run from the folder root."""
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


s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## State now",
                          "- **%s**: correction to the entry of 21:18: the combined poller (`bdq9mh8vy`, T-1383, T-1563, "
                          "T-1519 at 600 s) was restarted at 21:17:55 (its first line), not 21:24.\n" % NOW)
write("logs/gamma-decay-scheme.md", s)
print("logged at", NOW)
