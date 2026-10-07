param(
    [string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
)

$ErrorActionPreference = "Stop"
$Onset = 135
$Log = Join-Path $RepoRoot ".local\p4-replay\fgi-full-real8\gnss_sdr_stdout.log"
$Out = Join-Path $RepoRoot ".local\p4-replay\fgi-full-real8\postrun_summary.json"

if (-not (Test-Path -LiteralPath $Log)) { throw "Full replay log not found: $Log" }

function Convert-ReceiverTime([string]$line) {
    if ($line -match "Current receiver time:\s*(\d+)\s*min\s*(\d+)\s*s") { return ([int]$matches[1] * 60 + [int]$matches[2]) }
    if ($line -match "Current receiver time:\s*(\d+)\s*s") { return [int]$matches[1] }
    return $null
}
function EcefPoint($p) {
    if ($null -eq $p) { return $null }
    $a = 6378137.0
    $f = 1.0 / 298.257223563
    $e2 = $f * (2.0 - $f)
    $lat = $p.lat * [math]::PI / 180.0
    $lon = $p.lon * [math]::PI / 180.0
    $n = $a / [math]::Sqrt(1.0 - $e2 * [math]::Sin($lat) * [math]::Sin($lat))
    return [pscustomobject]@{
        x = ($n + $p.height_m) * [math]::Cos($lat) * [math]::Cos($lon)
        y = ($n + $p.height_m) * [math]::Cos($lat) * [math]::Sin($lon)
        z = ($n * (1.0 - $e2) + $p.height_m) * [math]::Sin($lat)
    }
}
function EcefDistanceMeters($a,$b) {
    if ($null -eq $a -or $null -eq $b) { return $null }
    $ea = EcefPoint $a
    $eb = EcefPoint $b
    return [math]::Sqrt(
        [math]::Pow($ea.x-$eb.x,2) +
        [math]::Pow($ea.y-$eb.y,2) +
        [math]::Pow($ea.z-$eb.z,2)
    )
}
function HaversineMeters($a,$b) {
    if ($null -eq $a -or $null -eq $b) { return $null }
    $r=6371000.0; $p1=$a.lat*[math]::PI/180; $p2=$b.lat*[math]::PI/180
    $dp=($b.lat-$a.lat)*[math]::PI/180; $dl=($b.lon-$a.lon)*[math]::PI/180
    $h=[math]::Sin($dp/2)*[math]::Sin($dp/2)+[math]::Cos($p1)*[math]::Cos($p2)*[math]::Sin($dl/2)*[math]::Sin($dl/2)
    return 2*$r*[math]::Atan2([math]::Sqrt($h),[math]::Sqrt(1-$h))
}

$sec = 0
$navPre=0; $navPost=0; $lossPre=0; $lossPost=0; $trackPre=0; $trackPost=0
$positions = @()
$firstFix = $null

foreach ($line in Get-Content -LiteralPath $Log) {
    $t = Convert-ReceiverTime $line
    if ($null -ne $t) { $sec = $t; continue }
    $post = $sec -ge $Onset
    if ($line -match "New GPS NAV message received") { if ($post) {$navPost++} else {$navPre++} }
    if ($line -match "Loss of lock") { if ($post) {$lossPost++} else {$lossPre++} }
    if ($line -match "Tracking of GPS L1 C/A signal started") { if ($post) {$trackPost++} else {$trackPre++} }
    if ($line -match "First position fix at (.+?) UTC is Lat = ([\-0-9.]+).*Long = ([\-0-9.]+).*Height = ([\-0-9.]+).*GDOP = ([\-0-9.]+)") {
        $firstFix=[pscustomobject]@{receiver_second=$sec; utc=$matches[1]; lat=[double]$matches[2]; lon=[double]$matches[3]; height_m=[double]$matches[4]; gdop=[double]$matches[5]}
    }
    if ($line -match "Position at (.+?) UTC using (\d+) observations is Lat = ([\-0-9.]+).*Long = ([\-0-9.]+).*Height = ([\-0-9.]+)") {
        $positions += [pscustomobject]@{receiver_second=$sec; utc=$matches[1]; observations=[int]$matches[2]; lat=[double]$matches[3]; lon=[double]$matches[4]; height_m=[double]$matches[5]}
    }
}

$pre = @($positions | Where-Object {$_.receiver_second -lt $Onset})
$post = @($positions | Where-Object {$_.receiver_second -ge $Onset})
$preLast = if ($pre.Count) {$pre[-1]} else {$null}
$postFirst = if ($post.Count) {$post[0]} else {$null}
$final = if ($positions.Count) {$positions[-1]} else {$null}

$summary=[ordered]@{
    artifact="p4_fgi_full_real8_postrun_summary"
    official_attack_onset_seconds=$Onset
    first_fix=$firstFix
    nav_messages_pre_onset=$navPre
    nav_messages_post_onset=$navPost
    tracking_starts_pre_onset=$trackPre
    tracking_starts_post_onset=$trackPost
    loss_of_lock_pre_onset=$lossPre
    loss_of_lock_post_onset=$lossPost
    pvt_positions_pre_onset=$pre.Count
    pvt_positions_post_onset=$post.Count
    last_pre_onset_position=$preLast
    first_post_onset_position=$postFirst
    final_position=$final
    onset_boundary_displacement_m=if($preLast -and $postFirst){[math]::Round((HaversineMeters $preLast $postFirst),3)}else{$null}
    onset_boundary_ecef_delta_m=if($preLast -and $postFirst){[math]::Round((EcefDistanceMeters $preLast $postFirst),3)}else{$null}
    prelast_to_final_displacement_m=if($preLast -and $final){[math]::Round((HaversineMeters $preLast $final),3)}else{$null}
    prelast_to_final_ecef_delta_m=if($preLast -and $final){[math]::Round((EcefDistanceMeters $preLast $final),3)}else{$null}
    claim_boundary="POST_RUN_OBSERVATION_ONLY_NO_CAUSAL_ATTRIBUTION"
}

$summary | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $Out -Encoding UTF8
$summary | ConvertTo-Json -Depth 6
Write-Host "SUMMARY_JSON = $Out"
