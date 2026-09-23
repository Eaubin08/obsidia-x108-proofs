# RUNTIME_STATUS_TAXONOMY

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1/SOURCE_STATUS_TAXONOMY.md`

Source Status: DOC_ONLY

Scope:
Définir la taxonomie canonique des statuts de runtime pour toutes les specs Obsidia.

Allowed:
- Utiliser les statuts définis ci-dessous dans toutes les specs

Forbidden:
- Inventer de nouveaux statuts sans mise à jour de cette spec
- Confondre RUNTIME_CODE et LEAN_PROVEN

Inputs: SOURCE_STATUS_TAXONOMY.md (Plan 1)

Outputs: Taxonomie de référence

Metrics: N/A

Invariants:
| Statut | Signification |
|--------|---------------|
| SOURCE_CANON | Fichier gelé — ne pas modifier sans protocole |
| RUNTIME_CODE | Code Python exécutable — pas de preuve formelle |
| PYTHON_SPEC | Python servant de spec — FORMAL_PROOF_PENDING |
| LEAN_PROVEN | Prouvé Lean 4 — périmètre proofs/lean/ uniquement |
| FORMAL_TLA | TLA+ vérifié TLC — périmètre formal/tla/ |
| PYTHON_TEST_ONLY | Tests Python uniquement |
| DOC_ONLY | Documentation Markdown |
| PLACEHOLDER | Stub minimal — pas d'implémentation |
| CANDIDATE | Données ou calculs candidats |
| DRY_RUN | Jamais exécuté en production |
| PROD_BLOCKED | Blocage technique vers production |
| PACK_PARTIAL | Pack externe incomplet |
| ABSENT_UNDER_THIS_NAME | Introuvable sous ce nom exact |
| SOURCE_FOUND_UNDER_DIFFERENT_NAME | Présent sous un autre nom |
| ABSENT_LOCAL_REPO | Repo absent du disque local |

X108 Boundary: KX108_ONLY

Tests Required: N/A

Proof Expected: N/A

Runtime Status: DOC_ONLY

Claim-Scope Notes:
Cette taxonomie est la référence normative pour toutes les specs Plan 2 et Plan 3.

Open Questions: Aucune
