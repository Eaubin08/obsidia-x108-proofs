# F74 — Fresh Clone Reproducibility
**Date** : 2026-05-30 | **Statut** : PASS P0 items | **Score audit** : 8/11 (était 0/11)

---

## Résumé

F74 couvre la reproductibilité du clone propre. Les 3 vrais P0 identifiés par la réconciliation F74/F77 sont tous résolus. Les 3 FAIL restants dans le script d'audit sont P2 optionnels ou des bugs de script.

| Item | Avant | Après |
|---|---|---|
| requirements.txt (app deps) | FAIL — 0 app dep | **PASS** — fastapi/uvicorn/pydantic ajoutés |
| .python-version | FAIL — MISSING | **PASS** — 3.12 créé |
| .env.example | FAIL — MISSING | **PASS** — template sans secrets créé |
| QUICKSTART.md | FAIL — MISSING | **PASS** — créé (redirect + guide complet) |
| scripts/run_api.sh | FAIL — MISSING | **PASS** — créé |
| requirements-dev.txt | FAIL — MISSING | **PASS** — créé |
| **Score global F74** | **0/11 CRITICAL** | **8/11 PARTIAL** |

---

## Fichiers créés / modifiés

| Fichier | Action | Contenu |
|---|---|---|
| `requirements.txt` | **MODIFIÉ** (backup créé) | Ajout fastapi, uvicorn, pydantic, pytest-asyncio, httpx |
| `requirements-dev.txt` | Créé | -r requirements.txt + ruff, mypy, pytest-cov |
| `.python-version` | Créé | `3.12` |
| `.env.example` | Créé | Template APP_ENV, CORS, Graphiti — aucun secret |
| `QUICKSTART.md` | Créé | Résumé TL;DR → QUICKSTART_FRESH_CLONE.md |
| `QUICKSTART_FRESH_CLONE.md` | Créé | Guide complet Windows + Linux |
| `scripts/run_api.ps1` | Créé | PowerShell — env vars + uvicorn |
| `scripts/run_api.sh` | Créé | bash — env vars + uvicorn |

**Backup** : `requirements.txt.bak_20260530_063501_CLAUDE_BEFORE_PATCH`

---

## Commandes Windows (PowerShell)

```powershell
# Clone + install
git clone https://github.com/Eaubin08/obsidia-x108-proofs.git
cd obsidia-x108-proofs
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
python -m pip install -r requirements.txt

# Tests offline
python -m pytest tests\sigma -q --tb=short
python -m pytest tests\api\test_f63_sigma_monitoring_endpoints_readonly.py tests\api\test_f65_sigma_bus_readonly_bridge.py -q --tb=short

# Démarrer l'API
.\scripts\run_api.ps1
```

---

## Commandes Linux / macOS (bash)

```bash
# Clone + install
git clone https://github.com/Eaubin08/obsidia-x108-proofs.git
cd obsidia-x108-proofs
python3.12 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt

# Tests offline
python -m pytest tests/sigma -q --tb=short
python -m pytest tests/api/test_f63_sigma_monitoring_endpoints_readonly.py tests/api/test_f65_sigma_bus_readonly_bridge.py -q --tb=short

# Démarrer l'API
bash scripts/run_api.sh
```

---

## Tests offline confirmés

| Suite | Tests | Résultat |
|---|---|---|
| tests/sigma (F60-F73) | 817 | ✅ PASS |
| tests/api F63 + F65 | 280 | ✅ PASS |
| pip install requirements.txt | — | ✅ EXIT=0 |

---

## F74 restant — 3 items non-bloquants

| Item | Raison du FAIL | Décision |
|---|---|---|
| T06 Makefile | P2 optionnel | Non créé — pas de Makefile dans le repo actuel |
| T09 pytest.ini | Faux positif — tests tournent sans | Non créé — 262 tests PASS sans pytest.ini |
| SIGMA count | Bug script (sigma/tests/ ignoré) | Script bug documenté dans réconciliation |

---

## Dépendances externes optionnelles

Ces composants ne sont pas requis pour les tests offline ou l'API locale :

| Service | Usage | Mode dégradé |
|---|---|---|
| Neo4j + ObsidiaShell (port 8011) | Graphiti live probe | Fallback gracieux — readonly index local |
| Internet (TSA) | RFC3161 timestamp | Skip si offline |
| Lean 4 / elan | Preuves formelles | Hors scope F74 |
| Java 17 / TLC | Model checking TLA+ | Hors scope F74 |

---

## Limites restantes → F76

| Blocker | Gate | Action |
|---|---|---|
| CORS `allow_origins=["*"]` actif | F76-T01 | Corriger dans main.py avec ALLOWED_ORIGINS env var |
| Dockerfile MISSING | F76-T02 | Créer Dockerfile Python 3.12-slim |
| Rate limiting MISSING | F76-T05 | Ajouter slowapi |
| APP_ENV guard /docs | F76-T09 | Désactiver /docs en production |
| Auth MISSING | F76-T10 | Ajouter API key minimum |

---

_F74 — Fresh Clone Reproducibility | 2026-05-30 | Aucun commit/tag/push_
