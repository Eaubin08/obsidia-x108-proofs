# TERMINAL_SESSION_ADAPTER_V0 — Internal Session Adapter

```
STATUS: APPROVED_AND_CLOSED
CANONICAL_NAME: TERMINAL_SESSION_ADAPTER_V0
SCOPE: INTERNAL_ADAPTER_ONLY
PUBLIC_COMMANDS: NONE
REAL_EXECUTION: FORBIDDEN
OBSIDURE_WIRING: FORBIDDEN
KX108_INTEGRATION: DEFERRED
RECLAIM: FORBIDDEN
```

```
DATE_APPROVED:        2026-07-28
APPROVAL:             Opérateur humain — mandat TERMINAL_SESSION_ADAPTER_V0_SPEC_AUTHORING
BASE_SHA:             b2011885bd7f9b52ce486983034f5046f2e56ea6
BASE_BRANCH:          feat/v17-part-b-rev01-synchronous-caller
PREDECESSOR:          docs/paliers/V17_PART_B_REV01_APPROVED.md
SPEC_BRANCH:          docs/terminal-session-adapter-v0-spec
```

> **Ce document est la spécification normative approuvée de TERMINAL_SESSION_ADAPTER_V0.**
> Il définit un adaptateur interne testé uniquement, sans commande publique,
> sans exécution réelle, sans câblage Obsidure ou Brody, et sans intégration KX108.
> Toutes les décisions ont été approuvées par l'opérateur humain dans le mandat
> `TERMINAL_SESSION_ADAPTER_V0_SPEC_AUTHORING` (2026-07-28).

---

## HUMAN_DECISIONS_APPROVED

> Section normative. Les décisions ci-dessous constituent la clôture formelle
> de la spécification TERMINAL_SESSION_ADAPTER_V0.

### DECISION_SCOPE — INTERNAL_ADAPTER_ONLY

L'adaptateur est interne au dépôt, dans `periphery/session_lock/`. Il ne constitue
pas une commande publique, pas un service, pas un daemon, pas une API réseau.
Son seul rôle est de fournir deux opérations testables isolément :
`inspect_lock` et `simulate_bounded_session`.

Il ne remplace pas `SynchronousHeartbeatCaller` ni `HeartbeatLockManager` :
il les orchestre dans un périmètre borné et injecté.

### DECISION_CLI — PUBLIC_COMMANDS_NONE

Aucune commande publique n'est créée dans ce palier.

`scripts/obsidia_cli.py` : **inchangé**.
`scripts/obsidia.ps1` : **inchangé**.

Aucune entrée dans le registre YAML du terminal.
Aucune aide, aucun trigger, aucun routage vers l'adaptateur.
Le câblage terminal est reporté à un palier ultérieur distinct.

### DECISION_LOCK_PATH — INJECTED_EXPLICIT_NO_PRODUCTION_PATH

Le `lock_path` est toujours injecté explicitement par l'appelant.
Aucune valeur par défaut dans le module.
Aucun chemin codé en dur dans le profil utilisateur, le répertoire de travail
ou le dépôt git.

Dans les tests : `tmp_path` (fixture pytest) uniquement.
En production : aucun chemin décidé dans ce palier.

### DECISION_SESSION_ID — INJECTED_EXPLICIT_NO_AUTO_GENERATION

Le `session_id` est toujours injecté explicitement par l'appelant.
Aucun UUID automatique, aucun timestamp, aucune génération dans le module.

Dans les tests : valeurs déterministes `TEST_SESSION_*` uniquement.
Format de production : reporté à un palier ultérieur.

### DECISION_H_V0 — FIXTURE_ONLY_NOT_PRODUCTION

`heartbeat_interval_seconds = 1.0`

Cette valeur est utilisée **uniquement dans les tests** de ce palier.
Elle est marquée : `TEST_FIXTURE_ONLY_NOT_PRODUCTION`

Elle ne constitue pas une valeur de production.
Elle ne devient pas un défaut du code de production.
La valeur de production reste : **PRODUCTION_VALUE_UNRESOLVED** (hérité de DECISION_H).

H est nécessaire au gate général (`_gate()` dans `HeartbeatLockManager`).
Sans H, toutes les opérations gated retournent `HEARTBEAT_CONFIG_MISSING`.

### DECISION_I_V0 — NOT_REQUIRED_OUTSIDE_RECLAIM

`max_v2_future_clock_skew_seconds = None`

