"""v9: the reference's doublet member energies no longer rest on one gate.

In the v9 data the 898.3 keV gate (fed through the isomer, few prompt counts) put the 647 keV doublet's centroid at
646.69 keV, 0.2 keV under every other gate that sees the lower member alone. The old rule took the lower member as the
mean of the gates within 0.15 keV of the lowest centroid, which was that gate alone, so the span grew and the gates of
551.8 and 1011.4 keV (centroids 647.37 and 647.39, both members) became undecided: the placement search then admitted
two more schemes with 16 levels. The new rule takes the gates that agree, within two standard errors, with the lowest
(highest) centroid that is itself certain to two standard errors.
Run from the folder root."""
from pathlib import Path

T = Path("tasks/active/gamma-decay-scheme")


def edit(path, pairs):
    p = T / path
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        n = s.count(old)
        assert n == 1, (path, n, old[:80])
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="\n")
    print("edited", p)


edit("solution/solve.py", [
    ('        if len(firm) >= 2:\n'
     '            cmin = min(r["centroid"] for r in firm)\n'
     '            cmax = max(r["centroid"] for r in firm)\n'
     '            def mean_of(rows):\n'
     '                w = np.array([1.0 / r["err"] ** 2 for r in rows])\n'
     '                return float(np.sum(w * np.array([r["centroid"] for r in rows])) / w.sum())\n'
     '            low = mean_of([r for r in firm if r["centroid"] <= cmin + 0.15])\n'
     '            high = mean_of([r for r in firm if r["centroid"] >= cmax - 0.15])\n',
     '        if len(firm) >= 2:\n'
     '            def mean_of(rows):\n'
     '                w = np.array([1.0 / r["err"] ** 2 for r in rows])\n'
     '                return float(np.sum(w * np.array([r["centroid"] for r in rows])) / w.sum())\n'
     '            # A member\'s energy is the mean of the gates that see it alone: those whose centroid is, within two\n'
     '            # standard errors, as low (as high) as the lowest (highest) centroid that holds to two standard errors.\n'
     '            # One gate that strays cannot then set a member by itself.\n'
     '            cmin = min(r["centroid"] + 2.0 * r["err"] for r in firm)\n'
     '            cmax = max(r["centroid"] - 2.0 * r["err"] for r in firm)\n'
     '            low = mean_of([r for r in firm if r["centroid"] - 2.0 * r["err"] <= cmin])\n'
     '            high = mean_of([r for r in firm if r["centroid"] + 2.0 * r["err"] >= cmax])\n'),
])
