"""Extract the pass@8 bundle (untrusted) and copy out each attempt's planets.json, reward and timing; digest each
trajectory. Nothing in the bundle runs. Run from the folder root:

    python -X utf8 -I -B work/rv-planet-census/v2/pull_pass8.py work/rv-planet-census/v2/pass8

Uses tools/pass3_report.py's extract_zip (absolute paths, '..' and links refused). planets.json is read from each
attempt's output.tar in memory (one regular member only), parsed as JSON, then written to outputs/aK.json."""
import importlib.util
import json
import subprocess
import sys
import tarfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("p3", "tools/pass3_report.py")
p3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p3)

base = Path(sys.argv[1])
zpath, x = base / "pass8.zip", p3.longpath(base / "x")
out, adir = base / "outputs", base / "attempts"
out.mkdir(exist_ok=True)
adir.mkdir(exist_ok=True)
if not x.exists() or not any(x.iterdir()):
    x.mkdir(parents=True, exist_ok=True)
    p3.extract_zip(zpath, x)

atts = sorted((p for p in x.rglob("attempt-*") if p.is_dir() and (p / "result.json").is_file()),
              key=lambda p: int(p.name.split("-")[-1]))
print("attempt folders:", len(atts))
for att in atts:
    k = att.name.split("-")[-1]
    reward = att / "verifier" / "reward.txt"
    rtext = reward.read_text(encoding="utf-8").strip() if reward.is_file() else "?"
    r = json.loads((att / "result.json").read_text(encoding="utf-8"))
    ag = r.get("agent_result") or {}
    mins = p3.minutes(r.get("agent_execution"))
    ctrf = att / "verifier" / "ctrf.json"
    tests = json.loads(ctrf.read_text(encoding="utf-8"))["results"]["tests"] if ctrf.is_file() else []
    failed = [t["name"].split("::")[-1] for t in tests if t.get("status") != "passed"]
    print("a%s reward %s agent %s min, episodes %s, cost %s, failed %s" % (
        k, rtext, "%.0f" % mins if mins else "?", (ag.get("metadata") or {}).get("n_episodes", "?"),
        ("$%.2f" % ag["cost_usd"]) if ag.get("cost_usd") else "?", failed or "none"))
    traj = att / "agent" / "trajectory.json"
    if traj.is_file():
        d = subprocess.run([sys.executable, "-X", "utf8", "-I", "-B", "tools/trajectory_digest.py", str(traj)],
                           capture_output=True, text=True, encoding="utf-8")
        (adir / ("attempt-%s.txt" % k)).write_text(d.stdout, encoding="utf-8", newline="\n")
    tar_path = att / "artifacts" / "app" / "submission" / "output.tar"
    if not tar_path.is_file():
        print("  no output.tar")
        continue
    with tarfile.open(tar_path) as tf:
        hit = [m for m in tf.getmembers() if m.isreg() and m.name.endswith("planets.json")]
        if len(hit) != 1:
            print("  no single regular planets.json", [(m.name, m.type) for m in tf.getmembers()][:5])
            continue
        data = tf.extractfile(hit[0]).read()
    json.loads(data)
    (out / ("a%s.json" % k)).write_bytes(data)
