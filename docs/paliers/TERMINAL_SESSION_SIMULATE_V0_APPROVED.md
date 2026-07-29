# TERMINAL_SESSION_SIMULATE_V0 — Spécification normative approuvée

```
STATUS: APPROVED_AND_CLOSED
CANONICAL_NAME: TERMINAL_SESSION_SIMULATE_V0
SCOPE: PUBLIC_BOUNDED_SESSION_SIMULATION_ONLY
PUBLIC_COMMAND: OBSIDIA_SESSION_SIMULATE
SIMULATED: TRUE
REAL_EXECUTION: FORBIDDEN
REPOSITORY_MUTATION: FORBIDDEN
TEMP_LOCK_MUTATION: ALLOWED_BOUNDED
PERSISTENT_LOCK: FORBIDDEN
OBSIDURE_WIRING: FORBIDDEN
BRODY_WIRING: FORBIDDEN
KX108_INTEGRATION: DEFERRED
RECLAIM: FORBIDDEN
```

```
SPEC_REVISION: REV01
```

---

## Contexte

Ce palier définit la première commande publique de simulation bornée de session.

Syntaxe canonique (une seule ligne — forme de référence) :

```
obsidia session simulate --lock-path "<chemin absolu>" --session-id "<identifiant>" --heartbeat-interval-seconds "<nombre>" --max-steps "<entier>" --control "<none|stop|abort>" --ack-temp-lock-mutation
```

Elle s'appuie exclusivement sur :

```
TerminalSessionAdapter.simulate_bounded_session(...)
```

Elle ne modifie aucun code métier, n'exécute aucun moteur Obsidure, n'appelle pas Brody,
ne prend aucune décision KX108, ne réalise aucun reclaim.

Branche source : `feat/terminal-session-inspect-v0`
SHA source : `6ff0b2120da3ed092adc70049ef844f798b2cfeb`

---

## Doctrine PERSISTENT_LOCK

```
PERSISTENT_LOCK: FORBIDDEN interdit toute persistance intentionnelle
ou toute session durable.

Un lock restant après un cleanup failure est un résidu d'échec,
pas une persistance autorisée.

Ce résidu :
- est signalé avec lock_exists_after=true ;
- n'est jamais supprimé par le script public ;
- n'est jamais reclaimé ;
- maintient ok=false ;
- entraîne exit 3, sauf incohérence de postcondition entraînant exit 1.
```

---

## Doctrine NO_REAL_TIME_WAITING_V0

```
NO_REAL_TIME_WAITING_V0
```

- Le caller actuel n'effectue aucun `sleep`.
- `heartbeat_interval_seconds` influence les données temporelles inscrites dans le lock JSON.
- Il ne crée pas une attente réelle entre les steps.
- `max_steps` borne le nombre d'opérations synchrones, pas la durée murale.
- V0 ne garantit aucune durée murale exacte.
- La commande ne prétend pas attendre `interval × steps` secondes.

---

## Décision A — Commande canonique

La syntaxe publique canonique unique, sur une seule ligne :

```
obsidia session simulate --lock-path "<chemin absolu>" --session-id "<identifiant>" --heartbeat-interval-seconds "<nombre>" --max-steps "<entier>" --control "<none|stop|abort>" --ack-temp-lock-mutation
```

**Toutes les options sont obligatoires.** Aucune n'a de valeur par défaut.

L'ordre canonique des options est obligatoire dans V0.

**Formes non autorisées :**

- option dupliquée
- option inconnue
- argument positionnel
- forme `--option=value`
- option abrégée
- valeur issue de l'environnement
- fichier de configuration
- découverte automatique
- session_id généré automatiquement
- lock_path généré automatiquement
- heartbeat implicite
- max_steps implicite
- control implicite
- acknowledgement implicite

---

## Décision B — Acknowledgement explicite

La présence littérale de `--ack-temp-lock-mutation` dans les arguments est obligatoire.

Elle signifie que l'humain accepte qu'un fichier de lock temporaire puisse être :

1. créé par la simulation ;
2. mis à jour par les heartbeats simulés ;
3. supprimé par le cleanup normal du caller.

Elle n'autorise pas :

- l'exécution de code métier
- la modification du dépôt
- la suppression d'un lock préexistant
- un reclaim
- l'admission d'une session réelle
- une décision KX108

En l'absence de ce marqueur, le script ne construit aucun adapter, ne crée aucun lock,
produit `INVOCATION_INVALID` et retourne le code `2`.

---

## Décision C — Lock path

`--lock-path` est obligatoire.

**Contraintes de validation — liste normative :**

