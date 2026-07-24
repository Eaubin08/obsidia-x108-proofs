# P67 — Boundary Semantic Split Audit

**Audit ID :** P67  
**Statut :** `P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT_READY`  
**Mode :** `AUDIT_ONLY` — aucun patch, aucun import, aucune modification  
**Branche :** `p67-boundary-semantic-split-audit`  
**Date :** 2026-06-07

---

## 1. Verdict court

### Pourquoi `readonly` était trop large

Le mot `readonly` couvrait des situations très différentes dans le repo :
- Un module avec `readonly: True` dans son boundary peut tout de même **écrire un rapport local** (scripts d'audit, manifests JSON/MD)
- Un module peut être **readonly côté décision** mais appeler un **subprocess local** pour scanner des fichiers
- Un composant SRL peut être **readonly canonical** mais écrire dans un `.jsonl` d'audit
- Les **connecteurs** (aviation, bank, trading) font des appels réseau `requests.post` — ce n'est pas un bypass de sécurité, c'est leur rôle fonctionnel documenté

P67 découpe le terme `readonly` en **14 dimensions boundary distinctes** pour éviter les faux conflits.

### Ce que P67 découpe

| Zone | Situation | Verdict |
|---|---|---|
| `decision_readonly` | 532 fichiers ne prennent pas de décision souveraine | SAFE |
| `act_readonly` | 445 fichiers confirment `emits_act=False` | SAFE |
| `dry_run_only` | 15 fichiers avec `DRY_RUN_ONLY=True` strict | SAFE |
| `local_audit_write` | 152 fichiers écrivent des .jsonl/manifests audit | ALLOWED |
| `artifact_write` | scripts/ et audit/ qui génèrent des rapports | ALLOWED |
| `report_write` | docs/ qui écrivent des MD/JSON narratifs | ALLOWED |
| `network_egress` | 7 fichiers — connecteurs fonctionnels + test fixtures | REVIEW |
| `subprocess` | 101 fichiers — majoritairement docs narrative, 1 route active | REVIEW |
| `graphiti_write` | 37 fichiers — **tous docs narrative ou zones quarantinées P66** | SAFE* |
| `kernel_mutation_true` | 42 fichiers — majoritairement tests + runtime_wiring gelé | REVIEW |
| `canonical_memory_write` | 37 fichiers — tests + docs | REVIEW |
| `runtime_allowed_now` | 124 fichiers dans `runtime_wiring/` gelé P56E | BLOCKED_PREEXISTING |

*Les 37 graphiti_write sont dans docs/ (narrative) ou dans les zones déjà quarantinées P66.

### Zones safe confirmées

- `bus/` — 8 fichiers : `DRY_RUN_ONLY=True`, `ACT_READONLY`, aucun egress
- `os_adapters/` — 5 fichiers : 100% `DRY_RUN_ONLY`, aucun write actif
- `SRL/` — 6 fichiers : `DECISION_READONLY`, aucun write actif

### Zones à revoir plus tard

- `connectors/` : `requests.post` présents — **fonctionnels, pas une anomalie** — revue P68
- `routes/brody.py`, `routes/os_map.py`, `routes/source_runtime_status.py` : `runtime_allowed_now` détecté — **runtime_wiring gelé P56E** — ne pas toucher
- `periphery/` : 186 fichiers UNKNOWN_REQUIRES_REVIEW — revue progressive P68+

---

## 2. Modèle boundary

| Boundary | Sens exact | Autorisé ? | Exemple |
|---|---|:---:|---|
| `decision_readonly` | La couche ne prend pas de décision souveraine (HOLD/BLOCK/ALLOW) | ✓ | SRL, bus, os_adapters |
| `act_readonly` | `emits_act=False` confirmé — aucun ACT émis | ✓ | Tous adapters P65 |
| `dry_run_only` | `DRY_RUN_ONLY=True` hardcodé — exécution réelle neutralisée | ✓ | bus/registry.py, os_adapters/* |
| `local_audit_write` | Écriture `.jsonl` log ou manifest local | ✓ (audit) | audit/world_action_bus.jsonl, manifests |
| `artifact_write` | Écriture rapport JSON/MD audit dans docs/ ou scripts/ | ✓ (audit) | scripts/generate_recursive_manifest.py |
| `report_write` | Écriture narrative MD/JSON dans docs/ | ✓ (docs) | docs/core_import/P67_*.md |
| `canonical_memory_write` | Écriture mémoire canonique Brody/session | ✗ INTERDIT | — dans chemin SRL readonly |
| `graphiti_write` | Écriture index Graphiti | ✗ INTERDIT | Zones quarantinées P66 uniquement |
| `neo4j_write` | Connexion Neo4j write | ✗ INTERDIT | `NEO4J_PASSWORD` obligatoire, fail fermé |
| `network_egress` | Appel réseau externe | REVIEW | connectors/ (fonctionnel), sigma/tools |
| `subprocess_execute` | Appel subprocess / os.system | REVIEW | 1 route active, reste docs/narrative |
| `path_exposure` | localhost / hardcode credential | REVIEW | fixtures test, env-driven OK |
| `kernel_mutation` | Mutation kernel X108 | ✗ INTERDIT | runtime_wiring gelé P56E |
| `sigma_mutation` | Modification sigma/ | ✗ PROTÉGÉ | sigma/ gel permanent |

---

## 3. Matrice par surface

| Surface | Fichiers scannés | Safe readonly | Dry-run | Writes locaux | Egress review | Path review | Risk |
|---|---:|---:|---:|---:|---:|---:|---|
| sigma | 78 | 40 | 0 | 0 | 1 | 0 | PROTÉGÉ |
| runtime_wiring | 61 | 36 | 0 | 0 | 0 | 0 | BLOQUÉ P56E |
| apps/obsidia_api | 91 | 66 | 7 | 0 | 0 | 0 | LOW |
| routes | 22 | 18 | 0 | 0 | 0 | 0 | REVIEW (runtime_allowed) |
| bus | 8 | 2 | 2 | 0 | 0 | 0 | SAFE |
| os_adapters | 5 | 4 | 5 | 0 | 0 | 0 | SAFE |
| periphery | 2593 | 105 | 0 | 26+ | 0 | 58+ | REVIEW partiel |
| SRL | 6 | 2 | 0 | 0 | 0 | 0 | SAFE |
| connectors | 7 | 4 | 0 | 0 | 3 | 3 | REVIEW (fonctionnel) |
| tools/scripts | 189 | 0 | 0 | 75 | 1 | 48 | ALLOWED (audit) |
| proofs/tests | 468 | 128 | 0 | 0 | 1 | 0 | TEST_SAFE |
| audit/docs | 895 | 152 | 3 | 0 | 2 | 0 | DOC_SAFE |

---

## 4. Findings critiques

### Pas dangereux

| Finding | Explication |
|---|---|
| `graphiti_write_true` dans docs/ | Mentions narratives dans audit docs — pas du code actif |
| `subprocess` dans docs/runtime/ | Descriptions de plans — pas de code exécutable |
| `requests.post` dans connectors/ | Fonctionnel et documenté — aviation_robo, bank_normal_flow, trading_live |
| `admin1234` dans proofs/V18_3_1/ | Code proof legacy — non exécuté, proof repo |
| `DRY_RUN_ONLY` absent dans routes/ | Routes existantes — non concernées par le pattern P65 |

### Review requis (P68+)

| Finding | Surface | Action future |
|---|---|---|
| `runtime_allowed_now` dans `routes/brody.py`, `routes/os_map.py`, `routes/source_runtime_status.py` | routes/ | P68 — vérifier que ces routes ne sont pas actives en prod |
| `NEO4J_PASSWORD` sans guard `fail fermé` dans quelques modules periphery | periphery/ | P68+ — vérifier chaque occurrence (P66 a déjà corrigé neo4j_brody_guide_bridge) |
| `kernel_mutation_true` dans 42 fichiers | tests/ + runtime_wiring/ | Vérifier que c'est uniquement tests et runtime_wiring gelé |
| `UNKNOWN_REQUIRES_REVIEW` 415 fichiers | periphery/ + audit_docs/ | Revue progressive — pas d'urgence |

### Interdit futur

| Finding | Règle |
|---|---|
| `canonical_memory_write` dans chemin SRL readonly | CANONICAL_MEMORY_WRITE_FORBIDDEN |
| `graphiti_write` hors zones MANUAL_GRAPHITI_WRITE_ZONE | GRAPHITI_WRITE_FORBIDDEN |
| `neo4j_write` sans opérateur humain KX108_ONLY | NEO4J_WRITE_FORBIDDEN |
| `kernel_mutation` hors P-palier autorisé | KERNEL_MUTATION_FORBIDDEN |

### Dettes préexistantes

| Fichier | Statut |
|---|---|
| `audit/world_action_bus.jsonl` | HASH_MISMATCH_PREEXISTING_P65 — manifest drift documenté |
| `proofs/PROOFKIT_REPORT.json` | HASH_MISMATCH_PREEXISTING_P65 — manifest drift documenté |
| `tests/test_invariants_against_engine.py` | ModuleNotFoundError: obsidia_os2 — module vendor absent |
| `tests/sigma_stress_test.py` | ModuleNotFoundError: agents.obsidia_sigma_v130 |
| `tests/test_agents_functional.py` | ImportError: TradingState from agents |
| `tests/test_consensus_inprocess.py` | ModuleNotFoundError: agents.run_pipeline |
| `tests/test_sigma_v18_9.py` | ModuleNotFoundError: agents.obsidia_sigma_v130 |

### Zones Graphiti write déjà quarantinées P66

Les deux modules write Graphiti identifiés sont hors chemin SRL readonly (quarantinés P66) :
- `graphiti_import_apply_guarded_manual_only` → `QUARANTINE_FOR_SRL_PATH`
- `graphiti_guarded_manual_apply_from_review_decision_readonly_memory_only` → `QUARANTINE_FOR_SRL_PATH`

---

## 5. Décision

P67 ne corrige pas. P67 classe.

Le modèle boundary à 14 dimensions permet de distinguer :
- ce qui est safe readonly (532 fichiers confirmés)
- ce qui est autorisé en mode audit local (artifact_write, report_write)
- ce qui nécessite review (network_egress, subprocess, path_exposure)
- ce qui est interdit sans exception (canonical_memory_write, graphiti_write hors zone, kernel_mutation)

**Prochain geste : P68 — API auth / route exposure audit.**

Focus P68 :
- `routes/brody.py`, `routes/os_map.py`, `routes/source_runtime_status.py` — `runtime_allowed_now` présent
- `connectors/` — appels réseau actifs à valider
- `NEO4J_PASSWORD` occurrences sans guard fail fermé

---

**Verdict :** `P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT_READY`
