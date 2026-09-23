# F74–F77 Finalization Audit

**Date :** 2026-05-30  
**Scope :** F74 Fresh Clone · F75 Lean Proofs · F76 Cloud/Prod · F77 Pack Externe  
**Context :** F66→F73 validés (263 PASS ciblés). 1253 tests Sigma PASS. Aucun commit/tag/push.  
**Mode :** AUDIT STRICT — lecture seule, aucune implémentation.

---

## Résumé exécutif

| Palier | Statut | Blockers critiques |
|---|---|---|
| F74 Fresh Clone | **PARTIAL** | requirements.txt incomplet, .python-version absent, 28+ tests ImportError |
| F75 Lean Proofs | **PARTIAL** | Noyau temporel LEAN_PROVEN. Sigma/Bus/Graphiti : PYTHON_TEST_ONLY uniquement |
| F76 Cloud/Prod | **PROD_BLOCKED** | CORS wildcard, auth absente, Dockerfile manquant, /health manquant |
| F77 Pack Externe | **PACK_PARTIAL** | ONE_PAGE manquant, external_pack/ inexistant, KNOWN_LIMITS non mis à jour |

**Recommandation d'ordre :** BUILD_F74 → BUILD_F76 partiel → BUILD_F75 validation → BUILD_F77 → BUILD_F76 complet → FINAL_REVIEW

---

## F74 — Fresh Clone Reproducibility

### Statut : PARTIAL

Un clone propre peut faire tourner les tests `tests/sigma/` (607 PASS), mais **ne peut pas démarrer l'API** sans packages manuels non déclarés.

### Fichiers trouvés

| Fichier | Statut |
|---|---|
| `README.md` | EXISTS — public-facing, mis à jour 2026-05-26 |
| `requirements.txt` | EXISTS — **incomplet** (5 packages seulement) |
| `.github/workflows/x108-periphery-ci.yml` | EXISTS — Python 3.12 |
| `.github/workflows/verify-proofs.yml` | EXISTS — Python 3.11 |
| `scripts/run_obsidia_api.ps1` | EXISTS — Windows PowerShell uniquement |
| `scripts/run_api_tests.ps1` | EXISTS — Windows PowerShell uniquement |

### Fichiers manquants (bloquants)

```
pyproject.toml              # MISSING — P0
requirements-dev.txt        # MISSING — P1
.python-version             # MISSING — P0 (3.11 CI / 3.12 CI / 3.13 local)
Makefile                    # MISSING — P2
pytest.ini / setup.cfg      # MISSING — P2 (legacy_root collecté par accident)
Dockerfile                  # MISSING — P0 (F76)
docker-compose.yml          # MISSING — P0 (F76)
.env.example                # MISSING — P0
QUICKSTART.md               # MISSING — P1
scripts/run_api.sh          # MISSING — P1 (Linux)
```

### Dépendances implicites critiques

**requirements.txt actuel :**
```
pytest>=7.0.0
pyopenssl>=23.0.0
cryptography>=41.0.0
requests>=2.31.0
pyyaml>=6.0
```

**Packages manquants pour démarrer l'API :**
- `fastapi` — ABSENT
- `uvicorn` — ABSENT
- `pydantic` — ABSENT

**Dépendances silencieuses :**
- `NEO4J_PASSWORD` env var — mode dégradé si absent
- `graphiti-lab/.env.graphiti.local` — chemin relatif hardcodé hors repo (`graphiti_env_loader.py`)
- Tous scripts de lancement `.ps1` — Windows uniquement

### Décalage Python

| Environnement | Version |
|---|---|
| Local dev | Python 3.13.3 |
| CI x108-periphery | Python 3.12 |
| CI verify-proofs | Python 3.11 |
| **Aucun .python-version** | — |

### Tests non reproductibles sur clone propre

| Fichier | Raison | Count |
|---|---|---|
| `test_brody_general_conversation_mode_readonly.py` | `ImportError: is_general_conversation_readonly` | 30 |
| `test_brody_semantic_advisory_utf8_runtime.py` | `ImportError: repair_mojibake_via_latin1_roundtrip` | 5 |
| `test_brody_freeze_metrics_snapshot_runtime.py` | `pointer_file_count=0` — fichiers locaux absents | 2 |
| `test_output_envelope_*.py` | `graphiti_write / compact` champs manquants | 15 |

### Commandes fresh clone Windows

