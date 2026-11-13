# gamma-decay-scheme: 5 criteria

3 pass, 1 fail (0 disputed), 0 not applicable, 0 inconclusive. Reviewer: astra (openai/gpt-6.1-sol), role independent, operator review platform quick check, 3 draw(s), 2026-11-06T02:52:29Z.
Rubric: `/home/ubuntu/tb4-toolkit-1.26/tbench-assess/src/tbench_assess/rubrics/audit-extra.toml`

| Section | Pass | Fail | Pending | N/A |
|---|---|---|---|---|
| Audit | 3 | 0 | 0 | 0 |
| Feasibility | 0 | 1 | 1 | 0 |

## Audit

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 1 | `english_only` | **PASS** | code+model | The instruction, README, station notes, code comments, docstrings and human-readable messages are in English. |
| 2 | `no_host_paths` | **PASS** | code | all 1 checks pass or do not apply (1 decided by code, 0 by the model) |
| 3 | `harbor_format` | **PASS** | code | all 19 checks pass or do not apply (19 decided by code, 0 by the model) |

## Feasibility

| # | Criterion | Outcome | Method | Why |
|---|---|---|---|---|
| 4 | `discoverable` | **FAIL** | code+model (model) | The output path, members, numeric types, ground state, intensity threshold, ordering freedom and tolerances are stated in instruction.md, while the station notes and calibration/production measurements provide routes to the physical quantities. However, README.md and tests/checks.txt explicitly identify an additional 17-level reconstruction satisfying the reduction's constraints, whereas the instruction requests every level without specifying a minimum-level interpretation. tests/test_outputs.py::test_levels requires exactly the expected 16 levels, and matched() requires only the corresponding transition placements. Selecting those as the complete physical scheme therefore depends on an unstated model-selection assumption, not an observable distinction supplied to the solver. [fail 2/3, pass 1/3] Evidence: instruction.md: "the excitation energy in keV of every level of the daughter that the parent's β decay populates"; README.md: "with 17 it finds one more, which adds a level at 2917.5 keV and a second unseen transition that no peak calls for" and "the instruction's \"every level\" means the 16"; tests/checks.txt: "17 levels, 2 unseen transitions, extra level at 2917.5 keV"; tests/test_outputs.py: "assert len(have) == len(want), \"%d levels listed, the scheme has %d\" % (len(have), len(want))". |
| 5 | `oracle_investigates` | **FAIL-PENDING-DISPOSITION** | code+model (model) | solution/solve.sh invokes a genuine measurement-based reduction, but solution/solve.py:main() stops at the first level-count bound admitting a solution and selects its final answer only from that bound. It explicitly finds wider schemes afterward, and README.md identifies the minimum-level convention as the reason to reject the additional 17-level candidate. That convention is neither specified by the instruction's request for every populated level nor established by a distinguishing measurement, so the oracle applies an unsupported selection decision that determines the graded count and placements. [a single draw found this defect with evidence against a pass majority and no second draw confirmed it: needs a disposition but does not block on its own (governance-disposable). pass 2/3, fail 1/3] Evidence: solution/solve.py: "for max_levels in range(2, 24):\n        solutions = search(lines, flags, ceiling, order, max_levels)\n        DIAG.setdefault(\"search_counts\", []).append((max_levels, len(solutions)))\n        if solutions:\n            break" and "sol = min(solutions, key=disagreement)"; tests/checks.txt: "schemes with at most 16 levels, ground state included: 1" and "schemes with at most 17 levels, ground state included: 2"; README.md: "An analyst does not add a
level the data do not need, so the instruction's \"every level\" means the 16." |

## Split verdicts: every draw

### `discoverable`: FAIL (fail 2/3, pass 1/3)

