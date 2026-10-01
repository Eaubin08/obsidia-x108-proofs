# JARJAR_GOVERNANCE_HANDOFF_V0

> **Objectif** : rendre le futur passage « JarJar-governance » resumable sans re-audit.
> Ce document capture l'état, les décisions, les contrats, et la feuille de route exacte
> pour brancher la gouvernance Obsidia X-108 côté JarJar.
> **Ne pas modifier JarJar avant d'avoir suivi la checklist §9.**

---

## §1 — Découpage architectural

```
┌──────────────────────────────────────────────────────────┐
│  Couche Obsidia (OpenJarvis)                              │
│  PREPARE → EAH → approbation humaine → KX108 → Binder   │
│  ↓ physical-executor boundary ↓                          │
│  JarJarFilesystemExecutor  (bridge V0)                   │
│  ↓                                                        │
│  NativeFilesystemBackend  (JarJar)                       │
│  UserPathPolicy            (JarJar — défense en profondeur)│
│  shutil.move / Path.mkdir                                 │
└──────────────────────────────────────────────────────────┘
```

**Invariants architecturaux permanents :**

| Clé | Valeur |
|-----|--------|
| `OPENJARVIS_AUTHORITY` | `NONE` |
| `KX108_ONLY` | `YES` |
| `AUTO_EXECUTE` | `NO` |
| `HUMAN_APPROVAL_REQUIRED` | `YES` |
| `NEW_PARALLEL_MUTATION_ENGINE` | `NO` |
| `GENERIC_WRITE_FILE_ENABLED` | `NO` |
| `GENERIC_SHELL_ENABLED` | `NO` |
| `GOVERNED_DELETE_FILE` | `DEFERRED_TO_V3_DESTRUCTIVE_OPERATIONS` |

**Règle d'or** : seul KX108 décide. JarJar exécute. Obsidia governe.
JarJar n'a aucune autorité de décision — c'est un exécuteur physique borné.

---

## §2 — Composants JarJar locaux (ne pas toucher pour l'instant)

### 2a — `NativeFilesystemBackend` (`jarvis/filesystem.py`)

- `file.move(source, target)` : valide via `UserPathPolicy`, appelle `shutil.move()`, retourne `ActionResult(ok=True/False)`
- `folder.create(path)` : crée avec `parents=True` — **attention** : le bridge ajoute un pré-check `parent.exists()` pour maintenir la sémantique `parents=False` d'Obsidia
- **Contrat critique** : le champ est `ok` (bool), PAS `success`

### 2b — `UserPathPolicy` (`jarvis/filesystem.py`)

- `validate(path, strict=False)` : bloque noms sensibles, vérifie `allowed_roots`
- `allowed_roots=()` = aucune restriction (vide = falsy short-circuit)
- Le bridge passe `allowed_roots=(exec_wt,)` → borné à l'espace de travail

### 2c — `ActionRequest` / `ActionResult` (`jarvis/contracts.py`)

```python
# ActionRequest (frozen dataclass)
ActionRequest(capability, arguments, target, source, session_id, risk, idempotency_key)

# ActionResult (frozen dataclass)
ActionResult(ok, message, data, backend, started_at, finished_at, evidence_refs)
# CRITIQUE : champ = ok (bool), PAS success
```

### 2d — Composants JarJar NON utilisés par le bridge V0

| Composant | Raison d'exclusion |
|-----------|-------------------|
| `HUDController` | Présentation pure, zéro logique d'exécution |
| `CostAwareCognitionRouter` | Cognition/LLM, pas un exécuteur |
| `ObsidiaPreInferenceAdapter` | `can_act=False`, `readonly=True` — advisory only |
| `FastIntentRouter` | Produit un `ActionRequest`, n'exécute pas |
| `JarjarHUD` | Interface Tk, voice loop — hors périmètre |

---

## §3 — Chemins d'action directs actuels (inventaire)

