from pathlib import Path
p = Path("tasks/active/dhva-fermi-surface/tests/generate.py")
s = p.read_text(encoding="utf-8")
old = '''            "   Spectral peaks F (signal/noise, noise the local median amplitude), from the reference's peak finder:"]
'''
new = '''            "   Fourier resolution 1/(1/B_low - 1/B_high): whole sweep 5-35 T %.2f T, 6-35 T %.2f T, 14-35 T %.2f T, "
            "22-35 T %.2f T" % tuple(1.0 / (1.0 / a - 1.0 / b) for a, b in ((5, 35), (6, 35), (14, 35), (22, 35))),
            "   Spectral peaks F (signal/noise, noise the local median amplitude), from the reference's peak finder:"]
'''
assert s.count(old) == 1
s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline="\n".encode().decode("unicode_escape"))
import ast; ast.parse(s); print("ok")