```powershell
git clone <REPO_URL> obsidia-x108-proofs
cd obsidia-x108-proofs
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
pip install fastapi uvicorn pydantic   # MANQUANT DU requirements.txt — à corriger
python -m pytest tests/sigma/ -q --tb=short
python -m pytest tests/api/test_f63_sigma_monitoring_endpoints_readonly.py tests/api/test_f65_sigma_bus_readonly_bridge.py -q
```

### Commandes fresh clone Linux

```bash
git clone <REPO_URL> obsidia-x108-proofs
cd obsidia-x108-proofs
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -r requirements.txt
pip install fastapi uvicorn pydantic   # MANQUANT — à corriger
python -m pytest tests/sigma/ -q --tb=short
```

---

## F75 — Lean / Formal Proofs

### Statut : PARTIAL

Le noyau temporel X108 est **formellement prouvé en Lean 4**. Les propriétés Sigma/Bus/Graphiti/Brody sont **PYTHON_TEST_ONLY**.

### Infrastructure Lean

```
Toolchain : leanprover/lean4:v4.28.0
Lakefile  : proofs/lean/lakefile.lean
Manifest  : proofs/lean/lake-manifest.json (no external deps)
Lean files: ~30 fichiers dans proofs/lean/
TLA files : formal/tla/ (X108.tla, X108_MC.tla, DistributedX108.tla)
```

### Table des propriétés

| Propriété | Statut | Fichier preuve | Test associé | Risque |
|---|---|---|---|---|
| `X108_no_act_before_tau` | **LEAN_PROVEN** | `TemporalKernel.lean` | tests/sigma/ | LOW |
| `X108_kernel_never_blocks` | **LEAN_PROVEN** | `TemporalKernel.lean` | tests/sigma/ | LOW |
| `X108_reversible_equals_base` | **LEAN_PROVEN** | `TemporalKernel.lean` | n/a | LOW |
| `D1_determinism` | **LEAN_PROVEN** | `Basic.lean` | n/a | LOW |
| `E2_no_act_below_threshold` | **LEAN_PROVEN** | `Basic.lean` | n/a | LOW |
| `Refinement.x108_never_blocks` | **LEAN_PROVEN** | `Refinement.lean` | n/a | LOW |
| `Refinement.refined_not_block` | **LEAN_PROVEN** | `Refinement.lean` | n/a | LOW |
| `P15_Immutability_Strong (Merkle)` | **LEAN_PROVEN** | `Sensitivity.lean` | `proofs/verify_merkle.py` | LOW |
| `P13_Immutability (Seal)` | **LEAN_PROVEN** | `Seal.lean` | n/a | LOW |
| `aggregate4_fail_closed (consensus)` | **LEAN_PROVEN** | `Consensus.lean` | n/a | LOW |
| `canonicalize_preserves_nonneg` | **LEAN_PROVEN** | `TemporalBridge.lean` | n/a | LOW |
| `skew_negative_implies_hold` | **LEAN_PROVEN** | `TemporalBridge.lean` | n/a | LOW |
| TLA+ X108 temporal safety | **FORMAL_TLA** | `X108_MC.tla` | CI verify-tla | MEDIUM |
| `KX108_ONLY in Sigma packets` | **PYTHON_TEST_ONLY** | `test_f62_*.py` | 650 sigma tests | MEDIUM |
| `no ACT from Sigma` | **PYTHON_TEST_ONLY** | `test_f73_*.py` | tests/sigma/ | MEDIUM |
| `no ACT from Brody` | **PYTHON_TEST_ONLY** | `test_brody_authority_escalation_no_act.py` | tests/api/ | MEDIUM |
| `Sigma readonly (readonly=True)` | **PYTHON_TEST_ONLY** | `test_f63_*.py` | 195 tests | MEDIUM |
| `bus sovereignty` | **PYTHON_TEST_ONLY** | `test_f65_*.py` | 85 tests | MEDIUM |
| `graphiti_write=False` | **PYTHON_TEST_ONLY** | `test_f70_*.py` | tests/sigma/ | MEDIUM |
| `memory_write=False` | **PYTHON_TEST_ONLY** | `test_no_memory_write_api.py` | tests/api/ | MEDIUM |
| `sanitizer rejects dangerous fields` | **PYTHON_TEST_ONLY** | `scripts/_f47_test_sanitizer.py` | F47 suite | MEDIUM |
| `P107 Lyapunov stability` | **DOC_ONLY** | `periphery/.../P107.lean` | NONE | HIGH |
| `P161 Calibration energetique` | **DOC_ONLY** | `periphery/.../P161.lean` | NONE | HIGH |