- chaîne non vide, sans espace initial ou final
- chemin absolu (`is_absolute()` = True)
- la cible n'existe pas, même comme lien symbolique pendant (voir algorithme de confinement)
- le parent existe
- le parent est un répertoire
- la cible est hors du dépôt (voir algorithme de confinement)
- ni la cible ni aucun parent existant n'est un symlink ou reparse point
- aucune création de répertoire parent
- aucun chemin UNC, préfixe `\\?\` ou `\\.\`

Le script construit un objet `Path` séparé uniquement pour la validation interne.

La valeur publique `lock_path` dans le JSON conserve **exactement** la chaîne fournie.

**Interdictions :**

- chemin relatif
- chemin dans le dépôt
- cible préexistante (fichier, répertoire ou lien symbolique)
- création de parent
- remplacement d'un fichier préexistant
- suppression préalable
- réparation
- fallback vers un chemin par défaut
- suppression manuelle d'un lock préexistant

### Algorithme de confinement normatif

#### Racine du dépôt (sans appel Git, sans lecture d'environnement)

```python
SCRIPT_PATH = Path(__file__).resolve(strict=True)
REPO_ROOT = SCRIPT_PATH.parent.parent
RESOLVED_REPO_ROOT = REPO_ROOT.resolve(strict=True)
```

#### Entrée publique

1. Refuser chaîne vide.
2. Refuser espace initial ou final.
3. Refuser tout non compatible avec un chemin absolu.
4. Construire `target = Path(raw_string)`.
5. Exiger `target.is_absolute()`.

#### Restrictions Windows V0

Rejeter immédiatement si la chaîne brute :

- commence par `\\` (UNC ou préfixe étendu) ;
- contient `\\?\` ou `\\.\` ;
- contient un segment de forme `~<chiffre>` (chemin court 8.3) ;
- contient `:` après le premier caractère (alternate data stream).

#### Vérification d'existence — cible

Utiliser `os.path.lexists(target)` :

- si `lexists` retourne True, rejeter (fichier, répertoire, ou lien symbolique pendant) ;
- cette règle couvre les dangling symlinks.

#### Vérification du parent

1. Exiger que le parent existe (`parent.exists()`).
2. Exiger que le parent soit un répertoire (`parent.is_dir()`).
3. Ne jamais créer de parent.

#### Reparse points et symlinks (Windows + POSIX)

Pour chaque composant existant entre la racine de volume et le parent inclus :

1. Appeler `os.lstat(component)`.
2. Rejeter si `Path(component).is_symlink()`.
3. Sous Windows, rejeter si :
   ```python
   st_result.st_file_attributes & stat.FILE_ATTRIBUTE_REPARSE_POINT
   ```
   Cette règle couvre junctions NTFS, symlinks Windows, et autres reparse points.

L'algorithme échoue de façon fermée pour toute exception d'inspection.

#### Résolution interne

```python
RESOLVED_TARGET = target.resolve(strict=False)
```

Cette valeur sert uniquement à la comparaison de confinement.
La chaîne publique n'est jamais modifiée.

#### Comparaison avec le dépôt

Sous Windows :

```python
import os
norm_target = os.path.normcase(os.path.normpath(str(RESOLVED_TARGET)))
norm_repo   = os.path.normcase(os.path.normpath(str(RESOLVED_REPO_ROOT)))
try:
    common = os.path.commonpath([norm_target, norm_repo])
    if common == norm_repo:
        reject()  # cible dans le dépôt
except ValueError:
    pass  # lecteurs différents → hors dépôt, accepté
```

Sous POSIX :

```python
try:
    common = os.path.commonpath([str(RESOLVED_TARGET), str(RESOLVED_REPO_ROOT)])
    if common == str(RESOLVED_REPO_ROOT):
        reject()
except ValueError:
    pass
