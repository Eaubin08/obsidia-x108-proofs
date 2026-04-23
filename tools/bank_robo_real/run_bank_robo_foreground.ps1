param(
  [Parameter(Mandatory=$true)][string]$RepoPath,
  [Parameter(Mandatory=$true)][string]$EnvFile,
  [int]$Port = 3018
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $RepoPath)) { throw "RepoPath not found: $RepoPath" }
if (-not (Test-Path $EnvFile)) { throw "EnvFile not found: $EnvFile" }

$envMap = @{}
Get-Content -LiteralPath $EnvFile | ForEach-Object {
  if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
    $k = $matches[1]
    $v = $matches[2].Trim().Trim('"').Trim("'")
    $envMap[$k] = $v
  }
}

Set-Location $RepoPath

$env:NODE_ENV = "development"
$env:PORT = [string]$Port

foreach ($k in @("DATABASE_URL","GEMINI_API_KEY","OAUTH_SERVER_URL","JWT_SECRET","OWNER_OPEN_ID","VITE_APP_ID")) {
  if ($envMap.ContainsKey($k) -and -not [string]::IsNullOrWhiteSpace($envMap[$k])) {
    Set-Item -Path ("Env:" + $k) -Value ([string]$envMap[$k])
  }
}

pnpm exec tsx server/_core/index.ts