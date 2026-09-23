param(
  [string]$Repo = "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"
)

Set-Location $Repo
chcp 65001 | Out-Null
$env:PYTHONPATH = $Repo
$env:PYTHONIOENCODING = "utf-8"
$env:OBSIDIA_TERMINAL_COLOR = "1"

python connectors\aviation_robo.py
