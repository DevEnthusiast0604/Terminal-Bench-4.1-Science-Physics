"""2026-11-13: v14's quick-check card reviewed and marked seen. Adds only."""
import re


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


row = ("| 2026-11-13 13:39 | the same card, reviewed | Marked seen 13:44 (`mark-seen` printed NOT CONFIRMED on the slow page; "
       "`updates` then listed the card as seen). Job 24365: 35 criteria 31 pass, 0 fail, 3 N/A "
       "(`verifier_execution_isolation`, `do_not_modify_enforced`, `artifact_efficiency`), `novel` NOT_PROVIDED (deferred "
       "to the full review); 5 extra pass. Reports in `work/gamma-decay-scheme/v14/criteria-35.md` and "
       "`criteria-extra.md`. Poller restarted for pass@3. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## State now",
                          "- **2026-11-13 13:45**: v14 quick-check card reviewed (31 pass, 0 fail, 3 N/A, `novel` deferred; "
                          "extra 5 of 5) and marked seen. pass@3 on Sol 6.1 running since 13:39; poller restarted.\n")
write("logs/gamma-decay-scheme.md", s)
print("logged")
