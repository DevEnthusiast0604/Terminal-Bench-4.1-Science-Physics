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

def per(body, x):
    s, k2 = body(x)
    ha, hb = s, L - s
    return (2 * math.pi * math.sqrt((k2 + ha * ha) / (G * ha)), 2 * math.pi * math.sqrt((k2 + hb * hb) / (G * hb)), ha, hb, k2)

rows = []
for heavy in (1.8, 2.2, 2.6, 3.0, 3.4):
    for hpos in (-0.12, -0.08, -0.04):
        for light in (0.3, 0.6, 0.9, 1.2):
            for slm in (1.2, 1.6, 2.0):
                body = make(1.4, -0.18, 1.18, [(heavy, hpos, 0.0025), (light, 1.12, 0.0010)], slm, 0.0010)
                xs = np.linspace(0.08, 0.92, 169)
                d = [(lambda p: (p[0] - p[1]) / p[0])(per(body, x)) for x in xs]
                for i in range(len(xs) - 1):
                    if d[i] * d[i + 1] < 0:
                        x0 = xs[i] - d[i] * (xs[i + 1] - xs[i]) / (d[i + 1] - d[i])
                        ta, tb, ha, hb, k2 = per(body, x0)
                        if abs(ha - hb) < 0.1:
                            continue
                        slope = (d[i + 1] - d[i]) / (xs[i + 1] - xs[i])
                        D = ha - hb
                        sens = 2 * abs(slope) * 0.06 * 0.0015 * L / D ** 2   # g error at +-60 mm with a 1.5 mm balance error
                        rows.append((round(sens, 6), heavy, hpos, light, slm, round(x0, 3), round(ha, 3), round(slope, 3)))
rows.sort(reverse=True)
for r in rows[:25]:
    print(r)
