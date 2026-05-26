# Run Brody Memory Intake Gate — Dry Run
# Reads pending_candidates.jsonl from personal memory sidecar.
# Generates DRY_RUN_PLAN + GATE_REPORT. No writes to Neo4j/Graphiti.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $ScriptDir "..")
Set-Location $RepoRoot

Write-Host "Brody Memory Intake Gate — DRY RUN" -ForegroundColor Cyan
Write-Host "Source: _local_audits/BRODY_TERMINAL_CHAT_CLIENT_V1/personal_memory/pending_candidates.jsonl" -ForegroundColor DarkGray
Write-Host "Output: _local_audits/BRODY_PERSONAL_SIDECAR_TO_REAL_INTAKE_GATE_V1/" -ForegroundColor DarkGray
Write-Host "No writes. neo4j_write=False  graphiti_write=False" -ForegroundColor Green
Write-Host ""

python scripts/brody_memory_intake_gate.py dry-run
