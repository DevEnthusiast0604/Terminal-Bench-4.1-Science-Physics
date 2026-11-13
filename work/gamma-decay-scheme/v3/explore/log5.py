"""2026-11-09 01:58: toolkit 3.7.0 downloaded and installed; the platform is now the TB4.1 Queue and T-1383 is gone.
Adds only (logs are append-only)."""


def read(path):
    return open(path, encoding="utf-8", newline="").read()


def write(path, text):
    open(path, "w", encoding="utf-8", newline="").write(text)


# --- briefing: a new dated section at the end
points = """
## Points added 2026-11-09

- (01:58) User: "download the updated Toolkit". The platform is now the **TB4.1 Queue**, with toolkit 3.7.0 dated
  2026-11-08. I downloaded it with `supertasker.py fetch gate/kit/download` to `work/toolkit/20261109/kit.zip` (1012516
  bytes, extracted to `x/`) and installed it at `~/tb4/tb4-starter-pack` (`tb4 --version`: 3.7.0). The old 3.3.0 is kept
  at `~/tb4/tb4-starter-pack-3.3.0`.
- (01:58) TB4.1's My tasks is empty. T-1383 and its queued v2 quick check are gone, `/task/T-1383` answers "not found",
  and Updates and To do are empty. The poller last ran on 11-06 and stopped at 12:09 after three status time-outs, so
  nothing was watched from then until 11-09. The Submit page (11-09 01:55) shows 2 of 2 new tasks left today, 66 quick
  checks and 79 pass@3 runs left this week, reset Monday Nov 16 00:00 UTC. The Workflow tab says:
  - only the first task needs a DAS Task ID;
  - the platform links a P3 ID pasted into DAS by itself, within about 10 minutes;
  - a quick-check flag can be disputed from the report, with a reason.
  Its section "Hard for the right reason" is saved in `work/toolkit/20261109/workflow-tab.txt`.
- (01:58) TB 4.1 rules in kit 3.7.0:
  - Every Python dependency comes from a committed lock: `environment/locks/pyproject.toml` plus `uv.lock`, made with
    `uv lock --directory environment/locks`. Never `pip install` in a Dockerfile.
  - uv 0.10.8, the version the template's Docker build uses, is installed here with `pip install --user`
    (`%APPDATA%/Python/Python312/Scripts/uv.exe`).
  - `tests/locks/judge/` is copied from the template unchanged.
  - The template's `tests/test.sh` gained root-only checks, so a task takes the new copy.
  - README metadata: Author as `Name (email)`, Category alone (`Science`), Tags as `<code>`. These are lint warnings,
    not failures.
  - The kit's own `uv.lock` files carry no canary line.
"""
s = read("logs/BRIEFING.md")
assert "## Points added 2026-11-09" not in s
write("logs/BRIEFING.md", s.rstrip("\n") + "\n" + points)

# --- status board: a new row right before "Archived:" (the last table row ends with the "\n" of the separator)
row = ("| gamma-decay-scheme | `tasks/active/gamma-decay-scheme/` | T-1383 (TB4.0, gone) | 4011092 | v2 "
       "(`gamma-decay-scheme-20261106.zip`, digest `7981e5c9…bed9`) | PLATFORM RESET: the platform is now the TB4.1 Queue "
       "(toolkit 3.7.0, 2026-11-08). My tasks is empty: T-1383 and v2's queued quick check are gone. Toolkit 3.7.0 "
       "installed (user: \"download the updated Toolkit\") | 2026-11-09 01:58 | Move the task to the 3.7.0 template "
       "(locks, test.sh, README metadata), lint, package, submit again as a new task with DAS 4011092, start the poller |")
s = read("logs/STATUS.md")
sep = "\nArchived:\n"
assert s.count(sep) == 1
write("logs/STATUS.md", s.replace(sep, "\n" + row + sep))

# --- task log: a State now bullet, right before "## Current design"
bullet = ("- **2026-11-09 01:58**: the platform is now the TB4.1 Queue (toolkit 3.7.0, 2026-11-08). My tasks is empty: "
          "T-1383 and v2's queued quick check are gone, and `/task/T-1383` answers \"not found\". The poller had stopped "
          "on 11-06 at 12:09 (three status time-outs). On the user's \"download the updated Toolkit\", kit 3.7.0 is "
          "installed. Next: move the task to the TB 4.1 template (dependency locks, the new `tests/test.sh`, README "
          "metadata) and submit it again as a new task with DAS 4011092.\n")
s = read("logs/gamma-decay-scheme.md")
anchor = "\n## Current design"
assert s.count(anchor) == 1
head, tail = s.split(anchor)
write("logs/gamma-decay-scheme.md", head.rstrip("\n") + "\n" + bullet + anchor + tail)

# --- physics state: a session event at the end
event = ("- **2026-11-09 01:58**: platform reset to the TB4.1 Queue (toolkit 3.7.0, 2026-11-08); My tasks empty, T-1383 "
         "gone. Kit 3.7.0 installed (3.3.0 kept as `~/tb4/tb4-starter-pack-3.3.0`). TB 4.1 needs committed uv locks "
         "for every Python dependency. Next: migrate the task and submit it again with DAS 4011092.\n")
s = read("work/physics-task-state.md")
write("work/physics-task-state.md", s.rstrip("\n") + "\n" + event)
print("done")
