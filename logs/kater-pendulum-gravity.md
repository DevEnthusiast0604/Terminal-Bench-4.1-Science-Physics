# kater-pendulum-gravity: task log

Read this log and `logs/STATUS.md` before opening any task file. Entries are summaries: the numbers, the
decision and where the evidence lives. All times are UTC (the platform shows UTC; this PC is UTC-7).

## Identity

| Field | Value |
|---|---|
| State | **Withdrawn 2026-10-28 11:08** (quick-check limit used up); archived |
| Source | `tasks/archive/kater-pendulum-gravity/`: output-task template in program mode (`RUN_PROGRAM=1`), deliverable `reduce.py`, cheat `forge-reward` aimed at `/app/output/reduce.py` |
| Platform | **T-0610**, https://queue.supertasker.ai/task/T-0610 (v1–v5 were burg-spectral-estimation, withdrawn 2026-10-27 01:10) |
| DAS Task ID | **3965796** (task page links it as linkedin.com/ai-trainer/tasks/7432487) |
| Category | Science / Physics |
| Target | pass@3 solved **1–2 of 3** |
| P3 IDs pasted into DAS | none yet |
| Zip on the platform | `deliveries/archive/kater-pendulum-gravity/kater-pendulum-gravity-v15-20261028.zip` = v15 (last upload), job 9231, task digest `sha256:8aec1e5e2e0ca1bc7044fe12fa3502af65c0f5d2fba4266b6d4f918d88918201`, zip sha256 `2dda4fc158b7cdbdd5341720c8ad2f6afd16ef50c5931fc6ad75d52d06995a54` |
| Older zips | `deliveries/archive/kater-pendulum-gravity/kater-pendulum-gravity-v{6..10}-20261027.zip`, `…-v{11..14}-20261028.zip` (v14 = job 9086, `5d3c853f…`; v13 = job 8949, `65a4c83b…`; v12 = job 8831, `79f156be…`; v11 = job 8691, `f616e3e3…`; v10 = job 8267) |
| Evidence | `work/kater-pendulum-gravity/v<N>/`: criteria reports, upload note, `pass3/pass3.zip` + `pass3/x/` (untrusted), `attempts/` digests, `explore/` scripts |
| Platform paths | per job J: `gate/task/J.zip`, `gate/criteria/J.md`, `gate/extra/J.md`, `gate/full/J.zip` (pass@3); `links T-0610 v<N>` lists them |

## State now

- **2026-10-28 00:29**: v11 uploaded with "Upload the fix" (job 8691); quick check queued; no unseen cards.
- **01:33**: quick check still running (it left the queue between 00:41 and 00:58); no cards yet. Watching paused at
  the user's request; resume with `tools/supertasker.py status T-0610` / `updates T-0610`.
- **01:34**: one-off check: quick check still running, 0 unseen cards. Rule from now on: log each card as soon as it
  appears (Seen = no), even with watching paused.
