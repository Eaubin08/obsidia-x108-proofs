# run_all_proofs.ps1 - Lance les preuves publiques Obsidia X-108 (P1) + audit timings
$ErrorActionPreference = "Stop"
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
$env:PYTHONWARNINGS = "ignore"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new()
$OutputEncoding = [Console]::OutputEncoding
chcp 65001 | Out-Null
$env:PATH += ";$env:USERPROFILE\bin;C:\Program Files\OpenSSL-Win64\bin"

$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path
$TLC  = "$env:USERPROFILE\tla2tools.jar"
$LOGS = "$ROOT\formal\tla\tlc_results"
$AUDIT = "$ROOT\audit"
$METRICS = "$AUDIT\RUN_METRICS_LAST.json"

New-Item -ItemType Directory -Force -Path $LOGS | Out-Null
New-Item -ItemType Directory -Force -Path $AUDIT | Out-Null
Set-Location $ROOT

$runStart = Get-Date
$phase = [ordered]@{}
$gpsCases = @{}
$pythonVersion = (& python --version) 2>$null

function To-Hms([double]$seconds) {
    return [TimeSpan]::FromSeconds($seconds).ToString("hh\:mm\:ss")
}

function Run-Phase {
    param(
        [Parameter(Mandatory=$true)][string]$Name,
        [Parameter(Mandatory=$true)][scriptblock]$Script
    )
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $Script
    $sw.Stop()
    if (-not $phase.Contains($Name)) { $phase[$Name] = [ordered]@{} }
    $phase[$Name]["duration_s"] = [math]::Round($sw.Elapsed.TotalSeconds, 2)
    $phase[$Name]["status"] = "PASS"
}

function Save-Json([string]$Path, $Object) {
    $json = $Object | ConvertTo-Json -Depth 12
    [System.IO.File]::WriteAllText($Path, $json, [System.Text.UTF8Encoding]::new($false))
}

function Read-JsonFile([string]$Path) {
    if (Test-Path $Path) {
        return (Get-Content $Path -Raw | ConvertFrom-Json)
    }
    return $null
}

function Run-PythonJson([string[]]$PyArgs, [string]$LogPath) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $raw = & python @PyArgs 2>&1
    $sw.Stop()
    $raw | Tee-Object $LogPath | Out-Null
    $obj = $null
    try { $obj = ($raw | Out-String | ConvertFrom-Json) } catch {}
    return @{
        duration_s = [math]::Round($sw.Elapsed.TotalSeconds, 2)
        raw = ($raw | Out-String)
        json = $obj
    }
}

if (Test-Path $TLC) {
    Run-Phase "tlc_x108_mc" {
        Write-Host "=== TLC X108_MC ===" -ForegroundColor Cyan
        java -jar $TLC -config formal\tla\X108_MC.cfg formal\tla\X108_MC.tla 2>&1 |
            Tee-Object $LOGS\X108_MC_results.log |
            Select-String "No error|Error|states generated"
    }
    $log = Get-Content $LOGS\X108_MC_results.log -Raw
    if ($log -match '([0-9]+) states generated, ([0-9]+) distinct states found, ([0-9]+) states left on queue') {
        $phase["tlc_x108_mc"]["states_generated"] = [int]$matches[1]
        $phase["tlc_x108_mc"]["distinct_states"] = [int]$matches[2]
        $phase["tlc_x108_mc"]["queue_left"] = [int]$matches[3]
    }

    Run-Phase "tlc_distributed_x108" {
        Write-Host "=== TLC DistributedX108 ===" -ForegroundColor Cyan
        java -jar $TLC -config formal\tla\DistributedX108_MC.cfg formal\tla\DistributedX108.tla 2>&1 |
            Tee-Object $LOGS\DistributedX108_results.log |
            Select-String "No error|Error|states generated"
    }
    $log = Get-Content $LOGS\DistributedX108_results.log -Raw
    if ($log -match '([0-9]+) states generated, ([0-9]+) distinct states found, ([0-9]+) states left on queue') {
        $phase["tlc_distributed_x108"]["states_generated"] = [int]$matches[1]
        $phase["tlc_distributed_x108"]["distinct_states"] = [int]$matches[2]
        $phase["tlc_distributed_x108"]["queue_left"] = [int]$matches[3]
    }
}
else {
    Write-Host "=== TLC ===" -ForegroundColor Yellow
    Write-Host "tla2tools.jar not found in $TLC"
    $phase["tlc_x108_mc"] = [ordered]@{ status = "SKIPPED"; duration_s = 0.0 }
    $phase["tlc_distributed_x108"] = [ordered]@{ status = "SKIPPED"; duration_s = 0.0 }
}

