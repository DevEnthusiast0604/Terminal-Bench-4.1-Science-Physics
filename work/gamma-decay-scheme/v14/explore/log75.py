"""2026-11-13: tabs the user keeps open still gather Playwright utility worlds (measured); poller slowed to 600 s.
Adds only: a BRIEFING point and a State now entry in logs/gamma-decay-scheme.md. Run from the folder root."""
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
point = ("- (%s) The tool's own tabs no longer gather Playwright utility worlds, but tabs the user keeps open still do: "
         "one per connection of any session. Measured 19:16 (`work/gamma-decay-scheme/v14/explore/count_worlds.py` on "
         "a `DEBUG=pw:protocol` log of `cdp_probe.py`): the T-1383 tab open since 18:52 held 10, `#submit` 6; a "
         "status call took 13 s and connecting 4 s. This afternoon's stall came at 387 to 2570 per tab. A poller at "
         "180 s adds 20 per tab per hour, so a watched tab reaches that range in about a day: poll at 600 s while "
         "pass@3 runs (results come hours apart), and when calls slow down, ask the user to close and reopen the tabs "
         "they watch (a reload does not clear them; the tool must not close a user's tab).\n" % NOW[11:])
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)

s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## State now",
                          "- **%s**: the user asked why checks keep timing out. Measured: status 13 s, connect 4 s; the "
                          "tabs kept open for the user hold 10 and 6 utility worlds after 24 min (BRIEFING point of "
                          "this time). Poller restarted at 600 s instead of 180 s. v14 pass@3 still running (restarted "
                          "by the platform at 18:44).\n" % NOW)
write("logs/gamma-decay-scheme.md", s)
print("logged at", NOW)