I n'est pas requis pour le parcours nominal de ce palier.
I n'est pas vérifié par `_gate()`.
I n'intervient que dans `classify_lock()` (si `heartbeat_at > now`)
et `prepare_reclaim_proposal()`.

`classify_lock()` et `prepare_reclaim_proposal()` sont **hors périmètre**
de TERMINAL_SESSION_ADAPTER_V0 (voir DECISION_FORBIDDEN_METHODS).

La valeur de production reste : **PRODUCTION_VALUE_UNRESOLVED** (hérité de DECISION_I).

### DECISION_J_V0 — NOT_REQUIRED_OUTSIDE_RECLAIM

`human_approved_corrected_gf_r01_sha256 = None`

J n'est pas requis pour ce palier.
J n'intervient que dans `prepare_reclaim_proposal()`.
Le reclaim est explicitement interdit (voir DECISION_RECLAIM_FORBIDDEN).

La valeur reste : **HUMAN_HASH_UNRESOLVED** (hérité de DECISION_J).

### DECISION_KX108_V0 — DEFERRED_NO_STUB

Aucune intégration KX108 dans ce palier.
Aucun faux verdict KX108 simulé.
Aucune autorité d'action prétendue.
Aucun import de `kernel/`.

Le résultat de l'adaptateur porte les champs documentaires suivants,
qui ne constituent aucune décision KX108 réelle :

```
authority:             NONE
sovereign:             false
decision_authority:    KX108_ONLY
kx108_decision_present: false
simulated:             true
isolated:              true
wired:                 false
mutation_scope:        TEMP_LOCK_ONLY
```

Ces champs sont documentaires. `decision_authority: KX108_ONLY` indique que
toute autorité réelle est reportée à KX108 — il ne prétend pas satisfaire cet
invariant dans ce palier.

### DECISION_RECLAIM_FORBIDDEN

Le reclaim est interdit dans ce palier. Sans exception ni cas particulier.

L'adaptateur ne doit jamais appeler :
- `execute_reclaim()`
- `prepare_reclaim_proposal()`
- `classify_lock()`

Ces trois méthodes sont **hors périmètre de TERMINAL_SESSION_ADAPTER_V0**.

`REAL_RECLAIM_EXECUTION_AUTHORIZED = False` (hérité de DECISION_G, PART_B_REV01)
reste maintenu sans modification.

Aucune description de chemin de reclaim ne doit apparaître dans le code
ou les tests de ce palier, même à titre de commentaire ou de cas futur.

### DECISION_RECEIPT_V0 — MEMORY_ONLY_NO_JSONL

Le résultat de l'adaptateur est un objet structuré retourné en mémoire uniquement.
Aucune écriture JSONL supplémentaire dans `.local_obsidia/receipts/`.
Aucune persistance sur disque hors du `lock_path` injecté dans `tmp_path`.

Le receipt de session persistant est reporté à un palier ultérieur.

### DECISION_OBSIDURE_BRODY_FORBIDDEN

Obsidure et Brody sont **hors périmètre** de ce palier.
Aucun import, aucun appel, aucun câblage.

---

## EXPLICITLY_NOT_AUTHORIZED

```
HORS PERIMETRE — TERMINAL_SESSION_ADAPTER_V0

- toute commande publique dans le terminal (obsidia_cli.py, obsidia.ps1)
- exécution réelle sur le repo de production
- câblage Obsidure ou Brody
- intégration KX108 réelle ou simulée
- reclaim de toute nature (classify, propose, execute)
- écriture JSONL de receipt persistant
- génération automatique de session_id (UUID, timestamp)
- chemin de lock codé en dur ou dérivé automatiquement
- valeur de production pour H, I ou J
- thread, asyncio, daemon, subprocess, scheduler
- réseau, HTTP, socket
- import de apps/, scripts/, sigma/, kernel/, Lean
- modification de heartbeat_lock_manager.py, heartbeat_caller.py, __init__.py
- modification de test_heartbeat_lock_manager.py, test_heartbeat_caller.py
- modification de obsidia_cli.py, obsidia.ps1, obsidia_registry.yaml
- appel à classify_lock()
- appel à prepare_reclaim_proposal()
- appel à execute_reclaim()
```

---

## 1. Identité du palier

| Champ | Valeur |
|---|---|
| Nom canonique | `TERMINAL_SESSION_ADAPTER_V0` |
| Périmètre | Adaptateur interne, tests uniquement |
| Palier précédent | `V17_PART_B_REV01` (APPROVED_AND_CLOSED, SHA `b2011885`) |
| Palier suivant | Non décidé — câblage terminal différé |
| Statut | **APPROVED_AND_CLOSED** |
| Branche de base | `feat/v17-part-b-rev01-synchronous-caller` |
| SHA de base | `b2011885bd7f9b52ce486983034f5046f2e56ea6` |

