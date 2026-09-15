# 19 · Interface : Workbench et Terminal

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Les surfaces opérateur : Workbench, Terminal, cartes de décision, vues d'événements. Elles lisent et soumettent des demandes explicites.

## Où elle intervient dans le trajet d'une demande

- **Étape 8 · Action contrôlée et trace** : Si c'est autorisé, l'action part par une frontière bornée. Elle est mesurée, scellée et rejouable, et reste visible dans le Workbench et le Terminal.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [apps/obsidia-workbench/](../../apps/obsidia-workbench) · Workbench (interface opérateur)

D'après le registre de fonctionnalités V3, **69 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `apps/obsidia-workbench/` | 59 |
| `periphery/interface/` | 5 |
| `periphery/workflow_governance_readonly/` | 3 |
| `scripts/` | 2 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (89)

### Documents de référence — à lire en premier

- [Brody GPT V1 — Final README](../demo/OBSIDIA_BRODY_GPT_V1_FINAL_README.md) · `docs/demo/OBSIDIA_BRODY_GPT_V1_FINAL_README.md`
  <br>Brody GPT V1 is a read-only advisory runtime component. It consults 7 runtime surfaces of the Obsidia X-108 governance system, aggregates their state, and produces context-only…
- [Obsidia Bus Layer — Public Demo Index](../demo/OBSIDIA_F59_BUS_LAYER_PUBLIC_DEMO_INDEX.md) · `docs/demo/OBSIDIA_F59_BUS_LAYER_PUBLIC_DEMO_INDEX.md`
  <br>The Obsidia bus layer is a read-only epistemic surface. It answers:
- [Obsidia X-108 — Operator Demo Guide (F39)](../demo/OBSIDIA_OPERATOR_DEMO_README_F39.md) · `docs/demo/OBSIDIA_OPERATOR_DEMO_README_F39.md`
  <br>cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofsREMOTEA5F21C6B"
- [Interface Ready Contracts V1](../interface/INTERFACE_READY_CONTRACTS_V1.md) · `docs/interface/INTERFACE_READY_CONTRACTS_V1.md`
  <br>- Represents the current state of the interface
- [Interface Module](../interface/README.md) · `docs/interface/README.md`
  <br>- readonly = True — interface is read-only
- [OBSIDIA_TERMINAL_PLAN_PANEL_V1 — spécification](../specs/OBSIDIA_TERMINAL_PLAN_PANEL_V1.md) · `docs/specs/OBSIDIA_TERMINAL_PLAN_PANEL_V1.md`
  <br>Couche : OBSIDIAACTIVEPLAN — panneau de pilotage lisible du terminal
- [OBSIDIA_TERMINAL_POST_ROUTER_FREEZE_V1](../specs/OBSIDIA_TERMINAL_POST_ROUTER_FREEZE_V1.md) · `docs/specs/OBSIDIA_TERMINAL_POST_ROUTER_FREEZE_V1.md`
  <br>- Nom : OBSIDIATERMINALPOSTROUTERFREEZEV1
- [OBSIDIA TERMINAL RECEIPT V0 — spécification](../specs/OBSIDIA_TERMINAL_RECEIPT_V0.md) · `docs/specs/OBSIDIA_TERMINAL_RECEIPT_V0.md`
  <br>Statut : format tracké, log vivant NON tracké.
- [OBSIDIA_TERMINAL_RESPONSE_ROUTER_V1 — spécification](../specs/OBSIDIA_TERMINAL_RESPONSE_ROUTER_V1.md) · `docs/specs/OBSIDIA_TERMINAL_RESPONSE_ROUTER_V1.md`
  <br>Couche : OBSIDIAANSWERROUTER (bannière de sortie : OBSIDIARESPONSE).
- [OBSIDIA_TERMINAL_STACK_FREEZE_V1](../specs/OBSIDIA_TERMINAL_STACK_FREEZE_V1.md) · `docs/specs/OBSIDIA_TERMINAL_STACK_FREEZE_V1.md`
  <br>- Nom : OBSIDIATERMINALSTACKFREEZEV1
- [OBSIDIA_TERMINAL_UX_COMPACT_V2 — spécification](../specs/OBSIDIA_TERMINAL_UX_COMPACT_V2.md) · `docs/specs/OBSIDIA_TERMINAL_UX_COMPACT_V2.md`
  <br>Scope : OBSIDIATERMINALUXCOMPACTV2. Première évolution V2 après le
