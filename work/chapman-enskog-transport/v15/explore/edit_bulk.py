"""Adds the bulk viscosity of the finite-rate conversion to the v15 draft (generator, oracle, self-check, judge,
instruction). Not shipped.
    python -X utf8 -I -B work/chapman-enskog-transport/v15/explore/edit_bulk.py work/chapman-enskog-transport/v15/task"""
import os
import sys

task = sys.argv[1]


def edit(rel, pairs):
    p = os.path.join(task, rel)
    s = open(p, encoding="utf-8").read()
    for old, new in pairs:
        assert s.count(old) == 1, (rel, old[:90])
        s = s.replace(old, new)
    open(p, "w", encoding="utf-8", newline="\n").write(s)


edit("tests/generate.py", [
    ('''"""Writes tests/expected.json: the reduced viscosity, thermal conductivity and gap conductivity of the instruction's''',
     '''"""Writes tests/expected.json: the reduced viscosity, bulk viscosity, thermal conductivity and gap conductivity of the
instruction's'''),
    ('''which runs from lambda_f (F -> 1) to lambda (F -> 0). The viscosity is the frozen one at the equilibrium x1.
''',
     '''which runs from lambda_f (F -> 1) to lambda (F -> 0). The viscosity is the frozen one at the equilibrium x1.

Bulk viscosity (a uniform expansion at the rate D = div v, no heat exchanged): the energy per molecule
e = 3/2 T + theta x2 (only the translational heat capacity 3/2 is frozen: collisions keep the levels) obeys
de/dt = -T D, and dx2/dt = (x2e(T) - x2) / tau with tau at the local, changing temperature. Once the start has died
out, x2 = x2e(T) + delta with delta = tau c_R D T / (theta c0) to first order, c_R = theta dx2e/dT = x1 x2 (theta / T)^2
and c0 = 3/2 + c_R. At the same n and e the equilibrium temperature is T + theta delta / c0, so the mean normal
pressure n T falls short of p_e by n theta delta / c0:
    eta_b = p tau c_R / (3/2 + c_R)^2,   p = n T
(in reduced units N T* TAU c_R / (3/2 + c_R)^2). At fixed energy the composition relaxes with tau 3/2 / c0, not tau.
'''),
    ('''QUANTITIES = ("viscosity", "thermal_conductivity", "gap_conductivity")''',
     '''QUANTITIES = ("viscosity", "bulk_viscosity", "thermal_conductivity", "gap_conductivity")'''),
    ('''def combine(c, x1, theta, T, N, W, TAU):
    """The three coefficients from the frozen ones c (instruction units) at the set's density, gap and tau."""''',
     '''def bulk(x1, theta, T, N, TAU):
    """eta_b = p tau c_R / (3/2 + c_R)^2, reduced, with p = N T and c_R = x1 x2 (theta / T)^2."""
    cR = x1 * (1.0 - x1) * (theta / T) ** 2
    return N * T * TAU * cR / (1.5 + cR) ** 2


def combine(c, x1, theta, T, N, W, TAU):
    """The four coefficients from the frozen ones c (instruction units) at the set's density, gap and tau."""'''),
    ('''    return {"viscosity": c["viscosity"], "thermal_conductivity": lf + lR,
            "gap_conductivity": lf * (lf + lR) / (lf + lR * F)}''',
     '''    return {"viscosity": c["viscosity"], "bulk_viscosity": bulk(x1, theta, T, N, TAU),
            "thermal_conductivity": lf + lR, "gap_conductivity": lf * (lf + lR) / (lf + lR * F)}'''),
    ('''    """The set's three coefficients at P (and the qmix.case record); only: cache just that pair's stages."""''',
     '''    """The set's four coefficients at P (and the qmix.case record); only: cache just that pair's stages."""'''),
])

edit("solution/transport.py", [
    ('''"""Reference program: the shear viscosity, the steady-state thermal conductivity at fast ortho-para conversion and
the conductivity of a layer between two non-catalytic walls at a finite conversion rate, of dilute H2 or D2, from the''',
     '''"""Reference program: the shear viscosity, the bulk viscosity of the finite-rate ortho-para conversion, the
steady-state thermal conductivity at fast conversion and the conductivity of a layer between two non-catalytic walls
at a finite conversion rate, of dilute H2 or D2, from the'''),
    ('''10000000); it prints one JSON object (the three reduced coefficients, with the mass m) on stdout and its progress on''',
     '''10000000); it prints one JSON object (the four reduced coefficients, with the mass m) on stdout and its progress on'''),
    ('''   F = tanh(kappa d / 2) / (kappa d / 2): lambda_f for a thin gap or slow conversion, lambda for a wide one.
''',
     '''   F = tanh(kappa d / 2) / (kappa d / 2): lambda_f for a thin gap or slow conversion, lambda for a wide one.
8. Bulk viscosity: in a uniform expansion at the rate div v with no heat exchanged, e = 3/2 T + theta x2 (collisions
   keep the levels, so only 3/2 is frozen) falls as de/dt = -T div v, and x2 lags x2e(T) by
   delta = tau c_R T div v / (theta c0), c_R = x1 x2 (theta / T)^2, c0 = 3/2 + c_R; the equilibrium state of the same
   n and e is warmer by theta delta / c0, so eta_b = p tau c_R / c0^2 with p = n T.
'''),
    ('''    res = {"viscosity": c["viscosity"] * s, "thermal_conductivity": lam / s,
           "gap_conductivity": lf * (lf + lR) / (lf + lR * F)}''',
     '''    cR = x1 * (1.0 - x1) * (theta / T) ** 2
    res = {"viscosity": c["viscosity"] * s, "bulk_viscosity": vals["N"] * T * vals["TAU"] * cR / (1.5 + cR) ** 2,
           "thermal_conductivity": lam / s, "gap_conductivity": lf * (lf + lR) / (lf + lR * F)}'''),
])

