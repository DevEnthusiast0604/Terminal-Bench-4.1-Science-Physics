"""2026-11-10: v6's pass@3 (job 20055, 2 of 3, P3 ID issued) reviewed and marked seen; the full review runs as the
platform's v7 on the same files. Adds only."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
HM = NOW[11:]
P3 = "P3-6AEE-4ACB-FA2A"


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


row = ("| 2026-11-10 12:33 | the same card, reviewed | Marked seen 12:41. pass@3 of v6 (job 20055): 2 of 3 solved, rewards "
       "[1, 1, 0]; the bundle's README carries %s and task digest `sha256:61344b23…562f` (v6). Analysis under "
       "\"pass@3 analyses\" (v6). The user submits on DAS (12:38: \"There is no need to submit on DAS automatically. I "
       "will do it.\"), so the P3 ID went to the user, not to DAS. The full review runs as the platform's v7 (job 20271), "
       "whose zip is byte-identical to the local v6 zip. Poller restarted for the review's decision. | yes |\n") % P3
analysis = """### v6 (T-1383 v6, job 20055, pass@3 ended 2026-11-10 12:33): 2 of 3 solved, QUALIFIES

- Sol 6.1 (`gpt-6.1-sol`), rewards [1, 1, 0]. Agent times 17.7, 12.0 and 28.6 min (39, 23 and 53 steps); input tokens
  1.92, 0.81 and 2.51 M. Bundle in `work/gamma-decay-scheme/v6/pass3/` (`pass3.zip`, untrusted extraction under `x/`,
  answers in `outputs/`, digests in `attempts/`, `summary.md` from `tools/scheme_report.py`).
- P3 ID **%s** ("this revision only"), task digest `sha256:61344b23…562f`, the v6 files. The user pastes it into DAS
  4011092 (user, 12:38).
- a1 and a2: every test passes. 16 of 16 levels, 31 of 31 transitions, worst intensity errors 10.2 and 12.1 percent
  (992.7 keV both times), parent half-life 4.366 and 4.367 s, isomer 1963.1 keV with 169.6 and 168.0 ns.
- a3: fails `test_transitions_placed`, `test_transition_energies` and `test_relative_intensities` on one line: it left
  out 1489.6 -> 0 keV (1489.6 keV, I 4.41). Its level graph never had that edge: it took the whole 1489.6 keV peak as the
  same-crystal sum of the 646.9 + 842.7 keV (and 646.9 + 524.3 + 318.4 keV) cascade and tested a crossover only at
  1171 keV (rightly rejected) and 842.7 keV (rightly kept). Everything else was right: 16 levels, the other 30
  transitions within 9.5 percent, half-life 4.367 s, isomer 1963.1 keV with 165.6 ns. Summing is one of the traps the
  README documents, so this is a failure at the stated difficulty.
- The v6 sentence worked as meant: all three tested the 511 keV peak and kept 3092.6 -> 2581.6 keV with I 0.78, 0.91
  and 0.82 (true 0.853: -8.9, +7.2 and -3.9 percent), each from coincidences rather than the shared singles peak; none
  listed any of the five decoy differences (403.4, 1120.4, 2263.2, 300.1, 1507.2 keV) or any other line outside the
  scheme. a3 rejected the second 459.6 keV candidate (3148.8 -> 2689.2) as too weak, rightly.
""" % P3
state = ("- **%s**: v6 QUALIFIED: pass@3 2 of 3 (job 20055, 12:33; card seen 12:41). P3 ID **%s**, given to the user, "
         "who submits on DAS 4011092 (user, 12:38: \"There is no need to submit on DAS automatically. I will do it.\"). "
         "The full review runs on the same files as the platform's **v7** (job 20271, queued 12:33, running by 12:37; "
         "its zip is byte-identical to the local v6 zip, sha256 `178bc2e8…a5fb`). The card says not to upload a new "
         "version meanwhile. Poller restarted for the review's decision.\n") % (NOW, P3)
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## pass@3 analyses", analysis)
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

point = ("- (%s) gamma-decay-scheme QUALIFIED: v6's pass@3 2 of 3 (job 20055), P3 ID %s, passed to the user for DAS "
         "4011092. a3 lost only the 1489.6 keV ground-state line, taken as a pure sum peak. The full review runs on the "
         "same files as the platform's v7 (job 20271): a full review adds its own version row. Don't upload while it "
         "runs. If it sends the task back, mind the numbering: the platform's next upload is v8, and `release.sh` "
         "names the archived zip v<N-1>, so N=8 would archive the v6 zip as v7.\n") % (HM, P3)
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)

event = ("- **%s**: v6 pass@3 2/3 (job 20055): QUALIFIED, P3 ID %s (to the user for DAS 4011092). a3 missed only "
         "1489.6 -> 0 (taken as a sum peak). Full review running as the platform's v7 (same files).\n") % (NOW, P3)
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v6 "
         "(`gamma-decay-scheme-20261110.zip`, digest `61344b23…562f`; the platform's v7 is the same files) | IN REVIEW: "
         "pass@3 **2 of 3** (job 20055, 12:33), P3 ID **%s**, given to the user for DAS 4011092; full review running "
         "(v7, job 20271) | %s | User pastes the P3 ID into DAS; wait for the review's decision (poller); no uploads "
         "meanwhile | [log](gamma-decay-scheme.md) |" % (P3, NOW))
lines.insert(last + 1, board)
write(path, "\n".join(lines))
print("done", NOW)
