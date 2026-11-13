"""2026-11-13: v13's quick check passed (05:54) and pass@3 started; the card, not yet reviewed. Adds only."""
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


row = ("| 2026-11-13 05:54 | the quick check passed (T-1383 v13) | \"All 40 criteria pass. pass@3 has started: three attempts "
       "by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: "
       "any edit needs a new check.\" Status: pass@3 running (\"pass@3 ran on Sol 6.1\"); version row v13: Quick check "
       "\"PASS, 36 of 40 pass\", pass@3 \"running, 0 of 3 ended\" 05:54. Uploaded 22:39, still running at 05:52 (poller). "
       "Poller exit 0 at 05:55. | no |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
s = insert_at_section_end(s, "## State now",
                          "- **2026-11-13 05:56**: v13 quick check PASSED (05:54; 36 of 40 as in earlier passes); pass@3 on "
                          "Sol 6.1 running. Card logged, not yet reviewed. Next: review the criteria reports, mark the card "
                          "seen, restart the poller.\n")
write("logs/gamma-decay-scheme.md", s)

st = read("logs/STATUS.md")
lines = st.split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| gamma-decay-scheme |"))
lines.insert(last + 1, "| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v13 "
             "(`gamma-decay-scheme-20261112.zip`, digest `9734bed4…b7e1`) | PASS@3: quick check passed 05:54 (36 of 40); "
             "pass@3 on Sol 6.1 running | 2026-11-13 05:56 | Review the criteria reports, mark the card seen, watch pass@3 "
             "(poller); on 1-2 of 3 give the user the new P3 ID for DAS 4011092 | [log](gamma-decay-scheme.md) |")
write("logs/STATUS.md", "\n".join(lines))

ps = read("work/physics-task-state.md")
ps = insert_at_slug_end(ps, "gamma-decay-scheme",
                        "- 2026-11-13 05:54: v13 quick check passed (36 of 40); pass@3 on Sol 6.1 running.\n")
write("work/physics-task-state.md", ps)
print("logged")
