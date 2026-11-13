# Tango Bravo IV / Terminal Bench 4: Project Guide and Reference

Source: [TB4 Queue — Learning](https://queue.supertasker.ai/#learning), inspected October 22, 2026. The room calls the project **Tango Bravo IV / Terminal Bench 4**. This guide consolidates all 11 written onboarding slides, all 15 written quality-course slides, and answers to their 8 + 23 knowledge-check questions. It is a paraphrased study reference, not an official review or a verbatim export. Embedded video narration is not included.

**Workflow update:** The subsequently inspected Workflow page documents toolkit **v3.0.0**. It requires only **Python 3.12+ locally** and runs execution controls, quality checks, pass@3 and full review on the platform. Use the [current workflow guide](TB4-workflow-guide.md) for setup and submission commands. The local Docker/Harbor and local runtime-check instructions retained below describe the learning slides, not requirements of the v3.0.0 workflow.

## Contents

- [Purpose and numerical rules](#purpose-and-numerical-rules)
- [Environment, originality and structure](#environment-originality-and-structure)
- [Prompt contract](#prompt-contract)
- [The 35 named criteria](#the-35-named-criteria)
- [The five project checks](#the-five-project-checks)
- [The 13 common errors and concrete defenses](#the-13-common-errors-and-concrete-defenses)
- [Workflow and report statuses](#workflow-and-report-statuses)
- [Pre-upload checklist](#pre-upload-checklist)
- [Onboarding answers](#answers-onboarding-knowledge-checks-8)
- [Quality-course answers](#answers-quality-course-knowledge-checks-23)
- [Source map](#source-map)

## Purpose and numerical rules

Build hard, economically valuable command-line tasks for Astra-6. Tasks must be original, objectively verifiable, solvable, fair, and difficult because of their professional technical challenge.

- Reward is exactly **0 or 1** at every reachable reward write. All graded tests must pass for 1; a genuine failing or missing test or crash is 0. No fractional credit.
- Infrastructure/provider faults are voids to rerun. Failed artifact capture is an error with **no reward**, not a scored agent failure.
- Oracle = **1**; no-op/nop = **0** for a task-related reason; each targeted cheat = **0**. A cheat scoring 1 blocks the task until the verifier is hardened.
- pass@3: exactly **1 or 2 of 3** Astra-6 attempts solved. Three solved is too easy; zero solved requires investigating difficulty, fairness and failures.
- pass@8: **1 through 6 of 8** qualify. Zero, seven or eight solved sends the task back.
- If reviewers make no changes, five new attempts join the original three. Any reviewer change means eight fresh attempts.
- Any file edit invalidates earlier checks, including pass@3. Rerun lint, oracle and nop, package and upload the new revision. A qualifying new pass@3 produces a **new P3 ID**.
- Agent budget: **28800 seconds**. Expert time is a separate, honest best-case human estimate in hours, greater than zero, with no automatic eight-hour cap.

## Environment, originality and structure

The onboarding specifies Docker running, Harbor **0.23.0**, git, Python **3.12+**, the project `tb4` command, and a supertasker.ai login using the Slack email. Obtain the toolkit from Workflow. Run commands from one work folder: `tb4 new` creates `tasks/`; checks write to `jobs/`.

```sh
export TB4_ROLE=attempter
tb4 new repo-fix billing-tax-rounding --dir tasks
```

Use `repo-fix` for a repository bug fix or feature, and `output-task` for an answer written to `/app/output`. Slugs use lowercase letters, digits and hyphens, at most three words.

An existing repository is a baseline only: maintained within the last six months, MIT or Apache 2.0, and pinned to one commit. Alternatively, create a realistic scenario with a real build system and test suite. The task should span several files/components, include its own tests, and need no dependency changes. Never reuse a public issue, PR or commit as the problem; reintroducing a known upstream bug also fails originality. Search the web and repository history and record the search. An introduced defect must not be exposed in git log, diff, reflog or stash.

| File | Purpose |
|---|---|
| `instruction.md` | Goal, symptoms and acceptance criteria in plain prose; no approach hints. |
| `task.toml` | Author, description, keywords/tags, expert time; repo and base commit for repo-fix; valid schema. |
| `environment/Dockerfile` | Pinned agent environment. |
| `tests/` | Separate verifier image and outcome tests. |
| `solution/` | Investigating, computing reference solution that scores 1. |
| `cheat/<name>/solve.sh` | Targeted grader attack that must score 0. |
| `README.md` | Accurate difficulty, solution, verification and required template sections; evidence-backed claims. |

## Prompt contract

Include situation and absolute location; observable goal/symptoms; inputs and sources of truth; acceptance criteria with exact numbers, paths and schemas; constraints; available feedback commands; and the standard trailer. State the outcome, not the diagnosis or solution procedure. Plain prose, no headings, no roleplay/preamble, absolute paths in backticks. The canary and trailer are exempt from the concision rule.

Every test maps to a prompt sentence and every requirement sentence to a test. Give the exact normative schema for structured outputs, in the prompt or a referenced spec: fields, types and allowed values. Examples alone are insufficient. State every tolerance, unit, format and protected-file requirement. Mechanically enforce protected files.

The last line must be:

> You have 28800 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.

## The 35 named criteria

| # | Exact name | Meaning / passing evidence |
|---|---|---|
| 1 | `verifiable` | Objective programmatic grading; no verifier runtime installation. LLM judging is exceptional and needs validated justification. |
| 2 | `outcome_verified` | Grade the final result through the stated interface and accept alternative valid approaches; process limits only to mechanically prevent cheating. |
| 3 | `functional_verification` | Execute real behavior or parse real artifacts, not source keywords or self-reported success. |
| 4 | `verification_explanation_quality` | README explains each check and threshold against legitimate variation and alternative solutions, not only the oracle. |
| 5 | `binary_reward` | Every reachable reward write is exactly 0 or 1. |
| 6 | `solvable` | Legitimate working oracle; an expert knowing the approach can implement it in a few hours. Repeat runs to exclude flakes. |
| 7 | `solution_quality` | Oracle computes results. Expensive precomputed artifacts require generator, runtime, provenance and regeneration instructions. |
| 8 | `solution_explanation_quality` | Plain-language README explains the actual oracle and why it works; matches `solve.sh`. |
| 9 | `difficult` | Genuine expertise, not obscure facts, LLM tricks, volume or a low pass rate. State the key realization an unsuccessful agent would miss. |
| 10 | `essential_difficulty` | Failures come from the intended technical challenge, not incidental formatting, precision, tool artifacts or time pressure. |
| 11 | `difficulty_explanation_quality` | Explain the intrinsic challenge, real data origin and professional user to a nonspecialist; model scores are not the argument. |
| 12 | `expert_time_estimate` | Plausible positive best-case human hours; distinguish human effort, implementation with answer known, agent budget and run limits. |
| 13 | `anti_cheat_robustness` | Root adversary threat model in agent environment; no answer leakage via files, layers, history or mutable inputs; inspect targeted cheat results. |
| 14 | `task_security` | Inspect every asset for malicious execution, exfiltration, host access, injection, obfuscation and cross-task interference. No host mounts or download-to-shell patterns. |
| 15 | `verifier_execution_isolation` | Unprivileged submitted code; root protects/decides reward; import-time code isolated; child processes cleaned; fail closed on missing tools. |
| 16 | `do_not_modify_enforced` | Fully check or restore protected files using a pristine copy so tampering is blocked or detected. |
| 17 | `deterministic_reproducible` | Repeated clean runs agree; randomness and mutable inputs controlled; commits, images and pip versions pinned. The course excludes apt versions from this pinning requirement. |
| 18 | `separate_verifier_configured` | `environment_mode` is `separate`; verifier owns `/tests` via `tests/Dockerfile`, has inputs and preinstalled tools; duplicated assets agree or are justified. |
| 19 | `environment_hygiene` | Agent image contains no grading tests, oracle or grading dependencies. |
| 20 | `resource_configuration` | CPU, memory and timeouts reflect measurements with controlled headroom; agent budget/trailer is 28800 seconds. |
| 21 | `artifact_efficiency` | Only deliverables transferred, fixed inputs baked in, atomic capture, missing distinguished from empty; never grade partial patches. |
| 22 | `test_instruction_alignment` | Complete bidirectional traceability; no hidden requirements. |
| 23 | `instruction_concision` | Concise human prose, absolute paths, no procedure hints; canary/trailer exempt. |
| 24 | `structured_data_schema` | Exact normative schema in prompt/referenced spec; examples alone insufficient. |
| 25 | `typos` | Cross-check actual paths, names, commands and identifiers, not just spelling. |
| 26 | `reviewable` | Nonspecialist can follow reasoning, expected-value derivation, domain context and provenance. |
| 27 | `category_and_tags` | Valid taxonomy matching the primary skill, not incidental tooling. |
| 28 | `task_name` | Kebab-case, at most three words. |
| 29 | `task_readme` | All four required template sections, accurate and synchronized with the implementation. The written slides do not enumerate all four headings. |
| 30 | `task_toml_schema` | Valid template/schema and values; validate with linter. |
| 31 | `no_extraneous_files` | Needed task files/license and cheat controls only; exclude caches, drafts, notes and run history from task directory. Keep ancillary provenance/run history outside it. |
| 32 | `ctrf_reporting` | CTRF at `/logs/verifier/ctrf.json`; pytest `--ctrf`; assert a collected-test floor. |
| 33 | `interesting` | Credible professional work with real economic value, including niche fields; explain who would pay and why. |
| 34 | `novel` | No memorized/public answer or duplicate task; search beyond repository as well as its history. |
| 35 | `agentic` | Requires observation, exploration, tools, debugging and adaptation, not one-shot generation or one command. |

## The five project checks

These supplement the 35 base criteria, giving **40 checks in total**.

| Project check | Requirement |
|---|---|
| English-only content | Write the instruction and every explanation in English. |
| No host paths | No paths from the author's machine or user folder anywhere in the task or its evidence. Container paths such as `/app/output` serve a different purpose and should be stated where required. |
| Harbor format | Required task layout with valid `task.toml`, environment, solution and verifier. |
| Discoverability | Required inputs, interfaces and tools are stated or discoverable in the environment; no hidden names or requirements. |
| Investigating oracle | Reference solution investigates and computes; retain derivations and generators instead of hardcoding the answer. |

## The 13 common errors and concrete defenses

1. **Readable answers.** Root owns `/tests` at 0700; expected files may be 0600. Submitted code runs as its own user and emits observations (e.g. `tests/emit.py`). A separate judge compares afterward and never imports submitted code. Assert that the unprivileged account cannot read expected values; test with an answer-hunting cheat.
2. **Submission changes its grader.** Restore all graded tests/config from `/pristine` after applying submission; reports are root-owned; kill submitted processes between phases; fill each cheat's `TARGET`; select exact graded test names.
3. **Exit code or printed word decides pass.** Parse CTRF, JUnit or `go test -json`. Require a minimum test count, zero failures and expected identities. Counts alone can be forged; per-case digests and a fixed list strengthen validation.
4. **Missing submission still graded.** Use v2 atomic capture into one checksummed patch/tar in `/app/submission`, where verifier image has no fallback code. Missing/mismatched capture is an infrastructure error with no reward. Write temporary file and move only after success.
5. **Swallowed errors or truncated output.** Failed copies, reads and caps stop grading. No `|| true` in grading steps, no missing-to-empty substitution, no grading just the first part of output. A genuine hanging submission can fail under a declared watchdog; distinguish this from infrastructure capture failure.
6. **Untested promise.** Map every requirement in `tests/requirements.json`; declare output files in `tests/grading.json` for wrong-answer controls. E.g. a promised per-line unit needs an actual check.
7. **Unstated test requirement.** State every tolerance/unit/format. If several attempts fail just one check, suspect the check first. Example mismatch: 0.02 nm tested versus 0.2 nm promised.
8. **Arbitrary oracle choice.** Make the contract unambiguous, including edge cases. Independent implementation from the interface alone should pass; reviewers arrange independent solution/contract review after DAS submission.
9. **Inconsistent time limits.** Put every step/cap in `tests/budget.json`; sequential caps plus margin fit outer timeout, and promised times equal test values. Valid nesting example: 10-second calls, 3000-second internal deadline, 3300-second watchdog, 3600-second verifier. Invalid: 4800 sequential seconds inside 3600.
10. **README/code mismatch.** Named files, steps and numbers exist; measured claims cite shipped evidence; ship the expected-value generator in `tests/`.
11. **Wrong upload.** One `<slug>.zip` containing one complete task directory, including cheats; claimed DAS task link supplied to Supertasker. No old tasks/versions, run folders, secrets or junk. Submit P3 ID to DAS, never a delivery ZIP.
12. **Wrong difficulty.** pass@3 only 1–2/3 and pass@8 only 1–6/8. Inspect timing checks, margins and oracle when all attempts fail the same timing condition; do not manufacture difficulty through defects.
13. **Author self-review presented as official review.** Authors improve tasks using criteria; only independent reviewers create official review records or accept/waive findings.

## Workflow and report statuses

1. Claim task in DAS; keep its link. Claim next task only after submitting current one in DAS.
2. Build locally; lint and validate current revision (oracle 1, nop 0, targeted cheats in place).
3. Upload one source ZIP through Submit. First task also needs DAS Task ID; afterward platform assigns task IDs such as T-0142.
4. Fix the task's **To do** items and send revisions via **Upload the fix** on that task.
5. Platform runs lint/controls and a lightweight assessment of all 40 checks, then starts pass@3 automatically.
6. In-range pass@3 generates P3 ID under **Updates**. Paste that new ID into the same DAS task and submit; platform links the records.
7. Review team performs controls, independent review, originality and all 40 checks, then pass@8. Cleared 1–6/8 goes to pre-delivery packaging. Major defects/out-of-range results return with feedback; minor fixes handled by team; holds await decision.

| Status | Meaning and action |
|---|---|
| PASS | Passed this check on this revision; not final task acceptance. |
| FAIL | Fix requirement failure and repeat local validation. |
| ERROR | Check did not complete; follow service status; not a scored failure and cannot be waived. |
| BLOCKED | Prerequisite or duplicate-upload rule stopped it; read reason, do not work around it. |
| MISSING | Required evidence absent for this revision; complete its producing stage. |
| FAIL-PENDING-DISPOSITION | A reviewer must decide; trainer cannot accept/waive. |

## Pre-upload checklist

Use this checklist on the exact revision being packaged. It consolidates the onboarding and quality-course requirements.

- [ ] State the core professional difficulty in one sentence and explain it in the README.
- [ ] Identify the professional user, economic value and realistic origin of the data.
- [ ] Confirm originality with web and repository-history searches; retain the search record outside the task directory.
- [ ] Use an eligible pinned repository baseline or a realistic newly built scenario.
- [ ] Map every requirement to a test and every test to a stated requirement.
- [ ] State exact output schemas, paths, units, tolerances and comparison rules.
- [ ] Enforce every protected-file constraint with checks or a pristine copy.
- [ ] Include the exact 28800-second trailer as the instruction's last line.
- [ ] Keep grading tests, expected answers, oracle and grading dependencies out of the agent image.
- [ ] Configure a separate verifier with preinstalled tools and protected expected answers, tests and reports.
- [ ] Run submitted code unprivileged, isolate import-time execution and clean up its child processes.
- [ ] Capture only required deliverables atomically; treat failed or mismatched capture as an error without reward.
- [ ] Parse structured test reports; check expected identities, minimum count and zero failures.
- [ ] Ensure every reachable reward write is exactly 0 or 1.
- [ ] Pin required dependencies and control randomness; repeat clean runs to check reproducibility.
- [ ] Measure resource needs; ensure sequential limits plus margin fit the verifier budget and match promised times.
- [ ] Run lint, oracle and nop on this revision: oracle 1, nop 0 for the correct reason.
- [ ] Include targeted cheat controls and verify each scores 0; fix any successful cheat.
- [ ] Supply a positive, honest best-case expert estimate in hours.
- [ ] Keep README explanations synchronized with the code, shipped evidence and expected-value generator.
- [ ] Validate `task.toml`, category/tags, slug, required README sections and CTRF output path.
- [ ] Package one complete task directory, with cheat controls and required license, as `<slug>.zip`.
- [ ] Exclude run folders, other tasks, old versions, caches, drafts, secrets and unrelated files.
- [ ] Upload through Supertasker with the claimed DAS task link; use **Upload the fix** for revisions.
- [ ] After qualifying pass@3, submit the new P3 ID in the same DAS task; claim the next task afterward.

Any edit makes earlier validation stale. Revalidate the changed revision before upload, and obtain a new qualifying pass@3/P3 ID when resubmitting it.

## Answers: onboarding knowledge checks (8)

| Slide | Question cue | Answer |
|---|---|---|
| 2 | One of twenty graded tests fails | **0**. |
| 2 | Required pass@3 solved count | **1 or 2 of 3**. |
| 4 | Where verifier runs | **In its own container**. |
| 5 | Use merged public PR's fix as task? | **No: it is a public-answer lookup**. |
| 6 | Test checks unmentioned field | **Send-back: testing the unstated**. |
| 8 | Which cases send task back? | **0/3**, **8/8**, and **reviewer's send-back**; not 2/3. |
| 9 | What to paste into DAS | **P3 ID** for this revision. |
| 11 | Which defects send task back? | **Verifier in agent container**, **unpinned pip package**, **fractional 0.6667 reward**. A symptom-only prompt is appropriate. |

## Answers: quality-course knowledge checks (23)

| Slide | Question cue | Answer |
|---|---|---|
| 1 | Quick check passed | **Full independent review of all 40 checks still follows DAS submission**. |
| 1 | FAIL-PENDING-DISPOSITION | **Wait; reviewer decides**. |
| 2 | Fractional reward formula, oracle reaches 1 | **Fails binary_reward; every reachable write must be 0 or 1**. |
| 2 | Functional verification | **Run fixed service and check responses**. |
| 3 | Proper difficulty argument | **Interaction between cache and scheduler means fixing one alone hides symptoms/breaks the other**. |
| 3 | expert_time_estimate | **Honest positive best-case skilled-human hours**. |
| 4 | Unenforced `/app/spec.md` protection | **do_not_modify_enforced fails**. |
| 4 | Where answers must never be reachable | **Agent-readable files, image layers, repository history**; root-only verifier folder is appropriate. |
| 5 | Grading pytest/tests copied into agent image | **environment_hygiene fails**. |
| 5 | Proper pip pin | **requests==2.32.3**. |
| 6 | Unmentioned `settled_at` tested | **test_instruction_alignment fails**. |
| 6 | JSON schema requirement | **Every field, type and allowed value in prompt/referenced spec**. |
| 7 | Valid slug | **billing-tax-rounding**. |
| 7 | Finance task using some ML | **Operations, Finance**; primary skill controls. |
| 8 | Exact fix in closed upstream PR | **Pick another problem and note searches**. |
| 9 | README cites `/Users/ana/work/data.csv` | **No host paths** fails. |
| 10 | Changed one test after oracle run | **Rerun lint, oracle and nop on new version**. |
| 11 | Regression-suite pass decision | **Parsed report: minimum count, zero failures and expected test names**. |
| 11 | Permitted expected-answer location | **Root-owned `/tests` at 0700 in verifier**. |
| 12 | Output copy fails | **Stop with error and write no reward**. |
| 13 | Three attempts fail only same check | **Suspect check's unstated tolerance/rule first**. |
| 14 | Prompt 20 minutes, test 1500 seconds | **Numbers must be equal**; 20 minutes is 1200 seconds. |
| 14 | Supertasker ZIP contents | **One complete task directory including cheat controls**. |

## Source map

All slide references below are within [TB4 Queue — Learning](https://queue.supertasker.ai/#learning) and may require the project login.

| Course | Slides | Material used in this guide |
|---|---|---|
| Tango Bravo IV: onboarding | 1–2 | Project purpose, target model, binary grading, control results and pass ranges. |
| Tango Bravo IV: onboarding | 3–4 | Environment setup, task types, folder contents and separate verifier. |
| Tango Bravo IV: onboarding | 5–7 | Originality, prompt contract, standard trailer and intended technical difficulty. |
| Tango Bravo IV: onboarding | 8–10 | Platform checks, pass@3, P3 ID, DAS submission, independent review and pass@8. |
| Tango Bravo IV: onboarding | 11 | Common causes of send-back. |
| Tango Bravo IV: quality criteria and common errors | 1 | How quick/full reviews use the 40 checks; report statuses. |
| Tango Bravo IV: quality criteria and common errors | 2 | Criteria 1–8: verification and oracle. |
| Tango Bravo IV: quality criteria and common errors | 3 | Criteria 9–12: difficulty and expert time. |
| Tango Bravo IV: quality criteria and common errors | 4 | Criteria 13–16: security, isolation and protected files. |
| Tango Bravo IV: quality criteria and common errors | 5 | Criteria 17–21: reproducibility, environments, resources and artifact capture. |
| Tango Bravo IV: quality criteria and common errors | 6 | Criteria 22–25: instruction/test alignment, concision, schemas and identifiers. |
| Tango Bravo IV: quality criteria and common errors | 7 | Criteria 26–32: reviewability, metadata, package and reporting. |
| Tango Bravo IV: quality criteria and common errors | 8 | Criteria 33–35: realism, originality and agentic work. |
| Tango Bravo IV: quality criteria and common errors | 9–10 | Strictly reviewed criteria, five project checks and pre-upload checklist. |
| Tango Bravo IV: quality criteria and common errors | 11 | Errors 1–3: readable answers, grader tampering and superficial pass detection. |
| Tango Bravo IV: quality criteria and common errors | 12 | Errors 4–5: missing capture, swallowed errors and truncated outputs. |
| Tango Bravo IV: quality criteria and common errors | 13 | Errors 6–8: untested promises, unstated requirements and arbitrary oracle choices. |
| Tango Bravo IV: quality criteria and common errors | 14 | Errors 9–13: budgets, README accuracy, upload, difficulty and official review. |
| Tango Bravo IV: quality criteria and common errors | 15 | Error-to-prevention quick reference. |

## Boundaries of this reference

This records the room as inspected, not future changes. Reinspect the TB4 tab if a later question depends on updated guidance. Embedded videos and linked external documentation may contain additional details; their full contents have not been verified. The inspected overview video had captions disabled. The guide does not invent missing template details such as the four README section headings or additional CLI commands. No knowledge-check answers were entered or submitted in the browser while compiling this reference.
