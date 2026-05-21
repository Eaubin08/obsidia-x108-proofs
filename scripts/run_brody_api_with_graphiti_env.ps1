param(
  [switch]$Reload
)

[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [System.Text.UTF8Encoding]::new()
$ErrorActionPreference = "Stop"

$Repo = Resolve-Path (Join-Path $PSScriptRoot "..")
$Root = Resolve-Path (Join-Path $Repo "..")

function Import-EnvFile {
  param([string]$Path)

  if (!(Test-Path -LiteralPath $Path)) {
    return
  }

  Write-Host "ENV_FILE=$Path"

  Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()

    if ($line -eq "") { return }
    if ($line.StartsWith("#")) { return }
    if ($line -notmatch "=") { return }

    $parts = $line -split "=", 2
    $key = $parts[0].Trim()
    $value = $parts[1].Trim()

    # remove surrounding quotes safely
    if ($value.Length -ge 2) {
      if (($value.StartsWith('"') -and $value.EndsWith('"')) -or ($value.StartsWith("'") -and $value.EndsWith("'"))) {
        $value = $value.Substring(1, $value.Length - 2)
      }
    }

    switch ($key) {
      "NEO4J_URI" { $env:NEO4J_URI = $value }
      "NEO4J_USER" { $env:NEO4J_USER = $value }
      "NEO4J_USERNAME" { $env:NEO4J_USERNAME = $value }
      "NEO4J_PASSWORD" { $env:NEO4J_PASSWORD = $value }

      "GRAPHITI_NEO4J_URI" { $env:GRAPHITI_NEO4J_URI = $value }
      "GRAPHITI_NEO4J_USER" { $env:GRAPHITI_NEO4J_USER = $value }
      "GRAPHITI_NEO4J_PASSWORD" { $env:GRAPHITI_NEO4J_PASSWORD = $value }
    }
  }
}

Write-Host "`n=== LOAD BRODY GRAPHITI ENV ===" -ForegroundColor Cyan

$envFiles = @(
  (Join-Path $Root "graphiti-lab\.env.graphiti.local"),
  (Join-Path $Root "obsidiashell-main\.env.obsidiashell.local"),
  (Join-Path $Repo ".env"),
  (Join-Path $Repo ".env.local")
)

foreach ($file in $envFiles) {
  Import-EnvFile -Path $file
}

if (-not $env:NEO4J_URI -and $env:GRAPHITI_NEO4J_URI) {
  $env:NEO4J_URI = $env:GRAPHITI_NEO4J_URI
}

if (-not $env:NEO4J_USER -and $env:GRAPHITI_NEO4J_USER) {
  $env:NEO4J_USER = $env:GRAPHITI_NEO4J_USER
}

if (-not $env:NEO4J_PASSWORD -and $env:GRAPHITI_NEO4J_PASSWORD) {
  $env:NEO4J_PASSWORD = $env:GRAPHITI_NEO4J_PASSWORD
}

if (-not $env:NEO4J_URI) {
  $env:NEO4J_URI = "bolt://127.0.0.1:7688"
}

if (-not $env:NEO4J_USER -and $env:NEO4J_USERNAME) {
  $env:NEO4J_USER = $env:NEO4J_USERNAME
}

if (-not $env:NEO4J_USER) {
  $env:NEO4J_USER = "neo4j"
}

Write-Host "`n=== SAFE ENV CHECK ===" -ForegroundColor Yellow

@{
  NEO4J_URI = $env:NEO4J_URI
  NEO4J_USER = $env:NEO4J_USER
  NEO4J_PASSWORD_SET = [bool]$env:NEO4J_PASSWORD
  NEO4J_PASSWORD_LENGTH = if ($env:NEO4J_PASSWORD) { $env:NEO4J_PASSWORD.Length } else { 0 }
  NEO4J_7688_OPEN = [bool](Test-NetConnection 127.0.0.1 -Port 7688 -InformationLevel Quiet)
} | ConvertTo-Json -Depth 6

Write-Host "`n=== START BRODY API 8000 ===" -ForegroundColor Green

Set-Location $Repo

$argsList = @(
  "-m", "uvicorn",
  "apps.obsidia_api.main:app",
  "--host", "127.0.0.1",
  "--port", "8000"
)

if ($Reload) {
  $argsList += "--reload"
}

python @argsList
