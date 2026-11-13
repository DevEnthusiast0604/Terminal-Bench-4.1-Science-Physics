"""2026-11-09 02:48: the 02:45 card reviewed and marked seen; poller restarted for pass@3. Adds only."""
import re


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


card = ("| 2026-11-09 02:45 | the same card, reviewed | Marked seen 02:48. Job 137 (reviewer astra, gpt-6.1-sol, 1 draw): "
        "35 criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, "
        "`artifact_efficiency`), `novel` NOT_PROVIDED (deferred to the full review); 5 extra all pass (`discoverable` and "
        "`oracle_investigates` too, v1's two failures). `task_readme` passed with the Author line without the email. "
        "Reports in `work/gamma-decay-scheme/v3/criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
write("logs/gamma-decay-scheme.md", insert_at_section_end(s, "## Platform updates", card))

point = ("- (02:48) T-0020's quick check (job 137, TB4.1's first for this account) passed all 40 criteria in 43 min "
         "(02:02 to 02:45). `task_readme` passed with the README Author line without the email, so that question does "
         "not block; pass@3 started at once.\n")
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)

event = ("- **2026-11-09 02:48**: quick-check card reviewed (job 137: 31 pass, 3 N/A, `novel` deferred; extra 5/5) and "
         "marked seen; poller restarted for the pass@3 card.\n")
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done")
