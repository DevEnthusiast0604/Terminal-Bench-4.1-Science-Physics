"""Compare each pass@3 attempt's planets.json with rv-planet-census's expected.json (data deliverable).

    python -X utf8 -I -B tools/census_report.py EXPECTED.json OUT.md ATTEMPT_NAME=PATH [ATTEMPT_NAME=PATH ...]

pass3_report.py is program-mode only and scheme_report.py is gamma's. This one only reads JSON files, so pointing it
at the untrusted extraction under work/<slug>/v<N>/pass3/x/ is safe. It repeats the grader's tests with the
instruction's bands (tests/test_outputs.py) and names the signal behind every missing or extra period (alias,
rotation, the eclipsing binary, a harmonic), so the report shows which trap an attempt fell into. It also prints the
eccentricity factor each reported minimum mass implies (mass / circular-orbit mass from the reported K and P): above
1 no eccentricity can make the two fields agree.
"""
import json
import math
import sys

PERIOD, AMPLITUDE, MASS, RADIUS, ROTATION = 0.02, 0.25, 0.25, 0.08, 0.10
TOP_KEYS = ["planets", "rotation_period_days"]
PLANET_KEYS = ["period_days", "semi_amplitude_m_s", "minimum_mass_earth", "radius_earth"]
GM_SUN, GM_EARTH, DAY = 1.3271244e20, 3.986004e14, 86400.0   # tests/generate.py
M_STAR = 0.690                                               # NOTES.md
SIDEREAL = 1.0027379                                         # cycles per solar day of the one-day alias
YEAR = 365.25
BINARY = 6.0473                                              # the second star's eclipsing binary (tests/generate.py)
UNDILUTED = (1.0 + 10 ** (-0.4 * 1.20)) ** -0.5              # radius factor when the second star's light is ignored


def number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def within(have, want, frac):
    return number(have) and abs(have - want) <= abs(want) * frac + 1e-12


def circular_mass(k, p):
    return k * (p * DAY / (2 * math.pi)) ** (1 / 3) * (GM_SUN * M_STAR) ** (2 / 3) / GM_EARTH


def signals(want):
    """Named periods an attempt may report instead of, or beside, the right ones."""
    out = []
    prot = want["rotation_period_days"]
    for f, name in ((1, "P_rot"), (0.5, "P_rot/2"), (1 / 3, "P_rot/3"), (2, "2 P_rot")):
        out.append((prot * f, name))
    for f, name in ((1, "the binary"), (0.5, "half the binary period"), (2, "twice the binary period")):
        out.append((BINARY * f, name))
    for q in want["planets"]:
        p = q["period_days"]
        tag = "%.4g d" % p
        out.append((p, "the planet at " + tag))
        for f, name in ((0.5, "half of "), (2, "twice ")):
            out.append((p * f, name + tag))
        for df, name in ((SIDEREAL, "one-day alias"), (1 / YEAR, "one-year alias")):
            for sgn in (1, -1):
                nu = abs(1 / p + sgn * df)
                if nu > 1e-9:
                    out.append((1 / nu, "%s (%+d) of %s" % (name, sgn, tag)))
    return out


def label(p, named):
    v, name = min(named, key=lambda t: abs(math.log(p / t[0])))
    return "%s (%.4g d, %+.2f%%)" % (name, v, 100 * (p / v - 1))


