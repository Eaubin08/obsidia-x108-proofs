param(
  [string]$BankRoboSrc = "",
  [string]$EnvFile = "",
  [int]$PreferredPort = 3018
)

$ErrorActionPreference = "Stop"

function Save-Utf8NoBom([string]$Path, [string]$Content) {
  $dir = Split-Path $Path -Parent
  if ($dir) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  $enc = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $enc)
}

function Get-EnvMap([string]$Path) {
  $map = @{}
  if (-not (Test-Path $Path)) { return $map }
  foreach ($line in Get-Content $Path) {
    if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
      $map[$matches[1]] = $matches[2].Trim().Trim('"').Trim("'")
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

function Invoke-UrlProbe([string]$url) {
  try {
    if ($url -match 'processTransaction$') {
      $resp = Invoke-WebRequest -UseBasicParsing -Method POST -Uri $url -ContentType "application/json" -Body '{"json":{}}' -TimeoutSec 10
    } else {
      $resp = Invoke-WebRequest -UseBasicParsing -Method GET -Uri $url -TimeoutSec 10
    }
    $body = [string]$resp.Content
    return [pscustomobject]@{
      url = $url
      ok = $true
      status_code = [int]$resp.StatusCode
      body_head = $body.Substring(0, [Math]::Min(300, $body.Length))
    }
  } catch {
    return [pscustomobject]@{
      url = $url
      ok = $false
      error = $_.Exception.Message
    }
  }
}

function Start-Case([string]$Name, [hashtable]$BaseEnv, [hashtable]$Overrides, [int]$Port, [string]$BankRoboSrc, [string]$RunDir) {
  $stdout = Join-Path $RunDir "$Name.stdout.log"
  $stderr = Join-Path $RunDir "$Name.stderr.log"

  $envMap = @{}
  foreach ($k in $BaseEnv.Keys) { $envMap[$k] = $BaseEnv[$k] }
  foreach ($k in $Overrides.Keys) {
    if ($null -eq $Overrides[$k]) { $envMap.Remove($k) | Out-Null }
    else { $envMap[$k] = $Overrides[$k] }
  }

  $holder = $null
  if ($Name -eq "PORT_OCCUPIED") {
    $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Loopback, $Port)
    $listener.Start()
    $holder = $listener
  }

  $envLines = @("`$env:NODE_ENV = 'development'","`$env:PORT = '$Port'")
  foreach ($k in @("DATABASE_URL","GEMINI_API_KEY","OAUTH_SERVER_URL","JWT_SECRET","OWNER_OPEN_ID","VITE_APP_ID")) {
    if ($envMap.ContainsKey($k) -and -not [string]::IsNullOrWhiteSpace($envMap[$k])) {
      $envLines += "`$env:$k = '$($envMap[$k].Replace("'", "''"))'"
    }
  }

  $boot = @"
Set-Location '$BankRoboSrc'
$($envLines -join "`r`n")
pnpm exec tsx server/_core/index.ts
"@

  $proc = Start-Process powershell.exe `
    -ArgumentList "-NoProfile","-ExecutionPolicy","Bypass","-Command",$boot `
    -RedirectStandardOutput $stdout `
    -RedirectStandardError $stderr `
    -PassThru

  Start-Sleep -Seconds 10

  $proc.Refresh()

  $stdoutText = ""
  $stderrText = ""
  if (Test-Path $stdout) { $stdoutText = Get-Content $stdout -Raw -ErrorAction SilentlyContinue }
  if (Test-Path $stderr) { $stderrText = Get-Content $stderr -Raw -ErrorAction SilentlyContinue }

  $actualPort = $null
  if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
    $m = [regex]::Match($stdoutText, 'Server running on http://localhost:(\d+)/')
    if ($m.Success) { $actualPort = [int]$m.Groups[1].Value }
  }

  $portsToProbe = @($actualPort, $Port) | Where-Object { $_ } | Select-Object -Unique
  $probe = @()
  foreach ($p in $portsToProbe) {
    $probe += Invoke-UrlProbe "http://localhost:$p/"
    $probe += Invoke-UrlProbe "http://localhost:$p/api/trpc/banking.processTransaction"
    $probe += Invoke-UrlProbe ("http://localhost:$p/api/trpc/banking.getRecentTransactions?input=" + [System.Uri]::EscapeDataString('{"json":{"limit":1}}'))
  }

  $processProbe = $probe | Where-Object { $_.url -match 'processTransaction$' } | Select-Object -First 1
  $recentProbe = $probe | Where-Object { $_.url -match 'getRecentTransactions' } | Select-Object -First 1

  $bootStatus = if ($actualPort -and $actualPort -eq $Port) {
    "BOOT_ON_PREFERRED_PORT"
  } elseif ($actualPort -and $actualPort -ne $Port) {
    "BOOT_ON_FALLBACK_PORT"
  } else {
    "BOOT_FAILED"
  }

  if (-not $proc.HasExited) {
    Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
  }
  if ($holder) { $holder.Stop() }

  return [pscustomobject]@{
    case = $Name
    process_id = $proc.Id
    has_exited = $proc.HasExited
    preferred_port = $Port
    parsed_port = $actualPort
    boot_status = $bootStatus
    fallback_port_used = [bool]($actualPort -and ($actualPort -ne $Port))
    stdout_log = $stdout
    stderr_log = $stderr
    stdout_length = $stdoutText.Length
    stderr_length = $stderrText.Length
    stdout_has_server_running = ($stdoutText -match 'Server running on http://localhost:')
    stderr_nonempty = -not [string]::IsNullOrWhiteSpace($stderrText)
    process_route_reachable = [bool]($processProbe -and $processProbe.ok)
    recent_route_reachable = [bool]($recentProbe -and $recentProbe.ok)
    http_probe = @($probe)
  }
}

