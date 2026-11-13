"""Writes tests/requirements.json for the v15 draft from its instruction's sentences (each quote must occur in it).
Not shipped."""
import json
import os
import sys

TASK = sys.argv[1]
ins = open(os.path.join(TASK, "instruction.md"), encoding="utf-8").read()
V, Bv, L, G = "test_viscosity", "test_bulk_viscosity", "test_thermal_conductivity", "test_gap_conductivity"
P = "test_program_output"
ALL, NUM, LG, PHYS = [P, V, Bv, L, G], [V, L, G], [L, G], [V, Bv, L, G]
R = [
    ("Write `/app/output/transport.py`, a Python program that the checker runs as "
     "`python3 transport.py G A L B T N W TAU`", ALL),
    ("It must exit with status 0 after writing to standard output exactly one JSON object with exactly four "
     "members, each a JSON number", ALL),
    ("`viscosity`, the reduced viscosity, `bulk_viscosity`, the reduced bulk viscosity, `thermal_conductivity`, the "
     "reduced thermal conductivity, and "
     "`gap_conductivity`, the reduced gap conductivity, of that gas at that reduced temperature, number density, gap "
     "and relaxation time", ALL),
    ("the reduced viscosity `η σ^2 / sqrt(m ε)`", [V]),
    ("the reduced thermal conductivity `λ σ^2 sqrt(m / ε) / k_B`", [L]),
    ("`λ` is the coefficient in the energy flux `-λ ∇T` in a steady state of the gas at rest at uniform pressure in "
     "which no net flux of molecules flows and the temperature varies so slowly in space that the conversion "
     "holds the composition everywhere at the equilibrium one for the local temperature; the energy flux is all "
     "the energy, translational and rotational, that the molecules carry through a unit area per unit time.", LG),
    ("`η` is the viscosity of the gas at the equilibrium composition for its temperature `T`.", [V]),
    ("A molecule changes between `J = 0` and `J = 1`, which also changes its nuclear-spin state, only on a conversion "
     "catalyst spread uniformly through the gas that takes no other part in its dynamics and neither stores nor "
     "carries energy: the energy that a molecule gains or loses when it converts is taken from or given to the gas "
     "where it converts.", [Bv, L, G]),
    ("The conversion changes the mole fraction `x` of the `J = 1` molecules at the rate `(x_e - x) / τ`, where `x_e` "
     "is its value when the molecules are spread over all their internal states as in thermal equilibrium at the "
     "local temperature and `τ` is a fixed relaxation time, long compared with the time between collisions, so that "
     "the conversion does not change the velocity distributions of the Boltzmann equation above at first order in "
     "the gradients.", PHYS),
    ("as the Chapman-Enskog solution of that Boltzmann equation gives them at first order in the gradients (the "
     "Navier-Stokes level): the exact solution of that order's linearized integral equations, not a truncated "
     "approximation to it", NUM),
    ("Apart from these internal states the molecules act as point particles: an H2 molecule has mass `m` and a D2 "
     "molecule mass `2 m`, and every pair of molecules interacts through the same spherical-core (Kihara) potential "
     "`V(r) = 4ε[((σ - a)/(r - a))^12 - ((σ - a)/(r - a))^6]` for `r > a`, with `V(r)` infinite for `r <= a`, which "
     "depends on nothing but `r`.", NUM),
    ("and `a` is the core diameter; a core ratio `a / σ` of 0 gives the Lennard-Jones 12-6 potential", NUM),
    ("where `G` is the gas, `H2` or `D2`, `A` is the core ratio `a / σ`, any value from 0 to 0.5, `L` is the quantum "
     "parameter `Λ*`, any value from 0.8 to 2.8, `B` is the reduced rotational constant `B` of an H2 molecule, "
     "whichever the gas, any value from 1 to 3, `T` is the reduced temperature `T*`, any value from 0.2 to 0.6, `N` "
     "is the reduced number density `n σ^3`, any value from 0.001 to 0.01, `W` is the reduced gap `d / σ`, any value "
     "from 1000 to 100000, and `TAU` is the reduced relaxation time `τ sqrt(ε / (m σ^2))`, any value from 10000 to "
     "10000000, all seven ranges including their ends; each number is given as a decimal number without an "
     "exponent, such as `0.35` or `2`.", ALL),
    ("They are wanted at a reduced temperature `T* = k_B T / ε`, where `k_B` is the Boltzmann constant, as these "
     "dimensionless values, with the mass `m` of an H2 molecule", PHYS),
    ("With `n` the number density, `η` and `λ` do not depend on the density.", [V, L]),
    ("The checker runs the program once on each of eight sets of `G`, `A`, `L`, `B`, `T`, `N`, `W` and `TAU` from "
     "those ranges, which it does not disclose, and compares each of the 32 numbers with the exact value; it accepts "
     "a number only when the two differ by at most 2e-5 times the exact value, and all 32 must be accepted.", ALL),
    ("Each run of the program gets 2 CPUs and 4 GB of memory, with Python 3.12, its standard library, numpy 2.3.3, "
     "scipy 1.18.1, sympy 1.14.0 and mpmath 1.3.0 and no other package, and at most 600 seconds of wall-clock time "
     "from the moment the checker starts it, interpreter start-up included: a program still running then is stopped, "
     "and that set fails.", ALL),
    ("Its standard input is empty, its environment holds only `HOME`, `TMPDIR`, `PATH` and `LANG`, and when it exits "
     "every process it started is stopped.", [P]),
    ("Its working directory is a read-only folder that holds only a copy of `transport.py`, and the folders that its "
     "`TMPDIR` and `HOME` environment variables name are writable for it; no file it writes may grow larger than "
     "67108864 bytes: a write past that size fails.", [P]),
    ("It may write at most 1048576 bytes to standard output, or that set fails; anything it writes to standard error "
     "is ignored.", ALL),
    ("`/app/output/transport.py` must be a regular file, not a link, of at most 20971520 bytes; the checker collects "
     "all of `/app/output` as one tar archive, which may hold at most 536870912 bytes, and grades only "
     "`transport.py` in it.", ALL),
    ("How strong the quantum effects are is set by the parameter `Λ* = h / (σ sqrt(m ε))`, where `m` is the mass of "
     "an H2 molecule.", NUM),
    ("The gas is dilute and far from degeneracy, so the velocity distributions of the two species obey the Boltzmann "
     "equation of classical kinetic theory for binary elastic collisions, in which the differential cross section of "
     "each collision is the quantum-mechanical one for the two molecules, averaged over their equally populated "
     "internal states, with the symmetry under the exchange of the two molecules that quantum mechanics requires "
     "when they are of the same species.", PHYS),
    ("For two molecules with reduced mass `μ` that collide with kinetic energy `E` in their centre-of-mass frame, let "
     "`k = sqrt(2 μ E) / ħ`; the phase shift `δ_l` of the partial wave with orbital angular momentum quantum number "
     "`l` is that of the solution `u(r)` of the radial equation `u'' = [l(l + 1) / r^2 + 2 μ (V(r) - E) / ħ^2] u` "
     "that vanishes at `r = a` and for large `r` is proportional to `sin(k r - l π / 2 + δ_l)`, and the scattering "
     "amplitude at the scattering angle `χ` is `f(χ) = (1 / (2 i k)) Σ_l (2 l + 1) (exp(2 i δ_l) - 1) "
     "P_l(cos χ)`, summed over every `l >= 0`, with `P_l` the Legendre polynomial of degree `l`.", NUM),
    ("Two molecules of different species scatter with the differential cross section `|f(χ)|^2`, with `μ` their "
     "reduced mass, as no collision changes their internal states.", NUM),
    ("For two molecules of the same species, `μ` is half the mass of one molecule, and the differential cross section "
     "is half the one for finding a molecule leaving at the scattering angle `χ`, so that an integral over every `χ` "
     "from 0 to `π`, as in the collision integrals, counts each final state once.", NUM),
    ("Every molecule is in the electronic ground state `X 1Σg+`, whose electron spin and electronic orbital angular "
     "momentum are zero, and in one of the two rotational levels `J = 0` and `J = 1`: the gas is cold enough that "
     "every higher level is to be left out.", PHYS),
    ("The proton has spin 1/2 and the deuteron spin 1, and the nuclear spins of a molecule are in the states that the "
     "symmetry of the molecule's own wave function allows in its rotational level.", PHYS),
    ("Within each level, every rotational sublevel and every nuclear-spin state that the molecules can be in is "
     "equally populated, and every collision between two molecules is elastic and leaves the rotational level, the "
     "rotational sublevel and the nuclear-spin state of both unchanged.", PHYS),
    ("The rotational energy of a molecule in level `J` is `J(J + 1) ħ^2 / (2 I)`, where `ħ = h / (2π)` with `h` the "
     "Planck constant and `I` is the molecule's moment of inertia, that of its two nuclei as point masses, each of "
     "half the molecule's mass, at a fixed distance from each other that is the same in H2 and in D2; the reduced "
     "rotational constant `B` is `ħ^2 / (2 I ε)` for an H2 molecule.", PHYS),
    ("The molecules in `J = 0` and those in `J = 1` are the two species of a binary mixture.", PHYS),
    ("`λ_gap` belongs to a layer of the gas, with the given `τ`, between two parallel plane walls a distance `d` apart "
     "that are held at the temperatures `T + ΔT / 2` and `T - ΔT / 2`, neither absorb nor emit molecules, and convert "
     "none: in the steady state the gas is at rest at uniform pressure and carries a uniform energy flux `q` from the "
     "warmer wall to the colder, and `λ_gap` is the limit of `q d / ΔT` as `ΔT` tends to 0.", [G]),
    ("Throughout the layer the gas is a continuum that obeys the first-order flux laws of the Boltzmann equation "
     "above, and at each wall its temperature is the wall's.", [G]),
    ("the reduced gap conductivity `λ_gap σ^2 sqrt(m / ε) / k_B`", [G]),
    ("`η_b` belongs to the gas in a uniform expansion at a small constant rate `∇·v`, with no gradient of temperature "
     "or composition and no heat exchanged: once the expansion has gone on for many times `τ`, the mean of the three "
     "normal pressures is `p_e - η_b ∇·v` to first order in `∇·v`, where `p_e` is the pressure that the gas would "
     "have in thermal equilibrium, its composition included, at the same number density and the same energy per unit "
     "volume.", [Bv]),
    ("the reduced bulk viscosity `η_b σ^2 / sqrt(m ε)`", [Bv]),
]
out = {"requirements": [], "unstated_ok": []}
for i, (q, t) in enumerate(R, 1):
    assert q in ins, (i, q[:70])
    out["requirements"].append({"id": "R%d" % i, "quote": q, "tests": t})
with open(os.path.join(TASK, "tests", "requirements.json"), "w", encoding="utf-8", newline="\n") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)
    fh.write("\n")
print(len(R), "requirements")
