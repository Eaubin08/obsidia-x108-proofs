param(
  [string]$BankRoboSrc = "",
  [string]$EnvFile = "",
  [int]$PreferredPort = 3018,
  [int]$Count = 10,
  [int]$RecentLimit = 50,
  [int]$PauseMs = 250,
  [string]$ScenarioName = "",
  [switch]$KeepServer,
  [int]$RecentRetryCount = 5,
  [int]$RecentRetryDelayMs = 350,
  [string]$BaseUrl = "",
  [switch]$UseExistingServer
)

$ErrorActionPreference = "Stop"

function Convert-ToPlain($obj) {
  if ($null -eq $obj) { return $null }

  if (
    $obj -is [string] -or
    $obj -is [int] -or
    $obj -is [long] -or
    $obj -is [double] -or
    $obj -is [decimal] -or
    $obj -is [bool] -or
    $obj -is [DateTime]
  ) {
    return $obj
  }

  if ($obj -is [System.Collections.IDictionary]) {
    $h = [ordered]@{}
    foreach ($k in $obj.Keys) {
      $h[$k] = Convert-ToPlain $obj[$k]
    }
    return $h
  }

  if ($obj -is [System.Collections.IEnumerable] -and -not ($obj -is [string])) {
    $arr = @()
    foreach ($x in $obj) {
      $arr += ,(Convert-ToPlain $x)
    }
    return $arr
  }

  $props = @($obj.PSObject.Properties)
  if ($props.Count -gt 0) {
    $h = [ordered]@{}
    foreach ($p in $props) {
      $h[$p.Name] = Convert-ToPlain $p.Value
    }
    return $h
  }

  return $obj
}

function Get-TrpcJson($obj) {
  if ($null -eq $obj) { return $null }

  try {
    if ($obj.result -and $obj.result.data -and $null -ne $obj.result.data.json) { return $obj.result.data.json }
    if ($obj.result -and $null -ne $obj.result.json) { return $obj.result.json }
    if ($null -ne $obj.json) { return $obj.json }
    return $obj
  } catch {
    return $obj
  }
}

function Extract-RecentRows($payload) {
  if ($null -eq $payload) { return @() }

  if ($payload -is [System.Array]) { return @($payload) }

  try {
    if ($payload.result -and $payload.result.data -and $null -ne $payload.result.data.json) {
      if ($payload.result.data.json -is [System.Array]) { return @($payload.result.data.json) }
    }
    if ($payload.result -and $null -ne $payload.result.json) {
      if ($payload.result.json -is [System.Array]) { return @($payload.result.json) }
    }
    if ($null -ne $payload.json) {
      if ($payload.json -is [System.Array]) { return @($payload.json) }
    }
    if ($null -ne $payload.data) {
      if ($payload.data -is [System.Array]) { return @($payload.data) }
    }
    if ($null -ne $payload.rows) {
      if ($payload.rows -is [System.Array]) { return @($payload.rows) }
    }
  } catch {}

  return @()
}

function Get-EnvMap([string]$Path) {
  $map = @{}
  if (-not (Test-Path $Path)) { return $map }

  foreach ($line in Get-Content $Path) {
    if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
      $k = $matches[1]
      $v = $matches[2].Trim().Trim('"').Trim("'")
      $map[$k] = $v
    }
  }

  return $map
}

function Find-EnvFile([string]$BankRoboSrc, [string]$Repo) {
  $candidates = @(
    (Join-Path $Repo "tools\bank_robo_real\local_env\.env.bank_robo.local"),
    (Join-Path $BankRoboSrc ".env.local"),
    (Join-Path $BankRoboSrc ".env"),
    (Join-Path $BankRoboSrc ".env.production"),
    (Join-Path $BankRoboSrc ".env.development"),
    (Join-Path (Split-Path $Repo -Parent) "Back-end-local\.env.local"),
    (Join-Path (Split-Path $Repo -Parent) "Back-end-local\.env")
  ) | Select-Object -Unique

  foreach ($f in $candidates) {
    if (Test-Path $f) {
      $raw = Get-Content $f -Raw -ErrorAction SilentlyContinue
      if ($raw -match '^\s*DATABASE_URL\s*=') { return $f }
    }
  }

  return $null
}

function Normalize-BaseUrl([string]$Url) {
  if ([string]::IsNullOrWhiteSpace($Url)) { return $null }
  return $Url.Trim().TrimEnd('/')
}

