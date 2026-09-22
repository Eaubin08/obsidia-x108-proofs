# TERMINAL_SESSION_INSPECT_V0 — Public Readonly Session Inspect Command

```
STATUS: APPROVED_AND_CLOSED
CANONICAL_NAME: TERMINAL_SESSION_INSPECT_V0
SCOPE: PUBLIC_READONLY_INSPECT_COMMAND_ONLY
PUBLIC_COMMAND: OBSIDIA_SESSION_INSPECT
LOCK_MUTATION: FORBIDDEN
SESSION_CREATION: FORBIDDEN
SIMULATION: FORBIDDEN
REAL_EXECUTION: FORBIDDEN
OBSIDURE_WIRING: FORBIDDEN
KX108_INTEGRATION: DEFERRED
RECLAIM: FORBIDDEN
```

```
DATE_APPROVED:        2026-07-29
APPROVAL:             Opérateur humain — mandat TERMINAL_SESSION_INSPECT_V0_SPEC_AUTHORING
BASE_SHA:             0ef8c5131952317faa6b585ab07d16ffdfcb4cea
BASE_BRANCH:          feat/terminal-session-adapter-v0
PREDECESSOR:          docs/paliers/TERMINAL_SESSION_ADAPTER_V0_APPROVED.md
SPEC_BRANCH:          docs/terminal-session-inspect-v0-spec
```

> **Ce document est la spécification normative approuvée de TERMINAL_SESSION_INSPECT_V0.**
> Il définit la première commande terminal publique utilisant `TerminalSessionAdapter`.
> L'opération est exclusivement une inspection en lecture seule d'un fichier de lock existant.
> Aucun code n'est implémenté dans ce palier. Toutes les décisions ont été approuvées par
> l'opérateur humain dans le mandat `TERMINAL_SESSION_INSPECT_V0_SPEC_AUTHORING` (2026-07-29).

---

## HUMAN_DECISIONS_APPROVED

> Section normative. Les décisions ci-dessous constituent la clôture formelle
> de la spécification TERMINAL_SESSION_INSPECT_V0.

### DECISION_A — COMMANDE_CANONIQUE

La syntaxe publique canonique unique approuvée est :

```text
obsidia session inspect --lock-path "<chemin explicite>"
```

Aucune syntaxe alternative n'est approuvée dans V0.

Syntaxes explicitement **interdites** :

