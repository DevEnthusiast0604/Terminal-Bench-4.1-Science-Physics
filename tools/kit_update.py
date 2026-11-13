"""Keep the TB4 toolkit current (user, 2026-11-13: "please download up-to-date toolkit always").

    python -X utf8 -I -B tools/kit_update.py            (folder root; tools/release.sh runs it before its checks)

Downloads the platform's toolkit (gate/kit/download, through tools/supertasker.py and the logged-in debug Chrome)
and compares its VERSION with the installed kit's (~/tb4/tb4-starter-pack/VERSION). When the platform's is newer:
the zip goes to work/toolkit/<UTC date>-<version digits>/kit.zip, extracted to x/ beside it; the installed kit is
kept as ~/tb4/tb4-starter-pack-<its version>, and the new one takes its place. Otherwise nothing is kept.

Exit 0: the kit is current, or the newer one is installed and its template is unchanged.
Exit 1: the platform's kit could not be fetched or read (platform or Chrome down): nothing changed.
Exit 3: a newer kit is installed and its template/ differs from the old one. Tasks copy tests/test.sh,
        tests/Dockerfile and tests/locks/judge/ from the template unchanged, so refresh those before the next upload.
Nothing here runs anything from the kit."""
import datetime
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

KIT = Path.home() / "tb4" / "tb4-starter-pack"
TOP = "tb4-starter-pack"


def vtuple(v):
    return tuple(int(p) for p in v.strip().split("."))


def safe_extract(zf, dest):
    for n in zf.namelist():
        p = PurePosixPath(n)
        if p.is_absolute() or ".." in p.parts or ":" in n:
            sys.exit("FAIL: unsafe member in the kit zip: %r" % n)
    zf.extractall(dest)


def differing(a, b, rel=""):
    """Paths (relative) whose content differs or that exist on one side only, __pycache__ left out."""
    out = []
    cmp = filecmp.dircmp(a, b, ignore=["__pycache__"])
    out += [rel + n for n in cmp.left_only + cmp.right_only]
    out += [rel + n for n in cmp.common_files if not filecmp.cmp(os.path.join(a, n), os.path.join(b, n), shallow=False)]
    for d in cmp.common_dirs:
        out += differing(os.path.join(a, d), os.path.join(b, d), rel + d + "/")
    return out


def main():
    installed = (KIT / "VERSION").read_text(encoding="utf-8").strip() if (KIT / "VERSION").exists() else "0"
    tmp = Path(tempfile.mkdtemp(prefix="tb4kit-"))
    try:
        zpath = tmp / "kit.zip"
        r = subprocess.run([sys.executable, "-X", "utf8", "-I", "-B", "tools/supertasker.py", "fetch", "gate/kit/download",
                            str(zpath)], capture_output=True, text=True, encoding="utf-8", timeout=400)
        if r.returncode != 0 or not zpath.exists():
            tail = (r.stdout + r.stderr).strip().splitlines()[-1:] or ["no output"]
            print("kit: WARNING: could not fetch the platform's toolkit (%s); installed kit %s" % (tail[0], installed))
            return 1
        try:
            with zipfile.ZipFile(zpath) as zf:
                offered = zf.read(TOP + "/VERSION").decode("utf-8").strip()
        except (zipfile.BadZipFile, KeyError) as e:
            print("kit: WARNING: the download is not a toolkit zip (%s); installed kit %s" % (e, installed))
            return 1
        if vtuple(offered) <= vtuple(installed):
            print("kit: %s installed, %s offered: current" % (installed, offered))
            return 0
        day = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d")
        dest = Path("work/toolkit") / ("%s-%s" % (day, offered.replace(".", "")))
        if dest.exists():
            sys.exit("FAIL: %s exists; install the kit by hand" % dest)
        old = KIT.parent / ("%s-%s" % (TOP, installed))
        if old.exists():
            sys.exit("FAIL: %s exists; install the kit by hand" % old)
        dest.mkdir(parents=True)
        shutil.copyfile(zpath, dest / "kit.zip")
        with zipfile.ZipFile(dest / "kit.zip") as zf:
            safe_extract(zf, dest / "x")
        os.rename(KIT, old)
        shutil.copytree(dest / "x" / TOP, KIT)
        changed = differing(str(old), str(KIT))
        print("kit: installed %s (was %s; kept as %s); download in %s" % (offered, installed, old, dest.as_posix()))
        print("kit: files that differ from %s: %s" % (installed, ", ".join(changed) or "none"))
        tmpl = [c for c in changed if c.startswith("template/")]
        if tmpl:
            print("kit: WARNING: the template changed (%s). Refresh each task's copies of tests/test.sh, tests/Dockerfile "
                  "and tests/locks/judge/ from it, then lint again." % ", ".join(tmpl))
            return 3
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
