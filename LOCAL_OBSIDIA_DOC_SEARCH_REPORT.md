# LOCAL OBSIDIA DOC SEARCH REPORT
**Date :** 2026-06-09  
**Mode :** READ-ONLY — aucun fichier modifié  
**Dossiers scannés :**
- `obsidia-x108-proofs/` (hors node_modules)
- `obsi aleger/OBSIDIA_CLASSE/`

---

## A — RAG / Retrieval / Context Packet

| Priorité | Fichier | Chemin |
|---|---|---|
| HIGH | `context_packet_flow.py` | `connectors/` |
| HIGH | `CONTEXT_PACKET_BUILDER_V2.md` | `docs/context/` |
| HIGH | `CONTEXT_PACKET_TO_X108_READONLY_INGRESS_V1.md` | `docs/context/` |
| HIGH | `CONTEXT_SIGNAL_ONLY_POLICY_V1.md` | `docs/context/` |
| HIGH | `GRAPHITI_CONTEXT_ADAPTER_V1.md` | `docs/graphiti/` |
| HIGH | `GRAPHITI_READONLY_BRIDGE_V1.md` | `docs/graphiti/` |
| HIGH | `GRAPHITI_NO_WRITE_POLICY_V1.md` | `docs/graphiti/` |
| HIGH | `brody_semantic_query_router.py` | `apps/obsidia_api/` |
| HIGH | `brody_runtime_context_adapter.py` | `apps/obsidia_api/` |
| HIGH | `brody_temporal_context_adapter.py` | `apps/obsidia_api/` |
| HIGH | `routes/context.py` | `apps/obsidia_api/routes/` |
| MEDIUM | `BRODY_TRIADIC_MEMORY_GOVERNOR_READONLY_V1.md` | `docs/periphery/` |
| MEDIUM | `interface_ready_memory_flow.py` | `connectors/` |
| MEDIUM | `BRODY_GRAPHITI_LIVE_READONLY_REPORT.md` | `docs/freeze/` |
| MEDIUM | `BRODY_LLM_OBSIDIEN_SOURCE_DOCS_AUDIT.md` | `docs/freeze/` |

**Résumé :** Le context packet est le mécanisme central RAG d'Obsidia. Il est construit dans `CONTEXT_PACKET_BUILDER_V2.md`, injecté en lecture seule vers X108 via `CONTEXT_PACKET_TO_X108_READONLY_INGRESS_V1.md`, et routé sémantiquement par `brody_semantic_query_router.py`. Graphiti est le graph-store readonly.

---

## B — RLHF / RCHF / Feedback humain / Calibration

| Priorité | Fichier | Chemin |
|---|---|---|
| HIGH | `FEEDBACK_MEMORY_CANDIDATE_POLICY_V0.md` | `docs/memory/` |
| HIGH | `MEMORY_CANDIDATE_LEDGER_V1.md` | `docs/memory/` |
| HIGH | `MEMORY_PROMOTION_MANUAL_ONLY_V1.md` | `docs/memory/` |
| HIGH | `memory_feedback_candidate_flow.py` | `connectors/` |
| HIGH | `brody_candidate_memory_adapter.py` | `apps/obsidia_api/` |
| HIGH | `BRODY_FREEZE_METRICS_SNAPSHOT` | `apps/obsidia_api/` |
| MEDIUM | `MEMORY_SECURITY_BOUNDARY_V1.md` | `docs/memory/` |
| MEDIUM | `MEMORY_SOURCE_REGISTRY_V1.md` | `docs/memory/` |
| MEDIUM | `BANK_TRADING_GPS_CALIBRATION_WORLDS_V0.md` | `docs/architecture/` |
| MEDIUM | `BRODY_THREE_FOUNDATIONS_VALIDATION_REPORT.md` | `docs/freeze/` |

