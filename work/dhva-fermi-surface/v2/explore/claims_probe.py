import sys, re
from pathlib import Path
kit = Path.home() / "tb4" / "tb4-starter-pack" / "lint"
sys.path.insert(0, str(kit))
import gates_static as G
text = G.strip_fences(G.read(Path("tasks/active/dhva-fermi-surface/README.md")))
for start, block in G.paragraphs(text):
    if start not in (128,):
        continue
    sents = [s for _, s in G.split_sentences(block.replace("\n", " "))]
    for s in sents:
        h = G.claim_hits(s)
        if h:
            print("HITS", h, "::", s)
            print("  outcome:", re.search(r"\b(pass\w*|fail\w*|solv\w*|scor\w*|attempt\w*|trials?|worst|measured|accuracy|success|oracle|gets?|got|achiev\w*)\b", G.TOLERANCE_PCT.sub(" ", s), re.I))