- **01:55**: v11 35-criteria report out before its card (`work/kater-pendulum-gravity/v11/criteria-35.md`): 31 pass,
  **2 FAIL**, 1 N/A, `novel` deferred.
  - Both FAILs (`verification_explanation_quality`, `test_instruction_alignment`) have one cause: instruction.md
    said "Anything it writes to standard error is ignored", but `tests/emit.py` fails a case past 1 MiB of stderr.
  - Fix prepared for v12:
    - instruction.md states both caps ("at most 1048576 bytes to standard output and … standard error, or that
      session fails; what it writes to standard error is not graded");
    - new R15 → all six tests;
    - README states the caps (`MAX_STDOUT_BYTES`, `MAX_STDERR_BYTES`).
  - Lint PASS, scan 0 problems. Upload waits for the card and the extra-criteria report, so everything is fixed in
    one round.
- **02:00**: card "the quick check found something to fix" (36/39, the same 2 FAILs). It asked to remove the stderr
  cap instead of stating it, so v12 follows the card (see Version history). Card marked seen at 02:07.
- **02:07**: v12 uploaded (job 8831); quick check queued. Watching resumed: the user asked to repeat
  fix-and-resubmit until the whole pipeline passes.
- **03:07**: v12 35-criteria report out before its card (`work/kater-pendulum-gravity/v12/criteria-35.md`):
  32 pass, **1 FAIL**, 1 N/A, `novel` deferred. The stderr fix passed.
  - FAIL `test_instruction_alignment`: the stated limits must equal the enforced ones:
    - instruction 600 s vs `CASE_TIMEOUT_SEC = 630`;
    - the 64 MiB per-file `ulimit -f 65536` was documented only in the README.
  - Fix prepared for v13:
    - instruction states "at most 630 seconds of wall-clock time from the moment the checker starts it, interpreter
      start-up included" and files "none of them larger than 67108864 bytes" (R11, R14 quotes updated);
    - README and the emit.py comment say the same.
  - Lint's D1 rule doesn't fire: no "each call" wording. Lint PASS, scan 0 problems. Waiting for the card.
- **03:10**: card "the quick check found something to fix" (37/39, 1 FAIL, marked AGAIN). Its fix:
  `CASE_TIMEOUT_SEC` → 600 (not the instruction → 630); disclose or remove the file cap; audit every limit in both
  test files. v13 follows the card. Card marked seen at 03:14.
- **03:14**: v13 uploaded (job 8949); quick check queued.
- **04:42**: v13 35-criteria report (`work/kater-pendulum-gravity/v13/criteria-35.md`): 32 pass, **1 FAIL**, 1 N/A,
  `novel` deferred. The 600 s and file-cap fixes passed.
  - FAIL `test_instruction_alignment`: instruction.md said the program "may write files only under" the TMPDIR and
    HOME folders, but nothing confines it (`/tmp` is writable), so a program writing elsewhere still passes.
- **04:47**: card "the quick check found something to fix" (37/39, the same FAIL, AGAIN). Its fix: route every
  program launch in `tests/test.sh` and `tests/emit.py` through filesystem confinement (writes only under HOME and
  TMPDIR), plus regression tests showing that writes elsewhere, `/tmp` included, can't pass unnoticed.
  - v14 departs from that fix and drops the unenforced claim instead, because the criterion only needs the instruction
    and the tests to agree.
  - Reasons: a confinement can't be tested here (no Docker or Linux), and getting it wrong could break the verifier.
  - Fallback if the same FAIL comes back on v14: implement the confinement the card asks for.
  - Card marked seen at 04:52.
- **04:52**: v14 uploaded (job 9086); quick check queued.
- **05:51**: v14 35-criteria report (`work/kater-pendulum-gravity/v14/criteria-35.md`): 33 pass, **0 FAIL**,
  1 N/A (`artifact_efficiency`), `novel` deferred to the full review. `test_instruction_alignment` passes.
- **05:56**: card "the quick check passed" (39/39). Extra criteria 5/5 (`v14/criteria-extra.md`). pass@3 started on
  v14; task files frozen until it ends. Card marked seen at 05:58.
- **06:33**: card "pass@3 solved 0 of 3". Logged at once, marked seen at 06:48 after the analysis (see pass@3
  analyses). Cause: h1's logbook mislabel was not stated in NOTES, so the check was unfair.
- **07:53**: v15 uploaded (job 9231); quick check queued. It states the logbook scope and adds h4's full swap
  (see Version history).
- **08:29**: v15 35-criteria report (`work/kater-pendulum-gravity/v15/criteria-35.md`): 32 pass, **1 FAIL**, 1 N/A,
  `novel` deferred. Extra 5/5 (`v15/criteria-extra.md`).
  - FAIL `test_instruction_alignment`: the instruction says `reduce.py` "must be a regular file, not a link", but
    `unpack` in `tests/tb4judge.py` (identical to the kit template) lets a folder named `reduce.py` through, and
    `python3 reduce.py` runs a folder's `__main__.py`, so such a folder could pass all six tests.
  - Local fix (not uploaded): `program_file()` in `tests/test_outputs.py`, called from `every_session`. Every test
    first checks with `os.lstat` that the unpacked `reduce.py` is a regular file of at most 20971520 bytes. The
    README verification bullet says so.
    - Emulated judge (`work/kater-pendulum-gravity/v16/explore/judge_check.py`): oracle 6/6; trust-logbook fails 5;
      empty fails 6; folder fails 6. Lint PASS, scan 97 files 0 problems.
- **08:35**: card "the quick check found something to fix" (37/39, the same FAIL, AGAIN). Logged at 08:40 and
  marked seen at 08:40.
  - The card's fix: validate the declared artifacts in `tests/tb4judge.py::unpack` before execution (`reduce.py` a
    regular, non-link file within 20971520 bytes), plus rejection tests for folders, links and oversized files.
  - **Quick-check limit used up** ($15.66 of $15.00 over 15 quick checks, all versions). Status: "Quick-check limit
    used up: with the review team".
    - The platform cannot take a new version, and the card says "Don't upload a new version of it".
    - The card counts pass@3 so far as 3, 3, 3, 3, 3, 3, 3, 0 of 3, and says another quick check will not find a
      version that is solved sometimes but not always.
    - A reviewer will either fix the task or raise its limit and say what to change; an update card follows.
    - Meanwhile the card suggests moving on to a new task (claim a new Attempt in DAS).
  - Decision: no upload. The local fix stays in `tasks/active/`; v15's zip stays in `deliveries/`. The loop of
    fix and resubmit is blocked until the reviewer's update.
