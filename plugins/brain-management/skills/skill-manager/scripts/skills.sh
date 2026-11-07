#!/usr/bin/env bash
# Install, list, update and remove Agent Skills for Claude Code and Codex.
# Global default: ~/.agents/skills/<name>, linked into ~/.claude/skills when needed.
# Folder scope: <folder>/.agents/skills/<name>, linked into <folder>/.claude/skills.
# Installed skills retain .source for safe updates. Removal moves skills to a timestamped trash directory.
#
# Usage:
#   skills.sh available [<source>]
#   skills.sh install <source> [<skill>...|all] [--to <folder>] [--force]
#   skills.sh list [--to <folder>]
#   skills.sh update [<skill>...] [--to <folder>]
#   skills.sh remove <skill>... [--to <folder>]

set -euo pipefail

KIT="Melvynx/ai-sprint-skills"
TRASH="${HOME}/.cache/removed-skills"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cmd="${1:-}"
shift || true

TO=""
FORCE=0
ARGS=()

while [ "$#" -gt 0 ]; do
  case "$1" in
    --to)
      [ "$#" -ge 2 ] || { echo "--to requires a folder" >&2; exit 2; }
      TO="$2"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    *)
      ARGS+=("$1")
      shift
      ;;
  esac
done

# Restore positional arguments consumed while parsing options.
set -- ${ARGS[@]+"${ARGS[@]}"}

if [ -n "$TO" ]; then
  ROOT="$(cd "$TO" 2>/dev/null && pwd)" || { echo "not a folder: $TO" >&2; exit 4; }
  DEST="$ROOT/.agents/skills"
  CLAUDE="$ROOT/.claude/skills"
else
  DEST="$HOME/.agents/skills"
  CLAUDE="$HOME/.claude/skills"
fi

skill_name() {
  local file="$1/SKILL.md"
  local name
  name="$(sed -n 's/^name:[[:space:]]*//p' "$file" | head -n1 | tr -d "\"'")"
  printf '%s' "${name:-$(basename "$1")}"
}

description_of() {
  sed -n 's/^description:[[:space:]]*//p' "$1/SKILL.md" | head -n1 | tr -d '"' | cut -c1-120
}

same_path() {
  [ "$(cd "$1" 2>/dev/null && pwd -P)" = "$(cd "$2" 2>/dev/null && pwd -P)" ]
}

link_skill() {
  local name="$1"
  same_path "$CLAUDE" "$DEST" && return 0
  mkdir -p "$CLAUDE"
  ln -sfn "$DEST/$name" "$CLAUDE/$name"
}

unlink_skill() {
  local name="$1"
  if [ -L "$CLAUDE/$name" ]; then
    rm -f "$CLAUDE/$name"
  fi
}

stash_skill() {
  local name="$1"
  mkdir -p "$TRASH"
  mv "$DEST/$name" "$TRASH/${name}-$(date +%Y%m%d-%H%M%S)"
}

fetch_source() {
  local source="${1%/}"
  local path=""
  REPO=""
  REF="HEAD"
  TOP=""

  if [ -d "$source" ]; then
    BASE="$(cd "$source" && pwd)"
    return 0
  fi

  source="${source#https://}"
  source="${source#http://}"
  source="${source#github.com/}"
  source="${source%.git}"

  case "$source" in
    */*/tree/*|*/*/blob/*)
      REPO="$(printf '%s' "$source" | cut -d/ -f1-2)"
      REF="$(printf '%s' "$source" | cut -d/ -f4)"
      path="$(printf '%s' "$source" | cut -d/ -f5-)"
      ;;
    */*)
      REPO="$(printf '%s' "$source" | cut -d/ -f1-2)"
      path="$(printf '%s' "$source" | cut -d/ -f3-)"
      ;;
    *)
      echo "invalid source: $1" >&2
      return 4
      ;;
  esac

  path="${path%/SKILL.md}"
  local output="$TMP/$(printf '%s' "$REPO@$REF" | tr '/' '_')"
  mkdir -p "$output"

  if ! curl -fsSL "https://codeload.github.com/$REPO/tar.gz/$REF" | tar -xz -C "$output"; then
    echo "cannot download $REPO at $REF" >&2
    return 4
  fi

  TOP="$(find "$output" -mindepth 1 -maxdepth 1 -type d | head -n1)"
  BASE="$TOP${path:+/$path}"
  [ -d "$BASE" ] || { echo "skill path not found: $path" >&2; return 4; }
}

skills_in_base() {
  find "$BASE" -name SKILL.md -not -path '*/.git/*' -not -path '*/node_modules/*' 2>/dev/null \
    | sed 's|/SKILL.md$||' | sort
}

