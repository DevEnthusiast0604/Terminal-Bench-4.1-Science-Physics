from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
entry = """- **2026-11-12 21:20**: the 19:48 poller stopped with exit 2 at 21:09: three status calls in a row (20:58, 21:04,
  21:08) timed out in `page.goto` waiting for "load" (30 s). Not a sign-out: the server answered curl in 0.5 s (401
  without cookies), and a fresh tab (`work/dhva-fermi-surface/v3/explore/probe_tab.py`, opened and closed again)
  showed the signed-in task view after 23 s to DOMContentLoaded: pass@3 still queued (19:40), 0 unseen. The platform
  was slow, so `tools/supertasker.py` `task_view` now waits for DOMContentLoaded (90 s) and then up to 30 s for the
  task view, plus 3.5 s for the cards; a status call took 28 s. Poller restarted at 21:20 (`poll4.out`).
"""
marker = "\n## Version history"
i = t.index(marker)
t = t[:i].rstrip("\n") + "\n" + entry + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
b = Path("logs/BRIEFING.md")
s = b.read_text(encoding="utf-8").rstrip("\n")
s += """
- (2026-11-12 21:20) `tools/supertasker.py` `task_view` no longer waits for the page's "load" event: from about 20:58
  the platform took over 30 s to fire it, every status call timed out and a poller stopped with exit 2, though the
  session was signed in and the app had rendered. It now waits for DOMContentLoaded (90 s), then up to 30 s for the
  task view and 3.5 s for the cards. If a poller stops with exit 2 on `Page.goto: Timeout`, open the page in a fresh
  tab before suspecting a sign-out (`work/dhva-fermi-surface/v3/explore/probe_tab.py` does it and closes the tab).
"""
b.write_text(s + "\n", encoding="utf-8", newline="\n")
print("ok")
