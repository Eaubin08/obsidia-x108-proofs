param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

$ptr = Join-Path $Root "CURRENT_BRODY_NATIVE_TERMINAL_DETECTOR_PATCH_V1_VALIDATE.txt"

if (!(Test-Path $ptr)) {
  throw "MISSING_DETECTOR_PATCH_VALIDATE_POINTER=$ptr"
}

$kv = @{}
Get-Content $ptr | ForEach-Object {
  if ($_ -match "^\s*([^=]+)=(.*)$") {
    $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
  }
}

if ($kv["STATUS"] -ne "BRODY_NATIVE_TERMINAL_DETECTOR_PATCH_V1_PASS") {
  throw "BAD_DETECTOR_PATCH_STATUS=$($kv["STATUS"])"
}

if ($kv["DETECTOR_OK"] -ne "True") {
  throw "DETECTOR_OK_NOT_TRUE"
}

if ($kv["BAD_NO_CRITICAL_PRESSURE_DETECTED"] -ne "False") {
  throw "BAD_NO_CRITICAL_PRESSURE_DETECTED_NOT_FALSE"
}

if ($kv["BOUNDARY_OK"] -ne "True") {
  throw "BOUNDARY_OK_NOT_TRUE"
}

Write-Host "BRODY_NATIVE_TERMINAL_DETECTOR_PATCH_READONLY_V1_PASS"
