"""Add the new task to the board, the briefing and the physics state file. Adds only, per the logging rule."""
board_row = (
    "| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v1 (`gamma-decay-scheme-20261106.zip`, "
    "digest `ac5b3e35…5357`) | IN REVIEW: v1 submitted (upload 1 of 5 on 11-06); quick check queued. New Science / Physics "
    "task, level scheme from a tape-station γγ run, started on the user's request of 11-06. | 2026-11-06 02:02 | Watch the "
    "quick check, then pass@3 (poller); log each card (Seen = no), review it, mark it seen | [log](gamma-decay-scheme.md) |\n"
)
s = open("logs/STATUS.md", encoding="utf-8", newline="").read()
i = s.index("\nArchived:\n")
s = s[:i].rstrip("\n") + "\n" + board_row + s[i + 1:]
open("logs/STATUS.md", "w", encoding="utf-8", newline="").write(s)

points = """- (00:45) User: "generate high difficult physics task and submit from now on" and "also watch the pipeline. try to re-work until it pass pass@3 step". This replaces the 11-05 23:51 stop: work on a new task, and rework until a P3 ID comes. "New DAS task id is 4011092": spent only by a P3 ID on this task.
- (02:02) New task `gamma-decay-scheme` submitted as T-1383, DAS 4011092 (upload 1 of 5 on 11-06): a level scheme from a moving-tape γγ run, data file, `RUN_PROGRAM=0`. Design and traps are in `logs/gamma-decay-scheme.md`. The design bet: inference from messy evidence, with NOTES promising nothing about the records, because every fully specified computation was solved 3 of 3.
- (02:02) The Toolkit is 3.3.2 on the platform (installed here: 3.3.0). The template is identical and the lint differences only relax rules, so the installed lint is enough. A copy is in `work/gamma-decay-scheme/kit/`.
- (02:02) `tb4 lint` crashes with UnicodeEncodeError (cp1252) once a lint line quotes a Greek letter. Run it, and `release.sh`, with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`.
- (02:02) `tests/generate.py` of this task also runs the reference on the shipped data and writes `tests/checks.txt`, so it takes about 80 s and counts as the allowed generator run, not as an oracle run.
"""
s = open("logs/BRIEFING.md", encoding="utf-8", newline="").read()
open("logs/BRIEFING.md", "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + points)

section = """
# gamma-decay-scheme

## Task identity

| Field | Value |
|---|---|
| Slug | `gamma-decay-scheme` |
| Source | `tasks/active/gamma-decay-scheme/` (output task, data file) |
| Category | Science / Physics |
| Platform ID | T-1383 (first submitted 2026-11-06 02:02) |
| DAS Task ID | 4011092 |
| Toolkit | tb4 3.3.0 installed, platform 3.3.2 |
| Target | quick check PASS; platform controls oracle 1, nop 0, cheat 0; pass@3 1/3 or 2/3 |
| P3 IDs pasted into DAS | none yet |

## Session events (newest last)

- **2026-11-06 02:02**: v1 submitted (upload 1 of 5 today), digest `ac5b3e35…5357`. Level scheme of an invented nucleus from a tape-station run: 16 levels, 30 transitions, parent half-life, isomer. Traps: production gain, escape peaks, sum peaks, two doublets, a shared line, an isomer behind an unseen transition. Bands 0.5 keV, 25%, 2%, 8%.
"""
s = open("work/physics-task-state.md", encoding="utf-8", newline="").read()
open("work/physics-task-state.md", "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + section)

old = "- On 2026-11-05 (23:51 UTC) the user stopped all work and had every task withdrawn, so `tasks/active/` is empty. Check\n  the newest rows of `logs/STATUS.md`, and don't restart uploads or pollers unless asked.\n"
new = "- On 2026-11-06 the user restarted work after the 11-05 stop: build hard physics tasks, submit them, watch the pipeline\n  and rework until pass@3 gives a P3 ID. The active task is `gamma-decay-scheme` (T-1383, DAS 4011092). Check the newest\n  rows of `logs/STATUS.md`.\n"
s = open("CLAUDE.md", encoding="utf-8", newline="").read()
assert old in s
open("CLAUDE.md", "w", encoding="utf-8", newline="").write(s.replace(old, new))
print("done")
