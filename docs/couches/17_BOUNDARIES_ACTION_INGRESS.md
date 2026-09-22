# 17 · Frontières d'action et ingress

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Les portes visibles entre les propositions et le noyau, puis entre le noyau et le monde : ingress, actions bloquées, gardes de non-décision, world calls.

## Où elle intervient dans le trajet d'une demande

- **Étape 6 · Frontière** : Les gardes d'ingress vérifient que seul un envelope valide atteint le noyau.
- **Étape 8 · Action contrôlée et trace** : Si c'est autorisé, l'action part par une frontière bornée. Elle est mesurée, scellée et rejouable, et reste visible dans le Workbench et le Terminal.

Voir le trajet complet : [guide général](../README.md).

Cette couche joue un rôle clé dans **le trajet 3 (action)** : voir [TRAJETS.md](../TRAJETS.md), qui explique aussi pourquoi Obsidia fonctionne sans entraînement.

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [periphery/x108_ingress/](../../periphery/x108_ingress) · gardes d'ingress vers X-108
- [tests/non_sovereignty/](../../tests/non_sovereignty) · tests de non-souveraineté
- [scripts/gates/](../../scripts/gates) · gates, dont le check de frontière du noyau

D'après le registre de fonctionnalités V3, **16 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `periphery/x108_ingress/` | 3 |
| `_runtime_wiring_preflight/` | 2 |
| `periphery/` | 2 |
| `apps/obsidia-workbench/` | 1 |
| `apps/obsidia_api/` | 1 |
| `audit/` | 1 |
| `periphery/engine_gates/` | 1 |
| `periphery/schemas/` | 1 |
| `periphery/workflow_governance_readonly/` | 1 |
| `periphery/world_calls/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (24)

### Documents de référence — à lire en premier

- [ACTION_LIFECYCLE_CONTRACT_V0](../act/ACTION_LIFECYCLE_CONTRACT_V0.md) · `docs/act/ACTION_LIFECYCLE_CONTRACT_V0.md`
  <br>INPUTCAPTURED → ACTIONCANDIDATEBUILT → PERIPHERYSCORED → SIGMAROUTED → X108EVALUATED → OS3TICKETED → GENCOINEVALUATED → WORLDACTIONDRYRUNREADY → FEEDBACKCAPTURED →…
- [WORLD_ACTION_DRY_RUN_POLICY_V0](../act/WORLD_ACTION_DRY_RUN_POLICY_V0.md) · `docs/act/WORLD_ACTION_DRY_RUN_POLICY_V0.md`
  <br>Le patch ne déclenche pas d’action monde réelle. Il retourne seulement une readiness.
- [F53 — Bus/Bridge Boundary Contract](../architecture/OBSIDIA_F53_BUS_BRIDGE_BOUNDARY_CONTRACT.md) · `docs/architecture/OBSIDIA_F53_BUS_BRIDGE_BOUNDARY_CONTRACT.md`
  <br>bus/bridge is a sovereign boundary carrier. Every response it emits — regardless of mode, route, or signal origin — carries the full sovereignty contract. No response may omit,…
- [Demo Boundary — Obsidia X-108](../demo/README_DEMO_BOUNDARY.md) · `docs/demo/README_DEMO_BOUNDARY.md`
  <br>Ce répertoire contient les documents de démonstration, scripts et rapports de phase F40-F60.
- [Investor Boundary — Obsidia X-108](../investor/README_INVESTOR_BOUNDARY.md) · `docs/investor/README_INVESTOR_BOUNDARY.md`
  <br>Les narratifs investisseur sont séparés du proof technique. Ils peuvent être partagés avec des tiers mais doivent respecter les bornes de claims établies par…
- [Public Boundary — Obsidia X-108 Proof](../public/README_PUBLIC_BOUNDARY.md) · `docs/public/README_PUBLIC_BOUNDARY.md`
  <br>Ce répertoire marque la frontière entre la surface proof publique et le moteur propriétaire interne.
- [World Calls Module](../world_calls/README.md) · `docs/world_calls/README.md`
  <br>- No world call without SovereignTicket
- [REPO_BOUNDARY.md — Frontière Canonique du Dépôt Public](../REPO_BOUNDARY.md) · `docs/REPO_BOUNDARY.md` *(référence probable)*
  <br>obsidia-x108-proofs n'est pas “Obsidia entier”.
- [ACTION_CANDIDATE_TO_WORLD_ACTION_FLOW_V0](../act/ACTION_CANDIDATE_TO_WORLD_ACTION_FLOW_V0.md) · `docs/act/ACTION_CANDIDATE_TO_WORLD_ACTION_FLOW_V0.md` *(référence probable)*
  <br>Passage ActionCandidate vers readiness dry-run. Aucun ACT monde réel dans ce patch.
- [ACTION_SEQUENCE_GOVERNOR_V0](../act/ACTION_SEQUENCE_GOVERNOR_V0.md) · `docs/act/ACTION_SEQUENCE_GOVERNOR_V0.md` *(référence probable)*
  <br>Couvre multi-step, async, tool-call risk, plan change.
- [Brody GPT V1 — Limitations and Boundaries](../release/BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md) · `docs/release/BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md` *(référence probable)*
  <br>This document states honestly and explicitly what Brody GPT V1 is, is not, proves, and does not prove. It is not a marketing document.

<details><summary><b>Rapports, audits et preuves d'exécution</b> (10)</summary>

**`docs/`**

- [WORLD_CALL_GATEWAY_INTEGRATION_REPORT.md](../WORLD_CALL_GATEWAY_INTEGRATION_REPORT.md) — World Call Gateway Integration Report — V4

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT.json](../core_import/P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT.json)
- [P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT.md](../core_import/P67_BOUNDARY_SEMANTIC_SPLIT_AUDIT.md) — P67 — Boundary Semantic Split Audit

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_V1_4_12A_CREATOR_BOUNDARY_TEST_REPORT.md](../freeze/BRODY_V1_4_12A_CREATOR_BOUNDARY_TEST_REPORT.md) — BRODY V1.4.12A CREATOR BOUNDARY TEST REPORT

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [F12C_TERMINAL_MUTATION_BOUNDARY_LIVE.txt](../runtime/F12C_TERMINAL_MUTATION_BOUNDARY_LIVE.txt)
- [F12C_TERMINAL_WRITE_BOUNDARY_LIVE.txt](../runtime/F12C_TERMINAL_WRITE_BOUNDARY_LIVE.txt)
- [F13A_PRE_UI_BRODY_TERMINAL_WRITE_BOUNDARY.txt](../runtime/F13A_PRE_UI_BRODY_TERMINAL_WRITE_BOUNDARY.txt)
- [OBSIDIA_F55_BUS_SIGNAL_INGRESS_PLAN_20260530_000000.json](../runtime/OBSIDIA_F55_BUS_SIGNAL_INGRESS_PLAN_20260530_000000.json)

**`docs/runtime/phase12f_a_api_samples/`** · *dossier lu par du code : ne pas déplacer*

- [negation_guard.json](../runtime/phase12f_a_api_samples/negation_guard.json)
- [write_boundary.json](../runtime/phase12f_a_api_samples/write_boundary.json)

</details>

<details><summary><b>Rapports de phases passées</b> (3)</summary>

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P56D_SIGMA_POST_GUARD_VETO_BOUNDARY.md](../core_import/P56D_SIGMA_POST_GUARD_VETO_BOUNDARY.md) — P56D — Sigma Post-Guard Veto Boundary

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE12E5_A_TOP_LEVEL_BOUNDARY_INVARIANT_PATCH_20260527.md](../runtime/BRODY_PHASE12E5_A_TOP_LEVEL_BOUNDARY_INVARIANT_PATCH_20260527.md) — BRODY_PHASE12E5_A_TOP_LEVEL_BOUNDARY_INVARIANT_PATCH_20260527
- [OBSIDIA_F55_BUS_SIGNAL_INGRESS_PLAN_20260530_000000.md](../runtime/OBSIDIA_F55_BUS_SIGNAL_INGRESS_PLAN_20260530_000000.md) — F55 — Bus/Signal Ingress Plan

</details>

## Fichiers liés au code

24 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
