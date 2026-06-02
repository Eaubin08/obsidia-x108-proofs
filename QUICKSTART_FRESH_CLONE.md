# Obsidia X-108 — Quick Start (Fresh Clone)
**Palier F74** — Reproductibilité fresh clone | Version 2026-05-30

---

## Objectif

Ce guide couvre l'installation minimale depuis un clone propre jusqu'aux premiers tests offline et au démarrage de l'API locale.

Il ne couvre pas : prod deployment, Docker, CORS sécurisé, auth, rate-limit (→ F76).

---

## Prérequis

### Windows

| Composant | Version minimale | Vérification |
|---|---|---|
| Python | 3.12 | `py -3.12 --version` |
| Git | 2.40+ | `git --version` |
| PowerShell | 7.0+ | `$PSVersionTable.PSVersion` |

### Linux / macOS

| Composant | Version minimale | Vérification |
|---|---|---|
| Python | 3.12 | `python3.12 --version` |
| Git | 2.40+ | `git --version` |
| bash | 4.0+ | `bash --version` |

> **Note** : Python 3.13 fonctionne localement. La cible officielle est 3.12 (`.python-version`).

---

## Installation — Windows (PowerShell)

```powershell
# 1. Cloner
git clone https://github.com/Eaubin08/obsidia-x108-proofs.git
cd obsidia-x108-proofs

# 2. Créer virtualenv
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Installer les dépendances
python -m pip install -U pip
python -m pip install -r requirements.txt

# 4. Copier le template d'environnement (optionnel pour tests offline)
Copy-Item .env.example .env
```

---

## Installation — Linux / macOS (bash)

```bash
# 1. Cloner
git clone https://github.com/Eaubin08/obsidia-x108-proofs.git
cd obsidia-x108-proofs

# 2. Créer virtualenv
python3.12 -m venv .venv
source .venv/bin/activate

# 3. Installer les dépendances
python -m pip install -U pip
python -m pip install -r requirements.txt

# 4. Copier le template d'environnement (optionnel pour tests offline)
cp .env.example .env
```

---

## Tests offline (sans serveur)

Ces tests ne nécessitent pas de serveur externe (Neo4j, Graphiti, SQL Server).
Ils utilisent FastAPI `TestClient` — entièrement offline.

### Windows

```powershell
# Suite Sigma (F60-F73) — entièrement offline
python -m pytest tests\sigma -q --tb=short

# Endpoints Sigma monitoring
python -m pytest tests\api\test_f63_sigma_monitoring_endpoints_readonly.py -q --tb=short

# Bus bridge F65
python -m pytest tests\api\test_f65_sigma_bus_readonly_bridge.py -q --tb=short

# OS Trad / IR / Reverse F72
python -m pytest tests\api\test_f72_os_trad_ir_reverse_pipeline_audit.py -q --tb=short

# Suite complète tests/sigma + tests/api ciblés
python -m pytest tests\sigma tests\api\test_f63_sigma_monitoring_endpoints_readonly.py tests\api\test_f65_sigma_bus_readonly_bridge.py -q --tb=short
```

### Linux / macOS

```bash
python -m pytest tests/sigma -q --tb=short
python -m pytest tests/api/test_f63_sigma_monitoring_endpoints_readonly.py -q --tb=short
python -m pytest tests/api/test_f65_sigma_bus_readonly_bridge.py -q --tb=short
python -m pytest tests/sigma tests/api/test_f63_sigma_monitoring_endpoints_readonly.py tests/api/test_f65_sigma_bus_readonly_bridge.py -q --tb=short
```

**Résultat attendu** : ~650+ tests PASS, 0 failed.

---

## Démarrage de l'API locale

### Windows

```powershell
.\scripts\run_api.ps1
# ou directement :
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000
```

### Linux / macOS

```bash
bash scripts/run_api.sh
# ou directement :
python -m uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000
```

---

## Smoke endpoints (API démarrée)

```bash
# Statut
curl http://127.0.0.1:8000/api/status

# Bus stats
curl http://127.0.0.1:8000/bus/stats

# Bus bridge (avec Sigma state F65)
curl http://127.0.0.1:8000/bus/bridge

# Sigma domains
curl http://127.0.0.1:8000/api/periphery/monitoring/sigma/domains

# Sigma evaluate
curl http://127.0.0.1:8000/api/periphery/monitoring/sigma/evaluate
```

---

## Tests dépendants de services externes

Ces tests nécessitent des services non inclus dans ce repo. Ils peuvent être skippés en fresh clone.

| Test | Service requis | Comportement sans service |
|---|---|---|
| Tests Graphiti live | Neo4j + ObsidiaShell port 8011 | Fallback gracieux, pas de crash |
| Scripts smoke live (`scripts/smoke_f67_*`) | uvicorn démarré sur port 8000 | Requiert serveur actif |
| Tests RFC3161 cross-platform | TSA providers internet | Skip si offline |
| Brody chat tests (LLM) | Brody LLM runtime | Pas de LLM réel en test offline |

---

## Limites de F74

Ce palier couvre **uniquement la reproductibilité du clone**.

| Item | Couvert par F74 | Palier responsable |
|---|---|---|
| Requirements API + test | ✅ | F74 (ce palier) |
| .python-version | ✅ | F74 |
| .env.example | ✅ | F74 |
| Scripts run_api | ✅ | F74 |
| CORS sécurisé prod | ❌ | F76 |
| Dockerfile / Docker | ❌ | F76 |
| Auth / rate limiting | ❌ | F76 |
| APP_ENV guard /docs | ❌ | F76 |
| Pack externe | ❌ | F77 |
| Preuves Lean P36/P107/P161 complètes | ❌ | G1/V4 |
| Lean full proof formal | ❌ | V4 |

---

## Dépendances optionnelles

```
# Preuves Lean (nécessite elan/lake)
elan toolchain install leanprover/lean4:v4.28.0
cd proofs/lean && lake build

# TLA+ model checking (nécessite Java 17 + TLC)
java -jar tla2tools.jar formal/tla/X108_MC.tla -config formal/tla/X108_MC.cfg

# Vérification Python
python proofs/verify_all.py
python proofs/verify_decision.py
python proofs/verify_merkle.py
```

---

*F74 — Fresh Clone Reproducibility | 2026-05-30 | KX108_ONLY | readonly*
