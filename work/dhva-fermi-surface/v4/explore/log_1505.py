from pathlib import Path

# the task log: a State now entry
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
entry = (
    "- **2026-11-13 15:05**: the 10:35 poller stopped with exit 2 at 14:31: status calls had timed out (170 s) from 11:52,\n"
    "  three in a row by 14:31. Not a sign-out and not the platform (curl 401 in 1.7 s; every tab answered a raw CDP\n"
    "  evaluate at once). Playwright's `connect_over_cdp` hung after the websocket opened: with DEBUG=pw:protocol,\n"
    "  `Runtime.enable` on each platform tab never answered while it replayed leftover Playwright utility worlds, one\n"
    "  per earlier connection (`__playwright_utility_world_page@<id>`): 776 in the T-1563 tab and 697 in the #submit tab\n"
    "  within 40 s. Long-lived tabs keep them across navigations, so every poll of every session added one to every\n"
    "  tab. Fix in `tools/supertasker.py`: each call works in a new tab (`fresh_page`) and leaves it as\n"
    "  `about:blank#tb4-keeper` (`retire`); the next call closes the keeper after opening its own tab, so the window\n"
    "  keeps one; `task_view` also closes a tab still on the same task's page from an earlier call. Tabs: the T-1383\n"
    "  and #submit tabs had already been closed by another session between 14:47 and 14:52 (none had a dialog, a chosen\n"
    "  file or a filled field); I closed the T-1563 tab (14:55) and the orphan #submit tab (14:59, the former T-1519\n"
    "  tab). Status calls then took 23 s (97 s before the last close). T-1563 unchanged: Waiting for a reviewer, last\n"
    "  change 10:13, 0 unseen. Poller restarted 15:00 (`work/dhva-fermi-surface/v4/poll7.out`).\n"
)
marker = "\n## Version history"
i = t.index(marker)
t = t[:i].rstrip("\n") + "\n" + entry + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")

# the briefing: a dated point at its end
b = Path("logs/BRIEFING.md")
s = b.read_text(encoding="utf-8").rstrip("\n")
s += ("\n- (2026-11-13 15:05) If `supertasker.py` calls time out while Chrome on 9224 and the platform both answer, count\n"
      "  the tabs (`curl -s 127.0.0.1:9224/json/list`): every Playwright connection leaves a utility world in every open\n"
      "  tab, a tab keeps them across navigations, and connecting replays them all. After two days the platform tabs held\n"
      "  700 to 776 each and every session's status call timed out (dhva's poller exit 2 at 14:31). Since 15:00 each call\n"
      "  opens its own tab and leaves it as `about:blank#tb4-keeper`, which the next call closes (`fresh_page`, `retire`).\n"
      "  A tab the tool did not leave that way (a manual one, or one from before the change) still collects worlds: close\n"
      "  it with `curl -s 127.0.0.1:9224/json/close/<id>` once a raw check shows nothing in progress in it, and never close\n"
      "  the last tab. Status took 23 s afterwards.\n")
b.write_text(s, encoding="utf-8", newline="\n")
print("ok")
