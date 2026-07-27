# V17 PART_B — Heartbeat Caller & Activation

```
STATUS:   DRAFT_NOT_APPROVED
REVISION: PART_B_REV01
PALIER:   PALIER_PROPOSAL_GUARD_RECLAIM_FIX_V17 PART_B
DATE:     2026-07-27
AUTHOR:   draft inféré — aucune approbation humaine
BASE_SHA: 69b8985ab21eb678ab7ed507e67c5c41e3441eaa (feat/v17-part-a-session-lock)
```

> **Ce document est un brouillon non approuvé.**
> Il ne constitue ni une spécification normative, ni une autorisation d'implémenter.
> Toute implémentation requiert une révision et une signature humaine explicite.
> Les exigences marquées `INFERENCE_FOR_REVIEW` sont des inférences soumises à
> validation. Les blocs `HUMAN_DECISION_REQUIRED` ne doivent pas être résolus
> unilatéralement.

---

## 1. Identité du palier

| Champ | Valeur |
|---|---|
| Identifiant | `V17_PART_B` |
| Révision draft | `PART_B_REV01` |
| Mandat complet | `PALIER_PROPOSAL_GUARD_RECLAIM_FIX_V17 PART_B` |
| Base normative | `PART_A_REV10` (APPROVED_AND_CLOSED, SHA `69b8985`) |
| Précédent palier | V17 PART_A (APPROVED_AND_CLOSED) |
| Palier suivant | V17 PART_C (indéterminé — voir §25) |
| Statut | **DRAFT_NOT_APPROVED** |

---

## 2. Statut

```
DRAFT_NOT_APPROVED

Ce brouillon est produit exclusivement à partir de :
  - deux mentions structurantes dans le code PART_A (lignes 13 et 131 de
    periphery/session_lock/heartbeat_lock_manager.py, commit 69b8985) ;
  - l'interface publique de HeartbeatLockManager telle qu'exposée dans
    periphery/session_lock/__init__.py ;
  - les 20 tests de periphery/tests/test_heartbeat_lock_manager.py.

Aucun document de spécification PART_B autonome n'a été retrouvé dans le
dépôt, l'historique git ou les archives locales (audit V17_PART_B_SPEC_NOT_FOUND,
2026-07-26).
```

---

## 3. Relation avec PART_A

`SOURCE_PART_A_CODE` — module docstring, ligne 13 :
> « la boucle est pilotée explicitement par un appelant futur (PART_B, non autorisé) »

`SOURCE_PART_A_CODE` — commentaire structurel, lignes 129–131 :
> « real_stale_lock_reclaim: NOT_AUTHORIZED (PART_A_REV10, statut final).
> Aucune configuration ne peut activer l'exécution réelle du reclaim :
> ce verrou est structurel et relève d'un futur palier (PART_B, non autorisé). »

PART_A expose une bibliothèque stateful sans boucle propre :
- aucun thread lancé,
- aucun import de `apps/`, `scripts/`, `sigma/`, `kernel/`,
- pilotage entièrement délégué à un appelant extérieur.

PART_B est cet appelant. Elle ne modifie pas PART_A.

---

## 4. Non-objectifs

Les éléments suivants sont explicitement hors périmètre de ce draft :

- Modifier `periphery/session_lock/heartbeat_lock_manager.py` (PART_A).
- Modifier `periphery/session_lock/__init__.py`.
- Modifier `periphery/tests/test_heartbeat_lock_manager.py`.
- Implémenter le reclaim réel (`execute_reclaim` reste `NOT_AUTHORIZED` sauf décision §19).
- Implémenter un wiring vers `apps/`, `scripts/`, `sigma/`, `kernel/`.
- Modifier tout fichier kernel, Lean, TLA+, CLI, Sigma, ou workflow existant.
- Fournir des valeurs par défaut aux paramètres humains manquants.
- Prendre des décisions listées aux blocs `HUMAN_DECISION_REQUIRED`.

---

## 5. Invariants hérités de PART_A

`SOURCE_PART_A_CODE` — module docstring, lignes 8–25 :

| Invariant | Valeur figée |
|---|---|
| `disabled by default` | `HeartbeatConfig.enabled = False` — toute opération fail-closed sans config |
| `aucun wiring runtime` | Aucun import de couches non periphery |
| `aucun reclaim réel` | `REAL_RECLAIM_EXECUTION_AUTHORIZED = False` (constante hardcodée l. 132) |
| `paramètres non inventables` | `heartbeat_interval_seconds`, `max_v2_future_clock_skew_seconds`, `human_approved_corrected_gf_r01_sha256` sans valeur par défaut |
| `toute ambiguïté → FAIL_CLOSED` | `human_recovery_required=True` sur tout résultat d'erreur normative |
| `DECISION_AUTHORITY=KX108_ONLY` | Déclaré dans docstring et `__init__.py` — mécanisme précis non spécifié dans PART_A |

