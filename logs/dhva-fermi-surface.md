# dhva-fermi-surface: task log

Read this log and `logs/STATUS.md` before opening any task file. Entries are summaries: the numbers, the decision and
where the evidence lives. All times are UTC (the platform shows UTC; this PC is UTC-8).

## Identity

| Field | Value |
|---|---|
| Source | `tasks/active/dhva-fermi-surface/` (output task, data files, `RUN_PROGRAM=0`; scaffolded 2026-11-10) |
| Platform | not submitted yet |
| DAS Task ID | **4034278** (given by the user 2026-11-10 for this task) |
| Category | Science / Physics |
| Target | pass@3 solved **1–2 of 3** |
| P3 IDs given to the user | none yet |
| Evidence | `work/dhva-fermi-surface/v<N>/`: `design.md`, `explore/` (audits, edit scripts), later criteria reports, pass@3 |
| Master generator | `tasks/active/dhva-fermi-surface/tests/generate.py` |

## State now

- **2026-11-10 (session start)**: user: "build high difficult science/physics task and submit with DAS task id
  4034278". Read BRIEFING, STATUS and the rv-planet-census and gamma logs before designing. Design: the gamma pattern
  (data-only inference, several independent expert traps), carried to de Haas-van Alphen quantum oscillations: find
  every extremal Fermi-surface orbit (frequency and cyclotron mass) of an invented metal from magnetization sweeps at
  twelve temperatures. See `work/dhva-fermi-surface/v1/design.md`. The user was told at the start that the generator,
  with its reference run, would be run during the build.
- **2026-11-10 21:30-22:45**: scaffolded with `tb4 new output-task` (task.toml rewritten with LF); locks copied from
  rv-planet-census (numpy 2.3.3, scipy 1.18.1, asciinema 2.4.0). Design audits with `tests/generate.py --audit`
  (outputs in `work/dhva-fermi-surface/v1/explore/audit*.out`); the reference's changes are listed in `design.md`.

- **2026-11-10 22:44-23:05**: generator runs 1 and 2 (`tests/generate.py`: data, `expected.json`, the reference on
  the shipped sweeps and on three further noise draws as parallel subprocesses, `checks.txt`). Run 1: the reference
  AGREES (frequencies within 0.018%, masses within 0.6%), but delta's mass scattered -0.5/+4.8/+7.0% over the draws and
  the textbook Fourier peak-height route is off by up to 8.5% even in a sensible 22-35 T window; with 10% a careful
  answer could fail on precision alone (rv's lesson), so the mass band is 15% (instruction, requirements, test,
  generator) and every orbit standing 10 sigma out gets its frequency refined. Run 2: AGREES, frequencies within
  0.005%, masses within 0.6% except delta -4.0%; draws within 1.3% except delta (-1.6, +2.8, +2.5%). The 15% band
  still rejects gamma's mass from the blended peak (+212 to +282%), a harmonic's mass and the arithmetic-mean field
  over 14-35 T for alpha, epsilon and the beta neck (+15 to +22%). Run 3 (23:05) adds only a Fourier-resolution line
  for the README. `tb4 lint` PASS, scan 0 problems. Outputs: `work/dhva-fermi-surface/v1/explore/gen*.out`,
  `checks.run1.txt`, `checks.run2.txt`.
- **2026-11-10 23:15-23:20**: README's step 2 made exact (half a main-lobe half-width in the high-field window), so
  the 23:15 zip (digest `9d6017ca…2ca3`, never uploaded) was deleted and the task packaged again: digest
  `87064573…ca271`. `release.sh --check` clean. Waited for 00:00 UTC so 11-10's fifth upload stayed free.
- **2026-11-11 00:01**: v1 submitted as a new task (`work/rv-planet-census/v1/explore/submit_newtab.py`, a tab of its
  own; DAS 4034278; check kind "Quick check (35 + 5)"; no note): "Queued: dhva-fermi-surface as task **T-1563**."
  Upload 1 of 5 on 11-11; the Submit page showed "1 of 2 new tasks left today". Output in
  `work/dhva-fermi-surface/v1/submit.out`. Poller started on T-1563 (`tools/poll_pipeline.py T-1563 43200 180`); the
  other sessions' pollers watch T-1519 and T-1383. The same page showed gamma-decay-scheme sent back at 00:00 (pass@3
  3 of 3): that is the gamma session's card, left unseen for it.
