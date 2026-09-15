# 11 · Haute périphérie : Sigma et Peripheral Mesh

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Sigma surveille la cohérence de la stack (contradictions, dérives, preuves manquantes), guide et explique, sans trancher. Le Peripheral Mesh regroupe les organes spécialisés : Path Compute, Timeverse, OIE, OCS, Causal Trace, Data et Provenance Gates, Reverse OS.

## Où elle intervient dans le trajet d'une demande

- **Étape 4 · Organes spécialisés** : Brody comprend et formule, la mémoire rappelle, les domaines vérifient leur terrain, Obsidure prépare un candidat, Sigma et le Peripheral Mesh mesurent la cohérence, Tree34 et Thermo apportent leurs lectures. Ils proposent, ils ne décident pas.

Voir le trajet complet : [guide général](../README.md).

Cette couche joue un rôle clé dans **le trajet 1 (cognition)** : voir [TRAJETS.md](../TRAJETS.md), qui explique aussi pourquoi Obsidia fonctionne sans entraînement.

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [sigma/run_pipeline.py](../../sigma/run_pipeline.py) · pipeline Sigma : `python sigma/run_pipeline.py bank sigma/examples/bank_normal.json`
- [sigma/sigma_monitor.py](../../sigma/sigma_monitor.py) · moniteur Sigma : `python sigma/sigma_monitor.py --json`
- [periphery/reverse_os/](../../periphery/reverse_os) · Reverse OS

D'après le registre de fonctionnalités V3, **44 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `_source_packs/REVERSE_OS_INTERLANGUAGE_CANON_V1/` | 13 |
| `periphery/` | 7 |
| `periphery/consciousness_regimes/` | 4 |
| `periphery/reverse_os/` | 4 |
| `specs/06_HIGH_PERIPHERY_SYSTEMS/` | 4 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 3 |
| `periphery/bdf/` | 3 |
| `periphery/hexaflux/` | 3 |
| `scripts/` | 2 |
| `runtime_wiring/source_runtime/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (30)

### Documents de référence — à lire en premier

- [Final Sigma Branch Review](../architecture/FINAL_SIGMA_BRANCH_REVIEW.md) · `docs/architecture/FINAL_SIGMA_BRANCH_REVIEW.md`
  <br>- Status: REVIEWREQUIRED
- [Sigma Final Freeze Index ? F60 to F68](../architecture/SIGMA_FINAL_FREEZE_INDEX_F60_TO_F68.md) · `docs/architecture/SIGMA_FINAL_FREEZE_INDEX_F60_TO_F68.md`
  <br>Date UTC: 20260530014524
- [PERMISSION_ECONOMIC_CONTRACT_V0](../periphery/PERMISSION_ECONOMIC_CONTRACT_V0.md) · `docs/periphery/PERMISSION_ECONOMIC_CONTRACT_V0.md`
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [OBSIDIA SIGMA GUIDANCE — spécification (V0 + FRESH_SIGNAL_V1)](../specs/OBSIDIA_SIGMA_GUIDANCE_V0.md) · `docs/specs/OBSIDIA_SIGMA_GUIDANCE_V0.md`
  <br>Scopes : SIGMAGUIDANCEV0, CALIBRATESIGMATERMINALGUIDANCEV0,
- [Sigma Public P1](../SIGMA.md) · `docs/SIGMA.md` *(référence probable)*
  <br>This document explains what Sigma means in the public P1 perimeter of obsidia-x108-proofs.
- [BANK_ADAPTER_MAPPING_V0](../periphery/BANK_ADAPTER_MAPPING_V0.md) · `docs/periphery/BANK_ADAPTER_MAPPING_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [BRODY_TRIADIC_MEMORY_GOVERNOR_READONLY_V1](../periphery/BRODY_TRIADIC_MEMORY_GOVERNOR_READONLY_V1.md) · `docs/periphery/BRODY_TRIADIC_MEMORY_GOVERNOR_READONLY_V1.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [DATA_PURITY_FRESHNESS_GATE_V0](../periphery/DATA_PURITY_FRESHNESS_GATE_V0.md) · `docs/periphery/DATA_PURITY_FRESHNESS_GATE_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [EML_SYMBOLIC_COMPRESSION_V0](../periphery/EML_SYMBOLIC_COMPRESSION_V0.md) · `docs/periphery/EML_SYMBOLIC_COMPRESSION_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [OCS_GENERATION_COST_LAYER_V0](../periphery/OCS_GENERATION_COST_LAYER_V0.md) · `docs/periphery/OCS_GENERATION_COST_LAYER_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [OPERATIONAL_CONSTANCE_LAYER_V0](../periphery/OPERATIONAL_CONSTANCE_LAYER_V0.md) · `docs/periphery/OPERATIONAL_CONSTANCE_LAYER_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [PERIPHERAL_TO_SIGMA_MAPPING_V0](../periphery/PERIPHERAL_TO_SIGMA_MAPPING_V0.md) · `docs/periphery/PERIPHERAL_TO_SIGMA_MAPPING_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [PROVENANCE_ANTI_MIMETIC_GATE_V0](../periphery/PROVENANCE_ANTI_MIMETIC_GATE_V0.md) · `docs/periphery/PROVENANCE_ANTI_MIMETIC_GATE_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [SIGMA_ADAPTATION_BOUNDARY_V0](../periphery/SIGMA_ADAPTATION_BOUNDARY_V0.md) · `docs/periphery/SIGMA_ADAPTATION_BOUNDARY_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [TIMEVERSE_TRAJECTORY_LAYER_V0](../periphery/TIMEVERSE_TRAJECTORY_LAYER_V0.md) · `docs/periphery/TIMEVERSE_TRAJECTORY_LAYER_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [TRADING_ADAPTER_MAPPING_V0](../periphery/TRADING_ADAPTER_MAPPING_V0.md) · `docs/periphery/TRADING_ADAPTER_MAPPING_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.

