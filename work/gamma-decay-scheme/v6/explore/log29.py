"""2026-11-10: the full review of v7 (= v6's files, job 20271) reviewed and marked seen; a person settles its items.
Adds only."""
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


row = ("| 2026-11-10 14:05 | the same card, reviewed | Marked seen 14:11. Report `/job/20271/report` (\"A reviewer decides "
       "next\"; text and HTML in `work/gamma-decay-scheme/v7/full-review/`): \"Return the task (critical): Review the "
       "overlap proviso in instruction.md's output paragraph alongside the README's stated key realization. Does that "
       "proviso merely define the deliverable, or tell the solver the contaminated-peak insight in advance?\" \"Needs "
       "review: a person settles it: look at the counterexample the probe names: do the tests reject it? look at the "
       "input the finding names: does a stated rule decide it, or do two rules disagree on it?\" Checks not passed (3): "
       "`contract_probes` (\"83 requirement(s) (3 dropped ...), 46 cite an enforcing test; 11 probed (1 from the grader "
       "…\"), `contract_generality` (\"FAIL-PENDING-DISPOSITION: 2 generator assumption(s) traced (0 dropped): 1 settled "
       "by a quoted rule, 1 not; 0 pair(s) of rules judged (0 …\"), `answer_leak.no_answer_leak` (\"Although it does not "
       "identify the 511 keV case, it announces this central realization rather than leaving it to be inferred from the "
       "run evidence.\"). The page cuts the two contract texts on the server (the HTML holds no more; the page makes no "
       "data request). Nothing accepted, waived or disputed; nothing to upload. Poller restarted. | yes |\n")
state = ("- **%s**: the full review (v7 = v6's files, job 20271) finished at 14:04; status \"Waiting for a reviewer\". "
         "A person settles three failed checks: the answer leak (critical, \"Return the task\": v6's proviso \"A "
         "transition can share its peak with radiation of another origin, whatever the peak's energy.\" against the "
         "README's key realization), `contract_probes` (a counterexample the tests may not reject; not named on the "
         "page) and `contract_generality` (one generator assumption not settled by a quoted rule; not named). No "
         "upload until the decision (the card: \"Nothing to upload for now\"). Poller restarted.\n") % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

point = ("- (%s) A full review can end in \"A reviewer decides next\" with items a person settles (TO CHECK on the "
         "card). The report page `/job/J/report` shows each failed check cut to about 200 characters on the server; "
         "there is no fuller view to fetch. v6's easing sentence drew `answer_leak.no_answer_leak` (critical): an "
         "instruction sentence that states the task's central realization counts as a leak even when it names no case. "
         "Ease a 0 of 3 in a way that leaves the realization to the evidence.\n") % HM
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)

event = ("- **%s**: full review of v7 (= v6) finished 14:04: a reviewer decides. Flags: answer leak (critical, the v6 "
         "proviso), contract_probes, contract_generality. Nothing to upload.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v6 "
         "(`gamma-decay-scheme-20261110.zip`, digest `61344b23…562f`; the platform's v7 is the same files) | IN REVIEW, "
         "DECIDING: pass@3 2 of 3 (P3-6AEE-4ACB-FA2A, with the user for DAS); full review finished 14:04 with 3 checks "
         "for a person: answer leak (critical, the v6 proviso), contract_probes, contract_generality | %s | Wait for the "
         "reviewer's decision (poller); no uploads; nothing accepted, waived or disputed | [log](gamma-decay-scheme.md) |"
         % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))
print("done", NOW)
