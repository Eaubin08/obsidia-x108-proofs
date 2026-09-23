# F74–F77 Validation Commands

**Date :** 2026-05-30  
**Mode :** READ-ONLY inspection uniquement — aucune commande ne modifie le repo.  
**Invariant :** decision_authority=KX108_ONLY · readonly=true · commit=NO · push=NO

---

## F74 — Fresh Clone Reproducibility

### Smoke test Sigma minimal (Windows — fonctionne aujourd'hui)

```powershell
cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofs_REMOTE_A5F21C6B"

# Vérifier requirements actuels
python -m pip install -r requirements.txt

# Smoke test Sigma — 607 tests attendus PASS
python -m pytest tests/sigma/ -q --tb=short

# Smoke test F63-F65 API — 280 tests attendus PASS
python -m pytest tests/api/test_f63_sigma_monitoring_endpoints_readonly.py tests/api/test_f65_sigma_bus_readonly_bridge.py -q --tb=short
```

### Simulation fresh clone Windows (à exécuter après F74-T01 : requirements.txt complété)

```powershell
# Étape 1 — clone
git clone <REPO_URL> obsidia-fresh-test
cd obsidia-fresh-test

# Étape 2 — venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip

# Étape 3 — install
pip install -r requirements.txt

# Étape 4 — test sigma minimal (ne requiert pas FastAPI)
python -m pytest tests/sigma/ -q --tb=short
# Attendu : 607 passed

# Étape 5 — test API sigma (requiert FastAPI dans requirements.txt)
python -m pytest tests/api/test_f63_sigma_monitoring_endpoints_readonly.py -q --tb=short
# Attendu : 195 passed

# Étape 6 — smoke API live (requiert uvicorn)
# uvicorn apps.obsidia_api.main:app --host 127.0.0.1 --port 8000 &
# python -m pytest tests/api/test_f67_sigma_live_smoke_api_audit.py -q
```

### Simulation fresh clone Linux (à exécuter après F74-T01 + F74-T05)

```bash
git clone <REPO_URL> obsidia-fresh-test
cd obsidia-fresh-test

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt   # après F74-T01 : inclut FastAPI

python -m pytest tests/sigma/ -q --tb=short
# Attendu : 607 passed

python -m pytest tests/api/test_f63_sigma_monitoring_endpoints_readonly.py -q --tb=short
# Attendu : 195 passed
```

### Diagnostic dépendances implicites

```powershell
# Vérifier packages installés
pip list | Select-String "fastapi|uvicorn|pydantic|cryptography|requests"

# Vérifier version Python
python --version

# Vérifier variables d'env critiques
$env:NEO4J_PASSWORD  # devrait être vide sur clone propre — mode dégradé OK
$env:OBSIDIA_API_BASE  # défaut 127.0.0.1:8000

# Vérifier que graphiti-lab/ n'existe pas hors repo (attendu)
Test-Path "..\graphiti-lab\.env.graphiti.local"
```

---

## F75 — Lean / Formal Proofs

### Installation elan (si absent)

```bash
# Linux/Mac
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
echo "$HOME/.elan/bin" >> ~/.bashrc
source ~/.bashrc

# Vérifier version
lean --version  # attendu: leanprover-community/lean4:v4.28.0
```

### Build Lean

```bash
cd proofs/lean

# Build complet (1ère fois : télécharge lean4 + compile)
lake build

# Vérifier axiomes du noyau temporel
lake env lean Obsidia/TemporalKernel.lean

# Vérifier toutes les axiomes référencées dans Audit.lean
lake env lean Obsidia/Audit.lean

# Build en mode verbose pour diagnostic
lake build --verbose
```

### Résultats attendus (lake build)

```
# Toutes ces propriétés doivent compiler sans error :
# Obsidia.D1_determinism
# Obsidia.TemporalKernel.X108_no_act_before_tau
# Obsidia.TemporalKernel.X108_kernel_never_blocks
# Obsidia.TemporalKernel.X108_reversible_equals_base
# Obsidia.Refinement.x108_never_blocks
# Obsidia.Refinement.refined_not_block
# Obsidia.Sensitivity.P15_Immutability_Strong
# Obsidia.Seal.P13_Immutability
# Obsidia.Consensus.aggregate4_fail_closed
```

### Vérification TLA+

```bash
# Prérequis : Java 17
java -version

# Télécharger tla2tools.jar (si absent)
curl -fL https://github.com/tlaplus/tlaplus/releases/download/v1.7.4/tla2tools.jar -o tla2tools.jar

# Lancer TLC sur X108_MC
java -jar tla2tools.jar -config formal/tla/X108_MC.cfg formal/tla/X108_MC.tla
# Résultats existants dans : formal/tla/tlc_results/

# Lancer TLC sur DistributedX108
java -jar tla2tools.jar -config formal/tla/DistributedX108_MC.cfg formal/tla/DistributedX108.tla
```

### Vérification proofs Python

```bash
cd proofs

# Verify all Python proofs
python verify_all.py

# Verify Merkle chain
python verify_merkle.py

# Verify decision envelope (si présent)
# python verify_decision.py decision_envelope.json
```

### CI Lean (reproduce verify-proofs.yml localement)

```bash
# Job verify-lean
cd proofs/lean
lake build

# Job verify-python-strict
python -m pip install --upgrade pip pytest cryptography pyopenssl requests
python proofs/verify_all.py

# Job verify-sigma-and-qa
python -m pytest sigma/tests -v  # si sigma/tests existe et non vide

# Job verify-tla
java -jar tla2tools.jar -config formal/tla/X108_MC.cfg formal/tla/X108_MC.tla
```

