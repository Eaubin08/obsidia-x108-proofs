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

---

## Contexte

Ce palier définit la première commande publique de simulation bornée de session :

```
obsidia session simulate --lock-path "<chemin absolu>" --session-id "<identifiant>" \
  --heartbeat-interval-seconds "<nombre>" --max-steps "<entier>" \
  --control "<none|stop|abort>" --ack-temp-lock-mutation
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

**Contraintes de validation :**

- chaîne non vide
- chemin absolu
- la cible n'existe pas avant la simulation
- le parent existe
- le parent est un répertoire
- la cible est hors du dépôt Git courant
- la cible n'est pas un symlink
- la cible n'est pas dans un répertoire symlinké
- aucune création de répertoire parent

Le script peut résoudre le chemin uniquement pour la validation de confinement et de symlinks.

La valeur publique `lock_path` dans le JSON conserve **exactement** la chaîne fournie.

**Interdictions :**

- chemin relatif
- chemin dans le dépôt
- fichier déjà existant
- répertoire existant comme cible
- création de parent
- remplacement d'un fichier préexistant
- suppression préalable
- réparation
- fallback vers un chemin par défaut
- suppression manuelle d'un lock préexistant

---

## Décision D — Session ID

`--session-id` est obligatoire.

**Contraintes V0 :**

- chaîne non vide
- longueur de 1 à 128 caractères inclus
- aucun retour à la ligne (`\n`, `\r`)
- aucun caractère de contrôle (codepoint < 32)
- aucun espace initial ou final
- aucune normalisation silencieuse

Le session_id est une identité de simulation uniquement.

```
SIMULATION_SESSION_ID_NOT_PRODUCTION
```

---

## Décision E — Heartbeat interval

`--heartbeat-interval-seconds` est obligatoire.

Le parser accepte une représentation décimale finie.

**Contraintes de simulation V0 :**

```
minimum inclusif : 0.01
maximum inclusif : 5.0
booléen interdit
NaN interdit
+Inf interdit
-Inf interdit
```

```
SIMULATION_INTERVAL_NOT_PRODUCTION
```

Ces bornes sont des garde-fous de simulation locale. Elles ne représentent aucune politique
de production.

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

Le script ne doit jamais utiliser `1.0` ou toute autre valeur par défaut quand l'option est absente.

---

## Décision F — Max steps

`--max-steps` est obligatoire.

**Contraintes V0 :**

```
type : entier strict (pas de booléen, pas de float)
minimum inclusif : 1
maximum inclusif : 100
```

```
SIMULATION_BOUNDS_V0
```

Ces bornes ne représentent aucune politique de production.

Une valeur hors limites entraîne : aucun adapter construit, aucun lock créé,
`INVOCATION_INVALID`, exit `2`.

---

## Décision G — Control request

`--control` est obligatoire.

**Valeurs exactes autorisées :**

```
none   → None
stop   → ControlRequest.STOP
abort  → ControlRequest.ABORT
```

La comparaison est sensible à la casse.

Non accepté : `NONE`, `STOP`, `ABORT`, valeur vide, valeur inconnue, valeurs multiples.

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
    └── python scripts/obsidia_session_simulate_cli.py  @remainingArgs
        └── validation publique bornée
        └── construction HeartbeatConfig explicite
        └── TerminalSessionAdapter().simulate_bounded_session(...)
        └── vérification lock_exists_after (lecture seule)
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

**Résolution du script Python :**

```powershell
python "$PSScriptRoot\obsidia_session_simulate_cli.py" @remainingArgs
exit $LASTEXITCODE
```

---

## Décision I — Imports futurs

**Imports autorisés dans le script dédié :**

```python
from __future__ import annotations

import json
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Optional, Sequence

