# V17 PART_B — Heartbeat Caller & Activation

```
REVISION:                   PART_B_REV01
PALIER:                     PALIER_PROPOSAL_GUARD_RECLAIM_FIX_V17 PART_B
CALLER_SUBSCOPE_STATUS:     APPROVED_AND_CLOSED
TOTAL_PART_B_STATUS:        PARTIAL_OPEN
APPROVED_SCOPE:             HEARTBEAT_CALLER_AND_BOUNDED_ACTIVATION_ONLY
NOT_CLOSED_BY_THIS_REVISION:
  - real stale lock reclaim execution
  - SECTION_14 mutation steps PART_B through PART_H
  - GF-R01 corrected artifact approval
  - HUMAN_APPROVED_CORRECTED_GF_R01_SHA256
  - production activation
  - terminal/runtime wiring
  - KX108 integration
  - historical sections 15 through 22 provenance
  - PART_B_REV02 versus PART_C allocation
DATE_DRAFT:      2026-07-27
DATE_APPROVED:   2026-07-27
SCOPE_NORMALIZED: 2026-07-27
AUTHOR_DRAFT:    draft inféré — aucune approbation humaine
APPROVAL:        Opérateur humain — mandat V17_PART_B_REV01_HUMAN_APPROVAL
BASE_SHA:        69b8985ab21eb678ab7ed507e67c5c41e3441eaa (feat/v17-part-a-session-lock)
PREDECESSOR:     docs/paliers/V17_PART_B_REV01_DRAFT.md (commit 92b2315)
```

> **Ce document est la spécification normative approuvée du sous-périmètre caller de V17 PART_B_REV01.**
> Il remplace le draft `V17_PART_B_REV01_DRAFT.md` (commit `92b2315`).
> Les décisions DECISION_A à DECISION_J ont été approuvées par l'opérateur humain.
> La fermeture porte uniquement sur le sous-périmètre caller (heartbeat caller & bounded activation).
> Le sous-périmètre caller de PART_B_REV01 est fermé ; la totalité de PART_B reste `PARTIAL_OPEN`.
> Les éléments marqués `INFERENCE_FOR_REVIEW` dans le draft et compatibles avec les
> décisions approuvées sont promus `APPROVED_INFERENCE`. Les décisions H, I, J
> restent non résolues pour les valeurs de production.

---

## HUMAN_DECISIONS_APPROVED

> Section normative. Les décisions ci-dessous ont été explicitement approuvées
> par l'opérateur humain dans le mandat `V17_PART_B_REV01_HUMAN_APPROVAL`.
> Elles constituent la clôture formelle du sous-périmètre caller de PART_B_REV01.

### DECISION_A — APPROVED_WITH_BOUNDED_CORRECTIONS

Le draft est approuvé comme base normative après intégration des décisions B–J.
Statut final : `APPROVED_AND_CLOSED`. Périmètre : implémentation minimale isolée uniquement.

### DECISION_B — SYNCHRONOUS_EXPLICIT_POLLING

Le caller PART_B utilisera une boucle synchrone, explicitement pilotée par son
appelant, sans thread, sans processus externe, sans daemon, sans asyncio, sans
ordonnanceur, sans Celery ni APScheduler ni mécanisme équivalent.

Ce choix est borné à PART_B_REV01. Un modèle différent pourra faire l'objet
d'un nouveau palier distinct si nécessaire.

### DECISION_C — DIRECT_EXPLICIT_CONFIG_INJECTION

La configuration sera fournie directement au caller par injection explicite d'un
objet `HeartbeatConfig`. Règles :
- `enabled=False` reste le défaut absolu ;
- aucune activation implicite ;
- aucune lecture automatique de variables d'environnement ;
- aucun fichier de configuration ;
- aucun secret manager ;
- aucun wiring terminal ou runtime ;
- aucun composant extérieur ne peut activer automatiquement le manager.

Dans les tests futurs et le harness borné, `enabled=True` peut être injecté
**explicitement** par le code appelant. Cela ne constitue pas une autorisation
d'activation réelle en production.

### DECISION_D — KX108_INTEGRATION_DEFERRED

Le mécanisme concret d'autorisation KX108 est reporté à un palier ultérieur.
Pour PART_B_REV01 :
- aucun import de `kernel/` ;
- aucun caller KX108 ;
- aucun faux stub prétendant représenter une autorisation KX108 réelle ;
- aucun bypass de KX108 ;
- aucune action externe ou irréversible n'est réalisée.

PART_B_REV01 est un composant isolé non activé dans le runtime. Il ne prétend
pas satisfaire à lui seul l'invariant `DECISION_AUTHORITY=KX108_ONLY`.

