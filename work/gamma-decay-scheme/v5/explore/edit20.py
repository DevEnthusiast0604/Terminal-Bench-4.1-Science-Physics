"""v5 (user, 2026-11-10: "Add it, upload again"): TB 4.1's check-task-fields.sh wants the README's Author line as
`Name (email)`, exactly as task.toml declares it. Builds the line from task.toml (no address typed by hand) and lets
tools/scan_task.py allow the author's own address on that one README line. Run from the folder root."""
import tomllib
from pathlib import Path

T = Path("tasks/active/gamma-decay-scheme")
md = tomllib.loads((T / "task.toml").read_text(encoding="utf-8"))["metadata"]
assert isinstance(md["author_name"], str) and isinstance(md["author_email"], str)
assert "author_organization" not in md

p = T / "README.md"
s = p.read_text(encoding="utf-8")
old = "- **Author:** %s\n" % md["author_name"]
new = "- **Author:** %s (%s)\n" % (md["author_name"], md["author_email"])
assert s.count(old) == 1, s.count(old)
p.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
print("edited", p)

p = Path("tools/scan_task.py")
s = p.read_text(encoding="utf-8")
pairs = [
    ("this machine's folder names, or an email address outside task.toml whose domain is not a reserved one\n"
     "(example.com/.org/.net, *.test, *.example, *.invalid), plus any symlink (tb4 package drops them) and any\n"
     "__pycache__ or .pytest_cache folder. Exit status 1 when anything is found.\n",
     "this machine's folder names, or an email address outside task.toml whose domain is not a reserved one\n"
     "(example.com/.org/.net, *.test, *.example, *.invalid), plus any symlink (tb4 package drops them) and any\n"
     "__pycache__ or .pytest_cache folder. Exit status 1 when anything is found. One exception: task.toml's own\n"
     "author_email on the README's `- **Author:**` line, which TB 4.1 requires as `Name (email)` (user, 2026-11-10).\n"),
    ("import pathlib\nimport re\nimport sys\n",
     "import pathlib\nimport re\nimport sys\nimport tomllib\n"),
    ("def scan(root):\n    problems, n_files = [], 0\n",
     "def author_emails(root):\n"
     "    \"\"\"task.toml's author_email values, the only addresses the README's Author line may hold.\"\"\"\n"
     "    try:\n"
     "        md = tomllib.loads((root / \"task.toml\").read_text(encoding=\"utf-8\")).get(\"metadata\", {})\n"
     "    except (OSError, tomllib.TOMLDecodeError):\n"
     "        return set()\n"
     "    v = md.get(\"author_email\", [])\n"
     "    return {e.encode() for e in ([v] if isinstance(v, str) else v)}\n"
     "\n"
     "\n"
     "def on_author_line(data, pos):\n"
     "    return data[data.rfind(b\"\\n\", 0, pos) + 1:].startswith(b\"- **Author:** \")\n"
     "\n"
     "\n"
     "def scan(root):\n    problems, n_files = [], 0\n    allowed = author_emails(root)\n"),
    ("            for m in EMAIL.finditer(data):\n"
     "                if not RESERVED.search(m.group(1).lower()):\n"
     "                    problems.append((\"email %s\" % m.group(0).decode(errors=\"replace\"), rel))\n",
     "            for m in EMAIL.finditer(data):\n"
     "                if RESERVED.search(m.group(1).lower()):\n"
     "                    continue\n"
     "                if rel == \"README.md\" and m.group(0) in allowed and on_author_line(data, m.start()):\n"
     "                    continue\n"
     "                problems.append((\"email %s\" % m.group(0).decode(errors=\"replace\"), rel))\n"),
]
for old, new in pairs:
    assert s.count(old) == 1, (s.count(old), old[:60])
    s = s.replace(old, new)
p.write_text(s, encoding="utf-8", newline="\n")
print("edited", p)
