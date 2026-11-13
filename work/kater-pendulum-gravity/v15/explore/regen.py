"""v15 regeneration with checks. Usage: python -I -B regen.py TASK_DIR
1. session.json of e1, e2, h1, h2, h3 as the generator now writes it must equal the shipped file byte for byte.
2. h4 is rebuilt in a temporary folder: under the renaming (new b1..b3 = old a1..a3, new a1..a3 = old b1..b3)
   every runs/ file must equal the old one except its '# run:' line, and every sync/ file exactly.
3. Only then: tests/cases/h4 is replaced and tests/expected.json rewritten (as generate.py main does)."""
import io
import json
import os
import shutil
import sys
import tempfile

task = os.path.abspath(sys.argv[1])
sys.path.insert(0, os.path.join(task, "tests"))
import generate as G  # noqa: E402

where = {n: os.path.join(task, "environment", "data", "sessions", n) if n in G.EXAMPLES
         else os.path.join(task, "tests", "cases", n) for n in G.SESSIONS}

for name in ("e1", "e2", "h1", "h2", "h3"):
    buf = io.StringIO()
    json.dump(G.session_record(G.SESSIONS[name]), buf, indent=2)
    buf.write("\n")
    with open(os.path.join(where[name], "session.json"), encoding="utf-8", newline="") as fh:
        old = fh.read()
    assert buf.getvalue() == old, name
    print(name, "session.json unchanged")

rename = {"b1": "a1", "b2": "a2", "b3": "a3", "a1": "b1", "a2": "b2", "a3": "b3"}   # new name -> old name
with tempfile.TemporaryDirectory() as tmp:
    new = os.path.join(tmp, "h4")
    G.write_session(new, "h4")
    for rid, old_rid in rename.items():
        with open(os.path.join(new, "runs", rid + ".csv"), "rb") as fh:
            a = fh.read().split(b"\n")
        with open(os.path.join(where["h4"], "runs", old_rid + ".csv"), "rb") as fh:
            b = fh.read().split(b"\n")
        assert a[0] == b"# run: " + rid.encode() and b[0] == b"# run: " + old_rid.encode(), (rid, a[0], b[0])
        assert a[1:] == b[1:], rid
        with open(os.path.join(new, "sync", rid + ".csv"), "rb") as fh:
            sa = fh.read()
        with open(os.path.join(where["h4"], "sync", old_rid + ".csv"), "rb") as fh:
            sb = fh.read()
        assert sa == sb, rid
        print("h4 %s = old %s (data identical, name changed)" % (rid, old_rid))
    with open(os.path.join(new, "session.json"), encoding="utf-8") as fh:
        print("h4 session.json runs:", json.load(fh)["runs"])
    shutil.rmtree(where["h4"])
    shutil.copytree(new, where["h4"])

expected = {name: G.truth(name) for name in G.SESSIONS if name not in G.EXAMPLES}
with open(os.path.join(task, "tests", "expected.json"), "w", newline="\n") as fh:
    json.dump(expected, fh, indent=2, sort_keys=True)
    fh.write("\n")
print("h4 replaced; expected.json rewritten; h4 run periods:", expected["h4"]["run_periods_s"])
