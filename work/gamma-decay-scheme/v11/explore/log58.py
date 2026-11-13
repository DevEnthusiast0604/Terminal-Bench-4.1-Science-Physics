"""2026-11-12: v12's full-review card reviewed and marked seen; waiting for a reviewer. Adds only."""
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


row = ("| 2026-11-12 07:32 | the same card, reviewed | Marked seen 07:37 (`updates` lists it as seen). Report "
       "`/job/22785/report` (\"A reviewer decides next\"; HTML and text in `work/gamma-decay-scheme/v12/full-review/`): "
       "\"Needs review: a person settles it\"; two checks did not pass: `contract_probes` (\"67 requirement(s) (3 "
       "dropped ...), 34 cite an enforcing test; 11 probed (1 from the grader …\") and `contract_generality` "
       "(\"FAIL-PENDING-DISPOSITION: 1 generator assumption(s) traced (0 dropped): 1 settled by a quoted rule, 0 not; 0 "
       "pair(s) of rules judged (0 …\"). The same pair v10's review left (3 assumptions then, 2 unsettled; 1 now, "
       "settled). No answer-leak finding. Nothing answered, disputed or uploaded. Poller restarted. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
state = ("- **%s**: v12's full review (= v11's files, job 22785) finished 07:32: \"A reviewer decides next\"; a person "
         "settles `contract_probes` and `contract_generality` (1 generator assumption, settled by a quoted rule). "
         "Waiting for a reviewer, then pass@8 on Astra 6; no upload. P3 ID P3-8546-0E6F-2BCD is with the user for DAS "
         "4011092.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

event = ("- **%s**: v12 full review finished 07:32 (job 22785): a reviewer settles contract_probes and "
         "contract_generality (1 assumption, settled by a quoted rule); no answer leak. Waiting.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", insert_at_slug_end(s, "gamma-decay-scheme", event))

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v12 = v11's files "
         "(`gamma-decay-scheme-20261111.zip`, digest `ebda2428…eaea`) | IN REVIEW: full review finished 07:32 (job "
         "22785), waiting for a reviewer (contract_probes, contract_generality); P3 ID P3-8546-0E6F-2BCD with the user "
         "| %s | Wait for the decision and pass@8 (poller); no upload; the user submits on DAS | "
         "[log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))
print("done", NOW)
