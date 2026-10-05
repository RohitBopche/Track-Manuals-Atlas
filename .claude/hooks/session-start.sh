#!/bin/bash
# Install the Python and Node dependencies so tests, gates and browser suites run in a fresh
# Claude Code cloud session. Local sessions are left alone. Idempotent; safe to rerun.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0
cd "${CLAUDE_PROJECT_DIR:-$(dirname "$0")/../..}"
python3 -m pip install -q -r requirements-dev.txt
npm ci --no-audit --no-fund --loglevel=error
# Browser suites look for Chrome via CHROME_PATH; point it at the preinstalled Chromium when present.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  for c in /opt/pw-browsers/chromium-*/chrome-linux/chrome; do
    [ -x "$c" ] && echo "export CHROME_PATH=$c" >> "$CLAUDE_ENV_FILE" && break
  done
fi
