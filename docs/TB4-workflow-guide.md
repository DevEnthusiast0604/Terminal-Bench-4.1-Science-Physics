# Tango Bravo IV / Terminal Bench 4: Workflow Guide

Source: [TB4 Queue — Workflow](https://queue.supertasker.ai/#workflow), read on October 22, 2026. Toolkit shown: **v3.0.0**, dated **October 17, 2026**, approximately **202 KB**.

This is a Markdown reference based on the visible Workflow page. It describes the current platform workflow and supplements the [project guide and quality reference](TB4-study-reference.md).

## Local requirements and platform responsibilities

The **v3.0.0 toolkit requires Python 3.12 or newer**. You do not need local Docker, a local model, or an API key for this workflow.

| On your machine | On the TB4 platform |
|---|---|
| Create a task from a template | Execute the reference solution, no-op and cheat controls |
| Fill the task files | Run the 35 base criteria and 5 project checks |
| Run structural lint | Run pass@3 |
| Package the task ZIP | Perform the full review |

The earlier onboarding slides mention local Docker and Harbor. For the **v3.0.0 authoring and submission workflow**, the Workflow page explicitly places execution and review on the platform. The task still contains Dockerfiles defining its agent and verifier environments; those are different from requiring Docker on the author's machine.

## Step 0: Get the toolkit

Download the official toolkit from the Workflow page:

- [Download toolkit v3.0.0](https://queue.supertasker.ai/gate/kit/download)
- Expected filename: `tb4-starter-pack-v3.0.0-2026-10-17.zip`

The page provides the following **Bash-style setup commands**. They are not native PowerShell commands.

```sh
mkdir -p ~/tb4 && unzip ~/Downloads/tb4-starter-pack-v3.0.0-2026-10-17.zip -d ~/tb4
export PATH="$HOME/tb4/tb4-starter-pack:$PATH"
tb4 --version            # tb4 3.0.0
tb4 new output-task my-task --dir tasks
```

The `export PATH` line applies only to the current terminal. Repeat it in each new terminal or add it to the appropriate shell profile.

The toolkit's `example/` directory shows the task files filled in. The download link was clicked during inspection, but download completion and local installation were **not verified**.

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

The linter reports failures and remaining placeholders file by file. Correct them and rerun until lint passes.

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

Use **Download pass@3 (.zip)** in **To do** to obtain the three attempts, including logs and test output. Read what the model did and why the tests failed before revising.

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

## Compact checklist

- [ ] Obtain the official v3.0.0 toolkit and have Python 3.12+ available.
- [ ] Choose one work folder and the correct template.
- [ ] Use a valid slug of at most three words.
- [ ] Fill every placeholder and every required task file.
- [ ] Keep agent/verifier repository base commits aligned.
- [ ] Preserve the shared harness except for requested template values.
- [ ] Set each cheat's `TARGET` to a real task file.
- [ ] Run lint until it passes.
- [ ] Package with `tb4 package` and upload the generated ZIP.
- [ ] Resolve quick-check items through **Upload the fix**.
- [ ] Inspect pass@3 logs if results are outside 1–2 of 3.
- [ ] Submit the new qualifying P3 ID in the corresponding DAS task.
- [ ] Check **To do**, **Updates** and **My tasks** for review progress.
- [ ] After any edit, repeat lint, package and upload; obtain fresh checks and a new qualifying P3 ID.

## Sources and scope

- [TB4 Queue — Workflow](https://queue.supertasker.ai/#workflow): toolkit version, setup commands, nine workflow steps, tracking interface and difficulty examples.
- [TB4 Queue — Learning](https://queue.supertasker.ai/#learning): complementary quality and review rules, summarized in the separate project reference.

The website was read directly in Chrome. This document does not certify that the toolkit was downloaded, installed or run. It records the workflow visible on the inspection date; check the live Workflow page for later toolkit versions or process changes.
