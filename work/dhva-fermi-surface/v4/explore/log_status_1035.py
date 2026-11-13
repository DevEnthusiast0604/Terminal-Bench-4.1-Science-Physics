from pathlib import Path
p = Path("logs/STATUS.md")
lines = p.read_text(encoding="utf-8").split("\n")
last = max(i for i, l in enumerate(lines) if l.startswith("| dhva-fermi-surface |"))
k = last
while k + 1 < len(lines) and lines[k + 1].startswith("|"):
    k += 1
row = ("| dhva-fermi-surface | `tasks/active/dhva-fermi-surface/` | T-1563 | 4034278 | v4 = v3's files "
       "(`dhva-fermi-surface-20261112.zip`, digest `428e960d…5769`) | IN REVIEW, DECIDING: full review (job 24020) "
       "finished, card 10:14 marked seen 10:34; \"Return the task (critical)\": README claims frequencies within 0.005% "
       "on the further draws, but checks.txt [5] shows gamma +0.006% for seed 40342782 (confirmed: a v2 line v3 left "
       "unchanged); a person settles `contract_probes` and `contract_generality`; controls not run | 2026-11-13 10:35 | "
       "Wait for the reviewer (poller T-1563); no upload while deciding; fix drafted in `work/dhva-fermi-surface/v5/task/`, "
       "to upload as v5 once the task is returned | [log](dhva-fermi-surface.md) |")
lines.insert(k + 1, row)
p.write_text("\n".join(lines), encoding="utf-8", newline="\n")
q = Path("work/physics-task-state.md")
s = q.read_text(encoding="utf-8").rstrip("\n")
s += ("\n- **2026-11-13 10:35**: v4's full review (job 24020) finished 10:14; a reviewer decides. Critical: the README's "
      "\"within 0.005% on the further draws\" (from v2) against gamma's +0.006% for seed 40342782 in checks.txt [5] (v3's "
      "redraws); a person settles `contract_probes` and `contract_generality`. Fix drafted as v5; no upload while the "
      "reviewer decides.\n")
q.write_text(s, encoding="utf-8", newline="\n")
print("ok")
