"""2026-11-10: v8 uploaded (release.sh, 18:16); the archive's numbering and the generator run. Adds only."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


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


state = ("- **%s**: v8 uploaded 18:16 with Upload the fix, no note (upload 3 of 5 on 11-10); task digest "
         "`sha256:c57359ae…a524`; quick check queued. Local and platform numbers agree again from v8: the archive "
         "`deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v7-20261110.zip` holds the v6 files, which are the "
         "platform's v7 (byte-identical, sha256 `178bc2e8…a5fb`); no separate v6 archive exists. The generator ran "
         "18:10-18:11 after telling the user (new data, expected.json, checks.txt; the reference inside every tolerance: "
         "levels 0.090 keV, energies 0.060 keV, |from - to - energy| 0.010 keV, intensities 7.1 percent, half-life 0.00 "
         "percent, isomer 0.6 percent; the 511 keV narrow part 63967 +- 1023 counts, I 4.31 against 4.41). Edit scripts: "
         "`work/gamma-decay-scheme/v8/explore/edit32.py` (instruction, requirements, grader, generator) and `edit33.py` "
         "(README). Poller restarted.\n") % NOW
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)
print("done", NOW)
