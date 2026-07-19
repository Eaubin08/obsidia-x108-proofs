param(
  [string]$ApiBase = "http://127.0.0.1:8000"
)

$Cmd = "cd '$PWD'; `$env:PYTHONPATH='$PWD'; `$env:OBSIDIA_API_BASE='$ApiBase'; python .\connectors\bank_normal_flow.py"

& "$PSScriptRoot\run_costed_v0.ps1" `
  -Family "DOMAIN_BANK" `
  -Route "/api/live/kernel/adapters/bank" `
  -RequestText "Bank connector costed route" `
  -CommandLine $Cmd

exit $LASTEXITCODE
