"""2026-11-11: v9's quick check (job 21129) reviewed and marked seen; pass@3 running. Adds only."""
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


row = ("| 2026-11-11 06:09 | the same card, reviewed | Marked seen 06:11. Job 21129 (reviewer astra, gpt-6.1-sol): 35 "
       "criteria 31 pass, 0 fail, 3 N/A (`verifier_execution_isolation`, `do_not_modify_enforced`, `artifact_efficiency`), "
       "`novel` NOT_PROVIDED (deferred to the full review); 5 extra all pass (3 draws, 06:08:58Z). Controls as in v8 "
       "(oracle, nop, verifier-repeat, tamper, wrong-answers; every recorded reward 0 or 1). Reports in "
       "`work/gamma-decay-scheme/v9/criteria-35.md` and `criteria-extra.md`. Poller restarted for pass@3. | yes |\n")
s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## Platform updates", row)
state = ("- **%s**: v9's quick check passed (job 21129, 06:09; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra "
         "pass). pass@3 running on Sol 6.1 from 06:09. Card marked seen 06:11; poller restarted.\n") % NOW
s = insert_at_section_end(s, "## State now", state)
write("logs/gamma-decay-scheme.md", s)

def insert_at_slug_end(text, slug, entry):
    i = text.index("| Slug | `%s` |" % slug)
    m = re.compile(r"^# ", re.M).search(text, i)
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


event = ("- **%s**: v9 (511 keV line at I 2.99 among doubled pair-production annihilation; robust doublet members in the "
         "reference) passed its quick check (job 21129); pass@3 running from 06:09.\n"
         "- **%s**: (note) this task's 2026-11-10 23:52 entry (v8 quick check passed) and 2026-11-11 00:09 entry (v8 "
         "pass@3 3/3, the v9 plan) were written at the file's end, under `# dhva-fermi-surface`. The gamma log scripts "
         "now write into this section, as `tools/log_release.py` does.\n") % (NOW, NOW)
other = ("- **%s**: (note from the gamma-decay-scheme session) the 2026-11-10 23:52 and 2026-11-11 00:09 entries just "
         "above are gamma-decay-scheme's (T-1383 v8 quick check passed; v8 pass@3 3/3 and the v9 plan), appended at the "
         "file's end by mistake.\n") % NOW
s = read("work/physics-task-state.md")
s = insert_at_slug_end(s, "gamma-decay-scheme", event)
s = insert_at_slug_end(s, "dhva-fermi-surface", other)
write("work/physics-task-state.md", s)

path = "logs/STATUS.md"
lines = read(path).split("\n")
last = max(i for i, ln in enumerate(lines) if ln.startswith("| gamma-decay-scheme |"))
board = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 | 4011092 | v9 "
         "(`gamma-decay-scheme-20261111.zip`, digest `f9413828…b47a`) | PASS@3: v9's quick check passed (job 21129, "
         "06:09; 31 pass, 0 fail, 3 N/A, `novel` deferred; 5 extra pass); pass@3 running on Sol 6.1 | %s | Wait for "
         "pass@3 (poller); 1 or 2 of 3: P3 ID to the user for DAS 4011092; 3 of 3: harden; 0 of 3: check fairness | "
         "[log](gamma-decay-scheme.md) |" % NOW)
lines.insert(last + 1, board)
write(path, "\n".join(lines))
print("done", NOW)