<details><summary><b>Rapports, audits et preuves d'exécution</b> (12)</summary>

**`docs/architecture/`** · *dossier lu par du code : ne pas déplacer*

- [SIGMA_REMAINDER_BRANCHING_AUDIT_F66_TO_F73.md](../architecture/SIGMA_REMAINDER_BRANCHING_AUDIT_F66_TO_F73.md) — Sigma Remainder Branching Audit — F66 to F73

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P56A_C_DIFF_obsidia_sigma_v130.diff](../core_import/P56A_C_DIFF_obsidia_sigma_v130.diff)
- [P56A_C_SIGMA_V130_RISK_SCAN.txt](../core_import/P56A_C_SIGMA_V130_RISK_SCAN.txt)
- [P56C_AUDIT_ONLY_P10_obsidia_sigma_v130.py.diff](../core_import/P56C_AUDIT_ONLY_P10_obsidia_sigma_v130.py.diff)
- [P74_SIGMA_SAFE_EVOLUTION.json](../core_import/P74_SIGMA_SAFE_EVOLUTION.json)

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [F18B_8000_EXISTING_REVERSE_OS_RUNTIME_PAYLOAD.json](../runtime/F18B_8000_EXISTING_REVERSE_OS_RUNTIME_PAYLOAD.json)
- [F18B_8012_EXISTING_REVERSE_OS_RUNTIME_PAYLOAD.json](../runtime/F18B_8012_EXISTING_REVERSE_OS_RUNTIME_PAYLOAD.json)
- [F18B_TERMINAL_EXISTING_REVERSE_OS_8000.txt](../runtime/F18B_TERMINAL_EXISTING_REVERSE_OS_8000.txt)
- [F18B_TERMINAL_EXISTING_REVERSE_OS_8012.txt](../runtime/F18B_TERMINAL_EXISTING_REVERSE_OS_8012.txt)
- [OBSIDIA_F23A6_0_ORCHESTRATOR_SIGMA_AWARENESS_AUDIT_20260528_220322.json](../runtime/OBSIDIA_F23A6_0_ORCHESTRATOR_SIGMA_AWARENESS_AUDIT_20260528_220322.json)
- [OBSIDIA_F23A6_0_ORCHESTRATOR_SIGMA_AWARENESS_AUDIT_20260528_220322.md](../runtime/OBSIDIA_F23A6_0_ORCHESTRATOR_SIGMA_AWARENESS_AUDIT_20260528_220322.md) — OBSIDIA F23A6.0 — ORCHESTRATOR SIGMA AWARENESS AUDIT
- [OBSIDIA_F2B_SIGMA_CALIBRATED_REPORT.md](../runtime/OBSIDIA_F2B_SIGMA_CALIBRATED_REPORT.md) — OBSIDIA F2B — SIGMA CALIBRATED REPORT

</details>

<details><summary><b>Rapports de phases passées</b> (2)</summary>

**`docs/demo/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_F60_SIGMA_REGISTRY_READINESS.md](../demo/OBSIDIA_F60_SIGMA_REGISTRY_READINESS.md) — F60 — Sigma Registry Readiness

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [BRODY_PHASE12L_RIGHTPANEL_ADAPTIVE_SIGMA_FREEZE_20260527.md](../runtime/BRODY_PHASE12L_RIGHTPANEL_ADAPTIVE_SIGMA_FREEZE_20260527.md) — BRODY_PHASE12L_RIGHTPANEL_ADAPTIVE_SIGMA_FREEZE_20260527

</details>

## Fichiers liés au code

30 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