- **2026-11-11 10:33-11:15**: the 00:01 poller had stopped with the previous session; a status call at 10:33 found
  two cards: the quick check passed (09:32, job 21089) and pass@3 solved 3 of 3 (09:52, Sol 6.1, sent back,
  REWORK). Both logged, reviewed, marked seen at 10:44. pass@3 digest and analysis below ("pass@3 analyses", v1).
  Decision: new physics (approved order, step 3, since every trap fell cleanly): the internal field. v2 is drafted in
  the active folder (no check is running on T-1563, so nothing to keep valid); design in
  `work/dhva-fermi-surface/v2/design.md`. The generator will run again for v2's data (the user was told at the start
  that it runs during the work).
- **2026-11-11 11:15-12:10**: v2 built in the active folder (design `work/dhva-fermi-surface/v2/design.md`). The
  electrons feel the flux density inside the sample, B = mu0 H + mu0 (1 - N) M, not the field column. The bar
  (0.250 x 0.200 x 1.600 mm, field along its length, now in NOTES.md) gives N = 0.0628 (Aharoni 1998) and
  K = 1.4721e-5 T per moment unit; the steady moment 1430 B - 0.10 B^3 puts B 1.9-2.2% above the field column, so every
  frequency read against the field column is 2.2-2.4% low (four times the band). alpha's amplitude 201 -> 900 makes
  the magnetic interaction a = K dm~/dB reach 0.209 at 0.35 K: against the field column the coldest 6-35 T spectrum
  has 14 peaks (combinations 2eps-alpha, 2eps+alpha, beta+alpha, ...), against B 8. Answers unchanged
  (`expected.json` byte-identical). Changes: `solution/solve.py` (step 0 converts the field axis; `--frame` for the
  routes), `tests/generate.py` (self-consistent B(H), STEADY, DRIFT, the routes, peak labels), NOTES.md (bar size,
  the moment as the sample's own after the empty-cell run, the field column as the magnet's field), instruction R5
  (F = hbar A / (2 pi e) with A the orbit's k-space area; `requirements.json` quote updated), `task.toml` and README
  tags (`magnetic-interaction`), README rewritten from the v2 checks.
  - Generator run 1 (11:20-11:42, 1318 s, exit 0): AGREES; frequencies within 0.009% (draws 0.024%), masses within
    1.7% but delta -6.6% (draws -8.3/-7.0/-2.3%, inside the 15% band); the reference against the field column and
    with the oscillatory magnetization only both DISAGREE (five of six orbits missed; the beta neck matched only by
    the beta belly's shifted entry). Output `work/dhva-fermi-surface/v2/explore/gen1.out`.
  - Generator run 2 (11:46-12:08, 1320 s, exit 0) after making the applied-field peak labels list both readings
    ("3 x alpha or gamma + alpha") and naming each route entry: data and `expected.json` sha256-identical to run 1,
    only `checks.txt` changed (reference 838 s). Output `gen2.out`, hashes `hashes_run1.txt`, `hashes_run2.txt`.
  - lint FAIL once on readme-claims ("worst" made "-2.3%" a measured claim in a block with no file path); reworded.
    Then `release.sh --check`: scan 0 problems, canary, every .py parses, lint PASS.
- **12:11**: v2 uploaded with Upload the fix, no note (upload 3 of 5 on 11-11); quick check queued. v2: internal field B = mu0 H + mu0 (1-N) M of a strongly paramagnetic bar (frequencies against the applied field 2.3% low) and magnetic interaction in the data; NOTES gives the bar's size and the moment as the sample's own; instruction defines F by the orbit's area; reference converts the field axis first See Version history (v2).
- **2026-11-12 00:12**: the v2 poller (`tools/poll_pipeline.py T-1563 43200 180`, from 12:11) reached its 12 h
  limit with no card (exit 1). v2's quick check was queued until about 20:31 and has been running since; the platform
  answered 503/502 briefly at 19:04, 19:52 and 21:58 (not counted as misses). Poller restarted at 00:12; outputs
  `work/dhva-fermi-surface/v2/poll1.out`, `poll2.out`. The v3 dials for each outcome are in
  `work/dhva-fermi-surface/v3/plan.md` (v1's attempts never mention the sample's size or magnetization).
- **2026-11-12 01:40-02:45**: v2's pass@3 card (0 of 3, 01:36) logged, analysed and marked seen 01:50 (analysis under
  "pass@3 analyses", v2). v3 built in the active folder (design `work/dhva-fermi-surface/v3/design.md`): delta
  7415 -> 7300 T, its mass, Dingle temperature, g and amplitude unchanged; everything else as v2. `tests/generate.py`:
  ORBITS, the harmonic coincidences up to p = 8 (was 6) and `combinations_near` (integer combinations of the other
  orbits, sum |n| <= 10, in frequency and mass), both written to checks.txt [1]. README: delta's bullet (7300 T, the
  coincidence check), the bands from the new checks, the reference's time.
  - Generator run (01:52-02:41, 2913 s, exit 0; the user was told it runs): AGREES. Frequencies within 0.002% (draws
    0.005%); masses within 1.6% but delta -3.7% (+-0.037, against +-0.17 in v2 with 8 x gamma 5.8 T away); draws
    delta -0.01, +2.8, -4.4%. Reference 1850 s on one CPU, against 838 s in v2: seven processes on six cores and
    probably another session's work at the same time. Output `work/dhva-fermi-surface/v3/explore/gen1.out`; v2's
    hashes in `hashes_v2.txt`.
  - [1]: delta's nearest harmonic is 8 x gamma, +120.8 T; 6 combinations within 0.1%, none within 15% in mass (the
    lightest 5.23). [2]: delta 7299.9 T, signal to noise 23 over 22-35 T, absent from 6-35 T and whole sweeps.
  - `release.sh --check`: scan 0 problems, canary, every .py parses, lint PASS.
  - BRIEFING point (02:05): test planted signals against harmonics and against mass-matching combinations before a
    generator run.
