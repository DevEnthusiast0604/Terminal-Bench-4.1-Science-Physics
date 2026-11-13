# pass@3 report: chapman-enskog-transport v12

Zip `work/chapman-enskog-transport/v12/pass3/pass3.zip`; provenance task digest `sha256:6385ddbafaea94bd8a46b4341edf8d9c4fd60935aeebc1bbb5eba52a349a39ce`. Tolerance: rtol 2e-05, thermal_diffusion_factor atol 1e-06.

| attempt | reward | tests | agent start | agent | verifier | episodes | cost | worst error / tolerance | program |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | all passed | 05:46 | 40 min | 7.6 min | 82 | $1.91 | 0.0621 at k08 thermal_diffusion_factor | 308 lines |
| 2 | 1 | all passed | 05:46 | 38 min | 12.7 min | 66 | $1.29 | 0.00818 at k08 thermal_diffusion_factor | 299 lines |
| 3 | 1 | all passed | 05:46 | 55 min | 27.0 min | 100 | $1.76 | 0.037 at k08 thermal_diffusion_factor | 300 lines |

Worst error per case as a fraction of the tolerance (quantity in brackets):

| case | a1 | a2 | a3 |
|---|---|---|---|
| k01 | 7.02e-05 (thermal_conductivity) | 8.61e-05 (thermal_diffusion_factor) | 0.00134 (thermal_diffusion_factor) |
| k02 | 0.00206 (thermal_diffusion_factor) | 0.00395 (thermal_diffusion_factor) | 0.00411 (thermal_diffusion_factor) |
| k03 | 3.07e-05 (thermal_diffusion_factor) | 0.000266 (thermal_diffusion_factor) | 2.19e-05 (thermal_diffusion_factor) |
| k04 | 0.0196 (thermal_diffusion_factor) | 0.00267 (thermal_diffusion_factor) | 0.0026 (thermal_diffusion_factor) |
| k05 | 9.36e-06 (viscosity) | 4.84e-05 (thermal_conductivity) | 2.03e-06 (binary_diffusion) |
| k06 | 2.63e-05 (binary_diffusion) | 2.15e-05 (thermal_diffusion_factor) | 8.2e-05 (thermal_diffusion_factor) |
| k07 | 0.000884 (thermal_diffusion_factor) | 0.00106 (thermal_diffusion_factor) | 0.000847 (thermal_diffusion_factor) |
| k08 | 0.0621 (thermal_diffusion_factor) | 0.00818 (thermal_diffusion_factor) | 0.037 (thermal_diffusion_factor) |
| k09 | 0.00558 (thermal_diffusion_factor) | 0.000175 (thermal_diffusion_factor) | 0.000115 (thermal_diffusion_factor) |
| k10 | 5.12e-05 (thermal_diffusion_factor) | 0.000314 (thermal_diffusion_factor) | 2.58e-05 (thermal_diffusion_factor) |

Keyword counts in each final program:

| keyword | a1 | a2 | a3 |
|---|---|---|---|
| nuclear | 0 | 0 | 0 |
| spin | 0 | 0 | 0 |
| ortho | 1 | 1 | 0 |
| para | 1 | 1 | 0 |
| fermion | 0 | 0 | 0 |
| boson | 1 | 0 | 0 |
| degenera | 0 | 0 | 0 |
| sublevel | 0 | 0 | 0 |
| weight | 4 | 3 | 6 |
| symmetr | 0 | 0 | 0 |
| resonan | 2 | 4 | 3 |
| brentq | 0 | 0 | 0 |
| Sonine | 2 | 1 | 2 |

Controls: nop 0, oracle-1 1, tamper-forge-reward 0, verifier-repeat-1 1, verifier-repeat-2 1, wrong-add-key 1, wrong-add-wrong-element 1, wrong-drop-record 1, wrong-perturb-number 1

Digests: `work/chapman-enskog-transport/v12/attempts/attempt-K.txt`; programs (copied, not run): `work/chapman-enskog-transport/v12/attempts/programs/aK/`.
