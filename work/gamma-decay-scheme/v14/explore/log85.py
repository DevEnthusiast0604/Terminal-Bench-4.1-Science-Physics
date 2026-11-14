"""2026-11-14: the platform came back from its outage with the debug Chrome signed out; poll_pipeline.py gained
`wait-sign-in`; poller restarted with it. Adds only. Run from the folder root."""
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
point = ("- (%s) The platform's outage (from 10:42, Cloudflare Tunnel error) ended by 21:56, and from then on every "
         "status call landed on the platform's sign-in page (page title \"Sign in · TB4.1 Queue\"): the debug Chrome's "
         "session had ended. Only the user can sign in again (in the debug Chrome window, port 9224); never type "
         "credentials or follow a sign-in flow for them. `tools/poll_pipeline.py` takes an optional fourth argument, "
         "`wait-sign-in`: a sign-in page before the run's first good status is then not a miss (one line, polling "
         "goes on, \"signed in again\" when a status answers), while a sign-in page after a good status still counts "
         "(three in a row end the watch with exit 2). Without the argument nothing changes.\n" % NOW)
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)

entry = ("- **%s**: the platform came back from its outage by 21:56 UTC, signed out: the combined poller (`budc8oo4k`, "
         "started 21:09) saw the Cloudflare Tunnel error at 21:09, then \"Sign in · TB4.1 Queue\" as the page title for "
         "every task from 21:56:50, and stopped at 22:20:45 after three misses in a row (exit 2). The user has to sign "
         "in again in the debug Chrome. Combined poller restarted with `wait-sign-in` (T-1383,T-1563,T-1519 at 600 s): "
         "it waits through the sign-out and goes on watching once a status answers.\n" % NOW)
for slug in ("gamma-decay-scheme", "dhva-fermi-surface", "rv-planet-census"):
    s = read("logs/%s.md" % slug)
    write("logs/%s.md" % slug, insert_at_section_end(s, "## State now", entry))
print("logged at", NOW)
