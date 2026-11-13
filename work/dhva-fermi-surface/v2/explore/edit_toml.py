from pathlib import Path
p = Path("tasks/active/dhva-fermi-surface/task.toml")
t = p.read_text(encoding="utf-8")
old_k = 'keywords = ["de-haas-van-alphen", "quantum-oscillations", "fermi-surface", "lifshitz-kosevich", "effective-mass", "fourier-analysis", "condensed-matter"]'
new_k = 'keywords = ["de-haas-van-alphen", "quantum-oscillations", "fermi-surface", "lifshitz-kosevich", "effective-mass", "magnetic-interaction", "fourier-analysis", "condensed-matter"]'
old_t = 'tags = ["quantum-oscillations", "fermi-surface", "lifshitz-kosevich", "effective-mass", "fourier-analysis", "condensed-matter"]'
new_t = 'tags = ["quantum-oscillations", "fermi-surface", "lifshitz-kosevich", "effective-mass", "magnetic-interaction", "fourier-analysis", "condensed-matter"]'
assert t.count(old_k) == 1 and t.count(old_t) == 1
t = t.replace(old_k, new_k).replace(old_t, new_t)
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
