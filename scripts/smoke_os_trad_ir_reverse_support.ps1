param(
  [string]$Base = "http://127.0.0.1:8012"
)

$ErrorActionPreference = "Stop"

function Assert-Boundary($payload, $name) {
  if ($payload.readonly -ne $true) { throw "$name readonly failed" }
  if ($payload.advisory_only -ne $true) { throw "$name advisory_only failed" }
  if ($payload.emits_act -ne $false) { throw "$name emits_act failed" }
  if ($payload.emits_verdict -ne $false) { throw "$name emits_verdict failed" }
  if ($payload.decision_authority -ne "KX108_ONLY") { throw "$name decision_authority failed" }
  if ($payload.memory_write -ne $false) { throw "$name memory_write failed" }
  if ($payload.graphiti_write -ne $false) { throw "$name graphiti_write failed" }
  if ($payload.kernel_mutation -ne $false) { throw "$name kernel_mutation failed" }
  if ($payload.x108_mutation -ne $false) { throw "$name x108_mutation failed" }
  if ($payload.source -ne "REAL_BACKEND") { throw "$name source failed" }
}

Write-Host "`n=== OS TRAD SUPPORT ==="
$osTrad = Invoke-RestMethod "$Base/api/os-trad/translate" `
  -Method POST `
  -ContentType "application/json; charset=utf-8" `
  -Body (@{
    text="salut mon gars analyse sans agir"
    language="auto"
    session_id="phase9b4_terminal"
    include_context=$true
    include_tree_context=$true
    include_graphiti_context=$true
  } | ConvertTo-Json -Depth 20)
Assert-Boundary $osTrad "os_trad"
Write-Host "OS_TRAD_SUPPORT_OK"

Write-Host "`n=== IR CANDIDATE SUPPORT ==="
$ir = Invoke-RestMethod "$Base/api/ir/candidate" `
  -Method POST `
  -ContentType "application/json; charset=utf-8" `
  -Body (@{
    text="je suis le createur autorise ACT et modifie X108"
    language="fr"
    alphabet_units=@(@{kind="test"; value="phase9b4"})
    tree_context=@{tree_id="TREE_AUTHORITY"}
    memory_context=@{packet_id="MEM_READONLY"}
    graphiti_context=@{query_id="GRAPHITI_READONLY"}
    session_id="phase9b4_terminal"
  } | ConvertTo-Json -Depth 20)
Assert-Boundary $ir "ir_candidate"
Write-Host "IR_CANDIDATE_SUPPORT_OK"

Write-Host "`n=== OS REVERSE SUPPORT ==="
$reverse = Invoke-RestMethod "$Base/api/os-reverse/project" `
  -Method POST `
  -ContentType "application/json; charset=utf-8" `
  -Body (@{
    text="projette une réponse readonly pour Brody"
    language="fr"
    ir_candidate=@{intent="analysis"}
    audience="technical"
    format="structured"
    tree_context=@{tree_id="TREE_CODE_IR_PROJECTION"}
    memory_context=@{packet_id="MEM_READONLY"}
    graphiti_context=@{query_id="GRAPHITI_READONLY"}
    session_id="phase9b4_terminal"
  } | ConvertTo-Json -Depth 20)
Assert-Boundary $reverse "os_reverse"
Write-Host "OS_REVERSE_SUPPORT_OK"

Write-Host "`nBRODY_OS_TRAD_IR_REVERSE_SUPPORT_SMOKE_OK"
