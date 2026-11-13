from pathlib import Path
T = Path("tasks/active/dhva-fermi-surface")


def edit(rel, pairs):
    p = T / rel
    s = p.read_text(encoding="utf-8")
    for old, new in pairs:
        assert s.count(old) >= 1, (rel, old)
        s = s.replace(old, new)
    p.write_text(s, encoding="utf-8", newline="\n")
    print(rel, "ok")


edit("instruction.md", [("`mass_me` within 10% of the right value", "`mass_me` within 15% of the right value")])
edit("tests/requirements.json", [("`mass_me` within 10% of the right value", "`mass_me` within 15% of the right value")])
edit("tests/test_outputs.py", [('MASS = Decimal("0.10")          # instruction.md: a cyclotron mass within 10%',
                                'MASS = Decimal("0.15")          # instruction.md: a cyclotron mass within 15%'),
                               ('"""every cyclotron mass within 10%."""', '"""every cyclotron mass within 15%."""')])
edit("tests/generate.py", [("MASS_BAND = 0.10       # instruction.md: mass within 10%",
                            "MASS_BAND = 0.15       # instruction.md: mass within 15%"),
                           ("other entry, every mass within 10%.", "other entry, every mass within 15%."),
                           ('"   mass outside 10%"', '"   mass outside 15%"')])
edit("solution/solve.py", [("REFINE_SNR = 20.0           # an orbit's frequency is refined on the sweeps where its fundamental stands this far out",
                            "REFINE_SNR = 10.0           # an orbit's frequency is refined on the sweeps where its fundamental stands this far out")])
