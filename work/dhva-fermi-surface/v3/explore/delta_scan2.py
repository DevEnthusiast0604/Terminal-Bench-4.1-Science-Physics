"""Integer combinations n of the five other orbits (sum |n| <= 10, as attempt 1 of v2 searched), and the half-integer
'mean beta' readings: for each candidate (F, m) of delta, how many lie within 0.1% in frequency and 15% in mass?
Plus the nearest harmonic p <= 8 of another orbit and the lightest combination within 0.1%."""
import itertools
orb = [(461.30, 0.660), (927.60, 0.270), (1186.40, 0.480), (2641.00, 1.210), (2702.60, 1.290)]
combos = []
for n in itertools.product(range(-10, 11), repeat=5):
    s = sum(abs(k) for k in n)
    if s == 0 or s > 10:
        continue
    F = sum(k * o[0] for k, o in zip(n, orb))
    if 7000 < F < 8000:
        combos.append((F, sum(abs(k) * o[1] for k, o in zip(n, orb)), n))
print("combinations in 7000-8000 T:", len(combos))
lightest = min(m for F, m, n in combos)
print("lightest combination mass in 7000-8000 T: %.3f" % lightest)
harm = sorted(p * o[0] for o in orb for p in range(1, 9))
for F0 in (7415, 7290, 7300, 7310, 7320, 7330, 7540, 7560, 7580, 7600):
    for m0 in (3.35, 2.6, 1.9, 1.7):
        near = [(F, m, n) for F, m, n in combos if abs(F / F0 - 1) < 0.001 and abs(m / m0 - 1) < 0.15]
        within = [(F, m, n) for F, m, n in combos if abs(F / F0 - 1) < 0.001]
        hn = min(harm, key=lambda h: abs(h - F0))
        print("F %5.0f m %.2f: combos within 0.1%%: %3d, of them mass within 15%%: %2d; lightest of them %.2f; nearest harmonic %.1f (%+.0f T)"
              % (F0, m0, len(within), len(near), min((m for F, m, n in within), default=float("nan")), hn, hn - F0))