- **11:08**: **withdrawn** at the user's request ("withdraw that task"), because the repeated too-easy results
  had used up the quick-check limit. Done with the new `tools/supertasker.py withdraw T-0610 "Withdraw the task"`;
  the review-team note was left empty. Platform status: "Withdrawn". No new card.
  - Archived: source → `tasks/archive/kater-pendulum-gravity/`; v15's zip →
    `deliveries/archive/kater-pendulum-gravity/kater-pendulum-gravity-v15-20261028.zip`.
  - The archived source is v15 plus the local regular-file fix (`program_file()`), which was never uploaded.
  - The user asked for a new, hard physics task, built and submitted under a new DAS attempt. It gets its own log.

## Current design (v11; v12–v14 change only the harness limits and how the instruction states them)

- **Deliverable**: `/app/output/reduce.py`, run as `python3 reduce.py SESSION_DIR` on four unseen sessions
  `tests/cases/h1..h4`. One JSON object with five members, the same as v10. Relative tolerances: g 4e-4, periods 1e-4
  (pivot and run), k 1e-3, release angles 2e-3. All numbers of all four sessions must pass. Limits: 600 s, 2 CPU, 4 GB,
  Python 3.12 + numpy 2.3.3 + scipy 1.18.1, read-only cwd and session.
- **Agent data**: `/app/data/NOTES.md` (rig, session.json fields, camera, files, stalls, "How sessions differ" limits) and
  example sessions `e1`, `e2` with no reference values.
- **Harness**: `tests/emit.py` per case, `CASE_TIMEOUT_SEC=600` since v13 (630 before), `MIN_WAIT_SEC` constant.
  Stdout is capped at 1 MiB; since v12 stderr is drained and discarded. Budget 60 + 4×660 + 120 + 180 margin = 3000 s.
  Six tests over all four sessions (`test_program_output` + five quantity tests). R1–R17 (R16 since v13, R17 since v14).
- **Graded sessions vs examples**: the examples have a pin on A (e1) or none (e2).
  - h1: pin on B; both weights moved since the balance; **logbook mislabel** (run b2 logged on B, hung on A).
  - h2: pins on both; square-on camera.
  - h3: steepest view (a 0.907, s +0.249); release 0.876 rad.
  - h4: pin on A 3.996 mm; light weight moved 38 mm.
- **Difficulty levers**: (1) the logbook mislabel in h1, which the instruction covers by defining periods by "the pivot
  the bar hung on". (2) Generalization beyond the examples: pins anywhere, stale CM, oblique or square-on views,
  stalls, rate, units.
- **Oracle** `solution/reduce.py`: `read_session` (CM carried to the run marks), `time_map` (floor criterion),
  `assign_pivots` (rough periods split at the largest log gap; majority vote of the logbook), `calibrate`, `pivots`.
  Worst 0.307 of tolerance over h1–h4, 12–18 s per session.
