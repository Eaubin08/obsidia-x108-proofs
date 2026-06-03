# P10A_ENGINE_RUNTIME_BRIDGE_PREFLIGHT_REPORT

**Phase:** P10A — Engine Runtime Bridge Preflight  
**Branche:** p8-runtime-dryrun-wiring  
**Date:** 2026-06-03  
**Statut:** READ_ONLY — aucune modification moteur exécutée  
**Verdict:** P10A_ENGINE_RUNTIME_BRIDGE_PREFLIGHT_READY

---

## 1. Où est le moteur existant

Le moteur Obsidia X-108 est structuré en deux couches principales :

| Couche | Racine | Rôle |
|--------|--------|------|
| **API** | `apps/obsidia_api/` | FastAPI V5B — tous les endpoints publics |
| **Périphérie** | `periphery/` | Modules métier (context, memory, brody, math_core, etc.) |

Point d'entrée API : `apps/obsidia_api/main.py` — FastAPI app V5B, titre "Obsidia X-108 API".  
Chargeur de composants : `apps/obsidia_api/runtime_loader.py` — `load_runtime_components()` avec `_safe_import()` (graceful fallback à `BACKEND_STUB` si module absent).

---

## 2. Modules existants identifiés

### 2.1 Modules sûrs confirmés

| Fichier | Classe / Fonction clé | Observations |
|---------|----------------------|--------------|
| `periphery/common.py` | `PeripheralSignalPacket`, `ActionCandidate` | `can_emit_act=False` guard, `assert_non_sovereign()` lève `PERIPHERY_CANNOT_EMIT_ACT` |
| `periphery/context/context_packet_builder.py` | `ContextPacket`, `build_context_packet()` | `can_decide=False` imposé, `assert_cannot_decide()` disponible |
| `periphery/context/context_packet_builder_v2.py` | `build_context_packet_v2()` | Chargé via `runtime_loader` → key `context` |
| `periphery/workflow_governance_readonly/adapters/x108_readonly_gateway_adapter.py` | `sop_to_x108_readonly_envelope()` | `runtime_binding=False`, `x108_merge=False`, `kernel_binding=False` |
| `periphery/workflow_governance_readonly/adapters/workflow_context_packet_adapter.py` | `sop_to_context_packet()` | Même garanties readonly |
| `periphery/workflow_governance_readonly/boundary.py` | `validate_readonly_output()`, `BoundaryViolation` | Garde readonly partagée |
| `apps/obsidia_api/runtime_loader.py` | `load_runtime_components()`, `_safe_import()` | Fallback propre — pattern extensible |
| `apps/obsidia_api/contracts.py` | `SovereignBase` | `readonly=True, emits_act=False, decision_authority=KX108_ONLY` |
| `apps/obsidia_api/safe_response.py` | `safe_backend_response()` | Emballage standard de toutes les réponses |
| `apps/obsidia_api/routes/x108.py` | router `/api/x108`, `_BOUNDARY` | Boundary dict canonique, pattern `KX108_ONLY` |

### 2.2 Symboles clés confirmés dans le moteur

| Symbole | Fichier | Conflit avec runtime_wiring ? |
|---------|---------|------------------------------|
| `ContextPacket` | `periphery/context/context_packet_builder.py` | **OUI — nom identique, champs différents** |
| `PeripheralSignalPacket` | `periphery/common.py` | Non — absent de runtime_wiring |
| `ActionCandidate` | `periphery/common.py` | Non — absent de runtime_wiring |
| `SovereignBase` | `apps/obsidia_api/contracts.py` | Non — Pydantic API uniquement |
| `_BOUNDARY` | `apps/obsidia_api/routes/x108.py` | Non — pattern dict, pas une classe |
| `BoundaryViolation` | `periphery/workflow_governance_readonly/boundary.py` | Non |

> **Conflit critique identifié :** `ContextPacket` existe dans DEUX espaces de noms :
> - `periphery.context.context_packet_builder.ContextPacket` → champs : `packet_id, action_id, status, content_hash, signals, can_decide`
> - `runtime_wiring.packet_types.ContextPacket` → champs : `source, context_id, advisory_only, emits_act, decision_authority, runtime_allowed_now, readonly`
>
> Le bridge P10B devra qualifier explicitement les imports pour éviter toute ambiguïté.

