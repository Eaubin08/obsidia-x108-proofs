# P73 — Agents Complementary Reconciliation

**Audit ID :** P73  
**Statut :** `P73_AGENTS_COMPLEMENTARY_RECONCILIATION_READY`  
**Mode :** `AUDIT_AND_READONLY_ADAPTERS` — aucun import en bloc, aucun écrasement sigma, aucune route active  
**Branche :** `p73-agents-complementary-reconciliation`  
**Date :** 2026-06-07

---

## 1. Verdict court

| Métrique | Valeur |
|---|---:|
| Agents/fichiers scannés | 33 |
| Déjà absorbés par sigma/proof (KEEP_PROOF_VERSION) | 18 |
| Doublons exacts (DO_NOT_IMPORT_DUPLICATE) | 6 |
| Adaptés readonly (ADAPT_READONLY_SIGNAL) | 1 |
| Référence doc uniquement (IMPORT_DOC_ONLY) | 1 |
| Bloqués — revue architecturale (BLOCKED) | 7 |
| Fichiers readonly créés | 2 |

**Pourquoi sigma/proof gagne par défaut :**  
sigma/ contient les versions P56B/P56D de tous les composants critiques (guard, obsidia_sigma_v130, run_pipeline, contracts, aggregation). Le core est antérieur et ne contient pas les patches gamma=1.0 (P56B) ni POST_GUARD_VETO_ONLY (P56D). Importer les versions core écraserait des corrections prouvées.

---

## 2. Modèle agents

| Catégorie | Sens | Action | Autorité |
|---|---|---|---|
| `KEEP_PROOF_VERSION` | Équivalent sigma/proof supérieur existe | Ne pas importer — utiliser sigma | NON_SOVEREIGN (via sigma) |
| `DO_NOT_IMPORT_DUPLICATE` | Doublon exact dans sigma/ — P62/P64 DO_NOT_IMPORT | Ne pas importer | NON_SOVEREIGN |
| `IMPORT_DOC_ONLY` | Utile uniquement pour référence documentaire | Référence, pas de runtime load | NON_SOVEREIGN |
| `ADAPT_READONLY_SIGNAL` | Signal non-souverain adapté sans file write ni action | Créer adapter readonly | NON_SOVEREIGN |
| `ADAPT_DRY_RUN_PROPOSAL` | Proposition dry-run avec DRY_RUN_ONLY=True | Créer adapter dry-run | NON_SOVEREIGN |
| `BLOCKED_REQUIRES_ARCHITECTURAL_REVIEW` | Contient write/network/runtime/action | Bloquer — revue requise | BLOCKED |
| `UNKNOWN_REQUIRES_REVIEW` | Classification incertaine | Revue manuelle | NON_DÉCIDÉ |

---

## 3. Matrice agents — 33 entrées

### agents/ (18 fichiers)

| Agent | Source | Équivalent sigma | Décision | Risque | Prochain geste |
|---|---|---|---|---|---|
| `__init__` | agents/ | — | BLOCKED | MEDIUM | DO_NOT_IMPORT |
| `aggregation` | agents/ | sigma/aggregation.py ✓ | KEEP_PROOF | NONE | USE_SIGMA |
| `base` | agents/ | sigma/base.py ✓ | KEEP_PROOF | NONE | USE_SIGMA |
| `contracts` | agents/ | sigma/contracts.py ✓ (P56B) | KEEP_PROOF | NONE | USE_SIGMA |
| `domains/bank_agents` | agents/domains/ | sigma/domains/bank_agents.py ✓ | KEEP_PROOF | LOW | USE_SIGMA |
| `domains/ecom_agents` | agents/domains/ | sigma/domains/ecom_agents.py ✓ | KEEP_PROOF | LOW | USE_SIGMA |
| `domains/meta_agents` | agents/domains/ | sigma/domains/meta_agents.py ✓ | KEEP_PROOF | NONE | USE_SIGMA |
| `domains/trading_agents` | agents/domains/ | sigma/domains/trading_agents.py ✓ | KEEP_PROOF | LOW | USE_SIGMA |
| `guard` | agents/ | sigma/guard.py ✓ (P56D) | **KEEP_PROOF_CRITIQUE** | HIGH_IF_REPLACED | USE_SIGMA_ONLY |
| `obsidia_sigma_v130` | agents/ | sigma/obsidia_sigma_v130.py ✓ (P56B) | **KEEP_PROOF_CRITIQUE** | HIGH_IF_REPLACED | USE_SIGMA_ONLY |
| `protocols` | agents/ | sigma/protocols.py ✓ (P56D) | KEEP_PROOF | NONE | USE_SIGMA |
| `registry` | agents/ | sigma/registry.py ✓ | KEEP_PROOF | NONE | USE_SIGMA |
| `run_pipeline` | agents/ | sigma/run_pipeline.py ✓ (P56D) | **KEEP_PROOF_CRITIQUE** | HIGH_IF_REPLACED | USE_SIGMA_ONLY |
| `sigma_config.json` | agents/ | sigma/sigma_config.json ✓ | DO_NOT_IMPORT | MEDIUM | DO_NOT_IMPORT |
| `sigma_dashboard` | agents/ | **aucun** | **ADAPT_READONLY_SIGNAL** | LOW_AFTER | ADAPTER_CREATED |
| `sigma_monitor` | agents/ | sigma/sigma_monitor.py ✓ | KEEP_PROOF | LOW | USE_SIGMA |
| `utils/__init__` | agents/utils/ | sigma/utils/__init__.py ✓ | DO_NOT_IMPORT | NONE | DO_NOT_IMPORT |
| `utils/indicators` | agents/utils/ | sigma/utils/indicators.py ✓ (IDENTICAL) | DO_NOT_IMPORT | NONE | WRAPPER_FOR_API |