### 3a — Ce qui EST gouverné aujourd'hui (V0–V2)

| Opération | Capability ID | Fichier |
|-----------|---------------|---------|
| Update fichier existant | `PC_GOVERNED_PREPARE` / `PC_GOVERNED_EXECUTE` | `obsidia_pc_capabilities_v1.py` |
| Create fichier nouveau | `PC_V2_CREATE_FILE_PREPARE` / `EXECUTE` | `obsidia_pc_capabilities_v2.py` |
| Move fichier | `PC_V2_MOVE_FILE_PREPARE` / `EXECUTE` | `obsidia_pc_capabilities_v2.py` |
| Apply patch | `PC_V2_APPLY_PATCH_PREPARE` / `EXECUTE` | `obsidia_pc_capabilities_v2.py` |
| Create répertoire | `PC_V2_CREATE_DIR_PREPARE` / `EXECUTE` | `obsidia_pc_capabilities_v2.py` |

### 3b — Ce qui N'est PAS encore gouverné (limites V0)

| Action JarJar | Statut |
|---------------|--------|
| window.open / UI / browser | DEFERRED — hors périmètre V0 |
| app_launch / process spawn | DEFERRED — hors périmètre V0 |
| visual capture / screenshot | DEFERRED — hors périmètre V0 |
| file delete | DEFERRED_TO_V3_DESTRUCTIVE_OPERATIONS |
| network / web requests | NON SCOPÉ |

---

## §4 — Design futur de l'adaptateur de gouvernance JarJar

### 4a — Ce que le bridge V0 prouve déjà

`scripts/jarjar_executor_bridge_v0.py` démontre :

1. `JarJarFilesystemExecutor` wrappe `NativeFilesystemBackend` avec `allowed_root` borné
2. `make_executor(repo_root)` = factory d'exécuteur borné
3. `bridge_rollback_move_file_execute(...)` = rollback V2_MOVE_FILE via JarJar
4. `self_check_bridge_v0()` = rapport d'invariants machine-vérifiable

### 4b — Injection dans V2 (PENDING — §7 de cette session)

Les 4 modifications de `obsidia_pc_capabilities_v2.py` à appliquer :

**Modification 1** — Signature `pc_v2_move_file_execute` (ligne 341–343) :
```python
# AVANT
def pc_v2_move_file_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, repo_root, session_id=""):

# APRÈS
def pc_v2_move_file_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, repo_root, session_id="", executor=None):
```

**Modification 2** — Exécution physique MOVE_FILE (ligne 369) :
```python
# AVANT (ligne 369)
    da.parent.mkdir(parents=True, exist_ok=True); os.replace(sa, da)

# APRÈS
    if executor is not None:
        _ex = executor.move_file(sa, da)
        if not _ex["ok"]:
            return _exec_rej(OP_MOVE_FILE, _CAP_MOVE_EXECUTE,
                             "JARJAR_EXECUTOR_FAILED:" + str(_ex.get("error", "")), session_id)
    else:
        da.parent.mkdir(parents=True, exist_ok=True); os.replace(sa, da)
```

**Modification 3** — Métadonnées SAR executor dans MOVE_FILE (dans le dict de retour) :
```python
# Ajouter après sealed_rollback_evidence_id dans le dict de retour :
            "executor_provider": executor.EXECUTOR_PROVIDER if executor else "OS_NATIVE",
            "executor_backend": executor.EXECUTOR_BACKEND if executor else "os.replace",
```

**Modification 4** — Signature + exécution physique CREATE_DIR (lignes 542–566) :
```python
# Signature (ligne 542–544) : ajouter executor=None
def pc_v2_create_dir_execute(
        prepared_result, human_authorized_eah, human_authorization_reference,
        *, stores_base_dir, repo_root, session_id="", executor=None):

# Exécution physique (ligne 566) :
# AVANT
    da.mkdir(parents=False, exist_ok=False)

# APRÈS
    if executor is not None:
        _ex = executor.create_dir(da)
        if not _ex["ok"]:
            return _exec_rej(OP_CREATE_DIR, _CAP_CDIR_EXECUTE,
                             "JARJAR_EXECUTOR_FAILED:" + str(_ex.get("error", "")), session_id)
    else:
        da.mkdir(parents=False, exist_ok=False)
```

