"""2026-11-12: v12 sent back, pass@8 on Astra 6 solved 7 of 8 (21:09). Card logged as unseen. Adds only."""
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


row = ("| 2026-11-12 21:09 | sent back to you (T-1383 v12 pass@8 7 of 8) | \"The task is returned because it is too easy: "
       "the target model solved 7 of its 8 pass@8 attempts on this version. This version added the weak 1081.4 keV "
       "transition hidden under the stronger 1082.3 keV line, which only gated spectra reveal; most attempts still found "
       "it, so that one transition does not make the task hard enough on its own. / A task must be solved in some "
       "attempts but not all. ... Make the task harder there, without changing what the instruction asks for, then lint "
       "and upload the new version. Before the next upload, the reference solution must still score 1, an empty solution "
       "must score 0, and a new pass@3 must run on the new version.\" Status: Sent back (REWORK); \"pass@8 ran on Astra "
       "6\"; links \"View report\", \"Download pass@3 (.zip, optional)\", \"Download pass@8 attempts (.zip)\". Poller exit "
       "0 at 21:16. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
