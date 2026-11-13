"""Fills the scaffold placeholders of tasks/active/dhva-fermi-surface (Dockerfile, solve.sh, cheat, grading.json)."""
from pathlib import Path

T = Path("tasks/active/dhva-fermi-surface")


def edit(rel, pairs):
    p = T / rel
    s = p.read_text(encoding="utf-8").replace("\r\n", "\n")
    for old, new in pairs:
        assert s.count(old) == 1, (rel, old)
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="\n")
    print(rel, "ok")


edit("environment/Dockerfile", [
    ("# <COPY the task inputs, never the expected outputs, e.g. COPY data/ /app/data/>",
     "# The magnetization sweeps and the notes on the experiment.\nCOPY data/ /app/data/"),
])
edit("solution/solve.sh", [
    ('"<input-path>"', "/app/data"),
    ('"/app/output/<deliverable-file>"', '"/app/output/orbits.json"'),
])
edit("cheat/symlink-answers/solve.sh", [
    ('TARGET="/app/output/<deliverable-file>"', 'TARGET="/app/output/orbits.json"'),
])
edit("tests/grading.json", [
    ('{\n  "difficulty_bar"', '{\n  "deliverables": ["/app/output/orbits.json"],\n  "difficulty_bar"'),
])
