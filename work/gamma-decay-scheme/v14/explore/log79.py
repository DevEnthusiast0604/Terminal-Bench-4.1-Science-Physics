"""2026-11-13: the user's rule "only this chat session": one session watches every task and fixes failures one by one.
Adds only: a BRIEFING point, State now entries and board rows for dhva-fermi-surface and rv-planet-census, and a
State now entry for gamma-decay-scheme. Run from the folder root."""
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


b = read("logs/BRIEFING.md")
point = ("- (%s) User: \"From now on, I want to use only this chat session. just one session. You should watch the every "
         "tasks pipelines. When failed, work one-by-one and upload.\" This replaces the split of 2026-11-10 to 11-13 "
         "(one session per task, point of 14:36 and the State now entries that leave T-1563 and T-1519 to other "
         "sessions). One session now owns gamma-decay-scheme (T-1383, DAS 4011092), dhva-fermi-surface (T-1563, DAS "
         "4034278) and rv-planet-census (T-1519, DAS 4040198): one poller for all of them, `python -X utf8 -I -B "
         "tools/poll_pipeline.py T-1383,T-1563,T-1519 43200 600` (it polls each in turn and exits on the first unseen "
         "card). When a check fails, fix that task, release it, then go back to watching; one task at a time, in the "
         "order the failures came. The five uploads a UTC day are shared by all tasks. At 600 s with three tasks the "
         "tabs the user keeps open gain about 18 utility worlds an hour: when status calls slow past about a minute, "
         "ask the user to close and reopen those tabs.\n" % NOW[11:])
write("logs/BRIEFING.md", (b if b.endswith("\n") else b + "\n") + point)

takeover = {
    "dhva-fermi-surface": ("T-1563", "4034278",
                           "status 19:36: IN REVIEW, \"Waiting for a reviewer\", v4 full review \"under evaluation by the "
                           "review team\", last change 10:13, 0 unseen. The fix for the critical README finding is still "
                           "drafted in `work/dhva-fermi-surface/v5/task/`, to upload as v5 once the task is returned.",
                           "v4 = v3's files (`dhva-fermi-surface-20261112.zip`, digest `428e960d…5769`)",
                           "IN REVIEW: waiting for a reviewer (full review job 24020 finished 10:14); 0 unseen at 19:36",
                           "Watched by the single session (poller T-1383,T-1563,T-1519 at 600 s). If returned, upload the "
                           "drafted v5 (`work/dhva-fermi-surface/v5/task/`)"),
    "rv-planet-census": ("T-1519", "4040198",
                         "status 19:36: IN REVIEW, \"pass@8 TOO EASY\" (Astra 6, 4 of 4 solved, the other 4 not run, "
                         "Nov 11), the reviewer has not decided whether it comes back; last change Nov 11, 0 unseen.",
                         "v1 (the platform's v2 is the same files)",
                         "IN REVIEW: pass@8 TOO EASY (4 of 4), reviewer deciding; 0 unseen at 19:36",
                         "Watched by the single session (poller T-1383,T-1563,T-1519 at 600 s). If returned, harden "
                         "(draft in `work/rv-planet-census/v3/`)"),
}
st = read("logs/STATUS.md")
lines = st.split("\n")
for slug, (tid, das, state, ver, board_state, nxt) in takeover.items():
    s = read("logs/%s.md" % slug)
    s = insert_at_section_end(s, "## State now",
                              "- **%s**: from now on one session watches every task (user: \"From now on, I want to use "
                              "only this chat session. just one session. You should watch the every tasks pipelines. When "
                              "failed, work one-by-one and upload.\"). This task's poller is the combined one, "
                              "`tools/poll_pipeline.py T-1383,T-1563,T-1519 43200 600`, started %s. %s\n"
                              % (NOW, NOW[11:], state))
    write("logs/%s.md" % slug, s)
    last = max(i for i, l in enumerate(lines) if l.startswith("| %s |" % slug))
    lines.insert(last + 1, "| %s | `tasks/active/%s/` | %s | %s | %s | %s | %s | %s | [log](%s.md) |"
                 % (slug, slug, tid, das, ver, board_state, NOW, nxt, slug))
write("logs/STATUS.md", "\n".join(lines))

g = read("logs/gamma-decay-scheme.md")
g = insert_at_section_end(g, "## State now",
                          "- **%s**: one session now watches every task (BRIEFING point of this time); T-1383 is polled "
                          "by the combined poller `T-1383,T-1563,T-1519` at 600 s. Kit 3.8.7 installed (19:32); v14 "
                          "lints PASS under it.\n" % NOW)
write("logs/gamma-decay-scheme.md", g)
print("logged at", NOW)
