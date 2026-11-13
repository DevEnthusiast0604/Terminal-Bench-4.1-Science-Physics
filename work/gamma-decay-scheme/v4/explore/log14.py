"""2026-11-09: the poller's exit 2 at 19:01 was a platform outage, not a sign-out. Adds only."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
HM = NOW[11:]


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


state = ("- **%s**: the poller (`brhvr59o1`) exited 2 at 19:01. From 18:55 three polls got the app's shell (title "
         "\"TB4.1 Queue\") without the task view; from 19:03 the platform did not answer at all (no response in 30 s). "
         "At 19:06 it answered again (HTTP 401 to a request without the session), and `status` showed the session "
         "intact: T-1383 v4's quick check still queued from 18:02, no new card. An outage, not a sign-out. Poller "
         "restarted (`bic7p1a3f`).\n") % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

point = ("- (%s) Outage pattern (18:55 to 19:06): the app's shell (title \"TB4.1 Queue\") without the task view for "
         "three polls makes the poller exit 2 although the session is fine, and the platform may then stop answering "
         "for a few minutes. Before suspecting a sign-out, ask the root without the session: `curl -s -o /dev/null -w "
         "\"%%{http_code}\" https://queue.supertasker.ai/` gives 401 when the platform is up and 000 or 5xx when it is "
         "down. Wait for 401, then run `status`, then restart the poller.\n") % HM
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)
print("done", NOW)