---

## 2. Architecture future

```
TerminalSessionAdapter
├── inspect_lock(lock_path)
└── simulate_bounded_session(
      lock_path,
      session_id,
      heartbeat_config,
      max_steps,
      control_request
    )
       └── HeartbeatLockManager
                └── SynchronousHeartbeatCaller
```

L'adaptateur n'est pas un sous-classement ni une extension des classes PART_B.
C'est une couche d'orchestration fine qui instancie et pilote les composants
existants à partir de paramètres injectés explicitement.

---

## 3. Fichiers canoniques

```
periphery/
  session_lock/
    heartbeat_lock_manager.py         ← PART_A — NE PAS TOUCHER
    heartbeat_caller.py               ← PART_B_REV01 — NE PAS TOUCHER
    __init__.py                       ← PART_A — NE PAS TOUCHER
    terminal_session_adapter.py       ← V0 — NOUVEAU (implémentation future)

  tests/
    test_heartbeat_lock_manager.py    ← PART_A — NE PAS TOUCHER
    test_heartbeat_caller.py          ← PART_B_REV01 — NE PAS TOUCHER
    test_terminal_session_adapter.py  ← V0 — NOUVEAU (tests futurs)

docs/
  paliers/
    V17_PART_B_REV01_APPROVED.md     ← PART_B_REV01 — NE PAS TOUCHER
    TERMINAL_SESSION_ADAPTER_V0_APPROVED.md  ← ce document
```

Aucun fichier hors de ce périmètre ne doit être créé ou modifié.

---

## 4. Spécification de `inspect_lock`

```python
def inspect_lock(lock_path: os.PathLike) -> dict:
```

**Contrat :**
- Lecture seule du fichier JSON désigné par `lock_path`.
- `lock_path` injecté explicitement — aucune valeur par défaut.
- Retourne un dictionnaire structuré contenant les champs présents dans le JSON.
- Si le fichier est absent : retourne un dict avec `present: false`.
- Si le fichier est invalide (JSON malformé ou incomplet) : retourne un dict avec
  `valid: false` et `error: <description bornée>`.
- Aucune instanciation de `HeartbeatLockManager`.
- Aucune instanciation de `SynchronousHeartbeatCaller`.
- Aucun appel à `classify_lock()`.
- Aucune suppression, aucun repair, aucune modification du fichier.
- Aucune écriture sur disque.

**Champs attendus dans le résultat :**

```
present:        bool
valid:          bool (False si absent ou malformé)
session_id:     str | None
lock_version:   str | None
created_at:     float | None
heartbeat_at:   float | None
error:          str | None
authority:      NONE
sovereign:      false
decision_authority: KX108_ONLY
kx108_decision_present: false
simulated:      false
isolated:       true
wired:          false
mutation_scope: NONE
```

---

## 5. Spécification de `simulate_bounded_session`

```python
def simulate_bounded_session(
    *,
    lock_path: os.PathLike,
    session_id: str,
    heartbeat_config: HeartbeatConfig,
    max_steps: int,
    control_request: Optional[ControlRequest] = None,
) -> SimulationResult:
```

**Contrat :**
- Tous les paramètres sont obligatoires et injectés explicitement.
- `lock_path` doit désigner un fichier absent au départ (tmp_path dans les tests).
- `heartbeat_config` doit avoir `enabled=True` et `heartbeat_interval_seconds` non None.
- Si `enabled=False` ou `heartbeat_interval_seconds is None` : fail-closed immédiat,
  aucune opération sur le lock.
- Instancie `HeartbeatLockManager` et `SynchronousHeartbeatCaller` en interne.
- Appelle `run_bounded(max_steps, control_request)`.
- Retourne un `SimulationResult` structuré (objet en mémoire — aucune écriture JSONL).
- Aucun moteur de code réel.
- Aucune mutation du repo hors du `lock_path` temporaire injecté.

**Invariants absolus :**
- Aucun thread, asyncio, daemon, scheduler.
- Aucun subprocess, réseau, socket.
- Aucun appel à `classify_lock()`, `prepare_reclaim_proposal()`, `execute_reclaim()`.
- Aucun import de `apps/`, `scripts/`, `sigma/`, `kernel/`.
- Aucune écriture hors du `lock_path` injecté.
- `mutation_scope: TEMP_LOCK_ONLY` — seul le `lock_path` temporaire est muté.

