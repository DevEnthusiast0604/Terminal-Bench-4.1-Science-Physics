"""2026-11-10: the user's decision on the README's Author line (the email goes there too). CLAUDE.md gets the new
rule in place; the briefing gets a dated point (adds only). Run from the folder root."""
import datetime
from pathlib import Path

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
HM = NOW[11:]

p = Path("CLAUDE.md")
s = p.read_text(encoding="utf-8")
old = ("No host paths in a task or its evidence. The author's\n"
       "  email appears only in `task.toml`. Leave Chrome ports 9222 and 9223 alone.\n")
new = ("No host paths in a task or its evidence. The author's\n"
       "  email appears only in `task.toml` and on the README's Author line, which TB 4.1 requires as `Name (email)`\n"
       "  exactly as `task.toml` declares it (user, 2026-11-10; `scan_task.py` allows it on that line and nowhere\n"
       "  else). Leave Chrome ports 9222 and 9223 alone.\n")
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
print("edited", p)

point = ("- (%s) User, 2026-11-10 01:56, on v4's static FAIL (job 19370): \"Add it, upload again\". The author's email "
         "now also goes on the README's Author line, `- **Author:** Name (email)`, built from task.toml's author_name "
         "and author_email (TB 4.1 `check-task-fields.sh`; kit 3.8.2's template and example do the same). It stays out "
         "of every other file: `tools/scan_task.py` allows task.toml's own address on that one README line only. This "
         "replaces the rule that the email appears only in task.toml, for every task under TB 4.1.\n") % HM
s = open("logs/BRIEFING.md", encoding="utf-8", newline="").read()
open("logs/BRIEFING.md", "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + point)
print("done", NOW)
