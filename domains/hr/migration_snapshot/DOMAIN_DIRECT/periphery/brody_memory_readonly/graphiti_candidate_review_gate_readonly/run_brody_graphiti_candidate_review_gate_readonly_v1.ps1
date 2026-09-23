param(
  [string]$PlanJsonl = "",
  [string]$OutDir = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repo = Resolve-Path (Join-Path $scriptDir "..\..\..")
$root = Split-Path $repo -Parent

if ($OutDir -eq "") {
  $ts = Get-Date -Format "yyyyMMdd_HHmmss"
  $OutDir = Join-Path $root "_local_audits\BRODY_GRAPHITI_CANDIDATE_REVIEW_GATE_READONLY_V1_$ts"
}

if ($PlanJsonl -eq "") {
  $remotePointer = Join-Path $root "CURRENT_BRODY_GRAPHITI_CANDIDATE_IMPORT_DRY_RUN_READONLY_V1_REMOTE_CLOSE.txt"
  $validatePointer = Join-Path $root "CURRENT_BRODY_GRAPHITI_CANDIDATE_IMPORT_DRY_RUN_READONLY_V1_VALIDATE.txt"

  $pointers = @($remotePointer, $validatePointer)

  foreach ($ptr in $pointers) {
    if (Test-Path $ptr) {
      $map = @{}
      Get-Content $ptr | ForEach-Object {
        if ($_ -match "^(.*?)=(.*)$") {
          $map[$matches[1]] = $matches[2]
        }
      }

      if ($map.ContainsKey("PLAN_JSONL") -and (Test-Path $map["PLAN_JSONL"])) {
        $PlanJsonl = $map["PLAN_JSONL"]
        break
      }
    }
  }
}

if ($PlanJsonl -eq "") {
  throw "PLAN_JSONL_NOT_FOUND"
}

$py = Join-Path $scriptDir "brody_graphiti_candidate_review_gate_readonly_v1.py"

python $py --plan-jsonl $PlanJsonl --out-dir $OutDir

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_GRAPHITI_CANDIDATE_REVIEW_GATE_READONLY_FAILED"
}