**Champs attendus dans `SimulationResult` :**

```
ok:                  bool
sequence_ok:         bool | None
cleanup_ok:          bool | None
first_failure:       str | None
steps_executed:      int
phase:               str
terminated:          bool
released:            bool
detail:              str
authority:           NONE
sovereign:           false
decision_authority:  KX108_ONLY
kx108_decision_present: false
simulated:           true
isolated:            true
wired:               false
mutation_scope:      TEMP_LOCK_ONLY
```

---

## 6. Configuration de test canonique

Uniquement dans les tests `test_terminal_session_adapter.py` :

```python
TEST_HEARTBEAT_CONFIG = HeartbeatConfig(
    enabled=True,
    heartbeat_interval_seconds=1.0,  # TEST_FIXTURE_ONLY_NOT_PRODUCTION
    max_v2_future_clock_skew_seconds=None,   # non requis hors reclaim
    human_approved_corrected_gf_r01_sha256=None,  # non requis hors reclaim
)
```

La valeur `1.0` est marquée `TEST_FIXTURE_ONLY_NOT_PRODUCTION`.
Elle ne devient pas un défaut du code de production.

Rappel des contraintes héritées :
- H est nécessaire au gate général — requis pour tout parcours nominal.
- I n'est pas requis pour le parcours nominal — `None` est conforme.
- J n'est pas requis — `None` est conforme, reclaim interdit.
- Aucun parcours de reclaim ne peut être invoqué depuis cet adaptateur.

---

## 7. Plan de tests normatif

Les tests futurs doivent couvrir au minimum les 22 scénarios suivants.
Tous les paramètres numériques sont des fixtures locales marquées
`TEST_FIXTURE_ONLY_NOT_PRODUCTION`.

| # | Scénario | Méthode concernée | Critère |
|---|---|---|---|
| 1 | Construction sans effet de bord | `TerminalSessionAdapter()` | Aucun IO, aucun lock créé |
| 2 | `inspect_lock` — chemin absent | `inspect_lock` | `present: false`, aucune exception |
| 3 | `inspect_lock` — JSON valide | `inspect_lock` | Champs retournés exacts, fichier non modifié |
| 4 | `inspect_lock` — JSON invalide | `inspect_lock` | `valid: false`, erreur bornée, fichier non modifié |
| 5 | `inspect_lock` ne modifie rien | `inspect_lock` | Bytes du fichier identiques avant/après |
| 6 | Simulation `enabled=False` fail-closed | `simulate_bounded_session` | `ok: false`, aucun lock créé |
| 7 | Configuration incomplète fail-closed | `simulate_bounded_session` | `enabled=True` + `interval=None` → `ok: false`, aucun lock |
| 8 | Simulation nominale | `simulate_bounded_session` | `sequence_ok: true`, `cleanup_ok: true`, lock absent en fin |
| 9 | Simulation avec `control_request=STOP` | `simulate_bounded_session` | Terminaison avant `max_steps`, `sequence_ok: true` |
| 10 | Simulation avec `control_request=ABORT` | `simulate_bounded_session` | Terminaison propre, `sequence_ok: true` |
| 11 | Lock existant refusé | `simulate_bounded_session` | Fichier pré-existant → `ok: false`, `sequence_ok: false`, lock non écrasé |
| 12 | Bootstrap échoué — aucun tick | `simulate_bounded_session` | `steps_executed: 0`, aucun tick appelé |
| 13 | Tick échoué — première erreur conservée | `simulate_bounded_session` | `first_failure` renseigné, `sequence_ok: false` |
| 14 | Release réussi | `simulate_bounded_session` | `cleanup_ok: true`, `released: true`, lock absent |
| 15 | Release échoué | `simulate_bounded_session` | `cleanup_ok: false`, pas de double release |
| 16 | Aucune mutation hors `tmp_path` | Les deux | Vérification de l'arborescence avant/après |
| 17 | Aucun appel à `classify_lock`, `prepare_reclaim_proposal`, `execute_reclaim` | Les deux | Vérification statique de l'AST du module |
| 18 | Aucun import interdit | `terminal_session_adapter.py` | Vérification statique : zéro import de `apps/`, `scripts/`, `sigma/`, `kernel/`, `obsidia_cli`, Obsidure, Brody |
| 19 | Aucun thread, asyncio, subprocess, réseau | `terminal_session_adapter.py` | Vérification statique de l'AST |
| 20 | Déterminisme | Les deux | Mêmes entrées → résultat identique à deux appels successifs |
| 21 | Aucune mutation Git | Les deux | `git status --porcelain` identique avant/après les tests |
| 22 | PART_A et PART_B_REV01 byte-identiques | — | `git diff` ne touche que les fichiers V0 |

