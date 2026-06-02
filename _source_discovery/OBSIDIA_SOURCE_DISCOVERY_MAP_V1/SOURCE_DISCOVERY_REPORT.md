# OBSIDIA_SOURCE_DISCOVERY_MAP_V1

**Date** : 2026-06-02
**Mode** : SOURCE_DISCOVERY_ONLY
**Repo principal** : `obsidia-x108-proofs_REMOTE_A5F21C6B`
**Branche** : `main`

---

## 1. Mode

```
SOURCE_DISCOVERY_ONLY
```

Aucun patch runtime. Aucun commit. Aucun push. Aucune spec finale créée.
Seuls les 6 fichiers du dossier `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1/` ont été créés.

---

## 2. Repos inspectés

| Repo | Présent localement | Statut | Notes |
|------|--------------------|--------|-------|
| `obsidia-x108-proofs_REMOTE_A5F21C6B` | OUI | PRESENT_LOCAL — repo principal | Branche main, ahead 1 par rapport à origin |
| `obsidia-x108-proofs` | OUI | PRESENT_LOCAL | Clone propre |
| `_obsidia-local-workspace` | OUI | PRESENT_LOCAL — données privées | Contient graphiti/mmonde/session-packets retirés du public |
| `obsidia-x108-proofs_PUSH_CLEAN_20260526_195026` | OUI | PRESENT_LOCAL | Snapshot push clean |
| `obsidia-x108-proofs-agentic-registry` | OUI | PRESENT_LOCAL | Registry agentic |
| `obsidia-x108-proofs-graph-memory` | OUI | PRESENT_LOCAL | Graphiti memory |
| `obsidiashell-main` | OUI | PRESENT_LOCAL | Shell Obsidia |
| `proofs` | OUI | PRESENT_LOCAL | Preuves Lean/TLA+ |
| `obsidia-engine-candidate` | OUI | PRESENT_LOCAL | Candidat moteur |
| `obsidia-workspace` (standalone) | NON | ABSENT_LOCAL_REPO | Workspace hub = intégré dans `periphery/OBSIDIA_V4_STRUCTURED_FULL/` |
| `Demo-obsidia-x108-proof` | NON VÉRIFIÉ | ABSENT_LOCAL_REPO | Hors scope session |
| `bank-robo` | NON VÉRIFIÉ | ABSENT_LOCAL_REPO | Hors scope session |
| `agentic-commerce-safe-demo-V2` | NON VÉRIFIÉ | ABSENT_LOCAL_REPO | Hors scope session |
| `Obsidia-lab-trad` | NON VÉRIFIÉ | ABSENT_LOCAL_REPO | Hors scope session |
| `obsidia-guard-v1-github` | NON VÉRIFIÉ | ABSENT_LOCAL_REPO | Hors scope session |
| `agi-vison` | NON VÉRIFIÉ | ABSENT_LOCAL_REPO | Hors scope session |
| `preprint-conscience` | NON VÉRIFIÉ | ABSENT_LOCAL_REPO | Hors scope session |

---

## 3. Résumé exécutif

### Ce qui est confirmé (sources réelles trouvées)

- **23/23 sources prioritaires** présentes dans `obsidia-x108-proofs_REMOTE_A5F21C6B`
- **8/8 chemins MMONDE/Tree34** présents (`periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/`)
- **Action lifecycle complet** : 10 états (INPUT_CAPTURED → CLOSED) + FEEDBACK_CAPTURED confirmés dans `periphery/action_lifecycle.py`
- **KX108 / X108 gate** : présent dans `os3_ticket.py`, `export_for_x108.py` — ALLOW/HOLD/BLOCK opérationnels
- **Shazam Cognitif** : `periphery/cognitive_trees/shazam_cognitif.py` — `can_decide=False`, `can_emit_act=False`
- **BDF Double Cerveau** : `periphery/bdf/double_brain_router.py` — `emits_act=False`, `emits_verdict=False`
- **HexaFlux/LTCU+** : `periphery/hexaflux/ltcu_plus.py` — `advisory_only=True`, `authorizes=False`
- **MCP Bridge** : `periphery/mcp_bridge.py` — `non_decision=True`
- **Gencoin** : `periphery/gencoin.py`, `gencoin_ledger.py` — ledger uniquement, `mint_allowed=False` si gate ≠ ALLOW
- **GPS / Aviation** : stack complet — adapter + connector + sigma domain
- **Agents 52 registry** : `periphery/.../10_AGENTS_52/agents_52.registry.json` — 52 agents, dont 10 premiers lus

