param(
  [string]$Root = "C:\Users\User\Desktop\obsidia-engine-proof-core"
)

$ErrorActionPreference = "Stop"

function Read-KvFile {
  param([string]$Path)

  if (!(Test-Path $Path)) {
    throw "MISSING_KV_FILE=$Path"
  }

  $kv = @{}
  Get-Content $Path | ForEach-Object {
    if ($_ -match "^\s*([^=]+)=(.*)$") {
      $kv[$matches[1].Trim([char]0xFEFF).Trim()] = $matches[2].Trim()
    }
  }

  return $kv
}

$x108 = Join-Path $Root "obsidia-x108-proofs"
$candidate = Join-Path $Root "obsidia-engine-candidate"

$inventoryPtr = Join-Path $x108 "CURRENT_BRODY_API_BRIDGE_CANDIDATE_COMPONENTS_INVENTORY_READONLY.txt"
$kv = Read-KvFile -Path $inventoryPtr

if ($kv["STATUS"] -ne "BRODY_API_BRIDGE_CANDIDATE_COMPONENTS_INVENTORY_READONLY_V1_PASS") {
  throw "BAD_INVENTORY_STATUS=$($kv["STATUS"])"
}

$inventoryJson = $kv["SOURCE_INVENTORY_JSON"]
if (!(Test-Path $inventoryJson)) {
  throw "MISSING_SOURCE_INVENTORY_JSON=$inventoryJson"
}

$inventory = Get-Content $inventoryJson -Raw | ConvertFrom-Json

$items = @()
if ($null -ne $inventory.files) {
  $items = @($inventory.files)
}
elseif ($null -ne $inventory.records) {
  $items = @($inventory.records)
}
elseif ($inventory -is [System.Array]) {
  $items = @($inventory)
}
else {
  throw "UNSUPPORTED_INVENTORY_SCHEMA=$inventoryJson"
}

if ($items.Count -lt 1) {
  throw "EMPTY_INVENTORY=$inventoryJson"
}

$drift = @()
$checked = 0

foreach ($it in $items) {
  $expectedSha = ""
  if ($null -ne $it.sha256) { $expectedSha = [string]$it.sha256 }
  elseif ($null -ne $it.SHA256) { $expectedSha = [string]$it.SHA256 }

  $rel = ""
  if ($null -ne $it.relative_path) { $rel = [string]$it.relative_path }
  elseif ($null -ne $it.path) { $rel = [string]$it.path }
  elseif ($null -ne $it.Path) { $rel = [string]$it.Path }

  $full = ""
  if ($null -ne $it.full_path) { $full = [string]$it.full_path }
  elseif ($null -ne $it.FullName) { $full = [string]$it.FullName }
  elseif ($rel) { $full = Join-Path $candidate $rel }

  if ([string]::IsNullOrWhiteSpace($expectedSha)) {
    $drift += [ordered]@{
      type = "MISSING_EXPECTED_SHA256"
      relative_path = $rel
      full_path = $full
      expected_sha256 = $null
      actual_sha256 = $null
    }
    continue
  }

  if ([string]::IsNullOrWhiteSpace($full)) {
    $drift += [ordered]@{
      type = "MISSING_FULL_PATH"
      relative_path = $rel
      full_path = $null
      expected_sha256 = $expectedSha
      actual_sha256 = $null
    }
    continue
  }

  if (!(Test-Path $full)) {
    $drift += [ordered]@{
      type = "MISSING_FILE"
      relative_path = $rel
      full_path = $full
      expected_sha256 = $expectedSha
      actual_sha256 = $null
    }
    continue
  }

  $actualSha = (Get-FileHash $full -Algorithm SHA256).Hash
  $checked++

  if ($actualSha -ne $expectedSha) {
    $drift += [ordered]@{
      type = "HASH_CHANGED"
      relative_path = $rel
      full_path = $full
      expected_sha256 = $expectedSha
      actual_sha256 = $actualSha
    }
  }
}

if ($drift.Count -gt 0) {
  Write-Host "BRODY_API_BRIDGE_LIVE_DRIFT_GUARD_READONLY_V1_WARN"
  $drift | ConvertTo-Json -Depth 20
  throw "LIVE_DRIFT_DETECTED_COUNT=$($drift.Count)"
}

Write-Host "BRODY_API_BRIDGE_LIVE_DRIFT_GUARD_READONLY_V1_PASS"
Write-Host "CHECKED_FILE_COUNT=$checked"
Write-Host "DRIFT_COUNT=0"
Write-Host "DECISION_AUTHORITY=KX108_ONLY"
Write-Host "RUNTIME_ENABLED=false"
Write-Host "EXTERNAL_ACCESS_ENABLED=false"
Write-Host "X108_RUNTIME_BINDING=false"
Write-Host "X108_MERGE=false"
