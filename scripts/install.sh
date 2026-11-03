#!/usr/bin/env bash
set -euo pipefail

repo="${OPENFDE_SCHOOL_REPO:-https://github.com/Alan-Youngzhe/OpenFDE-School.git}"
target="${OPENFDE_SCHOOL_DIR:-$HOME/.claude/skills/fde}"

normalize_repo() {
  local value="${1%/}"
  value="${value%.git}"
  case "$value" in
    git@github.com:*) value="https://github.com/${value#git@github.com:}" ;;
    ssh://git@github.com/*) value="https://github.com/${value#ssh://git@github.com/}" ;;
  esac
  printf '%s' "$value"
}

if ! command -v git >/dev/null 2>&1; then
  echo "OpenFDE School needs Git for safe install and updates." >&2
  echo "Open Claude Code and ask: 帮我检查并安装 Git，安装后运行 git --version 验证。" >&2
  exit 1
fi

mkdir -p "$(dirname "$target")"

if [ ! -e "$target" ]; then
  git clone --depth 1 "$repo" "$target"
elif [ -e "$target/.git" ]; then
  actual_repo="$(git -C "$target" remote get-url origin)"
  if [ "$(normalize_repo "$actual_repo")" != "$(normalize_repo "$repo")" ]; then
    echo "Target belongs to a different repository; refusing to update: $target" >&2
    exit 1
  fi
  dirty="$(git -C "$target" status --porcelain)"
  if [ -n "$dirty" ]; then
    echo "Refusing to overwrite local changes in: $target" >&2
    echo "Ask Claude Code to review or commit those changes before updating." >&2
    exit 1
  fi
  git -C "$target" pull --ff-only
else
  echo "Target exists but is not a Git checkout: $target" >&2
  echo "Move it to a backup location, then run this installer again." >&2
  exit 1
fi

test -f "$target/SKILL.md"

if command -v python3 >/dev/null 2>&1; then
  python3 "$target/scripts/validate_school.py"
else
  echo "Python 3 was not found; package validation was skipped." >&2
fi

echo
echo "OpenFDE School is ready at: $target"
echo "Open a new Claude Code session and type: /fde"
