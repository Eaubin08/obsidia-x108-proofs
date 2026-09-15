# 10 · Système cognitif : Brody, Obsidure, agents

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Brody est l'organe d'intégration sémantique, un moteur de contexte et pas un LLM : son micro-core (14 signaux), son balance engine (11 tensions) et son point cloud 21D analysent chaque demande avant d'assembler une réponse « True Voice » à partir de sources locales. Il comprend, contextualise, relie et décompose, mais ne décide pas et ne porte pas l'identité, qui appartient à Oxygen. Obsidure construit sous gouvernance (patch candidat, sandbox, test, preuve) et ne promeut rien seul. Les agents conseillent.

## Où elle intervient dans le trajet d'une demande

- **Étape 4 · Organes spécialisés** : Brody comprend et formule, la mémoire rappelle, les domaines vérifient leur terrain, Obsidure prépare un candidat, Sigma et le Peripheral Mesh mesurent la cohérence, Tree34 et Thermo apportent leurs lectures. Ils proposent, ils ne décident pas.

Voir le trajet complet : [guide général](../README.md).

**Guides à lire pour cette couche :** [TRAJETS.md](../TRAJETS.md) (comment Brody répond, étape par étape) · [EDUCATION.md](../EDUCATION.md) (Brody organe, Oxygen identité)

