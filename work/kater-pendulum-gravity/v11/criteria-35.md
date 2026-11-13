# kater-pendulum-gravity: 35 criteria

31 pass, 2 fail (0 disputed), 1 not applicable, 0 inconclusive, 1 inconclusive: evidence not provided (routed to the reviewer). Reviewer: astra (openai/gpt-6.1-sol), role independent, operator review platform quick check, 1 draw(s), 2026-10-28T01:54:52Z.
Rubric: `/home/ubuntu/tb4-toolkit-1.25/tbench-assess/src/tbench_assess/rubrics/tb4-35.toml`

| Section | Pass | Fail | Not provided | N/A |
|---|---|---|---|---|
| Verifier | 4 | 1 | 0 | 0 |
| Oracle | 3 | 0 | 0 | 0 |
| Difficulty | 4 | 0 | 0 | 0 |
| Safety | 4 | 0 | 0 | 0 |
| Reproducibility | 4 | 0 | 0 | 1 |
| Specification | 3 | 1 | 0 | 0 |
| Package | 7 | 0 | 0 | 0 |
| Realism | 1 | 0 | 0 | 0 |
| Novelty | 0 | 0 | 1 | 0 |
| Agentic | 1 | 0 | 0 | 0 |

## Verifier

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 1 | `verifiable` | **PASS** | code+model | The verifier deterministically executes the submission and compares its complete JSON output against fixed numerical references, with tooling baked into the verifier image and repeat controls reporting consistent results. |
| 2 | `outcome_verified` | **PASS** | code+model | The instruction specifies physical results and an output interface, while the tests compare those results without requiring the oracle's calibration, clock reconstruction, or period-estimation approach. |
| 3 | `functional_verification` | **PASS** | code+model | The checker runs reduce.py on four staged sessions and validates its exit status and numerical outputs rather than inspecting source keywords or accepting self-reported success. |
| 4 | `verification_explanation_quality` | **FAIL** | code+model (model) | README.md thoroughly explains the six output checks and calibrates the numerical tolerances against alternative reductions. However, tests/emit.py line 43 and run_case's stream-limit branch also fail a submission after more than 1 MiB of stderr, a grading condition absent from the verification explanation. This omission matters because numerically correct programs can fail solely through legitimate diagnostic output, despite instruction.md promising that stderr is ignored. Evidence: README.md: "recording its exit status and its whole standard output"; tests/emit.py: "MAX_STDERR_BYTES = 1 << 20     # more stderr fails the case too; every byte written counts, not what is left"; instruction.md: "Anything it writes to standard error is ignored." |
| 5 | `binary_reward` | **PASS** | code+model | tests/test.sh initializes the reward to 0 and reaches its final reward writes only through finish calls carrying 0 or 1, with no fractional scoring path. |

## Oracle

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 6 | `solvable` | **PASS** | code+model | The recorded oracle passes, and its compact, legitimate numerical implementation is reasonably implementable in a few hours by an expert already knowing the reduction strategy. |
| 7 | `solution_quality` | **PASS** | code+model | The oracle genuinely reconstructs clocks, calibrates the camera, estimates periods and release angles, and computes g and k from session measurements, with the implementation kept in a separate source file. |
| 8 | `solution_explanation_quality` | **PASS** | code+model | The Solution explanation connects the apparatus to the clock, pivot-assignment, camera-calibration and physical-reduction insights and accurately follows the oracle's implementation. |

## Difficulty

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 9 | `difficult` | **PASS** | code+model | Recovering true time and swing amplitude from an uncalibrated oblique view while accounting for rolling pivots, moved weights and inconsistent logbook entries requires genuine experimental-metrology and nonlinear-modeling expertise. |
| 10 | `essential_difficulty` | **PASS** | code+model | The intended challenge is physical inference and instrument reduction, with a small explicit output schema and numerical tolerances justified through alternative algorithms rather than arbitrary formatting precision. |
| 11 | `difficulty_explanation_quality` | **PASS** | code+model | The Difficulty explanation identifies concrete inference problems, explains their effects for non-specialists, describes the synthetic instrument simulation, and names laboratories that would perform this work without substituting model scores. |
| 12 | `expert_time_estimate` | **PASS** | code+model | The consistent, nonzero ten-hour expert estimate is plausible for the complete calibration, implementation and validation problem and is distinct from the eight-hour agent budget. |

