"""README of the v15 draft: the bulk viscosity. Not shipped."""
import sys

p = sys.argv[1]
s = open(p, encoding="utf-8").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:90]
    s = s.replace(old, new)


rep('''constant B from 1 to 3 and reduced temperature from 0.2 to 0.6, and with a density, a gap width and a relaxation time
for the third quantity (R13).''',
    '''constant B from 1 to 3 and reduced temperature from 0.2 to 0.6, and with a density, a gap width and a relaxation time
for the bulk viscosity and the gap conductivity (R13).''')
rep('''  counter-diffusion in turn (the derivation is in the `tests/generate.py` docstring). Over the graded sets kappa d runs from 2.2 to 9.2, and lambda_gap lies 0.63 % to
  24 % above lambda_f and 0.53 % to 27 % below lambda (`[gap]` in `tests/checks.txt`).''',
    '''  counter-diffusion in turn (the derivation is in the `tests/generate.py` docstring). Over the graded sets kappa d
  runs from 2.2 to 9.2, and lambda_gap lies 0.63 % to 24 % above lambda_f and 0.53 % to 27 % below lambda (`[gap]` in
  `tests/checks.txt`).''')
rep('''  band at six of the eight sets.
- **The steady state with fast conversion.**''',
    '''  band at six of the eight sets.
- **The bulk viscosity of a finite conversion rate, from the stated rate law rather than a remembered formula.** In a
  uniform expansion the temperature falls, the equilibrium composition with it, and the composition lags behind by an
  amount proportional to tau; the mean normal pressure n k_B T then falls short of the pressure of the equilibrium
  state of the same density and energy (R35). That gives eta_b = p tau c_R / (3/2 + c_R)^2 with
  c_R = x1 x2 (theta / T*)^2. Two choices decide it. tau is the instruction's relaxation time at the local, changing
  temperature (R9): at fixed energy the composition relaxes faster, with tau 3/2 / (3/2 + c_R), and the form that
  takes tau as that time is off by 1361 to 64793 tolerances. Only the translational heat capacity 3/2 is frozen,
  because collisions keep the rotational levels (R29): a frozen heat capacity of 5/2, as for a rotating molecule, is
  off by 19971 to 31612 tolerances (`[bulk]` in `tests/checks.txt`).
- **The steady state with fast conversion.**''')
rep('''both the diffusion law and the Dufour term. An expert who already knows this route''',
    '''both the diffusion law and the Dufour term, and the bulk viscosity follows from the lag of the composition at the
stated rate law with only the translational heat capacity frozen. An expert who already knows this route''')
rep('''tau* = 500000), as a self-check of its output. The program computes the three coefficients from the stated physics''',
    '''tau* = 500000), as a self-check of its output. The program computes the four coefficients from the stated physics''')
rep('''   lambda_gap = lambda_f lambda / (lambda_f + lambda_R F), F = tanh(kappa d / 2) / (kappa d / 2) (`main`).
''',
    '''   lambda_gap = lambda_f lambda / (lambda_f + lambda_R F), F = tanh(kappa d / 2) / (kappa d / 2) (`main`).
9. **Bulk viscosity.** eta_b = p tau c_R / (3/2 + c_R)^2 with p = n k_B T and c_R = x1 x2 (theta / T*)^2, in
   reduced units N T* TAU c_R / (3/2 + c_R)^2 from the program's inputs (`main`).
''')
rep('''symmetry of like collisions, and that walls which do not convert stop that counter-diffusion within a layer whose
thickness the coupled flux laws set.''',
    '''symmetry of like collisions, that walls which do not convert stop that counter-diffusion within a layer whose
thickness the coupled flux laws set, and that the same finite rate makes the gas resist expansion through the lag of
its composition.''')
rep('''`tests/expected.json` holds the 24 values: the viscosity, the thermal conductivity and the gap conductivity at each
of the eight graded sets,''',
    '''`tests/expected.json` holds the 32 values: the viscosity, the bulk viscosity, the thermal conductivity and the gap
conductivity at each of the eight graded sets,''')
rep('''weights of `SPECIES` in `tests/qmix.py`, and the two conductivities with conversion (`combine`); its docstring derives
both formulas.''',
    '''weights of `SPECIES` in `tests/qmix.py`, and the bulk viscosity and the two conductivities with conversion (`bulk`,
`combine`); its docstring derives the three formulas.''')
rep('''  factor, alone and in the first-order form lambda_f + lambda_R (1 - F), in tolerances.
''',
    '''  factor, alone and in the first-order form lambda_f + lambda_R (1 - F), in tolerances.
- `[bulk]`: the uniform expansion itself, integrated by scipy's DOP853 from equilibrium for 30 tau on the stated
  energy balance and rate law with nothing linearized, gives (p_e - p) / div v. Extrapolated to a vanishing rate from
  tau div v = 1e-6, 2e-6 and 4e-6, it agrees with the bulk viscosity of `combine` to 5.1e-13 at all eight sets. The
  same lines give c_R and the errors of the two other choices above, in tolerances.
''')
rep('''- `[P]`: Sonine indices up to 16, 20 (the oracle's) and 22 differ from 24 by at most 0.0001 tolerances over the 24
  graded values.''',
    '''- `[P]`: Sonine indices up to 16, 20 (the oracle's) and 22 differ from 24 by at most 0.0001 tolerances over the 32
  graded values.''')
rep('''24 values with a second complete implementation:''', '''32 values with a second complete implementation:''')
rep('''quadrature, angular rule, Sonine truncation or solver for the layer, and each changes''',
    '''quadrature, angular rule, Sonine truncation or solver for the layer or the expansion, and each changes''')
rep('''`tests/test_outputs.py` runs four tests. Each first checks that `transport.py` is a regular file and then reads the
program's run on all eight sets, so a missing program, a failed run or a malformed output fails all four:''',
    '''`tests/test_outputs.py` runs five tests. Each first checks that `transport.py` is a regular file and then reads the
program's run on all eight sets, so a missing program, a failed run or a malformed output fails all five:''')
rep('''with exactly `viscosity`, `thermal_conductivity` and `gap_conductivity`, all JSON numbers;''',
    '''with exactly `viscosity`, `bulk_viscosity`, `thermal_conductivity` and `gap_conductivity`, all JSON numbers;''')
rep('''| `test_thermal_conductivity` | R1-R3, R5, R6, R8-R17, R20-R31 |''',
    '''| `test_bulk_viscosity` | R1-R3, R8, R9, R13, R14, R16, R17, R20, R21, R23, R27-R31, R35, R36 | the eight reduced bulk viscosities of the finite-rate conversion at the set's density and relaxation time, the same way |
| `test_thermal_conductivity` | R1-R3, R5, R6, R8-R17, R20-R31 |''')
open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