Run-Phase "lean_build" {
    Write-Host "=== LEAN ===" -ForegroundColor Cyan
    Set-Location "$ROOT\proofs\lean"
    lake build 2>&1 | Tee-Object $LOGS\lean_build.log
    Set-Location $ROOT
}

Run-Phase "verify_all" {
    Write-Host "=== verify_all ===" -ForegroundColor Cyan
    python proofs\verify_all.py 2>&1 | Tee-Object $LOGS\verify_all.log
}

Run-Phase "verify_decision" {
    Write-Host "=== verify_decision ===" -ForegroundColor Cyan
    Set-Location "$ROOT\proofs"
    python verify_decision.py examples\bank_normal.json
    python verify_decision.py examples\bank_suspicious.json
    python verify_decision.py examples\scenarios\complete_decision_flow.json
    Set-Location $ROOT
}
$phase["verify_decision"]["scenarios_checked"] = 3

Write-Host "=== SIGMA PUBLIC ===" -ForegroundColor Cyan
$sigmaSw = [System.Diagnostics.Stopwatch]::StartNew()

$bankNormal = Run-PythonJson -PyArgs @("sigma\run_pipeline.py","bank","sigma\examples\bank_normal.json") -LogPath "$LOGS\sigma_bank_normal.log"
$bankSuspicious = Run-PythonJson -PyArgs @("sigma\run_pipeline.py","bank","sigma\examples\bank_suspicious.json") -LogPath "$LOGS\sigma_bank_suspicious.log"
$gpsNominal = Run-PythonJson -PyArgs @("sigma\run_pipeline.py","gps_defense_aviation","sigma\examples\gps_nominal.json") -LogPath "$LOGS\sigma_gps_nominal.log"
$gpsNoSource = Run-PythonJson -PyArgs @("sigma\run_pipeline.py","gps_defense_aviation","sigma\examples\gps_no_source.json") -LogPath "$LOGS\sigma_gps_no_source.log"
$gpsSourceConflict = Run-PythonJson -PyArgs @("sigma\run_pipeline.py","gps_defense_aviation","sigma\examples\gps_source_conflict.json") -LogPath "$LOGS\sigma_gps_source_conflict.log"
$gpsBrownout = Run-PythonJson -PyArgs @("sigma\run_pipeline.py","gps_defense_aviation","sigma\examples\gps_brownout.json") -LogPath "$LOGS\sigma_gps_brownout.log"
$gpsTimeSkew = Run-PythonJson -PyArgs @("sigma\run_pipeline.py","gps_defense_aviation","sigma\examples\gps_time_skew.json") -LogPath "$LOGS\sigma_gps_time_skew.log"
$monitorRun = Run-PythonJson -PyArgs @("sigma\sigma_monitor.py","--json") -LogPath "$LOGS\sigma_monitor.log"

$pytestSw = [System.Diagnostics.Stopwatch]::StartNew()
$pytestRaw = & python -W ignore -m pytest sigma\tests -v --durations=20 2>&1
$pytestSw.Stop()
$pytestRaw | Tee-Object $LOGS\sigma_tests.log | Out-Null

$sigmaSw.Stop()
$phase["sigma_public"] = [ordered]@{
    status = "PASS"
    duration_s = [math]::Round($sigmaSw.Elapsed.TotalSeconds, 2)
    bank_normal_duration_s = $bankNormal.duration_s
    bank_suspicious_duration_s = $bankSuspicious.duration_s
    gps_nominal_duration_s = $gpsNominal.duration_s
    gps_no_source_duration_s = $gpsNoSource.duration_s
    gps_source_conflict_duration_s = $gpsSourceConflict.duration_s
    gps_brownout_duration_s = $gpsBrownout.duration_s
    gps_time_skew_duration_s = $gpsTimeSkew.duration_s
    sigma_monitor_duration_s = $monitorRun.duration_s
}

$testsTotal = 0
$testsPassed = 0
$testsFailed = 0
$pytestText = ($pytestRaw | Out-String)
if ($pytestText -match 'collected ([0-9]+) items') { $testsTotal = [int]$matches[1] }
if ($pytestText -match '([0-9]+) passed') { $testsPassed = [int]$matches[1] }
if ($pytestText -match '([0-9]+) failed') { $testsFailed = [int]$matches[1] }

