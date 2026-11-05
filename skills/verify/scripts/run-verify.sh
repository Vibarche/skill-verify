#!/usr/bin/env bash
# Usage: bash run-verify.sh [TASK [tests,lint,build,typecheck|all]]
# Also accepts: --task TASK --gates GATES
set -uo pipefail

TASK='Vérification automatique post-tâche'
GATES=all
if [[ $# -gt 0 && $1 != --* ]]; then
  TASK=$1
  shift
  if [[ $# -gt 0 && $1 != --* ]]; then GATES=$1; shift; fi
fi
while [[ $# -gt 0 ]]; do
  case $1 in
    --task|--gates)
      if [[ $# -lt 2 || -z $2 ]]; then echo 'Missing option value' >&2; exit 2; fi
      if [[ $1 == --task ]]; then TASK=$2; else GATES=$2; fi
      shift 2 ;;
    *) echo "Unknown argument: $1" >&2; exit 2 ;;
  esac
done

ARGS=()
if [[ $GATES == all ]]; then
  ARGS=(--all)
else
  if [[ -z $GATES || $GATES == ,* || $GATES == *, || $GATES == *,,* ]]; then
    echo 'Invalid gate list' >&2; exit 2
  fi
  IFS=',' read -r -a GATE_LIST <<< "$GATES"
  for gate in "${GATE_LIST[@]}"; do
    case $gate in
      tests|lint|build|typecheck) ARGS+=("--$gate") ;;
      *) echo "Unknown gate: $gate" >&2; exit 2 ;;
    esac
  done
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)" || exit 2
if [[ ! -f $SCRIPT_DIR/check.sh ]]; then
  echo 'Verification runner unavailable: check.sh missing' >&2
  exit 2
fi
printf '[verify] Task: %s\n' "$TASK"
bash "$SCRIPT_DIR/check.sh" "${ARGS[@]}"
EXIT_CODE=$?
# check.sh currently uses exit 0 for both PASS and PARTIEL.
# Never promote that exit code to a claim of complete verification.
printf '[verify] Runner exit code: %s. Use the gate verdict above; completion alone is not PASS.\n' "$EXIT_CODE"
exit "$EXIT_CODE"
