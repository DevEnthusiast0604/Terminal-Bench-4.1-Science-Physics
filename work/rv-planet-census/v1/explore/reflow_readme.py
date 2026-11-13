"""Reflow the README draft's prose to 120 columns: paragraphs, '- ' bullets and 'N. ' items. Leaves the metadata
block, headings, tables and comments as they are."""
import re
import sys
import textwrap
from pathlib import Path

p = Path(sys.argv[1])
lines = p.read_text(encoding="utf-8").split("\n")
out, block, section = [], [], ""


def flush():
    global block
    if not block:
        return
    first = block[0]
    m = re.match(r"^(- |\d+\. )", first)
    lead = m.group(1) if m else ""
    text = " ".join(x.strip() for x in block)
    if lead:
        text = text[len(lead):]
    ind = " " * len(lead)
    out.extend(textwrap.wrap(text, width=120, initial_indent=lead, subsequent_indent=ind,
                             break_long_words=False, break_on_hyphens=False))
    block = []


for ln in lines:
    if ln.startswith("## "):
        flush()
        section = ln
        out.append(ln)
        continue
    raw = (section == "## Task Metadata" or ln.startswith("#") or ln.startswith("|") or ln.startswith("<!--")
           or not ln.strip())
    if raw:
        flush()
        out.append(ln)
        continue
    if re.match(r"^(- |\d+\. )", ln):
        flush()
    block.append(ln)
flush()
p.write_bytes("\n".join(out).encode("utf-8"))
print("reflowed", len(out), "lines; longest", max(len(x) for x in out if not x.startswith("- **Tags")))