### DECISION_E — CONFIG_INJECTION_ONLY

La seule source de configuration autorisée dans PART_B_REV01 est l'injection
directe de l'objet `HeartbeatConfig`. Toute autre source est hors périmètre.

### DECISION_F — STRUCTURED_RESULTS_ONLY

Aucun canal externe de notification n'est ajouté dans PART_B_REV01.
Les fautes et transitions sont observables uniquement par :
- les `OperationResult` retournés par chaque méthode ;
- les états publics déjà exposés par PART_A (`runtime_state`, `runtime_fault`, etc.).

Aucun callback, logger externe, webhook, bus d'événements, terminal, Sigma ou
canal KX108 n'est câblé dans cette révision.

### DECISION_G — REAL_RECLAIM_FORBIDDEN_IN_V17

Le reclaim réel reste interdit pendant tout V17. L'invariant :

```
REAL_RECLAIM_EXECUTION_AUTHORIZED = False
```

est maintenu. PART_B ne modifie pas PART_A, ne modifie pas cette constante,
n'enveloppe pas `execute_reclaim()`, et n'effectue aucune suppression équivalente.
Toute autorisation future du reclaim nécessitera un nouveau palier distinct,
une nouvelle spécification et une nouvelle approbation humaine.

### DECISION_H — PRODUCTION_VALUE_UNRESOLVED

Aucune valeur de production n'est approuvée pour `HEARTBEAT_INTERVAL_SECONDS`.
Les tests peuvent utiliser des fixtures injectées et explicitement marquées non
normatives. Aucune fixture ne devient un défaut du code de production.

### DECISION_I — PRODUCTION_VALUE_UNRESOLVED

Aucune valeur de production n'est approuvée pour
`MAX_V2_FUTURE_CLOCK_SKEW_SECONDS`. Ce paramètre reste `None` hors tests bornés.

### DECISION_J — HUMAN_HASH_UNRESOLVED

Aucune empreinte n'est approuvée pour `HUMAN_APPROVED_CORRECTED_GF_R01_SHA256`.
Aucun hash ne doit être inventé, calculé automatiquement ou présumé approuvé.
Le reclaim réel étant interdit (DECISION_G), cette absence ne bloque pas PART_B.

---

## APPROVED_IMPLEMENTATION_PROFILE

> Profil de référence normatif pour la future implémentation de PART_B_REV01.
> Toute déviation requiert un nouveau mandat humain.

```
V17_PART_B_MINIMAL_SAFE_IMPLEMENTATION

- caller isolé dans periphery/session_lock/
- polling synchrone explicite (DECISION_B: SYNCHRONOUS_EXPLICIT_POLLING)
- configuration injectée directement (DECISION_C/E: CONFIG_INJECTION_ONLY)
- disabled by default (enabled=False invariant PART_A)
- aucune activation réelle
- aucun thread, processus, daemon ou scheduler
- aucun wiring terminal ou runtime
- aucune intégration KX108 (DECISION_D: KX108_INTEGRATION_DEFERRED)
- aucun import de apps/, scripts/, sigma/, kernel/ ou Lean
- structured results only (DECISION_F: STRUCTURED_RESULTS_ONLY)
- reclaim réel interdit (DECISION_G: REAL_RECLAIM_FORBIDDEN_IN_V17)
- fixtures locales explicitement marquées non normatives dans les tests
- aucune valeur de production inventée (DECISION_H/I/J: UNRESOLVED)
```

---

## EXPLICITLY_NOT_AUTHORIZED

> Les éléments suivants sont explicitement hors périmètre de PART_B_REV01.
> Toute tentative d'implémentation est un blocage immédiat.

```
HORS PERIMETRE — PART_B_REV01

- activation réelle en production
- wiring runtime (apps/, scripts/)
- wiring terminal
- wiring ou intégration KX108
- exécution du reclaim (execute_reclaim avec succès)
- modification de PART_A (heartbeat_lock_manager.py, __init__.py, tests)
- background thread ou daemon
- scheduler ou event loop
- configuration automatique (env, fichiers, secrets)
- valeur numérique inventée pour H (HEARTBEAT_INTERVAL_SECONDS)
- valeur numérique inventée pour I (MAX_V2_FUTURE_CLOCK_SKEW_SECONDS)
- hash inventé ou calculé pour J (HUMAN_APPROVED_CORRECTED_GF_R01_SHA256)
- stub prétendant représenter une autorisation KX108 réelle
```

---

## 1. Identité du palier

