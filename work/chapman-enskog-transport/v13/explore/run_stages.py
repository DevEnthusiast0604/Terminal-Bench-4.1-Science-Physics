"""Fills the qmix cache for the v13 sets with one serial process per job (no multiprocessing pool, which stalls on
this machine), at most WORKERS at a time, and stops every child at the deadline (stages are written atomically, so
a stopped job loses only its current stage). Not shipped.
    python -B run_stages.py pairs|brk DEADLINE_SEC NAME...
pairs: res/base/pi of each pair of each set; brk: the brackets of each set (its pairs cached)."""
import os
import subprocess
import sys
import time

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
TESTS = os.path.join(ROOT, "tasks", "active", "chapman-enskog-transport", "tests")
CACHE = os.path.join(ROOT, "work", "chapman-enskog-transport", "v10", "cache")
LOGS = os.path.join(ROOT, "work", "chapman-enskog-transport", "v13", "gen")
WORKERS = 6


def main(phase, deadline, names):
    os.makedirs(LOGS, exist_ok=True)
    jobs = [(n, pk) for n in names for pk in ("11", "22", "12")] if phase == "pairs" else [(n, None) for n in names]
    env = dict(os.environ, QMIX_WORKERS="1", QMIX_CACHE=CACHE, PYTHONDONTWRITEBYTECODE="1")
    t_end = time.time() + deadline
    running, done, failed = [], [], []
    while jobs or running:
        while jobs and len(running) < WORKERS and time.time() < t_end - 20:
            n, pk = jobs.pop(0)
            code = ("import sys; sys.path.insert(0, %r); import generate as G; G.compute(%r, only=%r)"
                    % (TESTS, n, pk))
            err = open(os.path.join(LOGS, "%s-%s-%s.err" % (phase, n, pk or "all")), "a")
            running.append(((n, pk), subprocess.Popen([sys.executable, "-B", "-c", code], cwd=TESTS, env=env,
                                                      stdout=err, stderr=err), err, time.time()))
        for item in list(running):
            job, proc, err, t0 = item
            if proc.poll() is not None:
                err.close()
                running.remove(item)
                (done if proc.returncode == 0 else failed).append((job, proc.returncode, round(time.time() - t0)))
                print("finished", job, "rc", proc.returncode, "%.0f s" % (time.time() - t0), flush=True)
        if time.time() > t_end:
            for job, proc, err, t0 in running:
                proc.kill()
                proc.wait()
                err.close()
                print("stopped at the deadline", job, flush=True)
            break
        if not jobs and not running:
            break
        if jobs and time.time() >= t_end - 20 and not running:
            break
        time.sleep(2)
    print("done", len(done), "failed", failed, "not started", jobs, flush=True)


if __name__ == "__main__":
    main(sys.argv[1], float(sys.argv[2]), sys.argv[3:])
