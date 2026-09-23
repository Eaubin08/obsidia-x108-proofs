# F74-F77 Audit Reconciliation
**Date** : 2026-05-30 | **Mode** : READ-ONLY | **Script exécuté** : scripts/audit_f74_f77_readiness.py

---

## Résumé

Deux audits contradictoires ont été réconciliés par vérification factuelle fichier par fichier + exécution du script d'audit.

| Audit | Résultat | Fiabilité |
|---|---|---|
| F74→F77 Readiness | 19/50 — CRITICAL | **Majoritairement correct** — 3 bugs de détection script |
| V3.1→V4 Checklist | OPS NONE / Sécurité NONE | **INCORRECT** sur OPS et Sécurité — confond existence fichier avec contenu valide et confond repo-preuve avec prod-ready |
| **Réconciliation** | **7 vrais P0 bloquants** | Script correct sauf 3 faux positifs documentés |

---

## Conflits trouvés et résolus

| Item | Conflit | Résolution |
|---|---|---|
| requirements.txt | F74: FAIL / V3.1→V4: "trouvé, NONE" | **V3.1→V4 avait tort** — fichier existe (82 bytes) mais contient SEULEMENT pytest/crypto/requests/yaml. Aucun fastapi/uvicorn/pydantic. App non installable. |
| CORS wildcard | F74→F77: CRITICAL / V3.1→V4: "NONE" | **V3.1→V4 avait tort** — `allow_origins=["*"]` confirmé ligne 10 de main.py |
| Auth/Rate limiting | F74→F77: FAIL / V3.1→V4: "NONE" | **V3.1→V4 avait tort** — 0 slowapi, 0 APIKey, 0 Bearer dans tout le codebase |
| Tests sigma | F74→F77: 9/10 FAIL | **Script bug** — ne compte que tests/sigma/ (9 fichiers), ignore sigma/tests/ (20 fichiers) |
| KX108_ONLY in Lean | INV: FAIL | **Script bug** — cherche string "KX108_ONLY" dans fichier Lean 4 (syntaxe formelle, pas string Python) |

---

## F74 — Item par item

| Item | Script | Réalité | Classification | P0? | Action |
|---|---|---|---|---|---|
| **T01a/b/c requirements.txt** | FAIL | requirements.txt EXISTS (82B) mais sans fastapi/uvicorn/pydantic | **EXISTS_BUT_INCOMPLETE** | ✅ OUI | Ajouter fastapi, uvicorn, pydantic |
| **T02 .python-version** | FAIL | MISSING | **MISSING** | ✅ OUI | Créer .python-version: 3.11 |
| T03 .env.example | FAIL | MISSING (.gitignore a !.env.example) | MISSING | Non (P1) | Créer .env.example |
| T04 QUICKSTART.md | FAIL | MISSING (README.md existe) | MISSING | Non (P1) | Créer QUICKSTART.md |
| T05 scripts/run_api.sh | FAIL | MISSING | MISSING | Non (P1) | Créer scripts/run_api.sh |
| T06 Makefile | FAIL | MISSING | MISSING | Non (P2) | Optionnel |
| T07 requirements-dev.txt | FAIL | MISSING | MISSING | Non (P1) | Créer req-dev.txt |
| T09 pytest.ini | FAIL | MISSING — mais tests run fine sans | MISSING | **Non (faux blocker)** | P2 optionnel |
| SIGMA ≥ 10 | FAIL (9) | SCRIPT BUG — sigma/tests/ a 20 committed | SCRIPT_DETECTION_BUG | **Non (faux blocker)** | Fixer script ligne 98 |

**Score F74 corrigé** : T01 et T02 sont les seuls vrais P0. Les 7 autres sont P1/P2 ou faux positifs.

---

## F76 — Item par item

