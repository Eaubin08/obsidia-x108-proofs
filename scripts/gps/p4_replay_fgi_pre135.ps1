param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

$Image = "carlesfernandez/docker-gnsssdr:latest"
$ExpectedSha256 = "e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72"
$Input = Join-Path $RepoRoot "hackathons\nativebuilder-gps-defense\data\fgi-spoofrepo\pipeline_inputs\case_0001_l1e1_real8.dat"
$BaseConfig = Join-Path $RepoRoot "hackathons\nativebuilder-gps-defense\gnss_sdr_fgi_ut_dfmc_l1e1_official_gpsl1_pre135_real8_runtime.conf"
$OutDir = Join-Path $RepoRoot ".local\p4-replay\fgi-pre135"
$RuntimeConfig = Join-Path $OutDir "receiver_pre135_runtime.conf"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "Docker executable not found." }
if (-not (Test-Path -LiteralPath $Input -PathType Leaf)) { throw "Relinked FGI pipeline input not found. Run p4_relink_fgi_source.ps1 first." }
if (-not (Test-Path -LiteralPath $BaseConfig -PathType Leaf)) { throw "P4 pre-135 GNSS-SDR config not found: $BaseConfig" }

$inputHash = (Get-FileHash -LiteralPath $Input -Algorithm SHA256).Hash.ToLowerInvariant()
if ($inputHash -ne $ExpectedSha256) { throw "FGI pipeline input hash mismatch. Refusing replay." }

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$configText = Get-Content -LiteralPath $BaseConfig -Raw
$historicalOutputPrefix = "/work/hackathons/nativebuilder-gps-defense/rf_attack_benchmark/gnss_sdr_runs/fgi_ut_dfmc_l1e1_pre135_real8"
$configText = $configText.Replace($historicalOutputPrefix, ".")
Set-Content -LiteralPath $RuntimeConfig -Value $configText -Encoding UTF8

Write-Host "=== P4 FGI PRE-135 REPLAY ==="
Write-Host "INPUT_SHA256 = $inputHash"
Write-Host "CONFIG       = $RuntimeConfig"
Write-Host "OUTPUT       = $OutDir"
Write-Host "IMAGE        = $Image"
Write-Host ""
Write-Host "Historical benchmark outputs remain untouched; runtime output is isolated under .local/."

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    & docker run --rm `
        -v "${RepoRoot}:/work:ro" `
        -v "${OutDir}:/out" `
        -w /out `
        $Image `
        gnss-sdr `
        --config_file=/out/receiver_pre135_runtime.conf `
        --log_dir=/out 2>&1 |
        Tee-Object -FilePath (Join-Path $OutDir "gnss_sdr_stdout.log")
    $dockerExitCode = $LASTEXITCODE
}
finally {
    $ErrorActionPreference = $previousErrorActionPreference
}

if ($dockerExitCode -ne 0) { throw "GNSS-SDR replay exited with code $dockerExitCode" }

Write-Host ""
Write-Host "REPLAY_PROCESS_EXIT_OK = True"
Write-Host "OUTPUT_DIR = $OutDir"
Write-Host "This is a recorded-RF replay only; no P2 live-passive or P4 classification closure is claimed."
