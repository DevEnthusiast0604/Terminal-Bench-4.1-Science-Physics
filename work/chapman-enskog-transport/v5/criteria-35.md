# chapman-enskog-transport: 35 criteria

32 pass, 1 fail (0 disputed), 1 not applicable, 0 inconclusive, 1 inconclusive: evidence not provided (routed to the reviewer). Reviewer: astra (openai/gpt-6.1-sol), role independent, operator review platform quick check, 1 draw(s), 2026-10-30T16:21:37Z.
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
| 1 | `verifiable` | **PASS** | code+model | The verifier objectively checks complete program outputs against fixed numerical references, installs no tooling at verification time, and has successful repeat-run records. |
| 2 | `outcome_verified` | **PASS** | code+model | The instruction specifies physical quantities and an output contract, while grading accepts any computational approach that produces those quantities within tolerance. |
| 3 | `functional_verification` | **PASS** | code+model | The emitter executes the submitted program on ten inputs and the judge validates its exit status and actual numerical output rather than source keywords or self-reported success. |
| 4 | `verification_explanation_quality` | **PASS** | code+model | The README explains every graded check and supports the tolerances with convergence studies, finer quadrature, higher-precision solves, independent pure-gas calculations, and known limiting cases. |
| 5 | `binary_reward` | **PASS** | code+model | The harness prewrites reward 0 and every reachable finish call writes only 0 or 1, with infrastructure failures removing the reward instead of assigning partial credit. |

## Oracle

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 6 | `solvable` | **FAIL** | code+model (model) | The oracle is legitimate and has a recorded passing run, but that satisfies only the working-solution part of this criterion. task.toml lines 22–23 explicitly estimate 16 best-case hours for an expert who already knows the approach, consistent with the substantial scattering, high-order bracket, and convergence work in solution/transport.py. That is materially beyond the standard's few-hour known-approach implementation requirement. Evidence: task.toml: "# Best-case hours for an expert who knows the approach. Not the agent budget.\nexpert_time_estimate_hours = 16" |
| 7 | `solution_quality` | **PASS** | code+model | The separately stored oracle computes scattering cross sections, collision brackets, linear-system solutions, and convergence tails from the supplied parameters without embedding the graded answers. |
| 8 | `solution_explanation_quality` | **PASS** | code+model | The README accurately connects classical scattering, stable collision brackets, constrained transport problems, and algebraic convergence to the oracle's implementation. |

## Difficulty

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 9 | `difficult` | **PASS** | code+model | Accurate orbiting-collision integration and stable, converged unequal-mass Chapman-Enskog brackets require genuine computational kinetic-theory expertise rather than obscure recall or clerical work. |
| 10 | `essential_difficulty` | **PASS** | code+model | The demanding accuracy distinguishes converged transport solutions from physically meaningful but insufficient truncations, while the output schema itself remains only four plainly specified numbers. |
| 11 | `difficulty_explanation_quality` | **PASS** | code+model | The README identifies the intrinsic numerical and physical challenges, explains that the reference data are computed from the model potential, and names thermophysical-property specialists as the professional users. |
| 12 | `expert_time_estimate` | **PASS** | code+model | The nonzero 16-hour estimate is consistent across metadata and README and is plausible for deriving, implementing, and validating this specialized numerical calculation. |

## Safety

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 13 | `anti_cheat_robustness` | **PASS** | code+model | Answers and judge tooling exist only in the separate verifier, submitted artifacts cannot replace them, and the targeted reward-forging control ran and scored 0. |
| 14 | `task_security` | **PASS** | code+model | The assets contain task-scoped numerical computation, container setup, and bounded hardening controls, with no credential exfiltration, host-access mechanism, concealed executable payload, or unrelated interference. |
| 15 | `verifier_execution_isolation` | **PASS** | code+model | Submitted code runs as uid 1500 under privilege dropping, root protects and decides the reward in a separate interpreter, and bounded stream draining plus uid-wide cleanup stops descendants. |
| 16 | `do_not_modify_enforced` | **PASS** | code+model | The stated read-only runtime folder is enforced by root-owned extraction and unprivileged execution, and the instruction names no additional agent-side artifact that must remain unchanged. |

## Reproducibility

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 17 | `deterministic_reproducible` | **PASS** | code+model | Both images pin their bases and Python dependencies, grading uses fixed inputs and references without live services or randomness, and the reported regrades agree. |
| 18 | `separate_verifier_configured` | **PASS** | code+model | The verifier receives the declared submission archive, owns all reference inputs and tooling, and uses the same pinned numerical runtime as the agent image. |
| 19 | `environment_hygiene` | **PASS** | code+model | The agent image contains no tests, oracle, or test-only packages, while verifier tooling is baked separately and both apt installations update, clean their lists, and avoid version pins. |
| 20 | `resource_configuration` | **PASS** | code+model | The declared two-CPU, 4-GB runtime and 28800-second agent budget match the instruction, and the verifier budget accommodates ten 600-second cases plus bounded extraction and judging. |
| 21 | `artifact_efficiency` | **NOT_APPLICABLE** | code+model (model) | The answer is a single agent-produced Python source file with no large fixed baseline or dependency tree to transfer. |