### 4c — Principe de composition de politiques

```
Politique Obsidia (authoritative)
  → PREPARE/EAH/KX108 : si Obsidia refuse, JarJar n'est JAMAIS appelé
  → JarJar UserPathPolicy (défense en profondeur)
      → Si JarJar refuse : fail-closed
      → Si JarJar accepte ET Obsidia a approuvé : exécution physique
```

**Règle** : Obsidia autorise → JarJar exécute. JarJar ne valide JAMAIS la gouvernance.

---

## §5 — Mapping action → capability

| Action JarJar | Capability Obsidia | OpType V2 |
|---------------|-------------------|-----------|
| `file.move` | `PC_V2_MOVE_FILE_PREPARE` + `PC_V2_MOVE_FILE_EXECUTE` | `V2_MOVE_FILE` |
| `folder.create` | `PC_V2_CREATE_DIR_PREPARE` + `PC_V2_CREATE_DIR_EXECUTE` | `V2_CREATE_DIR` |
| `file.write` (nouveau) | `PC_V2_CREATE_FILE_PREPARE` + `PC_V2_CREATE_FILE_EXECUTE` | `V2_CREATE_FILE` |
| `file.patch` | `PC_V2_APPLY_PATCH_PREPARE` + `PC_V2_APPLY_PATCH_EXECUTE` | `V2_APPLY_PATCH` |
| `file.delete` | DEFERRED V3 | — |
| `window.*` / UI | DEFERRED hors périmètre | — |

---

## §6 — Ordre d'implémentation (JARJAR-G0 à G5)

### JARJAR-G0 (ACTUEL — en cours)
**Objectif** : prouver la substitution d'exécuteur sur `MOVE_FILE` + `CREATE_DIR`

Livrables :
- [x] `scripts/jarjar_executor_bridge_v0.py` — `JarJarFilesystemExecutor` + `make_executor` + `bridge_rollback_move_file_execute` + `self_check_bridge_v0`
- [ ] 4 modifications `obsidia_pc_capabilities_v2.py` (§4b — PENDING)
- [ ] `tests/test_jarjar_bridge_v0.py` — 13 cas de test
- [ ] Suite complète verte : V0 (22) + V1 (18) + V2 (52) + bridge (≥13)

### JARJAR-G1 (SUIVANT)
**Objectif** : brancher `GOVERNED_MOVE_FILE` depuis l'interface HUD JarJar

Pré-requis : JARJAR-G0 complété et tests verts.
Travail JarJar :
- Ajouter handler `GOVERNED_MOVE_FILE` dans le router JarJar
- Handler appelle `pc_v2_move_file_prepare()` → retourne draft à l'utilisateur
- Approbation utilisateur → appelle `pc_v2_move_file_execute(..., executor=make_executor(repo_root))`
- **NE PAS** modifier `HUDController` / cognition / voix

### JARJAR-G2
**Objectif** : `GOVERNED_CREATE_DIR` depuis HUD JarJar

Même pattern que G1 mais pour `CREATE_DIR`.

### JARJAR-G3
**Objectif** : `GOVERNED_CREATE_FILE` + `GOVERNED_APPLY_PATCH` depuis HUD JarJar

Étendre le router JarJar avec les 2 capabilities restantes.

### JARJAR-G4
**Objectif** : rollback gouverné depuis HUD JarJar

Brancher `bridge_rollback_move_file_execute()` dans le handler de rollback JarJar.
Pré-requis : G1 + stores accessibles depuis JarJar.

### JARJAR-G5 (DEFERRED)
**Objectif** : opérations destructives (delete) — V3 Obsidia requis d'abord

