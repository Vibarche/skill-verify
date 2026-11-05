#!/usr/bin/env bash
# Usage: bash check.sh [--tests] [--lint] [--build] [--typecheck] [--all] [--json]
set -euo pipefail

TS=$(date -u +%Y%m%dT%H%M%SZ)
VERIFY_DIR=".verify/${TS}"
mkdir -p "$VERIFY_DIR"

PASS=0
FAIL=0
SKIPPED=0
BLOQUE=0
REPORT="$VERIFY_DIR/report.json"

printf '[\n  "timestamp": "%s",\n  "gates": [\n' "$TS" > "$REPORT"
FIRST=true

add_result() {
  local name=$1 status=$2 exit_code=$3 command=${4:-}
  $FIRST || printf ',\n' >> "$REPORT"
  FIRST=false
  printf '    {"name": "%s", "status": "%s", "exit_code": %s, "command": "%s", "log": "%s"}' \
    "$name" "$status" "$exit_code" "$command" "$VERIFY_DIR/$name.log" >> "$REPORT"
  case $status in
    PASS) PASS=$((PASS + 1)); printf '  ✅ %s: PASS\n' "$name" ;;
    ECHEC) FAIL=$((FAIL + 1)); printf '  ❌ %s: ECHEC (exit %s)\n' "$name" "$exit_code" ;;
    BLOQUE) BLOQUE=$((BLOQUE + 1)); printf '  🔒 %s: BLOQUE (%s)\n' "$name" "$command" ;;
    SKIP) SKIPPED=$((SKIPPED + 1)); printf '  ⚠️  %s: SKIP (%s)\n' "$name" "$command" ;;
  esac
}

run_gate() {
  local name=$1 cmd=$2 required=$3 log="$VERIFY_DIR/$1.log"
  if [[ -z $cmd ]]; then
    if [[ $required == required ]]; then add_result "$name" BLOQUE 2 'command not detected'
    else add_result "$name" SKIP 0 'command not detected'; fi
    return
  fi
  printf '[verify] %s -> %s\n' "$name" "$cmd"
  set +e
  eval "$cmd" >"$log" 2>&1
  local code=$?
  set -e
  if [[ $code -eq 0 ]]; then add_result "$name" PASS 0 "$cmd"
  else add_result "$name" ECHEC "$code" "$cmd"; fi
}

detect_test_cmd() {
  if [[ -f package.json ]] && grep -Eq '"test"[[:space:]]*:' package.json; then echo 'npm test'; return; fi
  if [[ -f pytest.ini || -f pyproject.toml ]]; then echo 'pytest'; return; fi
  if [[ -f go.mod ]]; then echo 'go test ./...'; return; fi
  if compgen -G '*.csproj' >/dev/null || compgen -G '*.sln' >/dev/null; then echo 'dotnet test'; return; fi
}

detect_lint_cmd() {
  if [[ -f package.json ]] && grep -Eq '"lint"[[:space:]]*:' package.json; then echo 'npm run lint'; return; fi
  if command -v ruff >/dev/null 2>&1; then echo 'ruff check .'; return; fi
  if command -v flake8 >/dev/null 2>&1; then echo 'flake8 .'; return; fi
  if command -v golangci-lint >/dev/null 2>&1; then echo 'golangci-lint run'; return; fi
}

detect_build_cmd() {
  if [[ -f package.json ]] && grep -Eq '"build"[[:space:]]*:' package.json; then echo 'npm run build'; return; fi
  if [[ -f go.mod ]]; then echo 'go build ./...'; return; fi
  if compgen -G '*.csproj' >/dev/null || compgen -G '*.sln' >/dev/null; then echo 'dotnet build'; return; fi
}

detect_typecheck_cmd() {
  if [[ -f package.json ]] && grep -Eq '"typecheck"[[:space:]]*:' package.json; then echo 'npm run typecheck'; return; fi
  if [[ -f tsconfig.json ]] && command -v npx >/dev/null 2>&1; then echo 'npx tsc --noEmit'; return; fi
  if [[ -f pyproject.toml ]] && command -v mypy >/dev/null 2>&1; then echo 'mypy .'; return; fi
}

RUN_ALL=false RUN_TESTS=false RUN_LINT=false RUN_BUILD=false RUN_TYPECHECK=false JSON=false
if [[ $# -eq 0 ]]; then RUN_ALL=true; fi
while [[ $# -gt 0 ]]; do
  case $1 in
    --all) RUN_ALL=true ;; --tests) RUN_TESTS=true ;; --lint) RUN_LINT=true ;;
    --build) RUN_BUILD=true ;; --typecheck) RUN_TYPECHECK=true ;; --json) JSON=true ;;
    *) echo "Unknown option: $1" >&2; exit 2 ;;
  esac
  shift
done

if $RUN_ALL || $RUN_TESTS; then run_gate tests "$(detect_test_cmd)" required; fi
if $RUN_ALL || $RUN_LINT; then run_gate lint "$(detect_lint_cmd)" optional; fi
if $RUN_ALL || $RUN_BUILD; then run_gate build "$(detect_build_cmd)" optional; fi
if $RUN_ALL || $RUN_TYPECHECK; then run_gate typecheck "$(detect_typecheck_cmd)" optional; fi

printf '\n  ]\n}\n' >> "$REPORT"

VERDICT=PASS
if [[ $BLOQUE -gt 0 ]]; then VERDICT=BLOQUE
elif [[ $FAIL -gt 0 ]]; then VERDICT=ECHEC
elif [[ $SKIPPED -gt 0 ]]; then VERDICT=PARTIEL
fi

cat > "$REPORT.tmp" <<EOF
{"verdict":"$VERDICT","pass":$PASS,"fail":$FAIL,"skipped":$SKIPPED,"blocked":$BLOQUE}
EOF
mv "$REPORT.tmp" "$REPORT"

printf '\nVERIFY REPORT — %s\n' "$TS"
printf 'PASS=%s ECHEC=%s SKIP=%s BLOQUE=%s\n' "$PASS" "$FAIL" "$SKIPPED" "$BLOQUE"
printf 'Report: %s\n' "$REPORT"
printf 'VERDICT: %s\n' "$VERDICT"

case $VERDICT in
  PASS) exit 0 ;;
  PARTIEL) exit 3 ;;
  ECHEC) exit 1 ;;
  BLOQUE) exit 2 ;;
esac
