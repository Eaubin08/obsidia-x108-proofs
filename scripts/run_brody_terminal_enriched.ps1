param(
  [string]$Base = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

function Post-Json {
  param(
    [string]$EndpointPath,
    [hashtable]$Body
  )

  $json = $Body | ConvertTo-Json -Depth 40
  $url = "$Base$EndpointPath"

  $req = [System.Net.HttpWebRequest]::Create($url)
  $req.Method = "POST"
  $req.ContentType = "application/json; charset=utf-8"
  $req.Accept = "application/json"

  $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
  $req.ContentLength = $bytes.Length

  $stream = $req.GetRequestStream()
  $stream.Write($bytes, 0, $bytes.Length)
  $stream.Close()

  try {
    $res = $req.GetResponse()
    $rs = $res.GetResponseStream()
    $ms = New-Object System.IO.MemoryStream
    $rs.CopyTo($ms)
    $raw = $ms.ToArray()
    $text = [System.Text.Encoding]::UTF8.GetString($raw)
    return $text | ConvertFrom-Json
  } catch [System.Net.WebException] {
    $err = $_.Exception
    if ($err.Response) {
      $ers = $err.Response.GetResponseStream()
      $ems = New-Object System.IO.MemoryStream
      $ers.CopyTo($ems)
      $eraw = $ems.ToArray()
      $etext = [System.Text.Encoding]::UTF8.GetString($eraw)
      throw "HTTP_ERROR_UTF8: $etext"
    }
    throw
  }
}

function Get-Answer {
  param($Response)

  if ($Response.PSObject.Properties.Name -contains "final_answer") {
    return [string]$Response.final_answer
  }

  if ($Response.PSObject.Properties.Name -contains "response") {
    return [string]$Response.response
  }

  if ($Response.PSObject.Properties.Name -contains "answer") {
    return [string]$Response.answer
  }

  return ""
}

function Has-Field {
  param($Obj, [string]$Name)

  if ($null -eq $Obj) { return $false }
  return ($Obj.PSObject.Properties.Name -contains $Name)
}

function Print-Boundary {
  param(
    [string]$Name,
    $Response
  )

  Write-Host ""
  Write-Host "[$Name BOUNDARY]" -ForegroundColor DarkCyan
  Write-Host "readonly=$($Response.readonly)"
  Write-Host "advisory_only=$($Response.advisory_only)"
  Write-Host "emits_act=$($Response.emits_act)"
  Write-Host "emits_verdict=$($Response.emits_verdict)"
  Write-Host "decision_authority=$($Response.decision_authority)"
  Write-Host "memory_write=$($Response.memory_write)"
  Write-Host "graphiti_write=$($Response.graphiti_write)"
  Write-Host "kernel_mutation=$($Response.kernel_mutation)"
  Write-Host "x108_mutation=$($Response.x108_mutation)"
}

Write-Host "BRODY TERMINAL ENRICHED - /api/brody/chat + OS Trad + IR + OS Reverse"
Write-Host "Base: $Base"
Write-Host "Type exit to quit."

while ($true) {
  Write-Host ""
  $text = Read-Host "toi"

  if ($text -in @("exit", "quit", "q")) {
    break
  }

  if ([string]::IsNullOrWhiteSpace($text)) {
    continue
  }

  Write-Host ""
  Write-Host "=== 1 / BRODY CHAT PRIMARY ===" -ForegroundColor Cyan

  $chat = Post-Json "/api/brody/chat" @{
    message = $text
    text = $text
    language = "auto"
    session_id = "terminal_enriched"
    mode = "readonly"
  }

  $answer = Get-Answer $chat
  $chatHasSupportRoutes = Has-Field $chat "support_routes"
  $chatHasTranslationTrace = Has-Field $chat "translation_trace"

  Write-Host ""
  Write-Host "[BRODY ANSWER]" -ForegroundColor Green
  Write-Host $answer

  Write-Host ""
  Write-Host "[BRODY META]" -ForegroundColor DarkCyan
  Write-Host "source=$($chat.source)"
  Write-Host "graphiti_status=$($chat.graphiti_status)"
  Write-Host "neo4j_status=$($chat.neo4j_status)"
  Write-Host "readonly=$($chat.readonly)"
  Write-Host "emits_act=$($chat.emits_act)"
  Write-Host "memory_write=$($chat.memory_write)"
  Write-Host "decision_authority=$($chat.decision_authority)"
  Write-Host "has_support_routes=$chatHasSupportRoutes"
  Write-Host "has_translation_trace=$chatHasTranslationTrace"

  Write-Host ""
  Write-Host "=== 2 / OS TRAD SUPPORT ===" -ForegroundColor Cyan

  $osTrad = Post-Json "/api/os-trad/translate" @{
    text = $text
    language = "auto"
    session_id = "terminal_enriched"
    include_context = $true
    include_tree_context = $true
    include_graphiti_context = $true
  }

  Print-Boundary "OS_TRAD" $osTrad

  Write-Host ""
  Write-Host "[OS TRAD]" -ForegroundColor Yellow
  Write-Host "route=$($osTrad.route)"
  Write-Host "detected_language=$($osTrad.detected_language)"
  Write-Host "risk_flags=$($osTrad.risk_flags -join ', ')"
  Write-Host "constraints=$($osTrad.constraints -join ', ')"

  Write-Host ""
  Write-Host "=== 3 / IR CANDIDATE SUPPORT ===" -ForegroundColor Cyan

  $ir = Post-Json "/api/ir/candidate" @{
    text = $text
    language = "auto"
    alphabet_units = $osTrad.alphabet_units
    tree_context = $osTrad.tree_context
    graphiti_context = $osTrad.graphiti_context
    session_id = "terminal_enriched"
  }

  Print-Boundary "IR" $ir

  Write-Host ""
  Write-Host "[IR CANDIDATE]" -ForegroundColor Yellow
  Write-Host "route=$($ir.route)"
  Write-Host "intent=$($ir.ir_candidate.intent)"
  Write-Host "risk_flags=$($ir.ir_candidate.risk_flags -join ', ')"
  Write-Host "contradictions=$($ir.ir_candidate.contradictions -join ', ')"
  Write-Host "constraints=$($ir.ir_candidate.constraints -join ', ')"

  Write-Host ""
  Write-Host "=== 4 / OS REVERSE SUPPORT ===" -ForegroundColor Cyan

  $reverse = Post-Json "/api/os-reverse/project" @{
    text = $text
    language = "auto"
    ir_candidate = $ir.ir_candidate
    audience = "operator"
    format = "terminal"
    tree_context = $osTrad.tree_context
    graphiti_context = $osTrad.graphiti_context
    session_id = "terminal_enriched"
  }

  Print-Boundary "OS_REVERSE" $reverse

  Write-Host ""
  Write-Host "[OS REVERSE PROJECTION]" -ForegroundColor Yellow
  Write-Host "route=$($reverse.route)"
  Write-Host "response_mode=$($reverse.projection.response_mode)"
  Write-Host "summary=$($reverse.projection.summary)"
  Write-Host "next_safe_step=$($reverse.projection.next_safe_step)"
  Write-Host "boundary_notice=$($reverse.projection.boundary_notice)"

  Write-Host ""
  Write-Host "=== ENRICHED VERDICT ===" -ForegroundColor Magenta
  Write-Host "/api/brody/chat remains primary."
  Write-Host "Support routes provide separate evidence."
  Write-Host "No ACT. No verdict. No memory write. No kernel mutation. No X108 mutation."
}