Ne pas implémenter avant que `GOVERNED_DELETE_FILE` soit sorti de `DEFERRED_TO_V3_DESTRUCTIVE_OPERATIONS`.

---

## §7 — Contrats à réutiliser (ne pas réimplémenter)

### 7a — Contrats Obsidia disponibles dans `scripts/`

| Module | Ce qu'il fournit |
|--------|-----------------|
| `obsidia_pc_capabilities_v2.py` | PREPARE / EXECUTE / dispatcher V2 |
| `obsidia_sealed_evidence_v0.py` | `store_sealed_apply_receipt`, `load_*`, `verify_*` |
| `obsidia_execution_driver_v0.py` | Constantes de status : `PREPARED_AWAITING_HUMAN_APPROVAL`, `EXECUTED_OK` |
| `obsidia_test_contract.py` | `build_check`, `build_test_contract`, `CHECK_TYPE_*` |
| `obsidia_capability_graph_v0.py` | `capability_ids()`, `get_capability()` — registre Binder |
| `obsidia_governed_rollback_v0.py` | Rollback V1 seulement (`UPDATE_TARGET_FROM_SOURCE`) — NE gère PAS `V2_MOVE_FILE` |
| `jarjar_executor_bridge_v0.py` | `JarJarFilesystemExecutor`, `make_executor`, `bridge_rollback_move_file_execute` |

### 7b — Contrats JarJar à utiliser (pas à réécrire)

| Symbole | Fichier JarJar | Usage |
|---------|---------------|-------|
| `NativeFilesystemBackend` | `jarvis/filesystem.py` | Instancié via `JarJarFilesystemExecutor` UNIQUEMENT |
| `UserPathPolicy` | `jarvis/filesystem.py` | Injecté dans `NativeFilesystemBackend` via bridge |
| `ActionResult.ok` | `jarvis/contracts.py` | Vérification du résultat — champ `ok`, PAS `success` |
| `ActionRequest` | `jarvis/contracts.py` | Constructeur de requête executor |

### 7c — Chemin d'import JarJar

```python
# Variable d'environnement d'override (CI / machines différentes) :
JARJAR_SRC_PATH=/chemin/vers/Jarvis-iron-obsidia-/src

# Chemin relatif par défaut (depuis scripts/) :
../../Jarvis-iron-obsidia-/src
```

---

## §8 — Prohibitions (permanentes)

Ces règles ne peuvent pas être levées sans décision architecturale explicite :

1. **NE PAS** modifier le dépôt JarJar depuis OpenJarvis
2. **NE PAS** créer un deuxième lifecycle de gouvernance (doublon de PREPARE/EAH/KX108)
3. **NE PAS** appeler `NativeFilesystemBackend` directement depuis V2 — passer obligatoirement par `JarJarFilesystemExecutor`
4. **NE PAS** permettre à JarJar de prendre des décisions de gouvernance (`can_act=False` reste la règle)
5. **NE PAS** implémenter `GOVERNED_DELETE_FILE` avant V3 Obsidia
6. **NE PAS** activer les outils shell/fichier génériques d'OpenJarvis comme autorité d'exécution
7. **NE PAS** bypasser la borne `allowed_root` du `UserPathPolicy` JarJar
8. **NE PAS** utiliser `parents=True` dans `folder.create` sans pré-check `parent.exists()` — sémantique Obsidia = `parents=False`

---

## §9 — Checklist de reprise

Pour reprendre le travail JARJAR-G0 dans une nouvelle session :