| Champ | Valeur |
|---|---|
| Identifiant | `V17_PART_B` |
| Révision | `PART_B_REV01` |
| Mandat complet | `PALIER_PROPOSAL_GUARD_RECLAIM_FIX_V17 PART_B` |
| Base normative | `PART_A_REV10` (APPROVED_AND_CLOSED, SHA `69b8985`) |
| Précédent palier | V17 PART_A (APPROVED_AND_CLOSED) |
| Palier suivant | V17 PART_C (indéterminé — voir §25) |
| Statut caller REV01 | **APPROVED_AND_CLOSED** |
| Statut total PART_B | **PARTIAL_OPEN** |

---

## 2. Statut

```
CALLER_SUBSCOPE_STATUS: APPROVED_AND_CLOSED
TOTAL_PART_B_STATUS:    PARTIAL_OPEN

Ce document est la spécification normative du sous-périmètre caller de V17 PART_B_REV01.
Il ne constitue pas la clôture de toute la PART_B du palier.

Il est produit à partir de :
  - deux mentions structurantes dans le code PART_A (lignes 13 et 131 de
    periphery/session_lock/heartbeat_lock_manager.py, commit 69b8985) ;
  - l'interface publique de HeartbeatLockManager telle qu'exposée dans
    periphery/session_lock/__init__.py ;
  - les 20 tests de periphery/tests/test_heartbeat_lock_manager.py.

Les décisions DECISION_A à DECISION_J ont été approuvées par l'opérateur
humain le 2026-07-27 via le mandat V17_PART_B_REV01_HUMAN_APPROVAL.

Périmètre fermé : sous-périmètre caller uniquement (heartbeat caller & bounded activation).
Aucun document de spécification PART_B autonome antérieur n'a été retrouvé
dans le dépôt, l'historique git ou les archives locales
(audit V17_PART_B_SPEC_NOT_FOUND, 2026-07-26).
Audit de provenance : V17_PART_B_HISTORICAL_PROVENANCE_RECONCILIATION (2026-07-27) :
  verdict PROVENANCE_PARTIAL — responsabilités du reclaim et de GF-R01 restent ouvertes.
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

Les éléments suivants sont explicitement hors périmètre (voir aussi `EXPLICITLY_NOT_AUTHORIZED`) :

- Modifier `periphery/session_lock/heartbeat_lock_manager.py` (PART_A).
- Modifier `periphery/session_lock/__init__.py`.
- Modifier `periphery/tests/test_heartbeat_lock_manager.py`.
- Implémenter le reclaim réel (`execute_reclaim` reste `NOT_AUTHORIZED` — DECISION_G).
- Implémenter un wiring vers `apps/`, `scripts/`, `sigma/`, `kernel/`.
- Modifier tout fichier kernel, Lean, TLA+, CLI, Sigma, ou workflow existant.
- Fournir des valeurs par défaut aux paramètres humains H/I/J.
- Intégrer KX108 (DECISION_D : reporté).

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
| `DECISION_AUTHORITY=KX108_ONLY` | Déclaré dans docstring et `__init__.py` — mécanisme reporté (DECISION_D) |

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

Construite à partir du code source committé (`69b8985`), méthode `_gate()`
(lignes 225–238) et corps de chaque méthode publique.

### Résolution de la contradiction (rapport d'audit 2026-07-26)

**Affirmation erronée dans le rapport d'audit 2026-07-26 :**
> « l'absence d'un des trois paramètres bloque toutes les opérations »

**Réalité du code (`SOURCE_PART_A_CODE`) :**

`_gate()` vérifie uniquement :
1. `config.enabled == True` → sinon `MANAGER_DISABLED`
2. `config.heartbeat_interval_seconds is not None` → sinon `HEARTBEAT_CONFIG_MISSING`

`max_v2_future_clock_skew_seconds` et `human_approved_corrected_gf_r01_sha256`
ne sont pas vérifiés par `_gate()`. Ils bloquent uniquement les chemins
spécifiques documentés ci-dessous.

### Table par méthode

| Méthode | `enabled` requis | `interval` requis | `skew` requis | `gf_r01` requis | Lecture seule | Fichier muté | États runtime admis | Fail-closed possible | Autorisée PART_A | Rôle caller PART_B |
|---|---|---|---|---|---|---|---|---|---|---|
| `acquire_session_lock()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ❌ | lock JSON (création) | `NOT_STARTED` seulement | Oui | ✅ | Appelée une fois au démarrage |
| `heartbeat_tick()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ❌ | lock JSON (`heartbeat_at`) | `ACTIVE_WAITING`, `CONTROL_PENDING` | Oui | ✅ | Appelée en boucle |
| `request_control()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ✅ | aucun | tout état après `_gate` | Oui | ✅ | Injectée par l'appelant |
| `consume_control()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ✅ | aucun | `ACTIVE_WAITING`, `CONTROL_PENDING` | Oui | ✅ | Après handoff `CONSUME_CONTROL` |
| `commit_termination()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ✅ | aucun | `STOPPING`, `ABORTING` | Oui | ✅ | Après `consume_control()` |
| `classify_lock()` | ✅ via `_gate` | ✅ via `_gate` | ⚠️ si `heartbeat_at > now` | ❌ | ✅ | aucun | tout état après `_gate` | Oui (`UNCLASSIFIABLE_FAIL_CLOSED`) | ✅ | Optionnelle — diagnostic |
| `release_session()` | ✅ via `_gate` | ✅ via `_gate` | ❌ | ❌ | ❌ | lock JSON (suppression) | `ACTIVE_WAITING`, `CONTROL_PENDING`, `STOPPING`, `ABORTING`, `FAULTED` | Oui | ✅ | Fin de session |
| `prepare_reclaim_proposal()` | ✅ via `_gate` | ✅ via `_gate` | ⚠️ pour lock V2 | ✅ requis | ✅ | aucun | tout état après `_gate` | Oui | ✅ (proposition) | Optionnelle — diagnostic |
| `execute_reclaim()` | ❌ bypass `_gate` | ❌ bypass `_gate` | ❌ | ❌ | ✅ | aucun | ignoré | Oui (toujours) | ❌ structurel | Toujours fail-closed |

