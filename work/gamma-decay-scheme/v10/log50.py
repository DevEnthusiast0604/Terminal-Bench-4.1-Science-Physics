"""2026-11-11: log the sent-back card (v10 pass@8 on Astra 6: 8 of 8, TOO EASY, 18:12) as unseen. Adds only."""
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


row = ("| 2026-11-11 18:12 | sent back to you (T-1383 v10 pass@8 TOO EASY) | \"The target model solved all 8 of its "
       "attempts, so the task is too easy and comes back to you. A task must be solved in some but not all attempts. Look "
       "for what made it easy: a step the instruction spells out, an answer the data or the tests give away, a shortcut "
       "that skips the hard part. Make the task harder there, without changing what the instruction asks for, then lint "
       "and upload the new version.\" Status: Sent back (\"Read the note\", \"Upload the fix\", \"Withdraw\"); \"pass@8 "
       "ran on Astra 6.\" Version row v10: Full review \"send back\" 06:26; Reviewer \"advanced to pass@k\" 14:53; pass@8 "
       "TOO EASY, 0 of 8 failed, 18:12; Platform sent back (SBQ) 18:12; \"Download pass@8 attempts (.zip)\". Poller "
       "exit 0 at 18:13. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
