import textwrap
from pathlib import Path
p = Path("tasks/active/dhva-fermi-surface/README.md")
lines = p.read_text(encoding="utf-8").split("\n")
i = next(k for k, l in enumerate(lines) if l.startswith("- **15% on masses.**"))
j = i + 1
while j < len(lines) and lines[j].startswith("  "):
    j += 1
para = " ".join(l.strip() for l in lines[i:j])
assert para.startswith("- ")
wrapped = textwrap.wrap(para[2:], width=118, break_on_hyphens=False, break_long_words=False)
new = ["- " + wrapped[0]] + ["  " + w for w in wrapped[1:]]
lines[i:j] = new
p.write_text("\n".join(lines), encoding="utf-8", newline="\n")
print("\n".join(new))
print(max(len(l) for l in lines))
