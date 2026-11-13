"""List every decimal number in the task README that appears in none of tests/checks.txt, tests/expected.json (as
printed there or rounded to the README's digits), instruction.md and the generator's constants, so each can be
checked by hand. Reads text only. Run from the folder root."""
import json
import re
from pathlib import Path

T = Path("tasks/active/gamma-decay-scheme")
readme = (T / "README.md").read_text(encoding="utf-8")
pool = (T / "tests" / "checks.txt").read_text(encoding="utf-8") + (T / "instruction.md").read_text(encoding="utf-8") \
    + (T / "tests" / "generate.py").read_text(encoding="utf-8")
exp = json.loads((T / "tests" / "expected.json").read_text(encoding="utf-8"))
values = set()
for t in exp["transitions"]:
    for k in ("from_keV", "to_keV", "energy_keV", "relative_intensity"):
        values.add(float(t[k]))
values.update(float(v) for v in exp["levels_keV"])
values.update([float(exp["parent_half_life_s"]), float(exp["isomer"]["level_keV"]), float(exp["isomer"]["half_life_ns"])])
pool_nums = set(re.findall(r"-?\d+\.\d+", pool))
body = readme.split("## Difficulty explanation", 1)[1].split("## Relevant experience", 1)[0]
seen = set()
for m in re.finditer(r"(?<![\w.])-?\d+\.\d+", body):
    x = m.group(0)
    if x in seen:
        continue
    seen.add(x)
    if x in pool_nums or x.lstrip("-") in pool_nums:
        continue
    digits = len(x.split(".")[1])
    if any(abs(round(v, digits) - float(x)) < 0.5 * 10 ** -digits for v in values):
        continue
    line = body[:m.start()].count("\n")
    ctx = body[max(0, m.start() - 60):m.end() + 30].replace("\n", " ")
    print("%-10s ...%s..." % (x, ctx))
