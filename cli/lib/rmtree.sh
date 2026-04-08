#!/usr/bin/env bash
# Remove a directory tree. Usage: rmtree.sh <path>
set -euo pipefail
[ -d "$1" ] && rm -rf "$1"
