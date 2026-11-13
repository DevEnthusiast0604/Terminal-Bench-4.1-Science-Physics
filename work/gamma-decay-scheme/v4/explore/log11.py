"""2026-11-09: the v3 pass@3 analysis (job 19128, 3 of 3), the v4 design, kit 3.8.2. Adds only."""
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


analysis = """### v3 (T-1383 v3, job 19128, pass@3 ended 2026-11-09 14:37): 3 of 3 solved, TOO EASY

- Sol 6.1 (`gpt-6.1-sol`), rewards [1, 1, 1]. Agent times 11.4, 13.5 and 7.5 min (21, 32 and 21 steps); input tokens
  0.63, 1.33 and 0.63 M. Bundle in `work/gamma-decay-scheme/v3/pass3/` (`pass3.zip`, untrusted extraction under `x/`,
  answers pulled as JSON into `outputs/` by `v3/explore/pull_outputs.py`, digests in `attempts/`).
- `tools/scheme_report.py` (`v3/pass3/summary.md`): all three exact. Levels 16 of 16, transitions 30 of 30, parent
  half-life 4.37, 4.366 and 4.37 s, isomer 1963.1 keV with 165, 168 and 167 ns.
- Intensities (`v3/explore/intensity_errors.py`): worst 8.0, 14.9 and 13.1 percent, low on weak lines fed from high
  levels (992.7, 1092.0, 1143.4 keV): summing-out left uncorrected. A 10 percent band would have passed only a1, but the
  reference itself was 7.7 percent off, so the band was not the lever.
- Every trap fell to standard tools: the gain shift from room lines, time-profile shares (the 708 keV split), gated
  centroids for both doublets, sum peaks from the coincidence count over 7, escape peaks from 56Co ratios, the 38 keV
  isomeric exit from the delayed matrix.
- Shortcut in all three: the 511 keV peak set aside by its energy before any analysis (a1 `exclude=[...,511,...]`, a2
  `known=[...,511.,...]`, a3 `e!=511`), and the level differences that land on peaks of another origin (511.0 and
  403.4 keV) dismissed as "accounted for by summing, annihilation, or non-parent activity" with no gate checked.
- The bundle's README carries P3-DB4D-9D34-95EE with rewards [1, 1, 1]: not a qualifying result, so not for DAS.
- Hardening (v4), by the approved order (new physics once the agents handled the challenge cleanly) and the platform's
  "Hard for the right reason" (the model checks what it produced, never what it left out; deciding mark by mark what is
  real): a real transition on the annihilation line, 3092.6 -> 2581.6 keV (511.00 keV, I 0.853). The evidence is the
  narrow part of the production peak (the background run gives the annihilation shape) and its gates (941.3, 1092.0,
  1738.9 keV). Tried and dropped the same day: 3092.6 -> 2689.2 keV (403.4 keV) on the daughter's own line. The
  reference read it 28 percent low (summing-out at the top of a six-step cascade plus a 0.16 minority time share), and
  the stronger 551.8 keV line raised the 870.2 keV sum peak into a false doublet with 867.5 keV.
"""
state = ("- **%s**: v3's pass@3 reviewed (3 of 3, all exact; analysis under \"pass@3 analyses\"). v4 built in "
         "`tasks/active/gamma-decay-scheme/`: a real 511.00 keV transition hidden in the annihilation peak. Generator "
         "run (the user was told first): 16 levels, 31 transitions; the reference matches (intensities within 10.4 "
         "percent, the new line 0.80 for 0.853). `release.sh --check` passes under kit 3.8.2. At 17:58 the platform "
         "answered \"the platform is busy\"; the upload waits for it. Edit scripts `work/gamma-decay-scheme/v4/explore/"
         "edit13.py` to `edit19.py`.\n") % NOW
pitfall = ("- (%s) The reference turns coincidences into placement constraints. A parent line hidden under another "
           "activity's line inherits that activity's cascade partners (the daughter's 403.4-707.9 keV cascade would "
           "have tied 403.4 keV to the parent's 708.0 keV), so v4's `coincidence_flags` leaves a pair undecided when both "
           "peaks hold another activity. A split of the 511 keV peak must stop short of the 524.3 keV line (window 501 to "
           "518 keV), and a 6-sigma test on a parent time coefficient fails because the parent, ramp and daughter shapes "
           "are strongly correlated: test the narrow part's area and its parent share instead.\n") % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
s = insert_at_section_end(s, "## State now", state)
s = insert_at_section_end(s, "## Pitfalls", pitfall)
write("logs/gamma-decay-scheme.md", s)

points = (
    "- (%s) v3 pass@3 (job 19128): 3 of 3, all exact in 7 to 13 min. Its traps fell to standard tools; the shortcut all "
    "three took was setting the 511 keV peak aside by energy. v4 adds a real 511.00 keV transition there (3092.6 -> "
    "2581.6 keV, I 0.853), shown by the narrow part of the production peak and by its gates. Instruction, grader and "
    "requirements are unchanged; the data, `expected.json`, `checks.txt`, `generate.py`, `solve.py` and README changed.\n"
    "- (%s) Kit 3.8.2 is installed at `~/tb4/tb4-starter-pack` (download in `work/toolkit/20261109-382/`; 3.7.0 kept as "
    "`~/tb4/tb4-starter-pack-3.7.0`). Its lint fails a missing lockfile (3.7.0 warned; `TB4_STANDARD=4.0` makes it "
    "advice) and catches placeholder paths such as NN or NAME. v3 and v4 lint PASS under it.\n"
    "- (%s) TB4.1 task page: the Upload-the-fix dialog keeps `#ru-file`, `#ru-note` and `#ru-go`, and a separate `#ask` "
    "dialog (\"Why upload it anyway\", required) exists. When the platform is overloaded every page is a JSON error "
    "(\"the platform is busy: try again in a few seconds\") and `status` reports no task view: wait, it is not a "
    "sign-out.\n") % (HM, HM, HM)
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + points)

event = ("- **%s**: v3 pass@3 reviewed (3/3, all exact, 7 to 13 min). v4 = v3 plus a real 511.00 keV transition in the "
         "annihilation peak (3092.6 -> 2581.6 keV, I 0.853); generator run, reference matches; checks pass under kit "
         "3.8.2. Upload waits for the platform (busy at 17:58).\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done", NOW)
