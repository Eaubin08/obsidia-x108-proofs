# =============================================================================
# scripts/stack_status.ps1 — STATUS STRUCTURÉ STACK OBSIDIA
# Affiche pour chaque composant :
#   name / status / pid / port / health / launch_command / log_location /
#   coverage / authority / shutdown_command
#
# NE LANCE RIEN. NE MUTE RIEN. NE COMMIT RIEN.
# Lecture seule — health checks via netstat + HTTP GET readonly.
# decision_authority = KX108_ONLY
# =============================================================================

param(
    [switch]$Json,      # Sortie JSON brute
    [switch]$Quiet,     # Une ligne par composant uniquement
    [switch]$NoHttp     # Désactive les HTTP checks (netstat seulement)
)

$ErrorActionPreference = "SilentlyContinue"

# ── Chemins canoniques (auto-détection depuis $PSScriptRoot) ────────────────
$X108   = Split-Path -Parent $PSScriptRoot
$ROOT   = Split-Path -Parent $X108
$SHELL  = Join-Path $ROOT "obsidiashell-main"
$RT     = Join-Path $X108 "runtime_terrain_bank_trading_gps"

# ── URLs canoniques ──────────────────────────────────────────────────────────
$API    = "http://127.0.0.1:8000"
$GRAPH  = "http://127.0.0.1:8011"
$UI     = "http://127.0.0.1:5173"

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

function Get-PidOnPort {
    param([int]$Port)
    $line = netstat -ano 2>$null |
        Select-String ":$Port\s" |
        Where-Object { $_.Line -match "LISTENING" } |
        Select-Object -First 1
    if (-not $line) { return $null }
    $parts = ($line -split "\s+") | Where-Object { $_ -ne "" }
    return $parts[-1]
}

function Test-PortListening {
    param([int]$Port)
    return $null -ne (Get-PidOnPort $Port)
}

function Test-HttpHealth {
    param([string]$Url, [int]$TimeoutSec = 4)
    if ($NoHttp) { return "SKIPPED" }
    try {
        $resp = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec -ErrorAction Stop
        if ($resp.StatusCode -ge 200 -and $resp.StatusCode -lt 400) { return "OK" }
        return "HTTP_$($resp.StatusCode)"
    } catch {
        return "UNREACHABLE"
    }
}

function Find-ProcessByPattern {
    param([string]$Pattern)
    $p = Get-CimInstance Win32_Process |
        Where-Object { $_.CommandLine -match $Pattern } |
        Select-Object -First 1
    if ($p) { return $p.ProcessId } else { return $null }
}

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

    # PID
    $pid_ = $null
    if ($Port -gt 0) { $pid_ = Get-PidOnPort $Port }
    if (-not $pid_ -and $ProcessPattern) { $pid_ = Find-ProcessByPattern $ProcessPattern }

    # Status
    $portOk = ($Port -gt 0) -and (Test-PortListening $Port)
    $status = if ($portOk -or ($pid_)) { "UP" } elseif ($Port -gt 0) { "DOWN" } else { "UNKNOWN" }

    # Health
    $health = "N/A"
    if ($HealthUrl -and $status -eq "UP") {
        $health = Test-HttpHealth $HealthUrl
    } elseif ($status -eq "UP" -and -not $HealthUrl) {
        $health = "PORT_OK"
    } elseif ($status -eq "DOWN") {
        $health = "DOWN"
    }

    return [PSCustomObject]@{
        name             = $Name
        role             = $Role
        status           = $status
        pid              = if ($pid_) { $pid_ } else { "-" }
        port             = if ($Port -gt 0) { $Port } else { "-" }
        health           = $health
        launch_command   = $LaunchCommand
        log_location     = $LogLocation
        coverage         = $Coverage
        authority        = $Authority
        shutdown_command = $ShutdownCommand
    }
}

# =============================================================================
# DÉFINITION DES COMPOSANTS
# =============================================================================

$components = @()

# 1. Kernel Ragnarok — 3001
$kernelFile = Join-Path $RT "server.kernel.sealed.cjs"
$kernelPresent = Test-Path $kernelFile
$components += Build-Component `
    -Name            "KERNEL_RAGNAROK" `
    -Role            "Noyau X-108 — autorité finale (KX108_ONLY). PROTECTED." `
    -Port            3001 `
    -ProcessPattern  "server\.kernel\.sealed\.cjs" `
    -HealthUrl       "" `
    -LaunchCommand   "node $RT\server.kernel.sealed.cjs" `
    -LogLocation     "fenetre PowerShell RAGNAROK KERNEL 3001" `
    -Coverage        $(if ($kernelPresent) { "PRESENT_AND_RUNNABLE" } else { "ABSENT" }) `
    -Authority       "KX108_ONLY — décision finale" `
    -ShutdownCommand "obsidia stop  OU  Stop-Process -Id <PID> -Force"