### python_agents/ (15 fichiers)

| Agent | Source | Équivalent sigma | Décision | Risque | Prochain geste |
|---|---|---|---|---|---|
| `__init__` | python_agents/ | — | DO_NOT_IMPORT | NONE | DO_NOT_IMPORT |
| `aggregation` | python_agents/ | sigma/aggregation.py ✓ | KEEP_PROOF | NONE | USE_SIGMA |
| `base` | python_agents/ | sigma/base.py ✓ | BLOCKED | MEDIUM | REVIEW_BEFORE_MERGE |
| `contracts` | python_agents/ | sigma/contracts.py ✓ | KEEP_PROOF | NONE | USE_SIGMA |
| `demo_run` | python_agents/ | — | DO_NOT_IMPORT | LOW | DO_NOT_IMPORT |
| `domains/bank_agents` | python_agents/domains/ | sigma/domains/bank_agents.py ✓ | BLOCKED | MEDIUM | REVIEW_BEFORE_MERGE |
| `domains/ecom_agents` | python_agents/domains/ | sigma/domains/ecom_agents.py ✓ | BLOCKED | MEDIUM | REVIEW_BEFORE_MERGE |
| `domains/meta_agents` | python_agents/domains/ | sigma/domains/meta_agents.py ✓ | BLOCKED | MEDIUM | REVIEW_BEFORE_MERGE |
| `domains/trading_agents` | python_agents/domains/ | sigma/domains/trading_agents.py ✓ | **BLOCKED_NETWORK** | HIGH | REVIEW_NETWORK_GATE |
| `guard` | python_agents/ | sigma/guard.py ✓ (P56D) | **KEEP_PROOF_CRITIQUE** | HIGH_IF_REPLACED | USE_SIGMA_ONLY |
| `protocols` | python_agents/ | sigma/protocols.py ✓ | KEEP_PROOF | NONE | USE_SIGMA |
| `registry` | python_agents/ | sigma/registry.py ✓ | BLOCKED | MEDIUM | REVIEW_BEFORE_MERGE |
| `run_pipeline` | python_agents/ | sigma/run_pipeline.py ✓ (P56D) | **KEEP_PROOF_CRITIQUE** | HIGH_IF_REPLACED | USE_SIGMA_ONLY |
| `tests/test_agents_functional` | python_agents/tests/ | — | IMPORT_DOC_ONLY | NONE | REFERENCE_DOC |
| `utils/indicators` | python_agents/utils/ | sigma/utils/indicators.py ✓ (IDENTICAL) | DO_NOT_IMPORT | NONE | DO_NOT_IMPORT |

---

## 4. Agents adaptés (readonly)

| Adapter | Source | Readonly | Dry-run | ACT | Verdict | Write |
|---|---|:---:|:---:|:---:|:---:|:---:|
| `sigma_dashboard_readonly.py` | agents/sigma_dashboard.py | ✓ | ✓ | ✗ | ✗ | ✗ |
| `indicators_readonly.py` | agents/utils/indicators.py | ✓ | ✓ | ✗ | ✗ | ✗ |

