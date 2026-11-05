#!/usr/bin/env bash
# Claude Code hook: run verification after a completed task.
# This hook is intentionally non-blocking: it always exits 0.
# Install it through the Claude Code hooks configuration, not merely by copying it.
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
    print("|||")
    sys.exit(0)

event = str(data.get("hook_event_name") or "")
tool = str(data.get("tool_name") or "")
response = data.get("tool_response")
if response is None:
    response = data.get("tool_output") or data.get("output") or ""
if not isinstance(response, str):
    response = json.dumps(response, ensure_ascii=False)
stop_active = bool(data.get("stop_hook_active") or False)
print(f"{event}|||{tool}|||{stop_active}|||{response}")
PY

PARSED=$(printf '%s' "$INPUT" | python3 -c "$PARSE" 2>/dev/null || printf '|||')
IFS='|||' read -r EVENT TOOL STOP_ACTIVE RESPONSE <<< "$PARSED"

if [[ $STOP_ACTIVE == True ]]; then
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
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd)" || exit 0
RUNNER="$PROJECT_ROOT/skills/verify/scripts/run-verify.sh"

if [[ ! -f $RUNNER ]]; then
  printf '[verify-hook] Runner not found: %s\n' "$RUNNER" >&2
  exit 0
fi

printf '[verify-hook] Running verification.\n' >&2
bash "$RUNNER" "Post-task verification" all
exit 0
