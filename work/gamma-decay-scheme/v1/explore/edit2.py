from pathlib import Path
sol = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
t = sol.read_text(encoding="utf-8")

# coincidence_flags also returns an upper limit on each pair's strength.
old = """    flags = [[None] * n for _ in range(n)]
    strength = [[0.0] * n for _ in range(n)]
    delayed_pairs = []
"""
new = """    flags = [[None] * n for _ in range(n)]
    strength = [[0.0] * n for _ in range(n)]
    upper = [[float("inf")] * n for _ in range(n)]
    delayed_pairs = []
"""
assert old in t
t = t.replace(old, new)
old = """            strength[i][j] = strength[j][i] = tot / full
"""
new = """            strength[i][j] = strength[j][i] = tot / full
            upper[i][j] = upper[j][i] = (max(tot, 0.0) + 3.0 * sigma) / full
"""
assert old in t
t = t.replace(old, new)
old = "    return flags, strength, delayed_pairs\n"
new = "    return flags, strength, upper, delayed_pairs\n"
assert old in t
t = t.replace(old, new)
old = "    flags, strength, delayed_pairs = coincidence_flags(lines, coin, eff, k_scale)\n"
new = "    flags, strength, upper, delayed_pairs = coincidence_flags(lines, coin, eff, k_scale)\n"
assert old in t
t = t.replace(old, new)

# The search prunes on the strengths the partial scheme already predicts.
old = 'def search(lines, flags, order, max_levels, limit=2000000):\n    """Every scheme that agrees with the flags, the energy sums and an approximate intensity balance."""\n'
new = '''def search(lines, flags, upper, order, max_levels, limit=400000):
    """Every scheme that agrees with the flags, the energy sums, the measured strengths and the intensity balance.

    A line placed on a level is followed by that level's decays in proportion to their intensities. A partial scheme
    that predicts four times what the data allow for a pair can only get worse, whatever is placed later, unless the
    weaker decays still to come take over three quarters of the level.
    """
'''
assert old in t
t = t.replace(old, new)
old = """    def finish():
        nlev = len(levels)
"""
new = """    def strengths_ok():
        nlev = len(levels)
        out = [[] for _ in range(nlev)]
        total = [0.0] * nlev
        placed = [j for j in range(n) if place[j] is not None]
        for j in placed:
            out[place[j][0]].append(j)
            total[place[j][0]] += lines[j]["I"]
        flow = {}
        for a in sorted(range(nlev), key=lambda z: levels[z]):
            f = [0.0] * nlev
            f[a] = 1.0
            for j in out[a]:
                share = lines[j]["I"] / total[a]
                fy = flow[place[j][1]]
                for b in range(nlev):
                    f[b] += share * fy[b]
            flow[a] = f
        for g in placed:
            fy = flow[place[g][1]]
            ig = lines[g]["I"]
            for k in placed:
                if k == g or fy[place[k][0]] == 0.0:
                    continue
                ik = lines[k]["I"]
                frac = fy[place[k][0]] * ik / total[place[k][0]]
                if 0.25 * ig * frac / min(ig, ik) > upper[g][k]:
                    return False
        return True

    def finish():
        nlev = len(levels)
"""
assert old in t
t = t.replace(old, new)
old = """            place[i] = (x, y)
            if ok_new(i):
                step(pos + 1)
"""
new = """            place[i] = (x, y)
            if ok_new(i) and strengths_ok():
                step(pos + 1)
"""
assert old in t
t = t.replace(old, new)
old = "        solutions = search(lines, flags, order, max_levels)\n"
new = "        solutions = search(lines, flags, upper, order, max_levels)\n"
assert old in t
t = t.replace(old, new)
sol.write_text(t, encoding="utf-8", newline="\n")

st = Path("work/gamma-decay-scheme/v1/explore/stages.py")
s = st.read_text(encoding="utf-8")
s = s.replace("flags, strength, delayed = S.coincidence_flags(lines2, coin, eff, k_scale)", "flags, strength, upper, delayed = S.coincidence_flags(lines2, coin, eff, k_scale)")
s = s.replace("""    for m in range(14, 20):
        try:
            sols = S.search(lines2, flags, order, m)
        except RuntimeError as ex:
            print("max levels", m, ex)
            break
        print("max levels", m, "solutions", len(sols))
        if sols:
            for levels, place, hid in sols[:3]:
                print(sorted(round(v, 1) for v in levels), hid)
            break
""", """    import time
    for m in range(14, 19):
        t0 = time.time()
        try:
            sols = S.search(lines2, flags, upper, order, m)
        except RuntimeError as ex:
            print("max levels", m, ex, "%.1f s" % (time.time() - t0))
            break
        print("max levels", m, "solutions", len(sols), "%.1f s" % (time.time() - t0))
        for levels, place, hid in sols[:6]:
            print("   ", sorted(round(v, 1) for v in levels), hid)
""")
st.write_text(s, encoding="utf-8", newline="\n")
