# P61 — Bus Adapter Batch

**Status :** P61_BUS_ADAPTER_BATCH_READY
**Branche :** p61-bus-adapter-batch
**Date :** 2026-06-07

## Résumé

P61 traite les 4 fichiers `BUS_ADAPTER_BATCH` de P58 en mode **DRY_RUN_ONLY**.
2 fichiers adaptés créés, 1 bloqué (cible meilleure existante), 1 bloqué (import cassé).

## Fichiers adaptés (2)

### `apps/obsidia_api/bus/message.py`

- **Source :** `engine/bus/message.py`
- **Action :** `ADAPTED_DRY_RUN` — adapté depuis les dataclasses originales
- **Guards ajoutés :**
  - `DRY_RUN_ONLY = True` (constante module)
  - `IntentMsg.__post_init__` bloque `MsgIntentType.ACTION`
  - `MetaMsg.__post_init__` bloque `mode='live'`
  - `DecisionMsg.__post_init__` bloque toute décision hors `{BLOCK, HOLD}`
- **Garanties :** ACT ne peut jamais être retourné ou émis

### `apps/obsidia_api/bus/router.py`

- **Source :** `engine/bus/router.py`
- **Action :** `ADAPTED_DRY_RUN` — adapté depuis le router PROPOSE-only original
- **Guards ajoutés :**
  - `DRY_RUN_ONLY = True` (constante module)
  - `Router.register()` rejette tout module `ACTION`
  - `Router.run_propose_modules()` impose `dry_run=True` — lève `ValueError` sinon
  - Chaque résultat inclut `_dry_run=True` et `_act_emitted=False`
- **Garanties :** aucune route active, aucune émission ACT

## Bloqué — cible différente (1)

| Fichier | Raison |
|---|---|
| `engine/bus/__init__.py` → `apps/obsidia_api/bus/__init__.py` | Source vide, cible existante meilleure (commentaire F54) — non écrasé |

## Bloqué — adaptateur manuel requis (1)

| Fichier | Raison |
|---|---|
| `engine/bus/registry.py` → `apps/obsidia_api/bus/registry.py` | Import cassé : `from modules.os_trad.adapter import os_trad_propose` absent du repo proof. Adapter manuellement pour stubber la dépendance. |

## Périmètres non touchés

| Périmètre | Modifié |
|---|---|
| sigma/ | NON |
| runtime_wiring/ | NON |
| proofs/V18_3_1/ | NON |
| apps/obsidia_api/routes/ | NON |
| ACT | NON |
| memory_write | NON |
| graphiti_write | NON |
| kernel_mutation | NON |

## Suite

**P62** — MANUAL_REVIEW_DEFERRED (agents, engine, OS layers — revue architecturale)