- [Brody GPT V1 — Release Notes](../demo/OBSIDIA_BRODY_GPT_V1_RELEASE_NOTES.md) · `docs/demo/OBSIDIA_BRODY_GPT_V1_RELEASE_NOTES.md` *(référence probable)*
  <br>Sealed at: F42 · HEAD b67b2c3 · Tag: BRODYF41PUBLICINVESTORDEMONARRATIVEPACKPALIER20260529
- [BRIGHT_DATA_FAILURES_V1](../hackathons/BRIGHT_DATA_FAILURES_V1.md) · `docs/hackathons/BRIGHT_DATA_FAILURES_V1.md` *(référence probable)*
  <br>Rate limits, bot detection, JS render, geo-blocks, stale data, clean JSON, self-healing fetch.
- [HACKATHON_FAILURE_TAXONOMY_V1](../hackathons/HACKATHON_FAILURE_TAXONOMY_V1.md) · `docs/hackathons/HACKATHON_FAILURE_TAXONOMY_V1.md` *(référence probable)*
  <br>Bright Data : web réel/data fraîche. TechEx : gouvernance/audit/permissions. Milan : agents autonomes/paiements/trading/async/voix/production.
- [HACKATHON_TO_OBSIDIA_MAPPING_V1](../hackathons/HACKATHON_TO_OBSIDIA_MAPPING_V1.md) · `docs/hackathons/HACKATHON_TO_OBSIDIA_MAPPING_V1.md` *(référence probable)*
  <br>Chaque problème devient failurecode → gate → signal Sigma → GuardX108 → OS3 → condition Gencoin.
- [MILAN_AI_WEEK_FAILURES_V1](../hackathons/MILAN_AI_WEEK_FAILURES_V1.md) · `docs/hackathons/MILAN_AI_WEEK_FAILURES_V1.md` *(référence probable)*
  <br>Autonomous action, payments, trading, async, multimodal/voice, production readiness.
- [TECHEX_FAILURES_V1](../hackathons/TECHEX_FAILURES_V1.md) · `docs/hackathons/TECHEX_FAILURES_V1.md` *(référence probable)*
  <br>Guardrails, safety, monitoring, observability, hallucination, drift, misuse, permissions, audit, explainability, redteam.

<details><summary><b>Rapports, audits et preuves d'exécution</b> (51)</summary>

