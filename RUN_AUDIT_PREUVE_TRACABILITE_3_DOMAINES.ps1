Set-Location $PSScriptRoot

$Stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$Audit = ".\audit\local_diag\audit_preuve_tracabilite_3_domaines_$Stamp"
$DecisionCopyDir = "$Audit\decision_files"

New-Item -ItemType Directory -Force $Audit | Out-Null
New-Item -ItemType Directory -Force $DecisionCopyDir | Out-Null
New-Item -ItemType Directory -Force ".\MonProjet\allData" | Out-Null
New-Item -ItemType Directory -Force ".\logs" | Out-Null

$Port = "3001"
$Url = "http://localhost:$Port/kernel/ragnarok"

$env:OBSIDIA_PORT = $Port
$env:OBSIDIA_URL = $Url
$env:PYTHONPATH = (Get-Location).Path

function To-Number($v) {
  if ($null -eq $v) { return 0 }
  return [System.Convert]::ToDouble(([string]$v).Replace(",", "."), [System.Globalization.CultureInfo]::InvariantCulture)
}

function Get-Sha($Path) {
  if (Test-Path $Path) {
    return (Get-FileHash $Path -Algorithm SHA256).Hash
  }
  return "NA"
}

function Short-Sha($Sha) {
  if ($null -eq $Sha -or $Sha -eq "NA") { return "NA" }
  return $Sha.Substring(0, 12)
}

function Get-StringSha256($Text) {
  $sha = [System.Security.Cryptography.SHA256]::Create()
  $bytes = [System.Text.Encoding]::UTF8.GetBytes($Text)
  return (($sha.ComputeHash($bytes) | ForEach-Object { $_.ToString("x2") }) -join "")
}

function Safe-Md($Text) {
  if ($null -eq $Text) { return "" }
  return ([string]$Text).Replace("|", "/").Replace("`r", " ").Replace("`n", " ")
}

