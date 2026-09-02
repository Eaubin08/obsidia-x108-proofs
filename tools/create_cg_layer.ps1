param(
    [Parameter(Mandatory=$true)]
    [int]$CG,

    [Parameter(Mandatory=$true)]
    [string]$Name
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

    $content = $content.Replace("`r`n","`n")

    $lines = $content -split "`n"

    $clean = foreach ($line in $lines) {
        $line.TrimEnd()
    }

    $final = ($clean -join "`n").TrimEnd() + "`n"

    [System.IO.File]::WriteAllText(
        (Resolve-Path $Path),
        $final,
        $utf8
    )
}


Write-Host "=== CG$CG FINALIZER ==="

Write-Host "=== DOC NORMALIZATION ==="

Get-ChildItem docs -Filter "CG$CG*" -File |
ForEach-Object {
    Normalize-File $_.FullName
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
        throw "CG$CG COMMIT FAILURE"
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
