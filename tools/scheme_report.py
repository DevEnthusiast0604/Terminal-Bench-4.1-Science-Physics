"""Compare each pass@3 attempt's decay_scheme.json with a task's expected.json (gamma-decay-scheme: data deliverable).

    python -X utf8 -I -B tools/scheme_report.py EXPECTED.json OUT.md ATTEMPT_NAME=PATH [ATTEMPT_NAME=PATH ...]

pass3_report.py is program-mode only. This one only reads JSON files, so pointing it at the untrusted extraction under
work/<slug>/v<N>/pass3/x/ is safe. For each attempt it lists what the judge would say about every level and transition,
using the instruction's bands, so the report shows which trap an attempt fell into.
"""
import json
import sys

KEV = 0.5
HALF_LIFE = 0.02
ISOMER_HALF_LIFE = 0.08
INTENSITY = 0.25


def close(a, b, tol):
    return abs(a - b) <= tol


def nearest(value, options):
    return min(options, key=lambda x: abs(x - value)) if options else None


def report(name, path, want):
    out = ["## %s" % name, ""]
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return out + ["could not read the deliverable: %s" % exc, ""]
    if not isinstance(doc, dict):
        return out + ["not an object", ""]

    hl = doc.get("parent_half_life_s")
    if isinstance(hl, (int, float)):
        good = close(hl, want["parent_half_life_s"], want["parent_half_life_s"] * HALF_LIFE)
        out.append("parent half-life: %s against %s: %s" % (hl, want["parent_half_life_s"], "ok" if good else "OUT"))
    else:
        out.append("parent half-life: missing or not a number")

    have = sorted(v for v in doc.get("levels_keV", []) if isinstance(v, (int, float)))
    levels = sorted(want["levels_keV"])
    missing = [w for w in levels if not any(close(h, w, KEV) for h in have)]
    extra = [h for h in have if not any(close(h, w, KEV) for w in levels)]
    out += ["levels: %d listed, %d in the scheme" % (len(have), len(levels)),
            "  in the scheme, not listed within 0.5 keV: %s" % missing,
            "  listed, not in the scheme: %s" % extra]

    trans = [t for t in doc.get("transitions", []) if isinstance(t, dict)]
    used = set()
    rows = []
    wrong = {"placed": 0, "energy": 0, "intensity": 0}
    for w in want["transitions"]:
        hits = [k for k, t in enumerate(trans)
                if close(t.get("from_keV", -1e9), w["from_keV"], KEV) and close(t.get("to_keV", -1e9), w["to_keV"], KEV)]
        if len(hits) != 1:
            wrong["placed"] += 1
            by_energy = nearest(w["energy_keV"], [t.get("energy_keV", -1e9) for t in trans])
            rows.append("  %8.1f -> %8.1f  E %8.2f  I %6.2f  NOT PLACED (%d entries); nearest listed energy %s"
                        % (w["from_keV"], w["to_keV"], w["energy_keV"], w["relative_intensity"], len(hits), by_energy))
            continue
        used.add(hits[0])
        t = trans[hits[0]]
        notes = []
        if not close(t.get("energy_keV", -1e9), w["energy_keV"], KEV):
            wrong["energy"] += 1
            notes.append("ENERGY %s" % t.get("energy_keV"))
        i = t.get("relative_intensity", -1e9)
        if not close(i, w["relative_intensity"], w["relative_intensity"] * INTENSITY):
            wrong["intensity"] += 1
            notes.append("INTENSITY %s" % i)
        if notes:
            rows.append("  %8.1f -> %8.1f  E %8.2f  I %6.2f  %s" % (w["from_keV"], w["to_keV"], w["energy_keV"],
                                                                     w["relative_intensity"], "; ".join(notes)))
    others = [t for k, t in enumerate(trans) if k not in used]
    out += ["transitions: %d listed, %d in the scheme; not placed %d, energy out %d, intensity out %d"
            % (len(trans), len(want["transitions"]), wrong["placed"], wrong["energy"], wrong["intensity"])]
    out += rows
    out.append("  listed, not in the scheme: %d" % len(others))
    for t in others:
        out.append("  %8s -> %8s  E %8s  I %8s" % (t.get("from_keV"), t.get("to_keV"), t.get("energy_keV"), t.get("relative_intensity")))

    iso = doc.get("isomer") if isinstance(doc.get("isomer"), dict) else {}
    w = want["isomer"]
    lev, half = iso.get("level_keV"), iso.get("half_life_ns")
    good_lev = isinstance(lev, (int, float)) and close(lev, w["level_keV"], KEV)
    good_half = isinstance(half, (int, float)) and close(half, w["half_life_ns"], w["half_life_ns"] * ISOMER_HALF_LIFE)
    out.append("isomer: level %s against %s: %s; half-life %s against %s: %s"
               % (lev, w["level_keV"], "ok" if good_lev else "OUT", half, w["half_life_ns"], "ok" if good_half else "OUT"))
    return out + [""]


def main():
    want = json.load(open(sys.argv[1], encoding="utf-8"))
    out = ["# Attempts against the scheme", ""]
    for arg in sys.argv[3:]:
        name, path = arg.split("=", 1)
        out += report(name, path, want)
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote", sys.argv[2])


if __name__ == "__main__":
    main()
