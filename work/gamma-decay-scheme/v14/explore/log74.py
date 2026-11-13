"""2026-11-13: card "pass@3 is running again (not your task)" 18:44; the workspace moved to OneDrive; the debug Chrome
restarted on the moved profile. Argument: "no" logs the card unseen plus the state; "yes" logs it as marked seen.
Adds only. Run from the folder root."""
import datetime
import re
import sys

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
SEEN = sys.argv[1]
assert SEEN in ("no", "yes")


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
note = " Marked seen %s." % NOW[11:] if SEEN == "yes" else ""
s = insert_at_section_end(s, "## Platform updates",
                          "| 2026-11-13 18:44 | pass@3 is running again (not your task) (T-1383 v14) | \"pass@3 is running "
                          "again on the platform's side: its last run had a fault there, and nothing in your task caused "
                          "it. Nothing to do: you get an update when it ends.\" The v14 pass@3 started 13:39 had shown "
                          "\"running, 0 of 3 ended\" at every poll until then.%s | %s |\n" % (note, SEEN))
if SEEN == "no":
    s = insert_at_section_end(s, "## State now",
                              "- **%s**: work resumed at the user's request. At 18:37 no Chrome was running; it was started "
                              "again on port 9224 and was signed in. From about 18:41 the user moved the workspace from "
                              "`Documents\\Tango-arunufo` to `OneDrive\\Documents\\Tango-arunufo` (the folder root is now "
                              "there; the old folder is empty). The debug Chrome was closed while the profile moved and "
                              "started again at 18:52 on `OneDrive\\Documents\\Tango-arunufo\\.supertasker-profile`, still "
                              "signed in. The platform restarted v14's pass@3 at 18:44 after a fault on its side (card "
                              "above).\n" % NOW)
write("logs/gamma-decay-scheme.md", s)

if SEEN == "no":
    st = read("logs/STATUS.md")
    lines = st.split("\n")
    last = max(i for i, l in enumerate(lines) if l.startswith("| gamma-decay-scheme |"))
    lines.insert(last + 1, "| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v14 "
                 "(`gamma-decay-scheme-20261113.zip`, digest `eba494d8…0722`) | PASS@3: pass@3 on Sol 6.1 restarted by "
                 "the platform at 18:44 after a fault on its side | %s | Workspace now in `OneDrive\\Documents\\"
                 "Tango-arunufo`; debug Chrome on the moved profile; poller running. On 1-2 of 3 give the user the new "
                 "P3 ID for DAS 4011092 | [log](gamma-decay-scheme.md) |" % NOW)
    write("logs/STATUS.md", "\n".join(lines))

    b = read("logs/BRIEFING.md")
    point = ("- (%s) The workspace moved (user, 2026-11-13 about 18:41 UTC) to "
             "`C:\\Users\\Administrator\\OneDrive\\Documents\\Tango-arunufo`; the old `Documents\\Tango-arunufo` is "
             "empty. A shell may still start in the old folder: `cd` to the new root first in every call. Start the "
             "debug Chrome with `--remote-debugging-port=9224 --user-data-dir=<new root>\\.supertasker-profile`. Keep "
             "it open: the user watches progress in it.\n" % NOW[11:])
    write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)
print("logged at", NOW, "seen =", SEEN)
