"""Print the README blocks that tb4 lint's readme-claims gate counts as measured claims, with the
claim sentences, the numbers a receipt must hold and the paths the block cites."""
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.expanduser("~/tb4/tb4-starter-pack/lint"))
import gates_static as G  # noqa: E402

task = Path(sys.argv[1])
text = G.strip_fences(G.read(task / "README.md"))
sec = G.sections(text)
for start, block in G.paragraphs(text):
    if G.CLAIM_SKIP_SECTION.search(sec.get(start, "")) or block.lstrip().startswith("#"):
        continue
    sents = [s for _, s in G.split_sentences(block.replace("\n", " "))]
    table = block.lstrip().startswith("|")
    hits = [(s, G.claim_hits(s, intro=s.rstrip().endswith(":") and i == len(sents) - 1, table=table))
            for i, s in enumerate(sents)]
    claim = [(s, h) for s, h in hits if h]
    if not claim:
        continue
    paths = [t for k, t in G.readme_tokens(block.replace("\n", " ")) if k == "path" and not t.startswith("/")]
    print("=== line %d" % start)
    for s, h in claim:
        print("  HIT %s: %s" % (h, s[:200]))
    print("  NUMS", sorted(G.claim_numbers([s for s, _ in claim])))
    print("  PATHS", paths)
