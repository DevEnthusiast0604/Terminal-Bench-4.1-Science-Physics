"""Files of the task folder that differ from the v3 zip. Run from the folder root."""
import hashlib
import zipfile
from pathlib import Path

z = zipfile.ZipFile("deliveries/gamma-decay-scheme-20261109.zip")
root = Path("tasks/active/gamma-decay-scheme")
old = {n.split("/", 1)[1]: hashlib.sha256(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/") and "/" in n}
new = {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
print("changed:", sorted(k for k in new if k in old and old[k] != new[k]))
print("added:", sorted(k for k in new if k not in old))
print("removed:", sorted(k for k in old if k not in new))
