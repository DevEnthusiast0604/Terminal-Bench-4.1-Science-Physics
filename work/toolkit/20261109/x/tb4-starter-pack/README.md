# TB4 author kit

How to build a Terminal-Bench 4.0 task: the structure to follow, a template for
each kind of task, a finished example, and the `tb4` command to start a task,
check it and package it. Everything that runs the task (the controls, the model
attempts and the reviews) runs on the review platform, in the cloud.

The path, in order:

1. Create the task from the template and fill it (`tb4 new`).
2. Check its structure until it passes (`tb4 lint`).
3. Package it (`tb4 package`) and upload the zip on the review platform, with
   the task's DAS Task ID.
4. The platform runs the quick check. Fix what it flags and upload again with
   the same Task ID.
5. A passing quick check starts pass@3 by itself. When pass@3 is OK, the
   platform gives you a P3 ID: paste it into the DAS task and submit it.

What is in the kit:

| Path | What it is |
|---|---|
| `tb4` | The command: `tb4 new` starts a task from the template, `tb4 lint` checks its structure, `tb4 package` builds the zip you upload. |
| `lint/` | The structure checks `tb4 lint` runs. |
| `template/` | The two task skeletons, `repo-fix-task/` and `output-task/`. `tb4 new` copies one. |
| `example/runner-failure-visibility/` | A filled-in `repo-fix` task. Use it as the reference when a placeholder is not clear. |
| `VERSION` | The kit's version. |

## 1. Setup

### What you need

Python 3.12 or newer. That is all: `tb4` runs no Docker, no model and needs no
API key. (Docker and Harbor are optional, to try your solution locally: see
"Optional: run it on your machine" below.)

### Install (once)

Run this where you saved the download. It unzips the kit, puts `tb4` on your
PATH and shows the version:

```sh
mkdir -p ~/tb4 && unzip <zip-file-name> -d ~/tb4
export PATH="$HOME/tb4/tb4-starter-pack:$PATH"
tb4 --version
```

