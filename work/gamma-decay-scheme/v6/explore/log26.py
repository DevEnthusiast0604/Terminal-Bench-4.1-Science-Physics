"""2026-11-10: the user's DAS rule ("There is no need to submit on DAS automatically. I will do it."): CLAUDE.md's
DAS bullet and a briefing point. Logs only gain lines; CLAUDE.md's one bullet is replaced (as log18.py did for
Security)."""
import datetime

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
HM = NOW[11:]


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    open(path, "w", encoding="utf-8", newline="").write(text)


OLD = ("- **DAS.** Each new P3 ID goes into the task's own DAS ID. Never reuse a P3 ID or a spent DAS ID (the briefing lists\n"
       "  them), and never upload a zip to DAS.\n")
NEW = ("- **DAS.** The user submits on DAS: \"There is no need to submit on DAS automatically. I will do it.\" (user,\n"
       "  2026-11-10). Never open, fill or submit a DAS page (DAS is `linkedin.com/ai-trainer`); when pass@3 gives 1 or 2\n"
       "  of 3, tell the user the new P3 ID and the task's DAS ID. Never reuse a P3 ID or a spent DAS ID (the briefing\n"
       "  lists them), and never upload a zip to DAS.\n")
s = read("CLAUDE.md")
assert s.count(OLD) == 1, s.count(OLD)
write("CLAUDE.md", s.replace(OLD, NEW))

point = ("- (%s) User: \"There is no need to submit on DAS automatically. I will do it.\" The user pastes each P3 ID into "
         "DAS. Never open, fill or submit a DAS page (the platform's \"DAS task N\" link goes to "
         "`linkedin.com/ai-trainer/tasks/...`); at 1 or 2 of 3, tell the user the P3 ID and the DAS ID. This replaces "
         "\"paste each new P3 ID into the task's own DAS ID\" as an action of mine. Before the message arrived, one "
         "read-only probe had opened the DAS page of T-1383 in the debug Chrome; it ended with \"Target page, context or "
         "browser has been closed\" before reading anything, typed and clicked nothing, and left no tab (CDP list: "
         "platform tabs only).\n") % HM
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)
print("done", NOW)
