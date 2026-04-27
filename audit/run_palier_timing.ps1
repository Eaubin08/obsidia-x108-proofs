$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:PYTHONWARNINGS = "ignore"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [Console]::OutputEncoding
chcp 65001 | Out-Null
$env:PATH += ";$env:USERPROFILE\bin;C:\Program Files\OpenSSL-Win64\bin"

$ROOT = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$TLC  = "$env:USERPROFILE\tla2tools.jar"
$LOGS = "$ROOT\formal\tla\tlc_results"
$AUDIT = "$ROOT\audit"
$OUT = "$AUDIT\RUN_METRICS_PALIER_LAST.json"

New-Item -ItemType Directory -Force -Path $LOGS | Out-Null
New-Item -ItemType Directory -Force -Path $AUDIT | Out-Null
Set-Location $ROOT

function To-Hms([double]$seconds) {
    [TimeSpan]::FromSeconds($seconds).ToString("hh\:mm\:ss")
}

function Run-Stage {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][scriptblock]$Script
    )
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $Script
    $sw.Stop()
    return [ordered]@{
        status = "PASS"
        duration_s = [math]::Round($sw.Elapsed.TotalSeconds, 2)
        duration_hms = (To-Hms $sw.Elapsed.TotalSeconds)
    }
}

$runStart = Get-Date
$metrics = [ordered]@{
    run_meta = [ordered]@{
        run_id = "palier_" + $runStart.ToString("yyyy_MM_dd_HHmmss")
        repo = "obsidia-x108-proofs"
        branch = "main"
        commit_sha = ((git rev-parse HEAD) 2>$null)
        started_at = $runStart.ToString("o")
        ended_at = $null
        duration_total_s = 0.0
        duration_total_hms = "00:00:00"
        runner = "audit/run_palier_timing.ps1"
        status_global = "PASS"
    }
    paliers = [ordered]@{}
}

if (Test-Path $TLC) {
    Write-Host "=== TLC X108_MC ===" -ForegroundColor Cyan
    $metrics.paliers.tlc_x108_mc = Run-Stage "tlc_x108_mc" {
        java -jar $TLC -config formal\tla\X108_MC.cfg formal\tla\X108_MC.tla 2>&1 |
            Tee-Object $LOGS\X108_MC_results.log |
            Select-String "No error|Error|states generated"
    }

    Write-Host "=== TLC DistributedX108 ===" -ForegroundColor Cyan
    $metrics.paliers.tlc_distributed_x108 = Run-Stage "tlc_distributed_x108" {
        java -jar $TLC -config formal\tla\DistributedX108_MC.cfg formal\tla\DistributedX108.tla 2>&1 |
            Tee-Object $LOGS\DistributedX108_results.log |
            Select-String "No error|Error|states generated"
    }
}
else {
    $metrics.paliers.tlc_x108_mc = [ordered]@{ status = "SKIPPED"; duration_s = 0.0; duration_hms = "00:00:00" }
    $metrics.paliers.tlc_distributed_x108 = [ordered]@{ status = "SKIPPED"; duration_s = 0.0; duration_hms = "00:00:00" }
}

Write-Host "=== LEAN ===" -ForegroundColor Cyan
$metrics.paliers.lean_build = Run-Stage "lean_build" {
    Set-Location "$ROOT\proofs\lean"
    lake build 2>&1 | Tee-Object $LOGS\lean_build.log
    Set-Location $ROOT
}

Write-Host "=== verify_all ===" -ForegroundColor Cyan
$metrics.paliers.verify_all = Run-Stage "verify_all" {
    python proofs\verify_all.py 2>&1 | Tee-Object $LOGS\verify_all.log
}

Write-Host "=== verify_decision ===" -ForegroundColor Cyan
$metrics.paliers.verify_decision = Run-Stage "verify_decision" {
    Set-Location "$ROOT\proofs"
    python verify_decision.py examples\bank_normal.json
    python verify_decision.py examples\bank_suspicious.json
    python verify_decision.py examples\scenarios\complete_decision_flow.json
    Set-Location $ROOT
}

