# Remove a directory tree. Usage: pwsh -NoProfile -File rmtree.ps1 <path>
param([Parameter(Mandatory)][string]$TargetPath)
if (Test-Path $TargetPath) {
    Remove-Item -Recurse -Force $TargetPath
}
