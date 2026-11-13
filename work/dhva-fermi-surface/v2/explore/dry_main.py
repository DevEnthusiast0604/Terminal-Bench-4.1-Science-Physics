"""Runs generate.main() with the reference replaced by a no-op process: sections 1, 2 and the start of 4 must run."""
import importlib.util, subprocess, sys, time
from pathlib import Path
TASK = Path("tasks/active/dhva-fermi-surface")
spec = importlib.util.spec_from_file_location("gen", TASK / "tests" / "generate.py")
G = importlib.util.module_from_spec(spec); spec.loader.exec_module(G)
G.REDRAWS = 0
G.start_reference = lambda d, o, frame="internal": subprocess.Popen([sys.executable, "-c", "pass"])
t0 = time.time()
try:
    G.main()
except FileNotFoundError as e:
    print("reached the results (expected stop):", type(e).__name__, "after %.0f s" % (time.time() - t0))
