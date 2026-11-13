"""Append the pass@8 result of T-1519 v2 (job 20848, Astra 6) to the logs. Adds only; times from the clock (UTC)."""
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
anchor = "| 2026-11-11 03:59 | the same card, reviewed |"
assert s.count(anchor) == 1
i = s.index(anchor)
j = s.index("\n", i) + 1
row = ("| 2026-11-11 19:28 | pass@8 TOO EASY (T-1519 v2; no new card) | Seen by `supertasker.py status` at 19:35 (the poller "
       "of 04:03 had stopped with the earlier Claude Code session). The 03:59 card, already seen, now reads: \"IN REVIEW, "
       "CHECKING PASS@K. the pass@8 run has finished and the review team is checking it. Submit the task in DAS now if "
       "you haven't yet, but don't upload a new version: you get an update with the decision.\" (TO CHECK contract "
       "generality and the P3 ID as before). Task row: \"Status: pass@8 TOO EASY. Next: pass@8 solved 4 of 8: too "
       "easy. A reviewer decides whether it comes back to you to make it harder. pass@8 ran on Astra 6.\" Version row "
       "v2: Full review approved (Nov 10); Reviewer advanced to pass@k 19:07; pass@8 TOO EASY, 0 of 8 failed, 19:28; "
       "\"Download pass@8 attempts (.zip)\" (`gate/passk/20848.zip`). Report page: \"pass@8 TOO EASY. The model attempts "
       "ended out of range (4 solved). A reviewer decides whether it comes back to you to make it harder\". | yes |\n")
s = s[:j] + row + s[j:]

head = "## pass@3 analyses\n"
k = s.index("\n## Pitfalls")
block = """
### v2 pass@8 (T-1519 v2 = the v1 files, job 20848, pass@8 on Astra 6 ended 2026-11-11 19:28): 4 solved, TOO EASY

- The bundle (`work/rv-planet-census/v2/pass8/`: `pass8.zip`, untrusted `x/`, answers in `outputs/aK.json`, digests
  in `attempts/`, comparison `census.md`; extracted with `work/rv-planet-census/v2/pull_pass8.py`) holds 4 attempts,
  all reward 1: 8-10 min, 23-29 episodes, $2.14-2.60 each. The report says "ended out of range (4 solved)".
- Every trap handled in every attempt: rotation 34.2-34.46 d (Halpha quasi-periodic GP); d at 1.2195 d (the 5.47 d
  alias rejected jointly); c at 17.66-17.67 d (strong in both instruments across seasons; the evolving 16 d and the
  11.36 d power assigned to activity through the indicators); e at 113.6-114.8 d with its eccentric orbit and the
  single dip (duration and conjunction checked against the orbit); the 6.047 d binary rejected (alternating depths,
  RV amplitude 0.15 m/s at that period); dilution corrected. K within 10.5%, masses within 10.3%, b's radius +3.7 to
  +5.6%, e's +0.3 to +2.0%.
- Astra 6's playbook (a1's messages): periodograms of every observable with alias maps, joint Keplerian fits, a BLS
  search, binary vetting, residual signals classified by indicator overlap and seasonal stability, a quasi-periodic
  GP, transit fits with the stellar density and the dilution, posterior sampling of the single transit, daily and
  annual alias tests. The census as built is routine for it.
"""
s = s[:k] + block.rstrip("\n") + "\n" + s[k:]

anchor = "\n\n## Current design (v1, 2026-11-10)\n"
entry = (
    "- **%s %s**: the full review approved v2 (= v1) and a reviewer advanced it to pass@k (19:07). pass@8 on Astra 6\n"
    "  ended 19:28 \"TOO EASY\": the bundle holds 4 attempts, all solved, every trap handled (see pass@3 analyses, v2\n"
    "  pass@8). A reviewer decides whether it comes back for hardening; no upload meanwhile. The poller of 04:03 had\n"
    "  stopped with the earlier session (seen at 19:35; restarted 19:37). Next: draft a harder v3 in\n"
    "  `work/rv-planet-census/v3/` aimed at what Astra's playbook skips, so that it is ready if the task comes back.\n"
    % (day, hm))
s = s.replace(anchor, "\n" + entry.rstrip("\n") + anchor)
wr(p, s)

p = "logs/STATUS.md"
s = rd(p)
i = s.index("\nArchived:\n")
row = ("| rv-planet-census | `tasks/active/rv-planet-census/` | T-1519 | 4040198 | v1 (the platform's v2 is the same "
       "files) | IN REVIEW: full review approved; pass@8 on Astra 6 TOO EASY (4 solved of 4 run, job 20848, 19:28); a "
       "reviewer decides whether it comes back. pass@3 P3-DE0E-7F4D-56A1 is with the user | %s %s | Wait for the "
       "decision (poller T-1519); draft a harder v3 in `work/rv-planet-census/v3/` | [log](rv-planet-census.md) |\n"
       % (day, hm))
s = s[:i].rstrip("\n") + "\n" + row + s[i + 1:]
wr(p, s)

p = "work/physics-task-state.md"
s = rd(p)
j = lr.insert_at_slug_end(s, "rv-planet-census")
entry = ("- **%s %s**: full review approved; pass@8 on Astra 6 (job 20848, 19:28): 4 of 4 solved, TOO EASY, every trap\n"
         "  handled. A reviewer decides whether it comes back; v3 to be drafted against Astra 6's playbook." % (day, hm))
s = s[:j] + "\n" + entry + s[j:]
wr(p, s.rstrip("\n") + "\n")

p = "logs/BRIEFING.md"
s = rd(p)
s = s.rstrip("\n") + "\n" + (
    "- (%s) pass@8 can end before 8 attempts: T-1519's ended at 4 attempts, all solved (\"ended out of range (4\n"
    "  solved)\"), and the card was not replaced: the seen 03:59 card changed its text in place to \"IN REVIEW, CHECKING\n"
    "  PASS@K\", so the poller saw no unseen card. Read `status` (the task row) after any long gap, not only the cards.\n"
    "  A background poller dies with the Claude Code session that started it; after a restart, check `ps -ef | grep\n"
    "  poll_pipeline` and restart your own.\n" % hm)
wr(p, s)
print("logged at", day, hm)
