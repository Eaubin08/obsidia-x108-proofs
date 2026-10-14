param(
    [string]$SourcePath = "",
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path,
    [string]$ExpectedSha256 = ""
)

$ErrorActionPreference = "Stop"

if (-not $SourcePath) {
    $roots = @(
        (Join-Path $env:USERPROFILE "Downloads"),
        (Join-Path $env:USERPROFILE "Desktop"),
        "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\hackathons\nativebuilder-gps-defense\data\fgi-spoofrepo"
    ) | Where-Object { Test-Path -LiteralPath $_ -PathType Container }

    $matches = @()
    foreach ($root in $roots) {
        $matches += @(Get-ChildItem -LiteralPath $root -Recurse -File -Filter "MCD_L1_E1.dat" -ErrorAction SilentlyContinue)
    }

    $uniqueMatches = @($matches | Sort-Object FullName -Unique)
    if ($uniqueMatches.Count -eq 0) {
        throw "MCD_L1_E1.dat not found under Downloads, Desktop, or the historical FGI root."
    }
    if ($uniqueMatches.Count -gt 1) {
        Write-Host "Multiple MCD_L1_E1.dat candidates found:"
        $uniqueMatches | ForEach-Object { Write-Host " - $($_.FullName)" }
        throw "Refusing ambiguous held-out source selection. Re-run with -SourcePath."
    }
    $SourcePath = $uniqueMatches[0].FullName
}

if (-not (Test-Path -LiteralPath $SourcePath -PathType Leaf)) {
    throw "Held-out MCD source not found: $SourcePath"
}

$SourcePath = (Resolve-Path -LiteralPath $SourcePath).Path
$TargetDir = Join-Path $RepoRoot "hackathons\nativebuilder-gps-defense\data\fgi-spoofrepo\pipeline_inputs"
$Target = Join-Path $TargetDir "case_mcd_l1e1_real8.dat"
$ManifestDir = Join-Path $RepoRoot ".local\p4-heldout\mcd"
$Manifest = Join-Path $ManifestDir "source_manifest.json"

New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
New-Item -ItemType Directory -Force -Path $ManifestDir | Out-Null

$sourceHash = (Get-FileHash -LiteralPath $SourcePath -Algorithm SHA256).Hash.ToLowerInvariant()
$sourceSize = (Get-Item -LiteralPath $SourcePath).Length

if ($ExpectedSha256) {
    if ($sourceHash -ne $ExpectedSha256.ToLowerInvariant()) {
        throw "Held-out MCD source hash mismatch. Refusing relink."
    }
}

if (Test-Path -LiteralPath $Target) {
    $targetHash = (Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($targetHash -ne $sourceHash) {
        throw "Canonical MCD target already exists with a different hash: $Target"
    }
}
else {
    try {
        New-Item -ItemType HardLink -Path $Target -Target $SourcePath | Out-Null
        $linkKind = "HARDLINK"
    }
    catch {
        throw "Hardlink failed. Refusing to copy held-out RF implicitly. Source=$SourcePath Target=$Target Error=$($_.Exception.Message)"
    }
}

$targetHash = (Get-FileHash -LiteralPath $Target -Algorithm SHA256).Hash.ToLowerInvariant()
if ($targetHash -ne $sourceHash) {
    throw "Post-link hash mismatch. Refusing held-out replay."
}

$result = [ordered]@{
    artifact = "p4_fgi_meaconing_heldout_source_manifest"
    status = "SOURCE_BOUND_BEFORE_EXECUTION"
    source_file = $SourcePath
    canonical_input = $Target
    input_sha256 = $sourceHash
    size_bytes = $sourceSize
    expected_sha256_supplied = [bool]$ExpectedSha256
    used_for_classifier_calibration = $false
    thresholds_modified_after_source_binding = $false
    classifier = "P4_TEMPORAL_DISCONTINUITY_V0"
    claim_boundary = "HELD_OUT_RECORDED_RF_NO_CLASSIFICATION_YET"
}

$result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Manifest -Encoding UTF8

Write-Host ($result | ConvertTo-Json -Depth 6)
Write-Host "SOURCE_MANIFEST = $Manifest"
Write-Host "MCD_INPUT_SHA256 = $sourceHash"
