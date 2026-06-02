# F74–F77 Risk Register

**Date :** 2026-05-30  
**Mode :** READ-ONLY audit — aucune implémentation  
**Invariant :** decision_authority=KX108_ONLY · readonly=true · commit=NO · push=NO  
**Auteur :** Audit automatisé (Claude Code)

---

## Légende

| Champ | Valeurs possibles |
|---|---|
| Sévérité | `CRITICAL` `HIGH` `MEDIUM` `LOW` |
| Catégorie | `SECURITY` `REPRO` `FORMAL` `CLOUD` `PACK` `CI` `DOC` |
| Statut | `OPEN` `MITIGATED` `ACCEPTED` `RESOLVED` |
| Palier | `F74` `F75` `F76` `F77` `GLOBAL` |

---

## Risques CRITICAL

### RR-01 — CORS wildcard en production

| Champ | Valeur |
|---|---|
| **ID** | RR-01 |
| **Palier** | F76 |
| **Sévérité** | CRITICAL |
| **Catégorie** | SECURITY |
| **Statut** | OPEN |
| **Fichier** | `apps/obsidia_api/main.py:10` |

**Description :**  
`allow_origins=["*"]` autorise n'importe quel domaine à appeler l'API via un navigateur. En environnement de démonstration ou de production, cela expose toutes les routes (y compris `/brody/chat` et `/bus/signal`) à des origines arbitraires.

**Impact :**  
- N'importe quel site web peut faire des requêtes cross-origin vers l'API
- Routes Brody et Bus accessibles depuis `evil.com`
- Violation des politiques de sécurité web standard

**Mitigation actuelle :**  
Aucune. Le wildcard est la configuration active.

**Risque résiduel sans action :**  
Exposition complète. Bloquant pour toute démonstration externe ou déploiement.

**Action recommandée (F76-T01) :**  
```python
allow_origins=os.environ.get("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
```

**Deadline :** Avant toute démo externe — P0_BLOCKER

---

### RR-02 — Authentification absente sur toutes les routes

| Champ | Valeur |
|---|---|
| **ID** | RR-02 |
| **Palier** | F76 |
| **Sévérité** | CRITICAL |
| **Catégorie** | SECURITY |
| **Statut** | OPEN |
| **Fichier** | `apps/obsidia_api/routes/*.py` |

**Description :**  
Aucun mécanisme d'authentification (APIKey, Bearer token, OAuth, JWT) n'est implémenté sur aucune route. Les routes `/brody/chat`, `/bus/signal`, `/bus/bridge` sont accessibles sans aucune credential.

**Impact :**  
- Accès illimité à Brody (LLM) — coût potentiel illimité si exposé publiquement
- `/bus/signal` peut recevoir des signaux arbitraires
- Aucun audit trail d'accès par utilisateur

**Mitigation actuelle :**  
Aucune. Audit grep confirme : aucun `APIKey|HTTPBearer|OAuth|JWT` en dehors des commentaires et fichiers de test.

**Risque résiduel sans action :**  
Critique pour tout déploiement non-localhost. Acceptable uniquement en démo locale contrôlée.

**Action recommandée (F76-T10) :**  
APIKey minimal sur `/brody/` avant exposition publique. Documenter l'état dans `.env.example` et `SECURITY_NOTES.md`.

**Deadline :** Avant déploiement public — P3_LATER (acceptable pour démo locale)

---

### RR-03 — requirements.txt incomplet — API ne démarre pas sur clone propre

| Champ | Valeur |
|---|---|
| **ID** | RR-03 |
| **Palier** | F74 |
| **Sévérité** | CRITICAL |
| **Catégorie** | REPRO |
| **Statut** | OPEN |
| **Fichier** | `requirements.txt` |

**Description :**  
`fastapi`, `uvicorn[standard]`, et `pydantic>=2.0` sont absents de `requirements.txt`. Ces dépendances sont requises pour démarrer l'API. Sur un clone propre, `uvicorn apps.obsidia_api.main:app` échoue immédiatement.

**Impact :**  
- Tout nouvel utilisateur ou revieweur externe ne peut pas démarrer l'API
- Les tests API (`test_f63_*`, `test_f65_*`) échouent sur clone propre par ImportError
- La reproductibilité est compromise — invalidant les claims F74

**Mitigation actuelle :**  
Les packages sont présents dans l'environnement local actuel (installés manuellement). Aucune garantie pour un clone propre.