**Note sur `execute_reclaim()` :** bypass de `_gate()` (l. 668–675). Retourne
`RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED` quels que soient arguments et config.

---

## 8. Machine d'états du caller

`SOURCE_PART_A_CODE` — déduite de l'interface `HeartbeatRuntimeState`.
Compatible avec DECISION_B (SYNCHRONOUS_EXPLICIT_POLLING).

```
[INIT]
  └─► acquire_session_lock()
        ├─ ok → ACTIVE_WAITING
        └─ fail → [HALT — fail-closed]

[ACTIVE_WAITING]
  └─► heartbeat_tick()
        ├─ ok, handoff == RESUME_WAIT     → attendre interval → [ACTIVE_WAITING]
        ├─ ok, handoff == CONSUME_CONTROL → [CONTROL_PENDING]
        └─ fail (faute lock)              → [FAULTED]

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

[RELEASED]       — état final nominal
[HALT]           — état final anormal (fail-closed sans acquisition)
[RELEASE_FAILED] — état final anormal (human_recovery_required)
```

Conformément à DECISION_B, `request_control()` est appelée par l'appelant
synchrone depuis le même fil (ex. inspection d'un signal avant la boucle
ou entre deux ticks).

---

## 9. Modèle d'exécution — APPROVED

**DECISION_B : SYNCHRONOUS_EXPLICIT_POLLING**

Pseudo-code du caller approuvé :

```
acquire_session_lock()
while not done:
    result = heartbeat_tick()
    if result.ok and result.payload["handoff_action"] == "CONSUME_CONTROL":
        consume_control()
        commit_termination()
        done = True
    elif result.ok:
        # RESUME_WAIT — attendre interval (DECISION_H non résolue en prod)
        wait(interval)
    else:
        # faute — résultat structuré propagé (DECISION_F)
        done = True
release_session()
```

Règles impératives (DECISION_B) :
- aucun `threading.Thread` ;
- aucun `asyncio` ;
- aucun processus ou daemon ;
- aucun ordonnanceur.

---

## 10. Politique d'activation — APPROVED

**DECISION_C : DIRECT_EXPLICIT_CONFIG_INJECTION**

```python
# Seul mécanisme autorisé en PART_B_REV01 :
config = HeartbeatConfig(
    enabled=True,                        # injection explicite uniquement
    heartbeat_interval_seconds=<fixture>, # DECISION_H non résolue en prod
)
mgr = HeartbeatLockManager(config, lock_path, session_id)
```

Aucune variable d'environnement, fichier ou secret manager ne doit être lu.
Aucun composant extérieur n'active le manager.

---

## 11. Autorité KX108 — DEFERRED

**DECISION_D : KX108_INTEGRATION_DEFERRED**

`SOURCE_PART_A_CODE` — module docstring l. 25 et `__init__.py` l. 4 :
> `DECISION_AUTHORITY=KX108_ONLY`

PART_B_REV01 ne satisfait pas cet invariant de manière complète. Le mécanisme
concret est reporté. Aucun import de `kernel/`, aucun canal KX108, aucun stub
prétendant représenter une autorisation KX108 réelle.

---

