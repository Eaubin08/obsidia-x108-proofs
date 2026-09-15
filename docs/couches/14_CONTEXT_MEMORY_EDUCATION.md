# 14 · Mémoire, contexte, éducation

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

La continuité : sessions, projets, traces, Graphiti et Neo4j, paquets de contexte, promotion gouvernée. Une mémoire n'est jamais automatiquement une vérité canonique.

## Où elle intervient dans le trajet d'une demande

- **Étape 2 · Traduction et compréhension** : OS Trad et Unified Input IR la traduisent dans le langage d'Obsidia, avec son contexte, puis la routent.
- **Étape 4 · Organes spécialisés** : Brody comprend et formule, la mémoire rappelle, les domaines vérifient leur terrain, Obsidure prépare un candidat, Sigma et le Peripheral Mesh mesurent la cohérence, Tree34 et Thermo apportent leurs lectures. Ils proposent, ils ne décident pas.

Voir le trajet complet : [guide général](../README.md).

Cette couche joue un rôle clé dans **le trajet 2 (savoir)** : voir [TRAJETS.md](../TRAJETS.md), qui explique aussi pourquoi Obsidia fonctionne sans entraînement.

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [periphery/memory/](../../periphery/memory) · mémoire
- [.graph-memory/](../../.graph-memory) · mémoire graphe

D'après le registre de fonctionnalités V3, **89 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `runtime_contracts/education_benchmark_dry_run/` | 17 |
| `scripts/` | 8 |
| `_graphiti_readonly_indexes/GRAPHITI_READONLY_INDEX_V2_FUSION_20260512_224854/` | 7 |
| `periphery/memory/` | 6 |
| `.graph-memory/` | 5 |
| `periphery/context/` | 5 |
| `.graph-memory/reports/` | 4 |
| `apps/obsidia_api/` | 4 |
| `periphery/graphiti/` | 4 |
| `.claude/memory/` | 3 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (51)

### Documents de référence — à lire en premier

- [Context Signal-Only Policy V1](../context/CONTEXT_SIGNAL_ONLY_POLICY_V1.md) · `docs/context/CONTEXT_SIGNAL_ONLY_POLICY_V1.md`
  <br>Role: Context is signal. Signal is not decision. Context packets inform — they never decide.
- [Context Packet Module](../context/README.md) · `docs/context/README.md`
  <br>Tests: tests/periphery/testcontext.py + tests/nonsovereignty/testcontext.py
- [Education Module](../education/README.md) · `docs/education/README.md`
  <br>Education scoring for agentic governance. Evaluates education level as context input to X108 — never as decision authority. Education informs but does not grant permission.
- [Graphiti No-Write Policy V1](../graphiti/GRAPHITI_NO_WRITE_POLICY_V1.md) · `docs/graphiti/GRAPHITI_NO_WRITE_POLICY_V1.md`
  <br>Modules: graphitireadonlybridge.py, graphiticontextadapter.py, graphitifreezesnapshotreader.py
- [Graphiti Module](../graphiti/README.md) · `docs/graphiti/README.md`
  <br>Tests: tests/periphery/testgraphiti.py + tests/nonsovereignty/testgraphiti.py
- [FEEDBACK_MEMORY_CANDIDATE_POLICY_V0](../memory/FEEDBACK_MEMORY_CANDIDATE_POLICY_V0.md) · `docs/memory/FEEDBACK_MEMORY_CANDIDATE_POLICY_V0.md`
  <br>Feedback transformé en candidat mémoire. Aucune écriture mémoire réelle.
- [Memory Module](../memory/README.md) · `docs/memory/README.md`
  <br>- memorywriteallowed = False — memory candidates are capture-only
- [Context Packet Builder V2](../context/CONTEXT_PACKET_BUILDER_V2.md) · `docs/context/CONTEXT_PACKET_BUILDER_V2.md` *(référence probable)*
  <br>Role: Builds structured context packets from query results, graph data, and memory candidates.
- [Context Packet → X108 Read-Only Ingress V1](../context/CONTEXT_PACKET_TO_X108_READONLY_INGRESS_V1.md) · `docs/context/CONTEXT_PACKET_TO_X108_READONLY_INGRESS_V1.md` *(référence probable)*
  <br>The X108 Context Boundary is the read-only ingress point where context packets enter the X108 kernel perimeter. It validates packets, enforces the signal-only invariant, and…
- [Foundation A — Project Memory Freeze](../freeze/BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE.md) · `docs/freeze/BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE.md` *(référence probable)*
  <br>Status: FOUNDATIONAPARTIAL
- [Foundation B — Session Memory / Follow-up Freeze](../freeze/BRODY_FOUNDATION_B_SESSION_MEMORY_FOLLOWUP_FREEZE.md) · `docs/freeze/BRODY_FOUNDATION_B_SESSION_MEMORY_FOLLOWUP_FREEZE.md` *(référence probable)*
  <br>Status: FOUNDATIONBREADY
