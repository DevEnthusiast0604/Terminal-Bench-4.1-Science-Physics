"""2026-11-12: v11's quick check passed (job 22164, 05:34); pass@3 running on Sol 6.1. Card logged, reviewed, seen.
Adds only."""
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


rows = ("| 2026-11-12 05:34 | the quick check passed (T-1383 v11) | \"All 40 criteria pass. pass@3 has started: three "
        "attempts by the target model on these exact files. You get another update when it ends. Do not change the task "
        "meanwhile: any edit needs a new check.\" Status: pass@3 running (\"pass@3 ran on Sol 6.1\"); version row v11: "
        "Quick check \"PASS, 36 of 40 pass\", pass@3 \"running, 0 of 3 ended\" 05:34. Poller exit 0. | no |\n"
        "| 2026-11-12 05:34 | the same card, reviewed | Marked seen 05:38 (`mark-seen` printed NOT CONFIRMED on the slow "
        "page; `updates` then listed the card as seen). Job 22164: 35 criteria 31 pass, 0 fail, 3 N/A, `novel` "
        "NOT_PROVIDED (deferred to the full review); 5 extra pass (`english_only`, `no_host_paths`, `harbor_format`, "
        "`discoverable`, `oracle_investigates`). Reports in `work/gamma-decay-scheme/v11/criteria-35.md` and "
        "`criteria-extra.md`. Poller restarted. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", rows)
state = ("- **%s**: v11's quick check passed (job 22164, 05:34; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra "
         "pass). pass@3 running on Sol 6.1 from 05:34. Card seen 05:38; poller restarted. 1 or 2 of 3: the new P3 ID "
         "to the user for DAS 4011092; 3 of 3: harden; 0 of 3: check whether every attempt missed the 1081.40 keV line "
         "and ease it (design.md).\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

event = ("- **%s**: v11 (weak 1081.40 keV transition under E->B; 511 keV line at v8's strength) passed its quick check "
         "(job 22164); pass@3 running from 05:34.\n") % NOW
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", insert_at_slug_end(s, "gamma-decay-scheme", event))

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v11 "
         "(`gamma-decay-scheme-20261111.zip`, digest `ebda2428…eaea`) | PASS@3: v11's quick check passed (job 22164, "
         "05:34; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass); pass@3 running on Sol 6.1 | %s | Wait for "
         "pass@3 (poller); 1 or 2 of 3: P3 ID to the user for DAS 4011092; 3 of 3: harden; 0 of 3: check fairness, "
         "then ease | [log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))
print("done", NOW)
