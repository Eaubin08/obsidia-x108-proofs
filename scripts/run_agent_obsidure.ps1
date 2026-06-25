# scripts/run_agent_obsidure.ps1
# ==============================
# Lanceur PowerShell — Agent Obsidure CLI Standalone
# Usage :
#   .\scripts\run_agent_obsidure.ps1
#   .\scripts\run_agent_obsidure.ps1 -Objective "Créer le gate Bank P3-01"
#   .\scripts\run_agent_obsidure.ps1 -Domain TRADING -MaxCycles 2
#   .\scripts\run_agent_obsidure.ps1 -DryRun
#
# Prérequis :
#   - Python 3.10+  (python3 ou python dans le PATH)
#   - periphery/agents/agent_obsidure.py présent
#   - API Obsidia sur 8000 (optionnel — mode offline si absente)

param(
    [string]$Objective  = "",
    [string]$Domain     = "",
    [int]   $MaxCycles  = 0,
    [string]$Api        = "http://127.0.0.1:8000",
    [switch]$DryRun,
    [switch]$Quiet
)

# ── Résolution du repo root ────────────────────────────────────────────────
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot  = Split-Path -Parent $ScriptDir

# ── Variables d'environnement pour l'agent ────────────────────────────────
$env:OBSIDIA_API_BASE = $Api
$env:OBSIDURE_COLOR   = "1"
$env:PYTHONIOENCODING = "utf-8"

# ── Python disponible ? ───────────────────────────────────────────────────
$PythonCmd = $null
foreach ($candidate in @("python3", "python")) {
    if (Get-Command $candidate -ErrorAction SilentlyContinue) {
        $PythonCmd = $candidate
        break
    }
}
if (-not $PythonCmd) {
    Write-Error "Python introuvable dans le PATH. Installez Python 3.10+."
    exit 1
}

# ── Construction des arguments CLI ────────────────────────────────────────
$Args = @("$RepoRoot\scripts\obsidure_cli.py")

if ($Objective) { $Args += "--objective"; $Args += $Objective }
if ($Domain)    { $Args += "--domain";    $Args += $Domain    }
if ($MaxCycles -gt 0) { $Args += "--max-cycles"; $Args += "$MaxCycles" }
if ($DryRun)    { $Args += "--dry-run" }
if ($Quiet)     { $Args += "--quiet"   }
$Args += "--api"; $Args += $Api

# ── Lancement ────────────────────────────────────────────────────────────
Write-Host ""
Write-Host "  [OBSIDURE] Lancement depuis : $RepoRoot" -ForegroundColor Cyan
Write-Host "  [OBSIDURE] Python           : $PythonCmd" -ForegroundColor Cyan
Write-Host "  [OBSIDURE] API cible        : $Api"       -ForegroundColor Cyan
Write-Host "  [OBSIDURE] Kernel           : MUR DE BETON INTOUCHABLE" -ForegroundColor Yellow
Write-Host ""

Push-Location $RepoRoot
try {
    & $PythonCmd @Args
    $ExitCode = $LASTEXITCODE
} finally {
    Pop-Location
}

Write-Host ""
if ($ExitCode -eq 0) {
    Write-Host "  [OBSIDURE] Terminé correctement." -ForegroundColor Green
} elseif ($ExitCode -eq 2) {
    Write-Host "  [OBSIDURE] BLOC ABSOLU — chemin protégé détecté." -ForegroundColor Red
} elseif ($ExitCode -eq 3) {
    Write-Host "  [OBSIDURE] FAIL-CLOSED — backup échoué." -ForegroundColor Red
} else {
    Write-Host "  [OBSIDURE] Arrêt avec code $ExitCode." -ForegroundColor Yellow
}

exit $ExitCode
