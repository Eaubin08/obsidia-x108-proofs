# ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "server.kernel.sealed.cjs" -or
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "connectors\\bank_normal_flow.py" -or
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "connectors\\trading_live.py" -or
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "connectors\\aviation_robo.py" -or
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "server.kernel.sealed.cjs" -or
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "connectors\\bank_normal_flow.py" -or
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "connectors\\trading_live.py" -or
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "connectors\\aviation_robo.py" -or
    # ============================================================
# OBSIDIA BRODY ONLY STACK
# Neo4j 7475/7688 + API Brody 8000 + Graphiti 8011 + UI 5173
# + Brody V1 Chat + Brody Enriched + Brody Raw Inspector
# No domain connectors / No kernel 3001
# ============================================================

$ROOT  = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$REPO  = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$SHELL = "$ROOT\obsidiashell-main"
$UI_DIR = "$REPO\apps\obsidia-workbench"

$API   = "http://127.0.0.1:8000"
$GRAPH = "http://127.0.0.1:8011"
$UI    = "http://127.0.0.1:5173"

$NEO4J_BROWSER = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT    = "bolt://127.0.0.1:7688"

$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS = "$GRAPH/docs"

Set-Location $REPO

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "STOP BRODY ONLY STACK + DOMAIN/KERNEL CLEANUP" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  ForEach-Object {
    Write-Host "Stopping PID=$($_.ProcessId)" -ForegroundColor Yellow
    Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
  }

foreach ($port in @(3001, 8000, 8011, 5173)) {
  $pids = netstat -ano |
    Select-String ":$port\s" |
    Where-Object { $_.Line -match "LISTENING" } |
    ForEach-Object { ($_ -split "\s+")[-1] } |
    Sort-Object -Unique

  foreach ($pid in $pids) {
    if ($pid -and $pid -ne "0") {
      Write-Host "Killing port $port PID=$pid" -ForegroundColor Yellow
      Stop-Process -Id ([int]$pid) -Force -ErrorAction SilentlyContinue
    }
  }
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START NEO4J DOCKER — 7475 / 7688" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  docker start deploy-neo4j-1 | Out-Host
  Write-Host "Neo4j Docker OK / already running" -ForegroundColor Green
} catch {
  Write-Host "Docker start failed. If Neo4j is already connected on 127.0.0.1:7688, continue." -ForegroundColor Yellow
}

Start-Sleep -Seconds 3

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START API OBSIDIA / BRODY — 8000" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$REPO'; [Console]::Title='OBSIDIA API 8000 - BRODY ONLY'; `$env:PYTHONPATH='$REPO'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
)

Start-Sleep -Seconds 8

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "CHECK API 8000 + BRODY ROUTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

try {
  Invoke-RestMethod "$API/" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "API 8000 OK" -ForegroundColor Green
} catch {
  Write-Host "API 8000 NOT READY" -ForegroundColor Red
}

