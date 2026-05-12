param(
  [Parameter(Mandatory=$true)]
  [string]$Query,

  [int]$Limit = 8,

  [string]$OutJson = "",

  [string]$OutMd = ""
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $scriptDir "brody_context_packet_query_readonly_v1.py"

$argsList = @($py, "--query", $Query, "--limit", "$Limit")

if ($OutJson -ne "") {
  $argsList += @("--out-json", $OutJson)
}

if ($OutMd -ne "") {
  $argsList += @("--out-md", $OutMd)
}

python @argsList

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_CONTEXT_PACKET_QUERY_READONLY_FAILED"
}
