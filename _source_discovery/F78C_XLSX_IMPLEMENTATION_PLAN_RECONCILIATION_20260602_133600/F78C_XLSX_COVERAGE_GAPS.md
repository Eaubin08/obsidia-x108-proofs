# F78C_XLSX_COVERAGE_GAPS
# Date: 2026-06-02 — Status: XLSX_AUDIT_ONLY / READONLY

---

## Vue d'ensemble des gaps

| Catégorie | Lignes | % total |
|-----------|--------|---------|
| Déjà couverts (specs/ + runtime_contracts/) | ~84 | 3.1% |
| Couverts génériquement (boundaries P0-P3) | ~2739 | 100% (contrats) |
| Pas encore importés dans specs/ | ~2609 | 95.3% |
| Bloqués (packages/ + quarantine) | 28 | 1.0% |
| Archive uniquement | 45 | 1.6% |
| DO_NOT_IMPORT (.py runtime) | 57 | 2.1% |

---

## 1. Lignes DÉJÀ couvertes dans specs/

### External Signals — F04 DONE (27 lignes exactes)

| target_location | Fichiers | Statut local |
|-----------------|----------|-------------|
| specs/external_signals/component_specs/ | 24 | PRESENT (C459-C482) |
| specs/external_signals/family_specs/ | 3 | PRESENT (46-48) |
| specs/external_signals/packets/ | 3 | PRESENT (51-53) |

**Note :** Les 3 packets (51-53) sont comptés dans les 27 lignes.

### NPL — F04 DONE (non dans XLSX pack-by-pack mais couvert specs/12/)

Le XLSX ne liste pas le pack NPL (zip absent de raw/). Mais `specs/12_NARRATIVE_PROVENANCE_LAYER/`
contient 34 fichiers NPL importés lors de F04. Couvert hors XLSX.

---

## 2. Couverts génériquement par runtime_contracts/ (P0-P3)

Les 57 fichiers `runtime_contracts/` créés en Plan 3 P0-P3 établissent les **contrats**
pour TOUS les packs. Ils ne contiennent pas les fichiers specs des packs, mais définissent
les boundaries, schémas, et contrats contractuels.

| Coverage type | Détail |
|--------------|--------|
| Boundaries | 13 boundaries couvrent tous les packs (dont RSSI, RGPD, Atlas, Cognitive) |
| Schemas | 7 schemas JSON couvrent IntentEnvelope/ContextPacket/DecisionTicket/OS3Evidence/etc. |
| Contracts | 7 contrats couvrent la logique d'admission de tout pack futur |
| Dry-run harness | Docs X108 Gateway harness couvrent la logique de connexion future |

---

## 3. Pas encore importés — par pack

### RSSI_SECURITY (167 total → ~135 éligibles)

**Gap :** 0 fichier RSSI importé dans specs/
**Eligible à F03 :** ~135 fichiers (docs/specs/audit/ MD + JSON — hors .py et .runtime_freezes)
**Exclusions :** 16 .py + 14 .runtime_freezes

**Exemples de gaps F03 :**
```
RSSI_SECURITY/periphery/... → EXCLUDED (.py)
RSSI_SECURITY/docs/... → F03 pending
RSSI_SECURITY/audit/... → F03 pending
RSSI_SECURITY/specs/... → F03 pending
```

### RGPD_ISO (280 total → ~252 éligibles)

**Gap :** 0 fichier RGPD importé dans specs/
**Eligible à F03+F10 :** ~252 (iso27001/ + rgpd/ + rssi/ + deployment/ + legal/ + security/ + audit/ + ai_security/ + data_governance/)
**Exclusions :** 23 .py + 7 .runtime_freezes + 8 dups à résoudre

**Exemples de gaps F03 :**
```
iso27001/ISMS_SCOPE.md → F03 pending
rgpd/DATA_PROCESSING_REGISTER.md → F03 pending
rssi/RSSI_READINESS_MATRIX.md → F03 pending
legal/DPA_TEMPLATE.md → F03+F10 pending (2 versions — RICHER_VERSION_TO_KEEP)
ai_security/PROMPT_INJECTION_TESTS.md → F03 pending
data_governance/GRAPHITI_DATA_MAP.md → F03+F10 pending
```

### BRANCHABLE_ATLAS (1738 total → ~1676 éligibles)

**Gap :** 0 fichier Atlas importé dans specs/
**Eligible à F06 :** ~1676 (docs MD + JSON d'audit — hors .py + .pytest_cache + .runtime_freezes)
**Exclusions :** 18 .py + 20 .pytest_cache + 45 .runtime_freezes + 92 dups basenames

**Exemples de gaps F06 :**
```
FINAL_PASS_AUDIT_V0_7.md → F06 pending
FINAL_PASS_AUDIT_V0_7.json → F06 pending
registry/full_branchable_registry.json → F06 pending
patches/periphery_ops_world_atlas_routes_SNIPPET_NOT_APPLIED.py → EXCLUDED (.py)
.pytest_cache/ → EXCLUDED (quarantine)
.runtime_freezes/ → ARCHIVE_ONLY
```

### COGNITIVE_REINTEGRATION (513 total → ~508 éligibles)

**Gap :** 0 fichier Cognitive importé dans specs/
**Eligible à F07 :** ~508 (yaml components + schemas + packets — hors packages/ targets)
**Exclusions :** 5 packets qui ciblent packages/ (alternative: specs/cognitive/packets/)

**Exemples de gaps F07 (prioritaires) :**
```
P1_CONTRACTS (16 fichiers) :
  schemas/13_component_spec.schema.json → F07 P1
  schemas/16_packet.schema.json → F07 P1
  packets/50_receipts_packet.yaml → F07 P1 (target: specs/cognitive/packets/ not packages/)
  packets/47_memory_packet.yaml → F07 P1 (target: specs/cognitive/packets/)
  ...
P3_COGNITION_SPECS (458 yaml) :
  component_specs/C001_canon_map_legacy_cards.yaml → F07 P3
  ... (458 fichiers)
```

---

## 4. Bloqués

| Fichier | Raison |
|---------|--------|
| packages/ (8 fichiers) | packages/ interdit — alternative specs/ disponible |
| .pytest_cache/ (20 fichiers) | Artefacts pytest — QUARANTINE |

---

## 5. Archive uniquement (ne pas importer)

| Fichier | Raison |
|---------|--------|
| .runtime_freezes/ Atlas (45 fichiers) | Snapshots états runtime figés — valeur historique seule |

---

## 6. Claim-scope review requis

| Pack | Nb lignes | Motif |
|------|-----------|-------|
| RSSI_SECURITY | ~135 | Docs "security" ≠ certification RSSI |
| RGPD_ISO | ~252 | Docs "compliance" ≠ conformité légale ISO/RGPD |
| .py tous packs | 57 | Ne pas interpréter comme runtime branché |
