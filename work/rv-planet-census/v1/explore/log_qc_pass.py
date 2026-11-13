"""Append the 2026-11-10 quick-check entries for T-1519 v1 (job 20397) and the note on the misplaced gamma entries.

Adds only: a State now line in logs/rv-planet-census.md, a STATUS row, an event at the end of each of the two
sections of work/physics-task-state.md, and a BRIEFING point. Times come from the clock (UTC)."""
import datetime as dt

hm = dt.datetime.now(dt.timezone.utc).strftime("%H:%M")
day = "2026-11-10"


def rd(p):
    return open(p, encoding="utf-8", newline="").read()


def wr(p, s):
    assert "\r" not in s
    open(p, "w", encoding="utf-8", newline="").write(s)


# logs/rv-planet-census.md: end of "## State now" (just before "## Current design").
p = "logs/rv-planet-census.md"
s = rd(p)
anchor = "\n\n## Current design (v1, 2026-11-10)\n"
assert s.count(anchor) == 1
entry = (
    "- **%s %s**: v1's quick check passed (job 20397, card 20:33): 35 criteria 31 pass, 0 fail, 3 N/A, `novel`\n"
    "  deferred to the full review; 5 extra pass. The platform's own oracle run scored 1 (nop 0, symlink cheat 0), so the\n"
    "  reference also agrees under the lock's scipy 1.18.1. pass@3 running on Sol 6.1 from 20:33. Card marked seen 20:36;\n"
    "  poller restarted (T-1519 only). Uploads on 11-10: 4 of 5 used (the other session's gamma v8 at 18:17), so one is\n"
    "  left today. `work/physics-task-state.md` had gamma's 18:08 and 18:17 entries under `# rv-planet-census`: they\n"
    "  were appended at the file's end, which became this task's section at 14:33. `tools/log_release.py` now inserts\n"
    "  its entry at the end of the slug's own section (`insert_at_slug_end`; checked on a copy of the file); both\n"
    "  sections carry a note. Risk to weigh before the full review (BRIEFING 18:08, test the relations between reported\n"
    "  fields): `minimum_mass_earth` follows from `semi_amplitude_m_s` and `period_days` only through the eccentricity,\n"
    "  which the task does not ask for, so the two are checked on their own bands; see `work/rv-planet-census/v1/design.md`.\n"
    % (day, hm))
s = s.replace(anchor, "\n" + entry.rstrip("\n") + anchor)
wr(p, s)

# logs/STATUS.md: a new row before "Archived:".
p = "logs/STATUS.md"
s = rd(p)
i = s.index("\nArchived:\n")
row = ("| rv-planet-census | `tasks/active/rv-planet-census/` | T-1519 | 4040198 | v1 (`rv-planet-census-20261110.zip`, "
       "digest `527d1959…33c7`) | PASS@3: v1's quick check passed (job 20397, 20:33; 31 pass, 0 fail, 3 N/A, `novel` "
       "deferred; 5 extra pass; platform oracle 1, nop 0, cheat 0); pass@3 running on Sol 6.1 | %s %s | Wait for "
       "pass@3 (poller T-1519); 1 or 2 of 3: tell the user the P3 ID for DAS 4040198; 3 of 3: harden; 0 of 3: check "
       "fairness, ease through the evidence | [log](rv-planet-census.md) |\n" % (day, hm))
s = s[:i].rstrip("\n") + "\n" + row + s[i + 1:]
wr(p, s)

# work/physics-task-state.md: an event at the end of each section.
p = "work/physics-task-state.md"
s = rd(p)
assert s.endswith("README follows.\n") and s.count("\n# rv-planet-census\n") == 1
s = s.rstrip("\n") + "\n" + (
    "- **%s %s**: the 18:08 and 18:17 entries just above are gamma-decay-scheme's (T-1383 v7 sent back, v8 uploaded),\n"
    "  not this task's: they were appended at the file's end, which became this section at 14:33. `tools/log_release.py`\n"
    "  now writes into the slug's own section.\n"
    "- **%s %s**: v1's quick check passed (job 20397, 20:33; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass;\n"
    "  platform oracle 1, nop 0, cheat 0). pass@3 running on Sol 6.1 from 20:33.\n" % (day, hm, day, hm))
j = s.index("\n# rv-planet-census\n")
k = j
while s[k - 1] == "\n":
    k -= 1
note = ("\n- **%s %s**: (note from the rv-planet-census session) this task's 18:08 and 18:17 entries were written at the\n"
        "  file's end, under `# rv-planet-census`. `tools/log_release.py` now writes into the slug's own section." % (day, hm))
s = s[:k] + note + s[k:]
wr(p, s)

# logs/BRIEFING.md: a dated point at the end.
p = "logs/BRIEFING.md"
s = rd(p)
s = s.rstrip("\n") + "\n" + (
    "- (%s) `work/physics-task-state.md` holds one '# ' section per task, so its end is the newest task's section only.\n"
    "  `tools/log_release.py` appended there and put gamma's v8 entry under rv-planet-census (11-10 18:17); it now\n"
    "  inserts at the end of the slug's own section. Add hand-written events the same way, not at the file's end.\n" % hm)
wr(p, s)
print("logged at", hm)
