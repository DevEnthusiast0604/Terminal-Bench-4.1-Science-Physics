# Briefing: the main points of every log

Study this before any work (user, 2026-11-03). It condenses `logs/STATUS.md`, the task logs, `work/physics-task-state.md`
and the user's standing rules; the logs keep the full evidence and paths. Times are UTC.

Points are added with their date and never rewritten (user rule, 2026-10-29). When a point replaces an earlier one, the
new point says which. Add a point whenever a log entry teaches something that changes how the next session works: a new
user rule, platform behaviour, difficulty lesson or pitfall.

## Read order (a few minutes)

1. This file.
2. The newest row of `logs/STATUS.md` for the active task.
3. In the active task's log, only: the last "State now" entry, the last "Version history" entry, any "Platform updates"
   row with Seen = no, and the last "pass@3 analyses" entry. Open older entries only when a point here sends you there.
4. A physics task: `TB4_PHYSICS_PROMPT.md`, then the newest entries of `work/physics-task-state.md`.

## The user's rules

- Single agent: no sub-agents, forks or workflows. Everything runs in the foreground, except the pipeline poller (a
  `tools/supertasker.py status` loop), the one background job allowed (2026-10-30).
- **No local tests, ever** (2026-11-02, made absolute 2026-11-03). No oracle runs against `expected.json`, no timing
  runs, no reruns at tighter settings or higher order, no evidence units, no comparing approaches by running them. After
  an edit: lint, scan, package, Upload the fix. The one exception is computing new `expected.json` values when a change
  needs new answers: tell the user first, then run only the generator.
- Upload with no note (2026-11-02).
- Logs are append-only: add rows and dated entries, never edit earlier ones (2026-10-29).
- Log every update card as soon as it appears (Seen = no). Review it, mark it seen with `tools/supertasker.py mark-seen`
  and log that.
- Watch the pipeline all the time. When a check fails, fix the task and resubmit, and repeat until the whole pipeline
  passes.
- Target pass@3: 1–2 of 3. At 3/3 make it harder; at 0/3 first look for an unstated requirement or an unfair check.
- A hardening round should take 30 min to at most 2 h of work (2026-11-03). v8's took 6 h 8 min (see "Time per round").
- Physics tasks follow `TB4_PHYSICS_PROMPT.md` and keep `work/physics-task-state.md` current. At most three revision
  cycles per session; stop at qualification, an unresolved blocker or a pending result.
- At most five uploads per day, Upload the fix included.
- DAS: paste each new P3 ID into the task's own DAS ID (chapman: 3972746). Never reuse a P3 ID, never upload a zip to
  DAS. DAS 3965796 (kater) is spent: never use it again.
- README "Relevant experience" describes the author's real background: the user confirms the wording, so reuse the
  confirmed text.
- `tools/humanize.py` sends text off this machine: use it only when the user asks.
- Security: never read, copy or package `.supertasker-profile/`. No host paths in a task or its evidence. The author's
  email appears only in `task.toml`. Leave Chrome ports 9222 and 9223 alone (ours is 9224).

## Platform facts

- Cards: "the quick check passed" (pass@3 then starts on the same files), "the quick check found something to fix",
  "the quick check did not finish" and "pass@3 solved N of 3". At 1–2 of 3, Updates issues the P3 ID.
- The quick check is a static stage, 35 criteria and 5 extra checks. It can run without the Docker controls. Verdicts of
  NOT_PROVIDED that cite missing oracle, nop or cheat records go to the reviewer and don't block.
- Waits on T-0851, upload to quick-check card: 2 h 21 min (v4), 3 h 36 min (v3), 9 h 5 min (v7), 21 h 56 min (v5,
  18 h 25 min of it in the queue), about 33 h (v6, a job stuck "running" that finished by itself). Quick-check pass to
  pass@3 card: 1 h 12 min (v7), 3 h 38 min (v4), about 5 h (v3).
- pass@3 runs on Sol 6.1. Each attempt takes 21–65 min; the verifier then takes 5–38 min for ten program runs.
- **Quick-check budget: $15 per platform task.** T-0610 (kater) reached $15.66 after 15 quick checks. The platform then
  refused new versions until a reviewer acted, and the task was withdrawn. T-0851 has had 8 quick checks (v1–v8); the
  task page shows the spend.
- An identical zip is blocked while its check is queued or running, and after it ends. Any file edit voids every
  earlier check, pass@3 included. A stuck job can't be retried from here: the user reports it to the team lead.
- Paths per job J: `gate/task/J.zip`, `job/J/report`, `gate/criteria/J.md`, `gate/extra/J.md`, and the full pass@3 zip
  `gate/full/J.zip`. `links T-ID v<N>` lists them. Give `fetch` each path without its leading `/`.
- Criteria lessons:
  - `solvable` compares `expert_time_estimate_hours` with "an expert knowing the approach can implement it in a few
    hours". 16 h failed (chapman v5); 6, 10 and 12 h passed. Count the implementation only, not finding the route.
  - `instruction_concision` failed a sentence that only listed the installed libraries (chapman v2). Naming them inside
    the program's runtime-limits sentence (v4 onward) passed.
  - Program mode: state every enforced limit exactly. That means the time limit with start-up included, the stdout cap,
    the 67108864-byte file limit, empty stdin, the four environment variables, killed leftover processes, and the file
    and archive caps (kater v11–v13). Never promise a restriction the harness doesn't enforce. "AGAIN" on a card means
    the same criterion failed again, perhaps for a new reason.
  - Every shipped text file except JSON and dotfiles needs the canary line, generated evidence included (chapman v1
    failed on `tests/checks.txt`).
  - Name each `grading.json` deliverable with its `/app/output/` path, or the wrong-answers control has nothing to
    mutate. With a program deliverable that control prints "no JSON/CSV deliverable found … skipped": expected, not a
    defect.

## Difficulty lessons

- The target model solves in minutes anything it can put into a forward model and fit (kater v8–v10). It also solves
  any fully specified computation whose parts it can check itself, which the guide calls "applying a general method"
  (chapman v4).
- Given one disclosed case, it specialises to it and converges it with self-checks (chapman v3: 3/3, errors 1000×
  inside). Grade a stated range on hidden cases instead.
- It builds a synthetic generator from the stated scope and validates against it. So it handles every stated variation
  and misses every unstated one: an unstated variation gives 0/3 and is unfair (kater v14).
