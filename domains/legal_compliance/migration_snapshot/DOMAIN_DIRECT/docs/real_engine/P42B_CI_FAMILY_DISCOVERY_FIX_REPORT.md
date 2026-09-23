# P42B — CI Family Discovery Fix Report

**Date:** 2026-06-04
**Branch:** p10-real-engine-controlled-bridge
**Status:** P42B_CI_FAMILY_DISCOVERY_FIXED

---

## Cause CI

La fonction `list_available_families_cached()` dans `source_runtime_cache.py` filtrait
les familles par disponibilité des packs locaux (`is_pack_available_cached()`).

En fresh CI checkout, le répertoire `_source_packs/` est gitignored et absent.
Seule la famille `OS_TRAD_REVERSE_OS` était découverte (son pack est accessible
dans l'environnement CI). Les 7 autres familles retournaient un résultat vide.

---

## Différence local vs fresh checkout

| Environnement | Packs locaux | `list_available_families_cached()` avant P42B |
|---|---|---|
| Local dev | 8 familles | 8 familles |
| CI fresh checkout | 1 famille (OS_TRAD) | 1 famille |

Après P42B :

| Environnement | `list_available_families_cached()` après P42B |
|---|---|
| Local dev | 8 familles (depuis registry) |
| CI fresh checkout | 8 familles (depuis registry) |

---

## Familles registry-discoverable

Les 8 familles canoniques du registry `source_registry_summary.json` :

| Famille | Entrées | Source |
|---|---|---|
| ATLAS | 11 263 | F06_ATLAS_ZIP_INTERNAL_INVENTORY_CANON_DEDUPED.csv |
| COGNITIVE_REINTEGRATION | 2 052 | F07_COGNITIVE_ZIP_INTERNAL_INVENTORY.csv |
| COMPLIANCE_DATA_GOVERNANCE | 488 | F10_COMPLIANCE_DATA_GOVERNANCE_ZIP_INTERNAL_INVENTORY_DEDUPED.csv |
| EXTERNAL_SIGNALS | 82 | F04_EXTERNAL_SIGNALS_ZIP_INTERNAL_INVENTORY.csv |
| NARRATIVE_PROVENANCE_LAYER | 103 | F12_NPL_ZIP_INTERNAL_INVENTORY.csv |
| OS_TRAD_REVERSE_OS | 555 | P32_OS_TRAD_SAFE_ENTRY_CANDIDATES.csv |
| RSSI_RGPD | 976 | F03_RSSI_RGPD_ZIP_INTERNAL_INVENTORY_STRICT.csv |
| RSSI_SECURITY_PRESENTATION | 334 | F11_RSSI_SECURITY_ZIP_INTERNAL_INVENTORY.csv |

---

## Familles FULL_LOCAL vs METADATA_ONLY

| Mode | Signification | Hydration |
|---|---|---|
| `FULL_LOCAL` | Pack zip présent localement | Contenu de fichier réel chargé |
| `METADATA_ONLY` | Pack absent (CI fresh checkout) | Métadonnées registry uniquement |

Les ContextPackets METADATA_ONLY respectent tous les invariants de sécurité :
- `advisory_only = True`
- `readonly = True`
- `runtime_allowed_now = False`
- `emits_act = False`
- `decision_authority = KX108_ONLY`
- `source_status = "MISSING_LOCAL_PACK_METADATA_ONLY"`

---

## Fichiers modifiés

### `runtime_wiring/source_runtime/source_runtime_cache.py`

- Ajout de `list_discoverable_families()` : lit depuis `source_registry_summary.json`
  (commité en git, toujours présent), fallback sur le registry JSON complet.
- Ajout de `get_family_local_pack_availability()` : retourne un dict `family → bool`
  pour distinguer FULL_LOCAL de METADATA_ONLY par famille.
- Modification de `list_available_families_cached()` : délègue maintenant à
  `list_discoverable_families()`. Retourne toutes les familles du registry,
  indépendamment de la présence des packs locaux.

### `runtime_wiring/source_runtime/source_runtime_query.py`

- Ajout de `_is_discoverable()` : mêmes filtres de sécurité que `_is_routable()`
  mais sans vérification de disponibilité du pack local.
- Ajout de `_build_metadata_only_packet()` : construit un ContextPacket minimal
  valide depuis les métadonnées registry, sans lecture de fichier.
- Refonte de `query_source_packs()` : deux niveaux de candidats.
  - **Tier 1** (FULL_LOCAL) : entrées dont le pack est disponible → hydration complète.
  - **Tier 2** (METADATA_ONLY) : 1 entrée par famille non couverte par Tier 1 → metadata.

### `runtime_wiring/source_runtime/brody_source_context_bridge.py`

- Mise à jour du filtre `ok_results` : inclut maintenant `hydration_status == "METADATA_ONLY"`
  aux côtés de `"OK"`. Permet aux familles sans pack de contribuer au contexte Brody.

---

## Tests cassés réparés

| Test | Cause | Résultat après P42B |
|---|---|---|
| `test_smart_family_selection_in_payload` | `available_families=['OS_TRAD']` → COGNITIVE non sélectionnable | PASS |
| `test_preview_family_count_at_least_7` | `source_runtime_family_count=1` | PASS |
| `test_existing_families_still_present` | RSSI_RGPD absent de la liste | PASS |
| `test_source_runtime_families_list` | `len(families)=1 < 7` | PASS |
| `test_source_runtime_preview_with_packs` | `COGNITIVE_REINTEGRATION` absent de `selected_families` | PASS |

---

## Tests P42B ajoutés

Fichier : `tests/test_source_runtime_family_discovery_ci_p42b.py`

10 tests vérifiant :
1. `list_available_families_cached` retourne >=7 familles (fresh checkout)
2. `COGNITIVE_REINTEGRATION` discoverable
3. `RSSI_RGPD` discoverable
4. `OS_TRAD_REVERSE_OS` discoverable
5. Familles metadata-only restent `readonly=True` (skip si tous packs locaux)
6. Aucun `runtime_allowed_now=True` (skip si tous packs locaux)
7. Aucun `emits_act=True` (skip si tous packs locaux)
8. `decision_authority=KX108_ONLY` partout (skip si tous packs locaux)
9. Preview cognition sélectionne `COGNITIVE_REINTEGRATION`
10. Preview reverse sélectionne `OS_TRAD_REVERSE_OS`

Résultat local (tous packs disponibles) : **6 passed, 4 skipped**.
Résultat CI attendu (packs absents) : **10 passed**.

---

## Invariants NO_ACT / KX108_ONLY maintenus

- `runtime_allowed_now_true_count = 0` dans le registry (vérifié par `safety_invariants_ok`)
- Tous les ContextPackets METADATA_ONLY : `emits_act=False`, `decision_authority=KX108_ONLY`
- `_build_metadata_only_packet()` appelle `pkt.validate_invariants()` avant de retourner
- `route_packets()` retourne `ALLOW_CONTEXT_ONLY` (aucune violation de boundary)
- `check_forbidden_content.py` : `FORBIDDEN_CONTENT_PASS`

---

## Résultats de validation

```
python -m pytest tests/api/test_brody_source_pack_context_p28.py \
  tests/api/test_os_trad_reverse_preview_p32.py \
  tests/api/test_source_runtime_status_p29.py -q
→ 25 passed

python -m pytest tests/test_source_runtime_family_discovery_ci_p42b.py -q
→ 6 passed, 4 skipped

python -m pytest tests/ -q
→ 3673 passed, 4 skipped

python scripts/check_forbidden_content.py
→ FORBIDDEN_CONTENT_PASS

python scripts/generate_recursive_manifest.py && python scripts/verify_recursive_manifest.py
→ 7761 files, MANIFEST_VERIFIED
```
