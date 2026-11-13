import sys, os
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
import solve as S
mode = sys.argv[4]
if mode in ("gain", "none"):
    S.asymmetry = lambda runs, rho: 0.0
if mode == "none":
    S.golden = lambda fn, lo, hi, n=60: 1.0
S.main(sys.argv[2], sys.argv[3])
