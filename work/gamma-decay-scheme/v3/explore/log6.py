"""2026-11-09 02:02: v3 submitted to the TB4.1 Queue as the new task T-0020 (DAS 4011092). Adds only.
The Version history line keeps log_release.py's form ("- **vN, uploaded DAY HH:MM**") so the day's upload count sees it."""
import re


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


state = ("- **2026-11-09 02:02**: v3 submitted to the TB4.1 Queue as a new task through `#submit` with DAS 4011092: "
         "**T-0020** (its v1), IN REVIEW, quick check running from 02:02. No note. Upload 1 of 5 on 11-09; 1 of 2 new "
         "tasks left today. Poller started (`poll_pipeline.py T-0020 43200 180`). See Version history (v3).\n")
version = (
    "- **v3, uploaded 2026-11-09 02:02** (new task on the TB4.1 Queue: T-0020, DAS 4011092; the platform's v1). The "
    "task on the TB 4.1 template (kit 3.7.0): Python dependencies from committed uv locks (`environment/locks/`, and "
    "`tests/locks/judge/` from the template), the template's new `tests/test.sh` and `tests/Dockerfile`, README "
    "metadata in the 4.1 form (Category alone, Tags as `<code>`) and one README sentence on the locks. Data, answers, "
    "instruction and grader unchanged from v2.\n"
    "  - Zip `deliveries/gamma-decay-scheme-20261109.zip`: 2013353 bytes, 32 files; task digest "
    "`sha256:9b420950a1ad28a183dbf27b304b359ad81279c6464c9f3376f6f93a8dd9ad6d`; zip sha256 `c6c77406…e52e`.\n"
    "  - Previous zip archived as `deliveries/archive/gamma-decay-scheme/gamma-decay-scheme-v2-20261106.zip`.\n"
    "  - lint (kit 3.7.0): PASS, every structure check passes (73 rows, 0 FAIL, 1 WARN: the README Author line has no "
    "email, by the user's rule); scan: problems: 0.\n"
    "  - Edit script `work/gamma-decay-scheme/v3/explore/edit12.py`; the lock was made with uv 0.10.8 "
    "(`uv lock --directory environment/locks`): asciinema 2.4.0, numpy 2.3.3, scipy 1.18.1, with cp312 manylinux "
    "x86_64 wheels.\n")
pitfalls = (
    "- (2026-11-09) Local version numbers go on (v3, v4, ...), while TB4.1's T-0020 counts its own versions from v1: "
    "platform version = local version - 2. `supertasker.py links T-0020 v1` lists v3's jobs, and the next fix is "
    "`release.sh gamma-decay-scheme T-0020 4 ...` (archives v3, uploads the platform's v2).\n"
    "- (2026-11-09) TB 4.1 wants the README Author line as `Name (email)`, matching task.toml, and the user's rule keeps "
    "the email in task.toml only. v3 ships without it (lint WARN) and the question is with the user.\n")

s = read("logs/gamma-decay-scheme.md")
s = insert_at_section_end(s, "## State now", state)
s = insert_at_section_end(s, "## Version history", version)
s = insert_at_section_end(s, "## Pitfalls", pitfalls)
write("logs/gamma-decay-scheme.md", s)

row = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-0020 | 4011092 | v3 "
       "(`gamma-decay-scheme-20261109.zip`, digest `9b420950…ad6d`) | IN REVIEW: v3 submitted to the TB4.1 Queue as the "
       "new task T-0020 (its v1), no note (upload 1 of 5 on 11-09); quick check running from 02:02. TB 4.1 template "
       "(uv locks, new test.sh, README metadata); data, answers and grader unchanged | 2026-11-09 02:02 | Watch the "
       "quick check, then pass@3 (poller on T-0020); log each card (Seen = no), review it, mark it seen | "
       "[log](gamma-decay-scheme.md) |")
s = read("logs/STATUS.md")
sep = "\nArchived:\n"
assert s.count(sep) == 1
write("logs/STATUS.md", s.replace(sep, "\n" + row + sep))

event = ("- **2026-11-09 02:02**: v3 submitted to the TB4.1 Queue as **T-0020** (DAS 4011092; the platform's v1), "
         "upload 1 of 5 today, digest `9b420950…ad6d`. TB 4.1 template (uv locks, new test.sh, README metadata); data, "
         "answers and grader unchanged. Quick check running.\n")
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)

points = """- (02:02) gamma-decay-scheme is now **T-0020** on the TB4.1 Queue: submitted 02:02 with DAS 4011092 (upload 1 of 5 on
  11-09; 1 of 2 new tasks left today), and its quick check started at once. Local v3 is the platform's v1. `/task/T-0020`
  works with `supertasker.py status`, and the poller watches T-0020.
- (02:02) On TB4.1 the top tabs are buttons, and a goto to `#submit` keeps the last tab shown. `supertasker.py submit`
  now clicks Submit first, checks that the check kind (`#kind`) is "Quick check (35 + 5)", and stops if a contributor
  e-mail field (`#contrib`, hidden so far) shows. `tools/release.sh` exempts `uv.lock` from its canary check.
- (02:02) README Author line: TB 4.1 wants `Name (email)` to match task.toml, while the user's rule keeps the email in
  task.toml only. v3 ships without it (a lint WARN) and the user has been asked. If the quick check flags it, wait for
  their answer.
"""
s = read("logs/BRIEFING.md")
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + points)
print("done")