---

## F76 — Cloud / Prod Sécurisé

### Audit sécurité read-only (ne modifie rien)

```powershell
# Vérifier CORS wildcard
Select-String -Path apps\obsidia_api\main.py -Pattern "allow_origins"

# Vérifier absence auth
Select-String -Recurse -Path apps\obsidia_api\ -Filter "*.py" -Pattern "APIKey|HTTPBearer|OAuth|JWT" | Where-Object {$_ -notmatch "test|#"}

# Vérifier rate limiting
Select-String -Recurse -Path apps\obsidia_api\ -Filter "*.py" -Pattern "slowapi|RateLim|throttle"

# Vérifier secrets hardcodés
Select-String -Recurse -Path apps\ -Filter "*.py" -Pattern "password\s*=|api_key\s*=|secret\s*=" | Where-Object {$_ -notmatch "environ|test|#|False|None"}

# Vérifier présence /health route
Select-String -Recurse -Path apps\obsidia_api\routes\ -Filter "*.py" -Pattern "health"

# Vérifier .dockerignore
Get-Content .dockerignore

# Vérifier .env files (ne pas lire les valeurs)
Get-ChildItem -Filter ".env*" -Force | Select-Object Name
```

### Test Docker (après F76-T02 : Dockerfile créé)

```bash
# Build image
docker build -t obsidia-api:test .

# Test healthcheck
docker run -d -p 8000:8000 --name obsidia-test obsidia-api:test
curl http://localhost:8000/health   # attendu: 200 OK
curl http://localhost:8000/         # attendu: {service: obsidia-api}

# Cleanup
docker stop obsidia-test && docker rm obsidia-test
```

### Test CORS (après F76-T01 : CORS fixé)

```bash
# En dev : doit passer
curl -H "Origin: http://localhost:3000" http://localhost:8000/bus/stats

# En prod : doit rejeter origine non autorisée
curl -H "Origin: http://evil.com" http://localhost:8000/bus/stats
# Attendu : CORS error ou 403
```

### Vérification health/readiness

```bash
# Après F76-T04 — GET /health
curl http://127.0.0.1:8000/health
# Attendu : {"status": "ok", "version": "V5B", "decision_authority": "KX108_ONLY"}

# Readiness existante (Graphiti)
curl http://127.0.0.1:8000/readiness
```

---

## F77 — Pack Externe

### Audit documents existants (read-only)

```powershell
# Lister tous les docs demo
Get-ChildItem docs\demo\ | Select-Object Name, LastWriteTime

# Lister docs architecture F66-F73
Get-ChildItem docs\architecture\ | Where-Object {$_.Name -match "F6[6-9]|F7[0-7]"} | Select-Object Name

# Lister docs runtime récents
Get-ChildItem docs\runtime\ | Sort-Object LastWriteTime -Descending | Select-Object -First 20 | Select-Object Name, LastWriteTime

# Vérifier structure external_pack (attendu : absent)
Test-Path external_pack\
```

### Smoke test démo (valide le demo script existant)

```powershell
# Démarrer API en arrière-plan
# Start-Process uvicorn -ArgumentList "apps.obsidia_api.main:app --port 8000" -NoNewWindow

# Smoke F67 (si API démarre)
python -m pytest tests/api/test_f67_sigma_live_smoke_api_audit.py -q --tb=short

# Script smoke existant
python scripts/smoke_f67_sigma_live_smoke_api_audit.py
```

### Validation finale F66-F73 ciblée

```powershell
python -m pytest `
  tests/sigma/test_f66_sigma_orchestrator_preview_readonly.py `
  tests/api/test_f67_sigma_live_smoke_api_audit.py `
  tests/sigma/test_f70_sigma_graphiti_readonly_bridge.py `
  tests/sigma/test_f71_sigma_trees_activation_readonly.py `
  tests/api/test_f72_os_trad_ir_reverse_pipeline_audit.py `
  tests/sigma/test_f73_adversarial_boundary_advanced.py `
  -q --tb=short
# Attendu : 263 passed (résultat connu)
```

### Validation régression Sigma complète

```powershell
python -m pytest tests/sigma/ tests/api/test_f6*.py -q --tb=short
# Attendu : 1253+ passed
```

---

## Ordre d'exécution recommandé (validation end-to-end)

```
Phase 1 — BUILD_F74 (blocker résolution)
  → Mettre à jour requirements.txt
  → Créer .python-version, .env.example, QUICKSTART.md
  → Valider : smoke tests sigma + api sur clone propre

Phase 2 — BUILD_F76a (sécurité minimale)
  → Fix CORS main.py
  → Créer GET /health
  → Créer Dockerfile
  → Valider : docker build + curl /health

Phase 3 — BUILD_F75 (validation formelle)
  → lake build dans proofs/lean
  → TLC X108_MC.tla
  → Capturer résultats dans docs/runtime/

Phase 4 — BUILD_F77 (pack externe)
  → Créer external_pack/ avec ONE_PAGE + TECHNICAL_ANNEX + LIMITATIONS
  → Mettre à jour KNOWN_LIMITS.md
  → Valider : relecture par externe

Phase 5 — BUILD_F76b (durcissement complet)
  → Rate limiting
  → Auth si déploiement public
  → Nginx config

Phase 6 — FINAL_REVIEW
  → Smoke test clone propre Windows
  → Smoke test clone propre Linux (VM vierge)
  → Validation démo 3 min
```