1. **FAIL**: The output path, members, numeric types, ground state, intensity threshold, ordering freedom and tolerances are stated in instruction.md, while the station notes and calibration/production measurements provide routes to the physical quantities. However, README.md and tests/checks.txt explicitly identify an additional 17-level reconstruction satisfying the reduction's constraints, whereas the instruction requests every level without specifying a minimum-level interpretation. tests/test_outputs.py::test_levels requires exactly the expected 16 levels, and matched() requires only the corresponding transition placements. Selecting those as the complete physical scheme therefore depends on an unstated model-selection assumption, not an observable distinction supplied to the solver. Evidence: `instruction.md: "the excitation energy in keV of every level of the daughter that the parent's β decay populates"; README.md: "with 17 it finds one more, which adds a level at 2917.5 keV and a second unseen transition that no peak calls for" and "the instruction's \"every level\" means the 16"; tests/checks.txt: "17 levels, 2 unseen transitions, extra level at 2917.5 keV"; tests/test_outputs.py: "assert len(have) == len(want), \"%d levels listed, the scheme has %d\" % (len(have), len(want))".`
2. **PASS**: The output path, exact JSON members, numeric types, intensity floor, ordering freedom and tolerances are stated in instruction.md; the parent half-life, level list, transition placements, gamma energies, corrected relative intensities and isomer properties are recoverable through calibration, cycle-time fitting and coincidence analysis of the environment files documented in NOTES.md, with source energies supplied in source_lines.txt and natural-background line energies obtainable from public radionuclide gamma-emission tables.
3. **FAIL**: The output path, exact schemas, numerical types, units, intensity floor and tolerances are stated in instruction.md; NOTES.md and source_lines.txt describe the calibration, singles and coincidence measurements supporting energy, intensity and half-life estimation, while standard room-line energies are publicly tabulated. However, tests/test_outputs.py:test_levels requires exactly 16 levels, and matched() requires the specific transition endpoints in expected.json, although README.md and checks.txt acknowledge an additional 17-level candidate satisfying the reference placement constraints. Neither instruction.md nor NOTES.md requires the smallest scheme or the fewest unseen transitions, and the threshold explicitly permits unseen exits. Selecting the tested count and placements therefore depends on an unstated minimum-level model-selection assumption rather than a fact established by the supplied measurements. Evidence: `instruction.md: "`levels_keV` is an array with the excitation energy in keV of every level of the daughter that the parent's β decay populates, with the ground state as 0."; tests/test_outputs.py: "assert len(have) == len(want)"; tests/checks.txt: "schemes with at most 17 levels, ground state included: 2" and "17 levels, 2 unseen transitions, extra level at 2917.5 keV"; README.md: "An analyst does not add a level the data do not need, so the instruction's \"every level\" means the 16."; environment/data/NOTES.md: "nothing under it is recorded."`

### `oracle_investigates`: FAIL-PENDING-DISPOSITION (pass 2/3, fail 1/3)

