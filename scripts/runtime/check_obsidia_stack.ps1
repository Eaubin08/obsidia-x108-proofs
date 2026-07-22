param(
  [string]$Repo = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B",
  [string]$ApiBase = "http://127.0.0.1:8000",
  [int]$LatestN = 50
)

$ErrorActionPreference = "Continue"

Set-Location $Repo
chcp 65001 | Out-Null
$env:PYTHONPATH = $Repo
$env:PYTHONIOENCODING = "utf-8"
$env:OBSIDIA_API_BASE = $ApiBase
$env:OBSIDIA_TERMINAL_COLOR = "1"

$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$AuditDir = ".local_audits\P3Q0C_HEALTHCHECK_$stamp"
New-Item -ItemType Directory -Force -Path $AuditDir | Out-Null

$checks = New-Object System.Collections.Generic.List[object]

function Add-Check {
  param([string]$Name, [bool]$Ok, [string]$Detail)

  $script:checks.Add([pscustomobject]@{
    name = $Name
    ok = $Ok
    detail = $Detail
  }) | Out-Null

  if ($Ok) {
    Write-Host "[OK]   $Name :: $Detail" -ForegroundColor Green
  } else {
    Write-Host "[FAIL] $Name :: $Detail" -ForegroundColor Red
  }
}

function Get-NestedValue {
  param([object]$Obj, [string[]]$Paths)

  foreach ($path in $Paths) {
    $cur = $Obj
    $ok = $true

    foreach ($key in $path.Split(".")) {
      if ($null -eq $cur) {
        $ok = $false
        break
      }

      $prop = $cur.PSObject.Properties[$key]
      if ($null -eq $prop) {
        $ok = $false
        break
      }

      $cur = $prop.Value
    }

    if ($ok) {
      return $cur
    }
  }

  return $null
}

Write-Host "`n=== P3Q0C — OBSIDIA STACK HEALTHCHECK NON BLOCKING ===" -ForegroundColor Cyan
Write-Host "Repo=$Repo"
Write-Host "ApiBase=$ApiBase"
Write-Host "LatestN=$LatestN"
Write-Host "AuditDir=$AuditDir"

Add-Check "repo_exists" (Test-Path $Repo) $Repo

$kernelProcs = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "server\.kernel\.sealed\.cjs" })
$apiProcs = @(Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match "apps\.obsidia_api\.main" })

Add-Check "kernel_process_exists" ($kernelProcs.Count -ge 1) "count=$($kernelProcs.Count)"
Add-Check "api_process_exists" ($apiProcs.Count -ge 1) "count=$($apiProcs.Count)"

Add-Check "kernel_process_not_duplicated" ($kernelProcs.Count -eq 1) "count=$($kernelProcs.Count)"
Add-Check "api_process_not_duplicated" ($apiProcs.Count -eq 1) "count=$($apiProcs.Count)"

$kernelProcs | Select-Object ProcessId, Name, CommandLine | Format-List | Out-File "$AuditDir\kernel_processes.txt" -Encoding utf8
$apiProcs | Select-Object ProcessId, Name, CommandLine | Format-List | Out-File "$AuditDir\api_processes.txt" -Encoding utf8

$port3001 = @(netstat -ano | Select-String ":3001")
$port8000 = @(netstat -ano | Select-String ":8000")

Add-Check "port_3001_open" ($port3001.Count -ge 1) "matches=$($port3001.Count)"
Add-Check "port_8000_open" ($port8000.Count -ge 1) "matches=$($port8000.Count)"

$port3001 | Out-File "$AuditDir\netstat_3001.txt" -Encoding utf8
$port8000 | Out-File "$AuditDir\netstat_8000.txt" -Encoding utf8

try {
  $openapi = Invoke-WebRequest "$ApiBase/openapi.json" -UseBasicParsing -TimeoutSec 5
  Add-Check "api_openapi" ($openapi.StatusCode -eq 200) "status=$($openapi.StatusCode)"
  $openapi.Content | Out-File "$AuditDir\openapi.json" -Encoding utf8
} catch {
  Add-Check "api_openapi" $false $_.Exception.Message
}

Write-Host "`n=== DECISION JSON HEALTHCHECK ===" -ForegroundColor Cyan

$allData = "runtime_terrain_bank_trading_gps\allData"
$decisionFiles = @(Get-ChildItem $allData -Filter "decision_*.json" -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime)
$latest = @($decisionFiles | Select-Object -Last $LatestN)

Add-Check "decision_files_exist" ($decisionFiles.Count -gt 0) "count=$($decisionFiles.Count)"
Add-Check "latest_decision_files" ($latest.Count -gt 0) "latest_count=$($latest.Count)"

$rows = New-Object System.Collections.Generic.List[object]