# 2. API Obsidia/Brody — 8000
$components += Build-Component `
    -Name            "API_OBSIDIA_BRODY" `
    -Role            "API FastAPI + Brody chat. Cerveau OS_TRAD/IR/OS_REVERSE." `
    -Port            8000 `
    -ProcessPattern  "apps\.obsidia_api\.main:app" `
    -HealthUrl       "$API/api/health" `
    -LaunchCommand   "uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000" `
    -LogLocation     "fenetre PowerShell OBSIDIA API 8000" `
    -Coverage        "PRESENT_AND_RUNNABLE" `
    -Authority       "READONLY — POST Brody autorisé launcher humain uniquement" `
    -ShutdownCommand "obsidia stop  OU  Stop-Process -Id <PID> -Force"

# 3. Graphiti/ObsidiaShell — 8011
$shellPresent = Test-Path $SHELL
$components += Build-Component `
    -Name            "GRAPHITI_OBSIDIASHELL" `
    -Role            "Mémoire graphe sémantique — bridge frozen V20." `
    -Port            8011 `
    -ProcessPattern  "obsidia_core\.agent_bridge:app" `
    -HealthUrl       "$GRAPH/graph/v20/frozen/status" `
    -LaunchCommand   "uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011  (depuis $SHELL)" `
    -LogLocation     "fenetre PowerShell OBSIDIASHELL GRAPHITI 8011" `
    -Coverage        $(if ($shellPresent) { "PRESENT_AND_RUNNABLE" } else { "ABSENT — obsidiashell-main manquant" }) `
    -Authority       "READONLY — aucune écriture graphe sans approbation" `
    -ShutdownCommand "obsidia stop  OU  Stop-Process -Id <PID> -Force"

# 4. UI Workbench — 5173
$uiDir = Join-Path $X108 "apps\obsidia-workbench"
$uiPresent = Test-Path $uiDir
$components += Build-Component `
    -Name            "UI_WORKBENCH" `
    -Role            "Interface Vite/React Obsidia X-108." `
    -Port            5173 `
    -ProcessPattern  "npm run dev" `
    -HealthUrl       $UI `
    -LaunchCommand   "npm run dev -- --host 127.0.0.1 --port 5173  (depuis $uiDir)" `
    -LogLocation     "fenetre PowerShell OBSIDIA WORKBENCH UI 5173" `
    -Coverage        $(if ($uiPresent) { "PRESENT" } else { "ABSENT" }) `
    -Authority       "READONLY — UI display seulement" `
    -ShutdownCommand "obsidia stop  OU  Stop-Process -Id <PID> -Force"

# 5. Neo4j Docker — 7475/7688
$neo4jRunning = $null
try {
    $neo4jRunning = docker inspect --format "{{.State.Running}}" deploy-neo4j-1 2>$null
} catch {}
$neo4jStatus = if ($neo4jRunning -eq "true") { "UP" } elseif ($neo4jRunning -eq "false") { "DOWN" } else { "UNKNOWN" }
$components += [PSCustomObject]@{
    name             = "NEO4J_DOCKER"
    role             = "Base graphe Neo4j — persistance Graphiti."
    status           = $neo4jStatus
    pid              = "-"
    port             = "7475/7688"
    health           = $neo4jStatus
    launch_command   = "docker start deploy-neo4j-1"
    log_location     = "docker logs deploy-neo4j-1"
    coverage         = "UNKNOWN — dépend runtime Docker"
    authority        = "INFRASTRUCTURE — ne pas killer sans arrêt Graphiti d'abord"
    shutdown_command = "docker stop deploy-neo4j-1  (NE PAS tuer via obsidia stop)"
}

# 6. Terminal CLI (obsidia>)
$cliFile = Join-Path $X108 "scripts\obsidia_cli.py"
$cliPresent = Test-Path $cliFile
$components += [PSCustomObject]@{
    name             = "TERMINAL_CLI"
    role             = "Shell interactif non souverain. Routage NL. Aucune mutation."
    status           = if ($cliPresent) { "READY" } else { "ABSENT" }
    pid              = "-"
    port             = "-"
    health           = if ($cliPresent) { "FILE_OK" } else { "ABSENT" }
    launch_command   = "python scripts\obsidia_cli.py  OU  obsidia start"
    log_location     = "audit\obsidia_gateway_usage.jsonl (receipts JSONL)"
    coverage         = if ($cliPresent) { "PRESENT_AND_RUNNABLE" } else { "ABSENT" }
    authority        = "KX108_ONLY — decision_authority = KX108_ONLY. Aucun ACT."
    shutdown_command = "exit  OU  Ctrl+C"
}

