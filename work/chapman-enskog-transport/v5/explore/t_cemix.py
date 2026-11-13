"""Check: the shipped tests/ce_mix.py against the exploration code (cached kihara_mix blocks) and v4's pure gas."""
import sys
import time

sys.path.insert(0, "../../../../tasks/active/chapman-enskog-transport/tests")
import ce_mix as M  # noqa: E402
H_from_blocks = M.H_from_blocks
from survey import props  # noqa: E402

if __name__ == "__main__":
    t0 = time.time()
    acc = M.blocks(0.31, 1.0, 1.27, 12)
    r = M.coefficients(acc, 1.0, 0.4, 1.27, 12)
    v4 = {"viscosity": 0.14833617534439164, "thermal_conductivity": 0.5566487361344096,
          "binary_diffusion": 0.19360890549197105}
    print("equal masses vs v4 k05:", {k: "%.1e" % abs(r[k] / v4[k] - 1) for k in v4}, "alpha_T %.1e" %
          r["thermal_diffusion_factor"], "(%.0f s)" % (time.time() - t0))
    t0 = time.time()
    acc = M.blocks(0.8, 25.0, 50.0, 12)
    old = M.load_blocks("cache/blk_A0.8_m25_T50_P48_w1_n16.npz")
    old = {k: v[:13, :13] for k, v in old.items()}
    for x1 in (0.05, 0.5):
        r = M.coefficients(acc, 25.0, x1, 50.0, 12)
        o = props(H_from_blocks(old, "tensor", 25.0, x1, 50.0), H_from_blocks(old, "vector", 25.0, x1, 50.0),
                  1.0, 25.0, x1, 50.0, 12)
        names = dict(viscosity="eta", thermal_conductivity="lambda", binary_diffusion="D12",
                     thermal_diffusion_factor="alpha_T")
        print("x1 %g P12 vs cached P48 sub-blocks:" % x1,
              {k: "%.1e" % abs(r[k] / float(o[v]) - 1) for k, v in names.items()}, "(%.0f s)" % (time.time() - t0))