**Risque résiduel sans action :**  
Bloquant. Aucune démonstration externe possible sans cette correction.

**Action recommandée (F74-T01) :**  
```
fastapi>=0.110
uvicorn[standard]>=0.29
pydantic>=2.0
```

**Deadline :** Immédiat — P0_BLOCKER

---

## Risques HIGH

### RR-04 — Lean proofs revendiquées pour Sigma/Bus/Brody — PYTHON_TEST_ONLY

| Champ | Valeur |
|---|---|
| **ID** | RR-04 |
| **Palier** | F75 |
| **Sévérité** | HIGH |
| **Catégorie** | FORMAL |
| **Statut** | OPEN |
| **Fichier** | `proofs/lean/Obsidia/` |

**Description :**  
Les théorèmes Lean existants (`X108_no_act_before_tau`, `D1_determinism`, `P15_Immutability_Strong`, etc.) couvrent le noyau temporel X108 et les propriétés fondamentales. Aucun théorème Lean ne couvre les couches Sigma (F60-F73), Bus bridge, Graphiti readonly, ni Brody. Ces propriétés sont uniquement validées par des tests Python (`pytest`).

**Impact :**  
- Un auditeur externe pourrait confondre "607 tests Sigma passent" avec "propriétés Sigma formellement prouvées"
- Sur-vente potentielle involontaire des garanties formelles
- Perte de crédibilité si un auditeur qualifié examine le lakefile

**Mitigation actuelle :**  
Partielle — le lakefile est explicite sur les théorèmes présents. Mais aucun document `TECHNICAL_ANNEX` ne distingue clairement `LEAN_PROVEN` vs `PYTHON_TEST_ONLY`.

**Risque résiduel sans action :**  
Risque réputationnel significatif avec auditeurs techniques.

**Action recommandée (F75-T02, F77-T02) :**  
Créer `external_pack/TECHNICAL_ANNEX.md` avec section explicite :
```
## What is formally proven (Lean 4)
- X108_no_act_before_tau
- X108_kernel_never_blocks
- D1_determinism
...

## What is validated by Python tests only
- Sigma registry readonly (607 tests)
- Bus bridge sovereignty (85 tests)
- Graphiti write=False (tests only)
```

**Deadline :** Avant review externe — P1_REQUIRED

---

### RR-05 — graphiti_env_loader charge depuis chemin hors-repo

| Champ | Valeur |
|---|---|
| **ID** | RR-05 |
| **Palier** | F74 |
| **Sévérité** | HIGH |
| **Catégorie** | REPRO |
| **Statut** | OPEN |
| **Fichier** | `sigma/connectors/graphiti_env_loader.py` |

**Description :**  
Le module `graphiti_env_loader` charge silencieusement depuis `../graphiti-lab/.env.graphiti.local` — un chemin relatif en dehors du repo. Ce fichier n'existe pas sur clone propre. En mode dégradé, les connecteurs Graphiti retournent des stubs, mais aucune erreur explicite n'est levée.

**Impact :**  
- Dégradation silencieuse : les tests passent mais Graphiti n'est pas réellement connecté
- Un développeur sur clone propre ne sait pas que Graphiti est désactivé
- Comportement divergent entre dev local (avec graphiti-lab/) et CI (sans)

**Mitigation actuelle :**  
Mode dégradé implémenté. Les tests sigma passent malgré l'absence du fichier.

**Risque résiduel sans action :**  
Confusion pour tout nouveau contributeur. Documentation absente sur ce comportement.

**Action recommandée (F74-T08) :**  
Documenter dans `.env.example` :
```
# EXTERNAL DEPENDENCY (hors repo)
# Si Graphiti actif : créer ../graphiti-lab/.env.graphiti.local
# Si absent : mode dégradé automatique (Graphiti stubs)
```

**Deadline :** Avant QUICKSTART.md — P2_SHOULD

---

### RR-06 — Version Python non épinglée — divergences 3.11/3.12/3.13

| Champ | Valeur |
|---|---|
| **ID** | RR-06 |
| **Palier** | F74 |
| **Sévérité** | HIGH |
| **Catégorie** | CI |
| **Statut** | OPEN |
| **Fichier** | `.python-version` (absent) |

