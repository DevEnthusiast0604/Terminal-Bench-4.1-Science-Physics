"""2026-11-11: v9's build notes beyond the release row: the tie the first v9 data opened in the reference's search and
its fix; the briefing point that follows. Adds only."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")
HM = NOW[11:]


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    open(path, "w", encoding="utf-8", newline="").write(text)


def insert_at_section_end(text, header, entry):
    i = text.index(header)
    m = re.compile(r"^## ", re.M).search(text, i + len(header))
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


state = ("- **%s**: v9 build notes. The first v9 generator run (00:10, after telling the user) gave `[placement search]` "
         "3 schemes with 16 levels (6 with 17): extra levels at 2041.2 and 2500.8 keV, i.e. 1011.4 keV moved to a "
         "beta-fed level above 1489.6 keV and the 551.8/647.8 order swapped. Cause: the reference's doublet logic, not "
         "the physics. The 898.3 keV gate (fed through the isomer) read the 647 keV doublet at 646.69 keV, and the old "
         "rule (lower member = gates within 0.15 keV of the lowest centroid) took that gate alone, so the 551.8 and "
         "1011.4 keV gates (647.37, 647.39: both members) fell undecided. Fix in `solution/solve.py` `split_doublets` "
         "(`work/gamma-decay-scheme/v9/explore/edit40.py`): a member's energy is the mean of the gates that agree within "
         "two standard errors with the lowest (highest) centroid that holds to two standard errors. Rerun 00:20 (data "
         "and `expected.json` byte-identical): 1 scheme with 16 levels, 2 with 17 (extra 2917.6 keV), as in v8; "
         "reference intensities within 8.4 percent (was 12.0). `edit41.py` makes `checks.txt` name the coincidence "
         "route's furthest pair (318.4 with 1606.6 keV at 1.337, the 524.3+1082.3 sum in the 1606.6 keV peak; the only "
         "pair past 0.25); rerun 00:23, data identical. README figures from these checks (`edit42.py`). Upload 2 of 5 "
         "on 11-11 is right: dhva-fermi-surface's first upload (00:01) counts too.\n") % NOW
pitfall = ("- (2026-11-11) A fixed window around the most extreme gate centroid let one stray gate set a doublet member, "
           "which made the search's coincidence flags undecided and opened a tie at the fewest levels (v9's first data). "
           "After every generator run read `[placement search]`: the count at the fewest levels must be 1.\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## State now", state)
s = insert_at_section_end(s, "## Pitfalls", pitfall)
write("logs/gamma-decay-scheme.md", s)

point = ("- (%s) After any generator run, read `[placement search]` in `tests/checks.txt` before the README: the count "
         "at the fewest levels must be 1, or the instruction's fewest-levels rule leaves a tie (the reviewer's point on "
         "v7). In gamma-decay-scheme v9 a noise change alone opened one, through the reference's doublet logic; the fix "
         "went into `solve.py`, not the seed.\n") % HM
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)
print("done", NOW)
