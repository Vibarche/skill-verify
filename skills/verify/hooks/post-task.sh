#!/usr/bin/env bash
# Claude Code hook: run verification after a completed task.
# This hook is intentionally non-blocking: it always exits 0.
set -uo pipefail

INPUT=$(cat)

if ! command -v python3 >/dev/null 2>&1; then
  printf '[verify-hook] python3 unavailable; skipping verification.\n' >&2
  exit 0
fi

read -r -d '' PARSE <<'PY' || true
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    print("\n\n\n")
    sys.exit(0)

event = str(data.get("hook_event_name") or "")
tool = str(data.get("tool_name") or "")
response = data.get("tool_response")
if response is None:
    response = data.get("tool_output") or data.get("output") or ""
if not isinstance(response, str):
    response = json.dumps(response, ensure_ascii=False)
stop_active = "true" if data.get("stop_hook_active") else "false"
# One field per line; response is last and may contain any characters.
sys.stdout.write(f"{event}\n{tool}\n{stop_active}\n{response}\n")
PY

PARSED=$(printf '%s' "$INPUT" | python3 -c "$PARSE" 2>/dev/null || printf '\n\n\n')
mapfile -t FIELDS <<< "$PARSED"
EVENT="${FIELDS[0]:-}"
TOOL="${FIELDS[1]:-}"
STOP_ACTIVE="${FIELDS[2]:-false}"
RESPONSE="${FIELDS[3]:-}"

if [[ $STOP_ACTIVE == true ]]; then
  printf '[verify-hook] Stop verification already active; avoiding repeat run.\n' >&2
  exit 0
fi

COMPLETION_PATTERN='done|finished|completed|implemented|refactored|fixed|added|merged|shipped|deployed|PASS|feature complete|step complete|task complete'

SHOULD_VERIFY=false
if [[ $EVENT == Stop || $EVENT == SubagentStop ]]; then
  SHOULD_VERIFY=true
elif [[ $EVENT == PostToolUse && $TOOL == Bash ]]; then
  if grep -qiE "$COMPLETION_PATTERN" <<<"$RESPONSE"; then
    SHOULD_VERIFY=true
  fi
fi

if [[ -f .verify/pending-task ]]; then
  SHOULD_VERIFY=true
  rm -f .verify/pending-task
fi

if [[ $SHOULD_VERIFY != true ]]; then
  printf '[verify-hook] No completion condition matched; verification skipped.\n' >&2
  exit 0
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || exit 0
CANDIDATES=(
  "$SCRIPT_DIR/../scripts/run-verify.sh"
  "$SCRIPT_DIR/../../../skills/verify/scripts/run-verify.sh"
  "$PWD/skills/verify/scripts/run-verify.sh"
  "$PWD/.claude/skills/verify/scripts/run-verify.sh"
)

RUNNER=""
for candidate in "${CANDIDATES[@]}"; do
  if [[ -f $candidate ]]; then
    RUNNER="$candidate"
    break
  fi
done

if [[ -z $RUNNER ]]; then
  printf '[verify-hook] Verification runner not found.\n' >&2
  exit 0
fi

printf '[verify-hook] Running verification.\n' >&2
bash "$RUNNER" "Post-task verification" all
exit 0
