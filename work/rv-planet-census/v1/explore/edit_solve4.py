"""solve.py: start each transit fit from a mid-time found on a one-minute grid (run 3's fit of b stayed at the box
search's mid-time, 11 minutes late, and traded that for a high impact parameter: R +9.3%; probe_b3.out)."""
from pathlib import Path

p = Path("tasks/active/rv-planet-census/solution/solve.py")
s = p.read_bytes().decode("utf-8")


def sub(old, new):
    global s
    assert s.count(old) == 1, old[:90]
    s = s.replace(old, new)


sub('''    sm = np.convolve(yy, np.ones(15) / 15, "same")
    k0 = math.sqrt(max(1e-6, -float(np.min(sm))))
    lo, hi, scale = [0.002, -0.05], [0.3, 0.05], [0.005, 0.002]
''', '''    sm = np.convolve(yy, np.ones(15) / 15, "same")
    k0 = math.sqrt(max(1e-6, -float(np.min(sm))))

    def start(bq):
        """The mid-time offset on a one-minute grid, and the radius ratio that goes with it, at impact parameter bq:
        a box search's mid-time can be off by several minutes, enough for a fit to settle on a wrong chord."""
        best = (math.inf, 0.0, k0)
        for dt in np.arange(-0.04, 0.04 + 1e-9, 1.0 / 1440):
            m = transit_model(tt, P, tc0 + dt, e, w, aR, k0, bq, star["u1"], star["u2"])
            if np.any(np.isnan(m)) or not np.any(m > 0):
                continue
            A = max(-float(np.dot(yy, m) / np.dot(m, m)), 1e-4)
            c = float(np.sum((yy + A * m) ** 2))
            if c < best[0]:
                best = (c, float(dt), min(0.29, max(0.003, k0 * math.sqrt(A))))
        return best[1], best[2]

    lo, hi, scale = [0.002, -0.05], [0.3, 0.05], [0.005, 0.002]
''')

sub('''    for b0 in ((0.1, 0.4, 0.7) if fix_b is None else (None,)):
        x0 = [k0] + ([b0] if fix_b is None else []) + [0.0] + ([0.0] if free_P else [])
''', '''    for b0 in ((0.1, 0.4, 0.7) if fix_b is None else (None,)):
        dt0, ks = start(fix_b if b0 is None else b0)
        x0 = [ks] + ([b0] if fix_b is None else []) + [dt0] + ([0.0] if free_P else [])
''')

p.write_bytes(s.encode("utf-8"))
print("solve.py edited")
