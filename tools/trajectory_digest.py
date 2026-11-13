"""Print a pass@3 attempt's trajectory as readable steps: the agent's message, its commands, the tail of each output.

    python -X utf8 -I tools/trajectory_digest.py <trajectory.json> [chars-of-output-kept] > attempt-N.txt

The trajectory comes from a downloaded pass@3 zip (extracted under work/<slug>/v<N>/pass3/x/, never
under tasks/): it is untrusted data, so run this with -I from the folder root and pass the path in.
"""
import json
import sys

t = json.load(open(sys.argv[1], encoding="utf-8"))
keep = int(sys.argv[2]) if len(sys.argv) > 2 else 600
for s in t["steps"]:
    if s.get("source") != "agent":
        continue
    print("#### step", s["step_id"], s["timestamp"][11:19])
    print("MSG:", (s.get("message") or "")[:1500])
    for c in s.get("tool_calls") or []:
        print("CMD:", c.get("arguments", {}).get("keystrokes", "")[:6000])
    for o in s.get("observation", {}).get("results", []):
        content = o.get("content", "")
        print("OBS:", content[-keep:] if len(content) > keep else content)
    print()