- It tests the corners of the stated ranges, exactly the corners (chapman v7).
- Brute force beats slow-convergence traps. At v6, raw P = 64 was already inside the tolerance. At v7 the agents reached
  100–160 Sonine indices in 1–2 minutes. A Lorentz-limit probe showed that even an infinite mass ratio needs only about
  160–200, so wider ranges can't defeat brute force.
- The headroom shows how close they came. The worst errors were 1000× inside the tolerance (v3), 30–2000× (v4), 6× (v6)
  and 2.5× (v7, 0.40 of the tolerance).
- Not valid difficulty: volume, low timeouts or time pressure, incidental precision, tighter tolerances, extra
  requirements or formulas.
- What is left: judgment the data can't supply, physics that a generator built from the stated scope would leave out,
  and methods that look converged while being wrong. v8 tests the last one: narrow shape resonances that a fixed energy
  grid misses (result pending).

## Time per round

- v7: 10:23 to 15:46 on 11-02 (5 h 23 min). v8: 02:16 to 08:24 on 11-03 (6 h 8 min):
  - analysis and choice of design, 56 min;
  - quantum reference built and checked, 2 h 21 min;
  - speed, ranges, hidden sets and the answers, 1 h 53 min (the answers took 185–470 s per set on 6 workers);
  - evidence, oracle, task files, packaging and upload, 58 min.
- Most of it was local checking, and building after the result arrived, while the platform wait (hours) went unused.
- Proposed on 2026-11-03, waiting for the user's OK. None of it is in use yet:
  - build the next version during platform waits, kept in `work/` so the check now running stays valid;
  - a one-command pass@3 analysis;
  - an agreed order of hardening options;
  - one config file for the ranges and hidden sets, which a script writes into the documents;
  - a one-command release with templated log entries;
  - the generator allowed to run in the background during waits.
  Working while a result is pending departs from `TB4_PHYSICS_PROMPT.md`, so it needs that OK.

## Before every upload

1. Move the zip now in `deliveries/` to `deliveries/archive/<slug>/<slug>-v<N>-<UTC date>.zip`. `tb4 package` refuses
   when that day's zip exists, and it dates the zip in UTC.
2. Run `tb4 lint tasks/active/<slug>` (0 FAIL) and `python -I -B tools/scan_task.py tasks/active/<slug>` (exit 0).
   `grep -L -r "harbor-canary GUID" tasks/active/<slug>` may list only `*.json` and `.gitattributes`.
3. Run `tb4 package`, then `python -X utf8 -I -B tools/supertasker.py upload-fix T-ID <zip>` with no note. Log the
   digest and start the poller.

Also check:
- No CRLF: Python text writes and redirected `print` write CRLF on Windows, so use `newline="\n"` or
  `sed -i 's/\r$//'`. No `__pycache__`: run `python -B` from the folder root. No host paths.
- README: every number a claim uses sits in a cited task file; one sentence states the key realization; no pass rates
  or model names.
- Every variation in a graded case lies within what the instruction states. Every constraint sentence has a
  requirement quote.
- `emit.py`: a named constant in every `timeout=`. One emit pass runs all cases with a shared HOME and TMPDIR, so say
  "writable", not "empty". The emit cap covers N × `CASE_TIMEOUT_SEC` plus the drains.
- Pin a new pip package only when it has a cp312 manylinux wheel that fits the numpy pin.

## Windows and tools

- The Bash tool sends any call over 600 s to the background, whatever timeout it is given: split long runs.
- Git Bash rewrites a leading `/` in arguments.
- A heredoc holding Python `u''` breaks: write the script to the scratchpad with Write instead.
- `python3` is the Microsoft Store stub; `tb4` uses uv's `python3.13`; plain `python` is 3.12.10.
- `emit.py`'s pipe loop doesn't run on Windows.
- pass@3 downloads: extract under `work/<slug>/v<N>/pass3/x/`, never run anything inside, read with `-I`, and digest
  with `tools/trajectory_digest.py`.

## Tasks so far

- burg-spectral-estimation (T-0610 v1–v5): v2–v4 passed the quick check but were 3/3; withdrawn 2026-10-27 01:10.
- kater-pendulum-gravity (T-0610 v6–v15, DAS 3965796): pass@3 3, 3, 3, 3, 3, 3, 3 and 0 of 3; the quick-check budget
  ran out; withdrawn 2026-10-28 11:08.
- chapman-enskog-transport (T-0851, DAS 3972746, active; no P3 ID yet):
  - v1–v2: harness fixes (canary, library sentence);
  - v3: one disclosed gas, 3/3;
  - v4: a program for the whole family, graded on ten hidden pairs, 3/3;
  - v5: binary Kihara mixture with αT, `solvable` FAIL on the 16 h estimate;
  - v6: v5 with 6 h, 3/3;
  - v7: mass ratios up to 100, 3/3;
  - v8: quantum mixture, uploaded 2026-11-03 08:24, pending.
- v8 in brief:
  - Spin-0 bosons, `transport.py A R L X T`, with Λ* 0.8–2.8 and T* 0.2–0.6. Cross sections come from partial-wave
    phase shifts, symmetrized for like pairs.
  - Without resonance handling, hidden sets k01–k05 miss by 26–225 tolerances; k06–k10 are clean.
  - The oracle is `solution/transport.py` (FAST settings, 20 Sonine terms); the reference is `tests/generate.py`
    (P 24).
  - v8 was cycle 3 of 3 of the session that built it. At 1–2 of 3, paste the P3 ID into DAS 3972746. At 3/3 or 0/3,
    analyse the pass@3 zip and report.
- chapman-enskog-transport (T-0851) was withdrawn on 2026-11-05 23:50 at the user's request, with no P3 ID: all seven
  pass@3 runs were 3 of 3. No task is active; see Points added 2026-11-05 (23:51).

## Approved workflow (2026-11-03 12:15)

The user approved the four changes ("okay, that workflows is okay"). This replaces the "waiting for the user's OK"
point under "Time per round".
- Build the next version during platform waits, in `work/<slug>/v<N+1>/`, so the check now running stays valid. This
  relaxes `TB4_PHYSICS_PROMPT.md`'s stop on a pending result.
- The generator that computes `expected.json` answers may run in the background during waits, like the poller.
- Hardening options in this order, taken without asking; the pass@3 analysis decides which applies:
  1. put all hidden cases where the central challenge bites;
  2. extend a stated range into a harder region;
  3. new physics, only when the agents handled the current challenge cleanly.