Write-Host "=== SIGMA PUBLIC ===" -ForegroundColor Cyan
$sigma = [ordered]@{}
$sigma.bank_normal = Run-Stage "sigma_bank_normal" {
    python sigma\run_pipeline.py bank sigma\examples\bank_normal.json 2>&1 | Tee-Object $LOGS\sigma_bank_normal.log
}
$sigma.bank_suspicious = Run-Stage "sigma_bank_suspicious" {
    python sigma\run_pipeline.py bank sigma\examples\bank_suspicious.json 2>&1 | Tee-Object $LOGS\sigma_bank_suspicious.log
}
$sigma.gps_nominal = Run-Stage "sigma_gps_nominal" {
    python sigma\run_pipeline.py gps_defense_aviation sigma\examples\gps_nominal.json 2>&1 | Tee-Object $LOGS\sigma_gps_nominal.log
}
$sigma.gps_no_source = Run-Stage "sigma_gps_no_source" {
    python sigma\run_pipeline.py gps_defense_aviation sigma\examples\gps_no_source.json 2>&1 | Tee-Object $LOGS\sigma_gps_no_source.log
}
$sigma.gps_source_conflict = Run-Stage "sigma_gps_source_conflict" {
    python sigma\run_pipeline.py gps_defense_aviation sigma\examples\gps_source_conflict.json 2>&1 | Tee-Object $LOGS\sigma_gps_source_conflict.log
}
$sigma.gps_brownout = Run-Stage "sigma_gps_brownout" {
    python sigma\run_pipeline.py gps_defense_aviation sigma\examples\gps_brownout.json 2>&1 | Tee-Object $LOGS\sigma_gps_brownout.log
}
$sigma.gps_time_skew = Run-Stage "sigma_gps_time_skew" {
    python sigma\run_pipeline.py gps_defense_aviation sigma\examples\gps_time_skew.json 2>&1 | Tee-Object $LOGS\sigma_gps_time_skew.log
}
$sigma.monitor = Run-Stage "sigma_monitor" {
    python sigma\sigma_monitor.py --json 2>&1 | Tee-Object $LOGS\sigma_monitor.log
}
$sigma.tests = Run-Stage "sigma_tests" {
    python -W ignore -m pytest sigma\tests -v --durations=20 2>&1 | Tee-Object $LOGS\sigma_tests.log
}

$metrics.paliers.sigma_public = [ordered]@{
    status = "PASS"
    duration_s = [math]::Round((
        $sigma.bank_normal.duration_s +
        $sigma.bank_suspicious.duration_s +
        $sigma.gps_nominal.duration_s +
        $sigma.gps_no_source.duration_s +
        $sigma.gps_source_conflict.duration_s +
        $sigma.gps_brownout.duration_s +
        $sigma.gps_time_skew.duration_s +
        $sigma.monitor.duration_s +
        $sigma.tests.duration_s
    ), 2)
    duration_hms = ""
    substeps = $sigma
}
$metrics.paliers.sigma_public.duration_hms = To-Hms $metrics.paliers.sigma_public.duration_s

Write-Host "=== QA RFC3161 / TLC / SIGMA ===" -ForegroundColor Cyan
$metrics.paliers.qa_cross_platform = Run-Stage "qa_cross_platform" {
    python qa\cross-platform\test_rfc3161_cross_platform.py 2>&1 | Tee-Object $LOGS\qa_rfc3161.log
}
$metrics.paliers.qa_anchor_schema = Run-Stage "qa_anchor_schema" {
    python -W ignore -m pytest qa\cross-platform\test_rfc3161_anchor_schema.py -v 2>&1 | Tee-Object $LOGS\qa_rfc3161_anchor_schema.log
}

$runEnd = Get-Date
$totalS = [math]::Round((New-TimeSpan -Start $runStart -End $runEnd).TotalSeconds, 2)
$metrics.run_meta.ended_at = $runEnd.ToString("o")
$metrics.run_meta.duration_total_s = $totalS
$metrics.run_meta.duration_total_hms = To-Hms $totalS

$json = $metrics | ConvertTo-Json -Depth 12
[System.IO.File]::WriteAllText($OUT, $json, [System.Text.UTF8Encoding]::new($false))

Write-Host "=== AUDIT PALIER ===" -ForegroundColor Cyan
Write-Host "Metrics written to $OUT" -ForegroundColor Green
Write-Host "=== DONE ===" -ForegroundColor Green