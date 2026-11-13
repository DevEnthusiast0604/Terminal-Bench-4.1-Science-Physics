# gamma-decay-scheme: task log

Read this log and `logs/STATUS.md` before opening any task file. Entries are summaries: the numbers, the decision and
where the evidence lives. All times are UTC (the platform shows UTC; this PC is UTC-8).

## Identity

| Field | Value |
|---|---|
| Source | `tasks/active/gamma-decay-scheme/` (output task, data file, `RUN_PROGRAM=0`; scaffolded 2026-11-06) |
| Platform | **T-1383** (submitted 2026-11-06 02:02) |
| DAS Task ID | **4011092** (given by the user 2026-11-06 for this task) |
| Category | Science / Physics |
| Target | pass@3 solved **1–2 of 3** on Sol 6.1 |
| P3 IDs pasted into DAS | none yet |
| Evidence | `work/gamma-decay-scheme/v<N>/`: `design.md`, `explore/`, later criteria reports, pass@3 |
| Master generator | `tasks/active/gamma-decay-scheme/tests/generate.py` (`work/gamma-decay-scheme/v1/generate_draft.py` is its copy) |

## State now

- **2026-11-06 00:30**: started on the user's "generate high difficult physics task and submit from now on" and "also
  watch the pipeline. try to re-work until it pass pass@3 step". This replaces the 11-05 23:51 stop. DAS 4011092 given.
- **2026-11-06 02:02**: v1 submitted through `#submit` with DAS 4011092; queued as **T-1383**, IN REVIEW, quick check
  queued. No note. Poller started (`poll_pipeline.py T-1383 43200 180`). See Version history (v1).
