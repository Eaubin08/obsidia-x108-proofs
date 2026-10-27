# WIDE_DISCOVERY_FILE_MAP.md
# Mission: BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0
# Mode: READ_ONLY · Layer: DOCS · Date: 2026-06-17

---

## Statistiques globales

| Métrique | Valeur |
|---|---|
| Fichiers totaux (hors .git, node_modules, __pycache__, .venv) | 49 535 |
| Dossiers de premier niveau | ~30 |
| Profondeur max observée | 6+ niveaux |

---

## Carte des dossiers de premier niveau

### Dossiers canoniques (haute valeur éducative)

| Dossier | Contenu | Valeur |
|---|---|---|
| `docs/` | ~100 fichiers MD — spécifications, rapports, architecture, Sigma, Brody, Blockchain, world_calls | ⭐⭐⭐ HAUTE |
| `docs/brody/` | 5 fichiers — contrat Brody, runtime, langage, politique | ⭐⭐⭐ HAUTE |
| `docs/architecture/` | ~12 fichiers — stack complet, control plane, rebranching, freeze criteria | ⭐⭐⭐ HAUTE |
| `docs/act/` | 4 fichiers — action lifecycle, sequence governor, world action dry-run | ⭐⭐ MOYENNE |
| `docs/agents/` | 3 fichiers — layer registry, gate mapping, non-sovereign contract | ⭐⭐ MOYENNE |
| `docs/blockchain/` | 6 fichiers — Gencoin, bridge risk, DeFi gate, oracle freshness | ⭐⭐ MOYENNE |
| `docs/world_calls/` | README — policy world calls | ⭐⭐ MOYENNE |
| `formal/tla/` | X108.tla, DistributedX108.tla, MC configs, TLC results | ⭐⭐⭐ HAUTE |
| `sigma/` | run_pipeline.py, sigma_monitor.py, contracts.py, protocols.py, domains/, examples/, tests/ | ⭐⭐⭐ HAUTE |
| `proofs/` | lean/ (Obsidia.lean), verifiers/ (verify_all.py, verify_decision.py, verify_merkle.py) | ⭐⭐⭐ HAUTE |
| `agents/` | registry.json, registry.md, prompts/ (5 agents), routing/ | ⭐⭐ MOYENNE |
| `periphery/` | brody/, world_calls/, adapters/, agents/ (~30+ modules .py) | ⭐⭐⭐ HAUTE |
| `apps/obsidia_api/` | ~25 brody_*.py modules — orchestrateur complet Brody | ⭐⭐⭐ HAUTE |
| `apps/obsidia-workbench/` | Frontend React/Vite + backend FastAPI | ⭐ BASSE |
| `connectors/` | Connecteurs métier | ⭐ BASSE |
| `tests/` | test_*.py, adversarial/, non_sovereignty/, periphery/ | ⭐⭐ MOYENNE |
| `_local_audits/` | Audits BRODY en temps réel — historique de développement | ⭐⭐ MOYENNE |
| `_graphiti_readonly_indexes/` | Index Graphiti en lecture seule | ⭐ BASSE |
| `.graph-memory/` | ALLOWLIST, DENYLIST, sandbox policy, dry run plan | ⭐⭐ MOYENNE |
| `.claude/` | context/, memory/, skills/, agents/ — doctrine Obsidia | ⭐⭐⭐ HAUTE |
| `.claude/context/` | OBSIDIA_IDENTITY, WORKFLOW, PROTECTED_SCOPE, etc. | ⭐⭐⭐ HAUTE |
| `.claude/memory/` | SCRATCH.md, RISKS.md, P1_FREEZE.md | ⭐⭐ MOYENNE |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | Archive structurée V4 — 14 sous-dossiers | ⭐⭐ MOYENNE |
| `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/` | Archive monde / arbres 34 / reverse OS | ⭐⭐ MOYENNE |
| `.deepseek/pastes/` | Pastes DeepSeek historiques — sessions de debug BRODY | ⭐ BASSE |
| `_external_benchmarks/` | SWE-bench, BFCL, AgentDojo, TAU-bench, WebArena, GAIA, OSWorld | ⭐⭐ MOYENNE |
| `examples/` | bank_normal.json, bank_suspicious.json, trading_bullish.json, ecom_normal.json | ⭐⭐⭐ HAUTE |
| `patches/` | Patches overlay V5A, etc. | ⭐ BASSE |
| `qa/` | cross-platform RFC3161/TLC/Sigma | ⭐⭐ MOYENNE |
| `demos/` | Démos minimales | ⭐ BASSE |

---

## Fichiers racine à haute valeur

| Fichier | Rôle |
|---|---|
| `README.md` | Vue d'ensemble publique P1 |
| `PUBLIC_STATUS.md` | Matrice de vérification P1 |
| `START_HERE.md` | Navigation par profil |
| `PROOF_INDEX.md` | Index centralisé des preuves |
| `USE_CASES.md` | 5 cas d'usage concrets |
| `KNOWN_LIMITS.md` | Limites structurelles |
| `MANIFEST.md` | Manifeste public |
| `CLAUDE.md` | Doctrine Obsidia (entrypoint) |
| `AGENTS.md` | Politique agents |
| `docs/KERNEL_OVERVIEW.md` | Spécification noyau X-108 |
| `docs/GLOSSAIRE.md` | Glossaire technique |
| `docs/SIGMA.md` | Spécification Sigma P1 |
| `docs/RFC3161.md` | Ancrage cryptographique |
| `docs/LIMITS.md` | Limites structurelles |

---

## Zones exclues de la lecture (hors scope)

- `node_modules/` — dépendances npm (>35 000 fichiers)
- `__pycache__/` — bytecode compilé
- `.git/` — historique git
- `apps/obsidia-workbench/node_modules/` — idem
- `.pytest_cache/` — cache pytest

---

_Généré le 2026-06-17 par BRODY_WIDE_RND_DISCOVERY_AND_EDUCATION_EXTRACTION_V0_
