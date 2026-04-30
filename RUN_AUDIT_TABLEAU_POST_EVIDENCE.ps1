Set-Location $PSScriptRoot

$Audit = Get-ChildItem ".\audit\local_diag" -Directory -ErrorAction Stop |
  Where-Object { $_.Name -like "audit_evidence_board_3_domains_*" } |
  Sort-Object LastWriteTime -Descending |
  Select-Object -First 1

if (-not $Audit) {
  throw "Aucun dossier audit_evidence_board_3_domains_* trouve."
}

$AuditPath = $Audit.FullName

function Import-CsvSafe {
  param([string]$Name)
  $p = Join-Path $AuditPath $Name
  if (Test-Path $p) { return @(Import-Csv $p) }
  return @()
}

function Read-JsonSafe {
  param([string]$Name)
  $p = Join-Path $AuditPath $Name
  if (Test-Path $p) { return (Get-Content $p -Raw | ConvertFrom-Json) }
  return $null
}

function Read-TextSafe {
  param([string]$Name)
  $p = Join-Path $AuditPath $Name
  if (Test-Path $p) { return ((Get-Content $p -Raw).Trim()) }
  return "MISSING"
}

function Hash-FileSafe {
  param([string]$Name)
  $p = Join-Path $AuditPath $Name
  if (Test-Path $p) { return (Get-FileHash $p -Algorithm SHA256).Hash }
  return "MISSING"
}

function Short-Sha {
  param($Sha)
  $s = [string]$Sha
  if ([string]::IsNullOrWhiteSpace($s)) { return "" }
  if ($s.Length -gt 12) { return $s.Substring(0, 12) }
  return $s
}

function Get-Value {
  param($Obj, [string[]]$Names)

  if (-not $Obj) { return "" }

  foreach ($n in $Names) {
    $p = $Obj.PSObject.Properties | Where-Object { $_.Name -ieq $n } | Select-Object -First 1
    if ($p) { return $p.Value }
  }

  return ""
}

function As-Text {
  param($Value)

  if ($null -eq $Value) { return "" }
  if ($Value -is [string]) { return $Value }

  if ($Value -is [int] -or $Value -is [double] -or $Value -is [decimal] -or $Value -is [bool]) {
    return [string]$Value
  }

  try {
    return ($Value | ConvertTo-Json -Depth 20 -Compress)
  } catch {
    return [string]$Value
  }
}

function Clean-Md {
  param($Value)

  $s = As-Text $Value
  $s = $s.Replace([string][char]13, " ").Replace([string][char]10, " ").Replace("|", "/")

  if ($s.Length -gt 220) {
    $s = $s.Substring(0, 220) + "..."
  }

  return $s
}

function To-MdTable {
  param([object[]]$Rows, [string[]]$Props)

  $arr = @($Rows)

  if ($arr.Count -eq 0) {
    return @("_Aucune donnee._", "")
  }

  $lines = @()
  $lines += ("| " + ($Props -join " | ") + " |")

  $sep = @()
  foreach ($p in $Props) { $sep += "---" }
  $lines += ("| " + ($sep -join " | ") + " |")

  foreach ($row in $arr) {
    $vals = @()
    foreach ($p in $Props) {
      $vals += Clean-Md (Get-Value $row @($p))
    }
    $lines += ("| " + ($vals -join " | ") + " |")
  }

  return $lines
}

function Print-Section {
  param([string]$Title)

  Write-Host ""
  Write-Host "============================================================" -ForegroundColor Yellow
  Write-Host " $Title" -ForegroundColor Yellow
  Write-Host "============================================================" -ForegroundColor Yellow
}

$DecisionRows = @(Import-CsvSafe "audit_decision_summary.csv")
$TraceRows = @(Import-CsvSafe "TRACE_CHAINS_BY_DOMAIN.csv")
$CategoryRows = @(Import-CsvSafe "ALL_METRIC_CATEGORIES.csv")
$ProofRows = @(Import-CsvSafe "PROOF_CLAIMS_MATRIX.csv")
$RuntimeRows = @(Import-CsvSafe "runtime_file_hashes.csv")
$CreatedDecisionRows = @(Import-CsvSafe "decisions_created_during_audit.csv")
$AllMetricsRows = @(Import-CsvSafe "ALL_METRICS_FLAT.csv")
$RuntimeMetricRows = @(Import-CsvSafe "decision_runtime_metrics_flat.csv")
$Stats = Read-JsonSafe "TRACE_STATS.json"

