param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"
$Freeze = Join-Path $RepoRoot "hackathons\nativebuilder-gps-defense\rf_attack_benchmark\p4_temporal_classifier_freeze_v0.json"
$ReplayLog = Join-Path $RepoRoot ".local\p4-heldout\mcd\replay\gnss_sdr_stdout.log"
$OutDir = Join-Path $RepoRoot ".local\p4-heldout\mcd\validation"
$Detection = Join-Path $OutDir "detection.json"
$Evidence = Join-Path $OutDir "domain_evidence.json"
$Gate = Join-Path $OutDir "domain_gate_result.json"

if (-not (Test-Path -LiteralPath $Freeze -PathType Leaf)) { throw "Frozen classifier manifest missing." }
if (-not (Test-Path -LiteralPath $ReplayLog -PathType Leaf)) { throw "Held-out replay log missing. Run p4_replay_fgi_heldout_mcd.ps1 first." }

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

python (Join-Path $RepoRoot "scripts\gps\p4_validate_frozen_temporal_classifier.py") --freeze $Freeze --log $ReplayLog --out $Detection
if ($LASTEXITCODE -ne 0) { throw "Frozen temporal classifier validation failed." }

python (Join-Path $RepoRoot "scripts\gps\p4_temporal_detection_to_domain_evidence.py") --detection $Detection --out $Evidence
if ($LASTEXITCODE -ne 0) { throw "Temporal domain evidence generation failed." }

python (Join-Path $RepoRoot "scripts\gps\p4_temporal_domain_gate_replay.py") --evidence $Evidence --out $Gate
if ($LASTEXITCODE -ne 0) { throw "Temporal DomainState replay failed." }

Write-Host ""
Write-Host "HELDOUT_VALIDATION_COMPLETE = True"
Write-Host "DETECTION = $Detection"
Write-Host "DOMAIN_EVIDENCE = $Evidence"
Write-Host "DOMAIN_GATE = $Gate"
Write-Host "No recalibration was performed."
