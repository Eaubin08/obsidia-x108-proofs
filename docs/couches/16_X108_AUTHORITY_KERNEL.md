# 16 · Noyau d'autorité X-108

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Le juge unique (KX108_ONLY). Il évalue avant exécution et rend ACT, HOLD ou BLOCK, en fail-closed et de façon auditable. Aucun modèle, agent ou domaine ne devient souverain.

## Où elle intervient dans le trajet d'une demande

- **Étape 7 · Décision X-108** : Le noyau, seule autorité (KX108_ONLY), rend ACT, HOLD ou BLOCK. Il juge avant l'exécution et bloque en cas de doute (fail-closed).

Voir le trajet complet : [guide général](../README.md).

**Guides à lire pour cette couche :** [SECURITE.md](../SECURITE.md) (l'autorité isolée)

Cette couche joue un rôle clé dans **le trajet 3 (action)** : voir [TRAJETS.md](../TRAJETS.md), qui explique aussi pourquoi Obsidia fonctionne sans entraînement.

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [server.kernel.sealed.cjs](../../server.kernel.sealed.cjs) · pont Express du noyau · SCELLÉ, ne jamais modifier
- [formal/tla/X108.tla](../../formal/tla/X108.tla) · spécification TLA+ de X-108 (lancée par la CI)
- [proofs/tla/X108.tla](../../proofs/tla/X108.tla) · spécification TLA+ de référence
- [proofs/verifiers/verify_decision.py](../../proofs/verifiers/verify_decision.py) · vérifier une décision : `python proofs/verifiers/verify_decision.py examples/bank_suspicious.json`
- [specs/01_X108_AUTHORITY/](../../specs/01_X108_AUTHORITY) · spécifications d'autorité

D'après le registre de fonctionnalités V3, **13 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `specs/01_X108_AUTHORITY/` | 7 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 2 |
| `periphery/specs/` | 1 |
| `runtime_contracts/os3_evidence_dry_run/` | 1 |
| `runtime_contracts/schemas/` | 1 |
| `runtime_contracts/x108_gateway_dry_run_harness/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (15)

### Documents de référence — à lire en premier

- [PERIPHERY_NON_SOVEREIGNTY_CONTRACT_V0](../architecture/PERIPHERY_NON_SOVEREIGNTY_CONTRACT_V0.md) · `docs/architecture/PERIPHERY_NON_SOVEREIGNTY_CONTRACT_V0.md`
  <br>CanScore=true ; CanRecommendHold=true ; CanEmitAct=false ; CanAuthorize=false ; CanMutateKernel=false ; CanMintGencoinAlone=false.
- [KERNEL_BOUNDARY_CHECK_PROTOCOL](../protocols/KERNEL_BOUNDARY_CHECK_PROTOCOL.md) · `docs/protocols/KERNEL_BOUNDARY_CHECK_PROTOCOL.md`
  <br>Définir le check de frontière protégeant Kernel/X108 et les surfaces
- [KERNEL_OVERVIEW.md — Spécification du Noyau X-108](../KERNEL_OVERVIEW.md) · `docs/KERNEL_OVERVIEW.md` *(référence probable)*
  <br>Le Kernel X-108 est le noyau de gouvernance déterministe d'Obsidia. Il est le "juge" qui évalue les actions avant exécution selon des règles mathématiques strictes et auditables.
- [Capability Is Not Authority — V1](../civilization/CAPABILITY_IS_NOT_AUTHORITY_V1.md) · `docs/civilization/CAPABILITY_IS_NOT_AUTHORITY_V1.md` *(référence probable)*
  <br>A system capable of generating an output is not authorized to act on that capability unless a governance chain explicitly permits it.

<details><summary><b>Rapports, audits et preuves d'exécution</b> (4)</summary>

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_CORE_PROOF_METRIC_AUTHORITY_MATRIX_V0.json](../core_import/OBSIDIA_CORE_PROOF_METRIC_AUTHORITY_MATRIX_V0.json)
- [P56A_C0_GAMMA_OS3_AUTHORITY_AUDIT.json](../core_import/P56A_C0_GAMMA_OS3_AUTHORITY_AUDIT.json)

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md](../freeze/BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md) — BRODY RIGHTS / AUTHORITY / CAPABILITY MATRIX REPORT
- [BRODY_WORKBENCH_AUTHORITY_SNAPSHOT_REPORT.md](../freeze/BRODY_WORKBENCH_AUTHORITY_SNAPSHOT_REPORT.md) — BRODY WORKBENCH AUTHORITY SNAPSHOT REPORT

</details>

<details><summary><b>Archives</b> (7)</summary>

**`docs/freeze/BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234/`** · *dossier lu par du code : ne pas déplacer*

- [RECOVERY_VALIDATION_SUMMARY.txt](../freeze/BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234/RECOVERY_VALIDATION_SUMMARY.txt)
- [protected_files_diff.txt](../freeze/BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234/protected_files_diff.txt)
- [pytest_all_output.txt](../freeze/BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234/pytest_all_output.txt)
- [pytest_api_output.txt](../freeze/BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234/pytest_api_output.txt)
- [pytest_non_sovereignty_output.txt](../freeze/BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234/pytest_non_sovereignty_output.txt)
- [sigma_output.txt](../freeze/BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234/sigma_output.txt)
- [workbench_build_output.txt](../freeze/BRODY_RIGHTS_AUTHORITY_FINAL_VALIDATION_RECOVERY_20260520_064234/workbench_build_output.txt)

</details>

## Fichiers liés au code

15 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
