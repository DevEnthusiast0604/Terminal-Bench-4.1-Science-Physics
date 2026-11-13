"""2026-11-09 02:45 card: T-0020 v1 (local v3) quick check passed, pass@3 started. Logged with Seen = no. Adds only."""
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


card = ("| 2026-11-09 02:45 | the quick check passed (T-0020 v1 = local v3) | \"All 40 criteria pass. pass@3 has started: "
        "three attempts by the target model on these exact files.\" Poller exit 0 at 02:47. | no |\n")
s = read("logs/gamma-decay-scheme.md")
write("logs/gamma-decay-scheme.md", insert_at_section_end(s, "## Platform updates", card))

row = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-0020 | 4011092 | v3 "
       "(`gamma-decay-scheme-20261109.zip`, digest `9b420950…ad6d`) | PASS@3: v3 quick check PASSED 02:45 (all 40 "
       "criteria; the first quick check on TB4.1); pass@3 running | 2026-11-09 02:47 | Fetch and review the reports, "
       "mark the card seen; wait for the pass@3 card (poller). 1-2/3: P3 ID into DAS 4011092. 3/3: harden. 0/3: look "
       "for an unstated requirement or an unfair check first | [log](gamma-decay-scheme.md) |")
s = read("logs/STATUS.md")
sep = "\nArchived:\n"
assert s.count(sep) == 1
write("logs/STATUS.md", s.replace(sep, "\n" + row + sep))

event = "- **2026-11-09 02:45**: v3 (T-0020 v1) quick check PASSED, all 40 criteria; pass@3 started.\n"
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done")
