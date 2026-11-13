# v15 candidate (drafted 2026-11-05 12:25 UTC, during v14's wait; used only if v14 is 3/3)

Same gases, levels, potential, quantum scattering and frozen Chapman-Enskog machinery as v13/v14. The same eight
(G, A, L, B, T) sets, whose brackets are cached in work/chapman-enskog-transport/v10/cache (seconds to recompute).

New physics: finite conversion rate between two parallel walls a distance d apart, at T + dT/2 and T - dT/2
(dT -> 0). The walls neither absorb nor emit molecules and do not convert them; a catalyst spread uniformly through
the gas relaxes the J = 1 fraction at the rate -(x2 - x2e(T_local)) / tau. The gas is a continuum obeying the
first-order flux laws up to the walls, with no temperature jump. Output: the gap conductivity q d / dT.

Derivation (reduced units, k_B = 1; species 1 = J = 0; psi = x1 - x1e(T); D = D12 = (n D12) / n):
  J1 = -n D (psi' + a T'),  a = dx1e/dT + x1 x2 alpha_T / T = -(x1 x2 / T)(theta / T - alpha_T)
  q  = -lambda_f T' + b J1,  b = T alpha_T - theta          (uniform in the steady state)
  J1' = -n psi / tau;  walls: J1 = 0
  => lambda_R = n D a b = n D12 x1 x2 (theta / T - alpha_T)^2 (the v13 term)
  => psi'' = kappa^2 psi with kappa^2 = (1 + lambda_R / lambda_f) / (D tau)   <- the trap: not 1 / (D tau)
  => lambda_gap = lambda_f (lambda_f + lambda_R) / (lambda_f + lambda_R F),  F = tanh(kappa d / 2) / (kappa d / 2)
Limits: F -> 1 (slow conversion or narrow gap) gives lambda_f; F -> 0 gives lambda_f + lambda_R (v13).

Inputs to add: N = n sigma^3, W = d / sigma, TAU = tau sqrt(epsilon / (m sigma^2)) (H2 mass m), chosen per set so that
kappa d is about 1 to 10. Keep `viscosity` and `thermal_conductivity` (v13, fast conversion), add `gap_conductivity`.
Independent check for checks.txt: solve the coupled linear BVP (T, psi) numerically (finite differences or
scipy solve_bvp) and compare with the closed form.
