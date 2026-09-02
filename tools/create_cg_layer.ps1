param(
    [Parameter(Mandatory=$true)]
    [int]$CG,
    [Parameter(Mandatory=$true)]
    [string]$Name,
    [Parameter(Mandatory=$false)]
    [string]$Prefix="kx108"
)
$ErrorActionPreference = "Stop"
function Normalize-File {
    param(
        [string]$Path
    )
    if (!(Test-Path $Path)) {
        return
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $content = Get-Content $Path -Raw
    if ($null -eq $content) {
        return
    }
    $content = $content.Replace("`r`n","`n")
    $lines = $content -split "`n"
    $clean = foreach ($line in $lines) {
        $line.TrimEnd()
    }
    $final = ($clean -join "`n").TrimEnd() + "`n"
    [System.IO.File]::WriteAllText(
        (Get-Item $Path).FullName,
        $final,
        $utf8
    )
}
function Create-CGLayerFiles {
    param(
        [int]$CG,
        [string]$Name,
        [string]$Prefix
    )
    $slug = $Name.ToLower().Replace("-","_")
    $scriptPath = "scripts/kernel/${Prefix}_${slug}_v1.py"
    $testPath = "tests/cli/kernel/test_${Prefix}_${slug}_v1.py"
    $upper = $Name.ToUpper().Replace("-","_")
    $auditDoc =
    "docs/CG${CG}_${Prefix}_${upper}_FINAL_AUDIT_V1.md"
    $matrixDoc =
    "docs/CG${CG}_${Prefix}_${upper}_FINAL_CONFORMANCE_MATRIX_V1.md"
    New-Item $scriptPath -ItemType File -Force | Out-Null
    New-Item $testPath -ItemType File -Force | Out-Null
    New-Item $auditDoc -ItemType File -Force | Out-Null
    New-Item $matrixDoc -ItemType File -Force | Out-Null
    Write-Host "CREATED:"
    Write-Host $scriptPath
    Write-Host $testPath
    Write-Host $auditDoc
    Write-Host $matrixDoc
}
Write-Host "=== CG$CG BUILD ==="
Create-CGLayerFiles `
-CG $CG `
-Name $Name `
-Prefix $Prefix
Write-Host "=== DOC NORMALIZATION ==="
$docs = Get-ChildItem docs -Filter "CG$CG*" -File
foreach ($doc in $docs) {
    Normalize-File $doc.FullName
}
Write-Host "=== GIT CHECK ==="
git add .
git diff --cached --check
if ($LASTEXITCODE -ne 0) {
    throw "CG$CG DIFF FAILURE"
}
Write-Host "=== COMMIT ==="
if (git diff --cached --quiet) {
    Write-Host "NO CHANGES TO COMMIT"
}
else {
    git commit -m "feat(cg$CG): add kx108 $Name"
    if ($LASTEXITCODE -ne 0) {
        Write-Host "COMMIT ALREADY CLEAN"
    }
}
Write-Host "=== TAG ==="
$tag = "cg$CG-kx108-$Name-v1"
if (git tag --list $tag) {
    Write-Host "TAG EXISTS: $tag"
}
else {
    git tag $tag
}
Write-Host "CG$CG COMPLETE"
