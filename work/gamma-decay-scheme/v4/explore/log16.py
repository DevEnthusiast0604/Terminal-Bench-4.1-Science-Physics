"""2026-11-10: v4's quick check (job 19370) reviewed: a static FAIL on the README's Author line, not a platform
fault. Adds only."""
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


row = ("| 2026-11-10 01:50 | the same card, reviewed | Marked seen 01:53. Job 19370. The report (`/job/19370/report`) says "
       "FIX NEEDED, not a platform fault: 0 failed criteria, 1 warning, 110 passed, 6 n/a; the gate \"Static checks\" "
       "has 1 FAIL, upstream check `check-task-fields.sh`: \"README.md author metadata omits the email address specified "
       "in task.toml\" (Do: Author line `<name> (<email>)`, exactly as task.toml). Warning (Accept or Waive offered): "
       "`task_readme`: \"README metadata (TB 4.1): Author is not `Name (email)` as task.toml declares it\". The screens, "
       "the 35 criteria and the full review did not run. 5 extra criteria ran and all pass, 3 draws each "
       "(`work/gamma-decay-scheme/v4/criteria-extra.md`). The fix conflicts with the user's rule that the email appears "
       "only in task.toml: asked the user. Nothing accepted, waived or disputed. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
state = ("- **%s**: v4's quick check (job 19370) stopped at the static checks: TB 4.1's `check-task-fields.sh` fails "
         "a README whose Author line is not `Name (email)` exactly as task.toml declares it (kit 3.8.2's "
         "`lint/readme_format.py` and its template and example say the same; local lint only warns). Our README has "
         "the name alone, by the user's rule that the email appears only in task.toml. Asked the user; v4 waits. "
         "No upload on 11-10 yet (0 of 5).\n") % NOW
s = insert_at_section_end(s, "## State now", state)
pitfall = ("- (%s) TB 4.1 compares the README's metadata block with task.toml as text. The Author line must be "
           "`Name (email)` (organizations after ` | `); `tb4 lint` 3.8.2 only warns (`task_readme`), but the "
           "platform's upstream `check-task-fields.sh` fails it and the quick check stops before the 35 criteria. "
           "The card then reads \"did not finish (a platform fault)\": open View report before believing it.\n") % NOW
s = insert_at_section_end(s, "## Pitfalls", pitfall)
write("logs/gamma-decay-scheme.md", s)

point = ("- (%s) A TB4.1 card titled \"the quick check did not finish\" can hide a real static FAIL: v4's (job 19370) "
         "was `check-task-fields.sh` failing the README's Author line without the email. Always open View report "
         "(`/job/J/report`) before treating such a card as a platform fault. The README metadata block must match "
         "task.toml as text, Author as `Name (email)`; this conflicts with the rule that the email appears only in "
         "task.toml, which is the user's to settle.\n") % HM
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)

event = ("- **%s**: v4's quick check (job 19370) stopped at a static FAIL: the README's Author line must be "
         "`Name (email)` as task.toml declares it (TB 4.1). 5 extra criteria pass; the 35 did not run. Waiting on the "
         "user (the email-only-in-task.toml rule).\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done", NOW)
