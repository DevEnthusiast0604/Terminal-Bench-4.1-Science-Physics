"""2026-11-13 19:16: v14 pass@3 on Sol 6.1 QUALIFIED (2 of 3 failed); P3 ID P3-B911-F9F1-EDFA for DAS 4011092; full
review queued as v15 (= v14's files). Logs the card unseen. Adds only. Run from the folder root."""
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
                          "| 2026-11-13 19:16 | in review (T-1383 v14 pass@3 OK, 2 of 3 failed) | \"IN REVIEW / the full "
                          "review is running. Submit the task in DAS now if you haven't yet, but don't upload a new "
                          "version ... pass@3 is OK: 2 of 3 attempts failed. The full review has started on these exact "
                          "files ... P3 ID P3-B911-F9F1-EDFA / this revision only\". Status: Queued; 15 versions; newest "
                          "row v15 19:16 \"Full review queued\" (with a Cancel control: not to be pressed). Poller exit 0 at "
                          "19:17. | no |\n")
s = insert_at_section_end(s, "## State now",
                          "- **%s**: v14 pass@3 on Sol 6.1 QUALIFIED at 19:16 (1 of 3 solved; the run the platform "
                          "restarted at 18:44). P3 ID **P3-B911-F9F1-EDFA** (this revision only), for the user to paste "
                          "into DAS 4011092. The full review runs as v15 (= v14's files), queued 19:16; pass@8 on Astra 6 "
                          "comes with it (1-6 of 8 qualifies). No uploads until the review decides. Next: analyse the "
                          "pass@3 bundle, mark the card seen, watch the review.\n" % NOW)
write("logs/gamma-decay-scheme.md", s)

st = read("logs/STATUS.md")
lines = st.split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| gamma-decay-scheme |"))
lines.insert(last + 1, "| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v14 "
             "(`gamma-decay-scheme-20261113.zip`, digest `eba494d8…0722`); full review as v15 | IN REVIEW: pass@3 1 of 3 "
             "(QUALIFIED 19:16), P3-B911-F9F1-EDFA; full review queued | %s | User pastes P3-B911-F9F1-EDFA into DAS "
             "4011092. Watch the full review and pass@8 (1-6 of 8); no uploads meanwhile | [log](gamma-decay-scheme.md) |"
             % NOW)
write("logs/STATUS.md", "\n".join(lines))

ps = read("work/physics-task-state.md")
ps = insert_at_slug_end(ps, "gamma-decay-scheme",
                        "- **%s**: v14 pass@3 1/3 on Sol 6.1 (19:16, after a platform restart at 18:44): QUALIFIED, "
                        "P3 ID P3-B911-F9F1-EDFA (to the user for DAS 4011092). Full review queued as v15 (= v14's "
                        "files).\n" % NOW)
write("work/physics-task-state.md", ps)

b = read("logs/BRIEFING.md")
point = ("- (%s) Spent P3 ID: P3-B911-F9F1-EDFA (gamma-decay-scheme v14, pass@3 1 of 3 on Sol 6.1), given to the user "
         "for DAS 4011092. Never reuse it.\n" % NOW[11:])
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)
print("logged at", NOW)
