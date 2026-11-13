"""2026-11-10: a new board row for T-1383 v4 (quick check stopped at a static FAIL). Adds only."""
import datetime

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
path = "logs/STATUS.md"
lines = open(path, encoding="utf-8", newline="").read().split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
row = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v4 "
       "(`gamma-decay-scheme-20261109.zip`, digest `eebfdfcc…8e47`) | REWORK: v4's quick check (job 19370) stopped at the "
       "static checks, card \"did not finish\" (01:50, seen 01:53). Upstream `check-task-fields.sh` FAIL: the README's "
       "Author line must be `Name (email)` exactly as task.toml (TB 4.1); `task_readme` warns the same. 5 extra criteria "
       "pass; the 35 did not run | %s | Ask the user about the email in the README (their rule: the email only in "
       "task.toml); then fix, `release.sh gamma-decay-scheme T-1383 5 ...` | [log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, row)
open(path, "w", encoding="utf-8", newline="").write("\n".join(lines))
print("inserted after line", last + 1, NOW)