Cette couche joue un rôle clé dans **le trajet 1 (cognition)** : voir [TRAJETS.md](../TRAJETS.md), qui explique aussi pourquoi Obsidia fonctionne sans entraînement.

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [apps/obsidia_api/routes/brody.py](../../apps/obsidia_api/routes/brody.py) · route /api/brody/chat : le pipeline complet
- [apps/obsidia_api/brody_cognitive_micro_core.py](../../apps/obsidia_api/brody_cognitive_micro_core.py) · micro-core : 14 signaux, détection adversariale et irréversibilité
- [apps/obsidia_api/brody_balance_engine.py](../../apps/obsidia_api/brody_balance_engine.py) · balance engine : 11 tensions
- [apps/obsidia_api/brody_point_cloud_21d_selector.py](../../apps/obsidia_api/brody_point_cloud_21d_selector.py) · point cloud 21D : couches actives et budget
- [apps/obsidia_api/brody_true_voice_adapter.py](../../apps/obsidia_api/brody_true_voice_adapter.py) · réponse True Voice
- [apps/obsidia_api/brody_pre_reasoning_adapter.py](https://github.com/Eaubin08/obsidia-x108-proofs/blob/integration/harness-runtime-binder-v1/apps/obsidia_api/brody_pre_reasoning_adapter.py) **(H)** · pré-raisonnement : Reverse OS et C265 → C274
- [periphery/brody_memory_readonly/](../../periphery/brody_memory_readonly) · Brody : mémoire en lecture seule
- [periphery/agents/](../../periphery/agents) · agents

*(H) : présent sur la branche `integration/harness-runtime-binder-v1`, pas encore dans `main`.*

D'après le registre de fonctionnalités V3, **821 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `periphery/brody_memory_readonly/` | 495 |
| `apps/obsidia_api/` | 64 |
| `periphery/agents/` | 62 |
| `scripts/` | 29 |
| `sigma/` | 21 |
| `sigma/examples/` | 12 |
| `sigma/tools/` | 12 |
| `periphery/workflow_governance_readonly/` | 10 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 8 |
| `specs/08_MEMORY_BRODY_GRAPHITI/` | 7 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (87)

### Documents de référence — à lire en premier

- [NON_SOVEREIGN_AGENT_CONTRACT_V0](../agents/NON_SOVEREIGN_AGENT_CONTRACT_V0.md) · `docs/agents/NON_SOVEREIGN_AGENT_CONTRACT_V0.md`
  <br>Tout agent ajouté au stack est non souverain. canemitact=false, canauthorize=false, canmutatekernel=false, canwritememory=false.
- [Brody No-Decision Policy V1](../brody/BRODY_NO_DECISION_POLICY_V1.md) · `docs/brody/BRODY_NO_DECISION_POLICY_V1.md`
  <br>Brody répond. Brody ne décide pas. Every Brody response is advisory — it provides context, analysis, suggestions, and information. It never issues a binding decision, never…
- [Brody Response Contract V1](../brody/BRODY_RESPONSE_CONTRACT_V1.md) · `docs/brody/BRODY_RESPONSE_CONTRACT_V1.md`
  <br>decisionauthority: str = "KX108ONLY"   # Brody never decides
- [Brody Module](../brody/README.md) · `docs/brody/README.md`
  <br>- decisionauthority = "KX108ONLY" — Brody never decides
- [OBSIDURE_APPLY_PROTOCOL](../protocols/OBSIDURE_APPLY_PROTOCOL.md) · `docs/protocols/OBSIDURE_APPLY_PROTOCOL.md`
  <br>Standardiser le workflow d'application Obsidure : forge de code, preuves,
- [Brody GPT V1 — Proof Index F42→F48](../release/BRODY_GPT_V1_PROOF_INDEX_F42_F48.md) · `docs/release/BRODY_GPT_V1_PROOF_INDEX_F42_F48.md`
  <br>All SHA256 values are computed from the freeze manifest files in .runtimefreezes/.
- [BRODY_ONLY_STACK_RUNBOOK.md](../runtime_launchers/BRODY_ONLY_STACK_RUNBOOK.md) · `docs/runtime_launchers/BRODY_ONLY_STACK_RUNBOOK.md`
  <br>BRODY ONLY STACK — RUNBOOK
- [AGENT_LAYER_REGISTRY_V0](../agents/AGENT_LAYER_REGISTRY_V0.md) · `docs/agents/AGENT_LAYER_REGISTRY_V0.md` *(référence probable)*
  <br>Registry des agents de couche : Data, Provenance, Memory, EML, Energy, Timeverse, OCS, OC, Permission/Economic, OS3, Gencoin.
- [AGENT_TO_GATE_MAPPING_V0](../agents/AGENT_TO_GATE_MAPPING_V0.md) · `docs/agents/AGENT_TO_GATE_MAPPING_V0.md` *(référence probable)*
  <br>Chaque agent wrap un gate existant. Le registry permet de lister et exécuter les agents non souverains.
- [Brody Language Routing V1](../brody/BRODY_LANGUAGE_ROUTING_V1.md) · `docs/brody/BRODY_LANGUAGE_ROUTING_V1.md` *(référence probable)*
  <br>The Brody Language Router detects the language of incoming queries and routes them to the appropriate response pipeline. It preserves language boundaries and ensures responses…
- [Brody Organism Source Routing — V2C / V2D3](../brody/BRODY_ORGANISM_SOURCE_ROUTING_V2C_V2D3.md) · `docs/brody/BRODY_ORGANISM_SOURCE_ROUTING_V2C_V2D3.md` *(référence probable)*
  <br>Status: VALIDATEDRUNTIMEPASS
- [Brody Runtime Read-Only V1](../brody/BRODY_RUNTIME_READONLY_V1.md) · `docs/brody/BRODY_RUNTIME_READONLY_V1.md` *(référence probable)*
  <br>Brody Runtime is the main query interface. It accepts natural language queries, processes them through the language router, and returns advisory responses. Every response is…
- [CONVERSATION_CANON_CAPTURE_V0](../conversation/CONVERSATION_CANON_CAPTURE_V0.md) · `docs/conversation/CONVERSATION_CANON_CAPTURE_V0.md` *(référence probable)*
  <br>Pépites capturées : sources de vérité x108/demo, hackathons → failure codes, Bank/Trading/GPS comme mondes, X108 souverain, OS3 preuve, Gencoin post-proof, Timeverse, Sigma,…
- [BRODY EXISTING METRICS AND STATES MAP](../freeze/BRODY_EXISTING_METRICS_AND_STATES_MAP.md) · `docs/freeze/BRODY_EXISTING_METRICS_AND_STATES_MAP.md` *(référence probable)*
  <br>Scanning rule: a field is valid only if found in an actual module, pointer, or manifest file.
- [Foundation C — True Response Structure Freeze](../freeze/BRODY_FOUNDATION_C_TRUE_RESPONSE_STRUCTURE_FREEZE.md) · `docs/freeze/BRODY_FOUNDATION_C_TRUE_RESPONSE_STRUCTURE_FREEZE.md` *(référence probable)*
  <br>Status: FOUNDATIONCREADY
- [Brody Full Pointer Map](../freeze/BRODY_FULL_POINTER_MAP.md) · `docs/freeze/BRODY_FULL_POINTER_MAP.md` *(référence probable)*
  <br>To enable: set NEO4JURI, NEO4JPASSWORD, start Neo4j server, or start ObsidiaShell on 8011.
- [Brody Next Fix Plan — V5B](../freeze/BRODY_NEXT_FIX_PLAN.md) · `docs/freeze/BRODY_NEXT_FIX_PLAN.md` *(référence probable)*
  <br>FastAPI app with CORS, mounting routes, and startup verification:
- [Brody GPT V1 — Demo Commands](../release/BRODY_GPT_V1_DEMO_COMMANDS.md) · `docs/release/BRODY_GPT_V1_DEMO_COMMANDS.md` *(référence probable)*
  <br>All commands run from:
- [Brody GPT V1 — Public Release Package](../release/BRODY_GPT_V1_PUBLIC_RELEASE_PACKAGE.md) · `docs/release/BRODY_GPT_V1_PUBLIC_RELEASE_PACKAGE.md` *(référence probable)*
  <br>Status: SEALED · LIVE-CHECKED · CANON-AUDITED · OBSERVATION-TESTED · HARDENED · RELEASE-READINESS-CHECKED
- [AGENT OBSIDURE — Manuel Opérateur V1](../runtime/OBSIDIA_AGENT_OBSIDURE_MANUAL_V1.md) · `docs/runtime/OBSIDIA_AGENT_OBSIDURE_MANUAL_V1.md` *(référence probable)*
  <br>Statut : ACTIVECLIMODE

<details><summary><b>Rapports, audits et preuves d'exécution</b> (55)</summary>

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_AUTOMATION_LAYER_BINDING_REPORT.md](../freeze/BRODY_AUTOMATION_LAYER_BINDING_REPORT.md) — BRODY AUTOMATION LAYER BINDING REPORT
- [BRODY_AUTOMATION_SNAPSHOT_API_REPORT.md](../freeze/BRODY_AUTOMATION_SNAPSHOT_API_REPORT.md) — BRODY AUTOMATION SNAPSHOT API REPORT
- [BRODY_COGNITIVE_MODULE_RESOLUTION_TABLE.json](../freeze/BRODY_COGNITIVE_MODULE_RESOLUTION_TABLE.json)
- [BRODY_EXISTING_AUTOMATION_MODULES_AUDIT.md](../freeze/BRODY_EXISTING_AUTOMATION_MODULES_AUDIT.md) — BRODY EXISTING AUTOMATION MODULES AUDIT
- [BRODY_FINAL_ANSWER_CAPABILITY_PATCH_REPORT.md](../freeze/BRODY_FINAL_ANSWER_CAPABILITY_PATCH_REPORT.md) — BRODY FINAL ANSWER CAPABILITY PATCH REPORT
- [BRODY_FINAL_ANSWER_RESPONSE_MD_SPLIT_REPORT.md](../freeze/BRODY_FINAL_ANSWER_RESPONSE_MD_SPLIT_REPORT.md) — BRODY FINAL ANSWER vs RESPONSE_MD SPLIT REPORT
- [BRODY_FOUNDATION_C_TRUE_RESPONSE_STRUCTURE_FREEZE.json](../freeze/BRODY_FOUNDATION_C_TRUE_RESPONSE_STRUCTURE_FREEZE.json)
- [BRODY_FULL_EXISTING_RUNTIME_SOURCE_MAP.json](../freeze/BRODY_FULL_EXISTING_RUNTIME_SOURCE_MAP.json)
- [BRODY_FULL_LIVE_RUNTIME_CLOSE_REPORT.md](../freeze/BRODY_FULL_LIVE_RUNTIME_CLOSE_REPORT.md) — BRODY FULL LIVE RUNTIME CLOSE REPORT — V5B+
- [BRODY_GLOBAL_BRANCHAGE_AUDIT.json](../freeze/BRODY_GLOBAL_BRANCHAGE_AUDIT.json)
- [BRODY_LIVE_SMOKE_STRICT_REPORT.md](../freeze/BRODY_LIVE_SMOKE_STRICT_REPORT.md) — BRODY LIVE SMOKE STRICT REPORT
- [BRODY_LLM_OBSIDIEN_SOURCE_DOCS_AUDIT.md](../freeze/BRODY_LLM_OBSIDIEN_SOURCE_DOCS_AUDIT.md) — BRODY_LLM_OBSIDIEN_SOURCE_DOCS_AUDIT
- [BRODY_LOCAL_RESPONSE_ENGINE_AS_FINALIZER_REPORT.md](../freeze/BRODY_LOCAL_RESPONSE_ENGINE_AS_FINALIZER_REPORT.md) — Brody Local Response Engine as Finalizer Report — V5B+
- [BRODY_LOW_MATERIAL_TEXT_PREVIEW_PATCH_REPORT.md](../freeze/BRODY_LOW_MATERIAL_TEXT_PREVIEW_PATCH_REPORT.md) — BRODY_LOW_MATERIAL_TEXT_PREVIEW_PATCH_REPORT
- [BRODY_NO_RAW_TUPLE_CLOSE_REPORT.md](../freeze/BRODY_NO_RAW_TUPLE_CLOSE_REPORT.md) — Brody No Raw Tuple Close Report — V5B+
- [BRODY_P0_REAL_BACKEND_IMPLEMENTATION_REPORT.md](../freeze/BRODY_P0_REAL_BACKEND_IMPLEMENTATION_REPORT.md) — Brody P0 Real Backend Implementation Report — V5B
- [BRODY_REAL_BACKEND_AUDIT_REPORT.md](../freeze/BRODY_REAL_BACKEND_AUDIT_REPORT.md) — Brody Real Backend Audit Report — V5B Audit
- [BRODY_REAL_MODULE_DISCOVERY_FOR_API.md](../freeze/BRODY_REAL_MODULE_DISCOVERY_FOR_API.md) — Brody Real Module Discovery for API — V5B
- [BRODY_REAL_RESPONSE_MD_PIPELINE_REPORT.md](../freeze/BRODY_REAL_RESPONSE_MD_PIPELINE_REPORT.md) — Brody Real Response MD Pipeline Report — V5B+
- [BRODY_RUNTIME_MODULE_USAGE_REPORT.md](../freeze/BRODY_RUNTIME_MODULE_USAGE_REPORT.md) — Brody Runtime Module Usage Report — V5B
- [BRODY_SOURCE_OF_TRUTH_REBIND_REPORT.md](../freeze/BRODY_SOURCE_OF_TRUTH_REBIND_REPORT.md) — Brody Source-of-Truth Rebind Report
- [BRODY_THREE_FOUNDATIONS_CURRENT_STATE_AUDIT.md](../freeze/BRODY_THREE_FOUNDATIONS_CURRENT_STATE_AUDIT.md) — BRODY THREE FOUNDATIONS — Current State Audit
- [BRODY_THREE_FOUNDATIONS_VALIDATION_REPORT.md](../freeze/BRODY_THREE_FOUNDATIONS_VALIDATION_REPORT.md) — Brody Three Foundations — Validation Report
- [BRODY_TREE_POLICY_BINDING_REPORT.md](../freeze/BRODY_TREE_POLICY_BINDING_REPORT.md) — BRODY TREE POLICY BINDING REPORT
- [BRODY_UTF8_MOJIBAKE_AUDIT.md](../freeze/BRODY_UTF8_MOJIBAKE_AUDIT.md) — Brody UTF-8 Mojibake Audit Report
- [BRODY_UTF8_MOJIBAKE_FIX_FREEZE_REPORT.md](../freeze/BRODY_UTF8_MOJIBAKE_FIX_FREEZE_REPORT.md) — Brody UTF-8 Mojibake Fix — Freeze Report
- [BRODY_V1_4_12A_FINAL_ANSWER_BINDING_REPORT.md](../freeze/BRODY_V1_4_12A_FINAL_ANSWER_BINDING_REPORT.md) — BRODY V1.4.12A FINAL ANSWER BINDING REPORT
- [BRODY_V1_4_12A_FULL_INTEGRATION_CLOSE_REPORT.md](../freeze/BRODY_V1_4_12A_FULL_INTEGRATION_CLOSE_REPORT.md) — BRODY V1.4.12A FULL INTEGRATION CLOSE REPORT
- [BRODY_V1_4_12A_LIVE_SMOKE_OUTPUT.json](../freeze/BRODY_V1_4_12A_LIVE_SMOKE_OUTPUT.json)
- [BRODY_V1_4_12A_LIVE_STACK_FINAL_SMOKE_REPORT.md](../freeze/BRODY_V1_4_12A_LIVE_STACK_FINAL_SMOKE_REPORT.md) — BRODY V1.4.12A LIVE STACK FINAL SMOKE REPORT
- [BRODY_V1_4_12A_SOURCE_INSPECTION_REPORT.md](../freeze/BRODY_V1_4_12A_SOURCE_INSPECTION_REPORT.md) — Brody V1.4.12A — Source Inspection Report
- [FINAL_BRODY_FULL_CLOSE_REPORT.md](../freeze/FINAL_BRODY_FULL_CLOSE_REPORT.md) — FINAL BRODY FULL CLOSE REPORT
- [V5B_PLUS_BRODY_RESPONSE_MODULE_AUDIT.md](../freeze/V5B_PLUS_BRODY_RESPONSE_MODULE_AUDIT.md) — V5B+ Brody Response Module Audit
- [V5B_PLUS_BRODY_RESPONSE_QUALITY_REPORT.md](../freeze/V5B_PLUS_BRODY_RESPONSE_QUALITY_REPORT.md) — V5B+ Brody Response Quality Report

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE11B_NATIVE_COMPOSITION_REPORT_20260527.md](../runtime/BRODY_PHASE11B_NATIVE_COMPOSITION_REPORT_20260527.md) — BRODY_PHASE11B_NATIVE_COMPOSITION_REPORT_20260527
- [BRODY_PHASE11G_NATIVE_FULL_SURFACE_MANIFEST_20260527.json](../runtime/BRODY_PHASE11G_NATIVE_FULL_SURFACE_MANIFEST_20260527.json)
- [BRODY_PHASE9B5_FINAL_RECONNECT_FREEZE_AUDIT_20260527.md](../runtime/BRODY_PHASE9B5_FINAL_RECONNECT_FREEZE_AUDIT_20260527.md) — BRODY_PHASE9B5_FINAL_RECONNECT_FREEZE_AUDIT_20260527
- [BRODY_RECONNECT_FREEZE_20260527_MANIFEST_SHA256.txt](../runtime/BRODY_RECONNECT_FREEZE_20260527_MANIFEST_SHA256.txt)
- [F11A_BRODY_ROUTE_PAYLOAD_AUDIT.txt](../runtime/F11A_BRODY_ROUTE_PAYLOAD_AUDIT.txt)
- [F11A_CLIENT_BRODY_ENDPOINT_AUDIT.txt](../runtime/F11A_CLIENT_BRODY_ENDPOINT_AUDIT.txt)
- [F11B_DIFF_F4_TO_F5_ROUTES_BRODY.txt](../runtime/F11B_DIFF_F4_TO_F5_ROUTES_BRODY.txt)
- [F11B_DIFF_F5_TO_F6_ROUTES_BRODY.txt](../runtime/F11B_DIFF_F5_TO_F6_ROUTES_BRODY.txt)
- [F17C_8000_BRODY_SOURCE_LABEL_PAYLOAD.json](../runtime/F17C_8000_BRODY_SOURCE_LABEL_PAYLOAD.json)
- [F17C_8012_BRODY_SOURCE_LABEL_PAYLOAD.json](../runtime/F17C_8012_BRODY_SOURCE_LABEL_PAYLOAD.json)
- [F19A2_BRODY_PAYLOAD_8000_20260528_011308.json](../runtime/F19A2_BRODY_PAYLOAD_8000_20260528_011308.json)
- [F19A2_BRODY_PAYLOAD_8012_20260528_011308.json](../runtime/F19A2_BRODY_PAYLOAD_8012_20260528_011308.json)
- [F20A_BRODY_PAYLOAD_8000_20260528_012740.json](../runtime/F20A_BRODY_PAYLOAD_8000_20260528_012740.json)
- [F20A_BRODY_PAYLOAD_8012_20260528_012740.json](../runtime/F20A_BRODY_PAYLOAD_8012_20260528_012740.json)
- [F21A_BRODY_PAYLOAD_8000_20260528_014852.json](../runtime/F21A_BRODY_PAYLOAD_8000_20260528_014852.json)
- [F21A_BRODY_PAYLOAD_8012_20260528_014852.json](../runtime/F21A_BRODY_PAYLOAD_8012_20260528_014852.json)
- [F22C_BRODY_8000_20260528_065516.txt](../runtime/F22C_BRODY_8000_20260528_065516.txt)
- [F22C_BRODY_8012_20260528_065516.txt](../runtime/F22C_BRODY_8012_20260528_065516.txt)
- [OBSIDIA_F42_BRODY_GPT_V1_FINAL_RELEASE_REPORT_20260529_080000.md](../runtime/OBSIDIA_F42_BRODY_GPT_V1_FINAL_RELEASE_REPORT_20260529_080000.md) — OBSIDIA F42 — Brody GPT V1 Final Release Seal Report
- [OBSIDIA_F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_20260529_085000.json](../runtime/OBSIDIA_F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_20260529_085000.json)
- [OBSIDIA_F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_20260529_085000.md](../runtime/OBSIDIA_F43_BRODY_V1_FULL_LIVE_SERVER_PORT_MATRIX_AUDIT_20260529_085000.md) — OBSIDIA F43 — Brody V1 Full Live Server Port Matrix Audit