## Safety

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 13 | `anti_cheat_robustness` | **PASS** | code+model | The separate agent image contains only public session inputs, the reported full leak scan found no answers, and the verifier isolates unreadable references and root-owned observations while the targeted reward-forging control was rejected. |
| 14 | `task_security` | **PASS** | code+model | The executable assets perform legitimate setup, simulation, reduction and verification, including a transparent bounded adversarial control, without credential collection, data exfiltration, host access or concealed execution. |
| 15 | `verifier_execution_isolation` | **PASS** | code+model | Submitted code executes as uid 1500 after the reward channel is locked, root judges only captured output in a fresh interpreter, and cleanup kills all remaining runner processes, including detached descendants. |
| 16 | `do_not_modify_enforced` | **PASS** | code+model | The specified read-only deliverable and session folders are root-owned and unwritable by the runner, and each staged session is additionally checked with complete before-and-after tree digests. |

## Reproducibility

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 17 | `deterministic_reproducible` | **PASS** | code+model | The task uses fixed generated inputs, explicit noise seeds, digest-pinned base images and version-pinned Python dependencies, with recorded verifier regrades agreeing on reward and test statuses. |
| 18 | `separate_verifier_configured` | **PASS** | code+model | The verifier receives the declared submission artifact, owns its fixed cases and expected values, preinstalls its tooling, and matches the agent image's numerical runtime versions. |
| 19 | `environment_hygiene` | **PASS** | code+model | The agent image copies only data and installs task-runtime dependencies, the verifier owns pytest and CTRF tooling, and both Dockerfiles correctly combine apt update, unversioned installation and cache cleanup. |
| 20 | `resource_configuration` | **PASS** | code+model | The declared two CPUs and 4 GB suit the modest numerical workload, the agent receives 28800 seconds, and the 3000-second verifier budget accommodates four 660-second emit phases plus extraction, judging and cleanup headroom. |
| 21 | `artifact_efficiency` | **NOT_APPLICABLE** | code+model (model) | The answer is an inherently small agent-produced Python source file with no large source baseline or dependency tree to transfer, while fixed test inputs are baked into the verifier. |

## Specification

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 22 | `test_instruction_alignment` | **FAIL** | code+model (model) | instruction.md line 7 explicitly promises that anything written to stderr is ignored. In contrast, tests/emit.py line 43 defines a 1 MiB stderr limit, and run_case rejects the case when that stream exceeds it. A valid reduction emitting detailed fit diagnostics can therefore fail every output test under an unstated logging restriction. Evidence: instruction.md: "Anything it writes to standard error is ignored."; tests/emit.py: "MAX_STDERR_BYTES = 1 << 20     # more stderr fails the case too; every byte written counts, not what is left"; tests/emit.py: "if st[2] > st[1]:" and "raise ValueError(why)" |
| 23 | `instruction_concision` | **PASS** | code+model | The instruction gives a short laboratory context, absolute runtime locations, the necessary output contract and checker-runtime constraints without prescribing a reduction procedure or adding roleplay. |
| 24 | `structured_data_schema` | **PASS** | code+model | The instruction normatively defines all five top-level JSON members, the exact nested pivot and run keys, numerical types, units and physical meanings. |
| 25 | `typos` | **PASS** | code+model | The deliverable name, session layout, runtime paths, CLI invocation and JSON identifiers consistently match across the instruction, Dockerfiles, oracle and verifier. |

