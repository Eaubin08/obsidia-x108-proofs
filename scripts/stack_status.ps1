# =============================================================================
# scripts/stack_status.ps1 -- STATUS STRUCTURE STACK OBSIDIA
# Compatible: Windows PowerShell 5.1 + PowerShell 7+
# ASCII-only strings (no BOM issue).
#
# Usage:
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\stack_status.ps1
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\stack_status.ps1 -Quiet
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\stack_status.ps1 -Json
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\stack_status.ps1 -NoHttp
#
# NE LANCE RIEN. NE MUTE RIEN. NE COMMIT RIEN.
# Lecture seule -- health checks via netstat + HTTP GET readonly.
# decision_authority = KX108_ONLY
# =============================================================================

param(
    [switch]$Json,      # JSON output (machine-readable)
    [switch]$Quiet,     # One line per component
    [switch]$NoHttp     # Skip HTTP checks (netstat only)
)

$ErrorActionPreference = "SilentlyContinue"

# -- Canonical paths (auto-detect from $PSScriptRoot) ----------------------
$X108   = Split-Path -Parent $PSScriptRoot
$ROOT   = Split-Path -Parent $X108
$SHELL  = Join-Path $ROOT "obsidiashell-main"
$RT     = Join-Path $X108 "runtime_terrain_bank_trading_gps"

# -- Canonical URLs --------------------------------------------------------
$API    = "http://127.0.0.1:8000"
$GRAPH  = "http://127.0.0.1:8011"
$UI     = "http://127.0.0.1:5173"

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

function Get-PidOnPort {
    param([int]$Port)
    $line = netstat -ano 2>$null |
        Select-String ":$Port\s" |
        Where-Object { $_.Line -match "LISTENING" } |
        Select-Object -First 1
    if (-not $line) { return $null }
    $parts = ($line.Line -split "\s+") | Where-Object { $_ -ne "" }
    return $parts[-1]
}

function Test-PortListening {
    param([int]$Port)
    return ($null -ne (Get-PidOnPort $Port))
}

function Test-HttpHealth {
    param([string]$Url, [int]$TimeoutSec = 4)
    if ($NoHttp) { return "SKIPPED" }
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec -ErrorAction Stop
        if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 400) { return "OK" }
        return ("HTTP_" + $resp.StatusCode)
    } catch {
        return "UNREACHABLE"
    }
}

function Find-ProcessByPattern {
    param([string]$Pattern)
    $p = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -match $Pattern } |
        Select-Object -First 1
    if ($p) { return $p.ProcessId } else { return $null }
}

# Build-Component: returns a PSCustomObject for one stack component.
# All string parameters must be ASCII-safe before calling.
function Build-Component {
    param(
        [string]$Name,
        [string]$Role,
        [int]   $Port = 0,
        [string]$ProcessPattern = "",
        [string]$HealthUrl = "",
        [string]$LaunchCommand,
        [string]$LogLocation,
        [string]$Coverage,
        [string]$Authority,
        [string]$ShutdownCommand
    )

    # Resolve PID
    $foundPid = $null
    if ($Port -gt 0) { $foundPid = Get-PidOnPort $Port }
    if ((-not $foundPid) -and $ProcessPattern) {
        $foundPid = Find-ProcessByPattern $ProcessPattern
    }

    # Determine status
    $portUp = ($Port -gt 0) -and (Test-PortListening $Port)
    if ($portUp -or $foundPid) {
        $status = "UP"
    } elseif ($Port -gt 0) {
        $status = "DOWN"
    } else {
        $status = "UNKNOWN"
    }

    # Determine health
    $health = "N/A"
    if ($HealthUrl -and ($status -eq "UP")) {
        $health = Test-HttpHealth $HealthUrl
    } elseif (($status -eq "UP") -and (-not $HealthUrl)) {
        $health = "PORT_OK"
    } elseif ($status -eq "DOWN") {
        $health = "DOWN"
    }

    # PID display
    if ($foundPid) { $pidDisplay = $foundPid } else { $pidDisplay = "-" }
    if ($Port -gt 0) { $portDisplay = $Port } else { $portDisplay = "-" }

    return [PSCustomObject]@{
        name             = $Name
        role             = $Role
        status           = $status
        pid              = $pidDisplay
        port             = $portDisplay
        health           = $health
        launch_command   = $LaunchCommand
        log_location     = $LogLocation
        coverage         = $Coverage
        authority        = $Authority
        shutdown_command = $ShutdownCommand
    }
}

