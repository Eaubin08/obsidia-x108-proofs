param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"
$x108 = Join-Path $Root "obsidia-x108-proofs"

$required = @(
  "CURRENT_BRODY_RUNTIME_FREEZE_V1_4_12A_READONLY.txt",
  "CURRENT_BRODY_NATIVE_TERMINAL_SESSION_TEST_READONLY.txt",
  "CURRENT_BRODY_NATIVE_TERMINAL_DETECTOR_PATCH_READONLY.txt",
  "CURRENT_MEMORY_LAYER_AUTHORITY_MODEL_READONLY.txt"
)

foreach ($p in $required) {
  $full = Join-Path $x108 $p
  if (!(Test-Path $full)) {
    throw "MISSING_FREEZE_POINTER=$full"
  }
}

$memPtr = Join-Path $x108 "CURRENT_MEMORY_LAYER_AUTHORITY_MODEL_READONLY.txt"
$memRaw = Get-Content $memPtr -Raw

if ($memRaw -notmatch "MEMORY_LAYER_AUTHORITY_MODEL_READONLY") {
  throw "MEMORY_AUTHORITY_MODEL_POINTER_INVALID"
}

if ($memRaw -notmatch "DECISION_AUTHORITY=KX108_ONLY") {
  throw "KX108_AUTHORITY_NOT_CONFIRMED"
}

if ($memRaw -notmatch "MEMORY_DECISION=false") {
  throw "MEMORY_DECISION_NOT_FALSE"
}

if ($memRaw -notmatch "ALLOWED_TO_DECIDE=false") {
  throw "ALLOWED_TO_DECIDE_NOT_FALSE"
}

Write-Host "BRODY_X108_PROOF_STATE_FREEZE_V1_PASS"