- Short templated log entries, still append-only.

Tools for it (run from the folder root):
- `python -X utf8 -I -B tools/pass3_report.py work/<slug>/v<N> --job J --rtol 2e-5 --atol thermal_diffusion_factor=1e-6 --keywords a,b`:
  fetches `gate/full/J.zip`, extracts it safely, digests each attempt, copies the final programs (never runs them)
  and writes `pass3/summary.md`: rewards, tests, times, cost, the worst error per case against the tolerance,
  controls, the provenance digest, keyword counts.
- `bash tools/release.sh --check <slug>`: the pre-upload checks (no `__pycache__`, scan, canary in every non-JSON
  file, lint). Moves and sends nothing.
- `bash tools/release.sh <slug> <T-ID> <N> "<what changed>"`: the checks, then archive the old zip, package, Upload
  the fix with no note, and append the log, board and physics-state entries (`tools/log_release.py`).
- `python -X utf8 -I -B tools/poll_pipeline.py <T-ID> 43200 180` (Bash `run_in_background`): the pipeline poller;
  it exits when an unseen card appears.

## Pitfalls added 2026-11-03

- v8 shipped `tests/checks.txt` without the canary line: it was assembled from caches and the canary grep was
  skipped. `tools/release.sh` now refuses to package such a file, and `tests/checks.py` prints the canary first.
- (12:25) Don't cancel a queued check, even when the version under check has a known defect: wait for its result,
  then fix and upload (user: "wait until pipeline result ... there is no need to cancel").
