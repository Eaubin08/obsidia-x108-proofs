# 30 · Outillage, CI, staging

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Scripts développeur, CI, skills et outils d'inspection.

## Où elle intervient dans le trajet d'une demande

Couche **transverse** : elle encadre toutes les étapes plutôt qu'une seule.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

D'après le registre de fonctionnalités V3, **262 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `scripts/` | 108 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 65 |
| `tools/inspection/` | 13 |
| `.agents/skills/` | 11 |
| `scripts/performance/` | 10 |
| `.claude/skills/` | 9 |
| `.claude/commands/` | 8 |
| `.claude/context/` | 8 |
| `scripts/runtime/` | 6 |
| `tools/maintenance/` | 6 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (5)

### Documents de référence — à lire en premier

- [AI_TERMINAL_FIRST_COLLAB_PROTOCOL](../AI_TERMINAL_FIRST_COLLAB_PROTOCOL.md) · `docs/AI_TERMINAL_FIRST_COLLAB_PROTOCOL.md`
  <br>Protocole canonique de collaboration terminal-first entre Étienne et l’IA pour coder, patcher, auditer et générer des artefacts sans édition manuelle.
- [Politique CI/CD](../CI_POLICY.md) · `docs/CI_POLICY.md`
  <br>Ce document décrit la politique de CI/CD du dépôt obsidia-x108-proofs.
- [Local CI Runbook V1](../ci/LOCAL_CI_RUNBOOK_V1.md) · `docs/ci/LOCAL_CI_RUNBOOK_V1.md`
  <br>powershell -ExecutionPolicy Bypass -File scripts/runcilocal.ps1
- [GitHub Module](../github/README.md) · `docs/github/README.md`
  <br>GitHub workflow guard. Prevents automatic merges, enforces review requirements, and ensures no autonomous repository mutations. All GitHub actions require explicit human approval.
- [Protected Files CI Gate V1](../ci/PROTECTED_FILES_CI_GATE_V1.md) · `docs/ci/PROTECTED_FILES_CI_GATE_V1.md` *(référence probable)*
  <br>sigma/guard.py

## Fichiers liés au code

4 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