The `export` line lasts only for the current terminal: run it in every new one
(or add it to your shell's profile).

### What a slug is

The slug is the task's short name. It names the task folder, the task
(`terminal-bench/<slug>`) and the zip you upload. Use lowercase letters, digits
and hyphens, at most three words. `tb4 new` refuses anything else.

| Slug | OK? | Why |
|---|---|---|
| `billing-tax-rounding` | Yes | Three lowercase words |
| `ledger-v2-merge` | Yes | Digits are fine |
| `csvfix` | Yes | One word is fine |
| `Billing-Tax` | No | Uppercase |
| `billing_tax` | No | Underscore |
| `billing tax` | No | Space |
| `fix-the-billing-tax` | No | More than three words |
| `-billing` or `billing--tax` | No | Leading, trailing or double hyphen |

### Where to run

Pick one work folder and run every command from it. `tb4 new ... --dir tasks`
creates `tasks/` there, and `tb4 package` writes the zip to `deliveries/` there.

## 2. Create the task

### Start from the template

`repo-fix` is a bug fix or feature in a real repository. `output-task` writes
its answer to `/app/output`. The command creates `tasks/<slug>` and lists every
placeholder left to fill, by file and line:

```sh
tb4 new repo-fix <slug> --dir tasks
tb4 new output-task <slug> --dir tasks
```

For example `tb4 new repo-fix billing-tax-rounding --dir tasks`.

### Fill the files

Replace every placeholder `tb4 new` listed.

| File | What goes in it |
|---|---|
| `instruction.md` | What to build or fix, in plain prose. No hints about the approach. |
| `task.toml` | Your name and email, the description, keywords, tags, the expert time. For `repo-fix`, the repository path and base commit in the collect hook (`R=` and `B=`). |
| `environment/Dockerfile` | The agent's image. Same base commit as `tests/Dockerfile`. |
| `environment/locks/`, `tests/locks/repo/` | Every Python dependency, from a committed lockfile (TB 4.1): edit `pyproject.toml`, run `uv lock` as its first lines say, and commit `pyproject.toml` and `uv.lock`. Never `pip install` in a Dockerfile. `tests/locks/judge/` and `tests/locks/suite/` are template tooling: leave them as they are. |
| `tests/` | The verifier's image (`tests/Dockerfile`), `emit.py` and `test_outputs.py`, `expected.json`, and the `requirements.json`, `budget.json` and `grading.json` files. |
| `solution/` | Your reference solution. |
| `cheat/<name>/solve.sh` | A cheat that must score 0. See "Point the cheat at your task" below. |
| `README.md` | Difficulty, solution and verification. Every claim points at a file you ship. |

`example/runner-failure-visibility/` shows each of these files filled in.

If your verifier turns a measured number into the reward (an error, a match
rate, a speedup), write the measured value and the threshold it was compared
with to `/logs/verifier/reward-details.json`, on failing runs too. A reviewer
can then tell a near miss from a wrong approach.

To see what is left at any time, run `tb4 lint tasks/<slug>` (see "Check the
structure" below): it lists every placeholder still in the task, by file and line.

**Leave these alone:** `tests/test.sh` and the `[[verifier.collect]]` hook in
`task.toml` are the shared harness. Do not edit them, except the values the
template asks you to set: for `repo-fix`, `R=` and `B=` in the collect hook;
for `output-task`, `RUN_PROGRAM` near the top of `tests/test.sh` (1 when the
verifier runs a program you deliver, 0 for data files only).

### Point the cheat at your task

A cheat attacks the grader instead of solving the task, and it must score 0.
Keep the cheat that fits your task and set its `TARGET` to a real file of your
task:

| Task kind | Cheat and its TARGET |
|---|---|
| `repo-fix` | `cheat/forge-reward` and `cheat/skip-tests`: the same module your graded tests import, in both. |
| `output-task` whose verifier runs your program | `cheat/forge-reward`: the deliverable program. Delete `cheat/symlink-answers`. |
| `output-task` with data files only | `cheat/symlink-answers`: a deliverable file the judge reads. Delete `cheat/forge-reward`. |

Example (billing-tax-rounding), in `cheat/forge-reward/solve.sh`:

```sh
TARGET="/app/billing/invoice.py"
```

**TARGET must be reached by the graded run.** For `repo-fix`, a module the
graded tests import (a file your solution changes is a safe choice). For an
output task, the program the verifier runs or the file the judge reads. A
cheat that never fires also scores 0, so it proves nothing.

### Check the structure

```sh
tb4 lint tasks/<slug>
```

No Docker and no model, a few seconds, so run it after every edit. It checks
every file-level rule (placeholders, `task.toml`, the instruction, the README,
the requirements, budget and grading files, the verifier's structure) and
prints each problem as file and line. Fix every FAIL until it ends with
`lint: PASS`. Warnings never block: read them and decide.

## 3. Package and upload

```sh
tb4 package tasks/<slug>
```

It runs `tb4 lint` first and refuses while anything fails. When the lint
passes it writes `deliveries/<slug>-<YYYYMMDD>.zip`: the task folder, nothing
else. Upload that zip on the review platform (Submit tab) with the task's DAS
Task ID.

## 4. What the platform does

Everything below runs in the cloud; you follow it on the platform's Submit tab
(Updates and My tasks).

| Step | What happens |
|---|---|
| Quick check | The controls (your solution scores 1, doing nothing scores 0, the cheats score 0), the TB4 quality checks on every file of the task. You get a note with what to fix, one card per item. |
| Fix and upload again | Fix what the note lists, run `tb4 lint` and `tb4 package` again, and upload the new zip with the same Task ID. |
| pass@3 | A passing quick check starts it by itself: three attempts by the target model on those exact files. At least one must fail. If the model solves all three, the task is too easy: make it harder and upload it again. |
| P3 ID | When pass@3 is OK, the platform gives you a P3 ID. Paste it into the same DAS task and submit it for review. |
| Full review | Runs on the platform after pass@3. A reviewer decides what comes next. |

A revised task gets a new P3 ID from its own pass@3: never reuse one.

## If you edit a file

Any change to a task file makes the earlier checks out of date, pass@3
included. Run `tb4 lint` and `tb4 package` again and upload the new zip with
the same Task ID: the platform checks the new version from the start.

## Optional: run it on your machine

Not needed for the platform, but useful while you build the task: with Docker
and Harbor 0.25.0 installed, run your solution (expect 1) and an empty run
(expect 0):

```sh
harbor run -p tasks/<slug> -a oracle -k 1 -n 1 -o jobs --job-name <slug>-oracle
cat jobs/<slug>-oracle/*/verifier/reward.txt
harbor run -p tasks/<slug> -a nop -k 1 -n 1 -o jobs --job-name <slug>-nop
cat jobs/<slug>-nop/*/verifier/reward.txt
```

Read `reward.txt`, not the summary line, and delete a job folder before you
run it again.

## Updating from version 2

Version 3 drops `tb4 attempt` (model attempts run on the platform) and the old
`tb4 package` checks (review report, oracle and nop runs, pass@3): the zip is
now the task alone, and the platform runs the rest. Your `tasks/` are
untouched; `jobs/` and `deliveries/` from version 2 can be deleted.