## Package

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 26 | `reviewable` | **PASS** | code+model | The README supplies the domain reasoning and data provenance, while generate.py exposes the simulation and closed-form expected-value derivations independently of the reduction oracle. |
| 27 | `category_and_tags` | **PASS** | code+model | Science and Physics match the primary task, and the consistent tags specifically identify gravimetry, reversible pendulums, rolling pivots, camera calibration and time-base reconstruction. |
| 28 | `task_name` | **PASS** | code+model | kater-pendulum-gravity is a descriptive lowercase kebab-case slug with exactly three words and matches the configured task identifier. |
| 29 | `task_readme` | **PASS** | code+model | The README includes all required sections and provides useful reviewer-facing physics, provenance, implementation and validation context without duplicating the source implementation. |
| 30 | `task_toml_schema` | **PASS** | code | all 24 checks pass or do not apply (24 decided by code, 0 by the model) |
| 31 | `no_extraneous_files` | **PASS** | code+model | The listed assets serve the public inputs, oracle, verifier, reproducible data generation, tolerance validation or documented adversarial control, with no identified scratch or redundant build artifacts. |
| 32 | `ctrf_reporting` | **PASS** | code+model | The root pytest invocation emits a six-test CTRF report that is copied to /logs/verifier/ctrf.json, and graded early failures receive a fallback per-test report. |

## Realism

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 33 | `interesting` | **PASS** | code+model | An unattended gravity-reduction program for imperfect camera and pendulum measurements is credible, valuable work for metrology and geophysics laboratories despite its niche apparatus. |

## Novelty

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 34 | `novel` | **NOT_PROVIDED** | code (originality) | evidence not provided: originality: deferred to the full review: the quick check does not search originality (the full review runs tb4 originality and judges novel) |

## Agentic

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 35 | `agentic` | **PASS** | code+model | Building a reliable session reducer requires inspecting instrument records, exploring example data, testing clock and camera models, diagnosing discrepancies and iterating on numerical estimates rather than simple recall or a single command. |

## Structured review

