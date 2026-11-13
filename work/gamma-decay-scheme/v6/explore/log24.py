"""2026-11-10: v6's quick check (job 20055) reviewed and marked seen; pass@3 running. Adds only."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


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


row = ("| 2026-11-10 12:03 | the same card, reviewed | Marked seen 12:07. Job 20055 (reviewer astra, gpt-6.1-sol): "
       "35 criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, "
       "`artifact_efficiency`), `novel` NOT_PROVIDED (deferred to the full review); 5 extra all pass (3 draws, "
       "12:02:42Z). The new instruction sentence and R13 drew no finding. Reports in `work/gamma-decay-scheme/v6/"
       "criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
state = ("- **%s**: v6's quick check passed (job 20055, 12:03; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra "
         "pass). pass@3 running on Sol 6.1 from 12:03. Card marked seen 12:07; poller restarted.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

event = ("- **%s**: v6 (= v5 plus one instruction sentence, R13 and README) passed its quick check (job 20055); "
         "pass@3 running from 12:03.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v6 "
         "(`gamma-decay-scheme-20261110.zip`, digest `61344b23…562f`) | PASS@3: v6's quick check passed (job 20055, "
         "12:03; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass); pass@3 running on Sol 6.1 | %s | Wait for "
         "pass@3 (poller); 1 or 2 of 3: P3 ID into DAS 4011092; 3 of 3: harden; 0 of 3: check fairness | "
         "[log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))
print("done", NOW)
