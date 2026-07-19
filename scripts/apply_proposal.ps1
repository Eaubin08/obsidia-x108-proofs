param (
    [Parameter(Mandatory=$true)]
    [ValidatePattern('^[A-Za-z0-9_.-]+$')]
    [string]$ProposalId,

    [switch]$DryRun,
    [switch]$ConfirmApply
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
$ProposalRoot = Join-Path $RepoRoot "_PATCH_PROPOSALS"
$proposalDir = Join-Path $ProposalRoot $ProposalId
$jsonPath = Join-Path $proposalDir "proposal.json"

function Block($Message) {
    Write-Host "[BLOCK] $Message" -ForegroundColor Red
    exit 1
}

function Info($Message) {
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Ok($Message) {
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Warn($Message) {
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Resolve-InRepoTarget([string]$RelativePath) {
    if ([string]::IsNullOrWhiteSpace($RelativePath)) {
        Block "Patch target vide."
    }
    if ([System.IO.Path]::IsPathRooted($RelativePath)) {
        Block "Chemin absolu interdit: $RelativePath"
    }
    if ($RelativePath -match '(^|[\\/])\.\.([\\/]|$)') {
        Block "Chemin parent '..' interdit: $RelativePath"
    }
    if ($RelativePath -match '(^|[\\/])server\.kernel\.sealed(\.cjs)?$') {
        Block "Kernel sealed interdit: $RelativePath"
    }
    if ($RelativePath -match '(^|[\\/])(kernel|x108)([\\/]|$)') {
        Block "Mutation kernel/X108 interdite: $RelativePath"
    }

    $candidate = Join-Path $RepoRoot $RelativePath
    $parent = Split-Path $candidate -Parent
    if (-not (Test-Path $parent)) {
        New-Item -ItemType Directory -Force -Path $parent | Out-Null
    }

    $resolvedParent = (Resolve-Path $parent).Path
    if (-not $resolvedParent.StartsWith($RepoRoot.Path, [System.StringComparison]::OrdinalIgnoreCase)) {
        Block "Target hors repo interdite: $RelativePath"
    }

    return $candidate
}

function Resolve-InProposalSource([string]$SourcePath) {
    if ([string]::IsNullOrWhiteSpace($SourcePath)) {
        return $null
    }

    $candidate = if ([System.IO.Path]::IsPathRooted($SourcePath)) {
        $SourcePath
    } else {
        Join-Path $RepoRoot $SourcePath
    }

    if (-not (Test-Path $candidate)) {
        return $null
    }

    $resolved = (Resolve-Path $candidate).Path
    $resolvedProposal = (Resolve-Path $proposalDir).Path
    if (-not $resolved.StartsWith($resolvedProposal, [System.StringComparison]::OrdinalIgnoreCase)) {
        Block "Source hors proposal interdite: $SourcePath"
    }

    return $resolved
}

if (-not (Test-Path $jsonPath)) {
    Block "Proposal introuvable: $jsonPath"
}

if (-not $ConfirmApply) {
    $DryRun = $true
}

$json = Get-Content $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json

if (-not $json.patches) {
    Block "proposal.json ne contient aucun champ patches."
}

Info "OBSIDURE APPLY PROPOSAL — HUMAN APPROVED WRITE"
Info "ProposalId: $ProposalId"
Info "Mode: $(if ($DryRun) { 'DRY_RUN' } else { 'CONFIRMED_APPLY' })"
Info "RepoRoot: $($RepoRoot.Path)"
Write-Host ""

$plan = @()
foreach ($patch in $json.patches) {
    $srcResolved = Resolve-InProposalSource ([string]$patch.sandbox_path)
    $dstResolved = Resolve-InRepoTarget ([string]$patch.path)

    $plan += [pscustomobject]@{
        Source = $srcResolved
        Target = $dstResolved
        TargetRelative = [string]$patch.path
        HasSource = [bool]$srcResolved
    }
}

Write-Host "PLAN:"
foreach ($item in $plan) {
    if ($item.HasSource) {
        Write-Host "  COPY  $($item.Source) -> $($item.TargetRelative)"
    } else {
        Write-Host "  SKIP  $($item.TargetRelative)  (pas de sandbox_path existant)"
    }
}

Write-Host ""
if ($DryRun) {
    Warn "DRY_RUN actif : aucun fichier copié."
    Warn "Pour appliquer réellement : .\scripts\apply_proposal.ps1 -ProposalId $ProposalId -ConfirmApply"
    exit 0
}

if (-not $ConfirmApply) {
    Block "Apply réel bloqué sans -ConfirmApply."
}

$appliedCount = 0
foreach ($item in $plan) {
    if ($item.HasSource) {
        Copy-Item -Path $item.Source -Destination $item.Target -Force
        Ok "Appliqué: $($item.TargetRelative)"
        $appliedCount++
    } else {
        Warn "Ignoré: $($item.TargetRelative)"
    }
}

Ok "Proposal terminé. Fichiers copiés: $appliedCount"
Warn "Aucun git add, commit ou push n'a été exécuté."
