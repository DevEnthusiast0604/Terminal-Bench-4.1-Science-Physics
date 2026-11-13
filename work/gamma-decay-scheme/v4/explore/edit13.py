"""v4 (2026-11-09): two real transitions on peaks of another origin. M -> J (403.4 keV) lies on the daughter's own
403.4 keV line and M -> H (511.0 keV) on the annihilation line; all three v3 attempts set both peaks aside by energy.
Edits tests/generate.py (scheme, annihilation, checks) and solution/solve.py (annihilation split, shared-peak
coincidences). Every old string must occur exactly once. Run from the folder root."""
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


GEN = [
    ('# "g" is the ground state. A transition under THRESHOLD_KEV is emitted but never detected.\n',
     '# "g" is the ground state. A transition under THRESHOLD_KEV is emitted but never detected.\n'
     '# M -> J (403.4 keV) lies on the daughter\'s own 403.4 keV line, and M -> H (511.0 keV) on the annihilation line.\n'),
    ('    "M": (3092.6, 9.0, [("A", 45), ("Da", 20), ("I", 20), ("L", 15)]),\n',
     '    "M": (3092.6, 12.0, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("J", 36), ("H", 6)]),\n'),
    ("    parent = parent + N_PARENT * 2.0e-4 * peak(EDGES_RUN, 511.0, 1.3)\n",
     "    parent = parent + N_PARENT * 3.0e-4 * peak(EDGES_RUN, 511.0, 1.3)\n"),
    ('    out += ["[peak shared with the daughter\'s own decay]"]\n',
     '    out += ["[peaks shared with the daughter\'s own decay]"]\n'),
    ('    t = diag["isomer_time_spectrum"]\n    out += ["", "[isomer]",',
     '    s = diag["annihilation_split"]\n'
     '    near = min(expected["transitions"], key=lambda t: abs(t["energy_keV"] - 511.0))\n'
     '    out += ["", "[the peak at 511 keV: annihilation radiation and a line]",\n'
     '            "background run: the annihilation peak alone, sigma %.2f keV; a line at 511 keV has sigma %.2f keV"\n'
     '            % (s["sigma_broad"], s["sigma_line"]),\n'
     '            "production singles with both shapes: broad part %.0f +- %.0f counts, narrow part %.0f +- %.0f counts at %.2f keV"\n'
     '            % (s["broad"], s["broad_err"], s["narrow"], s["narrow_err"], s["E"]),\n'
     '            "the narrow part\'s share with the parent\'s time profile %.2f; I of the narrow part %.2f, scheme %.2f"\n'
     '            % (s["parent_share"], s["I"], near["relative_intensity"])]\n'
     '    out += ["", "[lines on shared peaks: net prompt coincidences above 5 sigma with the other lines, random pairs removed]"]\n'
     '    for g in diag["gates_of_shared_peaks"]:\n'
     '        seen = sorted((e, n) for e, n, sd in g["partners"] if n > 5.0 * sd)\n'
     '        out.append("%.1f keV: %s" % (g["E"], ", ".join("%.1f (%.0f)" % (e, n) for e, n in seen)))\n'
     '    t = diag["isomer_time_spectrum"]\n    out += ["", "[isomer]",'),
]

