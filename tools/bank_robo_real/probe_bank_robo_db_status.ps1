param(
  [Parameter(Mandatory=$true)][string]$BaseUrl
)

$ErrorActionPreference = "Stop"

$Urls = @(
  "$BaseUrl/api/trpc/banking.getRecentTransactions?input=$([System.Uri]::EscapeDataString('{""json"":{""limit"":1}}'))"
)

foreach ($u in $Urls) {
  try {
    $r = Invoke-RestMethod -Method GET -Uri $u -TimeoutSec 10
    $r | ConvertTo-Json -Depth 20
  } catch {
    [ordered]@{
      url = $u
      error = $_.Exception.Message
    } | ConvertTo-Json -Depth 10
  }
}