Ces invariants s'appliquent à PART_B sans modification.

---

## 6. Interfaces publiques consommables

`SOURCE_PART_A_CODE` — `periphery/session_lock/__init__.py` réexporte :

```python
from periphery.session_lock.heartbeat_lock_manager import (
    FailureCode,
    HeartbeatConfig,
    HeartbeatLockManager,
    HeartbeatRuntimeState,
    LockClassification,
    OperationResult,
)
```

Enums additionnels disponibles à l'import direct :

```python
from periphery.session_lock.heartbeat_lock_manager import (
    ControlRequest,    # STOP | ABORT
    HandoffAction,     # CONSUME_CONTROL | RESUME_WAIT
    TickAdmissionState,
)
```

---

## 7. Table de vérité des gates PART_A

Cette table est construite à partir du code source committé (`69b8985`),
en particulier la méthode `_gate()` (lignes 225–238) et le corps de chaque
méthode publique. Elle corrige une erreur du rapport d'audit précédent.

### Résolution de la contradiction

**Affirmation erronée (rapport d'audit 2026-07-26) :**
> « l'absence d'un des trois paramètres bloque toutes les opérations »

**Réalité du code (`SOURCE_PART_A_CODE`) :**

`_gate()` vérifie uniquement :
1. `config.enabled == True` → sinon `MANAGER_DISABLED`
2. `config.heartbeat_interval_seconds is not None` → sinon `HEARTBEAT_CONFIG_MISSING`

`max_v2_future_clock_skew_seconds` et `human_approved_corrected_gf_r01_sha256`
**ne sont pas vérifiés par `_gate()`**. Ils bloquent uniquement les chemins
spécifiques documentés ci-dessous.

### Table par méthode

| Méthode | `enabled` requis | `interval` requis | `skew` requis | `gf_r01` requis | Lecture seule | Fichier muté | États runtime admis | Fail-closed possible | Autorisée PART_A | Rôle caller PART_B |
|---|---|---|---|---|---|---|---|---|---|---|
| `acquire_session_lock()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ❌ | lock JSON (création) | `NOT_STARTED` seulement | Oui (`MANAGER_DISABLED`, `HEARTBEAT_CONFIG_MISSING`, `HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID`, `HEARTBEAT_LOCK_IDENTITY_MISMATCH`) | ✅ | Appelée une fois au démarrage de session |
| `heartbeat_tick()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ❌ | lock JSON (`heartbeat_at` mis à jour) | `ACTIVE_WAITING`, `CONTROL_PENDING` | Oui (`MANAGER_DISABLED`, `HEARTBEAT_CONFIG_MISSING`, `HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID`, `POST_ACTIVATION_HEARTBEAT_FAULT`) | ✅ | Appelée en boucle par le caller |
| `request_control()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ✅ (état interne seulement) | aucun | tout état (après `_gate`) | Oui (`MANAGER_DISABLED`, `HEARTBEAT_CONFIG_MISSING`) | ✅ | Injectée par l'opérateur ou gate externe |
| `consume_control()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ✅ (état interne seulement) | aucun | `ACTIVE_WAITING`, `CONTROL_PENDING` (FORBIDDEN en `ACTIVE_TICK`) | Oui (`HEARTBEAT_RUNTIME_CONTROL_CONSUMPTION_STATE_INVALID`) | ✅ | Appelée après handoff `CONSUME_CONTROL` |
| `commit_termination()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ✅ (état interne seulement) | aucun | `STOPPING`, `ABORTING` seulement | Oui (`HEARTBEAT_RUNTIME_TERMINATION_STATE_INVALID`) | ✅ | Appelée après `consume_control()` |
| `classify_lock()` | ✅ via `_gate` | ✅ via `_gate` | ⚠️ si `heartbeat_at > now` | ❌ | ✅ (lecture seule) | aucun | tout état (après `_gate`) | Oui (si `heartbeat_at > now` et `skew is None` → `UNCLASSIFIABLE_FAIL_CLOSED`) | ✅ | Optionnelle — diagnostic du lock |
| `release_session()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ❌ | lock JSON (suppression) | `ACTIVE_WAITING`, `CONTROL_PENDING`, `STOPPING`, `ABORTING`, `FAULTED` | Oui (plusieurs codes) | ✅ | Appelée en fin de session |
| `prepare_reclaim_proposal()` | ✅ via `_gate` | ✅ via `_gate` | ⚠️ pour lock V2 | ✅ requis | ✅ (aucune mutation si succès) | aucun | tout état (après `_gate`) | Oui (`RECLAIM_AUTHORIZATION_INVALID`) | ✅ (proposition seulement) | Optionnelle — diagnostic lock orphelin |
| `execute_reclaim()` | ❌ (bypass `_gate`) | ❌ (bypass `_gate`) | ❌ | ❌ | ✅ | aucun | ignoré | Oui (toujours `RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED`) | ❌ (structurellement refusée) | Toujours fail-closed — aucun usage en PART_B |

**Légende :**
- ✅ requis / applicable
- ❌ non requis / non applicable
- ⚠️ conditionnellement requis (selon données lues)

**Note sur `execute_reclaim()` :** cette méthode ne passe pas par `_gate()` (l. 668–675).
Elle retourne `RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED` **quels que soient les arguments
et l'état de la config**. PART_B ne doit pas l'appeler en attente d'un succès.

---

## 8. Machine d'états attendue du futur caller

`INFERENCE_FOR_REVIEW` — déduite de l'interface `HeartbeatRuntimeState` et de la
logique de `heartbeat_tick()` + `consume_control()` + `commit_termination()`.

```
[INIT]
  └─► acquire_session_lock()
        ├─ ok → ACTIVE_WAITING
        └─ fail → [HALT — fail-closed]

[ACTIVE_WAITING]
  └─► heartbeat_tick()
        ├─ ok, handoff == RESUME_WAIT    → attendre interval → [ACTIVE_WAITING]
        ├─ ok, handoff == CONSUME_CONTROL → [CONTROL_PENDING]
        └─ fail (faute lock)             → [FAULTED]

[CONTROL_PENDING]
  └─► consume_control()
        ├─ ok, consumed == STOP  → [STOPPING]
        ├─ ok, consumed == ABORT → [ABORTING]
        └─ fail                  → [FAULTED]

[STOPPING | ABORTING]
  └─► commit_termination()
        ├─ ok → [TERMINATED]
        └─ fail → [FAULTED]

[TERMINATED | FAULTED]
  └─► release_session()
        ├─ ok → [RELEASED]
        └─ fail → [RELEASE_FAILED — human recovery]

[RELEASED]   — état final nominal
[HALT]       — état final anormal (fail-closed sans acquisition du lock)
[RELEASE_FAILED] — état final anormal (human_recovery_required)
```

Les transitions `request_control()` et `classify_lock()` peuvent intervenir
à tout moment (depuis un thread de contrôle ou un gate externe) selon le
modèle d'exécution retenu — voir §9.

---

## 9. Modèle d'exécution à décider

```
HUMAN_DECISION_REQUIRED — DECISION_B

Choisir exactement un modèle d'exécution pour le caller PART_B.

Options identifiées (non exhaustives) :

A. Polling synchrone piloté
   Le caller s'exécute dans le fil d'exécution de l'opérateur.
   Il appelle heartbeat_tick() en boucle avec un sleep explicite.
   Aucun thread créé par PART_B.
   Compatibilité maximale avec l'invariant PART_A « aucun thread lancé ici »
   (NOTE : cet invariant s'applique à HeartbeatLockManager, pas nécessairement
   au caller PART_B lui-même).

B. Thread dédié
   PART_B crée un thread qui boucle sur heartbeat_tick() + sleep.
   PART_A ne lance aucun thread, mais PART_B peut en lancer un.
   Implique une synchronisation inter-thread pour request_control().

C. Processus externe
   Caller exécuté hors du processus principal.
   Communication via IPC ou fichier de signalisation.

D. Ordonnanceur existant
   La boucle est intégrée à un scheduler ou event loop déjà présent dans
   le système (ex. asyncio, APScheduler, etc.).
   Implique des dépendances supplémentaires à auditer.

E. Autre modèle défini humainement.

Décision attendue de l'opérateur avant toute implémentation.
```

---

## 10. Politique d'activation à décider

```
HUMAN_DECISION_REQUIRED — DECISION_C

Choisir l'autorité et le mécanisme d'activation (passage de enabled=True
+ heartbeat_interval_seconds à HeartbeatConfig).

Options identifiées (non exhaustives) :

A. Opérateur humain direct
   Variable d'environnement ou fichier de configuration modifié manuellement.

B. Terminal existant
   Le terminal Obsidia passe la config au caller PART_B.
   Implique un wiring terminal → PART_B à définir.

C. Gate externe
   Une gate (ex. engine_gates existant) autorise l'activation.
   Implique un audit du périmètre de la gate.

D. KX108 exclusif
   KX108 fournit la config au caller.
   Implique que le mécanisme d'autorisation KX108 soit spécifié (voir §11).

E. Combinaison de plusieurs autorités.

F. Autre mécanisme défini humainement.

SOURCE_PART_A_CODE (l. 229) : le message d'erreur indique
« activation humaine requise » — mais cela s'applique à HeartbeatLockManager,
non au caller PART_B. La source de la décision d'activation pour PART_B
reste non spécifiée dans PART_A.
```

---

## 11. Autorité KX108 à préciser

`SOURCE_PART_A_CODE` — module docstring, l. 25 :
> `DECISION_AUTHORITY=KX108_ONLY`

`SOURCE_PART_A_CODE` — `__init__.py`, l. 4 :
> `DECISION_AUTHORITY=KX108_ONLY`

```
HUMAN_DECISION_REQUIRED — DECISION_D

L'invariant DECISION_AUTHORITY=KX108_ONLY est déclaré dans PART_A mais son
mécanisme d'application n'est pas codé dans le composant.

Questions ouvertes pour PART_B :
1. KX108 doit-il valider chaque tick, ou seulement l'activation initiale ?
2. KX108 doit-il être en mesure d'émettre request_control(STOP|ABORT) ?
3. KX108 doit-il recevoir les résultats de classify_lock() ?
4. Le caller PART_B peut-il s'exécuter sans interaction KX108 tick-à-tick,
   ou KX108 doit-il approuver chaque transition ?
5. Quel est le canal de communication entre PART_B et KX108 ?

NE PAS déduire que KX108 « observe et autorise » sans source normative :
cette formulation n'apparaît pas dans PART_A. Elle constitue une INFERENCE
qui doit être validée.
```

---

## 12. Source de configuration à préciser

```
HUMAN_DECISION_REQUIRED — DECISION_E

PART_A exige trois paramètres sans valeur par défaut :
  - heartbeat_interval_seconds
  - max_v2_future_clock_skew_seconds
  - human_approved_corrected_gf_r01_sha256

Questions ouvertes :
1. Ces valeurs sont-elles stockées en variable d'environnement, fichier de
   configuration, secret manager ou fournie à la construction du caller ?
2. La config est-elle immuable une fois le caller démarré, ou reconfigurable
   en cours d'exécution ?
3. Qui valide que les valeurs fournies sont correctes avant activation ?
4. En cas d'absence d'un paramètre au démarrage, le caller doit-il
   bloquer l'ensemble du démarrage ou uniquement la fonctionnalité concernée ?

NE PAS inventer des valeurs par défaut. NE PAS utiliser les fixtures de test
(interval=10.0, skew=5.0) comme valeurs de production.
SOURCE_PART_A_TEST, l. 9–11 :
« Les valeurs numériques utilisées ici (interval=10, skew=5) sont des
FIXTURES DE TEST locales : elles n'établissent aucune valeur par défaut
de production (les paramètres humains restent non résolus). »
```

---

## 13. Paramètres humains manquants

Chaque paramètre est documenté avec sa portée exacte issue du code (`SOURCE_PART_A_CODE`).

### 13.1 HEARTBEAT_INTERVAL_SECONDS

| Champ | Valeur |
|---|---|
| Nom dans `HeartbeatConfig` | `heartbeat_interval_seconds: Optional[float] = None` |
| Vérifié par `_gate()` | **OUI** — son absence bloque toutes les opérations gated |
| Utilisé dans | `classify_lock()` ligne 469 : `2 * interval` comme seuil de staleness |
| Code d'erreur si absent | `HEARTBEAT_CONFIG_MISSING` |
| Valeur par défaut | **Aucune** |
| Valeur de test (non production) | `10.0` (fixture test uniquement) |
| Statut | `HUMAN_DECISION_REQUIRED` |

### 13.2 MAX_V2_FUTURE_CLOCK_SKEW_SECONDS

| Champ | Valeur |
|---|---|
| Nom dans `HeartbeatConfig` | `max_v2_future_clock_skew_seconds: Optional[float] = None` |
| Vérifié par `_gate()` | **NON** |
| Utilisé dans | `classify_lock()` ligne 476 : si `heartbeat_at > now` seulement |
| Utilisé dans | `prepare_reclaim_proposal()` ligne 627 : pour lock V2 seulement |
| Code d'erreur si absent (classify) | `RECLAIM_AUTHORIZATION_INVALID` + `UNCLASSIFIABLE_FAIL_CLOSED` |
| Code d'erreur si absent (reclaim V2) | `RECLAIM_AUTHORIZATION_INVALID` |
| Valeur par défaut | **Aucune** |
| Valeur de test (non production) | `5.0` (fixture test uniquement) |
| Statut | `HUMAN_DECISION_REQUIRED` |

### 13.3 HUMAN_APPROVED_CORRECTED_GF_R01_SHA256

| Champ | Valeur |
|---|---|
| Nom dans `HeartbeatConfig` | `human_approved_corrected_gf_r01_sha256: Optional[str] = None` |
| Vérifié par `_gate()` | **NON** |
| Utilisé dans | `prepare_reclaim_proposal()` ligne 620 : toujours, avant tout reclaim |
| Code d'erreur si absent | `RECLAIM_AUTHORIZATION_INVALID` : « tout reclaim réel interdit » |
| Valeur par défaut | **Aucune** |
| Signification | Hash SHA-256 d'un artefact approuvé humainement lié à GF_R01 |
| Statut | `HUMAN_DECISION_REQUIRED` |

---

## 14. Mutations autorisées pour le futur caller PART_B

`INFERENCE_FOR_REVIEW` — déduites de l'interface publique PART_A :

Le caller PART_B peut légitimement :

1. Instancier `HeartbeatLockManager` avec une `HeartbeatConfig` valide.
2. Appeler `acquire_session_lock()` une fois au démarrage.
3. Appeler `heartbeat_tick()` en boucle (rythme = §9 à décider).
4. Appeler `request_control(ControlRequest.STOP | ABORT)` en réponse à un signal.
5. Appeler `consume_control()` sur réception d'un `handoff == CONSUME_CONTROL`.
6. Appeler `commit_termination()` depuis `STOPPING` ou `ABORTING`.
7. Appeler `classify_lock()` à titre de diagnostic (lecture seule).
8. Appeler `prepare_reclaim_proposal()` à titre de diagnostic (lecture seule).
9. Appeler `release_session()` en fin de vie nominale ou post-faute.
10. Créer des fichiers propres à PART_B dans `periphery/` (nouveau module caller).
11. Créer des tests dans `periphery/tests/`.

---

## 15. Mutations interdites

`SOURCE_PART_A_CODE` + `INFERENCE_FOR_REVIEW` :

1. Modifier `periphery/session_lock/heartbeat_lock_manager.py`.
2. Modifier `periphery/session_lock/__init__.py`.
3. Modifier `periphery/tests/test_heartbeat_lock_manager.py`.
4. Modifier `REAL_RECLAIM_EXECUTION_AUTHORIZED` (sauf décision humaine §19).
5. Appeler `execute_reclaim()` en attente d'un succès — toujours `NOT_AUTHORIZED`.
6. Importer `apps/`, `scripts/`, `sigma/`, `kernel/` depuis le caller.
7. Fournir des valeurs numériques inventées aux paramètres humains.
8. Écraser un lock JSON existant (l. 253–256 : refus explicite).
9. Supprimer le lock JSON autrement que via `release_session()`.
10. Modifier le lock JSON autrement que via `heartbeat_tick()`.
11. Toucher `session_level3_owned`, `level1_locked`, `level2_locked` directement
    (champs publics mais normativement gérés par le manager).

---

## 16. Politique de faute

`SOURCE_PART_A_CODE` — `_enter_fault()` lignes 425–442 :

- Toute mismatch d'identité du lock JSON pendant un tick déclenche `FAULTED`.
- La première faute est préservée dans `runtime_fault`.
- Les fautes secondaires s'accumulent dans `secondary_faults`.
- `FAULTED` est un état terminal pour la boucle heartbeat.
- Depuis `FAULTED`, `release_session()` reste possible (l. 108–114 : `FAULTED` ∈ `RELEASE_ALLOWED_STATES`).
- Le caller PART_B doit propager la faute à l'opérateur et ne pas relancer la boucle.

`HUMAN_DECISION_REQUIRED — DECISION_F` :
Le mécanisme de notification de la faute à KX108 et à l'opérateur n'est pas
spécifié dans PART_A. PART_B doit définir ce canal.

---

## 17. Politique de terminaison

`SOURCE_PART_A_CODE` — `commit_termination()` lignes 386–423 :

Séquence nominale : `request_control(STOP)` → `heartbeat_tick()` retourne
`CONSUME_CONTROL` → `consume_control()` → `STOPPING` → `commit_termination()`.

`SOURCE_PART_A_CODE` — l. 422 :
> « jamais : suppression du lock JSON, auto-reclaim, toucher au Level 3 »

Après `commit_termination()` : `periodic_loop_terminated = True`, `terminal_event = True`.
La session reste ouverte (Level 3 détenu) jusqu'à `release_session()`.

`INFERENCE_FOR_REVIEW` : le caller PART_B doit appeler `release_session()`
après toute terminaison (nominale ou post-faute) pour libérer le Level 3.

---

## 18. Politique de release

`SOURCE_PART_A_CODE` — `release_session()` lignes 505–580 :

Préconditions vérifiées :
- `runtime_state ∈ RELEASE_ALLOWED_STATES` = {ACTIVE_WAITING, CONTROL_PENDING, STOPPING, ABORTING, FAULTED}
- `session_level3_owned == True`
- `tick_in_progress == False` et `level1_locked == level2_locked == False`

Transaction (PART_B..H de SECTION_13, déjà implémentée dans PART_A) :
- PART_D : validation état du lock JSON (bytes exacts)
- PART_E : unlink du lock JSON avec fsync + vérification d'absence
- PART_F : libération du target handle Level 3
- PART_G (finally) : libération des locks Level 1 et Level 2
- PART_H : vérification des postconditions

Résultat final : `session_release_state = "RELEASED"`.

---

## 19. Statut du reclaim réel

`SOURCE_PART_A_CODE` — constante l. 132 :
```python
REAL_RECLAIM_EXECUTION_AUTHORIZED = False
```

`SOURCE_PART_A_CODE` — `execute_reclaim()` lignes 668–675 :
```python
def execute_reclaim(self, *_args, **_kwargs) -> OperationResult:
    """Le reclaim réel (PART_B..H de SECTION_14 avec mutation) est
    structurellement refusé dans PART_A : real_stale_lock_reclaim est
    NOT_AUTHORIZED. Aucun paramètre ne peut lever ce refus."""
    return OperationResult.failure(
        FailureCode.RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED,
        "real_stale_lock_reclaim: NOT_AUTHORIZED (PART_A_REV10)",
    )
```

**Par défaut documentaire : `REAL_RECLAIM_EXECUTION_AUTHORIZED = False` est maintenu.**

```
HUMAN_DECISION_REQUIRED — DECISION_G

Choisir exactement une option pour le reclaim réel dans V17 :

A. Demeure définitivement interdit dans V17.
   REAL_RECLAIM_EXECUTION_AUTHORIZED reste False.
   execute_reclaim() continue de retourner NOT_AUTHORIZED.

B. Reporté à un palier PART_C distinct.
   V17 PART_B n'active pas le reclaim. Un futur palier V17 PART_C
   le spécifiera et l'implémentera sous nouvelles preuves.

C. Autorisé dans V17 PART_B sous conditions strictes.
   Implique de modifier heartbeat_lock_manager.py (PART_A) —
   ce qui requiert une approbation humaine explicite et un plan de
   vérification séparé.

D. Autre décision humaine.

Aucune option ne peut être retenue unilatéralement.
```

---

## 20. Périmètre futur des fichiers

`INFERENCE_FOR_REVIEW` — soumis à validation selon §9 (modèle d'exécution) :

```
periphery/
  session_lock/
    heartbeat_lock_manager.py       ← PART_A — NE PAS TOUCHER
    __init__.py                     ← PART_A — NE PAS TOUCHER
    heartbeat_caller.py             ← PART_B nouveau (nom provisoire)
    heartbeat_config_loader.py      ← PART_B optionnel (chargeur config)

  tests/
    test_heartbeat_lock_manager.py  ← PART_A — NE PAS TOUCHER
    test_heartbeat_caller.py        ← PART_B nouveau

docs/
  paliers/
    V17_PART_B_REV01_DRAFT.md      ← ce document
```

Le nom `heartbeat_caller.py` est provisoire. La structure exacte dépend du
modèle d'exécution retenu (§9) et de la politique d'activation (§10).

---

## 21. Plan de tests proposé

`INFERENCE_FOR_REVIEW` — aucun de ces tests n'est implémenté.

| # | Titre | Comportement attendu | Méthodes impliquées |
|---|---|---|---|
| T01 | Activation refusée sans config | Sans `enabled=True` + `interval`, toutes les opérations retournent `MANAGER_DISABLED` ou `HEARTBEAT_CONFIG_MISSING` | `acquire_session_lock`, `heartbeat_tick`, etc. |
| T02 | Boucle nominale N ticks | N appels à `heartbeat_tick()` retournent `RESUME_WAIT` et mettent à jour `heartbeat_at` | `acquire_session_lock`, `heartbeat_tick` × N |
| T03 | STOP nominal | `request_control(STOP)` → tick → `CONSUME_CONTROL` → `consume_control` → `STOPPING` → `commit_termination` → `TERMINATED` | séquence complète |
| T04 | ABORT nominal | Même séquence avec `ABORT` | séquence complète |
| T05 | Handoff `CONSUME_CONTROL` sans tick | `control_request_pending=True` avant tick → `heartbeat_tick` retourne `CONSUME_CONTROL` | `request_control`, `heartbeat_tick` |
| T06 | Handoff `RESUME_WAIT` | Aucune requête pendante → `heartbeat_tick` retourne `RESUME_WAIT` | `heartbeat_tick` |
| T07 | Identité lock modifiée pendant tick | Modification externe du lock JSON → `heartbeat_tick` déclenche `FAULTED` | `heartbeat_tick`, `_enter_fault` |
| T08 | Configuration partielle | `enabled=True` sans `interval` → `HEARTBEAT_CONFIG_MISSING` | `_gate` |
| T09 | Horloge future sans skew | `heartbeat_at > now` et `max_v2_future_clock_skew_seconds is None` → `UNCLASSIFIABLE_FAIL_CLOSED` | `classify_lock` |
| T10 | Release non quiescent | `tick_in_progress=True` → `release_session` retourne `RELEASE_HEARTBEAT_NOT_QUIESCENT` | `release_session` |
| T11 | Interruption caller | Simulation d'une interruption entre tick N et N+1 — le lock JSON reste intact, `release_session` réussit | scénario crash partiel |
| T12 | Redémarrage caller | Caller arrêté puis nouvelle instance créée — l'ancienne instance détient le lock, `acquire_session_lock` refuse l'écrasement | `acquire_session_lock` |
| T13 | Déterminisme | Mêmes entrées → mêmes résultats sur deux instances distinctes | toutes méthodes |
| T14 | Absence de mutation hors lock | Aucun fichier autre que le lock JSON n'est modifié pendant une boucle complète | ensemble du cycle |
| T15 | Reclaim réel toujours bloqué | `execute_reclaim()` retourne `RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED` quels que soient les arguments et l'état de la config | `execute_reclaim` |
| T16 | Absence de bypass KX108 | Aucun chemin d'exécution ne permet de contourner `DECISION_AUTHORITY=KX108_ONLY` | à définir selon §11 |

---

## 22. Critères de sortie

`INFERENCE_FOR_REVIEW` — soumis à validation humaine :

- [ ] Toutes les décisions `HUMAN_DECISION_REQUIRED` (DECISION_B à DECISION_G) ont été prises.
- [ ] Un document `V17_PART_B_REV01_APPROVED.md` a remplacé ce draft et porte une signature humaine explicite.
- [ ] Les 16 tests proposés (T01–T16) sont implémentés et passants.
- [ ] `PART_A_REV10` (commit `69b8985`) est inchangé.
- [ ] `execute_reclaim()` retourne toujours `RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED` (sauf si DECISION_G retient l'option C).
- [ ] Aucun import de `apps/`, `scripts/`, `sigma/`, `kernel/` dans le code PART_B.
- [ ] Le caller PART_B ne contient aucune valeur numérique inventée pour les paramètres humains.
- [ ] `git diff` entre `docs/v17-part-b-rev01-draft` et `origin/feat/v17-part-a-session-lock` ne touche que les fichiers du périmètre PART_B décrit au §20.

---

## 23. Conditions de HOLD/BLOCK

PART_B est en HOLD immédiat si l'une des conditions suivantes est vraie :

| Condition | Code d'erreur | Priorité |
|---|---|---|
| `enabled == False` | `MANAGER_DISABLED` | HOLD total |
| `heartbeat_interval_seconds is None` | `HEARTBEAT_CONFIG_MISSING` | HOLD total |
| `runtime_state` invalide pour l'opération | selon méthode | HOLD opération |
| `heartbeat_at > now` et `max_v2_future_clock_skew_seconds is None` | `UNCLASSIFIABLE_FAIL_CLOSED` | HOLD classify |
| `human_approved_corrected_gf_r01_sha256 is None` | `RECLAIM_AUTHORIZATION_INVALID` | HOLD reclaim |
| Lock JSON modifié extérieurement | `HEARTBEAT_LOCK_IDENTITY_MISMATCH` → `FAULTED` | HOLD boucle + faute |
| Décision humaine DECISION_B à DECISION_G non prise | (hors code) | HOLD implémentation |

`SOURCE_PART_A_CODE` — module docstring l. 22 :
> « toute ambiguïté produit FAIL_CLOSED + HUMAN_RECOVERY_DECISION_REQUIRED »

---

## 24. Décisions humaines obligatoires

Récapitulatif de toutes les décisions non inventables :

| ID | Section | Sujet | Obligatoire avant |
|---|---|---|---|
| DECISION_A | §1 | Validation formelle de ce draft | toute implémentation |
| DECISION_B | §9 | Modèle d'exécution du caller | création du fichier caller |
| DECISION_C | §10 | Autorité et mécanisme d'activation | création du fichier caller |
| DECISION_D | §11 | Mécanisme précis d'autorisation KX108 | intégration KX108 |
| DECISION_E | §12 | Source de configuration (valeurs numériques) | création de `HeartbeatConfig` de production |
| DECISION_F | §16 | Canal de notification de faute vers opérateur / KX108 | implémentation de la politique de faute |
| DECISION_G | §19 | Statut du reclaim réel dans V17 | toute référence à `execute_reclaim` |
| DECISION_H | §13.1 | Valeur de `HEARTBEAT_INTERVAL_SECONDS` | `HeartbeatConfig` de production |
| DECISION_I | §13.2 | Valeur de `MAX_V2_FUTURE_CLOCK_SKEW_SECONDS` | `HeartbeatConfig` de production si classify/reclaim V2 concernés |
| DECISION_J | §13.3 | Valeur de `HUMAN_APPROVED_CORRECTED_GF_R01_SHA256` | `HeartbeatConfig` de production si reclaim concerné |

---

## 25. Relation éventuelle avec PART_C

```
HUMAN_DECISION_REQUIRED — DECISION_G (voir §19)

Si DECISION_G retient l'option B (reclaim reporté à PART_C), alors :
- V17 PART_C aurait pour périmètre minimal l'implémentation de PART_B..H
  de SECTION_14 (execute_reclaim avec mutation réelle du lock orphelin).
- Cela impliquerait de modifier heartbeat_lock_manager.py (PART_A), ce qui
  requiert un plan de vérification séparé et une approbation humaine dédiée.
- Les sous-étapes PART_B..H de SECTION_14 sont déjà nommées dans le code
  (docstring de execute_reclaim, l. 669) mais non implémentées.

Si DECISION_G retient l'option A (reclaim définitivement interdit dans V17),
alors PART_C n'est pas nécessaire dans le cadre de V17.

Aucune autre mention de PART_C n'a été retrouvée dans les sources consultées.
```

---

## Annexe A — Sources primaires

| Source | Chemin | Commit |
|---|---|---|
| `SOURCE_PART_A_CODE` | `periphery/session_lock/heartbeat_lock_manager.py` | `69b8985` |
| `SOURCE_PART_A_CODE` | `periphery/session_lock/__init__.py` | `69b8985` |
| `SOURCE_PART_A_TEST` | `periphery/tests/test_heartbeat_lock_manager.py` | `69b8985` |

Aucun autre document de spécification V17 PART_B n'a été retrouvé.
Verdict de l'audit préalable : `V17_PART_B_SPEC_NOT_FOUND` (2026-07-26).

---

## Annexe B — Marqueurs utilisés

| Marqueur | Signification |
|---|---|
| `SOURCE_PART_A_CODE` | Fait extrait directement du code committé `69b8985` |
| `SOURCE_PART_A_TEST` | Fait extrait des tests committé `69b8985` |
| `INFERENCE_FOR_REVIEW` | Inférence logique soumise à validation humaine |
| `HUMAN_DECISION_REQUIRED` | Décision non inventable, ne peut être résolue unilatéralement |

---

*Fin du document V17_PART_B_REV01_DRAFT — STATUS: DRAFT_NOT_APPROVED*
