param(
  [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Installing acquisition dependencies..."
py -m pip install -r (Join-Path $ScriptDir "requirements.txt")

Write-Host "Downloading missing Z-ZOA datasets..."
py (Join-Path $ScriptDir "download_missing.py") --repo-root $RepoRoot

Write-Host "Finished. Check datasets/manifests/missing_download_manifest.json"
