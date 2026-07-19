param(
  [string]$ApiBase = "http://127.0.0.1:8000"
)

$Cmd = "cd '$PWD'; `$env:PYTHONPATH='$PWD'; `$env:OBSIDIA_API_BASE='$ApiBase'; python .\connectors\aviation_robo.py"

& "$PSScriptRoot\run_costed_v0.ps1" `
  -Family "DOMAIN_GPS_AVIATION" `
  -Route "/api/live/kernel/adapters/gps" `
  -RequestText "GPS Aviation connector costed route" `
  -CommandLine $Cmd

exit $LASTEXITCODE
