import math, numpy as np
G, L = 9.79184, 1.00003

def make(rod_m, rod_a, rod_b, bobs, sl_m, sl_i):
    def body(x):
        parts = [(rod_m, 0.5 * (rod_a + rod_b), rod_m * (rod_b - rod_a) ** 2 / 12)] + list(bobs) + [(sl_m, x, sl_i)]
        M = sum(p[0] for p in parts)
        s = sum(p[0] * p[1] for p in parts) / M
        I = sum(p[2] + p[0] * (p[1] - s) ** 2 for p in parts)
        return s, I / M
    return body

def rel(body, x):
    s, k2 = body(x)
    ha, hb = s, L - s
    ta = 2 * math.pi * math.sqrt((k2 + ha * ha) / (G * ha)); tb = 2 * math.pi * math.sqrt((k2 + hb * hb) / (G * hb))
    return (ta - tb) / ta, ha

rows = []
for heavy in np.arange(1.6, 4.01, 0.2):
    for hpos in (-0.14, -0.11, -0.08, -0.05):
        for light in np.arange(0.2, 1.61, 0.1):
            for slm in (1.0, 1.4, 1.8, 2.2):
                body = make(1.4, -0.18, 1.18, [(heavy, hpos, 0.0025), (light, 1.12, 0.0010)], slm, 0.0010)
                xs = np.linspace(0.06, 0.94, 177)
                d = np.array([rel(body, x)[0] for x in xs])
                idx = np.flatnonzero(d[:-1] * d[1:] < 0)
                cr = [xs[i] - d[i] * (xs[i + 1] - xs[i]) / (d[i + 1] - d[i]) for i in idx]
                for x0 in cr:
                    r0, ha = rel(body, x0)
                    if not (0.55 <= x0 <= 0.80 and 0.36 <= ha <= 0.43):
                        continue
                    if any(abs(c - x0) < 0.25 for c in cr if c != x0):
                        continue
                    slope = (rel(body, x0 + 0.005)[0] - rel(body, x0 - 0.005)[0]) / 0.01
                    D = 2 * ha - L
                    sens = 2 * abs(slope) * 0.06 * 0.0015 * L / D ** 2
                    rows.append((round(sens, 6), round(heavy, 2), hpos, round(light, 2), slm, round(x0, 4), round(ha, 4), round(slope, 4), [round(c, 3) for c in cr]))
rows.sort(reverse=True)
for r in rows[:20]:
    print(r)
print(len(rows))
