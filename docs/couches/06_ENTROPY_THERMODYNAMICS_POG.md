# 06 · Entropie et thermodynamique

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Thermo : mesure des coûts, de la dissipation et de l'entropie des trajectoires.

## Où elle intervient dans le trajet d'une demande

- **Étape 4 · Organes spécialisés** : Brody comprend et formule, la mémoire rappelle, les domaines vérifient leur terrain, Obsidure prépare un candidat, Sigma et le Peripheral Mesh mesurent la cohérence, Tree34 et Thermo apportent leurs lectures. Ils proposent, ils ne décident pas.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

D'après le registre de fonctionnalités V3, **42 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 16 |
| `specs/03_ENTROPY_DISCIPLINE/` | 10 |
| `periphery/pepites_search_algo/` | 5 |
| `_source_discovery/OBSIDIA_NPL_PACK_AUDIO_ENTROPY_AUDIT_V1/` | 3 |
| `_source_discovery/OBSIDIA_P107_P161_FORMAL_TARGET_AUDIT_V1/` | 1 |
| `apps/obsidia_api/` | 1 |
| `periphery/agents/` | 1 |
| `periphery/number_encoding/` | 1 |
| `run_lyapunov.py/` | 1 |
| `runtime_contracts/boundaries/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (14)

### Documents de référence — à lire en premier

- [ENERGY_THERMO_GOVERNOR_V0](../periphery/ENERGY_THERMO_GOVERNOR_V0.md) · `docs/periphery/ENERGY_THERMO_GOVERNOR_V0.md` *(référence probable)*
  <br>Bloc périphérique non souverain. Sortie attendue : PeripheralSignalPacket.
- [THERMODYNAMIC FRAMEWORK PREFLIGHT V0](../thermodynamic_framework/THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0.md) · `docs/thermodynamic_framework/THERMODYNAMIC_FRAMEWORK_PREFLIGHT_V0.md` *(référence probable)*
  <br>Generated: 2026-06-17T20:17:49

<details><summary><b>Rapports, audits et preuves d'exécution</b> (12)</summary>

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [F19A_THERMO_COHERENCE_TIME_PAYLOAD_8000_20260528_011049.json](../runtime/F19A_THERMO_COHERENCE_TIME_PAYLOAD_8000_20260528_011049.json)
- [F19A_THERMO_COHERENCE_TIME_PAYLOAD_8012_20260528_011049.json](../runtime/F19A_THERMO_COHERENCE_TIME_PAYLOAD_8012_20260528_011049.json)
- [F19B_8000_THERMO_COHERENCE_TIME_UNIFIED_PAYLOAD.json](../runtime/F19B_8000_THERMO_COHERENCE_TIME_UNIFIED_PAYLOAD.json)
- [F19B_8012_THERMO_COHERENCE_TIME_UNIFIED_PAYLOAD.json](../runtime/F19B_8012_THERMO_COHERENCE_TIME_UNIFIED_PAYLOAD.json)
- [F19B_TERMINAL_THERMO_UNIFIED_8000.txt](../runtime/F19B_TERMINAL_THERMO_UNIFIED_8000.txt)
- [F19B_TERMINAL_THERMO_UNIFIED_8012.txt](../runtime/F19B_TERMINAL_THERMO_UNIFIED_8012.txt)
- [OBSIDIA_F19A2_TARGETED_THERMO_COHERENCE_TIME_AUDIT_20260528_011308.json](../runtime/OBSIDIA_F19A2_TARGETED_THERMO_COHERENCE_TIME_AUDIT_20260528_011308.json)
- [OBSIDIA_F19A2_TARGETED_THERMO_COHERENCE_TIME_AUDIT_20260528_011308.txt](../runtime/OBSIDIA_F19A2_TARGETED_THERMO_COHERENCE_TIME_AUDIT_20260528_011308.txt)
- [OBSIDIA_F19A_THERMO_COHERENCE_TIME_SCORING_AUDIT_20260528_011049.json](../runtime/OBSIDIA_F19A_THERMO_COHERENCE_TIME_SCORING_AUDIT_20260528_011049.json)
- [OBSIDIA_F19A_THERMO_COHERENCE_TIME_SCORING_AUDIT_20260528_011049.txt](../runtime/OBSIDIA_F19A_THERMO_COHERENCE_TIME_SCORING_AUDIT_20260528_011049.txt)
- [OBSIDIA_F19B_THERMO_COHERENCE_TIME_UNIFIED_REPORT_20260528_032132.md](../runtime/OBSIDIA_F19B_THERMO_COHERENCE_TIME_UNIFIED_REPORT_20260528_032132.md) — OBSIDIA F19B — THERMO / COHERENCE / TIME UNIFIED PACKET
- [OBSIDIA_F3_THERMO_OPERATIONAL_REPORT.md](../runtime/OBSIDIA_F3_THERMO_OPERATIONAL_REPORT.md) — OBSIDIA F3 — THERMODYNAMICS OPERATIONAL REPORT

</details>

## Fichiers liés au code

13 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