$Repo = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
if ([string]::IsNullOrWhiteSpace($BankRoboSrc)) {
  $BankRoboSrc = Join-Path $Repo ".cache\upstream\bank-robo-src"
}
if ([string]::IsNullOrWhiteSpace($EnvFile)) {
  $EnvFile = Find-EnvFile -BankRoboSrc $BankRoboSrc -Repo $Repo
}
if (-not $EnvFile) {
  throw "No env file found with DATABASE_URL"
}

$baseEnv = Get-EnvMap $EnvFile

$Stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$RunDir = Join-Path $Repo "artifacts\bank_robo_real\fault_injection\$Stamp"
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$cases = @(
  @{ Name = "DB_MISSING_ENV"; Overrides = @{ DATABASE_URL = $null } },
  @{ Name = "DB_INVALID_URL"; Overrides = @{ DATABASE_URL = "mysql://invalid:invalid@127.0.0.1:65099/invalid" } },
  @{ Name = "OAUTH_MISSING"; Overrides = @{ OAUTH_SERVER_URL = $null } },
  @{ Name = "GEMINI_MISSING"; Overrides = @{ GEMINI_API_KEY = $null } },
  @{ Name = "PORT_OCCUPIED"; Overrides = @{} }
)

$results = @()
foreach ($c in $cases) {
  $results += Start-Case -Name $c.Name -BaseEnv $baseEnv -Overrides $c.Overrides -Port $PreferredPort -BankRoboSrc $BankRoboSrc -RunDir $RunDir
}

$summary = [ordered]@{
  status = "ok"
  run_dir = $RunDir
  env_file = $EnvFile
  bank_robo_src = $BankRoboSrc
  cases = @($results)
}

$SummaryPath = Join-Path $RunDir "fault_injection_summary.json"
$RowsPath = Join-Path $RunDir "fault_injection_rows.jsonl"
($results | ForEach-Object { $_ | ConvertTo-Json -Depth 20 -Compress }) -join "`n" | Set-Content -Encoding UTF8 $RowsPath
$summary | ConvertTo-Json -Depth 20 | Set-Content -Encoding UTF8 $SummaryPath

Write-Host ""
Write-Host "===== BANK-ROBO FAULT INJECTION READY ====="
Write-Host "RunDir:   $RunDir"
Write-Host "Summary:  $SummaryPath"
Write-Host ""
Get-Content $SummaryPath