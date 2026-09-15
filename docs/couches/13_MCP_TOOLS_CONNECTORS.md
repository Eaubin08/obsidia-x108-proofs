# 13 · Connecteurs, outils, MCP

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

L'admission des outils et l'interaction avec l'extérieur, isolées de toute autorité de décision.

## Où elle intervient dans le trajet d'une demande

- **Étape 1 · Entrée** : Une demande arrive : message humain, code, document, donnée, événement ou signal externe.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

D'après le registre de fonctionnalités V3, **39 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `specs/07_AGENTS_CONNECTORS_MCP/` | 10 |
| `connectors/` | 7 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 5 |
| `runtime_terrain_bank_trading_gps/connectors/` | 3 |
| `Demo-obsidia-x108-proof/connectors/` | 2 |
| `periphery/mcp/` | 2 |
| `scripts/` | 2 |
| `.claude/hooks/` | 1 |
| `.mcp.json/` | 1 |
| `periphery/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (4)

### Documents de référence — à lire en premier

- [MCP Module](../mcp/README.md) · `docs/mcp/README.md`
  <br>MCP permission matrix. Tool access is not permission. The matrix defines which tools are available to which agents — but availability does not imply authority. X108 is the sole…

<details><summary><b>Rapports, audits et preuves d'exécution</b> (3)</summary>

**`docs/`**

- [GITHUB_MCP_BENCHMARK_BACKLOG_REPORT.md](../GITHUB_MCP_BENCHMARK_BACKLOG_REPORT.md) — GitHub / MCP / Benchmark Governance Report

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P70_NETWORK_EGRESS_CONNECTORS_AUDIT.json](../core_import/P70_NETWORK_EGRESS_CONNECTORS_AUDIT.json)

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [LIVE_CONNECTORS_FINAL_FREEZE_20260527.md](../runtime/LIVE_CONNECTORS_FINAL_FREEZE_20260527.md) — LIVE_CONNECTORS_FINAL_FREEZE_20260527

</details>

## Fichiers liés au code

4 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
