"""2026-11-10: log v5's quick-check card (passed, 07:42) as unseen. Adds only."""
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


row = ("| 2026-11-10 07:42 | the quick check passed (T-1383 v5) | \"All 40 criteria pass. pass@3 has started: three "
       "attempts by the target model on these exact files. You get another update when it ends. Do not change the task "
       "meanwhile: any edit needs a new check.\" Version row: quick check PASS, 36 of 40 pass; pass@3 running on Sol "
       "6.1, 0 of 3 ended (from 07:42). Queued 01:58, running from about 07:26. Poller exit 0 at 07:44. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