- **02:45**: v3 uploaded with Upload the fix, no note (upload 1 of 5 on 11-12); quick check queued. v3: delta moved from 7415 to 7300 T, clear of gamma's eighth harmonic (5.8 T away before, 120.8 T now) and of every combination of the other orbits that matched it in frequency and mass; checks.txt [1] reports harmonics to p = 8 and the combination count; README from the v3 checks See Version history (v3).
- **2026-11-12 14:45**: the v3 poller (from 02:45) reached its 12 h limit with no card (exit 1). v3's quick check
  was queued until about 12:31 and has been running since. Poller restarted at 14:45; outputs
  `work/dhva-fermi-surface/v3/poll1.out`, `poll2.out`.
- **2026-11-12 21:20**: the 19:48 poller stopped with exit 2 at 21:09: three status calls in a row (20:58, 21:04,
  21:08) timed out in `page.goto` waiting for "load" (30 s). Not a sign-out: the server answered curl in 0.5 s (401
  without cookies), and a fresh tab (`work/dhva-fermi-surface/v3/explore/probe_tab.py`, opened and closed again)
  showed the signed-in task view after 23 s to DOMContentLoaded: pass@3 still queued (19:40), 0 unseen. The platform
  was slow, so `tools/supertasker.py` `task_view` now waits for DOMContentLoaded (90 s) and then up to 30 s for the
  task view, plus 3.5 s for the cards; a status call took 28 s. Poller restarted at 21:20 (`poll4.out`).
