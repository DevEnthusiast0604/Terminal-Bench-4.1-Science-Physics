"""Each attempt's worst error per quantity and session, as a fraction of its tolerance.
Usage: python -I -B margins.py EXPECTED_JSON OBS_JSONL [OBS_JSONL ...]  (reads data only)"""
import json
import sys

TOL = {"g_m_s2": 4e-4, "small_amplitude_period_s": 1e-4, "run_periods_s": 1e-4,
       "radius_of_gyration_m": 1e-3, "release_amplitude_rad": 2e-3}

expected = json.load(open(sys.argv[1], encoding="utf-8"))
expected = expected.get("cases", expected)
for path in sys.argv[2:]:
    print("==", path)
    for line in open(path, encoding="utf-8"):
        if not line.startswith("TB4-OBS "):
            continue
        obs = json.loads(line[len("TB4-OBS "):])
        case = obs["case"]
        got = json.loads(obs["value"]["stdout"])
        want = expected[case]
        row = []
        for key, tol in TOL.items():
            g, w = got[key], want[key]
            if isinstance(w, dict):
                worst = max((abs(g[k] - w[k]) / abs(w[k]) / tol, k) for k in w)
                row.append("%s %.3f(%s)" % (key.split("_")[0], worst[0], worst[1]))
            else:
                row.append("%s %.3f" % (key.split("_")[0], abs(g - w) / abs(w) / tol))
        print(case, "  ".join(row))
