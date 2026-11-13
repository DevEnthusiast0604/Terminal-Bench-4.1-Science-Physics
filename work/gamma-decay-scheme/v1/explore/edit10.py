"""checks.txt: what the one wider scheme adds, and the reference's run time."""
from pathlib import Path

S = Path("tasks/active/gamma-decay-scheme")

p = S / "solution" / "solve.py"
s = p.read_text(encoding="utf-8")
old = """    DIAG["search_counts"].append((max_levels + 1, len(search(lines, flags, ceiling, order, max_levels + 1))))
"""
new = """    wider = search(lines, flags, ceiling, order, max_levels + 1)
    DIAG["search_counts"].append((max_levels + 1, len(wider)))
    DIAG["wider_schemes"] = [{"levels": sorted(w[0]), "unseen": len(w[2])} for w in wider]
"""
assert old in s
p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

for gen in (S / "tests" / "generate.py", Path("work/gamma-decay-scheme/v1/generate_draft.py")):
    g = gen.read_text(encoding="utf-8")
    old = """        out.append("schemes with at most %d levels, ground state included: %d" % (m, n))
    out += ["", "[sum peaks:"""
    new = """        out.append("schemes with at most %d levels, ground state included: %d" % (m, n))
    for w in diag["wider_schemes"]:
        extra = [v for v in w["levels"] if not any(x - 0.5 <= v <= x + 0.5 for x in expected["levels_keV"])]
        out.append("%d levels, %d unseen transitions%s" % (len(w["levels"]), w["unseen"],
                                                          ", extra level at %.1f keV" % extra[0] if extra else ""))
    out += ["", "[sum peaks:"""
    assert old in g
    g = g.replace(old, new)
    old = """def write_checks(expected, result, diag, phi, fw, n1, n2, n3):"""
    new = """def write_checks(expected, result, diag, phi, fw, n1, n2, n3, seconds):"""
    assert old in g
    g = g.replace(old, new)
    old = """            "daughter decays per parent decay within a cycle: %.3f" % phi]
"""
    new = """            "daughter decays per parent decay within a cycle: %.3f" % phi,
            "the reference reduction's run time on one CPU: %.0f s" % seconds]
"""
    assert old in g
    g = g.replace(old, new)
    old = """        subprocess.run([sys.executable, "-X", "utf8", "-I", "-B", str(TASK / "solution" / "solve.py"), str(DATA), tmp,
                        "--diag", str(diag_path)], check=True)
"""
    new = """        started = time.time()
        subprocess.run([sys.executable, "-X", "utf8", "-I", "-B", str(TASK / "solution" / "solve.py"), str(DATA), tmp,
                        "--diag", str(diag_path)], check=True)
        seconds = time.time() - started
"""
    assert old in g
    g = g.replace(old, new)
    old = """    write_checks(expected, result, diag, phi, fw, n1, n2, len(rows))
"""
    new = """    write_checks(expected, result, diag, phi, fw, n1, n2, len(rows), seconds)
"""
    assert old in g
    g = g.replace(old, new)
    old = """import tempfile
"""
    new = """import tempfile
import time
"""
    assert old in g
    g = g.replace(old, new, 1)
    gen.write_text(g, encoding="utf-8", newline="\n")
print("done")
