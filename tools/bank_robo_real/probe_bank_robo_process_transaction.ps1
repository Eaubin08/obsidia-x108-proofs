param(
  [Parameter(Mandatory=$true)][string]$BaseUrl,
  [string]$Body = '{"json":{}}'
)

$ErrorActionPreference = "Stop"

$Url = "$BaseUrl/api/trpc/banking.processTransaction"
$r = Invoke-RestMethod -Method POST -Uri $Url -ContentType "application/json" -Body $Body -TimeoutSec 20
$r | ConvertTo-Json -Depth 50