try {
  $BODY_OBJ = @{
    message = "Test Brody readonly stack."
    mode = "readonly_brody_only_stack_launch"
    compact = $true
  }

  $BODY_JSON = $BODY_OBJ | ConvertTo-Json -Depth 10 -Compress

  $R = Invoke-RestMethod `
    -Uri "$API/api/brody/chat" `
    -Method POST `
    -ContentType "application/json; charset=utf-8" `
    -Body ([System.Text.Encoding]::UTF8.GetBytes($BODY_JSON)) `
    -TimeoutSec 20

  Write-Host "BRODY CHAT OK" -ForegroundColor Green
  $R | ConvertTo-Json -Depth 6 | Out-Host
} catch {
  Write-Host "BRODY CHAT TEST FAILED" -ForegroundColor Yellow
  Write-Host $_.Exception.Message -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START GRAPHITI / OBSIDIASHELL — 8011" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$SHELL'; [Console]::Title='OBSIDIASHELL GRAPHITI 8011'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
)

Start-Sleep -Seconds 7

try {
  Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | ConvertTo-Json -Depth 8 | Out-Host
  Write-Host "GRAPHITI 8011 OK" -ForegroundColor Green
} catch {
  Write-Host "GRAPHITI 8011 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START UI WORKBENCH — 5173" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process powershell -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd '$UI_DIR'; [Console]::Title='OBSIDIA WORKBENCH UI 5173'; npm run dev -- --host 127.0.0.1 --port 5173"
)

Start-Sleep -Seconds 8

try {
  $UI_STATUS = (Invoke-WebRequest "$UI" -UseBasicParsing -TimeoutSec 10).StatusCode
  Write-Host "UI 5173 OK status=$UI_STATUS" -ForegroundColor Green
} catch {
  Write-Host "UI 5173 NOT READY" -ForegroundColor Yellow
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "START 3 BRODY CHAT INSTANCES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

$BRODY_V1_CHAT = "$REPO\scripts\run_brody_terminal_chat.ps1"
$BRODY_ENRICHED_MAIN = "$REPO\scripts\run_brody_terminal_enriched.ps1"
$BRODY_ENRICHED_FALLBACK = "$REPO\ci_recheck_optional_publication\scripts\run_brody_terminal_enriched.ps1"
$BRODY_RAW = "$REPO\scripts\run_brody_terminal.ps1"

if (Test-Path $BRODY_V1_CHAT) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY V1 CHAT -> API 8000'; & '$BRODY_V1_CHAT' '$API'"
  )
  Write-Host "BRODY V1 CHAT launched" -ForegroundColor Green
} else {
  Write-Host "BRODY V1 CHAT script missing: $BRODY_V1_CHAT" -ForegroundColor Red
}

if (Test-Path $BRODY_ENRICHED_MAIN) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_MAIN' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from scripts/" -ForegroundColor Green
} elseif (Test-Path $BRODY_ENRICHED_FALLBACK) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY ENRICHED -> API 8000'; & '$BRODY_ENRICHED_FALLBACK' -Base '$API'"
  )
  Write-Host "BRODY ENRICHED launched from ci_recheck_optional_publication/" -ForegroundColor Green
} else {
  Write-Host "BRODY ENRICHED script missing" -ForegroundColor Red
}

if (Test-Path $BRODY_RAW) {
  Start-Process powershell -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy", "Bypass",
    "-Command",
    "cd '$REPO'; [Console]::Title='BRODY RAW INSPECTOR -> API 8000'; & '$BRODY_RAW' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
  )
  Write-Host "BRODY RAW INSPECTOR launched" -ForegroundColor Green
} else {
  Write-Host "BRODY RAW script missing: $BRODY_RAW" -ForegroundColor Red
}

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "OPEN BROWSERS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

Start-Process "$UI"
Start-Process "$GRAPH_WORKBENCH"
Start-Process "$GRAPH_DOCS"
Start-Process "$NEO4J_BROWSER"

Write-Host "`n============================================================" -ForegroundColor Cyan
Write-Host "FINAL BRODY ONLY CHECK" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan

netstat -ano | Select-String ":8000|:8011|:5173|:7475|:7688" | Out-Host

Get-CimInstance Win32_Process |
  Where-Object {
    $_.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green

.CommandLine -match "apps.obsidia_api.main:app" -or
    $_.CommandLine -match "obsidia_core.agent_bridge:app" -or
    $_.CommandLine -match "npm run dev" -or
    $_.CommandLine -match "vite" -or
    $_.CommandLine -match "run_brody_terminal_chat.ps1" -or
    $_.CommandLine -match "run_brody_terminal_enriched.ps1" -or
    $_.CommandLine -match "run_brody_terminal.ps1" -or
    $_.CommandLine -match "brody_terminal_chat.py"
  } |
  Select-Object ProcessId, Name, CommandLine |
  Format-Table -AutoSize

Write-Host "`nBRODY ONLY STACK READY" -ForegroundColor Green
Write-Host "API Brody/Obsidia  : $API"
Write-Host "Graphiti Bridge    : $GRAPH"
Write-Host "Graphiti Workbench : $GRAPH_WORKBENCH"
Write-Host "Graphiti Docs      : $GRAPH_DOCS"
Write-Host "UI Workbench       : $UI"
Write-Host "Neo4j Browser      : $NEO4J_BROWSER"
Write-Host "Neo4j Bolt         : $NEO4J_BOLT"
Write-Host "Brody V1 Chat      : launched"
Write-Host "Brody Enriched     : launched"
Write-Host "Brody Raw Inspector: launched"
Write-Host "Test /status in Brody V1 terminal." -ForegroundColor Green