- **2026-11-13 10:45**: v3 QUALIFIED at 01:28 (pass@3 2 of 3, job 22636): P3 ID P3-2F9B-5B0C-A1B0, with the user
  for DAS 4034278. The full review ran on v4 (= v3's files, job 24020) and finished 10:14: a reviewer decides, so no
  upload. Its critical finding holds: README "within 0.005% on the further draws [5]" (a v2 line) against gamma at
  +0.006% for seed 40342782 in v3's checks.txt [5]. Every other README figure re-read against checks.txt line by
  line (10:40): all agree; the derived ones (0.67 T at 35 T, 0.54%, 2.3%, the N = 0 and 1% size effects) follow
  from [1] by arithmetic. Draft `work/dhva-fermi-surface/v5/task/` = the active task with that one README word
  changed (0.006%); scan 0 problems. `contract_probes` and `contract_generality` wait for the reviewer's note,
  which names the counterexample and the assumption (gamma's did, 2026-11-10 17:56). Poller restarted 10:35
  (`work/dhva-fermi-surface/v4/poll6.out`).
- **2026-11-13 15:05**: the 10:35 poller stopped with exit 2 at 14:31: status calls had timed out (170 s) from 11:52,
  three in a row by 14:31. Not a sign-out and not the platform (curl 401 in 1.7 s; every tab answered a raw CDP
  evaluate at once). Playwright's `connect_over_cdp` hung after the websocket opened: with DEBUG=pw:protocol,
  `Runtime.enable` on each platform tab never answered while it replayed leftover Playwright utility worlds, one
  per earlier connection (`__playwright_utility_world_page@<id>`): 776 in the T-1563 tab and 697 in the #submit tab
  within 40 s. Long-lived tabs keep them across navigations, so every poll of every session added one to every
  tab. Fix in `tools/supertasker.py`: each call works in a new tab (`fresh_page`) and leaves it as
  `about:blank#tb4-keeper` (`retire`); the next call closes the keeper after opening its own tab, so the window
  keeps one; `task_view` also closes a tab still on the same task's page from an earlier call. Tabs: the T-1383
  and #submit tabs had already been closed by another session between 14:47 and 14:52 (none had a dialog, a chosen
  file or a filled field); I closed the T-1563 tab (14:55) and the orphan #submit tab (14:59, the former T-1519
  tab). Status calls then took 23 s (97 s before the last close). T-1563 unchanged: Waiting for a reviewer, last
  change 10:13, 0 unseen. Poller restarted 15:00 (`work/dhva-fermi-surface/v4/poll7.out`).
