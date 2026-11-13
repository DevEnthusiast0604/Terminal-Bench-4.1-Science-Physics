"""Edits the v15 draft's instruction.md: finite-rate conversion, the gap conductivity, three new inputs. Not shipped."""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:90]
    s = s.replace(old, new)


rep("only on a conversion catalyst spread through the gas that takes no other part in its dynamics",
    "only on a conversion catalyst spread uniformly through the gas that takes no other part in its dynamics")
rep("The conversion is slow compared with the collisions, so it does not change the velocity distributions of the "
    "Boltzmann equation above at first order in the gradients, and fast compared with diffusion, so at every point "
    "the molecules are spread over all their internal states as in thermal equilibrium at the local temperature. "
    "The quantities are the shear viscosity `η` and the thermal conductivity `λ` of the gas as the Chapman-Enskog "
    "solution of that Boltzmann equation gives them at first order in the gradients (the Navier-Stokes level): the "
    "exact solution of that order's linearized integral equations, not a truncated approximation to it. `η` is the "
    "viscosity of the gas at the equilibrium composition for its temperature `T`. `λ` is the coefficient in the "
    "energy flux `-λ ∇T` in a steady state of the gas at rest at uniform pressure in which no net flux of molecules "
    "flows, as between walls that neither absorb nor emit molecules, where the energy flux is all the energy, "
    "translational and rotational, that the molecules carry through a unit area per unit time. With `n` the number "
    "density, `η` and `λ` do not depend on the density.",
    "The conversion changes the mole fraction `x` of the `J = 1` molecules at the rate `(x_e - x) / τ`, where `x_e` "
    "is its value when the molecules are spread over all their internal states as in thermal equilibrium at the "
    "local temperature and `τ` is a fixed relaxation time, long compared with the time between collisions, so that "
    "the conversion does not change the velocity distributions of the Boltzmann equation above at first order in the "
    "gradients. The quantities are the shear viscosity `η`, the thermal conductivity `λ` and the gap conductivity "
    "`λ_gap` of the gas as the Chapman-Enskog solution of that Boltzmann equation gives them at first order in the "
    "gradients (the Navier-Stokes level): the exact solution of that order's linearized integral equations, not a "
    "truncated approximation to it. `η` is the viscosity of the gas at the equilibrium composition for its "
    "temperature `T`. `λ` is the coefficient in the energy flux `-λ ∇T` in a steady state of the gas at rest at "
    "uniform pressure in which no net flux of molecules flows, in the limit of fast conversion, `τ` tending to 0, in "
    "which the composition is everywhere the equilibrium one for the local temperature; the energy flux is all the "
    "energy, translational and rotational, that the molecules carry through a unit area per unit time. `λ_gap` "
    "belongs to a layer of the gas, with the given `τ`, between two parallel plane walls a distance `d` apart that "
    "are held at the temperatures `T + ΔT / 2` and `T - ΔT / 2`, neither absorb nor emit molecules, and convert "
    "none: in the steady state the gas is at rest at uniform pressure and carries a uniform energy flux `q` from the "
    "warmer wall to the colder, and `λ_gap` is the limit of `q d / ΔT` as `ΔT` tends to 0. Throughout the layer the "
    "gas is a continuum that obeys the first-order flux laws of the Boltzmann equation above, and at each wall its "
    "temperature is the wall's. With `n` the number density, `η` and `λ` do not depend on the density.")
rep("the reduced viscosity `η σ^2 / sqrt(m ε)` and the reduced thermal conductivity `λ σ^2 sqrt(m / ε) / k_B`.",
    "the reduced viscosity `η σ^2 / sqrt(m ε)`, the reduced thermal conductivity `λ σ^2 sqrt(m / ε) / k_B` and the "
    "reduced gap conductivity `λ_gap σ^2 sqrt(m / ε) / k_B`.")
rep("the checker runs as `python3 transport.py G A L B T`, where",
    "the checker runs as `python3 transport.py G A L B T N W TAU`, where")
rep("and `T` is the reduced temperature `T*`, any value from 0.2 to 0.6, all four ranges including their ends;",
    "`T` is the reduced temperature `T*`, any value from 0.2 to 0.6, `N` is the reduced number density `n σ^3`, any "
    "value from 0.001 to 0.01, `W` is the reduced gap `d / σ`, any value from 1000 to 100000, and `TAU` is the "
    "reduced relaxation time `τ sqrt(ε / (m σ^2))`, any value from 10000 to 10000000, all seven ranges including "
    "their ends;")
rep("exactly one JSON object with exactly two members, each a JSON number: `viscosity`, the reduced viscosity, and "
    "`thermal_conductivity`, the reduced thermal conductivity, of that gas at that reduced temperature.",
    "exactly one JSON object with exactly three members, each a JSON number: `viscosity`, the reduced viscosity, "
    "`thermal_conductivity`, the reduced thermal conductivity, and `gap_conductivity`, the reduced gap conductivity, "
    "of that gas at that reduced temperature, number density, gap and relaxation time.")
rep("The checker runs the program once on each of eight sets of `G`, `A`, `L`, `B` and `T` from those ranges, which "
    "it does not disclose, and compares each of the 16 numbers with the exact value; it accepts a number only when "
    "the two differ by at most 2e-5 times the exact value, and all 16 must be accepted.",
    "The checker runs the program once on each of eight sets of `G`, `A`, `L`, `B`, `T`, `N`, `W` and `TAU` from "
    "those ranges, which it does not disclose, and compares each of the 24 numbers with the exact value; it accepts "
    "a number only when the two differ by at most 2e-5 times the exact value, and all 24 must be accepted.")
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