## 12. Source de configuration — APPROVED

**DECISION_E : CONFIG_INJECTION_ONLY**

La seule source autorisée est l'injection directe de `HeartbeatConfig`.
Les paramètres H/I/J restent sans valeur de production (DECISION_H/I/J).

`SOURCE_PART_A_TEST`, l. 9–11 :
> « Les valeurs numériques utilisées ici (interval=10, skew=5) sont des
> FIXTURES DE TEST locales : elles n'établissent aucune valeur par défaut
> de production. »

---

## 13. Paramètres humains — statuts après approbation

### 13.1 HEARTBEAT_INTERVAL_SECONDS

| Champ | Valeur |
|---|---|
| Nom dans `HeartbeatConfig` | `heartbeat_interval_seconds: Optional[float] = None` |
| Vérifié par `_gate()` | **OUI** — son absence bloque toutes les opérations gated |
| Utilisé dans | `classify_lock()` l. 469 : `2 * interval` comme seuil de staleness |
| Code d'erreur si absent | `HEARTBEAT_CONFIG_MISSING` |
| Valeur de test (non production) | `10.0` (fixture locale — non normative) |
| Statut après DECISION_H | **PRODUCTION_VALUE_UNRESOLVED** |
| Requis pour dev isolé | Non |
| Requis pour tests | Non (fixture locale) |
| Requis pour activation réelle | **OUI** |

### 13.2 MAX_V2_FUTURE_CLOCK_SKEW_SECONDS

| Champ | Valeur |
|---|---|
| Nom dans `HeartbeatConfig` | `max_v2_future_clock_skew_seconds: Optional[float] = None` |
| Vérifié par `_gate()` | **NON** |
| Utilisé dans | `classify_lock()` l. 476 : si `heartbeat_at > now` seulement |
| Utilisé dans | `prepare_reclaim_proposal()` l. 627 : lock V2 seulement |
| Valeur de test (non production) | `5.0` (fixture locale — non normative) |
| Statut après DECISION_I | **PRODUCTION_VALUE_UNRESOLVED** — `None` hors tests |
| Requis pour dev isolé | Non |
| Requis pour activation réelle | Non si classify sur futur non attendu |

### 13.3 HUMAN_APPROVED_CORRECTED_GF_R01_SHA256

| Champ | Valeur |
|---|---|
| Nom dans `HeartbeatConfig` | `human_approved_corrected_gf_r01_sha256: Optional[str] = None` |
| Vérifié par `_gate()` | **NON** |
| Utilisé dans | `prepare_reclaim_proposal()` l. 620 |
| Code d'erreur si absent | `RECLAIM_AUTHORIZATION_INVALID` |
| Statut après DECISION_J | **HUMAN_HASH_UNRESOLVED** |
| Requis pour dev isolé | Non |
| Requis pour activation réelle | Non (reclaim interdit — DECISION_G) |

---

## 14. Mutations autorisées pour le caller PART_B

`SOURCE_PART_A_CODE` + décisions approuvées :

1. Instancier `HeartbeatLockManager` avec `HeartbeatConfig` injectée explicitement.
2. Appeler `acquire_session_lock()` une fois au démarrage.
3. Appeler `heartbeat_tick()` en boucle synchrone (DECISION_B).
4. Appeler `request_control(ControlRequest.STOP | ABORT)` en réponse à un signal synchrone.
5. Appeler `consume_control()` sur `handoff == CONSUME_CONTROL`.
6. Appeler `commit_termination()` depuis `STOPPING` ou `ABORTING`.
7. Appeler `classify_lock()` à titre de diagnostic (lecture seule).
8. Appeler `prepare_reclaim_proposal()` à titre de diagnostic (lecture seule).
9. Appeler `release_session()` en fin de vie nominale ou post-faute.
10. Créer `periphery/session_lock/heartbeat_caller.py` (nom provisoire).
11. Créer `periphery/tests/test_heartbeat_caller.py`.

---

## 15. Mutations interdites

`SOURCE_PART_A_CODE` + décisions approuvées :

1. Modifier `periphery/session_lock/heartbeat_lock_manager.py`.
2. Modifier `periphery/session_lock/__init__.py`.
3. Modifier `periphery/tests/test_heartbeat_lock_manager.py`.
4. Modifier `REAL_RECLAIM_EXECUTION_AUTHORIZED` (DECISION_G).
5. Appeler `execute_reclaim()` en attente d'un succès.
6. Importer `apps/`, `scripts/`, `sigma/`, `kernel/` depuis le caller.
7. Fournir des valeurs numériques inventées aux paramètres H/I/J.
8. Écraser un lock JSON existant (l. 253–256).
9. Supprimer le lock JSON autrement que via `release_session()`.
10. Modifier le lock JSON autrement que via `heartbeat_tick()`.
11. Lancer un thread, daemon ou ordonnanceur (DECISION_B).
12. Lire des variables d'environnement ou fichiers de configuration (DECISION_C/E).
13. Câbler un canal externe de notification (DECISION_F).
14. Stubber KX108 de manière prétendant satisfaire DECISION_AUTHORITY (DECISION_D).

