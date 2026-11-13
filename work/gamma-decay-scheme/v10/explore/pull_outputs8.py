"""Copy each pass@8 attempt's decay_scheme.json out of its untrusted output.tar, reading members into memory only
(no extraction to disk, no links followed), and print each attempt's reward and timing.
Run from the folder root: python -X utf8 -I -B <this> X_DIR OUT_DIR   (X_DIR holds attempt-1 ... attempt-8)"""
import json
import sys
import tarfile
from pathlib import Path

x, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for att in sorted(x.glob("attempt-*"), key=lambda p: int(p.name.split("-")[-1])):
    k = att.name.split("-")[-1]
    reward = (att / "verifier" / "reward.txt")
    rtext = reward.read_text(encoding="utf-8").strip() if reward.is_file() else "?"
    info = ""
    res = att / "result.json"
    if res.is_file():
        r = json.loads(res.read_text(encoding="utf-8"))
        ar = r.get("agent_result") or {}
        info = "%s .. %s in %s out %s" % (r.get("started_at"), r.get("finished_at"), ar.get("n_input_tokens"),
                                          ar.get("n_output_tokens"))
    print("attempt", k, "reward", rtext, info)
    tar_path = att / "artifacts" / "app" / "submission" / "output.tar"
    if not tar_path.is_file():
        print("  no output.tar")
        continue
    with tarfile.open(tar_path) as tf:
        hit = [m for m in tf.getmembers() if m.isreg() and m.name.endswith("decay_scheme.json")]
        if len(hit) != 1:
            print("  no single regular decay_scheme.json", [(m.name, m.type) for m in tf.getmembers()])
            continue
        data = tf.extractfile(hit[0]).read()
    json.loads(data)
    (out / ("a%s.json" % k)).write_bytes(data)
    print("  saved", out / ("a%s.json" % k), len(data), "bytes")
