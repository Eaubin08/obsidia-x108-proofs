# F74–F77 TODO Matrix

**Date :** 2026-05-30  
**Statut :** AUDIT_COMPLETE — aucune implémentation

Priorités :
- `P0_BLOCKER` — bloque clone/demo/release
- `P1_REQUIRED` — requis avant review externe
- `P2_SHOULD` — fortement recommandé
- `P3_LATER` — après les paliers principaux

Types :
`REPRO` `SECURITY` `CLOUD` `FORMAL` `PACK` `DOC` `CI` `SCRIPT` `RISK` `TEST`

---

## Matrice complète

| ID | Palier | Priorité | Type | Fichier / Chemin | Action | Risque si non fait | Validation |
|---|---|---|---|---|---|---|---|
| F74-T01 | F74 | P0_BLOCKER | REPRO | `requirements.txt` | Ajouter `fastapi>=0.110`, `uvicorn[standard]>=0.29`, `pydantic>=2.0` | L'API ne démarre pas sur clone propre | `pip install -r requirements.txt && uvicorn apps.obsidia_api.main:app` |
| F74-T02 | F74 | P0_BLOCKER | CI | `.python-version` | Créer avec `3.12` pour aligner CI periphery et dev | Comportements divergents Python 3.11/3.12/3.13 | `python --version` == 3.12.x |
| F74-T03 | F74 | P1_REQUIRED | REPRO | `.env.example` | Créer avec `NEO4J_PASSWORD=`, `OBSIDIA_API_BASE=`, `GRAPHITI_V20_HTTP_BASE=`, `ALLOWED_ORIGINS=`, `APP_ENV=dev` | Dépendances implicites invisibles pour clone propre | `cat .env.example` non vide |
| F74-T04 | F74 | P1_REQUIRED | DOC | `QUICKSTART.md` | Créer guide 5 commandes : venv + pip + pytest sigma + pytest api minimal | Friction maximale pour tout nouvel utilisateur | Testé sur VM vierge |
| F74-T05 | F74 | P1_REQUIRED | SCRIPT | `scripts/run_api.sh` | Créer équivalent Linux de `run_obsidia_api.ps1` | Linux/Mac exclus de toute procédure | `bash scripts/run_api.sh` lance uvicorn |
| F74-T06 | F74 | P2_SHOULD | CI | `Makefile` | Targets : `install`, `test-sigma`, `test-api`, `smoke`, `lint` | Automatisation absente — friction CI/CD | `make test-sigma` passe |
| F74-T07 | F74 | P2_SHOULD | REPRO | `requirements-dev.txt` | Créer avec pytest, mypy, ruff, black — séparé de requirements.txt prod | Confusion prod/dev | `pip install -r requirements-dev.txt` |
| F74-T08 | F74 | P2_SHOULD | DOC | `.env.example` | Documenter `graphiti-lab/.env.graphiti.local` chemin relatif implicite avec note "external — créer manuellement si Graphiti actif" | Import silencieux dégrade Brody sans erreur visible | Note dans .env.example |
| F74-T09 | F74 | P3_LATER | CI | `pytest.ini` | Créer avec `testpaths = tests/sigma tests/api` et `--tb=short` | `tests/legacy_root/` collecté par accident en CI | `pytest --co -q` ne collecte plus legacy_root |
| F74-T10 | F74 | P3_LATER | REPRO | `pyproject.toml` | Créer pyproject.toml minimal (project metadata, build backend) | `pip install -e .` impossible | `pip install -e .` passe |
| F75-T01 | F75 | P1_REQUIRED | FORMAL | `docs/runtime/` | Exécuter `lake build` localement (après installation elan) et capturer le résultat JSON dans docs/runtime/ | Preuves Lean déclarées mais non vérifiées localement | `lake build` exit 0, résultat dans docs/runtime/ |
| F75-T02 | F75 | P1_REQUIRED | DOC | `external_pack/TECHNICAL_ANNEX.md` | Documenter clairement frontière LEAN_PROVEN vs PYTHON_TEST_ONLY | Risque de sur-vente des preuves formelles à un auditeur externe | Section "What is formally proven" dans TECHNICAL_ANNEX |
| F75-T03 | F75 | P2_SHOULD | FORMAL | `proofs/lean/Obsidia/SigmaReadonly.lean` | Créer theorem `sigma_no_act` et `sigma_readonly` (propriété KX108_ONLY préservée dans les paquets Sigma) | Propriété la plus visible de F60-F73 non prouvée formellement | `lake env lean Obsidia/SigmaReadonly.lean` passe |
| F75-T04 | F75 | P2_SHOULD | FORMAL | `proofs/lean/` | Vérifier que P107/P161/P36 dans `periphery/` compilent (lakefile séparé ou import dans lake principal) | Fichiers Lean isolés hors du lakefile — statut inconnu | `lake build` sans erreur pour periphery lean files |
| F75-T05 | F75 | P2_SHOULD | FORMAL | `docs/runtime/TLC_X108_RESULTS.json` | Capturer résultat TLC (tlc_results/) dans un artefact documenté | Preuve TLA non accessible sans Java/TLC setup | Fichier JSON avec résultats TLC datés |
| F75-T06 | F75 | P3_LATER | FORMAL | `proofs/lean/Obsidia/BusBridgeReadonly.lean` | Théorème bus sovereignty (bus ne peut pas émettre décision) | FUTURE_FORMAL_TARGET | `lake build` sans erreur |
| F75-T07 | F75 | P3_LATER | FORMAL | `proofs/lean/Obsidia/GraphitiReadonly.lean` | Théorème `graphiti_write_always_false` | FUTURE_FORMAL_TARGET | `lake build` sans erreur |
| F76-T01 | F76 | P0_BLOCKER | SECURITY | `apps/obsidia_api/main.py:10` | Remplacer `allow_origins=["*"]` par `allow_origins=os.environ.get("ALLOWED_ORIGINS","http://localhost:8000").split(",")` | Wildcard CORS = n'importe quel site peut appeler l'API | `curl -H "Origin: evil.com"` retourne 403 en prod |
| F76-T02 | F76 | P0_BLOCKER | CLOUD | `Dockerfile` | Créer Dockerfile : `python:3.12-slim`, COPY, pip install requirements.txt, `CMD uvicorn apps.obsidia_api.main:app --host 0.0.0.0 --port 8000` | Déploiement container impossible | `docker build . && docker run -p 8000:8000 obsidia-api` |
| F76-T03 | F76 | P0_BLOCKER | CLOUD | `.env.example` | Créer avec toutes les variables (voir F74-T03) | Configuration opaque pour tout déploiement | Présent à la racine, non commité avec valeurs réelles |
| F76-T04 | F76 | P1_REQUIRED | CLOUD | `apps/obsidia_api/routes/status.py` | Créer `GET /health` retournant `{status: ok, version: V5B, decision_authority: KX108_ONLY, readonly: true}` | CI/CD healthcheck impossible — déploiement sans signal de vie | `curl localhost:8000/health` HTTP 200 |
| F76-T05 | F76 | P1_REQUIRED | SECURITY | `apps/obsidia_api/main.py` | Ajouter slowapi `@limiter.limit("60/minute")` sur `/brody/chat` et `/bus/signal` | DDoS trivial sur endpoints les plus coûteux | Test curl 100 req/min retourne 429 après 60 |
| F76-T06 | F76 | P1_REQUIRED | DOC | `docs/architecture/ROLLBACK_PLAN.md` | Documenter rollback minimal : `git revert HEAD + uvicorn reload + smoke test sigma` | Aucun plan de retour arrière en cas d'incident | Document présent et validé par un test smoke |
| F76-T07 | F76 | P2_SHOULD | CLOUD | `docker-compose.yml` | Créer docker-compose avec service app + healthcheck (sans Neo4j — dépendance externe) | Lancement container multi-services non automatisé | `docker compose up --build` démarre et /health répond |
| F76-T08 | F76 | P2_SHOULD | CLOUD | `deploy/nginx.conf` | Config nginx minimal : proxy_pass 127.0.0.1:8000, rate limit, headers sécurité | uvicorn exposé directement sans proxy en prod | Test avec nginx -t passe |
| F76-T09 | F76 | P2_SHOULD | SECURITY | `apps/obsidia_api/main.py` | Ajouter `APP_ENV` et désactiver `/docs` + `/redoc` quand `APP_ENV=prod` | Swagger UI exposé en prod — surface d'info | `curl /docs` retourne 404 en prod |
| F76-T10 | F76 | P3_LATER | SECURITY | `apps/obsidia_api/routes/brody.py` | Évaluer ajout APIKey ou Bearer token sur routes `/brody/` avant exposition publique | Accès Brody illimité si exposé publiquement | Auth validée + documentée dans .env.example |
| F77-T01 | F77 | P0_BLOCKER | PACK | `external_pack/ONE_PAGE.md` | 2 pages max : KX108_ONLY, what is proven (Lean), what is not, limits honnêtes (F74/F76 en cours) | Aucun document court pour présenter le projet | Relu par quelqu'un hors du projet |
| F77-T02 | F77 | P1_REQUIRED | PACK | `external_pack/TECHNICAL_ANNEX.md` | Couvrir F60-F73 : Sigma registry, evaluate, packets, monitoring, bus bridge, graphiti readonly, trees, OS Trad, adversarial | Auditeur externe sans vue technique F60-F73 | Présent avec table des modules et tests associés |
| F77-T03 | F77 | P1_REQUIRED | DOC | `docs/status/KNOWN_LIMITS.md` | Mettre à jour pour inclure F74/F76 limites : auth absente, Docker manquant, reproductibilité partielle | Document pré-F60 — ne reflète pas la réalité actuelle | Mention explicite "auth not yet implemented" |
| F77-T04 | F77 | P1_REQUIRED | PACK | `external_pack/REPRODUCIBILITY.md` | Guide clone propre Windows + Linux, prérequis, résultat attendu, commandes exactes | Réviseur externe ne peut pas reproduire seul | Testé sur machine vierge avant publication |
| F77-T05 | F77 | P1_REQUIRED | PACK | `external_pack/DECK_OUTLINE.md` | 10 slides : hook, problem, architecture KX108, preuves Lean, demo live, Sigma layer, Bus bridge, limitations, next steps, contact | Aucun deck mis à jour post-F60 | Structure approuvée par équipe |
| F77-T06 | F77 | P2_SHOULD | PACK | `external_pack/EVIDENCE_INDEX.md` | Index de tous les artefacts de preuve : fichiers Lean, rapports TLC, JSON audit F60-F73, SHA256 manifests | Auditeur ne sait pas quoi valider ni où chercher | Chaque entrée a chemin exact + date + statut |
| F77-T07 | F77 | P2_SHOULD | PACK | `external_pack/SECURITY_NOTES.md` | État honnête sécurité : ce qui est sécurisé (no ACT, no mutation) vs ce qui est TODO (auth, rate limit, CORS) | Auditeur découvre les manques en production → perte de crédibilité | Note explicite "auth not yet prod-ready" |
| F77-T08 | F77 | P3_LATER | PACK | `external_pack/REVIEWER_GUIDE.md` | Instructions auditeur externe : où regarder, quoi valider, quoi ne pas confondre (test vs preuve formelle) | Auditeur perd du temps ou fait de mauvaises conclusions | Présent avec checklist auditeur |

---

## Résumé par priorité

### P0_BLOCKER (5 items — à faire en premier)

| ID | Action |
|---|---|
| F74-T01 | requirements.txt : ajouter FastAPI + uvicorn + pydantic |
| F74-T02 | Créer .python-version = 3.12 |
| F76-T01 | CORS : remplacer `allow_origins=["*"]` |
| F76-T02 | Créer Dockerfile |
| F77-T01 | Créer external_pack/ONE_PAGE.md |

### P1_REQUIRED (11 items)

F74-T03, F74-T04, F74-T05, F75-T01, F75-T02, F76-T03, F76-T04, F76-T05, F76-T06, F77-T02, F77-T03, F77-T04, F77-T05

### P2_SHOULD (8 items)

F74-T06, F74-T07, F74-T08, F75-T03, F75-T04, F75-T05, F76-T07, F76-T08, F76-T09, F77-T06, F77-T07

### P3_LATER (6 items)

F74-T09, F74-T10, F75-T06, F75-T07, F76-T10, F77-T08
