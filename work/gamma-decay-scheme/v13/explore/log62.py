"""2026-11-12: v13 lessons from the build (search order, a second scheme with as few levels, the weak member's shares).
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


pitfall = """- (%s) v13 build. (1) The reference's search lets a line land only on a level that a line placed before it made.
  With 511.0 keV at I 4.22 just above 941.3 keV at 4.21, 511.0 came first, before any line had made 2581.6 keV, and no
  scheme fitted at any level count ("no scheme agrees with the data"). The fix, in `main()`: clean lines first, then lines
  on peaks shared with something else (share < 0.9 or the annihilation line), then the delayed feeders. (2) The search
  then found two schemes at 17 levels: the second puts 551.8 keV from 2041.4 to 1489.6 keV, beside 647.8 keV, because
  the 551.8 keV gate's centroid on the 647 keV doublet (647.40) sat within 2 sigma of the edge of the "both" band and
  the flag stayed undecided. The coincidence strength excludes it (1.948 +- 0.017 measured, 0.847 predicted by it,
  1.847 by the scheme kept). checks.txt `[placement search]` now prints every other scheme with as few levels and the
  pairs that tell it apart; the README must not claim a single minimal scheme unless that list is empty. (3) The
  weak member's I: 1.78 with a tailed line shape, 1.57 from the 318.4/524.3 gate proportions, 2.12 with Gaussians that
  leave out the tail (outside 25%%, for 1.61). The whole 1082 keV peak read as E->B is 14.27 for 12.99, inside 25%%,
  so only the missing transition fails an answer that overlooks it.
""" % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Pitfalls", pitfall)
write("logs/gamma-decay-scheme.md", s)

b = read("logs/BRIEFING.md")
point = ("- (%s) gamma-decay-scheme v13: when a scheme change moves the noise, re-read every evidence section before "
         "keeping a README claim. Here the search order failed one line (fixed by placing lines on shared peaks after "
         "clean ones), a second minimal scheme appeared, and most README figures moved. `[placement search]` now lists "
         "any other scheme with as few levels and the coincidence that excludes it.\n" % NOW[11:])
if not b.endswith("\n"):
    b += "\n"
write("logs/BRIEFING.md", b + point)
print("logged at", NOW)
