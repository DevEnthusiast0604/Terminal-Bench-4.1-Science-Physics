from pathlib import Path
sol = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
t = sol.read_text(encoding="utf-8")
old = """    def step(pos):
        count[0] += 1
"""
new = """    def step(pos):
        count[0] += 1
        DEPTHS[pos] = DEPTHS.get(pos, 0) + 1
"""
assert old in t
t = t.replace(old, new)
old = "def search(lines, flags, upper, order, max_levels, limit=400000):\n"
new = "DEPTHS = {}\n\n\ndef search(lines, flags, upper, order, max_levels, limit=400000):\n"
assert old in t
t = t.replace(old, new)
sol.write_text(t, encoding="utf-8", newline="\n")
s = Path("work/gamma-decay-scheme/v1/explore/stages.py").read_text(encoding="utf-8")
s = s.replace("""    import time
    for m in range(14, 19):
        t0 = time.time()
        try:
            sols = S.search(lines2, flags, upper, order, m)
""", """    import time
    print("order:", [(round(lines2[i]["E"], 1), round(lines2[i]["I"], 1)) for i in order], flush=True)
    for m in range(14, 19):
        t0 = time.time()
        S.DEPTHS.clear()
        try:
            sols = S.search(lines2, flags, upper, order, m, limit=int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else 400000)
            print("depths", sorted(S.DEPTHS.items()), flush=True)
""")
s = s.replace("""            print("max levels", m, ex, "%.1f s" % (time.time() - t0))
""", """            print("max levels", m, ex, "%.1f s" % (time.time() - t0))
            print("depths", sorted(S.DEPTHS.items()), flush=True)
""")
Path("work/gamma-decay-scheme/v1/explore/stages.py").write_text(s, encoding="utf-8", newline="\n")
