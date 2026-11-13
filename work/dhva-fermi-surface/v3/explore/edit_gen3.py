from pathlib import Path
import ast
p = Path("tasks/active/dhva-fermi-surface/tests/generate.py")
t = p.read_text(encoding="utf-8")

def sub(old, new, count=1):
    global t
    assert t.count(old) == count, (t.count(old), old[:60])
    t = t.replace(old, new)

sub('    ("delta", 7415.00, 3.350, 0.80, 1.90, 2.0, -1),', '    ("delta", 7300.00, 3.350, 0.80, 1.90, 2.0, -1),')

sub('''def coincidences(limit=40.0, p_max=6):
    rows = []''', '''def coincidences(limit=40.0, p_max=P_MAX):
    rows = []''')

sub('''def audit():''', '''def combinations_near(name, rel=0.001, mass_rel=0.15, n_max=10):
    """Integer combinations sum n_i F_i of the other orbits (sum |n_i| <= n_max) within `rel` of orbit `name`'s
    frequency: how many, how many also within `mass_rel` of its mass (a combination's thermal damping is that of the
    summed mass sum |n_i| m_i), and the lightest of them. A peak that such a combination matched in frequency and mass
    could be read as a composite rather than an orbit; none should."""
    target = next(o for o in ORBITS if o[0] == name)
    others = [o for o in ORBITS if o[0] != name]
    grids = np.meshgrid(*[np.arange(-n_max, n_max + 1)] * len(others), indexing="ij")
    n = np.stack([g.ravel() for g in grids], axis=1)
    n = n[(np.abs(n).sum(axis=1) <= n_max) & (np.abs(n).sum(axis=1) > 0)]
    F = n @ np.array([o[1] for o in others])
    m = np.abs(n) @ np.array([o[2] for o in others])
    near = np.abs(F / target[1] - 1.0) < rel
    both = near & (np.abs(m / target[2] - 1.0) < mass_rel)
    return int(near.sum()), int(both.sum()), (float(m[near].min()) if near.any() else float("nan"))


def audit():''')

sub('''    print("near-coincidences (|dF| < 40 T, p <= 6):", coincidences() or "none")''',
    '''    print("near-coincidences (|dF| < 40 T, p <= %d):" % P_MAX, coincidences() or "none")
    print("combinations of the other orbits near delta (count, also within 15%% in mass, lightest m):",
          combinations_near("delta"))''')

sub('''    out.append("   frequencies within 40 T of a harmonic p <= 6 of another orbit: %s"
               % ("; ".join(coincidences()) or "none"))''',
    '''    out.append("   frequencies within 40 T of a harmonic p <= %d of another orbit: %s"
               % (P_MAX, "; ".join(coincidences()) or "none"))
    dname, dF = ORBITS[-1][0], ORBITS[-1][1]
    hp = min(((p * o[1], p, o[0]) for o in ORBITS if o[0] != dname for p in range(1, P_MAX + 1)),
             key=lambda h: abs(h[0] - dF))
    cn, cb, cl = combinations_near(dname)
    out.append("   %s: the nearest harmonic of another orbit is %d x %s = %.1f T (%+.1f T); integer combinations of the "
               "other orbits" % (dname, hp[1], hp[2], hp[0], hp[0] - dF))
    out.append("   (sum |n| <= 10) within 0.1%% of its frequency: %d, of them within 15%% of its mass: %d (the lightest "
               "%.2f against %.2f)" % (cn, cb, cl, ORBITS[-1][2]))''')

ast.parse(t)
p.write_text(t, encoding="utf-8", newline="\n")
print("ok")
