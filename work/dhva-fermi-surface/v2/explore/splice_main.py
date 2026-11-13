from pathlib import Path
gen = Path("tasks/active/dhva-fermi-surface/tests/generate.py")
new = Path("work/dhva-fermi-surface/v2/explore/main_v2.txt").read_text(encoding="utf-8")

# fixes to the draft
new = new.replace('''    clean = build(np.random.default_rng(SEED), noise=False)
    h = clean[0]["B"]
    ratio = clean[0]["B_int"] / h
    pick = [int(np.argmin(np.abs(h - v))) for v in (5.0, 14.0, 20.0, 35.0)]
    out.append("   B / mu0 H in the coldest sweep (noise-free) at 5, 14, 20 and 35 T: %s"
               % ", ".join("%.5f" % ratio[k] for k in pick))
    sel = (h >= 14.0) & (h <= 35.0)
    scale_mass = float(np.mean(1.0 / h[sel]) / np.mean(1.0 / clean[0]["B_int"][sel]))
    out.append("   so over 14-35 T one cycle in 1/(mu0 H) is %.3f%% longer than in 1/B: every frequency read against the "
               "applied field is low by that" % (100 * (scale_mass - 1)))
    rows = []
    for s in clean:
        osc = s["M"] - steady_moment(s["B_int"])
''', '''    clean = build(np.random.default_rng(SEED), noise=False)
    h = clean[0]["B"]
    ratio = clean[0]["B_int"] / h
    pick = [int(np.argmin(np.abs(h - v))) for v in (5.0, 14.0, 20.0, 35.0)]
    out.append("   B / mu0 H in the coldest sweep (noise-free) at 5, 14, 20 and 35 T: %s"
               % ", ".join("%.5f" % ratio[k] for k in pick))

    def stretch(win):
        """Delta(1/mu0 H) / Delta(1/B) over a window of the applied field: a frequency read against mu0 H there is F
        divided by this."""
        i0, i1 = int(np.argmin(np.abs(h - win[0]))), int(np.argmin(np.abs(h - win[1])))
        b = clean[0]["B_int"]
        return float((1.0 / h[i0] - 1.0 / h[i1]) / (1.0 / b[i0] - 1.0 / b[i1]))

    out.append("   so a frequency read against the applied field is F divided by %.5f over 6-35 T, %.5f over 14-35 T and "
               "%.5f over 22-35 T" % (stretch((6.0, 35.0)), stretch((14.0, 35.0)), stretch((22.0, 35.0))))
    rows = []
    for s in clean:
        osc = sample_moment(s["B_int"], s["T"]) - steady_moment(s["B_int"])
''')
new = new.replace('''    out.append("   against the applied field as read (no conversion), each peak named by the orbits' frequencies "
               "divided by %.4f:" % scale_mass)
    for k, win in [(0, S.W_SEARCH), (0, S.W_HIGH), (9, S.W_HOT)]:
        pk = S.peaks_of(applied[k], win)
        width = 0.25 * S.lobe(win)
        out.append("   %5.2f K, %g-%g T: %s" % (applied[k]["T"], win[0], win[1], ", ".join(
            "%.1f (%.0f, %s)" % (p["f"], p["snr"], label_peak(p["f"], width, scale_mass)) for p in pk) or "none"))''',
'''    out.append("   against the applied field as read (no conversion), each peak named by the orbits' frequencies "
               "divided by the window's stretch (section 1):")
    for k, win in [(0, S.W_SEARCH), (0, S.W_HIGH), (9, S.W_HOT)]:
        pk = S.peaks_of(applied[k], win)
        width = 0.25 * S.lobe(win)
        out.append("   %5.2f K, %g-%g T: %s" % (applied[k]["T"], win[0], win[1], ", ".join(
            "%.1f (%.0f, %s)" % (p["f"], p["snr"], label_peak(p["f"], width, stretch(win))) for p in pk) or "none"))''')
new = new.replace('''    for label, outdir, t0, proc in procs:
        proc.wait()
    results = {}
    for label, outdir, t0, proc in procs:
        if proc.returncode != 0:
            raise SystemExit("the reference failed on %s" % label)
        results[label] = (json.loads((outdir / "orbits.json").read_text(encoding="utf-8"))["orbits"],
                          json.loads((outdir / "diagnostics.json").read_text(encoding="utf-8")),
                          time.time() - t0)''', '''    for th in watchers:
        th.join()
    results = {}
    for label, outdir, t0, proc in procs:
        if proc.returncode != 0:
            raise SystemExit("the reference failed on %s" % label)
        results[label] = (json.loads((outdir / "orbits.json").read_text(encoding="utf-8"))["orbits"],
                          json.loads((outdir / "diagnostics.json").read_text(encoding="utf-8")),
                          finish[label])''')
new = new.replace('''        procs.append((label, outdir, time.time(), start_reference(folder, outdir, frame)))
''', '''        procs.append((label, outdir, time.time(), start_reference(folder, outdir, frame)))
    finish = {}

    def watch(label, t0, proc):
        proc.wait()
        finish[label] = time.time() - t0

    watchers = [threading.Thread(target=watch, args=(label, t0, proc), daemon=True) for label, _, t0, proc in procs]
    for th in watchers:
        th.start()
''')
assert "scale_mass" not in new, "scale_mass left"
t = gen.read_text(encoding="utf-8")
i = t.index("def main():")
j = t.index('if __name__ == "__main__":')
t = t[:i] + new + t[j:]
t = t.replace("import tempfile\nimport time\n", "import tempfile\nimport threading\nimport time\n", 1)
assert "import threading" in t
gen.write_text(t, encoding="utf-8", newline="\n")
import ast; ast.parse(t)
print("spliced", len(t.splitlines()), "lines")