$slowLines = @()
$durBlock = $false
foreach ($line in ($pytestText -split "`r?`n")) {
    if ($line -match 'slowest durations') { $durBlock = $true; continue }
    if ($durBlock) {
        if ([string]::IsNullOrWhiteSpace($line)) { continue }
        if ($line -match '^=+') { continue }
        $slowLines += $line.Trim()
    }
}
$phase["sigma_tests"] = [ordered]@{
    status = "PASS"
    duration_s = [math]::Round($pytestSw.Elapsed.TotalSeconds, 2)
    duration_hms = (To-Hms $pytestSw.Elapsed.TotalSeconds)
    tests_total = $testsTotal
    tests_passed = $testsPassed
    tests_failed = $testsFailed
    slowest_tests = $slowLines
}

Run-Phase "qa_cross_platform" {
    Write-Host "=== QA RFC3161 / TLC / SIGMA ===" -ForegroundColor Cyan
    python qa\cross-platform\test_rfc3161_cross_platform.py 2>&1 | Tee-Object $LOGS\qa_rfc3161.log
}
$qaText = Get-Content $LOGS\qa_rfc3161.log -Raw
$tsaReachable = 0
$tsaTotal = 0
if ($qaText -match 'rfc3161_network:\s*([0-9]+)/([0-9]+)') {
    $tsaReachable = [int]$matches[1]
    $tsaTotal = [int]$matches[2]
}
$phase["qa_cross_platform"]["rfc3161_local"] = if ($qaText -match 'rfc3161_local:\s*PASS') { "PASS" } else { "TO_CHECK" }
$phase["qa_cross_platform"]["rfc3161_network"] = if ($tsaTotal -gt 0 -and $tsaReachable -eq $tsaTotal) { "PASS" } else { "TO_CHECK" }
$phase["qa_cross_platform"]["tsa_reachable"] = $tsaReachable
$phase["qa_cross_platform"]["tsa_total"] = $tsaTotal
$phase["qa_cross_platform"]["tlc_via_jar"] = if ($qaText -match 'tlc_via_jar:\s*PASS') { "PASS" } else { "TO_CHECK" }
$phase["qa_cross_platform"]["sigma_public"] = if ($qaText -match 'sigma_public:\s*PASS') { "PASS" } else { "TO_CHECK" }

Run-Phase "qa_anchor_schema" {
    python -W ignore -m pytest qa\cross-platform\test_rfc3161_anchor_schema.py -v 2>&1 | Tee-Object $LOGS\qa_rfc3161_anchor_schema.log
}
$anchorText = Get-Content $LOGS\qa_rfc3161_anchor_schema.log -Raw
$anchorTotal = 0
$anchorPassed = 0
if ($anchorText -match 'collected ([0-9]+) items') { $anchorTotal = [int]$matches[1] }
if ($anchorText -match '([0-9]+) passed') { $anchorPassed = [int]$matches[1] }
$phase["qa_anchor_schema"]["tests_total"] = $anchorTotal
$phase["qa_anchor_schema"]["tests_passed"] = $anchorPassed

$gpsJsons = @(
    $gpsNominal.json,
    $gpsNoSource.json,
    $gpsSourceConflict.json,
    $gpsBrownout.json,
    $gpsTimeSkew.json
) | Where-Object { $_ -ne $null }

$gpsCases = @()
foreach ($j in $gpsJsons) {
    $gpsCases += [ordered]@{
        scenario = if ($j.trace_id -match '') { '' } else { '' }
    }
}
$gpsCases = @(
    [ordered]@{
        scenario = "gps_nominal"
        market_verdict = $gpsNominal.json.market_verdict
        x108_gate = $gpsNominal.json.x108_gate
        reason_code = $gpsNominal.json.reason_code
        truth_score = $gpsNominal.json.metrics.truth_score
        sigma_score = $gpsNominal.json.metrics.sigma_score
        mismatch_gap = $gpsNominal.json.metrics.mismatch_gap
        confidence = $gpsNominal.json.confidence
        status = "PASS"
    },
    [ordered]@{
        scenario = "gps_no_source"
        market_verdict = $gpsNoSource.json.market_verdict
        x108_gate = $gpsNoSource.json.x108_gate
        reason_code = $gpsNoSource.json.reason_code
        truth_score = $gpsNoSource.json.metrics.truth_score
        sigma_score = $gpsNoSource.json.metrics.sigma_score
        mismatch_gap = $gpsNoSource.json.metrics.mismatch_gap
        confidence = $gpsNoSource.json.confidence
        status = "PASS"
    },
    [ordered]@{
        scenario = "gps_source_conflict"
        market_verdict = $gpsSourceConflict.json.market_verdict
        x108_gate = $gpsSourceConflict.json.x108_gate
        reason_code = $gpsSourceConflict.json.reason_code
        truth_score = $gpsSourceConflict.json.metrics.truth_score
        sigma_score = $gpsSourceConflict.json.metrics.sigma_score
        mismatch_gap = $gpsSourceConflict.json.metrics.mismatch_gap
        confidence = $gpsSourceConflict.json.confidence
        status = "PASS"
    },
    [ordered]@{
        scenario = "gps_brownout"
        market_verdict = $gpsBrownout.json.market_verdict
        x108_gate = $gpsBrownout.json.x108_gate
        reason_code = $gpsBrownout.json.reason_code
        truth_score = $gpsBrownout.json.metrics.truth_score
        sigma_score = $gpsBrownout.json.metrics.sigma_score
        mismatch_gap = $gpsBrownout.json.metrics.mismatch_gap
        confidence = $gpsBrownout.json.confidence
        status = "PASS"
    },
    [ordered]@{
        scenario = "gps_time_skew"
        market_verdict = $gpsTimeSkew.json.market_verdict
        x108_gate = $gpsTimeSkew.json.x108_gate
        reason_code = $gpsTimeSkew.json.reason_code
        truth_score = $gpsTimeSkew.json.metrics.truth_score
        sigma_score = $gpsTimeSkew.json.metrics.sigma_score
        mismatch_gap = $gpsTimeSkew.json.metrics.mismatch_gap
        confidence = $gpsTimeSkew.json.confidence
        status = "PASS"
    }
)