**Description :**  
- CI `verify-proofs.yml` : Python 3.11
- CI `periphery` : Python 3.12
- Environnement local actuel : Python 3.13.3
- Aucun fichier `.python-version` pour épingler la version

**Impact :**  
- Comportements divergents entre CI et dev local
- Risque de breaking changes liés aux dépréciations Python 3.12→3.13
- Impossible de garantir la reproductibilité du clone propre

**Mitigation actuelle :**  
Aucune. Les trois environnements utilisent des versions différentes sans mécanisme de synchronisation.

**Risque résiduel sans action :**  
Failures intermittentes difficiles à diagnostiquer. Reproductibilité compromise.

**Action recommandée (F74-T02) :**  
Créer `.python-version` avec `3.12` (version la plus utilisée en CI). Harmoniser CI `verify-proofs` vers 3.12.

**Deadline :** Immédiat — P0_BLOCKER

---

## Risques MEDIUM

### RR-07 — Dockerfile absent — déploiement container impossible

| Champ | Valeur |
|---|---|
| **ID** | RR-07 |
| **Palier** | F76 |
| **Sévérité** | MEDIUM |
| **Catégorie** | CLOUD |
| **Statut** | OPEN |
| **Fichier** | `Dockerfile` (absent) |

**Description :**  
Aucun `Dockerfile` n'existe dans le repo. Tout déploiement container (Docker, Kubernetes, cloud PaaS) est impossible sans cette étape.

**Impact :**  
- Démonstration cloud bloquée
- CI/CD docker build impossible
- Reproductibilité d'environnement non garantie

**Mitigation actuelle :**  
Aucune.

**Action recommandée (F76-T02) :**  
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "apps.obsidia_api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Deadline :** Avant démo cloud — P0_BLOCKER

---

### RR-08 — GET /health absent — healthcheck CI/CD impossible

| Champ | Valeur |
|---|---|
| **ID** | RR-08 |
| **Palier** | F76 |
| **Sévérité** | MEDIUM |
| **Catégorie** | CLOUD |
| **Statut** | OPEN |
| **Fichier** | `apps/obsidia_api/routes/status.py` (absent) |

**Description :**  
Aucune route `GET /health` n'est implémentée. L'endpoint `/readiness` (Graphiti) existe mais ne retourne pas les métadonnées requises (`decision_authority`, `version`, `readonly`).

**Impact :**  
- Les orchestrateurs Docker/Kubernetes ne peuvent pas vérifier la santé du service
- CI/CD smoke tests sans signal de vie
- Monitoring impossible sans endpoint dédié

**Mitigation actuelle :**  
`/readiness` retourne un status partiel, non standardisé.

**Action recommandée (F76-T04) :**  
```python
@router.get("/health")
def health():
    return {"status": "ok", "version": "V5B", "decision_authority": "KX108_ONLY", "readonly": True}
```

**Deadline :** Avant déploiement Docker — P1_REQUIRED

---

### RR-09 — Rate limiting absent — surface DDoS sur routes coûteuses

| Champ | Valeur |
|---|---|
| **ID** | RR-09 |
| **Palier** | F76 |
| **Sévérité** | MEDIUM |
| **Catégorie** | SECURITY |
| **Statut** | OPEN |
| **Fichier** | `apps/obsidia_api/routes/brody.py`, `apps/obsidia_api/routes/bus.py` |

**Description :**  
Aucun rate limiting (`slowapi`, `RateLimiter`) n'est présent. Les routes `/brody/chat` (LLM) et `/bus/signal` peuvent être appelées à fréquence illimitée.

**Impact :**  
- DDoS trivial sur `/brody/chat` → coûts LLM non bornés
- `/bus/signal` peut recevoir des milliers de signaux par minute
- Aucune protection contre abus accidentel ou intentionnel

**Mitigation actuelle :**  
Aucune. CORS wildcard aggrave ce risque (RR-01).

**Action recommandée (F76-T05) :**  
```python
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
@router.post("/brody/chat")
@limiter.limit("60/minute")
def chat(...): ...
```

**Deadline :** Avant exposition publique — P1_REQUIRED

---

### RR-10 — Résultats TLC non capturés dans artefacts documentés

| Champ | Valeur |
|---|---|
| **ID** | RR-10 |
| **Palier** | F75 |
| **Sévérité** | MEDIUM |
| **Catégorie** | FORMAL |
| **Statut** | OPEN |
| **Fichier** | `docs/runtime/TLC_X108_RESULTS.json` (absent) |

