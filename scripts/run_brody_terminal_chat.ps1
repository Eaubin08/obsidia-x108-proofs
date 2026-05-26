# Run Brody Terminal Chat Client V1
# Assumes the Obsidia API is already running on http://127.0.0.1:8000
# Does NOT launch Uvicorn, Docker, or Neo4j automatically.

$ErrorActionPreference = "Stop"

# ── UTF-8 environment ──────────────────────────────────────────────────────
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

# ── Navigate to repo root ──────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $RepoRoot

# ── Launch ─────────────────────────────────────────────────────────────────
Write-Host "Brody Terminal Chat Client V1" -ForegroundColor Cyan
Write-Host "Endpoint: http://127.0.0.1:8000" -ForegroundColor DarkGray
Write-Host ""

$Endpoint = if ($args.Count -gt 0) { $args[0] } else { "http://127.0.0.1:8000" }
python scripts/brody_terminal_chat.py $Endpoint
