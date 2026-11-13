from pathlib import Path
row = ("| dhva-fermi-surface | `tasks/active/dhva-fermi-surface/` | T-1563 | 4034278 | v1 (`dhva-fermi-surface-20261110.zip`, "
       "digest `87064573…ca271`) | REWORK: v1 quick check passed (job 21089, 09:32; 31 pass, 0 fail, 3 N/A, `novel` deferred; "
       "5 extra pass); pass@3 **3 of 3** TOO EASY (09:52, Sol 6.1), sent back (SBQ). Both cards marked seen 10:44. Every trap "
       "fell to a global Lifshitz-Kosevich fit | 2026-11-11 11:15 | Build v2: the internal field B = mu0 H + mu0 (1-N) M of a "
       "strongly paramagnetic sample (scale of every frequency, magnetic interaction); regenerate, Upload the fix, restart "
       "the poller | [log](dhva-fermi-surface.md) |")
p = Path("logs/STATUS.md")
t = p.read_text(encoding="utf-8")
assert t.count("\nArchived:") == 1
t = t.replace("\nArchived:", "\n" + row + "\nArchived:", 1)
p.write_text(t, encoding="utf-8", newline="\n")

ev = ("- **2026-11-11 11:15**: v1 quick check passed (job 21089, 09:32), pass@3 **3 of 3** (09:52, Sol 6.1), sent back.\n"
      "  Every trap fell to a direct least-squares fit of the Lifshitz-Kosevich model (gamma by its survival at 6.5 K and\n"
      "  above, delta from the residual, spin zero and half-frequency readings tested). v2 plan: the electrons feel\n"
      "  B = mu0 H + mu0 (1 - N) M; a strongly paramagnetic sample makes every frequency read against the applied field\n"
      "  about 2% low, and its oscillatory magnetization adds magnetic interaction (harmonics, combination frequencies).\n")
p = Path("work/physics-task-state.md")
t = p.read_text(encoding="utf-8")
last = t.rfind("\n# ")
assert t[last:].startswith("\n# dhva-fermi-surface"), t[last:last+40]
if not t.endswith("\n"):
    t += "\n"
t += ev
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
