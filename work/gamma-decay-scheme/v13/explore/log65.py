"""2026-11-13: v13's pass@3 card (0 of 3 on Sol 6.1, TOO HARD, sent back 07:23); not yet reviewed. Adds only."""
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


def insert_at_slug_end(text, slug, entry):
    i = text.index("| Slug | `%s` |" % slug)
    m = re.compile(r"^# ", re.M).search(text, i)
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


row = ("| 2026-11-13 07:23 | pass@3 solved 0 of 3 (T-1383 v13) | \"pass@3 solved 0 of 3: the target model failed all three "
       "attempts, so the task comes back to you. A task must be solved in some but not all attempts. If they fail on "
       "something the instruction never states, or on an environment problem, fix that; if they fail at the stated "
       "difficulty, make the task somewhat easier. Then lint and upload the new version.\" Status: Sent back; version row "
       "v13: pass@3 \"TOO HARD, 3 of 3 failed\" 07:23, Platform \"sent back (SBQ)\" 07:23. Poller exit 0. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## State now",
                          "- **2026-11-13 07:25**: v13 SENT BACK: pass@3 on Sol 6.1 solved 0 of 3 (07:23, TOO HARD). Card "
                          "logged, not yet reviewed. Next: fetch the pass@3 bundle, find where the attempts failed, mark "
                          "the card seen, then make v14 somewhat easier there.\n")
write("logs/gamma-decay-scheme.md", s)

st = read("logs/STATUS.md")
lines = st.split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| gamma-decay-scheme |"))
lines.insert(last + 1, "| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v13 "
             "(`gamma-decay-scheme-20261112.zip`, digest `9734bed4…b7e1`) | SENT BACK: pass@3 on Sol 6.1 0 of 3 (07:23), "
             "TOO HARD | 2026-11-13 07:25 | Analyse the pass@3 bundle, mark the card seen, make v14 somewhat easier where "
             "the attempts failed, upload with release.sh | [log](gamma-decay-scheme.md) |")
write("logs/STATUS.md", "\n".join(lines))

ps = read("work/physics-task-state.md")
ps = insert_at_slug_end(ps, "gamma-decay-scheme",
                        "- 2026-11-13 07:23: v13 pass@3 on Sol 6.1: 0 of 3 (TOO HARD), sent back.\n")
write("work/physics-task-state.md", ps)
print("logged")