- **Evidence** `tests/estimator_bounds.txt` (119 lines):
  - Four reductions × four sessions × three seeds, worst errors: run period 3.1e-5, pivot period 1.6e-5, g 3.2e-5,
    k 1.9e-5, release angle 1.2e-3.
  - Sensitivities: g 3.10–3.12 × the period error, k 3.35–3.46 ×.
  - Rough pivot groups 7.7–9.5 % apart, spread within a group ≤ 0.09 %.
  - Wrong methods all fail ≥ 1 session. Logbook trusted fails only h1 (g 7.1e-2). Camera ignored fails h1, h3 and h4.
    The knife-edge law on the pins fails h2 and h4. CM from the balance fails h1, h3 and h4.
- **Self-checks (v11)**:
  - Emulated judge: oracle 6/6; trust-logbook fails 5 tests; empty submission fails all 6.
  - `tb4 lint` PASS (77 rows); `scan_task.py` 97 files 0 problems; no `__pycache__`.

## Version history

- **v1–v5** (burg-spectral-estimation, another task): v2–v4 passed the quick check but were 3/3; v5 was withdrawn.
- **v6** (10-27 03:27): first kater upload, square-on camera, GPS sync, stalls. The quick check FAILed on relative
  paths and thin tolerance evidence.
- **v7** (11:09): absolute paths; five-estimator bounds. The quick check didn't finish: canary missing in
  `estimator_bounds.txt`.
- **v8** (11:34): canary only. Quick check passed 36/39. pass@3 3/3 (5–12 min, errors ~1e-5).
- **v9** (14:19): oblique uncalibrated camera and release angles. Quick check passed 36/39. pass@3 3/3.
- **v10** (20:49, job 8267): rolling pin on A (3.002 mm) and a stale CM record (heavy weight moved 20 mm).
  - Quick check passed 21:36: 31 pass, 3 N/A, `novel` deferred; extra 5/5.
  - pass@3 3/3 at 22:21, sent back (SBQ).
- **v11** (10-28 00:29, job 8691): program graded on four unseen sessions, plus the h1 logbook mislabel.
  - Rewrote: generator, data, NOTES, instruction, `reduce.py` + `solve.sh`, emit/test/requirements, the evidence
    and README.
  - `symlink-answers` became `forge-reward`; scipy 1.18.1 added to both images (checked on PyPI: cp312 manylinux
    wheel, numpy >=2.0,<2.8); expert time 7 h → 10 h.
  - Note in `work/kater-pendulum-gravity/v11/upload-note.txt`.
  - Quick check 02:00: 36/39, 2 FAIL (stderr cap vs "standard error is ignored"). Report in `v11/criteria-35.md`.
- **v12** (10-28 02:07, job 8831): the v11 quick-check fix only.
  - `tests/emit.py` `run_case` drains and discards stderr (no `MAX_STDERR_BYTES`, no `STDERR_KEPT`).
  - instruction.md states the stdout cap: "at most 1048576 bytes to standard output, or that session fails; anything
    it writes to standard error is ignored". Bound as R15 to all six tests.
  - README lists run_case's failure conditions (the stdout cap, the 630 s deadline), stderr discarded, leftover
    processes killed with a 2 s drain, and the template's 64 MiB per-file `ulimit -f`.
  - Self-check `work/kater-pendulum-gravity/v12/explore/test_emit_win.py`: run_case on Windows with a
    PeekNamedPipe selector.
    - Passed: 3 MiB of stderr ignored; exactly 1048576 bytes of stdout OK; 1048577 bytes fails; timeout fires;
      the oracle on e2 through run_case gives rc 0.
  - Lint PASS (77 rows), scan 0 problems. Data, tests, tolerances and the oracle are unchanged from v11.
  - Quick check 03:10: 37/39, 1 FAIL `test_instruction_alignment` (600 s stated vs 630 s enforced; the 64 MiB
    `ulimit -f` not in the instruction). Report in `v12/criteria-35.md`.
