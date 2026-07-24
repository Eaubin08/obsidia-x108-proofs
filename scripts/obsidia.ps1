# =============================================================================
# OBSIDIA COCKPIT V1.1 - Point d'entree unique du projet Obsidia X-108.
#
# Usage :
#   obsidia                     -> lance ou reutilise la stack + entre dans obsidia>
#   obsidia start               -> idem
#   obsidia restart             -> stop force + reboot + entre dans obsidia>
#   obsidia stop                -> stoppe les processus Obsidia (pas de shell)
#   obsidia open                -> ouvre les navigateurs UI/Graphiti/Neo4j
#   obsidia runtime             -> status runtime uniquement (pas de lancement)
#   obsidia status --full       -> idem
#   obsidia doctor --full       -> idem
#   obsidia cockpit status      -> idem
#   obsidia "<IN>"              -> route l'IN via le terminal CLI Python
#   obsidia --print-start-plan  -> affiche le plan de boot sans lancer
#
# Doctrine :
#   Terminal non souverain. X108 reste l'autorite finale.
#   Ce script PEUT lancer les serveurs car c'est une commande humaine explicite.
#   obsidia_cli.py ne lance JAMAIS de subprocess.
#   decision_authority = KX108_ONLY
#   Brody Enriched preferred -> -Base http://127.0.0.1:8000 (pas 8012)
#   Brody terminals = optionnels (non lances par defaut) - 'obsidia open' pour navigateurs
#   NEEDS_BACKGROUND_LOGGING_NEXT : logs services en fenetres visibles pour ce lot
# =============================================================================

$ErrorActionPreference = "Continue"

# --- Chemins canoniques -------------------------------------------------------
$ROOT    = "C:\Users\User\Desktop\obsidia-engine-proof-core"
$X108    = "$ROOT\obsidia-x108-proofs_REMOTE_A5F21C6B"
$RT      = "$X108\runtime_terrain_bank_trading_gps"
$SHELL   = "$ROOT\obsidiashell-main"
$UI_DIR  = "$X108\apps\obsidia-workbench"

# --- URLs canoniques ----------------------------------------------------------
$API             = "http://127.0.0.1:8000"
$KERNEL_URL      = "http://127.0.0.1:3001/kernel/ragnarok"
$GRAPH           = "http://127.0.0.1:8011"
$UI              = "http://127.0.0.1:5173"
$NEO4J_BROWSER   = "http://127.0.0.1:7475/browser/"
$NEO4J_BOLT      = "bolt://127.0.0.1:7688"
$GRAPH_WORKBENCH = "$GRAPH/graph/v20/frozen/workbench"
$GRAPH_DOCS      = "$GRAPH/docs"

# --- Ports canoniques ---------------------------------------------------------
# 3001 Kernel Ragnarok | 8000 API Obsidia/Brody | 8011 Graphiti | 5173 UI
# 7475 Neo4j Browser | 7688 Neo4j Bolt  (NE PAS tuer Neo4j par defaut)
# NOTE : 8012 = legacy non canonique - ne pas utiliser comme port principal
$PORTS_OBSIDIA = @(3001, 8000, 8011, 5173)

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================
function Write-ObsidiaHeader {
    param([string]$Title = "COCKPIT")
    Write-Host ""
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host "  OBSIDIA X-108 - $Title" -ForegroundColor Cyan
    Write-Host "  decision_authority = KX108_ONLY  |  terminal non souverain" -ForegroundColor DarkGray
    Write-Host "  ============================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step {
    param([string]$Tag, [string]$Msg)
    Write-Host "  [$Tag] $Msg" -ForegroundColor White
}

function Write-OK {
    param([string]$Msg)
    Write-Host "  [OK] $Msg" -ForegroundColor Green
}

function Write-WARN {
    param([string]$Msg)
    Write-Host "  [WARN] $Msg" -ForegroundColor Yellow
}

function Write-INFO {
    param([string]$Msg)
    Write-Host "       $Msg" -ForegroundColor Gray
}

# =============================================================================
# TEST STACK - Verifie si la stack est deja UP (ne lance rien)
# =============================================================================
function Test-ObsidiaStackRunning {
    try {
        Invoke-RestMethod "$API/api/health" -TimeoutSec 5 | Out-Null
        return $true
    } catch {
        return $false
    }
}