```

Aucun appel Git. Aucune lecture d'environnement. Aucun chemin par défaut.

---

## Décision D — Session ID

`--session-id` est obligatoire.

### Grammaire normative

```
SESSION_ID_GRAMMAR_V0:
^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$
```

**Conséquences normatives :**

- longueur : 1 à 128 caractères Python (`len()`) ;
- premier caractère : lettre ASCII ou chiffre ;
- caractères suivants autorisés : lettres ASCII, chiffres, `.`, `_`, `:`, `-` ;
- aucun espace interne, initial ou final ;
- aucun caractère Unicode non ASCII ;
- aucun caractère de contrôle (ni ASCII < 32, ni catégorie Unicode `Cc` ou `Cf`) ;
- aucune normalisation silencieuse ;
- la chaîne publique est préservée exactement.

```
SIMULATION_SESSION_ID_NOT_PRODUCTION
```

---

## Décision E — Heartbeat interval

`--heartbeat-interval-seconds` est obligatoire.

### Grammaire normative

```
HEARTBEAT_INTERVAL_GRAMMAR_V0:
^(?:0|[1-9][0-9]*)(?:\.[0-9]+)?$
```

### Parser futur obligatoire (séquence stricte)

1. Vérifier la regex sur la chaîne brute — aucun `strip` préalable.
2. Convertir avec `decimal.Decimal(value)`.
3. Vérifier `Decimal.is_finite()` = True.
4. Vérifier `0.01 <= valeur <= 5.0`.
5. Convertir explicitement en `float` pour `HeartbeatConfig`.

La locale système n'influence jamais le parsing.

**Valeurs acceptées (exemples) :**

```
0.01   0.1   1   1.0   5   5.0
```

**Valeurs rejetées (exemples) :**

```
.01   01   +1   -0   -1   1e-2   1E-2   1_0   0,5
NaN   Inf   Infinity   " 1"   "1 "
```

```
SIMULATION_INTERVAL_NOT_PRODUCTION
```

**Configuration construite :**

```python
HeartbeatConfig(
    enabled=True,
    heartbeat_interval_seconds=explicit_value,
    max_v2_future_clock_skew_seconds=None,
    human_approved_corrected_gf_r01_sha256=None,
)
```

**Paramètres de production non résolus :**

```
PRODUCTION_HEARTBEAT_INTERVAL: UNRESOLVED
PRODUCTION_FUTURE_CLOCK_SKEW: UNRESOLVED
PRODUCTION_GF_R01_HASH: UNRESOLVED
```

Le script ne doit jamais utiliser une valeur par défaut quand l'option est absente.

---

## Décision F — Max steps

`--max-steps` est obligatoire.

### Grammaire normative

```
MAX_STEPS_GRAMMAR_V0:
^(?:[1-9]|[1-9][0-9]|100)$
```

Cette grammaire accepte uniquement les chaînes décimales canoniques de `1` à `100`.

**Valeurs rejetées (exemples) :**

```
0   00   01   001   +1   -1   1.0   1e2   True   " 1"   "1 "   101
```

- Aucun `strip`.
- Aucune conversion silencieuse.
- Aucune valeur par défaut.
- Un échec de grammaire entraîne : aucun adapter construit, aucun lock créé,
  `INVOCATION_INVALID`, exit `2`.

```
SIMULATION_BOUNDS_V0
```

---

## Décision G — Control request

`--control` est obligatoire.

**Valeurs exactes autorisées :**

```
none   → None
stop   → ControlRequest.STOP
abort  → ControlRequest.ABORT
```

La comparaison est sensible à la casse. Aucun strip silencieux.

Non accepté : `NONE`, `STOP`, `ABORT`, `" stop "`, valeur vide, valeur inconnue, valeurs multiples.

`ControlRequest.NONE` n'existe pas dans l'énumération — la valeur `none` se mappe à `None`
(argument Python absent), conformément à la signature :

```python
simulate_bounded_session(..., control_request: Optional[ControlRequest] = None)
```

---

## Décision H — Architecture du routage

```
scripts/obsidia.ps1
└── route exacte : args[0] -ceq "session" et args[1] -ceq "simulate"
    └── python -B "$PSScriptRoot\obsidia_session_simulate_cli.py" @remainingArgs
        └── sys.dont_write_bytecode = True (avant tout import periphery)
        └── validation publique bornée
        └── confinement lock path (algorithme Décision C)
        └── construction HeartbeatConfig explicite
        └── TerminalSessionAdapter().simulate_bounded_session(...)
        └── vérification lock_exists_after (lecture seule)
        └── vérification des postconditions
        └── émission JSON déterministe stdout
        └── exit code normatif
```

**Le wrapper PowerShell :**

- reconnaît uniquement `session` puis `simulate` avec `-ceq` (sensible à la casse)
- ne normalise pas les arguments
- transmet le reste sans transformation via `@remainingArgs`
- transmet exactement le code retour Python via `exit $LASTEXITCODE`
- ne lit aucun lock
- ne construit aucune configuration
- ne lance aucun service
- n'appelle pas `obsidia_cli.py`
- n'appelle pas Brody, Obsidure ou KX108
- n'ajoute aucun texte sur stdout ou stderr

**Résolution du script Python (avec inhibition bytecode) :**

```powershell
python -B "$PSScriptRoot\obsidia_session_simulate_cli.py" @remainingArgs
exit $LASTEXITCODE
```

---

## Décision I — Imports futurs

**Imports canoniques dans le script dédié :**

```python
from __future__ import annotations

import decimal
import json
import os
import stat
import sys
sys.dont_write_bytecode = True  # avant tout import periphery

from collections.abc import Mapping
from pathlib import Path
from typing import Optional, Sequence

from periphery.session_lock.terminal_session_adapter import (
    TerminalSessionAdapter,
    TerminalSessionAdapterResult,
)