### Ce qui est seulement partiel

- **F77 Pack Externe** : `PACK_PARTIAL` — `external_pack/` inexistant, 9 fichiers manquants
- **Jarvis / Reverse OS / SSR** : `jarvis_projection.py` = PLACEHOLDER (stub 3 lignes)
- **Balance / BUV** : runtime sandbox présent (`balance_operator.py`) — pas de spec master unifiée
- **Lyapunov / PoG / Governed State** : Python specs présentes — FORMAL_PROOF_PENDING (pas de Lean proof pour ces fichiers)
- **.xyz / XYZ pipeline** : `BRANCHESXYZKLN.md` trouvé — contenu non lu en détail

### Ce qui est absent sous ce nom

- **Jcoin** : ABSENT_UNDER_THIS_NAME — 0 occurrences dans tout le repo
- **7 flux exacts (corpus canonique public)** : explicitement hors périmètre public (`docs/REPO_BOUNDARY.md:84`)
- **`agi_subordination_spec.md`** : concept présent dans `CAPABILITY_IS_NOT_AUTHORITY_V1.md` — pas de fichier dédié
- **`buv_master_spec.md`** : BALANCE_CANON.md est la source la plus proche
- **`obsidia-workspace`** (repo standalone) : workspace = `periphery/OBSIDIA_V4_STRUCTURED_FULL/`

### Ce qui est dangereux en claim-scope

- **"fully formally proven"** : FAUX pour Lyapunov/PoG/governed_state — Python spec uniquement
- **"production-ready"** : BLOQUÉ (F76 PROD_BLOCKED) — 4 bloqueurs : CORS wildcard, auth absente, Dockerfile manquant, /health manquant
- **"cloud-ready"** : NON — explicitement nié dans `BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md`
- **"AGI-ready"** : HORS_SCOPE — `docs/architecture/F74_F77_FINALIZATION_AUDIT.md:293`
- **Gencoin = token réel** : FAUX — `GENCOIN_NOT_A_TOKEN_POLICY_V1.md` : "Gencoin is NOT a real token"
- **Tree34 = moteur AGI** : NON — arbres = signaux contextuels, aucun ACT émis
- **Brody non souverain = inutile** : FAUX — Brody = signal contextuel précieux, readonly

---

## 4. Cartographie par blocs

### Bloc 1 — Workspace / Hub intellectuel

- **Terme Gemini** : `obsidia-workspace`, `fondations/`, `domaines/`, `agents/`, `gouvernance/`
- **Réalité GitHub** : `periphery/OBSIDIA_V4_STRUCTURED_FULL/` (15 dossiers : 00_INDEX à 14_REGROUPEMENTS_COHERENCE)
- **Chemin exact** : `periphery/OBSIDIA_V4_STRUCTURED_FULL/`
- **Structure** : `02_BLOCS_17/`, `03_PEPITES_161/`, `04_SPECS_40/`, `05_MODULES_A1_A24/`, `06_GARDIENS_DE_FOND_T1_T12/`, `07_AGENTS_ET_ROLES/`, `08_PREUVES_LEAN_TLA/`, etc.
- **Statut** : DOC_ONLY (arborescence de specs, pas de runtime)
- **Ce que la source prouve** : Hub intellectuel V4 structuré en 15 groupes thématiques
- **Ce qu'elle ne prouve pas** : Runtime — c'est une structure documentaire

---

### Bloc 2 — Scope public / Claim-scope

- **Source** : `docs/PROOF_SCOPE.md` — SOURCE_CANON
- **4 catégories de preuves** : Lean 4 (`proofs/lean/`), TLA+ (`formal/tla/`), Python exécutable (`proofs/`), Sigma minimale
- **Ce que PASS signifie** dans chaque catégorie : défini précisément dans le fichier
- **Spec future** : déjà spec — NE PAS MODIFIER
- **Risque** : confondre "PASS Python test" avec "preuve formelle" = CLAIM_SCOPE_RISK

