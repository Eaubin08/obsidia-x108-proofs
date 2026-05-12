param(
  [Parameter(Mandatory=$true)]
  [string]$HydratedPacketJson,

  [string]$OutJson = "",

  [string]$OutMd = "",

  [int]$MaxItems = 6
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $scriptDir "brody_local_response_engine_readonly_v1.py"

$argsList = @($py, "--hydrated-packet-json", $HydratedPacketJson, "--max-items", "$MaxItems")

if ($OutJson -ne "") {
  $argsList += @("--out-json", $OutJson)
}

if ($OutMd -ne "") {
  $argsList += @("--out-md", $OutMd)
}

python @argsList

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_LOCAL_RESPONSE_ENGINE_READONLY_FAILED"
}
