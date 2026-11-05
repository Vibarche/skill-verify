#!/usr/bin/env bash
# Isolated regression tests for skills/verify/hooks/post-task.sh.
# These tests use a temporary repository and a fake runner; they do not run real gates.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOK="$ROOT/skills/verify/hooks/post-task.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FAILED=0

expect() {
  local name=$1 expected=$2 actual=$3
  if [[ $expected == "$actual" ]]; then
    printf 'PASS %s\n' "$name"
  else
    printf 'FAIL %s: expected %s, got %s\n' "$name" "$expected" "$actual"
    FAILED=$((FAILED + 1))
  fi
}

make_repo() {
  local repo="$TMP/repo-$1"
  mkdir -p "$repo/skills/verify/scripts" "$repo/.verify"
  cat > "$repo/skills/verify/scripts/run-verify.sh" <<'EOF'
#!/usr/bin/env bash
printf 'FAKE_RUNNER\n'
exit 0
EOF
  chmod +x "$repo/skills/verify/scripts/run-verify.sh"
  cp "$HOOK" "$repo/post-task.sh"
  chmod +x "$repo/post-task.sh"
  printf '%s' "$repo"
}

run_hook() {
  local repo=$1 payload=$2
  (cd "$repo" && printf '%s' "$payload" | bash ./post-task.sh >/dev/null 2>&1)
  echo $?
}

runner_called() {
  local repo=$1 payload=$2
  (cd "$repo" && printf '%s' "$payload" | bash ./post-task.sh 2>/dev/null | grep -q 'FAKE_RUNNER')
  if [[ $? -eq 0 ]]; then echo yes; else echo no; fi
}

# Stop events should trigger verification.
REPO=$(make_repo stop)
PAYLOAD='{"hook_event_name":"Stop","stop_hook_active":false}'
expect 'Stop triggers runner' yes "$(runner_called "$REPO" "$PAYLOAD")"
expect 'Stop hook remains non-blocking' 0 "$(run_hook "$REPO" "$PAYLOAD")"

# SubagentStop should trigger verification.
REPO=$(make_repo subagent)
PAYLOAD='{"hook_event_name":"SubagentStop","stop_hook_active":false}'
expect 'SubagentStop triggers runner' yes "$(runner_called "$REPO" "$PAYLOAD")"

# A completed Bash command should trigger verification.
REPO=$(make_repo bash-complete)
PAYLOAD='{"hook_event_name":"PostToolUse","tool_name":"Bash","tool_response":"Task complete"}'
expect 'Bash completion triggers runner' yes "$(runner_called "$REPO" "$PAYLOAD")"

# A non-Bash tool must not trigger verification.
REPO=$(make_repo non-bash)
PAYLOAD='{"hook_event_name":"PostToolUse","tool_name":"Write","tool_response":"Task complete"}'
expect 'non-Bash tool does not trigger runner' no "$(runner_called "$REPO" "$PAYLOAD")"

# A Bash command without completion wording must not trigger verification.
REPO=$(make_repo bash-neutral)
PAYLOAD='{"hook_event_name":"PostToolUse","tool_name":"Bash","tool_response":"listed files"}'
expect 'neutral Bash output does not trigger runner' no "$(runner_called "$REPO" "$PAYLOAD")"

# stop_hook_active must prevent a repeated verification run.
REPO=$(make_repo repeat)
PAYLOAD='{"hook_event_name":"Stop","stop_hook_active":true}'
expect 'stop_hook_active prevents repeat runner' no "$(runner_called "$REPO" "$PAYLOAD")"

# A pending-task marker must trigger verification.
REPO=$(make_repo pending)
touch "$REPO/.verify/pending-task"
PAYLOAD='{"hook_event_name":"PostToolUse","tool_name":"Read","tool_response":"no completion"}'
expect 'pending-task marker triggers runner' yes "$(runner_called "$REPO" "$PAYLOAD")"
expect 'pending-task marker is consumed' no "$(test -f "$REPO/.verify/pending-task" && echo yes || echo no)"

# Invalid JSON must not crash the hook or run verification.
REPO=$(make_repo invalid)
expect 'invalid JSON remains non-blocking' 0 "$(run_hook "$REPO" 'not-json')"
expect 'invalid JSON does not trigger runner' no "$(runner_called "$REPO" 'not-json')"

# A missing runner must remain non-blocking.
REPO="$TMP/repo-missing-runner"
mkdir -p "$REPO"
cp "$HOOK" "$REPO/post-task.sh"
chmod +x "$REPO/post-task.sh"
PAYLOAD='{"hook_event_name":"Stop","stop_hook_active":false}'
expect 'missing runner remains non-blocking' 0 "$(run_hook "$REPO" "$PAYLOAD")"

if [[ $FAILED -gt 0 ]]; then
  printf '%s hook regression test(s) failed\n' "$FAILED" >&2
  exit 1
fi
printf 'All hook regression tests passed.\n'