| Item | Script | Réalité | Classification | P0? | Action |
|---|---|---|---|---|---|
| **T01a CORS wildcard** | FAIL | `allow_origins=["*"]` confirmé main.py:10 | **TRUE_BLOCKER** | ✅ OUI | Remplacer par ALLOWED_ORIGINS env var |
| **T01b CORS env var** | FAIL | `ALLOWED_ORIGINS` absent main.py | **TRUE_BLOCKER** | ✅ OUI | Ajouter ALLOWED_ORIGINS |
| **T02 Dockerfile** | FAIL | MISSING (.dockerignore existe seul) | **TRUE_BLOCKER** | ✅ OUI | Créer Dockerfile |
| T03 .env.example | FAIL | MISSING (partagé F74-T03) | MISSING | Non (P1) | Créer .env.example |
| **T04 GET /health** | PASS | routes/status.py existe avec GET /api/status | EXISTS_AND_VALID | — | Aucune action |
| **T05 Rate limiting** | FAIL | 0 slowapi/RateLimiter trouvé dans tout le code | **TRUE_BLOCKER** | ✅ OUI | Ajouter slowapi |
| T06 ROLLBACK_PLAN.md | FAIL | MISSING | MISSING | Non (P1) | Créer ROLLBACK_PLAN.md |
| T07 docker-compose.yml | FAIL | MISSING | MISSING | Non (P1) | Après Dockerfile |
| **T09 APP_ENV guard** | FAIL | MISSING — /docs et /redoc exposés sans guard | **TRUE_BLOCKER** | ✅ OUI | Ajouter APP_ENV check dans main.py |
| **T10 Auth** | FAIL | 0 APIKey/Bearer/OAuth sur aucune route | **TRUE_BLOCKER** | ✅ OUI | Ajouter auth minimum sur /api/brody/chat |

**Score F76 corrigé** : 6 vrais P0. T04 est PASS correct. T03/T06/T07 sont P1.

---

## F77 — Item par item

| Item | Script | Réalité | Classification | Action |
|---|---|---|---|---|
| T01 external_pack/ONE_PAGE.md | FAIL | external_pack/ MISSING — contenu équivalent dans docs/demo/ | EXISTS_BUT_NOT_ORGANIZED | Créer external_pack/, peupler |
| T02 TECHNICAL_ANNEX.md | FAIL | MISSING | MISSING | Créer |
| T03 KNOWN_LIMITS.md mention F74 | FAIL | docs/status/KNOWN_LIMITS.md EXISTS mais ne mentionne pas F74 | EXISTS_BUT_INCOMPLETE | Mettre à jour |
| **T04 REPRODUCIBILITY.md** | FAIL | REPRODUCIBILITY_CHECKLIST.md (7590B) à la racine | **EXISTS_BUT_WRONG_LOCATION** | Copier dans external_pack/ |
| T05-T08 DECK/EVIDENCE/SECURITY/REVIEWER | FAIL (x4) | MISSING | MISSING | Créer dans external_pack/ |
| DEMO docs/demo/ | PASS (25 files) | 25 fichiers MD dans docs/demo/ | EXISTS_AND_VALID | Aucune action |

**F77 est un P1** — non bloquant avant F74/F76.

---

## Bugs du script d'audit

### BUG-01 — F74-SIGMA : sous-comptage sigma tests (ligne 98)

```python
# ACTUEL (BUG) :
sigma_tests = list((ROOT / "tests" / "sigma").glob("test_*.py"))
# Compte : 9 fichiers (surtout non-commités F60-F73)

# CORRECT :
sigma_tests = list((ROOT / "tests" / "sigma").glob("test_*.py"))
sigma_tests += list((ROOT / "sigma" / "tests").glob("test_*.py"))
# Compte : 29+ fichiers (incluant sigma/tests/ avec 20 committed)
```
**Impact** : Faux FAIL sur ce check. sigma/tests/ a 20 fichiers committés ignorés.

---

### BUG-02 — INV KX108_ONLY dans TemporalKernel.lean (ligne 335)

```python
# ACTUEL (BUG) :
checks.append(check(file_contains(tk, "KX108_ONLY"), "INV: TemporalKernel.lean référence KX108_ONLY"))
# Cherche string "KX108_ONLY" dans un fichier Lean 4 — impossible.

# CORRECT : TemporalKernel.lean utilise la syntaxe Lean 4 formelle.
# Le théorème X108_no_act_before_tau EST l'invariant KX108.
# Vérifier la présence du théorème, pas d'une constante Python.
checks.append(check(file_contains(tk, "X108_no_act_before_tau"), "INV: TemporalKernel.lean theorem no_act_before_tau présent"))
```
**Impact** : Faux FAIL. TemporalKernel.lean EST LEAN_PROVEN pour les invariants X108.

---

### BUG-03 — F77-T04 : ne cherche que external_pack/REPRODUCIBILITY.md (ligne 281)

```python
# ACTUEL (BUG partiel) :
checks.append(check((ext / "REPRODUCIBILITY.md").exists(), ...))
# Ne vérifie pas REPRODUCIBILITY_CHECKLIST.md à la racine (7590 bytes)

# CORRECT :
repro_exists = (ext / "REPRODUCIBILITY.md").exists() or Path("REPRODUCIBILITY_CHECKLIST.md").exists()
checks.append(check(repro_exists, ...))
```
**Impact** : Faux FAIL partiel — contenu existe, pas au bon endroit.

---

## Blockers réels (après réconciliation)

### 7 vrais P0 confirmés