### Commandes de validation Lean

```bash
# Installer elan (si absent)
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
export PATH="$HOME/.elan/bin:$PATH"

# Build
cd proofs/lean
lake build

# Vérification axiomes
lake env lean Obsidia/Audit.lean
lake env lean Obsidia/TemporalKernel.lean
```

### Commande validation TLA+

```bash
java -jar tla2tools.jar -config formal/tla/X108_MC.cfg formal/tla/X108_MC.tla
```

---

## F76 — Cloud / Prod Sécurisé

### Statut : PROD_BLOCKED

**6 blockers critiques** interdisent tout déploiement public.

### Matrice sécurité

| Zone | Fichier | Statut | Risque | Action |
|---|---|---|---|---|
| **CORS** | `main.py:10` | CRITICAL_BLOCKER | `allow_origins=["*"]` wildcard | Restreindre à domaine prod |
| **AUTH** | `main.py` | ABSENT | Tous endpoints publics sans token | Ajouter HTTPBearer ou APIKey |
| **RATE LIMIT** | `main.py` | ABSENT | DDoS trivial | Ajouter slowapi |
| **DOCKER** | `.` | MISSING | Déploiement container impossible | Créer Dockerfile |
| **DOCKERIGNORE** | `.dockerignore` | EXISTS_ORPHAN | Dockerfile absent — incohérent | Créer Dockerfile associé |
| **ENV_EXAMPLE** | `.env.example` | MISSING | Configuration opaque | Créer .env.example |
| **SECRETS_GRAPHITI** | `graphiti_env_loader.py:10` | IMPLICIT_PATH | Chemin relatif hors repo | Documenter + log explicite |
| **SECRETS_NEO4J** | `brody_memory_response_chain_adapter.py:54` | ENV_VAR_OK | `os.environ.get()` — acceptable | Documenter dans .env.example |
| **HARDCODED_SECRETS** | `apps/` | NONE_FOUND | Aucun hardcodé détecté | Maintenir |
| **HEALTH** | `audit_middleware.py:35` | ROUTE_MISSING | `/health` mentionné mais pas implémenté | Créer GET /health |
| **READINESS** | `routes/graphiti.py:234` | PARTIAL | Graphiti seulement, pas global | Créer GET /readiness global |
| **LOGGING** | `audit_middleware.py` | PARTIAL | Audit présent, vérifier avant auth | Audit logs avant implémentation auth |
| **ROLLBACK** | `.` | MISSING | Aucun plan documenté | Documenter rollback minimal |
| **REVERSE_PROXY** | `.` | MISSING | uvicorn exposé directement | Créer config nginx |
| **PORT** | `run_obsidia_api.ps1` | IMPLICIT | Port 8000 non documenté README | Documenter |
| **API_EXPOSURE** | `main.py` | NO_ACT_ROUTES | Aucune route ACT — PASS | Maintenir |
| **X108_MUTATION** | `apps/` | NONE_FOUND | Aucune mutation X108 — PASS | Maintenir |

### Configuration actuelle main.py (à corriger)

```python
# ACTUEL — DANGEREUX EN PROD
app.add_middleware(CORSMiddleware,
    allow_origins=["*"],        # BLOCKER
    allow_methods=["GET","POST"],
    allow_headers=["*"])

# CORRIGÉ — prod safe
import os
ALLOWED = os.environ.get("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
app.add_middleware(CORSMiddleware,
    allow_origins=ALLOWED,
    allow_methods=["GET","POST"],
    allow_headers=["*"])
```

### Variables d'environnement à documenter

```bash
# .env.example (à créer)
NEO4J_PASSWORD=              # Optionnel — mode dégradé si absent
NEO4J_URI=bolt://localhost:7687  # Optionnel
OBSIDIA_API_BASE=http://127.0.0.1:8000
GRAPHITI_V20_HTTP_BASE=      # Optionnel — désactive Graphiti si vide
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
APP_ENV=dev                  # dev | staging | prod
```

---

## F77 — Pack Externe Final

### Statut : PACK_PARTIAL

Base documentaire F41 solide mais **non mise à jour pour F60-F73**. `external_pack/` inexistant.

### Documents trouvés

