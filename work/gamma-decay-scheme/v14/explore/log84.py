"""2026-11-14: the platform has been unreachable since 10:42 UTC (502, then Cloudflare Tunnel error); the combined
poller's window ended with no new card; poller restarted. Adds only. Run from the folder root."""
import datetime
import re

NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M")


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    assert "\r" not in text
    open(path, "w", encoding="utf-8", newline="").write(text)


def insert_at_section_end(text, header, entry):
    i = text.index(header)
    m = re.compile(r"^## ", re.M).search(text, i + len(header))
    j = m.start() if m else len(text)
    while j > 0 and text[j - 1] == "\n":
        j -= 1
    return text[:j] + "\n" + entry.rstrip("\n") + text[j:]


entry = ("- **%s**: the platform has been unreachable since 10:42 UTC: the combined poller (`b6a0li6cv`, started "
         "09:08) printed \"platform down (gateway error)\" at 10:42 (\"502: Bad gateway\") and never \"platform answering "
         "again\"; it reached its 12 h limit at 21:07:42 with the page title \"Cloudflare Tunnel error | "
         "queue.supertasker.ai | Cloudflare\" (exit 1, no new card). A status call for T-1383 at 21:08 gave the same "
         "tunnel error (Cloudflare answers, the platform's origin behind it does not: platform side). Last good status, "
         "09:08: T-1383 waiting for a reviewer (v15 full review), T-1563 waiting for a reviewer, T-1519 pass@8 TOO EASY "
         "with the reviewer deciding; 0 unseen on each. Combined poller restarted (T-1383,T-1563,T-1519 at 600 s); it "
         "keeps polling through gateway errors and prints when the platform answers again.\n" % NOW)
for slug in ("gamma-decay-scheme", "dhva-fermi-surface", "rv-planet-census"):
    s = read("logs/%s.md" % slug)
    write("logs/%s.md" % slug, insert_at_section_end(s, "## State now", entry))
print("logged at", NOW)
