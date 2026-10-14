param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"
$Image = "carlesfernandez/docker-gnsssdr:latest"
$ExpectedSha256 = "e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72"
$Input = Join-Path $RepoRoot "hackathons\nativebuilder-gps-defense\data\fgi-spoofrepo\pipeline_inputs\case_0001_l1e1_real8.dat"
$BaseConfig = Join-Path $RepoRoot "hackathons\nativebuilder-gps-defense\gnss_sdr_fgi_ut_dfmc_l1e1_full_real8_runtime.conf"
$OutDir = Join-Path $RepoRoot ".local\p4-replay\fgi-full-real8"
$RuntimeConfig = Join-Path $OutDir "receiver_full_real8_runtime.conf"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw "Docker executable not found." }
if (-not (Test-Path -LiteralPath $Input -PathType Leaf)) { throw "Relinked FGI input not found. Run p4_relink_fgi_source.ps1 first." }
if (-not (Test-Path -LiteralPath $BaseConfig -PathType Leaf)) { throw "Full real8 config not found: $BaseConfig" }

$inputHash = (Get-FileHash -LiteralPath $Input -Algorithm SHA256).Hash.ToLowerInvariant()
if ($inputHash -ne $ExpectedSha256) { throw "FGI pipeline input hash mismatch. Refusing replay." }

New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$configText = Get-Content -LiteralPath $BaseConfig -Raw
$historicalOutputPrefix = "/work/hackathons/nativebuilder-gps-defense/rf_attack_benchmark/gnss_sdr_runs/fgi_ut_dfmc_l1e1_full_real8"
$configText = $configText.Replace($historicalOutputPrefix, ".")
Set-Content -LiteralPath $RuntimeConfig -Value $configText -Encoding UTF8

Write-Host "=== P4 FGI FULL REAL8 REPLAY ==="
Write-Host "INPUT_SHA256 = $inputHash"
Write-Host "OFFICIAL_ATTACK_ONSET_SECONDS = 135"
Write-Host "OUTPUT = $OutDir"

$previousErrorActionPreference = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    & docker run --rm `
        -v "${RepoRoot}:/work:ro" `
        -v "${OutDir}:/out" `
        -w /out `
        $Image `
        gnss-sdr `
        --config_file=/out/receiver_full_real8_runtime.conf `
        --log_dir=/out 2>&1 |
        Tee-Object -FilePath (Join-Path $OutDir "gnss_sdr_stdout.log")
    $dockerExitCode = $LASTEXITCODE
}
finally { $ErrorActionPreference = $previousErrorActionPreference }

if ($dockerExitCode -ne 0) { throw "GNSS-SDR replay exited with code $dockerExitCode" }
$stdoutPath = Join-Path $OutDir "gnss_sdr_stdout.log"
$stdoutText = Get-Content -LiteralPath $stdoutPath -Raw -ErrorAction SilentlyContinue
foreach ($pattern in @("Unable to connect flowgraph","configuration file is not well defined","itemsize mismatch")) {
    if ($stdoutText -match [regex]::Escape($pattern)) { throw "GNSS-SDR replay failed despite process exit code 0: $pattern" }
}

Write-Host ""
Write-Host "REPLAY_PROCESS_EXIT_OK = True"
Write-Host "OUTPUT_DIR = $OutDir"
Write-Host "Recorded hostile RF replay only; classification and causal attribution remain separate."
