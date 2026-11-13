"""Foreground poll: run tools/supertasker.py status TASK every INTERVAL s until an unseen update card appears,
the status text contains MARKER (optional, e.g. "35 criteria" for an early report), or LIMIT s pass; then print
the last status. Run from the folder root.

    python -X utf8 -I -B poll.py T-0610 560 90 ["35 criteria"]
"""
import subprocess
import sys
import time

task, limit, interval = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
marker = sys.argv[4] if len(sys.argv) > 4 else None
end = time.time() + limit
while True:
    proc = subprocess.run([sys.executable, "-X", "utf8", "-I", "-B", "tools/supertasker.py", "status", task],
                          capture_output=True, text=True, encoding="utf-8")
    out = proc.stdout + proc.stderr
    tail = [ln for ln in out.splitlines() if "unseen update" in ln]
    stamp = time.strftime("%H:%M:%S", time.gmtime())
    if tail and not tail[-1].startswith("--- 0 "):
        print("%s UTC: %s" % (stamp, tail[-1]))
        print(out)
        break
    if marker and marker in out:
        print("%s UTC: status shows %r" % (stamp, marker))
        print(out)
        break
    if time.time() + interval > end:
        print("%s UTC: no new card yet" % stamp)
        print(out[-900:])
        break
    time.sleep(interval)
