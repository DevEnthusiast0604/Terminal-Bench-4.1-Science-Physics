import math, numpy as np
G = 9.79184
L = 1.00003

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

best = []
for heavy in (2.0, 2.5, 3.0, 3.5):
    for light in (0.5, 0.8, 1.0, 1.3):
        for slm in (0.6, 0.9, 1.2):
            body = make(1.6, -0.18, 1.18, [(heavy, -0.11, 0.0025), (light, 1.11, 0.0010)], slm, 0.0008)
            xs = np.linspace(0.05, 0.95, 181)
            d = [per(body, x)[0] - per(body, x)[1] for x in xs]
            for i in range(len(xs) - 1):
                if d[i] * d[i + 1] < 0:
                    x0 = xs[i] - d[i] * (xs[i + 1] - xs[i]) / (d[i + 1] - d[i])
                    ta, tb, ha, hb, k2 = per(body, x0)
                    slope = (per(body, x0 + 0.01)[0] - per(body, x0 + 0.01)[1] - (per(body, x0 - 0.01)[0] - per(body, x0 - 0.01)[1])) / 0.02
                    kind = "conj" if abs(ha - hb) > 0.05 else "sym"
                    best.append((heavy, light, slm, round(x0, 4), kind, round(ha, 4), round(hb, 4), round(slope / ta, 4)))
for b in best:
    print(b)
