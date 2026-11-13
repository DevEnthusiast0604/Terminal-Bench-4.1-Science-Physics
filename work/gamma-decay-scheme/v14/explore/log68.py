"""2026-11-13: v14 build lessons (the hidden member's share, the doublet flags, the generator's failure message).
Adds only: a Pitfalls entry in logs/gamma-decay-scheme.md and a point in logs/BRIEFING.md."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    assert "\r" not in text
    open(path, "w", encoding="utf-8", newline="").write(text)


def insert_at_section_end(text, header, entry):
    i = text.index(header)
    m = re.compile(r"^## ", re.M).search(text, i + len(header))
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


pitfall = """- (%s) v14 build. (1) With the hidden line at I 2.44 the reference's first run put it at 3.15 (+29%%) and the
  generator stopped. A two-member fit's share follows where the peak's centroid sits between the two energies, so it
  moves with the energy scale (0.05 keV moves it by about 0.06): the tailed fit was +13%% in v13 and +29%% in v14, and
  Gaussians alone were +35%% in v13 and -2.5%% in v14. The 318.4/524.3 keV gate proportions gave 0.1102 (truth 0.1104)
  and 0.1757 (0.1613). `hidden_members` now keeps a member on the fit but takes its share from the gates. (2) The
  same run found three schemes with 17 levels: 551.8 or 1011.4 keV placed beside 647.8 keV instead of above it, because
  those gates' centroids on the 647 keV doublet sat near the edge of the "both" band. `coincidence_flags` now marks a
  partner weaker than both members of a doublet in one cascade as seen with both when it brings more than 1.15 of the
  doublet's gamma rays per gamma ray of its own (three standard errors over); measured 1.91 for both. One scheme at 17
  levels again. (3) The generator's final assert now names the quantity outside its band and the three largest
  intensity differences; before, it printed nothing.
""" % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Pitfalls", pitfall)
write("logs/gamma-decay-scheme.md", s)

b = read("logs/BRIEFING.md")
point = ("- (%s) gamma-decay-scheme v14: the share of a weak member under a strong line from a fit of the peak's shape "
         "is set by the energy scale more than by the shape (0.05 keV moves it by about 0.06); gate proportions are "
         "robust. Size such a trap against the gate method, and expect a shape fit to land anywhere within about 30%%.\n"
         % NOW[11:])
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)
print("logged at", NOW)
