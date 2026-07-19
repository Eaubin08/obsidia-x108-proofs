param(
  [string]$ApiBase = "http://127.0.0.1:8000"
)

$Cmd = "cd '$PWD'; `$env:PYTHONPATH='$PWD'; `$env:OBSIDIA_API_BASE='$ApiBase'; python .\connectors\trading_live.py"

& "$PSScriptRoot\run_costed_v0.ps1" `
  -Family "DOMAIN_TRADING" `
  -Route "/api/live/kernel/adapters/trading" `
  -RequestText "Trading connector costed route" `
  -CommandLine $Cmd

exit $LASTEXITCODE
