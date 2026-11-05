#!/usr/bin/env bash
# Usage: bash run-verify.sh [TASK [tests,lint,build,typecheck|all]]
# Also accepts: --task TASK --gates GATES
# Exit codes: 0=PASS, 1=ECHEC, 2=BLOQUE/invalid invocation, 3=PARTIEL.
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
if bash "$SCRIPT_DIR/check.sh" "${ARGS[@]}"; then
  EXIT_CODE=0
else
  EXIT_CODE=$?
fi
case $EXIT_CODE in
  0) printf '[verify] PASS: check.sh reports successful selected gates; this does not authorize deployment.\n' ;;
  1) printf '[verify] ECHEC: verification failed. Inspect the gate logs.\n' >&2 ;;
  2) printf '[verify] BLOQUE: verification unavailable or invocation invalid. Inspect the diagnostics.\n' >&2 ;;
  3) printf '[verify] PARTIEL: verification is incomplete; do not treat this as PASS.\n' >&2 ;;
  *) printf '[verify] UNEXPECTED ERROR: check.sh exited with code %s; verification is not validated.\n' "$EXIT_CODE" >&2 ;;
esac
exit "$EXIT_CODE"
