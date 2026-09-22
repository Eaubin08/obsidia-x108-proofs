# 24 · Méthodes formelles : Lean et TLA+

> Guide de couche généré le 2026-09-15 à partir de `main` (5d27d003). Il sert d'**index** : aucun document n'a été déplacé, chaque lien pointe vers l'emplacement actuel du fichier.

## À quoi sert cette couche

Spécifications et preuves formelles (Lean 4, TLA+, obligations). Elles prouvent des propriétés bornées et ne prennent aucune décision métier.

## Où elle intervient dans le trajet d'une demande

- **Étape 5 · Preuves et gouvernance** : Tests, replay, Lean, ProofKit, receipts et checkpoints établissent ce qui est prouvé, avant tout passage au réel.

Voir le trajet complet : [guide général](../README.md).

## Où est son code aujourd'hui

**Points d'entrée connus :**

- [proofs/lean/](../../proofs/lean) · preuves Lean 4 · PROTÉGÉ
- [formal/tla/](../../formal/tla) · specs TLA+ lancées par la CI · PROTÉGÉ
- [periphery/lean_sandbox/](../../periphery/lean_sandbox) · bac à sable Lean

D'après le registre de fonctionnalités V3, **325 fichier(s)** du dépôt relèvent de cette couche. Principaux emplacements :

| Dossier | Fichiers |
|---|---:|
| `periphery/lean_sandbox/` | 151 |
| `proofs/lean/` | 114 |
| `formal/tla/` | 35 |
| `proofs/tla/` | 9 |
| `periphery/OBSIDIA_V4_STRUCTURED_FULL/` | 6 |
| `_FREEZE/VERIFY_CLAUDE_LEAN_ANALYSIS_20260626_155453/` | 3 |
| `_source_discovery/OBSIDIA_INVARIANT_GRAPH_AUDIT_V1/` | 3 |
| `specs/_invariant_graph/` | 2 |
| `external_pack/` | 1 |
| `proofs/` | 1 |

*Le registre V3 est partiel : 832 fichiers de code n'y sont pas classés et 304 fichiers récents n'y figurent pas. Les points d'entrée ci-dessus viennent de START_HERE.md, MODULE_MAP.md et docs/SIGMA.md.*

## Documents (21)

### Documents de référence — à lire en premier

- [F68.1 ? OpenAPI Duplicate X108 Status Cleanup](../architecture/F68_1_OPENAPI_DUPLICATE_X108_STATUS_CLEANUP.md) · `docs/architecture/F68_1_OPENAPI_DUPLICATE_X108_STATUS_CLEANUP.md`
  <br>- Status: PASS
- [F73.2 ? Runtime Blocker False Positive Cleanup](../architecture/F73_2_RUNTIME_BLOCKER_CLEANUP.md) · `docs/architecture/F73_2_RUNTIME_BLOCKER_CLEANUP.md`
  <br>- Status: PASSRUNTIMEBLOCKERCLEANED
- [FORMALISATION MATHÉMATIQUE — INDEX MAÎTRE](../formalisation_math/INDEX.md) · `docs/formalisation_math/INDEX.md`
  <br>Obsidia X-108 | Kernel déterministe souverain
- [GENCOIN_FORMAL_MATH_SPEC_V0_2](../gencoin/GENCOIN_FORMAL_MATH_SPEC_V0_2.md) · `docs/gencoin/GENCOIN_FORMAL_MATH_SPEC_V0_2.md`
  <br>GC = X108ALLOW × OS3PROOF × DATAOK × MEMORYSTABLE × ENERGYSTABLE × OCSTABLE × PERMISSIONOK × ECONOMICOK × max(0, VALUE-DEBT).
- [FILE DE FORMALISATION ET DE PREUVE — V3.2](../formalisation_math/FILE_DE_PREUVE.md) · `docs/formalisation_math/FILE_DE_PREUVE.md` *(référence probable)*
  <br>Source : V32ACTIONABLEARCHITECTUREGUIDE/08FORMALIZATIONANDPROOFQUEUE.md (2026-06-21)
- [GPS L-02 / L-06 Mapping Note](../formalisation_math/GPS_L02_L06_MAPPING_NOTE.md) · `docs/formalisation_math/GPS_L02_L06_MAPPING_NOTE.md` *(référence probable)*
  <br>Status: MAPPINGNOTENOTFINALPROOF
