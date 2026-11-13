#!/usr/bin/env bash
# One-command release of a new version (Git Bash, from the folder root):
#   bash tools/release.sh SLUG T-ID N "what changed, one or two sentences"   checks, archive, package, upload, log
#   bash tools/release.sh --check SLUG                                      only the checks: nothing moved or sent
# Checks: no __pycache__, tools/scan_task.py exit 0, the canary line in every shipped text file but *.json,
# .gitattributes and uv.lock, tb4 lint exit 0. Then the zip now in deliveries/ is archived as v(N-1), tb4 package writes the
# new zip, tools/supertasker.py uploads it with Upload the fix and no note (user, 2026-11-02), and
# tools/log_release.py appends the log entries. Nothing here runs the oracle or the verifier (no local tests,
# user, 2026-11-03). Afterwards start tools/poll_pipeline.py in the background.
set -euo pipefail
check_only=0
if [ "${1:-}" = "--check" ]; then check_only=1; shift; fi
slug=${1:?usage: release.sh [--check] SLUG [T-ID N CHANGE]}
T=tasks/active/$slug
[ -d "$T" ] || { echo "FAIL: no $T"; exit 1; }
export PATH="$HOME/tb4/tb4-starter-pack:$PATH"
py() { python -X utf8 -I -B "$@"; }

if [ "$check_only" = 0 ]; then
  tid=${2:?T-ID}; n=${3:?version number}; change=${4:?what changed}
  case "$n" in ''|*[!0-9]*) echo "FAIL: N must be a number"; exit 1;; esac
fi

echo "== checks"
if find "$T" -name __pycache__ | grep -q .; then echo "FAIL: __pycache__ under $T"; exit 1; fi
scan_out=$(py tools/scan_task.py "$T" 2>&1) || { echo "$scan_out"; echo "FAIL: scan_task.py"; exit 1; }
scan_line=$(printf '%s\n' "$scan_out" | tail -1)
echo "scan: $scan_line"
# uv.lock is uv's own output and the kit's templates ship it without a canary (TB 4.1, kit 3.7.0, 2026-11-09)
missing=$(grep -L -r "harbor-canary GUID" "$T" | grep -v -E '\.json$|/\.gitattributes$|/uv\.lock$' || true)
[ -z "$missing" ] || { echo "FAIL: no canary line in:"; echo "$missing"; exit 1; }
echo "canary: in every shipped text file but JSON, .gitattributes and uv.lock"
# tb4 lint does not parse solution/*.py: a broken string literal there reached v13's packaging (2026-11-05)
bad_py=""
while IFS= read -r f; do
  py -c "import ast, sys; ast.parse(open(sys.argv[1], encoding='utf-8').read())" "$f" >/dev/null 2>&1 || bad_py="$bad_py $f"
done < <(find "$T" -name '*.py')
[ -z "$bad_py" ] || { echo "FAIL: Python syntax error in:$bad_py"; exit 1; }
echo "python: every .py parses"
lint_out=$(tb4 lint "$T" 2>&1) || { echo "$lint_out"; echo "FAIL: tb4 lint"; exit 1; }
lint_line=$(printf '%s\n' "$lint_out" | grep -v '^\s*$' | tail -1)
lint_line=${lint_line#lint: }
echo "lint: $lint_line"
if [ "$check_only" = 1 ]; then echo "checks passed (nothing moved or sent)"; exit 0; fi

echo "== archive"
shopt -s nullglob
cur=(deliveries/"$slug"-*.zip)
[ "${#cur[@]}" -le 1 ] || { echo "FAIL: more than one $slug zip in deliveries/"; exit 1; }
archived=""
if [ "${#cur[@]}" = 1 ]; then
  d=${cur[0]##*-}; d=${d%.zip}
  mkdir -p "deliveries/archive/$slug"
  archived="deliveries/archive/$slug/$slug-v$((n - 1))-$d.zip"
  [ ! -e "$archived" ] || { echo "FAIL: $archived exists"; exit 1; }
  mv "${cur[0]}" "$archived"
  echo "archived ${cur[0]} as $archived"
fi

echo "== package"
pkg_out=$(tb4 package "$T" 2>&1) || { echo "$pkg_out"; echo "FAIL: tb4 package"; exit 1; }
printf '%s\n' "$pkg_out" | tail -4
zip="deliveries/$slug-$(date -u +%Y%m%d).zip"
[ -f "$zip" ] || { echo "FAIL: no $zip after packaging"; exit 1; }
digest=$(printf '%s\n' "$pkg_out" | grep -o 'sha256:[0-9a-f]\{64\}' | head -1)
[ -n "$digest" ] || digest=$(py "$HOME/tb4/tb4-starter-pack/lint/gatelib.py" "$T")

echo "== upload ($tid, no note)"
up_out=$(py tools/supertasker.py upload-fix "$tid" "$zip" 2>&1) || {
  echo "$up_out"; echo "FAIL: upload-fix. $zip is packaged and the old zip archived; nothing logged"; exit 1; }
printf '%s\n' "$up_out" | tail -6

echo "== log"
py tools/log_release.py "$slug" "$tid" "$n" "$zip" "$digest" "$archived" "$change" "$lint_line" "$scan_line"
echo "next: start the poller in the background: python -X utf8 -I -B tools/poll_pipeline.py $tid 43200 180"
