"""Edits the v15 draft's task.toml description and keywords. Not shipped."""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()
old_d = s[s.index('description = "'):s.index('"\n', s.index('description = "')) + 1]
new_d = ('description = "Write /app/output/transport.py, a Python program that computes the exact (converged) '
         'first-order Chapman-Enskog shear viscosity, steady-state thermal conductivity at fast ortho-para conversion '
         'and gap conductivity of a layer between two non-catalytic walls at a finite conversion rate, of dilute H2 or '
         'D2 as a binary mixture of its J = 0 and J = 1 levels with stated nuclear spins and rotational energies, '
         'interacting through one Kihara potential with quantum-mechanical cross sections from partial-wave phase '
         'shifts and the exchange symmetry of identical molecules, the conductivities including the conversion energy '
         'carried by counter-diffusion, its coupling to thermal diffusion and, in the gap, the reaction-diffusion '
         'boundary layer at the walls, for any core ratio a/sigma from 0 to 0.5, quantum parameter Lambda* from 0.8 to '
         '2.8, rotational constant B from 1 to 3, reduced temperature from 0.2 to 0.6, density, gap and relaxation time '
         'of the stated ranges, to 2e-5 relative within 600 s per run; it is graded on eight sets it never sees."')
assert s.count(old_d) == 1
s = s.replace(old_d, new_d)
old_k = '"thermal-diffusion", "transport-coefficients",'
assert s.count(old_k) == 1
s = s.replace(old_k, '"thermal-diffusion", "reaction-diffusion", "transport-coefficients",')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