def report(name, path, want):
    out = ["## %s" % name, ""]
    try:
        doc = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return out + ["could not read the deliverable: %s" % exc, ""], False
    named = signals(want)
    tests = {}
    shape = isinstance(doc, dict) and sorted(doc) == TOP_KEYS and number(doc.get("rotation_period_days")) \
        and isinstance(doc.get("planets"), list)
    planets = doc.get("planets") if shape else []
    for q in planets:
        if not (isinstance(q, dict) and sorted(q) == sorted(PLANET_KEYS) and all(number(q[k]) for k in PLANET_KEYS[:3])
                and (q["radius_earth"] is None or number(q["radius_earth"]))):
            shape = False
    tests["file_and_members"] = shape
    if not shape:
        out.append("members or types wrong: %s" % json.dumps(doc)[:400])
        return out + [""], False

    prot, rw = doc["rotation_period_days"], want["rotation_period_days"]
    tests["rotation_period"] = within(prot, rw, ROTATION)
    out.append("rotation: %s against %s (x%.3f): %s" % (prot, rw, prot / rw, "ok" if tests["rotation_period"] else "OUT"))

    used, found, k_ok, m_ok, r_ok = set(), True, True, True, True
    out.append("")
    out.append("| right P | reported P | K (dev) | m sin i (dev) | e factor | radius (dev) | verdict |")
    out.append("|---|---|---|---|---|---|---|")
    for w in want["planets"]:
        hits = [k for k, q in enumerate(planets) if within(q["period_days"], w["period_days"], PERIOD)]
        if len(hits) != 1:
            found = False
            near = min(planets, key=lambda q: abs(math.log(q["period_days"] / w["period_days"])), default=None) \
                if all(q["period_days"] > 0 for q in planets) else None
            out.append("| %s | %s | | | | | %s |" % (
                w["period_days"], "%d entries" % len(hits) if hits else "none",
                "MISSING; nearest reported %s" % (near["period_days"] if near else "-")))
            continue
        used.add(hits[0])
        q = planets[hits[0]]
        notes = []
        kd = q["semi_amplitude_m_s"] / w["semi_amplitude_m_s"] - 1
        md = q["minimum_mass_earth"] / w["minimum_mass_earth"] - 1
        ef = q["minimum_mass_earth"] / circular_mass(q["semi_amplitude_m_s"], q["period_days"]) \
            if q["semi_amplitude_m_s"] > 0 and q["period_days"] > 0 else float("nan")
        if not within(q["semi_amplitude_m_s"], w["semi_amplitude_m_s"], AMPLITUDE):
            k_ok = False
            notes.append("K OUT")
        if not within(q["minimum_mass_earth"], w["minimum_mass_earth"], MASS):
            m_ok = False
            notes.append("MASS OUT")
        if ef > 1.02:
            notes.append("mass above the circular value")
        rr, rh = w["radius_earth"], q["radius_earth"]
        if rr is None:
            rtxt = "null" if rh is None else "%s (should be null)" % rh
            if rh is not None:
                r_ok = False
                notes.append("RADIUS for a non-transiting planet")
        elif rh is None:
            rtxt = "null (right %s)" % rr
            r_ok = False
            notes.append("RADIUS null for a transiting planet")
        else:
            rtxt = "%s (%+.1f%%)" % (rh, 100 * (rh / rr - 1))
            if not within(rh, rr, RADIUS):
                r_ok = False
                notes.append("RADIUS OUT" + ("; the undiluted value is %.3g" % (rr * UNDILUTED)
                                             if abs(rh / (rr * UNDILUTED) - 1) < 0.05 else ""))
        out.append("| %s | %s (%+.3f%%) | %s (%+.1f%%) | %s (%+.1f%%) | %.3f | %s | %s |" % (
            w["period_days"], q["period_days"], 100 * (q["period_days"] / w["period_days"] - 1),
            q["semi_amplitude_m_s"], 100 * kd, q["minimum_mass_earth"], 100 * md, ef, rtxt,
            "; ".join(notes) if notes else "ok"))
    extra = [q for k, q in enumerate(planets) if k not in used]
    if extra:
        found = False
    out.append("")
    out.append("extra entries: %d" % len(extra))
    for q in extra:
        out.append("  P %s, K %s, m sin i %s, R %s: nearest named signal %s" % (
            q["period_days"], q["semi_amplitude_m_s"], q["minimum_mass_earth"], q["radius_earth"],
            label(q["period_days"], named) if q["period_days"] > 0 else "-"))
    tests["planets_found"] = found
    tests["semi_amplitudes"] = found and k_ok
    tests["minimum_masses"] = found and m_ok
    tests["radii"] = found and r_ok
    passed = all(tests.values())
    out.append("")
    out.append("tests: " + ", ".join("%s %s" % (k, "pass" if v else "FAIL") for k, v in tests.items()))
    out.append("would score: %d" % passed)
    return out + [""], passed


def main():
    want = json.load(open(sys.argv[1], encoding="utf-8"))
    out = ["# Attempts against the census", ""]
    scores = []
    for arg in sys.argv[3:]:
        name, path = arg.split("=", 1)
        lines, ok = report(name, path, want)
        out += lines
        scores.append("%s %d" % (name, ok))
    out.append("Scores by this report: " + ", ".join(scores) + ".")
    with open(sys.argv[2], "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(out) + "\n")
    print("wrote", sys.argv[2], "|", ", ".join(scores))


if __name__ == "__main__":
    main()
