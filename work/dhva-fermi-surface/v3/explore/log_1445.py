from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
entry = """- **2026-11-12 14:45**: the v3 poller (from 02:45) reached its 12 h limit with no card (exit 1). v3's quick check
  was queued until about 12:31 and has been running since. Poller restarted at 14:45; outputs
  `work/dhva-fermi-surface/v3/poll1.out`, `poll2.out`.
"""
marker = "\n## Version history"
i = t.index(marker)
t = t[:i].rstrip("\n") + "\n" + entry + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
