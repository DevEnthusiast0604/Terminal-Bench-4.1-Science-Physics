"""Edits the v15 draft's oracle (solution/transport.py, solve.sh) for the gap conductivity. Not shipped."""
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


edit("solution/transport.py", [
    ('''"""Reference program: the shear viscosity and the steady-state thermal conductivity of dilute H2 or D2 whose
ortho-para conversion keeps the populations of J = 0 and J = 1 at local equilibrium, from the Chapman-Enskog solution
for the binary mixture of the two levels (GASES), whose molecules interact through one Kihara potential and differ in
the exchange symmetry of their like collisions, with quantum-mechanical cross sections, computed from the potential
alone. Run as
    python3 transport.py G A L B T
(gas H2 or D2, core ratio a / sigma 0 to 0.5, quantum parameter Lambda* = h / (sigma sqrt(m epsilon)) with m the H2
mass 0.8 to 2.8, reduced rotational constant B of H2 1 to 3, reduced temperature T* 0.2 to 0.6); it prints one JSON
object (the two reduced coefficients, with the mass m) on stdout and its progress on stderr. Inside, species 1 is the
J = 0 level and sigma, epsilon, k_B, the molecule's mass and the number density are 1 (main converts).''',
     '''"""Reference program: the shear viscosity, the steady-state thermal conductivity at fast ortho-para conversion and
the conductivity of a layer between two non-catalytic walls at a finite conversion rate, of dilute H2 or D2, from the
Chapman-Enskog solution for the binary mixture of the levels J = 0 and J = 1 (GASES), whose molecules interact
through one Kihara potential and differ in the exchange symmetry of their like collisions, with quantum-mechanical
cross sections, computed from the potential alone. Run as
    python3 transport.py G A L B T N W TAU
(gas H2 or D2, core ratio a / sigma 0 to 0.5, quantum parameter Lambda* = h / (sigma sqrt(m epsilon)) with m the H2
mass 0.8 to 2.8, reduced rotational constant B of H2 1 to 3, reduced temperature T* 0.2 to 0.6, reduced density
n sigma^3 0.001 to 0.01, gap d / sigma 1000 to 100000, relaxation time tau sqrt(epsilon / (m sigma^2)) 10000 to
10000000); it prints one JSON object (the three reduced coefficients, with the mass m) on stdout and its progress on
stderr. Inside, species 1 is the J = 0 level and sigma, epsilon, k_B, the molecule's mass and the number density are 1
(main converts).'''),
    ('''   lambda = lambda_f + n D12 x1 x2 (theta / T - alpha_T)^2 (all frozen coefficients at the equilibrium x1).
''',
     '''   lambda = lambda_f + n D12 x1 x2 (theta / T - alpha_T)^2 (all frozen coefficients at the equilibrium x1).
7. Gap: between walls that neither pass nor convert molecules the deviation psi = x1 - x1e(T) relaxes as
   J1' = -n psi / tau, with J1 = -n D12 (psi' + a T'), a = -(x1 x2 / T)(theta / T - alpha_T), and the uniform energy
   flux q = -lambda_f T' + (T alpha_T - theta) J1, so n D12 a (T alpha_T - theta) = lambda_R = lambda - lambda_f;
   J1 = 0 at both walls. Eliminating T' gives psi'' = kappa^2 psi with kappa^2 = (1 + lambda_R / lambda_f) n /
   (n D12 tau), not n / (n D12 tau), and lambda_gap = q d / dT = lambda_f lambda / (lambda_f + lambda_R F) with
   F = tanh(kappa d / 2) / (kappa d / 2): lambda_f for a thin gap or slow conversion, lambda for a wide one.
'''),
    ('''RANGES = {"A": (0.0, 0.5), "L": (0.8, 2.8), "B": (1.0, 3.0), "T": (0.2, 0.6)}  # the instruction's''',
     '''RANGES = {"A": (0.0, 0.5), "L": (0.8, 2.8), "B": (1.0, 3.0), "T": (0.2, 0.6), "N": (0.001, 0.01),
          "W": (1000.0, 100000.0), "TAU": (10000.0, 10000000.0)}  # the instruction's'''),
    ('''    if len(argv) != 5 or argv[0] not in GASES:
        sys.exit("usage: python3 transport.py G A L B T   (gas %s, core ratio, Lambda* with the H2 mass, reduced "
                 "rotational constant of H2, T*)" % " or ".join(GASES))
    vals = dict(zip("ALBT", (float(v) for v in argv[1:])))''',
     '''    if len(argv) != 8 or argv[0] not in GASES:
        sys.exit("usage: python3 transport.py G A L B T N W TAU   (gas %s, core ratio, Lambda* with the H2 mass, "
                 "reduced rotational constant of H2, T*, n sigma^3, d / sigma, reduced tau)" % " or ".join(GASES))
    vals = dict(zip(("A", "L", "B", "T", "N", "W", "TAU"), (float(v) for v in argv[1:])))'''),
    ('''    s = math.sqrt(m1)                # back to the H2 mass m
    res = {"viscosity": c["viscosity"] * s, "thermal_conductivity": lam / s}''',
     '''    s = math.sqrt(m1)                # back to the H2 mass m
    lf, lR, D = lam_f / s, (lam - lam_f) / s, nD12 / s / vals["N"]      # D = n D12 / n, reduced
    kd = math.sqrt((1.0 + lR / lf) / (D * vals["TAU"])) * vals["W"]
    F = math.tanh(kd / 2.0) / (kd / 2.0)
    log("kappa d %.6g, F %.6g" % (kd, F))
    res = {"viscosity": c["viscosity"] * s, "thermal_conductivity": lam / s,
           "gap_conductivity": lf * (lf + lR) / (lf + lR * F)}'''),
])
edit("solution/solve.sh", [
    ('''# The oracle: installs the reference program (solution/transport.py, which computes the two coefficients from the
# potential, the masses, the nuclear spins, the rotational constant and Lambda* alone, for either gas and any core
# ratio, Lambda*, rotational constant and reduced temperature of the instruction's ranges) as''',
     '''# The oracle: installs the reference program (solution/transport.py, which computes the three coefficients from the
# potential, the masses, the nuclear spins, the rotational constant, Lambda*, the density, the gap and the relaxation
# time alone, for either gas and any set of the instruction's ranges) as'''),
    ('python3 /app/output/transport.py D2 0.25 1.5 2.5 0.4 > "$check/out.json"',
     'python3 /app/output/transport.py D2 0.25 1.5 2.5 0.4 0.005 10000 500000 > "$check/out.json"'),
    ('''assert sorted(got) == ["thermal_conductivity", "viscosity"], sorted(got)
assert all(isinstance(v, float) for v in got.values()), got
assert all(got[k] > 0 for k in ("thermal_conductivity", "viscosity")), got
print("D2, a/sigma = 0.25, Lambda* = 1.5, B = 2.5, T* = 0.4: %s" % got)''',
     '''assert sorted(got) == ["gap_conductivity", "thermal_conductivity", "viscosity"], sorted(got)
assert all(isinstance(v, float) for v in got.values()), got
assert all(got[k] > 0 for k in got), got
print("D2, a/sigma = 0.25, Lambda* = 1.5, B = 2.5, T* = 0.4, n sigma^3 = 0.005, d/sigma = 10000, tau* = 500000: %s"
      % got)'''),
])
print("ok")
