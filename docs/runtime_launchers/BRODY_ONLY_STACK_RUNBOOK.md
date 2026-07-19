
BRODY ONLY STACK — RUNBOOK
Scope

This launcher starts only the Brody operating stack:

Neo4j Browser: http://127.0.0.1:7475/browser/
Neo4j Bolt: bolt://127.0.0.1:7688
API Obsidia / Brody: http://127.0.0.1:8000
Graphiti / ObsidiaShell: http://127.0.0.1:8011
UI Workbench: http://127.0.0.1:5173
Brody V1 Chat
Brody Enriched
Brody Raw Inspector

It does not start:

Kernel Ragnarok 3001
Bank connector
Trading connector
GPS / Aviation connector
Launcher
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
.\scripts\start_brody_only_stack.ps1
Expected ports
8000 LISTENING = API Obsidia / Brody
8011 LISTENING = Graphiti / ObsidiaShell
5173 LISTENING = UI Workbench
7475 LISTENING = Neo4j Browser
7688 LISTENING = Neo4j Bolt
Brody test
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"

$BODY_OBJ = @{
  message = "Test Brody readonly stack."
  mode = "readonly_brody_only_test"
  compact = $true
}

$BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/brody/chat" `
  -Method POST `
  -ContentType "application/json; charset=utf-8" `
  -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) |
  ConvertTo-Json -Depth 8
Expected Brody flags
decision_authority = KX108_ONLY
readonly = true
advisory_only = true
emits_act = false
memory_write = false
graphiti_write = false
neo4j_write = false
Brody terminal instances
.\scripts\run_brody_terminal_chat.ps1 "http://127.0.0.1:8000"
.\scripts\run_brody_terminal_enriched.ps1 -Base "http://127.0.0.1:8000"
.\scripts\run_brody_terminal.ps1 -Base "http://127.0.0.1:8000" -SessionId "brody_terminal_raw_inspector"
