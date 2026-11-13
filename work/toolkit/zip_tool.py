"""List or safely extract a downloaded zip (the platform's toolkit). Run with python -X utf8 -I -B from the folder root.

    python -X utf8 -I -B work/toolkit/zip_tool.py list ZIP
    python -X utf8 -I -B work/toolkit/zip_tool.py extract ZIP NEW_EMPTY_DIR

Refuses absolute paths, drive letters, '..' parts and symlink entries, so nothing lands outside the target directory.
"""
import os
import stat
import sys
import zipfile


def unsafe(info):
    name = info.filename.replace("\\", "/")
    parts = name.split("/")
    mode = (info.external_attr >> 16) & 0xFFFF
    return (name.startswith("/") or (len(name) > 1 and name[1] == ":") or ".." in parts
            or stat.S_ISLNK(mode))


def main():
    cmd, path = sys.argv[1], sys.argv[2]
    z = zipfile.ZipFile(path)
    infos = z.infolist()
    bad = [i.filename for i in infos if unsafe(i)]
    print("entries %d, unsafe %s" % (len(infos), bad))
    if cmd == "list":
        for i in infos:
            print("%9d  %s" % (i.file_size, i.filename))
        return
    if bad:
        sys.exit("refusing to extract")
    out = sys.argv[3]
    if os.path.exists(out) and os.listdir(out):
        sys.exit("target directory is not empty")
    os.makedirs(out, exist_ok=True)
    z.extractall(out)
    print("extracted to", out)


if __name__ == "__main__":
    main()