edit("solution/solve.sh", [
    ('''# The oracle: installs the reference program (solution/transport.py, which computes the three coefficients from the''',
     '''# The oracle: installs the reference program (solution/transport.py, which computes the four coefficients from the'''),
    ('''assert sorted(got) == ["gap_conductivity", "thermal_conductivity", "viscosity"], sorted(got)''',
     '''assert sorted(got) == ["bulk_viscosity", "gap_conductivity", "thermal_conductivity", "viscosity"], sorted(got)'''),
])

edit("tests/test_outputs.py", [
    ('''tests/expected.json, the exact reduced viscosity, thermal conductivity and gap conductivity of each set, written by''',
     '''tests/expected.json, the exact reduced viscosity, bulk viscosity, thermal conductivity and gap conductivity of each
set, written by'''),
    ('''QUANTITIES = ["viscosity", "thermal_conductivity", "gap_conductivity"]''',
     '''QUANTITIES = ["viscosity", "bulk_viscosity", "thermal_conductivity", "gap_conductivity"]'''),
    ('''    exactly the three members, each a JSON number."""''', '''    exactly the four members, each a JSON number."""'''),
    ('''    JSON object with the three quantities as JSON numbers, and transport.py is a regular file within the size limit."""''',
     '''    JSON object with the four quantities as JSON numbers, and transport.py is a regular file within the size limit."""'''),
    ('''def test_thermal_conductivity():''',
     '''def test_bulk_viscosity():
    """R1-R3, R8, R9, R13, R14, R16, R17, R20, R21, R23, R27-R31, R35, R36: the reduced bulk viscosity of the
    finite-rate conversion at every set."""
    quantity("bulk_viscosity")


def test_thermal_conductivity():'''),
])

edit("instruction.md", [
    ('''The quantities are the shear viscosity `η`, the thermal conductivity `λ` and the gap conductivity `λ_gap` of the gas''',
     '''The quantities are the shear viscosity `η`, the bulk viscosity `η_b`, the thermal conductivity `λ` and the gap
conductivity `λ_gap` of the gas'''.replace("\n", " ")),
    ('''`η` is the viscosity of the gas at the equilibrium composition for its temperature `T`.''',
     '''`η` is the viscosity of the gas at the equilibrium composition for its temperature `T`. `η_b` belongs to the gas
in a uniform expansion at a small constant rate `∇·v`, with no gradient of temperature or composition and no heat
exchanged: once the expansion has gone on for many times `τ`, the mean of the three normal pressures is
`p_e - η_b ∇·v` to first order in `∇·v`, where `p_e` is the pressure that the gas would have in thermal equilibrium,
its composition included, at the same number density and the same energy per unit volume.'''.replace("\n", " ")),
    ('''the reduced viscosity `η σ^2 / sqrt(m ε)`, the reduced thermal conductivity `λ σ^2 sqrt(m / ε) / k_B` and the''',
     '''the reduced viscosity `η σ^2 / sqrt(m ε)`, the reduced bulk viscosity `η_b σ^2 / sqrt(m ε)`, the reduced thermal
conductivity `λ σ^2 sqrt(m / ε) / k_B` and the'''.replace("\n", " ")),
    ('''exactly one JSON object with exactly three members, each a JSON number: `viscosity`, the reduced viscosity, ''',
     '''exactly one JSON object with exactly four members, each a JSON number: `viscosity`, the reduced viscosity,
`bulk_viscosity`, the reduced bulk viscosity, '''.replace("\n", " ")),
    ('''and compares each of the 24 numbers with the exact value; it accepts a number only when the two differ by at most
2e-5 times the exact value, and all 24 must be accepted.'''.replace("\n", " "),
     '''and compares each of the 32 numbers with the exact value; it accepts a number only when the two differ by at most
2e-5 times the exact value, and all 32 must be accepted.'''.replace("\n", " ")),
])
print("ok")