---

### Bloc 3 — V3/V4 Gaps

- **Source** : `docs/V3_V4_GAP_ANALYSIS.md` — DOC_ONLY
- **Date** : 2026-05-19
- **Statut** : 22 domaines COMPLETE (Agent Registry, OS3 Replay, Gencoin Ledger/Debt/Distribution, Gencoin Sandbox, World Call Gateway, Math Core, Lyapunov, PoG, Language Router, Education Score, Bias Gate, Document Ingestion, Context Packet/X108 Ingress, MCP Permission Matrix, GitHub Workflow Guard, Benchmark, JSON Schemas, Integration Tests, Non-sovereignty Tests, Periphery Tests, Demo Connectors, Documentation, Validation 194 tests)
- **Ce que COMPLETE signifie** : implémentation Python présente — pas forcément preuve formelle

---

### Bloc 4 — Action lifecycle

- **Source** : `periphery/action_lifecycle.py` — RUNTIME_CODE
- **10 états** : INPUT_CAPTURED → ACTION_CANDIDATE_BUILT → PERIPHERY_SCORED → SIGMA_ROUTED → X108_EVALUATED → OS3_TICKETED → GENCOIN_EVALUATED → WORLD_ACTION_DRY_RUN_READY → FEEDBACK_CAPTURED → MEMORY_CANDIDATE_BUILT → CLOSED
- **Note** : FEEDBACK_CAPTURED (ligne 28) absent du prompt original — état présent dans la source
- **Statut** : RUNTIME_CODE — transitions définies en Python
- **Spec future** : `specs/ACTION_LIFECYCLE_SPEC_V1.md`

---

### Bloc 5 — Governed state / Entropy / Lyapunov / PoG

- **Sources** :
  - `periphery/math_core/governed_state.py` — PYTHON_SPEC
  - `periphery/math_core/lyapunov.py` — PYTHON_SPEC
  - `periphery/math_core/proof_of_governance.py` — PYTHON_SPEC
  - `periphery/energy_thermo.py` — PYTHON_SPEC
  - `periphery/gencoin_debt_model.py` — PYTHON_SPEC
- **Ce que la source prouve** : spécification Python des métriques (thermo_debt, delta_E, delta_C, computational_debt, timeline_drift, violence_score, feasibility_score)
- **Ce qu'elle ne prouve pas** : preuve formelle Lean — FORMAL_PROOF_PENDING pour tous ces fichiers
- **Risque** : "Lyapunov Python spec ≠ Lean proof" — ne jamais clamer stabilité prouvée formellement

---

### Bloc 6 — OS3 Ticket / Replay

- **Source** : `periphery/os3_ticket.py` — RUNTIME_CODE
- **Champs** : ticket_id, action_id, domain, x108_gate, reason_code, severity, scores, unknowns, risk_flags, contradictions, evidence_refs, input_hash, output_hash, trace_hash, merkle_root, replay_status
- **Hashes** : sha256(input), sha256(output), sha256({input+output+packet}), sha256([ih,oh,th]) = merkle_root
- **replay_status** : "NOT_RUN" par défaut
- **Spec future** : `specs/OS3_PROOF_TICKET_SPEC_V1.md`

---

### Bloc 7 — Balance / BUV

- **Sources** :
  - `periphery/gencoin_sandbox/balance_operator.py` — RUNTIME_CODE + SANDBOX
  - `docs/gencoin/sandbox_pre_freeze/BALANCE_CANON.md` — DOC_ONLY
  - `docs/gencoin/sandbox_pre_freeze/LIMITS_AND_STATUS.md` — DOC_ONLY
- **Terme Gemini** : BUV = Balance Universelle Valorisée (ou Balance Obsidienne)
- **Réalité** : pas de fichier `buv_master_spec.md` — BALANCE_CANON.md est la source canonique
- **Spec future** : `specs/BALANCE_BUV_MASTER_SPEC_V1.md`
- **Risque** : "Balance ≠ décision finale" — résultat d'une évaluation multi-facteur

