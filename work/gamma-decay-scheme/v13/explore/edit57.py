"""v13: revert the temporary failure printout (debug56) and place the lines found on a peak of another origin after
the clean ones: a line can only start above a level that the lines before it made. Run from the folder root."""
PATH = "tasks/active/gamma-decay-scheme/solution/solve.py"
s = open(PATH, encoding="utf-8", newline="").read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:80])
    s = s.replace(old, new)


rep("""        # DEBUG56
        for i in range(len(lines)):
            for k in range(len(lines)):
                if k != i:
                    print("DBG %8.2f %8.2f flag %s strength %.4f ceiling %.4f" % (lines[i]["E"], lines[k]["E"], flags[i][k],
                          strength[i][k], ceiling[i][k]), file=sys.stderr)
""", "")
rep("""    # Lines in delayed coincidence are placed last: where they land may have to be inferred from where they start.
    order = sorted(range(len(lines)), key=lambda i: (lines[i]["delayed_feeder"], -lines[i]["I"]))
""", """    # Lines in delayed coincidence are placed last: where they land may have to be inferred from where they start.
    # Lines found on a peak of another origin come just before them. A line can only start above a level that the
    # lines placed before it made, and their levels are made by clean lines.
    order = sorted(range(len(lines)), key=lambda i: (lines[i]["delayed_feeder"], lines[i].get("share", 1.0) < 0.9
                                                     or bool(lines[i].get("annihilation_line")), -lines[i]["I"]))
""")
open(PATH, "w", encoding="utf-8", newline="").write(s)
print("solve.py edited")
