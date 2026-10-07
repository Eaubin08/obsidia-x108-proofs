param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

$Image = "carlesfernandez/docker-gnsssdr:latest"
$Input = Join-Path $RepoRoot "hackathons\nativebuilder-gps-defense\data\fgi-spoofrepo\pipeline_inputs\case_mcd_l1e1_real8.dat"
$SourceManifest = Join-Path $RepoRoot ".local\p4-heldout\mcd\source_manifest.json"
$BaseConfig = Join-Path $RepoRoot "hackathons\nativebuilder-gps-defense\gnss_sdr_fgi_meaconing_dfmc_l1e1_full_real8_runtime.conf"
$OutDir = Join-Path $RepoRoot ".local\p4-heldout\mcd\replay"
$RuntimeConfig = Join-Path $OutDir "receiver_full_real8_runtime.conf"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "Docker executable not found." }
if (-not (Test-Path -LiteralPath $Input -PathType Leaf)) { throw "Held-out MCD canonical input not found. Run p4_relink_fgi_heldout_mcd.ps1 first." }
if (-not (Test-Path -LiteralPath $SourceManifest -PathType Leaf)) { throw "Held-out MCD source manifest missing." }
if (-not (Test-Path -LiteralPath $BaseConfig -PathType Leaf)) { throw "MCD real8 config missing: $BaseConfig" }

$manifest = Get-Content -LiteralPath $SourceManifest -Raw | ConvertFrom-Json
$inputHash = (Get-FileHash -LiteralPath $Input -Algorithm SHA256).Hash.ToLowerInvariant()
if ($inputHash -ne [string]$manifest.input_sha256) { throw "Held-out MCD input hash no longer matches the pre-execution source manifest." }

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$configText = Get-Content -LiteralPath $BaseConfig -Raw
$historicalOutputPrefix = "/work/hackathons/nativebuilder-gps-defense/rf_attack_benchmark/gnss_sdr_runs/fgi_meaconing_dfmc_l1e1_full_real8"
$configText = $configText.Replace($historicalOutputPrefix, ".")
Set-Content -LiteralPath $RuntimeConfig -Value $configText -Encoding UTF8

Write-Host "=== P4 HELD-OUT FULL REAL8 REPLAY ==="
Write-Host "INPUT_SHA256 = $inputHash"
Write-Host "CLASSIFIER = P4_TEMPORAL_DISCONTINUITY_V0 (frozen)"
Write-Host "TRUTH_LABEL_VISIBLE_TO_REPLAY = False"
Write-Host "OUTPUT = $OutDir"

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    $dockerArgs = @("run","--rm","-v","${RepoRoot}:/work:ro","-v","${OutDir}:/out","-w","/out",$Image,"gnss-sdr","--config_file=/out/receiver_full_real8_runtime.conf","--log_dir=/out")
    & docker @dockerArgs 2>&1 | Tee-Object -FilePath (Join-Path $OutDir "gnss_sdr_stdout.log")
    $dockerExitCode = $LASTEXITCODE
}
finally { $ErrorActionPreference = $previousErrorActionPreference }

if ($dockerExitCode -ne 0) { throw "GNSS-SDR held-out replay exited with code $dockerExitCode" }

$stdoutPath = Join-Path $OutDir "gnss_sdr_stdout.log"
$stdoutText = Get-Content -LiteralPath $stdoutPath -Raw -ErrorAction SilentlyContinue
foreach ($pattern in @("Unable to connect flowgraph","configuration file is not well defined","itemsize mismatch")) {
    if ($stdoutText -match [regex]::Escape($pattern)) { throw "GNSS-SDR held-out replay failed despite process exit code 0: $pattern" }
}

Write-Host ""
Write-Host "REPLAY_PROCESS_EXIT_OK = True"
Write-Host "OUTPUT_LOG = $stdoutPath"
Write-Host "No truth label or attack onset was supplied to receiver processing."
