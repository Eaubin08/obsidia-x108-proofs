# DOMAIN STACK ONLY — RUNBOOK

## Scope

This launcher starts only the domain execution matrix:

- Kernel Ragnarok: `http://127.0.0.1:3001`
- API Obsidia Live Kernel Bridge: `http://127.0.0.1:8000`
- Bank connector
- Trading connector
- GPS / Aviation connector

It does not start:

- Neo4j
- Graphiti / ObsidiaShell
- UI Workbench
- Brody terminals

## Launcher

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
.\scripts\start_domain_stack_only.ps1
Expected ports
3001 LISTENING = Kernel Ragnarok
8000 LISTENING = API Obsidia
Expected kernel logs
[BRIDGE] Routing -> Domain: bank
[KERNEL_DECISION]
[SAVE] decision_bank_...

[BRIDGE] Routing -> Domain: trading
[KERNEL_DECISION]
[SAVE] decision_trading_...

[BRIDGE] Routing -> Domain: gps_defense_aviation
[KERNEL_DECISION]
[SAVE] decision_gps_defense_aviation_...
API route check
$openapi = Invoke-RestMethod "http://127.0.0.1:8000/openapi.json"
$openapi.paths.PSObject.Properties |
  Where-Object { $_.Name -match "/api/live/kernel/adapters" } |
  Select-Object Name |
  Format-Table -AutoSize

Expected:

/api/live/kernel/adapters/bank
/api/live/kernel/adapters/trading
/api/live/kernel/adapters/gps
