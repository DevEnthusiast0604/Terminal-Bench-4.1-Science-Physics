# Physics task state (TB4)

The revision history that `TB4_PHYSICS_PROMPT.md` asks for (user, 2026-10-30), kept for the active Science → Physics
task. It condenses `logs/chapman-enskog-transport.md`, where the full evidence and paths live. Entries are added,
never edited (user rule, 2026-10-29). Times are UTC.

## Task identity

| Field | Value |
|---|---|
| Slug | `chapman-enskog-transport` |
| Source | `tasks/active/chapman-enskog-transport/` (output task: data file v1–v3, program `transport.py` from v4) |
| Category | Science / Physics |
| Platform ID | T-0851 (first submitted 2026-10-28 13:37) |
| DAS Task ID | 3972746 |
| Toolkit | tb4 3.3.0 |
| Target | quick check PASS; platform controls oracle 1, nop 0, cheat 0; pass@3 1/3 or 2/3 |
| P3 IDs pasted into DAS | none yet |

## Revisions

| Rev | Uploaded | Task digest | What the version is | Quick check | pass@3 |
|---|---|---|---|---|---|
| v1 | 10-28 13:37 (submit) | `241a593f…80b5` | pure Kihara gas, a/σ 0.5; η, λ, n·D at six disclosed T* (0.3–100) in `/app/output/transport.json`; 2e-5 relative | did not finish (job 9614): "tests/checks.txt: missing canary string"; extra 5/5 | not run |
| v2 | 10-28 13:52 | `66e1ff90…0be5` | v1 + canary line in `tests/checks.txt` | 32/36, 1 FAIL `instruction_concision` (sentence listing Python, numpy, scipy, sympy, mpmath); 3 TO SETTLE from controls outside the run's scope (job 9640) | not run |
| v3 | 10-28 15:00 | `9c802bdc…a142` | v2 without the library sentence | PASS, all 39 (job 9784) | **3/3**, too easy |
| v4 | 10-29 03:14 | `38e4657f…57bc` | program `transport.py A T` for the whole family (A 0–0.8, T* 0.1–500); η, λ, n·D on ten hidden pairs; Python only, 600 s per run | PASS, 38/39 (job 10901; 33 pass, 1 N/A, `novel` deferred; extra 5/5) | **3/3**, too easy |
| v5 | 10-29 18:28 | `29e8e53c…6faf` | binary Kihara mixture, unequal masses: `transport.py A R X T`; η, λ, n·D12, αT on ten hidden sets | queued since 18:28 | pending |
| v5 (result) | — | `29e8e53c…6faf` | as above | 37/40, 1 FAIL `solvable` on the 16 h expert estimate (job 11859, 10-30 16:24, after 18 h 25 min in the queue) | not run |
| v6 | 10-30 16:32 | `305a96a1…a911` | v5 with expert time 6 h, README key-realization sentence, deliverable path `/app/output/transport.py` | queued since 16:32 | pending |
| v6 (result) | — | `305a96a1…a911` | as above | PASS 38/40 (job 12517; 33 pass, 1 N/A, `novel` to the reviewer; extra 5/5) | **3/3**, too easy (11-01) |
| v7 | 11-02 15:46 | `b0e25c78…55f5` | v6 with R 1–100 and x1 0.001–0.95; k01, k02 and k04 at the dilute-light corner, graded at P = 128 on a split energy grid; raw P = 64 misses k01 αT by 1.79 tolerances | queued since 15:46 | pending |
| v7 (result) | — | `b0e25c78…55f5` | as above | PASS 38/40 (job 15102; 33 pass, 1 N/A, `novel` to the reviewer; extra 5/5) | **3/3**, too easy (11-03 02:03) |

## Revision records

- **v1–v2: harness fixes, no physics change.** The canary was missing from a generated evidence file, and one
  instruction sentence named the installed libraries. Each was fixed with the smallest edit.
- **v3: solved 3/3** (job 9784).
  - What the agents did: 21–31 min each. All three compiled a C++ scattering code with g++ (one through OpenMP and
    ctypes). They computed the brackets numerically (attempt 2 by Gauss quadrature over the centre-of-mass velocity)
    and used 8–12 Sonine terms, checked by doubling the terms and the grid and by hard-sphere limits.
  - Worst errors 4.1e-9 to 3.0e-8, about 1000× inside 2e-5.
  - Why it was easy: one disclosed gas at six disclosed temperatures. The agents specialised to that point, and every
    part of the computation could be self-checked.
  - Change for v4: a program for the whole family, graded on hidden pairs, in Python only, within 600 s per run.
- **v4: solved 3/3 again** (job 10901). Every control in the download behaved: oracle, nop, tamper, wrong-answer
  mutations, verifier repeats.
  - What the agents did: 23–32 min each. Pure numpy/scipy programs of 200–253 lines: a Galerkin Sonine formulation
    with numerical brackets, 12–16 terms, scattering in the turning radius with explicit orbiting branches. Self-checks
    at the ends of each range: hard-sphere normalisation, independent χ quadrature, grid and basis doubling.
  - The agents measured 18–66 s per pair against the 600 s limit.
  - Worst errors 8.8e-9 to 7.1e-7, 30–2000× inside the tolerance.
  - Why the v4 change was insufficient: generality, hidden cases and the Python-only limit added no failure mode. A
    fully specified computation whose parts all self-check is "applying a general method", and the series converged
    geometrically, so doubling checks were reliable.
  - Reasoning requirement changed for v5: judging convergence of an expansion that converges algebraically and looks
    converged early, with mixture brackets of high order and four coefficients that each have their own definition
    and sign convention.
