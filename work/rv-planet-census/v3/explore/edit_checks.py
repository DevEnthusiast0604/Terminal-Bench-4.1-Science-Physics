"""Edit the v3 draft generator's write_checks: search and 2:1 printing as helpers, and a section for the search run
again with a single dip's planet held at its conjunction. Usage (folder root):
python -X utf8 -I -B work/rv-planet-census/v3/explore/edit_checks.py"""
from pathlib import Path

p = Path("work/rv-planet-census/v3/task/rv-planet-census/tests/generate.py")
src = p.read_text(encoding="utf-8")
lines = src.split("\n")
start = next(i for i, l in enumerate(lines) if l == '    out += ["", "[the radial-velocity search, step by step]"]')
end = next(i for i, l in enumerate(lines) if l.startswith('    out += ["noise of the final model: %s" % diag["noise"],'))
old = lines[start:end]
assert old[-1].strip().startswith('"true orbit\'s at the same impact parameter'), old[-1]
new = '''    def search_lines(steps, ind=""):
        rows = []
        for s in steps:
            if "model" in s:
                rows.append(ind + "%s: lnL %.2f, noise %s" % (s["model"], s["lnL"], s["noise"]))
                continue
            rows.append(ind + "peaks %s -> %.5f d: dlnL %+.2f, K_vis %.2f +- %.2f, K_nir %.2f +- %.2f, ratio %.2f +- "
                        "%.2f: %s" % (s["periodogram_peaks"], s["period"], s["dlnL"], s["K_vis"], s["K_vis_err"],
                                      s["K_nir"], s["K_nir_err"], s["K_nir_over_K_vis"], s["ratio_err"], s["verdict"]))
            rows.append(ind + "    aliases fitted (period, chi-square above the best): %s"
                        % ", ".join("%.4f %+.1f" % (a, b) for a, b in s["aliases_dchi2"]))
        return rows

    def pair_lines(steps, ind=""):
        rows = []
        for s in steps:
            rows.append(ind + "planet at %.5f d as one eccentric orbit: K %.3f, e %.3f, omega %.3f, tc %.4f; lnL %.2f"
                        % (s["planet_period"], s["single_K"], s["single_e"], s["single_omega"], s["single_tc"],
                           s["single_lnL"]))
            if "dlnL" not in s:
                rows.append(ind + "    %s" % s["verdict"])
                continue
            rows.append(ind + "    circular, with a circular planet at 0.44 to 0.56 of its period: lnL %.2f, dlnL %+.2f; "
                        "outer %.5f d, K %.3f, e %.3f; inner %.5f d, K %.3f, e %.3f, K_vis %.2f +- %.2f, K_nir %.2f +- "
                        "%.2f: %s" % (s["pair_lnL"], s["dlnL"], s["outer_period"], s["outer_K"], s["outer_e"],
                                      s["inner_period"], s["inner_K"], s["inner_e"], s["inner_K_vis"],
                                      s["inner_K_vis_err"], s["inner_K_nir"], s["inner_K_nir_err"], s["verdict"]))
            want = min(PLANETS, key=lambda q: abs(q["P"] - s["planet_period"]))
            m1 = minimum_mass({"K": s["single_K"], "P": s["planet_period"], "e": s["single_e"]})
            rows.append(ind + "    the eccentric reading against the planet at %.4f d: K %+.1f percent, minimum mass %.3f "
                        "against %.3f, %+.1f percent" % (want["P"], pct(s["single_K"], want["K"]), m1,
                                                         minimum_mass(want), pct(m1, minimum_mass(want))))
            if want["R"] is not None:
                # where the eccentric reading puts the transit, and the impact parameter its speed at conjunction needs
                rho = lambda e, w: math.sqrt(1 - e * e) / (1 + e * math.sin(w))
                n = round((want["tc"] - s["single_tc"]) / s["planet_period"])
                off = s["single_tc"] + n * s["planet_period"] - want["tc"]
                k = want["R"] * R_EARTH / (R_STAR * R_SUN)
                factor = rho(s["single_e"], s["single_omega"]) / rho(want["e"], want["w"])
                chord = math.sqrt((1 + k) ** 2 - want["b"] ** 2) / factor
                mu = lambda b: math.sqrt(max(1 - b * b, 0.0))
                inten = lambda b: 1 - LD_U1 * (1 - mu(b)) - LD_U2 * (1 - mu(b)) ** 2
                if chord > 1 + k:
                    need = "no impact parameter gives it"
                else:
                    b1 = math.sqrt((1 + k) ** 2 - chord ** 2)
                    need = ("it needs b %.2f (true %.2f), where the limb is %s: the same depth then needs a radius "
                            "about %+.0f percent larger" % (b1, want["b"], "darker" if b1 > want["b"] else "brighter",
                                                           100 * (math.sqrt(inten(want["b"]) / inten(b1)) - 1)))
                rows.append(ind + "    its conjunction falls %+.2f d from the dip; a transit there lasts %.2f times as "
                            "long as the true orbit's at the same impact parameter, so to last as long as the dip %s"
                            % (off, factor, need))
        return rows

    out += ["", "[the radial-velocity search, step by step]"] + search_lines(diag["rv_search"])
    out += ["", "[one eccentric orbit or two planets near the 2:1 period ratio]"]
    out += pair_lines(diag["pair_test"]) if diag.get("pair_test") else ["no planet was fitted with e of 0.15 or more"]'''.split("\n")
lines[start:end] = new
src = "\n".join(lines)
anchor = '''        for c in s["candidates"]:
            out.append("    %s" % ", ".join("%s %s" % (k, v) for k, v in c.items()))
'''
assert src.count(anchor) == 1
src = src.replace(anchor, anchor + '''    out += ["", "[a single dip holds its planet's conjunction: the search again from there]"]
    if not diag.get("held_on_dip"):
        out.append("no single dip was held")
    for h in diag.get("held_on_dip", []):
        out.append("dip at %.4f held as the conjunction of the planet at %.4f d: lnL %.2f, against %.2f fitted to the "
                   "velocities alone" % (h["dip"], h["planet_period"], h["lnL_held"], h["lnL_free"]))
        out += search_lines(h["rv_search"], "    ")
        out += pair_lines(h["pair_test"], "    ") if h["pair_test"] else ["    no planet was fitted with e of 0.15 or more"]
''')
p.write_text(src, encoding="utf-8", newline="\n")
print("edited; lines", len(src.split("\n")))
