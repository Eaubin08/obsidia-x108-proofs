param(
  [switch]$DryRun
)

Write-Host "`n=== OBSIDIA / X108 — STOP KERNEL/API STACK ===" -ForegroundColor Cyan

$targets = @(
  "server\.kernel\.sealed\.cjs",
  "apps\.obsidia_api\.main"
)

$pattern = ($targets -join "|")

$processes = @(
  Get-CimInstance Win32_Process |
    Where-Object {
      $_.CommandLine -match $pattern
    }
)

if ($processes.Count -eq 0) {
  Write-Host "No Kernel/API process found." -ForegroundColor Green
  Write-Host "STATUS=STOP_OBSIDIA_STACK_NOTHING_TO_STOP" -ForegroundColor Green
  exit 0
}

$processes |
  Select-Object ProcessId, Name, CommandLine |
  Format-List

foreach ($p in $processes) {
  if ($DryRun) {
    Write-Host "DRY_RUN would stop PID=$($p.ProcessId) NAME=$($p.Name)" -ForegroundColor Yellow
  } else {
    Write-Host "STOP PID=$($p.ProcessId) NAME=$($p.Name)" -ForegroundColor Yellow
    Stop-Process -Id $p.ProcessId -Force
  }
}

if ($DryRun) {
  Write-Host "STATUS=STOP_OBSIDIA_STACK_DRY_RUN_DONE" -ForegroundColor Yellow
} else {
  Start-Sleep -Seconds 2
  Write-Host "STATUS=STOP_OBSIDIA_STACK_DONE" -ForegroundColor Green
}
