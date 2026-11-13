"""2026-11-09 14:05: the user paused background work; poller bsqfpq20s stopped. Adds only."""
import re


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


state = ("- **2026-11-09 14:05**: background work paused at the user's request (\"pls stop background working at the "
         "moment. I will let you know when needed\"): poller `bsqfpq20s` stopped. Its status line had not changed since "
         "02:48 (T-0020 v1: pass@3 queued from 02:45, no new card). Its last poll, at 14:04, got the TB4.1 sign-in page "
         "instead of the task (1 miss), so the session may have expired. Nothing watches T-0020 until the user says so.\n")
s = read("logs/gamma-decay-scheme.md")
write("logs/gamma-decay-scheme.md", insert_at_section_end(s, "## State now", state))

row = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-0020 | 4011092 | v3 "
       "(`gamma-decay-scheme-20261109.zip`, digest `9b420950…ad6d`) | PASS@3: quick check passed 02:45; pass@3 queued, "
       "no card by 14:04. Watching PAUSED by the user at 14:05 (poller stopped); the 14:04 poll got the sign-in page | "
       "2026-11-09 14:05 | Wait for the user's go-ahead. Then check the session (sign in again if needed), run "
       "`supertasker.py status T-0020`, restart the poller and handle the pass@3 card as planned | "
       "[log](gamma-decay-scheme.md) |")
s = read("logs/STATUS.md")
sep = "\nArchived:\n"
assert s.count(sep) == 1
write("logs/STATUS.md", s.replace(sep, "\n" + row + sep))

point = ("- (14:05) The user paused background work: \"pls stop background working at the moment. I will let you know "
         "when needed\". The T-0020 poller was stopped. Don't restart it, or start any other background run, until the "
         "user says so. Its last poll (14:04) got the TB4.1 sign-in page, so check the session before resuming.\n")
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)

event = ("- **2026-11-09 14:05**: background work paused by the user; poller stopped (no pass@3 card by 14:04; the 14:04 "
         "poll got the sign-in page).\n")
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done")
