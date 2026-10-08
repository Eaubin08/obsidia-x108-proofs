# CSSA historical batch discovery — READ ONLY.
# Enumerates known user-local locations and optional additional roots.
# Never creates a historical fixture or mutates any source.
param(
  [string[]]$AdditionalRoots = @()
)
$ErrorActionPreference = "Stop"
$batchId = "84a929c6f48a90c5"
$roots = @(
  $env:LOCALAPPDATA,
  $env:APPDATA,
  "$env:USERPROFILE\Desktop",
  "$env:USERPROFILE\Documents",
  "$env:USERPROFILE\Downloads"
) + $AdditionalRoots
$roots = $roots | Where-Object { $_ -and (Test-Path -LiteralPath $_) } | Select-Object -Unique
$found = @()
foreach ($root in $roots) {
  Write-Host "SCAN_ROOT $root"
  try {
    $matches = Get-ChildItem -LiteralPath $root -Recurse -File -Filter 'batch_proposal.json' -ErrorAction SilentlyContinue |
      Where-Object { $_.DirectoryName -match [regex]::Escape($batchId) }
    foreach ($file in $matches) {
      $hash = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash
      $valid = $false
      $count = $null
      try {
        $payload = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
        $valid = ($payload.batch_id -eq $batchId)
        if ($null -ne $payload.selected_candidates) { $count = @($payload.selected_candidates).Count }
      } catch {}
      $found += [pscustomobject]@{
        Path = $file.FullName; SHA256 = $hash; BatchIdMatches = $valid; SelectedCandidateCount = $count
      }
    }
  } catch {
    Write-Warning "Cannot enumerate $root : $($_.Exception.Message)"
  }
}
if ($found.Count -eq 0) {
  Write-Host "HISTORICAL_FIXTURE_NOT_FOUND_IN_SCANNED_ROOTS"
} else {
  $found | Format-List
  Write-Host "HISTORICAL_FIXTURE_CANDIDATES_FOUND_REQUIRES_INTEGRITY_REVIEW"
}
# No copy, restoration, test approval, or execution is performed.
