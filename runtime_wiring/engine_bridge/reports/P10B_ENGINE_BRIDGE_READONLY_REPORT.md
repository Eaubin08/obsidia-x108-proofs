# P10B_ENGINE_BRIDGE_READONLY_REPORT

**Status:** P10B_ENGINE_BRIDGE_READONLY_READY  
**Branche:** p8-runtime-dryrun-wiring  
**Phase:** P10B  
**Date:** 2026-06-03

---

## Summary

Création du pont moteur readonly `runtime_wiring/engine_bridge/` :

```
source_file_registry.json (14 779 entries)
  → route_sample_by_family() → 4 ContextPackets (runtime_wiring)
  → route_registry_packets_to_x108() → ALLOW_CONTEXT_ONLY / HOLD
  → _dry_run_packet_to_engine_preview() → engine schema preview (no periphery import)
  → EngineBridgePreview → api_payload_preview JSON
```

Aucune modification `apps/`. Aucune modification `periphery/`. KX108_ONLY.

---

## Fichiers créés

| Fichier | Rôle |
|---------|------|
| `runtime_wiring/engine_bridge/__init__.py` | module init |
| `runtime_wiring/engine_bridge/bridge_types.py` | dataclasses avec invariants fail_closed |
| `runtime_wiring/engine_bridge/readonly_engine_bridge.py` | bridge principal + `__main__` |
| `runtime_wiring/engine_bridge/api_adapter_preview.py` | payload JSON engine-compatible |
| `runtime_wiring/engine_bridge/reports/P10B_ENGINE_BRIDGE_READONLY_REPORT.md` | ce fichier |
| `_runtime_wiring_preflight/P10B_ENGINE_BRIDGE_RESULTS.md` | preflight results |

---

## Cibles moteur vues en P10A

| Cible | Catégorie P10A | Décision P10B |
|-------|---------------|---------------|
| `periphery/workflow_governance_readonly/adapters/x108_readonly_gateway_adapter.py` | SAFE_BRIDGE_TARGET | Non importé — bridge self-contained |
| `periphery/workflow_governance_readonly/adapters/workflow_context_packet_adapter.py` | SAFE_BRIDGE_TARGET | Non importé — bridge self-contained |
| `periphery/context/context_packet_builder.py` | SAFE_BRIDGE_TARGET | Schéma étudié par référence, **aucun import** |
| `apps/obsidia_api/runtime_loader.py` | NEEDS_HUMAN_DECISION | Non modifié — attente validation humaine |
| `apps/obsidia_api/contracts.py` | SAFE_BRIDGE_TARGET | Pattern `SovereignBase` copié par référence |
| `periphery/common.py` | FORBIDDEN_NOW | Non touché |
| `proofs/`, `formal/`, `runtime_contracts/` | FORBIDDEN_NOW | Non touché |

---

## Pourquoi apps/ et periphery/ non modifiés

1. **P10A classe `apps/obsidia_api/main.py` en NEEDS_HUMAN_DECISION** — enregistrer un nouveau router dans l'application live requiert validation explicite.
2. **`apps/obsidia_api/runtime_loader.py` NEEDS_HUMAN_DECISION** — ajouter une clé `runtime_wiring_preview` changerait le comportement de `load_runtime_components()` pour tous les endpoints existants.
3. **`periphery/` FORBIDDEN_NOW** — modifier les invariants de `PeripheralSignalPacket` ou `ContextPacket` risquerait de casser les 397 tests du moteur en production.
4. **Le bridge P10B est autosuffisant** — il n'a besoin d'aucun import `apps/` ni `periphery/` pour produire un preview complet et validé.

---

## Conflit ContextPacket — résolution par imports qualifiés

| Espace de noms | Classe | Champs |
|---------------|--------|--------|
| `periphery.context.context_packet_builder` | `ContextPacket` | `packet_id, action_id, status, content_hash, signals, can_decide` |
| `runtime_wiring.packet_types` | `ContextPacket` | `source, context_id, advisory_only, emits_act, decision_authority, runtime_allowed_now, readonly` |

**Résolution dans `readonly_engine_bridge.py` :**
- `periphery.context.context_packet_builder.ContextPacket` : **JAMAIS importé**
- `runtime_wiring.packet_types.ContextPacket` : utilisé via `route_sample_by_family()` (import indirect)
- La conversion vers le schéma moteur se fait dans `_dry_run_packet_to_engine_preview()` par **mapping de référence uniquement** (les noms de champs sont documentés en commentaire, pas importés)

---

## Pipeline bridge

