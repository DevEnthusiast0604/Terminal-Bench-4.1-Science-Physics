"""v14: the generator's final check names what it found outside a tolerance. Exact-match replacement in
tests/generate.py; run from the folder root."""
PATH = "tasks/active/gamma-decay-scheme/tests/generate.py"
s = open(PATH, encoding="utf-8", newline="").read()
old = """    assert e_dev <= 0.5 and i_dev <= 0.25 and hl <= 0.02 and iso <= 0.08 and iso_e <= 0.5 and gap <= 0.5
"""
new = """    worst = sorted(rows, key=lambda tr: -abs(tr[1]["relative_intensity"] - tr[0]["relative_intensity"])
                   / tr[0]["relative_intensity"])[:3]
    assert e_dev <= 0.5 and i_dev <= 0.25 and hl <= 0.02 and iso <= 0.08 and iso_e <= 0.5 and gap <= 0.5, (
        "energy %.3f keV, intensity %.3f, parent %.4f, isomer %.4f and %.3f keV, gap %.3f keV; largest intensity "
        "differences: %s" % (e_dev, i_dev, hl, iso, iso_e, gap, "; ".join(
            "%.2f keV %.3f for %.3f" % (t["energy_keV"], r["relative_intensity"], t["relative_intensity"]) for t, r in worst)))
"""
assert s.count(old) == 1
s = s.replace(old, new)
assert "\r" not in s
open(PATH, "w", encoding="utf-8", newline="").write(s)
print("generate.py edited")