- **2026-11-13 15:10**: `tools/supertasker.py` again: at 15:01 a leftover `/#submit` tab appeared (history 3, so a
  call's tab the platform sent from a task page to `#submit`, and the call was killed before it could blank it).
  `fresh_page` now also closes a platform tab whose page is older than `STALE_SEC` (900 s) with no open dialog and
  no file chosen; a call lasts under 3 minutes, so no tab in use qualifies. `task_view` leaves this call's own tabs
  open until it ends (upload-fix reads the status while its upload tab is still open). Status call 19 s.
- **2026-11-13 17:00**: the user asked the tool to leave their own tab alone. `tools/supertasker.py` now opens its tab in the background, marks its platform pages (sessionStorage), blanks its tab at the end and closes only its own keeper tabs and marked leftovers (older than 300 s). Test 16:58: status in 13 s; the user's T-1563 tab stayed in front, untouched. Three unmarked leftovers of other sessions' polls (T-1383, T-1519, #submit) stay open: closing them was refused by the permission check; left to the user. Poller at 20 minutes since 16:16 (`poll8.out`).
- **2026-11-13 17:53**: poller stopped at the user's request ("please stop background"). Last status: Waiting for a reviewer, last change 10:13, 0 unseen (`work/dhva-fermi-surface/v4/poll8.out`). Nothing runs in the background for T-1563 now; check `supertasker.py status T-1563` by hand, or restart the poller when the user asks.

## Version history

- **v1, uploaded 2026-11-11 00:01** (first submit, `submit_newtab.py` in its own tab, DAS 4034278, T-1563). The design
  in `work/dhva-fermi-surface/v1/design.md`: six orbits, frequency band 0.5%, mass band 15%, 7 requirements, 3 tests.
  - Zip `deliveries/dhva-fermi-surface-20261110.zip`: 1269916 bytes, 35 files; task digest
    `sha256:8706457336244da8d31ded35690dc3b59aab7de58a6c392a0b53cbf7621ca271`; zip sha256 `d2beabdb…603e`.
  - Reference on the shipped data (`tests/checks.txt`, generator run 3): frequencies within 0.005%, masses within
    0.6% except delta -4.0%; three further noise draws within 1.3% except delta (-1.6, +2.8, +2.5%); 576 s on one CPU.
  - lint: PASS, every structure check passes; scan: problems: 0. Upload 1 of 5 on 11-11.
  - Generator run three times during the build, reference included; the user was told. No oracle, verifier or Harbor
    run.
- **v2, uploaded 2026-11-11 12:11** (Upload the fix on T-1563). v2: internal field B = mu0 H + mu0 (1-N) M of a strongly paramagnetic bar (frequencies against the applied field 2.3% low) and magnetic interaction in the data; NOTES gives the bar's size and the moment as the sample's own; instruction defines F by the orbit's area; reference converts the field axis first
  - Zip `deliveries/dhva-fermi-surface-20261111.zip`: 1290603 bytes, 35 files; task digest `sha256:3494178779b8efc5ccd7aba399be2935f18da54603a3aae95401209e1ba97604`; zip sha256 `9c1736c2…f269`.
  - Previous zip archived as `deliveries/archive/dhva-fermi-surface/dhva-fermi-surface-v1-20261110.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.
- **v3, uploaded 2026-11-12 02:45** (Upload the fix on T-1563). v3: delta moved from 7415 to 7300 T, clear of gamma's eighth harmonic (5.8 T away before, 120.8 T now) and of every combination of the other orbits that matched it in frequency and mass; checks.txt [1] reports harmonics to p = 8 and the combination count; README from the v3 checks
  - Zip `deliveries/dhva-fermi-surface-20261112.zip`: 1291867 bytes, 35 files; task digest `sha256:428e960de8692bab99a6cdd087bf8e71bfd83cb07700dbd309f9225b96305769`; zip sha256 `82413db5…e239`.
  - Previous zip archived as `deliveries/archive/dhva-fermi-surface/dhva-fermi-surface-v2-20261111.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.

## Platform updates

| Card time (UTC) | Title | Result | Seen |
|---|---|---|---|
| 2026-11-11 09:32 | the quick check passed (T-1563 v1) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Version row: quick check PASS, 36 of 40 pass. Queued 00:01, running from about 05:01 (the poller's last sight). The 00:01 poller stopped with the session after 05:01; this card was found by a status call at 10:33. | no |
| 2026-11-11 09:52 | pass@3 solved 3 of 3 (T-1563 v1) | "The model solved all three attempts: the task is too easy. Make it harder, lint, and upload it again for a new review." Version row: pass@3 "TOO EASY, 0 of 3 failed" (09:52), Platform "sent back (SBQ)"; task status REWORK, "pass@3 ran on Sol 6.1". Job 21089. Found at 10:33. | no |
| 2026-11-11 09:32 | the same card, reviewed | Marked seen 10:44. Job 21089 (reviewer astra, gpt-6.1-sol): 35 criteria 31 pass, 0 fail, 3 N/A, `novel` NOT_PROVIDED (deferred to the full review); 5 extra pass; the platform's oracle 1, nop 0, tamper 0. Reports in `work/dhva-fermi-surface/v1/criteria-35.md` and `criteria-extra.md`. | yes |
| 2026-11-11 09:52 | the same card, reviewed | Marked seen 10:44. pass@3 of v1 (job 21089): **3 of 3** solved, rewards [1, 1, 1]; every designed trap fell in every attempt. Analysis under "pass@3 analyses" (v1). Status REWORK: v2 to be made harder and uploaded with Upload the fix. | yes |
| 2026-11-12 01:13 | the quick check passed (T-1563 v2) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Version row: quick check PASS, 36 of 40 pass; pass@3 running, 0 of 3 ended, on Sol 6.1. Queued 12:11, running from about 20:31, passed about 00:55. Seen by the restarted poller at 01:17. | no |
| 2026-11-12 01:13 | the same card, reviewed | Marked seen 01:18. Job 21778 (reviewer astra, gpt-6.1-sol): 35 criteria 31 pass, 0 fail, 3 N/A, `novel` NOT_PROVIDED (deferred to the full review); 5 extra pass. The reviewer's notes name the internal-field conversion (`solution_quality`, `oracle_investigates`: "corrects the field using sample dimensions supplied in NOTES.md") and magnetic feedback (`difficult`). Reports in `work/dhva-fermi-surface/v2/criteria-35.md` and `criteria-extra.md`. pass@3 running. | yes |
| 2026-11-12 01:36 | pass@3 solved 0 of 3 (T-1563 v2) | "pass@3 solved 0 of 3: the target model failed all three attempts, so the task comes back to you. A task must be solved in some but not all attempts. If they fail on something the instruction never states, or on an environment problem, fix that; if they fail at the stated difficulty, make the task somewhat easier. Then lint and upload the new version." Version row: pass@3 "TOO HARD, 3 of 3 failed" (01:36), Platform "sent back (SBQ)"; task status REWORK, "pass@3 ran on Sol 6.1". Job 21778. Seen by the poller at 01:39. | no |
| 2026-11-12 01:36 | the same card, reviewed | Marked seen 01:50. pass@3 of v2 (job 21778): **0 of 3** solved, rewards [0, 0, 0]; each attempt reported the five lighter orbits within 0.15% and 4% and left out delta (7415 T). Every attempt converted the field axis. Analysis under "pass@3 analyses" (v2). Status REWORK: v3 moves delta clear of the accidental coincidences two attempts used to drop it. | yes |
| 2026-11-12 19:40 | the quick check passed (T-1563 v3) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Version row: quick check PASS, 36 of 40 pass; pass@3 queued 19:40, on Sol 6.1. Queued 02:44, running from about 12:31, passed about 19:34 (status calls timed out 19:01-19:27). Seen by the poller at 19:43. | no |
| 2026-11-12 19:40 | the same card, reviewed | Marked seen 19:47. Job 22636 (reviewer astra, gpt-6.1-sol): 35 criteria 31 pass, 0 fail, 3 N/A (verifier_execution_isolation, do_not_modify_enforced, artifact_efficiency), `novel` NOT_PROVIDED (deferred to the full review); 5 extra pass. Reports in `work/dhva-fermi-surface/v3/criteria-35.md` and `criteria-extra.md`. pass@3 queued 19:40. | yes |
| 2026-11-13 01:28 | in review (T-1563 v3 -> v4) | "IN REVIEW. the full review is running. Submit the task in DAS now if you haven't yet, but don't upload a new version: you get an update when the review team has decided." "pass@3 is OK: 1 of 3 attempts failed. The full review has started on these exact files: you get an update when it ends." **P3 ID P3-2F9B-5B0C-A1B0** ("this revision only"). Version row: v4 (v3's files), Full review running 01:28. pass@3 queued 19:40, running from about 00:00, 2 of 3 ended by 01:25. Seen by the poller at 01:31. | no |
| 2026-11-13 01:28 | the same card, reviewed | Marked seen 01:36. pass@3 of v3 (job 22636, Sol 6.1): **2 of 3** solved, rewards [1, 1, 0]: QUALIFIED. a1 and a2 report all six orbits (delta 7300.56 and 7300.38 T, m 3.247 and 3.24); a3 reports the five lighter orbits and never searched a high-field window (the designed trap). P3 ID P3-2F9B-5B0C-A1B0 given to the user for DAS 4034278; the user submits on DAS. Full review running on v4 (= v3's files, job 24020); no upload meanwhile. Analysis under "pass@3 analyses" (v3). | yes |
| 2026-11-13 10:14 | in review (T-1563 v4) | "IN REVIEW, DECIDING. the full review has finished and the review team is deciding. Submit the task in DAS now if you haven't yet, but don't upload a new version: you get an update with the decision." "The review left 2 item(s) that a person has to settle. A reviewer settles them and decides what comes next: you get an update when one decides. Nothing to upload for now." TO CHECK Contract generality: "Contract-generality FAIL-PENDING-DISPOSITION: 1 generator assumption(s) traced (0 dropped): 0 settled by a quoted rule, 1 not". TO CHECK Stated facts.facts consistent: "README.md's frequency-tolerance discussion claims the reference is within 0.005% on every further noise draw" (cut off). P3 ID P3-2F9B-5B0C-A1B0 shown again. Status "Waiting for a reviewer"; v4 "Full review: under evaluation by the review team". Seen by the poller at 10:31 (it started 01:38). | no |
| 2026-11-13 10:14 | the same card, reviewed | Marked seen 10:34. Report `/job/24020/report` ("A reviewer decides next"; HTML and text in `work/dhva-fermi-surface/v4/full-review/`). **Return the task (critical):** "Compare README.md's claimed maximum frequency error on further draws with the γ result for seed 40342782 in tests/checks.txt section 5. Does the cited result support that bound?" `stated_facts.facts_consistent` fail: "tests/checks.txt section 5 reports γ at 927.66 T versus 927.60 T for seed 40342782, explicitly recording an error of +0.006%, outside that claimed bound." Confirmed: the README's bullet "0.5% on frequencies" still says "within 0.005% on the further draws [5]" from v2, and v3's redraw put γ at +0.006% (my v3 README check went by the diff and missed the unchanged line). A person settles `contract_probes` ("23 requirement(s) (3 dropped ...), 21 cite an enforcing test; 11 probed (1 from the grader …") and `contract_generality` ("1 generator assumption(s) traced (0 dropped): 0 settled by a quoted rule, 1 not ..."); the page truncates both, as it did for gamma. Controls not run this time (wrong-answers, missing-artifact, partial-artifact, readable-answers: "Could not run ... (`tb4 check <task>`)"). No upload while the reviewer decides; the fix is drafted in `work/dhva-fermi-surface/v5/task/`. Poller restarted. | yes |

## pass@3 analyses

### v1 (T-1563 v1, job 21089, pass@3 ended 2026-11-11 09:52): 3 of 3 solved, TOO EASY

- Sol 6.1, rewards [1, 1, 1]. Agent times 14, 19 and 11 min (33, 43 and 33 episodes), cost $0.46, $0.78 and $0.39.
  Bundle in `work/dhva-fermi-surface/v1/pass3/` (`pass3.zip`, untrusted extraction under `x/`, `summary.md`);
  answers in `work/dhva-fermi-surface/v1/attempts/programs/aK/orbits.json`, digests in `attempts/attempt-K.txt`.
- Answers: six orbits each time, frequencies within 0.02% (gamma 927.61-927.63, delta 7414.78-7415.05), masses
  within 3% (delta 3.255-3.30 against 3.35, the beta neck 1.20 against 1.21).
- How: spectra of several sweeps (0.35 to 18 K) over several windows at once; gamma kept because the 928 T peak
  outlives alpha's second harmonic at 6.5 K and above; then a direct least-squares fit of the Lifshitz-Kosevich model
  in field space (harmonics up to 8 with p m, spin factors), residual RMS down to the noise (2.0), delta found as a
  coherent residual and its 8 x gamma reading rejected by mass (3.3 against 2.15); half-frequency, sum-frequency and
  spin-zero readings tested and rejected.
- Difficulty, honestly: a global fit of the exact generating model recovers every parameter, and every trap built
  from that model (blend, spin zero, heavy orbit, neck/belly pair, harmonics) falls to it. None of the attempts
  turned the moment into a magnetization: v1's background slope, 1500 units per T on a 0.045 mm^3 sample, is a
  magnetization with mu0 M = 4.2% of the field, so the oscillations of such a sample would be periodic in
  1/B = 1/(mu0 H + mu0 (1 - N) M), not in 1/(mu0 H). The generator ignored that, and so did the attempts.
- Next (v2, `work/dhva-fermi-surface/v2/design.md`): physics a generator built from the stated scope leaves out:
  the electrons feel B, not the applied field. A strongly paramagnetic sample, with the full self-consistent internal
  field in the generator (the steady magnetization scales every frequency; the oscillatory one gives magnetic
  interaction: harmonics and combination frequencies that are not orbits).

### v2 (T-1563 v2, job 21778, pass@3 ended 2026-11-12 01:36): 0 of 3 solved, TOO HARD

- Sol 6.1, rewards [0, 0, 0]; each failed `test_orbits_found` and `test_masses`. Agent times 21, 11 and 10 min (50,
  30 and 28 episodes), cost $0.89, $0.38 and $0.40. Bundle in `work/dhva-fermi-surface/v2/pass3/` (`pass3.zip`,
  untrusted extraction under `x/`, `summary.md`); answers in `work/dhva-fermi-surface/v2/attempts/programs/aK/
  orbits.json`, digests in `attempts/attempt-K.txt`.
- Answers: five orbits each time, delta missing in all three. The five are right: a1 and a3 within 0.008% in
  frequency, a2 0.04-0.15% high (as with N = 0); masses within 1.5% (a1, a3) and 3.7% (a2).
- The internal field fell in every attempt, from the first steps: a1 noted the dimensions and the moment at once,
  inferred the induction correction from the oscillations and checked it against the bar's demagnetizing factor
  (0.06283, the same formula as the reference); a2 computed mu0 m / V and fitted the coefficient; a3 estimated N
  and compared spectra against mu0 H and against B. The magnetic-interaction combinations make K measurable from the
  data (they vanish only at the right K). So the v2 physics is routine for the model; it costs no attempt.
- Why delta was lost, each a different way:
  - a1 found it (fit 7414.75 T, m 3.20) and then dropped it as a composite, 4 x 1186.4 + (2641.0 + 2702.6) / 2 =
    7417.4 T with summed mass 3.17, "stronger evidence for a breakdown/composite oscillation than for an additional
    extremal orbit", and wrote the fewest-orbits set. The match is an accident of the orbit table: within 0.03% in
    frequency and 1% in mass.
  - a2 searched residuals over the whole sweep (1/B from 0.030 to 0.190, Hann taper, five coldest sweeps averaged)
    and never a high-field window; delta, damped below 20 T, sits at the tapered end and came out at the noise level
    (7417.74 T, 0.057 against a floor of about 0.06). This is the designed trap ("A heavy orbit seen only at high
    field").
  - a3 saw the high-frequency residual and put it down to omitted harmonics of gamma and epsilon, then fitted those
    with free amplitudes. gamma's eighth harmonic is 7420.8 T, 5.8 T from delta and unresolvable at high field; by
    Lifshitz-Kosevich it is 0.10 units at 30 T against delta's 2.34, so the reading is wrong, but the coincidence
    let a free-amplitude model absorb delta.
- Fairness: the instruction asks for every orbit the sweeps show; the fewest-orbits rule applies only to sets that
  account for every oscillation, and neither reading does by Lifshitz-Kosevich (a composite of a mean frequency is no
  orbit; 8 x gamma's amplitude is 24 times too small). But two of the three dismissals rest on coincidences nobody
  designed and the README never mentions: 8 x gamma 0.08% from delta, and a combination of the other orbits within
  0.03% and 1% in mass. v1's attempts met the same coincidences and rejected both by mass.
- A scan (`work/dhva-fermi-surface/v3/explore/delta_scan2.py`) over every integer combination of the other five
  orbits with sum |n| <= 10 (the depth a1 searched): at delta's 7415 T one lies within 0.1% in frequency and 15% in
  mass; at 7290-7310 T and 7560 T none does (the lightest within 0.1% at 7300 T weighs 5.23), and the nearest
  harmonic is 111-139 T away.
- Next (v3): delta at 7300 T, everything else as v2 (its mass 3.35, Dingle temperature, g and amplitude unchanged, so
  it is still seen only at high field and in the cold sweeps). The designed trap stays; the accidental readings go.
  Answers change (delta's frequency), so the generator runs again.

### v3 (T-1563 v3, job 22636, pass@3 ended 2026-11-13 01:28): 2 of 3 solved, QUALIFIED

- Sol 6.1, rewards [1, 1, 0]. Agent times 16, 10 and 8 min (51, 35 and 27 episodes), cost $0.60, $0.41 and $0.28.
  Bundle in `work/dhva-fermi-surface/v3/pass3/` (`pass3.zip`, untrusted extraction under `x/`, `summary.md`);
  answers in `work/dhva-fermi-surface/v3/attempts/programs/aK/orbits.json`, digests in `attempts/attempt-K.txt`.
- **P3 ID P3-2F9B-5B0C-A1B0** (this revision only), for DAS 4034278; the user submits on DAS. The full review runs
  on v4 (v3's files, job 24020); then pass@8 on Astra 6, which must land at 1-6 of 8.
- a1 and a2: all six orbits; delta at 7300.56 and 7300.38 T (+0.008%, +0.005%), mass 3.247 and 3.24 (-3.1%,
  -3.3%); the other five within 0.003% and 4% (a1 beta belly 1.278, -0.9%).
- a3: the five lighter orbits right (beta belly's mass 1.419, +10%, inside the band), delta missing. It never looked
  at a high-field window or mentioned a peak near 7300 T: the designed trap ("A heavy orbit seen only at high field").
- Moving delta clear of 8 x gamma and of mass-matching combinations did what v2's analysis predicted: the attempts
  that searched at high field kept delta; the one that did not, missed it. The internal field again fell in every
  attempt.

## Pitfalls

- A Python run redirected to a file buffers its output until it ends; use `python -u` for a long audit in the
  background.
