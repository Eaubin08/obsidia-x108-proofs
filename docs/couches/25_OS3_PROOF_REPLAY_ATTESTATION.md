# 25 · Preuve, replay, attestation (OS3)

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Merkle, replay, RFC3161, ProofKit, receipts : le runtime qui vérifie et scelle les décisions.

## Où elle intervient dans le trajet d'une demande

- **Étape 5 · Preuves et gouvernance** : Tests, replay, Lean, ProofKit, receipts et checkpoints établissent ce qui est prouvé, avant tout passage au réel.
- **Étape 8 · Action contrôlée et trace** : Si c'est autorisé, l'action part par une frontière bornée. Elle est mesurée, scellée et rejouable, et reste visible dans le Workbench et le Terminal.

Voir le trajet complet : [guide général](../README.md).

Cette couche joue un rôle clé dans **le trajet 3 (action)** : voir [TRAJETS.md](../TRAJETS.md), qui explique aussi pourquoi Obsidia fonctionne sans entraînement.

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [proofs/verifiers/verify_all.py](../../proofs/verifiers/verify_all.py) · vérifier toutes les preuves : `python proofs/verifiers/verify_all.py`
- [proofs/verify_merkle.py](../../proofs/verify_merkle.py) · vérifier une inclusion Merkle
- [audit_merkle.py](../../audit_merkle.py) · aide à l'audit Merkle
- [PROOF_INDEX.md](../../PROOF_INDEX.md) · index des preuves

D'après le registre de fonctionnalités V3, **90 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 39 |
| `runtime_contracts/os3_evidence_dry_run/` | 9 |
| `specs/11_PROOF_REPLAY_OS3/` | 9 |
| `proofs/` | 5 |
| `periphery/modules_agents/` | 3 |
| `periphery/` | 3 |
| `periphery/specs/` | 3 |
| `proofs/verifiers/` | 3 |
| `periphery/workflow_governance_readonly/` | 2 |
| `proofs/V18_3_1/` | 2 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (47)

### Documents de référence — à lire en premier

- [OS3_HASH_CHAIN_POLICY_V0](../os3/OS3_HASH_CHAIN_POLICY_V0.md) · `docs/os3/OS3_HASH_CHAIN_POLICY_V0.md`
  <br>OS3 ferme preuve, hash, replay et audit.
- [RFC3161 in P1](../RFC3161.md) · `docs/RFC3161.md` *(référence probable)*
  <br>This document explains how RFC3161 is treated inside the public P1 perimeter.
- [Merkle Seal Anchor Proposal V1](../freeze/MERKLE_SEAL_ANCHOR_PROPOSAL_V1.md) · `docs/freeze/MERKLE_SEAL_ANCHOR_PROPOSAL_V1.md` *(référence probable)*
  <br>Anchor the recursive manifest root hash (MANIFESTSHA256RECURSIVEROOT.txt) into merkleseal.json as a new entry:
- [OS3_PROOF_TICKET_SCHEMA_V0](../os3/OS3_PROOF_TICKET_SCHEMA_V0.md) · `docs/os3/OS3_PROOF_TICKET_SCHEMA_V0.md` *(référence probable)*
  <br>OS3 ferme preuve, hash, replay et audit.

<details><summary><b>Preuves scellées — ne pas modifier</b> (37)</summary>

**`docs/proof/`** · *dossier lu par du code : ne pas déplacer*

- [README_PROOF_BOUNDARY.md](../proof/README_PROOF_BOUNDARY.md) — Proof Boundary — Obsidia X-108

**`docs/proof/canonical_c2_conformance_pilot_v0/`** · *dossier lu par du code : ne pas déplacer*

- [.gitattributes](../proof/canonical_c2_conformance_pilot_v0/.gitattributes)
- [MANIFEST.json](../proof/canonical_c2_conformance_pilot_v0/MANIFEST.json)
- [README.md](../proof/canonical_c2_conformance_pilot_v0/README.md) — Canonical C2 Governed-Remediation Conformance Proof — v0

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/executions/approvals/appr-588b43e080a537ea42c5ce661678bdef/`** · *dossier lu par du code : ne pas déplacer*

- [approval.json](../proof/canonical_c2_conformance_pilot_v0/negative/executions/approvals/appr-588b43e080a537ea42c5ce661678bdef/approval.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/executions/executions/57420e49466cbd17/`** · *dossier lu par du code : ne pas déplacer*

