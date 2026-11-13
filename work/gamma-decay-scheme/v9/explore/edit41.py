"""v9: tests/checks.txt names the pair furthest from 1 in the coincidence route to the intensities, and counts the
pairs further from 1 than the 25 percent band, so the README can cite them.
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
    ('    good = [(m, p) for _, _, m, p in diag["strengths"]]\n'
     '    ratio = np.array([m / p for m, p in good])\n',
     '    good = [(m, p) for _, _, m, p in diag["strengths"]]\n'
     '    ratio = np.array([m / p for m, p in good])\n'
     '    worst = max(diag["strengths"], key=lambda r: abs(r[2] / r[3] - 1.0))\n'),
    ('            "measured over predicted: mean %.3f, rms %.3f, furthest from 1 by %.3f"\n'
     '            % (float(ratio.mean()), float(ratio.std()), float(np.abs(ratio - 1.0).max())),\n',
     '            "measured over predicted: mean %.3f, rms %.3f, furthest from 1 by %.3f (%.1f keV with %.1f keV, measured "\n'
     '            "%.3f, predicted %.3f); further from 1 than 0.25: %d"\n'
     '            % (float(ratio.mean()), float(ratio.std()), float(np.abs(ratio - 1.0).max()), worst[0], worst[1],\n'
     '               worst[2], worst[3], int(np.sum(np.abs(ratio - 1.0) > 0.25))),\n'),
])
