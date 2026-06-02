# WHO_CAN_READ_WRITE_DECIDE_ACT

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `docs/freeze/BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md`
- `periphery/x108_ingress/readonly_context_ingress.py`
- `periphery/brody/brody_runtime_readonly.py`
- `sigma/graphiti_readonly_bridge.py`

Source Status: SOURCE_CANON + RUNTIME_CODE

Scope: Matrice des droits read/write/decide/act pour chaque couche Obsidia.

Allowed:
- Utiliser cette matrice comme référence normative

Forbidden:
- Modifier les droits sans mise à jour de cette spec et de BRODY_RIGHTS_AUTHORITY_MATRIX_REPORT.md

Inputs: Sources de tous les composants

Outputs: Matrice de droits

Metrics: N/A

Invariants:
| Composant | Read | Write | Decide | ACT |
|-----------|------|-------|--------|-----|
| KX108 | OUI | OUI | OUI | OUI |
| Sigma | OUI | NON | NON | NON |
| Tree34 | OUI | NON | NON | NON |
| Brody | OUI | NON* | NON | NON |
| Graphiti | OUI | NON* | NON | NON |
| NPL | OUI | NON | NON | NON |
| Gencoin | OUI | NON** | NON | NON |
| GPS/Aviation | OUI | NON | NON | NON |
| Balance | OUI | NON | NON | NON |
| Agents 52 | OUI | NON | NON | NON |

*Write mémoire = gate humain obligatoire
**Write ledger = X108 ALLOW + OS3_PROOF obligatoires

X108 Boundary: KX108_ONLY = seul composant avec tous les droits
Tests Required: test_no_write_without_gate (Brody, Graphiti)
Proof Expected: Python test (assert_readonly())
Runtime Status: RUNTIME_CODE
Claim-Scope Notes: Cette matrice est contractuelle — respectée dans tous les Plans.
Open Questions: Aucune
