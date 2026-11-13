"""Drop the instruction's hint sentence ("A planet's period can lie close to a period of the star's own
variability.") before the first upload: gamma's full review (job 20271, 2026-11-10 14:04) flagged a sentence of this
kind as a critical answer leak. R5 goes with it; R6..R9 become R5..R8 in requirements.json and the README table."""
import json
import re
from pathlib import Path

T = Path("tasks/active/rv-planet-census")
HINT = " A planet's period can lie close to a period of the star's own variability."

ins = T / "instruction.md"
s = ins.read_bytes().decode("utf-8")
assert s.count(HINT) == 1
ins.write_bytes(s.replace(HINT, "").encode("utf-8"))

rq = T / "tests" / "requirements.json"
s = rq.read_bytes().decode("utf-8")
data = json.loads(s)
reqs = [r for r in data["requirements"] if r["quote"] != HINT.strip()]
assert len(reqs) == len(data["requirements"]) - 1
renum = {}
for i, r in enumerate(reqs, 1):
    renum[r["id"]] = "R%d" % i
lines = ['{', '  "requirements": [']
for i, r in enumerate(reqs):
    lines += ['    {',
              '      "id": %s,' % json.dumps(renum[r["id"]]),
              '      "quote": %s,' % json.dumps(r["quote"], ensure_ascii=False),
              '      "tests": [%s]' % ", ".join(json.dumps(x) for x in r["tests"]),
              '    }' + (',' if i < len(reqs) - 1 else '')]
lines += ['  ],', '  "context_ok": [']
lines += ['    %s' % json.dumps(c, ensure_ascii=False) + (',' if j < len(data["context_ok"]) - 1 else '')
          for j, c in enumerate(data["context_ok"])]
lines += ['  ],', '  "unstated_ok": %s' % json.dumps(data["unstated_ok"]), '}', '']
out = "\n".join(lines)
assert json.loads(out)["requirements"][4]["id"] == "R5"
rq.write_bytes(out.encode("utf-8"))
print("renumbered:", renum)

table = {
    "| `test_file_and_members` | R1, R6, R7 |": "| `test_file_and_members` | R1, R5, R6 |",
    "| `test_rotation_period` | R1, R3, R9 |": "| `test_rotation_period` | R1, R3, R8 |",
    "| `test_planets_found` | R1, R2, R4, R5, R6, R8 |": "| `test_planets_found` | R1, R2, R4, R5, R7 |",
    "| `test_semi_amplitudes` | R1, R4, R6, R8 |": "| `test_semi_amplitudes` | R1, R4, R5, R7 |",
    "| `test_minimum_masses` | R1, R4, R6, R8 |": "| `test_minimum_masses` | R1, R4, R5, R7 |",
    "| `test_radii` | R1, R4, R6, R8 |": "| `test_radii` | R1, R4, R5, R7 |",
}
for f in (T / "README.md", Path("work/rv-planet-census/v1/readme_draft.md")):
    s = f.read_bytes().decode("utf-8")
    for a, b in table.items():
        assert s.count(a) == 1, (f, a)
        s = s.replace(a, b)
    f.write_bytes(s.encode("utf-8"))
print("instruction, requirements and README updated")