from periphery.session_lock.heartbeat_lock_manager import (
    ControlRequest,
    HeartbeatConfig,
)
```

**Règles canoniques :**

- `ControlRequest` et `HeartbeatConfig` importés directement depuis
  `periphery.session_lock.heartbeat_lock_manager` — **jamais** depuis `terminal_session_adapter` de façon transitive.
- `TerminalSessionAdapter` et `TerminalSessionAdapterResult` importés depuis `terminal_session_adapter`.
- `periphery.session_lock.__init__` exporte `HeartbeatConfig` (via heartbeat_lock_manager),
  mais **pas** `ControlRequest`. L'import direct depuis `heartbeat_lock_manager` est plus stable.
- Ne jamais importer `HeartbeatLockManager`, `SynchronousHeartbeatCaller`, `CallerResult`,
  `OperationResult` ou `BoundedSessionResult` dans le script public.
- Les imports de types n'autorisent aucun appel direct au manager.
- `sys.dont_write_bytecode = True` doit précéder tout import de `periphery`.

Cette surface est vérifiée disponible au SHA `6ff0b2120da3ed092adc70049ef844f798b2cfeb`.

---

## Décision J — Opération unique

Après validation complète, le script appelle **une seule fois** :

```python
TerminalSessionAdapter().simulate_bounded_session(
    lock_path=lock_path,
    session_id=session_id,
    heartbeat_config=heartbeat_config,
    max_steps=max_steps,
    control_request=control_request,
)
```

**Jamais d'appel direct à :**

- `HeartbeatLockManager`
- `SynchronousHeartbeatCaller`
- `acquire_session_lock`
- `heartbeat_tick`
- `request_stop`
- `request_abort`
- `consume_and_terminate`
- `release_session`
- `run_bounded`
- `classify_lock`
- `prepare_reclaim_proposal`
- `execute_reclaim`

Le script ne duplique pas la machine d'états.

---

## Décision K — Sémantique de mutation

```
TEMP_LOCK_ONLY
```

La seule mutation autorisée est limitée au chemin explicitement fourni et validé.

La simulation **peut** (via la chaîne interne) :

- créer le lock
- mettre à jour ses heartbeats
- le supprimer via le cleanup normal

Le script public ne doit jamais :

- écrire lui-même le lock
- ouvrir le lock en écriture
- supprimer lui-même le lock
- réparer le lock
- forcer le cleanup
- effectuer un cleanup compensatoire
- masquer un cleanup failure

**En cas de cleanup failure :**

- `result.ok = false`
- `cleanup_ok = false`
- le lock résiduel n'est pas supprimé par le script
- exit `3` (sauf violation de postcondition → exit `1`)
- `lock_exists_after = true`
- aucune tentative de reclaim

Voir doctrine `PERSISTENT_LOCK` et Décision N pour la classification complète.

---

## Décision L — Envelope JSON

`stdout` contient exactement un objet JSON UTF-8.

**Champs publics exacts (25 champs) :**

```
command
ok
authority
sovereign
decision_authority
kx108_decision_present
operation
adapter_code
lock_path
session_id
heartbeat_interval_seconds
max_steps
control_request
sequence_ok
cleanup_ok
first_failure
steps_executed
terminated
released
simulated
isolated
wired
mutation_scope
lock_exists_after
detail
```

**Valeurs constantes :**

```
command               = "obsidia session simulate"
authority             = "NONE"
sovereign             = false
decision_authority    = "KX108_ONLY"
kx108_decision_present = false
operation             = "SIMULATE_BOUNDED_SESSION"
simulated             = true
isolated              = true
wired                 = true
mutation_scope        = "TEMP_LOCK_ONLY"
```

`wired=true` signifie que la commande publique appelle l'adapter. Cela ne signifie aucune
intégration moteur, Obsidure, Brody ou KX108.

**Champs dérivés du résultat adapter :**

- `ok` : `result.ok` (modifié si postcondition violée)
- `adapter_code` : `result.adapter_code.value` (peut être `"INVOCATION_INVALID"`, `"INTERNAL_ERROR"` ou `"POSTCONDITION_FAILED"` selon le chemin)
- `session_id` : valeur publique transmise (non issue du résultat adapter)
- `lock_path` : valeur publique transmise (non issue du résultat adapter)
- `sequence_ok` : `result.sequence_ok`
- `cleanup_ok` : `result.cleanup_ok`
- `first_failure` : voir Décision M
- `steps_executed` : `result.caller_result.steps_executed` si `result.caller_result` n'est pas `None`, sinon `0`
- `terminated` : `result.caller_result.terminated` si `result.caller_result` n'est pas `None`, sinon `false`
- `released` : `result.caller_result.released` si `result.caller_result` n'est pas `None`, sinon `false`
- `detail` : `result.detail`

**Champs construits par le script :**

- `heartbeat_interval_seconds` : valeur publique transmise (float)
- `max_steps` : valeur publique transmise (int)
- `control_request` : chaîne canonique transmise (`"none"`, `"stop"` ou `"abort"`)
- `lock_exists_after` : voir Décisions N et O

### Table normative — INVOCATION_INVALID

Produite avant construction de l'adapter. Exit `2` si JSON émis (sinon exit `1`).

```
command                   = "obsidia session simulate"
ok                        = false
authority                 = "NONE"
sovereign                 = false
decision_authority        = "KX108_ONLY"
kx108_decision_present    = false
operation                 = "SIMULATE_BOUNDED_SESSION"
adapter_code              = "INVOCATION_INVALID"
lock_path                 = chaîne brute si extraite sans ambiguïté, sinon null
session_id                = chaîne brute si extraite sans ambiguïté, sinon null
heartbeat_interval_seconds = valeur numérique validée ou null
max_steps                 = valeur validée ou null
control_request           = valeur validée ou null
sequence_ok               = null
cleanup_ok                = null
first_failure             = null
steps_executed            = 0
terminated                = false
released                  = false
simulated                 = true
isolated                  = true
wired                     = true
mutation_scope            = "TEMP_LOCK_ONLY"
lock_exists_after         = null
detail                    = "INVOCATION_INVALID"
```

Aucun message Python. Aucun détail d'exception.

### Table normative — INTERNAL_ERROR

Produite lors d'une erreur interne imprévue. Exit `1`.

```
adapter_code              = "INTERNAL_ERROR"
detail                    = "INTERNAL_ERROR"
lock_exists_after         = null (sauf si vérification déjà réussie)
[tous les autres champs comme INVOCATION_INVALID]
```

Aucun traceback. Aucun message Python. Stderr vide.

### Table normative — BOOTSTRAP FAILURE

Produite quand `caller.bootstrap()` échoue dans `run_bounded`.

```
ok                        = false
adapter_code              = "CALLER_FAILED"
sequence_ok               = null
cleanup_ok                = null
first_failure             = null
steps_executed            = 0
terminated                = false
released                  = false
lock_exists_after         = false (attendu — lock jamais créé)
exit                      = 3
```

Si `lock_exists_after=true` après bootstrap failure, appliquer la doctrine postcondition failure.

---

## Décision M — First failure

`first_failure` vaut `null` quand `CallerResult.first_failure is None`.

Sinon, la source est l'`OperationResult` contenu dans `CallerResult.first_failure`.

**Structure JSON normative exacte :**

```json
{
  "ok": false,
  "code": "FAILURE_CODE_VALUE",
  "fail_closed": true,
  "human_recovery_required": false,
  "detail": "description bornée"
}
```

**Règles de mapping :**

- `ok` : reprend `OperationResult.ok`
- `code` : `OperationResult.code.value` si le code existe (type `FailureCode`), sinon `null`
- `fail_closed` : reprend `OperationResult.fail_closed`
- `human_recovery_required` : reprend `OperationResult.human_recovery_required`
- `detail` : reprend `OperationResult.detail` (borné, aucun traceback)

**Champs jamais exposés dans `first_failure` :**

- `payload` (données internes) — jamais exposé
- `repr()` d'un objet Python
- traceback
- chemin interne du dépôt
- secret

---

## Décision N — Postconditions et lock_exists_after

### Invariants normatifs

```
cleanup_ok=true  implique  released=true
released=true    implique  lock_exists_after=false
result.ok=true   implique  cleanup_ok=true
result.ok=true   implique  released=true
result.ok=true   implique  lock_exists_after=false
bootstrap failure implique  lock_exists_after=false
```

### Vérification lock_exists_after

Après le retour de l'adapter, le script appelle une seule fois la vérification en lecture seule :

```python
lock_exists_after = os.path.lexists(lock_path)
```

Cette vérification :

- ne modifie rien
- ne déclenche aucun cleanup
- ne supprime jamais le lock résiduel

**Si cette vérification lève une exception :**

```
ok                = false
adapter_code      = "INTERNAL_ERROR"
detail            = "INTERNAL_ERROR"
lock_exists_after = null
exit              = 1
```

### Cas `cleanup_ok=false` + `lock_exists_after=false`

Résidu de cleanup non cohérent avec le filesystem — situation possible (race condition, autre processus).

```
ok               = false
exit             = 3
```

Aucune réinterprétation en succès. Aucune suppression.

### Postcondition failure

Si un invariant normé est violé (ex : `cleanup_ok=true` + `released=true` + `lock_exists_after=true`) :

```
ok               = false
adapter_code     = "POSTCONDITION_FAILED"
detail           = "POSTCONDITION_FAILED"
exit             = 1
```

Les champs `sequence_ok`, `cleanup_ok`, `first_failure`, `steps_executed`, `terminated`,
`released`, `lock_exists_after` conservent leurs valeurs observées.

Le lock n'est jamais supprimé.

### Codes `adapter_code` publics autorisés

Valeurs de l'enum `AdapterCode` (OK, LOCK_NOT_FOUND, etc.) + extensions publiques du script :

```
INVOCATION_INVALID
INTERNAL_ERROR
POSTCONDITION_FAILED
```

---

## Décision O — Codes retour

```
0 = simulation exécutée, result.ok=true et JSON émis
1 = erreur interne, postcondition violée, ou canal stdout défaillant (OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED)
2 = invocation ou validation publique invalide
3 = simulation exécutée, result.ok=false et JSON émis
```

Le script ne retourne jamais `0` si :

- `result.ok = false`
- l'émission JSON échoue
- un invariant de postcondition est violé

Aucun chemin ne peut retourner `0` avec un lock résiduel ou une incohérence de postcondition.

---

## Décision P — Stdout et stderr

**stdout :**

- exactement un JSON
- sérialisation déterministe (`sort_keys=True`, `ensure_ascii=False`, `separators=(",",":")`)
- au maximum un saut de ligne final

**stderr :**

- vide dans tous les parcours contrôlés
- aucun traceback
- aucun message libre
- aucun contenu du lock
- aucun détail d'exception Python

**Doctrine appliquée :**

```
OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED
```

Si stdout est défaillant :

- aucune exception échappée
- stderr vide
- exit `1`
- aucune deuxième tentative d'émission

---

## Décision Q — Receipts

Aucun receipt persistant dans V0.

**Interdictions :**

- JSONL
- `.local_obsidia`
- Merkle seal
- SHA Git écrit
- journal de session
- fichier de preuve
- identifiant généré
- historique persistant
- `__pycache__` ou `.pyc`

Le JSON stdout est le seul livrable public.

---

## Décision R — Interdictions dans le script Python

Le script Python ne doit contenir aucun :

```
subprocess       thread          asyncio         multiprocessing
socket           HTTP            réseau          Git
lecture d'env    import dynamique écriture fichier suppression fichier
rename/move      signal handler  daemon          boucle infinie
appel Obsidure   appel Brody     appel KX108     reclaim
```

La seule chaîne autorisée à muter le lock est :

```
TerminalSessionAdapter
→ SynchronousHeartbeatCaller
→ HeartbeatLockManager
```

---

## Décision S — Non-objectifs

V0 ne fournit pas :

- exécution de code réel
- modification du dépôt
- génération de patch
- commit / push / PR
- orchestration d'agent
- Obsidure / Brody / KX108 exécutable
- admission réelle
- lock persistant
- session réelle
- reprise après crash
- reclaim ou réparation de lock
- receipt persistant
- commande `session run`
- commande `session execute`
- commande `session resume`

---

## Fichiers futurs autorisés

```
scripts/obsidia.ps1
scripts/obsidia_session_simulate_cli.py
periphery/tests/test_obsidia_session_simulate_cli.py
```

Le document normatif `docs/paliers/TERMINAL_SESSION_SIMULATE_V0_APPROVED.md` est protégé
après approbation.

---

## Fichiers protégés

La future implémentation ne doit pas modifier :

```
scripts/obsidia_cli.py
scripts/obsidia_registry.yaml
scripts/obsidia_session_inspect_cli.py
periphery/tests/test_obsidia_session_inspect_cli.py
periphery/session_lock/terminal_session_adapter.py
periphery/tests/test_terminal_session_adapter.py
periphery/session_lock/heartbeat_caller.py
periphery/tests/test_heartbeat_caller.py
periphery/session_lock/heartbeat_lock_manager.py
periphery/tests/test_heartbeat_lock_manager.py
periphery/session_lock/__init__.py
docs/paliers/TERMINAL_SESSION_INSPECT_V0_APPROVED.md
docs/paliers/TERMINAL_SESSION_SIMULATE_V0_APPROVED.md
```

---

## Plan de tests futur (112 scénarios normatifs)

### Parser et acknowledgement (T01–T08)

1. aucun argument → exit 2
2. option manquante (--lock-path, --session-id, --heartbeat-interval-seconds, --max-steps, --control, --ack-temp-lock-mutation absents un à un) → exit 2
3. option inconnue → exit 2
4. option dupliquée → exit 2
5. ordre incorrect → exit 2
6. forme `--option=value` → exit 2
7. `--ack-temp-lock-mutation` absent → exit 2, adapter non construit
8. adapter non construit lors d'une invocation invalide

### Lock path (T09–T20)

9. chemin relatif rejeté
10. parent absent rejeté
11. parent non répertoire rejeté
12. cible déjà existante rejetée
13. cible répertoire rejetée
14. cible non-dangling symlink rejetée (`is_symlink()=True`, `exists()=True`)
15. parent symlink rejeté
16. chemin dans le dépôt rejeté
17. chemin absolu hors dépôt accepté
18. chemin avec espaces accepté
19. chemin Unicode accepté (si hors dépôt et parent valide)
20. chaîne publique préservée exactement dans `lock_path`

### Session ID (T21–T25)

21. vide rejeté
22. longueur > 128 rejetée
23. caractère de contrôle rejeté (ex : `\x01`)
24. espaces initial ou final rejetés
25. session_id valide préservé exactement

### Heartbeat interval (T26–T35)

26. option absente rejetée
27. booléen rejeté
28. zéro rejeté (`0`)
29. négatif rejeté
30. NaN rejeté
31. `+Inf` rejeté
32. `-Inf` rejeté
33. inférieur à 0.01 rejeté
34. supérieur à 5.0 rejeté
35. bornes 0.01 et 5.0 acceptées ; aucune valeur par défaut

### Max steps (T36–T41)

36. non entier rejeté (`1.0`)
37. booléen rejeté (`True`)
38. zéro rejeté
39. négatif rejeté
40. supérieur à 100 rejeté
41. bornes 1 et 100 acceptées

### Control request (T42–T46)

42. `none` mappé vers `None`
43. `stop` mappé vers `ControlRequest.STOP`
44. `abort` mappé vers `ControlRequest.ABORT`
45. casse différente (`NONE`, `STOP`, `ABORT`) rejetée
46. valeur inconnue rejetée

### Simulation (T47–T57)

47. simulation nominale bornée → exit 0, `lock_exists_after=false`
48. `--control stop` → résultat terminé proprement
49. `--control abort` → résultat terminé proprement
50. bootstrap failure → exit 3, `adapter_code=CALLER_FAILED`, `first_failure=null`, `steps_executed=0`
51. tick failure → `first_failure` contient `OperationResult` mappé selon Décision M, exit 3
52. cleanup success → `lock_exists_after=false`
53. cleanup failure → `lock_exists_after=true`, lock résiduel préservé
54. cleanup failure → aucune suppression manuelle par le script
55. lock préexistant → rejeté avant adapter, exit 2
56. adapter appelé exactement une fois
57. manager et caller jamais appelés directement par le script

### JSON (T58–T68)

58. 25 champs exacts (0 manquant, 0 surplus)
59. constantes d'autorité : `authority`, `sovereign`, `decision_authority`, `kx108_decision_present`, `operation`, `simulated`, `isolated`, `wired`, `mutation_scope`
60. `wired=true` public uniquement (adapter interne retourne `wired=false`)
61. `first_failure=null` en cas nominal
62. `first_failure` structuré avec `ok`, `code`, `fail_closed`, `human_recovery_required`, `detail` — aucun champ `operation`, `failure_code` ou `payload`
63. `lock_exists_after` exact après retour adapter
64. stdout = exactement un JSON sur une ligne avec saut final
65. stderr vide dans tous les parcours contrôlés
66. aucune séquence ANSI
67. aucun traceback sur stdout ou stderr
68. canal stdout cassé → exit 1, stderr vide, aucune exception échappée

### Effets de bord (T69–T78)

69. aucune mutation du dépôt
70. aucune création de fichier hors lock autorisé
71. aucun receipt JSONL
72. aucun accès Git
73. aucun accès réseau
74. aucune lecture de variable d'environnement
75. aucun subprocess, thread ou asyncio
76. aucun reclaim
77. aucun appel Obsidure, Brody ou KX108
78. aucun processus persistant après retour

### PowerShell (T79–T88)

79. route exacte `session simulate` déclenchée
80. route sensible à la casse (`SESSION SIMULATE` non routé)
81. autres variantes de casse non routées
82. arguments transmis sans transformation
83. code retour propagé exactement (0, 1, 2, 3)
84. aucun boot de service
85. `obsidia_cli.py` non invoqué
86. commande `inspect` toujours fonctionnelle après ajout
87. `session run` non exposé
88. `session execute` non exposé

### Intégrité blob (T89–T95)

89. `terminal_session_adapter.py` byte-identique
90. `obsidia_session_inspect_cli.py` byte-identique
91. `heartbeat_caller.py` byte-identique
92. `heartbeat_lock_manager.py` byte-identique
93. `obsidia_registry.yaml` byte-identique
94. `obsidia_cli.py` byte-identique
95. diff PowerShell limité à la nouvelle route `session simulate` et à `python -B`

### Scénarios complémentaires REV01 (T96–T112)

96. session_id avec espace interne rejeté (`"my id"`)
97. session_id Unicode non ASCII rejeté (`"session-é"`)
98. intervalle scientifique `1e-2` rejeté
99. intervalle avec espaces `" 1"` rejeté
100. max_steps `01` (zéro initial) rejeté
101. control `" stop "` (espaces) rejeté
102. `os.path.lexists` ou équivalent lève `OSError` → `INTERNAL_ERROR`, `lock_exists_after=null`, exit 1
103. postcondition `released=true` + `lock_exists_after=true` → `POSTCONDITION_FAILED`, exit 1
104. `cleanup_ok=false` + `lock_exists_after=false` → exit 3, pas de réinterprétation en succès
105. dangling symlink cible rejeté (`lexists=True`, `exists=False`)
106. parent junction/reparse point rejeté sous Windows
107. chemin dans dépôt avec casse différente rejeté sous Windows
108. chemin contenant `..` résolu dans le dépôt rejeté
109. chemin UNC `\\server\share\...` rejeté
110. aucun `__pycache__` ou `.pyc` créé après exécution (snapshot avant/après)
111. `first_failure.code` mappe `OperationResult.code.value` — champ `code`, pas `failure_code`
112. `payload` de `OperationResult` jamais exposé dans `first_failure`

---

## Tests de régression futurs

La future implémentation doit exécuter séparément :

```
python -m pytest periphery/tests/test_obsidia_session_simulate_cli.py -q
python -m pytest periphery/tests/test_obsidia_session_inspect_cli.py -q
python -m pytest periphery/tests/test_terminal_session_adapter.py -q
python -m pytest periphery/tests/test_heartbeat_caller.py -q
python -m pytest periphery/tests/test_heartbeat_lock_manager.py -q
```

Puis les cinq fichiers conjointement.

**Résultats de référence à préserver :**

```
inspect CLI : 72 passants
adapter     : 55 passants
caller      : 28 passants
manager     : 20 passants
```

---

## Paramètres de production différés

```
PRODUCTION_HEARTBEAT_INTERVAL   : UNRESOLVED
PRODUCTION_FUTURE_CLOCK_SKEW    : UNRESOLVED
PRODUCTION_GF_R01_HASH          : UNRESOLVED
PRODUCTION_SESSION_ID_POLICY    : UNRESOLVED
PRODUCTION_MAX_STEPS_POLICY     : UNRESOLVED
KX108_INTEGRATION               : DEFERRED
OBSIDURE_WIRING                 : DEFERRED
BRODY_WIRING                    : DEFERRED
```

---

## Checklist de validation du document REV01

- [x] 13 statuts normatifs présents
- [x] `SPEC_REVISION: REV01` présent
- [x] commande canonique sur une seule ligne (aucun `\` de continuation)
- [x] `--ack-temp-lock-mutation` obligatoire
- [x] `SIMULATION_SESSION_ID_NOT_PRODUCTION`
- [x] `SESSION_ID_GRAMMAR_V0` présente
- [x] `SIMULATION_INTERVAL_NOT_PRODUCTION`
- [x] `HEARTBEAT_INTERVAL_GRAMMAR_V0` présente
- [x] `MAX_STEPS_GRAMMAR_V0` présente
- [x] `SIMULATION_BOUNDS_V0`
- [x] codes 0, 1, 2 et 3 définis
- [x] table INVOCATION_INVALID présente
- [x] table INTERNAL_ERROR présente
- [x] table bootstrap failure présente
- [x] `POSTCONDITION_FAILED` présent
- [x] `TEMP_LOCK_ONLY`
- [x] `RECLAIM: FORBIDDEN`
- [x] `REAL_EXECUTION: FORBIDDEN`
- [x] `OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED`
- [x] `NO_REAL_TIME_WAITING_V0` présent
- [x] `python -B` présent dans le wrapper PowerShell
- [x] `sys.dont_write_bytecode = True` présent dans les imports futurs
- [x] algorithme de confinement complet (reparse points, junctions, UNC, dangling symlink)
- [x] `first_failure` sans `operation` ni `failure_code` — structure `OperationResult` correcte
- [x] terminologie `OperationResult contenu dans CallerResult.first_failure` — pas `CallerResult`
- [x] imports canoniques corrigés (`ControlRequest` et `HeartbeatConfig` depuis `heartbeat_lock_manager`)
- [x] `payload` jamais exposé dans `first_failure`
- [x] doctrine `PERSISTENT_LOCK` vs résidu d'échec explicitement énoncée
- [x] 112 scénarios de test (T01–T112)
- [x] aucune commande `session run`, `session execute` ou `session resume` approuvée
- [x] aucune valeur de production inventée