---

## 16. Politique de faute — APPROVED

`SOURCE_PART_A_CODE` — `_enter_fault()` lignes 425–442 :

- Toute mismatch d'identité du lock JSON déclenche `FAULTED`.
- La première faute est préservée dans `runtime_fault`.
- Les fautes secondaires s'accumulent dans `secondary_faults`.
- `FAULTED` est un état terminal pour la boucle heartbeat.
- Depuis `FAULTED`, `release_session()` reste possible.
- Le caller doit propager la faute par retour structuré et ne pas relancer.

**DECISION_F : STRUCTURED_RESULTS_ONLY** — fautes observables via `OperationResult`
et `mgr.runtime_fault`. Aucun canal externe câblé dans PART_B_REV01.

---

## 17. Politique de terminaison

`SOURCE_PART_A_CODE` — `commit_termination()` lignes 386–423 :

Séquence nominale (polling synchrone — DECISION_B) :
1. `request_control(STOP)` depuis le fil de la boucle.
2. `heartbeat_tick()` retourne `handoff == CONSUME_CONTROL`.
3. `consume_control()` → `STOPPING`.
4. `commit_termination()`.
5. `release_session()`.

`SOURCE_PART_A_CODE` — l. 422 :
> « jamais : suppression du lock JSON, auto-reclaim, toucher au Level 3 »

---

## 18. Politique de release

`SOURCE_PART_A_CODE` — `release_session()` lignes 505–580 :

Préconditions :
- `runtime_state ∈ {ACTIVE_WAITING, CONTROL_PENDING, STOPPING, ABORTING, FAULTED}`
- `session_level3_owned == True`
- `tick_in_progress == False` et `level1_locked == level2_locked == False`

Transaction PART_B..H de SECTION_13 (implémentée dans PART_A) :
- PART_D : validation état du lock JSON (bytes exacts)
- PART_E : unlink du lock JSON avec fsync + vérification d'absence
- PART_F : libération du target handle Level 3
- PART_G (finally) : libération des locks Level 1 et Level 2
- PART_H : vérification des postconditions

Résultat final : `session_release_state = "RELEASED"`.

---

## 19. Statut du reclaim réel — APPROVED

**DECISION_G : REAL_RECLAIM_FORBIDDEN_IN_V17**

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

**`REAL_RECLAIM_EXECUTION_AUTHORIZED = False` est maintenu pour tout V17.**

**`MUST_REMAIN_FALSE_UNDER_PART_B_REV01` — cette constante ne peut être modifiée
ni contournée dans aucune implémentation issue de PART_B_REV01. Toute lève de
cette interdiction requiert un mandat humain distinct avec une nouvelle spécification.**

---

## 20. Périmètre des fichiers PART_B_REV01

`SOURCE_PART_A_CODE` + DECISION_B/C/E :

```
periphery/
  session_lock/
    heartbeat_lock_manager.py       ← PART_A — NE PAS TOUCHER
    __init__.py                     ← PART_A — NE PAS TOUCHER
    heartbeat_caller.py             ← PART_B nouveau (nom provisoire)

  tests/
    test_heartbeat_lock_manager.py  ← PART_A — NE PAS TOUCHER
    test_heartbeat_caller.py        ← PART_B nouveau

docs/
  paliers/
    V17_PART_B_REV01_APPROVED.md   ← ce document
```

Aucun `heartbeat_config_loader.py` n'est autorisé (DECISION_C/E).

---

## 21. Plan de tests approuvé