SPLIT = '''

def annihilation_split(data, peaks, t_parent):
    """The production peak at 511 keV as annihilation radiation plus a γ-ray line at the same energy.

    The motion of the annihilating pair widens annihilation radiation beyond the detector's resolution. The background
    run holds that peak alone and gives its shape; a line has the width of the room lines. The narrow part's counts per
    time bin then say whose it is. When it is the parent's, the peak's entry becomes that line."""
    hit = [p for p in peaks.items if abs(p["E"] - 511.0) < 2.5]
    if not hit:
        return None
    p = hit[0]
    bg = fit_cluster(spectrum(data / "background.txt"), peaks.edges, [511.0], 1.2, pad=12.0)
    c_b, s_b = float(bg["c"][0]), float(bg["s"])
    s_n = peaks.fwhm(511.0) / 2.3548
    lo = max(int(np.searchsorted(peaks.edges, 511.0 - 14.0)) - 1, 0)
    hi = int(np.searchsorted(peaks.edges, 511.0 + 14.0))
    ed = peaks.edges[lo:hi + 1]
    mid = 0.5 * (ed[:-1] + ed[1:])
    t = (mid - mid.mean()) / max(mid.max() - mid.min(), 1e-9)
    yy = peaks.total[lo:hi].astype(float)
    w = 1.0 / np.sqrt(np.maximum(yy, 1.0))

    def design(c):
        return np.column_stack([binned_gauss(ed, c, s_n), binned_gauss(ed, c_b, s_b), np.ones_like(mid), t])

    def resid(th):
        d = design(th[0])
        beta = np.linalg.lstsq(d * w[:, None], yy * w, rcond=None)[0]
        return (yy - d @ beta) * w

    sol = least_squares(resid, [511.0], bounds=([509.5], [512.5]))
    c_n = float(sol.x[0])
    d = design(c_n)
    a = d * w[:, None]
    beta = np.linalg.lstsq(a, yy * w, rcond=None)[0]
    chi2 = float(np.sum(sol.fun ** 2)) / max(len(yy) - 5, 1)
    cov = np.linalg.pinv(a.T @ a) * max(chi2, 1.0)
    c_err = math.sqrt(max(float(np.linalg.pinv(sol.jac.T @ sol.jac)[0, 0]) * max(chi2, 1.0), 0.0))
    # The narrow part in each time bin, with both shapes held fixed.
    curve, cerr = np.zeros(N_BINS), np.zeros(N_BINS)
    for b in range(N_BINS):
        y = peaks.bins[lo:hi, b].astype(float)
        wb = 1.0 / np.sqrt(np.maximum(y, 1.0))
        ab = d * wb[:, None]
        curve[b] = np.linalg.lstsq(ab, y * wb, rcond=None)[0][0]
        cerr[b] = math.sqrt(max(float(np.linalg.pinv(ab.T @ ab)[0, 0]), 1.0))
    t_d = DIAG.get("daughter_half_life_s")
    shapes = cycle_shapes(t_parent, t_d)
    names = ["parent", "daughter", "ramp", "flat"] if t_d else ["parent", "ramp", "flat"]
    m = np.column_stack([shapes[n] for n in names]) / cerr[:, None]
    coef = nnls(m, curve / cerr)[0]
    pcov = np.linalg.pinv(m.T @ m)
    split = {"E": c_n, "E_err": c_err, "sigma_broad": s_b, "sigma_line": s_n, "narrow": float(beta[0]),
             "narrow_err": float(math.sqrt(max(cov[0, 0], 0.0))), "broad": float(beta[1]),
             "broad_err": float(math.sqrt(max(cov[1, 1], 0.0))), "parent_area": float(coef[0]),
             "parent_err": float(math.sqrt(max(pcov[0, 0], 0.0))),
             "parent_share": float(coef[0] / max(float(coef.sum()), 1e-9)), "I": 0.0}
    DIAG["annihilation_split"] = split
    if split["narrow"] > 6.0 * split["narrow_err"] and split["parent_area"] > 6.0 * split["parent_err"]:
        p.update({"E": c_n, "err": max(c_err, 0.02), "s": s_n, "width": 1.0, "area": split["narrow"],
                  "area_err": split["narrow_err"], "group": [c_n], "parent_area": split["parent_area"],
                  "parent_err": split["parent_err"], "shares": {"parent": split["parent_area"]},
                  "annihilation_line": True})
    return split


def half_life_of(items, off):'''

SOLVE = [
    ("whose centroid moves with the gate). The placement is an exhaustive search over level schemes that agree with every\n"
     "measured coincidence and absence of coincidence, the energy sums and the intensity balance.\n",
     "whose centroid moves with the gate). A peak of another origin can hold a transition too: the annihilation peak is split\n"
     "into the broad shape the background run gives it and a line, and a line of another activity keeps its parent's share.\n"
     "The placement is an exhaustive search over level schemes that agree with every measured coincidence and absence of\n"
     "coincidence, the energy sums and the intensity balance.\n"),
    ("\n\ndef half_life_of(items, off):", SPLIT),
    ('        if abs(p["E"] - 511.0) < 2.5:\n            excluded.append(("annihilation", p["E"], p["I"]))\n',
     '        if abs(p["E"] - 511.0) < 2.5 and not p.get("annihilation_line"):\n'
     '            excluded.append(("annihilation", p["E"], p["I"]))\n'),
    ("            else:\n                f = None\n"
     "            # For a member of a doublet only a centroid in a gate says which of the two a partner goes with.\n",
     "            else:\n                f = None\n"
     "            # When both peaks also hold another activity, their coincidence can be that activity's own cascade.\n"
     '            if f == 1 and a.get("share", 1.0) < 0.9 and b.get("share", 1.0) < 0.9:\n'
     "                f = None\n"
     "            # For a member of a doublet only a centroid in a gate says which of the two a partner goes with.\n"),
    ("    t_parent = separate_activities(peaks)\n",
     "    t_parent = separate_activities(peaks)\n    annihilation_split(data, peaks, t_parent)\n"),
    ("    lines = classify(peaks, coin, eff, ratios)\n",
     "    lines = classify(peaks, coin, eff, ratios)\n"
     "    for l in lines:\n"
     '        if l.get("annihilation_line"):\n'
     '            DIAG["annihilation_split"]["I"] = l["I"]\n'),
    ("    flags, strength, ceiling, delayed_pairs = coincidence_flags(lines, coin, eff, k_scale)\n",
     "    flags, strength, ceiling, delayed_pairs = coincidence_flags(lines, coin, eff, k_scale)\n"
     '    DIAG["gates_of_shared_peaks"] = []\n'
     "    for l in lines:\n"
     '        if l.get("share", 1.0) < 0.9 or l.get("annihilation_line"):\n'
     "            rows = []\n"
     "            for o in lines:\n"
     '                if o["peak"] != l["peak"]:\n'
     '                    n, var = coin.net(l["peak"], o["peak"])\n'
     '                    rows.append((o["E"], n, math.sqrt(max(var, 1.0))))\n'
     '            DIAG["gates_of_shared_peaks"].append({"E": l["E"], "partners": rows})\n'),
    ('                   if lines[i]["peak"] != lines[j]["peak"])\n',
     '                   if lines[i]["peak"] != lines[j]["peak"]\n'
     '                   and not (lines[i].get("share", 1.0) < 0.9 and lines[j].get("share", 1.0) < 0.9))\n'),
]

edit("tests/generate.py", GEN)
edit("solution/solve.py", SOLVE)
