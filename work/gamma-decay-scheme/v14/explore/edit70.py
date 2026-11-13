"""v14: a partner weaker than both members of a doublet that lies in one cascade, and that comes with more than one of
the doublet's gamma rays per gamma ray of its own, is in coincidence with both members: each member adds at most one.
The flag then holds whatever the gated centroid says. Exact-match replacement in solution/solve.py; run from the
folder root."""
PATH = "tasks/active/gamma-decay-scheme/solution/solve.py"
s = open(PATH, encoding="utf-8", newline="").read()
old = """            # For a member of a doublet only a centroid in a gate says which of the two a partner goes with. A gate
            # whose centroid sits on the strong member says nothing about a weak one: its share hardly moves it.
            for x, y in ((a, b), (b, a)):
                if x["member"] and f == 1:
"""
new = """            # Each member of a doublet in one cascade adds at most one of its gamma rays per gamma ray of a weaker
            # partner. A partner that comes with clearly more than one from the doublet's peak sees both members.
            both = False
            for x, y in ((a, b), (b, a)):
                if x["member"] and x.get("self") and f == 1:
                    if y["I"] <= min(l["I"] for l in lines if l["peak"] == x["peak"]):
                        per = k_scale * float(eff(a["peak"])) * float(eff(b["peak"])) * y["I"]
                        both = both or (tot - 3.0 * sigma) / per > 1.15
            # For a member of a doublet only a centroid in a gate says which of the two a partner goes with. A gate
            # whose centroid sits on the strong member says nothing about a weak one: its share hardly moves it.
            for x, y in ((a, b), (b, a)):
                if x["member"] and f == 1 and not both:
"""
assert s.count(old) == 1
s = s.replace(old, new)
assert "\r" not in s
open(PATH, "w", encoding="utf-8", newline="").write(s)
print("solve.py edited")
