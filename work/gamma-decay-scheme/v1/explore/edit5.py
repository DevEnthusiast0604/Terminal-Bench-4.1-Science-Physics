from pathlib import Path
sol = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
t = sol.read_text(encoding="utf-8")

# 1. Doublet split: by shape before the search when the members do not share a cascade.
old = """        for name, value in (("low", low), ("high", high)):
            q = dict(p)
            q["peak"] = e
            q["member"] = name
            q["E"] = value
            q["err"] = 0.08
            q["sees"] = sees
            q["I"] = 0.5 * p["I"]
            q["self"] = self_flag
            out.append(q)
"""
new = """        fraction = 0.5 if self_flag else shape_split(coin.peaks, e, low, high)
        for name, value, share in (("low", low, fraction), ("high", high, 1.0 - fraction)):
            q = dict(p)
            q["peak"] = e
            q["member"] = name
            q["E"] = value
            q["err"] = 0.08
            q["sees"] = sees
            q["I"] = share * p["I"]
            q["self"] = self_flag
            q["self_q"] = self_n / (k_scale * float(eff(e)) ** 2)
            out.append(q)
"""
assert old in t
t = t.replace(old, new)

old = 'def split_doublets(lines, coin, eff):\n'
new = '''def shape_split(peaks, e, low, high):
    """Share of the lower member in the singles peak, from two lines of known position and width."""
    s = peaks.fwhm(e) / 2.3548
    pad = 8.0 * s
    lo = int(np.searchsorted(peaks.edges, e - pad))
    hi = int(np.searchsorted(peaks.edges, e + pad))
    ed = peaks.edges[lo:hi + 1]
    mid = 0.5 * (ed[:-1] + ed[1:])
    t = (mid - mid.mean()) / (mid.max() - mid.min())
    d = np.column_stack([binned_gauss(ed, low, s), binned_gauss(ed, high, s), np.ones_like(mid), t])
    y = peaks.total[lo:hi]
    w = 1.0 / np.sqrt(np.maximum(y, 1.0))
    beta = np.linalg.lstsq(d * w[:, None], y * w, rcond=None)[0]
    return float(beta[0] / (beta[0] + beta[1]))


def cascade_split(total, q, other):
    """Intensity of the lower member of a doublet in one cascade.

    The peak's coincidence with itself counts upper x (lower / (lower + other)), where OTHER is what the level between
    them gives off besides the lower member, and the two members add up to TOTAL.
    """
    disc = (total - q) ** 2 - 4.0 * q * other
    return 0.5 * ((total - q) + math.sqrt(max(disc, 0.0)))


def split_doublets(lines, coin, eff):
'''
assert old in t
t = t.replace(old, new)

# 2. Balance with the cascade split of the candidate scheme.
old = """        hid = {a for a, _ in hidden}
        for a in range(1, nlev):
            if a in hid:
                continue
            into = sum(lines[i]["I"] for i in range(n) if place[i][1] == a)
            outof = sum(lines[i]["I"] for i in range(n) if place[i][0] == a)
"""
new = """        hid = {a for a, _ in hidden}
        values = [l["I"] for l in lines]
        for i, l in enumerate(lines):
            if l["member"] == "low" and l["self"]:
                j = next(k for k, o in enumerate(lines) if o["peak"] == l["peak"] and k != i)
                lower, top = (i, j) if place[i][0] == place[j][1] else (j, i)
                other = sum(values[k] for k in range(n) if place[k][0] == place[lower][0] and k != lower)
                values[lower] = cascade_split(values[i] + values[j], l["self_q"], other)
                values[top] = 2.0 * l["I"] - values[lower]
        for a in range(1, nlev):
            if a in hid:
                continue
            into = sum(values[i] for i in range(n) if place[i][1] == a)
            outof = sum(values[i] for i in range(n) if place[i][0] == a)
"""
assert old in t
t = t.replace(old, new)

# 3. split_intensities only finishes the cascade doublets now.
a = t.index("def split_intensities(lines, sol, coin, peaks, k_scale, eff, scale):")
b = t.index("def isomer_half_life(lines, sol, coin, delayed_pairs):")
new = '''def split_intensities(lines, sol):
    """The two members of a doublet in one cascade, now that the scheme says which is the upper one."""
    _, place, _ = sol
    for i, l in enumerate(lines):
        if l["member"] == "low" and l["self"]:
            j = next(k for k, o in enumerate(lines) if o["peak"] == l["peak"] and k != i)
            lower, top = (i, j) if place[i][0] == place[j][1] else (j, i)
            total = lines[i]["I"] + lines[j]["I"]
            other = sum(o["I"] for k, o in enumerate(lines) if place[k][0] == place[lower][0] and k != lower)
            lines[lower]["I"] = cascade_split(total, l["self_q"], other)
            lines[top]["I"] = total - lines[lower]["I"]
    return lines


'''
t = t[:a] + new + t[b:]
old = "    lines = split_intensities(lines, sol, coin, peaks, k_scale, eff, scale)\n"
new = "    lines = split_intensities(lines, sol)\n"
assert old in t
t = t.replace(old, new)
sol.write_text(t, encoding="utf-8", newline="\n")
