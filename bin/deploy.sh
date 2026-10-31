#!/usr/bin/env bash
# Distribute templates into Hermes profiles.
# Usage: bin/deploy.sh <role> [<role> …]   (or no args for every existing profile)
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
H="${HERMES_HOME:-$HOME/.hermes}"
OWNER="${HERMES_OWNER:-$(id -un)}"

[ -d "$H/profiles" ] || { echo "ERROR: $H/profiles not found" >&2; exit 1; }

roles=("$@")
if [ ${#roles[@]} -eq 0 ]; then
  while IFS= read -r d; do roles+=("${d##*/}"); done < <(find "$H/profiles" -mindepth 1 -maxdepth 1 -type d | sort)
fi
[ ${#roles[@]} -gt 0 ] || { echo "no profiles in $H/profiles, nothing to deploy"; exit 0; }

install -d -m 755 "$H/scripts"
install -m 755 "$REPO/bin/state.py" "$H/scripts/state.py"

common="$(sed -n '/^```text$/,/^```$/p' "$REPO/templates/common-rules.md" | sed '1d;$d')"

for role in "${roles[@]}"; do
  case "$role" in ''|*[!A-Za-z0-9_-]*) echo "skip $role: invalid name" >&2; continue ;; esac
  dst="$H/profiles/$role"
  [ -d "$dst" ] || { echo "skip $role: no profile"; continue; }

  # SOUL: template with the common-rules block appended verbatim.
  sed '/templates\/common-rules.md/d' "$REPO/templates/SOUL.template.md" > "$dst/SOUL.md"
  printf '%s\n' "$common" >> "$dst/SOUL.md"

  install -d -m 755 "$dst/skills/$role"
  install -m 644 "$REPO/templates/SKILL.template.md" "$dst/skills/$role/SKILL.md"
  chown -R "$OWNER" "$dst/SOUL.md" "$dst/skills/$role" 2>/dev/null || true

  printf '%-14s soul=%s rules=%s skill=%s\n' "$role" \
    "$(wc -l < "$dst/SOUL.md")" \
    "$(grep -c 'COMMON RULES' "$dst/SOUL.md")" \
    "$(wc -l < "$dst/skills/$role/SKILL.md")"
  ok=$role
done

echo "--- state helper ---"
"$H/scripts/state.py" read "${ok:?no valid role deployed}" >/dev/null 2>&1 && echo "state.py OK"