$DecisionView = foreach ($r in $DecisionRows) {
  $domain = Get-Value $r @("Domaine", "domain")
  $gate = Get-Value $r @("Gate", "gate")
  $verdict = Get-Value $r @("Verdict", "verdict")
  $reason = Get-Value $r @("Reason", "reason")
  $integrity = Get-Value $r @("Integrity", "integrity")
  $governance = Get-Value $r @("Governance", "governance")
  $readiness = Get-Value $r @("Readiness", "readiness")
  $mean = Get-Value $r @("Moyenne", "mean3", "mean")
  $severity = Get-Value $r @("Severity", "severity")
  $metricCount = Get-Value $r @("MetricCount", "metric_count")

  $security = switch ($gate) {
    "BLOCK" { "REFUS AVANT ACTION" }
    "HOLD"  { "TEMPORISATION X-108" }
    "ACT"   { "ACTION AUTORISEE" }
    default { "LECTURE INCOMPLETE" }
  }

  [PSCustomObject]@{
    Domaine = $domain
    Verdict = $verdict
    Gate = $gate
    Integrity = $integrity
    Governance = $governance
    Readiness = $readiness
    Moyenne = $mean
    Severity = $severity
    Reason = $reason
    MetricCount = $metricCount
    Lecture = $security
  }
}

$TraceView = foreach ($r in $TraceRows) {
  [PSCustomObject]@{
    Domaine = Get-Value $r @("domain", "Domaine")
    InputSHA = Short-Sha (Get-Value $r @("Input", "InputSHA", "input_sha", "input_hash"))
    ResponseSHA = Short-Sha (Get-Value $r @("Response", "ResponseSHA", "response_sha", "response_hash"))
    MetricsSHA = Short-Sha (Get-Value $r @("Metrics", "MetricsSHA", "metrics_sha", "metrics_hash"))
    MetricCount = Get-Value $r @("metric_count", "MetricCount")
    DecisionCount = Get-Value $r @("decision_count", "DecisionCount")
    DecisionSHA = Short-Sha (Get-Value $r @("DecisionHashes", "decision_hashes", "DecisionSHA"))
    Gate = Get-Value $r @("gate", "Gate")
    Reason = Get-Value $r @("reason", "Reason")
  }
}

$StatsView = @()
if ($Stats) {
  foreach ($p in $Stats.PSObject.Properties) {
    $StatsView += [PSCustomObject]@{
      Cle = $p.Name
      Valeur = As-Text $p.Value
    }
  }
}

$HashView = @(
  [PSCustomObject]@{ Element = "MERKLE_BEFORE_SHA256"; SHA256 = Hash-FileSafe "merkle_seal_before.json"; Source = "merkle_seal_before.json" }
  [PSCustomObject]@{ Element = "MERKLE_AFTER_SHA256"; SHA256 = Hash-FileSafe "merkle_seal_after.json"; Source = "merkle_seal_after.json" }
  [PSCustomObject]@{ Element = "TRACE_MANIFEST_SHA256"; SHA256 = Hash-FileSafe "TRACE_MANIFEST.json"; Source = "TRACE_MANIFEST.json" }
  [PSCustomObject]@{ Element = "AUDIT_ROOT_SHA256"; SHA256 = Read-TextSafe "AUDIT_ROOT_SHA256.txt"; Source = "AUDIT_ROOT_SHA256.txt" }
  [PSCustomObject]@{ Element = "REPORT_SHA256"; SHA256 = Read-TextSafe "REPORT_SHA256.txt"; Source = "REPORT_SHA256.txt" }
  [PSCustomObject]@{ Element = "SERVER_STDOUT_SHA256"; SHA256 = Hash-FileSafe "server.stdout.log"; Source = "server.stdout.log" }
  [PSCustomObject]@{ Element = "SERVER_STDERR_SHA256"; SHA256 = Hash-FileSafe "server.stderr.log"; Source = "server.stderr.log" }
)

