#!/usr/bin/env bash
# Copies every shared/*.md file into skills/<skill>/references/,
# and the templates that exec-setup needs into skills/exec-setup/references/.
# Usage:
#   scripts/sync-shared.sh          write copies (idempotent)
#   scripts/sync-shared.sh --check  exit 1 if any copy is missing or differs (for CI)
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED_DIR="$ROOT/shared"
SKILLS_DIR="$ROOT/skills"
MODE="write"

case "${1:-}" in
  "") ;;
  --check) MODE="check" ;;
  -h|--help)
    sed -n '2,5p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  *)
    echo "Unknown argument: $1" >&2
    exit 2
    ;;
esac

shopt -s nullglob
shared_files=("$SHARED_DIR"/*.md)
skill_dirs=("$SKILLS_DIR"/*/)

if [ ${#shared_files[@]} -eq 0 ]; then
  echo "No shared files found in $SHARED_DIR" >&2
  exit 1
fi
if [ ${#skill_dirs[@]} -eq 0 ]; then
  echo "No skills found in $SKILLS_DIR" >&2
  exit 1
fi

drift=0
updated=0

for skill_dir in "${skill_dirs[@]}"; do
  skill_dir="${skill_dir%/}"
  skill_name="$(basename "$skill_dir")"
  [ -f "$skill_dir/SKILL.md" ] || continue
  ref_dir="$skill_dir/references"

  for src in "${shared_files[@]}"; do
    name="$(basename "$src")"
    dst="$ref_dir/$name"
    if [ "$MODE" = "check" ]; then
      if [ ! -f "$dst" ]; then
        echo "MISSING  skills/$skill_name/references/$name"
        drift=1
      elif ! cmp -s "$src" "$dst"; then
        echo "DRIFT    skills/$skill_name/references/$name"
        drift=1
      fi
    else
      mkdir -p "$ref_dir"
      if [ ! -f "$dst" ] || ! cmp -s "$src" "$dst"; then
        cp "$src" "$dst"
        echo "UPDATED  skills/$skill_name/references/$name"
        updated=$((updated + 1))
      fi
    fi
  done
done

# Templates used at runtime by exec-setup (source:destination name).
TEMPLATE_MAP=(
  "templates/exec-profile.template.md:skills/exec-setup/references/profile-template.md"
  "templates/schedules.md:skills/exec-setup/references/schedules.md"
)
for pair in "${TEMPLATE_MAP[@]}"; do
  src="$ROOT/${pair%%:*}"
  dst="$ROOT/${pair#*:}"
  [ -f "$src" ] || { echo "Missing template ${pair%%:*}" >&2; exit 1; }
  [ -d "$(dirname "$dst")/.." ] || continue
  if [ "$MODE" = "check" ]; then
    if [ ! -f "$dst" ]; then
      echo "MISSING  ${pair#*:}"
      drift=1
    elif ! cmp -s "$src" "$dst"; then
      echo "DRIFT    ${pair#*:}"
      drift=1
    fi
  else
    mkdir -p "$(dirname "$dst")"
    if [ ! -f "$dst" ] || ! cmp -s "$src" "$dst"; then
      cp "$src" "$dst"
      echo "UPDATED  ${pair#*:}"
      updated=$((updated + 1))
    fi
  fi
done

if [ "$MODE" = "check" ]; then
  if [ "$drift" -ne 0 ]; then
    echo "Shared copies are out of sync. Run scripts/sync-shared.sh" >&2
    exit 1
  fi
  echo "OK: shared copies are in sync (${#shared_files[@]} files x ${#skill_dirs[@]} skills)"
else
  echo "Done: $updated file(s) updated"
fi