- [execution.json](../proof/canonical_c2_conformance_pilot_v0/negative/executions/executions/57420e49466cbd17/execution.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/kx108_post/`** · *dossier lu par du code : ne pas déplacer*

- [kxpost-1d7c12381fe63a211a2b33765d0f58f3.json](../proof/canonical_c2_conformance_pilot_v0/negative/kx108_post/kxpost-1d7c12381fe63a211a2b33765d0f58f3.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/kx108_pre/`** · *dossier lu par du code : ne pas déplacer*

- [kxpre-59f76e6cd9338e106de3c2052bc2a05e.json](../proof/canonical_c2_conformance_pilot_v0/negative/kx108_pre/kxpre-59f76e6cd9338e106de3c2052bc2a05e.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/ledger/`** · *dossier lu par du code : ne pas déplacer*

- [entries.jsonl](../proof/canonical_c2_conformance_pilot_v0/negative/ledger/entries.jsonl)
- [events.jsonl](../proof/canonical_c2_conformance_pilot_v0/negative/ledger/events.jsonl)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/pre_execution_context/`** · *dossier lu par du code : ne pas déplacer*

- [pec-5f7b35f95483a4ac15e16b2f820cadfc.json](../proof/canonical_c2_conformance_pilot_v0/negative/pre_execution_context/pec-5f7b35f95483a4ac15e16b2f820cadfc.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/rollback_results/`** · *dossier lu par du code : ne pas déplacer*

- [rbk-659f421139a2813712f548ce066406da.json](../proof/canonical_c2_conformance_pilot_v0/negative/rollback_results/rbk-659f421139a2813712f548ce066406da.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/sealed_receipts/`** · *dossier lu par du code : ne pas déplacer*

- [sar-7058c70bb319294dc18807d2b96afad3.json](../proof/canonical_c2_conformance_pilot_v0/negative/sealed_receipts/sar-7058c70bb319294dc18807d2b96afad3.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/sealed_rollback_evidence/`** · *dossier lu par du code : ne pas déplacer*

- [sre-6ece1d558c11cf58c9ed18123163960b.json](../proof/canonical_c2_conformance_pilot_v0/negative/sealed_rollback_evidence/sre-6ece1d558c11cf58c9ed18123163960b.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/selector/batches/1c21b719e8823ece/`** · *dossier lu par du code : ne pas déplacer*

- [batch_proposal.json](../proof/canonical_c2_conformance_pilot_v0/negative/selector/batches/1c21b719e8823ece/batch_proposal.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/negative/test_contract_results/`** · *dossier lu par du code : ne pas déplacer*

- [tcr-874879a85312201faeb0fdb80112f8f5.json](../proof/canonical_c2_conformance_pilot_v0/negative/test_contract_results/tcr-874879a85312201faeb0fdb80112f8f5.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/executions/approvals/appr-b819b7ec6b5477adc1a5d5c9d373d29a/`** · *dossier lu par du code : ne pas déplacer*

- [approval.json](../proof/canonical_c2_conformance_pilot_v0/positive/executions/approvals/appr-b819b7ec6b5477adc1a5d5c9d373d29a/approval.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/executions/executions/da1004250ce41e47/`** · *dossier lu par du code : ne pas déplacer*

- [execution.json](../proof/canonical_c2_conformance_pilot_v0/positive/executions/executions/da1004250ce41e47/execution.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/kx108_post/`** · *dossier lu par du code : ne pas déplacer*

- [kxpost-4fdea9d68801952861eb76cf0df591da.json](../proof/canonical_c2_conformance_pilot_v0/positive/kx108_post/kxpost-4fdea9d68801952861eb76cf0df591da.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/kx108_pre/`** · *dossier lu par du code : ne pas déplacer*

- [kxpre-10d592db211c0dc11b3944f81a6fe047.json](../proof/canonical_c2_conformance_pilot_v0/positive/kx108_pre/kxpre-10d592db211c0dc11b3944f81a6fe047.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/ledger/`** · *dossier lu par du code : ne pas déplacer*

- [entries.jsonl](../proof/canonical_c2_conformance_pilot_v0/positive/ledger/entries.jsonl)
- [events.jsonl](../proof/canonical_c2_conformance_pilot_v0/positive/ledger/events.jsonl)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/pre_execution_context/`** · *dossier lu par du code : ne pas déplacer*

- [pec-541a04676f48b09b21efebcafda3f9b7.json](../proof/canonical_c2_conformance_pilot_v0/positive/pre_execution_context/pec-541a04676f48b09b21efebcafda3f9b7.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/sealed_receipts/`** · *dossier lu par du code : ne pas déplacer*

- [sar-9cece6875a7e6ff5533515766c9573c4.json](../proof/canonical_c2_conformance_pilot_v0/positive/sealed_receipts/sar-9cece6875a7e6ff5533515766c9573c4.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/sealed_rollback_evidence/`** · *dossier lu par du code : ne pas déplacer*

- [sre-de0d0875ce2932ed3d09b861faa706b6.json](../proof/canonical_c2_conformance_pilot_v0/positive/sealed_rollback_evidence/sre-de0d0875ce2932ed3d09b861faa706b6.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/selector/batches/25dcf1b92f147d09/`** · *dossier lu par du code : ne pas déplacer*

- [batch_proposal.json](../proof/canonical_c2_conformance_pilot_v0/positive/selector/batches/25dcf1b92f147d09/batch_proposal.json)

**`docs/proof/canonical_c2_conformance_pilot_v0/positive/test_contract_results/`** · *dossier lu par du code : ne pas déplacer*

- [tcr-cd240c25ba9bff9dd547576e5ccfb15e.json](../proof/canonical_c2_conformance_pilot_v0/positive/test_contract_results/tcr-cd240c25ba9bff9dd547576e5ccfb15e.json)

**`docs/proof/stage4_bounded_mission_authority_closure_v0/`** · *dossier lu par du code : ne pas déplacer*

- [.gitattributes](../proof/stage4_bounded_mission_authority_closure_v0/.gitattributes)
- [CLOSURE_DOSSIER.md](../proof/stage4_bounded_mission_authority_closure_v0/CLOSURE_DOSSIER.md) — Stage 4 — Bounded Mission Authority — Closure Dossier (V0)
- [HASH_MANIFEST.txt](../proof/stage4_bounded_mission_authority_closure_v0/HASH_MANIFEST.txt)
- [MANIFEST.json](../proof/stage4_bounded_mission_authority_closure_v0/MANIFEST.json)
- [README.md](../proof/stage4_bounded_mission_authority_closure_v0/README.md) — `stage4_bounded_mission_authority_closure_v0/`
- [abc_execution_dossier.json](../proof/stage4_bounded_mission_authority_closure_v0/abc_execution_dossier.json)
- [attack_matrix.json](../proof/stage4_bounded_mission_authority_closure_v0/attack_matrix.json)
- [central_authority_map.json](../proof/stage4_bounded_mission_authority_closure_v0/central_authority_map.json)
- [formal_runtime_assurance_map.json](../proof/stage4_bounded_mission_authority_closure_v0/formal_runtime_assurance_map.json)
- [tcb_and_limitations.json](../proof/stage4_bounded_mission_authority_closure_v0/tcb_and_limitations.json)

</details>

<details><summary><b>Rapports, audits et preuves d'exécution</b> (4)</summary>

**`docs/`**

- [P2_BANK_REPLAY_RESULTS.md](../P2_BANK_REPLAY_RESULTS.md) — P2 BANK REPLAY RESULTS

**`docs/investor/`** · *dossier lu par du code : ne pas déplacer*

- [GPS_V01_REPLAY_AND_KERNEL_LIVE_NOTE.md](../investor/GPS_V01_REPLAY_AND_KERNEL_LIVE_NOTE.md) — GPS V0.1 Replay And Kernel Live Note

**`docs/os3/`** · *dossier lu par du code : ne pas déplacer*

- [OS3_REPLAY_MANIFEST_V0.md](../os3/OS3_REPLAY_MANIFEST_V0.md) — OS3_REPLAY_MANIFEST_V0

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_F42_BRODY_GPT_V1_FINAL_RELEASE_SEAL_20260529_080000.json](../runtime/OBSIDIA_F42_BRODY_GPT_V1_FINAL_RELEASE_SEAL_20260529_080000.json)

</details>

<details><summary><b>Archives</b> (2)</summary>

**`docs/runtime/archive/`** · *dossier lu par du code : ne pas déplacer*

- [RAGNAROK_SEAL_1bc96a52_8007.json](../runtime/archive/RAGNAROK_SEAL_1bc96a52_8007.json)
- [RAGNAROK_TO_CURRENT_RUNTIME_SEAL_MIGRATION.md](../runtime/archive/RAGNAROK_TO_CURRENT_RUNTIME_SEAL_MIGRATION.md) — RAGNAROK → CURRENT RUNTIME SEAL — MIGRATION RECORD

</details>

## Fichiers liés au code

47 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
