# TB4 learning update — October 28, 2026

Sources: [Learning room](https://queue.supertasker.ai/#learning) and [Workflow page](https://queue.supertasker.ai/#workflow), read directly in Chrome. This is a paraphrased study reference, not an official project policy document.

## Completion

All 62 written slides were reviewed. Previously saved correct answers were reviewed, and outstanding knowledge checks were answered. Each course reached 100%; all four Completed badges remained after reloading the platform.

| Campaign | Slides | Correct answers | Status |
|---|---:|---:|---|
| Onboarding | 11 | 8/8 | Completed |
| Task design in depth | 15 | 17/17 | Completed |
| Quality criteria and common errors | 15 | 23/23 | Completed |
| Workflow and submission | 21 | 42/42 | Completed |
| **Total** | **62** | **90/90** | **All completed** |

The review covered written lessons, examples, criteria, common errors and quiz feedback. Linked video narration and external documentation were not reviewed in full during this update.

## Source discrepancy

The live sources disagree. Do not merge them into one apparently consistent procedure.

| Topic | Learning courses, including October 15 workflow changelog | Workflow page, toolkit v3.3.0 dated October 25 |
|---|---|---|
| Local setup | Docker, Harbor 0.23.0, git, Python 3.12+, project tb4 command. | Python 3.12+ only; no local Docker, model or API key. |
| Before upload | Lint, local oracle = 1 and nop = 0; repeat after every edit. | Lint and package locally; execution controls and reviews run on the platform. |
| DAS association | Claim an Attempt and supply its DAS link before uploading. | First task needs a DAS Task ID; subsequent new tasks get platform IDs without a DAS ID at upload. |
| Revisions | Original DAS task, fresh qualifying P3 ID. | Upload the fix on the existing platform task; new P3 ID in the same DAS task. |

Quiz answers follow the displayed learning material. The [workflow guide](TB4-workflow-guide.md) records the newer platform page. Neither page explicitly reconciles the differences. Obtain a project-owner ruling if authoring work depends on the disputed local prerequisites or initial DAS process.

## Shared numerical rules

- Reward is exactly 0 or 1. Every graded test must pass for 1; no partial credit.
- Oracle = 1; nop = 0 because task tests fail, not because setup fails; each exercised cheat = 0.
- pass@3 qualifies only at 1/3 or 2/3. At 0/3, investigate solvability, fairness and complexity. At 3/3, increase genuine difficulty. Change the task and repeat validation; do not rerun unchanged files for a preferred score.
- pass@8 qualifies at 1–6/8. Results 0/8, 7/8 and 8/8 are returned.
- No QM changes: five new trials join the original three. Any QM change: eight fresh trials.
- A successful cheat blocks delivery regardless of the model pass rate.
- Harness/provider faults are voids, not scored failures. Inspect agent logs when results resemble nop. Missing/mismatched capture is an error with no reward. The workflow course also says agent timeout is not a scored failure.
- The learning workflow specifies five submissions per trainer per day and a six-hour authoring budget per task, concentrated on choosing the problem and writing the prompt.
- Agent budget: 28800 seconds. Expert time is a separate, positive, honest best-case human-hours estimate with no automatic eight-hour cap.

## Task design in depth

The seven prompt elements are situation/location; observable goal or symptoms; inputs and source-of-truth precedence; acceptance criteria; constraints; available feedback; and the standard trailer. Situation/location and trailer are always present, with goal and/or acceptance criteria. Use concise plain prose and absolute paths in backticks. Avoid headings, Markdown lists, em dashes, roleplay, diagnostic hints and step-by-step solutions.

Write tests first, then state their contract. Map every requirement sentence to tests and every test back to the stated contract. Define exact structured-output fields, types, allowed values, units, tolerances and completeness. Examples do not replace a normative schema. Mechanically protect files the instruction says must not change.

The final line is:

> You have 28800 seconds to complete this task. Do not cheat by using online solutions or hints specific to this task.

The annotated examples cover session-window symptoms and a protected design specification; live database cutover with observable error/staleness/latency requirements and fresh-deployment checks; and MVCC/LSM behavior where retaining all versions indefinitely is not an acceptable workaround.

Explain the central professional challenge in one sentence in the README. Interacting components, plausible wrong fixes, evidence interpretation and persistent correctness can create valid difficulty. Random thresholds, hidden helper names, incidental precision, volume, time pressure and broken setup cannot. Read failed attempts before revising.

### Originality and classification

An existing repository needs a recent eligible baseline, MIT or Apache 2.0 licensing at the pinned commit, and realistic software. From-scratch tasks still need a realistic build system, test suite and code structure. Use several relevant components, your own tests, and no dependency changes required to solve the task.

Do not use public issue/PR/commit fixes or reintroduce known upstream bugs. Search the web and repository history; retain a novelty note with queries and findings outside the submitted task directory. An introduced defect must not be exposed by log, diff, reflog or stash.

Task types: bug fix, new feature, performance, migration/port, reimplementation and security. Classify by the primary skill, not incidental tools. Subcategory must be nonempty.

| Category | Subcategories shown in the course |
|---|---|
| Science | Biology, Chemistry, Physics, Earth, Robotics, Math, Linguistics |
| Software | Algorithms, Systems, Databases, Data engineering, Frontend, Languages |
| ML | Training, Inference, Evaluation, Kernels |
| Operations | Finance, Logistics, Supply chain, Claims, Compliance, Marketing |
| Security | Cryptography, Reverse engineering, Forensics, AppSec |
| Hardware | CAD, RTL |
| Media | Music, Design |

### Runtime and task files

The learning reference is Harbor 0.23.0 with Terminus-2. Agent timeout is 28800 seconds; typical verifier timeout is 600 seconds, sized for the full suite. Build timeout is typically 600–1800 seconds. CPU choices: 1, 2, 4, 8, 16. Memory: 1024–32768 MB in powers of two. At most one H100. Omit allow_internet entirely; the lessons say CI rejects both true and false.

Pin commits, image tags and pip packages using ==; avoid mutable branches and latest. The course excludes apt versions from this pinning rule. Preinstall verifier dependencies in its image.

| File | Responsibility |
|---|---|
| environment/Dockerfile and tests/Dockerfile | Separate images; same pinned BASE_COMMIT. |
| tests/emit.py | Execute submission and emit observations, without expected answers. |
| tests/test_outputs.py and tests/expected.json | Protected judge and expected results. |
| tests/requirements.json | Instruction-to-test mapping. |
| tests/budget.json | Steps/caps; sequential caps plus margin fit outer timeout. |
| tests/grading.json | Repo, base commit, tests, regression suite and output files. |
| solution/ | Legitimate solution that investigates and computes. |
| cheat/ | Negative controls with a real, exercised TARGET. |
| README.md | Difficulty, solution and verification tied to shipped evidence. |

Preserve shared test.sh and collection hooks except template-requested values. For repo-fix, forge-reward targets a module imported by graded tests. For executable outputs, keep forge-reward targeting the deliverable program. For data-only outputs, keep symlink-answers targeting a file read by the judge. Remove the inapplicable control. A cheat that never executes proves nothing even when it scores zero.

## Quality and common errors

The [project reference](TB4-study-reference.md) retains all 35 named criteria, five project checks and 13 common errors, re-reviewed this session. Practical requirements include:

1. Grade actual behavior and complete artifacts through structured reports, expected test names, a minimum count and zero failures.
2. Keep expected answers inaccessible to submitted code. Isolate unprivileged execution from the protected judge and reward writer. Restore pristine tests/configuration and stop child processes.
3. Capture deliverables atomically with integrity checks. Missing capture, failed copying and truncated evidence must not silently become graded empty/partial results.
4. Enforce the entire stated contract without hidden requirements. Suspect an unstated rule when multiple attempts fail only one check.
5. Synchronize README, schemas, budgets, paths and implementation. Ship generators for expected values.
6. Preserve novelty, economic value and a professional explanation of difficulty. A low pass rate alone is insufficient.
7. Authors cannot create official independent-review records or waive findings.

## Workflow and review knowledge

The learning sequence is: claim/resume DAS Attempt; choose an original problem; choose type/category/subcategory; write aligned tests and prompt; build pinned environments and validate; upload ZIP with DAS link; inspect pass@3; submit the fresh P3 ID in the same DAS task before claiming another.

The ZIP contains one complete source task, including tests, solution and cheat controls. Keep local jobs, provenance notes, old runs, unrelated tasks, caches and secrets outside it. Authors do not assemble evidence/, MANIFEST.json, DELIVERY.md or prebuilt delivery images.

A ZIP hash detects duplicates; a revision digest identifies tested files; a P3 ID identifies a qualifying run. These differ from the DAS link. Identical ZIPs are blocked while queued/running and after completion, including quality FAIL. The learning course permits retry only if earlier lightweight execution failed to run.

Review covers controls, independent review, originality and all 40 criteria. Cleared in-range pass@8 permits Pre-delivery; QMs package and first upload the ZIP to DAS there. Delivery is later. Returned work keeps its original DAS task and requires fixes, renewed validation and a fresh P3 ID; a new Attempt cannot bypass a return.

PASS applies to a check on one revision. FAIL requires correction. ERROR means execution did not complete validly. BLOCKED identifies a prerequisite or duplicate rule. MISSING means evidence is absent. FAIL-PENDING-DISPOSITION/hold awaits a QM decision.

## Updated toolkit download

Workflow lists v3.3.0, dated 2026-10-25, approximately 299 KB. Download completed to:

C:\Users\Administrator\Downloads\tb4-starter-pack-v3.3.0-2026-10-25.zip

Verified length: 305781 bytes. SHA-256:

```text
2eb82e067e9059f7deb1bbaccf04a0ad9e54ccca596eaf48fc38e50351ae34d5
```

The hash prefix matches the link's displayed prefix. The toolkit was not installed or executed. See the updated workflow guide for the displayed setup commands.
