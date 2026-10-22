#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 ]]; then echo "usage: scan_sensitive.sh PATH..." >&2; exit 2; fi
status=0
for path in "$@"; do
  [[ -e "$path" ]] || continue
  if [[ -d "$path" ]]; then
    files=$(find "$path" -type f ! -path '*/.git/*' ! -path '*/node_modules/*')
  else
    files="$path"
  fi
  while IFS= read -r file; do
    [[ -n "$file" ]] || continue
    base=$(basename "$file")
    if [[ "$base" =~ ^\.env($|\.)|\.pem$|\.key$|id_rsa|id_ed25519|credentials|secret ]]; then
      echo "SENSITIVE_PATH: $file"; status=1; continue
    fi
    if LC_ALL=C grep -IlqE 'AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|BEGIN (RSA|OPENSSH|EC|PRIVATE) KEY|(api[_-]?key|token|password|secret)[[:space:]]*[:=][[:space:]]*["'"'"']?[A-Za-z0-9_./+=-]{12,}' "$file" 2>/dev/null; then
      echo "SENSITIVE_CONTENT: $file"; status=1
    fi
  done <<< "$files"
done
if [[ $status -ne 0 ]]; then echo "Sensitive material detected; review before publishing." >&2; fi
exit "$status"
