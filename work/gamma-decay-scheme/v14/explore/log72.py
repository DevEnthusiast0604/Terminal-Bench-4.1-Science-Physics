"""2026-11-13: the T-1383 poller stopped at the user's request ("please stop background"). Adds only."""
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


s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## State now",
                          "- **%s**: the poller for T-1383 (running since 14:59) stopped at the user's request "
                          "(\"please stop background\"). Its polls, every 180 s, found the page unchanged throughout: "
                          "v14 pass@3 on Sol 6.1 running, 0 of 3 ended, 0 unseen cards. Nothing watches T-1383 now; "
                          "restart the poller only when the user resumes the work.\n" % NOW)
write("logs/gamma-decay-scheme.md", s)

st = read("logs/STATUS.md")
lines = st.split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| gamma-decay-scheme |"))
lines.insert(last + 1, "| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v14 "
             "(`gamma-decay-scheme-20261113.zip`, digest `eba494d8…0722`) | PASS@3: pass@3 on Sol 6.1 running (0 of 3 "
             "ended at the last poll) | %s | Poller stopped at the user's request; no watch running. When the user "
             "resumes: restart the poller; on 1-2 of 3 give the user the new P3 ID for DAS 4011092 "
             "| [log](gamma-decay-scheme.md) |" % NOW)
write("logs/STATUS.md", "\n".join(lines))
print("logged at", NOW)
