# 15 · Atlas et signaux externes

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Les observations externes et leur provenance, en lecture seule.

## Où elle intervient dans le trajet d'une demande

- **Étape 1 · Entrée** : Une demande arrive : message humain, code, document, donnée, événement ou signal externe.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

D'après le registre de fonctionnalités V3, **61 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `specs/external_signals/` | 37 |
| `runtime_contracts/atlas_scenario_spec/` | 9 |
| `runtime_contracts/external_signals_dry_run/` | 7 |
| `_source_discovery/F06_ATLAS_CANON_REPAIR_20260602_160517/` | 2 |
| `_source_discovery/F06_ATLAS_IMPORT_AUDIT_20260602_160052/` | 2 |
| `runtime_contracts/boundaries/` | 2 |
| `agents/prompts/` | 1 |
| `periphery/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (4)

### Documents de référence — à lire en premier

- [OBSIDIA RSSI External Signals Patch V1](../source_packs/external_signals/README.md) · `docs/source_packs/external_signals/README.md`
  <br>This patch adds the missing external-category signal layer for the RSSI pack.
- [Merge Instructions for RSSI Zip](../source_packs/external_signals/MERGE_INSTRUCTIONS.md) · `docs/source_packs/external_signals/MERGE_INSTRUCTIONS.md` *(référence probable)*
  <br>Apply this patch to the RSSI zip by copying the directories into the RSSI pack root.

<details><summary><b>Rapports, audits et preuves d'exécution</b> (2)</summary>

**`docs/source_packs/external_signals/`** · *dossier lu par du code : ne pas déplacer*

- [SHA256SUMS.txt](../source_packs/external_signals/SHA256SUMS.txt)
- [VALIDATION_REPORT.yaml](../source_packs/external_signals/VALIDATION_REPORT.yaml)

</details>

## Fichiers liés au code

4 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
