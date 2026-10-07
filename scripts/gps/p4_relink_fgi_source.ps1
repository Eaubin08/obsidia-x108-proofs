param(
    [string]$Source = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\hackathons\nativebuilder-gps-defense\data\fgi-spoofrepo\FGISpoofRepo\UT_DFMC\UTD_L1_E1.dat",
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"

$ExpectedSha256 = "e8da962e92cfdbcb677361ce769a54f26dc385417bac9fd618492dcd02fb2d72"
$TargetDir = Join-Path $RepoRoot "hackathons\nativebuilder-gps-defense\data\fgi-spoofrepo\pipeline_inputs"
$Target = Join-Path $TargetDir "case_0001_l1e1_real8.dat"

Write-Host "=== P4 FGI SOURCE RELINK ==="
Write-Host "SOURCE = $Source"
Write-Host "TARGET = $Target"

if (-not (Test-Path -LiteralPath $Source -PathType Leaf)) {
    throw "FGI source not found: $Source"
}

$sourceItem = Get-Item -LiteralPath $Source
$sourceHash = (Get-FileHash -LiteralPath $Source -Algorithm SHA256).Hash.ToLowerInvariant()

Write-Host "SOURCE_SIZE_BYTES = $($sourceItem.Length)"
Write-Host "SOURCE_SHA256     = $sourceHash"
Write-Host "EXPECTED_SHA256   = $ExpectedSha256"

if ($sourceHash -ne $ExpectedSha256) {
    throw "FGI source SHA256 mismatch. Refusing relink."
}

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null

if (Test-Path -LiteralPath $Target) {
    $targetHash = (Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($targetHash -ne $ExpectedSha256) {
        throw "Target exists with unexpected SHA256: $Target"
    }
    Write-Host "TARGET_ALREADY_VALID = True"
}
else {
    try {
        New-Item -ItemType HardLink -Path $Target -Target $Source | Out-Null
    }
    catch {
        throw "Hardlink creation failed. No 9+ GiB copy was attempted. Source and target must remain on the same NTFS volume. $($_.Exception.Message)"
    }
}

$finalHash = (Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash.ToLowerInvariant()
$finalItem = Get-Item -LiteralPath $Target

if ($finalHash -ne $ExpectedSha256) {
    throw "Relink verification failed."
}

Write-Host ""
Write-Host "RELINK_OK = True"
Write-Host "TARGET_SIZE_BYTES = $($finalItem.Length)"
Write-Host "TARGET_SHA256     = $finalHash"
Write-Host "COPY_PERFORMED    = False"
Write-Host ""
Write-Host "P4 recorded hostile RF source is locally reconnected."
Write-Host "This does not claim P2 live-passive closure or P4 hostile-classification closure."
