"""Append the 2026-11-10 pass@3 result of T-1519 v1 (job 20397): a STATUS row and a physics-state event.

Adds only. The physics-state event goes at the end of this task's own section (tools/log_release.insert_at_slug_end).
Times come from the clock (UTC)."""
import datetime as dt
import importlib.util

spec = importlib.util.spec_from_file_location("log_release", "tools/log_release.py")
lr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lr)

hm = dt.datetime.now(dt.timezone.utc).strftime("%H:%M")
day = "2026-11-10"


def rd(p):
    return open(p, encoding="utf-8", newline="").read()


def wr(p, s):
    assert "\r" not in s
    open(p, "w", encoding="utf-8", newline="").write(s)


p = "logs/STATUS.md"
s = rd(p)
i = s.index("\nArchived:\n")
row = ("| rv-planet-census | `tasks/active/rv-planet-census/` | T-1519 | 4040198 | v1 (`rv-planet-census-20261110.zip`, "
       "digest `527d1959…33c7`; the platform's v2 is the same files) | IN REVIEW: pass@3 **2 of 3** (job 20397, 20:46), "
       "P3 ID **P3-DE0E-7F4D-56A1**, given to the user for DAS 4040198; full review queued (v2, job 20848) | %s %s | "
       "User pastes the P3 ID into DAS 4040198; wait for the full review (poller T-1519); no upload meanwhile | "
       "[log](rv-planet-census.md) |\n" % (day, hm))
s = s[:i].rstrip("\n") + "\n" + row + s[i + 1:]
wr(p, s)

p = "work/physics-task-state.md"
s = rd(p)
j = lr.insert_at_slug_end(s, "rv-planet-census")
entry = ("- **%s %s**: v1 pass@3 2/3 (job 20397, 20:46): QUALIFIED, P3 ID P3-DE0E-7F4D-56A1 (to the user for DAS\n"
         "  4040198; the user submits on DAS). Full review queued at 20:55 as the platform's v2 (job 20848)." % (day, hm))
s = s[:j] + "\n" + entry + s[j:]
wr(p, s.rstrip("\n") + "\n")
print("logged at", hm)