| # | Titre | Comportement attendu | Statut |
|---|---|---|---|
| T01 | Activation refusée sans config | Sans `enabled=True` + `interval`, fail-closed | Approuvé |
| T02 | Boucle nominale N ticks | N ticks → `RESUME_WAIT`, `heartbeat_at` mis à jour | Approuvé |
| T03 | STOP nominal | Séquence STOP → `RELEASED` | Approuvé |
| T04 | ABORT nominal | Séquence ABORT → `RELEASED` | Approuvé |
| T05 | Handoff `CONSUME_CONTROL` | `control_request_pending` → tick → `CONSUME_CONTROL` | Approuvé |
| T06 | Handoff `RESUME_WAIT` | Aucune requête → tick → `RESUME_WAIT` | Approuvé |
| T07 | Identité lock modifiée | Lock modifié externement → `FAULTED` | Approuvé |
| T08 | Configuration partielle | `enabled=True` sans `interval` → `HEARTBEAT_CONFIG_MISSING` | Approuvé |
| T09 | Horloge future sans skew | `heartbeat_at > now`, skew None → `UNCLASSIFIABLE_FAIL_CLOSED` | Approuvé |
| T10 | Release non quiescent | `tick_in_progress=True` → `RELEASE_HEARTBEAT_NOT_QUIESCENT` | Approuvé |
| T11 | Interruption caller | Lock intact après interruption, release réussit | Approuvé |
| T12 | Redémarrage caller | Nouvelle instance → `acquire` refuse l'écrasement | Approuvé |
| T13 | Déterminisme | Mêmes entrées → mêmes résultats | Approuvé |
| T14 | Absence de mutation hors lock | Aucun fichier tiers modifié | Approuvé |
| T15 | Reclaim réel toujours bloqué | `execute_reclaim()` → `NOT_AUTHORIZED` quels que soient les args | Approuvé |
| T16 | Absence de bypass KX108 | (différé — DECISION_D non résolue) | Différé |

Toutes les valeurs numériques dans les tests sont des fixtures locales
non normatives (DECISION_H/I : PRODUCTION_VALUE_UNRESOLVED).

---

## 22. Critères de sortie de PART_B_REV01

- [x] DECISION_A à DECISION_J inscrites dans ce document.
- [ ] `periphery/session_lock/heartbeat_caller.py` créé et conforme au profil approuvé.
- [ ] `periphery/tests/test_heartbeat_caller.py` créé avec T01–T15 passants.
- [ ] `PART_A_REV10` (commit `69b8985`) inchangé.
- [ ] `execute_reclaim()` retourne toujours `RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED`.
- [ ] Aucun import de `apps/`, `scripts/`, `sigma/`, `kernel/` dans le code PART_B.
- [ ] Aucune valeur de production inventée pour H/I/J.
- [ ] Aucun thread, daemon ou scheduler dans le caller.
- [ ] `git diff` ne touche que les fichiers du périmètre §20.

---

## 23. Conditions de HOLD/BLOCK

| Condition | Code d'erreur | Priorité |
|---|---|---|
| `enabled == False` | `MANAGER_DISABLED` | HOLD total |
| `heartbeat_interval_seconds is None` | `HEARTBEAT_CONFIG_MISSING` | HOLD total |
| `runtime_state` invalide pour l'opération | selon méthode | HOLD opération |
| `heartbeat_at > now` et `skew is None` | `UNCLASSIFIABLE_FAIL_CLOSED` | HOLD classify |
| `gf_r01 is None` (reclaim) | `RECLAIM_AUTHORIZATION_INVALID` | N/A en PART_B_REV01 |
| Lock JSON modifié extérieurement | `FAULTED` | HOLD boucle |

`SOURCE_PART_A_CODE` — docstring l. 22 :
> « toute ambiguïté produit FAIL_CLOSED + HUMAN_RECOVERY_DECISION_REQUIRED »

---

## 24. Décisions — statuts finaux

| ID | Sujet | Statut |
|---|---|---|
| DECISION_A | Validation formelle du draft | **APPROVED_WITH_BOUNDED_CORRECTIONS** |
| DECISION_B | Modèle d'exécution | **SYNCHRONOUS_EXPLICIT_POLLING** |
| DECISION_C | Autorité et mécanisme d'activation | **DIRECT_EXPLICIT_CONFIG_INJECTION** |
| DECISION_D | Mécanisme précis d'autorisation KX108 | **KX108_INTEGRATION_DEFERRED** |
| DECISION_E | Source de configuration | **CONFIG_INJECTION_ONLY** |
| DECISION_F | Canal de notification de faute | **STRUCTURED_RESULTS_ONLY** |
| DECISION_G | Statut du reclaim réel dans V17 | **REAL_RECLAIM_FORBIDDEN_IN_V17** |
| DECISION_H | Valeur de `HEARTBEAT_INTERVAL_SECONDS` | **PRODUCTION_VALUE_UNRESOLVED** |
| DECISION_I | Valeur de `MAX_V2_FUTURE_CLOCK_SKEW_SECONDS` | **PRODUCTION_VALUE_UNRESOLVED** |
| DECISION_J | Valeur de `HUMAN_APPROVED_CORRECTED_GF_R01_SHA256` | **HUMAN_HASH_UNRESOLVED** |

