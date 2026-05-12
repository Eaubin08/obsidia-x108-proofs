param(
  [Parameter(Mandatory=$true)]
  [string]$PacketJson,

  [string]$OutJson = "",

  [string]$OutMd = "",

  [int]$MaxItems = 6
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $scriptDir "brody_context_packet_consumer_readonly_v1.py"

$argsList = @($py, "--packet-json", $PacketJson, "--max-items", "$MaxItems")

if ($OutJson -ne "") {
  $argsList += @("--out-json", $OutJson)
}

if ($OutMd -ne "") {
  $argsList += @("--out-md", $OutMd)
}

python @argsList

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_CONTEXT_PACKET_CONSUMER_READONLY_FAILED"
}