---

### Bloc 8 — Gencoin / Jcoin

- **Sources** :
  - `periphery/gencoin.py` — RUNTIME_CODE
  - `periphery/gencoin_ledger.py` — RUNTIME_CODE
  - `periphery/gencoin_debt_model.py` — PYTHON_SPEC
  - `periphery/gencoin_distribution.py` — RUNTIME_CODE
  - `docs/gencoin/GENCOIN_FORMAL_MATH_SPEC_V0_2.md` — DOC_ONLY
  - `docs/gencoin/GENCOIN_DISTRIBUTION_LAW_V0.md` — DOC_ONLY
  - `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md` — SOURCE_CANON
  - `periphery/blockchain/token_policy.py` — SOURCE_CANON
- **Jcoin** : ABSENT_UNDER_THIS_NAME — 0 occurrences dans tout le repo
- **Formule GC** : `GC = X108_ALLOW × OS3_PROOF × DATA_OK × MEMORY_STABLE × ENERGY_STABLE × OC_STABLE × PERMISSION_OK × ECONOMIC_OK × max(0, VALUE-DEBT)`
- **Statut** : candidate — ledger append-only, jamais on-chain
- **Risque** : "candidate ≠ token réel" — BLOCK absolu sur MINT/DEPLOY/CREATE

---

### Bloc 9 — GPS / Défense / Aviation

- **Sources** :
  - `periphery/adapters/gps_adapter.py` — RUNTIME_CODE
  - `connectors/aviation_robo.py` — RUNTIME_CODE
  - `sigma/domains/gps_defense_aviation_agents.py` — RUNTIME_CODE
  - `docs/periphery/GPS_ADAPTER_MAPPING_V0.md` — DOC_ONLY
  - `docs/architecture/BANK_TRADING_GPS_CALIBRATION_WORLDS_V0.md` — DOC_ONLY
- **Scores présents** : trajectory_drift_score, source_conflict_score, time_skew_score, brownout_score
- **Verdicts possibles** : ABORT_TRAJECTORY, RECALC_TRAJECTORY, TRAJECTORY_VALID
- **Statut** : RUNTIME_CODE + DRY_RUN — POST local uniquement (`http://127.0.0.1:8000`)
- **Risque** : "GPS strategic surface ≠ défense production" — validation externe requise

---

### Bloc 10 — Tree34 / AGI / Flux

- **Sources** :
  - `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/00_INDEX/ARBORESCENCE_COMPLETE.md` — DOC_ONLY
  - `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/04_ARBRES_34_TENSOR_MATRIX/` — DOC_ONLY
  - `apps/obsidia_api/brody_tree_policy.py` — RUNTIME_CODE (T31 = "Arbre des Flux")
- **7 flux** : mentionnés dans `docs/REPO_BOUNDARY.md:84` comme HORS périmètre public
- **Arbres T20-T34** : présents dans arborescence — signaux contextuels uniquement
- **Statut** : DOC_ONLY + RUNTIME_CODE partiel
- **Risque** : "Tree34 ≠ moteur AGI" — signaux contextuels, aucun ACT émis

---

### Bloc 11 — Shazam / Reverse OS / BDF / HexaFlux / MCP Bridge

