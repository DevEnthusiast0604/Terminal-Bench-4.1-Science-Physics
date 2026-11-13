# chapman-enskog-transport: 35 criteria

32 pass, 1 fail (0 disputed), 1 not applicable, 0 inconclusive, 1 inconclusive: evidence not provided (routed to the reviewer). Reviewer: astra (openai/gpt-6.1-sol), role independent, operator review platform quick check, 1 draw(s), 2026-11-05T23:15:58Z.
Rubric: `/home/ubuntu/tb4-toolkit-1.26/tbench-assess/src/tbench_assess/rubrics/tb4-35.toml`

| Section | Pass | Fail | Not provided | N/A |
|---|---|---|---|---|
| Verifier | 5 | 0 | 0 | 0 |
| Oracle | 2 | 1 | 0 | 0 |
| Difficulty | 4 | 0 | 0 | 0 |
| Safety | 4 | 0 | 0 | 0 |
| Reproducibility | 4 | 0 | 0 | 1 |
| Specification | 4 | 0 | 0 | 0 |
| Package | 7 | 0 | 0 | 0 |
| Realism | 1 | 0 | 0 | 0 |
| Novelty | 0 | 0 | 1 | 0 |
| Agentic | 1 | 0 | 0 | 0 |

## Verifier

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 1 | `verifiable` | **PASS** | code+model | The verifier deterministically executes each submission, checks complete JSON outputs against numerical references, and uses tooling baked into its image without runtime installation. |
| 2 | `outcome_verified` | **PASS** | code+model | Grading checks the four final numerical results and the declared execution contract without inspecting the solver's numerical method or development process. |
| 3 | `functional_verification` | **PASS** | code+model | The submitted program is actually executed on all eight cases, and its exit status and complete output are checked rather than source keywords or self-reported success. |
| 4 | `verification_explanation_quality` | **PASS** | code+model | The README accurately explains every graded check and supports the tolerance with independent component validations, convergence measurements, legitimate numerical variation, and explicit limitations of the evidence. |
| 5 | `binary_reward` | **PASS** | code+model | Every reachable verifier reward write is either the initial zero or a finish call with zero or one, while infrastructure failures remove the reward. |

## Oracle

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 6 | `solvable` | **FAIL** | code+model (model) | The supplied oracle is legitimate and its recorded run passed, but README.md's Difficulty explanation explicitly estimates about nine hours for an expert who already knows the route. The phase propagation, resonance integration, collision kernels, and transport systems in solution/transport.py confirm substantial known-approach implementation work, not merely time spent discovering the solution. This does not meet the separate requirement that an expert knowing the approach can implement it in a few hours. Evidence: README.md: "An expert who already knows this route writes it in\nabout nine hours (the oracle is `solution/transport.py`)" |
| 7 | `solution_quality` | **PASS** | code+model | The separate oracle source genuinely computes scattering, collision brackets, equilibrium composition, and transport coefficients from the supplied parameters rather than returning stored case answers. |
| 8 | `solution_explanation_quality` | **PASS** | code+model | The README explains the physical insights and numerical strategy consistently with the oracle, including exchange symmetry, counter-diffusion, the coupled gap boundary layer, and bulk relaxation. |

## Difficulty

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 9 | `difficult` | **PASS** | code+model | Reconciling quantum exchange statistics, converged kinetic-theory transport, narrow scattering resonances, and reaction-diffusion coupling requires genuine professional computational-physics expertise. |
| 10 | `essential_difficulty` | **PASS** | code+model | The central challenges are physical derivation and numerical convergence, while the output schema is simple and the tolerance leaves substantial room above measured reference errors. |
| 11 | `difficulty_explanation_quality` | **PASS** | code+model | The explanation identifies specific intrinsic challenges, describes thermophysical-library and cryogenic-engineering users, and explains that the reference values arise from the stated model rather than an external dataset. |
| 12 | `expert_time_estimate` | **PASS** | code+model | The nonzero nine-hour estimate is consistent across metadata and README and is plausible for the extensive specialized numerical implementation, independently of the solvable criterion's shorter implementation requirement. |

## Safety

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 13 | `anti_cheat_robustness` | **PASS** | code+model | The agent image contains no answers or oracle, the separate verifier protects reference data and reward files from submitted code, and the inspected daemonized reward-forgery control was recorded as rejected. |
| 14 | `task_security` | **PASS** | code+model | The assets contain legitimate numerical computation, container setup, and verification logic, with the explicitly scoped reward-forgery payload serving only as a bounded adversarial control rather than hidden malicious behavior. |
| 15 | `verifier_execution_isolation` | **PASS** | code+model | Submitted code runs as uid 1500 after reward protection, root judges only captured output on a separate interpreter, and bounded draining plus uid-wide cleanup handles surviving descendants. |
| 16 | `do_not_modify_enforced` | **PASS** | code+model | The instruction's read-only execution folder and program copy are enforced through root ownership and non-writable permissions before the unprivileged program runs. |