---

## 3. Ce que runtime_wiring peut brancher sans casser

### 3.1 — Point de branchement principal : `runtime_loader.py`

`load_runtime_components()` utilise `_safe_import()` avec fallback propre. On peut ajouter une entrée `runtime_wiring` dans le dictionnaire retourné **sans modifier la logique existante** :

```python
# AJOUT POSSIBLE EN P10B — aucune modification des entrées existantes
from runtime_wiring.engine_bridge.readonly_engine_bridge import (
    get_registry_summary_preview,
)
components["runtime_wiring_preview"] = {
    "status": "DRY_RUN_ONLY",
    "get_registry_summary_preview": get_registry_summary_preview,
    "decision_authority": "KX108_ONLY",
    "runtime_activation": False,
}
```

Ce branchement est **additionnel uniquement** — il ne modifie pas les clés `brody`, `context`, `x108_ingress`, etc.

### 3.2 — Point de branchement secondaire : boundary partagée

`periphery/workflow_governance_readonly/boundary.py` expose `validate_readonly_output()`.  
Le bridge peut l'importer en lecture pour valider ses propres sorties **sans modifier** le module.

### 3.3 — Référence de format : `periphery/context/context_packet_builder.py`

Le bridge peut importer `ContextPacket` (moteur) uniquement pour **comparaison de format** ou **preview de compatibilité**, jamais pour instancier un vrai packet.

### 3.4 — Adaptateurs workflow readonly

`sop_to_context_packet()` et `sop_to_x108_readonly_envelope()` peuvent être appelés en **preview-only** depuis un module bridge, uniquement si du texte SOP (source de spec) est fourni. Ils ne déclenchent aucune action monde.

---

## 4. Ce qu'il ne faut pas toucher

| Fichier / Module | Raison |
|-----------------|--------|
| `apps/obsidia_api/main.py` | Enregistrement des routers — toute modification change l'API live |
| `apps/obsidia_api/routes/x108.py` | Endpoints /api/x108 existants — ne pas modifier sans review |
| `periphery/common.py` | Définit les invariants `can_emit_act` — modification = risque de régression tous tests |
| `periphery/context/context_packet_builder.py` | Utilisé par runtime_loader — toute modification peut casser le context endpoint |
| `periphery/workflow_governance_readonly/agents/` | Internals du swarm — hors scope bridge |
| `proofs/`, `formal/`, `merkle*`, `seal*` | Crypto-ancré — FORBIDDEN |
| `runtime_contracts/` | Spécifications figées — FORBIDDEN |
| `_source_packs/`, `_freezes/` | Archives — FORBIDDEN |

---

## 5. Fichiers à créer en P10B

```
runtime_wiring/engine_bridge/
runtime_wiring/engine_bridge/__init__.py
runtime_wiring/engine_bridge/readonly_engine_bridge.py
runtime_wiring/engine_bridge/api_adapter_preview.py
runtime_wiring/engine_bridge/reports/P10B_ENGINE_BRIDGE_REPORT.md
tests/test_engine_bridge_p10b.py
```

### Responsabilités

**`readonly_engine_bridge.py`**
- Importe `runtime_wiring.packet_types.ContextPacket` (dry-run)
- Expose `registry_packet_to_engine_preview(entry)` → dict preview compatible `ContextPacketResponse`
- Importe `periphery.context.context_packet_builder.ContextPacket` comme référence de format uniquement (import qualifié explicite pour éviter le conflit de nom)
- Expose `get_registry_summary_preview()` → résumé readonly du registre
- Ne crée jamais un vrai `periphery.context.context_packet_builder.ContextPacket`

**`api_adapter_preview.py`**
- Expose `build_api_preview(entry)` → dict simulant la réponse `/api/context/from-message`
- Inclut `_PREVIEW_BOUNDARY = {"dry_run": True, "runtime_activation": False, "decision_authority": "KX108_ONLY"}`
- Jamais de vrai appel HTTP / FastAPI

---

## 6. Fichiers à modifier éventuellement en P10B

| Fichier | Modification | Condition |
|---------|-------------|-----------|
| `apps/obsidia_api/runtime_loader.py` | Ajouter clé `runtime_wiring_preview` | **Uniquement avec validation humaine explicite** |
| `runtime_wiring/README.md` | Ajouter section P10B Engine Bridge | Libre |