install_skill() {
  local source_folder="$1"
  local name
  name="$(skill_name "$source_folder")"

  if [ ! -f "$source_folder/SKILL.md" ]; then
    echo "missing SKILL.md in $source_folder" >&2
    return 4
  fi

  if [ -e "$DEST/$name" ] || [ -L "$DEST/$name" ]; then
    if [ ! -f "$DEST/$name/.source" ] && [ "$FORCE" -ne 1 ]; then
      echo "exists=$name; use --force only after reviewing it" >&2
      return 3
    fi
    if [ -f "$DEST/$name/.source" ]; then
      rm -rf "$DEST/$name"
    else
      stash_skill "$name"
    fi
  fi

  mkdir -p "$DEST"
  cp -R "$source_folder" "$DEST/$name"
  rm -rf "$DEST/$name/.git"
  printf '%s\n' "${REPO:+https://github.com/$REPO/tree/$REF}${REPO:-$source_folder}" > "$DEST/$name/.source"
  link_skill "$name"
  echo "installed=$name -> $DEST/$name"
}

install_command() {
  [ "$#" -gt 0 ] || { echo "usage: skills.sh install <source> [<skill>...|all]" >&2; exit 2; }
  local source="$1"
  shift
  local wanted=("$@")

  if [ ! -d "$source" ] && [[ "$source" != */* ]]; then
    wanted=("$source" "$@")
    source="$KIT"
  fi

  fetch_source "$source"
  local found
  found="$(skills_in_base)"
  [ -n "$found" ] || { echo "no SKILL.md found in $source" >&2; exit 4; }

  if [ "${#wanted[@]}" -eq 0 ]; then
    local count
    count="$(printf '%s\n' "$found" | wc -l)"
    if [ "$count" -gt 1 ]; then
      echo "multiple skills available; specify one or use all:" >&2
      while IFS= read -r folder; do
        printf '  %-22s %s\n' "$(skill_name "$folder")" "$(description_of "$folder")" >&2
      done <<< "$found"
      exit 2
    fi
    wanted=(all)
  fi

  local status=0
  for wanted_name in "${wanted[@]}"; do
    local matched=0
    while IFS= read -r folder; do
      local current
      current="$(skill_name "$folder")"
      if [ "$wanted_name" = "all" ] || [ "$wanted_name" = "$current" ] || [ "$wanted_name" = "$(basename "$folder")" ]; then
        matched=1
        install_skill "$folder" || status=$?
      fi
    done <<< "$found"
    [ "$matched" -eq 1 ] || { echo "unknown skill: $wanted_name" >&2; status=4; }
  done
  exit "$status"
}

case "$cmd" in
  available)
    fetch_source "${1:-$KIT}"
    while IFS= read -r folder; do
      local_name="$(skill_name "$folder")"
      if [ -f "$DEST/$local_name/.source" ]; then
        state=installed
      elif [ -e "$DEST/$local_name" ]; then
        state=own
      else
        state=available
      fi
      printf '%-22s %-10s %s\n' "$local_name" "$state" "$(description_of "$folder")"
    done < <(skills_in_base)
    ;;
  install)
    install_command "$@"
    ;;
  list)
    for folder in "$DEST"/*/; do
      [ -f "$folder/SKILL.md" ] || continue
      folder="${folder%/}"
      if [ -f "$folder/.source" ]; then
        origin="$(sed 's|https://github.com/||; s|/tree/.*||' "$folder/.source")"
      else
        origin=own
      fi
      printf '%-22s %-28s %s\n' "$(basename "$folder")" "$origin" "$(description_of "$folder")"
    done
    ;;
  update)
    names=("$@")
    if [ "${#names[@]}" -eq 0 ]; then
      for folder in "$DEST"/*/; do
        [ -f "$folder/.source" ] && names+=("$(basename "$folder")")
      done
    fi
    [ "${#names[@]}" -gt 0 ] || { echo "no skill-manager-installed skills found"; exit 0; }
    FORCE=1
    local_status=0
    for name in "${names[@]}"; do
      [ -f "$DEST/$name/.source" ] || { echo "skipped=$name; no .source metadata" >&2; continue; }
      install_command "$(cat "$DEST/$name/.source")" "$name" || local_status=$?
    done
    exit "$local_status"
    ;;
  remove)
    [ "$#" -gt 0 ] || { echo "usage: skills.sh remove <skill>..." >&2; exit 2; }
    status=0
    for name in "$@"; do
      if [ -e "$DEST/$name" ] || [ -L "$DEST/$name" ]; then
        stash_skill "$name"
        unlink_skill "$name"
        echo "removed=$name; kept in $TRASH"
      else
        echo "missing=$name" >&2
        status=4
      fi
    done
    exit "$status"
    ;;
  *)
    sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
    exit 2
    ;;
esac
