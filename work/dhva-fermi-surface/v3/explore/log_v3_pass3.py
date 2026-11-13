from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
analysis = """
### v3 (T-1563 v3, job 22636, pass@3 ended 2026-11-13 01:28): 2 of 3 solved, QUALIFIED

- Sol 6.1, rewards [1, 1, 0]. Agent times 16, 10 and 8 min (51, 35 and 27 episodes), cost $0.60, $0.41 and $0.28.
  Bundle in `work/dhva-fermi-surface/v3/pass3/` (`pass3.zip`, untrusted extraction under `x/`, `summary.md`);
  answers in `work/dhva-fermi-surface/v3/attempts/programs/aK/orbits.json`, digests in `attempts/attempt-K.txt`.
- **P3 ID P3-2F9B-5B0C-A1B0** (this revision only), for DAS 4034278; the user submits on DAS. The full review runs
  on v4 (v3's files, job 24020); then pass@8 on Astra 6, which must land at 1-6 of 8.
- a1 and a2: all six orbits; delta at 7300.56 and 7300.38 T (+0.008%, +0.005%), mass 3.247 and 3.24 (-3.1%,
  -3.3%); the other five within 0.003% and 4% (a1 beta belly 1.278, -0.9%).
- a3: the five lighter orbits right (beta belly's mass 1.419, +10%, inside the band), delta missing. It never looked
  at a high-field window or mentioned a peak near 7300 T: the designed trap ("A heavy orbit seen only at high field").
- Moving delta clear of 8 x gamma and of mass-matching combinations did what v2's analysis predicted: the attempts
  that searched at high field kept delta; the one that did not, missed it. The internal field again fell in every
  attempt.
"""
marker2 = "\n## Pitfalls"
j = t.index(marker2)
t = t[:j].rstrip("\n") + "\n" + analysis + t[j:]
p.write_text(t, encoding="utf-8", newline="\n")
s = Path("logs/STATUS.md")
lines = s.read_text(encoding="utf-8").split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| dhva-fermi-surface |"))
k = last
while k + 1 < len(lines) and lines[k + 1].startswith("|"):
    k += 1
row = ("| dhva-fermi-surface | `tasks/active/dhva-fermi-surface/` | T-1563 | 4034278 | v4 = v3's files "
       "(`dhva-fermi-surface-20261112.zip`, digest `428e960d…5769`) | IN REVIEW: v3 pass@3 **2 of 3**, QUALIFIED (job 22636, "
       "01:28), **P3 ID P3-2F9B-5B0C-A1B0** (given to the user for DAS 4034278); full review running as v4 (job 24020) "
       "since 01:28; card marked seen 01:36 | 2026-11-13 01:38 | Wait for the full review and pass@8 on Astra 6 (poller "
       "T-1563); no upload meanwhile; the user submits on DAS | [log](dhva-fermi-surface.md) |")
lines.insert(k + 1, row)
s.write_text("\n".join(lines), encoding="utf-8", newline="\n")
q = Path("work/physics-task-state.md")
w = q.read_text(encoding="utf-8").rstrip("\n")
w += ("\n- **2026-11-13 01:38**: v3 pass@3 **2 of 3**, QUALIFIED (job 22636, 01:28): P3 ID P3-2F9B-5B0C-A1B0 for DAS "
      "4034278 (with the user). The two attempts that searched at high field kept delta at 7300 T; the third never "
      "looked there. Full review running on v4 (= v3's files, job 24020).\n")
q.write_text(w, encoding="utf-8", newline="\n")
print("ok")
