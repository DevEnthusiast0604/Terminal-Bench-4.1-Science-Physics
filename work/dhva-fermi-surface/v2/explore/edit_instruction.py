from pathlib import Path
import json
old = ("Each object has exactly the members `frequency_T`, the orbit's de Haas-van Alphen frequency in tesla, and "
       "`mass_me`, its cyclotron effective mass in units of the free-electron mass.")
new = ("Each object has exactly the members `frequency_T`, the orbit's de Haas-van Alphen frequency F = hbar A / (2 pi e) "
       "in tesla, with A the area the orbit encloses in k-space, and `mass_me`, its cyclotron effective mass in units of "
       "the free-electron mass.")
p = Path("tasks/active/dhva-fermi-surface/instruction.md")
t = p.read_text(encoding="utf-8")
assert t.count(old) == 1
p.write_text(t.replace(old, new), encoding="utf-8", newline="\n")
r = Path("tasks/active/dhva-fermi-surface/tests/requirements.json")
t = r.read_text(encoding="utf-8")
assert t.count(json.dumps(old)[1:-1]) == 1
r.write_text(t.replace(json.dumps(old)[1:-1], json.dumps(new)[1:-1]), encoding="utf-8", newline="\n")
d = json.loads(r.read_text(encoding="utf-8"))
ins = p.read_text(encoding="utf-8")
for q in d["requirements"]:
    assert q["quote"] in ins, q["id"]
for q in d["context_ok"]:
    assert q in ins
print("instruction and requirements updated; every quote found")