- **v5: hypothesis under test.**
  - Central physics challenge: for a dilute light species among heavy molecules the Sonine series converges
    algebraically. At `k01` the αT increment falls as P^-5.25. Raw truncation needs P ≥ 42 for all 40 graded values,
    and stopping when the four-index increment is inside the tolerance leaves 7/40 outside (`k07` αT 24 tolerances
    off). Reaching that order needs mixture brackets that stay accurate past index 40: the Ω-sum route cancels by
    1e13–1e17 and fails above P ≈ 16 in float64. A justified tail estimate is the alternative.
  - Evidence: `tests/checks.txt` [conv], [kernels], [isotropic].
  - Interacting parts:
    - λ is the heat flux at equal mean velocities;
    - the momentum condition for D12 and αT;
    - the αT sign convention: inverted sign at `k05`, zero at `k08` (equal masses);
    - orbiting at low T*.
  - Risks to read for in pass@3:
    - v3's attempt 2 already found the stable quadrature route for brackets, so high P may come easily (3/3 again);
    - if attempts fail only on the 600 s limit, that is time pressure, not physics, which `essential_difficulty`
      excludes.
  - Pending for the next revision whatever the result: the README should lead with one sentence naming the central
    challenge (2026-10-28 docs), and the "Accuracy within a time limit" difficulty bullet should be reworded.

## Session events (newest last)

- **2026-10-30 02:10**: file created on the user's instruction to follow `TB4_PHYSICS_PROMPT.md`.
  - Cycle count for its "up to three revision/submission cycles per active session": 0 used, counted from this
    instruction. Uploads on 2026-10-30 UTC so far: 0 of 5.
  - State: v5's quick check is a pending result that cannot be retrieved yet (queued since 10-29 18:28, 7 h 42 min).
    The loop holds, as the prompt requires. A background poller started at 00:47 wakes this session on the next card.
    It runs only while this Claude Code session is open.
  - Next action when a card appears: log it (Seen = no), review it, mark it seen.
    - Quick check PASS: wait for pass@3.
    - Quick check FAIL: fix, lint, scan, package and Upload the fix (cycle 1).
    - pass@3 1–2/3: stop difficulty changes and paste the new P3 ID into DAS 3972746.
    - pass@3 3/3 or 0/3: download the pass@3 zip to `work/chapman-enskog-transport/v5/pass3/` and analyse all three
      trajectories before changing anything.
- **2026-10-30 12:46**: blocker. v5's quick check (job 11859) is still "queued" after 18 h 16 min; the poller saw no
  page change from 00:46 to 12:44. Earlier quick checks waited 36 min (v4) and 2 h 40 min (v3).
  - The Submit page shows no notice: 66 quick checks and 971 pass@3 runs left this week.
  - Not fixable from the task side, and cancelling is a platform action, so this goes to the user.
  - Exact manual action: ask the team lead whether job 11859 is stuck or waiting behind a backlog.
  - If the user decides to replace the check: cancel it and upload v6 with the two pending README changes, as cycle 1.
  - Cycles used 0/3; uploads today 0/5. A new background poller started at 12:46.
- **2026-10-30 16:24**: v5's quick check result. It ran from 12:53 and returned 37/40.
  - The 1 FAIL is `solvable`. The criterion asks that an expert who knows the approach can implement the task in a
    few hours, and task.toml said 16 best-case hours. v3's 10 h and v4's 12 h had passed it.
  - Not a physics or grader defect. The oracle scored 1 on its recorded run, and every difficulty criterion passed:
    `difficult`, `essential_difficulty`, `difficulty_explanation_quality`, `expert_time_estimate`.
  - Static warning `grading_names`: the deliverable was named without `/app/output/`, so the wrong-answers control had
    no mutant.
  - What the result demonstrated: nothing yet about difficulty, because pass@3 did not run.
- **2026-10-30 16:32**: cycle 1 of 3, v6 uploaded with Upload the fix (upload 1 of 5 today).
  - Smallest effective change, three files:
    - expert time 6 h, the honest best case for an expert who knows the route (scattering about 1.5 h, brackets 2 h,
      linear problems 1 h, tail and checks 1.5 h);
    - README: one sentence for the central realization, one for the estimate, the time-limit bullet removed;
    - `tests/grading.json`: deliverables `/app/output/transport.py`.
  - The reviewer's remedy (precomputed scattering and brackets, narrower convergence) was not taken: it would remove
    the central challenge.
  - No physics, test or oracle change, so the v5 hypothesis is still untested.
  - Next action: watch the quick check, then pass@3. Read all three trajectories whatever the result. The background
    poller is running.
- **2026-10-31 04:33**: pending result, platform side.
  - v6's quick check (job 12517) has been "running" since 18:12, 10 h 19 min.
  - Report: INCOMPLETE. Static checks 35/35 (the `grading_names` warning is fixed); the criteria stage shows "error"
    with no reason.
  - v4 once showed the same transient error and finished on its own.
  - Nothing to change in the task, and an identical zip can't be re-run. The loop holds and the background poller
    watches.
  - Manual action if it does not move: the user reports job 12517 to the team lead.
  - Cycles used 1/3; uploads 2026-10-31: 0/5.
- **2026-10-31 16:32**: still blocked. Job 12517 has been "running" for 22 h 19 min with the same criteria-stage
  error; nothing on the platform changed in 12 h.
  - Manual action required: the user reports job 12517 to the team lead.
  - The loop stays stopped as the prompt requires, with no edits and no uploads. The background poller watches for a
    card.
- **2026-10-31 17:46**: background watch stopped at the user's request. Nothing monitors the platform now. Resume with
  a `tools/supertasker.py status T-0851` check when the user asks. State unchanged: v6 job 12517 stuck "running"
  (last checked 16:31). Cycles used 1/3.
