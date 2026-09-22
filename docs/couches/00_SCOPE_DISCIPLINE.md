# 00 · Périmètre et discipline

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Ce que le projet prétend et ne prétend pas : statut public, limites, gouvernance du périmètre. C'est la porte d'entrée qui fixe les frontières des affirmations.

## Où elle intervient dans le trajet d'une demande

Couche **transverse** : elle encadre toutes les étapes plutôt qu'une seule.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

D'après le registre de fonctionnalités V3, **48 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `specs/00_SCOPE_DISCIPLINE/` | 9 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 3 |
| `runtime_contracts/compliance_data_governance_spec/` | 3 |
| `runtime_contracts/rssi_rgpd_compliance_spec/` | 3 |
| `runtime_contracts/education_benchmark_dry_run/` | 2 |
| `runtime_contracts/freeze_audit/` | 2 |
| `runtime_contracts/reports/` | 2 |
| `specs/12_NARRATIVE_PROVENANCE_LAYER/` | 2 |
| `.claude/context/` | 1 |
| `REPRODUCIBILITY_CHECKLIST.md/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (34)

### Documents de référence — à lire en premier

- [METRICS STATUS POLICY](../METRICS_STATUS_POLICY.md) · `docs/METRICS_STATUS_POLICY.md`
  <br>Status: UPDATEDFROMAUDITMAPPINGV0
- [Obsidia / Kernel X108](../README_OBSIDIA_X108_GITHUB_V2.md) · `docs/README_OBSIDIA_X108_GITHUB_V2.md`
  <br>Obsidia / Kernel X108 est une architecture de gouvernance décisionnelle pour systèmes IA, agents autonomes et workflows critiques.
- [F69 ? Test Suite Taxonomy Baseline](../architecture/F69_TEST_SUITE_TAXONOMY_BASELINE.md) · `docs/architecture/F69_TEST_SUITE_TAXONOMY_BASELINE.md`
  <br>- Status: PASSTAXONOMYGENERATED
- [F71.1 ? Risk Flags Classification](../architecture/F71_1_RISK_FLAGS_CLASSIFICATION.md) · `docs/architecture/F71_1_RISK_FLAGS_CLASSIFICATION.md`
  <br>- Status: PASSNONBLOCKING
- [F72.1 ? Risk Flags Classification](../architecture/F72_1_RISK_FLAGS_CLASSIFICATION.md) · `docs/architecture/F72_1_RISK_FLAGS_CLASSIFICATION.md`
  <br>- Status: PASSNONBLOCKING
- [F73.1 ? Blocking Risk Classification](../architecture/F73_1_BLOCKING_RISK_CLASSIFICATION.md) · `docs/architecture/F73_1_BLOCKING_RISK_CLASSIFICATION.md`
  <br>- Status: FAILRUNTIMEBLOCKERSREMAIN
- [F74–F77 Validation Commands](../architecture/F74_F77_COMMANDS.md) · `docs/architecture/F74_F77_COMMANDS.md`
  <br>cd "C:\Users\User\Desktop\obsidia-engine-proof-core\obsidia-x108-proofsREMOTEA5F21C6B"
- [F74–F77 Risk Register](../architecture/F74_F77_RISK_REGISTER.md) · `docs/architecture/F74_F77_RISK_REGISTER.md`
  <br>alloworigins=[""] autorise n'importe quel domaine à appeler l'API via un navigateur. En environnement de démonstration ou de production, cela expose toutes les routes (y…
- [F74–F77 TODO Matrix](../architecture/F74_F77_TODO_MATRIX.md) · `docs/architecture/F74_F77_TODO_MATRIX.md`
  <br>Priorités :
- [OBSIDIA X-108 — Gate Status V4](../architecture/OBSIDIA_X108_V4_GATE_STATUS.md) · `docs/architecture/OBSIDIA_X108_V4_GATE_STATUS.md`
  <br>Lean build : proofs/lean/lakefile.lean → BUILD SUCCESS (formal/tla/tlcresults/leanbuild.log)
- [Rollback Plan — F74 / F76a / F76b](../architecture/ROLLBACK_PLAN.md) · `docs/architecture/ROLLBACK_PLAN.md`
  <br>Date : 2026-05-30 | Jamais de git reset --hard
- [OBSIDIA_LOCAL_CORPUS_V2 — spécification](../specs/OBSIDIA_LOCAL_CORPUS_V2.md) · `docs/specs/OBSIDIA_LOCAL_CORPUS_V2.md`
  <br>Scope : LOCALCORPUSEXTENSIONV2. Extension données uniquement du
- [Periphery public index](../status/PERIPHERY_PUBLIC_INDEX.md) · `docs/status/PERIPHERY_PUBLIC_INDEX.md`
  <br>Status: READONLYPUBLICINDEX
- [Status documentation index](../status/README_STATUS_INDEX.md) · `docs/status/README_STATUS_INDEX.md`
  <br>Status: PUBLICDOCSURFACEINDEX
- [Limits](../LIMITS.md) · `docs/LIMITS.md` *(référence probable)*
  <br>This document states the structural limits of the public P1 perimeter.
- [Proof Scope](../PROOF_SCOPE.md) · `docs/PROOF_SCOPE.md` *(référence probable)*
  <br>Ce document définit comment lire le périmètre public de preuves de obsidia-x108-proofs après le freeze P1.
- [Carte du dépôt (Repo Map)](../REPO_MAP.md) · `docs/REPO_MAP.md` *(référence probable)*
  <br>Ce fichier aide un lecteur externe à naviguer dans le dépôt public P1.
- [NOT_YET_IMPLEMENTED_AFTER_V2](../roadmap/NOT_YET_IMPLEMENTED_AFTER_V2.md) · `docs/roadmap/NOT_YET_IMPLEMENTED_AFTER_V2.md` *(référence probable)*
  <br>À faire : runtime ACT réel, Graphiti/Brody feedback, ledger Gencoin persistant, tests adversariaux, seuils par domaine, vue régulateur, machine-checking.
- [Graphiti full records keep decision](../status/GRAPHITI_FULL_RECORDS_KEEP_DECISION.md) · `docs/status/GRAPHITI_FULL_RECORDS_KEEP_DECISION.md` *(référence probable)*
  <br>Status: KEEPFULLRECORDS
- [Known Limits](../status/KNOWN_LIMITS.md) · `docs/status/KNOWN_LIMITS.md` *(référence probable)*
  <br>External dependencies:
- [Statut public](../status/PUBLIC_STATUS.md) · `docs/status/PUBLIC_STATUS.md` *(référence probable)*
  <br>P1 FERMÉ
- [Repository Map](../status/REPO_MAP.md) · `docs/status/REPO_MAP.md` *(référence probable)*
  <br>Root:
- [USE_CASES.md — Cas d'Usage Concrets](../status/USE_CASES.md) · `docs/status/USE_CASES.md` *(référence probable)*
  <br>Une banque reçoit une transaction de 8 000€ d'un compte vers un compte inconnu. Les signaux de fraude sont élevés : nouveau destinataire, montant anormal, heure inhabituelle.

<details><summary><b>Rapports, audits et preuves d'exécution</b> (10)</summary>

**`docs/`**

- [DEFERRED_PHASES_CLOSED_REPORT.md](../DEFERRED_PHASES_CLOSED_REPORT.md) — Deferred Phases Closed Report
- [DO_NOT_TOUCH_REPORT_FINAL.md](../DO_NOT_TOUCH_REPORT_FINAL.md) — Do Not Touch Report — Final

**`docs/architecture/`** · *dossier lu par du code : ne pas déplacer*

- [F71_34_TREES_DEEP_ACTIVATION_AUDIT.md](../architecture/F71_34_TREES_DEEP_ACTIVATION_AUDIT.md) — F71 ? 34 Trees Deep Activation Audit
- [F73_3_SCOPE_AWARE_FINAL_AUDIT.md](../architecture/F73_3_SCOPE_AWARE_FINAL_AUDIT.md) — F73.3 ? Scope-Aware Final Adversarial Audit
- [F73_ADVERSARIAL_HARDENING_ADVANCED_AUDIT.md](../architecture/F73_ADVERSARIAL_HARDENING_ADVANCED_AUDIT.md) — F73 ? Adversarial Hardening Advanced Audit
- [F74_F77_AUDIT_RECONCILIATION.md](../architecture/F74_F77_AUDIT_RECONCILIATION.md) — F74-F77 Audit Reconciliation
- [F74_F77_FINALIZATION_AUDIT.md](../architecture/F74_F77_FINALIZATION_AUDIT.md) — F74–F77 Finalization Audit
- [OBSIDIA_X108_V4_CHECKLIST_AUDIT.md](../architecture/OBSIDIA_X108_V4_CHECKLIST_AUDIT.md) — OBSIDIA X-108 — Audit Checklist V4

**`docs/status/`** · *dossier lu par du code : ne pas déplacer*

- [DEFERRED_PHASES_REPORT.md](../status/DEFERRED_PHASES_REPORT.md) — Deferred Phases Report — Obsidia X-108

**`docs/status/mmonde_reconciliation/`** · *dossier lu par du code : ne pas déplacer*

- [O1_NON_ACTION_LEGITIME_ROOT_CANONICAL_MINIMAL_V1.md](../status/mmonde_reconciliation/O1_NON_ACTION_LEGITIME_ROOT_CANONICAL_MINIMAL_V1.md) — O1 — Non-Action Légitime

</details>

<details><summary><b>Rapports de phases passées</b> (1)</summary>

**`docs/`**

- [P2_ROADMAP.md](../P2_ROADMAP.md) — Trajectoire P2 et suite

</details>

## Fichiers liés au code

33 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
