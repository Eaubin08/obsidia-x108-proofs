param(
  [Parameter(Mandatory=$true)]
  [ValidateSet("BRODY_CHAT","BRODY_MEMORY","BRODY_FASTPATH","DOMAIN_BANK","DOMAIN_TRADING","DOMAIN_GPS_AVIATION","OBSIDURE_LEAN","OBSIDURE_CODE","X108_GUARD","SIGMA_REPORT","RUNTIME_API","UNKNOWN")]
  [string]$Family,

  [Parameter(Mandatory=$true)]
  [string]$Route,

  [string]$RequestText = "",

  [Parameter(Mandatory=$true)]
  [string]$CommandLine
)

$Root = Resolve-Path "$PSScriptRoot\.."
$Runner = Join-Path $Root "scripts\performance\run_with_cost_event_v0.py"

python $Runner --family $Family --route $Route --request-text $RequestText -- powershell -NoProfile -ExecutionPolicy Bypass -Command $CommandLine
exit $LASTEXITCODE