- **2026-11-02 11:15**: v6 result, with all three trajectories read. Quick check PASS 38/40, then pass@3 **3/3** on
  Sol 6.1. Both cards are marked seen.
  - What the agents did: 46–63 min each.
    - All three found the stable bracket route: Gauss quadrature over the centre-of-mass velocity with angular
      harmonics; attempt 3 used analytic Hermite integrals.
    - They checked by hard-sphere limits and nested truncations.
    - Their final programs use a fixed 64 functions for heavy mixtures. Attempt 1 is adaptive up to 80. None
      estimates a tail.
  - Worst errors: 0.07–0.17 of the tolerance, all at k01 αT, the hardest set (R 40, x1 0.05). The verifier took
    69–230 s per run against 600 s.
  - Why the v5 hypothesis failed: the algebraic tail exists, but at the edge of the stated range (R ≤ 40) raw P = 64
    is already within 3.5e-6. Brute force at a high fixed order passes, so the convergence judgment was never tested.
  - Change for v7 (cycle 2): the same central challenge made decisive.
    - Stated mass ratios go far enough that raw truncation at the P a 600 s run affords misses αT by several
      tolerances.
    - Only a justified power-law tail, or a much faster bracket code, reaches 2e-5 there.
    - No new outputs, no tighter tolerance.
  - Risks:
    - Agents may calibrate a tail offline with very high P, and pass 3/3 again.
    - The reference needs a high P_REF, and its tail must be checked against an even higher one.
- **2026-11-02 15:46**: cycle 2 of 3. v7 uploaded with Upload the fix (upload 1 of 5 today).
  - Range: R up to 100 (R 200 could not be pinned with P ≤ 128) and x1 down to 0.001.
  - Sets: k01, k02 and k04 graded at P = 128 on the split grid (panels ≤ 0.35 in ln E above max(T*/2, 1.6 E_c)).
  - [conv] at k01 αT: raw P 64 1.79 tolerances, P 80 0.89, P 96 0.47; with the tail at P 64, 0.19. Without a tail,
    all 40 values are inside only from P = 78 on.
  - The reference's limits spread by ≤ 0.049 tolerances.
  - The user asked for no local tests. `checks.txt` was rebuilt from cached units: [precision] covers the seven
    P = 64 sets and [grid] covers k06 only.
  - Stop rule: pending result. Next: check `status T-0851` in the foreground and handle each card.
- **2026-11-03 02:52**: v7 result, with all three trajectories read. Quick check PASS 38/40, then pass@3 **3/3** on
  Sol 6.1. Both cards are marked seen.
  - What the agents did: 46–65 min each. They wrote fast, stable bracket codes: generating-function recurrences
    (a1), or centre-of-mass/relative separation (a2, a3). They used asymmetric light/heavy bases and raised the
    order: a1 to 100, a2 to 160 (up to 224), a3 to 120 (up to 128). All three checked against references of order
    90–140 at exactly the corner (0.8, 100, 0.001, 50). None estimated a tail.
  - Worst errors: 0.40, 0.07 and 0.21 of the tolerance, all at k01 αT.
  - Why the v7 change was insufficient: brute force reaches 100–160 indices in 1–2 minutes, and every value is
    inside from P = 78. The tail judgment never had to be made.
  - Probe (`work/chapman-enskog-transport/v8/explore/lorentz.py`, the Lorentz limit m2 → ∞, x1 → 0): αT needs
    P ≈ 160 at A 0.8, T* 50 and P ≈ 180 at T* 500. The error falls as P^-2.2 out to P = 1024.
  - So no extension of R, x1 or T* takes this computation beyond brute force. The classical-mixture design is
    saturated: v3, v4, v6 and v7 were all 3/3.
  - Next (cycle 3 of 3, the last this session): this needs a redesign of the core challenge (prompt step 5), which
    goes to the user to decide.
- **2026-11-03 03:12**: the user chose "Quantum mixture (Recommended)" for v8, cycle 3 of 3 and the last of this
  session.
  - Same binary Kihara mixture and four outputs. The molecules become light spin-0 bosons, with Λ* =
    h / (σ sqrt(m1 ε)) as a fifth input and T* about 0.2–3.
  - Phase-shift cross sections: symmetrized amplitudes for like pairs, a distinguishable amplitude for the unlike
    pair, and each pair's own reduced mass.
  - Intended discriminator: narrow shape resonances, which an energy grid misses while it still looks converged.
  - Risks:
    - Reference correctness (symmetrization factor, Λ* scaling, high-ℓ and r^-6 tails, completeness of the
      resonance search). Validate with the classical limit at small Λ*, analytic hard-sphere phase shifts and
      convergence in step, range, ℓ and energy grid.
    - A brute-force fine grid could still catch the resonances. Check this before fixing the sets.
- **2026-11-03 05:33**: v8 reference checked in `work/chapman-enskog-transport/v8/explore/` (author self-review).
  - Phase shifts agree with DOP853 to 1e-10–1e-12, with 6th-order step convergence and the right classical limit
    (Λ*² scaling for like and unlike pairs).
  - At A 0.1, R 4, Λ* 0.8, T* 0.3 there are 13 shape resonances (widths 2e-11 to 3e-2). Product integration
    around them equals a direct evaluation to 6.3e-12. P 16 is within 0.03 tolerance of P 32.
  - A dense fixed grid with no resonance handling misses αT by 29–32 tolerances and D12 by 1.5–2.0. The trap is
    real and points the way the design intended.
  - Open: the oracle cost (about 3× too slow for 600 s on 2 CPUs), the ranges and the hidden sets.
- **2026-11-03 08:24**: cycle 3 of 3. v8 uploaded with Upload the fix (upload 1 of 5 today), digest
  `17001fe2…74a1`.
  - Evidence (`tests/checks.txt`): the reference is good to about 0.01 tolerance (P 24 vs P 32 at k10: 0.0082;
    settings: 7.6e-8 relative in Q). The oracle (FAST, P 20) is within 0.06.
  - Trap: without resonance handling, k01–k05 miss by 26–225 tolerances (mostly αT and D12). k07 (R = 1) has
    αT = 3.4e-5, 34 times the floor, because like and unlike collisions differ.
  - Stop rule: if pass@3 comes back 3/3 or 0/3, stop and report (cycle limit); at 1–2/3, paste the P3 ID into DAS
    3972746.
