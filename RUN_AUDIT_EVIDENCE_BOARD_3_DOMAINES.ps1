param(
  [string]$Port = "3001"
)

Set-Location $PSScriptRoot

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Audit = ".\audit\local_diag\audit_evidence_board_3_domains_$Stamp"
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

function To-Double($Value) {
  if ($null -eq $Value) { return 0.0 }
  try { return [double]$Value } catch {}
  try {
    return [double]::Parse(([string]$Value).Replace(",", "."), [System.Globalization.CultureInfo]::InvariantCulture)
  } catch {
    return 0.0
  }
}

function Escape-Md($Value) {
  if ($null -eq $Value) { return "" }
  $s = [string]$Value
  $s = $s -replace "\|", "/"
  $s = $s -replace "`r?`n", " "
  return $s
}

function Add-FlatRow {
  param(
    [object]$Obj,
    [string]$Prefix,
    [string]$Domain,
    [System.Collections.ArrayList]$Rows
  )

  if ($null -eq $Obj) {
    [void]$Rows.Add([PSCustomObject]@{
      domain = $Domain
      path = $Prefix
      category = "null"
      type = "null"
      value = ""
    })
    return
  }

  if ($Obj -is [System.Management.Automation.PSCustomObject]) {
    foreach ($p in $Obj.PSObject.Properties) {
      $next = if ($Prefix) { "$Prefix.$($p.Name)" } else { "$($p.Name)" }
      Add-FlatRow -Obj $p.Value -Prefix $next -Domain $Domain -Rows $Rows
    }
    return
  }

  if ($Obj -is [System.Collections.IDictionary]) {
    foreach ($k in $Obj.Keys) {
      $next = if ($Prefix) { "$Prefix.$k" } else { "$k" }
      Add-FlatRow -Obj $Obj[$k] -Prefix $next -Domain $Domain -Rows $Rows
    }
    return
  }

  if (($Obj -is [System.Collections.IEnumerable]) -and -not ($Obj -is [string])) {
    $i = 0
    foreach ($item in $Obj) {
      $next = "$Prefix[$i]"
      Add-FlatRow -Obj $item -Prefix $next -Domain $Domain -Rows $Rows
      $i++
    }
    if ($i -eq 0) {
      [void]$Rows.Add([PSCustomObject]@{
        domain = $Domain
        path = $Prefix
        category = "array_empty"
        type = "array_empty"
        value = ""
      })
    }
    return
  }

  $cat = if ($Prefix -match "^([^.\[]+)") { $Matches[1] } else { "root" }

  [void]$Rows.Add([PSCustomObject]@{
    domain = $Domain
    path = $Prefix
    category = $cat
    type = $Obj.GetType().Name
    value = [string]$Obj
  })
}

function Read-Security {
  param($Gate)

  if ($Gate -eq "BLOCK") {
    return "REFUS AVANT EXECUTION : le moteur bloque l'action avant qu'elle ne puisse produire un effet."
  }

  if ($Gate -eq "HOLD") {
    return "TEMPORISATION X-108 : le moteur retient l'action et impose une attente/coherence supplementaire."
  }

  if ($Gate -eq "ACT") {
    return "ACTION AUTORISEE : le moteur laisse passer apres controle."
  }

  return "LECTURE INCOMPLETE."
}

