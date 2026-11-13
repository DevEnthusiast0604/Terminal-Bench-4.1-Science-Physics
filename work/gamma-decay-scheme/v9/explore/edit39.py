"""v9 (v8's pass@3: 3 of 3, job 20645): the 511 keV line stays easy to notice but its intensity now needs the line
separated from the parent's own annihilation radiation.
- TARGET: M's beta feeding 11.75 -> 10.85 and its branch to H 31 -> 21, H's beta feeding 2.75 -> 3.65: the line at
  I about 3.0, feeding about a third of H; every other line keeps its intensity.
- Pair production of the parent's lines: 3.0e-4 -> 6.0e-4 detected annihilation photons per parent decay.
- write_checks records the readings a solver gets when the peak is read as one line: the whole peak, the peak less
  the background run's annihilation radiation scaled to the run, and the narrow part, measured from the shipped files.
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


edit("tests/generate.py", [
    ('# M -> H (511.0 keV) lies on the annihilation line and feeds about half of H.\n',
     '# M -> H (511.0 keV) lies on the annihilation line and feeds about a third of H.\n'),
    ('    "H": (2581.6, 2.75, [("Da", 50), ("B", 35), ("C", 15)]),\n',
     '    "H": (2581.6, 3.65, [("Da", 50), ("B", 35), ("C", 15)]),\n'),
    ('    "M": (3092.6, 11.75, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("H", 31)]),\n',
     '    "M": (3092.6, 10.85, [("A", 45), ("Da", 20), ("I", 20), ("L", 15), ("H", 21)]),\n'),
    ("    # A little annihilation radiation follows the pair production of the parent's high-energy lines.\n"
     "    parent = parent + N_PARENT * 3.0e-4 * peak(EDGES_RUN, 511.0, 1.3)\n",
     "    # Annihilation radiation follows the pair production of the parent's high-energy lines in the crystals and in\n"
     "    # the shield around them, with the parent's time profile.\n"
     "    parent = parent + N_PARENT * 6.0e-4 * peak(EDGES_RUN, 511.0, 1.3)\n"),
    ('            "the narrow part\'s share with the parent\'s time profile %.2f; I of the narrow part %.2f, scheme %.2f"\n'
     '            % (s["parent_share"], s["I"], near["relative_intensity"])]\n',
     '            "the narrow part\'s share with the parent\'s time profile %.2f; I of the narrow part %.2f, scheme %.2f"\n'
     '            % (s["parent_share"], s["I"], near["relative_intensity"])]\n'
     '    # The readings of the peak taken as one line, from the shipped files: the whole peak, and the peak less the\n'
     '    # background run\'s annihilation radiation scaled to the run.\n'
     '    bg = np.loadtxt(DATA / "background.txt")[:, 1]\n'
     '    mid = 0.5 * (EDGES_RUN[:-1] + EDGES_RUN[1:])\n'
     '    win = np.abs(mid - 511.0) < 5.0\n'
     '    side = (np.abs(mid - 511.0) > 7.0) & (np.abs(mid - 511.0) < 12.0)\n'
     '    room = (bg[win].sum() - bg[side].mean() * win.sum()) * T_RUN / BG_SECONDS\n'
     '    whole = s["I"] * (s["narrow"] + s["broad"]) / s["narrow"]\n'
     '    less_room = s["I"] * (s["narrow"] + s["broad"] - room) / s["narrow"]\n'
     '    out += ["the background run\'s annihilation peak scaled to the run\'s %.0f s: %.0f counts" % (T_RUN, room),\n'
     '            "read as one line: I %.2f from the whole peak, %.2f from the peak less that room share, %.2f from the "\n'
     '            "narrow part; scheme %.2f" % (whole, less_room, s["I"], near["relative_intensity"])]\n'),
])
