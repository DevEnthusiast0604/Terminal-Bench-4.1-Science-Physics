"""2026-11-13: platform access stalled 14:19-14:58 (Playwright utility worlds piled up in long-lived tabs); restored
after another session's patch to tools/supertasker.py (14:51); poller restarted. Adds only."""
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
                          "- **%s**: v14 pass@3 on Sol 6.1 still running (status at 14:58: \"running, 0 of 3 ended\", "
                          "0 unseen cards). The poller started at 13:45 stopped with exit 2 at 14:31: status calls timed "
                          "out (170 s) at 14:19, 14:25 and 14:31, and a manual call then timed out in `connect_over_cdp` "
                          "(180 s). Cause and fix under Pitfalls. Status took 32 s at 14:58; poller restarted.\n" % NOW)
s = insert_at_section_end(s, "## Pitfalls",
                          "- (%s) Platform access stalled from 14:19 to 14:58. Each Playwright connection over CDP adds a "
                          "utility world (`__playwright_utility_world_page@...`) to every open tab; the tab keeps it after "
                          "the connection ends, even across a reload, and the next connection replays them all as "
                          "`Runtime.executionContextCreated` events. The long-lived queue tabs held 387 to 2571 each "
                          "(4970 in all after reloading two of them), so status calls slowed until they timed out. "
                          "Reloading did not help; closing the old tabs did. Raw CDP over a websocket answered at once "
                          "throughout, so the browser and the sign-in were fine. A status call started just after the "
                          "closures connected late and then failed at `new_page` with `TargetClosedError`. Since 14:51 "
                          "`tools/supertasker.py` (patched by another session) opens a tab per call, leaves it as "
                          "`about:blank#tb4-keeper`, and the next call closes it.\n" % NOW)
write("logs/gamma-decay-scheme.md", s)

st = read("logs/STATUS.md")
lines = st.split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| gamma-decay-scheme |"))
lines.insert(last + 1, "| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v14 "
             "(`gamma-decay-scheme-20261113.zip`, digest `eba494d8…0722`) | PASS@3: pass@3 on Sol 6.1 running (0 of 3 "
             "ended at 14:58) | %s | Platform access stalled 14:19-14:58 (Playwright utility worlds in old tabs; "
             "supertasker.py patched 14:51); poller restarted. On 1-2 of 3 give the user the new P3 ID for DAS 4011092 "
             "| [log](gamma-decay-scheme.md) |" % NOW)
write("logs/STATUS.md", "\n".join(lines))

b = read("logs/BRIEFING.md")
point = ("- (%s) If `supertasker.py` calls slow down over days and then time out in `connect_over_cdp` while "
         "`http://127.0.0.1:9224/json/version` still answers, look at the open queue tabs: every past Playwright "
         "connection left a utility world in each tab it saw, and connecting replays them all (gamma-decay-scheme "
         "Pitfalls, 2026-11-13). Since 2026-11-13 14:51 the tool works in a tab of its own per call and the next call "
         "closes it, so its own tabs no longer pile them up; any other long-lived tab still does. Close such a tab only "
         "when no other session's call is running (`Get-CimInstance Win32_Process` lists them).\n" % NOW[11:])
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)
print("logged at", NOW)