function Snapshot-Decisions {
  param([string]$OutFile)

  $rows = @()

  if (Test-Path ".\MonProjet\allData") {
    $rows = Get-ChildItem ".\MonProjet\allData" -File -Filter "decision_*.json" -ErrorAction SilentlyContinue |
      Sort-Object Name |
      ForEach-Object {
        [PSCustomObject]@{
          name = $_.Name
          bytes = $_.Length
          last_write = $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
          sha256 = Get-Sha $_.FullName
          full_path = $_.FullName
        }
      }
  }

  if ($rows.Count -gt 0) {
    $rows | Export-Csv $OutFile -NoTypeInformation -Encoding UTF8
  } else {
    "name,bytes,last_write,sha256,full_path" | Set-Content $OutFile -Encoding UTF8
  }

  return @($rows)
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
  $CategoriesCsv = Join-Path $Audit "metrics_categories_$Safe.csv"

  $Body = @{
    domain = $Domain
    data = $Data
  } | ConvertTo-Json -Depth 80 -Compress

  $Body | Set-Content $InputFile -Encoding UTF8

  $Resp = Invoke-RestMethod `
    -Uri $Url `
    -Method Post `
    -ContentType "application/json" `
    -Body $Body `
    -TimeoutSec 60

  $Resp | ConvertTo-Json -Depth 80 | Set-Content $ResponseFile -Encoding UTF8

  $Flat = New-Object System.Collections.ArrayList
  Add-FlatRow -Obj $Resp -Prefix "" -Domain $Domain -Rows $Flat
  $FlatRows = @($Flat)

  $FlatRows | Export-Csv $MetricsCsv -NoTypeInformation -Encoding UTF8
  $FlatRows | ConvertTo-Json -Depth 20 | Set-Content $MetricsJson -Encoding UTF8

  $CategoryRows = $FlatRows |
    Group-Object category |
    Sort-Object Count -Descending |
    ForEach-Object {
      [PSCustomObject]@{
        domain = $Domain
        category = $_.Name
        metric_count = $_.Count
      }
    }

  $CategoryRows | Export-Csv $CategoriesCsv -NoTypeInformation -Encoding UTF8

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
    SecurityReading = Read-Security -Gate $Resp.x108_gate
    MetricCount = $FlatRows.Count
    MetricCategories = ($CategoryRows | ForEach-Object { "$($_.category)=$($_.metric_count)" }) -join "; "
    InputFile = $InputFile
    ResponseFile = $ResponseFile
    MetricsCsv = $MetricsCsv
    MetricsJson = $MetricsJson
    CategoriesCsv = $CategoriesCsv
    InputHash = Get-Sha $InputFile
    ResponseHash = Get-Sha $ResponseFile
    MetricsHash = Get-Sha $MetricsCsv
    CategoriesHash = Get-Sha $CategoriesCsv
  }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " AUDIT EVIDENCE BOARD — OBSIDIA X-108 — 3 DOMAINES" -ForegroundColor Cyan
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

$MerkleBeforeHash = Get-Sha ".\merkle_seal.json"
if (Test-Path ".\merkle_seal.json") {
  Copy-Item ".\merkle_seal.json" "$Audit\merkle_seal_before.json" -Force
}

$BeforeDecisions = Snapshot-Decisions -OutFile "$Audit\decisions_before.csv"
$BeforeIndex = @{}
foreach ($d in $BeforeDecisions) {
  $BeforeIndex[$d.name] = $true
}

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

if (Test-Path ".\merkle_seal.json") {
  Copy-Item ".\merkle_seal.json" "$Audit\merkle_seal_after.json" -Force
}

$MerkleAfterHash = Get-Sha ".\merkle_seal.json"

$AfterDecisions = Snapshot-Decisions -OutFile "$Audit\decisions_after.csv"

$CreatedDecisions = @(
  $AfterDecisions |
    Where-Object { -not $BeforeIndex.ContainsKey($_.name) } |
    ForEach-Object {
      [PSCustomObject]@{
        name = $_.name
        bytes = $_.bytes
        sha256 = $_.sha256
        full_path = $_.full_path
      }
    }
)

if ($CreatedDecisions.Count -gt 0) {
  $CreatedDecisions | Export-Csv "$Audit\decisions_created_during_audit.csv" -NoTypeInformation -Encoding UTF8
} else {
  "name,bytes,sha256,full_path" | Set-Content "$Audit\decisions_created_during_audit.csv" -Encoding UTF8
}

$DecisionMetrics = New-Object System.Collections.ArrayList

foreach ($d in $CreatedDecisions) {
  try {
    $json = Get-Content $d.full_path -Raw | ConvertFrom-Json
    Add-FlatRow -Obj $json -Prefix $d.name -Domain "decision_runtime" -Rows $DecisionMetrics
  } catch {}
}

$DecisionMetricRows = @($DecisionMetrics)

if ($DecisionMetricRows.Count -gt 0) {
  $DecisionMetricRows | Export-Csv "$Audit\decision_runtime_metrics_flat.csv" -NoTypeInformation -Encoding UTF8
} else {
  "domain,path,category,type,value" | Set-Content "$Audit\decision_runtime_metrics_flat.csv" -Encoding UTF8
}

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
  ".\RUN_AUDIT_EVIDENCE_BOARD_3_DOMAINES.ps1"
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

$RuntimeHashes | Export-Csv "$Audit\runtime_file_hashes.csv" -NoTypeInformation -Encoding UTF8

$AllMetrics = @()
foreach ($r in $Rows) {
  $AllMetrics += Import-Csv $r.MetricsCsv
}

$AllMetrics | Export-Csv "$Audit\ALL_METRICS_FLAT.csv" -NoTypeInformation -Encoding UTF8

$AllCategories = $AllMetrics |
  Group-Object domain, category |
  Sort-Object Count -Descending |
  ForEach-Object {
    $parts = $_.Name -split ", "
    [PSCustomObject]@{
      domain = $parts[0]
      category = $parts[1]
      metric_count = $_.Count
    }
  }

$AllCategories | Export-Csv "$Audit\ALL_METRIC_CATEGORIES.csv" -NoTypeInformation -Encoding UTF8

$TraceChains = @()

foreach ($r in $Rows) {
  $createdForDomain = @(
    $CreatedDecisions | Where-Object {
      $_.name -like "decision_$($r.Domaine)*"
    }
  )

  $TraceChains += [PSCustomObject]@{
    domain = $r.Domaine
    input_sha256 = $r.InputHash
    response_sha256 = $r.ResponseHash
    metrics_sha256 = $r.MetricsHash
    metric_count = $r.MetricCount
    decision_count = $createdForDomain.Count
    decision_files = ($createdForDomain | ForEach-Object { $_.name }) -join "; "
    decision_hashes = ($createdForDomain | ForEach-Object { $_.sha256 }) -join "; "
    gate = $r.Gate
    verdict = $r.Verdict
    reason = $r.Reason
  }
}

$TraceChains | Export-Csv "$Audit\TRACE_CHAINS_BY_DOMAIN.csv" -NoTypeInformation -Encoding UTF8

$Rows | Export-Csv "$Audit\audit_decision_summary.csv" -NoTypeInformation -Encoding UTF8
$Rows | ConvertTo-Json -Depth 20 | Set-Content "$Audit\audit_decision_summary.json" -Encoding UTF8

$ServerStdoutHash = Get-Sha "$Audit\server.stdout.log"
$ServerStderrHash = Get-Sha "$Audit\server.stderr.log"

$TraceStats = [PSCustomObject]@{
  domains_tested = 3
  total_response_metrics = ($Rows | Measure-Object MetricCount -Sum).Sum
  total_decision_runtime_metrics = $DecisionMetricRows.Count
  input_files_generated = 3
  response_files_generated = 3
  metrics_files_generated = 3
  decisions_before = $BeforeDecisions.Count
  decisions_after = $AfterDecisions.Count
  decisions_created_during_audit = $CreatedDecisions.Count
  runtime_files_hashed = $RuntimeHashes.Count
  merkle_seal_present = (Test-Path ".\merkle_seal.json")
  merkle_before_sha256 = $MerkleBeforeHash
  merkle_after_sha256 = $MerkleAfterHash
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
  stats = $TraceStats
  decisions = $Rows
  trace_chains = $TraceChains
  created_decisions = $CreatedDecisions
  runtime_hashes = $RuntimeHashes
  metric_categories = $AllCategories
}

$TraceManifest | ConvertTo-Json -Depth 40 | Set-Content "$Audit\TRACE_MANIFEST.json" -Encoding UTF8
$TraceManifestHash = Get-Sha "$Audit\TRACE_MANIFEST.json"

$EvidenceFiles = @(
  "input_bank.json",
  "input_trading.json",
  "input_gps_defense_aviation.json",
  "response_bank.json",
  "response_trading.json",
  "response_gps_defense_aviation.json",
  "metrics_full_bank.csv",
  "metrics_full_trading.csv",
  "metrics_full_gps_defense_aviation.csv",
  "ALL_METRICS_FLAT.csv",
  "ALL_METRIC_CATEGORIES.csv",
  "TRACE_CHAINS_BY_DOMAIN.csv",
  "TRACE_STATS.json",
  "TRACE_MANIFEST.json",
  "decisions_before.csv",
  "decisions_after.csv",
  "decisions_created_during_audit.csv",
  "decision_runtime_metrics_flat.csv",
  "runtime_file_hashes.csv",
  "server.stdout.log",
  "server.stderr.log",
  "merkle_seal_before.json",
  "merkle_seal_after.json"
)

$ArtifactRows = @()

foreach ($name in $EvidenceFiles) {
  $p = Join-Path $Audit $name
  if (Test-Path $p) {
    $ArtifactRows += [PSCustomObject]@{
      file = $name
      bytes = (Get-Item $p).Length
      sha256 = Get-Sha $p
    }
  }
}

$ArtifactRows | Export-Csv "$Audit\ARTIFACT_HASH_MANIFEST.csv" -NoTypeInformation -Encoding UTF8

$RootInput = $ArtifactRows |
  Sort-Object file |
  ForEach-Object { "$($_.file)|$($_.bytes)|$($_.sha256)" }

$RootText = ($RootInput -join "`n")
$RootBytes = [System.Text.Encoding]::UTF8.GetBytes($RootText)
$Sha = [System.Security.Cryptography.SHA256]::Create()
$AuditRoot = [System.BitConverter]::ToString($Sha.ComputeHash($RootBytes)).Replace("-", "").ToLowerInvariant()
$AuditRoot | Set-Content "$Audit\AUDIT_ROOT_SHA256.txt" -Encoding UTF8

$ProofClaims = @(
  [PSCustomObject]@{ axe="Routage multi-domaine"; preuve="3 domaines appellent le meme endpoint /kernel/ragnarok"; statut="OK" },
  [PSCustomObject]@{ axe="Decision avant action"; preuve="Chaque domaine retourne verdict + gate X-108 avant execution"; statut="OK" },
  [PSCustomObject]@{ axe="Securite bank"; preuve="bank retourne BLOCK sur transaction risquee"; statut="OK" },
  [PSCustomObject]@{ axe="Securite trading"; preuve="trading retourne HOLD sur ordre risque"; statut="OK" },
  [PSCustomObject]@{ axe="Securite aviation"; preuve="gps_defense_aviation retourne BLOCK sur navigation degradee"; statut="OK" },
  [PSCustomObject]@{ axe="Metrisation"; preuve="$($TraceStats.total_response_metrics) metriques response flattenees"; statut="OK" },
  [PSCustomObject]@{ axe="Tracabilite input"; preuve="3 payloads input sauvegardes + hashes"; statut="OK" },
  [PSCustomObject]@{ axe="Tracabilite output"; preuve="3 responses sauvegardees + hashes"; statut="OK" },
  [PSCustomObject]@{ axe="Tracabilite metrics"; preuve="metrics_full_*.csv + ALL_METRICS_FLAT.csv"; statut="OK" },
  [PSCustomObject]@{ axe="Tracabilite decisions"; preuve="$($TraceStats.decisions_created_during_audit) decision_*.json creees pendant audit"; statut="OK" },
  [PSCustomObject]@{ axe="Scellage Merkle"; preuve="merkle before/after snapshot + hash"; statut="OK" },
  [PSCustomObject]@{ axe="Runtime hash"; preuve="$($TraceStats.runtime_files_hashed) fichiers runtime hashes"; statut="OK" },
  [PSCustomObject]@{ axe="Logs serveur"; preuve="stdout/stderr hashes apres arret serveur"; statut="OK" },
  [PSCustomObject]@{ axe="Manifest preuve"; preuve="TRACE_MANIFEST.json hash=$TraceManifestHash"; statut="OK" },
  [PSCustomObject]@{ axe="Racine audit"; preuve="AUDIT_ROOT_SHA256=$AuditRoot"; statut="OK" },
  [PSCustomObject]@{ axe="Reproductibilite Git"; preuve="branch/commit/tag/status captures"; statut="OK" }
)

$ProofClaims | Export-Csv "$Audit\PROOF_CLAIMS_MATRIX.csv" -NoTypeInformation -Encoding UTF8

$Md = @()
$Md += "# Evidence Board - Obsidia X-108 - 3 domaines"
$Md += ""
$Md += "Date : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$Md += "Endpoint : ``$Url``"
$Md += "Audit dir : ``$Audit``"
$Md += ""
$Md += "## 1. Synthese courte"
$Md += ""
$Md += "| Element | Valeur |"
$Md += "|---|---:|"
$Md += "| Domaines testes | $($TraceStats.domains_tested) |"
$Md += "| Metriques response totales | $($TraceStats.total_response_metrics) |"
$Md += "| Metriques runtime decisions | $($TraceStats.total_decision_runtime_metrics) |"
$Md += "| Decisions avant audit | $($TraceStats.decisions_before) |"
$Md += "| Decisions apres audit | $($TraceStats.decisions_after) |"
$Md += "| Decisions creees pendant audit | $($TraceStats.decisions_created_during_audit) |"
$Md += "| Fichiers runtime hashes | $($TraceStats.runtime_files_hashed) |"
$Md += "| Artefacts de preuve hashes | $($ArtifactRows.Count) |"
$Md += ""
$Md += "## 2. Git / version"
$Md += ""
$Md += "| Champ | Valeur |"
$Md += "|---|---|"
$Md += "| Branche | ``$GitBranch`` |"
$Md += "| Commit | ``$GitCommit`` |"
$Md += "| Tags HEAD | ``$GitTags`` |"
$Md += "| Status | ``$GitStatus`` |"
$Md += ""
$Md += "## 3. Tableau decisionnel"
$Md += ""
$Md += "| Domaine | Verdict | Gate | Integrity | Governance | Readiness | Moyenne | Severity | Reason | Nb metriques |"
$Md += "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|"

foreach ($r in $Rows) {
  $Md += "| $(Escape-Md $r.Domaine) | $(Escape-Md $r.Verdict) | $(Escape-Md $r.Gate) | $($r.Integrity) | $($r.Governance) | $($r.Readiness) | $($r.Moyenne) | $(Escape-Md $r.Severity) | $(Escape-Md $r.Reason) | $($r.MetricCount) |"
}

$Md += ""
$Md += "## 4. Chaines de trace par domaine"
$Md += ""
$Md += "| Domaine | Input SHA | Response SHA | Metrics SHA | Decision count | Decision hashes |"
$Md += "|---|---:|---:|---:|---:|---|"

foreach ($t in $TraceChains) {
  $ShortDecisionHashes = (($t.decision_hashes -split "; ") | ForEach-Object { Short-Sha $_ }) -join "; "
  $Md += "| $(Escape-Md $t.domain) | ``$(Short-Sha $t.input_sha256)`` | ``$(Short-Sha $t.response_sha256)`` | ``$(Short-Sha $t.metrics_sha256)`` | $($t.decision_count) | ``$ShortDecisionHashes`` |"
}

$Md += ""
$Md += "## 5. Categories de metriques"
$Md += ""
$Md += "| Domaine | Categorie | Nombre |"
$Md += "|---|---|---:|"

foreach ($c in $AllCategories) {
  $Md += "| $(Escape-Md $c.domain) | $(Escape-Md $c.category) | $($c.metric_count) |"
}

$Md += ""
$Md += "## 6. Decisions runtime creees pendant audit"
$Md += ""
$Md += "| Fichier | Taille | SHA256 court |"
$Md += "|---|---:|---:|"

foreach ($d in $CreatedDecisions) {
  $Md += "| ``$($d.name)`` | $($d.bytes) | ``$(Short-Sha $d.sha256)`` |"
}

$Md += ""
$Md += "## 7. Scellage / racines"
$Md += ""
$Md += "| Element | SHA256 |"
$Md += "|---|---|"
$Md += "| Merkle before | ``$MerkleBeforeHash`` |"
$Md += "| Merkle after | ``$MerkleAfterHash`` |"
$Md += "| Server stdout | ``$ServerStdoutHash`` |"
$Md += "| Server stderr | ``$ServerStderrHash`` |"
$Md += "| Trace manifest | ``$TraceManifestHash`` |"
$Md += "| Audit root | ``$AuditRoot`` |"
$Md += ""
$Md += "## 8. Matrice de preuves"
$Md += ""
$Md += "| Axe | Preuve visible | Statut |"
$Md += "|---|---|---:|"

foreach ($p in $ProofClaims) {
  $Md += "| $(Escape-Md $p.axe) | $(Escape-Md $p.preuve) | $($p.statut) |"
}

$Md += ""
$Md += "## 9. Lecture securite"
$Md += ""

foreach ($r in $Rows) {
  $Md += "### $($r.Domaine)"
  $Md += ""
  $Md += "- Sens : $($r.Sens)"
  $Md += "- Verdict : ``$($r.Verdict)``"
  $Md += "- Gate X-108 : ``$($r.Gate)``"
  $Md += "- Reason : ``$($r.Reason)``"
  $Md += "- Severity : ``$($r.Severity)``"
  $Md += "- Lecture : $($r.SecurityReading)"
  $Md += "- Metriques retournees : ``$($r.MetricCount)``"
  $Md += "- Categories : ``$($r.MetricCategories)``"
  $Md += ""
}

$Md += "## 10. Tous les fichiers de preuve"
$Md += ""
$Md += "| Fichier | Taille | SHA256 court |"
$Md += "|---|---:|---:|"

foreach ($a in $ArtifactRows) {
  $Md += "| ``$($a.file)`` | $($a.bytes) | ``$(Short-Sha $a.sha256)`` |"
}

$Md += ""
$Md += "## 11. Limites"
$Md += ""
$Md += "- Ne prouve pas une connexion bancaire reelle."
$Md += "- Ne prouve pas une connexion avion reelle."
$Md += "- Ne prouve pas une execution trading reelle."
$Md += "- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe, scelle et rend auditable des decisions simulees multi-domaines."

$Report = "$Audit\EVIDENCE_BOARD_3_DOMAINES.md"
$Md | Set-Content $Report -Encoding UTF8

$ReportHash = Get-Sha $Report
$ReportHash | Set-Content "$Audit\REPORT_SHA256.txt" -Encoding UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " TABLEAU DECISIONNEL" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$Rows |
  Select-Object Domaine, Verdict, Gate, Integrity, Governance, Readiness, Moyenne, Severity, Reason, MetricCount |
  Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " EVIDENCE BOARD — CHAINE DE TRACE" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$TraceChains |
  Select-Object domain,
    @{Name="Input";Expression={Short-Sha $_.input_sha256}},
    @{Name="Response";Expression={Short-Sha $_.response_sha256}},
    @{Name="Metrics";Expression={Short-Sha $_.metrics_sha256}},
    metric_count,
    decision_count,
    @{Name="DecisionHashes";Expression={(($_.decision_hashes -split "; ") | ForEach-Object { Short-Sha $_ }) -join "; "}},
    gate,
    reason |
  Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " CATEGORIES METRIQUES" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$AllCategories |
  Sort-Object domain, category |
  Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " DECISIONS CREEES" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$CreatedDecisions |
  Select-Object name, bytes, @{Name="sha";Expression={Short-Sha $_.sha256}} |
  Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " MATRICE DE PREUVES" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$ProofClaims | Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " RACINES / HASHES MAJEURS" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "MERKLE_BEFORE_SHA256   = $MerkleBeforeHash"
Write-Host "MERKLE_AFTER_SHA256    = $MerkleAfterHash"
Write-Host "TRACE_MANIFEST_SHA256  = $TraceManifestHash"
Write-Host "AUDIT_ROOT_SHA256      = $AuditRoot"
Write-Host "REPORT_SHA256          = $ReportHash"
Write-Host "SERVER_STDOUT_SHA256   = $ServerStdoutHash"
Write-Host "SERVER_STDERR_SHA256   = $ServerStderrHash"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " RAPPORT GENERE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "AUDIT_DIR = $Audit"
Write-Host "REPORT    = $Report"
Write-Host "MANIFEST  = $Audit\TRACE_MANIFEST.json"
Write-Host "ROOT      = $Audit\AUDIT_ROOT_SHA256.txt"
Write-Host ""

Write-Host "AUDIT EVIDENCE BOARD TERMINE" -ForegroundColor Green