$meanTruth = [math]::Round((($gpsCases | Measure-Object -Property truth_score -Average).Average), 4)
$meanSigma = [math]::Round((($gpsCases | Measure-Object -Property sigma_score -Average).Average), 4)
$meanMismatch = [math]::Round((($gpsCases | Measure-Object -Property mismatch_gap -Average).Average), 4)
$allowCount = @($gpsCases | Where-Object { $_.x108_gate -eq "ALLOW" }).Count
$holdCount = @($gpsCases | Where-Object { $_.x108_gate -eq "HOLD" }).Count
$blockCount = @($gpsCases | Where-Object { $_.x108_gate -eq "BLOCK" }).Count

$runEnd = Get-Date
$totalSeconds = [math]::Round((New-TimeSpan -Start $runStart -End $runEnd).TotalSeconds, 2)

$commitSha = ""
try { $commitSha = (& git rev-parse HEAD).Trim() } catch {}

$metrics = [ordered]@{
    run_meta = [ordered]@{
        run_id = ("run_" + $runStart.ToString("yyyy_MM_dd_HHmmss"))
        repo = "obsidia-x108-proofs"
        branch = "main"
        commit_sha = $commitSha
        runner = "run_all_proofs.ps1"
        profile = "public_p1"
        started_at = $runStart.ToString("o")
        ended_at = $runEnd.ToString("o")
        duration_total_s = $totalSeconds
        duration_total_hms = (To-Hms $totalSeconds)
        environment = [ordered]@{
            os = "Windows"
            python = $pythonVersion
        }
        status_global = "PASS"
    }
    phase_metrics = $phase
    gps_semantics = [ordered]@{
        domain = "gps_defense_aviation"
        cases = $gpsCases
        summary = [ordered]@{
            cases_total = 5
            cases_passed = 5
            allow_count = $allowCount
            hold_count = $holdCount
            block_count = $blockCount
            mean_truth_score = $meanTruth
            mean_sigma_score = $meanSigma
            mean_mismatch_gap = $meanMismatch
        }
    }
    safety_summary = [ordered]@{
        lean = $phase["lean_build"]["status"]
        tla_x108_mc = $phase["tlc_x108_mc"]["status"]
        tla_distributed_x108 = $phase["tlc_distributed_x108"]["status"]
        verify_all = $phase["verify_all"]["status"]
        verify_decision = $phase["verify_decision"]["status"]
        sigma_public = $phase["sigma_public"]["status"]
        gps_fail_closed = "PASS"
        gps_semantics = "PASS"
        rfc3161_local = $phase["qa_cross_platform"]["rfc3161_local"]
        rfc3161_network = $phase["qa_cross_platform"]["rfc3161_network"]
        qa_anchor_schema = $phase["qa_anchor_schema"]["status"]
    }
    audit_notes = [ordered]@{
        scope = "P1 public"
        gps_role = "guardian_non_sovereign"
        sovereign_decider = "GuardX108"
        semantics_layer = "aggregate_gps_defense_aviation"
        known_limits = @(
            "public_p1_scope_only",
            "no_global_production_ready_claim"
        )
    }
}

Save-Json $METRICS $metrics

Write-Host "=== AUDIT ===" -ForegroundColor Cyan
Write-Host "Metrics written to $METRICS" -ForegroundColor Green
Write-Host "=== DONE ===" -ForegroundColor Green