Methods: 2 by code, 33 by one model question with code checks, 0 by one model question. A code check fails a criterion only on present, current evidence; a check without its record is not provided (the model's verdict stands). A code verdict is never the model's.

### `verifiable` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `verifiable.nop_scores_zero` The unchanged environment (nop) scores 0. | record nop | PASS | kater-pendulum-gravity-gates/nop.json | nop PASS: nop scored 0 on 1 of 1 runs |
| `verifiable.runtime_installs` tests/test.sh installs no verifier tooling at verify time (apt-get install, curl / sh, pip install other than the agent's pinned -r /app/ manifest, npm install, uv tool install). | code: tests/test.sh scan | PASS | tests/test.sh | tests/test.sh installs nothing at verify time (the agent's pinned manifest aside) |
| `verifiable.lint` tb4-lint finds no FAIL row tagged [verifiable]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [verifiable] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `verifiable.pack_rules` No starter-pack static finding X3.3 or X3.4: the verifier grades the whole captured output or file, or rejects an oversized one, never a truncated prefix or suffix (F01, F02). | code: pack_rules_verifiable | fact | – | no X3.3/X3.4 finding in the placeholders, lint, requirements, budget, readme-claims, readme-code, structure, content record(s) |

### `outcome_verified` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `outcome.process` Tests that look at the process, history or tools the agent used. | code: process_checks | fact | – | tests that look at process or tools: tests/emit.py:12: It holds NO expected values: the answers live in tests/expected.json, which only; tests/estimator_bounds.py:9: shipped data exactly) and reduced four ways, which are compared with the truth the data were built from.; tests/generate.py:8: (tests/cases, which the checker stages one at a time for the submitted program). expected.json holds the truth; tests/generate.py:31: * a 16-bit frame counter of delivered frames, which wraps;; tests/generate.py:32: * stalls: the sensor misses 2 to 15 frames that the counter never counts (never the frame in which the; tests/generate.py:198: first = int(round(held * rate))                  # the sensor frame at which the catch lets go |
| `outcome_verified.lint` tb4-lint finds no FAIL row tagged [outcome_verified]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [outcome_verified] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `functional_verification` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `functional.source_grep` Tests that read source files as text (keyword checks). | code: source_grep | fact | – | no test reads source files as text |
| `functional_verification.lint` tb4-lint finds no FAIL row tagged [functional_verification]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [functional_verification] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `verification_explanation_quality` — **FAIL** (code+model) — decisive: `model`

Model (one question): FAIL

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `verification_expl.section` README.md has a filled ## Verification explanation (present, no template text, 40+ words). | code: README scan | PASS | README.md | `## Verification explanation` is filled (961 words) |
| `verification_expl.tolerances` When the tests use tolerances or thresholds, the verification explanation addresses the bounds. | code: tests + README scan | PASS | tests/estimator_bounds.py:303, tests/estimator_bounds.py:355, tests/estimator_bounds.py:405, tests/estimator_bounds.py:406, README.md | the tests use tolerances (tests/estimator_bounds.py:303, tests/estimator_bounds.py:355, tests/estimator_bounds.py:405, tests/estimator_bounds.py:406) and the verification explanation addresses them |
| `verification_explanation_quality.lint` tb4-lint finds no FAIL row tagged [verification_explanation_quality]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [verification_explanation_quality] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `verification_expl.pack_rules` No starter-pack static finding C2: a cleanup guarantee (no descendant or process survives) is no broader than the cleanup code (F06). | code: pack_rules_verification_explanation_quality | fact | – | no C2 finding in the placeholders, lint, requirements, budget, readme-claims, readme-code, structure, content record(s) |

### `binary_reward` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `binary_reward.decider` The binary_reward decider (structured.CODE_CRITERIA) holds: fail when a reward write has a fractional shape (a ratio, a weighted sum, round/format of a score, a reward -= penalty, a non-0/1 literal) or a recorded run wrote a reward other than 0 or 1; not_provided when the scan finds no reward write; else pass with the write sites cited. | code: binary_reward decider | PASS | tests/test.sh:41, tests/test.sh:42, tests/test.sh:101, tests/test.sh:102, live: starter-pack gates_static.py lint | static_writes: 4 reward write site(s), none fractional: tests/test.sh:41, tests/test.sh:42, tests/test.sh:101, tests/test.sh:102; recorded_rewards: every recorded reward is 0 or 1: oracle (1 reward(s)), nop (1 reward(s)), verifier-repeat (0 reward(s)), tamper (1 reward(s)), wrong-answers (0 reward(s)); lint: no FAIL row tagged [binary_reward] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `solvable` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `solvable.oracle_passes` The oracle scored 1 on every recorded run (n of n). | record oracle | PASS | kater-pendulum-gravity-gates/oracle.json | oracle 1 of 1 runs scored 1; oracle PASS: oracle scored 1 on 1 of 1 runs |
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
| `solution_expl.section` README.md has a filled ## Solution explanation. | code: README scan | PASS | README.md | `## Solution explanation` is filled (440 words) |
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
| `difficulty_expl.section` README.md has a filled ## Difficulty explanation. | code: README scan | PASS | README.md | `## Difficulty explanation` is filled (877 words) |
| `difficulty_expl.no_scores` The difficulty explanation cites no pass rates or model results. | code: README scan | PASS | README.md | no pass rates or attempt scores in the difficulty explanation |
| `difficulty_explanation_quality.lint` tb4-lint finds no FAIL row tagged [difficulty_explanation_quality]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [difficulty_explanation_quality] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `expert_time_estimate` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `expert_time_estimate.decider` The expert_time_estimate decider (structured.CODE_CRITERIA) holds: fail when it is missing, not a number, below 0.1 h or above 160 h, or the README states a different expert time; otherwise pass (no eight-hour cap). | code: expert_time_estimate decider | PASS | task.toml, README.md, live: starter-pack gates_static.py lint | range: expert_time_estimate_hours = 10 (plausible range; no eight-hour cap); readme_agrees: README expert time matches task.toml; lint: no FAIL row tagged [expert_time_estimate] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |
| `expert_time.facts` The estimate next to the difficulty explanation (for the model: is it plausible?). | code: expert_time_facts | fact | – | expert_time_estimate_hours 10; difficulty explanation 877 words; instruction 491 words |

### `anti_cheat_robustness` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `anti_cheat.cheats_scored_zero` Every shipped cheat trial scored 0. | record tamper | PASS | kater-pendulum-gravity-gates/tamper.json | every cheat scored 0: forge-reward PASS (reward 0.0) |
| `anti_cheat.readable_answers` The runner uid cannot read /tests, /logs or a pristine copy in the verifier image. | record readable-answers | PASS | kater-pendulum-gravity-gates/readable-answers.json | readable-answers PASS: nothing under /tests is readable by the runner uid; /pristine exposes nothing |
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
| `isolation.kill_by_uid` Where tests/ kills runner processes by uid (the 1.6.0 hardening standard). | code: kill_by_uid | fact | – | kill-by-uid at tests/emit.py:64, tests/test.sh:47, tests/test.sh:57, tests/test.sh:59; privilege drops at tests/test.sh:57, 232 |
| `isolation.lint` tb4-lint finds no FAIL row tagged [verifier_execution_isolation]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [verifier_execution_isolation] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `do_not_modify_enforced` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `protect.phrases` The do-not-modify constraints the instruction states. | code: protect_phrases | fact | – | do-not-modify constraints in the instruction: instruction.md:7: The checker runs the program once on each of four other sessions recorded with the same rig, which differ from the two examples within the l |
| `do_not_modify_enforced.lint` tb4-lint finds no FAIL row tagged [do_not_modify_enforced]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [do_not_modify_enforced] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `deterministic_reproducible` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `reproducible.repeat_records` Repeated clean runs agree: the oracle-determinism and verifier-repeat records pass. | record oracle-determinism + verifier-repeat | PASS | kater-pendulum-gravity-gates/oracle-determinism.json, kater-pendulum-gravity-gates/verifier-repeat.json | oracle-determinism PASS: 1 oracle run and 2 verifier regrades report the same reward and the same 6 test ids with the same statuses; verifier-repeat PASS: 2 regrades of one oracle trial report reward 1 and the same 6 test ids and statuses |
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
| `resources.values` The configured timeouts and resources, and which template defaults are kept. | code: resources | fact | – | agent timeout 28800.0, verifier timeout 3000.0, cpus 2, memory_mb 4096, storage_mb 10240, gpus 0; template defaults kept: ['storage_mb'] |
| `resource_configuration.lint` tb4-lint finds no FAIL row tagged [resource_configuration]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [resource_configuration] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `artifact_efficiency` — **NOT_APPLICABLE** (code+model) — decisive: `model`

Model (one question): NOT_APPLICABLE

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `artifacts.whole_tree` task.toml artifacts do not name the whole tree (/app, /root, /home or /). | code: artifacts_scope | fact | – | task.toml artifacts = ['/app/submission'] |
| `artifacts.missing_vs_empty` A missing submission is not graded (the missing-artifact control writes no reward). | record missing-artifact | PASS | kater-pendulum-gravity-gates/missing-artifact.json | missing-artifact PASS: missing-artifact: no reward written, verifier error RewardFileNotFoundError |
| `artifacts.no_partial_patch` A damaged submission is not graded (the partial-artifact control writes no reward). | record partial-artifact | PASS | kater-pendulum-gravity-gates/partial-artifact.json | partial-artifact PASS: partial-artifact: no reward written, verifier error RewardFileNotFoundError |
| `artifacts.collect_faithful` The git-diff-patch collect's fail-safe mechanics (atomic capture, pinned diff baseline, excluding or not smuggling build/dependency trees, a loud reward 0 on an apply failure, never grading a partial tree, manifest reset/reinstall) hold -- credited by equivalent safeguards and the missing/partial-artifact controls; N/A when the task has no git-diff-patch collect. | code: collect_faithful | fact | – | no git-diff-patch [[verifier.collect]]: the patch-mechanism rules do not apply |
| `artifacts.lint` tb4-lint finds no FAIL row tagged [artifact_efficiency]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [artifact_efficiency] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `test_instruction_alignment` — **FAIL** (code+model) — decisive: `model`

Model (one question): FAIL

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `alignment.requirements_bound` On a v2 task, tests/requirements.json binds every constraint sentence to a graded test that exists (the starter pack's requirements gate). A legacy task without requirements.json is not judged here. | code: requirements | fact | – | requirements PASS (live: starter-pack gates_static.py requirements): syntactic traceability: 14 requirements, 6 graded tests, 7 constraint sentences; every quote, test and constraint is bound; semantic assertion coverage is not evaluated |
| `alignment.lint` tb4-lint finds no FAIL row tagged [test_instruction_alignment]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [test_instruction_alignment] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `instruction_concision` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `instruction.shape` Instruction length, relative paths, headings and tool mentions. | code: instruction_shape | fact | – | 483 words; relative paths in backticks: ['reduce.py', 'session.json']; headings: 0; tool/library mentions: none |
| `instruction.cause_named` The instruction does not name the root cause or the exact place to change (the screen's leak question): sentences that might. | code: instruction_names_cause | fact | – | no sentence names a cause or a place to change (by pattern) |
| `instruction_concision.lint` tb4-lint finds no FAIL row tagged [instruction_concision]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [instruction_concision] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `structured_data_schema` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `schema.outputs` Where the tests parse structured output, and whether the instruction names its fields. | code: structured_outputs | fact | – | the tests parse structured output at tests/tb4judge.py:10, tests/tb4judge.py:57, tests/tb4judge.py:152, tests/tb4judge.py:153, tests/tb4judge.py:159, tests/tb4judge.py:180; the instruction does not name fields, columns, keys or a schema |
| `structured_data_schema.lint` tb4-lint finds no FAIL row tagged [structured_data_schema]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [structured_data_schema] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `typos` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `typos.decider` The typos decider (structured.CODE_CRITERIA) holds: fail only when a path instruction.md names does not exist (the agent acts on it); a README path that resolves nowhere is a WARN for the reviewer, never a FAIL; an /app path in a cloned repository is listed as unverified. | code: typos decider | PASS | live: starter-pack gates_static.py readme-code, live: starter-pack gates_static.py lint | paths: 36 named path(s) checked, none missing from instruction.md; readme_code: readme-code PASS: 34 README references checked; 0 dangling, unbacked or inconsistent; 0 receipt-only (wrapper evidence, needs a disposition); lint: no FAIL row tagged [typos] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

### `reviewable` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `reviewable.literals` Long literal expected values in the tests (their derivation). | code: hardcoded_expected | fact | – | literal expected values in the tests (derivation to check): tests/generate.py:61, tests/generate.py:62, tests/generate.py:63, tests/generate.py:74, tests/generate.py:75, tests/generate.py:76, tests/generate.py:86, tests/generate.py:87 |
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
| `task_name.facts` The slug and its tokens (for the model: is it descriptive?). | code: task_name_facts | fact | – | slug 'kater-pendulum-gravity': 3 token(s) ['kater', 'pendulum', 'gravity'] |

### `task_readme` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `readme.experience` README.md has a filled ## Relevant experience. | code: README scan | PASS | README.md | `## Relevant experience` is filled (29 words) |
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

Model note (not a verdict): The fixed code verdict is PASS.

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

Model note (not a verdict): The fixed verdict is NOT_PROVIDED; originality searching and its full-review disposition are absent from the supplied evidence.

### `agentic` — **PASS** (code+model)

Model (one question): PASS

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `agentic.attempts` What the attempts show (number of steps, tools used). | code: attempts_present | fact | – | no attempts |
| `agentic.lint` tb4-lint finds no FAIL row tagged [agentic]. | live: starter-pack gates_static.py lint | PASS | live: starter-pack gates_static.py lint | no FAIL row tagged [agentic] (tb4-lint: 77 rows, 0 FAIL, 0 WARN (warnings never block)) |