$DataCountView = @(
  [PSCustomObject]@{ Bloc = "Domaines testes"; Nombre = @($DecisionView).Count; Fichier = "audit_decision_summary.csv"; Sens = "Nombre de domaines passes dans le moteur" }
  [PSCustomObject]@{ Bloc = "Metriques flattenees"; Nombre = @($AllMetricsRows).Count; Fichier = "ALL_METRICS_FLAT.csv"; Sens = "Toutes les donnees retournees par le moteur mises a plat" }
  [PSCustomObject]@{ Bloc = "Metriques runtime decisions"; Nombre = @($RuntimeMetricRows).Count; Fichier = "decision_runtime_metrics_flat.csv"; Sens = "Donnees extraites des decision runtime" }
  [PSCustomObject]@{ Bloc = "Categories metriques"; Nombre = @($CategoryRows).Count; Fichier = "ALL_METRIC_CATEGORIES.csv"; Sens = "Regroupement des metriques par familles" }
  [PSCustomObject]@{ Bloc = "Decisions creees"; Nombre = @($CreatedDecisionRows).Count; Fichier = "decisions_created_during_audit.csv"; Sens = "Nouveaux fichiers decision JSON produits pendant audit" }
  [PSCustomObject]@{ Bloc = "Fichiers runtime hashes"; Nombre = @($RuntimeRows).Count; Fichier = "runtime_file_hashes.csv"; Sens = "Fichiers moteur critiques hashes" }
  [PSCustomObject]@{ Bloc = "Claims preuve"; Nombre = @($ProofRows).Count; Fichier = "PROOF_CLAIMS_MATRIX.csv"; Sens = "Axes de preuve declares OK" }
)

$PostReport = Join-Path $AuditPath "POST_AUDIT_TABLEAUX_STRUCTURES.md"
$FullMetricsReport = Join-Path $AuditPath "ALL_METRICS_READABLE.md"
$IndexReport = Join-Path $AuditPath "POST_AUDIT_INDEX_PREUVES.md"