- `obsidia inspect`
- `obsidia session`
- `obsidia session inspect` (sans argument `--lock-path`)
- `obsidia session inspect <chemin>` (chemin positionnel sans nom d'option)
- `obsidia session inspect --auto`
- `obsidia session inspect --default`
- `obsidia session inspect --latest`
- toute forme utilisant un glob, un wildcard ou une découverte automatique.

Le chemin doit toujours être fourni **explicitement par l'humain**.
La commande ne complète aucun chemin, ne propose aucune valeur, ne lit aucune configuration.

### DECISION_B — ARCHITECTURE_DU_ROUTAGE

L'architecture de routage future autorisée est :

```text
scripts/obsidia.ps1
└── route exacte : session inspect --lock-path <value>
    └── python scripts/obsidia_session_inspect_cli.py --lock-path <value>
        └── TerminalSessionAdapter().inspect_lock(lock_path)
```

Le script Python dédié (`scripts/obsidia_session_inspect_cli.py`) devra importer
**uniquement** :

- la stdlib strictement nécessaire (`sys`, `json`, `argparse` ou équivalent minimal) ;
- `TerminalSessionAdapter` ;
- les enums et types de résultat nécessaires depuis
  `periphery.session_lock.terminal_session_adapter`.

Le fichier `scripts/obsidia_cli.py` reste **protégé et inchangé**.
La doctrine de `obsidia_cli.py` reste intacte :

- aucun import de `periphery` ;
- aucun subprocess ;
- aucun POST ;
- aucune mutation ;
- aucun moteur.

Le script dédié `obsidia_session_inspect_cli.py` est **distinct** de `obsidia_cli.py`
et ne l'importe pas.

### DECISION_C — WRAPPER_POWERSHELL

`scripts/obsidia.ps1` pourra ultérieurement recevoir une route exacte pour :

```text
session inspect --lock-path <value>
```

Le wrapper doit uniquement :

1. reconnaître la sous-commande exacte (`session inspect`) ;
2. vérifier la présence **structurelle** de l'argument `--lock-path` ;
3. invoquer `scripts/obsidia_session_inspect_cli.py` avec l'argument transmis à l'identique ;
4. transmettre le code de retour du script Python sans le modifier ;
5. ne pas interpréter le contenu du lock ;
6. ne pas décider si le lock est valide ou non ;
7. ne pas supprimer, réparer ou modifier le lock.

Le wrapper ne devient **pas** une autorité d'admission.
Les autres routes existantes de `obsidia.ps1` restent inchangées.

### DECISION_D — CHEMIN_EXPLICITE

`--lock-path` est **obligatoire**. Son absence produit une erreur d'invocation (exit 2).

Interdictions absolues pour la valeur de ce paramètre :

- aucune valeur par défaut ;
- aucune lecture de variable d'environnement ;
- aucune lecture de configuration ou de profil ;
- aucune recherche dans le dépôt ;
- aucune recherche dans le profil utilisateur ;
- aucune recherche de fichier récent ;
- aucune génération de chemin ;
- aucun `Path.resolve()` imposé ;
- aucune transformation en chemin absolu ;
- aucun glob ;
- aucune récursion de répertoire.

Le chemin transmis au script dédié doit être **identique** à celui fourni par l'humain.
`TerminalSessionAdapter.inspect_lock()` est la seule autorité de résolution.

### DECISION_E — OPERATION_UNIQUE

Le script dédié ne doit appeler que :

```python
TerminalSessionAdapter().inspect_lock(lock_path)
```

Appels **interdits** dans le script dédié :

- `simulate_bounded_session`
- `HeartbeatLockManager`
- `SynchronousHeartbeatCaller`
- `bootstrap`
- `tick`
- `request_stop`
- `request_abort`
- `consume_and_terminate`
- `release`
- `run_bounded`
- `classify_lock`
- `prepare_reclaim_proposal`
- `execute_reclaim`

Le script ne doit **pas** réimplémenter la validation du schéma du lock.
La source de vérité est exclusivement `TerminalSessionAdapter.inspect_lock()`.

### DECISION_F — SORTIE_PUBLIQUE

La sortie standard est **exactement un objet JSON UTF-8**.

Interdictions pour la sortie :

- aucun texte décoratif mélangé au JSON ;
- aucun tableau, bannière, couleur ANSI, message interactif.

Envelope publique minimale en cas de succès :

```json
{
  "command": "obsidia session inspect",
  "ok": true,
  "authority": "NONE",
  "sovereign": false,
  "decision_authority": "KX108_ONLY",
  "kx108_decision_present": false,
  "operation": "INSPECT_LOCK",
  "adapter_code": "OK",
  "lock_path": "<chemin transmis>",
  "session_id": "<valeur ou null>",
  "lock_record": {},
  "simulated": false,
  "isolated": true,
  "wired": true,
  "mutation_scope": "NONE",
  "detail": "INSPECT_OK"
}
```

Note normative sur `wired=true` : ce champ signifie uniquement que la commande
publique est reliée à l'adapter via le script dédié. Cela ne signifie **pas** :

- moteur branché ;
- session admise ;
- action autorisée ;
- KX108 intégré ;
- Obsidure branché.

En cas d'échec, le script produit la même structure d'envelope avec :

- `ok=false` ;
- `adapter_code` descriptif retourné par l'adapter ;
- `lock_record=null` ;
- `session_id=null` ;
- aucun traceback dans la sortie ;
- aucune réparation ;
- aucune décision souveraine.

### DECISION_G — SERIALISATION_LOCK_RECORD

Le `lock_record` interne est profondément immuable (`MappingProxyType`, tuples récursifs).

Pour la sortie JSON uniquement, le script pourra effectuer une conversion récursive
**sans mutation** du résultat de l'adapter :

- `Mapping` (dont `MappingProxyType`) → objet JSON ;
- `tuple` → tableau JSON ;
- scalaires → inchangés.

Cette conversion :

- ne doit pas modifier le résultat de l'adapter ;
- ne doit pas écrire de fichier ;
- ne doit pas injecter de champ supplémentaire ;
- ne doit pas retirer de champ existant ;
- ne doit pas interpréter les valeurs.

### DECISION_H — CODES_DE_RETOUR

Codes de processus normatifs :

```text
0  =  inspection réussie, result.ok=true
2  =  invocation invalide ou argument obligatoire absent (avant toute inspection)
3  =  inspection exécutée mais result.ok=false
1  =  erreur interne inattendue encapsulée (exception non prévue)
```

Pour le code `1` (erreur interne inattendue) :

- produire un JSON fail-closed sur stdout ;
- ne jamais imprimer de traceback sur stdout ni sur stderr ;
- `authority="NONE"` ;
- `sovereign=false` ;
- `kx108_decision_present=false` ;
- `lock_record=null`.

Le script **ne doit jamais** retourner `0` lorsque l'adapter retourne `ok=false`.

### DECISION_I — STDERR_ET_STDOUT

`stdout` :

- exactement un objet JSON ;
- toujours utilisé pour le résultat structuré (succès et échec).

`stderr` :

- vide dans les parcours normaux ;
- aucune stack trace ;
- aucun secret ;
- aucun contenu du fichier de lock.

Les erreurs structurées restent sur `stdout`.

### DECISION_J — AUTHORITY

Valeurs obligatoires dans toute envelope produite par cette commande :

```text
authority:             NONE
sovereign:             false
decision_authority:    KX108_ONLY
kx108_decision_present: false
simulated:             false
isolated:              true
mutation_scope:        NONE
```

La commande ne doit **jamais** produire les termes suivants comme jugement :

- `ACT`
- `HOLD`
- `BLOCK`
- `ALLOW`
- `DENY`
- `AUTHORIZED`
- `ADMITTED`
- `RECLAIMABLE`
- `STALE`
- `ACTIVE`

Elle rapporte uniquement le résultat **descriptif** de l'inspection telle que
retournée par `TerminalSessionAdapter.inspect_lock()`.

### DECISION_K — RECEIPTS

Aucun receipt persistant dans V0.

Interdictions absolues :

- aucune écriture JSONL ;
- aucune écriture dans `.local_obsidia` ;
- aucun log de session ;
- aucun Merkle seal ;
- aucun SHA Git ;
- aucun identifiant généré ;
- aucune écriture de preuve.

La sortie JSON sur stdout est le **seul livrable** de la commande.

### DECISION_L — SECURITE_ET_EFFETS_DE_BORD

Le script Python dédié (`obsidia_session_inspect_cli.py`) ne doit contenir aucun :

- `subprocess` ;
- `thread` ;
- `asyncio` ;
- `multiprocessing` ;
- réseau (socket, HTTP, requête) ;
- accès Git ;
- import dynamique (`importlib`, `__import__`) ;
- lecture de variable d'environnement ;
- écriture de fichier ;
- suppression de fichier ;
- renommage ou déplacement de fichier ;
- réparation de lock ;
- signal handler ;
- daemon ;
- boucle infinie.

Le **seul** accès fichier autorisé est celui effectué **à l'intérieur** de
`TerminalSessionAdapter.inspect_lock(lock_path)`.

### DECISION_M — NON_OBJECTIFS_V0

V0 ne fournit **pas** :

- `obsidia session simulate`
- `obsidia session run`
- `obsidia run`
- `obsidia build`
- `obsidia execute`
- `obsidia resume`
- admission de session
- gestion de session active
- heartbeat public
- STOP public
- ABORT public
- moteur de code
- Obsidure
- Brody
- KX108 exécutable
- receipt persistant
- reclaim
- réparation de lock

---

## FICHIERS_FUTURS_AUTORISES

La future implémentation pourra modifier ou créer uniquement :

```text
scripts/obsidia.ps1                              (ajout route session inspect)
scripts/obsidia_session_inspect_cli.py           (nouveau script dédié)
periphery/tests/test_obsidia_session_inspect_cli.py   (nouveaux tests)
```

Le chemin canonique retenu pour les tests est :

```text
periphery/tests/test_obsidia_session_inspect_cli.py
```

Ce choix est cohérent avec la convention existante du dépôt (`periphery/tests/`
héberge tous les tests unitaires des composants `periphery/session_lock/`).

---

## FICHIERS_PROTEGES

La future implémentation ne devra **pas** modifier :

```text
scripts/obsidia_cli.py
scripts/obsidia_registry.yaml
periphery/session_lock/terminal_session_adapter.py
periphery/tests/test_terminal_session_adapter.py
periphery/session_lock/heartbeat_caller.py
periphery/session_lock/heartbeat_lock_manager.py
periphery/session_lock/__init__.py
```

---

## PLAN_DE_TESTS_FUTUR

Les tests suivants sont **requis au minimum** pour valider l'implémentation :

| # | Cas de test | Attendu |
|---|---|---|
| 1 | Commande sans `--lock-path` | exit 2 |
| 2 | Argument inconnu | exit 2 |
| 3 | Argument `--lock-path` dupliqué | exit 2 |
| 4 | Chemin absent (fichier inexistant) | JSON ok=false, exit 3 |
| 5 | Chemin non-fichier (répertoire) | JSON ok=false, exit 3 |
| 6 | Fichier présent, JSON invalide | JSON ok=false, exit 3 |
| 7 | JSON valide, schéma invalide | JSON ok=false, exit 3 |
| 8 | Lock valide, tous les champs corrects | JSON ok=true, exit 0 |
| 9 | stdout contient exactement un objet JSON | assertion structurelle |
| 10 | stderr vide | assertion structurelle |
| 11 | Aucun code ANSI dans stdout | assertion négative |
| 12 | Aucun traceback dans stdout ni stderr | assertion négative |
| 13 | `lock_record` sérialisé sans mutation du résultat adapter | vérification via spy |
| 14 | Champs supplémentaires imbriqués dans le lock conservés | présence in JSON |
| 15 | bool, tuple et mappings convertis correctement | assertion de type JSON |
| 16 | Champs authority constants sur toutes les exécutions | `authority=NONE`, `sovereign=false`, etc. |
| 17 | Aucune valeur souveraine dans l'envelope | assertion négative |
| 18 | Aucune création de fichier lors d'une inspection | vérification système de fichiers |
| 19 | Aucune modification du fichier de lock | comparaison bytes avant/après |
| 20 | Aucune suppression du fichier de lock | existence vérifiée après |
| 21 | Aucune écriture hors stdout | vérification système de fichiers |
| 22 | Aucun receipt JSONL créé | assertion négative |
| 23 | Aucun import de `obsidia_cli` dans le nouveau script | AST statique |
| 24 | Aucun import interdit dans `obsidia_session_inspect_cli.py` | AST statique |
| 25 | Aucun appel autre que `inspect_lock` dans le script dédié | AST statique |
| 26 | Aucun appel reclaim | AST statique |
| 27 | Aucun accès Git | AST statique |
| 28 | Aucun accès réseau | AST statique |
| 29 | Aucune lecture d'environnement | AST statique |
| 30 | Route PowerShell exacte reconnue (`session inspect --lock-path`) | test intégration wrapper |
| 31 | Autres routes PowerShell existantes inchangées | test non-régression wrapper |
| 32 | Code de retour PowerShell identique au code Python | comparaison exit codes |
| 33 | `terminal_session_adapter.py` byte-identique au commit `0ef8c51` | `git hash-object` |
| 34 | `heartbeat_caller.py` et `heartbeat_lock_manager.py` byte-identiques | `git hash-object` |
| 35 | Aucune commande `session simulate` exposée par le wrapper | assertion négative |

---

## CRITERES_DE_SORTIE_FUTURS

L'implémentation sera prête pour le palier suivant **uniquement si** :

- tous les tests `test_obsidia_session_inspect_cli.py` passent ;
- les 55 tests adapter (`test_terminal_session_adapter.py`) passent ;
- les 28 tests caller (`test_heartbeat_caller.py`) passent ;
- les 20 tests manager (`test_heartbeat_lock_manager.py`) passent ;
- aucune mutation du fichier de lock lors d'une inspection ;
- aucune mutation du dépôt (aucun fichier protégé modifié) ;
- stdout est un JSON unique sur toutes les branches d'exécution ;
- aucune commande supplémentaire n'est exposée (`session simulate`, `session run`, etc.) ;
- aucun fichier protégé n'est modifié ;
- aucune autorité nouvelle n'est créée ou simulée.

---

## PARAMETRES_DIFFERES

Les éléments suivants restent **hors périmètre** de ce palier et ne sont pas approuvés :

- câblage Obsidure ;
- intégration KX108 exécutable ;
- décision DECISION_AUTHORITY (reportée, `KX108_ONLY` sans stub) ;
- gestion de session active (heartbeat, STOP, ABORT) ;
- receipt persistant ou Merkle seal ;
- commande `obsidia session simulate` ;
- toute commande au-delà de `obsidia session inspect`.
