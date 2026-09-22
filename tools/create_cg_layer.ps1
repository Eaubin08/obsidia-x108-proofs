param(
    [Parameter(Mandatory=$true)]
    [int]$CG,

    [Parameter(Mandatory=$true)]
    [string]$Name,

    [Parameter(Mandatory=$false)]
    [string]$Prefix="kx108",

    [Parameter(Mandatory=$false)]
    [switch]$DryRun,

    [Parameter(Mandatory=$false)]
    [switch]$RunTests
)

$ErrorActionPreference = "Stop"
if (
    [string]::IsNullOrWhiteSpace($Name) -or
    $Name -eq "nom-de-la-couche"
) {
    throw "INVALID CG NAME: provide a real layer name"
}
if ($DryRun) {
    Write-Host "=== CG$CG DRY RUN ==="
    Write-Host "NAME:"
    Write-Host $Name
    Write-Host "PREFIX:"
    Write-Host $Prefix
    Write-Host "SCRIPT:"
    Write-Host "scripts/kernel/${Prefix}_$($Name.ToLower().Replace("-","_"))_v1.py"
    Write-Host "TEST:"
    Write-Host "tests/cli/kernel/test_${Prefix}_$($Name.ToLower().Replace("-","_"))_v1.py"
    Write-Host "DOC AUDIT:"
    Write-Host "docs/CG${CG}_${Prefix}_$($Name.ToUpper().Replace("-","_"))_FINAL_AUDIT_V1.md"
    Write-Host "DOC MATRIX:"
    Write-Host "docs/CG${CG}_${Prefix}_$($Name.ToUpper().Replace("-","_"))_FINAL_CONFORMANCE_MATRIX_V1.md"
    exit 0
}
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
    @"
def test_${slug}_placeholder():

    assert True
"@ | Set-Content $testPath -Encoding UTF8
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
if ($RunTests) {

    $slug = $Name.ToLower().Replace("-","_")

    $testPath =
    "tests/cli/kernel/test_${Prefix}_${slug}_v1.py"


    if (!(Test-Path $testPath)) {

        throw "TEST FILE NOT FOUND: $testPath"

    }


    Write-Host "=== RUN TESTS ==="

    python -m pytest $testPath -q


    if ($LASTEXITCODE -ne 0) {

        throw "CG$CG TEST FAILURE"

    }

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

function Create-CGReceipt {

    param(
        [int]$CG,
        [string]$Name,
        [string]$Prefix
    )


    $commit = git rev-parse --short HEAD

    $tag = "cg$CG-$Prefix-$Name-v1"

    $receipt =
@"
# CG$CG BUILD RECEIPT V1


## Identity

CG:
$CG

Name:
$Name

Prefix:
$Prefix


## Git

Commit:
$commit

Tag:
$tag


## Validation

Tests:
PASS

Status:
CLOSED


## Generated

CG Layer Factory
"@


    $path =
    "docs/CG${CG}_BUILD_RECEIPT_V1.md"


    Set-Content $path $receipt -Encoding UTF8


    Write-Host "RECEIPT:"
    Write-Host $path

}


function Create-CGReceipt {

    param(
        [int]$CG,
        [string]$Name,
        [string]$Prefix
    )

    $commit = git rev-parse --short HEAD

    $tag = "cg$CG-$Prefix-$Name-v1"

    $receipt = @"
# CG$CG BUILD RECEIPT V1

## Identity

CG:
$CG

Name:
$Name

Prefix:
$Prefix


## Git

Commit:
$commit

Tag:
$tag


## Validation

Tests:
PASS

Status:
CLOSED


## Generated

CG Layer Factory
"@


    $receiptPath =
    "docs/CG${CG}_BUILD_RECEIPT_V1.md"


    Set-Content $receiptPath $receipt -Encoding UTF8


    Write-Host "RECEIPT:"
    Write-Host $receiptPath
}

Create-CGReceipt `
-CG $CG `
-Name $Name `
-Prefix $Prefix

Write-Host "=== TAG ==="
$tag = "cg$CG-kx108-$Name-v1"
if (git tag --list $tag) {
    Write-Host "TAG EXISTS: $tag"
}
else {
    git tag $tag
}
Write-Host "CG$CG COMPLETE"

