# F78C_XLSX_TARGET_PATH_DUPLICATES
# Date: 2026-06-02 — Status: XLSX_AUDIT_ONLY / READONLY

---

## Résumé

| Type | Nb | Gravité | Action |
|------|-----|---------|--------|
| target_location "dupliqués" (groupage normal) | 48 | FAIBLE — multiple files per folder | DUPLICATE_SAFE |
| packages/ conflicts | 8 | HAUTE | DO_NOT_IMPORT_ABSOLUTE |
| runtime_contracts/ conflicts | 0 | AUCUNE | — |
| specs/ direct write conflicts | 0 | AUCUNE | — |

**Clarification critique (reprise COLLISION_RESOLUTION_PLAN) :**
Les 48 "target paths dupliqués" sont des **dossiers cibles** partagés par plusieurs fichiers.
C'est du groupage normal — chaque fichier a un nom distinct dans son dossier.
Il n'y a pas 48 conflits de noms de fichiers.

---

## Top 10 target_locations — groupage (nombre de fichiers)

| target_location | Fichiers | Pack | Nature |
|-----------------|----------|------|--------|
| atlas/world_protocol_atlas/ | 878 | BRANCHABLE_ATLAS | Dossier principal Atlas — normal |
| atlas/source_extraction/ | 714 | BRANCHABLE_ATLAS | Extraction source Atlas — normal |
| cognition/component_specs/ | 458 | COGNITIVE_REINTEGRATION | Component specs cognitifs — normal |
| security/rssi/modules/ | 80 | RSSI_SECURITY | Modules RSSI — normal |
| docs/source_packs/rgpd_iso/ | 46 | RGPD_ISO | Docs RGPD — normal |
| atlas/cards/ | 38 | BRANCHABLE_ATLAS | Cards Atlas — normal |
| cognition/family_specs/ | 25 | COGNITIVE_REINTEGRATION | Family specs — normal |
| audit/evidence/atlas/ | 25 | BRANCHABLE_ATLAS | Evidence Atlas — normal |
| specs/external_signals/component_specs/ | 24 | EXTERNAL_SIGNALS | DÉJÀ IMPORTÉ — normal |
| security/rssi/security_cases/ | 24 | RSSI_SECURITY | Security cases — normal |

Tous ces groupages sont **DUPLICATE_SAFE** — noms de fichiers distincts au sein du dossier.

---

## packages/ conflicts — 8 lignes BLOQUÉES

| Pack | Fichier | target_location | Classe |
|------|---------|-----------------|--------|
| EXTERNAL_SIGNALS | packets/51_temporal_context_header.packet.yaml | packages/shared/packets/external_signals/ | COLLISION_BLOCKING |
| EXTERNAL_SIGNALS | packets/52_temporal_receipt.packet.yaml | packages/shared/packets/external_signals/ | COLLISION_BLOCKING |
| EXTERNAL_SIGNALS | packets/53_consequence_boundary.packet.yaml | packages/shared/packets/external_signals/ | COLLISION_BLOCKING |
| COGNITIVE_REINTEGRATION | packets/50_receipts_packet.yaml | packages/shared/packets/cognition/ | COLLISION_BLOCKING |
| COGNITIVE_REINTEGRATION | packets/47_memory_packet.yaml | packages/shared/packets/cognition/ | COLLISION_BLOCKING |
| COGNITIVE_REINTEGRATION | packets/49_world_action_candidate_packet.yaml | packages/shared/packets/cognition/ | COLLISION_BLOCKING |
| COGNITIVE_REINTEGRATION | packets/46_input_context_packet.yaml | packages/shared/packets/cognition/ | COLLISION_BLOCKING |
| COGNITIVE_REINTEGRATION | packets/48_output_intent_packet.yaml | packages/shared/packets/cognition/ | COLLISION_BLOCKING |

**Décision : DO_NOT_IMPORT_ABSOLUTE**
`packages/` est une interdiction absolue dans ce repo.
Alternative pour les packets COGNITIVE : import dans `specs/cognitive/packets/` lors de F07.
Les 3 packets EXTERNAL_SIGNALS (51-53) sont **déjà importés** dans `specs/external_signals/packets/`.

---

## runtime_contracts/ conflicts

Aucune ligne XLSX ne cible `runtime_contracts/`.
Les 57 fichiers de `runtime_contracts/` sont créés par Plan 3 P0-P3 (docs contractuels).
Pas de conflit.

---

## specs/ write conflicts

Les seules lignes XLSX qui ciblent `specs/` :
```
specs/external_signals/component_specs/ — 24 fichiers (déjà importés F04)
specs/external_signals/family_specs/    — 3 fichiers (déjà importés F04)
specs/external_signals/packets/         — 3 fichiers (déjà importés F04)
```
**Ces 30 lignes sont ALREADY_IMPORTED.** Pas de conflit d'écrasement.

---

## Chemins interdits détectés

| Chemin interdit | Occurrences | Décision |
|----------------|-------------|----------|
| packages/shared/packets/external_signals/ | 3 | DO_NOT_IMPORT_ABSOLUTE |
| packages/shared/packets/cognition/ | 5 | DO_NOT_IMPORT_ABSOLUTE |
| periphery/ (group: periphery/world_protocol_atlas) | 28 rows Atlas | DO_NOT_IMPORT_RUNTIME (.py) |
| periphery/ (group: periphery/rssi_security_pack) | 22 rows RSSI | DO_NOT_IMPORT_RUNTIME (.py) |

---

## Classification globale

| Classe | Nb lignes | Exemple |
|--------|-----------|---------|
| DUPLICATE_SAFE | 2653 | Groupage dossier normal |
| ALREADY_RESOLVED_BY_D1_D4 | 27 | External Signals F04 |
| COLLISION_BLOCKING | 8 | packages/ DO_NOT_IMPORT |
| QUARANTINE_REQUIRED | 20 | .pytest_cache BRANCHABLE_ATLAS |
| DUPLICATE_REVIEW | 0 | Aucun vrai doublon de fichier |
