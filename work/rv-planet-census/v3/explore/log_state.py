"""Append one event to the rv-planet-census section of work/physics-task-state.md (at the section's end).

Usage (folder root): python -X utf8 -I -B work/rv-planet-census/v3/explore/log_state.py ENTRY.txt
ENTRY.txt holds the entry's lines, starting with "- **YYYY-MM-DD HH:MM**: "."""
import sys
from pathlib import Path

sys.path.insert(0, "tools")
from log_release import insert_at_slug_end  # noqa: E402

path = Path("work/physics-task-state.md")
text = path.read_text(encoding="utf-8")
entry = Path(sys.argv[1]).read_text(encoding="utf-8").replace("\r\n", "\n").strip("\n")
j = insert_at_slug_end(text, "rv-planet-census")
path.write_text(text[:j] + "\n" + entry + text[j:], encoding="utf-8", newline="\n")
print("inserted at", j)
