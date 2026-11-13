"""Extract an untrusted zip into a fresh directory: refuses absolute paths, '..' parts, links and
anything that would land outside the target. Usage: python -I -B safe_extract.py ZIP DEST"""
import os
import stat
import sys
import zipfile

src, dest = sys.argv[1], sys.argv[2]
if os.path.exists(dest) and os.listdir(dest):
    sys.exit("destination is not empty: " + dest)
os.makedirs(dest, exist_ok=True)
root = os.path.realpath(dest)
total = 0
with zipfile.ZipFile(src) as z:
    for info in z.infolist():
        name = info.filename.replace("\\", "/")
        parts = [p for p in name.split("/") if p]
        mode = info.external_attr >> 16
        if name.startswith("/") or ":" in name or ".." in parts or stat.S_ISLNK(mode):
            sys.exit("unsafe entry: " + info.filename)
        target = os.path.realpath(os.path.join(root, *parts)) if parts else root
        if target != root and not target.startswith(root + os.sep):
            sys.exit("entry escapes the destination: " + info.filename)
        if info.is_dir():
            os.makedirs(target, exist_ok=True)
            continue
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with z.open(info) as fin, open(target, "wb") as fout:
            while True:
                chunk = fin.read(1 << 20)
                if not chunk:
                    break
                fout.write(chunk)
                total += len(chunk)
        print(info.file_size, name)
print("extracted bytes", total)
