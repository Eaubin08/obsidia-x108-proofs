param(
  [string]$Repo = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B",
  [switch]$ForceRestart,
  [int]$WaitSeconds = 5
)

Set-Location $Repo

Write-Host "`n=== OBSIDIA / X108 — START STACK ===" -ForegroundColor Cyan
Write-Host "Repo=$Repo" -ForegroundColor Gray
Write-Host "ForceRestart=$ForceRestart" -ForegroundColor Gray

if ($ForceRestart) {
  Write-Host "`n=== FORCE RESTART: STOP EXISTING KERNEL/API ===" -ForegroundColor Yellow
  powershell -ExecutionPolicy Bypass -File "$Repo\scripts\runtime\stop_obsidia_stack.ps1"
  Start-Sleep -Seconds 2
}

$kernelScript = "$Repo\scripts\runtime\start_kernel.ps1"
$apiScript = "$Repo\scripts\runtime\start_api.ps1"

Write-Host "`nStarting Kernel terminal..." -ForegroundColor Cyan
Start-Process powershell.exe -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-File", $kernelScript
)

Start-Sleep -Seconds 3

Write-Host "Starting API terminal..." -ForegroundColor Cyan
Start-Process powershell.exe -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-File", $apiScript
)

Write-Host "`nWaiting $WaitSeconds seconds before status check..." -ForegroundColor Yellow
Start-Sleep -Seconds $WaitSeconds

powershell -ExecutionPolicy Bypass -File "$Repo\scripts\runtime\status_obsidia_stack.ps1" -LatestN 50

Write-Host "`nSTATUS=START_OBSIDIA_STACK_DONE" -ForegroundColor Green