function Get-PortFromBaseUrl([string]$Url) {
  try {
    $uri = [Uri]$Url
    if ($uri.IsDefaultPort) {
      if ($uri.Scheme -eq "https") { return 443 }
      return 80
    }
    return [int]$uri.Port
  } catch {
    return $null
  }
}

function Start-BankRoboProcess([string]$BankRoboSrc, [hashtable]$envMap, [int]$PreferredPort, [string]$StdOutLog, [string]$StdErrLog) {
  $envLines = @(
    "`$env:NODE_ENV = 'development'",
    "`$env:PORT = '$PreferredPort'"
  )

  foreach ($k in @("DATABASE_URL","GEMINI_API_KEY","OAUTH_SERVER_URL","JWT_SECRET","OWNER_OPEN_ID","VITE_APP_ID")) {
    if ($envMap.ContainsKey($k) -and -not [string]::IsNullOrWhiteSpace($envMap[$k])) {
      $escaped = $envMap[$k].Replace("'", "''")
      $envLines += "`$env:$k = '$escaped'"
    }
  }

  $boot = @"
Set-Location '$BankRoboSrc'
$($envLines -join "`r`n")
pnpm exec tsx server/_core/index.ts
"@

  $proc = Start-Process powershell.exe `
    -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-Command",$boot `
    -RedirectStandardOutput $StdOutLog `
    -RedirectStandardError $StdErrLog `
    -PassThru

  return $proc
}

function Wait-BankRoboReady([System.Diagnostics.Process]$proc, [string]$StdOutLog, [string]$StdErrLog) {
  $actualPort = $null
  $stdoutText = ""
  $stderrText = ""

  1..40 | ForEach-Object {
    Start-Sleep -Seconds 2

    if (Test-Path $StdOutLog) {
      $tmp = Get-Content $StdOutLog -Raw -ErrorAction SilentlyContinue
      if ($null -ne $tmp) { $stdoutText = [string]$tmp }

      if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
        $m = [regex]::Match($stdoutText, 'Server running on http://localhost:(\d+)/')
        if ($m.Success) {
          $actualPort = [int]$m.Groups[1].Value
          return
        }
      }
    }

    if (Test-Path $StdErrLog) {
      $tmp = Get-Content $StdErrLog -Raw -ErrorAction SilentlyContinue
      if ($null -ne $tmp) { $stderrText = [string]$tmp }
    }

    if ($proc.HasExited) { return }
  }

  return [pscustomobject]@{
    ActualPort = $actualPort
    StdOut = $stdoutText
    StdErr = $stderrText
  }
}

function Wait-ExistingServerReady([string]$BaseUrl, [int]$Attempts = 20, [int]$DelayMs = 1000) {
  $probeUrl = $BaseUrl + "/api/trpc/banking.getRecentTransactions?input=" + [System.Uri]::EscapeDataString('{"json":{"limit":1}}')
  $lastError = $null

  for ($attempt = 1; $attempt -le $Attempts; $attempt++) {
    try {
      $resp = Invoke-RestMethod -Method GET -Uri $probeUrl -TimeoutSec 15
      return [pscustomobject]@{
        ok = $true
        attempts = $attempt
        probe_url = $probeUrl
        payload = (Convert-ToPlain $resp)
      }
    } catch {
      $lastError = $_.Exception.Message
      if ($attempt -lt $Attempts) {
        Start-Sleep -Milliseconds $DelayMs
      }
    }
  }

  return [pscustomobject]@{
    ok = $false
    attempts = $Attempts
    probe_url = $probeUrl
    error = $lastError
  }
}

function Invoke-RecentWithRetry([string]$RecentUrl, [int]$MaxAttempts, [int]$DelayMs) {
  $lastErr = $null
  $lastRaw = $null
  $lastJson = $null
  $lastCount = 0

  for ($attempt = 1; $attempt -le $MaxAttempts; $attempt++) {
    try {
      $resp = Invoke-RestMethod -Method GET -Uri $RecentUrl -TimeoutSec 30
      $lastRaw = Convert-ToPlain $resp
      $lastJson = Convert-ToPlain (Get-TrpcJson $resp)
      $rows = @(Extract-RecentRows $resp)
      $lastCount = $rows.Count

      if ($rows.Count -gt 0) {
        return [pscustomobject]@{
          ok = $true
          error = $null
          raw = $lastRaw
          json = $lastJson
          attempts = $attempt
          row_count = $rows.Count
        }
      }

      if ($attempt -lt $MaxAttempts) {
        Start-Sleep -Milliseconds $DelayMs
      }
    } catch {
      $lastErr = $_.Exception.Message
      if ($attempt -lt $MaxAttempts) {
        Start-Sleep -Milliseconds $DelayMs
      }
    }
  }

  return [pscustomobject]@{
    ok = $false
    error = $(if ($lastErr) { $lastErr } else { "recent returned empty after retries" })
    raw = $lastRaw
    json = $lastJson
    attempts = $MaxAttempts
    row_count = $lastCount
  }
}

