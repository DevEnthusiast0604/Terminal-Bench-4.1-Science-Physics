from pathlib import Path

p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
entry = (
    "- **2026-11-13 15:10**: `tools/supertasker.py` again: at 15:01 a leftover `/#submit` tab appeared (history 3, so a\n"
    "  call's tab the platform sent from a task page to `#submit`, and the call was killed before it could blank it).\n"
    "  `fresh_page` now also closes a platform tab whose page is older than `STALE_SEC` (900 s) with no open dialog and\n"
    "  no file chosen; a call lasts under 3 minutes, so no tab in use qualifies. `task_view` leaves this call's own tabs\n"
    "  open until it ends (upload-fix reads the status while its upload tab is still open). Status call 19 s.\n"
)
marker = "\n## Version history"
i = t.index(marker)
t = t[:i].rstrip("\n") + "\n" + entry + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")

b = Path("logs/BRIEFING.md")
s = b.read_text(encoding="utf-8").rstrip("\n")
s += ("\n- (15:10) Addendum to 15:05: `fresh_page` also closes a platform tab whose page is older than 15 minutes with no\n"
      "  open dialog and no file chosen (a call the poller kills at 170 s never blanks its tab). Close tabs by hand only\n"
      "  when calls are already too slow for that to happen.\n")
b.write_text(s, encoding="utf-8", newline="\n")
print("ok")
