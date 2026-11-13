"""v11 edit 2 of 2: solution/solve.py. A doublet whose members the gates tell apart (a moved doublet) can have one
member far weaker than the other. Then (1) its first share comes from the singles centroid, not from a fit of two
shapes; (2) a gate whose centroid sits on the strong member says nothing about the weak one, whose small share hardly
moves it; (3) once the scheme is known, the shares come from the gates on the lines below each member.
Every replacement must match once."""
from pathlib import Path

P = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
s = P.read_bytes().decode("utf-8")
assert "\r" not in s

OLD1 = '''        fraction = 0.5 if self_flag else shape_split(coin.peaks, e, low, high)
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
'''
NEW1 = '''        fraction, weak, by_centroid = 0.5, None, None
        if not self_flag:
            # The singles centroid lies between the members at their shares. A member under a quarter of the peak
            # hardly changes its shape, so a fit of two shapes cannot hold it; the centroid gives its first share, and
            # the gates below each member give the share once the scheme is known (split_moved).
            by_centroid = (high - e) / span
            if by_centroid < 0.25:
                weak, fraction = "low", max(by_centroid, 0.02)
            elif by_centroid > 0.75:
                weak, fraction = "high", min(by_centroid, 0.98)
            else:
                fraction = shape_split(coin.peaks, e, low, high)
        report[-1]["share_by_centroid"] = by_centroid
        report[-1]["weak"] = weak
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
            q["weak"] = name == weak
            out.append(q)
'''

OLD2 = '''            # For a member of a doublet only a centroid in a gate says which of the two a partner goes with.
            for x, y in ((a, b), (b, a)):
                if x["member"] and f == 1:
                    seen = x["sees"].get(y["peak"])
                    f = None if seen is None else (1 if seen in (x["member"], "both") else 0)
'''
NEW2 = '''            # For a member of a doublet only a centroid in a gate says which of the two a partner goes with. A gate
            # whose centroid sits on the strong member says nothing about a weak one: its share hardly moves it.
            for x, y in ((a, b), (b, a)):
                if x["member"] and f == 1:
                    seen = x["sees"].get(y["peak"])
                    if seen is None:
                        f = None
                    elif seen in (x["member"], "both"):
                        f = 1
                    else:
                        f = None if x.get("weak") else 0
'''

OLD3 = '''def isomer_half_life(lines, sol, coin, delayed_pairs):'''
NEW3 = '''def split_moved(lines, sol, coin, eff):
    """The members of a doublet that the gates tell apart, now that the scheme says where each one goes.

    A gate on lines below a member that sees that member alone counts I x (the share of the member's cascade that runs
    through the gate's lines) x the two efficiencies x one scale common to all pairs. The ratio of the two members'
    values sets their shares of the singles peak, and the scale drops out. Left out: gates that also lie below the
    other member, and pairs with delayed coincidences, which the isomer splits between the time windows.
    """
    levels, place, hidden = sol
    nlev = len(levels)
    out_i = {}
    for i in range(len(lines)):
        out_i.setdefault(place[i][0], []).append(i)
    hid = dict(hidden)
    order = sorted(range(nlev), key=lambda k: -levels[k])

    def flow_from(start):
        f = [0.0] * nlev
        f[start] = 1.0
        for a in order:
            if f[a] == 0.0 or a == 0:
                continue
            if a in hid:
                f[hid[a]] += f[a]
                continue
            tot = sum(lines[i]["I"] for i in out_i.get(a, []))
            for i in out_i.get(a, []):
                f[place[i][1]] += f[a] * lines[i]["I"] / tot
        return f

    pairs = {}
    for i, l in enumerate(lines):
        if l["member"] and not l["self"]:
            pairs.setdefault(l["peak"], {})[l["member"]] = i
    report = []
    for peak, pair in sorted(pairs.items()):
        if len(pair) != 2:
            continue
        flows = {name: flow_from(place[i][1]) for name, i in pair.items()}
        est = {}
        for name, i in pair.items():
            other = "high" if name == "low" else "low"
            rows = []
            for gate, seen in sorted(lines[i]["sees"].items()):
                if seen != name:
                    continue
                share, shared = 0.0, 0.0
                for k, o in enumerate(lines):
                    if o["peak"] != gate:
                        continue
                    x = place[k][0]
                    b = o["I"] / sum(lines[z]["I"] for z in out_i[x])
                    share += flows[name][x] * b
                    shared += flows[other][x] * b
                if share < 0.05 or shared > 0.0:
                    continue
                dn, dv, _, _ = coin.delayed(peak, gate)
                if abs(dn) > 5.0 * math.sqrt(max(dv, 1.0)):
                    continue
                n, var = coin.net(peak, gate)
                if n <= 5.0 * math.sqrt(max(var, 1.0)):
                    continue
                value = n / (float(eff(lines[i]["E"])) * float(eff(gate)) * share)
                rows.append((value, value * math.sqrt(var) / n, gate))
            if rows:
                w = np.array([1.0 / r[1] ** 2 for r in rows])
                v = np.array([r[0] for r in rows])
                est[name] = (float(np.sum(w * v) / w.sum()), [r[2] for r in rows])
        entry = {"E": peak, "before": {n: lines[i]["I"] for n, i in pair.items()},
                 "gates": {n: est[n][1] for n in est}, "share_low": None}
        if len(est) == 2:
            total = sum(lines[i]["I"] for i in pair.values())
            low_share = est["low"][0] / (est["low"][0] + est["high"][0])
            lines[pair["low"]]["I"] = low_share * total
            lines[pair["high"]]["I"] = (1.0 - low_share) * total
            entry["share_low"] = low_share
        entry["after"] = {n: lines[i]["I"] for n, i in pair.items()}
        entry["energies"] = {n: lines[i]["E"] for n, i in pair.items()}
        report.append(entry)
    DIAG["moved_splits"] = report
    return lines


def isomer_half_life(lines, sol, coin, delayed_pairs):'''

OLD4 = '''    lines = split_intensities(lines, sol)
    level_values = refine_levels(lines, sol)'''
NEW4 = '''    lines = split_intensities(lines, sol)
    lines = split_moved(lines, sol, coin, eff)
    level_values = refine_levels(lines, sol)'''

for old, new in ((OLD1, NEW1), (OLD2, NEW2), (OLD3, NEW3), (OLD4, NEW4)):
    n = s.count(old)
    assert n == 1, (n, old[:80])
    s = s.replace(old, new)
P.write_bytes(s.encode("utf-8"))
print("solve.py: 4 edits")