- [LYAPUNOV, PROOF OF GOVERNANCE ET ÉNERGIE — Spécification mathématique](../formalisation_math/LYAPUNOV_ET_POG.md) · `docs/formalisation_math/LYAPUNOV_ET_POG.md` *(référence probable)*
  <br>Note : Ces formules sont des spécifications Python pour le scoring de gouvernance runtime.
- [SCOPE ET PÉRIMÈTRE DES PREUVES — Obsidia X-108](../formalisation_math/SCOPE_ET_PERIMETRE.md) · `docs/formalisation_math/SCOPE_ET_PERIMETRE.md` *(référence probable)*
  <br>- Répertoire : proofs/lean/
- [STATUTS DE FORMALISATION MATHÉMATIQUE — Pépites et Lois](../formalisation_math/STATUTS_FORMALISATION.md) · `docs/formalisation_math/STATUTS_FORMALISATION.md` *(référence probable)*
- [THÉORÈMES LEAN 4 ET TLA+ — TEXTE BRUT DES FICHIERS](../formalisation_math/THEOREMES_LEAN4_TLA_BRUTS.md) · `docs/formalisation_math/THEOREMES_LEAN4_TLA_BRUTS.md` *(référence probable)*
  <br>-- decisioneqACTiff
- [INVENTAIRE DES THÉORÈMES LEAN 4 — Obsidia X-108](../formalisation_math/THEOREMES_LEAN_INVENTAIRE.md) · `docs/formalisation_math/THEOREMES_LEAN_INVENTAIRE.md` *(référence probable)*
  <br>Localisation : periphery/OBSIDIAV4STRUCTUREDFULL/08PREUVESLEANTLA/

<details><summary><b>Rapports, audits et preuves d'exécution</b> (5)</summary>

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.json](../core_import/P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.json)
- [P77_CANON_WORDING_TARGETED_CLEANUP.json](../core_import/P77_CANON_WORDING_TARGETED_CLEANUP.json)

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_F2C_ANTI_MISMATCH_FORMAL_REPORT.md](../runtime/OBSIDIA_F2C_ANTI_MISMATCH_FORMAL_REPORT.md) — OBSIDIA F2C — ANTI-MISMATCH FORMAL REPORT
- [OBSIDIA_F5A_34_TREES_FORMAL_AUDIT_REPORT_20260527_214458.md](../runtime/OBSIDIA_F5A_34_TREES_FORMAL_AUDIT_REPORT_20260527_214458.md) — OBSIDIA F5A — 34 TREES FORMAL AUDIT REPORT

**`docs/security/`** · *dossier lu par du code : ne pas déplacer*

- [PUBLICATION_SECURITY_GATE_CLEAN.json](../security/PUBLICATION_SECURITY_GATE_CLEAN.json)

</details>

<details><summary><b>Rapports de phases passées</b> (4)</summary>

**`docs/core_import/`** · *dossier lu par du code : ne pas déplacer*

- [P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.md](../core_import/P72_INVARIANT_GRAPH_FORMAL_PROOF_ALIGNMENT.md) — P72 — Invariant Graph & Formal Proof Alignment
- [P77_CANON_WORDING_TARGETED_CLEANUP.md](../core_import/P77_CANON_WORDING_TARGETED_CLEANUP.md) — P77 — Canon Wording Targeted Cleanup

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_F23A6_BLOCK_CHECKPOINT_CLEAN_20260528_224425.md](../runtime/OBSIDIA_F23A6_BLOCK_CHECKPOINT_CLEAN_20260528_224425.md) — OBSIDIA F23A6 — CLEAN BLOCK CHECKPOINT

**`docs/status/`** · *dossier lu par du code : ne pas déplacer*

- [PUBLIC_REPO_CLEANUP_FREEZE_20260526.md](../status/PUBLIC_REPO_CLEANUP_FREEZE_20260526.md) — PUBLIC REPO CLEANUP FREEZE — 2026-05-26

</details>

<details><summary><b>Archives</b> (1)</summary>

**`docs/runtime/`** · *dossier lu par du code : ne pas déplacer*

- [OBSIDIA_F31_0_CLEANUP_UNTRACKED_DEBT_INVENTORY_20260529_014612.json](../runtime/OBSIDIA_F31_0_CLEANUP_UNTRACKED_DEBT_INVENTORY_20260529_014612.json)

</details>

## Fichiers liés au code

14 de ces documents sont lus par des scripts, des tests, l'API ou le Workbench, directement ou via leur dossier. Ils restent donc à leur place tant que ce code n'est pas adapté.

---
*Classement automatique : carte du guide V3 et règles sur les noms de fichiers. Une erreur de couche se corrige dans la carte de rangement.*
