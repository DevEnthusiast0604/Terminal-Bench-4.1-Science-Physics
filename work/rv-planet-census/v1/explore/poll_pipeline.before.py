"""Background pipeline watch: run tools/supertasker.py status TASK every INTERVAL s from the folder root.

Prints one UTC-stamped line whenever the task page changes. Exits with the full status page when an
unseen update card appears (exit 0), when the page has not answered for 3 polls in a row (exit 2), or
when LIMIT s have passed (exit 1). A Cloudflare error page (502, 503, 504, 52x, 530 or "Tunnel error": the
platform itself is down, as on 2026-11-05 from 14:53, flapping until after 16:00) is not a miss: it prints one
line when the outage starts and one when it ends. Any other page without the task view (a sign-in page, or the
app's shell while its backend fails) counts as a miss.

    python -X utf8 -I -B tools/poll_pipeline.py T-0851 43200 180      (Bash run_in_background, folder root)
"""
import re
import subprocess
import sys
import time

task, limit, interval = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
end = time.time() + limit
last_sig = None
misses = 0
outage = False
out = ""
GATEWAY = re.compile(r"page title: .*\b(50[234]|52[0-7]|530)\b|Bad gateway|Gateway time-?out|Service unavailable"
                     r"|Tunnel error|Origin is unreachable|Web server is down", re.I)
while True:
    stamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    try:
        proc = subprocess.run([sys.executable, "-X", "utf8", "-I", "-B", "tools/supertasker.py", "status", task],
                              capture_output=True, text=True, encoding="utf-8", timeout=170)
        out = proc.stdout + proc.stderr
    except subprocess.TimeoutExpired:
        out = "(status call timed out after 170 s)"
    m = re.search(r"^--- (\d+) unseen update", out, re.M)
    if m is None and GATEWAY.search(out):
        if not outage:
            print("%s UTC: platform down (gateway error), still polling: %s" % (
                stamp, " | ".join(out.strip().splitlines()[-2:])), flush=True)
        outage, misses = True, 0
    elif m is None:
        misses += 1
        print("%s UTC: no status (%d in a row): %s" % (stamp, misses, " | ".join(out.strip().splitlines()[-4:])),
              flush=True)
        if misses >= 3:
            print(out, flush=True)
            sys.exit(2)
    else:
        if outage:
            print("%s UTC: platform answering again" % stamp, flush=True)
        misses, outage = 0, False
        lines = [ln.strip() for ln in out.splitlines() if ln.strip() and not ln.startswith("Your note:")]
        sig = " | ".join(lines)
        if sig != last_sig:
            print("%s UTC: %s" % (stamp, sig), flush=True)
            last_sig = sig
        if int(m.group(1)) > 0:
            print("%s UTC: %s unseen update(s)" % (stamp, m.group(1)), flush=True)
            print(out, flush=True)
            sys.exit(0)
    if time.time() + interval > end:
        print("%s UTC: limit reached, no new card" % stamp, flush=True)
        print(out, flush=True)
        sys.exit(1)
    time.sleep(interval)
