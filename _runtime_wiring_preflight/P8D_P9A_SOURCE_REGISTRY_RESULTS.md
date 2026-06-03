# P8D_P9A_SOURCE_REGISTRY_RESULTS
# _runtime_wiring_preflight/P8D_P9A_SOURCE_REGISTRY_RESULTS.md

## Run Info

- **Branche:** p8-runtime-dryrun-wiring
- **Date:** 2026-06-03
- **Script:** `runtime_wiring/source_registry/build_source_file_registry.py`

## Résultat Global

```
P8D_P9A_SOURCE_PACK_FILE_REGISTRY_BRIDGE_READY
```

## Inventaires chargés

| Famille | CSV | Entrées brutes | Doublons skip | Entrées retenues |
|---------|-----|----------------|---------------|-----------------|
| COGNITIVE_REINTEGRATION | F07_COGNITIVE_ZIP_INTERNAL_INVENTORY.csv | 3591 | 1539 | 2052 |
| RSSI_RGPD | F03_RSSI_RGPD_ZIP_INTERNAL_INVENTORY_STRICT.csv | 2440 | 1464 | 976 |
| ATLAS | F06_ATLAS_ZIP_INTERNAL_INVENTORY_CANON_DEDUPED.csv | 11263 | 0 | 11263 |
| COMPLIANCE_DATA_GOVERNANCE | F10_COMPLIANCE_DATA_GOVERNANCE_ZIP_INTERNAL_INVENTORY_DEDUPED.csv | 488 | 0 | 488 |
| **TOTAL** | | **17782** | **3003** | **14779** |

## Fichiers générés

| Fichier | Taille |
|---------|--------|
| `runtime_wiring/source_registry/source_file_registry.json` | 13 674 657 octets (~13,7 MB) |
| `runtime_wiring/source_registry/source_file_registry.csv` | 7 113 024 octets (~7,1 MB) |
| `runtime_wiring/source_registry/source_registry_summary.json` | 1 823 octets |

## Safety Invariants

| Invariant | Valeur |
|-----------|--------|
| `runtime_allowed_now=True` count | **0** |
| `emits_act=True` count | **0** |
| `emits_decision=True` count | **0** |
| `zip_extraction` | **false** |
| `source_pack_import` | **false** |
| `runtime_activation` | **false** |
| .py fichiers classés DO_NOT_IMPORT_RUNTIME | **240 / 240 (100%)** |
| `safety_invariants_ok` | **true** |

## Fichiers NON modifiés

- `runtime_contracts/` — intact
- `specs/` — intact
- `periphery/` — intact
- `apps/` — intact
- `_source_packs/` — intact (aucun zip ouvert)
- `_freezes/` — intact
- `.claude/settings.local.json` — intact
- `packages/` — absent (non créé)

## Commande de repro

```bash
python runtime_wiring/source_registry/build_source_file_registry.py
```

## Prochain chantier

P9B — Registry-to-Adapter Dry-Run Router Tests
