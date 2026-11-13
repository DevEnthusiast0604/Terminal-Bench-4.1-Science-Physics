"""2026-11-13: the 21:11 card (T-1383 v15 full review finished, deciding) reviewed and marked seen; report saved;
what the contract-generality item most likely points at. Adds only. Run from the folder root."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    assert "\r" not in text
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


s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates",
                          "| 2026-11-13 21:11 | in review (T-1383 v15 full review finished, deciding) | Same card as the "
                          "row above, reviewed: report `job/25040/report` saved as "
                          "`work/gamma-decay-scheme/v14/full-review/report-25040.html`. Marked seen %s (`mark-seen` printed "
                          "NOT CONFIRMED [False]; `updates` shows `[seen] in review | 21:11`). | yes |\n" % NOW[11:])
s = insert_at_section_end(s, "## State now",
                          "- **%s**: the v15 full review (job 25040) failed the same two checks as v12's (job 22785), which "
                          "the reviewer then approved: contract_probes (\"67 requirement(s) (3 dropped ...), 34 cite an "
                          "enforcing test; 11 probed (1 from the grader ...\") and contract_generality. The report shows only "
                          "the truncated one-line summaries. What changed: v12 had \"1 generator assumption(s) traced: 1 "
                          "settled by a quoted rule, 0 not\", v15 has \"0 settled by a quoted rule, 1 not\". instruction.md "
                          "and NOTES.md did not change from v12 to v14; generate.py did: the weak line under E -> B "
                          "(1082.3 keV) is now Y -> A (1081.4 keV, a fifth of its intensity, level Y 1399.8 keV) instead "
                          "of X -> Da, and \"no gate shows it alone, and only the peak's shape and the gates' proportions "
                          "tell the two apart\" (generator comment). The traced assumption is most likely that this hidden "
                          "member counts as a transition \"that this run detected\": no sentence of the instruction or NOTES "
                          "says that a line inside a stronger line's peak counts as detected (the fewest-levels rule does "
                          "not decide it, since Y feeds B anyway). Nothing to upload: a reviewer settles it. If the task "
                          "comes back on this point, the fix is a stated rule (for example in NOTES.md: a transition counts "
                          "as detected when the data show it, also inside the peak of a stronger line), weighed against "
                          "pass@8 (it hints at the hidden line). Combined poller restarted 21:24 (`bdq9mh8vy`).\n" % NOW)
write("logs/gamma-decay-scheme.md", s)

st = read("logs/STATUS.md")
lines = st.split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| gamma-decay-scheme |"))
lines.insert(last + 1, "| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v14 "
             "(`gamma-decay-scheme-20261113.zip`, digest `eba494d8…0722`); full review as v15 | IN REVIEW, DECIDING: "
             "full review finished 21:11, 1 item for a person (contract generality: 1 generator assumption not settled "
             "by a quoted rule); P3-B911-F9F1-EDFA | %s | A reviewer decides; nothing to upload. Then pass@8 (1-6 of 8) "
             "| [log](gamma-decay-scheme.md) |" % NOW)
write("logs/STATUS.md", "\n".join(lines))

ps = read("work/physics-task-state.md")
ps = insert_at_slug_end(ps, "gamma-decay-scheme",
                        "- **%s**: full review v15 finished 21:11: IN REVIEW, DECIDING; contract generality left 1 "
                        "generator assumption unsettled (most likely whether the hidden Y -> A 1081.4 keV line under E -> B "
                        "counts as detected). Waiting for the reviewer; no upload.\n" % NOW)
write("work/physics-task-state.md", ps)
print("logged at", NOW)