# =============================================================================
# COMPONENT DEFINITIONS
# =============================================================================

$components = @()

# ---- 1. Kernel Ragnarok -- port 3001 ----------------------------------------
$kernelFile = Join-Path $RT "server.kernel.sealed.cjs"
$kernelPresent = Test-Path $kernelFile
if ($kernelPresent) { $kernelCoverage = "PRESENT_AND_RUNNABLE" } else { $kernelCoverage = "ABSENT" }
$kernelLaunch = "node " + (Join-Path $RT "server.kernel.sealed.cjs")

$components += Build-Component `
    -Name            "KERNEL_RAGNAROK" `
    -Role            "Kernel X-108 - decision authority KX108_ONLY. PROTECTED." `
    -Port            3001 `
    -ProcessPattern  "server\.kernel\.sealed\.cjs" `
    -HealthUrl       "" `
    -LaunchCommand   $kernelLaunch `
    -LogLocation     "PowerShell window RAGNAROK KERNEL 3001" `
    -Coverage        $kernelCoverage `
    -Authority       "KX108_ONLY - final authority" `
    -ShutdownCommand "obsidia stop  OR  Stop-Process -Id [PID] -Force"

# ---- 2. API Obsidia/Brody -- port 8000 --------------------------------------
$apiBrodyLaunch = "uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
$components += Build-Component `
    -Name            "API_OBSIDIA_BRODY" `
    -Role            "FastAPI + Brody chat. OS_TRAD/IR/OS_REVERSE brain." `
    -Port            8000 `
    -ProcessPattern  "apps\.obsidia_api\.main:app" `
    -HealthUrl       "$API/api/health" `
    -LaunchCommand   $apiBrodyLaunch `
    -LogLocation     "PowerShell window OBSIDIA API 8000" `
    -Coverage        "PRESENT_AND_RUNNABLE" `
    -Authority       "READONLY - POST Brody allowed from human launcher only" `
    -ShutdownCommand "obsidia stop  OR  Stop-Process -Id [PID] -Force"

# ---- 3. Graphiti/ObsidiaShell -- port 8011 ----------------------------------
$shellPresent = Test-Path $SHELL
if ($shellPresent) { $shellCoverage = "PRESENT_AND_RUNNABLE" } else { $shellCoverage = "ABSENT - obsidiashell-main missing" }
$graphitiLaunch = "uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011  (from " + $SHELL + ")"
$components += Build-Component `
    -Name            "GRAPHITI_OBSIDIASHELL" `
    -Role            "Semantic graph memory - frozen V20 bridge." `
    -Port            8011 `
    -ProcessPattern  "obsidia_core\.agent_bridge:app" `
    -HealthUrl       "$GRAPH/graph/v20/frozen/status" `
    -LaunchCommand   $graphitiLaunch `
    -LogLocation     "PowerShell window OBSIDIASHELL GRAPHITI 8011" `
    -Coverage        $shellCoverage `
    -Authority       "READONLY - no graph write without approval" `
    -ShutdownCommand "obsidia stop  OR  Stop-Process -Id [PID] -Force"

# ---- 4. UI Workbench -- port 5173 -------------------------------------------
$uiDir = Join-Path $X108 "apps\obsidia-workbench"
$uiPresent = Test-Path $uiDir
if ($uiPresent) { $uiCoverage = "PRESENT" } else { $uiCoverage = "ABSENT" }
$uiLaunch = "npm run dev -- --host 127.0.0.1 --port 5173  (from " + $uiDir + ")"
$components += Build-Component `
    -Name            "UI_WORKBENCH" `
    -Role            "Vite/React interface Obsidia X-108." `
    -Port            5173 `
    -ProcessPattern  "npm run dev" `
    -HealthUrl       $UI `
    -LaunchCommand   $uiLaunch `
    -LogLocation     "PowerShell window OBSIDIA WORKBENCH UI 5173" `
    -Coverage        $uiCoverage `
    -Authority       "READONLY - display only" `
    -ShutdownCommand "obsidia stop  OR  Stop-Process -Id [PID] -Force"