**Résumé :** Obsidia ne fait pas de RLHF au sens classique (pas d'entraînement de poids). Le mécanisme équivalent est la **mémoire candidate** : feedback humain capturé → candidat validé manuellement → promotion vers mémoire permanente. Fichiers clés : `MEMORY_PROMOTION_MANUAL_ONLY_V1.md` et `memory_feedback_candidate_flow.py`.

---

## C — Automatisation de l'automatisation

| Priorité | Fichier | Chemin |
|---|---|---|
| HIGH | `brody_automation_orchestrator.py` | `apps/obsidia_api/` |
| HIGH | `brody_full_runtime_orchestrator.py` | `apps/obsidia_api/` |
| HIGH | `brody_full_runtime_reconnect.py` | `apps/obsidia_api/` |
| HIGH | `BRODY_AUTOMATION_LAYER_BINDING_REPORT.md` | `docs/freeze/` |
| HIGH | `BRODY_AUTOMATION_SNAPSHOT_API_REPORT.md` | `docs/freeze/` |
| HIGH | `BRODY_EXISTING_AUTOMATION_MODULES_AUDIT.md` | `docs/freeze/` |
| HIGH | `BRODY_WORKBENCH_AUTOMATION_PANEL_REPORT.md` | `docs/freeze/` |
| MEDIUM | `CONTROL_PLANE_ORCHESTRATOR_SPEC_V0.md` | `docs/architecture/` |
| MEDIUM | `AGENTIC_ENGINE_EXTENSION_MAP_V0.md` | `docs/architecture/` |
| MEDIUM | `audit_brody.py` | `apps/obsidia-workbench/` |

**Résumé :** L'orchestrateur principal est `brody_full_runtime_orchestrator.py`. Il gère le cycle complet : context packet → réponse → snapshot. La couche automation est documentée dans `BRODY_AUTOMATION_LAYER_BINDING_REPORT.md`.

---

## D — Loop / Boucle / Orchestration / Planification

| Priorité | Fichier | Chemin |
|---|---|---|
| HIGH | `brody_operator_loop_adapter.py` | `apps/obsidia_api/` |
| HIGH | `brody_bridge_lifecycle.py` | `apps/obsidia_api/` |
| HIGH | `ACTION_SEQUENCE_GOVERNOR_V0.md` | `docs/act/` |
| HIGH | `ACTION_LIFECYCLE_CONTRACT_V0.md` | `docs/act/` |
| HIGH | `ACTION_CANDIDATE_TO_WORLD_ACTION_FLOW_V0.md` | `docs/act/` |
| HIGH | `WORLD_ACTION_DRY_RUN_POLICY_V0.md` | `docs/act/` |
| HIGH | `CONTROL_PLANE_ORCHESTRATOR_SPEC_V0.md` | `docs/architecture/` |
| HIGH | `CI_PIPELINE_X108_PERIPHERY_V1.md` | `docs/ci/` |
| MEDIUM | `brody_real_response_pipeline.py` | `apps/obsidia_api/` |
| MEDIUM | `brody_memory_response_chain_adapter.py` | `apps/obsidia_api/` |
| MEDIUM | `OS3_REPLAY_MANIFEST_V0.md` | `docs/os3/` |
| MEDIUM | `OS3_HASH_CHAIN_POLICY_V0.md` | `docs/os3/` |
| LOW | `routes/periphery_ops.py` | `apps/obsidia_api/routes/` |

**Résumé :** La boucle opérateur est dans `brody_operator_loop_adapter.py`. Le cycle action est gouverné par `docs/act/`. OS3 gère le replay de preuves. Le pipeline de réponse est `brody_real_response_pipeline.py`.

---

## E — Chemin fidèle / Cohérence / Gouvernance du chemin

| Priorité | Fichier | Chemin |
|---|---|---|
| HIGH | `COGNITION_TO_ACTION_GOVERNANCE_V1.md` | `docs/civilization/` |
| HIGH | `CAPABILITY_IS_NOT_AUTHORITY_V1.md` | `docs/civilization/` |
| HIGH | `OBSIDIA_AS_AGENTIC_GOVERNANCE_INFRASTRUCTURE_V1.md` | `docs/civilization/` |
| HIGH | `AGENTIC_CONSTITUTIONAL_CIVILIZATION_STACK_V1.md` | `docs/civilization/` |
| HIGH | `SOURCE_OF_TRUTH_POLICY_V0.md` | `docs/architecture/` |
| HIGH | `CROSS_LAYER_STABILIZATION_MATRIX_V0.md` | `docs/architecture/` |
| HIGH | `routing_rules.md` | `agents/routing/` |
| HIGH | `AGENT_TO_GATE_MAPPING_V0.md` | `docs/agents/` |
| HIGH | `NON_SOVEREIGN_AGENT_CONTRACT_V0.md` | `docs/agents/` |
| HIGH | `brody_tree_policy.py` | `apps/obsidia_api/` |
| HIGH | `brody_tree_policy_adapter.py` | `apps/obsidia_api/` |
| HIGH | `brody_source_of_truth_adapter.py` | `apps/obsidia_api/` |
| MEDIUM | `BRODY_NO_DECISION_POLICY_V1.md` | `docs/brody/` |
| MEDIUM | `PERIPHERY_NON_SOVEREIGNTY_CONTRACT_V0.md` | `docs/architecture/` |
| MEDIUM | `O5_ELIMINATION_DECISIONNELLE.md` | `periphery/.../02_CONSTITUTION_LOIS_OBSIDIENNES/` |
| MEDIUM | `O8_SEPARATION_COGNITION_ACTION.md` | `periphery/.../02_CONSTITUTION_LOIS_OBSIDIENNES/` |
| MEDIUM | `.claude/context/AGENTIC_ROUTING.md` | `.claude/context/` |

**Résumé :** Le "chemin fidèle" est incarné par la tree_policy + source_of_truth + lois obsidiennes (O1–O8). La séparation cognition/action (O8) est le principe central. `COGNITION_TO_ACTION_GOVERNANCE_V1.md` est le doc le plus stratégique ici.

---

## F — X108 / KX108 / Authority / Guard / Proof / Replay

| Priorité | Fichier | Chemin |
|---|---|---|
| HIGH | `apps/obsidia_api/routes/x108.py` | `apps/obsidia_api/routes/` |
| HIGH | `apps/obsidia-workbench/src/views/X108View.tsx` | frontend |
| HIGH | `BACKEND_BINDING_PLAN_X108_PROOFS.md` | `apps/obsidia-workbench/` |
| HIGH | `X108_REBRANCHING_POLICY_V0.md` | `docs/architecture/` |
| HIGH | `O3_EPREUVE_TEMPORELLE_X108.md` | `periphery/.../02_CONSTITUTION_LOIS_OBSIDIENNES/` |
| HIGH | `brody_rights_authority_matrix.py` | `apps/obsidia_api/` |
| HIGH | `BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md` | `docs/freeze/` |
| HIGH | `BRODY_WORKBENCH_AUTHORITY_SNAPSHOT_REPORT.md` | `docs/freeze/` |
| HIGH | `OS3_PROOF_TICKET_SCHEMA_V0.md` | `docs/os3/` |
| HIGH | `OS3_REPLAY_MANIFEST_V0.md` | `docs/os3/` |
| HIGH | `ONCHAIN_AUDIT_PACKET_V1.md` | `docs/blockchain/` |
| HIGH | `CANON_GUARDIAN.md` | `agents/prompts/` |
| HIGH | `PROOF_SENTINEL.md` | `agents/prompts/` |
| HIGH | `PROOF_INDEX.md` | racine repo |
| MEDIUM | `FREEZE_CRITERIA_FULL_STACK_V0.md` | `docs/architecture/` |
| MEDIUM | `FULL_STACK_FREEZE_MANIFEST_V0.md` | `docs/freeze/` |
| MEDIUM | `x108-periphery-ci.yml` | `.github/workflows/` |

**Résumé :** X108 est le kernel d'autorité finale. La route `x108.py` est le seul endpoint autorisé à valider les décisions. La matrix d'autorité est dans `brody_rights_authority_matrix.py`. OS3 gère le replay de preuves hashées.

---

## G — Brody / Memory / Opérateur

| Priorité | Fichier | Chemin |
|---|---|---|
| HIGH | `brody_full_runtime_orchestrator.py` | `apps/obsidia_api/` |
| HIGH | `brody_project_memory_adapter.py` | `apps/obsidia_api/` |
| HIGH | `brody_project_memory_runtime.py` | `apps/obsidia_api/` |
| HIGH | `brody_session_memory_adapter.py` | `apps/obsidia_api/` |
| HIGH | `brody_session_memory_runtime.py` | `apps/obsidia_api/` |
| HIGH | `brody_candidate_memory_adapter.py` | `apps/obsidia_api/` |
| HIGH | `brody_cognitive_modules_adapter.py` | `apps/obsidia_api/` |
| HIGH | `BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE.md` | `docs/freeze/` |
| HIGH | `BRODY_FOUNDATION_B_SESSION_MEMORY_FOLLOWUP_FREEZE.md` | `docs/freeze/` |
| HIGH | `BRODY_FOUNDATION_C_TRUE_RESPONSE_STRUCTURE_FREEZE.md` | `docs/freeze/` |
| HIGH | `BRODY_THREE_FOUNDATIONS_CURRENT_STATE_AUDIT.md` | `docs/freeze/` |
| HIGH | `BRODY_LANGUAGE_ROUTING_V1.md` | `docs/brody/` |
| HIGH | `BRODY_RESPONSE_CONTRACT_V1.md` | `docs/brody/` |
| HIGH | `BRODY_RUNTIME_READONLY_V1.md` | `docs/brody/` |
| HIGH | `brody_memory_readonly_flow.py` | `connectors/` |
| HIGH | `BrodyPanel.tsx` | `apps/obsidia-workbench/src/components/` |
| HIGH | `brodyResponseComposer.ts` | `apps/obsidia-workbench/src/lib/` |
| MEDIUM | `BRODY_FULL_POINTER_MAP.md` | `docs/freeze/` |
| MEDIUM | `BRODY_RUNTIME_MODULE_USAGE_REPORT.md` | `docs/freeze/` |
| MEDIUM | `routes/brody.py` | `apps/obsidia_api/routes/` |
| MEDIUM | `routes/brody_monitoring.py` | `apps/obsidia_api/routes/` |
| MEDIUM | `routes/memory.py` | `apps/obsidia_api/routes/` |

**Résumé :** Brody a 3 fondations : project_memory, session_memory, true_response_structure. Il est opérateur (prépare/orchestre) mais ne décide pas (BRODY_NO_DECISION_POLICY). Les routes API sont `brody.py` et `brody_monitoring.py`.

---

## H — Jeux / Simulateurs / Éducation agentique

| Priorité | Fichier | Chemin |
|---|---|---|
| HIGH | `OBSIDIA_MMONDE_REVERSE_OS_34ARBRES_AGENTS_P2PLUS_V1/` | `periphery/` — 34 arbres décisionnels complets |
| HIGH | `ARBRE_01__Arbre_de_l_Humain/` (+ 33 autres) | `periphery/.../04_ARBRES_34_TENSOR_MATRIX/` |
| HIGH | `WORLD_ACTION_DRY_RUN_POLICY_V0.md` | `docs/act/` |
| HIGH | `TRANSACTION_SIMULATOR_DRYRUN_V1.md` | `docs/blockchain/` |
| HIGH | `docs/education/README.md` | `docs/education/` |
| HIGH | `O5_ELIMINATION_DECISIONNELLE.md` | `periphery/.../02_CONSTITUTION/` |
| MEDIUM | `BANK_SCENARIOS.md` | `docs/` |
| MEDIUM | `P2_BANK_ADVERSARIAL_SCOPE.md` | `docs/` |
| MEDIUM | `P2_BANK_FUZZ_SCALE_SCOPE.md` | `docs/` |
| MEDIUM | `BANK_ROBO_REAL_E2E_VALIDATION.md` | `docs/` |
| MEDIUM | `HACKATHON_TO_OBSIDIA_MAPPING_V1.md` | `docs/hackathons/` |
| MEDIUM | `HACKATHON_FAILURE_TAXONOMY_V1.md` | `docs/hackathons/` |
| LOW | `connectors/aviation_robo.py` | `connectors/` |
| LOW | `connectors/bank_normal_flow.py` | `connectors/` |

**Résumé :** Les 34 Arbres (`OBSIDIA_MMONDE`) sont les environnements décisionnels d'éducation agentique — chaque arbre a ses règles d'activation, exemples, non-décision contract et tests. `WORLD_ACTION_DRY_RUN_POLICY_V0.md` est la politique de simulation sans effet réel.

---

## Doublons probables détectés

| Groupe | Fichiers similaires |
|---|---|
| Brody response | `brody_backend_response_composer.py` ↔ `brody_structured_response_engine_adapter.py` ↔ `brody_true_response_structure_adapter.py` — variantes du même mécanisme |
| Brody memory | `brody_project_memory_adapter.py` ↔ `brody_project_memory_runtime.py` — adapter + runtime du même module |
| Brody session | `brody_session_memory_adapter.py` ↔ `brody_session_memory_runtime.py` — idem |
| Authority reports | `BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md` ↔ `BRODY_WORKBENCH_AUTHORITY_SNAPSHOT_REPORT.md` — même périmètre |
| Context docs | `CONTEXT_PACKET_BUILDER_V2.md` ↔ `CONTEXT_PACKET_TO_X108_READONLY_INGRESS_V1.md` — complémentaires, pas doublons réels |
| Freeze close reports | `FINAL_BRODY_FULL_CLOSE_REPORT.md` ↔ `BRODY_FULL_LIVE_RUNTIME_CLOSE_REPORT.md` — rapports d'étape successifs |

---

## Synthèse — Documents prioritaires pour construire Band / Brody / RAG-RCHF / X108 / Jeux

| Couche | Fichier clé | Action recommandée |
|---|---|---|
| **Band** (coordination visible) | `CONTROL_PLANE_ORCHESTRATOR_SPEC_V0.md` | Lire comme spec principale |
| **Band** | `ACTION_SEQUENCE_GOVERNOR_V0.md` + `ACTION_LIFECYCLE_CONTRACT_V0.md` | Defines the visible loop |
| **Brody** (orchestration) | `brody_full_runtime_orchestrator.py` | Code source central |
| **Brody** | `BRODY_THREE_FOUNDATIONS_CURRENT_STATE_AUDIT.md` | Vue d'état complète |
| **RAG** | `CONTEXT_PACKET_BUILDER_V2.md` | Spec du context packet |
| **RCHF** | `FEEDBACK_MEMORY_CANDIDATE_POLICY_V0.md` + `MEMORY_PROMOTION_MANUAL_ONLY_V1.md` | Politique de feedback |
| **X108** | `brody_rights_authority_matrix.py` | Authority matrix code |
| **X108** | `O3_EPREUVE_TEMPORELLE_X108.md` | Loi constitutionnelle X108 |
| **Jeux** | `periphery/OBSIDIA_MMONDE.../04_ARBRES_34_TENSOR_MATRIX/` | 34 arbres décisionnels |
| **Jeux** | `WORLD_ACTION_DRY_RUN_POLICY_V0.md` | Politique de simulation |

