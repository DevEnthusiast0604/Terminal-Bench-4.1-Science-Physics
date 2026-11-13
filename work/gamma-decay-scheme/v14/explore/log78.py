"""2026-11-13: toolkit 3.8.7 installed; the user's rule to keep the toolkit current; tools/kit_update.py. Adds only.
Run from the folder root."""
import datetime

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    assert "\r" not in text
    open(path, "w", encoding="utf-8", newline="").write(text)


b = read("logs/BRIEFING.md")
point = ("- (%s) User: \"please download up-to-date toolkit always\". The platform offered kit 3.8.7 (installed: 3.8.2). "
         "Downloaded to `work/toolkit/20261113-387/` (kit.zip 1013939 bytes, extracted to `x/`) and installed at "
         "`~/tb4/tb4-starter-pack` (`tb4 --version`: 3.8.7); 3.8.2 kept as `~/tb4/tb4-starter-pack-3.8.2`. Only VERSION, "
         "`lint/gates_static.py` and `lint/grader_hygiene.py` changed, all relaxations (recorded check counts, an author's "
         "email inside EQUIVALENCE.json, `evidence/cheat/<name>` folders, test modules named in the instruction, more "
         "wordings of \"/app/output is collected\"); the template is identical. gamma-decay-scheme lints PASS under it "
         "(0 FAIL, 0 WARN). From now on `tools/kit_update.py` does this: it fetches `gate/kit/download`, compares VERSION "
         "and installs a newer kit the same way (exit 0 current or installed, 1 not reachable, 3 template changed). "
         "`tools/release.sh` runs it first; run it by hand at the start of a session and before packaging a new task.\n"
         % NOW[11:])
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)
print("logged at", NOW)