**sigma_dashboard_readonly.py :**  
- Adaptation : suppression de `plt.savefig()` (écrivait `proofs/V18_9/sigma_dashboard.png`)
- Suppression de matplotlib comme dépendance requise
- Retourne `get_sigma_stability_data()` → dict, pas de PNG
- Lit `proofs/PROOFKIT_REPORT.json` en lecture seule
- Placé sous `apps/obsidia_api/agents_readonly/` — hors sigma/, hors routes/

**indicators_readonly.py :**  
- Wrapper readonly isolé — même fonctions que sigma/utils/indicators.py
- Pas d'import sigma direct (isolation couche API)
- Mathématiques pures (sma, ema, rsi, zscore, bollinger, realized_volatility)
- Aucune dépendance externe, aucun file write

---

## 5. Agents bloqués

### BLOCKED_REQUIRES_ARCHITECTURAL_REVIEW (7)

1. **agents/__init__.py** — Module init sans boundary DRY_RUN_ONLY. Import en bloc interdit.
2. **python_agents/base.py** — Différences potentielles avec sigma/base.py. Revue avant merge.
3. **python_agents/domains/bank_agents.py** — Agents domaine bank retournent des verdicts. Revue architecturale.
4. **python_agents/domains/ecom_agents.py** — Agents domaine ecom retournent des verdicts. Revue requise.
5. **python_agents/domains/meta_agents.py** — Meta-agents orchestrent d'autres agents. Revue architecturale.
6. **python_agents/domains/trading_agents.py** — **ccxt dependency** = réseau externe possible. NETWORK_EGRESS_REVIEW_REQUIRED (P70 finding porté). Gate dry_run obligatoire.
7. **python_agents/registry.py** — Registry orchestre la résolution des agents — peut influencer le chemin de décision.

---

## 6. Lien P72 — Contraintes invariants appliquées

| Invariant P72 | Application P73 |
|---|---|
| `NO_PERIPHERY_DECISION_AUTHORITY` | Aucun agent adapté ne retourne ALLOW/HOLD/BLOCK final |
| `DRY_RUN_ONLY_ADAPTERS` | DRY_RUN_ONLY=True dans chaque adapter readonly créé |
| `KX108_ONLY_DECISION_AUTHORITY` | DECISION_AUTHORITY="KX108_ONLY" dans __init__ et chaque adapter |
| `PYTHON_TESTED_NOT_LEAN_PROVEN` | agents/ n'ajoutent pas de preuves Lean — tests Python seulement |
| `NO_KERNEL_MUTATION_FROM_PERIPHERY` | KERNEL_MUTATION=False dans tous les adapters |
| `NO_GRAPHITI_WRITE` | GRAPHITI_WRITE=False — aucun adapter n'écrit en graphiti |
| `NO_MEMORY_WRITE_WITHOUT_GATE` | MEMORY_WRITE=False — aucun adapter n'écrit en mémoire |
| `SIGMA_POST_GUARD_VETO_ONLY` | sigma/ non modifié — guard.py/run_pipeline.py préservés P56D |

---

## 7. Décision

P73 ne transforme pas les agents en autorité. P73 ne fait que :
- **Garder** les 18 équivalents sigma/proof supérieurs
- **Documenter** les 6 doublons exacts DO_NOT_IMPORT
- **Adapter** sigma_dashboard en signal readonly (data dict, pas de PNG)
- **Créer** un wrapper readonly indicators pour l'API layer
- **Bloquer** les 7 agents à risque (trading ccxt, domaines, registry)

**sigma/ protégé :** guard.py (P56D), obsidia_sigma_v130.py (P56B gamma=1.0), run_pipeline.py (P56D), contracts.py (P56B GPS), aggregation.py (P56B GPS), sigma_config.json (P56B), utils/indicators.py (identique), sigma_monitor.py (CLI P56B).

**Findings ouverts portés :**
- python_agents/domains/trading_agents.py — ccxt network (P70 carrying)
- POST /preview + POST /os-map/query sans auth (P69/P71 carrying)

**Prochain geste : P74 — Sigma Safe Evolution.**

---

**Verdict :** `P73_AGENTS_COMPLEMENTARY_RECONCILIATION_READY`
