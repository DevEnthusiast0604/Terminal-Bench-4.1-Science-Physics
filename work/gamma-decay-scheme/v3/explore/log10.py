"""2026-11-09: two unseen cards on T-1383 (the platform restored it; the 02:02 upload T-0020 is its v3). Logged with
Seen = no, plus the platform change. Adds only."""
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


cards = (
    "| 2026-11-09 14:37 | pass@3 solved 3 of 3 (T-1383 v3 = the 02:02 upload, job 19128) | \"The model solved all three "
    "attempts: the task is too easy. Make it harder, lint, and upload it again for a new review.\" Version row: pass@3 "
    "TOO EASY, 0 of 3 failed; Platform: sent back (SBQ) 14:37; task status Sent back (REWORK). Found at %s (the "
    "poller had been stopped at 14:05 at the user's request). | no |\n"
    "| 2026-11-06 (shown as \"Nov 6\") | the quick check did not finish (T-1383 v2, job 18856) | \"The quick check stopped "
    "before it had a result (a platform fault, not your task). Upload the task again; if it stops again, tell your team "
    "lead.\" First shown %s, after the platform restored T-1383. v2's content went up again as v3 (T-0020 at 02:02). "
    "| no |\n") % (HM, NOW)

state = (
    "- **%s**: the platform restored T-1383 (DAS 4011092, 3 versions; T-0851 and T-0610 are listed again) and "
    "`/task/T-0020` says \"not found\": the 02:02 upload is now **T-1383 v3** (job 19128, which was 137). v3: quick check "
    "PASS (36 of 40 pass), pass@3 **TOO EASY, 0 of 3 failed** (14:37, Sol 6.1), status Sent back (REWORK). Two unseen "
    "cards logged. Next: review pass@3 (`gate/full/19128.zip`), mark the cards seen, harden as v4, Upload the fix.\n") % NOW

pitfall = (
    "- (%s) The platform restored T-1383 and folded T-0020 into it as v3, so platform versions equal local versions "
    "again: the 02:02 point \"platform version = local version - 2\" no longer holds. The next fix is "
    "`release.sh gamma-decay-scheme T-1383 4 ...`. v3's jobs are under 19128 (`links T-1383 v3`); the updates list "
    "also shows `gate/full/137.zip`.\n") % NOW

s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## State now", state)
s = insert_at_section_end(s, "## Platform updates", cards)
s = insert_at_section_end(s, "## Pitfalls", pitfall)
write("logs/gamma-decay-scheme.md", s)

row = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v3 "
       "(`gamma-decay-scheme-20261109.zip`, digest `9b420950…ad6d`) | REWORK: v3 pass@3 3/3 TOO EASY (job 19128, "
       "14:37). The platform restored T-1383; T-0020 is gone and its upload is T-1383 v3 | %s | Review pass@3 "
       "(`gate/full/19128.zip`), mark both cards seen, harden as v4, `release.sh gamma-decay-scheme T-1383 4` | "
       "[log](gamma-decay-scheme.md) |") % NOW
s = read("logs/STATUS.md")
sep = "\nArchived:\n"
assert s.count(sep) == 1
write("logs/STATUS.md", s.replace(sep, "\n" + row + sep))

points = (
    "- (%s) The user resumed work (\"please continue working on from now on. just watch the pipeline as well\"); "
    "the 14:05 pause is over.\n"
    "- (%s) The platform restored the old data: T-1383 (gamma-decay-scheme, 3 versions), T-0851 and T-0610 are back, "
    "`/task/T-0020` says \"not found\", and the 02:02 upload is T-1383 v3 (job 19128). Local and platform versions "
    "match again. v3 came back from pass@3 at 14:37 as TOO EASY (3 of 3), so it is a hardening round. The page offers "
    "kit v3.8.2; counters: 2 of 2 new tasks left today, 74 quick checks and 1028 pass@3 runs left this week. The "
    "session was signed in at 17:20, so the 14:04 sign-in page came from the switchover.\n") % (HM, HM)
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + points)

event = ("- **%s**: platform restored T-1383; the 02:02 upload is its v3. v3 pass@3 **3/3 TOO EASY** (job 19128, "
         "14:37), sent back. Hardening round next (v4).\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done", NOW)
