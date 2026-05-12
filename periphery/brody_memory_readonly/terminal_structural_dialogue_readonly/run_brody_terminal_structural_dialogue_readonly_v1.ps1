param([string]$Once = "", [int]$Limit = 8, [int]$MaxItems = 6, [string]$SessionDir = "")
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$x108 = Resolve-Path (Join-Path $scriptDir "..\..\..")
$args = @((Join-Path $scriptDir "brody_terminal_structural_dialogue_readonly_v1.py"), "--x108-root", "$x108", "--limit", "$Limit", "--max-items", "$MaxItems")
if ($Once) { $args += @("--once", $Once) }; if ($SessionDir) { $args += @("--session-dir", $SessionDir) }
python @args