1. **PASS**: The reference reads the calibration, background, singles and coincidence files, fits the measured quantities and computes a minimum-level reconstruction rather than copying TARGET, expected.json or task-specific ground-truth values.
2. **PASS**: The reference reads the run files, fits calibration and activity profiles, classifies and splits peaks using measured coincidences, searches and refines level schemes, and estimates the isomer lifetime from delayed counts rather than importing the invented scheme or expected answers.
3. **FAIL**: solution/solve.sh invokes a genuine measurement-based reduction, but solution/solve.py:main() stops at the first level-count bound admitting a solution and selects its final answer only from that bound. It explicitly finds wider schemes afterward, and README.md identifies the minimum-level convention as the reason to reject the additional 17-level candidate. That convention is neither specified by the instruction's request for every populated level nor established by a distinguishing measurement, so the oracle applies an unsupported selection decision that determines the graded count and placements. Evidence: `solution/solve.py: "for max_levels in range(2, 24):\n solutions = search(lines, flags, ceiling, order, max_levels)\n DIAG.setdefault(\"search_counts\", []).append((max_levels, len(solutions)))\n if solutions:\n break" and "sol = min(solutions, key=disagreement)"; tests/checks.txt: "schemes with at most 16 levels, ground state included: 1" and "schemes with at most 17 levels, ground state included: 2"; README.md: "An analyst does not add a level the data do not need, so the instruction's \"every level\" means the 16."`

## Structured review

Methods: 2 by code, 3 by one model question with code checks, 0 by one model question. A code check fails a criterion only on present, current evidence; a check without its record is not provided (the model's verdict stands). A code verdict is never the model's.

### `english_only` — **PASS** (code+model)

Model (one question): PASS pass 3/3

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `english.prefilter` No prose unit (instruction, README, comments; test data aside) is clearly in another language. | code: language pre-filter | PASS | – | 17 prose unit(s): none clearly in another language (the model judges mixed or subtle cases) |

### `no_host_paths` — **PASS** (code)

Source: starter-pack checks/task_ship.py hostpaths (the task) and hygiene.host_path_hits (a delivery's evidence/ and provenance/)

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `hostpaths` no path of the author's machine in the task (or in a delivery's evidence and provenance) | code: host-path scan | PASS | – | no host path found |

Model note (not a verdict): Code-decided PASS.

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

Model note (not a verdict): Code-decided PASS.

### `discoverable` — **FAIL** (code+model) — decisive: `model`

Model (one question): FAIL fail 2/3, pass 1/3

- Draw 1 of 3: FAIL: The output path, members, numeric types, ground state, intensity threshold, ordering freedom and tolerances are stated in instruction.md, while the station notes and calibration/production measurements provide routes to the physical quantities. However, README.md and tests/checks.txt explicitly identify an additional 17-level reconstruction satisfying the reduction's constraints, whereas the instruction requests every level without specifying a minimum-level interpretation. tests/test_outputs.py::test_levels requires exactly the expected 16 levels, and matched() requires only the corresponding transition placements. Selecting those as the complete physical scheme therefore depends on an unstated model-selection assumption, not an observable distinction supplied to the solver. (evidence: instruction.md: "the excitation energy in keV of every level of the daughter that the parent's β decay populates"; README.md: "with 17 it finds one more, which adds a level at 2917.5 keV and a second unseen transition that no peak calls for" and "the instruction's \"every level\" means the 16"; tests/checks.txt: "17 levels, 2 unseen transitions, extra level at 2917.5 keV"; tests/test_outputs.py: "assert len(have) == len(want), \"%d levels listed, the scheme has %d\" % (len(have), len(want))".)
- Draw 2 of 3: PASS: The output path, exact JSON members, numeric types, intensity floor, ordering freedom and tolerances are stated in instruction.md; the parent half-life, level list, transition placements, gamma energies, corrected relative intensities and isomer properties are recoverable through calibration, cycle-time fitting and coincidence analysis of the environment files documented in NOTES.md, with source energies supplied in source_lines.txt and natural-background line energies obtainable from public radionuclide gamma-emission tables.
- Draw 3 of 3: FAIL: The output path, exact schemas, numerical types, units, intensity floor and tolerances are stated in instruction.md; NOTES.md and source_lines.txt describe the calibration, singles and coincidence measurements supporting energy, intensity and half-life estimation, while standard room-line energies are publicly tabulated. However, tests/test_outputs.py:test_levels requires exactly 16 levels, and matched() requires the specific transition endpoints in expected.json, although README.md and checks.txt acknowledge an additional 17-level candidate satisfying the reference placement constraints. Neither instruction.md nor NOTES.md requires the smallest scheme or the fewest unseen transitions, and the threshold explicitly permits unseen exits. Selecting the tested count and placements therefore depends on an unstated minimum-level model-selection assumption rather than a fact established by the supplied measurements. (evidence: instruction.md: "`levels_keV` is an array with the excitation energy in keV of every level of the daughter that the parent's β decay populates, with the ground state as 0."; tests/test_outputs.py: "assert len(have) == len(want)"; tests/checks.txt: "schemes with at most 17 levels, ground state included: 2" and "17 levels, 2 unseen transitions, extra level at 2917.5 keV"; README.md: "An analyst does not add a level the data do not need, so the instruction's \"every level\" means the 16."; environment/data/NOTES.md: "nothing under it is recorded.")

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `discoverable.literals` Long literal expected values in the tests: each must be stated or derivable from the environment. | code: hardcoded_expected | fact | – | no long literal value lists in tests |
| `discoverable.requirements` tests/requirements.json binds every constraint sentence to a graded test (the requirements gate), as a fact. | code: requirements | fact | – | no requirements record |

### `oracle_investigates` — **FAIL-PENDING-DISPOSITION** (code+model) — decisive: `model`

Model (one question): FAIL-PENDING-DISPOSITION pass 2/3, fail 1/3

- Draw 1 of 3: PASS: The reference reads the calibration, background, singles and coincidence files, fits the measured quantities and computes a minimum-level reconstruction rather than copying TARGET, expected.json or task-specific ground-truth values.
- Draw 2 of 3: PASS: The reference reads the run files, fits calibration and activity profiles, classifies and splits peaks using measured coincidences, searches and refines level schemes, and estimates the isomer lifetime from delayed counts rather than importing the invented scheme or expected answers.
- Draw 3 of 3: FAIL: solution/solve.sh invokes a genuine measurement-based reduction, but solution/solve.py:main() stops at the first level-count bound admitting a solution and selects its final answer only from that bound. It explicitly finds wider schemes afterward, and README.md identifies the minimum-level convention as the reason to reject the additional 17-level candidate. That convention is neither specified by the instruction's request for every populated level nor established by a distinguishing measurement, so the oracle applies an unsupported selection decision that determines the graded count and placements. (evidence: solution/solve.py: "for max_levels in range(2, 24):\n solutions = search(lines, flags, ceiling, order, max_levels)\n DIAG.setdefault(\"search_counts\", []).append((max_levels, len(solutions)))\n if solutions:\n break" and "sol = min(solutions, key=disagreement)"; tests/checks.txt: "schemes with at most 16 levels, ground state included: 1" and "schemes with at most 17 levels, ground state included: 2"; README.md: "An analyst does not add a level the data do not need, so the instruction's \"every level\" means the 16.")

| Check | Source | Verdict | Citation | Detail |
|---|---|---|---|---|
| `oracle_investigates.derivation` What solve.sh asks of the system (reads, runs, probes) and what it applies ready-made (copied files, heredocs, literals). | code: solution_derivation | fact | – | commands that read or probe the system: none; prepared files or heredocs applied: none; other files under solution/: ['solution/solve.py'] |

