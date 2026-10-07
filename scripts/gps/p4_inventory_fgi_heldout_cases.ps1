param(
    [string]$FgiRoot = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B\hackathons\nativebuilder-gps-defense\data\fgi-spoofrepo\FGISpoofRepo",
    [string]$Out = ""
)

$ErrorActionPreference = "Stop"

$expected = @(
    @{ scenario = "Targeted_SFMC"; file = "TGS_L1_E1.dat"; duration_s = 373 },
    @{ scenario = "Targeted_DFMC"; file = "TGD_L1_E1.dat"; duration_s = 373 },
    @{ scenario = "Untargeted_DFMC"; file = "UTD_L1_E1.dat"; duration_s = 377 },
    @{ scenario = "Meaconing_DFMC"; file = "MCD_L1_E1.dat"; duration_s = 478 }
)

$items = foreach ($case in $expected) {
    $candidate = Join-Path (Join-Path $FgiRoot $case.scenario) $case.file
    $exists = Test-Path -LiteralPath $candidate -PathType Leaf
    $length = if ($exists) { (Get-Item -LiteralPath $candidate).Length } else { $null }
    [pscustomobject]@{
        scenario = $case.scenario
        file = $case.file
        expected_duration_s = $case.duration_s
        exists = $exists
        size_bytes = $length
        path = $candidate
        used_for_p4_development = ($case.file -eq "UTD_L1_E1.dat")
        held_out_candidate = ($case.file -ne "UTD_L1_E1.dat")
    }
}

$result = [ordered]@{
    artifact = "p4_fgi_heldout_local_inventory"
    fgi_root = $FgiRoot
    expected_case_count = $expected.Count
    present_case_count = @($items | Where-Object { $_.exists }).Count
    held_out_present_count = @($items | Where-Object { $_.exists -and $_.held_out_candidate }).Count
    cases = $items
    note = "Inventory only. No RF data is modified, copied, hashed or executed."
}

$json = $result | ConvertTo-Json -Depth 6
$json

if ($Out) {
    $parent = Split-Path -Parent $Out
    if ($parent) { New-Item -ItemType Directory -Force -Path $parent | Out-Null }
    Set-Content -LiteralPath $Out -Value $json -Encoding UTF8
    Write-Host "INVENTORY_JSON = $Out"
}