# ---- 5. Neo4j -- ports 7475 (Browser) + 7688 (Instance) --------------------
$neo4jRunning = $null
try {
    $neo4jRunning = (docker inspect --format "{{.State.Running}}" deploy-neo4j-1 2>$null)
} catch {}
if ($neo4jRunning -eq "true") {
    $neo4jStatus = "UP"
} elseif ($neo4jRunning -eq "false") {
    $neo4jStatus = "DOWN"
} else {
    $neo4jStatus = "UNKNOWN"
}

# Browser port 7475
$components += [PSCustomObject]@{
    name             = "NEO4J_BROWSER"
    role             = "Neo4j Browser - graph visualization. Local container deploy-neo4j-1."
    status           = $neo4jStatus
    pid              = "-"
    port             = 7475
    health           = $neo4jStatus
    launch_command   = "docker start deploy-neo4j-1"
    log_location     = "docker logs deploy-neo4j-1"
    coverage         = "UNKNOWN - depends on Docker runtime"
    authority        = "INFRASTRUCTURE - do not kill without stopping Graphiti first"
    shutdown_command = "docker stop deploy-neo4j-1  (NOT via obsidia stop)"
}

# Instance port 7688
$components += [PSCustomObject]@{
    name             = "NEO4J_INSTANCE"
    role             = "Neo4j Bolt endpoint. Graphiti connects here (bolt://127.0.0.1:7688)."
    status           = $neo4jStatus
    pid              = "-"
    port             = 7688
    health           = $neo4jStatus
    launch_command   = "docker start deploy-neo4j-1"
    log_location     = "docker logs deploy-neo4j-1"
    coverage         = "UNKNOWN - depends on Docker runtime"
    authority        = "INFRASTRUCTURE - same container as NEO4J_BROWSER"
    shutdown_command = "docker stop deploy-neo4j-1  (NOT via obsidia stop)"
}

# ---- 6. Bank connector ------------------------------------------------------
$bankFile = Join-Path $X108 "connectors\bank_normal_flow.py"
$bankPresent = Test-Path $bankFile
if ($bankPresent) { $bankCoverage = "PRESENT_AND_RUNNABLE" } else { $bankCoverage = "ABSENT" }
$bankStatus = if ($bankPresent) { "UNKNOWN" } else { "ABSENT" }
$bankFoundPid = Find-ProcessByPattern "connectors\\\\bank_normal_flow\.py"
if ($bankFoundPid) { $bankStatus = "UP" }
$components += [PSCustomObject]@{
    name             = "CONNECTOR_BANK"
    role             = "Bank domain connector -> API 8000."
    status           = $bankStatus
    pid              = if ($bankFoundPid) { $bankFoundPid } else { "-" }
    port             = "-"
    health           = $bankStatus
    launch_command   = "python connectors\bank_normal_flow.py  (OBSIDIA_API_BASE=http://127.0.0.1:8000)"
    log_location     = "PowerShell window bank_normal_flow.py"
    coverage         = $bankCoverage
    authority        = "READONLY - domain data only"
    shutdown_command = "obsidia stop  OR  Stop-Process -Id [PID] -Force"
}

# ---- 7. Trading connector ---------------------------------------------------
$tradingFile = Join-Path $X108 "connectors\trading_live.py"
$tradingPresent = Test-Path $tradingFile
if ($tradingPresent) { $tradingCoverage = "PRESENT_AND_RUNNABLE" } else { $tradingCoverage = "ABSENT" }
$tradingStatus = if ($tradingPresent) { "UNKNOWN" } else { "ABSENT" }
$tradingFoundPid = Find-ProcessByPattern "connectors\\\\trading_live\.py"
if ($tradingFoundPid) { $tradingStatus = "UP" }
$components += [PSCustomObject]@{
    name             = "CONNECTOR_TRADING"
    role             = "Trading domain connector -> API 8000."
    status           = $tradingStatus
    pid              = if ($tradingFoundPid) { $tradingFoundPid } else { "-" }
    port             = "-"
    health           = $tradingStatus
    launch_command   = "python connectors\trading_live.py  (OBSIDIA_API_BASE=http://127.0.0.1:8000)"
    log_location     = "PowerShell window trading_live.py"
    coverage         = $tradingCoverage
    authority        = "READONLY - domain data only"
    shutdown_command = "obsidia stop  OR  Stop-Process -Id [PID] -Force"
}

