param(
  [Parameter(Mandatory=$true)][string]$BaseUrl,
  [int]$Limit = 5
)

$ErrorActionPreference = "Stop"

$Url = "$BaseUrl/api/trpc/banking.getRecentTransactions?input=" + [System.Uri]::EscapeDataString("{""json"":{""limit"":$Limit}}")
$r = Invoke-RestMethod -Method GET -Uri $Url -TimeoutSec 20
$r | ConvertTo-Json -Depth 50