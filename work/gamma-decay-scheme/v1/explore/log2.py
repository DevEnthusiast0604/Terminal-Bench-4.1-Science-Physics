"""Correction of two time stamps, added rather than edited (logging rule)."""
line = "- (02:12) Correction: the user's first request for this task came at 00:32 (transcript). The stamps 00:45 in this file's point and 00:30 in `logs/gamma-decay-scheme.md` were my estimates.\n"
s = open("logs/BRIEFING.md", encoding="utf-8", newline="").read()
open("logs/BRIEFING.md", "w", encoding="utf-8", newline="").write(s.rstrip("\n") + "\n" + line)

s = open("logs/gamma-decay-scheme.md", encoding="utf-8", newline="").read()
old = "## Current design (v1, 2026-11-06)"
new = "- **2026-11-06 02:12**: correction: the request above came at 00:32 (transcript); 00:30 was an estimate.\n\n" + old
i = s.index(old)
head = s[:i].rstrip("\n") + "\n"
open("logs/gamma-decay-scheme.md", "w", encoding="utf-8", newline="").write(head + new + s[i + len(old):])
print("done")
