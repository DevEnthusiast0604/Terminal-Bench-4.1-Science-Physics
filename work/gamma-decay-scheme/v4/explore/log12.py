"""2026-11-09: the two T-1383 cards reviewed and marked seen. Adds only."""
import datetime
import re

HM = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M")


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


cards = ("| 2026-11-09 14:37 | pass@3 solved 3 of 3, reviewed | Marked seen %s. Analysis under \"pass@3 analyses\" (v3): "
         "all three exact; v4 hardens with a real 511.00 keV line in the annihilation peak. | yes |\n"
         "| 2026-11-06 (\"Nov 6\") | the quick check did not finish, reviewed | Marked seen %s. A platform fault on v2's "
         "quick check; v2's content went up again as v3, which passed its quick check. Nothing to do. | yes |\n") % (HM, HM)
s = read("logs/gamma-decay-scheme.md")
write("logs/gamma-decay-scheme.md", insert_at_section_end(s, "## Platform updates", cards))
event = "- **2026-11-09 %s**: both T-1383 cards (pass@3 3/3 at 14:37; the Nov 6 quick-check fault) marked seen.\n" % HM
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done", HM)