---

## 8. Fichiers protégés — interdiction absolue de modification

Les fichiers suivants ne doivent pas être modifiés dans ce palier :

```
periphery/session_lock/heartbeat_lock_manager.py
periphery/session_lock/heartbeat_caller.py
periphery/session_lock/__init__.py
periphery/tests/test_heartbeat_lock_manager.py
periphery/tests/test_heartbeat_caller.py
scripts/obsidia_cli.py
scripts/obsidia.ps1
scripts/obsidia_registry.yaml
```

Toute modification de ces fichiers constitue un blocage immédiat.

---

## 9. Invariants absolus

| Invariant | Valeur |
|---|---|
| Commande publique | NONE |
| Exécution réelle | FORBIDDEN |
| Câblage Obsidure | FORBIDDEN |
| Câblage Brody | FORBIDDEN |
| Intégration KX108 | DEFERRED |
| Reclaim (classify, propose, execute) | FORBIDDEN |
| Thread / asyncio / daemon | FORBIDDEN |
| Subprocess / réseau / socket | FORBIDDEN |
| Import hors periphery | FORBIDDEN |
| Écriture hors `lock_path` injecté | FORBIDDEN |
| Receipt JSONL supplémentaire | FORBIDDEN |
| Valeur de production pour H/I/J | FORBIDDEN |
| `lock_path` codé en dur | FORBIDDEN |
| `session_id` généré automatiquement | FORBIDDEN |
| `REAL_RECLAIM_EXECUTION_AUTHORIZED` | `False` — invariant hérité, immuable |
| `mutation_scope` | `TEMP_LOCK_ONLY` (simulate) ou `NONE` (inspect) |

---

## 10. Relation avec PART_B_REV01

TERMINAL_SESSION_ADAPTER_V0 s'appuie sur PART_B_REV01 sans le modifier.

Les fichiers `heartbeat_caller.py` et `heartbeat_lock_manager.py` (SHA de base
`b2011885`) sont la seule source de vérité pour le comportement du caller et du manager.

La présente spécification ne modifie aucune décision de PART_B_REV01.
Elle n'ouvre pas et ne ferme pas les items `PARTIAL_OPEN` de PART_B :
- le reclaim réel reste `FORBIDDEN` ;
- GF-R01 reste non résolu ;
- les décisions H, I, J de production restent `UNRESOLVED`.

---

## 11. Ce que ce palier ne clôt pas

```
CONFIRMED_OPEN_AFTER_V0

- câblage terminal (commande publique : palier ultérieur)
- exécution réelle sur le repo de production
- intégration KX108
- reclaim (FORBIDDEN — hérité de DECISION_G PART_B_REV01)
- GF-R01 hash (HUMAN_HASH_UNRESOLVED — hérité de DECISION_J)
- valeurs de production H/I/J (PRODUCTION_VALUE_UNRESOLVED)
- session_id format de production (reporté)
- lock_path de production (reporté)
- receipt de session persistant (reporté)
- câblage Obsidure (FORBIDDEN dans ce palier)
- câblage Brody (FORBIDDEN dans ce palier)
```

---

## 12. Critères de sortie du palier

- [x] Spécification normative créée et approuvée.
- [ ] `periphery/session_lock/terminal_session_adapter.py` créé et conforme à §3–§5.
- [ ] `periphery/tests/test_terminal_session_adapter.py` créé avec les 22 scénarios passants.
- [ ] PART_A et PART_B_REV01 byte-identiques (SHA `b2011885` inchangé dans les fichiers protégés).
- [ ] `git diff` ne touche que les deux nouveaux fichiers et ce document.
- [ ] Aucun import interdit dans `terminal_session_adapter.py`.
- [ ] Aucun appel à `classify_lock`, `prepare_reclaim_proposal` ou `execute_reclaim`.
- [ ] Aucune valeur de production inventée pour H/I/J.
- [ ] `TEST_FIXTURE_ONLY_NOT_PRODUCTION` présent sur la valeur `1.0`.
- [ ] `TEMP_LOCK_ONLY` présent dans les résultats de `simulate_bounded_session`.

---

*Fin du document TERMINAL_SESSION_ADAPTER_V0_APPROVED — STATUS: APPROVED_AND_CLOSED*