- (20:30) Windows paths over 260 characters fail here (no long-path support): `tools/pass3_report.py` extracts with the
  `\\?\` prefix, which fixed it. Its first run, on a copy of v7's download, took 4 s and matched the v7 analysis
  (worst error 0.40 of the tolerance, k01 αT).

## Points added 2026-11-04

- (16:50) Waits: v8, upload to card 12 h 26 min (a static failure); v9, 19 h 50 min to "the quick check passed". The
  watcher's 12 h limit ran out once on each; restart it and keep waiting.
- (16:50) The quantum design (v9) passed its first criteria run: 33 pass, 0 fail, `novel` deferred to the full review.
  pass@3 started 11-04 16:45.
- (21:35) v9 pass@3 3/3 (worst 0.010–0.022 of the tolerance, agents 28–72 min). The instruction handed over the
  like-pair formula, so the task was a fully specified computation. Every numerical trap in it (narrow resonances,
  partial waves, Sonine order) was anticipated, located and checked. Lesson: a formula given is a formula applied.
  v10 states the physics instead (species, nuclear spins, levels, conserved internal states, exchange symmetry) and
  leaves the like-pair weights to be derived. The classical limit, rigid spheres and convergence checks can't test
  those weights.
- (21:35) A design change voids generated evidence such as `tests/checks.txt`, and the no-local-tests rule forbids
  rerunning it. Drop the evidence and cite code, CASES and `expected.json` in the README instead.
- (22:15) Generator stalls: a `multiprocessing.Pool.imap` waits forever when a worker dies silently (v10's first run, 21:27, no
  traceback). Watch the run with a Monitor that flags 8 min without a new stage line; stop it and restart it with the
  same `QMIX_CACHE`, which resumes at the stalled stage (v10: k02 passed in 33 s on the restart, all ten sets in 24 min).

## Points added 2026-11-05

- (00:05) v10's quick check failed `verification_explanation_quality`: without `tests/checks.txt` the README had no
  quantified reference-error or convergence evidence. A README that only names the settings and the tolerance fails;
  keep measured evidence (Sonine orders, settings, energy grid) even when a design change forces a new computation.
  The user approved a short evidence run for this (00:10).
- (00:44) The pool stalls have a cause: on this machine a spawned worker can die at its first task with
  `OSError: [WinError 6] The handle is invalid` in the queue's `get`, so `multiprocessing.Pool` waits forever.
  `tests/qmix.py` `pmap` now uses `ProcessPoolExecutor` and runs a broken map in this process.
- (04:03) `verification_explanation_quality` wants two things beyond the reference's own convergence (v11 failed
  again with only [P] and [step]): checks of each part against independent methods (v9's [bessel], [ode],
  [classical], [kernels], [isotropic]: 3 min in one process, no pool), and a paragraph saying what the checks leave
  out and why the band leaves room for other correct methods. Avoid "passes" in README prose: lint's readme-claims
  flags it as a measured claim without a receipt.
- (10:58) The 00:44 `ProcessPoolExecutor` change to `pmap` was reverted. `pmap` is the plain Pool again, and
  `QMIX_WORKERS=1` maps in-process. `qmix.case(..., only=pair)` caches one pair's stages, and stage files are written
  to `.part` and then renamed. `work/chapman-enskog-transport/v13/explore/run_stages.py` runs one serial process per
  pair (then one per set for the brackets), six at a time, and stops them all at a deadline under 600 s. v13's six
  new equal-mass sets took 16 min in three foreground calls, with no stall.
- (10:58) A `python -c` edit with `\\n` in a replacement string writes a real newline into the file. v13's oracle got
  an unterminated string, and `tb4 lint` does not catch that because it does not parse `solution/*.py`. Parse every
  `.py` with `ast.parse` before release; `tools/release.sh` now does. Heredocs whose text holds quotes or backticks
  break in this Bash tool ("unexpected EOF"): write such edit scripts to a file in `work/<slug>/v<N>/explore/`.
- (10:58) v13's sharpest check is `k03` (H2, Λ* 2.4, T* 0.6). There α_T = 2.6e-3, and its two terms in λ (the
  diffusion law and the Dufour term) move λ by 26.6 tolerances: dropping the coupling, or keeping only one half,
  fails. At the other sets the coupling stays under 0.16 tolerances.
- (12:22) v13's quick check failed instruction_concision on a sentence that an earlier design needed: "H is the atom whose nucleus is a proton, D a deuteron" was required while HD was a species, and became hand-holding once only H2 and D2 remained. After a design change, re-read the instruction for sentences the old design needed.
- (15:05) A Cloudflare "502: Bad gateway" page means the platform itself is down (11-05 from 14:53), not a sign-out; `supertasker.py status` then finds no task view. `tools/poll_pipeline.py` now keeps polling through gateway errors (502/503/504) and prints when the outage starts and ends; it still stops after three other misses (a real sign-out). Don't touch the session for a 502: check `http://127.0.0.1:9224/json/version`, look at the page title, wait.
- (15:05) In edit scripts written through a Bash heredoc, a regex `\b` can arrive in the file as a real backspace byte (0x08): `tools/poll_pipeline.py` got two. After such an edit, check the bytes (`od -c`, or `grep -c $'\x08'`).
- (16:04) The 11-05 outage also showed "Cloudflare Tunnel error" pages (the platform's tunnel to Cloudflare down) between 502s; the poller counts those as outage too since 16:04. A "TB4 queue" title without the task view is the app's shell, which could also be a sign-in page, so it still counts as a miss.
- (20:30) v14 pass@3 was 3 of 3 (agents 38-98 min, worst error 4e-4 of the tolerance). The local-equilibrium conversion cost them nothing: they put the temperature dependence of the equilibrium composition into the standard Chapman-Enskog vector source, which carries the Dufour and thermal-diffusion coupling automatically. Any effect that is only a changed source or weight in the standard linearized problem is free for them. Finite rates break this: v15 (uploaded 20:27, upload 5 of 5 on 11-05) grades a gap conductivity between non-converting walls (coupled reaction-diffusion layer) and a bulk viscosity from the composition lag (tau at fixed temperature; frozen heat capacity 3/2).
- (20:30) Agents may install a compiler in the agent container, compile a native kernel and embed it in the deliverable (v14 a3: 12.8 MB transport.py with a base85 zlib blob). Program sizes of 3-13 MB are normal now; they compute each set at run time.
- (23:23) `solvable` failed v15 on the README sentence "An expert who already knows this route writes it in about nine hours" (job 18258), while `expert_time_estimate` passed the same 9. Keep the estimate at what has passed (6 h in v6-v7, 8 h in v9-v14) and phrase it as implementing a known route; a new output's derivation adds little implementation time.
- (23:51) The user stopped all work ("please stop everything"), then asked to withdraw every task. T-0851 was withdrawn at 23:50 with `tools/supertasker.py withdraw T-0851 "Withdraw the task"` and an empty note. It was then archived: the sources are the unsent v16, and the zips are in `deliveries/archive/chapman-enskog-transport/`. The withdraw dialog says a withdrawn task keeps its history and can take a new version later. Both tasks on the account (T-0610, T-0851) now show WITHDRAWN.
- (23:51) The Submit page (11-05 23:49) shows the account's limits: Tier Starter, "2 of 2 new tasks left today" ("New versions of your tasks don't count"), "Quick checks left this week: 72" and "pass@3 runs left this week: 968", reset Monday Nov 9 00:00 UTC. It offers toolkit 3.3.2 (2026-11-01), while `~/tb4/tb4-starter-pack` here is 3.3.0. Nobody tested whether a per-task quick-check budget (kater was refused after its 15th check) also applies.

## Points added 2026-11-06

- (00:29) `TB4_PHYSICS_PROMPT.md` is not needed (user: "No need to TB4_PHYSICS_PROMPT"). This replaces every point above that sends a physics task to it: step 4 of the read order now starts at `work/physics-task-state.md`, and the limits the prompt set (three revision cycles per session, the stop on a pending result) no longer apply.
- (00:45) User: "generate high difficult physics task and submit from now on" and "also watch the pipeline. try to re-work until it pass pass@3 step". This replaces the 11-05 23:51 stop: work on a new task, and rework until a P3 ID comes. "New DAS task id is 4011092": spent only by a P3 ID on this task.
- (02:02) New task `gamma-decay-scheme` submitted as T-1383, DAS 4011092 (upload 1 of 5 on 11-06): a level scheme from a moving-tape γγ run, data file, `RUN_PROGRAM=0`. Design and traps are in `logs/gamma-decay-scheme.md`. The design bet: inference from messy evidence, with NOTES promising nothing about the records, because every fully specified computation was solved 3 of 3.
- (02:02) The Toolkit is 3.3.2 on the platform (installed here: 3.3.0). The template is identical and the lint differences only relax rules, so the installed lint is enough. A copy is in `work/gamma-decay-scheme/kit/`.
- (02:02) `tb4 lint` crashes with UnicodeEncodeError (cp1252) once a lint line quotes a Greek letter. Run it, and `release.sh`, with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8`.
- (02:02) `tests/generate.py` of this task also runs the reference on the shipped data and writes `tests/checks.txt`, so it takes about 80 s and counts as the allowed generator run, not as an oracle run.
- (02:12) Correction: the user's first request for this task came at 00:32 (transcript). The stamps 00:45 in this file's point and 00:30 in `logs/gamma-decay-scheme.md` were my estimates.
- (02:59) `discoverable` and `oracle_investigates` read the task's own evidence: gamma-decay-scheme v1 failed because `tests/checks.txt` and the README documented a 17-level scheme the data do not exclude, while the instruction said only "every level". When an inverse problem's solution is not unique, state the selection rule in the instruction (v2: "the one with the fewest levels"). A quick check on this data task took 50 min.

## Points added 2026-11-09

- (01:58) User: "download the updated Toolkit". The platform is now the **TB4.1 Queue**, with toolkit 3.7.0 dated
  2026-11-08. I downloaded it with `supertasker.py fetch gate/kit/download` to `work/toolkit/20261109/kit.zip` (1012516
  bytes, extracted to `x/`) and installed it at `~/tb4/tb4-starter-pack` (`tb4 --version`: 3.7.0). The old 3.3.0 is kept
  at `~/tb4/tb4-starter-pack-3.3.0`.
- (01:58) TB4.1's My tasks is empty. T-1383 and its queued v2 quick check are gone, `/task/T-1383` answers "not found",
  and Updates and To do are empty. The poller last ran on 11-06 and stopped at 12:09 after three status time-outs, so
  nothing was watched from then until 11-09. The Submit page (11-09 01:55) shows 2 of 2 new tasks left today, 66 quick
  checks and 79 pass@3 runs left this week, reset Monday Nov 16 00:00 UTC. The Workflow tab says:
  - only the first task needs a DAS Task ID;
  - the platform links a P3 ID pasted into DAS by itself, within about 10 minutes;
  - a quick-check flag can be disputed from the report, with a reason.
  Its section "Hard for the right reason" is saved in `work/toolkit/20261109/workflow-tab.txt`.
- (01:58) TB 4.1 rules in kit 3.7.0:
  - Every Python dependency comes from a committed lock: `environment/locks/pyproject.toml` plus `uv.lock`, made with
    `uv lock --directory environment/locks`. Never `pip install` in a Dockerfile.
  - uv 0.10.8, the version the template's Docker build uses, is installed here with `pip install --user`
    (`%APPDATA%/Python/Python312/Scripts/uv.exe`).
  - `tests/locks/judge/` is copied from the template unchanged.
  - The template's `tests/test.sh` gained root-only checks, so a task takes the new copy.
  - README metadata: Author as `Name (email)`, Category alone (`Science`), Tags as `<code>`. These are lint warnings,
    not failures.
  - The kit's own `uv.lock` files carry no canary line.
- (02:02) gamma-decay-scheme is now **T-0020** on the TB4.1 Queue: submitted 02:02 with DAS 4011092 (upload 1 of 5 on
  11-09; 1 of 2 new tasks left today), and its quick check started at once. Local v3 is the platform's v1. `/task/T-0020`
  works with `supertasker.py status`, and the poller watches T-0020.
- (02:02) On TB4.1 the top tabs are buttons, and a goto to `#submit` keeps the last tab shown. `supertasker.py submit`
  now clicks Submit first, checks that the check kind (`#kind`) is "Quick check (35 + 5)", and stops if a contributor
  e-mail field (`#contrib`, hidden so far) shows. `tools/release.sh` exempts `uv.lock` from its canary check.
- (02:02) README Author line: TB 4.1 wants `Name (email)` to match task.toml, while the user's rule keeps the email in
  task.toml only. v3 ships without it (a lint WARN) and the user has been asked. If the quick check flags it, wait for
  their answer.
- (02:48) T-0020's quick check (job 137, TB4.1's first for this account) passed all 40 criteria in 43 min (02:02 to 02:45). `task_readme` passed with the README Author line without the email, so that question does not block; pass@3 started at once.
- (14:05) The user paused background work: "pls stop background working at the moment. I will let you know when needed". The T-0020 poller was stopped. Don't restart it, or start any other background run, until the user says so. Its last poll (14:04) got the TB4.1 sign-in page, so check the session before resuming.
- (17:22) The user resumed work ("please continue working on from now on. just watch the pipeline as well"); the 14:05 pause is over.
- (17:22) The platform restored the old data: T-1383 (gamma-decay-scheme, 3 versions), T-0851 and T-0610 are back, `/task/T-0020` says "not found", and the 02:02 upload is T-1383 v3 (job 19128). Local and platform versions match again. v3 came back from pass@3 at 14:37 as TOO EASY (3 of 3), so it is a hardening round. The page offers kit v3.8.2; counters: 2 of 2 new tasks left today, 74 quick checks and 1028 pass@3 runs left this week. The session was signed in at 17:20, so the 14:04 sign-in page came from the switchover.
- (17:59) v3 pass@3 (job 19128): 3 of 3, all exact in 7 to 13 min. Its traps fell to standard tools; the shortcut all three took was setting the 511 keV peak aside by energy. v4 adds a real 511.00 keV transition there (3092.6 -> 2581.6 keV, I 0.853), shown by the narrow part of the production peak and by its gates. Instruction, grader and requirements are unchanged; the data, `expected.json`, `checks.txt`, `generate.py`, `solve.py` and README changed.
- (17:59) Kit 3.8.2 is installed at `~/tb4/tb4-starter-pack` (download in `work/toolkit/20261109-382/`; 3.7.0 kept as `~/tb4/tb4-starter-pack-3.7.0`). Its lint fails a missing lockfile (3.7.0 warned; `TB4_STANDARD=4.0` makes it advice) and catches placeholder paths such as NN or NAME. v3 and v4 lint PASS under it.
- (17:59) TB4.1 task page: the Upload-the-fix dialog keeps `#ru-file`, `#ru-note` and `#ru-go`, and a separate `#ask` dialog ("Why upload it anyway", required) exists. When the platform is overloaded every page is a JSON error ("the platform is busy: try again in a few seconds") and `status` reports no task view: wait, it is not a sign-out.
- (18:02) v4 is up: T-1383 v4, IN REVIEW, quick check queued at 18:02 (upload 2 of 5 on 11-09, no note; digest `eebfdfcc…8e47`; v3's zip archived as `gamma-decay-scheme-v3-20261109.zip`). The poller watches T-1383 again.
- (18:02) `supertasker.py upload-fix` on TB4.1: update cards carry "Upload the fixed task" buttons, so it now clicks the task view's one exact "Upload the fix" button, and it stops unanswered if the platform's "Why upload it anyway" dialog (`#ask`) opens. `release.sh` stopped at the upload this time (the old click found three buttons): the zip was packaged and v3 archived, so the upload and `log_release.py` were run by hand rather than running `release.sh` again, which would have archived the new zip as v3. CLAUDE.md now says so.
- (19:07) Outage pattern (18:55 to 19:06): the app's shell (title "TB4.1 Queue") without the task view for three polls makes the poller exit 2 although the session is fine, and the platform may then stop answering for a few minutes. Before suspecting a sign-out, ask the root without the session: `curl -s -o /dev/null -w "%{http_code}" https://queue.supertasker.ai/` gives 401 when the platform is up and 000 or 5xx when it is down. Wait for 401, then run `status`, then restart the poller.
- (01:54) A TB4.1 card titled "the quick check did not finish" can hide a real static FAIL: v4's (job 19370) was `check-task-fields.sh` failing the README's Author line without the email. Always open View report (`/job/J/report`) before treating such a card as a platform fault. The README metadata block must match task.toml as text, Author as `Name (email)`; this conflicts with the rule that the email appears only in task.toml, which is the user's to settle.
- (01:58) User, 2026-11-10 01:56, on v4's static FAIL (job 19370): "Add it, upload again". The author's email now also goes on the README's Author line, `- **Author:** Name (email)`, built from task.toml's author_name and author_email (TB 4.1 `check-task-fields.sh`; kit 3.8.2's template and example do the same). It stays out of every other file: `tools/scan_task.py` allows task.toml's own address on that one README line only. This replaces the rule that the email appears only in task.toml, for every task under TB 4.1.
- (08:10) v5 pass@3 (job 19705): 0 of 3. All three dropped 511 keV by energy as a room line before any analysis; a2 and a3 were otherwise exact. Judged fair (nothing unstated; the data show the line). v6 adds one sentence to the instruction, "A transition can share its peak with radiation of another origin, whatever the peak's energy.", bound as R13; the intensity (the broad part is mostly the parent's own pair production) and the five decoy differences still decide. Data and answers unchanged.
- (12:39) User: "There is no need to submit on DAS automatically. I will do it." The user pastes each P3 ID into DAS. Never open, fill or submit a DAS page (the platform's "DAS task N" link goes to `linkedin.com/ai-trainer/tasks/...`); at 1 or 2 of 3, tell the user the P3 ID and the DAS ID. This replaces "paste each new P3 ID into the task's own DAS ID" as an action of mine. Before the message arrived, one read-only probe had opened the DAS page of T-1383 in the debug Chrome; it ended with "Target page, context or browser has been closed" before reading anything, typed and clicked nothing, and left no tab (CDP list: platform tabs only).
- (12:42) gamma-decay-scheme QUALIFIED: v6's pass@3 2 of 3 (job 20055), P3 ID P3-6AEE-4ACB-FA2A, passed to the user for DAS 4011092. a3 lost only the 1489.6 keV ground-state line, taken as a pure sum peak. The full review runs on the same files as the platform's v7 (job 20271): a full review adds its own version row. Don't upload while it runs. If it sends the task back, mind the numbering: the platform's next upload is v8, and `release.sh` names the archived zip v<N-1>, so N=8 would archive the v6 zip as v7.
- (14:12) A full review can end in "A reviewer decides next" with items a person settles (TO CHECK on the card). The report page `/job/J/report` shows each failed check cut to about 200 characters on the server; there is no fuller view to fetch. v6's easing sentence drew `answer_leak.no_answer_leak` (critical): an instruction sentence that states the task's central realization counts as a leak even when it names no case. Ease a 0 of 3 in a way that leaves the realization to the evidence.
- (14:36) New physics task `rv-planet-census`, **T-1519** (DAS 4040198), submitted 14:33 at the user's request of 2026-11-10 ("build new high difficult science/physics task and submit with DAS task ID 4040198"). The gamma pattern: data-only inference (`RUN_PROGRAM=0`) with several independent expert traps; `tests/generate.py` writes the data, expected.json and checks.txt from an invented system and stops unless the reference lands inside every band. Its instruction carries no hint sentence (see 14:12). `tools/poll_pipeline.py` takes comma-separated T-IDs, but two pollers must never watch the same task: each `status` reloads that task's tab.
- (14:36) Two sessions can work in this folder at once: on 2026-11-10 one handled gamma (T-1383) while another built rv-planet-census. Before killing a poller, read its command line (`ps -ef | grep poll_pipeline`) and the newest log entries: a poller another session started is that session's to stop. `supertasker.py submit` takes the first platform tab, which can be a tab a poller reloads, so the first submit ran through `work/rv-planet-census/v1/explore/submit_newtab.py` (the same submit in a tab of its own, closed afterwards).
- (14:36) A reference that agrees once can still hang on a fragile fit. In rv-planet-census run 3 a transit fit started from the box search's mid-time (12 minutes late) and settled on a wrong chord (radius +9.3%). Probe the fit behind any graded number whose error sits near its band before trusting the band (`work/rv-planet-census/v1/explore/probe_b*.py`).
- (18:08) A full review sent T-1383 back: (1) an instruction sentence that states the task's central realization is an answer leak even when it names no case; (2) a grader that checks `from_keV`, `to_keV` and `energy_keV` each on its own accepts an entry whose fields disagree with each other by up to three tolerances; test the relations between reported fields, not only each field. Easing after a 0 of 3 must go through the data's evidence, never the instruction's words.
- (20:39) `work/physics-task-state.md` holds one '# ' section per task, so its end is the newest task's section only.
  `tools/log_release.py` appended there and put gamma's v8 entry under rv-planet-census (11-10 18:17); it now
  inserts at the end of the slug's own section. Add hand-written events the same way, not at the file's end.
- (21:02) rv-planet-census QUALIFIED: v1's pass@3 2 of 3 (job 20397), P3 ID P3-DE0E-7F4D-56A1, passed to the user for
  DAS 4040198; the full review runs as the platform's v2 (job 20848). Every designed trap fell in all three
  attempts (8 to 11 min): phase coherence between two spectrographs, secondary-eclipse vetting, one transit tied to
  an eccentric orbit, a stated dilution. The one failure was a precision edge (b's radius +9.3% against 8%). For
  Sol 6.1 these exoplanet moves are routine: a harder census needs evidence that standard steps get wrong.
- (21:06) `tools/pass3_report.py` now runs on a data task too: it extracts, digests and copies each attempt's output and
  skips the per-case table. Compare the answers with the task's own reader: `tools/scheme_report.py` (gamma),
  `tools/census_report.py` (rv-planet-census; it names the signal behind every wrong or extra period).
- (23:16) dhva-fermi-surface (DAS 4034278, new, built 11-10) applies rv's precision lesson before upload: its
  generator runs the reference on the shipped draw and on three further noise draws as parallel subprocesses
  (one CPU each; about ten minutes together) and a textbook route beside it, and writes both to checks.txt.
  The mass band went from 10% to 15% when the weakest orbit scattered by up to 7% over the draws and the textbook
  route was off by up to 8.5%; the band still rejects every wrong route checks.txt shows. Set a band from such a
  spread, not from the reference's one result. Its central trap follows the 21:02 point: an orbit 5 T above a
  harmonic, inside every cold spectrum's resolution, so frequency-only classification and peak-height masses
  both go wrong.
- (00:09) The 511 keV line's strength switches whether Sol 6.1 looks at the annihilation peak at all: I 0.853 gave 0 of 3 (the peak set aside by energy), 4.41 gave 3 of 3 (found by coincidences). Harden through what the attempts then do with the peak, its intensity, rather than through whether they notice it.
- (00:29) After any generator run, read `[placement search]` in `tests/checks.txt` before the README: the count at the fewest levels must be 1, or the instruction's fewest-levels rule leaves a tie (the reviewer's point on v7). In gamma-decay-scheme v9 a noise change alone opened one, through the reference's doublet logic; the fix went into `solve.py`, not the seed.
- (06:37) gamma-decay-scheme v9 qualified at 1 of 3 with two different traps: one attempt set the 511 keV line aside with the room lines (I 2.99), one rejected the sub-threshold isomer step. The attempts that noticed the 511 keV line all separated it from the broad annihilation radiation, so its shape trap adds little on its own; the noticing and the isomer traps carry the difficulty.
- (18:34) pass@8 runs on Astra 6 and is far stronger than Sol 6.1 on pass@3: gamma-decay-scheme v10 (Sol 1 of 3) went 8 of 8 there, every attempt exact. Astra 6 runs a full spectroscopy playbook unprompted (gain recalibration, time profiles of every peak, gated centroids for doublets, quantitative sum and escape checks, signed delayed coincidences, an audit of weak peaks). A trap that only decides whether a peak gets noticed won't hold it; the task needs a step where careful, standard analysis still has to make a judgement the data settle.
- (18:58) To harden against Astra 6, aim at what its audits skip, read from the pass@8 code rather than from its messages: in gamma-decay-scheme v10 one attempt dropped gated peaks within 4 keV of a listed peak, tested only unplaced peaks against level differences and left the doublets out of its check for unexpected coincidences. v11 hides a weak transition under a strong, already placed peak whose only clean gate is a doublet.
- (19:40) pass@8 can end before 8 attempts: T-1519's ended at 4 attempts, all solved ("ended out of range (4
  solved)"), and the card was not replaced: the seen 03:59 card changed its text in place to "IN REVIEW, CHECKING
  PASS@K", so the poller saw no unseen card. Read `status` (the task row) after any long gap, not only the cards.
  A background poller dies with the Claude Code session that started it; after a restart, check `ps -ef | grep
  poll_pipeline` and restart your own.
- (21:50) A planted degeneracy must stay fair once the deciding evidence is used; check it under the reference's own
  noise model on the shipped draw before the generator run. rv-planet-census v3 hides a planet f at 2:1 behind an
  eccentric reading of its neighbour e. At f's first phase the activity pulled f's K by 28% exactly where e's single
  transit could not tell the readings apart, so f moved to a phase where the transit time decides (probes in
  `work/rv-planet-census/v3/explore/`). Then the reference itself fitted the added planet with e 0.73, on an orbit
  crossing e's, and K +43%: test every eccentricity (Lucy and Sweeney) and keep orbits from crossing before K is
  graded.
- (2026-11-12 02:05) dhva-fermi-surface v2 (internal field B = mu0 H + mu0 (1 - N) M, magnetic interaction) went
  0 of 3 on Sol 6.1, but not on the new physics: every attempt converted the field axis from its first steps (NOTES
  gave the bar's size and called the moment the sample's own; the magnetic-interaction combinations let them fit K
  from the data). All three lost the heavy orbit delta instead, two of them through coincidences nobody designed:
  gamma's eighth harmonic 5.8 T away (absorbed by a free-amplitude harmonic) and a combination of the other orbits
  matching delta in frequency (0.03%) and mass (1%), read as a "composite" and dropped by the fewest-orbits rule. Before
  a generator run, test every planted signal against harmonics up to the generated order and against integer
  combinations of the others as deep as attempts search (sum |n| <= 10), in frequency and in mass:
  `combinations_near` in dhva's `tests/generate.py` does it and writes the result to checks.txt [1].
- (06:02) gamma-decay-scheme v11 qualified at 1 of 3 on Sol 6.1 through one trap only: a weak transition (I 1.22) 0.9 keV under a strong placed line (I 13.0), whose only clean gate is a doublet. The two failed attempts were otherwise exact; the one that passed found it with a weak-peak search and took its intensity from the clean gate. A single trap aimed at a specific blind spot gave a cleaner result than stacking noticing traps.
- (2026-11-12 21:20) `tools/supertasker.py` `task_view` no longer waits for the page's "load" event: from about 20:58
  the platform took over 30 s to fire it, every status call timed out and a poller stopped with exit 2, though the
  session was signed in and the app had rendered. It now waits for DOMContentLoaded (90 s), then up to 30 s for the
  task view and 3.5 s for the cards. If a poller stops with exit 2 on `Page.goto: Timeout`, open the page in a fresh
  tab before suspecting a sign-out (`work/dhva-fermi-surface/v3/explore/probe_tab.py` does it and closes the tab).
- (21:45) gamma-decay-scheme v11/v12: one weak line hidden under a strong one gave Sol 6.1 1 of 3 but Astra 6 7 of 8. Astra 6 found it two ways: by checking every difference of two placed levels against the peaks (the line's upper level was placed by a clean line) and in the gate on a doublet member that it examines anyway. Sol 6.1 used only the first. A hidden line holds Astra 6 only if no cheap check points straight at it.
- (22:40) gamma-decay-scheme v13: when a scheme change moves the noise, re-read every evidence section before keeping a README claim. Here the search order failed one line (fixed by placing lines on shared peaks after clean ones), a second minimal scheme appeared, and most README figures moved. `[placement search]` now lists any other scheme with as few levels and the coincidence that excludes it.
- (2026-11-13 01:50) The pass@8 range, in one place: the docs say 1 to 6 solved of 8 qualify, and 0, 7 or 8 solved
  send the task back (`docs/TB4-study-reference (2).md` lines 36-37, `docs/TB4-learning-update-2026-10-28.md` line
  37). Counted in failures, as the platform's card once did ("TOO EASY, 0 of 8 failed"), that is 2 to 7 failed. The
  platform agrees at the top: gamma-decay-scheme v12, 7 solved of 8, was sent back TOO EASY (2026-11-12 21:09). It
  also stops early: T-1519's pass@8 ran 4 attempts, all solved, and ended "out of range (4 solved)". Aim for 2 to 5
  solved of 8, with at least one of the first four attempts failing.
- (2026-11-13 01:50) The user confirmed: "pass@8 qualifies at 1-6/8" (solved attempts of 8).
- (07:32) gamma-decay-scheme v13 (0 of 3 on Sol 6.1): a trap that needs a level difference only works when the upper level is placed early. Sol 6.1 matches level differences to peaks once, before it adds levels from weak lines, and does not repeat it.
- (07:51) gamma-decay-scheme v14: the share of a weak member under a strong line from a fit of the peak's shape is set by the energy scale more than by the shape (0.05 keV moves it by about 0.06); gate proportions are robust. Size such a trap against the gate method, and expect a shape fit to land anywhere within about 30%.
- (14:59) If `supertasker.py` calls slow down over days and then time out in `connect_over_cdp` while `http://127.0.0.1:9224/json/version` still answers, look at the open queue tabs: every past Playwright connection left a utility world in each tab it saw, and connecting replays them all (gamma-decay-scheme Pitfalls, 2026-11-13). Since 2026-11-13 14:51 the tool works in a tab of its own per call and the next call closes it, so its own tabs no longer pile them up; any other long-lived tab still does. Close such a tab only when no other session's call is running (`Get-CimInstance Win32_Process` lists them).
- (2026-11-13 15:05) If `supertasker.py` calls time out while Chrome on 9224 and the platform both answer, count
  the tabs (`curl -s 127.0.0.1:9224/json/list`): every Playwright connection leaves a utility world in every open
  tab, a tab keeps them across navigations, and connecting replays them all. After two days the platform tabs held
  700 to 776 each and every session's status call timed out (dhva's poller exit 2 at 14:31). Since 15:00 each call
  opens its own tab and leaves it as `about:blank#tb4-keeper`, which the next call closes (`fresh_page`, `retire`).
  A tab the tool did not leave that way (a manual one, or one from before the change) still collects worlds: close
  it with `curl -s 127.0.0.1:9224/json/close/<id>` once a raw check shows nothing in progress in it, and never close
  the last tab. Status took 23 s afterwards.
- (15:10) Addendum to 15:05: `fresh_page` also closes a platform tab whose page is older than 15 minutes with no
  open dialog and no file chosen (a call the poller kills at 170 s never blanks its tab). Close tabs by hand only
  when calls are already too slow for that to happen.
- (2026-11-13 15:12) User rule: "You don't need to work until re-work. watch the pipeline only okay ?" While a task waits on the platform, only watch it (poller, log the cards); start drafts, fixes or tool work only once the task is sent back for rework.
- (15:29) The user watches the debug Chrome window and asked to see the task page there, so a call now leaves its tab on the task page (only other pages go blank as about:blank#tb4-keeper); the next call on that task opens a fresh tab and closes the old one, so the page refreshes about every 3 minutes and no tab lives long.
- (2026-11-13 15:31) The user, completing the 15:12 rule: "if failed, you should work while watching pipeline." So: while the platform is deciding, only watch; as soon as a check fails or the task is sent back, start the fix at once, keep the poller running through the rework, and resubmit (the standing rule in CLAUDE.md).
- (2026-11-13 15:39) User rule, standing: "From now on, please use the git as well. I just configured git for pushing as well. So after you updated task, please commeit and push as well on the last step always. keep this rule". The folder is now a git repo (remote `origin` = GitHub, branch `main`). The last step of every task update (release, new task, fix, log entries) is `git add -A`, `git commit`, `git push origin main`; check `git status` before staging so nothing under `.supertasker-profile/` or any secret goes in (`.gitignore` covers both), and report a failed push.
- (2026-11-13 15:42) Git for Windows sets `core.autocrlf=true` system-wide, so a checkout, reset or stash would rewrite task files with CRLF and fail `scan_task.py`. This repo now has `core.autocrlf=false` in its local config; keep it that way. First commit-and-push under the new rule: 8c9357d.
- (2026-11-13 15:40) User: "check pipeline every 20 mins", "not every 3 mins". Run the poller with INTERVAL 1200, not 180: `tools/poll_pipeline.py T-ID 43200 1200`.
- (2026-11-13 17:00) User: "please don't close the tab which i opened, just my own one". `tools/supertasker.py` now opens its tab in the background (Target.createTarget, background), so the tab in front stays in front; marks every platform page it opens (sessionStorage `tb4-tool-tab`); blanks its tab as about:blank#tb4-keeper at the end; and closes only keeper tabs and marked pages older than 300 s with no dialog and no file chosen. Unmarked tabs (the user's, and leftovers from before 16:57) are never closed by the tool; closing another session's leftover tab by hand was refused by the permission check, so ask the user. A tab kept open still collects worlds: if calls slow down again, ask the user to close and reopen it.
- (18:55) The workspace moved (user, 2026-11-13 about 18:41 UTC) to `C:\Users\Administrator\OneDrive\Documents\Tango-arunufo`; the old `Documents\Tango-arunufo` is empty. A shell may still start in the old folder: `cd` to the new root first in every call. Start the debug Chrome with `--remote-debugging-port=9224 --user-data-dir=<new root>\.supertasker-profile`. Keep it open: the user watches progress in it.
- (19:17) The tool's own tabs no longer gather Playwright utility worlds, but tabs the user keeps open still do: one per connection of any session. Measured 19:16 (`work/gamma-decay-scheme/v14/explore/count_worlds.py` on a `DEBUG=pw:protocol` log of `cdp_probe.py`): the T-1383 tab open since 18:52 held 10, `#submit` 6; a status call took 13 s and connecting 4 s. This afternoon's stall came at 387 to 2570 per tab. A poller at 180 s adds 20 per tab per hour, so a watched tab reaches that range in about a day: poll at 600 s while pass@3 runs (results come hours apart), and when calls slow down, ask the user to close and reopen the tabs they watch (a reload does not clear them; the tool must not close a user's tab).
- (19:18) Spent P3 ID: P3-B911-F9F1-EDFA (gamma-decay-scheme v14, pass@3 1 of 3 on Sol 6.1), given to the user for DAS 4011092. Never reuse it.
- (19:32) User: "please download up-to-date toolkit always". The platform offered kit 3.8.7 (installed: 3.8.2). Downloaded to `work/toolkit/20261113-387/` (kit.zip 1013939 bytes, extracted to `x/`) and installed at `~/tb4/tb4-starter-pack` (`tb4 --version`: 3.8.7); 3.8.2 kept as `~/tb4/tb4-starter-pack-3.8.2`. Only VERSION, `lint/gates_static.py` and `lint/grader_hygiene.py` changed, all relaxations (recorded check counts, an author's email inside EQUIVALENCE.json, `evidence/cheat/<name>` folders, test modules named in the instruction, more wordings of "/app/output is collected"); the template is identical. gamma-decay-scheme lints PASS under it (0 FAIL, 0 WARN). From now on `tools/kit_update.py` does this: it fetches `gate/kit/download`, compares VERSION and installs a newer kit the same way (exit 0 current or installed, 1 not reachable, 3 template changed). `tools/release.sh` runs it first; run it by hand at the start of a session and before packaging a new task.
