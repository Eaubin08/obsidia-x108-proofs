param(
  [Parameter(Mandatory=$true)][string]$RepoPath,
  [Parameter(Mandatory=$true)][string]$EnvFile,
  [int]$PreferredPort = 3018,
  [int]$WaitSeconds = 15
)

$ErrorActionPreference = "Stop"

$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$RunDir = Join-Path $RepoPath ("artifacts_runtime_autopsy_" + (Get-Date -Format "yyyyMMdd-HHmmss"))
New-Item -ItemType Directory -Force -Path $RunDir | Out-Null

$StdOutPath = Join-Path $RunDir "stdout.txt"
$StdErrPath = Join-Path $RunDir "stderr.txt"
$ProbePath  = Join-Path $RunDir "probe.json"

$job = Start-Job -ArgumentList $RepoPath, $EnvFile, $PreferredPort -ScriptBlock {
  param($RepoPathArg, $EnvFileArg, $PortArg)

  $envMap = @{}
  Get-Content -LiteralPath $EnvFileArg | ForEach-Object {
    if ($_ -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
      $k = $matches[1]
      $v = $matches[2].Trim().Trim('"').Trim("'")
      $envMap[$k] = $v
    }
  }

  Set-Location $RepoPathArg
  $env:NODE_ENV = "development"
  $env:PORT = [string]$PortArg

  foreach ($k in @("DATABASE_URL","GEMINI_API_KEY","OAUTH_SERVER_URL","JWT_SECRET","OWNER_OPEN_ID","VITE_APP_ID")) {
    if ($envMap.ContainsKey($k) -and -not [string]::IsNullOrWhiteSpace($envMap[$k])) {
      Set-Item -Path ("Env:" + $k) -Value ([string]$envMap[$k])
    }
  }

  pnpm exec tsx server/_core/index.ts
}

Start-Sleep -Seconds $WaitSeconds
$jobState = (Get-Job -Id $job.Id).State
$output = (Receive-Job -Id $job.Id -Keep *>&1 | Out-String)
Set-Content -Encoding UTF8 $StdOutPath $output

$listen = Get-NetTCPConnection -LocalPort $PreferredPort -State Listen -ErrorAction SilentlyContinue |
  Select-Object LocalAddress, LocalPort, OwningProcess, State

[ordered]@{
  repo_path = $RepoPath
  env_file = $EnvFile
  job_id = $job.Id
  job_state = $jobState
  preferred_port = $PreferredPort
  listen_count = @($listen).Count
  listen_rows = @($listen)
  output_path = $StdOutPath
  output_length = $output.Length
} | ConvertTo-Json -Depth 10 | Set-Content -Encoding UTF8 $ProbePath

Write-Host "Probe: $ProbePath"
Write-Host "Output: $StdOutPath"