- **2026-11-03 12:21**: v8 defect found before its quick check ran: `tests/checks.txt` has no canary line (static failure, as v1). Fix ready in `tasks/active/`; upload pending the user's choice (cancel v8's queued check and upload now, or wait).
- **2026-11-03 12:25**: no cancel (user). Waiting for v8's quick-check card; then upload the canary fix as v9.
- **2026-11-03 20:54**: v8 quick check (job 15742) failed the static stage on the canary in `tests/checks.txt`, as predicted; extra 5/5 pass; the 35 criteria were blocked, so v9 is their first run on the quantum design. Releasing v9 = v8 + canary fix.
- **2026-11-03 20:55**: v9 uploaded (upload 2 of 5 today), digest `59b4393f…b878`. Canary line restored as line 1 of `tests/checks.txt` (v8's quick check, job 15742, failed the static `check-canary.sh` on it), and `tests/checks.py` main() prints it first. Nothing else changed from v8.
- **2026-11-04 16:47**: v9 quick check passed (card 16:45 on 11-04; page 38 of 40), the first criteria run on the quantum design; pass@3 queued on Sol 6.1.
- **2026-11-04 21:06**: v9 pass@3 = 3/3 (card 21:05, Sol 6.1): the quantum mixture with shape resonances is too easy. Downloading the full zip for the analysis.
- **2026-11-04 22:12**: v10 uploaded (upload 1 of 5 today), digest `6d78ddee…f65b`. The species become five hydrogen isotopologues in stated rotational levels (pH2, oH2, HD, oD2, pD2; masses m, 1.5 m, 2 m), and the instruction states the physics (ground states, nuclear spins, equally populated internal states kept by collisions, exchange symmetry for like pairs) instead of the like-pair cross section, so the program must derive the like-pair weights; interface S1 S2 A L X T; tests/checks.py and checks.txt removed.
- **2026-11-05 01:53**: v11 uploaded (upload 1 of 5 today), digest `683bbb52…d7d5`. README Verification explanation gives measured convergence evidence again, from the new tests/checks.py and tests/checks.txt: Sonine indices 16, 20 and 22 against 24 over all 40 values, and tighter and oracle settings against the reference settings at k04 and k06; the energy-integration grid is described from tests/qmix.py.
- **2026-11-05 04:02**: v12 uploaded (upload 2 of 5 today), digest `6385ddba…39ce`. README Verification explanation separates independent-method checks ([bessel], [ode], [classical], [kernels], [isotropic], ported from v9 to the isotopologue code) from the reference's own convergence ([P], [step]), states what the checks do not cover, and explains the acceptance band for other correct methods; tests/checks.py and checks.txt extended.
- **2026-11-05 10:58**: v13 uploaded (upload 3 of 5 today), digest `ae8d8fdd…1f76`. New physics: H2 or D2 kept at local ortho-para equilibrium by a catalyst, graded on the viscosity and the steady-state thermal conductivity, which adds the conversion energy carried by the counter-diffusing J = 0 and J = 1 molecules and its coupling to thermal diffusion (diffusion law and Dufour term); interface G A L B T, eight new sets, tests, requirements, README, oracle and checks.txt rebuilt.
- **2026-11-05 11:01**: User: keep revising until pass@3 gives a P3 ID (no withdrawal on 3/3; overrides the 10:17 choice and the three-cycle limit). Each failure: full pass@3 logs, fix, much harder, release.
- **2026-11-05 12:19**: v14 uploaded (upload 4 of 5 today), digest `1dc49ebf…c0cc`. instruction_concision fix from the v13 quick check (job 17654): the sentence explaining that H's nucleus is a proton and D's a deuteron is deleted from instruction.md; nothing else changes.
- **2026-11-05 12:40**: v15 draft finished in `work/chapman-enskog-transport/v15/task/` (gap conductivity between non-catalytic walls at a finite conversion rate, κ² = (1 + λ_R/λ_f) n/(n D12 τ)); evidence from the caches in seconds; held until v14's pass@3 result.
- **2026-11-05 18:22**: v14 quick check passed (job 17742, all 40 criteria); pass@3 running on Sol 6.1 (v13's physics). v15 draft held in work/.
- **2026-11-05 20:27**: v15 uploaded (upload 5 of 5 today), digest `a21d74da…cd8d`. Finite conversion rate: two new graded outputs, gap_conductivity (a layer between walls that neither pass nor convert molecules; new inputs N, W, TAU) and bulk_viscosity (the composition lag in a uniform expansion); viscosity and thermal_conductivity as in v13/v14. Evidence in tests/checks.txt [gap] (solve_bvp, 1.2e-13) and [bulk] (integrated expansion, 5.1e-13); 36 requirements, 5 tests, expert time 9 h.
- **2026-11-05 23:51**: T-0851 was withdrawn at the user's request (23:50 UTC, after "please stop everything"). v16 (expert time 6 h, the fix for v15's `solvable` FAIL) was never uploaded, and no P3 ID was issued. The sources are archived in `tasks/archive/chapman-enskog-transport/` and the v15 zip in `deliveries/archive/chapman-enskog-transport/`. No physics task is active.

# gamma-decay-scheme

## Task identity

| Field | Value |
|---|---|
| Slug | `gamma-decay-scheme` |
| Source | `tasks/active/gamma-decay-scheme/` (output task, data file) |
| Category | Science / Physics |
| Platform ID | T-1383 (first submitted 2026-11-06 02:02) |
| DAS Task ID | 4011092 |
| Toolkit | tb4 3.3.0 installed, platform 3.3.2 |
| Target | quick check PASS; platform controls oracle 1, nop 0, cheat 0; pass@3 1/3 or 2/3 |
| P3 IDs pasted into DAS | none yet |

## Session events (newest last)

- **2026-11-06 02:02**: v1 submitted (upload 1 of 5 today), digest `ac5b3e35…5357`. Level scheme of an invented nucleus from a tape-station run: 16 levels, 30 transitions, parent half-life, isomer. Traps: production gain, escape peaks, sum peaks, two doublets, a shared line, an isomer behind an unseen transition. Bands 0.5 keV, 25%, 2%, 8%.
- **2026-11-06 02:58**: v2 uploaded (upload 2 of 5 today), digest `7981e5c9…bed9`. The instruction now states the selection rule the quick check asked for (job 18754, discoverable): of the schemes that agree with the data, the one with the fewest levels. README, tests/checks.txt and the judge's docstrings say the same; data and expected.json unchanged.
- **2026-11-09 01:58**: platform reset to the TB4.1 Queue (toolkit 3.7.0, 2026-11-08); My tasks empty, T-1383 gone. Kit 3.7.0 installed (3.3.0 kept as `~/tb4/tb4-starter-pack-3.3.0`). TB 4.1 needs committed uv locks for every Python dependency. Next: migrate the task and submit it again with DAS 4011092.
- **2026-11-09 02:02**: v3 submitted to the TB4.1 Queue as **T-0020** (DAS 4011092; the platform's v1), upload 1 of 5 today, digest `9b420950…ad6d`. TB 4.1 template (uv locks, new test.sh, README metadata); data, answers and grader unchanged. Quick check running.
- **2026-11-09 02:45**: v3 (T-0020 v1) quick check PASSED, all 40 criteria; pass@3 started.
- **2026-11-09 02:48**: quick-check card reviewed (job 137: 31 pass, 3 N/A, `novel` deferred; extra 5/5) and marked seen; poller restarted for the pass@3 card.
- **2026-11-09 14:05**: background work paused by the user; poller stopped (no pass@3 card by 14:04; the 14:04 poll got the sign-in page).
- **2026-11-09 17:22**: platform restored T-1383; the 02:02 upload is its v3. v3 pass@3 **3/3 TOO EASY** (job 19128, 14:37), sent back. Hardening round next (v4).
- **2026-11-09 17:59**: v3 pass@3 reviewed (3/3, all exact, 7 to 13 min). v4 = v3 plus a real 511.00 keV transition in the annihilation peak (3092.6 -> 2581.6 keV, I 0.853); generator run, reference matches; checks pass under kit 3.8.2. Upload waits for the platform (busy at 17:58).
- **2026-11-09 18:00**: both T-1383 cards (pass@3 3/3 at 14:37; the Nov 6 quick-check fault) marked seen.
- **2026-11-09 18:02**: v4 uploaded (upload 2 of 5 today), digest `eebfdfcc…8e47`. v4: a real 511.00 keV transition (3092.6 -> 2581.6 keV, I 0.853) hidden in the annihilation peak, shown only by the narrow part of that peak and by its coincidences; new data, expected.json and checks.txt from the generator; the reference splits the 511 keV peak with the background run's annihilation shape; README updated. Instruction, grader and requirements unchanged.
- **2026-11-10 01:54**: v4's quick check (job 19370) stopped at a static FAIL: the README's Author line must be `Name (email)` as task.toml declares it (TB 4.1). 5 extra criteria pass; the 35 did not run. Waiting on the user (the email-only-in-task.toml rule).
- **2026-11-10 01:59**: v5 uploaded (upload 1 of 5 today), digest `7065d1bf…b7f8`. README's Author line is now 'Name (email)' exactly as task.toml declares it: TB 4.1's check-task-fields.sh failed v4 on it (job 19370; user: "Add it, upload again"). Nothing else changed.
- **2026-11-10 07:45**: v5 (= v4 plus the README's Author line with the email) passed its quick check (job 19705); pass@3 running from 07:42.
- **2026-11-10 08:10**: v5 pass@3 0/3 (job 19705): the 511.00 keV line missed by all three (511 set aside as a room line). v6 = v5 plus one instruction sentence (a transition can share its peak with radiation of another origin, whatever the peak's energy), R13 and README; no new data.
- **2026-11-10 08:11**: v6 uploaded (upload 2 of 5 today), digest `61344b23…562f`. v5 pass@3 0/3 (job 19705): all three set the 511 keV peak aside by energy. The instruction now says: "A transition can share its peak with radiation of another origin, whatever the peak's energy." (bound as R13); README updated. Data, expected.json, checks.txt, generate.py and solve.py unchanged.
- **2026-11-10 12:07**: v6 (= v5 plus one instruction sentence, R13 and README) passed its quick check (job 20055); pass@3 running from 12:03.
- **2026-11-10 12:42**: v6 pass@3 2/3 (job 20055): QUALIFIED, P3 ID P3-6AEE-4ACB-FA2A (to the user for DAS 4011092). a3 missed only 1489.6 -> 0 (taken as a sum peak). Full review running as the platform's v7 (same files).
- **2026-11-10 14:12**: full review of v7 (= v6) finished 14:04: a reviewer decides. Flags: answer leak (critical, the v6 proviso), contract_probes, contract_generality. Nothing to upload.
- **2026-11-10 20:39**: (note from the rv-planet-census session) this task's 18:08 and 18:17 entries were written at the
  file's end, under `# rv-planet-census`. `tools/log_release.py` now writes into the slug's own section.
- **2026-11-11 00:28**: v9 uploaded (upload 2 of 5 today), digest `f9413828…b47a`. 511 keV line at I 2.99 (M beta 10.85, M->H 21, H beta 3.65) and the parent's pair-production annihilation doubled to 6.0e-4 per decay: read as one line the peak gives 4.34 whole or 4.10 less the room's share, the two shapes or coincidences give it; reference doublet members from the gates that agree within two standard errors (one stray gate had made the search admit three 16-level schemes; one again); checks.txt names the coincidence route's furthest pair; README figures from the v9 checks
- **2026-11-11 06:12**: v9 (511 keV line at I 2.99 among doubled pair-production annihilation; robust doublet members in the reference) passed its quick check (job 21129); pass@3 running from 06:09.
- **2026-11-11 06:12**: (note) this task's 2026-11-10 23:52 entry (v8 quick check passed) and 2026-11-11 00:09 entry (v8 pass@3 3/3, the v9 plan) were written at the file's end, under `# dhva-fermi-surface`. The gamma log scripts now write into this section, as `tools/log_release.py` does.
- **2026-11-11 06:37**: v9 pass@3 1/3 (job 21129): QUALIFIED, P3 ID P3-4DCE-3D5C-5E63 (to the user for DAS 4011092). a1 left the 511.00 keV line out (set aside with the room lines); a3 rejected the sub-threshold 38.1 keV step (isomer at 1925.0, three extra levels); a2 exact. Full review as v10 (= v9's files) from 06:26.
- **2026-11-11 10:34**: v10 full review finished 08:23 (job 21495): a reviewer settles contract_probes and contract_generality; no answer leak. Waiting.
- **2026-11-11 18:34**: v10 pass@8 on Astra 6: 8/8 (job 21495, 18:12), TOO EASY, sent back. All 8 exact; worst intensity error 7-10% (limit 25%). Astra 6 handles both v9 traps (511 keV line, sub-threshold isomer step) routinely. v11: harden for Astra 6, keep Sol 6.1 at 1-2 of 3.
- **2026-11-11 18:57**: v11 uploaded (upload 4 of 5 today), digest `ebda2428…eaea`. New level at 2721.70 keV (beta-fed): a clean 1879.00 keV line to 842.70 keV and a weak 1081.40 keV line (I 1.22) to 1640.30 keV, 0.9 keV under E->B 1082.30 keV (I 13.02), seen only in the gate on the 1322 keV doublet (centroid 1081.44 keV; the 1082 keV peak's width 1.02 of resolution). 511 keV line back to v8 (M beta 11.75, M->H 31, H beta 2.75, I 4.30; pair-production annihilation 3.0e-4). solve.py: a doublet member under a quarter of its peak takes its first share from the singles centroid, a gate on the strong member leaves it undecided, and split_moved shares the peak from the gates below each member. 17 levels, 33 transitions; reference within 9.1% (the weak member), one scheme at 17 levels. README and tests/checks.txt updated; instruction unchanged.
- **2026-11-11 18:58**: v11 design: weak 1081.40 keV transition (I 1.22) from a new beta-fed level at 2721.70 keV to 1640.30 keV, 0.9 keV under E->B (I 13.02), whose only clean gate is the 1322 keV doublet; 511 keV line back to v8. Notes in `work/gamma-decay-scheme/v11/design.md`.
- **2026-11-12 05:38**: v11 (weak 1081.40 keV transition under E->B; 511 keV line at v8's strength) passed its quick check (job 22164); pass@3 running from 05:34.
- **2026-11-12 06:02**: v11 pass@3 1/3 (job 22164, 05:53): QUALIFIED, P3 ID P3-8546-0E6F-2BCD (to the user for DAS 4011092). a1 and a3 missed only the weak 1081.40 keV line under E->B; a2 exact. Full review as v12 from 05:53.
- **2026-11-12 07:37**: v12 full review finished 07:32 (job 22785): a reviewer settles contract_probes and contract_generality (1 assumption, settled by a quoted rule); no answer leak. Waiting.
- **2026-11-12 21:45**: v12 pass@8 on Astra 6: 7/8 (job 22785, 21:09), TOO EASY, sent back. Only a4 missed the hidden 1081.40 keV line; the rest found it by the level difference 2721.7 - 1640.3 or in the 1321.9 keV gate. v13: harden for Astra 6, keep Sol 6.1 at 1-2 of 3.
- **2026-11-12 22:39**: v13 uploaded (upload 2 of 5 today), digest `9734bed4…b7e1`. v13: the weak 1081.4 keV transition now leaves a level at 1399.8 keV fed only by the beta decay (557.1 keV to 842.7 keV) for 318.4 keV, 0.9 keV under 1082.3 keV; its one coincidence partner, 318.4 keV, lies below the strong line too, so no gate isolates it (v12's 2721.7 keV level and its gate route dropped). solve.py: hidden_members fits level differences near strong peaks with a tailed line shape; the search places lines on shared peaks after the clean ones; checks.txt lists the other 17-level scheme and why the coincidences exclude it; README from the v13 checks
- 2026-11-13 05:54: v13 quick check passed (36 of 40); pass@3 on Sol 6.1 running.
- 2026-11-13 07:23: v13 pass@3 on Sol 6.1: 0 of 3 (TOO HARD), sent back.
- 2026-11-13 07:32: v13 pass@3 analysed: all three missed only the hidden 1081.40 keV line (the 1399.8 keV level came late, by its weak 557.1 keV line). v14: stronger 557.1 keV and hidden line.
- **2026-11-13 07:50**: v14 uploaded (upload 1 of 5 today), digest `eba494d8…0722`. v14: more beta feeding to the 1399.8 keV level (1.9 to 3.6, branches 55/45), so its 557.1 keV line is a regular line (I 2.98) and the level stands from the start; the hidden 1081.4 keV line is now I 2.44, a fifth of 1082.3 keV, and still no gate isolates it. solve.py: the hidden member's share comes from the 318.4/524.3 keV gates (the shape fit's share moves with the energy scale); a partner with more than 1.15 of a one-cascade doublet's gamma rays per gamma ray of its own sees both members (no false 17-level schemes); generate.py names what falls outside a tolerance; README from the v14 checks
- 2026-11-13 13:39: v14 quick check passed (36 of 40); pass@3 on Sol 6.1 running.
- **2026-11-13 19:18**: v14 pass@3 1/3 on Sol 6.1 (19:16, after a platform restart at 18:44): QUALIFIED, P3 ID P3-B911-F9F1-EDFA (to the user for DAS 4011092). Full review queued as v15 (= v14's files).
- **2026-11-13 21:18**: full review v15 finished 21:11: IN REVIEW, DECIDING; contract generality left 1 generator assumption unsettled (most likely whether the hidden Y -> A 1081.4 keV line under E -> B counts as detected). Waiting for the reviewer; no upload.

# rv-planet-census

## Task identity

| Field | Value |
|---|---|
| Slug | `rv-planet-census` |
| Source | `tasks/active/rv-planet-census/` (output task, data files, `RUN_PROGRAM=0`) |
| Category | Science / Physics |
| Platform ID | T-1519 (first submitted 2026-11-10 14:33) |
| DAS Task ID | 4040198 |
| Toolkit | tb4 3.8.2 installed, platform 3.8.3 |
| Target | quick check PASS; platform controls oracle 1, nop 0, cheat 0; pass@3 1/3 or 2/3 |
| P3 IDs given to the user | none yet |

## Session events (newest last)

- **2026-11-10 14:33**: v1 submitted (upload 3 of 5 today), digest `527d1959…33c7`. Planet census of an invented active
  K dwarf (0.690 Msun, 0.672 Rsun): visible velocities with CRX, dLW and Halpha (317 visits, 3 seasons), near-infrared
  velocities (158, 2 seasons), 2 sectors of 2-minute photometry with an eclipsing binary 1.20 mag fainter in the
  aperture. Answer: rotation 34.28 d and four planets, d 1.2196 d, b 2.876 d (transits), c 17.648 d (2.9% from
  P_rot/2), e 115.30 d (e 0.31, one transit). Traps: rotation from Halpha's process against its periodogram peaks, c
  beside P_rot/2, one-day and one-year aliases, the binary, e's single transit, the second star's light. Bands: period
  2%, K and minimum mass 25%, radius 8%, rotation 10%. Reference (generator run 4): periods 0.87%, K 8.0%, masses
  12.0%, radii 1.7%, rotation 0.1%. No hint sentence in the instruction (gamma's full review called one an answer leak).
- **2026-11-10 18:08**: v7 (= v6) SENT BACK by the reviewer: the proviso leaks the key realization; the grader lacks a from/to/energy consistency check. v8 in progress: proviso out, consistency rule in, the 511 keV line strengthened about fivefold in the data (new generator run).
- **2026-11-10 18:17**: v8 uploaded (upload 4 of 5 today), digest `c57359ae…a524`. v7 (= v6) was sent back by the reviewer (17:56). The instruction loses the proviso (an answer leak) and gains a stated rule, energy_keV within 0.5 keV of from_keV minus to_keV, tested by test_transition_consistency (R13). The 511 keV line is strengthened in the data (I 0.853 -> 4.41, feeding half of the 2581.6 keV level); new data, expected.json and checks.txt from the generator; README follows.
- **2026-11-10 20:39**: the 18:08 and 18:17 entries just above are gamma-decay-scheme's (T-1383 v7 sent back, v8 uploaded),
  not this task's: they were appended at the file's end, which became this section at 14:33. `tools/log_release.py`
  now writes into the slug's own section.
- **2026-11-10 20:39**: v1's quick check passed (job 20397, 20:33; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass;
  platform oracle 1, nop 0, cheat 0). pass@3 running on Sol 6.1 from 20:33.
- **2026-11-10 20:57**: v1 pass@3 2/3 (job 20397, 20:46): QUALIFIED, P3 ID P3-DE0E-7F4D-56A1 (to the user for DAS
  4040198; the user submits on DAS). Full review queued at 20:55 as the platform's v2 (job 20848).
- **2026-11-11 04:03**: full review of v2 (= v1, job 20848) finished 03:59: a reviewer decides. One check for a person,
  `contract_generality` (3 generator assumptions, 1 not settled by a quoted rule). No answer leak.
- **2026-11-11 19:40**: full review approved; pass@8 on Astra 6 (job 20848, 19:28): 4 of 4 solved, TOO EASY, every trap
  handled. A reviewer decides whether it comes back; v3 to be drafted against Astra 6's playbook.
- **2026-11-11 19:58**: v3 drafted (no upload until the reviewer decides): a non-transiting planet f at 56.90 d
  (K 1.80 m/s, circular) just inside half of e's period, with e made nearly circular (e 0.04), so the reading every
  attempt made, one eccentric orbit for e, becomes the trap (Anglada-Escude et al. 2010 degeneracy). Probe: the
  eccentric reading is worse by chi-square 70 (activity removed exactly) or 32 (activity regressed on Halpha); it
  still puts the transit at the dip but needs b 0.82 and a radius about 10% large. Photometric noise lowered (520
  ppm white, 60 red). Reference gains `pair_test`; generator run started 19:57.
- **2026-11-11 21:47**: v3 draft complete (no upload until the reviewer decides). Design v3c: f at 56.90 d, K 2.00 m/s,
  circular, 0.75 of its period after e's dip; e nearly circular (e 0.04). The velocities alone favour one eccentric
  orbit for e (a circular pair gains only dlnL 7.91, under the 15 a planet needs; that reading misses f and puts e's K
  28.1% high); the single transit settles it (the eccentric conjunction falls 12.7 d and 6 sigma before the dip; held
  there, the search finds f at dlnL +18). Run 2 failed on f's K (+43%: a free e of 0.73 on an orbit crossing e's, not
  significant at dlnL 1.8); the reference then gained `crossing_penalty`, circular pairs in `pair_test` and
  `eccentricity_test` (Lucy and Sweeney at 5%, dlnL 3.0). Run 3 agrees: every value in band (largest K error c -6.7%,
  f +3.2%, e's radius +2.0%). README rewritten from run 3; lint PASS, scan clean.

# dhva-fermi-surface

## Task identity

| Field | Value |
|---|---|
| Slug | `dhva-fermi-surface` |
| Source | `tasks/active/dhva-fermi-surface/` (output task, data files, `RUN_PROGRAM=0`) |
| Category | Science / Physics |
| Platform ID | not submitted yet |
| DAS Task ID | 4034278 |
| Toolkit | tb4 3.8.2 installed |
| Target | quick check PASS; platform controls oracle 1, nop 0, cheat 0; pass@3 1/3 or 2/3 |
| P3 IDs given to the user | none yet |

## Session events (newest last)

- **2026-11-10 23:16**: v1 built and packaged (`deliveries/dhva-fermi-surface-20261110.zip`, 35 files, task digest
  `9d6017ca…2ca3`), not yet submitted (11-10 has 4 of 5 uploads used; submit after 00:00 UTC). de Haas-van Alphen
  magnetization sweeps of an invented metal, B || c, 5-35 T, twelve temperatures 0.35-18 K. Answer: six extremal orbits,
  alpha 461.30 T (0.660), gamma 927.60 (0.270), epsilon 1186.40 (0.480), beta neck 2641.00 (1.210), beta belly 2702.60
  (1.290), delta 7415.00 (3.350). Traps: gamma 5.0 T above 2 alpha (one blended peak in every cold spectrum; alone at
  9-18 K), epsilon's spin factor 0.063 (fundamental weaker than its second harmonic), delta heavy (only in a 22-35 T
  spectrum of the coldest sweeps), the beta neck/belly pair, seven harmonic peaks, B_eff in R_T. Bands: frequency
  0.5%, mass 15%. Reference (generator run 3): frequencies within 0.005%, masses within 0.6% except delta -4.0%; three
  further noise draws within 1.3% except delta (-1.6, +2.8, +2.5%). No hint sentence in the instruction.
- **2026-11-10 23:52**: v8 (no proviso; consistency rule; 511 keV line at I 4.41) passed its quick check (job 20645); pass@3 running from 23:48.
- **2026-11-11 00:01**: v1 submitted as T-1563 (DAS 4034278; upload 1 of 5 on 11-11), digest `87064573…ca271`
  (repackaged after a README wording fix; the 23:16 digest was never uploaded). Quick check queued; poller on T-1563.
- **2026-11-11 00:09**: v8 pass@3 3/3 (job 20645): all exact; the 511 keV line found by coincidences. v9: line at I about 3.0 and pair-production annihilation doubled, so its intensity needs the shapes or coincidences.
- **2026-11-11 06:12**: (note from the gamma-decay-scheme session) the 2026-11-10 23:52 and 2026-11-11 00:09 entries just above are gamma-decay-scheme's (T-1383 v8 quick check passed; v8 pass@3 3/3 and the v9 plan), appended at the file's end by mistake.
- **2026-11-11 11:15**: v1 quick check passed (job 21089, 09:32), pass@3 **3 of 3** (09:52, Sol 6.1), sent back.
  Every trap fell to a direct least-squares fit of the Lifshitz-Kosevich model (gamma by its survival at 6.5 K and
  above, delta from the residual, spin zero and half-frequency readings tested). v2 plan: the electrons feel
  B = mu0 H + mu0 (1 - N) M; a strongly paramagnetic sample makes every frequency read against the applied field
  about 2% low, and its oscillatory magnetization adds magnetic interaction (harmonics, combination frequencies).
- **2026-11-11 12:11**: v2 uploaded (upload 3 of 5 today), digest `34941787…7604`. v2: internal field B = mu0 H + mu0 (1-N) M of a strongly paramagnetic bar (frequencies against the applied field 2.3% low) and magnetic interaction in the data; NOTES gives the bar's size and the moment as the sample's own; instruction defines F by the orbit's area; reference converts the field axis first
- **2026-11-12 01:20**: v2 quick check passed (job 21778, 01:13 card; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass); marked seen 01:18. pass@3 running on Sol 6.1.
- **2026-11-12 01:55**: v2 pass@3 **0 of 3** (01:36, job 21778), sent back. The internal field fell in every attempt (the magnetic-interaction combinations make K measurable); all three lost delta: a composite reading matching in frequency and mass, no high-field search, and gamma's eighth harmonic 5.8 T away absorbing it. v3: delta to 7300 T, clear of every harmonic and of mass-matching combinations; the high-field trap stays.
- **2026-11-12 02:45**: v3 uploaded (upload 1 of 5 today), digest `428e960d…5769`. v3: delta moved from 7415 to 7300 T, clear of gamma's eighth harmonic (5.8 T away before, 120.8 T now) and of every combination of the other orbits that matched it in frequency and mass; checks.txt [1] reports harmonics to p = 8 and the combination count; README from the v3 checks
- **2026-11-12 19:48**: v3 quick check passed (job 22636, 19:40 card; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass); marked seen 19:47. pass@3 queued on Sol 6.1.
- **2026-11-13 01:38**: v3 pass@3 **2 of 3**, QUALIFIED (job 22636, 01:28): P3 ID P3-2F9B-5B0C-A1B0 for DAS 4034278 (with the user). The two attempts that searched at high field kept delta at 7300 T; the third never looked there. Full review running on v4 (= v3's files, job 24020).
- **2026-11-13 10:35**: v4's full review (job 24020) finished 10:14; a reviewer decides. Critical: the README's "within 0.005% on the further draws" (from v2) against gamma's +0.006% for seed 40342782 in checks.txt [5] (v3's redraws); a person settles `contract_probes` and `contract_generality`. Fix drafted as v5; no upload while the reviewer decides.
