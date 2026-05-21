# V5A — Run All Internal Local Flows
# All flows are dry-run only. No real ACT. No network. No wallet.

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

$flows = @(
    "v3_v4_full_stack_flow",
    "v4_controlled_runtime_flow",
    "bank_full_stack_flow",
    "trading_full_stack_flow",
    "gps_full_stack_flow",
    "memory_brody_graphiti_flow",
    "blockchain_security_dryrun_flow",
    "world_call_gateway_flow"
)

Write-Host "`n=== V5A Internal Flow Runner: ALL LOCAL FLOWS ===" -ForegroundColor Cyan
$passed = 0
$failed = 0

foreach ($flow in $flows) {
    Write-Host "`n[$($passed+$failed+1)/$($flows.Count)] $flow..." -ForegroundColor Yellow
    python -m demos.local_flows.$flow
    if ($LASTEXITCODE -eq 0) {
        $passed++
    } else {
        Write-Host "FAILED" -ForegroundColor Red
        $failed++
    }
}

Write-Host "`n=== Results: $passed passed, $failed failed ===" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
if ($failed -gt 0) { exit 1 }