- **v13** (10-28 03:14, job 8949): every enforced limit is stated in instruction.md.
  - `CASE_TIMEOUT_SEC` 630 → 600, matching the instruction ("600 seconds of wall-clock time from the moment the
    checker starts it, interpreter start-up included").
  - New instruction text:
    - files under TMPDIR/HOME at most 67108864 bytes (`ulimit -f 65536`);
    - empty stdin; environment only HOME/TMPDIR/PATH/LANG; leftover processes stopped at exit;
    - `reduce.py` a regular file, not a link, ≤ 20971520 bytes; the `/app/output` tar ≤ 536870912 bytes.
  - Requirement quotes R7, R11, R14 updated, R16 added. The README lists every limit with its code.
  - Self-check: lint PASS (16 requirements); scan 0 problems; `test_emit_win.py` all PASS. Note in `v13/upload-note.txt`.
  - Quick check 04:47: 37/39, 1 FAIL `test_instruction_alignment` (AGAIN): the "may write files only under TMPDIR and
    HOME" claim isn't enforced. Report in `v13/criteria-35.md`.
- **v14** (10-28 04:52, job 9086): the v13 quick-check fix only, plus one statement found in an audit of every sentence.
  - The unenforced write restriction is gone. The instruction now says only what holds: the TMPDIR and HOME folders
    "are empty and writable for it", and "no file it writes may grow larger than 67108864 bytes" (R14).
  - New R17 → all six tests: "Where the checker runs it, `/app/data` does not exist: the session folder it is given is
    all the data it gets." (The verifier image has no `/app/data`.)
  - README Verification: why a write elsewhere can't reach the grade. The judge runs `-I` with a clean env in a
    root-owned directory, reads only the captured observations from a root-only folder, and runs after every runner
    process is killed. It also covers `/app/data` being absent.
  - Self-check: lint PASS (17 requirements, 9 constraint sentences); scan 0 problems. Note in `v14/upload-note.txt`.
  - Quick check passed 05:56: 33 pass, 0 FAIL, 1 N/A, `novel` deferred; extra 5/5. pass@3 started.
  - pass@3 06:33: **0/3**, all three on h1's unstated logbook mislabel (see pass@3 analyses).
- **v15** (10-28 07:53, job 9231): fairness fix plus a difficulty lever on the same skill.
  - NOTES "How sessions differ" gains: "the logbook's pivots: the pivot written down for a run, and with it the
    run's name, may be the wrong one, for any number of a session's runs".
  - generate.py: a run's written pivot is its name's first letter (`logbook` key removed). h4 is renamed so that
    every run carries the other pivot's name: b1–b3 hung on A, a1–a3 on B. The run order is kept, so the data
    are byte-identical to v14 apart from the names (`v15/explore/regen.py` checked this).
  - expected.json: only h4's run keys change.
  - Oracle `assign_pivots(runs, geo)`: still groups runs by rough period, but pairs groups with pivots by
    physics, keeping the pairing whose `pairing_g` is nearer `G_STANDARD` 9.80665. The logbook decides nothing.
    The rough-period pairing g is 9.78–9.82 m/s² against 12.57–13.36 for the other pairing.
  - Oracle worst error is still 0.307 of tolerance. Emulated judge: oracle 6/6; trust-logbook fails 5 tests, on
    h1 (everything) and h4 (g, pivot periods, k); empty fails all 6.
  - estimator_bounds.py: static "pairing" lines (exchanged pairing g 12.5698–13.3824). The logbook-trusted line
    is generalised (h4: g +3.36e-1). Rough lines now carry the pairing g. New wrong rule "logbook majority per
    period group": passes h1, fails h4 on g, pivot periods and k.
    - Re-run in full: every estimator line is identical to v14. Only the 14 logbook/rough lines changed and 23
      were added; CRLF was stripped after the Windows stdout redirect.
  - README updated: difficulty bullet, solution step 3, wrong-method list. Lint PASS, scan 0 problems. Note in
    `v15/upload-note.txt`.
  - Expected p per attempt is about 0.5–0.85. Attempts that also test majority-wrong groups in their own
    synthetic generator will pass.
    - Next lever if 3/3: stand flexure (`v15/explore/flexure.py`). At c = 1–2e-5 m/N it biases g by
      1.2–2.5 × tolerance and changes the amplitude law by up to 8.5e-5 at 0.9 rad.

## Platform updates (every card on T-0610; seen = reviewed and marked seen)

| Time (UTC) | Version | Card | What it said | Action | Seen |
|---|---|---|---|---|---|
| 10-26 (several) | v1–v5 | burg cards | quick checks and pass@3 3/3 | (another task) | yes |
| 10-27 03:51 | v6 | the quick check found something to fix | 2 FAIL: relative paths; tolerance evidence | fixed in v7 | yes |
| 10-27 11:12 | v7 | the quick check did not finish | canary missing in tests/estimator_bounds.txt | fixed in v8 | yes |
| 10-27 11:54 | v8 | the quick check passed | pass@3 started | waited | yes |
| 10-27 12:07 | v8 | pass@3 solved 3 of 3 | too easy | v9 redesign | yes |
| 10-27 17:38 | v9 | the quick check passed | pass@3 started | waited | yes |
| 10-27 19:46 | v9 | pass@3 solved 3 of 3 | too easy, sent back (SBQ) | v10 hardening | yes |
| 10-27 21:36 | v10 | the quick check passed | 31 pass, 3 N/A, novel deferred; extra 5/5 | waited | yes |
| 10-27 22:21 | v10 | pass@3 solved 3 of 3 | too easy, sent back (SBQ) | v11 redesign | yes |
| 10-28 02:00 | v11 | the quick check found something to fix | 36/39, 2 FAIL: stderr cap in `tests/emit.py` contradicts "standard error is ignored"; card's fix: remove the stderr cap (drain and discard), README to list every remaining run_case limit | fixed in v12 | yes (02:07) |
| 10-28 03:10 | v12 | the quick check found something to fix | 37/39, 1 FAIL (AGAIN): run limits ≠ instruction (630 vs 600 s; unstated 64 MiB file cap); fix: CASE_TIMEOUT_SEC 600, disclose the cap, audit all limits | fixed in v13 | yes (03:14) |
| 10-28 04:47 | v13 | the quick check found something to fix | 37/39, 1 FAIL (AGAIN): "may write files only under TMPDIR and HOME" is not enforced (`/tmp` writable); card's fix: confine every program launch in test.sh/emit.py to HOME and TMPDIR, with regression tests for writes elsewhere | v14 drops the claim instead (states only what holds); confinement is the fallback | yes (04:52) |
| 10-28 05:56 | v14 | the quick check passed | 39/39 (33 pass, 1 N/A, novel deferred; extra 5/5); pass@3 started | wait for pass@3 | yes (05:58) |
| 10-28 06:33 | v14 | pass@3 solved 0 of 3 | all three attempts failed; fix an unstated requirement or environment problem, or make it somewhat easier | all three trusted h1's logbook (unstated in NOTES): v15 states the scope | yes (06:48) |
| 10-28 08:35 | v15 | the quick check found something to fix | 37/39, 1 FAIL (AGAIN): a folder named `reduce.py` passes every test although the instruction requires a regular file; fix: validate declared artifacts in `tests/tb4judge.py::unpack` before execution, plus rejection tests for folders, links and oversized files. **Quick-check limit used up** ($15.66 of $15.00, 15 checks): no new version accepted; with the review team; pass@3 so far 3,3,3,3,3,3,3,0 | do not upload; fix kept local; wait for the reviewer's update | yes (08:40) |

## pass@3 analyses

- **v8 (3/3)**: piecewise clock from the sync plus a damped-ODE fit; 5–12 min; errors ~1e-5.
- **v9 (3/3)**: 7m57s, 8m37s and 6m41s. Each attempt found the stall deficits, then ran one joint ODE fit through a
  three-parameter view. Errors were 40–300× inside the tolerances.
- **v14 (0/3)**, card 06:33. Attempts took 22m, 26m and 27m. Zip and extraction in `work/kater-pendulum-gravity/v14/pass3/`,
  digests in `v14/attempts/`, error margins from `v14/explore/margins.py`.
  - All three fail the same three tests (g, pivot periods, k), all on **h1 only**: pivot b 1.8914–1.8931 s,
    g 10.61–10.63 vs 9.82137, k 0.367 vs 0.3489. Each trusted the logbook, which puts b2 on B though the bar hung on A.
    No digest mentions the logbook.
  - Everything else is far inside tolerance (fractions of it on h2–h4: g ≤ 0.025, pivot periods ≤ 0.074, run periods
    ≤ 0.18, k ≤ 0.011, release ≤ 0.12), often tighter than the oracle.
  - Method: each attempt wrote a synthetic generator that samples NOTES' "How sessions differ" limits and validated
    its program on it. So any limit NOTES states gets handled, and a variation NOTES omits gets missed.
  - Verdict: **unfair**. The instruction promises the graded sessions differ "within the limits that NOTES states",
    and NOTES never states that a logbook pivot can be wrong.
  - Every attempt applied the pin (the full rolling EOM, J = k² + h² + 2rc(1−cos θ)) and the CM shift within minutes
    of reading NOTES.
  - All used naive stall detectors (median + 1.5, −1.5 against rate×Δs, round < −1). Those barely bias a
    least-squares period, because the clock fit absorbs the same step.
- **Lesson (v8–v10)**: any effect that NOTES states, or that a forward model can fit, is solved in minutes. What is left:
  - judgments the data alone don't supply (which record to trust);
  - a contract graded on cases the agent never sees.

## Pitfalls (check before every upload)

1. Every shipped text file needs the `harbor-canary GUID` line (v7).
2. instruction.md: runtime paths absolute and in full (v6). Every constraint sentence needs a requirement quote.
   Never promise "no network" unless it is enforced (lint FAILs it).
3. The README tolerance evidence must give numerical bounds from independent valid estimators, rounding included (v6).
   The readme-claims gate needs each claim paragraph to cite a task file that holds one of its numbers (e.g.
   `tests/estimator_bounds.txt`, or a `SESSIONS` value in `tests/generate.py`). E-notation figures don't count.
   Debug it with `python3.13 -I -B work/kater-pendulum-gravity/v11/explore/claims_debug.py tasks/active/<slug>`.
4. No `__pycache__` under `tasks/`: run with `python -B` from the folder root.
5. `tb4 package` refuses when the day's zip exists. Archive the platform zip first. The package date is UTC, so after
   17:00 local the zip is dated the next day.
6. After a generator change, regenerate the data, `expected.json` and `estimator_bounds.txt` together, then re-run
   `work/.../v11/explore/check_oracle.py` and `judge_check.py`, lint and `scan_task.py`.
7. Stalls must not cover a GPS onset; rates near an integer number of frames per second bias the stall sizes.
8. Git Bash rewrites a leading `/` in arguments: pass platform paths without it.
9. Never run anything from inside an extracted pass@3 folder; use `-I` and pass paths as arguments.
10. CRLF: Python text writes and redirected `print` produce CRLF on Windows. Use `newline="\n"` or `sed -i 's/\r$//'`,
    and run `tools/scan_task.py` before every package.
11. emit.py's budget gate flags any literal number in a `timeout=` expression: use a named constant.
12. Pin new pip packages only after checking PyPI for a cp312 manylinux wheel compatible with the numpy pin.
13. Program mode (`RUN_PROGRAM=1`): the quick check wants every enforced limit stated **exactly** in instruction.md
    (v11 and v12 were sent back for this). The limits:
    - `CASE_TIMEOUT_SEC` equals the stated time, interpreter start-up included;
    - the stdout cap; stderr uncapped if the instruction says it is ignored;
    - `ulimit -f` 67108864 bytes per file; empty stdin; environment HOME/TMPDIR/PATH/LANG; leftover processes killed;
    - deliverable a regular file ≤ `max_submission_mb`; `/app/output` tar ≤ `archive_cap_mb`.

    "AGAIN" on a card means the same criterion failed again, possibly for a new reason. It is not a verdict on the
    previous fix. Never state a restriction the harness doesn't enforce (v13: "may write files only under TMPDIR and
    HOME"); state the facts instead.
14. `emit.py`'s pipe loop can't run on Windows; test it with `work/kater-pendulum-gravity/v12/explore/test_emit_win.py`
    (PeekNamedPipe selector).
15. Every variation in a graded session must fall inside NOTES' "How sessions differ" list, because the instruction
    promises exactly that. v14's h1 logbook mislabel wasn't listed, and pass@3 came back 0/3 with every attempt
    failing that one thing.
    - The target model writes a synthetic generator from that list and validates against it, so it handles every
      listed variation and misses every unlisted one.
    - Difficulty therefore has to come from the edges of a stated scope (v15: "any number" of runs, h4 all of
      them) or from physics its generator would leave out.
16. On Windows, `python script.py > file` writes CRLF. Strip it with `sed -i 's/\r$//'` before scan and package
    (the evidence file in v15).
