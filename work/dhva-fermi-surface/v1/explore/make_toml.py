"""Writes tasks/active/dhva-fermi-surface/task.toml from rv-planet-census's, with LF line ends."""
from pathlib import Path

src = Path("tasks/active/rv-planet-census/task.toml").read_text(encoding="utf-8").replace("\r\n", "\n")
dst = Path("tasks/active/dhva-fermi-surface/task.toml")


def rep(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new)


s = src
s = rep(s, 'name = "terminal-bench/rv-planet-census"', 'name = "terminal-bench/dhva-fermi-surface"')
s = rep(s, 'description = "Find the planets of a K dwarf from two spectrographs\' radial velocities, activity indicators '
           'and a space light curve, and write their periods, semi-amplitudes, minimum masses and radii with the star\'s '
           'rotation period to /app/output/planets.json."',
        'description = "Find the extremal Fermi-surface orbits of a metal for one field direction from de Haas-van Alphen '
        'magnetization sweeps at twelve temperatures, and write each orbit\'s frequency and cyclotron mass to '
        '/app/output/orbits.json."')
s = rep(s, 'keywords = ["exoplanets", "radial-velocity", "stellar-activity", "gaussian-process", "transit-photometry", '
           '"aliasing", "eclipsing-binary"]',
        'keywords = ["de-haas-van-alphen", "quantum-oscillations", "fermi-surface", "lifshitz-kosevich", '
        '"effective-mass", "fourier-analysis", "condensed-matter"]')
s = rep(s, 'tags = ["exoplanets", "radial-velocity", "stellar-activity", "transit-photometry", "gaussian-process", '
           '"aliasing"]',
        'tags = ["quantum-oscillations", "fermi-surface", "lifshitz-kosevich", "effective-mass", "fourier-analysis", '
        '"condensed-matter"]')
s = rep(s, "expert_time_estimate_hours = 7", "expert_time_estimate_hours = 6")
dst.write_text(s, encoding="utf-8", newline="\n")
print("written", len(s), "bytes,", s.count("\r"), "CR")