from periphery.session_lock.terminal_session_adapter import (
    ControlRequest,
    HeartbeatConfig,
    TerminalSessionAdapter,
    TerminalSessionAdapterResult,
)
```

**Constat d'implémentation :** `HeartbeatConfig` et `ControlRequest` sont exportés par
`periphery.session_lock.terminal_session_adapter` mais **pas** par
`periphery.session_lock.__init__`. Le chemin d'import canonique est donc :

```python
from periphery.session_lock.terminal_session_adapter import (
    ControlRequest,
    HeartbeatConfig,
    TerminalSessionAdapter,
    TerminalSessionAdapterResult,
)
```

Cette surface est vérifiée disponible au SHA `6ff0b2120da3ed092adc70049ef844f798b2cfeb`.

**Le script ne doit jamais importer directement :**

- `HeartbeatLockManager`
- `SynchronousHeartbeatCaller`
- `CallerResult`
- `BoundedSessionResult`

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
- exit `3`
- `lock_exists_after = true`
- aucune tentative de reclaim

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

- `ok` : `result.ok`
- `adapter_code` : `result.adapter_code.value`
- `session_id` : valeur publique transmise (non issue du résultat)
- `lock_path` : valeur publique transmise (non issue du résultat)
- `sequence_ok` : `result.sequence_ok`
- `cleanup_ok` : `result.cleanup_ok`
- `first_failure` : voir Décision M
- `steps_executed` : `result.caller_result.steps_executed` si `result.caller_result` n'est pas `None`, sinon `null`
- `terminated` : `result.caller_result.terminated` si `result.caller_result` n'est pas `None`, sinon `null`
- `released` : `result.caller_result.released` si `result.caller_result` n'est pas `None`, sinon `null`
- `detail` : `result.detail`

**Champs construits par le script :**

- `heartbeat_interval_seconds` : valeur publique transmise (float)
- `max_steps` : valeur publique transmise (int)
- `control_request` : chaîne canonique transmise (`"none"`, `"stop"` ou `"abort"`)
- `lock_exists_after` : voir Décision N

---

## Décision M — First failure

`first_failure` vaut `null` quand aucune première erreur n'existe.

Sinon, objet JSON minimal structuré :

```json
{
  "operation": "<chaîne>",
  "ok": false,
  "failure_code": "<chaîne>",
  "detail": "<chaîne>"
}
```

**Interdit dans `first_failure` :**

- traceback
- objet Python brut
- chemin interne du dépôt
- secret
- stack
- représentation `repr()`

La conversion préserve la première erreur retournée par le caller sans la remplacer.
`first_failure` est dérivé de `result.first_failure` (objet `CallerResult` interne) ;
le script l'extrait et le sérialise en un objet JSON minimal.

---

## Décision N — Lock exists after

Après le retour de l'adapter, le script vérifie en lecture seule si le chemin du lock existe.

```
lock_exists_after: true | false
```

Cette vérification :

- ne modifie rien
- ne déclenche aucun cleanup
- ne transforme pas le résultat de l'adapter
- ne transforme jamais un échec en succès

En succès nominal attendu : `lock_exists_after = false`

En cleanup failure : `lock_exists_after` peut être `true`

**Incohérence interdite :** si `cleanup_ok=true` et `released=true` et `lock_exists_after=true`,
le script rapporte cette incohérence comme résultat `ok=false` sans supprimer le lock.

---

## Décision O — Codes retour

```
0 = simulation exécutée, result.ok=true et JSON émis
1 = erreur interne ou canal stdout défaillant (OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED)
2 = invocation ou validation publique invalide
3 = simulation exécutée, result.ok=false et JSON émis
```

Le script ne retourne jamais `0` si :

- `result.ok = false`
- l'émission JSON échoue
- `lock_exists_after=true` alors que `cleanup_ok=true` et `released=true`

Toute incohérence entre `cleanup_ok=true`, `released=true`, `lock_exists_after=true` est
rapportée fail-closed sans supprimer le lock.

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

## Plan de tests futur (95 scénarios)

### Parser et acknowledgement (T01–T08)

1. aucun argument → exit 2
2. option manquante (chaque option obligatoire absente) → exit 2
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
14. cible symlink rejetée
15. parent symlink rejeté
16. chemin dans le dépôt rejeté
17. chemin absolu hors dépôt accepté
18. chemin avec espaces accepté
19. chemin Unicode accepté
20. chaîne publique préservée exactement dans `lock_path`

### Session ID (T21–T25)

21. vide rejeté
22. longueur > 128 rejetée
23. caractère de contrôle rejeté
24. espaces initial ou final rejetés
25. session_id valide préservé exactement

### Heartbeat interval (T26–T35)

26. option absente rejetée
27. booléen rejeté
28. zéro rejeté
29. négatif rejeté
30. NaN rejeté
31. `+Inf` rejeté
32. `-Inf` rejeté
33. inférieur à 0.01 rejeté
34. supérieur à 5.0 rejeté
35. bornes 0.01 et 5.0 acceptées ; aucune valeur par défaut

### Max steps (T36–T41)

36. non entier rejeté
37. booléen rejeté
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
50. bootstrap failure → exit 3, premier adapter_code approprié
51. tick failure → `first_failure` préservé, exit 3
52. cleanup success → `lock_exists_after=false`
53. cleanup failure → `lock_exists_after=true`, lock résiduel préservé
54. cleanup failure → aucune suppression manuelle par le script
55. lock préexistant → rejeté sans suppression
56. adapter appelé exactement une fois
57. manager et caller jamais appelés directement par le script

### JSON (T58–T68)

58. 25 champs exacts (0 manquant, 0 surplus)
59. constantes d'autorité : `authority`, `sovereign`, `decision_authority`, `kx108_decision_present`, `operation`, `simulated`, `isolated`, `wired`, `mutation_scope`
60. `wired=true` public uniquement
61. `first_failure=null` en cas nominal
62. `first_failure` structuré en objet minimal en cas d'échec
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
83. code retour propagé exactement
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
95. diff PowerShell limité à la nouvelle route `session simulate`

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

## Checklist de validation du document

- [x] 13 statuts normatifs présents
- [x] commande canonique exacte
- [x] `--ack-temp-lock-mutation` obligatoire
- [x] `SIMULATION_SESSION_ID_NOT_PRODUCTION`
- [x] `SIMULATION_INTERVAL_NOT_PRODUCTION`
- [x] `SIMULATION_BOUNDS_V0`
- [x] codes 0, 1, 2 et 3 définis
- [x] `TEMP_LOCK_ONLY`
- [x] `RECLAIM: FORBIDDEN`
- [x] `REAL_EXECUTION: FORBIDDEN`
- [x] `OUTPUT_CHANNEL_FAILURE_FAIL_CLOSED`
- [x] aucune commande `session run` ou `session execute` approuvée
- [x] aucune valeur de production inventée