| Composant | Fichier source | Statut | Constraint clé |
|-----------|----------------|--------|----------------|
| Shazam Cognitif | `periphery/cognitive_trees/shazam_cognitif.py` | RUNTIME_CODE + ADVISORY_ONLY | `can_decide=False`, `can_emit_act=False` |
| BDF Double Cerveau | `periphery/bdf/double_brain_router.py` | RUNTIME_CODE + ADVISORY_ONLY | `emits_act=False`, `emits_verdict=False` |
| HexaFlux / LTCU+ | `periphery/hexaflux/ltcu_plus.py` | RUNTIME_CODE + ADVISORY_ONLY | `advisory_only=True`, `authorizes=False` |
| MCP Bridge | `periphery/mcp_bridge.py` | RUNTIME_CODE + ADVISORY_ONLY | `non_decision=True`, `policy_scope=READONLY_CONTEXT` |
| Jarvis / SSR | `periphery/jarvis_projection.py` | PLACEHOLDER | Stub 3 lignes — pas d'implémentation |
| Reverse OS | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/06_REVERSE_OS_SSR_JARVIS/` | DOC_ONLY | Dossier présent, contenu non lu |

---

### Bloc 12 — Agents 52

- **Source** : `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/10_AGENTS_52/agents_52.registry.json` — SOURCE_CANON
- **10 premiers agents lus** : OBSIDIA_ATLAS_INGESTOR, CANON_GUARDIAN, GRAPH_BUILDER, TERMINAL_BUILDER, PROOF_SENTINEL, CO_PILOTE_CODE, CI_REPO_SURGEON, REPO_HISTORIAN, VERSION_COMPARATOR, CARTOGRAPHE_PREUVES
- **Constraint** : `AgentPeripheral ↛ ACT` — `Decision = KX108` — `non_decision_contract` pour tout agent périphérique
- **Statut** : SOURCE_CANON — ne pas modifier sans protocole freeze

---

### Bloc 13 — Brody / Graphiti / Mémoire

- **Sources** :
  - `periphery/brody/brody_runtime_readonly.py` — RUNTIME_CODE + READONLY
  - `sigma/graphiti_readonly_bridge.py` — RUNTIME_CODE + READONLY
  - `docs/freeze/BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md` — SOURCE_CANON
  - `docs/freeze/BRODY_TREE_POLICY_BINDING_REPORT.md` — SOURCE_CANON
  - `apps/obsidia_api/brody_tree_policy.py` — RUNTIME_CODE
- **Contrainte** : Brody = readonly + advisory — toute écriture graphiti/neo4j nécessite gate humain (NEEDS_HUMAN_VALIDATION)
- **Risque** : "Brody non souverain ≠ Brody inutile" — signal contextuel de haute valeur

---

### Bloc 14 — F74-F77

| Feature | Statut | Bloqueurs documentés |
|---------|--------|----------------------|
| F74 Fresh Clone | COMPLETE | Procédures Windows + Linux dans `F74_F77_FINALIZATION_AUDIT.md` |
| F75 Lean Proofs | À vérifier | Périmètre `proofs/lean/` — non inspecté dans cette session |
| F76 Cloud/Prod | PROD_BLOCKED | CORS wildcard (`allow_origins=["*"]`), auth absente, Dockerfile manquant, /health manquant |
| F77 Pack Externe | PACK_PARTIAL | `external_pack/` inexistant, ONE_PAGE.md manquant, 9 fichiers à créer |

---

## 5. Concepts Gemini corrigés

| Terme Gemini | Correction GitHub réelle | Source | Notes |
|--------------|--------------------------|--------|-------|
| `/domaine/` | `02_BLOCS_17/` ou `04_SPECS_40/` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | Structure en blocs numérotés, pas `domaines/` |
| `/agent/` | `07_AGENTS_ET_ROLES/` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/07_AGENTS_ET_ROLES/` | — |
| `/fondation/` | `06_GARDIENS_DE_FOND_T1_T12/` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/06_GARDIENS_DE_FOND_T1_T12/` | — |
| `BUV` | `BALANCE_CANON.md` + `balance_operator.py` | `docs/gencoin/sandbox_pre_freeze/`, `periphery/gencoin_sandbox/` | BUV = concept audio/Gemini — terme réel = Balance Obsidienne |
| `Jcoin` | ABSENT — possible alias Gencoin | — | 0 occurrences dans tout le repo — clarification humaine requise |
| `obsidia-workspace` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | `periphery/` | Pas de repo standalone — workspace intégré |
| `.xyz` | `BRANCHESXYZKLN.md` | `periphery/OBSIDIA_V4_STRUCTURED_FULL/12_EXTENSIONS_R_D/` | Nom différent — contenu à vérifier |
| `sept flux / 7 flux` | T31 = "Arbre des Flux" | `apps/obsidia_api/brody_tree_policy.py:40` + `docs/REPO_BOUNDARY.md:84` | 7 flux exacts = HORS périmètre public |
| `Reverse OS` | `06_REVERSE_OS_SSR_JARVIS/` + `jarvis_projection.py` (stub) | `periphery/OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/` | Dossier présent, jarvis = PLACEHOLDER |
| `FEEDBACK_CAPTURED` (absent du prompt) | `FEEDBACK_CAPTURED` — 9e état du lifecycle | `periphery/action_lifecycle.py:28` | État présent dans source — à décider si public |

---

## 6. Points oubliés ou sous-sortis

| Point | Fichier réel | Statut | Note |
|-------|-------------|--------|------|
| Shazam Cognitif | `periphery/cognitive_trees/shazam_cognitif.py` | RUNTIME_CODE + ADVISORY_ONLY | Patterns : LANGUAGE, CAUSAL, RISK, AUTHORITY, EPISTEMIC, GOVERNANCE |
| BDF Double Cerveau | `periphery/bdf/double_brain_router.py` | RUNTIME_CODE + ADVISORY_ONLY | System 1 vs System 2 routing |
| HexaFlux / LTCU+ | `periphery/hexaflux/ltcu_plus.py` | RUNTIME_CODE + ADVISORY_ONLY | Context drift longue durée |
| MCP Bridge to Obsidia IR | `periphery/mcp_bridge.py` | RUNTIME_CODE + ADVISORY_ONLY | `policy_scope=READONLY_CONTEXT` |
| Reverse OS / SSR | `06_REVERSE_OS_SSR_JARVIS/` + `jarvis_projection.py` | PLACEHOLDER | Stub 3 lignes |
| Action lifecycle (FEEDBACK_CAPTURED) | `periphery/action_lifecycle.py:28` | RUNTIME_CODE | 9e état — absent du prompt original |
| Governed state metrics | `periphery/math_core/governed_state.py`, `energy_thermo.py` | PYTHON_SPEC | thermo_debt, delta_E, delta_C = Python uniquement |
| OS3ProofTicket (replay_status) | `periphery/os3_ticket.py` | RUNTIME_CODE | `replay_status="NOT_RUN"` par défaut — replay non implémenté |
| Aviation connector POST local | `connectors/aviation_robo.py` | RUNTIME_CODE + DRY_RUN | `http://127.0.0.1:8000` — pas de défense prod |
| F74-F77 bloqueurs | `docs/architecture/F74_F77_FINALIZATION_AUDIT.md:193-282` | DOC_ONLY | F76 PROD_BLOCKED + F77 PACK_PARTIAL |

