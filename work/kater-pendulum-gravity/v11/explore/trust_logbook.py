"""The oracle with session.json's logbook pivots trusted (no assign_pivots); errors / tolerance for h1."""
import importlib.util, os, sys
task = sys.argv[1]
sys.path.insert(0, os.path.join(task, "tests"))
import generate as G
spec = importlib.util.spec_from_file_location("reduce", os.path.join(task, "solution", "reduce.py"))
R = importlib.util.module_from_spec(spec); spec.loader.exec_module(R)
R.assign_pivots = lambda runs, logged: (dict(logged), {r: 0.0 for r in runs})
for name in sys.argv[2:]:
    got, want = R.reduce_session(os.path.join(task, "tests/cases", name)), G.truth(name)
    rel = lambda h, w, t: (h / w - 1) / t
    print(name, "g %+.1f" % rel(got["g_m_s2"], want["g_m_s2"], 4e-4), "k %+.1f" % rel(got["radius_of_gyration_m"], want["radius_of_gyration_m"], 1e-3),
          " ".join("T_%s %+.1f" % (p, rel(got["small_amplitude_period_s"][p], want["small_amplitude_period_s"][p], 1e-4)) for p in "ab"),
          " ".join("P_%s %+.1f" % (r, rel(got["run_periods_s"][r], want["run_periods_s"][r], 1e-4)) for r in sorted(want["run_periods_s"])),
          " ".join("A_%s %+.2f" % (r, rel(got["release_amplitude_rad"][r], want["release_amplitude_rad"][r], 2e-3)) for r in sorted(want["release_amplitude_rad"])))