# ---- 8. GPS/Aviation connector ----------------------------------------------
$gpsFile = Join-Path $X108 "connectors\aviation_robo.py"
$gpsPresent = Test-Path $gpsFile
if ($gpsPresent) { $gpsCoverage = "PRESENT_AND_RUNNABLE" } else { $gpsCoverage = "ABSENT" }
$gpsStatus = if ($gpsPresent) { "UNKNOWN" } else { "ABSENT" }
$gpsFoundPid = Find-ProcessByPattern "connectors\\\\aviation_robo\.py"
if ($gpsFoundPid) { $gpsStatus = "UP" }
$components += [PSCustomObject]@{
    name             = "CONNECTOR_GPS_AVIATION"
    role             = "GPS/Aviation domain connector -> API 8000."
    status           = $gpsStatus
    pid              = if ($gpsFoundPid) { $gpsFoundPid } else { "-" }
    port             = "-"
    health           = $gpsStatus
    launch_command   = "python connectors\aviation_robo.py  (OBSIDIA_API_BASE=http://127.0.0.1:8000)"
    log_location     = "PowerShell window aviation_robo.py"
    coverage         = $gpsCoverage
    authority        = "READONLY - domain data only"
    shutdown_command = "obsidia stop  OR  Stop-Process -Id [PID] -Force"
}

# ---- 9. Brody Enriched terminal (preferred) ---------------------------------
$brodyEnrichedFile = Join-Path $X108 "scripts\run_brody_terminal_enriched.ps1"
$brodyEnrichedPresent = Test-Path $brodyEnrichedFile
if ($brodyEnrichedPresent) { $brodyEnrichedCoverage = "PRESENT_AND_RUNNABLE" } else { $brodyEnrichedCoverage = "ABSENT" }
$brodyEnrichedStatus = "UNKNOWN"
$brodyEnrichedPid = Find-ProcessByPattern "run_brody_terminal_enriched\.ps1"
if ($brodyEnrichedPid) { $brodyEnrichedStatus = "UP" }
if (-not $brodyEnrichedPresent) { $brodyEnrichedStatus = "ABSENT" }
$components += [PSCustomObject]@{
    name             = "BRODY_ENRICHED_TERMINAL"
    role             = "Brody enriched chat terminal (preferred). Points to API 8000."
    status           = $brodyEnrichedStatus
    pid              = if ($brodyEnrichedPid) { $brodyEnrichedPid } else { "-" }
    port             = "-"
    health           = $brodyEnrichedStatus
    launch_command   = "powershell.exe -File scripts\run_brody_terminal_enriched.ps1 -Base http://127.0.0.1:8000"
    log_location     = "PowerShell window BRODY ENRICHED"
    coverage         = $brodyEnrichedCoverage
    authority        = "READONLY - readonly=true emits_act=false decision_authority=KX108_ONLY"
    shutdown_command = "Ctrl+C in Brody window"
}

# ---- 10. Obsidure agent -----------------------------------------------------
$obsidureFile = Join-Path $X108 "periphery\agents\agent_obsidure.py"
$obsidurePresent = Test-Path $obsidureFile
if ($obsidurePresent) { $obsidureCoverage = "PRESENT_AND_RUNNABLE (standalone)" } else { $obsidureCoverage = "ABSENT" }
$obsidureStatus = if ($obsidurePresent) { "READY" } else { "ABSENT" }
$components += [PSCustomObject]@{
    name             = "AGENT_OBSIDURE"
    role             = "Peripheral builder. AVDR. Sandbox. Proposals. HUMAN_APPROVED_WRITE."
    status           = $obsidureStatus
    pid              = "-"
    port             = "-"
    health           = if ($obsidurePresent) { "FILE_OK" } else { "ABSENT" }
    launch_command   = "powershell.exe -File scripts\run_agent_obsidure.ps1  OR  python scripts\obsidure_cli.py"
    log_location     = "_PATCH_PROPOSALS\[id]\RECEIPT.md"
    coverage         = $obsidureCoverage
    authority        = "HUMAN_APPROVED_WRITE - all output waits for human approval"
    shutdown_command = "quit  OR  Ctrl+C"
}

