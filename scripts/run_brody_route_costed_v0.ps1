param(
  [string]$Base = "http://127.0.0.1:8000",
  [string]$Message = "Test Brody costed route.",
  [string]$Mode = "costed_route_v0"
)

$BodyObj = @{
  message = $Message
  mode = $Mode
  compact = $true
}
$BodyJson = $BodyObj | ConvertTo-Json -Depth 10 -Compress

$Cmd = @"
`$BodyObj = @{
  message = '$Message'
  mode = '$Mode'
  compact = `$true
}
`$BodyJson = `$BodyObj | ConvertTo-Json -Depth 10 -Compress
Invoke-RestMethod -Uri '$Base/api/brody/chat' -Method POST -ContentType 'application/json; charset=utf-8' -Body ([System.Text.Encoding]::UTF8.GetBytes(`$BodyJson)) -TimeoutSec 30 | ConvertTo-Json -Depth 8
"@

& "$PSScriptRoot\run_costed_v0.ps1" `
  -Family "BRODY_CHAT" `
  -Route "/api/brody/chat" `
  -RequestText $Message `
  -CommandLine $Cmd

exit $LASTEXITCODE
