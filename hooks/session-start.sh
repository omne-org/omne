#!/usr/bin/env bash
# omne kernel boot hook — runs on Claude Code session start.
# Reads kernel and distro manifests, prints installation info.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR/../scripts"

python "$SCRIPTS_DIR/query_install.py"