> **Règle P10B :** aucune modification de `apps/` ou `periphery/` sans validation humaine préalable.

---

## 7. Tests à prévoir en P10C

| Test | Description | Assertion clé |
|------|-------------|--------------|
| `test_engine_bridge_no_live_call` | Vérifie qu'aucun appel HTTP / FastAPI n'est fait | `monkeypatch.setattr(requests, 'get', crash)` → pas d'erreur |
| `test_registry_packet_to_engine_preview_format` | Le preview dict a les champs du `ContextPacketResponse` moteur | `packet_id, action_id, status, content_hash, signals, can_decide` présents |
| `test_engine_bridge_boundary_preserved` | Flags boundary inchangés après bridge | `decision_authority=KX108_ONLY`, `emits_act=False`, `dry_run=True` |
| `test_context_packet_name_no_collision` | Les deux ContextPacket sont distincts et non interchangeables | `isinstance()` ou import qualifié |
| `test_api_preview_dry_run_only` | `build_api_preview()` inclut `dry_run=True`, `runtime_activation=False` | Assertions sur le dict retourné |
| `test_engine_bridge_no_apps_write` | Le bridge n'écrit rien dans `apps/` ou `periphery/` | Scan de `open()` + `write()` dans le module |
| `test_engine_bridge_blocklist` | Aucun `ACT`, `kernel_mutation`, `world_action` dans les sorties | Scan contenu output |
| `test_no_packages_created` | `packages/` absent | `assert not Path('packages').exists()` |

---

## 8. Verdict

```
P10A_ENGINE_RUNTIME_BRIDGE_PREFLIGHT_READY
```

| Phase | Résultat |
|-------|---------|
| Precheck git | PASS — branche p8-runtime-dryrun-wiring, commit P9E présent, 34 tests verts |
| Inspection `apps/obsidia_api/main.py` | INSPECTÉ — FastAPI V5B, boundary KX108_ONLY |
| Inspection `periphery/common.py` | INSPECTÉ — PeripheralSignalPacket, can_emit_act=False |
| Inspection `periphery/context/context_packet_builder.py` | INSPECTÉ — ContextPacket moteur, can_decide=False |
| Inspection `periphery/workflow_governance_readonly/` | INSPECTÉ — 3 adaptateurs readonly, boundary validée |
| Inspection `apps/obsidia_api/runtime_loader.py` | INSPECTÉ — _safe_import extensible, SAFE_BRIDGE_TARGET |
| Inspection `apps/obsidia_api/routes/x108.py` | INSPECTÉ — pattern _BOUNDARY, READONLY_REFERENCE_ONLY |
| Conflit de nom ContextPacket | IDENTIFIÉ — plan P10B avec imports qualifiés |
| Blocklist moteur | CLAIRE — aucun fichier interdit dans scope P10B |
| Aucune modification exécutée | CONFIRMÉ |

### Classification des cibles

| Catégorie | Fichiers |
|-----------|---------|
| **A. SAFE_BRIDGE_TARGET** | `periphery/workflow_governance_readonly/adapters/*`, `periphery/context/context_packet_builder.py` (référence), `apps/obsidia_api/runtime_loader.py` (extension additive uniquement), `apps/obsidia_api/contracts.py` |
| **B. READONLY_REFERENCE_ONLY** | `periphery/workflow_governance_readonly/boundary.py`, `apps/obsidia_api/routes/x108.py`, `apps/obsidia_api/routes/context.py`, `apps/obsidia_api/safe_response.py` |
| **C. NEEDS_HUMAN_DECISION** | `apps/obsidia_api/main.py` (enregistrement router), `apps/obsidia_api/runtime_loader.py` (si modification) |
| **D. FORBIDDEN_NOW** | `periphery/common.py` (invariants critiques), `periphery/context/context_packet_builder.py` (pas de modification), `proofs/`, `formal/`, `runtime_contracts/`, `_source_packs/`, `_freezes/` |

### Prochain chantier

**P10B — Engine Bridge Readonly Adapter**  
Créer `runtime_wiring/engine_bridge/` avec `readonly_engine_bridge.py` et `api_adapter_preview.py`.  
Aucune modification `apps/periphery` sans validation humaine préalable.
