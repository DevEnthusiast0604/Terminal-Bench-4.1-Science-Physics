from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
entry = """- **2026-11-12 00:12**: the v2 poller (`tools/poll_pipeline.py T-1563 43200 180`, from 12:11) reached its 12 h
  limit with no card (exit 1). v2's quick check was queued until about 20:31 and has been running since; the platform
  answered 503/502 briefly at 19:04, 19:52 and 21:58 (not counted as misses). Poller restarted at 00:12; outputs
  `work/dhva-fermi-surface/v2/poll1.out`, `poll2.out`. The v3 dials for each outcome are in
  `work/dhva-fermi-surface/v3/plan.md` (v1's attempts never mention the sample's size or magnetization).
"""
marker = "\n## Version history"
i = t.index(marker)
t = t[:i].rstrip("\n") + "\n" + entry + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
