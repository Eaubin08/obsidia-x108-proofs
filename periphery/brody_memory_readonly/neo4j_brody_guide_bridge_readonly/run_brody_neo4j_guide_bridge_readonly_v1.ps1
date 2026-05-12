param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("validate","import","query")]
  [string]$Mode,

  [string]$Query = "",
  [int]$Limit = 10,
  [int]$BatchSize = 250
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..\..\..")
$Root = Resolve-Path (Join-Path $RepoRoot "..")

$ptrRoot = Join-Path $Root "CURRENT_GRAPHITI_READONLY_INDEX_V2.txt"
$ptrRepo = Join-Path $RepoRoot "CURRENT_GRAPHITI_READONLY_INDEX_V2.txt"

if (Test-Path $ptrRoot) {
  $ptr = Get-Content $ptrRoot
} elseif (Test-Path $ptrRepo) {
  $ptr = Get-Content $ptrRepo
} else {
  throw "GRAPHITI_V2_POINTER_NOT_FOUND"
}

$records = ($ptr | Where-Object { $_ -like "RECORDS=*" }) -replace "^RECORDS=", ""

if (!(Test-Path $records)) {
  throw "GRAPHITI_V2_RECORDS_NOT_FOUND=$records"
}

$py = Join-Path $ScriptDir "brody_neo4j_guide_bridge_readonly_v1.py"

if ($Mode -eq "validate") {
  & python $py --records $records --mode validate
} elseif ($Mode -eq "import") {
  & python $py --records $records --mode import --batch-size $BatchSize
} else {
  & python $py --records $records --mode query --query $Query --limit $Limit
}

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_NEO4J_GUIDE_BRIDGE_FAILED"
}