| Étape | Fonction | Entrée | Sortie |
|-------|----------|--------|--------|
| 1 | `load_registry_json()` | `source_file_registry.json` | 14 779 `SourceFileRegistryEntry` |
| 2 | Vérification summary | `source_registry_summary.json` | `safety_invariants_ok=True` |
| 3 | `route_registry_packets_to_x108(critical=False)` | 14 779 entries | `ALLOW_CONTEXT_ONLY` |
| 4 | `route_registry_packets_to_x108(critical=True)` | 14 779 entries | `HOLD` |
| 5 | `route_sample_by_family(sample_size=1)` | 14 779 entries | 4 `ContextPacket` (dry-run) |
| 6 | `_dry_run_packet_to_engine_preview()` | dry-run `ContextPacket` | engine preview dict (4 entries) |
| 7 | `EngineBridgeSafetyStatus()` | — | safety flags all False |
| 8 | `EngineBridgeInput` + `EngineBridgeOutput` | steps 1–7 | dataclasses validés fail_closed |
| 9 | `build_api_preview_payload()` | `EngineBridgeOutput` + résultats | JSON engine-compatible |
| 10 | `validate_engine_bridge_safety()` | `EngineBridgePreview` | True ou ValueError |

---

## Décisions observées

| Scénario | Packets | Decision | Emits Act | Proof Claim | Engine Mutation |
|----------|---------|----------|-----------|-------------|----------------|
| Context only | 4 | `ALLOW_CONTEXT_ONLY` | false | false | false |
| Critical action | 4 | `HOLD` | false | false | false |

Engine packets preview (4/4) :
- `cp-dryrun-atlas-*` → `status=READY, can_decide=False, emits_act=False`
- `cp-dryrun-cognitive-*` → `status=READY, can_decide=False, emits_act=False`
- `cp-dryrun-compliance-*` → `status=READY, can_decide=False, emits_act=False`
- `cp-dryrun-rssi_rgpd-*` → `status=READY, can_decide=False, emits_act=False`

---

## Garanties no-act / no-runtime / no-engine-mutation

| Invariant | Mécanisme | Valeur |
|-----------|-----------|--------|
| `emits_act` | `EngineBridgeSafetyStatus.__post_init__()` fail_closed | `false` |
| `runtime_active` | `EngineBridgeOutput.__post_init__()` fail_closed | `false` |
| `engine_mutation` | `EngineBridgeOutput.__post_init__()` fail_closed | `false` |
| `apps_mutation` | `EngineBridgeOutput.__post_init__()` fail_closed | `false` |
| `periphery_mutation` | `EngineBridgeOutput.__post_init__()` fail_closed | `false` |
| `proof_claim` | `EngineBridgeOutput.__post_init__()` fail_closed | `false` |
| `decision_authority` | `_validate_safety()` dans tous les dataclasses | `KX108_ONLY` |
| `bridge_status` | `EngineBridgeOutput.__post_init__()` | `ENGINE_BRIDGE_PREVIEW_ONLY` |
| No ACT token | `validate_api_preview_payload()` scan | 0 occurrence |
| No apps/ import | Audit statique — aucun `import apps` | confirmé |
| No periphery/ import | Audit statique — aucun `import periphery` | confirmé |

---

## Résultat tests P8C + P9B

```
python -m pytest tests/test_runtime_wiring_p8c.py tests/test_source_registry_p9b.py -q
34 passed in 0.62s
```

---

## Prochain chantier — P10C

**P10C — Engine Bridge Tests**

Tests à créer dans `tests/test_engine_bridge_p10c.py` :

| Test | Assertion |
|------|-----------|
| `test_bridge_types_invariants` | Tous les dataclasses rejettent les violations fail_closed |
| `test_bridge_types_valid_construction` | Construction valide sans exception |
| `test_build_engine_bridge_preview` | 14 779 entries, 4 familles, ALLOW_CONTEXT_ONLY, HOLD |
| `test_engine_bridge_no_apps_import` | Aucun `import apps` dans engine_bridge/*.py |
| `test_engine_bridge_no_periphery_import` | Aucun `import periphery` dans engine_bridge/*.py |
| `test_engine_packets_preview_format` | 4 packets, champs engine schema présents, `can_decide=False` |
| `test_validate_api_preview_payload_valid` | payload valide → True |
| `test_validate_api_preview_payload_violations` | emits_act=True → ValueError, ACT token → ValueError |
| `test_build_safe_response_preview` | envelope `ok=True`, boundary correct |
| `test_no_packages_created` | `packages/` absent |
