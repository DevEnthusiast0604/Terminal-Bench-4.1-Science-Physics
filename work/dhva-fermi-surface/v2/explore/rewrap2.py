import textwrap
from pathlib import Path
p = Path("tasks/active/dhva-fermi-surface/README.md")
t = p.read_text(encoding="utf-8")
old = "It reads only the files there and works as a\nquantum-oscillation analyst would:"
new = ("It reads only the sweep files, with the bar's\ndimensions from NOTES.md written into it as constants, "
       "and works as a quantum-oscillation analyst would:")
assert t.count(old) == 1
t = t.replace(old, new)
lines = t.split("\n")

def rewrap(start, first, rest):
    i = next(k for k, l in enumerate(lines) if l.startswith(start))
    j = i + 1
    while j < len(lines) and lines[j].startswith(rest) and not lines[j].startswith(first):
        j += 1
    para = " ".join(l.strip() for l in lines[i:j])[len(first):]
    w = textwrap.wrap(para, width=120 - len(first), break_on_hyphens=False, break_long_words=False)
    lines[i:j] = [first + w[0]] + [rest + x for x in w[1:]]

rewrap("- **An orbit under a harmonic.**", "- ", "  ")
rewrap("`solution/solve.sh` runs", "", "")
p.write_text("\n".join(lines), encoding="utf-8", newline="\n")
long = [(k + 1, len(l)) for k, l in enumerate(lines) if len(l) > 120 and not l.startswith("|")]
print("long lines:", long)
