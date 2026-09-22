# 21 · Valeur : Gencoin et Jcoin

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Attestation de valeur, ledger et frontières économiques, sans autorité d'exécution.

## Où elle intervient dans le trajet d'une demande

- **Étape 4 · Organes spécialisés** : Brody comprend et formule, la mémoire rappelle, les domaines vérifient leur terrain, Obsidure prépare un candidat, Sigma et le Peripheral Mesh mesurent la cohérence, Tree34 et Thermo apportent leurs lectures. Ils proposent, ils ne décident pas.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [periphery/gencoin_sandbox/](../../periphery/gencoin_sandbox) · bac à sable Gencoin

D'après le registre de fonctionnalités V3, **30 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `specs/10_VALUE_GENCOIN_JCOIN/` | 11 |
| `periphery/gencoin_sandbox/` | 6 |
| `periphery/` | 4 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 3 |
| `periphery/contrats/` | 2 |
| `scripts/` | 2 |
| `periphery/schemas/` | 1 |
| `specs/_imports_readonly/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (42)

### Documents de référence — à lire en premier

- [GENCOIN_ANTI_SPECULATION_PROTOCOL_V0](../gencoin/GENCOIN_ANTI_SPECULATION_PROTOCOL_V0.md) · `docs/gencoin/GENCOIN_ANTI_SPECULATION_PROTOCOL_V0.md`
  <br>GC = X108ALLOW × OS3PROOF × DATAOK × MEMORYSTABLE × ENERGYSTABLE × OCSTABLE × PERMISSIONOK × ECONOMICOK × max(0, VALUE-DEBT).
- [GENCOIN_THERMODYNAMIC_VALUE_MODEL_V0](../gencoin/GENCOIN_THERMODYNAMIC_VALUE_MODEL_V0.md) · `docs/gencoin/GENCOIN_THERMODYNAMIC_VALUE_MODEL_V0.md`
  <br>GC = X108ALLOW × OS3PROOF × DATAOK × MEMORYSTABLE × ENERGYSTABLE × OCSTABLE × PERMISSIONOK × ECONOMICOK × max(0, VALUE-DEBT).
- [OBSIDIA_GENCOIN_ENGINE_LARGE_SANDBOX_PRE_FREEZE](../gencoin/sandbox_pre_freeze/README.md) · `docs/gencoin/sandbox_pre_freeze/README.md`
  <br>Statut: PREFREEZE / SANDBOXREADY / NOTPHYSICSCLOSED
- [GENCOIN_DISTRIBUTION_LAW_V0](../gencoin/GENCOIN_DISTRIBUTION_LAW_V0.md) · `docs/gencoin/GENCOIN_DISTRIBUTION_LAW_V0.md` *(référence probable)*
  <br>GC = X108ALLOW × OS3PROOF × DATAOK × MEMORYSTABLE × ENERGYSTABLE × OCSTABLE × PERMISSIONOK × ECONOMICOK × max(0, VALUE-DEBT).
- [GENCOIN_HUMAN_AI_DEBT_LEDGER_V0](../gencoin/GENCOIN_HUMAN_AI_DEBT_LEDGER_V0.md) · `docs/gencoin/GENCOIN_HUMAN_AI_DEBT_LEDGER_V0.md` *(référence probable)*
  <br>GC = X108ALLOW × OS3PROOF × DATAOK × MEMORYSTABLE × ENERGYSTABLE × OCSTABLE × PERMISSIONOK × ECONOMICOK × max(0, VALUE-DEBT).
- [GENCOIN_VALUE_PROOF_ECONOMY_V0_2](../gencoin/GENCOIN_VALUE_PROOF_ECONOMY_V0_2.md) · `docs/gencoin/GENCOIN_VALUE_PROOF_ECONOMY_V0_2.md` *(référence probable)*
  <br>GC = X108ALLOW × OS3PROOF × DATAOK × MEMORYSTABLE × ENERGYSTABLE × OCSTABLE × PERMISSIONOK × ECONOMICOK × max(0, VALUE-DEBT).
- [AVDR — canon](../gencoin/sandbox_pre_freeze/AVDR_CANON.md) · `docs/gencoin/sandbox_pre_freeze/AVDR_CANON.md` *(référence probable)*
  <br>AVDR = Accueil -> Vibration -> Déploiement -> Résolution.
- [Balance Obsidienne — canon](../gencoin/sandbox_pre_freeze/BALANCE_CANON.md) · `docs/gencoin/sandbox_pre_freeze/BALANCE_CANON.md` *(référence probable)*
  <br>La Balance n'est pas un invariant pur du noyau bas.
- [Formules noyau sandbox](../gencoin/sandbox_pre_freeze/FORMULAS.md) · `docs/gencoin/sandbox_pre_freeze/FORMULAS.md` *(référence probable)*
  <br>assistedratio = (paux + pstorageout) / (pinraw + paux + pstorageout)
- [Gencoin — canon conversationnel](../gencoin/sandbox_pre_freeze/GENCOIN_CANON.md) · `docs/gencoin/sandbox_pre_freeze/GENCOIN_CANON.md` *(référence probable)*
  <br>Gencoin est la couche économique d'Obsidia visant à monétiser une valeur réelle produite par des systèmes gouvernés, auditables et contextuellement validés, afin que des…
- [Limites / statuts](../gencoin/sandbox_pre_freeze/LIMITS_AND_STATUS.md) · `docs/gencoin/sandbox_pre_freeze/LIMITS_AND_STATUS.md` *(référence probable)*
  <br>ABSENT dans ce pack au sens preuve physique réelle.
- [PACK A — Familles physiques](../gencoin/sandbox_pre_freeze/PACK_A_FAMILLES_PHYSIQUES.md) · `docs/gencoin/sandbox_pre_freeze/PACK_A_FAMILLES_PHYSIQUES.md` *(référence probable)*
  <br>- grandeur primaire captée: rotation / inertie / transfert mécanique
- [PACK B — M2 captation](../gencoin/sandbox_pre_freeze/PACK_B_M2_CAPTATION.md) · `docs/gencoin/sandbox_pre_freeze/PACK_B_M2_CAPTATION.md` *(référence probable)*
  <br>- grandeur captée exacte: vitesse angulaire + inertie effective
- [PACK C — M3 conversion](../gencoin/sandbox_pre_freeze/PACK_C_M3_CONVERSION.md) · `docs/gencoin/sandbox_pre_freeze/PACK_C_M3_CONVERSION.md` *(référence probable)*
  <br>- entrée exacte: rotation omega + couple
- [PACK D — M4 topologies](../gencoin/sandbox_pre_freeze/PACK_D_M4_TOPOLOGIES.md) · `docs/gencoin/sandbox_pre_freeze/PACK_D_M4_TOPOLOGIES.md` *(référence probable)*
- [PACK F — Besoin / mission / contexte](../gencoin/sandbox_pre_freeze/PACK_F_MISSION_CONTEXTE.md) · `docs/gencoin/sandbox_pre_freeze/PACK_F_MISSION_CONTEXTE.md` *(référence probable)*
  <br>- type: hybride continu + impulsionnel
- [PACK G — Métriques / observabilité](../gencoin/sandbox_pre_freeze/PACK_G_METRICS.md) · `docs/gencoin/sandbox_pre_freeze/PACK_G_METRICS.md` *(référence probable)*
- [PACK H — Hypothèses / branches mortes](../gencoin/sandbox_pre_freeze/PACK_H_HYPOTHESES.md) · `docs/gencoin/sandbox_pre_freeze/PACK_H_HYPOTHESES.md` *(référence probable)*
- [PACK I — Saturations / anti-emballement](../gencoin/sandbox_pre_freeze/PACK_I_SATURATIONS.md) · `docs/gencoin/sandbox_pre_freeze/PACK_I_SATURATIONS.md` *(référence probable)*
  <br>- seuil bas: perte signal -> HOLD
- [PACK J — Transitions d'état](../gencoin/sandbox_pre_freeze/PACK_J_TRANSITIONS.md) · `docs/gencoin/sandbox_pre_freeze/PACK_J_TRANSITIONS.md` *(référence probable)*
- [Protos](../gencoin/sandbox_pre_freeze/PROTOS.md) · `docs/gencoin/sandbox_pre_freeze/PROTOS.md` *(référence probable)*
  <br>D1 + C1 + M4A + M2A + M3A1
- [Carte d'états](../gencoin/sandbox_pre_freeze/STATES.md) · `docs/gencoin/sandbox_pre_freeze/STATES.md` *(référence probable)*
  <br>États:
- [Zones / traces / remédiation — canon](../gencoin/sandbox_pre_freeze/ZONES_SECURITE_CANON.md) · `docs/gencoin/sandbox_pre_freeze/ZONES_SECURITE_CANON.md` *(référence probable)*
  <br>Réponse rapide sur cas déjà connus, déjà typés, déjà couverts par invariants.
- [sandbox_engine.py](../gencoin/sandbox_pre_freeze/sandbox_engine.py) · `docs/gencoin/sandbox_pre_freeze/sandbox_engine.py` *(référence probable)*
- [test_sandbox_engine.py](../gencoin/sandbox_pre_freeze/test_sandbox_engine.py) · `docs/gencoin/sandbox_pre_freeze/test_sandbox_engine.py` *(référence probable)*

<details><summary><b>Rapports, audits et preuves d'exécution</b> (16)</summary>

**`docs/`**

- [GENCOIN_SANDBOX_INGESTION_REPORT.md](../GENCOIN_SANDBOX_INGESTION_REPORT.md) — Gencoin Sandbox Ingestion Report

**`docs/freeze/`** · *dossier lu par du code : ne pas déplacer*

- [GENCOIN_POST_PROOF_LEDGER_V0_REPORT.md](../freeze/GENCOIN_POST_PROOF_LEDGER_V0_REPORT.md) — GENCOIN_POST_PROOF_LEDGER_V0_REPORT

**`docs/gencoin/sandbox_pre_freeze/`** · *dossier lu par du code : ne pas déplacer*

- [MANIFEST_SHA256.json](../gencoin/sandbox_pre_freeze/MANIFEST_SHA256.json)
- [TRANSITIONS.csv](../gencoin/sandbox_pre_freeze/TRANSITIONS.csv)

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [F20B_8000_GENCOIN_COGNITIVE_LEDGER_PAYLOAD.json](../runtime/F20B_8000_GENCOIN_COGNITIVE_LEDGER_PAYLOAD.json)
- [F20B_8012_GENCOIN_COGNITIVE_LEDGER_PAYLOAD.json](../runtime/F20B_8012_GENCOIN_COGNITIVE_LEDGER_PAYLOAD.json)
- [F20B_TERMINAL_GENCOIN_COGNITIVE_LEDGER_8000.txt](../runtime/F20B_TERMINAL_GENCOIN_COGNITIVE_LEDGER_8000.txt)
- [F20B_TERMINAL_GENCOIN_COGNITIVE_LEDGER_8012.txt](../runtime/F20B_TERMINAL_GENCOIN_COGNITIVE_LEDGER_8012.txt)
- [F20C_TERMINAL_GENCOIN_COGNITIVE_LEDGER_VISIBLE_8000.txt](../runtime/F20C_TERMINAL_GENCOIN_COGNITIVE_LEDGER_VISIBLE_8000.txt)
- [F20C_TERMINAL_GENCOIN_COGNITIVE_LEDGER_VISIBLE_8012.txt](../runtime/F20C_TERMINAL_GENCOIN_COGNITIVE_LEDGER_VISIBLE_8012.txt)
- [OBSIDIA_F20A_GENCOIN_COGNITIVE_VALUE_LEDGER_AUDIT_20260528_012740.json](../runtime/OBSIDIA_F20A_GENCOIN_COGNITIVE_VALUE_LEDGER_AUDIT_20260528_012740.json)
- [OBSIDIA_F20A_GENCOIN_COGNITIVE_VALUE_LEDGER_AUDIT_20260528_012740.txt](../runtime/OBSIDIA_F20A_GENCOIN_COGNITIVE_VALUE_LEDGER_AUDIT_20260528_012740.txt)
- [OBSIDIA_F20B_GENCOIN_COGNITIVE_LEDGER_REPORT_20260528_033253.md](../runtime/OBSIDIA_F20B_GENCOIN_COGNITIVE_LEDGER_REPORT_20260528_033253.md) — OBSIDIA F20B — GENCOIN COGNITIVE VALUE / READONLY LEDGER
- [OBSIDIA_F20C_TERMINAL_GENCOIN_LEDGER_VISIBLE_REPORT_20260528_033600.md](../runtime/OBSIDIA_F20C_TERMINAL_GENCOIN_LEDGER_VISIBLE_REPORT_20260528_033600.md) — OBSIDIA F20C — TERMINAL GENCOIN COGNITIVE LEDGER VISIBLE
- [OBSIDIA_F2A_TRANSVERSE_VALUE_INTERFACE_PREP_REPORT.md](../runtime/OBSIDIA_F2A_TRANSVERSE_VALUE_INTERFACE_PREP_REPORT.md) — OBSIDIA F2A — TRANSVERSE VALUE INTERFACE PREP REPORT
- [OBSIDIA_F4_GENCOIN_SHADOW_VALUE_LAYER_REPORT.md](../runtime/OBSIDIA_F4_GENCOIN_SHADOW_VALUE_LAYER_REPORT.md) — OBSIDIA F4 — GENCOIN SHADOW VALUE LAYER REPORT

</details>

<details><summary><b>Rapports de phases passées</b> (1)</summary>

**`docs/gencoin/sandbox_pre_freeze/`** · *dossier lu par du code : ne pas déplacer*

- [PACK_E_P3_P4.md](../gencoin/sandbox_pre_freeze/PACK_E_P3_P4.md) — PACK E — P3 / P4

</details>

## Fichiers liés au code

42 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
