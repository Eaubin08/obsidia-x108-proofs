# F78B_CLAIM_SCOPE_AND_BOUNDARY_WARNINGS
# _source_discovery/F78B_SOURCE_PACKS_DEEP_DIFF_AUDIT_20260602_132021/
# Date: 2026-06-02
# Status: SOURCE_AUDIT_ONLY / READONLY

---

## Règle générale

```
F78B est un audit de source.
F78B ne valide pas juridiquement.
F78B ne certifie pas formellement.
F78B ne brancht pas les packs.
F78B ne rend pas les packs runtime-ready.
F78B identifie ce qui peut être intégré et comment — pas plus.
```

---

## Interdictions de claim par pack

### RSSI Security

```
❌ "RSSI sécurise effectivement le runtime"
❌ "RSSI_SECURITY est certifié"
❌ "RSSI prouve la sécurité du système"
❌ "periphery/rssi_security_pack/ est actif"
❌ "RSSI_SECURITY autorise X108"

✅ "RSSI source copied readonly — 167 fichiers — F03 required"
✅ "RSSI pack = EVIDENCE_ONLY — docs audit uniquement"
✅ "periphery/.py = DO_NOT_IMPORT — exclus de F03"
✅ "RSSI_EVIDENCE_ONLY boundary appliquée"
```

### RGPD ISO

```
❌ "RGPD conforme"
❌ "ISO certifié"
❌ "Obsidia est RGPD-compliant"
❌ "RGPD readiness = certification légale"
❌ "periphery/rssi_security_pack/ RGPD est actif"

✅ "RGPD source copied readonly — 311 fichiers — F03+F10 required"
✅ "RGPD pack = COMPLIANCE_CLAIM_SCOPE_GUARD — readiness docs uniquement"
✅ "periphery/.py = DO_NOT_IMPORT — exclus de F03"
✅ "RGPD readiness ≠ conformité légale — guard obligatoire"
✅ "RGPD_COMPLIANCE_SCOPE_GUARD boundary appliquée"
```

### Branchable Atlas

```
❌ "Atlas est branché"
❌ "Atlas est runtime-ready"
❌ "Atlas est actif dans le système"
❌ "periphery/world_protocol_atlas/ est intégré"
❌ "F78B intègre Atlas"

✅ "Atlas source copied readonly — 1738 fichiers — F06 required"
✅ "Atlas = ATLAS_READONLY_ADVISORY_ONLY — contexte cartographique futur"
✅ "periphery/.py = DO_NOT_IMPORT — exclus de F06"
✅ ".runtime_freezes/ = RAW_ARCHIVE_ONLY — jamais dans specs/"
✅ ".pytest_cache/ = QUARANTINE_DO_NOT_IMPORT"
✅ "ATLAS_READONLY_ADVISORY_ONLY boundary appliquée"
```

### Cognitive Reintegration

```
❌ "Cognitive est actif"
❌ "Cognitive Reintegration est branché au runtime"
❌ "Cognitive Reintegration est runtime-ready"

✅ "Cognitive source copied readonly — 519 fichiers — F07 required"
✅ "Cognitive = COGNITIVE_REINTEGRATION_ADVISORY_ONLY — advisory futur"
✅ "Pack propre : 0 .py, 0 dups — candidat prioritaire pour F07"
✅ "COGNITIVE_REINTEGRATION_ADVISORY_ONLY boundary appliquée"
```

### External Signals

```
❌ "External Signals autorise X108"
❌ "External Signals produit des décisions"
❌ "External Signals remplace X108"
❌ "External Signals est une autorité"

✅ "External Signals SPEC_IMPORTED (F04) — advisory temporel uniquement"
✅ "37/41 fichiers du zip déjà importés dans specs/external_signals/"
✅ "EXTERNAL_SIGNALS_SIGNAL_ONLY boundary appliquée"
✅ "X108 reste seul droit de passage"
```

### NPL

```
❌ "NPL prouve"
❌ "NPL valide juridiquement"
❌ "NPL est une preuve formelle"
❌ "NPL autorise X108"

✅ "NPL importé dans specs/12_NARRATIVE_PROVENANCE_LAYER/ (34 fichiers)"
✅ "NPL = ADVISORY_ONLY — enrichissement contexte uniquement"
✅ "NPL_ADVISORY_ONLY boundary appliquée"
```

### P107/P161

```
❌ "P107 est Lean-prouvé"
❌ "P161 est Lean-prouvé"
❌ "P107/P161 ont autorité runtime"
❌ "P107/P161 sont des lois formelles certifiées"

✅ "P107/P161 = PYTHON_SPEC_NOT_LEAN_PROVEN"
✅ "Metrics advisory Python spec uniquement"
✅ "P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY boundary appliquée"
```

### F78B lui-même

```
❌ "F78B intègre les fichiers"
❌ "F78B déploie les packs"
❌ "F78B valide juridiquement ou formellement"
❌ "F78B certifie les sources"
❌ "F78B rend les packs runtime-ready"
❌ "Après F78B, les packs peuvent être utilisés directement"

✅ "F78B = SOURCE_AUDIT_ONLY"
✅ "F78B identifie les décisions KEEP/INTEGRATE/ARCHIVE pour chaque pack"
✅ "F78B est le prérequis de F03/F06/F07/F10"
✅ "F78B ne modifie pas le runtime"
✅ "F78B ne crée pas d'import effectif"
```

---

## Formulations autorisées — référence

| Sujet | Formulation autorisée |
|-------|----------------------|
| Zips sources | "source copied readonly" |
| Packs non extraits | "audit candidate / spec candidate" |
| Après F03/F06/F07 | "source-only archive intégrée" |
| Claim scope packs | "claim-scope locked until import audit" |
| Futures importations | "future import gated on F78B → F0x" |
| X108 | "X108 remains sole decision passage" |
| runtime_contracts | "contractual bridge only — no runtime execution" |
| RSSI posture | "RSSI security posture documentation — evidence only" |
| RGPD readiness | "RGPD readiness documentation — compliance claim scope guarded" |
| Atlas | "Atlas cartographic context — readonly advisory future" |
| Cognitive | "Cognitive reintegration spec — advisory future" |

---

## Claim-scope locks appliqués par ce run F78B

| Pack | Claim-scope lock | Boundary |
|------|-----------------|----------|
| RSSI_EXT | SPEC_IMPORTED / SIGNAL_ONLY | EXTERNAL_SIGNALS_SIGNAL_ONLY |
| RSSI_SEC | EVIDENCE_ONLY / F03_PENDING | RSSI_EVIDENCE_ONLY |
| RSSI_RGPD | COMPLIANCE_SCOPE_GUARD / F03+F10_PENDING | RGPD_COMPLIANCE_SCOPE_GUARD |
| ATLAS | COPIED_READONLY / F06_PENDING | ATLAS_READONLY_ADVISORY_ONLY |
| COGNITIVE | COPIED_READONLY / F07_PENDING | COGNITIVE_REINTEGRATION_ADVISORY_ONLY |
| NPL | ADVISORY_ONLY / IMPORTED | NPL_ADVISORY_ONLY |
| P107/P161 | PYTHON_SPEC_NOT_LEAN_PROVEN | P107_P161_NOT_PROVEN_RUNTIME_AUTHORITY |