```
[ ] 1. Lire ce fichier (docs/JARJAR_GOVERNANCE_HANDOFF_V0.md)
[ ] 2. Lire scripts/jarjar_executor_bridge_v0.py
        Vérifier : self_check_bridge_v0() retourne les bons invariants
[ ] 3. Appliquer les 4 modifications §4b à obsidia_pc_capabilities_v2.py
        - Modif 1 : executor=None sur pc_v2_move_file_execute (ligne ~343)
        - Modif 2 : dispatch executor vs os.replace (ligne ~369)
        - Modif 3 : métadonnées SAR executor_provider/executor_backend dans return MOVE_FILE
        - Modif 4 : executor=None + dispatch sur pc_v2_create_dir_execute (lignes ~544, ~566)
[ ] 4. Écrire tests/test_jarjar_bridge_v0.py — 13 cas minimum (liste §10)
[ ] 5. Lancer la suite complète :
        cd obsidia-openjarvis-install-v0
        python -m pytest tests/ -v --tb=short
[ ] 6. Confirmer : V0 (22) + V1 (18) + V2 (52) + bridge (≥13) = tous verts
[ ] 7. Stager les fichiers JARJAR-G0 :
        git add scripts/jarjar_executor_bridge_v0.py
        git add scripts/obsidia_pc_capabilities_v2.py
        git add tests/test_jarjar_bridge_v0.py
        git add docs/JARJAR_GOVERNANCE_HANDOFF_V0.md
[ ] 8. git commit (ne pas push sans approbation explicite)
[ ] 9. Passer à JARJAR-G1 seulement si tous les tests sont verts
```

---

## §10 — Rapport de sortie (JARJAR-G0)

### Tests bridge requis (13 cas minimum)

| # | Cas | Assertion clé |
|---|-----|---------------|
| T01 | `self_check_bridge_v0()` invariants | `openjarvis_authority=="NONE"`, `kx108_only==True` |
| T02 | PREPARE ne déclenche pas JarJar | `kx108_invocations==0`, JarJar non importé |
| T03 | Pas d'approbation → JarJar jamais appelé | `status=="EAH_MISMATCH"`, fichier inchangé |
| T04 | Mauvais EAH → JarJar jamais appelé | `status=="EAH_MISMATCH"` |
| T05 | KX108 DENY → JarJar jamais appelé | `status` contient `KX108_PRE_GATE` |
| T06 | Workspace invalide → JarJar jamais appelé | `status=="PATH_UNSAFE"` ou traversal rejected |
| T07 | Exécution valide → exactement 1 appel JarJar | `status==EXECUTED_OK`, fichier déplacé |
| T08 | Réalized state vérifié après move | `da.exists()`, `not sa.exists()`, sha256 intact |
| T09 | Receipt identifie executor JarJar | `executor_provider=="JARJAR"` dans return |
| T10 | Rollback restaure état exact | `sa.exists()`, `not da.exists()`, sha256 == before |
| T11 | CREATE_DIR via JarJar | `status==EXECUTED_OK`, répertoire créé |
| T12 | Mutation directe JarJar non exposée | `NativeFilesystemBackend` non accessible depuis V2 sans bridge |
| T13 | Régression — caps V2 existantes inchangées | V2 sans `executor` → comportement OS natif identique |

### État des livrables

```
scripts/jarjar_executor_bridge_v0.py      CREE (session précédente)
scripts/obsidia_pc_capabilities_v2.py     PENDING (4 modifications §4b)
tests/test_jarjar_bridge_v0.py            PENDING
docs/JARJAR_GOVERNANCE_HANDOFF_V0.md      CE FICHIER
```

### Preuves de conformité à produire

```bash
# 1. Invariants bridge
python -c "import sys; sys.path.insert(0,'scripts');     from jarjar_executor_bridge_v0 import self_check_bridge_v0;     import json; print(json.dumps(self_check_bridge_v0(), indent=2))"
# Attendu : openjarvis_authority: "NONE", kx108_only: true

# 2. Suite de tests complète
python -m pytest tests/ -v --tb=short
# Attendu : 0 failures

# 3. Périmètre git
git diff --stat HEAD
# Attendu : seuls les fichiers JARJAR-G0 modifiés
```

---

*Généré le 2026-10-01 — Session JarJarExecutorBridge V0 — Etienne Aubin*