**Description :**  
Les modèles TLA+ (`X108_MC.tla`, `DistributedX108.tla`) existent et sont vérifiés par le CI `verify-tla`. Mais les résultats de TLC ne sont pas capturés dans un artefact documenté accessible sans Java/TLC.

**Impact :**  
- Un auditeur externe ne peut pas voir les résultats de vérification TLA+ sans setup Java
- Les résultats CI sont éphémères (GitHub Actions logs)
- Pas de traçabilité horodatée des résultats TLC

**Mitigation actuelle :**  
`formal/tla/tlc_results/` existe (contenu non vérifié localement).

**Action recommandée (F75-T05) :**  
Capturer le résultat TLC dans `docs/runtime/TLC_X108_RESULTS.json` avec timestamp, version TLC, résultat (PASS/FAIL), propriétés vérifiées.

**Deadline :** Avant pack externe — P2_SHOULD

---

### RR-11 — external_pack/ absent — pack externe impossible

| Champ | Valeur |
|---|---|
| **ID** | RR-11 |
| **Palier** | F77 |
| **Sévérité** | MEDIUM |
| **Catégorie** | PACK |
| **Statut** | OPEN |
| **Fichier** | `external_pack/` (absent) |

**Description :**  
Le répertoire `external_pack/` n'existe pas. Aucun document de présentation externe n'est disponible : ni `ONE_PAGE.md`, ni `TECHNICAL_ANNEX.md`, ni `REPRODUCIBILITY.md`, ni `DECK_OUTLINE.md`.

**Impact :**  
- Aucun document court pour présenter le projet à un revieweur externe
- Toute démo externe nécessite d'expliquer le contexte depuis zéro
- KNOWN_LIMITS.md pré-F60 ne reflète pas la réalité actuelle

**Mitigation actuelle :**  
`docs/demo/` contient des documents F41 (datés 2026-05-29). Non structurés pour un auditeur externe.

**Action recommandée (F77-T01, F77-T02, F77-T03, F77-T04, F77-T05) :**  
Créer `external_pack/` avec les 5 documents requis. Mettre à jour `KNOWN_LIMITS.md` pour inclure les limites F74/F76.

**Deadline :** Avant review externe — P0_BLOCKER (ONE_PAGE), P1_REQUIRED (autres)

---

### RR-12 — Scripts de lancement Linux absents

| Champ | Valeur |
|---|---|
| **ID** | RR-12 |
| **Palier** | F74 |
| **Sévérité** | MEDIUM |
| **Catégorie** | REPRO |
| **Statut** | OPEN |
| **Fichier** | `scripts/run_api.sh` (absent) |

**Description :**  
`run_obsidia_api.ps1` existe (Windows). Aucun équivalent Linux/Mac (`run_api.sh`). La procédure de lancement est exclusivement documentée pour Windows.

**Impact :**  
- Contributeurs Linux/Mac exclus de toute procédure de lancement documentée
- Simulation fresh clone Linux impossible sans script équivalent
- QUICKSTART.md ne peut pas être multiplateforme sans ce fichier

**Mitigation actuelle :**  
La commande uvicorn est connue mais non documentée pour Linux.

**Action recommandée (F74-T05) :**  
```bash
#!/usr/bin/env bash
# scripts/run_api.sh
set -e
uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000
```

**Deadline :** Avant QUICKSTART.md — P1_REQUIRED

---

## Risques LOW

### RR-13 — .env.example absent

| Champ | Valeur |
|---|---|
| **ID** | RR-13 |
| **Palier** | F74 |
| **Sévérité** | LOW |
| **Catégorie** | REPRO |
| **Statut** | OPEN |
| **Fichier** | `.env.example` (absent) |

**Description :**  
Les variables d'environnement requises (`NEO4J_PASSWORD`, `OBSIDIA_API_BASE`, `GRAPHITI_V20_HTTP_BASE`, `ALLOWED_ORIGINS`, `APP_ENV`) ne sont documentées nulle part. Un développeur sur clone propre ne sait pas quelles variables configurer.

**Action recommandée (F74-T03) :** Créer `.env.example` avec toutes les variables et valeurs par défaut.

**Deadline :** P1_REQUIRED

---

### RR-14 — QUICKSTART.md absent

