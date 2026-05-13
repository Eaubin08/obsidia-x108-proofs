param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$reviewPtr = Join-Path $Root "CURRENT_MEMORY_LAYER_REVIEW_USER_SESSION_RUNTIME_GRAPHITI.txt"
if (!(Test-Path $reviewPtr)) { throw "MISSING_MEMORY_LAYER_REVIEW_POINTER=$reviewPtr" }

$kv = @{}
Get-Content $reviewPtr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

function RequireTrue([string]$key) {
  if ($kv[$key] -ne "True") {
    throw "BAD_OR_MISSING_$key=$($kv[$key])"
  }
}

RequireTrue "USER_MEMORY_PRESENT"
RequireTrue "SESSION_MEMORY_PRESENT"
RequireTrue "RUNTIME_MEMORY_PRESENT"
RequireTrue "GRAPHITI_MEMORY_PRESENT"
RequireTrue "HAS_X108_PROOF_POINTERS"
RequireTrue "HAS_BRODY_RUNTIME_PROOF"
RequireTrue "HAS_NATIVE_TERMINAL_PROOF"
RequireTrue "HAS_DETECTOR_PATCH_PROOF"

if ($kv["MEMORY_DECISION"] -ne "false") { throw "MEMORY_DECISION_NOT_FALSE" }
if ($kv["ALLOWED_TO_DECIDE"] -ne "false") { throw "ALLOWED_TO_DECIDE_NOT_FALSE" }
if ($kv["EMITS_ACT"] -ne "false") { throw "EMITS_ACT_NOT_FALSE" }
if ($kv["EMITS_VERDICT"] -ne "false") { throw "EMITS_VERDICT_NOT_FALSE" }
if ($kv["DECISION_AUTHORITY"] -ne "KX108_ONLY") { throw "BAD_DECISION_AUTHORITY=$($kv["DECISION_AUTHORITY"])" }
if ($kv["KERNEL_MUTATION"] -ne "false") { throw "KERNEL_MUTATION_NOT_FALSE" }
if ($kv["X108_RUNTIME_BINDING"] -ne "false") { throw "X108_RUNTIME_BINDING_NOT_FALSE" }
if ($kv["X108_MERGE"] -ne "false") { throw "X108_MERGE_NOT_FALSE" }
if ($kv["GRAPHITI_INDEX_WRITE"] -ne "false") { throw "GRAPHITI_INDEX_WRITE_NOT_FALSE" }
if ($kv["NEO4J_WRITE_EXECUTED"] -ne "false") { throw "NEO4J_WRITE_EXECUTED_NOT_FALSE" }
if ($kv["MEMORY_INTAKE"] -ne "false") { throw "MEMORY_INTAKE_NOT_FALSE" }

Write-Host "MEMORY_LAYER_AUTHORITY_MODEL_READONLY_V1_PASS"
