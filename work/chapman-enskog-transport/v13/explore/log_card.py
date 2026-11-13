"""Appends rows to the task log's "Platform updates" table (before the next section). Not shipped.
    python -X utf8 -I -B log_card.py LOG ROW [ROW ...]"""
import sys

path, rows = sys.argv[1], sys.argv[2:]
lines = open(path, encoding="utf-8").read().split("\n")
start = lines.index("## Platform updates")
end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
last = max(i for i in range(start, end) if lines[i].startswith("|"))
lines[last + 1:last + 1] = rows
open(path, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
print("added", len(rows), "row(s) after line", last + 1)