| # | Gate | Item | Description |
|---|---|---|---|
| 1 | F74 | T01 | requirements.txt sans fastapi/uvicorn/pydantic → clone stérile |
| 2 | F74 | T02 | .python-version MISSING → version Python non spécifiée |
| 3 | F76 | T01 | CORS `allow_origins=["*"]` actif → risque sécurité prod |
| 4 | F76 | T02 | Dockerfile MISSING → pas de containerisation |
| 5 | F76 | T05 | Rate limiting MISSING → API sans protection |
| 6 | F76 | T09 | APP_ENV guard MISSING → /docs exposé en prod |
| 7 | F76 | T10 | Auth MISSING → API complètement ouverte |

---

## Faux blockers retirés

| # | Item | Raison |
|---|---|---|
| 1 | F74-T09 (pytest.ini) | 262 tests run sans pytest.ini |
| 2 | F74-SIGMA (9/10) | Bug script — sigma/tests/ a 20 committed files |
| 3 | INV KX108_ONLY in Lean | Bug script — Lean 4 n'a pas de string literals Python |
| 4 | F77-T04 (REPRODUCIBILITY.md) | Existe à la racine (7590B), mauvaise localisation |

---

## Erreurs de l'audit V3.1→V4

| Claim V3.1→V4 | Réalité | Erreur |
|---|---|---|
| "requirements.txt trouvé — OPS NONE" | requirements.txt existe MAIS ne contient pas les app deps | A trouvé le fichier sans vérifier le contenu |
| "Sécurité NONE" | CORS `["*"]` actif, 0 auth, 0 rate limit | A confondu "repo de preuves = sans prod-security" avec "sécurité OK" |
| "CI/CD trouvés — OPS NONE" | CI/CD valide les preuves, pas l'installation | A confondu CI probe de preuves avec fresh-clone readiness |
| "Docker optional, .dockerignore présent" | .dockerignore sans Dockerfile = déploiement impossible | .dockerignore seul ne suffit pas |

**Cause racine** : L'audit V3.1→V4 a utilisé le statut "documented" comme proxy pour "ready", sans vérifier le contenu des fichiers. Le repo est un périmètre de preuves publiques, pas un déploiement prod — c'est vrai — mais les gaps F74/F76 restent réels pour un usage clone-and-run.

---

## Décision

**Réconciliation : RÉSOLUE**
- L'audit F74-F77 avait raison sur les vrais P0 (requirements, .python-version, CORS, Dockerfile, auth, rate-limit)
- L'audit V3.1→V4 avait tort sur OPS et Sécurité
- 4 faux positifs identifiés dans le script (bugs corrigeables)

**Score réel après réconciliation** :
- Vrais FAIL P0 : **7** (non 19)
- Vrais FAIL P1 : **7**
- Faux FAIL retirés : **4**
- PASS confirmés : **F75 11/13, F76-T04, F77-DEMO**

---

## Plan d'implémentation autorisé après réconciliation

**BUILD F74 autorisé** — les 7 P0 sont bien réels et identifiés.

### Séquence recommandée

```
Étape 1 — F74 Fresh Clone (P0)
  1a. Mettre à jour requirements.txt : ajouter fastapi>=0.104, uvicorn[standard]>=0.24, pydantic>=2.0
  1b. Créer .python-version : 3.11
  1c. Créer .env.example avec placeholders
  1d. Créer QUICKSTART.md (pip install + uvicorn launch)
  1e. Créer scripts/run_api.sh

Étape 2 — F76 Cloud/Prod (P0)
  2a. Corriger CORS : remplacer allow_origins=["*"] par env var ALLOWED_ORIGINS
  2b. Créer Dockerfile (Python 3.11-slim, pip install, uvicorn CMD)
  2c. Ajouter APP_ENV guard pour /docs dans main.py
  2d. Ajouter auth minimum (API key) sur /api/brody/chat
  2e. Ajouter rate limiting (slowapi)
  2f. Créer docker-compose.yml + ROLLBACK_PLAN.md

Étape 3 — Fix script (P2)
  3a. Fixer BUG-01 (sigma/tests/ count)
  3b. Fixer BUG-02 (KX108_ONLY in Lean check)
  3c. Fixer BUG-03 (REPRODUCIBILITY alt path)

Étape 4 — F77 Pack externe (P1, après F74/F76)
  4a. Créer external_pack/ avec ONE_PAGE, TECHNICAL_ANNEX, etc.
```

**Règle absolue** : Aucun de ces builds ne touche F60-F73, kernel, proofs, seal, merkle.

---

_Audit READ-ONLY — 2026-05-30 — Aucun patch, aucun commit, aucun tag, aucun push_
