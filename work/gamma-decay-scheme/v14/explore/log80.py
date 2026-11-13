"""2026-11-13 21:11: T-1383 full review (v15) finished, IN REVIEW / DECIDING with 1 item for a person to settle
(Contract generality FAIL-PENDING-DISPOSITION). Logs the card unseen. Adds only. Run from the folder root."""
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


s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates",
                          "| 2026-11-13 21:11 | in review (T-1383 v15 full review finished, deciding) | \"IN REVIEW, "
                          "DECIDING / the full review has finished and the review team is deciding. Submit the task in "
                          "DAS now if you haven't yet, but don't upload a new version: you get an update with the "
                          "decision. / The review left 1 item(s) that a person has to settle. A reviewer settles them and "
                          "decides what comes next ... Nothing to upload for now. ... TO CHECK Contract generality / "
                          "Contract-generality FAIL-PENDING-DISPOSITION: 1 generator assumption(s) traced (0 dropped): 0 "
                          "settled by a quoted rule, 1 not / P3 ID P3-B911-F9F1-EDFA / this revision only\". Status: "
                          "Waiting for a reviewer; 15 versions; last change 21:10; newest row v15 19:16 \"Full review / "
                          "under evaluation by the review team\" with View report. Poller exit 0 at 21:14 (one status "
                          "call timed out at 21:00 after 170 s, the next one worked). | no |\n")
s = insert_at_section_end(s, "## State now",
                          "- **%s**: the v15 full review finished (card 21:11): IN REVIEW, DECIDING, one item for a person "
                          "to settle, Contract generality FAIL-PENDING-DISPOSITION (1 generator assumption traced, not "
                          "settled by a quoted rule). Nothing to upload; a reviewer decides. The P3 ID on the card is the "
                          "same P3-B911-F9F1-EDFA (DAS 4011092, with the user). Next: read the report's contract-generality "
                          "item, mark the card seen, watch for the decision.\n" % NOW)
write("logs/gamma-decay-scheme.md", s)
print("logged at", NOW)
