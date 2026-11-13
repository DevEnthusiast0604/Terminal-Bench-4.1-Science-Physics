"""2026-11-10: log the "sent back to you" card (17:56, the reviewer's decision on v7 = v6's files) as unseen. Adds
only. The note itself is saved verbatim in work/gamma-decay-scheme/v7/full-review/sent-back-note.txt."""
import datetime
import re
import sys

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
SRC = sys.argv[1]   # the poller's output file, which holds the card's text


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


src = read(SRC).replace("\r\n", "\n")
start = src.index("[UNSEEN] sent back to you | 17:56")
end = src.index("[exited with code", start)
note = src[start:end].rstrip() + "\n"
write("work/gamma-decay-scheme/v7/full-review/sent-back-note.txt", note)

row = ("| 2026-11-10 17:56 | sent back to you (T-1383 v7 = v6's files) | Reviewer: sent back (SBQ) 17:56; task REWORK, "
       "status Sent back (\"Next: Read the reviewer's note, fix the task and upload it again with Upload the fix.\"). "
       "Two problems to fix: (1) instruction.md line 5's proviso \"A transition can share its peak with radiation of "
       "another origin, whatever the peak's energy.\" announces the README's key realization; the instruction must define "
       "the deliverable, members and tolerances without it, the insight coming only from the run's data. (2) the "
       "verifier checks `from_keV`, `to_keV` and `energy_keV` each on its own, never their mutual consistency: 842.7 -> "
       "318.4 reported as 843.19 -> 317.91 with 524.30 keV (endpoints 525.28 keV apart) scored reward 1.0 on the live "
       "verifier (three judges agreed it is wrong); the fix must check consistency without tightening any field's own "
       "bound. Optional: `tests/generate.py` line 64 builds the scheme from a fixed TARGET and never exercises a tie "
       "between two placements with equally few levels; state a tie-break or add a generator case. Then: oracle 1, empty "
       "0, new pass@3. Full note in `work/gamma-decay-scheme/v7/full-review/sent-back-note.txt`. Poller exit 0 at 17:57. "
       "| no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW, len(note))
