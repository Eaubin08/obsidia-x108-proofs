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

function Hash-FileSafePath {
  param([string]$Path)
  if (Test-Path $Path) { return (Get-FileHash $Path -Algorithm SHA256).Hash }
  return "MISSING"
}

function Hash-FileSafeName {
  param([string]$Name)
  return Hash-FileSafePath (Join-Path $AuditPath $Name)
}

function Short-Sha {
  param($Sha)
  $s = [string]$Sha
  if ([string]::IsNullOrWhiteSpace($s)) { return "" }
  if ($s.Length -gt 12) { return $s.Substring(0, 12) }
  return $s
}

function Get-Val {
  param($Obj, [string[]]$Names)

  if (-not $Obj) { return "" }

  foreach ($n in $Names) {
    $p = $Obj.PSObject.Properties | Where-Object { $_.Name -ieq $n } | Select-Object -First 1
    if ($p) { return $p.Value }
  }

  return ""
}

function Clean-Md {
  param($Value)
  $s = [string]$Value
  $s = $s.Replace("`r", " ").Replace("`n", " ").Replace("|", "/")
  if ($s.Length -gt 220) { $s = $s.Substring(0, 220) + "..." }
  return $s
}

function To-MdTable {
  param([object[]]$Rows, [string[]]$Props)

  $arr = @($Rows)
  if ($arr.Count -eq 0) { return @("_Aucune donnee._", "") }

  $lines = @()
  $lines += "| " + ($Props -join " | ") + " |"
  $lines += "| " + (($Props | ForEach-Object { "---" }) -join " | ") + " |"

  foreach ($row in $arr) {
    $vals = @()
    foreach ($p in $Props) {
      $vals += Clean-Md (Get-Val $row @($p))
    }
    $lines += "| " + ($vals -join " | ") + " |"
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
$CategoryRows = @(Import-CsvSafe "ALL_METRIC_CATEGORIES.csv")
$ProofRows = @(Import-CsvSafe "PROOF_CLAIMS_MATRIX.csv")
$RuntimeRows = @(Import-CsvSafe "runtime_file_hashes.csv")
$CreatedDecisionRows = @(Import-CsvSafe "decisions_created_during_audit.csv")
$AllMetricsRows = @(Import-CsvSafe "ALL_METRICS_FLAT.csv")
$RuntimeMetricRows = @(Import-CsvSafe "decision_runtime_metrics_flat.csv")

$Domains = @("bank", "trading", "gps_defense_aviation")

$DecisionView = foreach ($r in $DecisionRows) {
  $domain = Get-Val $r @("Domaine", "domain")
  $gate = Get-Val $r @("Gate", "gate")

  $lecture = switch ($gate) {
    "BLOCK" { "REFUS AVANT ACTION" }
    "HOLD"  { "TEMPORISATION X-108" }
    "ACT"   { "ACTION AUTORISEE" }
    default { "LECTURE INCOMPLETE" }
  }

  [PSCustomObject]@{
    Domaine = $domain
    Verdict = Get-Val $r @("Verdict", "verdict")
    Gate = $gate
    Integrity = Get-Val $r @("Integrity", "integrity")
    Governance = Get-Val $r @("Governance", "governance")
    Readiness = Get-Val $r @("Readiness", "readiness")
    Moyenne = Get-Val $r @("Moyenne", "mean3", "mean")
    Severity = Get-Val $r @("Severity", "severity")
    Reason = Get-Val $r @("Reason", "reason")
    MetricCount = Get-Val $r @("MetricCount", "metric_count")
    Lecture = $lecture
  }
}

$TraceView = foreach ($d in $Domains) {
  $decisionForDomain = $CreatedDecisionRows |
    Where-Object { (Get-Val $_ @("name", "Name")) -like "decision_$d*" } |
    Select-Object -First 1

  $decisionSha = Get-Val $decisionForDomain @("sha", "SHA", "Sha256")

  $decisionRow = $DecisionView |
    Where-Object { $_.Domaine -eq $d } |
    Select-Object -First 1

  [PSCustomObject]@{
    Domaine = $d
    InputSHA = Short-Sha (Hash-FileSafeName "input_$d.json")
    ResponseSHA = Short-Sha (Hash-FileSafeName "response_$d.json")
    MetricsSHA = Short-Sha (Hash-FileSafeName "metrics_full_$d.csv")
    MetricCount = if ($decisionRow) { $decisionRow.MetricCount } else { "" }
    DecisionCount = @($CreatedDecisionRows | Where-Object { (Get-Val $_ @("name", "Name")) -like "decision_$d*" }).Count
    DecisionSHA = Short-Sha $decisionSha
    Gate = if ($decisionRow) { $decisionRow.Gate } else { "" }
    Reason = if ($decisionRow) { $decisionRow.Reason } else { "" }
  }
}

$DataCountView = @(
  [PSCustomObject]@{ Bloc = "Domaines testes"; Nombre = @($DecisionView).Count; Fichier = "audit_decision_summary.csv"; Sens = "Nombre de domaines passes dans le moteur" }
  [PSCustomObject]@{ Bloc = "Metriques flattenees"; Nombre = @($AllMetricsRows).Count; Fichier = "ALL_METRICS_FLAT.csv"; Sens = "Toutes les donnees retournees par le moteur mises a plat" }
  [PSCustomObject]@{ Bloc = "Metriques runtime decisions"; Nombre = @($RuntimeMetricRows).Count; Fichier = "decision_runtime_metrics_flat.csv"; Sens = "Donnees extraites des decisions runtime" }
  [PSCustomObject]@{ Bloc = "Categories metriques"; Nombre = @($CategoryRows).Count; Fichier = "ALL_METRIC_CATEGORIES.csv"; Sens = "Regroupement des metriques par familles" }
  [PSCustomObject]@{ Bloc = "Decisions creees"; Nombre = @($CreatedDecisionRows).Count; Fichier = "decisions_created_during_audit.csv"; Sens = "Nouveaux fichiers decision JSON produits pendant audit" }
  [PSCustomObject]@{ Bloc = "Fichiers runtime hashes"; Nombre = @($RuntimeRows).Count; Fichier = "runtime_file_hashes.csv"; Sens = "Fichiers moteur critiques hashes" }
  [PSCustomObject]@{ Bloc = "Claims preuve"; Nombre = @($ProofRows).Count; Fichier = "PROOF_CLAIMS_MATRIX.csv"; Sens = "Axes de preuve declares OK" }
)

$HashView = @(
  [PSCustomObject]@{ Element = "MERKLE_BEFORE_SHA256"; SHA256 = Hash-FileSafeName "merkle_seal_before.json"; Source = "merkle_seal_before.json" }
  [PSCustomObject]@{ Element = "MERKLE_AFTER_SHA256"; SHA256 = Hash-FileSafeName "merkle_seal_after.json"; Source = "merkle_seal_after.json" }
  [PSCustomObject]@{ Element = "TRACE_MANIFEST_SHA256"; SHA256 = Hash-FileSafeName "TRACE_MANIFEST.json"; Source = "TRACE_MANIFEST.json" }
  [PSCustomObject]@{ Element = "AUDIT_ROOT_SHA256"; SHA256 = (Get-Content (Join-Path $AuditPath "AUDIT_ROOT_SHA256.txt") -Raw).Trim(); Source = "AUDIT_ROOT_SHA256.txt" }
  [PSCustomObject]@{ Element = "REPORT_SHA256"; SHA256 = (Get-Content (Join-Path $AuditPath "REPORT_SHA256.txt") -Raw).Trim(); Source = "REPORT_SHA256.txt" }
  [PSCustomObject]@{ Element = "SERVER_STDOUT_SHA256"; SHA256 = Hash-FileSafeName "server.stdout.log"; Source = "server.stdout.log" }
  [PSCustomObject]@{ Element = "SERVER_STDERR_SHA256"; SHA256 = Hash-FileSafeName "server.stderr.log"; Source = "server.stderr.log" }
)

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

$PostReport = Join-Path $AuditPath "POST_AUDIT_TABLEAUX_STRUCTURES_V2.md"

$Md = @()
$Md += "# Post-audit structure V2 - Evidence Board 3 domaines"
$Md += ""
$Md += "Audit source : $AuditPath"
$Md += "Date lecture : $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
$Md += ""
$Md += "## 1. Lecture executive"
$Md += ""
$Md += "Chaine prouvee : payload domaine -> endpoint Node -> pipeline Sigma/Python -> verdict metier -> gate X-108 -> decision runtime -> fichiers traces -> hashes -> manifest -> racine audit."
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
$Md += "## 5. Categories de metriques"
$Md += ""
$Md += To-MdTable -Rows $CategoryRows -Props @("domain", "category", "metric_count")
$Md += ""
$Md += "## 6. Matrice de preuves"
$Md += ""
$Md += To-MdTable -Rows $ProofRows -Props @("axe", "preuve", "statut")
$Md += ""
$Md += "## 7. Hashes majeurs"
$Md += ""
$Md += To-MdTable -Rows $HashView -Props @("Element", "SHA256", "Source")
$Md += ""
$Md += "## 8. Decisions creees pendant audit"
$Md += ""
$Md += To-MdTable -Rows $CreatedDecisionRows -Props @("name", "bytes", "sha", "FullName")
$Md += ""
$Md += "## 9. Fichiers runtime hashes"
$Md += ""
$Md += To-MdTable -Rows $RuntimeRows -Props @("file", "bytes", "sha256")
$Md += ""
$Md += "## 10. Index fichiers produits"
$Md += ""
$Md += To-MdTable -Rows $FilesView -Props @("Fichier", "KB", "SHA12", "LastWrite")

$Md | Set-Content $PostReport -Encoding UTF8

Print-Section "POST-AUDIT V2 - DECISIONS"
$DecisionView | Format-Table -AutoSize

Print-Section "POST-AUDIT V2 - CHAINES DE TRACE CORRIGEES"
$TraceView | Format-Table -AutoSize

Print-Section "POST-AUDIT V2 - CE QUI EST COMPTE"
$DataCountView | Format-Table -AutoSize

Print-Section "POST-AUDIT V2 - HASHES MAJEURS"
$HashView |
  Select-Object Element, @{Name="SHA12";Expression={Short-Sha $_.SHA256}}, Source |
  Format-Table -AutoSize

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host " RAPPORT V2 GENERE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "AUDIT_DIR = $AuditPath"
Write-Host "REPORT_V2 = $PostReport"
Write-Host ""
Write-Host "Lecture :"
Write-Host "Get-Content -Raw ""$PostReport"""
Write-Host ""
Write-Host "POST-AUDIT V2 TERMINE" -ForegroundColor Green
