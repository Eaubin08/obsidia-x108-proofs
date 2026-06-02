# F78C_XLSX_ROW_TO_PHASE_MAP
# Date: 2026-06-02 — Status: XLSX_AUDIT_ONLY / READONLY

---

## Distribution des 2739 lignes par phase

| Phase | Lignes | % | Packs concernés |
|-------|--------|---|-----------------|
| F06_ATLAS | 1676 | 61.2% | BRANCHABLE_ATLAS |
| F07_COGNITIVE | 508 | 18.5% | COGNITIVE_REINTEGRATION |
| F03_RSSI_RGPD | 387 | 14.1% | RSSI_SECURITY + RGPD_ISO |
| SOURCE_ONLY | 76 | 2.8% | EXTERNAL_SIGNALS (F04 done) + .runtime_freezes |
| REVIEW_REQUIRED | 64 | 2.3% | .py dans Atlas/RSSI/RGPD + registry/ |
| BLOCKED | 28 | 1.0% | packages/ (8) + .pytest_cache (20) |

---

## Groupe F03 — RSSI + RGPD (387 lignes import-eligible)

### RSSI_SECURITY (167 total → ~135 import-eligible)

| Décision | Lignes | Description |
|----------|--------|-------------|
| INTEGRATE_TO_SPECS_LATER | ~135 | docs/specs/audit/controls/risk MD+JSON |
| DO_NOT_IMPORT_RUNTIME | 16 | periphery/rssi_security_pack/*.py |
| ARCHIVE_ONLY | ~14 | .runtime_freezes/ |
| REVIEW_REQUIRED | ~2 | Fichiers tests .py |

**Familles concernées :** security posture / audit narrative / controls / evidence / RSSI modules
**Risques :** 16 .py à exclure — claim RSSI ≠ certification réelle
**Prérequis F03 :** F78B ✅ — exclusion .py planifiée — boundary RSSI_EVIDENCE_ONLY
**Boundaries :** `KX108_ONLY; DOC_OR_AUDIT_ONLY; NO_RUNTIME_AUTHORITY; NO_ACT`

### RGPD_ISO (280 total → ~252 import-eligible)

| Décision | Lignes | Description |
|----------|--------|-------------|
| INTEGRATE_TO_SPECS_LATER | ~252 | iso27001/ + rgpd/ + rssi/ + deployment/ + security/ + legal/ + audit/ |
| DO_NOT_IMPORT_RUNTIME | 23 | periphery/rssi_security_pack/*.py |
| ARCHIVE_ONLY | ~7 | .runtime_freezes/ |
| REVIEW_REQUIRED | ~5 | DPA_TEMPLATE.md doublon (RICHER_VERSION_TO_KEEP) |

**Familles concernées :** RGPD articles + ISO 27001 + RSSI readiness + legal docs + AI security
**Risques :** 23 .py à exclure — claim RGPD ≠ conformité légale — 8 dups internes à résoudre
**Prérequis F03 :** F78B ✅ — résoudre 8 dups — boundary RGPD_COMPLIANCE_SCOPE_GUARD
**Boundaries :** `KX108_ONLY; COMPLIANCE_CLAIM_SCOPE_GUARD; NO_RUNTIME_AUTHORITY; NO_ACT`

---

## Groupe F06_ATLAS (1676 lignes import-eligible)

| Décision | Lignes | Description |
|----------|--------|-------------|
| INTEGRATE_TO_SPECS_LATER | ~1676 | docs Atlas + cards + audit docs |
| DO_NOT_IMPORT_RUNTIME | 18 | periphery/world_protocol_atlas/*.py + patches/*.py |
| ARCHIVE_ONLY | 45 | .runtime_freezes/ |
| QUARANTINE | 20 | .pytest_cache/ |

**Familles concernées :**
- `docs/world_protocol_atlas` (878 fichiers) — documentation Atlas principale
- `docs/full_doc_extraction` (714 fichiers) — extraction complète docs
- `docs/obsidia_cards` (38) — cartes Obsidia
- `docs/modules` (80) — modules RSSI dans Atlas
- Audits FINAL_PASS_V0_3 → V0_7 — audit docs Atlas

**Complexité :** Atlas est le pack le plus volumineux (1738 fichiers). Import sélectif recommandé.
**Risques :** 18 .py + .pytest_cache + .runtime_freezes + 92 dups basenames (snapshots versionnés)
**Prérequis F06 :** F78B ✅ — exclusion .py + .pytest_cache + sélection manuelle snapshots
**Boundaries :** `KX108_ONLY; ATLAS_CONTEXT_ONLY; READONLY_BY_DEFAULT; NO_ACT`

---

## Groupe F07_COGNITIVE (508 lignes import-eligible)

| Décision | Lignes | Description |
|----------|--------|-------------|
| INTEGRATE_TO_SPECS_LATER | ~508 | yaml specs + schemas + packets |
| DO_NOT_IMPORT_RUNTIME | 5 | packets/ ciblant packages/ (alternative: specs/cognitive/packets/) |
| P1_CONTRACTS (priorité haute) | 16 | Contracts + schemas (IMPORT_CONTRACT_SCHEMA_PACKET) |
| P2_COGNITION_CONTRACTS | 39 | Docs + proof surface |

**Familles concernées :**
- `cognition/component_specs/` (458 yaml) — 458 component specs (C001-C458)
- `cognition/family_specs/` (25 yaml) — familles 21-45
- `cognition/schemas/` (8 json) — schemas
- `cognition/packets/` (9 yaml) — packets cognition (attention: 5 ciblent packages/)

**Point d'attention :** 5 packets Cognitive ciblent `packages/` — alternative = `specs/cognitive/packets/`
**Prérequis F07 :** F78B ✅ — pack le plus propre (0 .py hors packages/, 0 dups)
**Boundaries :** `KX108_ONLY; COGNITIVE_SIGNAL_ONLY; ADVISORY_ONLY; NO_ACT; NO_VERDICT_FINAL`

---

## Groupe SOURCE_ONLY (76 lignes)

| Pack | Lignes | Raison |
|------|--------|--------|
| EXTERNAL_SIGNALS (specs/ target) | 27 | ALREADY_IMPORTED (F04) |
| EXTERNAL_SIGNALS (docs/ target) | 4 | KEEP_SOURCE_ONLY — docs externes |
| EXTERNAL_SIGNALS (registry/ target) | 7 | REVIEW_REQUIRED — appendices non encore importés |
| BRANCHABLE_ATLAS (.runtime_freezes) | 45 | ARCHIVE_ONLY |

---

## Groupe REVIEW_REQUIRED (64 lignes)

| Description | Lignes | Pack |
|-------------|--------|------|
| .py files Atlas | 18 | BRANCHABLE_ATLAS |
| .py files RSSI | 16 | RSSI_SECURITY |
| .py files RGPD | 23 | RGPD_ISO |
| registry/ external_signals | 7 | EXTERNAL_SIGNALS |

Tous les .py = DO_NOT_IMPORT_RUNTIME (decision finale).
Les 7 registry/ External Signals = à intégrer dans `registry/appendices/external_signals/` lors F04b ou F05.

---

## Groupe BLOCKED (28 lignes)

| Description | Lignes | Décision |
|-------------|--------|----------|
| packages/ conflicts (3 EXT + 5 COG) | 8 | DO_NOT_IMPORT_ABSOLUTE |
| .pytest_cache Atlas | 20 | KEEP_QUARANTINE |

---

## Récapitulatif priorisé

```
Priorité 1 (Cognitive P1_CONTRACTS) : 16 lignes — schémas/contrats cognitifs
Priorité 2 (Security RSSI/RGPD) : ~60 lignes — P2_SECURITY + P2_COMPLIANCE
Priorité 3 (Cognition P3 + Atlas P2 branching) : ~477 + 26 lignes
Priorité 4 (Atlas bulk + Atlas evidence) : ~1642 lignes
Priorité 5 (Quarantine) : 20 lignes — DO_NOT_IMPORT
```