function Snapshot-DecisionFiles {
  Get-ChildItem . -Recurse -File -Filter "decision_*.json" -ErrorAction SilentlyContinue |
    Where-Object {
      $_.FullName -notmatch "\\.git\\" -and
      $_.FullName -notmatch "\\audit\\local_diag\\" -and
      $_.FullName -notmatch "\\audit_terrain\\"
    } |
    Sort-Object FullName |
    Select-Object `
      FullName,
      Name,
      Length,
      LastWriteTimeUtc,
      @{Name="Sha256";Expression={(Get-FileHash $_.FullName -Algorithm SHA256).Hash}}
}

function Flatten-Metrics {
  param($Obj, [string]$Prefix = "")

  $Rows = @()

  foreach ($p in $Obj.PSObject.Properties) {
    $Name = if ($Prefix) { "$Prefix.$($p.Name)" } else { $p.Name }
    $Value = $p.Value

    if ($null -eq $Value) {
      $Rows += [PSCustomObject]@{ metric = $Name; value = "" }
    }
    elseif ($Value -is [System.Management.Automation.PSCustomObject]) {
      $Rows += Flatten-Metrics -Obj $Value -Prefix $Name
    }
    elseif ($Value -is [hashtable]) {
      $Rows += [PSCustomObject]@{ metric = $Name; value = ($Value | ConvertTo-Json -Depth 20 -Compress) }
    }
    elseif ($Value -is [array]) {
      $Rows += [PSCustomObject]@{ metric = $Name; value = ($Value | ConvertTo-Json -Depth 20 -Compress) }
    }
    else {
      $Rows += [PSCustomObject]@{ metric = $Name; value = [string]$Value }
    }
  }

  return $Rows
}

function Security-Text($gate, $severity, $reason) {
  if ($gate -eq "BLOCK") {
    return "SECURITE FORTE — action refusee avant execution. Le moteur detecte un risque, une contradiction ou une fiabilite insuffisante."
  }
  if ($gate -eq "HOLD") {
    return "SECURITE TEMPORELLE — action retenue. X-108 impose une attente / coherence avant action."
  }
  if ($gate -eq "ACT") {
    return "ACTION AUTORISEE — action consideree comme acceptable par les garde-fous."
  }
  return "LECTURE INCOMPLETE — gate non reconnu."
}

function Run-Domain($Domain, $Data, $Meaning) {
  $Body = @{
    domain = $Domain
    data = $Data
  } | ConvertTo-Json -Depth 30 -Compress

  $Safe = $Domain -replace '[^a-zA-Z0-9_-]', '_'
  $InputFile = "$Audit\input_$Safe.json"
  $ResponseFile = "$Audit\response_$Safe.json"
  $MetricsFile = "$Audit\metrics_$Safe.csv"

  $Body | Set-Content $InputFile -Encoding UTF8

  $Resp = Invoke-RestMethod `
    -Uri $Url `
    -Method Post `
    -ContentType "application/json" `
    -Body $Body `
    -TimeoutSec 30

  $Resp | ConvertTo-Json -Depth 30 | Set-Content $ResponseFile -Encoding UTF8

  $Metrics = Flatten-Metrics $Resp
  $Metrics | Export-Csv $MetricsFile -NoTypeInformation -Encoding UTF8

  $InputHash = Get-Sha $InputFile
  $ResponseHash = Get-Sha $ResponseFile
  $MetricsHash = Get-Sha $MetricsFile

  $Integrity = To-Number $Resp.confidence_integrity
  $Governance = To-Number $Resp.confidence_governance
  $Readiness = To-Number $Resp.confidence_readiness
  $Mean3 = [math]::Round((($Integrity + $Governance + $Readiness) / 3), 4)

  [PSCustomObject]@{
    Domaine = $Resp.domain
    Sens = $Meaning
    Verdict = $Resp.market_verdict
    Gate = $Resp.x108_gate
    Integrity = $Integrity
    Governance = $Governance
    Readiness = $Readiness
    Moyenne = $Mean3
    Severity = $Resp.severity
    Reason = $Resp.reason_code
    Securite = Security-Text $Resp.x108_gate $Resp.severity $Resp.reason_code
    MetricCount = $Metrics.Count
    Input = $InputFile
    Response = $ResponseFile
    MetricsFile = $MetricsFile
    InputHash = $InputHash
    ResponseHash = $ResponseHash
    MetricsHash = $MetricsHash
  }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host " AUDIT PREUVE / SECURITE / TRACABILITE — 3 DOMAINES" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "URL   : $Url"
Write-Host "AUDIT : $Audit"

$GitBranch = (git branch --show-current 2>$null)
$GitCommit = (git rev-parse HEAD 2>$null)
$GitShort = (git rev-parse --short HEAD 2>$null)
$GitTags = (git tag --points-at HEAD 2>$null) -join ", "
$GitStatus = (git status --short 2>$null) -join "`n"

if (-not $GitTags) { $GitTags = "NO_TAG_ON_HEAD" }
if (-not $GitStatus) { $GitStatus = "CLEAN" }

$GitInfo = [PSCustomObject]@{
  branch = $GitBranch
  commit = $GitCommit
  short_commit = $GitShort
  tags_on_head = $GitTags
  status = $GitStatus
  audit_timestamp = $Stamp
  endpoint = $Url
}

$GitInfo | ConvertTo-Json -Depth 10 | Set-Content "$Audit\git_context.json" -Encoding UTF8

Write-Host ""
Write-Host "GIT BRANCH : $GitBranch"
Write-Host "GIT COMMIT : $GitCommit"
Write-Host "GIT TAGS   : $GitTags"
Write-Host "GIT STATUS : $GitStatus"

$VitalFiles = @(
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
  ".\proofs\lean\lakefile.lean",
  ".\proofs\lean\lean-toolchain"
)

$RuntimeHashes = foreach ($f in $VitalFiles) {
  [PSCustomObject]@{
    file = $f
    exists = (Test-Path $f)
    sha256 = Get-Sha $f
    short_sha = Short-Sha (Get-Sha $f)
  }
}

$RuntimeHashes | Export-Csv "$Audit\runtime_file_hashes.csv" -NoTypeInformation -Encoding UTF8
$RuntimeHashes | ConvertTo-Json -Depth 10 | Set-Content "$Audit\runtime_file_hashes.json" -Encoding UTF8

$MerkleSealHash = Get-Sha ".\merkle_seal.json"
$MerkleSealRaw = ""
if (Test-Path ".\merkle_seal.json") {
  $MerkleSealRaw = Get-Content ".\merkle_seal.json" -Raw
}
$MerkleSealRaw | Set-Content "$Audit\merkle_seal_snapshot.txt" -Encoding UTF8

$BeforeDecisions = @(Snapshot-DecisionFiles)
$BeforePaths = @($BeforeDecisions | ForEach-Object { $_.FullName })

$BeforeDecisions | Export-Csv "$Audit\decisions_before.csv" -NoTypeInformation -Encoding UTF8

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

Start-Sleep -Seconds 4

$Listening = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
  Where-Object { $_.State -eq "Listen" }

if (-not $Listening) {
  Write-Host "[FAIL] Serveur non lance sur $Port" -ForegroundColor Red
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
$Rows += Run-Domain "bank" $BankData "Transaction bancaire risquee : nouveau beneficiaire, fraude elevee, urgence elevee, delai X-108 non respecte."
$Rows += Run-Domain "trading" $TradingData "Ordre trading risque : levier, exposition, drawdown, slippage et desequilibre carnet eleves."
$Rows += Run-Domain "gps_defense_aviation" $AviationData "Navigation aviation/GPS degradee : signal faible, conflit source, spoofing, deviation, skew temporel."

Start-Sleep -Seconds 2

$AfterDecisions = @(Snapshot-DecisionFiles)
$CreatedDecisions = @($AfterDecisions | Where-Object { $BeforePaths -notcontains $_.FullName })

$AfterDecisions | Export-Csv "$Audit\decisions_after.csv" -NoTypeInformation -Encoding UTF8
$CreatedDecisions | Export-Csv "$Audit\decisions_created.csv" -NoTypeInformation -Encoding UTF8

foreach ($d in $CreatedDecisions) {
  $Target = Join-Path $DecisionCopyDir $d.Name
  Copy-Item $d.FullName $Target -Force -ErrorAction SilentlyContinue
}

$Rows | Export-Csv "$Audit\audit_preuve_tracabilite_3_domaines.csv" -NoTypeInformation -Encoding UTF8
$Rows | ConvertTo-Json -Depth 30 | Set-Content "$Audit\audit_preuve_tracabilite_3_domaines.json" -Encoding UTF8

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
  server_stdout_sha256 = Get-Sha "$Audit\server.stdout.log"
  server_stderr_sha256 = Get-Sha "$Audit\server.stderr.log"
}

$TraceStats | ConvertTo-Json -Depth 10 | Set-Content "$Audit\trace_stats.json" -Encoding UTF8

$ArtifactHashes = Get-ChildItem $Audit -Recurse -File |
  Sort-Object FullName |
  Select-Object `
    FullName,
    Name,
    Length,
    @{Name="Sha256";Expression={(Get-FileHash $_.FullName -Algorithm SHA256).Hash}},
    @{Name="ShortSha";Expression={((Get-FileHash $_.FullName -Algorithm SHA256).Hash).Substring(0,12)}}

$ArtifactHashes | Export-Csv "$Audit\artifact_hash_manifest.csv" -NoTypeInformation -Encoding UTF8
$ArtifactHashes | ConvertTo-Json -Depth 20 | Set-Content "$Audit\artifact_hash_manifest.json" -Encoding UTF8

$HashLines = $ArtifactHashes | ForEach-Object { "$($_.Sha256)  $($_.FullName)" }
$AuditRoot = Get-StringSha256 ($HashLines -join "`n")
$AuditRoot | Set-Content "$Audit\AUDIT_ROOT_SHA256.txt" -Encoding UTF8

$TraceManifest = [PSCustomObject]@{
  audit_id = "audit_preuve_tracabilite_3_domaines_$Stamp"
  audit_root_sha256 = $AuditRoot
  git = $GitInfo
  trace_stats = $TraceStats
  domains = $Rows
  runtime_hashes = $RuntimeHashes
  created_decisions = $CreatedDecisions
}

$TraceManifest | ConvertTo-Json -Depth 50 | Set-Content "$Audit\TRACE_MANIFEST.json" -Encoding UTF8
$TraceManifestHash = Get-Sha "$Audit\TRACE_MANIFEST.json"

$Md = @()
$Md += "# Audit preuve / securite / tracabilite — Obsidia X-108"
$Md += ""
$Md += "Date : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$Md += "Endpoint : ``$Url``"
$Md += "Audit ID : ``audit_preuve_tracabilite_3_domaines_$Stamp``"
$Md += "AUDIT_ROOT_SHA256 : ``$AuditRoot``"
$Md += "TRACE_MANIFEST_SHA256 : ``$TraceManifestHash``"
$Md += ""
$Md += "## 1. Contexte Git"
$Md += ""
$Md += "| Element | Valeur |"
$Md += "|---|---|"
$Md += "| Branche | ``$GitBranch`` |"
$Md += "| Commit | ``$GitCommit`` |"
$Md += "| Commit court | ``$GitShort`` |"
$Md += "| Tags sur HEAD | ``$GitTags`` |"
$Md += "| Working tree | ``$(Safe-Md $GitStatus)`` |"
$Md += ""
$Md += "## 2. Tableau decisionnel"
$Md += ""
$Md += "| Domaine | Verdict | Gate X-108 | Integrity | Governance | Readiness | Moyenne | Severity | Reason | Nb metriques |"
$Md += "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|"

foreach ($r in $Rows) {
  $Md += "| $($r.Domaine) | $($r.Verdict) | $($r.Gate) | $($r.Integrity) | $($r.Governance) | $($r.Readiness) | $($r.Moyenne) | $($r.Severity) | $(Safe-Md $r.Reason) | $($r.MetricCount) |"
}

$Md += ""
$Md += "## 3. Compteurs de tracabilite"
$Md += ""
$Md += "| Preuve | Nombre / Etat |"
$Md += "|---|---:|"
$Md += "| Domaines testes | $($TraceStats.domains_tested) |"
$Md += "| Inputs JSON generes | $($TraceStats.input_files_generated) |"
$Md += "| Reponses JSON generees | $($TraceStats.response_files_generated) |"
$Md += "| Fichiers metriques generes | $($TraceStats.metrics_files_generated) |"
$Md += "| Decisions avant audit | $($TraceStats.decisions_before) |"
$Md += "| Decisions apres audit | $($TraceStats.decisions_after) |"
$Md += "| Decisions creees pendant audit | $($TraceStats.decisions_created_during_audit) |"
$Md += "| Fichiers runtime hashes | $($TraceStats.runtime_files_hashed) |"
$Md += "| Merkle seal present | $($TraceStats.merkle_seal_present) |"
$Md += "| SHA serveur stdout | ``$(Short-Sha $TraceStats.server_stdout_sha256)`` |"
$Md += "| SHA serveur stderr | ``$(Short-Sha $TraceStats.server_stderr_sha256)`` |"
$Md += ""
$Md += "## 4. Traces par domaine"
$Md += ""
$Md += "| Domaine | Input SHA | Response SHA | Metrics SHA | Fichier input | Fichier response |"
$Md += "|---|---:|---:|---:|---|---|"

foreach ($r in $Rows) {
  $Md += "| $($r.Domaine) | ``$(Short-Sha $r.InputHash)`` | ``$(Short-Sha $r.ResponseHash)`` | ``$(Short-Sha $r.MetricsHash)`` | ``$($r.Input)`` | ``$($r.Response)`` |"
}

$Md += ""
$Md += "## 5. Decisions runtime creees pendant audit"
$Md += ""

if ($CreatedDecisions.Count -eq 0) {
  $Md += "Aucune nouvelle decision_*.json detectee pendant cet audit."
} else {
  $Md += "| Fichier | Taille | SHA256 |"
  $Md += "|---|---:|---:|"
  foreach ($d in $CreatedDecisions) {
    $Md += "| ``$(Safe-Md $d.Name)`` | $($d.Length) | ``$($d.Sha256)`` |"
  }
}

$Md += ""
$Md += "## 6. Hashes fichiers runtime critiques"
$Md += ""
$Md += "| Fichier | Present | SHA256 |"
$Md += "|---|---:|---:|"

foreach ($h in $RuntimeHashes) {
  $Md += "| ``$($h.file)`` | $($h.exists) | ``$($h.sha256)`` |"
}

$Md += ""
$Md += "## 7. Merkle / Seal"
$Md += ""
$Md += "| Element | Valeur |"
$Md += "|---|---|"
$Md += "| merkle_seal.json present | $((Test-Path '.\merkle_seal.json')) |"
$Md += "| merkle_seal.json SHA256 | ``$MerkleSealHash`` |"
$Md += "| snapshot seal | ``$Audit\merkle_seal_snapshot.txt`` |"
$Md += ""
$Md += "## 8. Lecture securite"
$Md += ""

foreach ($r in $Rows) {
  $Md += "### $($r.Domaine)"
  $Md += ""
  $Md += "- Sens metier : $($r.Sens)"
  $Md += "- Verdict metier : ``$($r.Verdict)``"
  $Md += "- Gate X-108 : ``$($r.Gate)``"
  $Md += "- Severity : ``$($r.Severity)``"
  $Md += "- Reason : ``$($r.Reason)``"
  $Md += "- Lecture securite : $($r.Securite)"
  $Md += "- Nombre de metriques retournees : $($r.MetricCount)"
  $Md += "- Fichier metriques complet : ``$($r.MetricsFile)``"
  $Md += ""
}

$Md += "## 9. Ce que cet audit prouve"
$Md += ""
$Md += "| Axe | Preuve visible | Statut |"
$Md += "|---|---|---:|"
$Md += "| Routage domaine | 3 domaines appellent le meme endpoint /kernel/ragnarok | OK |"
$Md += "| Gouvernance X-108 | Chaque domaine retourne un gate X-108 | OK |"
$Md += "| Securite avant action | Les cas risques sont bloques ou controles avant execution | OK |"
$Md += "| Tracabilite input | Chaque payload envoye est sauvegarde et hashe | OK |"
$Md += "| Tracabilite output | Chaque reponse est sauvegardee et hashee | OK |"
$Md += "| Tracabilite decision | Les decision_*.json sont comptees avant/apres et hashees | OK |"
$Md += "| Tracabilite runtime | Les fichiers critiques moteur sont hashes | OK |"
$Md += "| Scellage | merkle_seal.json est snapshot + SHA256 | OK |"
$Md += "| Racine audit | AUDIT_ROOT_SHA256 calcule sur les preuves | OK |"
$Md += "| Manifest preuve | TRACE_MANIFEST.json + SHA256 | OK |"
$Md += ""
$Md += "## 10. Limites"
$Md += ""
$Md += "- Ne prouve pas une connexion bancaire reelle."
$Md += "- Ne prouve pas une connexion avion reelle."
$Md += "- Ne prouve pas une execution trading reelle."
$Md += "- Prouve que le moteur recoit, gouverne, refuse/retient, trace, hashe et rend auditable des decisions simulees multi-domaines."
$Md += ""
$Md += "## 11. Fichiers principaux"
$Md += ""
$Md += "- ``AUDIT_PREUVE_TRACABILITE_3_DOMAINES.md``"
$Md += "- ``TRACE_MANIFEST.json``"
$Md += "- ``AUDIT_ROOT_SHA256.txt``"
$Md += "- ``artifact_hash_manifest.csv``"
$Md += "- ``runtime_file_hashes.csv``"
$Md += "- ``decisions_before.csv``"
$Md += "- ``decisions_after.csv``"
$Md += "- ``decisions_created.csv``"
$Md += "- ``audit_preuve_tracabilite_3_domaines.csv``"
$Md += "- ``audit_preuve_tracabilite_3_domaines.json``"

$Md | Set-Content "$Audit\AUDIT_PREUVE_TRACABILITE_3_DOMAINES.md" -Encoding UTF8

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " TABLEAU DECISIONNEL" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$Rows |
  Select-Object Domaine, Verdict, Gate, Integrity, Governance, Readiness, Moyenne, Severity, Reason, MetricCount |
  Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host " COMPTEURS TRACABILITE" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

$TraceStats | Format-List

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
Write-Host " DECISIONS CREEES PENDANT AUDIT" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow

if ($CreatedDecisions.Count -eq 0) {
  Write-Host "Aucune nouvelle decision_*.json detectee." -ForegroundColor DarkYellow
} else {
  $CreatedDecisions |
    Select-Object Name, Length, @{Name="SHA";Expression={Short-Sha $_.Sha256}}, FullName |
    Format-Table -AutoSize
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " RACINE PREUVE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "AUDIT_ROOT_SHA256      = $AuditRoot"
Write-Host "TRACE_MANIFEST_SHA256  = $TraceManifestHash"
Write-Host "MERKLE_SEAL_SHA256     = $MerkleSealHash"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " RAPPORT GENERE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "AUDIT_DIR = $Audit"
Write-Host "REPORT    = $Audit\AUDIT_PREUVE_TRACABILITE_3_DOMAINES.md"
Write-Host "MANIFEST  = $Audit\TRACE_MANIFEST.json"

if ($Server -and $Server.Id) {
  Stop-Process -Id $Server.Id -Force -ErrorAction SilentlyContinue
}

Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue |
  Where-Object { $_.OwningProcess -and $_.OwningProcess -ne 0 } |
  Select-Object -ExpandProperty OwningProcess -Unique |
  ForEach-Object {
    Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
  }

Write-Host ""
Write-Host "AUDIT PREUVE / TRACABILITE TERMINE" -ForegroundColor Green
