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

function Write-Host "=== TAG ==="
$tag = "cg$CG-kx108-$Name-v1"
if (git tag --list $tag) {
    Write-Host "TAG EXISTS: $tag"
}
else {
    git tag $tag
}
Write-Host "CG$CG COMPLETE"












