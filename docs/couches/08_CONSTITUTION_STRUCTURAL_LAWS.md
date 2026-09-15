# 08 · Constitution et lois structurelles

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Les contraintes constitutionnelles entre couches, qui expliquent les frontières et l'autorité.

## Où elle intervient dans le trajet d'une demande

Couche **conceptuelle** : elle ne s'exécute pas dans le trajet, elle définit le vocabulaire et les lois que les autres couches appliquent.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

D'après le registre de fonctionnalités V3, **20 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `specs/02_INTERLAYER_CONSTITUTION/` | 8 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 6 |
| `periphery/specs/` | 3 |
| `Demo-obsidia-x108-proof/connectors/` | 1 |
| `periphery/` | 1 |
| `specs/_imports_readonly/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (27)

### Documents de référence — à lire en premier

- [AGENTIC_ENGINE_EXTENSION_MAP_V0](../architecture/AGENTIC_ENGINE_EXTENSION_MAP_V0.md) · `docs/architecture/AGENTIC_ENGINE_EXTENSION_MAP_V0.md`
  <br>Le moteur ajouté est une extension périphérique : agents, action lifecycle, sequence governor, dry-run gateway, feedback memory candidate.
- [CONTROL_PLANE_ORCHESTRATOR_SPEC_V0](../architecture/CONTROL_PLANE_ORCHESTRATOR_SPEC_V0.md) · `docs/architecture/CONTROL_PLANE_ORCHESTRATOR_SPEC_V0.md`
  <br>Le control plane orchestre les gates et fusionne les signaux. Il ne décide pas.
- [CROSS_LAYER_STABILIZATION_MATRIX_V0](../architecture/CROSS_LAYER_STABILIZATION_MATRIX_V0.md) · `docs/architecture/CROSS_LAYER_STABILIZATION_MATRIX_V0.md`
  <br>Chaque couche produit un score ou un signal. Aucun score ne produit ACT.
- [F74 — Fresh Clone Reproducibility](../architecture/F74_FRESH_CLONE_REPRODUCIBILITY.md) · `docs/architecture/F74_FRESH_CLONE_REPRODUCIBILITY.md`
  <br>Date : 2026-05-30 | Statut : PASS P0 items | Score audit : 8/11 (était 0/11)
- [F76b — Prod Security Complete](../architecture/F76B_PROD_SECURITY_COMPLETE.md) · `docs/architecture/F76B_PROD_SECURITY_COMPLETE.md`
  <br>Date : 2026-05-30 | Statut : PASS | F76 score : 10/10
- [OBSIDIA_FULL_AGENTIC_CONSTITUTIONAL_STACK_V0](../architecture/OBSIDIA_FULL_AGENTIC_CONSTITUTIONAL_STACK_V0.md) · `docs/architecture/OBSIDIA_FULL_AGENTIC_CONSTITUTIONAL_STACK_V0.md`
  <br>Pipeline complet : INPUT → Control Plane → Data → Provenance → Memory → Sigma → EML → Energy → Timeverse → OCS → Operational Constance → Permission/Economic → X-108 → OS3 →…
- [OBSIDIA X-108 — File Map V4](../architecture/OBSIDIA_X108_V4_FILE_MAP.md) · `docs/architecture/OBSIDIA_X108_V4_FILE_MAP.md`
  <br>Total .lean locaux : 27 fichiers | sorry : 0
- [OBSIDIA X-108 — TODO Matrix V4](../architecture/OBSIDIA_X108_V4_TODO_MATRIX.md) · `docs/architecture/OBSIDIA_X108_V4_TODO_MATRIX.md`
  <br>ID | Domaine | Gate | Priorité | Type | Fichier/Chemin | Action | Risque si non fait | Validation
- [REPO_BOUNDARY_POLICY_V0](../architecture/REPO_BOUNDARY_POLICY_V0.md) · `docs/architecture/REPO_BOUNDARY_POLICY_V0.md`
  <br>Frontière : preuve/specs/tests dans x108-proofs ; runtime/connecteurs dans Demo.
- [RUNBOOK_TERMINAL_FIRST_V0](../architecture/RUNBOOK_TERMINAL_FIRST_V0.md) · `docs/architecture/RUNBOOK_TERMINAL_FIRST_V0.md`
  <br>PowerShell-first. Aucun éditeur manuel requis.
- [SOURCE_OF_TRUTH_POLICY_V0](../architecture/SOURCE_OF_TRUTH_POLICY_V0.md) · `docs/architecture/SOURCE_OF_TRUTH_POLICY_V0.md`
  <br>obsidia-x108-proofs = preuve. Demo-obsidia-x108-proof = terrain. Autres repos = archives migrables.
- [X108_REBRANCHING_POLICY_V0](../architecture/X108_REBRANCHING_POLICY_V0.md) · `docs/architecture/X108_REBRANCHING_POLICY_V0.md`
  <br>Branchement autorisé : PeripheralSignalPacket → Sigma/Guard → OS3 → Gencoin.
- [ENV_KEYS_MATRIX](../contracts/env/ENV_KEYS_MATRIX.md) · `docs/contracts/env/ENV_KEYS_MATRIX.md`
- [OBSIDIA_OPERATOR_DOCTRINE](../protocols/OBSIDIA_OPERATOR_DOCTRINE.md) · `docs/protocols/OBSIDIA_OPERATOR_DOCTRINE.md`
  <br>Ce document définit les règles doctrinales d'opération de l'architecture Obsidia X-108.
- [OBSIDIA_PREMORTEM_PROTOCOL](../protocols/OBSIDIA_PREMORTEM_PROTOCOL.md) · `docs/protocols/OBSIDIA_PREMORTEM_PROTOCOL.md`
  <br>Le premortem est une analyse prospective des risques d'un APPLY avant son exécution.
- [OIE_BENCHMARK_PROTOCOL](../protocols/OIE_BENCHMARK_PROTOCOL.md) · `docs/protocols/OIE_BENCHMARK_PROTOCOL.md`
  <br>Standardiser les benchmarks de l'Obsidia Inference Economy (OIE).
- [SIGMA_GUIDANCE_V0_APPLY_PROTOCOL](../protocols/SIGMA_GUIDANCE_V0_APPLY_PROTOCOL.md) · `docs/protocols/SIGMA_GUIDANCE_V0_APPLY_PROTOCOL.md`
  <br>Standardiser l'application et l'interprétation de Sigma Guidance V0.
- [OBSIDIA_TERMINAL_ALIASES_NATURELS_V2 — spécification](../specs/OBSIDIA_TERMINAL_ALIASES_NATURELS_V2.md) · `docs/specs/OBSIDIA_TERMINAL_ALIASES_NATURELS_V2.md`
  <br>Scope : ALIASESNATURELSV2 (+ correction Thermo issue de
- [OBSIDIA_TERMINAL_DOCX_ADAPTER_V3](../specs/OBSIDIA_TERMINAL_DOCX_ADAPTER_V3.md) · `docs/specs/OBSIDIA_TERMINAL_DOCX_ADAPTER_V3.md`
  <br>V3 ajoute le support de lecture DOCX au terminal Obsidia via extraction stdlib-only
- [OBSIDIA_TERMINAL_LARGE_DOC_READ_V2 (tranche V2A) — spécification](../specs/OBSIDIA_TERMINAL_LARGE_DOC_READ_V2.md) · `docs/specs/OBSIDIA_TERMINAL_LARGE_DOC_READ_V2.md`
  <br>Scope : LARGEDOCREADV2A — moitié (a) du design
- [OBSIDIA_TERMINAL_LARGE_DOC_READ_V2B — spécification](../specs/OBSIDIA_TERMINAL_LARGE_DOC_READ_V2B.md) · `docs/specs/OBSIDIA_TERMINAL_LARGE_DOC_READ_V2B.md`
  <br>Scope : LARGEDOCREADV2B. Implémente SUMMARIZELOCALPROGRESSIVE,
- [OBSIDIA_TERMINAL_LOCAL_READ_GUIDE_V1 — spécification](../specs/OBSIDIA_TERMINAL_LOCAL_READ_GUIDE_V1.md) · `docs/specs/OBSIDIA_TERMINAL_LOCAL_READ_GUIDE_V1.md`
  <br>Scope : LOCALREADGUIDEV1, issu du design
- [OBSIDIA_TERMINAL_RESPONSE_ROUTER_NL_INTENT_V2 — spécification](../specs/OBSIDIA_TERMINAL_RESPONSE_ROUTER_NL_INTENT_V2.md) · `docs/specs/OBSIDIA_TERMINAL_RESPONSE_ROUTER_NL_INTENT_V2.md`
  <br>Scope : OBSIDIAANSWERROUTERNLINTENTV2. Extension de la couche
- [Agentic Constitutional Civilization Stack — V1](../civilization/AGENTIC_CONSTITUTIONAL_CIVILIZATION_STACK_V1.md) · `docs/civilization/AGENTIC_CONSTITUTIONAL_CIVILIZATION_STACK_V1.md` *(référence probable)*
  <br>The Agentic Constitutional Civilization Stack describes how a deterministic governance kernel (Obsidia X-108) anchors a layered system of agentic components into a…
- [Obsidia as Agentic Governance Infrastructure — V1](../civilization/OBSIDIA_AS_AGENTIC_GOVERNANCE_INFRASTRUCTURE_V1.md) · `docs/civilization/OBSIDIA_AS_AGENTIC_GOVERNANCE_INFRASTRUCTURE_V1.md` *(référence probable)*
  <br>Obsidia X-108 is a deterministic governance kernel — not a model, not a framework, not a platform. It is the constitutional core of a layered agentic system.

<details><summary><b>Rapports, audits et preuves d'exécution</b> (2)</summary>

**`docs/architecture/`** · *dossier lu par du code : ne pas déplacer*

- [F72_OS_TRAD_IR_REVERSE_DEEP_PIPELINE_AUDIT.md](../architecture/F72_OS_TRAD_IR_REVERSE_DEEP_PIPELINE_AUDIT.md) — F72 ? OS Trad / IR / Reverse Deep Pipeline Audit

**`docs/protocols/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_VERIFICATION_LOOP_PROTOCOL.md](../protocols/OBSIDIA_VERIFICATION_LOOP_PROTOCOL.md) — OBSIDIA_VERIFICATION_LOOP_PROTOCOL

</details>

## Fichiers liés au code

26 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