## Specification

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 22 | `test_instruction_alignment` | **PASS** | code+model | The five tests and runtime harness cover the stated file, JSON, numerical, execution, and size requirements without imposing an unstated algorithm or output convention. |
| 23 | `instruction_concision` | **PASS** | code+model | The instruction supplies necessary physical conventions and deployment constraints, names the absolute deliverable path, and avoids procedural solution hints or unrelated narrative. |
| 24 | `structured_data_schema` | **PASS** | code+model | The instruction normatively requires exactly one JSON object with exactly four named numerical members and defines the physical meaning of each member. |
| 25 | `typos` | **PASS** | code+model | The deliverable path, command arguments, JSON identifiers, case identifiers, and referenced generator and oracle files agree across the instruction, implementation, and tests. |

## Package

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 26 | `reviewable` | **PASS** | code+model | The README provides domain context and an auditable chain from the potential through generated expected values to independent checks and numerical uncertainty estimates. |
| 27 | `category_and_tags` | **PASS** | code+model | Science and Physics accurately identify the primary domain, and the kinetic-theory, Chapman-Enskog, gas-mixture, thermal-diffusion, and classical-scattering tags are specific and relevant. |
| 28 | `task_name` | **PASS** | code+model | The slug chapman-enskog-transport is descriptive lowercase kebab-case with exactly three tokens and matches the declared task name. |
| 29 | `task_readme` | **PASS** | code+model | The README contains all required sections and supplies useful mathematical, verification, provenance, and professional context rather than merely duplicating the deliverable code. |
| 30 | `task_toml_schema` | **PASS** | code | all 24 checks pass or do not apply (24 decided by code, 0 by the model) |
| 31 | `no_extraneous_files` | **PASS** | code+model | The supplied files serve environment setup, submission verification, the oracle, reference generation and validation, documented hardening controls, or required task scaffolding. |
| 32 | `ctrf_reporting` | **PASS** | code+model | The root judge runs pytest with --ctrf, copies its report to /logs/verifier/ctrf.json, and creates a per-test fallback report on early grading exits. |

## Realism

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 33 | `interesting` | **PASS** | code+model | Reference transport calculations for validating gas-property libraries are credible paid scientific-software work with practical value to thermophysical-property specialists. |

## Novelty

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 34 | `novel` | **NOT_PROVIDED** | code (originality) | evidence not provided: originality: deferred to the full review: the quick check does not search originality (the full review runs tb4 originality and judges novel) |

