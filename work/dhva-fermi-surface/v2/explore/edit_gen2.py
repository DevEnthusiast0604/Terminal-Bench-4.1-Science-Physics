from pathlib import Path
import ast
p = Path("tasks/active/dhva-fermi-surface/tests/generate.py")
t = p.read_text(encoding="utf-8")

old_label = t[t.index("def label_peak(f, width, scale):"):t.index("def main():")]
new_label = '''def label_peak(f, width, scale):
    """What a peak of a spectrum taken against the applied field can be, with every orbit's frequency divided by
    `scale` (the window's stretch): an orbit, a harmonic p x orbit, or a combination p x orbit +- r x alpha (magnetic
    interaction). Of the readings within `width`, the simplest first (orbits and harmonics before combinations), and a
    second one when there is one."""
    names = {o[0]: o[1] / scale for o in ORBITS}
    found = []
    for name, F in names.items():
        for p in range(1, P_MAX + 1):
            for r in range(-3, 4):
                if name == "alpha" and r:
                    continue
                g = p * F + r * names["alpha"]
                d = abs(f - g)
                if g > 0 and d < width:
                    lab = (name if p == 1 else "%d x %s" % (p, name)) + ("" if r == 0 else " %s %s" % (
                        "+" if r > 0 else "-", "alpha" if abs(r) == 1 else "%d x alpha" % abs(r)))
                    found.append(((abs(r), p > 1, d), lab))
    found.sort()
    return "?" if not found else " or ".join(lab for _, lab in found[:2])


'''
t = t.replace(old_label, new_label)

old = '''    out.append("   the sample's steady moment %.0f B %+.2f B^3 units (B in T), the same at every temperature, and the "
               "oscillations' own" % STEADY)'''
new = '''    out.append("   the sample's moment: a steady part %.0f B %+.2f B^3 units (B in T), the same at every temperature, plus "
               "the oscillations;" % STEADY)
    out.append("   B is solved from B = mu0 H + K m(B) at every reading, so the oscillations' own magnetization feeds back")'''
assert t.count(old) == 1
t = t.replace(old, new)

old = '''        res, dg, el = results[label]
        ok, lines = judge(res, truth)
        out.append("   %s: %s" % (what, "AGREES" if ok else "DISAGREES"))
        out += ["   " + ln for ln in lines]'''
new = '''        res, dg, el = results[label]
        ok, lines = judge(res, truth)
        out.append("   %s: %s" % (what, "AGREES" if ok else "DISAGREES"))
        out += ["   " + ln for ln in lines]
        named = []
        for r in sorted(res, key=lambda r: r["frequency_T"]):
            f = r["frequency_T"]
            o = min(ORBITS, key=lambda o: abs(f * stretch(S.W_MASS) / o[1] - 1.0))
            if abs(f * stretch(S.W_MASS) / o[1] - 1.0) <= FREQ_BAND:
                named.append("%.2f (%s, %.2f%% below its F)" % (f, o[0], 100 * (1.0 - f / o[1])))
            else:
                named.append("%.2f (%s)" % (f, label_peak(f, 0.25 * S.lobe(S.W_MASS), stretch(S.W_MASS))))
        out.append("      its entries, named with the stretch over 14-35 T: %s" % ", ".join(named))'''
assert t.count(old) == 1
t = t.replace(old, new)
ast.parse(t)
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
