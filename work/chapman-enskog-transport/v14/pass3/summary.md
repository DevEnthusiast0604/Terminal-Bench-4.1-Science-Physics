# pass@3 report: chapman-enskog-transport v14

Zip `work/chapman-enskog-transport/v14/pass3/pass3.zip`; provenance task digest `sha256:1dc49ebfccf21c897185927f76d3a4c23d16bf60ed857b672af233d2e1f1c0cc`. Tolerance: rtol 2e-05.

| attempt | reward | tests | agent start | agent | verifier | episodes | cost | worst error / tolerance | program |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 1 | all passed | 18:18 | 98 min | 10.8 min | 100 | $1.51 | 9.38e-05 at k07 thermal_conductivity | 30079 lines |
| 2 | 1 | all passed | 18:18 | 46 min | 7.5 min | 81 | $1.60 | 7.24e-05 at k01 thermal_conductivity | 281 lines |
| 3 | 1 | all passed | 18:18 | 38 min | 7.6 min | 84 | $1.56 | 0.000391 at k03 thermal_conductivity | 188 lines |

Worst error per case as a fraction of the tolerance (quantity in brackets):

| case | a1 | a2 | a3 |
|---|---|---|---|
| k01 | 2.43e-05 (thermal_conductivity) | 7.24e-05 (thermal_conductivity) | 0.000322 (thermal_conductivity) |
| k02 | 1.35e-05 (viscosity) | 9.85e-06 (viscosity) | 4.48e-05 (thermal_conductivity) |
| k03 | 1.42e-05 (thermal_conductivity) | 1.49e-05 (thermal_conductivity) | 0.000391 (thermal_conductivity) |
| k04 | 1.54e-05 (thermal_conductivity) | 5.2e-06 (viscosity) | 9.51e-05 (thermal_conductivity) |
| k05 | 1.22e-06 (viscosity) | 1.37e-05 (viscosity) | 1.45e-05 (viscosity) |
| k06 | 2.11e-05 (thermal_conductivity) | 2.54e-05 (thermal_conductivity) | 4.46e-05 (thermal_conductivity) |
| k07 | 9.38e-05 (thermal_conductivity) | 3.8e-06 (thermal_conductivity) | 0.000239 (thermal_conductivity) |
| k08 | 1.44e-05 (viscosity) | 3.31e-05 (viscosity) | 1.85e-05 (viscosity) |

Keyword counts in each final program:

| keyword | a1 | a2 | a3 |
|---|---|---|---|
| Dufour | 0 | 0 | 0 |
| alpha | 0 | 10 | 0 |
| thermal_diffusion | 0 | 0 | 0 |
| kT | 1727 | 2028 | 7116 |
| k_T | 14 | 25 | 92 |
| Onsager | 0 | 0 | 0 |
| Butler | 0 | 0 | 0 |
| Brokaw | 0 | 0 | 0 |
| reacting | 0 | 0 | 0 |
| conversion | 1 | 0 | 0 |
| theta | 0 | 0 | 0 |
| dx1 | 12 | 32 | 87 |
| equilibrium | 2 | 1 | 1 |

Controls: nop 0, oracle-1 1, tamper-forge-reward 0, verifier-repeat-1 1, verifier-repeat-2 1, wrong-add-key 1, wrong-add-wrong-element 1, wrong-drop-record 1, wrong-perturb-number 1

Digests: `work/chapman-enskog-transport/v14/attempts/attempt-K.txt`; programs (copied, not run): `work/chapman-enskog-transport/v14/attempts/programs/aK/`.
