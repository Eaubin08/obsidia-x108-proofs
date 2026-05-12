param(
  [Parameter(Mandatory=$true)][string]$Source,
  [string]$Label = "SOURCE"
)

$ErrorActionPreference = "Stop"

Set-Location "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-engine-candidate"

python "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-engine-candidate\zip1_sandbox_mutable\ZIP1_X108_MUTABLE_20260508_183610\periphery\brody_obsidien_v1_6_world_source_intake_readonly\brody_world_source_intake_readonly_v1_6.py" --source "$Source" --out-root "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-engine-candidate\_world_intake" --label "$Label"
