param(
  [Parameter(Mandatory=$true)]
  [string]$PacketJson,

  [string]$OutJson = "",

  [string]$OutMd = "",

  [string[]]$Root = @(),

  [int]$MaxChars = 1400
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$py = Join-Path $scriptDir "brody_content_hydration_readonly_v1.py"

$argsList = @($py, "--packet-json", $PacketJson, "--max-chars", "$MaxChars")

if ($OutJson -ne "") {
  $argsList += @("--out-json", $OutJson)
}

if ($OutMd -ne "") {
  $argsList += @("--out-md", $OutMd)
}

foreach ($r in $Root) {
  if ($r -ne "") {
    $argsList += @("--root", $r)
  }
}

python @argsList

if ($LASTEXITCODE -ne 0) {
  throw "BRODY_CONTENT_HYDRATION_READONLY_FAILED"
}