---

## 25. Relation éventuelle avec PART_C

DECISION_G maintient le reclaim interdit dans V17. Un palier PART_C éventuel
aurait pour périmètre minimal l'implémentation de `execute_reclaim()` avec
mutation réelle (PART_B..H de SECTION_14). Cela impliquerait de modifier
`heartbeat_lock_manager.py` (PART_A), avec une nouvelle spécification et
une nouvelle approbation humaine dédiées.

---

## 26. Scope provenance correction

PART_B_REV01 est la première tranche approuvée de V17 PART_B au sein du
`PALIER_PROPOSAL_GUARD_RECLAIM_FIX_V17`. Elle couvre uniquement le caller
heartbeat synchrone isolé défini dans le sous-périmètre
`HEARTBEAT_CALLER_AND_BOUNDED_ACTIVATION_ONLY`.

Elle ne clôt pas toute la PART_B du palier. L'audit de provenance
`V17_PART_B_HISTORICAL_PROVENANCE_RECONCILIATION` (2026-07-27) a établi :

- Les lignes 13 et 131 de `heartbeat_lock_manager.py` (commit `69b8985`) attribuent
  à PART_B une double responsabilité : (1) la boucle caller heartbeat et (2) le reclaim
  réel (SECTION_14 PART_B..H avec mutation).
- La présente révision couvre uniquement la responsabilité (1).
- La responsabilité (2) reste non autorisée et non implémentée.
- La provenance historique des sections 15–22 n'a pu être vérifiée dans aucun
  fichier versionné ou archive locale, mais la numérotation des sections dans le
  code PART_A (SECTION_12, 13, 14) est cohérente avec un plan où PART_B débute
  à la section 15.

**Aucun comportement approuvé dans REV01 ne doit être élargi par inférence.**
Toute extension du périmètre requiert un mandat humain distinct.

---

## 27. Remaining PART_B responsibilities

### CONFIRMED_OPEN

```
CONFIRMED_OPEN:

- real reclaim remains structurally forbidden
    (REAL_RECLAIM_EXECUTION_AUTHORIZED = False — MUST_REMAIN_FALSE_UNDER_PART_B_REV01)
- GF-R01 hash remains unresolved
    (DECISION_J: HUMAN_HASH_UNRESOLVED — aucun hash approuvé ou calculé)
- no mutation implementation exists for SECTION_14 PART_B..H
    (execute_reclaim() retourne toujours RECLAIM_REAL_EXECUTION_NOT_AUTHORIZED)
```

### PROVENANCE_UNRESOLVED

```
PROVENANCE_UNRESOLVED:

- exact historical content of sections 15–22
    (aucun fichier source retrouvé — non vérifiable depuis les archives disponibles)
- exact relation to sections 23–30
    (aucun fichier source retrouvé — PART_C non définie)
- whether the remaining work is PART_B_REV02 or PART_C
    (décision non prise — requiert un mandat humain distinct)
```

PART_B_REV02 et PART_C sont deux alternatives non décidées. Aucune des deux
n'est autorisée à être inférée ou commencée depuis ce document.

---

## Annexe A — Sources primaires

| Source | Chemin | Commit |
|---|---|---|
| `SOURCE_PART_A_CODE` | `periphery/session_lock/heartbeat_lock_manager.py` | `69b8985` |
| `SOURCE_PART_A_CODE` | `periphery/session_lock/__init__.py` | `69b8985` |
| `SOURCE_PART_A_TEST` | `periphery/tests/test_heartbeat_lock_manager.py` | `69b8985` |

Aucun document de spécification V17 PART_B autonome antérieur.
Audit préalable : `V17_PART_B_SPEC_NOT_FOUND` (2026-07-26).
Draft de référence : `V17_PART_B_REV01_DRAFT.md`, commit `92b2315`.
Mandat d'approbation : `V17_PART_B_REV01_HUMAN_APPROVAL` (2026-07-27).

---

## Annexe B — Marqueurs utilisés

| Marqueur | Signification |
|---|---|
| `SOURCE_PART_A_CODE` | Fait extrait directement du code committé `69b8985` |
| `SOURCE_PART_A_TEST` | Fait extrait des tests commités `69b8985` |
| `APPROVED_INFERENCE` | Inférence validée par les décisions approuvées |
| `HUMAN_DECISION_REQUIRED` | Réservé aux décisions non encore approuvées (H/I/J non résolues) |

---

*Fin du document V17_PART_B_REV01_APPROVED — CALLER_SUBSCOPE_STATUS: APPROVED_AND_CLOSED — TOTAL_PART_B_STATUS: PARTIAL_OPEN*