$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent

if ([string]::IsNullOrWhiteSpace($BankRoboSrc)) {
  $BankRoboSrc = Join-Path $Repo ".cache\upstream\bank-robo-src"
}
if (-not (Test-Path $BankRoboSrc)) {
  throw "BankRoboSrc not found: $BankRoboSrc"
}

if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $EnvFile = Find-EnvFile -BankRoboSrc $BankRoboSrc -Repo $Repo
}
$envMap = @{}
if ($EnvFile) { $envMap = Get-EnvMap $EnvFile }

$UseExisting = $UseExistingServer -or -not [string]::IsNullOrWhiteSpace($BaseUrl)
if ($UseExisting -and [string]::IsNullOrWhiteSpace($BaseUrl)) {
  $BaseUrl = "http://localhost:$PreferredPort"
}
$BaseUrl = Normalize-BaseUrl $BaseUrl

$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$RunDir = Join-Path $Repo "artifacts\bank_robo_real\batch_probe\$Stamp"
$StdOutLog = $null
$StdErrLog = $null
$RowsJsonl = Join-Path $RunDir "batch_probe_rows.jsonl"
$SummaryJson = Join-Path $RunDir "batch_probe_summary.json"
$MetaJson = Join-Path $RunDir "meta.json"

New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$proc = $null
$actualPort = $null
$mode = $(if ($UseExisting) { "existing_server" } else { "managed_server" })
$existingReady = $null