- [Graphiti Context Adapter V1](../graphiti/GRAPHITI_CONTEXT_ADAPTER_V1.md) · `docs/graphiti/GRAPHITI_CONTEXT_ADAPTER_V1.md` *(référence probable)*
  <br>The Graphiti Context Adapter transforms raw Graphiti graph results into structured context packets that can be consumed by Brody, memory candidates, and the X108 ingress. It…
- [Graphiti Read-Only Bridge V1](../graphiti/GRAPHITI_READONLY_BRIDGE_V1.md) · `docs/graphiti/GRAPHITI_READONLY_BRIDGE_V1.md` *(référence probable)*
  <br>The Graphiti Read-Only Bridge provides a query interface to the Graphiti knowledge graph for context enrichment. It reads graph relationships, entity data, and episode history…
- [Memory Candidate Ledger V1](../memory/MEMORY_CANDIDATE_LEDGER_V1.md) · `docs/memory/MEMORY_CANDIDATE_LEDGER_V1.md` *(référence probable)*
  <br>The Memory Candidate Ledger stores memory candidates in an append-only structure. Candidates are captured with content hash, source type, and status — but the ledger never…
- [Memory Promotion — Manual Only V1](../memory/MEMORY_PROMOTION_MANUAL_ONLY_V1.md) · `docs/memory/MEMORY_PROMOTION_MANUAL_ONLY_V1.md` *(référence probable)*
  <br>Role: Memory promotion requires human review. Automatic promotion is absolutely blocked.
- [Memory Security Boundary V1](../memory/MEMORY_SECURITY_BOUNDARY_V1.md) · `docs/memory/MEMORY_SECURITY_BOUNDARY_V1.md` *(référence probable)*
  <br>Role: Security boundary protecting memory from unauthorized writes and automatic promotion.
- [Memory Source Registry V1](../memory/MEMORY_SOURCE_REGISTRY_V1.md) · `docs/memory/MEMORY_SOURCE_REGISTRY_V1.md` *(référence probable)*
  <br>The Memory Source Registry defines the valid types of memory sources and validates that each memory candidate comes from an authorized source. It classifies sources but never…

<details><summary><b>Rapports, audits et preuves d'exécution</b> (30)</summary>

**`docs/architecture/`** · *dossier lu par du code : ne pas déplacer*