# 7. Obsidure Agent
$obsidureFile = Join-Path $X108 "periphery\agents\agent_obsidure.py"
$obsidurePresent = Test-Path $obsidureFile
$obsidureCli = Join-Path $X108 "scripts\obsidure_cli.py"
$components += [PSCustomObject]@{
    name             = "AGENT_OBSIDURE"
    role             = "Bâtisseur périphérique. AVDR. Sandbox. Proposals. HUMAN_APPROVED_WRITE."
    status           = if ($obsidurePresent) { "READY" } else { "ABSENT" }
    pid              = "-"
    port             = "-"
    health           = if ($obsidurePresent) { "FILE_OK" } else { "ABSENT" }
    launch_command   = "pwsh -File scripts\run_agent_obsidure.ps1  OU  python scripts\obsidure_cli.py"
    log_location     = "_PATCH_PROPOSALS\<id>\RECEIPT.md"
    coverage         = if ($obsidurePresent) { "PRESENT_AND_RUNNABLE (standalone)" } else { "ABSENT" }
    authority        = "HUMAN_APPROVED_WRITE — toute sortie attend approbation humaine"
    shutdown_command = "quit  OU  Ctrl+C"
}

# =============================================================================
# AFFICHAGE
# =============================================================================

if ($Json) {
    $components | ConvertTo-Json -Depth 10
    exit 0
}

if (-not $Quiet) {
    Write-Host ""
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host "  OBSIDIA X-108 — STACK STATUS" -ForegroundColor Cyan
    Write-Host "  decision_authority = KX108_ONLY  |  lecture seule" -ForegroundColor DarkGray
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host ""
}

foreach ($c in $components) {
    $color = switch ($c.status) {
        "UP"      { "Green" }
        "READY"   { "Green" }
        "DOWN"    { "Red" }
        "ABSENT"  { "Red" }
        "UNKNOWN" { "Yellow" }
        default   { "White" }
    }
    if ($Quiet) {
        Write-Host ("  {0,-24} {1,-8} port={2,-10} health={3}" -f $c.name, $c.status, $c.port, $c.health) -ForegroundColor $color
    } else {
        Write-Host ("  ── {0}" -f $c.name) -ForegroundColor $color
        Write-Host ("     role       : {0}" -f $c.role) -ForegroundColor Gray
        Write-Host ("     status     : {0}" -f $c.status) -ForegroundColor $color
        Write-Host ("     pid        : {0}" -f $c.pid)
        Write-Host ("     port       : {0}" -f $c.port)
        Write-Host ("     health     : {0}" -f $c.health) -ForegroundColor $color
        Write-Host ("     coverage   : {0}" -f $c.coverage) -ForegroundColor DarkGray
        Write-Host ("     authority  : {0}" -f $c.authority) -ForegroundColor DarkGray
        Write-Host ("     launch     : {0}" -f $c.launch_command) -ForegroundColor DarkGray
        Write-Host ("     logs       : {0}" -f $c.log_location) -ForegroundColor DarkGray
        Write-Host ("     shutdown   : {0}" -f $c.shutdown_command) -ForegroundColor DarkGray
        Write-Host ""
    }
}

if (-not $Quiet) {
    Write-Host "  ============================================================" -ForegroundColor Cyan
    $up    = ($components | Where-Object { $_.status -in @("UP","READY") }).Count
    $down  = ($components | Where-Object { $_.status -in @("DOWN","ABSENT") }).Count
    $unk   = ($components | Where-Object { $_.status -eq "UNKNOWN" }).Count
    Write-Host ("  RÉSUMÉ : {0} UP/READY  |  {1} DOWN/ABSENT  |  {2} UNKNOWN" -f $up, $down, $unk) -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  DÉMARRER la stack : pwsh -File scripts\obsidia.ps1" -ForegroundColor DarkGray
    Write-Host "  ARRÊTER la stack  : pwsh -File scripts\obsidia.ps1 stop" -ForegroundColor DarkGray
    Write-Host "  OBSIDURE seul     : pwsh -File scripts\run_agent_obsidure.ps1" -ForegroundColor DarkGray
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host ""
}
