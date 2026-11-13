"""2026-11-11: v11 design notes (State now, Pitfalls, physics-state, BRIEFING). Adds only."""
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


def insert_at_slug_end(text, slug, entry):
    i = text.index("| Slug | `%s` |" % slug)
    m = re.compile(r"^# ", re.M).search(text, i)
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


s = read("logs/gamma-decay-scheme.md")
state = ("- **%s**: v11 design notes in `work/gamma-decay-scheme/v11/design.md`. The weak 1081.40 keV line aims at what "
         "the pass@8 attempts skipped: a4 dropped gated peaks within 4 keV of a listed peak, tested only unplaced peaks "
         "against level differences and left the doublets out of its check for unexpected coincidences; a8 matched level "
         "differences within 0.7 keV (X - Da lies 0.82 keV from the 1082.22 keV peak). The 511 keV line went back to v8 "
         "(Sol 6.1 3 of 3 there) so that the new trap carries the difficulty for both models. Generator run once "
         "(the user was told first): reference within 9.1%%, one scheme at 17 levels. Poller running.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
pit = ("- (2026-11-11) In `split_doublets` a gate that sees both members of a doublet with a weak member reads at the "
       "strong member's energy (the 318.4 keV gate on the 1082 keV peak: 1082.20 keV), so the old rule flagged the weak "
       "member as absent there and the search could not place it. A weak member's flag is now undecided wherever the "
       "gate's centroid sits on the strong member.\n")
s = insert_at_section_end(s, "## Pitfalls", pit)
write("logs/gamma-decay-scheme.md", s)

event = ("- **%s**: v11 design: weak 1081.40 keV transition (I 1.22) from a new beta-fed level at 2721.70 keV to "
         "1640.30 keV, 0.9 keV under E->B (I 13.02), whose only clean gate is the 1322 keV doublet; 511 keV line back to "
         "v8. Notes in `work/gamma-decay-scheme/v11/design.md`.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", insert_at_slug_end(s, "gamma-decay-scheme", event))

point = ("- (%s) To harden against Astra 6, aim at what its audits skip, read from the pass@8 code rather than from its "
         "messages: in gamma-decay-scheme v10 one attempt dropped gated peaks within 4 keV of a listed peak, tested only "
         "unplaced peaks against level differences and left the doublets out of its check for unexpected coincidences. "
         "v11 hides a weak transition under a strong, already placed peak whose only clean gate is a doublet.\n" % NOW[11:])
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + point)
print("done", NOW)
