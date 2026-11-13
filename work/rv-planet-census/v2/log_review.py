"""Append the full review's result for T-1519 v2 (= the v1 files, job 20848): the reviewed card row, a State now line,
a STATUS row and a physics-state event. Adds only; times from the clock (UTC)."""
import datetime as dt
import importlib.util

spec = importlib.util.spec_from_file_location("log_release", "tools/log_release.py")
lr = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lr)
now = dt.datetime.now(dt.timezone.utc)
day, hm = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")


def rd(p):
    return open(p, encoding="utf-8", newline="").read()


def wr(p, s):
    assert "\r" not in s
    open(p, "w", encoding="utf-8", newline="").write(s)


p = "logs/rv-planet-census.md"
s = rd(p)
card = "The full review ran from 20:55 (running at 21:01) to 03:59. Poller exit 0 at 04:00. | no |\n"
assert s.count(card) == 1
row = ("| 2026-11-11 03:59 | the same card, reviewed | Marked seen 04:02. Report `/job/20848/report` (\"A reviewer decides "
       "next\"; HTML and text in `work/rv-planet-census/v2/full-review/`): \"Needs review: a person settles it: look at the "
       "input the finding names: does a stated rule decide it, or do two rules disagree on it?\" Checks not passed (1): "
       "`contract_generality` (\"Contract-generality FAIL-PENDING-DISPOSITION: 3 generator assumption(s) traced (0 "
       "dropped): 2 settled by a quoted rule, 1 not; 0 pair(s) of rules judged (0 …\", cut on the server). No answer "
       "leak, no `contract_probes` failure, `novel` not raised. Nothing to upload. Poller restarted. | yes |\n")
s = s.replace(card, card + row)
anchor = "\n\n## Current design (v1, 2026-11-10)\n"
assert s.count(anchor) == 1
entry = (
    "- **%s %s**: the full review (platform v2 = the v1 files, job 20848) finished 03:59: \"Waiting for a reviewer\".\n"
    "  One check for a person: `contract_generality`, 3 generator assumptions traced, 2 settled by a quoted rule, 1 not\n"
    "  (the page cuts the text; it does not name the assumption). Candidates in `tests/generate.py` that no instruction\n"
    "  sentence fixes: the rotation period is the one at the spot belt's middle latitude, 20 deg (the star rotates\n"
    "  differentially: 34.0 d at the equator, -0.8%%, 36.6 d at the pole, +6.6%%, so every latitude is inside the 10%%\n"
    "  band); Earth's radius is the equatorial 6378.1 km (the mean one moves a radius by 0.1%%); the minimum mass solves\n"
    "  the mass function with the planet's own mass. None of them moves a graded answer across its band. No answer leak and no probe\n"
    "  failure this time (the hint sentence was removed before the first upload). Nothing to upload until a reviewer\n"
    "  decides; if the task is sent back, the next upload is platform v3, drafted in `work/rv-planet-census/v3/task/`.\n"
    "  Uploads on 11-11 so far: 2 of 5 (dhva-fermi-surface v1 00:01, gamma v9 00:28, other sessions).\n" % (day, hm))
s = s.replace(anchor, "\n" + entry.rstrip("\n") + anchor)
wr(p, s)

p = "logs/STATUS.md"
s = rd(p)
i = s.index("\nArchived:\n")
row = ("| rv-planet-census | `tasks/active/rv-planet-census/` | T-1519 | 4040198 | v1 (`rv-planet-census-20261110.zip`, "
       "digest `527d1959…33c7`; the platform's v2 is the same files) | IN REVIEW, DECIDING: pass@3 2 of 3 "
       "(P3-DE0E-7F4D-56A1, with the user for DAS 4040198); full review finished 03:59 with 1 check for a person: "
       "`contract_generality` (1 generator assumption not settled by a quoted rule) | %s %s | Wait for the reviewer's "
       "decision (poller T-1519); no upload meanwhile | [log](rv-planet-census.md) |\n" % (day, hm))
s = s[:i].rstrip("\n") + "\n" + row + s[i + 1:]
wr(p, s)

p = "work/physics-task-state.md"
s = rd(p)
j = lr.insert_at_slug_end(s, "rv-planet-census")
entry = ("- **%s %s**: full review of v2 (= v1, job 20848) finished 03:59: a reviewer decides. One check for a person,\n"
         "  `contract_generality` (3 generator assumptions, 1 not settled by a quoted rule). No answer leak." % (day, hm))
s = s[:j] + "\n" + entry + s[j:]
wr(p, s.rstrip("\n") + "\n")
print("logged at", day, hm)