</details>

<details><summary><b>Rapports de phases passées</b> (8)</summary>

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE11G_NATIVE_FULL_SURFACE_FREEZE_20260527.md](../runtime/BRODY_PHASE11G_NATIVE_FULL_SURFACE_FREEZE_20260527.md) — BRODY_PHASE11G_NATIVE_FULL_SURFACE_FREEZE_20260527
- [BRODY_PHASE12I0_STABLE_STATE_BEFORE_FREESTYLE_FREEZE_20260527.md](../runtime/BRODY_PHASE12I0_STABLE_STATE_BEFORE_FREESTYLE_FREEZE_20260527.md) — BRODY_PHASE12I0_STABLE_STATE_BEFORE_FREESTYLE_FREEZE_20260527
- [BRODY_PHASE12I_E_FREESTYLE_STABLE_FREEZE_20260527.md](../runtime/BRODY_PHASE12I_E_FREESTYLE_STABLE_FREEZE_20260527.md) — BRODY_PHASE12I_E_FREESTYLE_STABLE_FREEZE_20260527
- [BRODY_PHASE12M_LONG_MULTI_SESSION_FREEZE_20260527.md](../runtime/BRODY_PHASE12M_LONG_MULTI_SESSION_FREEZE_20260527.md) — BRODY_PHASE12M_LONG_MULTI_SESSION_FREEZE_20260527
- [BRODY_PHASE8F_ADAPTATION_POSITION_FREEZE_20260527.md](../runtime/BRODY_PHASE8F_ADAPTATION_POSITION_FREEZE_20260527.md) — BRODY_PHASE8F_ADAPTATION_POSITION_FREEZE_20260527
- [BRODY_RECONNECT_FREEZE_20260527.md](../runtime/BRODY_RECONNECT_FREEZE_20260527.md) — BRODY_RECONNECT_FREEZE_20260527
- [OBSIDIA_F32_1_BRODY_FULL_RUNTIME_INTEGRATION_READONLY_PACKET_20260529_023206.md](../runtime/OBSIDIA_F32_1_BRODY_FULL_RUNTIME_INTEGRATION_READONLY_PACKET_20260529_023206.md) — OBSIDIA F32.1 — BRODY FULL RUNTIME INTEGRATION READONLY PACKET
- [OBSIDIA_F33_1_BRODY_RUNTIME_ENTRYPOINT_READONLY_20260529_012937.md](../runtime/OBSIDIA_F33_1_BRODY_RUNTIME_ENTRYPOINT_READONLY_20260529_012937.md) — OBSIDIA F33.1 — BRODY RUNTIME ENTRYPOINT READONLY