## Reproducibility

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 17 | `deterministic_reproducible` | **PASS** | code+model | Base images and pinnable packages are pinned, task-relevant inputs are fixed, numerical grading has no randomness or live-service dependency, and the supplied repeat records report consistent outcomes. |
| 18 | `separate_verifier_configured` | **PASS** | code+model | The collected submission supplies the only agent-produced input, all reference and harness files are baked into the verifier, and matching runtime dependencies and separate judge tooling are preinstalled. |
| 19 | `environment_hygiene` | **PASS** | code+model | The agent image contains only task runtime packages and terminal support, the verifier owns tests and judge dependencies, and both Dockerfiles correctly update, install, and clean apt without version pins. |
| 20 | `resource_configuration` | **PASS** | code+model | The two-CPU, four-GB environments match the declared execution contract, the recorded oracle passed under the case limits, and the verifier budget explicitly accommodates eight 600-second cases plus bounded overhead. |
| 21 | `artifact_efficiency` | **NOT_APPLICABLE** | code+model (model) | The intended artifact is a single inherently small agent-produced Python answer with no source-tree baseline, fixed input tree, or dependency directory requiring transfer. |

## Specification

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 22 | `test_instruction_alignment` | **PASS** | code+model | The eight-case numerical comparisons, exact four-number JSON contract, file requirements, and runtime limits trace to the instruction, while physical-model requirements are exercised through their resulting coefficients. |
| 23 | `instruction_concision` | **PASS** | code+model | Although lengthy, the instruction specifies a deliberately precise physical model and restricted execution contract without prescribing numerical procedures, and its relative CLI name is explicitly grounded in the stated working directory and absolute deliverable path. |
| 24 | `structured_data_schema` | **PASS** | code+model | The instruction normatively requires exactly one JSON object with exactly four named members, each a JSON number, and defines the meaning and units of every member. |
| 25 | `typos` | **PASS** | code+model | The deliverable path, command arguments, gas identifiers, output keys, and referenced implementation files agree across instruction, oracle, harness, and README. |

## Package

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 26 | `reviewable` | **PASS** | code+model | The expected values have an included generator, documented physical derivations, and reproducible independent component checks that expose both numerical provenance and validation limitations. |
| 27 | `category_and_tags` | **PASS** | code+model | Science and Physics accurately describe the primary domain, and the matching metadata tags identify specific kinetic-theory and transport phenomena. |
| 28 | `task_name` | **PASS** | code+model | The slug chapman-enskog-transport is descriptive lowercase kebab-case with exactly three tokens and matches the configured task name. |
| 29 | `task_readme` | **PASS** | code+model | The README supplies all required sections and useful, accurate reviewer context about the physics, implementation, reference provenance, numerical validation, and verifier hardening. |
| 30 | `task_toml_schema` | **PASS** | code | all 24 checks pass or do not apply (24 decided by code, 0 by the model) |
| 31 | `no_extraneous_files` | **PASS** | code+model | The supplied files serve scaffolding, image construction, execution, reference generation, numerical validation, documentation, or the targeted anti-cheat control, with no visible scratch or unused artifact files. |
| 32 | `ctrf_reporting` | **PASS** | code+model | Pytest emits per-test CTRF that root copies to /logs/verifier/ctrf.json, and early grading failures receive a report stub before the binary reward is finalized. |

## Realism

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 33 | `interesting` | **PASS** | code+model | A reference transport solver for catalysed cryogenic hydrogen has credible professional value for thermophysical-library validation and hydrogen-processing engineering despite the deliberately idealized model. |

## Novelty

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 34 | `novel` | **NOT_PROVIDED** | code (originality) | evidence not provided: originality: deferred to the full review: the quick check does not search originality (the full review runs tb4 originality and judges novel) |

## Agentic

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 35 | `agentic` | **PASS** | code+model | Developing a reliable solver with resonance handling, convergence control, and a tight execution budget requires meaningful numerical experiments, debugging, profiling, and iterative terminal work rather than simple recall or one-command completion. |

## Structured review

