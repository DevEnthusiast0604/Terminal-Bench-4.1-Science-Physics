# pass@3 report: chapman-enskog-transport v9

Zip `work/chapman-enskog-transport/v9/pass3/pass3.zip`; provenance task digest `sha256:59b4393f91efae36f73fdbc4020f25a49b10d5ae333861d519b467292afdb878`. Tolerance: rtol 2e-05, thermal_diffusion_factor atol 1e-06.

| attempt | reward | tests | agent start | agent | verifier | episodes | cost | worst error / tolerance | program |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | all passed | 19:26 | 28 min | 28.1 min | 58 | $0.99 | 0.0136 at k10 thermal_diffusion_factor | 221 lines |
| 2 | 1 | all passed | 19:26 | 62 min | 35.7 min | 100 | $2.27 | 0.0223 at k09 thermal_diffusion_factor | 191 lines |
| 3 | 1 | all passed | 19:26 | 72 min | 23.5 min | 100 | $2.12 | 0.0102 at k09 thermal_diffusion_factor | 197 lines |

Worst error per case as a fraction of the tolerance (quantity in brackets):

| case | a1 | a2 | a3 |
|---|---|---|---|
| k01 | 0.0105 (thermal_diffusion_factor) | 0.0116 (thermal_diffusion_factor) | 0.00512 (thermal_diffusion_factor) |
| k02 | 0.000591 (thermal_diffusion_factor) | 0.000693 (binary_diffusion) | 0.000377 (binary_diffusion) |
| k03 | 0.000396 (thermal_diffusion_factor) | 0.000217 (thermal_diffusion_factor) | 0.000141 (thermal_diffusion_factor) |
| k04 | 0.000191 (thermal_diffusion_factor) | 2.29e-05 (thermal_diffusion_factor) | 0.000842 (thermal_diffusion_factor) |
| k05 | 0.00122 (thermal_diffusion_factor) | 0.00273 (thermal_diffusion_factor) | 0.00189 (thermal_diffusion_factor) |
| k06 | 0.000151 (thermal_diffusion_factor) | 0.000309 (thermal_diffusion_factor) | 0.000272 (thermal_diffusion_factor) |
| k07 | 0.000143 (thermal_conductivity) | 1.29e-05 (viscosity) | 1.67e-06 (thermal_diffusion_factor) |
| k08 | 0.0032 (binary_diffusion) | 1.7e-05 (thermal_diffusion_factor) | 1.59e-05 (thermal_diffusion_factor) |
| k09 | 0.00124 (thermal_diffusion_factor) | 0.0223 (thermal_diffusion_factor) | 0.0102 (thermal_diffusion_factor) |
| k10 | 0.0136 (thermal_diffusion_factor) | 0.00793 (thermal_diffusion_factor) | 0.00596 (thermal_diffusion_factor) |

Keyword counts in each final program:

| keyword | a1 | a2 | a3 |
|---|---|---|---|
| resonan | 3 | 3 | 6 |
| bisect | 0 | 0 | 0 |
| adaptive | 1 | 1 | 2 |
| quad | 4 | 3 | 0 |
| breit | 0 | 0 | 0 |
| wigner | 0 | 0 | 0 |
| numerov | 1 | 0 | 0 |
| log_deriv | 0 | 0 | 0 |
| brentq | 3 | 2 | 2 |
| mpmath | 0 | 0 | 0 |

Controls: nop 0, oracle-1 1, tamper-forge-reward 0, verifier-repeat-1 1, verifier-repeat-2 1, wrong-add-key 1, wrong-drop-record 1, wrong-perturb-number 1

Digests: `work/chapman-enskog-transport/v9/attempts/attempt-K.txt`; programs (copied, not run): `work/chapman-enskog-transport/v9/attempts/programs/aK/`.
