from pathlib import Path
p = Path("logs/STATUS.md")
lines = p.read_text(encoding="utf-8").split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| dhva-fermi-surface |"))
k = last
while k + 1 < len(lines) and lines[k + 1].startswith("|"):
    k += 1
row = ("| dhva-fermi-surface | `tasks/active/dhva-fermi-surface/` | T-1563 | 4034278 | v2 (`dhva-fermi-surface-20261111.zip`, "
       "digest `34941787…7604`) | REWORK: v2 pass@3 **0 of 3** TOO HARD (01:36, job 21778, Sol 6.1), sent back (SBQ); card "
       "marked seen 01:50. Every attempt converted the field axis and got the five lighter orbits; all three left out "
       "delta (a1 as a composite 4 eps + mean beta matching in F and m, a2 never searched a high-field window, a3 into "
       "a free 8 x gamma 5.8 T away) | 2026-11-12 01:55 | Build v3: delta 7415 -> 7300 T (no harmonic within 111 T, no "
       "combination of the others within 0.1% and 15% in mass); regenerate, Upload the fix, poller | "
       "[log](dhva-fermi-surface.md) |")
lines.insert(k + 1, row)
p.write_text("\n".join(lines), encoding="utf-8", newline="\n")
q = Path("work/physics-task-state.md")
s = q.read_text(encoding="utf-8").rstrip("\n")
s += ("\n- **2026-11-12 01:55**: v2 pass@3 **0 of 3** (01:36, job 21778), sent back. The internal field fell in every "
      "attempt (the magnetic-interaction combinations make K measurable); all three lost delta: a composite reading "
      "matching in frequency and mass, no high-field search, and gamma's eighth harmonic 5.8 T away absorbing it. v3: "
      "delta to 7300 T, clear of every harmonic and of mass-matching combinations; the high-field trap stays.\n")
q.write_text(s, encoding="utf-8", newline="\n")
print("ok")