Methods: 2 by code, 33 by one model question with code checks, 0 by one model question. A code check fails a criterion only on present, current evidence; a check without its record is not provided (the model's verdict stands). A code verdict is never the model's.

### `verifiable` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `verifiable.nop_scores_zero` The unchanged environment (nop) scores 0. | record nop | PASS | chapman-enskog-transport-gates/nop.json | nop PASS: nop scored 0 on 1 of 1 runs |
| `verifiable.runtime_installs` tests/test.sh installs no verifier tooling at verify time (apt-get install, curl / sh, pip install other than the agent's pinned -r /app/ manifest, npm install, uv tool install). | code: tests/test.sh scan | PASS | tests/test.sh | tests/test.sh installs nothing at verify time (the agent's pinned manifest aside) |
| `verifiable.lint` tb4-lint finds no FAIL row tagged [verifiable]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [verifiable] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `verifiable.pack_rules` No starter-pack static finding X3.3 or X3.4: the verifier grades the whole captured output or file, or rejects an oversized one, never a truncated prefix or suffix (F01, F02). | code: pack_rules_verifiable | fact | – | no X3.3/X3.4 finding in the placeholders, lint, requirements, budget, readme-claims, readme-code, structure, content record(s) |

### `outcome_verified` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `outcome.process` Tests that look at the process, history or tools the agent used. | code: process_checks | fact | – | tests that look at process or tools: tests/ce_mix.py:4: counterpart of tests/qmix.py, which takes its collision kernels (Kernels, rules) from here; the judge never imports; tests/ce_mix.py:41: species' mean velocities, which vanish then), r_i1 = -(15/4) x_i sqrt(2T / m_i);; tests/ce_ref.py:10: OUTERMOST root of F. h(r) = r^3 V'(r) / 2 is the E b^2 at which V + E b^2 / r^2 is stationary; below its maximum; tests/emit.py:12: It holds NO expected values: the answers live in tests/expected.json, which only; tests/generate.py:31: which runs from lambda_f (F -> 1) to lambda (F -> 0). The viscosity is the frozen one at the equilibrium x1.; tests/qmix.py:3: species (SPECIES), which interact through one Kihara potential and differ in mass and in the exchange symmetry of |
| `outcome_verified.lint` tb4-lint finds no FAIL row tagged [outcome_verified]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [outcome_verified] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `functional_verification` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `functional.source_grep` Tests that read source files as text (keyword checks). | code: source_grep | fact | – | no test reads source files as text |
| `functional_verification.lint` tb4-lint finds no FAIL row tagged [functional_verification]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [functional_verification] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `verification_explanation_quality` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `verification_expl.section` README.md has a filled ## Verification explanation (present, no template text, 40+ words). | code: README scan | PASS | README.md | `## Verification explanation` is filled (1392 words) |
| `verification_expl.tolerances` When the tests use tolerances or thresholds, the verification explanation addresses the bounds. | code: tests + README scan | PASS | tests/ce_mix.py:54, tests/ce_mix.py:340, tests/ce_ref.py:231, tests/checks.py:2, README.md | the tests use tolerances (tests/ce_mix.py:54, tests/ce_mix.py:340, tests/ce_ref.py:231, tests/checks.py:2) and the verification explanation addresses them |
| `verification_explanation_quality.lint` tb4-lint finds no FAIL row tagged [verification_explanation_quality]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [verification_explanation_quality] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `verification_expl.pack_rules` No starter-pack static finding C2: a cleanup guarantee (no descendant or process survives) is no broader than the cleanup code (F06). | code: pack_rules_verification_explanation_quality | fact | – | no C2 finding in the placeholders, lint, requirements, budget, readme-claims, readme-code, structure, content record(s) |

### `binary_reward` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `binary_reward.decider` The binary_reward decider (structured.CODE_CRITERIA) holds: fail when a reward write has a fractional shape (a ratio, a weighted sum, round/format of a score, a reward -= penalty, a non-0/1 literal) or a recorded run wrote a reward other than 0 or 1; not_provided when the scan finds no reward write; else pass with the write sites cited. | code: binary_reward decider | PASS | tests/test.sh:41, tests/test.sh:42, tests/test.sh:101, tests/test.sh:102, live: starter-pack gates_static.py lint | static_writes: 4 reward write site(s), none fractional: tests/test.sh:41, tests/test.sh:42, tests/test.sh:101, tests/test.sh:102; recorded_rewards: every recorded reward is 0 or 1: oracle (1 reward(s)), nop (1 reward(s)), verifier-repeat (0 reward(s)), tamper (1 reward(s)), wrong-answers (0 reward(s)); lint: no FAIL row tagged [binary_reward] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `solvable` — **FAIL** (code+model) — decisive: `model`

Model (one question): FAIL

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `solvable.oracle_passes` The oracle scored 1 on every recorded run (n of n). | record oracle | PASS | chapman-enskog-transport-gates/oracle.json | oracle 1 of 1 runs scored 1; oracle PASS: oracle scored 1 on 1 of 1 runs |
| `solvable.lint` tb4-lint finds no FAIL row tagged [solvable]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [solvable] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `solution_quality` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `solution.heredocs` solve.sh inlines no heredoc longer than 20 lines. | code: solve.sh scan | PASS | solution/solve.sh | no heredoc over 20 lines in solve.sh |
| `solution_quality.lint` tb4-lint finds no FAIL row tagged [solution_quality]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [solution_quality] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `solution_explanation_quality` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `solution_expl.section` README.md has a filled ## Solution explanation. | code: README scan | PASS | README.md | `## Solution explanation` is filled (546 words) |
| `solution_explanation_quality.lint` tb4-lint finds no FAIL row tagged [solution_explanation_quality]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [solution_explanation_quality] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `difficult` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `difficult.attempts` What the attempts show (the difficulty-adjudication after pass@3, difficulty records, rewards). | code: attempts_present | fact | – | no attempts |
| `difficult.lint` tb4-lint finds no FAIL row tagged [difficult]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [difficult] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `essential_difficulty` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `difficulty.attempts` What the attempts show: the difficulty-adjudication (after pass@3), difficulty and attempts-failed-diff records and each shipped attempt's reward, failed tests and analysis. | code: attempts_present | fact | – | no attempts |
| `essential_difficulty.lint` tb4-lint finds no FAIL row tagged [essential_difficulty]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [essential_difficulty] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `difficulty_explanation_quality` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `difficulty_expl.section` README.md has a filled ## Difficulty explanation. | code: README scan | PASS | README.md | `## Difficulty explanation` is filled (1093 words) |
| `difficulty_expl.no_scores` The difficulty explanation cites no pass rates or model results. | code: README scan | PASS | README.md | no pass rates or attempt scores in the difficulty explanation |
| `difficulty_explanation_quality.lint` tb4-lint finds no FAIL row tagged [difficulty_explanation_quality]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [difficulty_explanation_quality] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `expert_time_estimate` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `expert_time_estimate.decider` The expert_time_estimate decider (structured.CODE_CRITERIA) holds: fail when it is missing, not a number, below 0.1 h or above 160 h, or the README states a different expert time; otherwise pass (no eight-hour cap). | code: expert_time_estimate decider | PASS | task.toml, README.md, live: starter-pack gates_static.py lint | range: expert_time_estimate_hours = 9 (plausible range; no eight-hour cap); readme_agrees: README expert time matches task.toml; lint: no FAIL row tagged [expert_time_estimate] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `expert_time.facts` The estimate next to the difficulty explanation (for the model: is it plausible?). | code: expert_time_facts | fact | – | expert_time_estimate_hours 9; difficulty explanation 1093 words; instruction 1452 words |

### `anti_cheat_robustness` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `anti_cheat.cheats_scored_zero` Every shipped cheat trial scored 0. | record tamper | PASS | chapman-enskog-transport-gates/tamper.json | every cheat scored 0: forge-reward PASS (reward 0.0) |
| `anti_cheat.readable_answers` The runner uid cannot read /tests, /logs or a pristine copy in the verifier image. | record readable-answers | PASS | chapman-enskog-transport-gates/readable-answers.json | readable-answers PASS: nothing under /tests is readable by the runner uid; /pristine exposes nothing |
| `anti_cheat.no_oracle_in_image` No copy of the reference solution is in environment/ (for a patch: the lines it adds), and the agent Dockerfile COPYs no file named like the oracle (solution, solve, oracle, golden, ground truth). Public samples and worked examples are not checked here. | code: answer_in_image | fact | – | leak scan of environment/: 0 copy of solution material; 0 file(s) or column(s) named answer/expected (usually the intended public samples: weigh whether any is a HIDDEN answer); partial runs of test lines are the same data format, not by themselves a leak |
| `anti_cheat.lint` tb4-lint finds no FAIL row tagged [anti_cheat_robustness]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [anti_cheat_robustness] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `task_security` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `security.no_host_access` No docker socket, privileged mode or host network/pid in the task files. | code: host_access | fact | – | no host access found by the scan |
| `security.no_obfuscation` No decoded payload is executed (base64/xxd piped into a shell, eval/exec of decoded text). | code: obfuscation | fact | – | no decoded payload executed found by the scan |
| `security.no_prompt_injection` No text in instruction.md, README.md, tests/ or solution/ addresses a reviewer or model to change a verdict. | code: injection | fact | – | no text addressed to a reviewer or model found by the scan |
| `security.lint` tb4-lint finds no FAIL row tagged [task_security]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [task_security] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `verifier_execution_isolation` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `isolation.privilege_drop` Where tests/test.sh drops privileges (setpriv/runuser/su/gosu) before running agent code. | code: unprivileged | fact | – | tests/test.sh drops privileges at line(s) 57, 232 |
| `isolation.reward_root_first_last` The runner uid never writes the reward, and root pre-sets it to 0 or removes it before the first runner command. | code: reward_root | fact | – | reward writes at tests/test.sh:41, 42, 101, 102; privilege drops at 57, 232 |
| `isolation.reward_dir_locked` The reward directory (/logs/verifier) is locked (chmod 700) before the first runner command; /tests is not readable by the runner. Locking /logs itself is not required. | code: logs_locked | fact | – | /logs locks at tests/test.sh:35; first privilege drop at 57; readable-answers PASS |
| `isolation.kill_by_uid` Where tests/ kills runner processes by uid (the 1.6.0 hardening standard). | code: kill_by_uid | fact | – | kill-by-uid at tests/emit.py:84, tests/test.sh:47, tests/test.sh:57, tests/test.sh:59; privilege drops at tests/test.sh:57, 232 |
| `isolation.lint` tb4-lint finds no FAIL row tagged [verifier_execution_isolation]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [verifier_execution_isolation] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `do_not_modify_enforced` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `protect.phrases` The do-not-modify constraints the instruction states. | code: protect_phrases | fact | – | do-not-modify constraints in the instruction: instruction.md:9: Write `/app/output/transport.py`, a Python program that the checker runs as `python3 transport.py G A L B T N W TAU`, where `G` is the gas,  |
| `do_not_modify_enforced.lint` tb4-lint finds no FAIL row tagged [do_not_modify_enforced]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [do_not_modify_enforced] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `deterministic_reproducible` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `reproducible.repeat_records` Repeated clean runs agree: the oracle-determinism and verifier-repeat records pass. | record oracle-determinism + verifier-repeat | PASS | chapman-enskog-transport-gates/oracle-determinism.json, chapman-enskog-transport-gates/verifier-repeat.json | oracle-determinism PASS: 1 oracle run and 2 verifier regrades report the same reward and the same 5 test ids with the same statuses; verifier-repeat PASS: 2 regrades of one oracle trial report reward 1 and the same 5 test ids and statuses |
| `reproducible.deps_pinned` Every base image is digest-pinned (the content gate's FROM rule: a tag is not a pin), pip installs are ==-pinned, apt packages are not version-pinned. | code: pins | fact | – | FROM without a digest: 0 (live: starter-pack gates_static.py content); unpinned pip installs: 0; apt version pins: 0 |
| `reproducible.lint` tb4-lint finds no FAIL row tagged [deterministic_reproducible]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [deterministic_reproducible] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `separate_verifier_configured` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `separate.runtime_installs` tests/test.sh installs no verifier tooling at verify time. | code: tests/test.sh scan | PASS | tests/test.sh | tests/test.sh installs nothing at verify time (the agent's pinned manifest aside) |
| `separate_verifier_configured.lint` tb4-lint finds no FAIL row tagged [separate_verifier_configured]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [separate_verifier_configured] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `environment_hygiene` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `hygiene.no_oracle_in_image` No copy of the reference solution in environment/ and no oracle-named COPY in the agent Dockerfile (public samples are not checked here). | code: answer_in_image | fact | – | leak scan of environment/: 0 copy of solution material; 0 file(s) or column(s) named answer/expected (usually the intended public samples: weigh whether any is a HIDDEN answer); partial runs of test lines are the same data format, not by themselves a leak |
| `hygiene.apt_clean_unpinned` Every apt-get install runs after apt-get update in the same RUN, cleans /var/lib/apt/lists, and pins no apt version. | code: Dockerfile scan | PASS | – | 2 apt-get install RUN(s): each updates, cleans /var/lib/apt/lists and pins no version |
| `hygiene.lint` tb4-lint finds no FAIL row tagged [environment_hygiene]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [environment_hygiene] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `hygiene.pack_rules` No starter-pack static finding D1: no Dockerfile RUN build or install step is masked by // true, // :, // exit 0 or ; true (F04). | code: pack_rules_environment_hygiene | fact | – | no D1 finding in the placeholders, lint, requirements, budget, readme-claims, readme-code, structure, content record(s) |

### `resource_configuration` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `resources.values` The configured timeouts and resources, and which template defaults are kept. | code: resources | fact | – | agent timeout 28800.0, verifier timeout 5260.0, cpus 2, memory_mb 4096, storage_mb 10240, gpus 0; template defaults kept: ['storage_mb'] |
| `resource_configuration.lint` tb4-lint finds no FAIL row tagged [resource_configuration]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [resource_configuration] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `artifact_efficiency` — **NOT_APPLICABLE** (code+model) — decisive: `model`

Model (one question): NOT_APPLICABLE

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `artifacts.whole_tree` task.toml artifacts do not name the whole tree (/app, /root, /home or /). | code: artifacts_scope | fact | – | task.toml artifacts = ['/app/submission'] |
| `artifacts.missing_vs_empty` A missing submission is not graded (the missing-artifact control writes no reward). | record missing-artifact | PASS | chapman-enskog-transport-gates/missing-artifact.json | missing-artifact PASS: missing-artifact: no reward written, verifier error RewardFileNotFoundError |
| `artifacts.no_partial_patch` A damaged submission is not graded (the partial-artifact control writes no reward). | record partial-artifact | PASS | chapman-enskog-transport-gates/partial-artifact.json | partial-artifact PASS: partial-artifact: no reward written, verifier error RewardFileNotFoundError |
| `artifacts.collect_faithful` The git-diff-patch collect's fail-safe mechanics (atomic capture, pinned diff baseline, excluding or not smuggling build/dependency trees, a loud reward 0 on an apply failure, never grading a partial tree, manifest reset/reinstall) hold -- credited by equivalent safeguards and the missing/partial-artifact controls; N/A when the task has no git-diff-patch collect. | code: collect_faithful | fact | – | no git-diff-patch [[verifier.collect]]: the patch-mechanism rules do not apply |
| `artifacts.lint` tb4-lint finds no FAIL row tagged [artifact_efficiency]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [artifact_efficiency] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `test_instruction_alignment` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `alignment.requirements_bound` On a v2 task, tests/requirements.json binds every constraint sentence to a graded test that exists (the starter pack's requirements gate). A legacy task without requirements.json is not judged here. | code: requirements | fact | – | requirements PASS (live: starter-pack gates_static.py requirements): syntactic traceability: 36 requirements, 5 graded tests, 15 constraint sentences; every quote, test and constraint is bound; semantic assertion coverage is not evaluated |
| `alignment.lint` tb4-lint finds no FAIL row tagged [test_instruction_alignment]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [test_instruction_alignment] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `instruction_concision` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `instruction.shape` Instruction length, relative paths, headings and tool mentions. | code: instruction_shape | fact | – | 1444 words; relative paths in backticks: ['transport.py']; headings: 0; tool/library mentions: none |
| `instruction.cause_named` The instruction does not name the root cause or the exact place to change (the screen's leak question): sentences that might. | code: instruction_names_cause | fact | – | no sentence names a cause or a place to change (by pattern) |
| `instruction_concision.lint` tb4-lint finds no FAIL row tagged [instruction_concision]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [instruction_concision] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `structured_data_schema` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `schema.outputs` Where the tests parse structured output, and whether the instruction names its fields. | code: structured_outputs | fact | – | the tests parse structured output at tests/checks.py:61, tests/checks.py:541, tests/generate.py:139, tests/tb4judge.py:10, tests/tb4judge.py:57, tests/tb4judge.py:152; the instruction does not name fields, columns, keys or a schema |
| `structured_data_schema.lint` tb4-lint finds no FAIL row tagged [structured_data_schema]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [structured_data_schema] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `typos` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `typos.decider` The typos decider (structured.CODE_CRITERIA) holds: fail only when a path instruction.md names does not exist (the agent acts on it); a README path that resolves nowhere is a WARN for the reviewer, never a FAIL; an /app path in a cloned repository is listed as unverified. | code: typos decider | PASS | live: starter-pack gates_static.py readme-code, live: starter-pack gates_static.py lint | paths: 51 named path(s) checked, none missing from instruction.md; readme_code: readme-code PASS: 54 README references checked; 0 dangling, unbacked or inconsistent; 0 receipt-only (wrapper evidence, needs a disposition); lint: no FAIL row tagged [typos] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `reviewable` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `reviewable.literals` Long literal expected values in the tests (their derivation). | code: hardcoded_expected | fact | – | no long literal value lists in tests |
| `reviewable.lint` tb4-lint finds no FAIL row tagged [reviewable]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [reviewable] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `category_and_tags` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `category_and_tags.decider` The category_and_tags decider (structured.CODE_CRITERIA) holds: fail when category is not one of the seven domains, subcategory is empty, tags are empty or repeated, or the README metadata tags disagree with task.toml. | code: category_and_tags decider | PASS | task.toml, live: starter-pack gates_static.py lint | metadata_subcategory_present: [metadata].subcategory is set; metadata_tags_present: [metadata].tags is set; category_allowed: category is one of the seven domains; tags_valid: tags is a non-empty list of distinct strings; tags_specific: no generic tag among 6; readme_tags: README tags match task.toml; lint: no FAIL row tagged [category_and_tags] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `task_name` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `task_name.decider` The task_name decider (structured.CODE_CRITERIA) holds: fail when the folder is not lowercase kebab-case with at most three words, or [task].name is not terminal-bench/<folder>. | code: task_name decider | PASS | task.toml, live: starter-pack gates_static.py lint | slug_format: folder name is lowercase kebab-case, at most 3 tokens; task_name: [task].name is terminal-bench/<folder>; lint: no FAIL row tagged [task_name] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `task_name.facts` The slug and its tokens (for the model: is it descriptive?). | code: task_name_facts | fact | – | slug 'chapman-enskog-transport': 3 token(s) ['chapman', 'enskog', 'transport'] |

### `task_readme` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `readme.experience` README.md has a filled ## Relevant experience. | code: README scan | PASS | README.md | `## Relevant experience` is filled (33 words) |
| `task_readme.lint` tb4-lint finds no FAIL row tagged [task_readme]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [task_readme] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `readme.pack_rules` No starter-pack static finding C1: a cryptographic claim (Ed25519, ECDSA, RSA signature, cryptographic signing) is backed by cryptographic code in the task (F05). | code: pack_rules_task_readme | fact | – | no C1 finding in the placeholders, lint, requirements, budget, readme-claims, readme-code, structure, content record(s) |

### `task_toml_schema` — **PASS** (code)

Source: tbench-assess task_rules.parameters (every FAIL-level rule other than name, category, tags and expert time), tb4-lint's task_toml_schema rows (Harbor's allowed keys)

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `task_toml_parses` task.toml parses | tbench-assess task_rules.parameters | PASS | task.toml | task.toml parses |
| `schema_version_present` schema_version is set | tbench-assess task_rules.parameters | PASS | task.toml | schema_version is set |
| `metadata_table` [metadata] is a table | tbench-assess task_rules.parameters | PASS | task.toml | [metadata] is a table |
| `metadata_author_name_present` [metadata].author_name is set | tbench-assess task_rules.parameters | PASS | task.toml | [metadata].author_name is set |
| `metadata_author_email_present` [metadata].author_email is set | tbench-assess task_rules.parameters | PASS | task.toml | [metadata].author_email is set |
| `metadata_category_present` [metadata].category is set | tbench-assess task_rules.parameters | PASS | task.toml | [metadata].category is set |
| `author_email_valid` author_email is a well-formed address | tbench-assess task_rules.parameters | PASS | task.toml | author_email is a well-formed address |
| `author_github_valid` author_github is a valid GitHub username | tbench-assess task_rules.parameters | PASS | task.toml | author_github is a valid GitHub username |
| `no_allow_internet` allow_internet is absent everywhere | tbench-assess task_rules.parameters | PASS | task.toml | allow_internet is absent everywhere |
| `environment_cpus` [environment].cpus is one of [1, 2, 4, 8, 16] | tbench-assess task_rules.parameters | PASS | task.toml | [environment].cpus is one of [1, 2, 4, 8, 16] |
| `environment_memory` [environment].memory_mb is one of the allowed sizes | tbench-assess task_rules.parameters | PASS | task.toml | [environment].memory_mb is one of the allowed sizes |
| `environment_build_timeout_sec` [environment].build_timeout_sec is a positive number | tbench-assess task_rules.parameters | PASS | task.toml | [environment].build_timeout_sec is a positive number |
| `environment_storage_mb` [environment].storage_mb is a positive number | tbench-assess task_rules.parameters | PASS | task.toml | [environment].storage_mb is a positive number |
| `verifier_environment_cpus` [verifier.environment].cpus is one of [1, 2, 4, 8, 16] | tbench-assess task_rules.parameters | PASS | task.toml | [verifier.environment].cpus is one of [1, 2, 4, 8, 16] |
| `verifier_environment_memory` [verifier.environment].memory_mb is one of the allowed sizes | tbench-assess task_rules.parameters | PASS | task.toml | [verifier.environment].memory_mb is one of the allowed sizes |
| `verifier_environment_build_timeout_sec` [verifier.environment].build_timeout_sec is a positive number | tbench-assess task_rules.parameters | PASS | task.toml | [verifier.environment].build_timeout_sec is a positive number |
| `verifier_environment_storage_mb` [verifier.environment].storage_mb is a positive number | tbench-assess task_rules.parameters | PASS | task.toml | [verifier.environment].storage_mb is a positive number |
| `agent_timeout` [agent].timeout_sec is exactly 28800 | tbench-assess task_rules.parameters | PASS | task.toml | [agent].timeout_sec is exactly 28800 |
| `verifier_timeout_in_range` [verifier].timeout_sec is in (0, 28800] | tbench-assess task_rules.parameters | PASS | task.toml | [verifier].timeout_sec is in (0, 28800] |
| `verifier_separate` [verifier].environment_mode is "separate" | tbench-assess task_rules.parameters | PASS | task.toml | [verifier].environment_mode is "separate" |
| `artifacts_declared` artifacts lists what the agent produces | tbench-assess task_rules.parameters | PASS | task.toml | artifacts lists what the agent produces |
| `artifacts_not_whole_tree` artifacts never name the whole tree | tbench-assess task_rules.parameters | PASS | task.toml | artifacts never name the whole tree |
| `trailer_matches_timeout` the instruction trailer quotes [agent].timeout_sec | tbench-assess task_rules.parameters | PASS | task.toml | the instruction trailer quotes [agent].timeout_sec |
| `lint` tb4-lint's task_toml_schema rows pass | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [task_toml_schema] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

Model note (not a verdict): The code-decided PASS is retained.

### `no_extraneous_files` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `no_extraneous_files.decider` The no_extraneous_files decider (structured.CODE_CRITERIA) holds: fail on editor/OS/cache files or a top-level entry other than instruction.md, task.toml, README.md, environment/, tests/, solution/, cheat/, .gitignore, .gitattributes. | code: no_extraneous_files decider | PASS | live: starter-pack gates_static.py lint | no_stray_files: no editor, OS or cache files in the task; references: every file is copied by a Dockerfile or named by a task file; top_level: the task folder holds only the task layout; lint: no FAIL row tagged [no_extraneous_files] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `ctrf_reporting` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `ctrf_reporting.decider` The ctrf_reporting decider (structured.CODE_CRITERIA) holds: not_applicable when the tests have no discrete structure (no pytest, no test_*.py); pass when the verifier writes /logs/verifier/ctrf.json; fail otherwise. | code: ctrf_reporting decider | PASS | tests/test.sh:36, tests/test.sh:72, tests/test.sh:91, tests/test.sh:92, tests/test.sh:440, tests/test.sh:447, live: starter-pack gates_static.py lint | ctrf: CTRF report written for /logs/verifier: tests/test.sh:36, tests/test.sh:72, tests/test.sh:91, tests/test.sh:92, tests/test.sh:440, tests/test.sh:447; lint: no FAIL row tagged [ctrf_reporting] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `ctrf_reporting.pack_rules` No starter-pack static finding X3.1: every finish or reward path of tests/test.sh also writes or stubs /logs/verifier/ctrf.json (F03). | code: pack_rules_ctrf_reporting | fact | – | no X3.1 finding in the placeholders, lint, requirements, budget, readme-claims, readme-code, structure, content record(s) |

### `interesting` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `interesting.lint` tb4-lint finds no FAIL row tagged [interesting]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [interesting] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `novel` — **NOT_PROVIDED** (code) — decisive: `originality`

Source: _provenance/<slug>/ORIGINALITY.json (or a delivery's provenance/ORIGINALITY.json), from `tb4 originality`

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `originality` ORIGINALITY.json status (judged by the full review) | ORIGINALITY.json | NOT_PROVIDED | – | deferred to the full review: the quick check does not search originality (the full review runs tb4 originality and judges novel) |

Model note (not a verdict): The code-decided NOT_PROVIDED is retained; the deferred full originality search is not among the supplied evidence.

### `agentic` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `agentic.attempts` What the attempts show (number of steps, tools used). | code: attempts_present | fact | – | no attempts |
| `agentic.lint` tb4-lint finds no FAIL row tagged [agentic]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [agentic] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

