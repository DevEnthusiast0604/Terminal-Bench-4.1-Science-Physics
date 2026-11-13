from pathlib import Path
sol = Path("tasks/active/gamma-decay-scheme/solution/solve.py")
t = sol.read_text(encoding="utf-8")
old = """                if flags[i][k] == 1 and not p:
                    return
                if flags[i][k] == 0 and p:
                    return
"""
new = """                if flags[i][k] == 1 and not p:
                    REJECTS.append(("flag 1 without a path", lines[i]["E"], lines[k]["E"]))
                    return
                if flags[i][k] == 0 and p:
                    REJECTS.append(("flag 0 with a path", lines[i]["E"], lines[k]["E"]))
                    return
"""
assert old in t
t = t.replace(old, new)
old = """            if into > 1.2 * outof + 0.5:
                return
"""
new = """            if into > 1.2 * outof + 0.5:
                REJECTS.append(("balance", levels[a], into, outof))
                return
"""
assert old in t
t = t.replace(old, new)
old = """                if not below:
                    return
"""
new = """                if not below:
                    REJECTS.append(("no decay", levels[a]))
                    return
"""
assert old in t
t = t.replace(old, new)
t = t.replace("DEPTHS = {}\n", "DEPTHS = {}\nREJECTS = []\n")
sol.write_text(t, encoding="utf-8", newline="\n")
s = Path("work/gamma-decay-scheme/v1/explore/stages.py").read_text(encoding="utf-8")
s = s.replace("""            print("depths", sorted(S.DEPTHS.items()), flush=True)
        except""", """            print("depths", sorted(S.DEPTHS.items()), flush=True)
            print("rejects", S.REJECTS[-8:], flush=True)
        except""")
Path("work/gamma-decay-scheme/v1/explore/stages.py").write_text(s, encoding="utf-8", newline="\n")