# =============================================================================
# ARRET - Stop uniquement les processus Obsidia (pas Neo4j)
# =============================================================================
function Stop-OldObsidiaProcesses {
    Write-Step "STOP" "Arret processus Obsidia precedents..."
    Get-CimInstance Win32_Process | Where-Object {
        $_.CommandLine -match "server\.kernel\.sealed\.cjs" -or
        $_.CommandLine -match "apps\.obsidia_api\.main:app" -or
        $_.CommandLine -match "connectors\\bank_normal_flow\.py" -or
        $_.CommandLine -match "connectors\\trading_live\.py" -or
        $_.CommandLine -match "connectors\\aviation_robo\.py" -or
        $_.CommandLine -match "obsidia_core\.agent_bridge:app" -or
        $_.CommandLine -match "npm run dev" -or
        $_.CommandLine -match "\\vite\\" -or
        $_.CommandLine -match "run_brody_terminal_chat\.ps1" -or
        $_.CommandLine -match "run_brody_terminal_enriched\.ps1" -or
        $_.CommandLine -match "run_brody_terminal\.ps1" -or
        $_.CommandLine -match "brody_terminal_chat\.py"
    } | ForEach-Object {
        Write-INFO "Arret PID=$($_.ProcessId)"
        Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

# =============================================================================
# PORTS - Liberer 3001/8000/8011/5173 uniquement
# =============================================================================
function Clear-ObsidiaPorts {
    Write-Step "PORT" "Liberation des ports Obsidia (3001/8000/8011/5173)..."
    foreach ($port in $PORTS_OBSIDIA) {
        $pids = netstat -ano 2>$null |
            Select-String ":$port\s" |
            Where-Object { $_.Line -match "LISTENING" } |
            ForEach-Object { ($_ -split "\s+")[-1] } |
            Sort-Object -Unique
        foreach ($pid_ in $pids) {
            if ($pid_ -and $pid_ -match "^\d+$" -and [int]$pid_ -ne 0) {
                Stop-Process -Id ([int]$pid_) -Force -ErrorAction SilentlyContinue
                Write-INFO "Port $port libere (PID $pid_)"
            }
        }
    }
    Start-Sleep -Seconds 2
}

# =============================================================================
# NEO4J - Docker deploy-neo4j-1 (warning seulement si absent)
# =============================================================================
function Start-Neo4jIfAvailable {
    Write-Step "NEO4J" "docker start deploy-neo4j-1  (7475/7688)..."
    try {
        docker start deploy-neo4j-1 | Out-Host
        Write-OK "Neo4j deploy-neo4j-1 demarre"
    } catch {
        Write-WARN "Docker non disponible ou deploy-neo4j-1 absent - continuez."
    }
    Start-Sleep -Seconds 3
}

# =============================================================================
# KERNEL RAGNAROK - 3001
# =============================================================================
function Start-KernelRagnarok {
    Write-Step "KERNEL" "Kernel Ragnarok - port 3001..."
    if (-not (Test-Path "$RT\server.kernel.sealed.cjs")) {
        Write-WARN "server.kernel.sealed.cjs absent dans $RT - Kernel 3001 non lance"
        return
    }
    Start-Process powershell -ArgumentList @(
        "-NoExit", "-Command",
        "[Console]::Title='RAGNAROK KERNEL 3001 - AUTHORITY'; Set-Location '$RT'; node .\server.kernel.sealed.cjs"
    )
    Write-OK "Kernel Ragnarok lance - port 3001"
    Start-Sleep -Seconds 4
}

# =============================================================================
# API OBSIDIA/BRODY - 8000
# =============================================================================
function Start-ObsidiaApiBrody {
    Write-Step "API" "API Obsidia/Brody - port 8000..."
    Start-Process powershell -ArgumentList @(
        "-NoExit", "-Command",
        "[Console]::Title='OBSIDIA API 8000 - BRODY LIVE KERNEL BRIDGE'; Set-Location '$X108'; `$env:PYTHONPATH='$X108'; `$env:OBSIDIA_KERNEL_URL='$KERNEL_URL'; python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000"
    )
    Write-OK "API Obsidia/Brody lancee - port 8000"
    Start-Sleep -Seconds 7
}

# =============================================================================
# TEST API + BRODY - GET health + POST Brody Chat
# POST Brody est autorise dans ce launcher PowerShell humain explicite.
# obsidia_cli.py n'a PAS ce droit.
# =============================================================================
function Test-ApiAndBrody {
    Write-Step "TEST" "Verification API 8000 + Brody Chat..."
    try {
        Invoke-RestMethod "$API/api/health" -TimeoutSec 10 | Out-Null
        Write-OK "API 8000 /api/health OK"
    } catch {
        Write-WARN "API 8000 /api/health : $($_.Exception.Message)"
    }
    # POST Brody Chat - autorise uniquement dans ce launcher PowerShell humain explicite
    # obsidia_cli.py n'a PAS ce droit (pas de POST Brody dans le terminal).
    try {
        $body = @{ message = "Test Brody readonly stack."; mode = "readonly_stack_launch"; compact = $true } |
            ConvertTo-Json -Depth 10 -Compress
        Invoke-RestMethod -Uri "$API/api/brody/chat" -Method POST `
            -ContentType "application/json; charset=utf-8" `
            -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) `
            -TimeoutSec 20 | Out-Null
        Write-OK "Brody V1 Chat /api/brody/chat OK"
    } catch {
        Write-WARN "Brody chat : $($_.Exception.Message)"
    }
}

# =============================================================================
# GRAPHITI / OBSIDIASHELL - 8011
# =============================================================================
function Start-Graphiti {
    Write-Step "GRAPHITI" "Graphiti/ObsidiaShell - port 8011..."
    if (-not (Test-Path $SHELL)) {
        Write-WARN "obsidiashell-main absent ($SHELL) - Graphiti 8011 non lance"
        return
    }
    Start-Process powershell -ArgumentList @(
        "-NoExit", "-Command",
        "[Console]::Title='OBSIDIASHELL GRAPHITI 8011'; Set-Location '$SHELL'; `$env:PYTHONPATH='$SHELL'; python -m uvicorn obsidia_core.agent_bridge:app --host 127.0.0.1 --port 8011 --log-level warning"
    )
    Write-OK "Graphiti lance - port 8011"
    Start-Sleep -Seconds 7
    try {
        Invoke-RestMethod "$GRAPH/graph/v20/frozen/status" -TimeoutSec 10 | Out-Null
        Write-OK "Graphiti 8011 /graph/v20/frozen/status OK"
    } catch {
        Write-WARN "Graphiti 8011 non repond encore : $($_.Exception.Message)"
    }
}

# =============================================================================
# UI WORKBENCH - 5173
# =============================================================================
function Start-WorkbenchUi {
    Write-Step "UI" "Workbench UI - port 5173..."
    if (-not (Test-Path $UI_DIR)) {
        Write-WARN "apps/obsidia-workbench absent ($UI_DIR) - UI 5173 non lancee"
        return
    }
    Start-Process powershell -ArgumentList @(
        "-NoExit", "-Command",
        "[Console]::Title='OBSIDIA WORKBENCH UI 5173'; Set-Location '$UI_DIR'; npm run dev -- --host 127.0.0.1 --port 5173"
    )
    Write-OK "UI lancee - port 5173"
    Start-Sleep -Seconds 8
    try {
        $uiStatus = (Invoke-WebRequest $UI -UseBasicParsing -TimeoutSec 10).StatusCode
        Write-OK "UI 5173 OK - status=$uiStatus"
    } catch {
        Write-WARN "UI 5173 non repond encore : $($_.Exception.Message)"
    }
}

# =============================================================================
# DOMAIN CONNECTORS - Bank / Trading / GPS-Aviation
# =============================================================================
function Start-DomainConnectors {
    Write-Step "DOMAINS" "Connecteurs Bank / Trading / GPS-Aviation..."
    if (-not (Test-Path "$X108\connectors")) {
        Write-WARN "connectors/ absent - connecteurs domaine non lances"
        return
    }
    foreach ($connector in @("bank_normal_flow.py", "trading_live.py", "aviation_robo.py")) {
        $path = "$X108\connectors\$connector"
        if (Test-Path $path) {
            Start-Process powershell -ArgumentList @(
                "-NoExit", "-Command",
                "[Console]::Title='$connector -> KERNEL BRIDGE 8000'; Set-Location '$X108'; `$env:PYTHONPATH='$X108'; `$env:OBSIDIA_API_BASE='$API'; python .\connectors\$connector"
            )
            Write-INFO "Connecteur $connector lance -> $API"
        } else {
            Write-WARN "Connecteur $connector absent : $path"
        }
    }
    Start-Sleep -Seconds 2
}

# =============================================================================
# BRODY TERMINALS - Chat / Enriched (preferred) / Raw Inspector
# Brody Enriched = version preferee - DOIT utiliser -Base $API (8000, pas 8012)
# NOTE : non lances par defaut dans le boot. Brody reste accessible via API 8000
#        et via le terminal obsidia>. Fenetres Brody optionnelles future.
# =============================================================================
function Start-BrodyTerminals {
    Write-Step "BRODY" "Terminaux Brody (Chat / Enriched / Raw Inspector)..."

    # Brody V1 Chat
    $script_chat = "$X108\scripts\run_brody_terminal_chat.ps1"
    if (Test-Path $script_chat) {
        Start-Process powershell -ArgumentList @(
            "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
            "[Console]::Title='BRODY V1 CHAT -> API 8000'; cd '$X108'; & '$script_chat' '$API'"
        )
        Write-OK "Brody V1 Chat -> $API"
    } else {
        Write-WARN "run_brody_terminal_chat.ps1 absent"
    }

    # Brody Enriched - version preferee - -Base $API (8000, pas 8012)
    $script_enriched = "$X108\scripts\run_brody_terminal_enriched.ps1"
    if (Test-Path $script_enriched) {
        Start-Process powershell -ArgumentList @(
            "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
            "[Console]::Title='BRODY ENRICHED -> API 8000 (PREFERRED)'; cd '$X108'; & '$script_enriched' -Base '$API'"
        )
        Write-OK "Brody Enriched -> $API  (preferred, pas 8012)"
    } else {
        Write-WARN "run_brody_terminal_enriched.ps1 absent"
    }

    # Brody Raw Inspector
    $script_raw = "$X108\scripts\run_brody_terminal.ps1"
    if (Test-Path $script_raw) {
        Start-Process powershell -ArgumentList @(
            "-NoExit", "-ExecutionPolicy", "Bypass", "-Command",
            "[Console]::Title='BRODY RAW INSPECTOR -> API 8000'; cd '$X108'; & '$script_raw' -Base '$API' -SessionId 'brody_terminal_raw_inspector'"
        )
        Write-OK "Brody Raw Inspector -> $API"
    } else {
        Write-WARN "run_brody_terminal.ps1 absent"
    }
}

# =============================================================================
# NAVIGATEURS - UI / Graphiti / Neo4j
# Appele uniquement via 'obsidia open' - pas dans le boot par defaut.
# =============================================================================
function Open-ObsidiaBrowsers {
    Write-Step "BROWSER" "Ouverture des navigateurs Obsidia..."
    foreach ($url in @($UI, $GRAPH_WORKBENCH, $GRAPH_DOCS, $NEO4J_BROWSER)) {
        try {
            Start-Process $url
            Write-INFO "Ouvert : $url"
        } catch {
            Write-WARN "Impossible d'ouvrir : $url"
        }
    }
}

# =============================================================================
# AFFICHAGE PORTS FINAUX
# =============================================================================
function Show-FinalPortsAndProcesses {
    Write-Host ""
    Write-Host "  --- PORTS CANONIQUES -------------------------------------------" -ForegroundColor Cyan
    Write-Host "  3001  Kernel Ragnarok      (X108 - autorite finale, KX108_ONLY)"
    Write-Host "  8000  API Obsidia/Brody    (Brody Enriched preferred)"
    Write-Host "  8011  Graphiti/ObsidiaShell"
    Write-Host "  5173  Workbench UI"
    Write-Host "  7475  Neo4j Browser        (Docker deploy-neo4j-1)"
    Write-Host "  7688  Neo4j Bolt           (Docker deploy-neo4j-1)"
    Write-Host "  NOTE  8012 = legacy non canonique - ne pas utiliser" -ForegroundColor Yellow
    Write-Host ""
    netstat -ano 2>$null | Select-String ":3001|:8000|:8011|:5173" |
        Where-Object { $_.Line -match "LISTENING" } | Out-Host
}

# =============================================================================
# STATUS RUNTIME VIA CLI PYTHON (lecture seule - aucun lancement)
# =============================================================================
function Invoke-ObsidiaRuntimeStatus {
    Write-Step "STATUS" "Carte runtime Obsidia (lecture seule - CLI Python)..."
    python "$X108\scripts\obsidia_cli.py" "runtime"
}

# =============================================================================
# AIDE COCKPIT
# =============================================================================
function Show-ObsidiaCockpitHelp {
    Write-Host ""
    Write-Host "  --- COCKPIT OBSIDIA V1.1 - COMMANDES RAPIDES ------------------" -ForegroundColor Cyan
    Write-Host "  Terminal  : (vous etes dans obsidia> - tapez directement)"
    Write-Host "  IN libre  : <votre demande>"
    Write-Host "  Runtime   : runtime"
    Write-Host "  Brody     : capabilities brody"
    Write-Host "  Obsidure  : peux tu coder"
    Write-Host "  Sigma     : sigma coherence"
    Write-Host "  OIE       : oie benchmark"
    Write-Host "  Lean      : preuves lean"
    Write-Host "  Domains   : domains bank trading gps"
    Write-Host "  Aide      : help"
    Write-Host "  Quitter   : exit"
    Write-Host ""
    Write-Host "  Depuis PowerShell : obsidia open  -> navigateurs"
    Write-Host "  Depuis PowerShell : obsidia stop  -> arrete la stack"
    Write-Host ""
    Write-Host "  decision_authority = KX108_ONLY | terminal non souverain" -ForegroundColor DarkGray
    Write-Host ""
}

# =============================================================================
# SHELL INTERACTIF - Entre dans obsidia> (sans argument = shell interactif CLI)
# =============================================================================
function Enter-ObsidiaInteractiveShell {
    Write-Step "SHELL" "Entree dans le terminal interactif Obsidia (TUI layout)..."
    Write-INFO "Tapez 'exit' ou Ctrl+C pour quitter. Retour PowerShell apres exit."
    python "$X108\scripts\obsidia_cli.py" --tui
}

# =============================================================================
# PLAN DE BOOT - imprime seulement, ne lance rien (utilise par les tests)
# =============================================================================
function Print-StartPlan {
    Write-ObsidiaHeader "PLAN DE BOOT (--print-start-plan)"
    Write-Host "  ATTENTION : affichage du plan uniquement - aucun service lance."
    Write-Host ""
    Write-Host "  COMPORTEMENT 'obsidia' / 'obsidia start' :" -ForegroundColor Cyan
    Write-Host "  ---------------------------------------------------------------"
    Write-Host "  A  Test-ObsidiaStackRunning -> si UP : boot skip, entre dans obsidia>"
    Write-Host "  B  Si DOWN : lance les services core suivants :"
    $plan = @(
        "01  docker start deploy-neo4j-1            ports 7475/7688  Neo4j Docker",
        "02  node server.kernel.sealed.cjs           port  3001       Kernel Ragnarok (X108 autorite)",
        "03  uvicorn apps.obsidia_api.main:app       port  8000       API Obsidia/Brody",
        "04  GET  $API/api/health                   test  API",
        "05  POST $API/api/brody/chat               test  Brody Chat (POST launcher humain uniquement)",
        "06  uvicorn obsidia_core.agent_bridge:app   port  8011       Graphiti/ObsidiaShell",
        "07  GET  $GRAPH/graph/v20/frozen/status    test  Graphiti",
        "08  npm run dev -- --host 127.0.0.1 --port 5173              UI Workbench",
        "09  GET  $UI                               test  UI",
        "10  python connectors\bank_normal_flow.py                    Bank connector",
        "11  python connectors\trading_live.py                        Trading connector",
        "12  python connectors\aviation_robo.py                       GPS/Aviation connector",
        "13  python scripts\obsidia_cli.py 'runtime'                  Carte runtime (lecture seule)",
        "14  python scripts\obsidia_cli.py           (sans arg)       Enter-ObsidiaInteractiveShell -> obsidia>"
    )
    foreach ($s in $plan) { Write-Host "  $s" }
    Write-Host ""
    Write-Host "  NON LANCES PAR DEFAUT (optionnels) :" -ForegroundColor DarkGray
    Write-Host "  -  run_brody_terminal_*.ps1  (Brody accessible via API 8000 et obsidia>)"
    Write-Host "  -  navigateurs  (utiliser 'obsidia open')"
    Write-Host ""
    Write-Host "  COMPORTEMENT 'obsidia restart' :" -ForegroundColor Cyan
    Write-Host "  Stop-OldObsidiaProcesses + Clear-ObsidiaPorts + boot complet + obsidia>"
    Write-Host ""
    Write-Host "  COMPORTEMENT 'obsidia stop' :" -ForegroundColor Cyan
    Write-Host "  Stop-OldObsidiaProcesses + Clear-ObsidiaPorts"
    Write-Host ""
    Write-Host "  COMPORTEMENT 'obsidia open' :" -ForegroundColor Cyan
    Write-Host "  Open-ObsidiaBrowsers (UI / Graphiti / Neo4j)"
    Write-Host ""
    Write-Host "  AUTORITE : decision_authority = KX108_ONLY" -ForegroundColor Yellow
    Write-Host "  LEGACY   : 8012 = non canonique" -ForegroundColor Yellow
    Write-Host "  BRODY    : Enriched preferred -> -Base http://127.0.0.1:8000" -ForegroundColor Yellow
    Write-Host ""
}

# =============================================================================
# FULL STACK BOOT
# Si -ForceRestart : kill + clear ports avant de lancer
# Sinon : verifie si stack UP, skip si deja active
# NOTE : Brody terminals et navigateurs NON lances par defaut
# =============================================================================
function Start-ObsidiaFullStack {
    param([switch]$ForceRestart)

    if ($ForceRestart) {
        Write-ObsidiaHeader "COCKPIT RESTART - FORCE"
        Stop-OldObsidiaProcesses
        Clear-ObsidiaPorts
    } else {
        if (Test-ObsidiaStackRunning) {
            Write-ObsidiaHeader "COCKPIT - STACK DEJA ACTIVE"
            Write-OK "Stack deja active - boot skip (API 8000 repond)"
            Write-INFO "Pour forcer un restart : obsidia restart"
            Write-INFO "Pour arreter la stack  : obsidia stop"
            return
        }
        Write-ObsidiaHeader "COCKPIT BOOT - FULL STACK"
    }

    Start-Neo4jIfAvailable
    Start-KernelRagnarok
    Start-ObsidiaApiBrody
    Test-ApiAndBrody
    Start-Graphiti
    Start-WorkbenchUi
    Start-DomainConnectors
    # NOTE: Brody terminals non lances par defaut.
    # Brody reste accessible via API 8000 et via le terminal obsidia>.
    # Brody Enriched preferred - -Base http://127.0.0.1:8000 (pas 8012).
    # Pour lancer les fenetres Brody manuellement : Start-BrodyTerminals
    # NOTE: Navigateurs non ouverts par defaut.
    # Pour ouvrir les navigateurs : obsidia open
    Show-FinalPortsAndProcesses
}

# =============================================================================
# POINT D'ENTREE PRINCIPAL
# =============================================================================
$_first = if ($args.Count -gt 0) { $args[0].ToLower().Trim() } else { "" }

if ($args.Count -eq 0 -or $_first -eq "start") {
    # Boot conditionnel (skip si UP) + runtime + aide + shell interactif
    Start-ObsidiaFullStack
    Invoke-ObsidiaRuntimeStatus
    Show-ObsidiaCockpitHelp
    Enter-ObsidiaInteractiveShell

} elseif ($_first -eq "restart") {
    # Force stop + reboot complet + runtime + aide + shell interactif
    Start-ObsidiaFullStack -ForceRestart
    Invoke-ObsidiaRuntimeStatus
    Show-ObsidiaCockpitHelp
    Enter-ObsidiaInteractiveShell

} elseif ($_first -eq "stop") {
    # Stop uniquement - pas de shell
    Write-ObsidiaHeader "COCKPIT STOP"
    Stop-OldObsidiaProcesses
    Clear-ObsidiaPorts
    Write-OK "Stack Obsidia arretee."

} elseif ($_first -eq "open") {
    # Navigateurs uniquement
    Open-ObsidiaBrowsers

} elseif ($_first -eq "--print-start-plan") {
    # Plan uniquement - ne lance rien
    Print-StartPlan

} elseif ($_first -eq "chat") {
    # Gateway fusionne : router pre-inference -> memory -> brody -> claude -p
    # Level 0/2 repondus localement (0 token). Escalade LLM uniquement si necessaire.
    # POST Brody active ici : 'obsidia chat' est un lanceur humain explicite
    # (meme statut doctrinal que les launchers PowerShell Brody).
    Write-ObsidiaHeader "GATEWAY CHAT - COURT-CIRCUIT PRE-INFERENCE"
    $env:OBSIDIA_GATEWAY_ALLOW_BRODY_POST = "1"
    $env:OBSIDIA_BRODY_BASE = $API
    $rest = if ($args.Count -gt 1) { $args[1..($args.Count - 1)] } else { @() }
    python "$X108\scripts\obsidia_gateway.py" @rest

} else {
    # runtime / status / doctor / cockpit + tous les IN libres -> CLI Python
    python "$X108\scripts\obsidia_cli.py" @args
}
