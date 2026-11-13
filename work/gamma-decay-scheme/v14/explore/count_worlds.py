"""Count the Playwright utility worlds each tab replays on connect, from a DEBUG=pw:protocol log of cdp_probe.py.
Usage: python -X utf8 -I -B count_worlds.py LOG. Reads the log only."""
import collections
import json
import re
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
urls, worlds = {}, collections.Counter()
for line in text.splitlines():
    m = re.search(r"(?:SEND|RECV) ►?◀? ?(\{.*\})\s*$", line)
    if not m:
        i = line.find("{")
        if i < 0:
            continue
        raw = line[i:]
    else:
        raw = m.group(1)
    try:
        msg = json.loads(raw)
    except ValueError:
        continue
    if msg.get("method") == "Target.attachedToTarget":
        p = msg["params"]
        urls[p["sessionId"]] = p["targetInfo"].get("url", "")[:70]
    elif msg.get("method") == "Runtime.executionContextCreated":
        name = msg["params"]["context"].get("name", "")
        if name.startswith("__playwright_utility_world"):
            worlds[msg.get("sessionId", "?")] += 1
for sid, n in worlds.most_common():
    print("%4d  %s" % (n, urls.get(sid, sid)))
