# Tango Bravo IV / Terminal Bench 4: Detailed Workflow Guide

Source: [TB4 Queue — Workflow](https://queue.supertasker.ai/#workflow), read on October 28, 2026. Toolkit shown: **v3.3.0**, dated **October 25, 2026**, approximately **299 KB**.

This detailed Markdown reference combines the visible Workflow page, the full workflow learning campaign and the downloaded v3.3.0 author-kit documentation, with source differences marked explicitly. It describes the current platform workflow and supplements the [project guide and quality reference](TB4-study-reference.md).

## Contents

- [Local requirements and platform responsibilities](#local-requirements-and-platform-responsibilities)
- [Step 0: Get the toolkit](#step-0-get-the-toolkit)
- [1. Create the task](#1-create-the-task)
- [2. Fill the task files](#2-fill-the-task-files)
- [3. Check the structure](#3-check-the-structure)
- [4. Package the task](#4-package-the-task)
- [5. Upload to Supertasker](#5-upload-to-supertasker)
- [6. Address the quick check](#6-address-the-quick-check)
- [7. Review pass@3](#7-review-pass3)
- [8. Submit the P3 ID in DAS](#8-submit-the-p3-id-in-das)
- [9. Follow the full review](#9-follow-the-full-review)
- [Changes invalidate earlier checks](#changes-invalidate-earlier-checks)
- [Where to track progress](#where-to-track-progress)
- [Designing difficulty for the right reason](#designing-difficulty-for-the-right-reason)
- [Platform workflow and learning sequence compared](#platform-workflow-and-learning-sequence-compared)
- [Toolkit contents, version migration and approved edits](#toolkit-contents-version-migration-and-approved-edits)
- [Optional local runtime checks, and the learning-course requirement](#optional-local-runtime-checks-and-the-learning-course-requirement)
- [Identity, duplicate prevention and fair use](#identity-duplicate-prevention-and-fair-use)
- [Read results before deciding the next action](#read-results-before-deciding-the-next-action)
- [Full review, pass@8 and returned work](#full-review-pass8-and-returned-work)
- [Operational decision checklist](#operational-decision-checklist)
- [Sources and verified scope for this detailed edition](#sources-and-verified-scope-for-this-detailed-edition)
- [Answers: workflow knowledge checks (42)](#answers-workflow-knowledge-checks-42)

## Local requirements and platform responsibilities

The **v3.3.0 toolkit requires Python 3.12 or newer**. You do not need local Docker, a local model, or an API key for this workflow.

| On your machine | On the TB4 platform |
|---|---|
| Create a task from a template | Execute the reference solution, no-op and cheat controls |
| Fill the task files | Run the 35 base criteria and 5 project checks |
| Run structural lint | Run pass@3 |
| Package the task ZIP | Perform the full review |

**Source discrepancy confirmed October 28:** the Learning courses still require local Docker/Harbor and local oracle/nop runs, and instruct authors to supply a claimed DAS link before upload. The current Workflow page places execution on the platform and asks for a DAS Task ID only on the first task. This guide records the live Workflow page; it does not claim the two sources agree. See [the updated learning notes](TB4-learning-update-2026-10-28.md#source-discrepancy) for the comparison. Task Dockerfiles remain required even when execution happens on the platform.

## Step 0: Get the toolkit

Download the official toolkit from the Workflow page:

- [Download toolkit v3.3.0](https://queue.supertasker.ai/gate/kit/download)
- Expected filename: `tb4-starter-pack-v3.3.0-2026-10-25.zip`

The page provides the following **Bash-style setup commands**. They are not native PowerShell commands.

```sh
mkdir -p ~/tb4 && unzip ~/Downloads/tb4-starter-pack-v3.3.0-2026-10-25.zip -d ~/tb4
export PATH="$HOME/tb4/tb4-starter-pack:$PATH"
tb4 --version            # tb4 3.3.0
tb4 new output-task my-task --dir tasks
```

The `export PATH` line applies only to the current terminal. Repeat it in each new terminal or add it to the appropriate shell profile.

The toolkit's `example/` directory shows the task files filled in. The v3.3.0 download completed on October 28 to `C:\Users\Administrator\Downloads\tb4-starter-pack-v3.3.0-2026-10-25.zip` (305781 bytes). SHA-256: `2eb82e067e9059f7deb1bbaccf04a0ad9e54ccca596eaf48fc38e50351ae34d5`; its prefix matches the download link. Installation and toolkit execution were not performed.

## 1. Create the task

Choose one work folder and run every task command from it. Select the appropriate template:

| Template | Use |
|---|---|
| `repo-fix` | A bug fix or feature in a real repository. |
| `output-task` | A task that writes its answer to `/app/output`. |

Choose one of these commands and replace `<slug>` with the task's short name:

```sh
tb4 new repo-fix <slug> --dir tasks
```

```sh
tb4 new output-task <slug> --dir tasks
```

The slug uses lowercase letters, digits and hyphens, with **at most three words**. Example: `billing-tax-rounding`.

`tb4 new` lists the remaining placeholders by file and line. Fill every required placeholder.

## 2. Fill the task files

| File or directory | Required content |
|---|---|
| `instruction.md` | What to build or fix, in plain prose, without hints about the approach. |
| `task.toml` | Author name/email, description, keywords, tags and expert time. For `repo-fix`, fill the repository path and base commit in the collect hook's `R=` and `B=` values. |
| `environment/Dockerfile` | Agent image using the same repository base commit as `tests/Dockerfile`. |
| `tests/` | Verifier image, `emit.py`, `test_outputs.py`, `expected.json`, and the requirements, budget and grading files. |
| `solution/` | Reference solution that solves the task and must score **1**. |
| `cheat/<name>/solve.sh` | An attack on the grader that must score **0**. Set its `TARGET` to a real file in the task. |
| `README.md` | Difficulty, solution and verification explanations. Every claim points to a file shipped with the task. |

Preserve the shared harness: leave **`tests/test.sh`** and the **`[[verifier.collect]]` hook** unchanged except for values the template explicitly asks you to fill.

## 3. Check the structure

```sh
tb4 lint tasks/<slug>
```

The linter reports failures and remaining placeholders file by file. Correct them and rerun until `lint: PASS`. The v3.3.0 kit says linter warnings do not block packaging; read and assess them. This is separate from an official reviewer finding, which authors cannot waive.

Passing lint establishes structural readiness; execution controls and quality review run on the platform.

## 4. Package the task

```sh
tb4 package tasks/<slug>
```

Packaging runs lint first and refuses to continue while anything fails. When successful, it writes:

```text
deliveries/<slug>-<YYYYMMDD>.zip
```

The ZIP contains the task folder and nothing else. Keep unrelated tasks, old revisions, local run folders, caches and secrets out of the submission.

## 5. Upload to Supertasker

Open the [Submit tab](https://queue.supertasker.ai/#submit) and upload the packaged ZIP.

- **First task:** also provide the DAS Task ID, the number after `Task #` in DAS.
- **Later new tasks:** no DAS Task ID is needed at initial upload. The platform assigns its own task ID, such as `T-0142`, visible in **My tasks**.
- **Later versions of an existing task:** use **Upload the fix** on that task. This preserves one task and its version history.

## 6. Address the quick check

The platform runs the task controls and all **35 + 5 quality checks** against the uploaded files.

| Control | Required result |
|---|---|
| Reference solution / oracle | **1** |
| Doing nothing / no-op | **0** |
| Each cheat | **0** |

Items requiring changes appear in **To do**, one item per card.

For each revision:

1. Correct the reported problems.
2. Run `tb4 lint tasks/<slug>`.
3. Run `tb4 package tasks/<slug>`.
4. Upload the new ZIP using **Upload the fix** on the existing task.

If a reported flag appears incorrect, the report provides a dispute action where you can give a reason. A dispute is different from accepting or waiving an official reviewer finding.

## 7. Review pass@3

A passing quick check starts pass@3 automatically: three attempts by the target model on the **exact uploaded files**.

| Solved attempts | Result and next action |
|---|---|
| **1 or 2 of 3** | Qualifies; the platform issues a P3 ID. |
| **3 of 3** | Too easy; increase the genuine technical difficulty and upload a revision. |
| **0 of 3** | Returned for revision; inspect failures, fix unstated requirements or unfairness, or make the task somewhat easier. |

Read the three attempts and their logs/test output in the available task reports before revising. The earlier October 22 guide recorded a **Download pass@3 (.zip)** control; its availability was not reverified in a task report during this learning update.

Upload the revised task through **Upload the fix**.

## 8. Submit the P3 ID in DAS

When pass@3 qualifies, the new **P3 ID** appears in **Updates**.

1. Copy the P3 ID into the corresponding DAS task.
2. Submit that DAS task for review.
3. Do **not** upload the task ZIP to DAS; the P3 ID is what DAS needs.

The platform finds the P3 ID in DAS and links the two task records automatically, normally within **about 10 minutes**. **My tasks** then shows the linked DAS task alongside the platform task ID.

Every revised task needs its own qualifying pass@3 and **new P3 ID**. Put that new ID in the **same DAS task**. Never reuse an old P3 ID.

## 9. Follow the full review

Full review runs on the platform after pass@3, and a reviewer decides the next action. A returned task appears in **To do** with the reviewer's comment and an **Upload the fix** button.

The learning courses provide the fuller review rules, including pass@8; see the [project guide and quality reference](TB4-study-reference.md).

## Changes invalidate earlier checks

**Editing any task file invalidates the earlier checks, including pass@3.** Run lint, package the updated task and use **Upload the fix**. The platform checks the new revision from the beginning.

Do not treat results or a P3 ID from an earlier version as evidence for changed files.

## Where to track progress

| Interface section | Purpose |
|---|---|
| **To do** | Work that requires your action, including fixes and returned tasks. |
| **Updates** | Notifications that a check or pass@3 has finished; qualifying P3 IDs. |
| **My tasks** | Task IDs, version history, completed stages and linked DAS tasks. |

## Designing difficulty for the right reason

The Workflow page gives observations from tasks that achieved 1 or 2 successful attempts out of 3. These are design guidance, not additional formal checks. The quality course separately requires a professional explanation of difficulty; a pass rate alone does not establish that explanation.

### Work the model often handles well

- Reading all records and applying explicitly supplied rules or a general method.
- Reproducing a worked sample or matching a reference report.

A task relying only on these can be too easy.

### Failure patterns observed in qualifying tasks

| Pattern | Examples from the Workflow page | Design lesson |
|---|---|---|
| Trusting mutually consistent records | A spinach recall: records assigned pulls to the oldest pallet, but actual lane operation used the newest first. Failed attempts missed 13 affected batches. | Require reasoning about the real system and complete coverage, with the scope explicitly stated. |
| Missing exceptions despite a complete-looking answer | An insurance claim attributed two units to a freeze, while an earlier wall leak required setting a unit aside under the manual. A data-hall task similarly used coherent but false operator records. | The task may require challenging evidence and checking what should be excluded, not just validating listed results. |
| Stopping when a visible example passes | A data-lake solution matched a sample yet produced zero rows for an unseen table; a log audit labeled 43 delivered events as lost on an unseen host-day. | Grade the entire stated contract across cases beyond the worked example. |
| Misinterpreting messy evidence | Scanned speed tapes led one attempt to report no trace and another to invent emergency braking and overspeed. | Realistic input interpretation can create genuine difficulty when the required judgments are clear. |

The governing rule is: **state the full scope, then grade all of it**. The instruction, or a specification it makes binding, must define completeness. For example, a recall task must cover every batch containing ingredient or rework from a recalled lot if that is what the tests require.

Vague instructions, undisclosed filenames or fields, environment tricks, hints revealing the fix and partial-credit rewards do not create acceptable difficulty.

## Platform workflow and learning sequence compared

The main numbered steps in this guide reproduce the live Workflow page for v3.3.0. The Learning course retains a different local-validation and DAS-link procedure. The downloaded toolkit README independently confirms that Docker/Harbor checks are **optional locally**: it places controls, model trials and review in the cloud. Its DAS-ID wording is broader than the live page and does not mention the first-task exception.

| Stage | Current Workflow page / v3.3.0 kit | Learning course wording |
|---|---|---|
| Preparation | Python 3.12+; toolkit creates/lints/packages task. | Project machine with Docker, Harbor 0.23.0, git, Python and tb4; set TB4_ROLE. |
| Claiming | Workflow page distinguishes first-task DAS ID from later platform task IDs. | Claim DAS Attempt first; supply the original task link. Claim next only after submitting current task. |
| Validation | Local structural lint; runtime controls execute on platform. Docker/Harbor are optional locally in kit. | Local lint, oracle = 1 and nop = 0 are required before each upload. |
| Revision upload | Upload the fix on the existing platform task. | Changed ZIP associated with the same DAS link. |
| P3 submission | New P3 ID into the corresponding existing DAS task; no ZIP. | Same rule, explicitly validate category/details and ID match before submitting. |

For operational use, follow the current interface and versioned toolkit. Do not claim the old course's local-execution requirement still applies to the v3.3.0 path. Conversely, do not rewrite the quiz's expected answer: it reflects its displayed source. If the assignment's DAS-link instruction conflicts with the upload form, obtain a project ruling. No such ruling was obtained while preparing this guide.

## Toolkit contents, version migration and approved edits

The verified download is v3.3.0, 305781 bytes. The archive was read without installing or executing it. It contains:

| Path in `tb4-starter-pack/` | Use |
|---|---|
| `tb4` | Create, lint and package commands. |
| `lint/` | Structural validation rules. |
| `template/repo-fix-task/` | Repo-fix skeleton selected by `tb4 new repo-fix`. |
| `template/output-task/` | Output task skeleton. |
| `example/runner-failure-visibility/` | Completed repo-fix example for interpreting placeholders. |
| `README.md` | Authoring, upload and optional local-execution instructions. |
| `VERSION` | Toolkit version record. |

The kit says version 3 removed `tb4 attempt`: official model trials run on the platform. Packaging no longer requires the old local review report, oracle/nop runs and pass@3 evidence; the package is the source task and the platform runs the checks. Preserve your source tasks when updating tooling. Old run folders are historical evidence and should stay outside the submitted task.

For shared harness files, the kit's allowed edits are narrower than a general invitation to rewrite the verifier:

- Repo-fix: fill collection-hook `R=` (repository path) and `B=` (base commit).
- Output task: set `RUN_PROGRAM` near the start of `tests/test.sh` to 1 if the verifier runs a delivered program, 0 for data-only output.
- Preserve other shared harness code. Fill task-specific tests, observations, grading declarations, solution and cheat targets in their intended files.

A slug may contain lowercase words and digits separated by single hyphens, at most three words. Uppercase, underscores, spaces, a leading/trailing hyphen or repeated hyphens are rejected. Examples: `billing-tax-rounding`, `ledger-v2-merge`, `csvfix`.

### Suggested working-folder layout

This diagram combines the toolkit's task/delivery folders with the optional local-evidence folder. Do not put `jobs/` or private author notes inside a task directory.

```text
work-folder/
  tasks/
    your-slug/
      instruction.md
      task.toml
      README.md
      environment/Dockerfile
      tests/
      solution/
      cheat/
  deliveries/
    your-slug-YYYYMMDD.zip
  jobs/                      optional local control evidence
  author-notes/              optional private provenance and revision notes
```

The `author-notes/` name is an organizational suggestion, not a required project path. Use the actual template for its full file layout.

## Optional local runtime checks, and the learning-course requirement

The following Bash commands are shown in Learning and are compatible with the optional local-debugging purpose described by the v3.3.0 kit. They are **not required local prerequisites of the current platform workflow**. They require Docker running and Harbor 0.23.0; they do not require a model API key.

Replace `<slug>` and `<run-id>` before running; angle-bracket placeholders are not literal shell arguments. Use a fresh run ID so results cannot be confused with previous revisions.

```sh
export TB4_ROLE=attempter

tb4 lint tasks/<slug>

harbor run -p tasks/<slug> -a oracle -k 1 -n 1 -o jobs --job-name <slug>-oracle-<run-id>
cat jobs/<slug>-oracle-<run-id>/*/verifier/reward.txt

harbor run -p tasks/<slug> -a nop -k 1 -n 1 -o jobs --job-name <slug>-nop-<run-id>
cat jobs/<slug>-nop-<run-id>/*/verifier/reward.txt
```

Read the actual `reward.txt`, not only the summary. Oracle must score 1; nop must score 0 because graded tests fail. A build failure, missing tool or broken capture is not a valid negative control. Inspect structured reports and logs, and repeat controls after changes if using them as evidence of that revision's behavior. Controls are not model attempts.

`TB4_ROLE=attempter` identifies the author role in the learning instructions; it does not start reviews or log in to the platform. The kit's simpler local examples use fixed job names; fresh run IDs preserve earlier evidence without deleting it.

The optional personal pass@1 proxy in Learning is separate: a fresh agent may receive only the prompt and agent-visible files. It receives no hidden tests or solution. Its result is rough design feedback and never replaces official pass@3 or supplies official evidence.

## Identity, duplicate prevention and fair use

| Identifier | What it identifies | What it does not establish |
|---|---|---|
| Platform task ID, such as T-0142 | The platform task and its revision history. | A qualifying model result. |
| DAS Task ID/link | The assignment in DAS. | The tested ZIP or revision. |
| ZIP hash | Exact upload bytes, used for duplicate detection. | A P3 validation ID. |
| Revision digest | Files bound to validation evidence. | Approval of a changed revision. |
| P3 validation ID | A particular qualifying pass@3 run and revision. | Final quality acceptance or approval of later edits. |

The learning course says identical ZIPs are blocked when earlier checks are queued/running or completed, including completed quality FAIL. Retry identical bytes only if the prior lightweight execution failed to run. A duplicate block starts no new checks, pass@3 or model usage. Read the prior-run reference and status rather than attempting to evade the block.

The learning quota is **five submissions per trainer per day**. A task outside the pass@3 range must be substantively revised and revalidated; do not repeatedly submit the unchanged task hoping for a different score. Follow service/support instructions for infrastructure errors.

## Read results before deciding the next action

| Result | Meaning | Next action |
|---|---|---|
| PASS | This check passed on this revision. | Continue to the next required stage; not final acceptance. |
| FAIL | A quality requirement failed. | Correct it, lint/package and upload a revision; local controls also repeat under the learning procedure. |
| ERROR | Execution did not complete validly. | Inspect service status/logs; do not count as a model failure or waive it. |
| BLOCKED | A prerequisite or duplicate rule prevented execution. | Read the reason and existing-run reference; resolve the prerequisite. |
| MISSING | Evidence required for this revision is absent. | Complete the stage that produces it. |
| FAIL-PENDING-DISPOSITION / hold | Official reviewer decision required. | Wait for the recorded QM decision; author cannot accept or waive it. |

For scored model failures, read both the agent log and verifier report. A report identical to nop can mean a real failed attempt or a harness/provider fault that never let the agent work. Only the agent log distinguishes them. Voids are rerun. Missing capture or corrupted evidence must not become reward 0. The learning course says agent timeout is not a scored failure; inspect whether the run produced a valid completed result.

## Full review, pass@8 and returned work

The learning course provides the detailed review policy below. The live Workflow page summarizes full review as a platform stage after pass@3.

| Stage/outcome | Action |
|---|---|
| DAS Attempt submitted | Task moves to Review; author may claim another task. |
| Full review | OPS/QMs assess runtime controls, independent review, originality and all 35 base + 5 project criteria. |
| No QM modification | Five fresh trials join the original three for eight total. |
| Any QM modification | Run eight fresh trials on the changed revision. |
| Review clears and 1–6/8 solved | Eligible for Pre-delivery, not immediate Delivery. |
| 0/8, 7/8 or 8/8 | Return for task changes and complete renewed validation. |
| Major defect | Original DAS Attempt returns with actionable feedback. |
| Minor defect | QM may fix in Review; changed files require fresh trials. |
| Hold/inconclusive result | Await the recorded QM decision. |
| Any cheat scores 1 | Block delivery until the verifier is hardened, regardless of model results. |

The cheat control is separate from the model attempts. It does not count toward pass@3 or pass@8.

When work returns:

1. Read the review report and identify the substantive defect.
2. Revise the source task and synchronize the prompt, tests, solution, README and metadata.
3. Run lint and package. If using local controls, repeat them on the changed revision; Learning requires this step.
4. Use **Upload the fix** on the existing platform task. Preserve the original DAS task association.
5. Complete the new quick check and a fresh qualifying pass@3.
6. Replace the old P3 ID with the new one in the same DAS task and resubmit.

Never create a separate Attempt to bypass a return or reuse a previous P3 ID for changed files. QMs build the Pre-delivery package and first upload the task ZIP to DAS at that stage. Authors submit the P3 ID and required category/details, not the task ZIP or local run logs.

## Operational decision checklist

### Before starting

- [ ] Confirm toolkit version and live workflow requirements.
- [ ] Distinguish the platform path from older learning-only local prerequisites.
- [ ] Identify the existing assignment/task when revising; preserve its history.
- [ ] Choose repo-fix or output-task and a valid short slug.
- [ ] Establish originality, permitted licensing and a pinned baseline.

### Before upload

- [ ] Fill every placeholder and truthful author metadata.
- [ ] State complete acceptance criteria and exact schemas; map every requirement to tests.
- [ ] Use the exact trailer and resource values required by the project.
- [ ] Keep grader/answers separate and submitted execution unprivileged.
- [ ] Set every retained cheat TARGET to an actually exercised file.
- [ ] Match README descriptions to shipped implementation/evidence.
- [ ] Clear structural failures with `tb4 lint`.
- [ ] Package with `tb4 package`; inspect that it contains one task folder.
- [ ] Exclude job folders, private notes, secrets, caches and old revisions.
- [ ] Use the platform's required DAS field for initial upload, or Upload the fix for a revision.

### After upload

- [ ] Read To do findings and resolve them on a new revision.
- [ ] Distinguish scored failures from infrastructure errors/voids.
- [ ] Inspect all three attempts when pass@3 is out of range.
- [ ] Submit only a fresh qualifying P3 ID for this revision in the corresponding DAS task.
- [ ] Follow Review feedback and preserve task identity on returns.
- [ ] Never treat a quick-check PASS, P3 ID or in-range pass rate alone as final acceptance.

## Sources and verified scope for this detailed edition

- **Workflow page:** https://queue.supertasker.ai/#workflow, inspected October 28, 2026; toolkit v3.3.0 dated October 25; platform execution, nine-step process, UI sections and difficulty examples.
- **Learning:** https://queue.supertasker.ai/#learning, all four campaigns and 62 written slides; numerical rules, authoring contract, 40 checks, 13 common errors, local-learning sequence and review/return policy.
- **Downloaded toolkit:** `tb4-starter-pack-v3.3.0-2026-10-25.zip`, SHA-256 `2eb82e067e9059f7deb1bbaccf04a0ad9e54ccca596eaf48fc38e50351ae34d5`; root README and both task-template READMEs inspected for this edition.

The toolkit was downloaded and its documentation read; it was not installed or run. No task was authored, uploaded or submitted to DAS while preparing these guides. Learning quiz completion is separate from task validation. Source snapshots are dated; this edition does not claim future changes have been checked.

## Answers: workflow knowledge checks (42)

Answers below follow the displayed course. In particular, its local oracle/nop requirement and claimed-DAS-link rule differ from the newer v3.3.0 workflow documented above.

| # | Slide | Question cue | Correct answer |
|---|---:|---|---|
| 1 | 1 | Older video conflicts with current written workflow | Follow the written workflow. |
| 2 | 2 | 19 of 20 tests pass | Reward 0. |
| 3 | 2 | pass@3 = 3/3 | Too easy; change the task and restart validation. |
| 4 | 2 | Provider fault | Void/rerun, not a scored failure. |
| 5 | 3 | Random threshold near misses | Suspect a broken or unclear task, not valid difficulty. |
| 6 | 3 | Nop fails because image build fails | Invalid control; tests must fail for task-related reasons. |
| 7 | 4 | When to claim the next task | After submitting the current task in DAS. |
| 8 | 5 | Existing public fix | Reject that problem; choose an original one. |
| 9 | 5 | Accepted repository licenses | MIT and Apache 2.0. |
| 10 | 5 | Introduced defect visible in history | Remove answer disclosure from agent-visible history/state. |
| 11 | 6 | Finance task uses some ML | Operations/Finance; classify by primary skill. |
| 12 | 6 | MySQL to PostgreSQL | Migration or port. |
| 13 | 7 | FROM python:latest | Mutable upstream image changes the environment and may bring the fix. Pin an image tag. |
| 14 | 7 | Personal pass@1 = 0/1 replaces pass@3? | No. It is an informal proxy only. |
| 15 | 8 | What to upload to DAS | No task ZIP/logs; submit the new P3 ID, category and required details. |
| 16 | 8 | pass@3 = 0/3 | Fix solvability/complexity, change the task and repeat validation. |
| 17 | 8 | Supertasker email | The email matching the Slack account. |
| 18 | 9 | Valid slug | ledger-close-fix. |
| 19 | 9 | TB4_ROLE=attempter | Identifies the author role; does not start reviews or log in. |
| 20 | 10 | Expected values | tests/expected.json, read by the protected judge. |
| 21 | 10 | Instruction-to-test mapping | tests/requirements.json. |
| 22 | 11 | Data-only output cheat | Keep symlink-answers, remove forge-reward. |
| 23 | 11 | TARGET never reached | A zero score proves nothing if the attack never fires. |
| 24 | 12 | Test edited after controls | Repeat lint, oracle and nop on the new version under the learning procedure. |
| 25 | 12 | Local jobs directory | Outside the task directory and ZIP. |
| 26 | 13 | Which files stay outside ZIP | Local jobs and superseded runs; retain solution and cheat controls inside the task. |
| 27 | 13 | Author assembles evidence/, MANIFEST.json, DELIVERY.md? | No; review team handles the delivery package. |
| 28 | 14 | Agent timeout | 28800 seconds. |
| 29 | 14 | allow_internet | Omit the key; both explicit values are rejected by the learning contract. |
| 30 | 14 | Valid memory | 4096 MB. |
| 31 | 15 | Result resembles nop | Read the agent log to distinguish an actual attempt from a void. |
| 32 | 16 | Identical ZIP after quality FAIL | Blocked; change the task first. |
| 33 | 16 | Daily quota | Five submissions per trainer. |
| 34 | 17 | P3 ID after revision | Use the new ID from that revision's qualifying run. |
| 35 | 17 | Infrastructure error counts as 0? | No; it is not a scored failure. |
| 36 | 18 | Returned DAS task | Preserve the original task/link and resubmit there with a new P3 ID. |
| 37 | 19 | QM changed task | Eight fresh trials. |
| 38 | 19 | pass@8 = 8/8 | Return for task changes. |
| 39 | 19 | Cheat = 1, model = 4/8 | Delivery blocked until the verifier is hardened. |
| 40 | 20 | FAIL-PENDING-DISPOSITION | Await QM decision; do not self-waive. |
| 41 | 20 | BLOCKED duplicate | Read the preventing rule and existing-run reference; do not bypass it. |
| 42 | 21 | Which comes first in Learning | Local lint and oracle/nop, then Supertasker, then P3 submission in DAS. |
