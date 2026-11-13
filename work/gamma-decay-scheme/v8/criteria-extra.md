# gamma-decay-scheme: 5 criteria

5 pass, 0 fail (0 disputed), 0 not applicable, 0 inconclusive. Reviewer: astra (openai/gpt-6.1-sol), role independent, operator review platform quick check, 3 draw(s), 2026-11-10T23:48:22Z.
Rubric: `/home/ubuntu/tb4-toolkit-1.26/tbench-assess/src/tbench_assess/rubrics/audit-extra.toml`

| Section | Pass | Fail | N/A |
|---|---|---|---|
| Audit | 3 | 0 | 0 |
| Feasibility | 2 | 0 | 0 |

## Audit

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 1 | `english_only` | **PASS** | code+model | The instructions, README, station notes, code comments, docstrings and human-readable messages are all in English. |
| 2 | `no_host_paths` | **PASS** | code | all 1 checks pass or do not apply (1 decided by code, 0 by the model) |
| 3 | `harbor_format` | **PASS** | code | all 19 checks pass or do not apply (19 decided by code, 0 by the model) |

## Feasibility

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 4 | `discoverable` | **PASS** | code+model | The output path, JSON structure, numeric types, intensity floor, ordering rules, minimum-level requirement and tolerances are stated in instruction.md, while the tested energies, placements, intensities and half-lives are inferable from the documented run files and source tables, as demonstrated by the data-reading reduction and its recorded agreement with the generated ground truth. |
| 5 | `oracle_investigates` | **PASS** | code+model | The oracle reads the supplied calibration, background, singles and coincidence files to estimate gain, activity shares, line identities, doublets, level placements, intensities and lifetimes rather than inserting the target scheme or its answer values. |

## Structured review

Methods: 2 by code, 3 by one model question with code checks, 0 by one model question. A code check fails a criterion only on present, current evidence; a check without its record is not provided (the model's verdict stands). A code verdict is never the model's.

### `english_only` — **PASS** (code+model)

Model (one question): PASS pass 3/3

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `english.prefilter` No prose unit (instruction, README, comments; test data aside) is clearly in another language. | code: language pre-filter | PASS | – | 19 prose unit(s): none clearly in another language (the model judges mixed or subtle cases) |

### `no_host_paths` — **PASS** (code)

Source: starter-pack checks/task_ship.py hostpaths (the task) and hygiene.host_path_hits (a delivery's evidence/ and provenance/)

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `hostpaths` no path of the author's machine in the task (or in a delivery's evidence and provenance) | code: host-path scan | PASS | – | no host path found |

Model note (not a verdict): PASS, as fixed by the supplied code-decided verdict.

### `harbor_format` — **PASS** (code)

Source: `harbor tasks schema` (JSON Schema) + the TB4 [metadata] fields + task_rules.structure

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `schema` task.toml validates against `harbor tasks schema` and has no key the schema does not declare | code: harbor tasks schema | PASS | task.toml | task.toml validates against the Harbor schema |
| `file.instruction_md` instruction.md exists | tbench-assess task_rules.structure | PASS | – | instruction.md exists |
| `file.task_toml` task.toml exists | tbench-assess task_rules.structure | PASS | – | task.toml exists |
| `file.README_md` README.md exists | tbench-assess task_rules.structure | PASS | – | README.md exists |
| `file.environment_Dockerfile` environment/Dockerfile exists | tbench-assess task_rules.structure | PASS | – | environment/Dockerfile exists |
| `file.tests_Dockerfile` tests/Dockerfile exists | tbench-assess task_rules.structure | PASS | – | tests/Dockerfile exists |
| `file.tests_test_sh` tests/test.sh exists | tbench-assess task_rules.structure | PASS | – | tests/test.sh exists |
| `file.solution_solve_sh` solution/solve.sh exists | tbench-assess task_rules.structure | PASS | – | solution/solve.sh exists |
| `tests_present` tests/ holds at least one test_*.py | tbench-assess task_rules.structure | PASS | – | tests/ holds at least one test_*.py |
| `slug_format` folder name is lowercase kebab-case, at most 3 tokens | tbench-assess task_rules.structure | PASS | – | folder name is lowercase kebab-case, at most 3 tokens |
| `canary.instruction_md` instruction.md starts with the canary | tbench-assess task_rules.structure | PASS | – | instruction.md starts with the canary |
| `canary.README_md` README.md starts with the canary | tbench-assess task_rules.structure | PASS | – | README.md starts with the canary |
| `canary.task_toml` task.toml starts with the canary | tbench-assess task_rules.structure | PASS | – | task.toml starts with the canary |
| `canary.environment_Dockerfile` environment/Dockerfile starts with the canary | tbench-assess task_rules.structure | PASS | – | environment/Dockerfile starts with the canary |
| `canary.tests_Dockerfile` tests/Dockerfile starts with the canary | tbench-assess task_rules.structure | PASS | – | tests/Dockerfile starts with the canary |
| `canary.tests_test_sh` tests/test.sh starts with the canary | tbench-assess task_rules.structure | PASS | – | tests/test.sh starts with the canary |
| `canary.solution_solve_sh` solution/solve.sh starts with the canary | tbench-assess task_rules.structure | PASS | – | solution/solve.sh starts with the canary |
| `instruction_trailer` instruction.md ends with the exact trailer | tbench-assess task_rules.structure | PASS | – | instruction.md ends with the exact trailer |
| `readme_sections` README.md has the four required sections | tbench-assess task_rules.structure | PASS | – | README.md has the four required sections |

Model note (not a verdict): PASS, as fixed by the supplied code-decided verdict.

### `discoverable` — **PASS** (code+model)

Model (one question): PASS pass 3/3

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `discoverable.literals` Long literal expected values in the tests: each must be stated or derivable from the environment. | code: hardcoded_expected | fact | – | no long literal value lists in tests |
| `discoverable.requirements` tests/requirements.json binds every constraint sentence to a graded test (the requirements gate), as a fact. | code: requirements | fact | – | no requirements record |

### `oracle_investigates` — **PASS** (code+model)

Model (one question): PASS pass 3/3

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `oracle_investigates.derivation` What solve.sh asks of the system (reads, runs, probes) and what it applies ready-made (copied files, heredocs, literals). | code: solution_derivation | fact | – | commands that read or probe the system: none; prepared files or heredocs applied: none; other files under solution/: ['solution/solve.py'] |

