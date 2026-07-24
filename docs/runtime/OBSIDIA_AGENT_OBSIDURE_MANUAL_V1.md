# AGENT OBSIDURE — Manuel Opérateur V1
**Statut** : `ACTIVE_CLI_MODE`  
**Agents fusionnés** : CO_PILOTE_CODE (#6) × CI_REPO_SURGEON (#7)  
**Rôle** : Bâtisseur et Brancheur périphérique Obsidia X-108  
**Fichier source** : `periphery/agents/agent_obsidure.py`  
**Date** : 2026-06-25  

> **Pour l'opérateur humain (ROLE_005).**  
> Ce manuel couvre le lancement, la mécanique interne, les pistes d'amélioration UX, et la traçabilité SRL.

---

## TABLE DES MATIÈRES

1. [Commandes de lancement et d'utilisation](#1-commandes-de-lancement-et-dutilisation)
2. [Comment fonctionne Obsidure — mécanique interne](#2-comment-fonctionne-obsidure--mécanique-interne)
3. [Idées d'amélioration UX et fonctionnalités](#3-idées-damélioration-ux-et-fonctionnalités)
4. [Traçabilité avancée des sessions — intégration SRL](#4-traçabilité-avancée-des-sessions--intégration-srl)

---

## 1. Commandes de lancement et d'utilisation

### Prérequis

```
Python 3.10+  dans le PATH
repo root     C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B
API optionnelle http://127.0.0.1:8000  (mode offline si absente)
```

### 1.1 Lancer toute la stack (Kernel + API)

Avant de lancer Obsidure avec connexion à OS_TRAD_REVERSE, démarrer les serveurs :

```powershell
# Depuis le repo root — ouvre 2 terminaux séparés
powershell -ExecutionPolicy Bypass -File "scripts\runtime\start_obsidia_stack.ps1"

# Forcer le redémarrage si déjà en cours
powershell -ExecutionPolicy Bypass -File "scripts\runtime\start_obsidia_stack.ps1" -ForceRestart

# Vérifier l'état de la stack sans relancer
powershell -ExecutionPolicy Bypass -File "scripts\runtime\status_obsidia_stack.ps1"
```

> **Ports** : Kernel X-108 → `3001` | API FastAPI → `8000`

---

### 1.2 Mode interactif simple (recommandé pour débuter)

```powershell
# Via le launcher PowerShell (recommandé)
.\scripts\run_agent_obsidure.ps1

# Via Python directement
python scripts\obsidure_cli.py
```

L'agent affiche la bannière, les frontières de sécurité actives, puis attend un objectif :

```
[OBSIDURE] Objectif > Créer le gate Bank P3-01
```

Commandes spéciales en mode interactif :

| Commande  | Effet |
|-----------|-------|
| `status`  | Phase courante, cycles, nombre de proposals |
| `srl`     | Résumé des 4 strates mémoire (lecture seule) |
| `domains` | Audit des gates P3 Bank / Trading / GPS / ECOM |
| `boundary`| Affiche les frontières de sécurité immuables |
| `quit`    | Arrêt propre |

---

### 1.3 Objectif direct en paramètre (mode non-interactif)

```powershell
# Gate Bank P3-01
.\scripts\run_agent_obsidure.ps1 -Objective "Créer le gate bank P3-01" -Domain BANK

# Nuisance registry Trading
.\scripts\run_agent_obsidure.ps1 -Objective "Créer le nuisance registry Trading P3-04" -Domain TRADING

# Connecteur GPS
.\scripts\run_agent_obsidure.ps1 -Objective "Brancher aviation_robo.py pour GPS" -Domain GPS

# Limiter à 1 cycle
.\scripts\run_agent_obsidure.ps1 -Objective "Audit connecteurs Bank" -MaxCycles 1
```

Équivalent Python :

```powershell
python scripts\obsidure_cli.py --objective "Créer le gate bank P3-01" --domain BANK
python scripts\obsidure_cli.py --objective "Créer le nuisance registry Trading P3-04" --domain TRADING --max-cycles 1
```

---

### 1.4 Cible mathématique Lean 4

```powershell
# Via PowerShell
.\scripts\run_agent_obsidure.ps1 -Objective "Créer théorème périphérique P107 monotonie décision" -Domain LEAN

# Via Python
python scripts\obsidure_cli.py --objective "Théorème Lean P107 sur la garde temporelle beforeTau" --domain LEAN
```

> Obsidure lit d'abord `proofs/lean/Obsidia/Basic.lean` et `TemporalKernel.lean` en **read-only** pour constituer son contexte mathématique, puis génère le théorème en sandbox avec `lake build`.

---

### 1.5 Mode audit seul (dry-run — aucun fichier créé)

```powershell
# PowerShell
.\scripts\run_agent_obsidure.ps1 -Objective "Analyser les connecteurs GPS" -DryRun

# Python
python scripts\obsidure_cli.py --objective "Analyser connecteurs GPS" --dry-run
```

> En dry-run, l'agent interroge OS_TRAD_REVERSE et affiche `intent` + `risk_flags`, mais ne crée ni sandbox ni proposal.

---

### 1.6 Mode silencieux (logs minimaux)

```powershell
.\scripts\run_agent_obsidure.ps1 -Objective "Créer gate Bank" -Domain BANK -Quiet
python scripts\obsidure_cli.py --objective "Créer gate Bank" --domain BANK --quiet
```

---

### 1.7 Codes de sortie

| Code | Signification |
|------|---------------|
| `0`  | Cycle AVDR terminé — proposal émis avec succès |
| `2`  | **BLOC ABSOLU** — chemin protégé détecté (`ProtectedPathError`) |
| `3`  | **FAIL-CLOSED** — backup pré-modification échoué (`BackupFailedError`) |
| `4`  | Erreur non anticipée |

---

### 1.8 Où trouver les résultats

Chaque cycle produit un dossier dans `_PATCH_PROPOSALS/<uuid>/` :

```
_PATCH_PROPOSALS/
  <uuid>/
    proposal.json    ← données complètes (patches, OS_TRAD, stabilisation, SRL card)
    RECEIPT.md       ← rapport lisible par l'opérateur (ROLE_005)
```

Les fichiers générés dans la sandbox éphémère sont dans :

```
_EPHEMERAL_CODE_SANDBOX_<timestamp>/
```

> **Aucun de ces fichiers n'est appliqué automatiquement au repo.** L'opérateur copie manuellement les fichiers approuvés, puis fait `git add` + `git commit`.

---

## 2. Comment fonctionne Obsidure — mécanique interne

### 2.1 La boucle A.V.D.R.

Obsidure exécute un cycle en 4 phases séquentielles et non-inversibles :

```
┌─────────────────────────────────────────────────────────────┐
│  A — AUDIT                                                  │
│  Lit l'objectif. Interroge OS_TRAD_REVERSE pour traduire    │
│  l'intention en alphabet Obsidia (intent, constraints,      │
│  risk_flags). Lit en READ-ONLY le kernel + preuves Lean     │
│  pour constituer un contexte mathématique de référence.     │
├─────────────────────────────────────────────────────────────┤
│  V — VALIDATION (Fail-Closed)                               │
│  Crée un backup des fichiers à modifier AVANT tout.         │
│  Si le backup échoue → arrêt immédiat (BackupFailedError).  │
│  Les fichiers lus en read-only NE sont PAS backupés.        │
├─────────────────────────────────────────────────────────────┤
│  D — DISRUPTION (boucle de stabilisation)                   │
│  Génère le code / théorème Lean dans une sandbox éphémère.  │
│  TESTE la conformité contre les lois du Kernel.             │
│  Si violation → auto-correction et nouvelle tentative.      │
│  Si stable → sort de la boucle (max 3 tentatives).          │
├─────────────────────────────────────────────────────────────┤
│  R — RÉINTÉGRATION                                          │
│  Émet le PATCH_PROPOSAL (JSON + RECEIPT.md).                │
│  Attend HUMAN_APPROVED_WRITE. Ne commit rien.               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 La boucle de stabilisation interne (Phase D)

C'est le mécanisme clé d'autonomie d'Obsidure :

```
Tentative 1 → génère le code → teste conformité
    │ PASS → sort de la boucle → Phase R
    │ FAIL (ex: lake build échoue, keyword interdit)
    ↓
Tentative 2 → auto-correction (sanitiseur + fallback Lean) → teste conformité
    │ PASS → sort de la boucle → Phase R
    │ FAIL
    ↓
Tentative 3 (max) → meilleure version disponible → Phase R quand même
```

**Tests de conformité exécutés à chaque tentative :**

| Type de violation | Détection | Correction automatique |
|---|---|---|
| `LEAN_BUILD_ERROR` | `lake build` retourne une erreur | Bascule vers théorème trivial `True := by trivial` |
| `FORBIDDEN_KEYWORD` | `git commit/push`, `kernel_mutation=True`, etc. | Sanitiseur supprime / remplace |
| `PROTECTED_PATH_WRITE_REF` | Référence en écriture vers un chemin scellé | Erreur remontée — jamais corrigée automatiquement |
| `KERNEL_LOGIC_REPLICA` | Fonction `decide` avec ALLOW/HOLD/BLOCK | Contexte d'erreur injecté dans la prochaine génération |

### 2.3 OS_TRAD_REVERSE — les yeux d'Obsidure

Sans OS_TRAD_REVERSE, Obsidure serait aveugle sur l'intention réelle de l'objectif. Le traducteur transforme un texte libre en structure formelle :

```
"Créer le gate bank P3-01"
        ↓  POST /api/os-trad/translate
alphabet_units, detected_language, risk_flags
        ↓  POST /api/ir/candidate
intent = "CREATE_PATCH"
constraints = ["P3-01", "BANK", "ALLOW/HOLD/BLOCK"]
target_paths = ["domains/bank/bank_x108_gate.py"]
```

Si l'API est hors ligne, Obsidure bascule sur une analyse locale heuristique (mode `OFFLINE`) et continue.

### 2.4 Le Mur du Kernel — la loi absolue

Le Kernel X-108 est **immuable**. Il ne change pas. Il n'évolue pas. Il juge.

Tout appel à Obsidure qui tenterait de modifier les fichiers scellés déclenche une `ProtectedPathError` immédiate et un arrêt avec code `2` :

```python
PROTECTED_INFIXES = (
    "server.kernel.sealed.cjs",   # Kernel Node.js scellé
    "proofs/V18_",                # 18 preuves canoniques
    "proofs/lean/57_preuves",     # 57 preuves Lean scellées
    "merkle_seal.json",           # Ancre Merkle
    "rfc3161",                    # Horodatage RFC3161
)
```

La **lecture** de ces fichiers est légale (Phase A) — c'est leur seule contribution à Obsidure : servir de boussole mathématique par le refus.

### 2.5 Frontières immuables

Ces valeurs sont gelées au démarrage et vérifiées avant chaque phase :

```python
kernel_mutation   = False   # JAMAIS
x108_merge        = False   # JAMAIS
emits_act         = False   # JAMAIS
allowed_to_decide = False   # JAMAIS
sandbox_mode      = "HUMAN_APPROVED_WRITE"
```

Si une de ces valeurs est altérée à l'exécution → `ImmutableBoundaryError` → arrêt.

---

## 3. Idées d'amélioration UX et fonctionnalités

### Idée 1 — Historique des objectifs avec rappel (`--history`)

**Problème actuel :** En mode interactif, l'opérateur retape ses objectifs à chaque session.

**Proposition :** Persister l'historique des objectifs dans `periphery/brody_memory_readonly/ACTIVE/obsidure_history.jsonl` (une ligne JSON par entrée). Ajouter une commande `history` en mode interactif et un flag `--history N` pour réafficher les N derniers objectifs.

```powershell
# Voir les 10 derniers objectifs
python scripts\obsidure_cli.py --history 10

# Relancer le dernier objectif
python scripts\obsidure_cli.py --replay-last
```

**Contrainte :** L'écriture de l'historique est un PATCH_PROPOSAL comme les autres — pas une écriture directe.

---

### Idée 2 — Affichage "Rich" des diffs dans le terminal

**Problème actuel :** Le RECEIPT.md est lisible mais nécessite d'ouvrir un fichier externe.

**Proposition :** Ajouter une dépendance optionnelle `rich` (déjà commun dans l'écosystème Python) pour afficher directement dans le terminal :
- Un tableau coloré des patches proposés (vert = CREATE, jaune = REVIEW)
- Un diff visuel côte-à-côte (avant/après) pour les fichiers modifiés
- Un bandeau de statut de la boucle de stabilisation (tentative N/3, violations)

```powershell
# Activer l'affichage rich (si rich installé)
python scripts\obsidure_cli.py --objective "Gate Bank" --rich
```

**Avantage :** L'opérateur voit immédiatement si la stabilisation a réussi sans ouvrir un fichier.

---

### Idée 3 — Watchdog de cohérence Lean (`--lean-watch`)

**Problème actuel :** Obsidure génère un théorème, tente `lake build`, mais si `lake` est absent la vérification est impossible.

**Proposition :** Un mode `--lean-watch` qui surveille le dossier `_PATCH_PROPOSALS/` et déclenche automatiquement `lake build` dès qu'un nouveau `.lean` y apparaît. Résultat enregistré dans `lean_build_result.json` à côté du RECEIPT.md.

```powershell
# Lancer le watchdog en arrière-plan
python scripts\obsidure_cli.py --lean-watch &
```

**Complément :** Ajouter un indicateur `lean_verified: true/false` dans le RECEIPT.md final.

---

### Idée 4 — Mode `--explain` (audit sans génération + rapport pédagogique)

**Problème actuel :** L'opérateur ne sait pas toujours pourquoi Obsidure a classé un objectif en `LEAN_SANDBOX` plutôt que `CREATE_PATCH`.

**Proposition :** Un mode `--explain` qui affiche le raisonnement complet d'Obsidure avant toute génération :
- Objectif reçu → alphabet OS_TRAD → intent détecté → domaine détecté
- Contexte mathématique chargé (quels fichiers, quels théorèmes de référence)
- Règles de conformité qui s'appliqueront
- Estimation du nombre de tentatives nécessaires

```powershell
python scripts\obsidure_cli.py --objective "Théorème P107 garde temporelle" --explain
```

Ce mode est 100% read-only — aucune sandbox, aucun proposal. Idéal pour comprendre avant d'agir.

---

## 4. Traçabilité avancée des sessions — intégration SRL

### 4.1 Architecture cible : SessionCard automatique

Chaque lancement d'Obsidure doit laisser une trace dans la **Session Registry Layer (SRL)** — la mémoire long terme d'Obsidia. Actuellement, la `SessionCard` est générée mais n'est pas écrite automatiquement (`memory_write=False`). Elle est jointe au PATCH_PROPOSAL pour application manuelle.

**Concept d'intégration complète :**

```
Lancement Obsidure
       ↓
Phase A : OS_TRAD + contexte math
       ↓
SRL → créer une SessionCard CANDIDATE
      {
        tier: "ACTIVE",
        domain: "BANK",
        objective: "Créer gate bank P3-01",
        cycle_id: "<uuid>",
        stabilization_attempts: 2,
        final_status: "STABILIZED",
        kernel_violations_detected: ["FORBIDDEN_KEYWORD"],
        lean_build: "BUILD_SUCCESS",
        created_at: "2026-06-25T..."
      }
       ↓
Phase R : PATCH_PROPOSAL contient la SessionCard
       ↓
Opérateur approuve → écrit la card dans SRL/ACTIVE/
```

### 4.2 Les 4 strates SRL et leur signification pour Obsidure

| Strate | Durée de vie | Ce qu'elle contient |
|---|---|---|
| `ACTIVE` | < 24h | Sessions en cours, proposals non encore appliqués |
| `SEMI_ACTIVE` | 1–30 jours | Cycles appliqués avec succès, gates créés, Lean compilé |
| `COLD` | > 30 jours | Archives — gates stables, théorèmes intégrés dans V18 |
| `GHOST_SIDE_TABLE` | Permanent | Tentatives rejetées par le Kernel, violations de frontière — **rien n'est effacé** |

### 4.3 La Ghost Memory — traçabilité des refus

Quand Obsidure détecte une violation de frontière (code de sortie `2`) ou échoue sur les 3 tentatives de stabilisation, la SessionCard est automatiquement classée en `GHOST_SIDE_TABLE` avec la raison du rejet :

```json
{
  "tier": "GHOST_SIDE_TABLE",
  "ghost_reason": "MAX_ATTEMPTS_REACHED",
  "kernel_violations": [
    {"type": "LEAN_BUILD_ERROR", "details": "unknown identifier 'decideX108'"},
    {"type": "LEAN_BUILD_ERROR", "details": "unknown identifier 'decideX108'"},
    {"type": "LEAN_BUILD_ERROR", "details": "unknown identifier 'decideX108'"}
  ],
  "lean_fallback_used": true,
  "note": "3 tentatives épuisées — version triviale émise pour review humaine"
}
```

**Principe Ghost Memory :** Un rejet n'est jamais perdu. Il constitue une information sur ce qu'il ne faut **pas** tenter, et peut être réactivé si le contexte change (ex : imports Lean mis à jour, nouveau theorème de référence disponible).

### 4.4 Concept de promotion de strate

Les SessionCards progressent dans les strates selon les décisions de l'opérateur :

```
ACTIVE (proposal émis)
    ↓ opérateur approuve et applique
SEMI_ACTIVE (gate créé, testé)
    ↓ gate stable depuis > 30 jours
COLD (archive long terme)

ACTIVE (proposal émis)
    ↓ opérateur rejette ou Kernel bloque
GHOST_SIDE_TABLE (rejet permanent — consultable, jamais supprimé)
```

La commande `srl` en mode interactif affiche le comptage actuel de chaque strate :

```
[OBSIDURE] Objectif > srl

  Mémoire SRL (lecture seule) :
    ACTIVE               : 3 fichier(s)
    SEMI_ACTIVE          : 12 fichier(s)
    COLD                 : 47 fichier(s)
    GHOST_SIDE_TABLE     : 8 fichier(s)
    memory_write : False (invariant permanent)
```

### 4.5 Fichier de traçabilité opérateur recommandé

Pour un suivi manuel en attendant l'automatisation SRL complète, maintenir ce fichier :

```
periphery/brody_memory_readonly/ACTIVE/OBSIDURE_SESSION_LOG.md
```

Format suggéré par session :

```markdown
## 2026-06-25 — Cycle #3 — Gate Bank P3-01

- Objectif : Créer le gate bank P3-01
- Intent détecté : CREATE_PATCH (BANK)
- Stabilisation : STABILIZED (2/3 tentatives)
- Violation détectée T1 : FORBIDDEN_KEYWORD → sanitisé
- Violation détectée T2 : aucune → PASS
- Proposal : _PATCH_PROPOSALS/<uuid>/RECEIPT.md
- Statut opérateur : APPROUVÉ → appliqué le 2026-06-25
- SRL cible : SEMI_ACTIVE (gate testé et stable)
```

---

## ANNEXE — Rappel des fichiers clés

| Fichier | Rôle |
|---|---|
| `periphery/agents/agent_obsidure.py` | Source unique de vérité — toute la logique AVDR |
| `scripts/obsidure_cli.py` | Point d'entrée CLI (args, bannière, boucle interactive) |
| `scripts/run_agent_obsidure.ps1` | Launcher PowerShell avec paramètres typés |
| `scripts/runtime/start_obsidia_stack.ps1` | Démarre Kernel (3001) + API (8000) |
| `_PATCH_PROPOSALS/<uuid>/RECEIPT.md` | Rapport lisible par ROLE_005 après chaque cycle |
| `_EPHEMERAL_CODE_SANDBOX_<ts>/` | Sandbox éphémère — code généré avant approbation |
| `periphery/brody_memory_readonly/` | Racine SRL — lecture seule pour Obsidure |

---

*Document généré par Agent Obsidure / CO_PILOTE_CODE #6 × CI_REPO_SURGEON #7*  
*Kernel X-108 = MUR DE BÉTON INTOUCHABLE — kernel_mutation: False, permanent*
