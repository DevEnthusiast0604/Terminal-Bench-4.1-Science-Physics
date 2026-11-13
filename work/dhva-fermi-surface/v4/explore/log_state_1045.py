from pathlib import Path
p = Path("logs/dhva-fermi-surface.md")
t = p.read_text(encoding="utf-8")
entry = (
    "- **2026-11-13 10:45**: v3 QUALIFIED at 01:28 (pass@3 2 of 3, job 22636): P3 ID P3-2F9B-5B0C-A1B0, with the user\n"
    "  for DAS 4034278. The full review ran on v4 (= v3's files, job 24020) and finished 10:14: a reviewer decides, so no\n"
    "  upload. Its critical finding holds: README \"within 0.005% on the further draws [5]\" (a v2 line) against gamma at\n"
    "  +0.006% for seed 40342782 in v3's checks.txt [5]. Every other README figure re-read against checks.txt line by\n"
    "  line (10:40): all agree; the derived ones (0.67 T at 35 T, 0.54%, 2.3%, the N = 0 and 1% size effects) follow\n"
    "  from [1] by arithmetic. Draft `work/dhva-fermi-surface/v5/task/` = the active task with that one README word\n"
    "  changed (0.006%); scan 0 problems. `contract_probes` and `contract_generality` wait for the reviewer's note,\n"
    "  which names the counterexample and the assumption (gamma's did, 2026-11-10 17:56). Poller restarted 10:35\n"
    "  (`work/dhva-fermi-surface/v4/poll6.out`).\n"
)
marker = "\n## Version history"
i = t.index(marker)
t = t[:i].rstrip("\n") + "\n" + entry + t[i:]
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