# ---- 11. Terminal CLI (obsidia>) --------------------------------------------
$cliFile = Join-Path $X108 "scripts\obsidia_cli.py"
$cliPresent = Test-Path $cliFile
$cliStatus = if ($cliPresent) { "READY" } else { "ABSENT" }
$cliHealth = if ($cliPresent) { "FILE_OK" } else { "ABSENT" }
$cliCoverage = if ($cliPresent) { "PRESENT_AND_RUNNABLE" } else { "ABSENT" }
$components += [PSCustomObject]@{
    name             = "TERMINAL_CLI"
    role             = "Non-sovereign interactive shell. NL routing. No mutation. KX108_ONLY."
    status           = $cliStatus
    pid              = "-"
    port             = "-"
    health           = $cliHealth
    launch_command   = "python scripts\obsidia_cli.py  OR  powershell.exe -File scripts\obsidia.ps1"
    log_location     = "audit\obsidia_gateway_usage.jsonl (JSONL receipts)"
    coverage         = $cliCoverage
    authority        = "KX108_ONLY - decision_authority=KX108_ONLY. No ACT."
    shutdown_command = "exit  OR  Ctrl+C"
}

# =============================================================================
# OUTPUT
# =============================================================================

if ($Json) {
    $components | ConvertTo-Json -Depth 10
    exit 0
}

if (-not $Quiet) {
    Write-Host ""
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host "  OBSIDIA X-108 -- STACK STATUS" -ForegroundColor Cyan
    Write-Host "  decision_authority = KX108_ONLY  |  read-only" -ForegroundColor DarkGray
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host ""
}

foreach ($c in $components) {
    $st = $c.status
    if ($st -eq "UP" -or $st -eq "READY") {
        $color = "Green"
    } elseif ($st -eq "DOWN" -or $st -eq "ABSENT") {
        $color = "Red"
    } elseif ($st -eq "UNKNOWN") {
        $color = "Yellow"
    } else {
        $color = "White"
    }

    if ($Quiet) {
        $line = "  {0,-28} {1,-8} port={2,-10} health={3}" -f $c.name, $c.status, $c.port, $c.health
        Write-Host $line -ForegroundColor $color
    } else {
        Write-Host ("  -- " + $c.name) -ForegroundColor $color
        Write-Host ("     role       : " + $c.role) -ForegroundColor Gray
        Write-Host ("     status     : " + $c.status) -ForegroundColor $color
        Write-Host ("     pid        : " + $c.pid)
        Write-Host ("     port       : " + $c.port)
        Write-Host ("     health     : " + $c.health) -ForegroundColor $color
        Write-Host ("     coverage   : " + $c.coverage) -ForegroundColor DarkGray
        Write-Host ("     authority  : " + $c.authority) -ForegroundColor DarkGray
        Write-Host ("     launch     : " + $c.launch_command) -ForegroundColor DarkGray
        Write-Host ("     logs       : " + $c.log_location) -ForegroundColor DarkGray
        Write-Host ("     shutdown   : " + $c.shutdown_command) -ForegroundColor DarkGray
        Write-Host ""
    }
}

if (-not $Quiet) {
    Write-Host "  ============================================================" -ForegroundColor Cyan
    $upCount   = 0
    $downCount = 0
    $unkCount  = 0
    foreach ($c in $components) {
        if ($c.status -eq "UP" -or $c.status -eq "READY") { $upCount++ }
        elseif ($c.status -eq "DOWN" -or $c.status -eq "ABSENT") { $downCount++ }
        else { $unkCount++ }
    }
    Write-Host ("  SUMMARY: " + $upCount + " UP/READY  |  " + $downCount + " DOWN/ABSENT  |  " + $unkCount + " UNKNOWN") -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  START stack : powershell.exe -File scripts\obsidia.ps1" -ForegroundColor DarkGray
    Write-Host "  STOP  stack : powershell.exe -File scripts\obsidia.ps1 stop" -ForegroundColor DarkGray
    Write-Host "  OBSIDURE    : powershell.exe -File scripts\run_agent_obsidure.ps1" -ForegroundColor DarkGray
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host ""
}
