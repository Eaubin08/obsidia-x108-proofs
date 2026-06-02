# F78C_XLSX_SHEET_INVENTORY
# _source_discovery/F78C_XLSX_IMPLEMENTATION_PLAN_RECONCILIATION_20260602_133600/
# Date: 2026-06-02
# Status: XLSX_AUDIT_ONLY / READONLY

---

## Fichier XLSX

```
Path:  _source_packs/OBSIDIA_UNIFIED_IMPLEMENTATION_BACKLOG_RICH_NO_DUPES_V1/raw/
       OBSIDIA_IMPLEMENTATION_PLAN_FILE_BY_FILE_V1.xlsx
SHA256 (SUMMARY sheet): voir colonne SHA256 par pack
```

---

## Inventaire des sheets

| # | Sheet | Lignes non-vides | Colonnes | Rôle |
|---|-------|-----------------|----------|------|
| 1 | README | 6 | 2 | Description du workbook |
| 2 | SUMMARY | 7 (1 header + 6 data) | 8 | Résumé par pack — ZIP source, files, SHA256, rôle, stage |
| 3 | IMPLEMENT_ORDER | 12 (1 header + 11 data) | 7 | Ordre F00→F10 avec gates et boundaries |
| 4 | FILE_PLAN_ALL | **2740 (1 header + 2739 data)** | 13 | Plan complet tous packs |
| 5 | EXT_SIGNALS | 42 (1 header + 41 data) | 13 | Filtre External Signals uniquement |
| 6 | RSSI_SECURITY | 168 (1 header + 167 data) | 13 | Filtre RSSI Security uniquement |
| 7 | COGNITIVE | 514 (1 header + 513 data) | 13 | Filtre Cognitive Reintegration uniquement |
| 8 | ATLAS | 1739 (1 header + 1738 data) | 13 | Filtre Branchable Atlas uniquement |
| 9 | RGPD_ISO | 281 (1 header + 280 data) | 13 | Filtre RGPD ISO uniquement |
| 10 | ACTION_COUNTS | 44 (1 header + 43 data) | 4 | Comptages par pack + action + priorité |

**Total lignes data : 2739 (FILE_PLAN_ALL)**

---

## Colonnes des sheets FILE_PLAN (identiques pour les 5 packs + ALL)

| Colonne | Type | Description |
|---------|------|-------------|
| source_zip | string | Nom du zip source |
| pack | string | Nom du pack (EXTERNAL_SIGNALS, RSSI_SECURITY, etc.) |
| source_path | string | Chemin dans le zip source |
| relative_path | string | Chemin relatif du fichier |
| group | string | Groupe thématique (docs/world_protocol_atlas, periphery/rssi_security_pack, etc.) |
| target_location | string | Chemin cible dans le repo |
| os_layer | string | Couche OS (OS1, OS2, OS3, compliance, etc.) |
| implementation_action | string | Action requise (IMPORT_DOC, QUARANTINE, etc.) |
| priority | string | Priorité (P1_CONTRACTS, P2_SECURITY, P3_ATLAS_CONTENT, P4_, P5_QUARANTINE) |
| boundary | string | Boundary KX108 applicable |
| dependency | string | Dépendances |
| test_audit_required | string | Tests requis |
| file_size_bytes | int | Taille en bytes |

---

## Sheet SUMMARY — données extraites

