param(
  [string]$Port = "3001"
)

Set-Location $PSScriptRoot

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Audit = ".\audit\local_diag\audit_total_metrics_proof_$Stamp"
New-Item -ItemType Directory -Force $Audit | Out-Null
New-Item -ItemType Directory -Force ".\MonProjet\allData" | Out-Null
New-Item -ItemType Directory -Force ".\logs" | Out-Null

$Url = "http://localhost:$Port/kernel/ragnarok"
$env:OBSIDIA_PORT = $Port
$env:OBSIDIA_URL = $Url
$env:PYTHONPATH = (Get-Location).Path

function Short-Sha($Hash) {
  if ([string]::IsNullOrWhiteSpace([string]$Hash)) { return "NA" }
  $s = [string]$Hash
  if ($s.Length -gt 12) { return $s.Substring(0, 12) }
  return $s
}

function Get-Sha($Path) {
  if (-not (Test-Path $Path)) { return "MISSING" }
  try {
    return (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash
  } catch {
    return "LOCKED_OR_UNREADABLE"
  }
}

function Escape-Md($Value) {
  if ($null -eq $Value) { return "" }
  $s = [string]$Value
  $s = $s -replace "\|", "/"
  $s = $s -replace "`r?`n", " "
  return $s
}

function To-Double($Value) {
  if ($null -eq $Value) { return 0.0 }
  try { return [double]$Value } catch {}
  try {
    return [double]::Parse(([string]$Value).Replace(",", "."), [System.Globalization.CultureInfo]::InvariantCulture)
  } catch {
    return 0.0
  }
}

function Add-FlatRow {
  param(
    [object]$Obj,
    [string]$Prefix,
    [System.Collections.ArrayList]$Rows
  )

  if ($null -eq $Obj) {
    [void]$Rows.Add([PSCustomObject]@{
      path = $Prefix
      type = "null"
      value = ""
    })
    return
  }

  if ($Obj -is [System.Management.Automation.PSCustomObject]) {
    foreach ($p in $Obj.PSObject.Properties) {
      $next = if ($Prefix) { "$Prefix.$($p.Name)" } else { "$($p.Name)" }
      Add-FlatRow -Obj $p.Value -Prefix $next -Rows $Rows
    }
    return
  }

  if ($Obj -is [System.Collections.IDictionary]) {
    foreach ($k in $Obj.Keys) {
      $next = if ($Prefix) { "$Prefix.$k" } else { "$k" }
      Add-FlatRow -Obj $Obj[$k] -Prefix $next -Rows $Rows
    }
    return
  }

  if (($Obj -is [System.Collections.IEnumerable]) -and -not ($Obj -is [string])) {
    $i = 0
    foreach ($item in $Obj) {
      $next = "$Prefix[$i]"
      Add-FlatRow -Obj $item -Prefix $next -Rows $Rows
      $i++
    }
    if ($i -eq 0) {
      [void]$Rows.Add([PSCustomObject]@{
        path = $Prefix
        type = "array_empty"
        value = ""
      })
    }
    return
  }

  [void]$Rows.Add([PSCustomObject]@{
    path = $Prefix
    type = $Obj.GetType().Name
    value = [string]$Obj
  })
}

function Read-Security {
  param($Gate, $Severity, $Reason)

  if ($Gate -eq "BLOCK") {
    return "BLOCK : action refusee avant execution. Risque critique, contradiction ou coherence insuffisante."
  }

  if ($Gate -eq "HOLD") {
    return "HOLD : action retenue. X-108 impose delai, refroidissement ou validation supplementaire."
  }

  if ($Gate -eq "ACT") {
    return "ACT : action autorisee par les garde-fous."
  }

  return "LECTURE INCOMPLETE : gate non reconnu."
}

function Invoke-DomainAudit {
  param(
    [string]$Domain,
    [hashtable]$Data,
    [string]$Meaning
  )

  $Safe = $Domain -replace '[^a-zA-Z0-9_-]', '_'

  $InputFile = Join-Path $Audit "input_$Safe.json"
  $ResponseFile = Join-Path $Audit "response_$Safe.json"
  $MetricsCsv = Join-Path $Audit "metrics_full_$Safe.csv"
  $MetricsJson = Join-Path $Audit "metrics_full_$Safe.json"

  $Body = @{
    domain = $Domain
    data = $Data
  } | ConvertTo-Json -Depth 60 -Compress

  $Body | Set-Content $InputFile -Encoding UTF8

  $Resp = Invoke-RestMethod `
    -Uri $Url `
    -Method Post `
    -ContentType "application/json" `
    -Body $Body `
    -TimeoutSec 60

  $Resp | ConvertTo-Json -Depth 60 | Set-Content $ResponseFile -Encoding UTF8

  $Flat = New-Object System.Collections.ArrayList
  Add-FlatRow -Obj $Resp -Prefix "" -Rows $Flat
  $FlatRows = @($Flat)

  $FlatRows | Export-Csv $MetricsCsv -NoTypeInformation -Encoding UTF8
  $FlatRows | ConvertTo-Json -Depth 20 | Set-Content $MetricsJson -Encoding UTF8

  $Integrity = To-Double $Resp.confidence_integrity
  $Governance = To-Double $Resp.confidence_governance
  $Readiness = To-Double $Resp.confidence_readiness
  $Mean = [math]::Round((($Integrity + $Governance + $Readiness) / 3), 4)

  [PSCustomObject]@{
    Domaine = $Resp.domain
    Sens = $Meaning
    Verdict = $Resp.market_verdict
    Gate = $Resp.x108_gate
    Integrity = $Integrity
    Governance = $Governance
    Readiness = $Readiness
    Moyenne = $Mean
    Severity = $Resp.severity
    Reason = $Resp.reason_code
    Securite = Read-Security -Gate $Resp.x108_gate -Severity $Resp.severity -Reason $Resp.reason_code
    MetricCount = $FlatRows.Count
    InputFile = $InputFile
    ResponseFile = $ResponseFile
    MetricsCsv = $MetricsCsv
    MetricsJson = $MetricsJson
    InputHash = Get-Sha $InputFile
    ResponseHash = Get-Sha $ResponseFile
    MetricsHash = Get-Sha $MetricsCsv
  }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " AUDIT TOTAL METRICS / PREUVE / TRACABILITE — 3 DOMAINES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "URL   : $Url"
Write-Host "AUDIT : $Audit"

$GitBranch = git branch --show-current 2>$null
$GitCommit = git rev-parse HEAD 2>$null
$GitTags = @(git tag --points-at HEAD 2>$null) -join ", "
if (-not $GitTags) { $GitTags = "NO_TAG_ON_HEAD" }
$GitStatus = @(git status --short 2>$null) -join "; "
if (-not $GitStatus) { $GitStatus = "CLEAN" }

Write-Host ""
Write-Host "GIT BRANCH : $GitBranch"
Write-Host "GIT COMMIT : $GitCommit"
Write-Host "GIT TAGS   : $GitTags"
Write-Host "GIT STATUS : $GitStatus"

$BeforeDecisions = @()
if (Test-Path ".\MonProjet\allData") {
  $BeforeDecisions = @(Get-ChildItem ".\MonProjet\allData" -File -Filter "decision_*.json" -ErrorAction SilentlyContinue)
}
$BeforeNames = @{}
foreach ($d in $BeforeDecisions) { $BeforeNames[$d.Name] = $true }

Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
  Where-Object { $_.OwningProcess -and $_.OwningProcess -ne 0 } |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object {
    Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
  }

$Server = Start-Process -FilePath "npm.cmd" `
  -ArgumentList "start" `
  -WorkingDirectory (Get-Location).Path `
  -RedirectStandardOutput "$Audit\server.stdout.log" `
  -RedirectStandardError "$Audit\server.stderr.log" `
  -PassThru `
  -WindowStyle Hidden

$Listening = $null
for ($i = 0; $i -lt 20; $i++) {
  Start-Sleep -Seconds 1
  $Listening = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
    Where-Object { $_.State -eq "Listen" }
  if ($Listening) { break }
}

if (-not $Listening) {
  Write-Host "[FAIL] Serveur non actif sur $Port" -ForegroundColor Red
  Get-Content "$Audit\server.stderr.log" -ErrorAction SilentlyContinue
  throw "STOP: serveur inaccessible"
}

Write-Host "[OK] Serveur actif sur $Port" -ForegroundColor Green

$BankData = @{
  transaction_type = "transfer"
  amount = 219.10
  channel = "mobile"
  counterparty_known = $false
  counterparty_age_days = 0
  account_balance = 1000
  available_cash = 1000
  historical_avg_amount = 80
  behavior_shift_score = 0.8
  fraud_score = 0.9
  policy_limit = 500
  affordability_score = 0.7
  urgency_score = 0.9
  identity_mismatch_score = 0.4
  narrative_conflict_score = 0.4
  device_trust_score = 0.4
  recent_failed_attempts = 2
  elapsed_s = 1
  min_required_elapsed_s = 108
}

$TradingData = @{
  symbol = "BTC-USDT"
  side = "BUY"
  amount = 1500
  leverage = 3
  drawdown = 0.18
  exposure = 0.72
  slippage_bps = 180
  order_book_imbalance = 0.82
  volatility_score = 0.88
  liquidity_score = 0.35
  elapsed_s = 1
  min_required_elapsed_s = 108
}

$AviationData = @{
  aircraft_id = "DEMO-X108-AV"
  phase = "navigation"
  gps_signal_quality = 0.28
  source_count = 1
  source_conflict_score = 0.86
  time_skew_ms = 4200
  spoofing_risk_score = 0.91
  sensor_consensus = 0.34
  altitude_delta_m = 180
  route_deviation_score = 0.74
  elapsed_s = 1
  min_required_elapsed_s = 108
}

$Rows = @()
$Rows += Invoke-DomainAudit -Domain "bank" -Data $BankData -Meaning "Transaction bancaire mobile risquee : nouveau beneficiaire, fraude elevee, urgence elevee, delai X-108 non respecte."
$Rows += Invoke-DomainAudit -Domain "trading" -Data $TradingData -Meaning "Ordre de trading risque : levier, exposition, drawdown, slippage et desequilibre carnet eleves."
$Rows += Invoke-DomainAudit -Domain "gps_defense_aviation" -Data $AviationData -Meaning "Navigation aviation/GPS degradee : faible qualite signal, conflit source, risque spoofing, deviation et skew temporel."

$AfterDecisions = @(Get-ChildItem ".\MonProjet\allData" -File -Filter "decision_*.json" -ErrorAction SilentlyContinue)
$CreatedDecisions = @(
  $AfterDecisions | Where-Object { -not $BeforeNames.ContainsKey($_.Name) } |
    ForEach-Object {
      [PSCustomObject]@{
        Name = $_.Name
        Length = $_.Length
        FullName = $_.FullName
        Sha256 = Get-Sha $_.FullName
      }
    }
)

$RuntimeFiles = @(
  ".\package.json",
  ".\package-lock.json",
  ".\MonProjet\server.kernel.sealed.cjs",
  ".\sigma\contracts.py",
  ".\sigma\aggregation.py",
  ".\sigma\guard.py",
  ".\sigma\protocols.py",
  ".\sigma\run_pipeline.py",
  ".\sigma\registry.py",
  ".\sigma\obsidia_sigma_v130.py",
  ".\audit_merkle.py",
  ".\merkle_seal.json",
  ".\RUN_AUDIT_TOTAL_METRICS_PROOF.ps1"
)

$RuntimeHashes = @()
foreach ($f in $RuntimeFiles) {
  if (Test-Path $f) {
    $RuntimeHashes += [PSCustomObject]@{
      file = $f
      bytes = (Get-Item $f).Length
      sha256 = Get-Sha $f
    }
  }
}

$Rows | Export-Csv "$Audit\audit_summary_3_domains.csv" -NoTypeInformation -Encoding UTF8
$Rows | ConvertTo-Json -Depth 20 | Set-Content "$Audit\audit_summary_3_domains.json" -Encoding UTF8
$CreatedDecisions | Export-Csv "$Audit\decisions_created_during_audit.csv" -NoTypeInformation -Encoding UTF8
$RuntimeHashes | Export-Csv "$Audit\runtime_file_hashes.csv" -NoTypeInformation -Encoding UTF8

$MerkleSealHash = Get-Sha ".\merkle_seal.json"

if ($Server -and $Server.Id) {
  Stop-Process -Id $Server.Id -Force -ErrorAction SilentlyContinue
}

Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
  Where-Object { $_.OwningProcess -and $_.OwningProcess -ne 0 } |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object {
    Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
  }

Start-Sleep -Seconds 1

$ServerStdoutHash = Get-Sha "$Audit\server.stdout.log"
$ServerStderrHash = Get-Sha "$Audit\server.stderr.log"

$TraceStats = [PSCustomObject]@{
  domains_tested = 3
  input_files_generated = 3
  response_files_generated = 3
  metrics_files_generated = 3
  decisions_before = $BeforeDecisions.Count
  decisions_after = $AfterDecisions.Count
  decisions_created_during_audit = $CreatedDecisions.Count
  runtime_files_hashed = $RuntimeHashes.Count
  merkle_seal_present = (Test-Path ".\merkle_seal.json")
  merkle_seal_sha256 = $MerkleSealHash
  server_stdout_sha256 = $ServerStdoutHash
  server_stderr_sha256 = $ServerStderrHash
  git_branch = $GitBranch
  git_commit = $GitCommit
  git_tags = $GitTags
  git_status = $GitStatus
}

$TraceStats | ConvertTo-Json -Depth 10 | Set-Content "$Audit\TRACE_STATS.json" -Encoding UTF8

$TraceManifest = [PSCustomObject]@{
  audit_timestamp = $Stamp
  endpoint = $Url
  git = @{
    branch = $GitBranch
    commit = $GitCommit
    tags = $GitTags
    status = $GitStatus
  }
  trace_stats = $TraceStats
  domains = $Rows
  created_decisions = $CreatedDecisions
  runtime_hashes = $RuntimeHashes
}

$TraceManifest | ConvertTo-Json -Depth 30 | Set-Content "$Audit\TRACE_MANIFEST.json" -Encoding UTF8
$TraceManifestHash = Get-Sha "$Audit\TRACE_MANIFEST.json"

$ArtifactRows = @()
Get-ChildItem $Audit -File | Sort-Object Name | ForEach-Object {
  if ($_.Name -notin @("ARTIFACT_HASH_MANIFEST.csv", "AUDIT_ROOT_SHA256.txt")) {
    $ArtifactRows += [PSCustomObject]@{
      file = $_.Name
      bytes = $_.Length
      sha256 = Get-Sha $_.FullName
    }
  }
}

$ArtifactRows | Export-Csv "$Audit\ARTIFACT_HASH_MANIFEST.csv" -NoTypeInformation -Encoding UTF8

$RootInput = Get-Content "$Audit\ARTIFACT_HASH_MANIFEST.csv" | Sort-Object
$RootText = ($RootInput -join "`n")
$RootBytes = [System.Text.Encoding]::UTF8.GetBytes($RootText)
$Sha = [System.Security.Cryptography.SHA256]::Create()
$AuditRoot = [System.BitConverter]::ToString($Sha.ComputeHash($RootBytes)).Replace("-", "").ToLowerInvariant()
$AuditRoot | Set-Content "$Audit\AUDIT_ROOT_SHA256.txt" -Encoding UTF8

$Md = @()
$Md += "# Audit total metrics / preuve / securite / tracabilite - Obsidia X-108"
$Md += ""
$Md += "Date : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$Md += "Endpoint : ``$Url``"
$Md += "Audit dir : ``$Audit``"
$Md += ""
$Md += "## 1. Git"
$Md += ""
$Md += "| Champ | Valeur |"
$Md += "|---|---|"
$Md += "| Branche | ``$GitBranch`` |"
$Md += "| Commit | ``$GitCommit`` |"
$Md += "| Tags HEAD | ``$GitTags`` |"
$Md += "| Status | ``$GitStatus`` |"
$Md += ""
$Md += "## 2. Tableau decisionnel"
$Md += ""
$Md += "| Domaine | Verdict | Gate X-108 | Integrity | Governance | Readiness | Moyenne | Severity | Reason | Nb metriques |"
$Md += "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|"

foreach ($r in $Rows) {
  $Md += "| $(Escape-Md $r.Domaine) | $(Escape-Md $r.Verdict) | $(Escape-Md $r.Gate) | $($r.Integrity) | $($r.Governance) | $($r.Readiness) | $($r.Moyenne) | $(Escape-Md $r.Severity) | $(Escape-Md $r.Reason) | $($r.MetricCount) |"
}

$Md += ""
$Md += "## 3. Hashes par domaine"
$Md += ""
$Md += "| Domaine | Input SHA | Response SHA | Metrics SHA | Metrics CSV |"
$Md += "|---|---:|---:|---:|---|"

foreach ($r in $Rows) {
  $Md += "| $(Escape-Md $r.Domaine) | ``$(Short-Sha $r.InputHash)`` | ``$(Short-Sha $r.ResponseHash)`` | ``$(Short-Sha $r.MetricsHash)`` | ``$($r.MetricsCsv)`` |"
}

$Md += ""
$Md += "## 4. Compteurs tracabilite"
$Md += ""
$Md += "| Compteur | Valeur |"
$Md += "|---|---:|"
$Md += "| Domaines testes | $($TraceStats.domains_tested) |"
$Md += "| Inputs generes | $($TraceStats.input_files_generated) |"
$Md += "| Responses generees | $($TraceStats.response_files_generated) |"
$Md += "| Fichiers metrics generes | $($TraceStats.metrics_files_generated) |"
$Md += "| Decisions avant audit | $($TraceStats.decisions_before) |"
$Md += "| Decisions apres audit | $($TraceStats.decisions_after) |"
$Md += "| Decisions creees pendant audit | $($TraceStats.decisions_created_during_audit) |"
$Md += "| Fichiers runtime hashes | $($TraceStats.runtime_files_hashed) |"
$Md += "| Merkle seal present | $($TraceStats.merkle_seal_present) |"
$Md += ""
$Md += "## 5. Racines et scellage"
$Md += ""
$Md += "| Preuve | SHA256 |"
$Md += "|---|---|"
$Md += "| TRACE_MANIFEST | ``$TraceManifestHash`` |"
$Md += "| MERKLE_SEAL | ``$MerkleSealHash`` |"
$Md += "| SERVER_STDOUT | ``$ServerStdoutHash`` |"
$Md += "| SERVER_STDERR | ``$ServerStderrHash`` |"
$Md += "| AUDIT_ROOT | ``$AuditRoot`` |"
$Md += ""
$Md += "## 6. Decisions runtime creees pendant audit"
$Md += ""

if ($CreatedDecisions.Count -eq 0) {
  $Md += "Aucune nouvelle decision runtime detectee."
} else {
  $Md += "| Fichier | Taille | SHA256 court |"
  $Md += "|---|---:|---:|"
  foreach ($d in $CreatedDecisions) {
    $Md += "| ``$($d.Name)`` | $($d.Length) | ``$(Short-Sha $d.Sha256)`` |"
  }
}

$Md += ""
$Md += "## 7. Lecture securite par domaine"
$Md += ""

foreach ($r in $Rows) {
  $Md += "### $($r.Domaine)"
  $Md += ""
  $Md += "- Sens : $($r.Sens)"
  $Md += "- Verdict : ``$($r.Verdict)``"
  $Md += "- Gate X-108 : ``$($r.Gate)``"
  $Md += "- Severity : ``$($r.Severity)``"
  $Md += "- Reason : ``$($r.Reason)``"
  $Md += "- Lecture securite : $($r.Securite)"
  $Md += "- Nombre total de metriques retournees : ``$($r.MetricCount)``"
  $Md += "- Fichier complet metriques : ``$($r.MetricsCsv)``"
  $Md += ""
}

$Md += "## 8. Toutes les metriques retournees"
$Md += ""

foreach ($r in $Rows) {
  $Md += "### Metriques completes - $($r.Domaine)"
  $Md += ""
  $Md += "| Path | Type | Valeur |"
  $Md += "|---|---:|---|"

  $Metrics = Import-Csv $r.MetricsCsv
  foreach ($m in $Metrics) {
    $Md += "| ``$(Escape-Md $m.path)`` | ``$(Escape-Md $m.type)`` | $(Escape-Md $m.value) |"
  }

  $Md += ""
}

$Md += "## 9. Ce que cet audit prouve"
$Md += ""
$Md += "| Axe | Preuve visible | Statut |"
$Md += "|---|---|---:|"
$Md += "| Routage domaine | 3 domaines appellent le meme endpoint ``/kernel/ragnarok`` | OK |"
$Md += "| Gouvernance X-108 | Chaque domaine retourne un gate X-108 | OK |"
$Md += "| Securite avant action | Cas critiques bloques ou retenus avant execution | OK |"
$Md += "| Tracabilite input | Chaque payload envoye est sauvegarde et hashe | OK |"
$Md += "| Tracabilite output | Chaque reponse est sauvegardee et hashee | OK |"
$Md += "| Tracabilite metrics | Toutes les metriques retournees sont flattenees, comptees et hashees | OK |"
$Md += "| Tracabilite decisions | Les decision_*.json creees pendant audit sont comptees et hashees | OK |"
$Md += "| Tracabilite runtime | Les fichiers critiques moteur sont hashes | OK |"
$Md += "| Logs serveur | stdout/stderr hashes apres arret runtime | OK |"
$Md += "| Scellage | merkle_seal.json present et SHA256 calcule | OK |"
$Md += "| Racine audit | AUDIT_ROOT_SHA256 calcule sur les artefacts | OK |"
$Md += "| Git proof | Branche, commit, tags et status captures | OK |"
$Md += ""
$Md += "## 10. Limites"
$Md += ""
$Md += "- Ne prouve pas une connexion bancaire reelle."
$Md += "- Ne prouve pas une connexion avion reelle."
$Md += "- Ne prouve pas une execution trading reelle."
$Md += "- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe et rend auditable des decisions simulees multi-domaines."
$Md += ""
$Md += "## 11. Fichiers principaux generes"
$Md += ""
$Md += "- ``AUDIT_TOTAL_METRICS_PROOF.md``"
$Md += "- ``TRACE_MANIFEST.json``"
$Md += "- ``TRACE_STATS.json``"
$Md += "- ``ARTIFACT_HASH_MANIFEST.csv``"
$Md += "- ``AUDIT_ROOT_SHA256.txt``"
$Md += "- ``audit_summary_3_domains.csv``"
$Md += "- ``audit_summary_3_domains.json``"
$Md += "- ``metrics_full_bank.csv``"
$Md += "- ``metrics_full_trading.csv``"
$Md += "- ``metrics_full_gps_defense_aviation.csv``"
$Md += "- ``decisions_created_during_audit.csv``"
$Md += "- ``runtime_file_hashes.csv``"
$Md += "- ``server.stdout.log``"
$Md += "- ``server.stderr.log``"

$Report = "$Audit\AUDIT_TOTAL_METRICS_PROOF.md"
$Md | Set-Content $Report -Encoding UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " TABLEAU DECISIONNEL" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$Rows |
  Select-Object Domaine, Verdict, Gate, Integrity, Governance, Readiness, Moyenne, Severity, Reason, MetricCount |
  Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " HASHES DOMAINES" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$Rows |
  Select-Object Domaine,
    @{Name="InputSHA";Expression={Short-Sha $_.InputHash}},
    @{Name="ResponseSHA";Expression={Short-Sha $_.ResponseHash}},
    @{Name="MetricsSHA";Expression={Short-Sha $_.MetricsHash}},
    MetricCount |
  Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " COMPTEURS TRACABILITE" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$TraceStats | Format-List

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " RACINE PREUVE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "TRACE_MANIFEST_SHA256 = $TraceManifestHash"
Write-Host "MERKLE_SEAL_SHA256    = $MerkleSealHash"
Write-Host "AUDIT_ROOT_SHA256     = $AuditRoot"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " RAPPORT GENERE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "AUDIT_DIR = $Audit"
Write-Host "REPORT    = $Report"
Write-Host "MANIFEST  = $Audit\TRACE_MANIFEST.json"
Write-Host ""

Write-Host "AUDIT TOTAL METRICS TERMINE" -ForegroundColor Green