## Agentic

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 35 | `agentic` | **PASS** | code+model | Developing a stable and sufficiently fast solver across orbiting collisions and slow mixture convergence requires numerical experiments, profiling, validation, debugging, and iterative adaptation. |

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
| `outcome.process` Tests that look at the process, history or tools the agent used. | code: process_checks | fact | – | tests that look at process or tools: tests/ce_mix.py:41: species' mean velocities, which vanish then), r_i1 = -(15/4) x_i sqrt(2T / m_i);; tests/ce_mix.py:52: with k near 5 at m2 = 40, x1 = 0.05 (the light molecules' collision rate is not constant in speed, which the; tests/ce_ref.py:10: OUTERMOST root of F. h(r) = r^3 V'(r) / 2 is the E b^2 at which V + E b^2 / r^2 is stationary; below its maximum; tests/checks.py:483: say("[conv] the last P at which any value is outside: %d" % max([p for p in outside if outside[p]] or [0])); tests/emit.py:12: It holds NO expected values: the answers live in tests/expected.json, which only; tests/tb4judge.py:5: load_json(path), loads_json(text)  JSON in which every member is named once and no NaN or Infinity appears |
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
| `verification_expl.section` README.md has a filled ## Verification explanation (present, no template text, 40+ words). | code: README scan | PASS | README.md | `## Verification explanation` is filled (984 words) |
| `verification_expl.tolerances` When the tests use tolerances or thresholds, the verification explanation addresses the bounds. | code: tests + README scan | PASS | tests/ce_mix.py:324, tests/ce_ref.py:231, tests/checks.py:2, tests/checks.py:20, README.md | the tests use tolerances (tests/ce_mix.py:324, tests/ce_ref.py:231, tests/checks.py:2, tests/checks.py:20) and the verification explanation addresses them |
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
| `solution_expl.section` README.md has a filled ## Solution explanation. | code: README scan | PASS | README.md | `## Solution explanation` is filled (363 words) |
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
| `difficulty_expl.section` README.md has a filled ## Difficulty explanation. | code: README scan | PASS | README.md | `## Difficulty explanation` is filled (652 words) |
| `difficulty_expl.no_scores` The difficulty explanation cites no pass rates or model results. | code: README scan | PASS | README.md | no pass rates or attempt scores in the difficulty explanation |
| `difficulty_explanation_quality.lint` tb4-lint finds no FAIL row tagged [difficulty_explanation_quality]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [difficulty_explanation_quality] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `expert_time_estimate` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `expert_time_estimate.decider` The expert_time_estimate decider (structured.CODE_CRITERIA) holds: fail when it is missing, not a number, below 0.1 h or above 160 h, or the README states a different expert time; otherwise pass (no eight-hour cap). | code: expert_time_estimate decider | PASS | task.toml, README.md, live: starter-pack gates_static.py lint | range: expert_time_estimate_hours = 16 (plausible range; no eight-hour cap); readme_agrees: README expert time matches task.toml; lint: no FAIL row tagged [expert_time_estimate] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `expert_time.facts` The estimate next to the difficulty explanation (for the model: is it plausible?). | code: expert_time_facts | fact | – | expert_time_estimate_hours 16; difficulty explanation 652 words; instruction 714 words |

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
| `isolation.kill_by_uid` Where tests/ kills runner processes by uid (the 1.6.0 hardening standard). | code: kill_by_uid | fact | – | kill-by-uid at tests/emit.py:86, tests/test.sh:47, tests/test.sh:57, tests/test.sh:59; privilege drops at tests/test.sh:57, 232 |
| `isolation.lint` tb4-lint finds no FAIL row tagged [verifier_execution_isolation]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [verifier_execution_isolation] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `do_not_modify_enforced` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `protect.phrases` The do-not-modify constraints the instruction states. | code: protect_phrases | fact | – | do-not-modify constraints in the instruction: instruction.md:7: Write `/app/output/transport.py`, a Python program that the checker runs as `python3 transport.py A R X T`, where `A` is the core ratio `a / |
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
| `resources.values` The configured timeouts and resources, and which template defaults are kept. | code: resources | fact | – | agent timeout 28800.0, verifier timeout 6460.0, cpus 2, memory_mb 4096, storage_mb 10240, gpus 0; template defaults kept: ['storage_mb'] |
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
| `alignment.requirements_bound` On a v2 task, tests/requirements.json binds every constraint sentence to a graded test that exists (the starter pack's requirements gate). A legacy task without requirements.json is not judged here. | code: requirements | fact | – | requirements PASS (live: starter-pack gates_static.py requirements): syntactic traceability: 21 requirements, 5 graded tests, 10 constraint sentences; every quote, test and constraint is bound; semantic assertion coverage is not evaluated |
| `alignment.lint` tb4-lint finds no FAIL row tagged [test_instruction_alignment]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [test_instruction_alignment] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `instruction_concision` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `instruction.shape` Instruction length, relative paths, headings and tool mentions. | code: instruction_shape | fact | – | 706 words; relative paths in backticks: ['transport.py']; headings: 0; tool/library mentions: none |
| `instruction.cause_named` The instruction does not name the root cause or the exact place to change (the screen's leak question): sentences that might. | code: instruction_names_cause | fact | – | no sentence names a cause or a place to change (by pattern) |
| `instruction_concision.lint` tb4-lint finds no FAIL row tagged [instruction_concision]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [instruction_concision] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `structured_data_schema` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `schema.outputs` Where the tests parse structured output, and whether the instruction names its fields. | code: structured_outputs | fact | – | the tests parse structured output at tests/checks.py:72, tests/checks.py:98, tests/generate.py:81, tests/tb4judge.py:10, tests/tb4judge.py:57, tests/tb4judge.py:152; the instruction does not name fields, columns, keys or a schema |
| `structured_data_schema.lint` tb4-lint finds no FAIL row tagged [structured_data_schema]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [structured_data_schema] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `typos` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `typos.decider` The typos decider (structured.CODE_CRITERIA) holds: fail only when a path instruction.md names does not exist (the agent acts on it); a README path that resolves nowhere is a WARN for the reviewer, never a FAIL; an /app path in a cloned repository is listed as unverified. | code: typos decider | PASS | live: starter-pack gates_static.py readme-code, live: starter-pack gates_static.py lint | paths: 38 named path(s) checked, none missing from instruction.md; readme_code: readme-code PASS: 42 README references checked; 0 dangling, unbacked or inconsistent; 0 receipt-only (wrapper evidence, needs a disposition); lint: no FAIL row tagged [typos] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

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
| `category_and_tags.decider` The category_and_tags decider (structured.CODE_CRITERIA) holds: fail when category is not one of the seven domains, subcategory is empty, tags are empty or repeated, or the README metadata tags disagree with task.toml. | code: category_and_tags decider | PASS | task.toml, live: starter-pack gates_static.py lint | metadata_subcategory_present: [metadata].subcategory is set; metadata_tags_present: [metadata].tags is set; category_allowed: category is one of the seven domains; tags_valid: tags is a non-empty list of distinct strings; tags_specific: no generic tag among 5; readme_tags: README tags match task.toml; lint: no FAIL row tagged [category_and_tags] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

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

Model note (not a verdict): Fixed code verdict: PASS.

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

Model note (not a verdict): Fixed code verdict: NOT_PROVIDED; the full originality review and its evidence remain outstanding.

### `agentic` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `agentic.attempts` What the attempts show (number of steps, tools used). | code: attempts_present | fact | – | no attempts |
| `agentic.lint` tb4-lint finds no FAIL row tagged [agentic]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [agentic] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

