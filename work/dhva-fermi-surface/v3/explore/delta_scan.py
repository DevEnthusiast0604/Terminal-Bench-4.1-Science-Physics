"""Where can delta sit so that no harmonic (p <= 8) of another orbit and no low-order combination of the others,
with a summed mass near delta's, lies close to it? Prints the nearest offenders for candidate frequencies."""
import itertools
orb = {"alpha": (461.30, 0.660), "gamma": (927.60, 0.270), "epsilon": (1186.40, 0.480),
       "beta_neck": (2641.00, 1.210), "beta_belly": (2702.60, 1.290)}
M_DELTA = 3.35
names = list(orb)
combos = []
rng = range(-4, 5)
for n in itertools.product(rng, repeat=len(names)):
    s = sum(abs(k) for k in n)
    if s == 0 or s > 6:
        continue
    F = sum(k * orb[nm][0] for k, nm in zip(n, names))
    m = sum(abs(k) * orb[nm][1] for k, nm in zip(n, names))
    if 6800 < F < 8200:
        combos.append((F, m, n))
# half-integer readings like "4 eps + (neck + belly)/2"
for a in range(1, 7):
    for b in range(0, 3):
        F = a * orb["epsilon"][0] + b * 0.5 * (orb["beta_neck"][0] + orb["beta_belly"][0])
        if 6800 < F < 8200:
            combos.append((F, a * 0.48 + b * 1.25, ("%d eps + %d mean beta" % (a, b),)))
harm = [(p * orb[nm][0], p * orb[nm][1], nm, p) for nm in names for p in range(1, 9)]

def label(n):
    if isinstance(n[0], str):
        return n[0]
    return " ".join("%+d%s" % (k, nm[:3]) for k, nm in zip(n, names) if k)

for F0 in [7415, 7240, 7260, 7280, 7300, 7320, 7340, 7500, 7520, 7540, 7560, 7580, 7600, 7620, 7640, 7660, 7680, 7700, 7720, 7740, 7760, 7780]:
    hn = min(harm, key=lambda h: abs(h[0] - F0))
    near = [(abs(F - F0) / F0, F, m, n) for F, m, n in combos if abs(F - F0) / F0 < 0.005 and abs(m / M_DELTA - 1) < 0.25]
    near.sort()
    print("%6.0f  nearest harmonic %d x %s = %.1f (%+.1f T, %+.2f%%)  low-order sums within 0.5%% and mass within 25%%: %d %s"
          % (F0, hn[3], hn[2], hn[0], hn[0] - F0, 100 * (hn[0] / F0 - 1), len(near),
             "; ".join("%s = %.1f (%.2f%%, m %.2f)" % (label(n), F, 100 * d, m) for d, F, m, n in near[:3])))
