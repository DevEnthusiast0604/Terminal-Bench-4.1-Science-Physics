from pathlib import Path
p = Path("logs/STATUS.md")
lines = p.read_text(encoding="utf-8").split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| dhva-fermi-surface |"))
k = last
while k + 1 < len(lines) and lines[k + 1].startswith("|"):
    k += 1
row = ("| dhva-fermi-surface | `tasks/active/dhva-fermi-surface/` | T-1563 | 4034278 | v3 (`dhva-fermi-surface-20261112.zip`, "
       "digest `428e960d…5769`) | PASS@3: v3's quick check passed (job 22636, card 19:40; 31 pass, 0 fail, 3 N/A, `novel` "
       "deferred; 5 extra pass); card marked seen 19:47; pass@3 queued on Sol 6.1 | 2026-11-12 19:48 | Wait for pass@3 "
       "(poller T-1563); 1 or 2 of 3: P3 ID to the user for DAS 4034278; 3 of 3: delta's strength next "
       "(`work/dhva-fermi-surface/v3/design.md`) | [log](dhva-fermi-surface.md) |")
lines.insert(k + 1, row)
p.write_text("\n".join(lines), encoding="utf-8", newline="\n")
q = Path("work/physics-task-state.md")
s = q.read_text(encoding="utf-8").rstrip("\n")
s += ("\n- **2026-11-12 19:48**: v3 quick check passed (job 22636, 19:40 card; 31 pass, 0 fail, 3 N/A, `novel` deferred; "
      "5 extra pass); marked seen 19:47. pass@3 queued on Sol 6.1.\n")
q.write_text(s, encoding="utf-8", newline="\n")
print("ok")