foreach ($file in $latest) {
  try {
    $data = Get-Content $file.FullName -Raw | ConvertFrom-Json

    $domain = Get-NestedValue $data @("domain", "domain_sigma_envelope.domain")
    $gate = Get-NestedValue $data @("x108_gate", "domain_sigma_envelope.x108_gate")
    $verdict = Get-NestedValue $data @("market_verdict", "domain_sigma_envelope.market_verdict")
    $raw = Get-NestedValue $data @("raw_engine", "domain_sigma_envelope.raw_engine")

    $consensus = $null
    $agentVoteDetails = $null
    $obs = $null

    if ($null -ne $raw) {
      $consensusProp = $raw.PSObject.Properties["consensus"]
      $agentProp = $raw.PSObject.Properties["agent_vote_details"]
      if ($null -ne $consensusProp) { $consensus = $consensusProp.Value }
      if ($null -ne $agentProp) { $agentVoteDetails = $agentProp.Value }
    }

    if ($null -ne $consensus) {
      $obsProp = $consensus.PSObject.Properties["observation_ratio"]
      if ($null -ne $obsProp) { $obs = $obsProp.Value }
    }

    $row = [pscustomobject]@{
      file = $file.Name
      domain = $domain
      gate = $gate
      verdict = $verdict
      has_consensus = ($null -ne $consensus)
      has_agent_vote_details = ($null -ne $agentVoteDetails)
      does_not_authorize_action = if ($null -ne $consensus -and $null -ne $consensus.PSObject.Properties["does_not_authorize_action"]) { $consensus.PSObject.Properties["does_not_authorize_action"].Value } else { $null }
      does_not_override_x108_gate = if ($null -ne $consensus -and $null -ne $consensus.PSObject.Properties["does_not_override_x108_gate"]) { $consensus.PSObject.Properties["does_not_override_x108_gate"].Value } else { $null }
      observation_authority = if ($null -ne $obs -and $null -ne $obs.PSObject.Properties["authority"]) { $obs.PSObject.Properties["authority"].Value } else { $null }
      observation_display_only = if ($null -ne $obs -and $null -ne $obs.PSObject.Properties["display_only"]) { $obs.PSObject.Properties["display_only"].Value } else { $null }
      formal_result_status = if ($null -ne $consensus -and $null -ne $consensus.PSObject.Properties["formal_result_status"]) { $consensus.PSObject.Properties["formal_result_status"].Value } else { $null }
      consensus_authority = if ($null -ne $consensus -and $null -ne $consensus.PSObject.Properties["authority"]) { $consensus.PSObject.Properties["authority"].Value } else { $null }
    }

    $rows.Add($row) | Out-Null
  } catch {
    $rows.Add([pscustomobject]@{
      file = $file.Name
      parse_error = $_.Exception.Message
    }) | Out-Null
  }
}

$rows | ConvertTo-Json -Depth 8 | Out-File "$AuditDir\P3Q0C_decision_rows.json" -Encoding utf8

$validRows = @($rows | Where-Object { -not $_.PSObject.Properties["parse_error"] })
$domains = @($validRows | Group-Object domain | ForEach-Object { "$($_.Name)=$($_.Count)" })
$gates = @($validRows | Group-Object gate | ForEach-Object { "$($_.Name)=$($_.Count)" })

Add-Check "latest_parse_ok" ($validRows.Count -eq $latest.Count) "valid=$($validRows.Count)/$($latest.Count)"
Add-Check "latest_have_consensus" (@($validRows | Where-Object { $_.has_consensus -eq $true }).Count -eq $validRows.Count) "latest=$($validRows.Count)"
Add-Check "latest_have_agent_vote_details" (@($validRows | Where-Object { $_.has_agent_vote_details -eq $true }).Count -eq $validRows.Count) "latest=$($validRows.Count)"
Add-Check "latest_consensus_non_authorizing" (@($validRows | Where-Object { $_.does_not_authorize_action -eq $true }).Count -eq $validRows.Count) "latest=$($validRows.Count)"
Add-Check "latest_consensus_no_gate_override" (@($validRows | Where-Object { $_.does_not_override_x108_gate -eq $true }).Count -eq $validRows.Count) "latest=$($validRows.Count)"
Add-Check "latest_observation_authority_none" (@($validRows | Where-Object { $_.observation_authority -eq "NONE" }).Count -eq $validRows.Count) "latest=$($validRows.Count)"
Add-Check "latest_observation_display_only" (@($validRows | Where-Object { $_.observation_display_only -eq $true }).Count -eq $validRows.Count) "latest=$($validRows.Count)"

Write-Host "`nDomains: $($domains -join ', ')" -ForegroundColor Cyan
Write-Host "Gates: $($gates -join ', ')" -ForegroundColor Cyan

$failed = @($checks | Where-Object { $_.ok -ne $true })
$status = if ($failed.Count -eq 0) { "PASS" } else { "FAIL" }

$summary = [pscustomobject]@{
  status = $status
  failed_count = $failed.Count
  total_checks = $checks.Count
  audit_dir = $AuditDir
  domains = $domains
  gates = $gates
  checks = $checks
}

$summary | ConvertTo-Json -Depth 8 | Out-File "$AuditDir\P3Q0C_healthcheck_summary.json" -Encoding utf8

Write-Host "`n=== P3Q0C FINAL STATUS ===" -ForegroundColor Cyan

if ($status -eq "PASS") {
  Write-Host "STATUS=P3Q0C_HEALTHCHECK_PASS" -ForegroundColor Green
} else {
  Write-Host "STATUS=P3Q0C_HEALTHCHECK_FAIL" -ForegroundColor Red
  $failed | Format-Table -AutoSize
}

Write-Host "AUDIT_DIR=$AuditDir" -ForegroundColor Green
