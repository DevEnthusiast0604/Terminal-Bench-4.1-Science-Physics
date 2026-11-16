"""2026-11-16: the task page answers 404 since about 02:09; the poller stopped (exit 2); the user asked to stop the
background work. Adds only. Run from the folder root."""
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
point = ("- (%s) User: \"please stop background for now\". No poller runs (the last one had already stopped at 02:30); "
         "do not start one, or any other background job, until the user asks. Platform state at the time: from about "
         "02:09 UTC the task page `/task/T-1383` answers HTTP 404 `text/plain` \"not found\" (the status call shows an "
         "empty page title), where it had shown the sign-in page since 2026-11-14 21:56; `/` answers 200 with the app "
         "(\"TB4.1 Queue\"). Either the task route changed or the session/account changed: not looked into further, at "
         "the user's request.\n" % NOW)
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)

entry = ("- **%s**: the combined poller (`bpw5ym4lg`, started 2026-11-15 22:25, `wait-sign-in`) saw the sign-in page until "
         "about 02:00, then from 02:09:09 a page with no title three times in a row and stopped at 02:30:26 (exit 2). "
         "`supertasker.py fetch task/T-1383` at 02:31: HTTP 404 `text/plain` \"not found\"; `fetch /`: 200, the app. The "
         "user then asked \"please stop background for now\": no poller restarted; nothing runs in the background. Nothing "
         "seen on any task since the good status of 2026-11-14 09:08.\n" % NOW)
for slug in ("gamma-decay-scheme", "dhva-fermi-surface", "rv-planet-census"):
    s = read("logs/%s.md" % slug)
    write("logs/%s.md" % slug, insert_at_section_end(s, "## State now", entry))
print("logged at", NOW)
