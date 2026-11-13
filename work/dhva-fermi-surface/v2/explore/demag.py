"""Aharoni (1998) magnetometric demagnetizing factor of a rectangular prism 2a x 2b x 2c, field along c."""
import math, sys

def demag_prism(a, b, c):
    a, b, c = 0.5 * a, 0.5 * b, 0.5 * c          # half-lengths
    r = math.sqrt(a * a + b * b + c * c)
    ab, bc, ac = math.sqrt(a * a + b * b), math.sqrt(b * b + c * c), math.sqrt(a * a + c * c)
    s = ((b * b - c * c) / (2 * b * c) * math.log((r - a) / (r + a))
         + (a * a - c * c) / (2 * a * c) * math.log((r - b) / (r + b))
         + b / (2 * c) * math.log((ab + a) / (ab - a))
         + a / (2 * c) * math.log((ab + b) / (ab - b))
         + c / (2 * a) * math.log((bc - b) / (bc + b))
         + c / (2 * b) * math.log((ac - a) / (ac + a))
         + 2 * math.atan(a * b / (c * r))
         + (a ** 3 + b ** 3 - 2 * c ** 3) / (3 * a * b * c)
         + (a * a + b * b - 2 * c * c) / (3 * a * b * c) * r
         + c / (a * b) * (ac + bc)
         - (ab ** 3 + bc ** 3 + ac ** 3) / (3 * a * b * c))
    return s / math.pi

def prolate(m):
    return (m / math.sqrt(m * m - 1) * math.log(m + math.sqrt(m * m - 1)) - 1) / (m * m - 1)

for dims in [(1, 1, 1), (1, 1, 2), (1, 1, 8), (0.25, 0.2, 1.6), (0.6, 0.5, 0.15), (10, 10, 0.1)]:
    print(dims, "N_c = %.5f" % demag_prism(*dims))
print("cube sum check", demag_prism(1, 2, 3) + demag_prism(2, 3, 1) + demag_prism(3, 1, 2))
print("prolate spheroid m=8: %.5f, m=7.1: %.5f" % (prolate(8), prolate(7.1)))
