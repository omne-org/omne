# omne kernel boot hook — runs on Claude Code session start.
# Reads kernel and distro manifests, prints installation info.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ScriptsDir = Join-Path $ScriptDir "..\scripts"

python (Join-Path $ScriptsDir "query_install.py")
