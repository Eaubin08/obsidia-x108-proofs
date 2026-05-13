param(
  [string]$OutDir = "",
  [string]$Neo4jUri = "bolt://localhost:7688",
  [int]$Limit = 500
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $scriptDir "..\..\..")
$workspaceRoot = Split-Path -Parent $repoRoot

$envFiles = @(
  (Join-Path $workspaceRoot "graphiti-lab\.env.graphiti.local"),
  (Join-Path $workspaceRoot "obsidiashell-main\.env.obsidiashell.local")
)

foreach ($envFile in $envFiles) {
  if (Test-Path $envFile) {
    Get-Content $envFile | ForEach-Object {
      if ($_ -match "^\s*#" -or $_ -notmatch "=") { return }
      $k, $v = $_ -split "=", 2
      $k = $k.Trim()
      $v = $v.Trim().Trim('"').Trim("'")
      if ($k -match "^(NEO4J_URI|NEO4J_USER|NEO4J_USERNAME|NEO4J_PASSWORD|NEO4J_DATABASE)$") {
        [Environment]::SetEnvironmentVariable($k, $v, "Process")
      }
    }
  }
}

$env:NEO4J_URI = $Neo4jUri

if (!$env:NEO4J_PASSWORD) {
  throw "NEO4J_PASSWORD_MISSING"
}

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $workspaceRoot "_local_audits\BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_V1_$ts"
}

New-Item -ItemType Directory -Force $OutDir | Out-Null

$py = Join-Path $scriptDir "brody_post_graphiti_apply_verify_readonly_v1.py"

python $py `
  --out-dir $OutDir `
  --neo4j-uri $Neo4jUri `
  --limit $Limit

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_POST_GRAPHITI_APPLY_VERIFY_READONLY_FAILED"
}
