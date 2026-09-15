# 23 · Sécurité et conformité

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Modèles de menace, permissions, supervision humaine, RSSI, RGPD, rotation des secrets.

## Où elle intervient dans le trajet d'une demande

Couche **transverse** : elle encadre toutes les étapes plutôt qu'une seule.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

D'après le registre de fonctionnalités V3, **33 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `runtime_contracts/rssi_rgpd_compliance_spec/` | 11 |
| `runtime_contracts/compliance_data_governance_spec/` | 9 |
| `_source_discovery/F03_RSSI_RGPD_CANON_REPAIR_20260602_155630/` | 2 |
| `_source_discovery/F03_RSSI_RGPD_IMPORT_AUDIT_20260602_155234/` | 2 |
| `_source_discovery/F10_COMPLIANCE_DATA_GOVERNANCE_IMPORT_AUDIT_20260602_160941/` | 2 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 2 |
| `scripts/` | 2 |
| `external_pack/` | 1 |
| `periphery/specs/` | 1 |
| `runtime_contracts/boundaries/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (15)

### Documents de référence — à lire en premier

- [Bias Module](../bias/README.md) · `docs/bias/README.md`
  <br>Bias detection and tracing. Detects cognitive bias in agent output and flags it for review. Never blocks autonomously — flagged bias goes to X108 as context signal.
- [RSSI Evidence Pack — Obsidia X-108](../rssi/README_RSSI_EVIDENCE_PACK.md) · `docs/rssi/README_RSSI_EVIDENCE_PACK.md`
  <br>Ce répertoire indexe le pack d'evidence RSSI local constitué en P79. Le pack distingue :
- [RSSI Evidence Index — Obsidia X-108](../rssi/RSSI_EVIDENCE_INDEX.md) · `docs/rssi/RSSI_EVIDENCE_INDEX.md`
- [Branch Protection Policy — Obsidia X-108](../security/BRANCH_PROTECTION_POLICY.md) · `docs/security/BRANCH_PROTECTION_POLICY.md`
  <br>À configurer via GitHub Settings → Branches → Branch protection rules sur main :
- [Obsidia X-108 - GPS / Defense Response to Space Threats](../investor/SPACE_THREATS_GPS_DEFENSE_RESPONSE_NOTE.md) · `docs/investor/SPACE_THREATS_GPS_DEFENSE_RESPONSE_NOTE.md` *(référence probable)*
  <br>This note translates current public space-threat themes - GNSS jamming,
- [RSSI — Do Not Publish — Obsidia X-108](../rssi/RSSI_DO_NOT_PUBLISH.md) · `docs/rssi/RSSI_DO_NOT_PUBLISH.md` *(référence probable)*
- [RSSI Evidence Boundary — Obsidia X-108](../rssi/RSSI_EVIDENCE_BOUNDARY.md) · `docs/rssi/RSSI_EVIDENCE_BOUNDARY.md` *(référence probable)*
  <br>RSSI EVIDENCE PACK (publiable)
- [Pre-Publication Security Checklist — Obsidia X-108](../security/PRE_PUBLICATION_SECURITY_CHECKLIST.md) · `docs/security/PRE_PUBLICATION_SECURITY_CHECKLIST.md` *(référence probable)*
  <br>docs/runtime/archive/phase1012legacyuntracked20260527/BRODYPHASE12E4A2DOMAINRACCORDAUDIT20260527.md
- [PUBLICATION_SECURITY_GATE_CLEAN](../security/PUBLICATION_SECURITY_GATE_CLEAN.md) · `docs/security/PUBLICATION_SECURITY_GATE_CLEAN.md` *(référence probable)*
  <br>Status: CLEANPUBLICATIONSECURITYGATE

<details><summary><b>Rapports, audits et preuves d'exécution</b> (3)</summary>

**`docs/contracts/env/`**

- [ENV_KEYS_MATRIX.csv](../contracts/env/ENV_KEYS_MATRIX.csv)

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json](../core_import/POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.json)

**`docs/security/`** · *dossier lu par du code : ne pas déplacer*

- [GITHUB_SECURITY_AUDIT.md](../security/GITHUB_SECURITY_AUDIT.md) — GitHub Security Audit — Obsidia X-108

</details>

<details><summary><b>Rapports de phases passées</b> (3)</summary>

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.md](../core_import/POST_P80_SECRET_ROTATION_PUBLICATION_HARDENING.md) — Post-P80 — Secret Rotation and Publication Hardening

**`docs/security/`** · *dossier lu par du code : ne pas déplacer*

- [POST_P80_PUBLICATION_HARDENING_PLAN.md](../security/POST_P80_PUBLICATION_HARDENING_PLAN.md) — Post-P80 — Publication Hardening Plan
- [POST_P80_SECRET_ROTATION_PLAN.md](../security/POST_P80_SECRET_ROTATION_PLAN.md) — Post-P80 — Secret Rotation Plan

</details>

## Fichiers liés au code

14 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
