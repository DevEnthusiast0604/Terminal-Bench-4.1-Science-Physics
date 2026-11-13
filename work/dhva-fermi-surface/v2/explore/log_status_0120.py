from pathlib import Path
p = Path("logs/STATUS.md")
t = p.read_text(encoding="utf-8")
rows = [l for l in t.split("\n") if l.startswith("| dhva-fermi-surface |")]
last = rows[-1]
row = ("| dhva-fermi-surface | `tasks/active/dhva-fermi-surface/` | T-1563 | 4034278 | v2 (`dhva-fermi-surface-20261111.zip`, "
       "digest `34941787…7604`) | PASS@3: v2's quick check passed (job 21778, card 01:13; 31 pass, 0 fail, 3 N/A, `novel` "
       "deferred; 5 extra pass); card marked seen 01:18; pass@3 running on Sol 6.1 | 2026-11-12 01:20 | Wait for pass@3 "
       "(poller T-1563); 1 or 2 of 3: P3 ID to the user for DAS 4034278; 3 of 3 or 0 of 3: see "
       "`work/dhva-fermi-surface/v3/plan.md` | [log](dhva-fermi-surface.md) |")
i = t.index(last) + len(last)
# the newest board row goes after the last row of the board table
end = t.index("\n", i) if "\n" in t[i:] else len(t)
tbl_end = i
lines = t.split("\n")
# find the board table: the contiguous block of lines starting with "|" that holds `last`
k = lines.index(last)
while k + 1 < len(lines) and lines[k + 1].startswith("|"):
    k += 1
lines.insert(k + 1, row)
p.write_text("\n".join(lines), encoding="utf-8", newline="\n")
print("ok, inserted after line", k + 1)
q = Path("work/physics-task-state.md")
s = q.read_text(encoding="utf-8").rstrip("\n")
s += ("\n- **2026-11-12 01:20**: v2 quick check passed (job 21778, 01:13 card; 31 pass, 0 fail, 3 N/A, `novel` deferred; "
      "5 extra pass); marked seen 01:18. pass@3 running on Sol 6.1.\n")
q.write_text(s, encoding="utf-8", newline="\n")
print("ok physics")