| Pack | Source ZIP | Files | Size KB | Canonical role | Integration stage | Runtime status |
|------|-----------|-------|---------|---------------|-------------------|----------------|
| EXTERNAL_SIGNALS | OBSIDIA_RSSI_EXTERNAL_SIGNALS_PATCH_V1 | 41 | 57.2 | Temporal sidecar / anti-replay / bounded tool-call | F04 after authority + audit | Backlog/spec/evidence |
| RSSI_SECURITY | OBSIDIA_RSSI_SECURITY_PRESENTATION_PACK_V1 | 167 | 445.4 | RSSI security posture, audit narrative, controls | F03 early OS3 audit | Backlog/spec/evidence |
| COGNITIVE_REINTEGRATION | OBSIDIA_COGNITIVE_REINTEGRATION_SPEC_V1_VERIFIED_FULL | 513 | 827.9 | Cognitive components, packets, schemas, metrics | F07 after memory/atlas boundaries | Backlog/spec/evidence |
| BRANCHABLE_ATLAS | OBSIDIA_BRANCHABLE_ATLAS_FULL_V0_7_FINAL_PASS | 1738 | 4104.9 | World/protocol atlas, branchable contexts | F06 after Graphiti/Brody readonly | Backlog/spec/evidence |
| RGPD_ISO | OBSIDIA_RSSI_RGPD_ISO_READINESS_PACK_V2 | 280 | 783.5 | RGPD / ISO / RSSI readiness and compliance evidence | F03/F10 OS3 compliance | Backlog/spec/evidence |

**Note SUMMARY :** Toutes les lignes Runtime status = "Backlog/spec/evidence unless explicitly wired through X108".
Aucun pack n'est présenté comme runtime-ready dans le XLSX.

---

## Sheet IMPLEMENT_ORDER — F00→F10

| Stage | Name | Purpose | Gate/Boundary |
|-------|------|---------|--------------|
| F00 | SOURCE FREEZE + LEDGER | Fix origin, hash | No runtime import |
| F01 | AUTHORITY CONTRACTS | Lock X108/KX108_ONLY | No peripheral ACT |
| F02 | CENTRAL REGISTRY | 2700+ files tractable | Registry cannot decide |
| F03 | OS3 SECURITY/RGPD/ISO | Proof/compliance surface | Docs/evidence only |
| F04 | EXTERNAL SIGNALS | Temporal proof, anti-replay | Signal only, X108 final |
| F05 | MEMORY READONLY | Graphiti/Brody as context | memory_decision=false |
| F06 | BRANCHABLE ATLAS | Territory/maps/domains | Atlas context only |
| F07 | COGNITIVE REINTEGRATION | Import cognitive body advisory | Advisory only |
| F08 | NPL PROVENANCE | Cultural/narrative provenance | Readonly, no truth verdict |
| F09 | EDUCATION VERTICAL | First impact vertical | No diagnosis/manipulation |
| F10 | BENCHMARKS + DEMO | Quantify and publish | Demo cannot bypass kernel |

**Note :** Plan 3 P0-P3 couvre F01 (authority contracts via runtime_contracts/).
F04 External Signals est DÉJÀ traité (specs/external_signals/ présent).
F00 est partiellement traité (source freeze P0 baseline + F78B/F78C).

---

## Distribution des lignes par priorité (FILE_PLAN_ALL)

| Priorité | Lignes | Pack principal |
|----------|--------|---------------|
| P3_ATLAS_CONTENT | 878 | BRANCHABLE_ATLAS |
| P4_ATLAS_EVIDENCE_OR_DOCS | 814 | BRANCHABLE_ATLAS |
| P3_COGNITION_SPECS | 451 | COGNITIVE_REINTEGRATION |
| P3_DOCS_EVIDENCE | 355 | RSSI+RGPD |
| P2_COMPLIANCE | 60 | RGPD_ISO |
| P2_COGNITION_CONTRACTS | 39 | COGNITIVE_REINTEGRATION |
| P2_SECURITY | 32 | RSSI_SECURITY |
| P2_SECURITY_PROOF | 30 | RSSI_SECURITY |
| P2_ATLAS_BRANCHING | 26 | BRANCHABLE_ATLAS |
| P1_CONTRACTS | 23 | COGNITIVE_REINTEGRATION |
| P5_QUARANTINE | 20 | BRANCHABLE_ATLAS (.pytest_cache) |
| P1_KERNEL_ADJACENT | 11 | EXTERNAL_SIGNALS |
