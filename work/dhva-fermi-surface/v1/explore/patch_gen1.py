from pathlib import Path
p = Path("tasks/active/dhva-fermi-surface/tests/generate.py")
s = p.read_text(encoding="utf-8")
old1 = '''    peaks = S.inventory(sweeps, (S.W_SEARCH,))
    orbits, _ = S.classify(peaks)
    out.append("   the inventory from one window, 6-35 T: orbits %s; no peak within 0.5%% of %.2f T, so that orbit is "
               "never reported" % (", ".join("%.1f" % o["f"] for o in orbits), max(t["frequency_T"] for t in truth)))
'''
new1 = '''    peaks = S.inventory(sweeps, (S.W_SEARCH,))
    orbits, _ = S.classify(peaks)
    out.append("   the inventory from one window, 6-35 T: orbits %s; no peak at all within 0.5%% of %s"
               % (", ".join("%.1f" % o["f"] for o in orbits),
                  ", ".join("%.2f T" % t["frequency_T"] for t in truth
                            if not any(abs(p["f"] - t["frequency_T"]) <= FREQ_BAND * t["frequency_T"] for p in peaks))))
'''
assert s.count(old1) == 1
s = s.replace(old1, new1)
old2 = "        k = min(range(len(freqs)), key=lambda k: abs(freqs[k] - 927.6))\n"
new2 = "        k = min(range(len(freqs)), key=lambda k: abs(freqs[k] - next(o[1] for o in ORBITS if o[0] == \"gamma\")))\n"
assert s.count(old2) == 1
s = s.replace(old2, new2)
p.write_text(s, encoding="utf-8", newline="\n")
import ast; ast.parse(s); print("ok")
