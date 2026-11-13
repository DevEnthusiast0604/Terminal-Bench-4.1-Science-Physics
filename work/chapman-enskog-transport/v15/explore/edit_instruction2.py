"""Second pass on the v15 draft's instruction (catalyst wording, lambda without a tau -> 0 limit) and the R6 quote.
Not shipped."""
import os
import sys

task = sys.argv[1]
OLD_L = ("`λ` is the coefficient in the energy flux `-λ ∇T` in a steady state of the gas at rest at uniform pressure in "
         "which no net flux of molecules flows, in the limit of fast conversion, `τ` tending to 0, in which the "
         "composition is everywhere the equilibrium one for the local temperature; the energy flux is all the energy, "
         "translational and rotational, that the molecules carry through a unit area per unit time.")
NEW_L = ("`λ` is the coefficient in the energy flux `-λ ∇T` in a steady state of the gas at rest at uniform pressure in "
         "which no net flux of molecules flows and the temperature varies so slowly in space that the conversion "
         "holds the composition everywhere at the equilibrium one for the local temperature; the energy flux is all "
         "the energy, translational and rotational, that the molecules carry through a unit area per unit time.")
pairs = {
    "instruction.md": [
        ("where the collisions follow quantum mechanics and a catalyst keeps the two nuclear-spin modifications of the "
         "gas in equilibrium with each other.",
         "where the collisions follow quantum mechanics and a catalyst converts the two nuclear-spin modifications of "
         "the gas into each other at a finite rate."),
        (OLD_L, NEW_L)],
    os.path.join("..", "explore", "write_requirements.py"): [
        ('''    ("`λ` is the coefficient in the energy flux `-λ ∇T` in a steady state of the gas at rest at uniform pressure in "
     "which no net flux of molecules flows, in the limit of fast conversion, `τ` tending to 0, in which the "
     "composition is everywhere the equilibrium one for the local temperature; the energy flux is all the energy, "
     "translational and rotational, that the molecules carry through a unit area per unit time.", LG),''',
         '''    ("`λ` is the coefficient in the energy flux `-λ ∇T` in a steady state of the gas at rest at uniform pressure in "
     "which no net flux of molecules flows and the temperature varies so slowly in space that the conversion "
     "holds the composition everywhere at the equilibrium one for the local temperature; the energy flux is all "
     "the energy, translational and rotational, that the molecules carry through a unit area per unit time.", LG),''')],
}
for rel, reps in pairs.items():
    p = os.path.join(task, rel)
    s = open(p, encoding="utf-8").read()
    for old, new in reps:
        assert s.count(old) == 1, (rel, old[:80])
        s = s.replace(old, new)
    open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
