#!/usr/bin/env bash
# Regression tests for skills/verify/scripts/check.sh
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CHECK="$ROOT/skills/verify/scripts/check.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
FAILED=0

expect() {
  local name=$1 expected=$2 actual=$3
  if [[ $expected == "$actual" ]]; then printf 'PASS %s\n' "$name"; else printf 'FAIL %s: expected %s, got %s\n' "$name" "$expected" "$actual"; FAILED=$((FAILED+1)); fi
}

run_check() {
  local dir=$1; shift
  (cd "$dir" && bash "$CHECK" "$@" >/dev/null 2>&1)
  echo $?
}

# Unknown option must fail closed.
expect 'rejects unknown option' 2 "$(run_check "$TMP" --unknown)"

# No detected gates means blocked, not success.
expect 'no gates is blocked' 2 "$(run_check "$TMP" --all)"

# A failing required test gate must fail.
mkdir -p "$TMP/fail"
cat > "$TMP/fail/package.json" <<'EOF'
{"scripts":{"test":"false"}}
EOF
expect 'failing tests is failure' 1 "$(run_check "$TMP/fail" --tests)"

# A passing required test gate with no optional gates is PASS.
mkdir -p "$TMP/pass"
cat > "$TMP/pass/package.json" <<'EOF'
{"scripts":{"test":"true"}}
EOF
expect 'passing tests is pass' 0 "$(run_check "$TMP/pass" --tests)"

# A passing required gate plus a missing optional gate is PARTIEL, not PASS.
mkdir -p "$TMP/partial"
cat > "$TMP/partial/package.json" <<'EOF'
{"scripts":{"test":"true"}}
EOF
expect 'missing optional gate is partial' 3 "$(run_check "$TMP/partial" --all)"

# Typecheck must be independent from build.
mkdir -p "$TMP/types"
cat > "$TMP/types/tsconfig.json" <<'EOF'
{"compilerOptions":{"noEmit":true}}
EOF
expect 'typecheck unavailable is blocked' 2 "$(run_check "$TMP/types" --typecheck)"

if [[ $FAILED -gt 0 ]]; then
  printf '%s regression test(s) failed\n' "$FAILED" >&2
  exit 1
fi
printf 'All check.sh regression tests passed.\n'