$Md = @()
$Md += "# Post-audit structure - Evidence Board 3 domaines"
$Md += ""
$Md += ("Audit source : {0}" -f $AuditPath)
$Md += ("Date lecture : {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
$Md += ""
$Md += "## 1. Lecture executive"
$Md += ""
$Md += "Cet audit demontre une chaine complete : payload domaine -> endpoint Node -> pipeline Sigma/Python -> verdict metier -> gate X-108 -> decision runtime -> fichiers traces -> hashes -> manifest -> racine audit."
$Md += ""
$Md += "## 2. Tableau decisionnel"
$Md += ""
$Md += To-MdTable -Rows $DecisionView -Props @("Domaine", "Verdict", "Gate", "Integrity", "Governance", "Readiness", "Moyenne", "Severity", "Reason", "MetricCount", "Lecture")
$Md += ""
$Md += "## 3. Chaine de trace par domaine"
$Md += ""
$Md += To-MdTable -Rows $TraceView -Props @("Domaine", "InputSHA", "ResponseSHA", "MetricsSHA", "MetricCount", "DecisionCount", "DecisionSHA", "Gate", "Reason")
$Md += ""
$Md += "## 4. Ce qui est compte"
$Md += ""
$Md += To-MdTable -Rows $DataCountView -Props @("Bloc", "Nombre", "Fichier", "Sens")
$Md += ""
$Md += "## 5. Compteurs de tracabilite"
$Md += ""
$Md += To-MdTable -Rows $StatsView -Props @("Cle", "Valeur")
$Md += ""
$Md += "## 6. Categories de metriques"
$Md += ""
$Md += To-MdTable -Rows $CategoryRows -Props @("domain", "category", "metric_count")
$Md += ""
$Md += "## 7. Matrice de preuves"
$Md += ""
$Md += To-MdTable -Rows $ProofRows -Props @("axe", "preuve", "statut")
$Md += ""
$Md += "## 8. Hashes majeurs"
$Md += ""
$Md += To-MdTable -Rows $HashView -Props @("Element", "SHA256", "Source")
$Md += ""
$Md += "## 9. Decisions creees pendant audit"
$Md += ""
$Md += To-MdTable -Rows $CreatedDecisionRows -Props @("name", "bytes", "sha", "FullName")
$Md += ""
$Md += "## 10. Fichiers runtime hashes"
$Md += ""
$Md += To-MdTable -Rows $RuntimeRows -Props @("file", "bytes", "sha256")
$Md += ""
$Md += "## 11. Lecture froide"
$Md += ""
$Md += "- Le moteur ne sort pas seulement un verdict."
$Md += "- Il retourne des metriques exploitables."
$Md += "- Il garde les inputs."
$Md += "- Il garde les outputs."
$Md += "- Il genere des decisions runtime."
$Md += "- Il hashe les artefacts."
$Md += "- Il produit un manifest."
$Md += "- Il calcule une racine audit."
$Md += "- Il rattache la preuve a Git : branche, commit, tag, status."
$Md += ""
$Md += "Conclusion : audit multi-domaines reproductible, trace, hashe, lisible, avec preuve de decision avant action."

$Md | Set-Content $PostReport -Encoding UTF8

$AllCols = @()
if (@($AllMetricsRows).Count -gt 0) {
  $AllCols = $AllMetricsRows[0].PSObject.Properties.Name
}

$FullMd = @()
$FullMd += "# Toutes les metriques flattenees"
$FullMd += ""
$FullMd += ("Audit source : {0}" -f $AuditPath)
$FullMd += ("Total lignes : {0}" -f @($AllMetricsRows).Count)
$FullMd += ""

if ($AllCols.Count -gt 0) {
  $FullMd += To-MdTable -Rows $AllMetricsRows -Props $AllCols
} else {
  $FullMd += "_Aucune metrique detectee._"
}

$FullMd | Set-Content $FullMetricsReport -Encoding UTF8

$FilesView = Get-ChildItem $AuditPath -File |
  Sort-Object Name |
  ForEach-Object {
    [PSCustomObject]@{
      Fichier = $_.Name
      KB = [math]::Round($_.Length / 1KB, 2)
      SHA12 = Short-Sha ((Get-FileHash $_.FullName -Algorithm SHA256).Hash)
      LastWrite = $_.LastWriteTime
    }
  }

$IndexMd = @()
$IndexMd += "# Index preuves audit"
$IndexMd += ""
$IndexMd += ("Audit source : {0}" -f $AuditPath)
$IndexMd += ""
$IndexMd += "## Rapports lisibles"
$IndexMd += ""
$IndexMd += "- POST_AUDIT_TABLEAUX_STRUCTURES.md"
$IndexMd += "- ALL_METRICS_READABLE.md"
$IndexMd += "- EVIDENCE_BOARD_3_DOMAINES.md"
$IndexMd += ""
$IndexMd += "## Fichiers sources"
$IndexMd += ""
$IndexMd += To-MdTable -Rows $FilesView -Props @("Fichier", "KB", "SHA12", "LastWrite")

$IndexMd | Set-Content $IndexReport -Encoding UTF8

Print-Section "POST-AUDIT - DECISIONS"
$DecisionView | Format-Table -AutoSize

Print-Section "POST-AUDIT - CHAINES DE TRACE"
$TraceView | Format-Table -AutoSize

Print-Section "POST-AUDIT - CE QUI EST COMPTE"
$DataCountView | Format-Table -AutoSize

Print-Section "POST-AUDIT - HASHES MAJEURS"
$HashView |
  Select-Object Element, @{Name="SHA12";Expression={Short-Sha $_.SHA256}}, Source |
  Format-Table -AutoSize

Print-Section "POST-AUDIT - MATRICE DE PREUVES"
$ProofRows | Format-Table -AutoSize

Print-Section "POST-AUDIT - FICHIERS GENERES"
$FilesView | Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " RAPPORTS POST-AUDIT GENERES" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "AUDIT_DIR         = $AuditPath"
Write-Host "STRUCTURED_REPORT = $PostReport"
Write-Host "FULL_METRICS      = $FullMetricsReport"
Write-Host "INDEX_PREUVES     = $IndexReport"
Write-Host ""
Write-Host "Commande lecture rapport :"
Write-Host "Get-Content -Raw ""$PostReport"""
Write-Host ""
Write-Host "POST-AUDIT TABLEAUX TERMINE" -ForegroundColor Green