---

## 7. Risques de dilution

| Paire de confusion | Danger réel |
|--------------------|-------------|
| Preuve publique ≠ production complète | PROOF_SCOPE.md définit le périmètre — ne pas extrapoler |
| "COMPLETE" ≠ preuve formelle | V3/V4 gap dit COMPLETE = Python implémenté, pas Lean-prouvé |
| dry-run ≠ production | GPS connector et aviation_robo = POST local uniquement |
| candidate ≠ token réel | Gencoin = ledger append-only — BLOCK absolu sur MINT |
| Balance ≠ décision finale | balance_operator.py = scoring sandbox, KX108 décide |
| Tree34 ≠ moteur AGI | Signaux contextuels uniquement — aucun ACT émis par les arbres |
| Brody non souverain ≠ Brody inutile | Brody = signal contextuel précieux + mémoire readonly |
| GPS strategic surface ≠ défense production | Validation externe requise pour tout usage défense |
| Lyapunov Python spec ≠ Lean proof | FORMAL_PROOF_PENDING pour tous les fichiers math_core/ |
| "AGI-ready" | HORS_SCOPE — explicitement interdit dans les audits F74-F77 |

---

## 8. Verdict Plan 1

```
PLAN1_SOURCE_DISCOVERY_READY
```

**Justification** :
- 23/23 sources prioritaires confirmées
- 8/8 chemins MMONDE/Tree34 confirmés
- Concepts Gemini corrigés (workspace, domaines, BUV, .xyz, Jcoin)
- Absences documentées (Jcoin, 7 flux publics)
- Risques de claim-scope identifiés et sourcés
- Aucun fichier runtime modifié
- 6 fichiers de rapport créés dans `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1/`
- Plan 2 prêt à recevoir la SOURCE_TO_SPEC_MAPPING.md et PLAN2_INPUT_MATRIX.md