| Champ | Valeur |
|---|---|
| **ID** | RR-14 |
| **Palier** | F74 |
| **Sévérité** | LOW |
| **Catégorie** | DOC |
| **Statut** | OPEN |
| **Fichier** | `QUICKSTART.md` (absent) |

**Description :**  
Aucun guide de démarrage rapide (5 commandes) pour un nouvel utilisateur. La documentation existante suppose une connaissance préalable du projet.

**Action recommandée (F74-T04) :** Créer `QUICKSTART.md` avec : venv + pip + pytest sigma + pytest api minimal.

**Deadline :** P1_REQUIRED

---

### RR-15 — /docs et /redoc exposés en mode production potentiel

| Champ | Valeur |
|---|---|
| **ID** | RR-15 |
| **Palier** | F76 |
| **Sévérité** | LOW |
| **Catégorie** | SECURITY |
| **Statut** | OPEN |
| **Fichier** | `apps/obsidia_api/main.py` |

**Description :**  
La Swagger UI (`/docs`) et ReDoc (`/redoc`) sont actifs par défaut. Si l'API est déployée en production sans désactivation explicite, la surface d'information exposée inclut tous les endpoints, modèles Pydantic, et schémas.

**Action recommandée (F76-T09) :**  
```python
docs_url = None if os.environ.get("APP_ENV") == "prod" else "/docs"
```

**Deadline :** P2_SHOULD

---

## Matrice de synthèse

| ID | Palier | Sévérité | Catégorie | Statut | TODO associé |
|---|---|---|---|---|---|
| RR-01 | F76 | CRITICAL | SECURITY | OPEN | F76-T01 |
| RR-02 | F76 | CRITICAL | SECURITY | OPEN | F76-T10 |
| RR-03 | F74 | CRITICAL | REPRO | OPEN | F74-T01 |
| RR-04 | F75 | HIGH | FORMAL | OPEN | F75-T02, F77-T02 |
| RR-05 | F74 | HIGH | REPRO | OPEN | F74-T08 |
| RR-06 | F74 | HIGH | CI | OPEN | F74-T02 |
| RR-07 | F76 | MEDIUM | CLOUD | OPEN | F76-T02 |
| RR-08 | F76 | MEDIUM | CLOUD | OPEN | F76-T04 |
| RR-09 | F76 | MEDIUM | SECURITY | OPEN | F76-T05 |
| RR-10 | F75 | MEDIUM | FORMAL | OPEN | F75-T05 |
| RR-11 | F77 | MEDIUM | PACK | OPEN | F77-T01…T05 |
| RR-12 | F74 | MEDIUM | REPRO | OPEN | F74-T05 |
| RR-13 | F74 | LOW | REPRO | OPEN | F74-T03 |
| RR-14 | F74 | LOW | DOC | OPEN | F74-T04 |
| RR-15 | F76 | LOW | SECURITY | OPEN | F76-T09 |

---

## NO-GO conditions (bloquants release)

Les risques suivants doivent être résolus avant toute release ou démo externe :

1. **RR-01** — CORS wildcard → F76-T01
2. **RR-03** — requirements.txt incomplet → F74-T01
3. **RR-06** — .python-version absent → F74-T02
4. **RR-07** — Dockerfile absent → F76-T02
5. **RR-11** — external_pack/ONE_PAGE.md absent → F77-T01

---

## Invariants vérifiés (hors scope risque)

Les propriétés suivantes sont confirmées STABLES et ne constituent pas des risques :

| Invariant | Preuve | Niveau |
|---|---|---|
| `decision_authority=KX108_ONLY` | Lean `D1_determinism` + 1253+ tests | LEAN_PROVEN + TEST |
| `readonly=True` (Sigma) | 607 tests sigma/ | PYTHON_TEST_ONLY |
| `emits_act=False` | Lean `X108_no_act_before_tau` | LEAN_PROVEN |
| `kernel_mutation=False` | Lean `X108_kernel_never_blocks` | LEAN_PROVEN |
| `graphiti_write=False` | Tests F70 | PYTHON_TEST_ONLY |
| `neo4j_write=False` | Tests F70 | PYTHON_TEST_ONLY |
| `brody_decision=False` | Tests F66-F73 | PYTHON_TEST_ONLY |
| `memory_write=False` | Tests F60-F73 | PYTHON_TEST_ONLY |

---

*Registre généré le 2026-05-30 — MODE AUDIT READ-ONLY — aucune modification repo*
