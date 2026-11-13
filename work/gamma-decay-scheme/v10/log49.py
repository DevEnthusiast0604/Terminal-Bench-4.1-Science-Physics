"""2026-11-11: v10's full-review card reviewed and marked seen; waiting for a reviewer. Adds only."""
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


def insert_at_slug_end(text, slug, entry):
    i = text.index("| Slug | `%s` |" % slug)
    m = re.compile(r"^# ", re.M).search(text, i)
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


row = ("| 2026-11-11 08:23 | the same card, reviewed | Marked seen 10:34. Report `/job/21495/report` (\"A reviewer decides "
       "next\"; text and HTML in `work/gamma-decay-scheme/v10/full-review/`): \"Needs review: a person settles it\"; two "
       "checks did not pass: `contract_probes` (\"67 requirement(s) (3 dropped ...), 35 cite an enforcing test; 11 probed "
       "(1 from the grader …\") and `contract_generality` (\"FAIL-PENDING-DISPOSITION: 3 generator assumption(s) traced (0 "
       "dropped): 1 settled by a quoted rule, 2 not; 0 pair(s) of rules judged (0 …\"). The page truncates both; the "
       "details come with the reviewer's decision. No answer-leak finding this time (v7 had one). Nothing answered, "
       "disputed or uploaded. Poller restarted. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
state = ("- **%s**: v10's full review (= v9's files, job 21495) finished 08:23: \"A reviewer decides next\"; a person "
         "settles `contract_probes` and `contract_generality` (no answer leak now). Waiting for a reviewer; no upload. "
         "P3 ID P3-4DCE-3D5C-5E63 is with the user for DAS 4011092.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

event = ("- **%s**: v10 full review finished 08:23 (job 21495): a reviewer settles contract_probes and contract_generality; "
         "no answer leak. Waiting.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", insert_at_slug_end(s, "gamma-decay-scheme", event))

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v10 = v9's files "
         "(`gamma-decay-scheme-20261111.zip`, digest `f9413828…b47a`) | IN REVIEW: full review finished 08:23 (job 21495), "
         "waiting for a reviewer (contract_probes, contract_generality); P3 ID P3-4DCE-3D5C-5E63 with the user | %s | "
         "Wait for the decision (poller); no upload; the user submits on DAS | [log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))
print("done", NOW)