| Fichier | Type | Statut |
|---|---|---|
| `docs/demo/OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md` | Demo script | EXISTS — daté 2026-05-29 |
| `docs/demo/OBSIDIA_F41_INVESTOR_JURY_FAQ.md` | FAQ investor | EXISTS |
| `docs/demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md` | Pitch | EXISTS |
| `docs/demo/OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md` | Claims boundary | EXISTS |
| `docs/demo/OBSIDIA_F43_LIVE_SERVER_RUNBOOK.md` | Runbook | EXISTS |
| `docs/status/KNOWN_LIMITS.md` | Limitations | EXISTS — **pré-F60, non mis à jour** |
| `docs/status/USE_CASES.md` | Use cases | EXISTS |
| `docs/architecture/SIGMA_FINAL_FREEZE_INDEX_F60_TO_F68.md` | Sigma index | EXISTS |
| `README.md` | Entry point public | EXISTS — mis à jour 2026-05-26 |

### Documents manquants pour pack externe

```
external_pack/README_EXTERNAL.md    # P1 — entrée du pack
external_pack/ONE_PAGE.md           # P0 — synthèse 2 pages
external_pack/DEMO_3_MIN_SCRIPT.md  # P1 — version mise à jour F73
external_pack/DECK_OUTLINE.md       # P1 — 10 slides outline
external_pack/TECHNICAL_ANNEX.md    # P1 — F60-F73 complet
external_pack/LIMITATIONS.md        # P1 — limites honnêtes F76 incluses
external_pack/REPRODUCIBILITY.md    # P1 — guide clone propre
external_pack/SECURITY_NOTES.md     # P2 — état sécurité honnête
external_pack/EVIDENCE_INDEX.md     # P2 — index de toutes les preuves
external_pack/REVIEWER_GUIDE.md     # P3 — guide auditeur externe
```

### Claims à contrôler avant publication

| Claim | Verdict | Message recommandé |
|---|---|---|
| "Preuves formelles" | PARTIAL | Noyau temporel X108 prouvé en Lean 4. Sigma/Bus/Brody : tests Python uniquement. |
| "Production-ready" | NON | F76 bloque : CORS wildcard, auth absente, Docker manquant |
| "Cloud-ready" | NON | Voir F76 blockers |
| "AGI ready" | HORS_SCOPE | Ne pas mentionner |
| "KX108_ONLY authority" | OUI | 1253+ tests PASS, architecture prouvée |
| "readonly everywhere" | OUI | Validé F60-F73 |
| "no ACT emitted" | OUI | Validé F47/F73/F65 |
| "Reproducible clone" | PARTIEL | Sigma tests OK, API nécessite packages manquants |

### Message externe recommandé

> Obsidia X-108 est un noyau de gouvernance déterministe à autorité décisionnelle unique (KX108_ONLY). Le noyau temporel est prouvé formellement en Lean 4. Les contraintes d'opérateur (no ACT, readonly, no mutation) sont validées par 1253+ tests automatisés couvrant F60-F73. Le système est en phase de finalisation de reproductibilité (F74) et durcissement production (F76) avant release externe.

---

## No-Go Blockers

1. **Ne pas déployer publiquement** avant F76 CORS + auth résolus
2. **Ne pas présenter comme "prod-ready"** tant que Dockerfile et .env.example manquent
3. **Ne pas clamer "fully formally proven"** — seul le noyau temporel X108 est LEAN_PROVEN
4. **Ne pas déployer sans GET /health** opérationnel (CI/CD bloqué)

## Ce qui peut attendre

- Preuves Lean Sigma/Bus/Graphiti — FUTURE_FORMAL_TARGET
- Nginx/reverse proxy — après Dockerfile stable
- AUTH complet HTTPBearer — après CORS + health fixes
- `external_pack/REVIEWER_GUIDE.md` — après pack principal
- `pyproject.toml` — nice to have
- `Makefile` — confort

## Ordre d'exécution recommandé

```
1. BUILD_F74  — requirements.txt + .python-version + .env.example + QUICKSTART.md
2. BUILD_F76a — CORS fix + GET /health + Dockerfile
3. BUILD_F75  — lake build local + TLC validation + capturer résultats
4. BUILD_F77  — external_pack/ ONE_PAGE + TECHNICAL_ANNEX + LIMITATIONS
5. BUILD_F76b — Rate limiting + auth + nginx (si déploiement public)
6. FINAL_REVIEW — Smoke test clone propre Windows + Linux
```
