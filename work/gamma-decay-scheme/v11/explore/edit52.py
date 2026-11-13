"""v11: tests/generate.py writes the reference's split of a doublet with a weak member into tests/checks.txt, under
[peaks that are two transitions]. Every replacement must match once."""
from pathlib import Path

P = Path("tasks/active/gamma-decay-scheme/tests/generate.py")
s = P.read_bytes().decode("utf-8")
assert "\r" not in s

OLD = '''    out += ["other candidate lines: width/resolution from %.2f to %.2f, largest self-coincidence strength %.3f"
            % (min(widths), max(widths), max(abs(r["self_strength"]) for r in diag["doublet_tests"] if not r["moved"])), ""]
'''
NEW = '''    out += ["other candidate lines: width/resolution from %.2f to %.2f, largest self-coincidence strength %.3f"
            % (min(widths), max(widths), max(abs(r["self_strength"]) for r in diag["doublet_tests"] if not r["moved"]))]
    for m in diag["moved_splits"]:
        if m["share_low"] is None:
            continue
        test = next(r for r in diag["doublet_tests"] if abs(r["E"] - m["E"]) < 0.01)
        lo, hi = m["energies"]["low"], m["energies"]["high"]
        t_lo = min(expected["transitions"], key=lambda t: abs(t["energy_keV"] - lo))
        t_hi = min(expected["transitions"], key=lambda t: abs(t["energy_keV"] - hi))
        out.append("%.2f keV: the lower member's share of the peak %.3f from its singles centroid, %.3f from the gates "
                   "on the lines below each member (%s keV for %.2f keV, %s keV for %.2f keV); I %.2f and %.2f, scheme "
                   "%.2f and %.2f"
                   % (m["E"], test["share_by_centroid"], m["share_low"],
                      " ".join("%.1f" % g for g in m["gates"]["low"]), lo,
                      " ".join("%.1f" % g for g in m["gates"]["high"]), hi,
                      m["after"]["low"], m["after"]["high"], t_lo["relative_intensity"], t_hi["relative_intensity"]))
    out += [""]
'''
n = s.count(OLD)
assert n == 1, n
s = s.replace(OLD, NEW)
P.write_bytes(s.encode("utf-8"))
print("generate.py: checks section added")