- [F70_1_GRAPHITI_AUDIT_UTF8SIG_REPAIR.md](../architecture/F70_1_GRAPHITI_AUDIT_UTF8SIG_REPAIR.md) — F70.1 ? Graphiti Audit UTF-8-SIG Repair
- [F70_GRAPHITI_BRODY_MEMORY_DEEP_AUDIT.md](../architecture/F70_GRAPHITI_BRODY_MEMORY_DEEP_AUDIT.md) — F70 ? Graphiti / Brody Memory Deep Audit

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P66_SRL_READONLY_MEMORY_LAYER.json](../core_import/P66_SRL_READONLY_MEMORY_LAYER.json)

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE.json](../freeze/BRODY_FOUNDATION_A_PROJECT_MEMORY_FREEZE.json)
- [BRODY_FOUNDATION_B_SESSION_MEMORY_FOLLOWUP_FREEZE.json](../freeze/BRODY_FOUNDATION_B_SESSION_MEMORY_FOLLOWUP_FREEZE.json)
- [BRODY_GRAPHITI_LIVE_READONLY_REPORT.md](../freeze/BRODY_GRAPHITI_LIVE_READONLY_REPORT.md) — Brody Graphiti Live Bootstrap Report
- [BRODY_GRAPHITI_LIVE_RUNTIME_CLOSE_REPORT.md](../freeze/BRODY_GRAPHITI_LIVE_RUNTIME_CLOSE_REPORT.md) — BRODY GRAPHITI LIVE RUNTIME CLOSE REPORT
- [BRODY_REAL_MEMORY_RESPONSE_CHAIN_LIVE_RETEST_AFTER_PATCH.json](../freeze/BRODY_REAL_MEMORY_RESPONSE_CHAIN_LIVE_RETEST_AFTER_PATCH.json)
- [BRODY_REAL_MEMORY_RESPONSE_CHAIN_LIVE_RETEST_AFTER_PATCH.md](../freeze/BRODY_REAL_MEMORY_RESPONSE_CHAIN_LIVE_RETEST_AFTER_PATCH.md) — Brody Real Memory→Response Chain — Live Retest After Patch

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE12B_MEMORY_MATERIAL_BINDING_REPORT_20260527.md](../runtime/BRODY_PHASE12B_MEMORY_MATERIAL_BINDING_REPORT_20260527.md) — BRODY_PHASE12B_MEMORY_MATERIAL_BINDING_REPORT_20260527
- [BRODY_PHASE12D_MEMORY_MATERIAL_BINDING_MANIFEST_20260527.json](../runtime/BRODY_PHASE12D_MEMORY_MATERIAL_BINDING_MANIFEST_20260527.json)
- [F17A_8000_BRODY_GRAPHITI_PAYLOAD.json](../runtime/F17A_8000_BRODY_GRAPHITI_PAYLOAD.json)
- [F17A_8011_GRAPHITI_V20_PROBE.json](../runtime/F17A_8011_GRAPHITI_V20_PROBE.json)
- [F17B_8000_BRODY_GRAPHITI_RECONNECT_PAYLOAD.json](../runtime/F17B_8000_BRODY_GRAPHITI_RECONNECT_PAYLOAD.json)
- [F17B_TERMINAL_GRAPHITI_V20_RECONNECT.txt](../runtime/F17B_TERMINAL_GRAPHITI_V20_RECONNECT.txt)
- [F22C_8000_GRAPHITI_STATUS_20260528_065516.json](../runtime/F22C_8000_GRAPHITI_STATUS_20260528_065516.json)
- [F22C_GRAPHITI_8011_STATUS_20260528_065516.json](../runtime/F22C_GRAPHITI_8011_STATUS_20260528_065516.json)
- [F22C_GRAPHITI_WORKBENCH_8011_20260528_065516.json](../runtime/F22C_GRAPHITI_WORKBENCH_8011_20260528_065516.json)
- [F22C_NEO4J_20260528_065516.txt](../runtime/F22C_NEO4J_20260528_065516.txt)
- [F22C_NEO4J_CYPHER_20260528_065516.txt](../runtime/F22C_NEO4J_CYPHER_20260528_065516.txt)
- [OBSIDIA_F17A_GRAPHITI_8000_8012_REAL_PARITY_AUDIT_20260528_040000.md](../runtime/OBSIDIA_F17A_GRAPHITI_8000_8012_REAL_PARITY_AUDIT_20260528_040000.md) — OBSIDIA F17A — GRAPHITI 8000 / 8011 / 8012 REAL PARITY AUDIT
- [OBSIDIA_F17B_GRAPHITI_V20_FROZEN_HTTP_RECONNECT_REPORT_20260528_022023.md](../runtime/OBSIDIA_F17B_GRAPHITI_V20_FROZEN_HTTP_RECONNECT_REPORT_20260528_022023.md) — OBSIDIA F17B — GRAPHITI V20 FROZEN HTTP RECONNECT REPORT
- [OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_20260528_083733.json](../runtime/OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_20260528_083733.json)
- [OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_20260528_083733.md](../runtime/OBSIDIA_F23A1_MEMORY_REFLEX_ORCHESTRATOR_SOURCE_AUDIT_20260528_083733.md) — OBSIDIA F23A1 — MEMORY REFLEX / ORCHESTRATOR SOURCE AUDIT
- [OBSIDIA_F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_20260529_003311.json](../runtime/OBSIDIA_F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_20260529_003311.json)
- [OBSIDIA_F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_20260529_003046.json](../runtime/OBSIDIA_F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_20260529_003046.json)
- [OBSIDIA_F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_20260529_003046.md](../runtime/OBSIDIA_F29_0_MEMORY_GRAPHITI_RECONCILIATION_AUDIT_20260529_003046.md) — OBSIDIA F29.0 — MEMORY / GRAPHITI RECONCILIATION AUDIT
- [OBSIDIA_F29_2_NEO4J_MANUAL_GUARD_REAUDIT_20260529_005542.json](../runtime/OBSIDIA_F29_2_NEO4J_MANUAL_GUARD_REAUDIT_20260529_005542.json)
- [OBSIDIA_F6_MEMORY_PROMOTION_GUARD_FREEZE_REPORT_20260527_221117.md](../runtime/OBSIDIA_F6_MEMORY_PROMOTION_GUARD_FREEZE_REPORT_20260527_221117.md) — OBSIDIA F6 — MEMORY PROMOTION GUARD FREEZE REPORT

**`docs/runtime/phase12f_a_api_samples/`** · *dossier lu par du code : ne pas déplacer*

- [memory_enriched.json](../runtime/phase12f_a_api_samples/memory_enriched.json)

</details>

<details><summary><b>Rapports de phases passées</b> (3)</summary>

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P66_SRL_READONLY_MEMORY_LAYER.md](../core_import/P66_SRL_READONLY_MEMORY_LAYER.md) — P66 — SRL Readonly Memory Layer

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE12D_MEMORY_MATERIAL_BINDING_FREEZE_20260527.md](../runtime/BRODY_PHASE12D_MEMORY_MATERIAL_BINDING_FREEZE_20260527.md) — BRODY_PHASE12D_MEMORY_MATERIAL_BINDING_FREEZE_20260527
- [OBSIDIA_F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_20260529_003311.md](../runtime/OBSIDIA_F29_0B_MEMORY_GRAPHITI_DANGER_CLASSIFICATION_20260529_003311.md) — OBSIDIA F29.0B — MEMORY / GRAPHITI DANGER CLASSIFICATION

</details>

<details><summary><b>Archives</b> (1)</summary>

**`docs/runtime/archive/phase10_12_legacy_untracked_20260527/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE12A_TER_MEMORY_MATERIAL_BINDING_AUDIT_20260527.md](../runtime/archive/phase10_12_legacy_untracked_20260527/BRODY_PHASE12A_TER_MEMORY_MATERIAL_BINDING_AUDIT_20260527.md) — BRODY_PHASE12A_TER_MEMORY_MATERIAL_BINDING_AUDIT_20260527

</details>

## Fichiers liés au code

51 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