- **2026-11-06 02:12**: correction: the request above came at 00:32 (transcript); 00:30 was an estimate.
- **02:58**: v2 uploaded with Upload the fix, no note (upload 2 of 5 on 11-06); quick check queued. The instruction now states the selection rule the quick check asked for (job 18754, discoverable): of the schemes that agree with the data, the one with the fewest levels. README, tests/checks.txt and the judge's docstrings say the same; data and expected.json unchanged. See Version history (v2).
- **2026-11-09 01:58**: the platform is now the TB4.1 Queue (toolkit 3.7.0, 2026-11-08). My tasks is empty: T-1383 and v2's queued quick check are gone, and `/task/T-1383` answers "not found". The poller had stopped on 11-06 at 12:09 (three status time-outs). On the user's "download the updated Toolkit", kit 3.7.0 is installed. Next: move the task to the TB 4.1 template (dependency locks, the new `tests/test.sh`, README metadata) and submit it again as a new task with DAS 4011092.
- **2026-11-09 02:02**: v3 submitted to the TB4.1 Queue as a new task through `#submit` with DAS 4011092: **T-0020** (its v1), IN REVIEW, quick check running from 02:02. No note. Upload 1 of 5 on 11-09; 1 of 2 new tasks left today. Poller started (`poll_pipeline.py T-0020 43200 180`). See Version history (v3).
- **2026-11-09 14:05**: background work paused at the user's request ("pls stop background working at the moment. I will let you know when needed"): poller `bsqfpq20s` stopped. Its status line had not changed since 02:48 (T-0020 v1: pass@3 queued from 02:45, no new card). Its last poll, at 14:04, got the TB4.1 sign-in page instead of the task (1 miss), so the session may have expired. Nothing watches T-0020 until the user says so.
- **2026-11-09 17:22**: the platform restored T-1383 (DAS 4011092, 3 versions; T-0851 and T-0610 are listed again) and `/task/T-0020` says "not found": the 02:02 upload is now **T-1383 v3** (job 19128, which was 137). v3: quick check PASS (36 of 40 pass), pass@3 **TOO EASY, 0 of 3 failed** (14:37, Sol 6.1), status Sent back (REWORK). Two unseen cards logged. Next: review pass@3 (`gate/full/19128.zip`), mark the cards seen, harden as v4, Upload the fix.
- **2026-11-09 17:59**: v3's pass@3 reviewed (3 of 3, all exact; analysis under "pass@3 analyses"). v4 built in `tasks/active/gamma-decay-scheme/`: a real 511.00 keV transition hidden in the annihilation peak. Generator run (the user was told first): 16 levels, 31 transitions; the reference matches (intensities within 10.4 percent, the new line 0.80 for 0.853). `release.sh --check` passes under kit 3.8.2. At 17:58 the platform answered "the platform is busy"; the upload waits for it. Edit scripts `work/gamma-decay-scheme/v4/explore/edit13.py` to `edit19.py`.
- **18:02**: v4 uploaded with Upload the fix, no note (upload 2 of 5 on 11-09); quick check queued. v4: a real 511.00 keV transition (3092.6 -> 2581.6 keV, I 0.853) hidden in the annihilation peak, shown only by the narrow part of that peak and by its coincidences; new data, expected.json and checks.txt from the generator; the reference splits the 511 keV peak with the background run's annihilation shape; README updated. Instruction, grader and requirements unchanged. See Version history (v4).
- **2026-11-09 19:07**: the poller (`brhvr59o1`) exited 2 at 19:01. From 18:55 three polls got the app's shell (title "TB4.1 Queue") without the task view; from 19:03 the platform did not answer at all (no response in 30 s). At 19:06 it answered again (HTTP 401 to a request without the session), and `status` showed the session intact: T-1383 v4's quick check still queued from 18:02, no new card. An outage, not a sign-out. Poller restarted (`bic7p1a3f`).
- **2026-11-10 01:54**: v4's quick check (job 19370) stopped at the static checks: TB 4.1's `check-task-fields.sh` fails a README whose Author line is not `Name (email)` exactly as task.toml declares it (kit 3.8.2's `lint/readme_format.py` and its template and example say the same; local lint only warns). Our README has the name alone, by the user's rule that the email appears only in task.toml. Asked the user; v4 waits. No upload on 11-10 yet (0 of 5).
- **01:59**: v5 uploaded with Upload the fix, no note (upload 1 of 5 on 11-10); quick check queued. README's Author line is now 'Name (email)' exactly as task.toml declares it: TB 4.1's check-task-fields.sh failed v4 on it (job 19370; user: "Add it, upload again"). Nothing else changed. See Version history (v5).
- **2026-11-10 07:45**: v5's quick check passed (job 19705, 07:42; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass). pass@3 running on Sol 6.1 from 07:42. Card marked seen 07:45; poller restarted.
- **2026-11-10 08:10**: v5's pass@3: 0 of 3 (job 19705, 07:59; card seen 08:08). All three set the 511 keV peak aside by energy and missed the 511.00 keV line; a2 and a3 had everything else right. Fair, so v6 eases the noticing step: one instruction sentence (no peak named), R13, README. Next: `release.sh` v6.
- **08:11**: v6 uploaded with Upload the fix, no note (upload 2 of 5 on 11-10); quick check queued. v5 pass@3 0/3 (job 19705): all three set the 511 keV peak aside by energy. The instruction now says: "A transition can share its peak with radiation of another origin, whatever the peak's energy." (bound as R13); README updated. Data, expected.json, checks.txt, generate.py and solve.py unchanged. See Version history (v6).
- **2026-11-10 12:07**: v6's quick check passed (job 20055, 12:03; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass). pass@3 running on Sol 6.1 from 12:03. Card marked seen 12:07; poller restarted.
- **2026-11-10 12:42**: v6 QUALIFIED: pass@3 2 of 3 (job 20055, 12:33; card seen 12:41). P3 ID **P3-6AEE-4ACB-FA2A**, given to the user, who submits on DAS 4011092 (user, 12:38: "There is no need to submit on DAS automatically. I will do it."). The full review runs on the same files as the platform's **v7** (job 20271, queued 12:33, running by 12:37; its zip is byte-identical to the local v6 zip, sha256 `178bc2e8…a5fb`). The card says not to upload a new version meanwhile. Poller restarted for the review's decision.
- **2026-11-10 14:12**: the full review (v7 = v6's files, job 20271) finished at 14:04; status "Waiting for a reviewer". A person settles three failed checks: the answer leak (critical, "Return the task": v6's proviso "A transition can share its peak with radiation of another origin, whatever the peak's energy." against the README's key realization), `contract_probes` (a counterexample the tests may not reject; not named on the page) and `contract_generality` (one generator assumption not settled by a quoted rule; not named). No upload until the decision (the card: "Nothing to upload for now"). Poller restarted.
- **2026-11-10 18:08**: SENT BACK 17:56 (REWORK). Fixing as v8 (the platform's next version; v7 was v6's files): no proviso; a stated and tested consistency rule; the 511 keV line strengthened in the data (TARGET: M's β feeding 9.5 -> 11.75 and its branch to H 6 -> 31, H's β feeding 5.0 -> 2.75, so every other line keeps its intensity and the 511 keV line feeds about half of H, I about 4.4). New data and answers: the generator runs after telling the user.
- **18:17**: v8 uploaded with Upload the fix, no note (upload 4 of 5 on 11-10); quick check queued. v7 (= v6) was sent back by the reviewer (17:56). The instruction loses the proviso (an answer leak) and gains a stated rule, energy_keV within 0.5 keV of from_keV minus to_keV, tested by test_transition_consistency (R13). The 511 keV line is strengthened in the data (I 0.853 -> 4.41, feeding half of the 2581.6 keV level); new data, expected.json and checks.txt from the generator; README follows. See Version history (v8).
- **2026-11-10 18:17**: v8 uploaded 18:16 with Upload the fix, no note (upload 3 of 5 on 11-10); task digest `sha256:c57359ae…a524`; quick check queued. Local and platform numbers agree again from v8: the archive `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v7-20261110.zip` holds the v6 files, which are the platform's v7 (byte-identical, sha256 `178bc2e8…a5fb`); no separate v6 archive exists. The generator ran 18:10-18:11 after telling the user (new data, expected.json, checks.txt; the reference inside every tolerance: levels 0.090 keV, energies 0.060 keV, |from - to - energy| 0.010 keV, intensities 7.1 percent, half-life 0.00 percent, isomer 0.6 percent; the 511 keV narrow part 63967 +- 1023 counts, I 4.31 against 4.41). Edit scripts: `work/gamma-decay-scheme/v8/explore/edit32.py` (instruction, requirements, grader, generator) and `edit33.py` (README). Poller restarted.
- **2026-11-10 23:52**: v8's quick check passed (job 20645, 23:48; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass). pass@3 running on Sol 6.1 from 23:48. Card marked seen 23:52; poller restarted.
- **2026-11-11 00:09**: v8's pass@3 3 of 3 (job 20645, 00:00; card seen 00:09). Building v9: the 511 keV line at I about 3.0 (TARGET: M's beta feeding 10.85, its branch to H 21; H's beta feeding 3.65) and the parent's pair-production annihilation doubled (6.0e-4 per decay), so the line's intensity needs the two shapes or coincidences; new data from the generator after telling the user.
- **00:28**: v9 uploaded with Upload the fix, no note (upload 2 of 5 on 11-11); quick check queued. 511 keV line at I 2.99 (M beta 10.85, M->H 21, H beta 3.65) and the parent's pair-production annihilation doubled to 6.0e-4 per decay: read as one line the peak gives 4.34 whole or 4.10 less the room's share, the two shapes or coincidences give it; reference doublet members from the gates that agree within two standard errors (one stray gate had made the search admit three 16-level schemes; one again); checks.txt names the coincidence route's furthest pair; README figures from the v9 checks See Version history (v9).
- **2026-11-11 00:29**: v9 build notes. The first v9 generator run (00:10, after telling the user) gave `[placement search]` 3 schemes with 16 levels (6 with 17): extra levels at 2041.2 and 2500.8 keV, i.e. 1011.4 keV moved to a beta-fed level above 1489.6 keV and the 551.8/647.8 order swapped. Cause: the reference's doublet logic, not the physics. The 898.3 keV gate (fed through the isomer) read the 647 keV doublet at 646.69 keV, and the old rule (lower member = gates within 0.15 keV of the lowest centroid) took that gate alone, so the 551.8 and 1011.4 keV gates (647.37, 647.39: both members) fell undecided. Fix in `solution/solve.py` `split_doublets` (`work/gamma-decay-scheme/v9/explore/edit40.py`): a member's energy is the mean of the gates that agree within two standard errors with the lowest (highest) centroid that holds to two standard errors. Rerun 00:20 (data and `expected.json` byte-identical): 1 scheme with 16 levels, 2 with 17 (extra 2917.6 keV), as in v8; reference intensities within 8.4 percent (was 12.0). `edit41.py` makes `checks.txt` name the coincidence route's furthest pair (318.4 with 1606.6 keV at 1.337, the 524.3+1082.3 sum in the 1606.6 keV peak; the only pair past 0.25); rerun 00:23, data identical. README figures from these checks (`edit42.py`). Upload 2 of 5 on 11-11 is right: dhva-fermi-surface's first upload (00:01) counts too.
- **2026-11-11 06:12**: v9's quick check passed (job 21129, 06:09; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass). pass@3 running on Sol 6.1 from 06:09. Card marked seen 06:11; poller restarted.
- **2026-11-11 06:37**: v9 QUALIFIED: pass@3 1 of 3 (job 21129, 06:26; card seen 06:36). P3 ID **P3-4DCE-3D5C-5E63**, given to the user, who submits on DAS 4011092 (never by this session). The full review runs as v10 (byte-identical to the v9 zip), queued 06:26. Don't upload while it runs.
- **2026-11-11 10:34**: v10's full review (= v9's files, job 21495) finished 08:23: "A reviewer decides next"; a person settles `contract_probes` and `contract_generality` (no answer leak now). Waiting for a reviewer; no upload. P3 ID P3-4DCE-3D5C-5E63 is with the user for DAS 4011092.
- **2026-11-11 18:34**: v10 SENT BACK: pass@8 on Astra 6 solved 8 of 8 (18:12, TOO EASY; card seen 18:33). Every attempt exact (16 levels, 31 transitions, isomer), worst intensity error 7-10% against 25%. Next: v11, harder for Astra 6 without changing what the instruction asks, while Sol 6.1 keeps at least 1 of 3. The P3 ID P3-4DCE-3D5C-5E63 stays spent; a qualifying v11 pass@3 gives a new one.
- **18:57**: v11 uploaded with Upload the fix, no note (upload 4 of 5 on 11-11); quick check queued. New level at 2721.70 keV (beta-fed): a clean 1879.00 keV line to 842.70 keV and a weak 1081.40 keV line (I 1.22) to 1640.30 keV, 0.9 keV under E->B 1082.30 keV (I 13.02), seen only in the gate on the 1322 keV doublet (centroid 1081.44 keV; the 1082 keV peak's width 1.02 of resolution). 511 keV line back to v8 (M beta 11.75, M->H 31, H beta 2.75, I 4.30; pair-production annihilation 3.0e-4). solve.py: a doublet member under a quarter of its peak takes its first share from the singles centroid, a gate on the strong member leaves it undecided, and split_moved shares the peak from the gates below each member. 17 levels, 33 transitions; reference within 9.1% (the weak member), one scheme at 17 levels. README and tests/checks.txt updated; instruction unchanged. See Version history (v11).
- **2026-11-11 18:58**: v11 design notes in `work/gamma-decay-scheme/v11/design.md`. The weak 1081.40 keV line aims at what the pass@8 attempts skipped: a4 dropped gated peaks within 4 keV of a listed peak, tested only unplaced peaks against level differences and left the doublets out of its check for unexpected coincidences; a8 matched level differences within 0.7 keV (X - Da lies 0.82 keV from the 1082.22 keV peak). The 511 keV line went back to v8 (Sol 6.1 3 of 3 there) so that the new trap carries the difficulty for both models. Generator run once (the user was told first): reference within 9.1%, one scheme at 17 levels. Poller running.
- **2026-11-12 02:21**: the poller started 18:57 exited 2 at 02:10 after three status calls in a row timed out (the task page did not finish loading within 30 s; earlier 502 gateway errors 19:04-19:07 and 21:58-22:01). Not a sign-out: the debug Chrome was up, the site answered a plain request at once, and a direct `supertasker.py status T-1383` at 02:17-02:20 worked (about 170 s). v11's quick check is still queued (since 2026-11-11 18:57), no unseen card. Poller restarted.
- **2026-11-12 05:38**: v11's quick check passed (job 22164, 05:34; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass). pass@3 running on Sol 6.1 from 05:34. Card seen 05:38; poller restarted. 1 or 2 of 3: the new P3 ID to the user for DAS 4011092; 3 of 3: harden; 0 of 3: check whether every attempt missed the 1081.40 keV line and ease it (design.md).
- **2026-11-12 06:02**: v11 QUALIFIED: pass@3 1 of 3 on Sol 6.1 (job 22164, 05:53; card seen 06:02). P3 ID **P3-8546-0E6F-2BCD**, given to the user, who submits on DAS 4011092 (never by this session). a1 and a3 missed only the 1081.40 keV transition under E->B; a2 exact. The full review runs as v12 (= v11's files), queued 05:53. Don't upload while it runs; then pass@8 on Astra 6.
- **2026-11-12 07:37**: v12's full review (= v11's files, job 22785) finished 07:32: "A reviewer decides next"; a person settles `contract_probes` and `contract_generality` (1 generator assumption, settled by a quoted rule). Waiting for a reviewer, then pass@8 on Astra 6; no upload. P3 ID P3-8546-0E6F-2BCD is with the user for DAS 4011092.
- **2026-11-12 19:23**: the poller started 07:37 saw "Waiting for a reviewer" all day (one slow call at 12:41) and exited 2 at 19:18 after three status calls in a row timed out (the task page did not load within 30 s). Not a sign-out: the debug Chrome was up and the site answered a plain request at once; a direct status at 19:21 timed out the same way. No new card seen. Poller restarted.
- **2026-11-12 21:45**: v12 SENT BACK: pass@8 on Astra 6 solved 7 of 8 (21:09, TOO EASY; card seen). a4 alone missed the 1081.40 keV line; the other seven found it by the level difference 2721.7 - 1640.3 or in the 1321.9 keV gate. Next: v13 (draft in `work/gamma-decay-scheme/v13/`), harder for Astra 6 without changing what the instruction asks, while Sol 6.1 keeps at least 1 of 3. P3-8546-0E6F-2BCD is spent; a qualifying v13 pass@3 gives a new P3 ID for DAS 4011092.
- **22:39**: v13 uploaded with Upload the fix, no note (upload 2 of 5 on 11-12); quick check queued. v13: the weak 1081.4 keV transition now leaves a level at 1399.8 keV fed only by the beta decay (557.1 keV to 842.7 keV) for 318.4 keV, 0.9 keV under 1082.3 keV; its one coincidence partner, 318.4 keV, lies below the strong line too, so no gate isolates it (v12's 2721.7 keV level and its gate route dropped). solve.py: hidden_members fits level differences near strong peaks with a tailed line shape; the search places lines on shared peaks after the clean ones; checks.txt lists the other 17-level scheme and why the coincidences exclude it; README from the v13 checks See Version history (v13).
- **2026-11-13 05:56**: v13 quick check PASSED (05:54; 36 of 40 as in earlier passes); pass@3 on Sol 6.1 running. Card logged, not yet reviewed. Next: review the criteria reports, mark the card seen, restart the poller.
- **2026-11-13 05:59**: v13 quick-check card reviewed (31 pass, 0 fail, 3 N/A, `novel` deferred; extra 5 of 5) and marked seen. pass@3 on Sol 6.1 running since 05:54; poller restarted.
- **2026-11-13 07:25**: v13 SENT BACK: pass@3 on Sol 6.1 solved 0 of 3 (07:23, TOO HARD). Card logged, not yet reviewed. Next: fetch the pass@3 bundle, find where the attempts failed, mark the card seen, then make v14 somewhat easier there.
- **2026-11-13 07:32**: v13 pass@3 card reviewed and marked seen. All three attempts missed only the hidden 1081.40 keV line: they placed 1399.8 keV late, by its weak 557.1 keV line, after matching level differences to peaks. Next: v14 with 557.1 keV a regular line and a somewhat stronger hidden line (draft in `work/gamma-decay-scheme/v14/`).
- **07:50**: v14 uploaded with Upload the fix, no note (upload 1 of 5 on 11-13); quick check queued. v14: more beta feeding to the 1399.8 keV level (1.9 to 3.6, branches 55/45), so its 557.1 keV line is a regular line (I 2.98) and the level stands from the start; the hidden 1081.4 keV line is now I 2.44, a fifth of 1082.3 keV, and still no gate isolates it. solve.py: the hidden member's share comes from the 318.4/524.3 keV gates (the shape fit's share moves with the energy scale); a partner with more than 1.15 of a one-cascade doublet's gamma rays per gamma ray of its own sees both members (no false 17-level schemes); generate.py names what falls outside a tolerance; README from the v14 checks See Version history (v14).
- **2026-11-13 13:41**: v14 quick check PASSED (13:39; 36 of 40 as before); pass@3 on Sol 6.1 running. Card logged, not yet reviewed. Next: review the criteria reports, mark the card seen, restart the poller.
- **2026-11-13 13:45**: v14 quick-check card reviewed (31 pass, 0 fail, 3 N/A, `novel` deferred; extra 5 of 5) and marked seen. pass@3 on Sol 6.1 running since 13:39; poller restarted.
- **2026-11-13 14:59**: v14 pass@3 on Sol 6.1 still running (status at 14:58: "running, 0 of 3 ended", 0 unseen cards). The poller started at 13:45 stopped with exit 2 at 14:31: status calls timed out (170 s) at 14:19, 14:25 and 14:31, and a manual call then timed out in `connect_over_cdp` (180 s). Cause and fix under Pitfalls. Status took 32 s at 14:58; poller restarted.
- **2026-11-13 17:53**: the poller for T-1383 (running since 14:59) stopped at the user's request ("please stop background"). Its polls, every 180 s, found the page unchanged throughout: v14 pass@3 on Sol 6.1 running, 0 of 3 ended, 0 unseen cards. Nothing watches T-1383 now; restart the poller only when the user resumes the work.
- **2026-11-13 18:55**: work resumed at the user's request. At 18:37 no Chrome was running; it was started again on port 9224 and was signed in. From about 18:41 the user moved the workspace from `Documents\Tango-arunufo` to `OneDrive\Documents\Tango-arunufo` (the folder root is now there; the old folder is empty). The debug Chrome was closed while the profile moved and started again at 18:52 on `OneDrive\Documents\Tango-arunufo\.supertasker-profile`, still signed in. The platform restarted v14's pass@3 at 18:44 after a fault on its side (card above).
- **2026-11-13 19:17**: the user asked why checks keep timing out. Measured: status 13 s, connect 4 s; the tabs kept open for the user hold 10 and 6 utility worlds after 24 min (BRIEFING point of this time). Poller restarted at 600 s instead of 180 s. v14 pass@3 still running (restarted by the platform at 18:44).
- **2026-11-13 19:18**: v14 pass@3 on Sol 6.1 QUALIFIED at 19:16 (1 of 3 solved; the run the platform restarted at 18:44). P3 ID **P3-B911-F9F1-EDFA** (this revision only), for the user to paste into DAS 4011092. The full review runs as v15 (= v14's files), queued 19:16; pass@8 on Astra 6 comes with it (1-6 of 8 qualifies). No uploads until the review decides. Next: analyse the pass@3 bundle, mark the card seen, watch the review.
- **2026-11-13 19:20**: the v14 pass@3 card is reviewed and marked seen; analysis under pass@3 analyses (a1 exact; a2 missed the hidden 1081.40 keV line; a3 missed the weak 1092.00 keV line). The full review (v15) is queued; poller at 600 s.
- **2026-11-13 19:37**: one session now watches every task (BRIEFING point of this time); T-1383 is polled by the combined poller `T-1383,T-1563,T-1519` at 600 s. Kit 3.8.7 installed (19:32); v14 lints PASS under it.

## Current design (v1, 2026-11-06)

Full design: `work/gamma-decay-scheme/v1/design.md`. The agent gets a moving-tape β-decay run on an invented nucleus
(singles by time in cycle, prompt, random and delayed γγ matrices, room background, three source runs) and writes the
level scheme: parent half-life, 16 levels, 30 placed transitions with energies and relative intensities, the isomer's
level and half-life. Bands: 0.5 keV, 25%, 2%, 8%. The instruction names no trap and NOTES makes no promise about the
records. Traps, each with evidence in the data:

1. Production gain differs from the source runs (0.61, 1.14, 1.66 keV at 500, 1500, 2500 keV); room lines give it.
2. Escape peaks (2263.19 fits level H minus level A; 1752.21; 1507.76), room lines and cascades, annihilation.
3. Self-coincident doublet 646.9/647.8 in one cascade (split by self-coincidence).
4. Level doublet 1640.3/1641.6 (lines 1321.9/1323.2), seen only through gate centroids, width and Ritz residuals.
5. 707.9 of the daughter's own decay under the real 708.0 (whole peak about 52% high).
6. Sum peaks: 842.7 is a crossover plus a sum (4.09 against 2.71), 1171.5 a pure sum with an exact Ritz match, 965.6 a
   floating pure sum.
7. Isomer at 1963.1 keV, 168 ns, leaves only through an unseen 38.1 keV transition. Prompt pairs across it are cut to
   18.6%; the delayed matrix carries the link.
8. Ritz false friends: M−J 403.4 (granddaughter), M−H 511.0, F−B 1120.4 (room), H−A 2263.2 (escape).

Dials for later rounds. At 3/3: closer doublets, more mixed lines, weaker evidence, or a hidden-data program mode. At
0/3: first find which trap failed and check it for unfairness, then widen the doublet separation or strengthen that
trap's evidence.

## Version history

- **v1, uploaded 2026-11-06 02:02** (first submit, `supertasker.py submit`, DAS 4011092, T-1383). The design above.
  - Zip `deliveries/gamma-decay-scheme-20261106.zip`: 1996734 bytes; task digest
    `sha256:ac5b3e3514b524b0339df7af77dceedbc9c25d696d0fe255a2991f8e125d5357`.
  - Reference on the shipped data (`tests/checks.txt`): 16 levels within 0.040 keV, 30 transitions all on the right
    levels, energies within 0.020 keV, intensities within 7.7%, half-life 0.11%, isomer 2.1%, 21 s on one CPU.
  - lint: PASS, 0 FAIL, 0 WARN; scan: 0 problems. Upload 1 of 5 on 11-06.
  - Generator run during the build, reference included; the user was told. No oracle, verifier or Harbor run.
- **v2, uploaded 2026-11-06 02:58** (Upload the fix on T-1383). The instruction now states the selection rule the quick check asked for (job 18754, discoverable): of the schemes that agree with the data, the one with the fewest levels. README, tests/checks.txt and the judge's docstrings say the same; data and expected.json unchanged.
  - Zip `deliveries/gamma-decay-scheme-20261106.zip`: 1997023 bytes, 28 files; task digest `sha256:7981e5c9d60ec13c93b689117c7d777317d61f42cd37a1212ff4470e2acfbed9`; zip sha256 `429188c3…bb44`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v1-20261106.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.
- **v3, uploaded 2026-11-09 02:02** (new task on the TB4.1 Queue: T-0020, DAS 4011092; the platform's v1). The task on the TB 4.1 template (kit 3.7.0): Python dependencies from committed uv locks (`environment/locks/`, and `tests/locks/judge/` from the template), the template's new `tests/test.sh` and `tests/Dockerfile`, README metadata in the 4.1 form (Category alone, Tags as `<code>`) and one README sentence on the locks. Data, answers, instruction and grader unchanged from v2.
  - Zip `deliveries/gamma-decay-scheme-20261109.zip`: 2013353 bytes, 32 files; task digest `sha256:9b420950a1ad28a183dbf27b304b359ad81279c6464c9f3376f6f93a8dd9ad6d`; zip sha256 `c6c77406…e52e`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v2-20261106.zip`.
  - lint (kit 3.7.0): PASS, every structure check passes (73 rows, 0 FAIL, 1 WARN: the README Author line has no email, by the user's rule); scan: problems: 0.
  - Edit script `work/gamma-decay-scheme/v3/explore/edit12.py`; the lock was made with uv 0.10.8 (`uv lock --directory environment/locks`): asciinema 2.4.0, numpy 2.3.3, scipy 1.18.1, with cp312 manylinux x86_64 wheels.
- **v4, uploaded 2026-11-09 18:02** (Upload the fix on T-1383). v4: a real 511.00 keV transition (3092.6 -> 2581.6 keV, I 0.853) hidden in the annihilation peak, shown only by the narrow part of that peak and by its coincidences; new data, expected.json and checks.txt from the generator; the reference splits the 511 keV peak with the background run's annihilation shape; README updated. Instruction, grader and requirements unchanged.
  - Zip `deliveries/gamma-decay-scheme-20261109.zip`: 2029775 bytes, 32 files; task digest `sha256:eebfdfcc38bcc5d2b9b1197ce7ec9ca79848d623503715d2c56e78acacdf8e47`; zip sha256 `24b25349…2614`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v3-20261109.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.
- **v5, uploaded 2026-11-10 01:59** (Upload the fix on T-1383). README's Author line is now 'Name (email)' exactly as task.toml declares it: TB 4.1's check-task-fields.sh failed v4 on it (job 19370; user: "Add it, upload again"). Nothing else changed.
  - Zip `deliveries/gamma-decay-scheme-20261110.zip`: 2029793 bytes, 32 files; task digest `sha256:7065d1bf755e48094c04bcc2a777ba918ac9721e809bda7190e705d97a4fb7f8`; zip sha256 `bcb864fc…f486`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v4-20261109.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.
- **v6, uploaded 2026-11-10 08:11** (Upload the fix on T-1383). v5 pass@3 0/3 (job 19705): all three set the 511 keV peak aside by energy. The instruction now says: "A transition can share its peak with radiation of another origin, whatever the peak's energy." (bound as R13); README updated. Data, expected.json, checks.txt, generate.py and solve.py unchanged.
  - Zip `deliveries/gamma-decay-scheme-20261110.zip`: 2030012 bytes, 32 files; task digest `sha256:61344b233e9e73478f0d734db099121bb3bfc7e3a6503dea04e3134c5635562f`; zip sha256 `178bc2e8…a5fb`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v5-20261110.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.
- **v8, uploaded 2026-11-10 18:17** (Upload the fix on T-1383). v7 (= v6) was sent back by the reviewer (17:56). The instruction loses the proviso (an answer leak) and gains a stated rule, energy_keV within 0.5 keV of from_keV minus to_keV, tested by test_transition_consistency (R13). The 511 keV line is strengthened in the data (I 0.853 -> 4.41, feeding half of the 2581.6 keV level); new data, expected.json and checks.txt from the generator; README follows.
  - Zip `deliveries/gamma-decay-scheme-20261110.zip`: 2050631 bytes, 32 files; task digest `sha256:c57359ae0c591789a1d9a2d2765a583902ba096791f2a7ba1af1c80f1d30a524`; zip sha256 `69557550…ede6`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v7-20261110.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.
- **v9, uploaded 2026-11-11 00:28** (Upload the fix on T-1383). 511 keV line at I 2.99 (M beta 10.85, M->H 21, H beta 3.65) and the parent's pair-production annihilation doubled to 6.0e-4 per decay: read as one line the peak gives 4.34 whole or 4.10 less the room's share, the two shapes or coincidences give it; reference doublet members from the gates that agree within two standard errors (one stray gate had made the search admit three 16-level schemes; one again); checks.txt names the coincidence route's furthest pair; README figures from the v9 checks
  - Zip `deliveries/gamma-decay-scheme-20261111.zip`: 2046319 bytes, 32 files; task digest `sha256:f94138281b667b75352b41d118a99aef899fbbdf0ece4a80a3803c48c90eb47a`; zip sha256 `b81f8481…809a`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v8-20261110.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.
- **v11, uploaded 2026-11-11 18:57** (Upload the fix on T-1383). New level at 2721.70 keV (beta-fed): a clean 1879.00 keV line to 842.70 keV and a weak 1081.40 keV line (I 1.22) to 1640.30 keV, 0.9 keV under E->B 1082.30 keV (I 13.02), seen only in the gate on the 1322 keV doublet (centroid 1081.44 keV; the 1082 keV peak's width 1.02 of resolution). 511 keV line back to v8 (M beta 11.75, M->H 31, H beta 2.75, I 4.30; pair-production annihilation 3.0e-4). solve.py: a doublet member under a quarter of its peak takes its first share from the singles centroid, a gate on the strong member leaves it undecided, and split_moved shares the peak from the gates below each member. 17 levels, 33 transitions; reference within 9.1% (the weak member), one scheme at 17 levels. README and tests/checks.txt updated; instruction unchanged.
  - Zip `deliveries/gamma-decay-scheme-20261111.zip`: 2085211 bytes, 32 files; task digest `sha256:ebda24280c3395f7ca3ffee3607271e8871352533164ea0e9d52bc8dc966eaea`; zip sha256 `c313a75d…97a3`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v10-20261111.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.
- **v13, uploaded 2026-11-12 22:39** (Upload the fix on T-1383). v13: the weak 1081.4 keV transition now leaves a level at 1399.8 keV fed only by the beta decay (557.1 keV to 842.7 keV) for 318.4 keV, 0.9 keV under 1082.3 keV; its one coincidence partner, 318.4 keV, lies below the strong line too, so no gate isolates it (v12's 2721.7 keV level and its gate route dropped). solve.py: hidden_members fits level differences near strong peaks with a tailed line shape; the search places lines on shared peaks after the clean ones; checks.txt lists the other 17-level scheme and why the coincidences exclude it; README from the v13 checks
  - Zip `deliveries/gamma-decay-scheme-20261112.zip`: 2068330 bytes, 32 files; task digest `sha256:9734bed45bf25fee979c6a6e6275ded8b5587933373ae1c817c1c3452641b7e1`; zip sha256 `fee546a1…fc7e`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v12-20261111.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.
- **v14, uploaded 2026-11-13 07:50** (Upload the fix on T-1383). v14: more beta feeding to the 1399.8 keV level (1.9 to 3.6, branches 55/45), so its 557.1 keV line is a regular line (I 2.98) and the level stands from the start; the hidden 1081.4 keV line is now I 2.44, a fifth of 1082.3 keV, and still no gate isolates it. solve.py: the hidden member's share comes from the 318.4/524.3 keV gates (the shape fit's share moves with the energy scale); a partner with more than 1.15 of a one-cascade doublet's gamma rays per gamma ray of its own sees both members (no false 17-level schemes); generate.py names what falls outside a tolerance; README from the v14 checks
  - Zip `deliveries/gamma-decay-scheme-20261113.zip`: 2075881 bytes, 32 files; task digest `sha256:eba494d847fd276daa0635cb7b404f7d064e276ad9d3592d812b53d070f90722`; zip sha256 `5bcfd4b4…0613`.
  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v13-20261112.zip`.
  - lint: PASS, every structure check passes; scan: problems: 0.

## Platform updates

| Card time (UTC) | Title | Result | Seen |
|---|---|---|---|
| 2026-11-06 02:52 | the quick check found something to fix (job 18754) | v1: 34 of 39, 1 FAIL `discoverable`: the instruction asks for every level and does not exclude the 17-level scheme that `tests/checks.txt` documents. `oracle_investigates` FAIL-PENDING-DISPOSITION on the same point (1 of 3 draws, does not block). 35 criteria: 31 pass, 3 N/A, `novel` deferred. | no |
| 2026-11-06 02:52 | the same card, reviewed | Marked seen 02:57. Fixed in v2: the instruction states the rule of the fewest levels. | yes |
| 2026-11-09 02:45 | the quick check passed (T-0020 v1 = local v3) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files." Poller exit 0 at 02:47. | no |
| 2026-11-09 02:45 | the same card, reviewed | Marked seen 02:48. Job 137 (reviewer astra, gpt-6.1-sol, 1 draw): 35 criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, `artifact_efficiency`), `novel` NOT_PROVIDED (deferred to the full review); 5 extra all pass (`discoverable` and `oracle_investigates` too, v1's two failures). `task_readme` passed with the Author line without the email. Reports in `work/gamma-decay-scheme/v3/criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |
| 2026-11-09 14:37 | pass@3 solved 3 of 3 (T-1383 v3 = the 02:02 upload, job 19128) | "The model solved all three attempts: the task is too easy. Make it harder, lint, and upload it again for a new review." Version row: pass@3 TOO EASY, 0 of 3 failed; Platform: sent back (SBQ) 14:37; task status Sent back (REWORK). Found at 17:22 (the poller had been stopped at 14:05 at the user's request). | no |
| 2026-11-06 (shown as "Nov 6") | the quick check did not finish (T-1383 v2, job 18856) | "The quick check stopped before it had a result (a platform fault, not your task). Upload the task again; if it stops again, tell your team lead." First shown 2026-11-09 17:22, after the platform restored T-1383. v2's content went up again as v3 (T-0020 at 02:02). | no |
| 2026-11-09 14:37 | pass@3 solved 3 of 3, reviewed | Marked seen 18:00. Analysis under "pass@3 analyses" (v3): all three exact; v4 hardens with a real 511.00 keV line in the annihilation peak. | yes |
| 2026-11-06 ("Nov 6") | the quick check did not finish, reviewed | Marked seen 18:00. A platform fault on v2's quick check; v2's content went up again as v3, which passed its quick check. Nothing to do. | yes |
| 2026-11-10 01:50 | the quick check did not finish (T-1383 v4) | "The quick check stopped before it had a result (a platform fault, not your task). Upload the task again; if it stops again, tell your team lead." The card also lists a FIX: "README.md author metadata omits the email address specified in task.toml. Set the author metadata in README.md to '<name> (<email>)' so it matches task.toml exactly." Version row: quick check failed, View report; task status Did not finish (REWORK). Queued 18:02, running from about 01:48, ended 01:50. Poller exit 0 at 01:51. | no |
| 2026-11-10 01:50 | the same card, reviewed | Marked seen 01:53. Job 19370. The report (`/job/19370/report`) says FIX NEEDED, not a platform fault: 0 failed criteria, 1 warning, 110 passed, 6 n/a; the gate "Static checks" has 1 FAIL, upstream check `check-task-fields.sh`: "README.md author metadata omits the email address specified in task.toml" (Do: Author line `<name> (<email>)`, exactly as task.toml). Warning (Accept or Waive offered): `task_readme`: "README metadata (TB 4.1): Author is not `Name (email)` as task.toml declares it". The screens, the 35 criteria and the full review did not run. 5 extra criteria ran and all pass, 3 draws each (`work/gamma-decay-scheme/v4/criteria-extra.md`). The fix conflicts with the user's rule that the email appears only in task.toml: asked the user. Nothing accepted, waived or disputed. | yes |
| 2026-11-10 07:42 | the quick check passed (T-1383 v5) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Version row: quick check PASS, 36 of 40 pass; pass@3 running on Sol 6.1, 0 of 3 ended (from 07:42). Queued 01:58, running from about 07:26. Poller exit 0 at 07:44. | no |
| 2026-11-10 07:42 | the same card, reviewed | Marked seen 07:45. Job 19705 (reviewer astra, gpt-6.1-sol, 1 draw): 35 criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, `artifact_efficiency`), `novel` NOT_PROVIDED (deferred to the full review); 5 extra all pass (3 draws). The README's Author line with the email cleared the static checks. Reports in `work/gamma-decay-scheme/v5/criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |
| 2026-11-10 07:59 | pass@3 solved 0 of 3 (T-1383 v5) | "pass@3 solved 0 of 3: the target model failed all three attempts, so the task comes back to you. A task must be solved in some but not all attempts. If they fail on something the instruction never states, or on an environment problem, fix that; if they fail at the stated difficulty, make the task somewhat easier. Then lint and upload the new version." Version row: pass@3 TOO HARD, 3 of 3 failed (Sol 6.1); Platform: sent back (SBQ) 07:59; task status Sent back. Poller exit 0 at 08:01. | no |
| 2026-11-10 07:59 | the same card, reviewed | Marked seen 08:08. Analysis under "pass@3 analyses" (v5): all three missed the 511.00 keV line, set aside by energy as a room line; fair, so v6 eases the noticing step with one instruction sentence. | yes |
| 2026-11-10 12:03 | the quick check passed (T-1383 v6) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Version row: quick check PASS, 36 of 40 pass; pass@3 running on Sol 6.1, 0 of 3 ended (from 12:03). Queued 08:11, running from about 11:46 (the poller's first sight). Poller exit 0 at 12:05. | no |
| 2026-11-10 12:03 | the same card, reviewed | Marked seen 12:07. Job 20055 (reviewer astra, gpt-6.1-sol): 35 criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, `artifact_efficiency`), `novel` NOT_PROVIDED (deferred to the full review); 5 extra all pass (3 draws, 12:02:42Z). The new instruction sentence and R13 drew no finding. Reports in `work/gamma-decay-scheme/v6/criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |
| 2026-11-10 12:33 | in review (T-1383, pass@3 of v6) | "IN REVIEW. the full review is running. Submit the task in DAS now if you haven't yet, but don't upload a new version: you get an update when the review team has decided. pass@3 is OK: 1 of 3 attempts failed. The full review has started on these exact files: you get an update when it ends. Your pass@3 is done on these files: copy its P3 ID below and paste it into the same DAS task to submit it." P3 ID **P3-6AEE-4ACB-FA2A** ("this revision only"; "Open the same task in DAS, paste the P3 ID and submit the task for review. There is no zip to upload to DAS. Never reuse an earlier P3 ID for a revised task."). Task row: IN REVIEW, 7 versions, last change 12:33, status Queued; newest version row "T-1383 · v7" (12:33) with Full review queued and "Download pass@3 (.zip, optional)". pass@3 ran on Sol 6.1 from 12:03. Poller exit 0 at 12:35. | no |
| 2026-11-10 12:33 | the same card, reviewed | Marked seen 12:41. pass@3 of v6 (job 20055): 2 of 3 solved, rewards [1, 1, 0]; the bundle's README carries P3-6AEE-4ACB-FA2A and task digest `sha256:61344b23…562f` (v6). Analysis under "pass@3 analyses" (v6). The user submits on DAS (12:38: "There is no need to submit on DAS automatically. I will do it."), so the P3 ID went to the user, not to DAS. The full review runs as the platform's v7 (job 20271), whose zip is byte-identical to the local v6 zip. Poller restarted for the review's decision. | yes |
| 2026-11-10 14:05 | in review (T-1383 v7, full review finished) | "IN REVIEW, DECIDING. the full review has finished and the review team is deciding. Submit the task in DAS now if you haven't yet, but don't upload a new version: you get an update with the decision. The review left 2 item(s) that a person has to settle. A reviewer settles them and decides what comes next: you get an update when one decides. Nothing to upload for now." TO CHECK: "Contract generality: waits for a decision. Contract-generality FAIL-PENDING-DISPOSITION: 2 generator assumption(s) traced (0 dropped): 1 settled by a quoted rule, 1 not"; TO CHECK: "Answer leak. no answer leak. The difficulty README identifies the key realization as a peak of another origin not necessarily being free of a genuine transition". P3 ID P3-6AEE-4ACB-FA2A shown again. Task row: status Waiting for a reviewer ("Next: pass@3 is done on these files: a reviewer decides what comes next."), last change 14:04; v7's Full review "under evaluation by the review team" with View report. Poller exit 0 at 14:08. | no |
| 2026-11-10 14:05 | the same card, reviewed | Marked seen 14:11. Report `/job/20271/report` ("A reviewer decides next"; text and HTML in `work/gamma-decay-scheme/v7/full-review/`): "Return the task (critical): Review the overlap proviso in instruction.md's output paragraph alongside the README's stated key realization. Does that proviso merely define the deliverable, or tell the solver the contaminated-peak insight in advance?" "Needs review: a person settles it: look at the counterexample the probe names: do the tests reject it? look at the input the finding names: does a stated rule decide it, or do two rules disagree on it?" Checks not passed (3): `contract_probes` ("83 requirement(s) (3 dropped ...), 46 cite an enforcing test; 11 probed (1 from the grader …"), `contract_generality` ("FAIL-PENDING-DISPOSITION: 2 generator assumption(s) traced (0 dropped): 1 settled by a quoted rule, 1 not; 0 pair(s) of rules judged (0 …"), `answer_leak.no_answer_leak` ("Although it does not identify the 511 keV case, it announces this central realization rather than leaving it to be inferred from the run evidence."). The page cuts the two contract texts on the server (the HTML holds no more; the page makes no data request). Nothing accepted, waived or disputed; nothing to upload. Poller restarted. | yes |
| 2026-11-10 17:56 | sent back to you (T-1383 v7 = v6's files) | Reviewer: sent back (SBQ) 17:56; task REWORK, status Sent back ("Next: Read the reviewer's note, fix the task and upload it again with Upload the fix."). Two problems to fix: (1) instruction.md line 5's proviso "A transition can share its peak with radiation of another origin, whatever the peak's energy." announces the README's key realization; the instruction must define the deliverable, members and tolerances without it, the insight coming only from the run's data. (2) the verifier checks `from_keV`, `to_keV` and `energy_keV` each on its own, never their mutual consistency: 842.7 -> 318.4 reported as 843.19 -> 317.91 with 524.30 keV (endpoints 525.28 keV apart) scored reward 1.0 on the live verifier (three judges agreed it is wrong); the fix must check consistency without tightening any field's own bound. Optional: `tests/generate.py` line 64 builds the scheme from a fixed TARGET and never exercises a tie between two placements with equally few levels; state a tie-break or add a generator case. Then: oracle 1, empty 0, new pass@3. Full note in `work/gamma-decay-scheme/v7/full-review/sent-back-note.txt`. Poller exit 0 at 17:57. | no |
| 2026-11-10 17:56 | the same card, reviewed | Marked seen 18:08. Both problems accepted as stated (the user's standing mandate: fix and resubmit). v8 plan: (1) drop the proviso; (2) a stated consistency rule, `energy_keV` within 0.5 keV of `from_keV` minus `to_keV`, as its own sentence (R9's quote stays whole), with a new test `test_transition_consistency` bound to a new R13 (and R1, R5); every honest answer so far keeps the gap within 0.10 keV (`v8/explore/gap_stats.py` over expected.json and the nine pass@3 answers of v3, v5 and v6), the reviewer's case has 0.98 keV; (3) ease through the data instead of words, since v5 (no proviso) gave 0 of 3: the 511 keV line made about five times stronger; (4) the optional tie point answered in the README (the search finds one scheme at the fewest levels, so no tie arises). | yes |
| 2026-11-10 23:48 | the quick check passed (T-1383 v8) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Version row: quick check PASS, 36 of 40 pass; pass@3 running on Sol 6.1, 0 of 3 ended (from 23:48). Queued 18:16, still queued at 23:32 by the poller. Poller exit 0 at 23:51. | no |
| 2026-11-10 23:48 | the same card, reviewed | Marked seen 23:52. Job 20645 (reviewer astra, gpt-6.1-sol): 35 criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, `artifact_efficiency`), `novel` NOT_PROVIDED (deferred to the full review); 5 extra all pass (3 draws, 23:48:22Z). `test_instruction_alignment` names the new transition-consistency check among the covered requirements. Reports in `work/gamma-decay-scheme/v8/criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |
| 2026-11-11 00:00 | pass@3 solved 3 of 3 (T-1383 v8) | "The model solved all three attempts: the task is too easy. Make it harder, lint, and upload it again for a new review." Version row: pass@3 TOO EASY, 0 of 3 failed (Sol 6.1); Platform: sent back (SBQ) 00:00; task REWORK, status Sent back. Poller exit 0 at 00:02. | no |
| 2026-11-11 00:00 | the same card, reviewed | Marked seen 00:09. Analysis under "pass@3 analyses" (v8): all three exact, the 511 keV line found by coincidences in each. v9 hardens the intensity of that line, not its noticing. | yes |
| 2026-11-11 06:09 | the quick check passed (T-1383 v9) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Version row: quick check PASS, 36 of 40 pass; pass@3 running on Sol 6.1, 0 of 3 ended (from 06:09). Queued 00:28, running by 05:50 (poller). Poller exit 0 at 06:09. | no |
| 2026-11-11 06:09 | the same card, reviewed | Marked seen 06:11. Job 21129 (reviewer astra, gpt-6.1-sol): 35 criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, `artifact_efficiency`), `novel` NOT_PROVIDED (deferred to the full review); 5 extra all pass (3 draws, 06:08:58Z). Controls as in v8 (oracle, nop, verifier-repeat, tamper, wrong-answers; every recorded reward 0 or 1). Reports in `work/gamma-decay-scheme/v9/criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |
| 2026-11-11 06:26 | in review (T-1383 v9 pass@3 QUALIFIED; full review as v10) | "IN REVIEW / the full review is running. Submit the task in DAS now if you haven't yet, but don't upload a new version: you get an update when the review team has decided. / pass@3 is OK: 2 of 3 attempts failed. The full review has started on these exact files: you get an update when it ends. / Your pass@3 is done on these files: copy its P3 ID below and paste it into the same DAS task to submit it." P3 ID **P3-4DCE-3D5C-5E63** (this revision only). pass@3 on Sol 6.1 from 06:09: 1 of 3 ended 06:22, 2 of 3 06:25. Newest version v10 (06:26), full review queued, "Download pass@3 (.zip, optional)". Poller exit 0 at 06:29. | no |
| 2026-11-11 06:26 | the same card, reviewed | Marked seen 06:36. P3 ID P3-4DCE-3D5C-5E63 given to the user for DAS 4011092 (the user submits on DAS). The v10 zip (`gate/task/21495.zip`) is byte-identical to the v9 delivery (sha256 b81f8481…809a). pass@3 bundle `gate/full/21129.zip`: README rewards [0, 1, 0], task digest f9413828…b47a. Analysis under "pass@3 analyses" (v9). Poller restarted for the full review. | yes |
| 2026-11-11 08:23 | in review (T-1383 v10 full review finished) | "IN REVIEW, DECIDING / the full review has finished and the review team is deciding. ... don't upload a new version: you get an update with the decision. / The review left 1 item(s) that a person has to settle. ... Nothing to upload for now." TO CHECK: Contract generality: waits for a decision ("Contract-generality FAIL-PENDING-DISPOSITION: 3 generator assumption(s) traced (0 dropped): 1 settled by a quoted rule, 2 not"). Status: Waiting for a reviewer; v10 "under evaluation by the review team". P3 ID unchanged (P3-4DCE-3D5C-5E63). The poller started 06:37 had stopped with the earlier session; seen by `supertasker.py status` at 10:31. | no |
| 2026-11-11 08:23 | the same card, reviewed | Marked seen 10:34. Report `/job/21495/report` ("A reviewer decides next"; text and HTML in `work/gamma-decay-scheme/v10/full-review/`): "Needs review: a person settles it"; two checks did not pass: `contract_probes` ("67 requirement(s) (3 dropped ...), 35 cite an enforcing test; 11 probed (1 from the grader …") and `contract_generality` ("FAIL-PENDING-DISPOSITION: 3 generator assumption(s) traced (0 dropped): 1 settled by a quoted rule, 2 not; 0 pair(s) of rules judged (0 …"). The page truncates both; the details come with the reviewer's decision. No answer-leak finding this time (v7 had one). Nothing answered, disputed or uploaded. Poller restarted. | yes |
| 2026-11-11 18:12 | sent back to you (T-1383 v10 pass@8 TOO EASY) | "The target model solved all 8 of its attempts, so the task is too easy and comes back to you. A task must be solved in some but not all attempts. Look for what made it easy: a step the instruction spells out, an answer the data or the tests give away, a shortcut that skips the hard part. Make the task harder there, without changing what the instruction asks for, then lint and upload the new version." Status: Sent back ("Read the note", "Upload the fix", "Withdraw"); "pass@8 ran on Astra 6." Version row v10: Full review "send back" 06:26; Reviewer "advanced to pass@k" 14:53; pass@8 TOO EASY, 0 of 8 failed, 18:12; Platform sent back (SBQ) 18:12; "Download pass@8 attempts (.zip)". Poller exit 0 at 18:13. | no |
| 2026-11-11 18:12 | the same card, reviewed | Marked seen 18:33. No reviewer note beyond the card. pass@8 bundle `gate/passk/21495.zip` in `work/gamma-decay-scheme/v10/pass8/` (x/ untrusted; outputs/a1-a8.json, summary.md, intensity_errors.txt, attempts/). Astra 6 got the whole scheme in all 8 attempts; see pass@3 analyses (v10 pass@8). Next: v11, harder for Astra 6 while Sol 6.1 keeps 1-2 of 3. | yes |
| 2026-11-12 05:34 | the quick check passed (T-1383 v11) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Status: pass@3 running ("pass@3 ran on Sol 6.1"); version row v11: Quick check "PASS, 36 of 40 pass", pass@3 "running, 0 of 3 ended" 05:34. Poller exit 0. | no |
| 2026-11-12 05:34 | the same card, reviewed | Marked seen 05:38 (`mark-seen` printed NOT CONFIRMED on the slow page; `updates` then listed the card as seen). Job 22164: 35 criteria 31 pass, 0 fail, 3 N/A, `novel` NOT_PROVIDED (deferred to the full review); 5 extra pass (`english_only`, `no_host_paths`, `harbor_format`, `discoverable`, `oracle_investigates`). Reports in `work/gamma-decay-scheme/v11/criteria-35.md` and `criteria-extra.md`. Poller restarted. | yes |
| 2026-11-12 05:53 | in review (T-1383 v11 pass@3 OK, 2 of 3 failed) | "IN REVIEW / the full review is running. Submit the task in DAS now if you haven't yet, but don't upload a new version ... pass@3 is OK: 2 of 3 attempts failed. The full review has started on these exact files ... P3 ID P3-8546-0E6F-2BCD / this revision only ... Never reuse an earlier P3 ID for a revised task." Status: Queued; version row v12 (= v11's files): Full review queued 05:53; "Download pass@3 (.zip, optional)". Poller exit 0. | no |
| 2026-11-12 05:53 | the same card, reviewed | Marked seen 06:02 (`mark-seen` printed NOT CONFIRMED on the slow page; `updates` then listed it as seen). pass@3 bundle `gate/full/22164.zip` in `work/gamma-decay-scheme/v11/pass3/` (x/ untrusted; outputs/a1-a3.json, summary.md, intensity_errors.txt, attempts/). Rewards [0, 1, 0]; see pass@3 analyses (v11). P3 ID P3-8546-0E6F-2BCD given to the user for DAS 4011092. Nothing uploaded; poller restarted for the full review. | yes |
| 2026-11-12 07:32 | in review (T-1383 v12 full review finished) | "IN REVIEW, DECIDING / the full review has finished and the review team is deciding. ... don't upload a new version: you get an update with the decision. / The review left 1 item(s) that a person has to settle. ... Nothing to upload for now." TO CHECK: Contract generality: waits for a decision ("Contract-generality FAIL-PENDING-DISPOSITION: 1 generator assumption(s) traced (0 dropped): 1 settled by a quoted rule, 0 not"). P3 ID unchanged (P3-8546-0E6F-2BCD). Poller exit 0. | no |
| 2026-11-12 07:32 | the same card, reviewed | Marked seen 07:37 (`updates` lists it as seen). Report `/job/22785/report` ("A reviewer decides next"; HTML and text in `work/gamma-decay-scheme/v12/full-review/`): "Needs review: a person settles it"; two checks did not pass: `contract_probes` ("67 requirement(s) (3 dropped ...), 34 cite an enforcing test; 11 probed (1 from the grader …") and `contract_generality` ("FAIL-PENDING-DISPOSITION: 1 generator assumption(s) traced (0 dropped): 1 settled by a quoted rule, 0 not; 0 pair(s) of rules judged (0 …"). The same pair v10's review left (3 assumptions then, 2 unsettled; 1 now, settled). No answer-leak finding. Nothing answered, disputed or uploaded. Poller restarted. | yes |
| 2026-11-12 21:09 | sent back to you (T-1383 v12 pass@8 7 of 8) | "The task is returned because it is too easy: the target model solved 7 of its 8 pass@8 attempts on this version. This version added the weak 1081.4 keV transition hidden under the stronger 1082.3 keV line, which only gated spectra reveal; most attempts still found it, so that one transition does not make the task hard enough on its own. / A task must be solved in some attempts but not all. ... Make the task harder there, without changing what the instruction asks for, then lint and upload the new version. Before the next upload, the reference solution must still score 1, an empty solution must score 0, and a new pass@3 must run on the new version." Status: Sent back (REWORK); "pass@8 ran on Astra 6"; links "View report", "Download pass@3 (.zip, optional)", "Download pass@8 attempts (.zip)". Poller exit 0 at 21:16. | no |
| 2026-11-12 21:09 | the same card, reviewed | Marked seen about 21:28 (`mark-seen` printed NOT CONFIRMED on the slow page; `updates` then listed it as seen). No reviewer note beyond the card. pass@8 bundle `gate/passk/22785.zip` in `work/gamma-decay-scheme/v12/pass8/` (x/ untrusted; outputs/a1-a8.json, summary.md, intensity_errors.txt, attempts/). Astra 6 found the hidden 1081.40 keV line in 7 of 8; see pass@3 analyses (v12 pass@8). Next: v13, harder for Astra 6 while Sol 6.1 keeps 1-2 of 3. | yes |
| 2026-11-13 05:54 | the quick check passed (T-1383 v13) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Status: pass@3 running ("pass@3 ran on Sol 6.1"); version row v13: Quick check "PASS, 36 of 40 pass", pass@3 "running, 0 of 3 ended" 05:54. Uploaded 22:39, still running at 05:52 (poller). Poller exit 0 at 05:55. | no |
| 2026-11-13 05:54 | the same card, reviewed | Marked seen 05:59 (`mark-seen` printed NOT CONFIRMED on the slow page; `updates` then listed the card as seen). Job 23827: 35 criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, `artifact_efficiency`), `novel` NOT_PROVIDED (deferred to the full review); 5 extra pass (`english_only`, `no_host_paths`, `harbor_format`, `discoverable`, `oracle_investigates`). Reports in `work/gamma-decay-scheme/v13/criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |
| 2026-11-13 07:23 | pass@3 solved 0 of 3 (T-1383 v13) | "pass@3 solved 0 of 3: the target model failed all three attempts, so the task comes back to you. A task must be solved in some but not all attempts. If they fail on something the instruction never states, or on an environment problem, fix that; if they fail at the stated difficulty, make the task somewhat easier. Then lint and upload the new version." Status: Sent back; version row v13: pass@3 "TOO HARD, 3 of 3 failed" 07:23, Platform "sent back (SBQ)" 07:23. Poller exit 0. | no |
| 2026-11-13 07:23 | the same card, reviewed | Marked seen about 07:31 (`mark-seen` printed NOT CONFIRMED on the slow page; `updates` then listed it as seen). pass@3 bundle `gate/full/23827.zip` in `work/gamma-decay-scheme/v13/pass3/` (x/ untrusted; outputs/a1-a3.json pulled with `v10/explore/pull_outputs8.py`, compared by `v13/explore/compare13.py`; digests in `v13/attempts/`). All three missed the hidden 1081.40 keV line and nothing else; see pass@3 analyses (v13). Next: v14, somewhat easier at that trap. | yes |
| 2026-11-13 13:39 | the quick check passed (T-1383 v14) | "All 40 criteria pass. pass@3 has started: three attempts by the target model on these exact files. You get another update when it ends. Do not change the task meanwhile: any edit needs a new check." Status: pass@3 running ("pass@3 ran on Sol 6.1"); version row v14: Quick check "PASS, 36 of 40 pass", pass@3 "running, 0 of 3 ended" 13:39. Uploaded 07:49. Poller exit 0 at 13:40. | no |
| 2026-11-13 13:39 | the same card, reviewed | Marked seen 13:44 (`mark-seen` printed NOT CONFIRMED on the slow page; `updates` then listed the card as seen). Job 24365: 35 criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, `artifact_efficiency`), `novel` NOT_PROVIDED (deferred to the full review); 5 extra pass. Reports in `work/gamma-decay-scheme/v14/criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |
| 2026-11-13 18:44 | pass@3 is running again (not your task) (T-1383 v14) | "pass@3 is running again on the platform's side: its last run had a fault there, and nothing in your task caused it. Nothing to do: you get an update when it ends." The v14 pass@3 started 13:39 had shown "running, 0 of 3 ended" at every poll until then. | no |
| 2026-11-13 18:44 | pass@3 is running again (not your task) (T-1383 v14) | "pass@3 is running again on the platform's side: its last run had a fault there, and nothing in your task caused it. Nothing to do: you get an update when it ends." The v14 pass@3 started 13:39 had shown "running, 0 of 3 ended" at every poll until then. Marked seen 18:56. | yes |
| 2026-11-13 19:16 | in review (T-1383 v14 pass@3 OK, 2 of 3 failed) | "IN REVIEW / the full review is running. Submit the task in DAS now if you haven't yet, but don't upload a new version ... pass@3 is OK: 2 of 3 attempts failed. The full review has started on these exact files ... P3 ID P3-B911-F9F1-EDFA / this revision only". Status: Queued; 15 versions; newest row v15 19:16 "Full review queued" (with a Cancel control: not to be pressed). Poller exit 0 at 19:17. | no |
| 2026-11-13 19:16 | the same card, reviewed | Marked seen 19:20 (`mark-seen` printed NOT CONFIRMED on the slow page; `updates` then listed the card as seen). pass@3 bundle `gate/full/24365.zip` in `work/gamma-decay-scheme/v14/pass3/` (x/ untrusted); analysis under pass@3 analyses. | yes |

## pass@3 analyses
### v3 (T-1383 v3, job 19128, pass@3 ended 2026-11-09 14:37): 3 of 3 solved, TOO EASY

- Sol 6.1 (`gpt-6.1-sol`), rewards [1, 1, 1]. Agent times 11.4, 13.5 and 7.5 min (21, 32 and 21 steps); input tokens
  0.63, 1.33 and 0.63 M. Bundle in `work/gamma-decay-scheme/v3/pass3/` (`pass3.zip`, untrusted extraction under `x/`,
  answers pulled as JSON into `outputs/` by `v3/explore/pull_outputs.py`, digests in `attempts/`).
- `tools/scheme_report.py` (`v3/pass3/summary.md`): all three exact. Levels 16 of 16, transitions 30 of 30, parent
  half-life 4.37, 4.366 and 4.37 s, isomer 1963.1 keV with 165, 168 and 167 ns.
- Intensities (`v3/explore/intensity_errors.py`): worst 8.0, 14.9 and 13.1 percent, low on weak lines fed from high
  levels (992.7, 1092.0, 1143.4 keV): summing-out left uncorrected. A 10 percent band would have passed only a1, but the
  reference itself was 7.7 percent off, so the band was not the lever.
- Every trap fell to standard tools: the gain shift from room lines, time-profile shares (the 708 keV split), gated
  centroids for both doublets, sum peaks from the coincidence count over 7, escape peaks from 56Co ratios, the 38 keV
  isomeric exit from the delayed matrix.
- Shortcut in all three: the 511 keV peak set aside by its energy before any analysis (a1 `exclude=[...,511,...]`, a2
  `known=[...,511.,...]`, a3 `e!=511`), and the level differences that land on peaks of another origin (511.0 and
  403.4 keV) dismissed as "accounted for by summing, annihilation, or non-parent activity" with no gate checked.
- The bundle's README carries P3-DB4D-9D34-95EE with rewards [1, 1, 1]: not a qualifying result, so not for DAS.
- Hardening (v4), by the approved order (new physics once the agents handled the challenge cleanly) and the platform's
  "Hard for the right reason" (the model checks what it produced, never what it left out; deciding mark by mark what is
  real): a real transition on the annihilation line, 3092.6 -> 2581.6 keV (511.00 keV, I 0.853). The evidence is the
  narrow part of the production peak (the background run gives the annihilation shape) and its gates (941.3, 1092.0,
  1738.9 keV). Tried and dropped the same day: 3092.6 -> 2689.2 keV (403.4 keV) on the daughter's own line. The
  reference read it 28 percent low (summing-out at the top of a six-step cascade plus a 0.16 minority time share), and
  the stronger 551.8 keV line raised the 870.2 keV sum peak into a false doublet with 867.5 keV.
### v5 (T-1383 v5, job 19705, pass@3 ended 2026-11-10 07:59): 0 of 3 solved, TOO HARD

- Sol 6.1 (`gpt-6.1-sol`), rewards [0, 0, 0]. Agent times 13.7, 15.8 and 15.9 min (32, 23 and 21 steps); input tokens
  1.16, 0.73 and 0.58 M. Bundle in `work/gamma-decay-scheme/v5/pass3/` (`pass3.zip`, untrusted extraction under `x/`,
  answers in `outputs/`, digests in `attempts/`, `summary.md` from `tools/scheme_report.py`).
- Each attempt passed 4 of 7 tests (members, half-life, levels, isomer) and failed `test_transitions_placed`,
  `test_transition_energies` and `test_relative_intensities`. Levels 16 of 16 in all three; parent half-life 4.372,
  4.368 and 4.369 s; isomer 1963.1 keV with 158.3, 165.7 and 170.1 ns.
- a2 and a3: 30 of 31 transitions, missing only 3092.6 -> 2581.6 keV (511.00 keV, I 0.853); every other intensity
  within 11.2 and 13.7 percent. a1: 29 of 31, also missing 941.3 keV, which it read as the single-escape peak of
  1452.3 keV (1452.3 - 941.3 = 511.0: the triangle 3092.6 -> 2581.6 -> 1640.3 against 3092.6 -> 1640.3), and 1489.6
  keV at 4.41 for 3.26.
- Cause: all three put 511 keV in a list of room lines from general knowledge (a1 `bgE=[...,510.999,...]`, a2
  `bge=[...,511.,...]`, a3 `bglines=[...,511,...]`) and removed it before any analysis. a3's own coincidence table
  showed 511.0 keV in the gates of 1322.47 keV (232 counts) and 1738.9 keV (120), and a gated peak at 511.097 keV
  with sigma 0.64 keV; it did not follow them up.
- Fairness: instruction.md and NOTES.md say nothing of 511 keV or annihilation; the line is above the floor (0.853
  against 0.5); the data show it (narrow part 11967 +- 482 counts, parent share 0.98, gates of 941.3, 1092.0 and
  1738.9 keV); the reference reads 0.80. Only one pair of levels is 511 keV apart. No unstated requirement and no
  unfair check: the attempts failed at the stated difficulty.
- The bundle's README carries P3-3C8F-10C6-C3A0 with rewards [0, 0, 0]: not a qualifying result, not for DAS.
- v6 (the platform: "make the task somewhat easier"): one instruction sentence, "A transition can share its peak with
  radiation of another origin, whatever the peak's energy." It removes the shortcut (setting a peak aside by its
  energy) and names no peak. Still to decide: which of the six level differences on peaks of another origin hold a
  transition (511.0 keV only; 403.4, 1120.4, 2263.2, 300.1 and 1507.2 keV do not), and the 511 keV line's intensity.
  By the generator's constants about 9000 of the broad part's counts come from pair production of the parent's own
  lines (N_PARENT 3.0e7 times 3.0e-4), with the parent's time profile, and the room's share is about 3500 (0.8 per s
  over 4320 s): taking off only the room's share leaves about 1.75 times the line, outside 25 percent. The two
  shapes (sigma 1.50 against 0.67 keV) or coincidence intensities give it. Requirement R13 binds the sentence to the
  three transition tests; the README follows. Data, expected.json, checks.txt, generate.py and solve.py unchanged,
  so no generator run.
### v6 (T-1383 v6, job 20055, pass@3 ended 2026-11-10 12:33): 2 of 3 solved, QUALIFIES

- Sol 6.1 (`gpt-6.1-sol`), rewards [1, 1, 0]. Agent times 17.7, 12.0 and 28.6 min (39, 23 and 53 steps); input tokens
  1.92, 0.81 and 2.51 M. Bundle in `work/gamma-decay-scheme/v6/pass3/` (`pass3.zip`, untrusted extraction under `x/`,
  answers in `outputs/`, digests in `attempts/`, `summary.md` from `tools/scheme_report.py`).
- P3 ID **P3-6AEE-4ACB-FA2A** ("this revision only"), task digest `sha256:61344b23…562f`, the v6 files. The user pastes it into DAS
  4011092 (user, 12:38).
- a1 and a2: every test passes. 16 of 16 levels, 31 of 31 transitions, worst intensity errors 10.2 and 12.1 percent
  (992.7 keV both times), parent half-life 4.366 and 4.367 s, isomer 1963.1 keV with 169.6 and 168.0 ns.
- a3: fails `test_transitions_placed`, `test_transition_energies` and `test_relative_intensities` on one line: it left
  out 1489.6 -> 0 keV (1489.6 keV, I 4.41). Its level graph never had that edge: it took the whole 1489.6 keV peak as the
  same-crystal sum of the 646.9 + 842.7 keV (and 646.9 + 524.3 + 318.4 keV) cascade and tested a crossover only at
  1171 keV (rightly rejected) and 842.7 keV (rightly kept). Everything else was right: 16 levels, the other 30
  transitions within 9.5 percent, half-life 4.367 s, isomer 1963.1 keV with 165.6 ns. Summing is one of the traps the
  README documents, so this is a failure at the stated difficulty.
- The v6 sentence worked as meant: all three tested the 511 keV peak and kept 3092.6 -> 2581.6 keV with I 0.78, 0.91
  and 0.82 (true 0.853: -8.9, +7.2 and -3.9 percent), each from coincidences rather than the shared singles peak; none
  listed any of the five decoy differences (403.4, 1120.4, 2263.2, 300.1, 1507.2 keV) or any other line outside the
  scheme. a3 rejected the second 459.6 keV candidate (3148.8 -> 2689.2) as too weak, rightly.
### v8 (T-1383 v8, job 20645, pass@3 ended 2026-11-11 00:00): 3 of 3 solved, TOO EASY

- Sol 6.1 (`gpt-6.1-sol`), rewards [1, 1, 1]. Agent times 9.7, 10.3 and 9.4 min (25, 24 and 27 steps); input tokens
  0.65, 0.75 and 0.88 M. Bundle in `work/gamma-decay-scheme/v8/pass3/` (untrusted extraction under `x/`, answers in
  `outputs/`, digests in `attempts/`, `summary.md`). The bundle's README carries P3-4C55-BFAB-2B18 with rewards
  [1, 1, 1]: not a qualifying result, not for DAS.
- All three: 16 of 16 levels, 31 of 31 transitions, half-life 4.379, 4.37 and 4.375 s, isomer 1963.1 keV with 169.0,
  168.0 and 169.0 ns. Worst intensity errors 12.9, 15.4 and 19.6 percent (1323.2, 992.7 and 1606.6 keV).
- The 511 keV line (I 4.41): +8.2, -1.9 and +6.3 percent. Against each attempt's median error on the other lines
  (-1.5, -2.1, -0.9) that is +9.7, +0.2 and +7.2: a2 isolated the line (coincidences); a1 and a3 kept part of the
  broad annihilation part (a3 took the production peak's area with no annihilation correction).
- How it was found: no attempt set 511 keV aside by energy this time (a1's room list for the gain had no 511; a2 took
  511 out of its gain anchors). The strong narrow peak entered the line list, and the coincidences of 941.3, 1092.0
  and 1738.9 keV placed it ("The network also supports a real transition at approximately 511 keV, overlapping
  annihilation radiation", a2; "it cannot simply be discarded as annihilation radiation", a3).
- Reading: the line's strength decides whether the model looks at the peak at all: I 0.853 -> 0 of 3 (v5), 4.41 ->
  3 of 3 (v8); with the proviso at 0.853 all three looked (v6) and measured it within 9 percent.
- v9 (harden, within the approved order: the same physics made to decide the grade): keep the line easy to notice
  (I about 3.0, still a third of the feeding of 2581.6 keV) and make its intensity depend on separating the line from
  the parent's own annihilation radiation: pair production of the parent's lines raised from 3.0e-4 to 6.0e-4 detected
  annihilation photons per parent decay. Then the whole peak, the peak less the background run's annihilation, and a
  parent-time-profile share all read about 40 to 50 percent high; the two shapes or the coincidences give the line.
  `tests/checks.txt` will record those readings (new lines in `write_checks`).
### v9 (T-1383 v9, job 21129, pass@3 ended 2026-11-11 06:26): 1 of 3 solved, QUALIFIED

- Sol 6.1 (`gpt-6.1-sol`), rewards [0, 1, 0]; P3 ID **P3-4DCE-3D5C-5E63** (bundle README and the card agree). Agent times
  12.9, 15.7 and 17.4 min (33, 27 and 39 steps); input tokens 1.26, 0.99 and 1.52 M. Bundle in
  `work/gamma-decay-scheme/v9/pass3/` (untrusted extraction under `x/`, answers in `outputs/`, digests in `attempts/`,
  `summary.md`).
- a1 (0): 16 of 16 levels, 30 of 31 transitions: the 511.00 keV line (I 2.99) not placed. It used 510.999 keV as a room
  line for its gain, listed the 510.99 keV peak among the parent-profile peaks at I 4.006 (whole peak), and finally
  excluded it with the room lines. Worst intensity error otherwise 21.7 percent (708.0 keV, inside the band).
- a2 (1): exact. The 511 keV peak decomposed into the line and broad annihilation radiation (narrow part about 41,000
  counts): -6.0 percent. Worst intensity error 10.8 percent (1323.2 keV).
- a3 (0): the 511 keV line found and separated the same way (narrow part about 44,000 counts): +0.4 percent. It failed
  the isomer: it put the isomer at 1925.0 keV and, explicitly rejecting "a hidden low-energy ground-state step" for the
  sub-threshold 38.1 keV transition, built three extra levels 38.1 keV low (2594.9, 2823.3, 3054.5 keV) for 669.9,
  898.3, 231.2 and 459.6 keV: 18 levels where 16 do, 708.0 keV left out, 231.2 and 459.6 keV split between two
  placements (intensities -44 and -63 percent). That placement contradicts the prompt partners of 231.2 and 459.6 keV
  (2018.7, 1219.8; 1143.4, 992.7) and the instruction's fewest-levels rule: a reasoning slip, not a task defect.
- Reading: at I 2.99 among doubled pair-production annihilation, the attempts that noticed the line also separated its
  shape (a2, a3); the shape trap did not catch them, the noticing trap caught a1. The isomer trap, passed by every v8
  attempt, caught a3. Both failures are fair: the evidence is in the shipped files (README bullets "The annihilation
  peak holds a line" and "One level has no visible exit").
- The full review started as v10 (06:26) on the same files.
### v10 pass@8 (T-1383 v10 = v9's files, job 21495, pass@8 on Astra 6 ended 2026-11-11 18:12): 8 of 8 solved, TOO EASY

- The card: "The target model solved all 8 of its attempts, so the task is too easy and comes back to you. ... Make the
  task harder there, without changing what the instruction asks for". pass@8 runs on Astra 6 and must land at 1-6 of 8;
  pass@3 runs on Sol 6.1 and must land at 1-2 of 3. v8 gave Sol 3/3, v9 1/3; v10 (same files as v9) gave Astra 8/8.
- Attempts 17:50-18:12, 11-19 min and 15-26 steps each. All 8 exact on structure: 16/16 levels, 31/31 transitions,
  isomer at 1963.1 with 164.3-168.0 ns (168.0), parent 4.361-4.370 s (4.37), every energy within 0.1 keV.
- Intensities (grader: 25%): worst error per attempt 7.2-10.0%. 992.7 keV is -7.2 to -10.0% in all 8 (the reference
  itself -8.3%); 511.0 keV -1.3 to -6.0%; the 647 keV doublet members within 6%. Nothing came near the limit.
- What Astra 6 did, in every attempt: gain recalibration on the room lines; time-profile fits of every peak; doublets
  from width, self-coincidence and gated centroids; quantitative sum (coincidences over 7) and escape checks; the 708
  keV mixed peak by its timing; the 511 keV line by coincidences with H's three other exits plus a narrow/broad shape
  fit; the isomer by signed delayed coincidences; an audit of weak peaks; coincidence checks of second placements
  (459.6 = N-J considered and rejected). The two traps that caught Sol 6.1 in v9 (the 511 keV line set aside, the
  sub-threshold isomer step) are routine for Astra 6.
- Design notes so far (`work/gamma-decay-scheme/v11/explore/`): `candidates.py` finds no existing level pair 0.5-1.3
  keV from a line except pairs through the Da/Db doublet, whose gates can't be told apart; `summing_out.py` shows the
  generator's summing-out costs at most -5.2% uncorrected and would need an unrealistic array to matter.
### v11 (T-1383 v11, job 22164, pass@3 on Sol 6.1 ended 2026-11-12 05:53): 1 of 3 solved, QUALIFIED

- P3 ID **P3-8546-0E6F-2BCD** (this revision only), given to the user for DAS 4011092. The full review runs as v12
  (= v11's files, `gate/task/22785.zip`), queued 05:53.
- Rewards [0, 1, 0]. a1 and a3 are exact apart from one thing: both leave out the 1081.40 keV transition from
  2721.70 to 1640.30 keV (I 1.22) and keep the whole 1082 keV peak as E->B (+9.0% and +8.2%). Both found the level at
  2721.70 keV through the 1879.0 keV line. a2 is exact: its weak-peak search flagged "an unresolved component near
  1081.4 keV" next to the 1879.0 keV level, and it took the weak line's intensity from "its exclusive 1322-keV
  coincidence" (-5.5%), E->B -2.7%.
- Every other part held in all three: 17 levels, the 511 keV line (-17.6%, -5.2%, -2.3%), the isomer at 1963.1 keV
  (168.5-172.0 ns), the parent at 4.3625-4.3734 s. Worst intensity errors 18.1%, 14.4%, 11.5% against 25% (a1:
  1092.0 keV -18.1%, 511.0 keV -17.6%).
- The trap works as designed on Sol 6.1, and it is the only one that caught an attempt. Whether Astra 6 misses it
  (pass@8 needs 1-6 of 8) is the open question.
### v12 pass@8 (T-1383 v12 = v11's files, job 22785, pass@8 on Astra 6 ended 2026-11-12 21:09): 7 of 8 solved, TOO EASY

- The card: "This version added the weak 1081.4 keV transition hidden under the stronger 1082.3 keV line, which only
  gated spectra reveal; most attempts still found it, so that one transition does not make the task hard enough on its
  own." pass@8 must land at 1-6 of 8.
- Attempts 20:17-21:00, 15-21 min each. a4 failed, on that line alone: it kept the whole 1082 keV peak as E->B (+7.8%)
  and its weak-peak search "found no overlooked transition". Everything else in a4 was exact.
- The other seven listed 1081.40 keV (errors -13.7% to +6.0%); worst intensity error per attempt 9.2-13.7% (limit
  25%). All 8: 17 levels, the isomer at 1963.1 keV, the parent half-life within 0.2%.
- Two routes found it, either one enough:
  - The level difference. Once 1879.0 keV places 2721.7 keV, 2721.7 - 1640.3 falls on the 1082 keV peak (a2: "The
    existing 2721.7-keV level would also produce a 1081.4-keV transition to 1640.3 keV, unresolved beneath the
    stronger 1082.3-keV line. This must be tested before writing the output."; a3 planned to "test for an additional
    1081.4/1082.3 keV doublet"; a5 and a7 the same).
  - The gate on 1321.9 keV, a member of the 1322 keV doublet that every attempt gates on anyway (a6: "The 1322-gated
    spectrum reveals a second 1082-region transition at about 1081.5 keV"; a8: "A previously hidden approximately
    1081.4 keV branch appears in the 1321.9 keV gate"; a1 used it to rule out the low-energy tail).
  A fit of the 1082 keV peak with two members at fixed energies (several with a low-energy tail in the line shape) or
  the gate's own area then gave the intensity.
- Sol 6.1 found the line in 1 of 3 (v11), by the level difference only. Astra 6 found it in 7 of 8, by either route.
### v13 (T-1383 v13, job 23827, pass@3 on Sol 6.1 ended 2026-11-13 07:23): 0 of 3 solved, TOO HARD

- Rewards [0, 0, 0], each failing test_transitions_placed, test_transition_energies and test_relative_intensities on
  one thing: the missing 1081.40 keV transition from 1399.8 to 318.4 keV (I 1.61). All three have the 17 levels
  exact, the 1399.8 keV level among them, the other 32 transitions within the bands (worst 1606.6 keV +20.1%, +20.3%,
  and 1082.3 keV read whole +10.5% to +12.3%), the parent at 4.368-4.372 s and the isomer at 1963.1 keV (165-167 ns).
  Agent time 15, 21 (29 with the verifier) and 15 min.
- All three found the level at 1399.8 keV through 557.1 keV (I 1.32, 5.3 keV above 551.8 keV at I 7.7), and late: a1
  about two thirds through ("The 557.1 keV peak is a genuine weak candidate with strong 318/524 coincidences and may
  require an additional level near 1399.8 keV"), a2 about two thirds through, a3 near its end ("one previously missed
  transition ... It therefore adds a minimally necessary level near 1399.8 keV"). Their matching of level differences
  to peaks came before that (a3: "1082.219 [(1924.9, 842.7, 1082.2)]") and none repeated it with the new level. a2
  tested 1399.8 keV to the ground state (the 1400.6 keV sum peak) but not to 318.4 keV.
- None flagged the 1082 keV peak itself: a2 compared its singles and gated centroids (1082.21 and 1082.25 keV) and
  went on.
- So the trap failed at its trigger, not at the measurement. In v11 (Sol 1 of 3) the hidden line's upper level was
  placed early by an isolated clean line (1879.0 keV), and the one success also took the intensity from a gate that
  isolated the weak line, which v13 removed.
- v14 plan: make 557.1 keV a regular line (more beta feeding to 1399.8 keV), so the level stands from the start, and
  the hidden line somewhat stronger, so a plain two-Gaussian fit lands nearer the band; still no gate isolates it.
### v14 (T-1383 v14, job 24365, pass@3 on Sol 6.1 ended 2026-11-13 19:16): 1 of 3 solved, QUALIFIED

- P3 ID **P3-B911-F9F1-EDFA** (this revision only), given to the user for DAS 4011092. The full review runs as v15
  (= v14's files), queued 19:16. The run started 13:39 had a fault on the platform's side and was restarted at 18:44;
  the attempts' agents started 18:49 and took 15 to 18 min, the verifier 4.5 to 10.6 min.
- Rewards [1, 0, 0] (`work/gamma-decay-scheme/v14/pass3/summary.md`; outputs in `pass3/outputs/`, compared with
  `work/gamma-decay-scheme/v13/explore/compare13.py`). All three found 17 levels, the 1399.8 keV level and its
  557.1 keV line (I 2.90 to 3.00 for 2.98): the stronger feeding of v14 made that level easy to place.
- a1 is exact: 33 of 33 transitions; the hidden 1081.41 keV line at I 2.10 (-13.8%); worst other errors 647.8 keV
  +13.1%, 646.9 keV -7.4%; parent 4.380 s, isomer 1963.1 keV 170.5 ns.
- a2 leaves out the hidden 1081.40 keV line (the v13 failure) and keeps the whole 1082 keV peak as 1925.0 -> 842.7
  (+16.1%); 708.0 keV at -24.9% sits at the band's edge.
- a3 finds the hidden line (1081.38 keV, I 2.96, +21.6%) but never detects the weak 1092.00 keV line (2581.6 ->
  1489.6 keV, I 1.25; the reference measures 1.20 in `tests/checks.txt`): its trajectory digest
  (`attempts/attempt-3.txt`) never mentions 1092 keV. 511.0 keV at -23.4% is near the edge too.
- So two independent ways to fail: the hidden line (found by 2 of 3; their intensities 2.10 and 2.96 for 2.44, both
  inside 25%) and a missed weak line. The v12 pass@8 on Astra 6 solved 7 of 8 with a weaker hidden line (I 1.22); if
  this pass@8 comes back TOO EASY, the next hardening has to hide something Astra 6's level-difference check does not
  reach (BRIEFING 2026-11-12 21:45).

## Pitfalls

- `tb4 lint` prints non-ASCII through cp1252 and crashes with UnicodeEncodeError once a lint line quotes a β or γ. Run
  it with `PYTHONUTF8=1 PYTHONIOENCODING=utf-8` for this task; `release.sh` needs the same.
- lint's requirements check flags any `abs(a - b) < x` under `tests/`, `generate.py` too, as a tolerance the instruction
  never states. Write it as `b - x < a < b + x` in design code.
- `tests/emit.py` and `cheat/forge-reward/` are for program mode only and were deleted; a data task keeps
  `cheat/symlink-answers/`.
- `pass3_report.py` is program-mode only. This task needs a comparator of each attempt's `decay_scheme.json` from the
  untrusted extraction.
- (2026-11-09) Local version numbers go on (v3, v4, ...), while TB4.1's T-0020 counts its own versions from v1: platform version = local version - 2. `supertasker.py links T-0020 v1` lists v3's jobs, and the next fix is `release.sh gamma-decay-scheme T-0020 4 ...` (archives v3, uploads the platform's v2).
- (2026-11-09) TB 4.1 wants the README Author line as `Name (email)`, matching task.toml, and the user's rule keeps the email in task.toml only. v3 ships without it (lint WARN) and the question is with the user.
- (2026-11-09 17:22) The platform restored T-1383 and folded T-0020 into it as v3, so platform versions equal local versions again: the 02:02 point "platform version = local version - 2" no longer holds. The next fix is `release.sh gamma-decay-scheme T-1383 4 ...`. v3's jobs are under 19128 (`links T-1383 v3`); the updates list also shows `gate/full/137.zip`.
- (2026-11-09 17:59) The reference turns coincidences into placement constraints. A parent line hidden under another activity's line inherits that activity's cascade partners (the daughter's 403.4-707.9 keV cascade would have tied 403.4 keV to the parent's 708.0 keV), so v4's `coincidence_flags` leaves a pair undecided when both peaks hold another activity. A split of the 511 keV peak must stop short of the 524.3 keV line (window 501 to 518 keV), and a 6-sigma test on a parent time coefficient fails because the parent, ramp and daughter shapes are strongly correlated: test the narrow part's area and its parent share instead.
- (2026-11-10 01:54) TB 4.1 compares the README's metadata block with task.toml as text. The Author line must be `Name (email)` (organizations after ` | `); `tb4 lint` 3.8.2 only warns (`task_readme`), but the platform's upstream `check-task-fields.sh` fails it and the quick check stops before the 35 criteria. The card then reads "did not finish (a platform fault)": open View report before believing it.
- (2026-11-10 08:10) A `cd` into `work/<slug>/v<N>/pass3/x/` in a Bash call persists, because the folder is inside the working directories: the next commands then run inside the untrusted tree. List and read it with paths from the folder root instead (happened at 08:03 on 11-10; nothing ran there, the next call went back).
- (2026-11-11) A fixed window around the most extreme gate centroid let one stray gate set a doublet member, which made the search's coincidence flags undecided and opened a tie at the fewest levels (v9's first data). After every generator run read `[placement search]`: the count at the fewest levels must be 1.
- (2026-11-11) In `split_doublets` a gate that sees both members of a doublet with a weak member reads at the strong member's energy (the 318.4 keV gate on the 1082 keV peak: 1082.20 keV), so the old rule flagged the weak member as absent there and the search could not place it. A weak member's flag is now undecided wherever the gate's centroid sits on the strong member.
- (2026-11-12 22:40) v13 build. (1) The reference's search lets a line land only on a level that a line placed before it made.
  With 511.0 keV at I 4.22 just above 941.3 keV at 4.21, 511.0 came first, before any line had made 2581.6 keV, and no
  scheme fitted at any level count ("no scheme agrees with the data"). The fix, in `main()`: clean lines first, then lines
  on peaks shared with something else (share < 0.9 or the annihilation line), then the delayed feeders. (2) The search
  then found two schemes at 17 levels: the second puts 551.8 keV from 2041.4 to 1489.6 keV, beside 647.8 keV, because
  the 551.8 keV gate's centroid on the 647 keV doublet (647.40) sat within 2 sigma of the edge of the "both" band and
  the flag stayed undecided. The coincidence strength excludes it (1.948 +- 0.017 measured, 0.847 predicted by it,
  1.847 by the scheme kept). checks.txt `[placement search]` now prints every other scheme with as few levels and the
  pairs that tell it apart; the README must not claim a single minimal scheme unless that list is empty. (3) The
  weak member's I: 1.78 with a tailed line shape, 1.57 from the 318.4/524.3 gate proportions, 2.12 with Gaussians that
  leave out the tail (outside 25%, for 1.61). The whole 1082 keV peak read as E->B is 14.27 for 12.99, inside 25%,
  so only the missing transition fails an answer that overlooks it.
- (2026-11-13 07:51) v14 build. (1) With the hidden line at I 2.44 the reference's first run put it at 3.15 (+29%) and the
  generator stopped. A two-member fit's share follows where the peak's centroid sits between the two energies, so it
  moves with the energy scale (0.05 keV moves it by about 0.06): the tailed fit was +13% in v13 and +29% in v14, and
  Gaussians alone were +35% in v13 and -2.5% in v14. The 318.4/524.3 keV gate proportions gave 0.1102 (truth 0.1104)
  and 0.1757 (0.1613). `hidden_members` now keeps a member on the fit but takes its share from the gates. (2) The
  same run found three schemes with 17 levels: 551.8 or 1011.4 keV placed beside 647.8 keV instead of above it, because
  those gates' centroids on the 647 keV doublet sat near the edge of the "both" band. `coincidence_flags` now marks a
  partner weaker than both members of a doublet in one cascade as seen with both when it brings more than 1.15 of the
  doublet's gamma rays per gamma ray of its own (three standard errors over); measured 1.91 for both. One scheme at 17
  levels again. (3) The generator's final assert now names the quantity outside its band and the three largest
  intensity differences; before, it printed nothing.
- (2026-11-13 14:59) Platform access stalled from 14:19 to 14:58. Each Playwright connection over CDP adds a utility world (`__playwright_utility_world_page@...`) to every open tab; the tab keeps it after the connection ends, even across a reload, and the next connection replays them all as `Runtime.executionContextCreated` events. The long-lived queue tabs held 387 to 2571 each (4970 in all after reloading two of them), so status calls slowed until they timed out. Reloading did not help; closing the old tabs did. Raw CDP over a websocket answered at once throughout, so the browser and the sign-in were fine. A status call started just after the closures connected late and then failed at `new_page` with `TargetClosedError`. Since 14:51 `tools/supertasker.py` (patched by another session) opens a tab per call, leaves it as `about:blank#tb4-keeper`, and the next call closes it.