</details>

<details><summary><b>Archives</b> (4)</summary>

**`docs/runtime/archive/phase10_12_legacy_untracked_20260527/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE12A_BIS_NATIVE_VOICE_SOURCE_AUDIT_20260527.md](../runtime/archive/phase10_12_legacy_untracked_20260527/BRODY_PHASE12A_BIS_NATIVE_VOICE_SOURCE_AUDIT_20260527.md) — BRODY_PHASE12A_BIS_NATIVE_VOICE_SOURCE_AUDIT_20260527
- [BRODY_PHASE12A_NATIVE_VOICE_SOURCE_AUDIT_20260527.md](../runtime/archive/phase10_12_legacy_untracked_20260527/BRODY_PHASE12A_NATIVE_VOICE_SOURCE_AUDIT_20260527.md) — BRODY_PHASE12A_NATIVE_VOICE_SOURCE_AUDIT_20260527
- [BRODY_PHASE12E0_A_STRUCTURAL_NO_MATERIAL_PROOF_AUDIT_20260527.md](../runtime/archive/phase10_12_legacy_untracked_20260527/BRODY_PHASE12E0_A_STRUCTURAL_NO_MATERIAL_PROOF_AUDIT_20260527.md) — BRODY_PHASE12E0_A_STRUCTURAL_NO_MATERIAL_PROOF_AUDIT_20260527
- [BRODY_PHASE12E4_A_SEMANTIC_DRIFT_SOURCE_AUDIT_20260527.md](../runtime/archive/phase10_12_legacy_untracked_20260527/BRODY_PHASE12E4_A_SEMANTIC_DRIFT_SOURCE_AUDIT_20260527.md) — BRODY_PHASE12E4_A_SEMANTIC_DRIFT_SOURCE_AUDIT_20260527

</details>

## Fichiers liés au code

85 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
