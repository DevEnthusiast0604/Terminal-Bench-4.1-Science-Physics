"""Append the standard entries for an upload (tools/release.sh calls it; run from the folder root):

    python -X utf8 -I -B tools/log_release.py SLUG T-ID N ZIP DIGEST ARCHIVED "CHANGE" "LINT" "SCAN" [--dry-run]

Adds, never edits (user rule, 2026-10-29): a dated line at the end of "State now" and an entry at the end of
"Version history" in logs/SLUG.md, a new row on logs/STATUS.md, and an entry in work/physics-task-state.md when
that file tracks SLUG. --dry-run prints the entries and writes nothing. Short entries (user, 2026-11-03).
"""
import datetime as dt
import glob
import hashlib
import re
import sys
import zipfile


def insert_at_section_end(text, header):
    """Insert point: just before the next '## ' header after HEADER, ahead of the blank lines that precede it."""
    i = text.index(header)
    m = re.compile(r"^## ", re.M).search(text, i + len(header))
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return j


def insert_at_slug_end(text, slug):
    """Insert point in work/physics-task-state.md: the end of SLUG's '# ' section, just before the next '# ' heading
    and ahead of the blank lines that precede it. The file's end is the end of the newest task's section only, so an
    entry for an older task appended there landed under the wrong task (gamma's v8 under rv-planet-census, 11-10)."""
    i = text.index("| Slug | `%s` |" % slug)
    m = re.compile(r"^# ", re.M).search(text, i)
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return j


def main():
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    dry = len(args) != len(sys.argv) - 1
    slug, tid, n, zpath, digest, archived, change, lint, scan = args
    now = dt.datetime.now(dt.timezone.utc)
    day, hm = now.strftime("%Y-%m-%d"), now.strftime("%H:%M")
    data = open(zpath, "rb").read()
    zsha = hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(zpath) as z:
        nfiles = sum(1 for i in z.infolist() if not i.is_dir())
    pat = re.compile(r"^- \*\*v\d+, uploaded %s " % day, re.M)
    k = 1 + sum(len(pat.findall(open(p, encoding="utf-8").read())) for p in glob.glob("logs/*.md"))
    short = digest.replace("sha256:", "")
    short = "%s…%s" % (short[:8], short[-4:])
    zname = zpath.replace("\\", "/").split("/")[-1]

    state = ("- **%s**: v%s uploaded with Upload the fix, no note (upload %d of 5 on %s); quick check queued. %s See "
             "Version history (v%s).\n" % (hm, n, k, day[5:], change, n))
    version = ("- **v%s, uploaded %s %s** (Upload the fix on %s). %s\n"
               "  - Zip `deliveries/%s`: %d bytes, %d files; task digest `%s`; zip sha256 `%s…%s`.\n"
               "  - %s\n"
               "  - lint: %s; scan: %s.\n" % (
                   n, day, hm, tid, change, zname, len(data), nfiles, digest, zsha[:8], zsha[-4:],
                   ("Previous zip archived as `%s`." % archived) if archived else "No previous zip in deliveries/.",
                   lint, scan))
    board = open("logs/STATUS.md", encoding="utf-8", newline="").read()
    rows = [r for r in board.splitlines() if r.startswith("| %s |" % slug)]
    das = rows[-1].split("|")[4].strip() if rows else "?"
    row = ("| %s | `tasks/active/%s/` | %s | %s | v%s (`%s`, digest `%s`) | IN REVIEW: v%s uploaded with Upload the "
           "fix, no note (upload %d of 5 on %s); quick check queued. %s | %s %s | Watch the quick check, then pass@3 "
           "(poller); log each card (Seen = no), review it, mark it seen | [log](%s.md) |\n" % (
               slug, slug, tid, das, n, zname, short, n, k, day[5:], change, day, hm, slug))
    phys = open("work/physics-task-state.md", encoding="utf-8", newline="").read()
    tracks = ("| Slug | `%s` |" % slug) in phys
    pentry = "- **%s %s**: v%s uploaded (upload %d of 5 today), digest `%s`. %s\n" % (day, hm, n, k, short, change)

    if dry:
        print(state, version, row, pentry if tracks else "(physics state not tracking %s)\n" % slug, sep="\n")
        return
    log_path = "logs/%s.md" % slug
    s = open(log_path, encoding="utf-8", newline="").read()
    j = insert_at_section_end(s, "## State now")
    s = s[:j] + "\n" + state.rstrip("\n") + s[j:]
    j = insert_at_section_end(s, "## Version history")
    s = s[:j] + "\n" + version.rstrip("\n") + s[j:]
    open(log_path, "w", encoding="utf-8", newline="").write(s)
    i = board.index("\nArchived:\n")
    board = board[:i].rstrip("\n") + "\n" + row + board[i + 1:]
    open("logs/STATUS.md", "w", encoding="utf-8", newline="").write(board)
    if tracks:
        j = insert_at_slug_end(phys, slug)
        phys = phys[:j] + "\n" + pentry.rstrip("\n") + phys[j:]
        open("work/physics-task-state.md", "w", encoding="utf-8", newline="").write(phys.rstrip("\n") + "\n")
    print("logged v%s: %s, logs/STATUS.md%s" % (n, log_path, ", work/physics-task-state.md" if tracks else ""))


if __name__ == "__main__":
    main()
