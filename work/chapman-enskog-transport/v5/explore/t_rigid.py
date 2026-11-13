"""Rigid-sphere checks of mixsolve: identical masses -> pure gas; first approximations."""
import time
import mpmath as mp
import numpy as np
from mixsolve import Brackets, transport, rigid_omega

P = 10
t0 = time.time()
br = Brackets(1.0, 1.0, P + 2)
print("brackets %.1f s" % (time.time() - t0))
om = rigid_omega(1.0, 1.0, 1.0)
eta1 = 5 / (16 * np.sqrt(np.pi))
D1 = 3 / (8 * np.sqrt(np.pi))
for Pm in (1, 2, 3, 5, 8, 10):
    r = transport(br, 0.5, 1.0, om, Pm)
    print(Pm, "eta/eta1 %.9f" % (r["eta"] / eta1), "lam/(15/4 eta1) %.9f" % (r["lambda"] / (3.75 * eta1)),
          "D/D1 %.9f" % (r["D12"] / D1), "alphaT %.2e" % r["alpha_T"])
print("expect eta 1.016034, lambda 1.025218, D 1.018954 (limits)")