**`docs/demo/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_F43_LIVE_SERVER_RUNBOOK.md](../demo/OBSIDIA_F43_LIVE_SERVER_RUNBOOK.md) — Brody GPT V1 — Live Server Runbook (F43)
- [OBSIDIA_F47_HARDENING_RESULTS.md](../demo/OBSIDIA_F47_HARDENING_RESULTS.md) — F47 — Hardening Results
- [OBSIDIA_F50_LIVE_DEMO_READINESS_REPORT.md](../demo/OBSIDIA_F50_LIVE_DEMO_READINESS_REPORT.md) — F50 — Live Demo Readiness Report
- [OBSIDIA_F54_BUS_BRIDGE_LIVE_ROUTE_READINESS.md](../demo/OBSIDIA_F54_BUS_BRIDGE_LIVE_ROUTE_READINESS.md) — F54 — Bus/Bridge Live Route Readiness
- [OBSIDIA_F56_BUS_SIGNAL_LIVE_ROUTE_READINESS.md](../demo/OBSIDIA_F56_BUS_SIGNAL_LIVE_ROUTE_READINESS.md) — F56 — Bus/Signal Live Route Readiness
- [OBSIDIA_F57_BUS_LAYER_READINESS_REPORT.md](../demo/OBSIDIA_F57_BUS_LAYER_READINESS_REPORT.md) — F57 — Bus Layer Readiness Report

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_WORKBENCH_AUTOMATION_PANEL_REPORT.md](../freeze/BRODY_WORKBENCH_AUTOMATION_PANEL_REPORT.md) — BRODY WORKBENCH AUTOMATION PANEL REPORT
- [BRODY_WORKBENCH_BINDING_GAP_REPORT.md](../freeze/BRODY_WORKBENCH_BINDING_GAP_REPORT.md) — Brody Workbench Binding Gap Report
- [BRODY_WORKBENCH_V1_4_12A_RENDER_REPORT.md](../freeze/BRODY_WORKBENCH_V1_4_12A_RENDER_REPORT.md) — BRODY WORKBENCH V1.4.12A RENDER REPORT

**`docs/real_engine/`** · *dossier lu par du code : ne pas déplacer*

- [P29_WORKBENCH_SOURCE_RUNTIME_SURFACE_REPORT.md](../real_engine/P29_WORKBENCH_SOURCE_RUNTIME_SURFACE_REPORT.md) — P29 — Workbench / API Source Runtime Surface Report
- [P38_WORKBENCH_FULL_OS_MAP_REPORT.md](../real_engine/P38_WORKBENCH_FULL_OS_MAP_REPORT.md) — P38 — Workbench Full OS Map — Rapport
- [P46_WORKBENCH_VIEWS_COVERAGE_REPORT.md](../real_engine/P46_WORKBENCH_VIEWS_COVERAGE_REPORT.md) — P46 — Workbench Views Coverage Report

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [F10A_TERMINAL_COMMAND_PACKET_AUDIT.txt](../runtime/F10A_TERMINAL_COMMAND_PACKET_AUDIT.txt)
- [F10B_UI_COMMAND_PACKET_DISPLAY_AUDIT.txt](../runtime/F10B_UI_COMMAND_PACKET_DISPLAY_AUDIT.txt)
- [F12A_TERMINAL_ONCE_ARCHITECTURE_20260527_230633.txt](../runtime/F12A_TERMINAL_ONCE_ARCHITECTURE_20260527_230633.txt)
- [F12A_TERMINAL_ONCE_COMMAND_PACKET_20260527_230633.txt](../runtime/F12A_TERMINAL_ONCE_COMMAND_PACKET_20260527_230633.txt)
- [F12A_TERMINAL_ONCE_DEBUG_FASTAPI_20260527_230633.txt](../runtime/F12A_TERMINAL_ONCE_DEBUG_FASTAPI_20260527_230633.txt)
- [F15C_TERMINAL_LIVE_ONLY_8000.txt](../runtime/F15C_TERMINAL_LIVE_ONLY_8000.txt)
- [F15_RIGHTPANEL_LIVE_PAYLOAD_8000.json](../runtime/F15_RIGHTPANEL_LIVE_PAYLOAD_8000.json)
- [F17C_TERMINAL_SOURCE_LABEL_CHECK_8000.txt](../runtime/F17C_TERMINAL_SOURCE_LABEL_CHECK_8000.txt)
- [F17C_TERMINAL_SOURCE_LABEL_CHECK_8012.txt](../runtime/F17C_TERMINAL_SOURCE_LABEL_CHECK_8012.txt)
- [F22C_UI_5173_20260528_065516.json](../runtime/F22C_UI_5173_20260528_065516.json)
- [F8A_RIGHTPANEL_OPERATOR_VIEW_AUDIT.txt](../runtime/F8A_RIGHTPANEL_OPERATOR_VIEW_AUDIT.txt)
- [F9A_BRODY_TERMINAL_CHAT_AUDIT.txt](../runtime/F9A_BRODY_TERMINAL_CHAT_AUDIT.txt)
- [OBSIDIA_F12A_TERMINAL_CHAT_VISIBLE_SMOKE_REPORT_20260527_230633.md](../runtime/OBSIDIA_F12A_TERMINAL_CHAT_VISIBLE_SMOKE_REPORT_20260527_230633.md) — OBSIDIA F12A — TERMINAL CHAT VISIBLE SMOKE REPORT
- [OBSIDIA_F13A_LIVE_UI_CHAT_SMOKE_BASELINE_REPORT_20260527_233032.md](../runtime/OBSIDIA_F13A_LIVE_UI_CHAT_SMOKE_BASELINE_REPORT_20260527_233032.md) — OBSIDIA F13A — LIVE UI CHAT SMOKE BASELINE
- [OBSIDIA_F13_LIVE_UI_CHAT_SMOKE_FREEZE_REPORT_20260527_233241.md](../runtime/OBSIDIA_F13_LIVE_UI_CHAT_SMOKE_FREEZE_REPORT_20260527_233241.md) — OBSIDIA F13 — LIVE UI CHAT SMOKE FREEZE REPORT
- [OBSIDIA_F14_COMMAND_COPY_BUTTON_UI_FREEZE_REPORT_20260527_234834.md](../runtime/OBSIDIA_F14_COMMAND_COPY_BUTTON_UI_FREEZE_REPORT_20260527_234834.md) — OBSIDIA F14 — COMMAND COPY BUTTON UI FREEZE REPORT
- [OBSIDIA_F15B_RIGHTPANEL_AND_TERMINAL_LIVE_ONLY_REPAIR_REPORT_20260528_000000.md](../runtime/OBSIDIA_F15B_RIGHTPANEL_AND_TERMINAL_LIVE_ONLY_REPAIR_REPORT_20260528_000000.md) — OBSIDIA F15B — RIGHTPANEL + TERMINAL LIVE-ONLY REPAIR FREEZE REPORT
- [OBSIDIA_F15_RIGHTPANEL_REAL_PAYLOAD_ALIGNMENT_AUDIT_20260527_235913.md](../runtime/OBSIDIA_F15_RIGHTPANEL_REAL_PAYLOAD_ALIGNMENT_AUDIT_20260527_235913.md) — OBSIDIA F15 — RIGHTPANEL REAL PAYLOAD ALIGNMENT AUDIT
- [OBSIDIA_F22E_C3_UI_SURFACE_CHECK_20260528_073417.json](../runtime/OBSIDIA_F22E_C3_UI_SURFACE_CHECK_20260528_073417.json)
- [OBSIDIA_F22E_C3_UI_SURFACE_CHECK_20260528_073624.json](../runtime/OBSIDIA_F22E_C3_UI_SURFACE_CHECK_20260528_073624.json)
- [OBSIDIA_F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_20260529_090000.json](../runtime/OBSIDIA_F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_20260529_090000.json)
- [OBSIDIA_F8_RIGHTPANEL_TRANSVERSE_STACK_FREEZE_REPORT_20260527_222924.md](../runtime/OBSIDIA_F8_RIGHTPANEL_TRANSVERSE_STACK_FREEZE_REPORT_20260527_222924.md) — OBSIDIA F8 — RIGHTPANEL TRANSVERSE STACK FREEZE REPORT
- [OBSIDIA_F9_BRODY_TERMINAL_CHAT_VIEW_FREEZE_REPORT_20260527_223335.md](../runtime/OBSIDIA_F9_BRODY_TERMINAL_CHAT_VIEW_FREEZE_REPORT_20260527_223335.md) — OBSIDIA F9 — BRODY TERMINAL CHAT VIEW FREEZE REPORT

**`docs/runtime/f12b_quality_parity_20260527_231054/`** · *dossier lu par du code : ne pas déplacer*

- [p1_port_8000_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p1_port_8000_terminal.txt)
- [p1_port_8012_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p1_port_8012_terminal.txt)
- [p2_port_8000_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p2_port_8000_terminal.txt)
- [p2_port_8012_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p2_port_8012_terminal.txt)
- [p3_port_8000_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p3_port_8000_terminal.txt)
- [p3_port_8012_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p3_port_8012_terminal.txt)
- [p4_port_8000_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p4_port_8000_terminal.txt)
- [p4_port_8012_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p4_port_8012_terminal.txt)
- [p5_port_8000_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p5_port_8000_terminal.txt)
- [p5_port_8012_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p5_port_8012_terminal.txt)
- [p6_port_8000_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p6_port_8000_terminal.txt)
- [p6_port_8012_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p6_port_8012_terminal.txt)
- [p7_port_8000_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p7_port_8000_terminal.txt)
- [p7_port_8012_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p7_port_8012_terminal.txt)
- [p8_port_8000_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p8_port_8000_terminal.txt)
- [p8_port_8012_terminal.txt](../runtime/f12b_quality_parity_20260527_231054/p8_port_8012_terminal.txt)

</details>

<details><summary><b>Rapports de phases passées</b> (20)</summary>

**`docs/demo/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_F40_OPERATOR_RELEASE_CANDIDATE_CHECKLIST.md](../demo/OBSIDIA_F40_OPERATOR_RELEASE_CANDIDATE_CHECKLIST.md) — Obsidia X-108 — Release Candidate Checklist (F40 RC1)
- [OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md](../demo/OBSIDIA_F41_DEMO_SCRIPT_3_5_MIN.md) — Obsidia X-108 — Oral Demo Script (3–5 minutes)
- [OBSIDIA_F41_INVESTOR_JURY_FAQ.md](../demo/OBSIDIA_F41_INVESTOR_JURY_FAQ.md) — FAQ Investisseur / Jury — Obsidia X-108 (F41 RC1)
- [OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md](../demo/OBSIDIA_F41_PUBLIC_INVESTOR_PITCH.md) — Obsidia X-108 — Public Investor Pitch (F41 RC1)
- [OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md](../demo/OBSIDIA_F41_WHAT_IT_PROVES_AND_DOES_NOT_PROVE.md) — Ce que cette démonstration prouve — et ce qu'elle ne prouve pas
- [OBSIDIA_F45_CANONICAL_OBSERVATION_FINDINGS.md](../demo/OBSIDIA_F45_CANONICAL_OBSERVATION_FINDINGS.md) — Brody GPT V1 — F45 Canonical Observation Findings
- [OBSIDIA_F46_F47_PATCH_SEQUENCE.md](../demo/OBSIDIA_F46_F47_PATCH_SEQUENCE.md) — Brody GPT V1 — F47 Patch Sequence
- [OBSIDIA_F46_PUBLIC_READINESS_GATE.md](../demo/OBSIDIA_F46_PUBLIC_READINESS_GATE.md) — Brody GPT V1 — Public Readiness Gate
- [OBSIDIA_F48_RELEASE_READINESS_DECISION.md](../demo/OBSIDIA_F48_RELEASE_READINESS_DECISION.md) — F48 — Release Readiness Decision
- [OBSIDIA_F51_BUS_STATS_DEBT_DECISION.md](../demo/OBSIDIA_F51_BUS_STATS_DEBT_DECISION.md) — F51 — Bus Stats Debt Decision
- [OBSIDIA_F52_BUS_BRIDGE_INTENT.md](../demo/OBSIDIA_F52_BUS_BRIDGE_INTENT.md) — F52 — Bus/Bridge : Intention Architecturale
- [OBSIDIA_F53_BUS_BRIDGE_F54_IMPLEMENTATION_DECISION.md](../demo/OBSIDIA_F53_BUS_BRIDGE_F54_IMPLEMENTATION_DECISION.md) — F53 — Bus/Bridge : Décision d'implémentation F54
- [OBSIDIA_F55_F56_IMPLEMENTATION_DECISION.md](../demo/OBSIDIA_F55_F56_IMPLEMENTATION_DECISION.md) — F55 — Bus/Signal : Décision d'implémentation F56
- [OBSIDIA_F58_BUS_LAYER_METADATA_READINESS.md](../demo/OBSIDIA_F58_BUS_LAYER_METADATA_READINESS.md) — F58 — Bus Layer Metadata Readiness

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE11D_TERMINAL_NATIVE_DISPLAY_20260527.md](../runtime/BRODY_PHASE11D_TERMINAL_NATIVE_DISPLAY_20260527.md) — BRODY_PHASE11D_TERMINAL_NATIVE_DISPLAY_20260527
- [BRODY_PHASE11E_RIGHTPANEL_NATIVE_DISPLAY_20260527.md](../runtime/BRODY_PHASE11E_RIGHTPANEL_NATIVE_DISPLAY_20260527.md) — BRODY_PHASE11E_RIGHTPANEL_NATIVE_DISPLAY_20260527
- [BRODY_PHASE12E2_T_TERMINAL_UTF8_TRUE_VOICE_PATCH_20260527.md](../runtime/BRODY_PHASE12E2_T_TERMINAL_UTF8_TRUE_VOICE_PATCH_20260527.md) — BRODY_PHASE12E2_T_TERMINAL_UTF8_TRUE_VOICE_PATCH_20260527
- [BRODY_PHASE12J_G_ADAPTIVE_POLICY_TERMINAL_API_FREEZE_20260527.md](../runtime/BRODY_PHASE12J_G_ADAPTIVE_POLICY_TERMINAL_API_FREEZE_20260527.md) — BRODY_PHASE12J_G_ADAPTIVE_POLICY_TERMINAL_API_FREEZE_20260527
- [OBSIDIA_F36_1_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE_20260529_033111.md](../runtime/OBSIDIA_F36_1_USER_SCENARIO_BRODY_WORKBENCH_CONTROLLED_RESPONSE_20260529_033111.md) — OBSIDIA F36 — User Scenario Brody Workbench Controlled Response
- [OBSIDIA_F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_20260529_090000.md](../runtime/OBSIDIA_F45_CANONICAL_OBSERVATION_TERMINAL_TEST_BATTERY_20260529_090000.md) — OBSIDIA F45 — Canonical Observation Terminal Test Battery

</details>

<details><summary><b>Archives</b> (1)</summary>

**`docs/runtime/archive/phase10_12_legacy_untracked_20260527/scripts/`** · *dossier lu par du code : ne pas déplacer*

- [smoke_phase10_real_user_terminal_compare.ps1](../runtime/archive/phase10_12_legacy_untracked_20260527/scripts/smoke_phase10_real_user_terminal_compare.ps1)

</details>

## Fichiers liés au code

89 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
