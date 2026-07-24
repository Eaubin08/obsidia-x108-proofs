param(
  [string]$GraphBase = "http://127.0.0.1:8011"
)

$Cmd = "Invoke-RestMethod '$GraphBase/graph/v20/frozen/status' -TimeoutSec 20 | ConvertTo-Json -Depth 8"

& "$PSScriptRoot\run_costed_v0.ps1" `
  -Family "BRODY_MEMORY" `
  -Route "/graph/v20/frozen/status" `
  -RequestText "Graphiti status costed route" `
  -CommandLine $Cmd

exit $LASTEXITCODE