if ($UseExisting) {
  $existingReady = Wait-ExistingServerReady -BaseUrl $BaseUrl -Attempts 20 -DelayMs 1000
  if (-not $existingReady.ok) {
    [ordered]@{
      status = "existing_server_not_ready"
      mode = $mode
      base_url = $BaseUrl
      preferred_port = $PreferredPort
      env_file = $EnvFile
      bank_robo_src = $BankRoboSrc
      readiness_probe = $existingReady
    } | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 $MetaJson

    throw "existing server not ready at $BaseUrl"
  }

  $actualPort = Get-PortFromBaseUrl $BaseUrl
} else {
  $StdOutLog = Join-Path $RunDir "server_stdout.log"
  $StdErrLog = Join-Path $RunDir "server_stderr.log"

  $stale = Get-NetTCPConnection -LocalPort $PreferredPort -State Listen -ErrorAction SilentlyContinue
  if ($stale) {
    $procIds = $stale | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($procId in $procIds) {
      Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
  }

  $proc = Start-BankRoboProcess -BankRoboSrc $BankRoboSrc -envMap $envMap -PreferredPort $PreferredPort -StdOutLog $StdOutLog -StdErrLog $StdErrLog
  $ready = Wait-BankRoboReady -proc $proc -StdOutLog $StdOutLog -StdErrLog $StdErrLog

  if (-not $ready.ActualPort) {
    [ordered]@{
      status = "boot_failed"
      mode = $mode
      bank_robo_src = $BankRoboSrc
      env_file = $EnvFile
      preferred_port = $PreferredPort
      stdout_log = $StdOutLog
      stderr_log = $StdErrLog
      stdout_length = $ready.StdOut.Length
      stderr_length = $ready.StdErr.Length
      process_id = $proc.Id
      has_exited = $proc.HasExited
    } | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 $MetaJson

    throw "bank-robo did not become ready. Inspect: $StdOutLog / $StdErrLog"
  }

  $actualPort = $ready.ActualPort
  $BaseUrl = "http://localhost:$actualPort"
}

$ProcessUrl = "$BaseUrl/api/trpc/banking.processTransaction"
$RecentUrlBase = "$BaseUrl/api/trpc/banking.getRecentTransactions"

$rows = @()

for ($i = 1; $i -le $Count; $i++) {
  $reqTs = (Get-Date).ToString("o")

  $body = if ([string]::IsNullOrWhiteSpace($ScenarioName)) {
    '{"json":{}}'
  } else {
    '{"json":{"scenarioName":"' + $ScenarioName.Replace('"','\"') + '"}}'
  }

  $processOk = $true
  $processRaw = $null
  $processJson = $null
  $processErr = $null

  try {
    $resp = Invoke-RestMethod -Method POST -Uri $ProcessUrl -ContentType "application/json" -Body $body -TimeoutSec 30
    $processRaw = Convert-ToPlain $resp
    $processJson = Convert-ToPlain (Get-TrpcJson $resp)
  } catch {
    $processOk = $false
    $processErr = $_.Exception.Message
  }

  Start-Sleep -Milliseconds $PauseMs

  $recentUrl = $RecentUrlBase + "?input=" + [System.Uri]::EscapeDataString("{""json"":{""limit"":$RecentLimit}}")
  $recentResult = Invoke-RecentWithRetry -RecentUrl $recentUrl -MaxAttempts $RecentRetryCount -DelayMs $RecentRetryDelayMs

  $row = [ordered]@{
    request_index = $i
    requested_at = $reqTs

    process_ok = $processOk
    process_error = $processErr

    recent_ok = $recentResult.ok
    recent_error = $recentResult.error
    recent_attempts = $recentResult.attempts
    recent_row_count = $recentResult.row_count

    scenario_name = $(if ($processJson -and $processJson.scenario) { $processJson.scenario.name } else { $null })
    decision = $(if ($processJson) { $processJson.decision } else { $null })
    reason = $(if ($processJson) { $processJson.reason } else { $null })
    metrics = $(if ($processJson) { $processJson.metrics } else { $null })
    ontological_tests = $(if ($processJson) { $processJson.ontologicalTests } else { $null })
    roi_contribution = $(if ($processJson) { $processJson.roiContribution } else { $null })

    process_raw = $processRaw
    process_json = $processJson
    recent_raw = $recentResult.raw
    recent_json = $recentResult.json
  }

  $rows += [pscustomobject]$row
}

$summary = [ordered]@{
  status = "ok"
  mode = $mode
  using_existing_server = $UseExisting
  base_url = $BaseUrl
  bank_robo_src = $BankRoboSrc
  env_file = $EnvFile
  preferred_port = $PreferredPort
  actual_port = $actualPort
  process_id = $(if ($proc) { $proc.Id } else { $null })
  count = $Count
  recent_limit = $RecentLimit
  recent_retry_count = $RecentRetryCount
  recent_retry_delay_ms = $RecentRetryDelayMs
  process_ok_count = @($rows | Where-Object { $_.process_ok }).Count
  process_error_count = @($rows | Where-Object { -not $_.process_ok }).Count
  recent_ok_count = @($rows | Where-Object { $_.recent_ok }).Count
  recent_error_count = @($rows | Where-Object { -not $_.recent_ok }).Count
  recent_route_available = (@($rows | Where-Object { $_.recent_ok }).Count -gt 0)
  decisions = @{}
  rows_jsonl = $RowsJsonl
  summary_json = $SummaryJson
  meta_json = $MetaJson
  stdout_log = $StdOutLog
  stderr_log = $StdErrLog
}

foreach ($g in ($rows | Where-Object { $_.decision } | Group-Object decision)) {
  $summary.decisions[$g.Name] = $g.Count
}

($rows | ForEach-Object { $_ | ConvertTo-Json -Depth 40 -Compress }) -join "`n" | Set-Content -Encoding UTF8 $RowsJsonl
$summary | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 $SummaryJson

[ordered]@{
  status = "ok"
  mode = $mode
  using_existing_server = $UseExisting
  base_url = $BaseUrl
  bank_robo_src = $BankRoboSrc
  env_file = $EnvFile
  preferred_port = $PreferredPort
  actual_port = $actualPort
  process_id = $(if ($proc) { $proc.Id } else { $null })
  stdout_log = $StdOutLog
  stderr_log = $StdErrLog
  readiness_probe = $existingReady
  rows_jsonl = $RowsJsonl
  summary_json = $SummaryJson
  created_at = (Get-Date).ToString("o")
} | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 $MetaJson

if (-not $UseExisting -and -not $KeepServer -and $proc) {
  Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "===== BANK-ROBO BATCH PROBE READY ====="
Write-Host "Mode:        $mode"
Write-Host "BaseUrl:     $BaseUrl"
Write-Host "RunDir:      $RunDir"
Write-Host "Rows:        $RowsJsonl"
Write-Host "Summary:     $SummaryJson"
Write-Host "Meta:        $MetaJson"
Write-Host "Actual port: $actualPort"
Write-Host ""
Get-Content $SummaryJson