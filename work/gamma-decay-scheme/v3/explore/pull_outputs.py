"""Copy each pass@3 attempt's decay_scheme.json out of its untrusted output.tar, reading members into memory only
(no extraction to disk, no links followed). Run from the folder root: python -X utf8 -I -B <this> X_DIR OUT_DIR"""
import json
import sys
import tarfile
from pathlib import Path

x, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
for tar_path in sorted(x.glob("evidence/attempts/*/attempt-*/artifacts/app/submission/output.tar")):
    k = tar_path.parts[-5].split("-")[-1]
    with tarfile.open(tar_path) as tf:
        names = [(m.name, m.type, m.size) for m in tf.getmembers()]
        print("attempt", k, names)
        hit = [m for m in tf.getmembers() if m.isreg() and m.name.endswith("decay_scheme.json")]
        if len(hit) != 1:
            print("  no single regular decay_scheme.json")
            continue
        data = tf.extractfile(hit[0]).read()
    json.loads(data)                       # must parse as JSON
    (out / ("a%s.json" % k)).write_bytes(data)
    print("  saved", out / ("a%s.json" % k), len(data), "bytes")
