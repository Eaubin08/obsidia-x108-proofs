# REPRODUCIBILITY_BOUNDARY_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `docs/architecture/F74_F77_FINALIZATION_AUDIT.md` (section Fresh Clone)
- `QUICKSTART.md`, `QUICKSTART_FRESH_CLONE.md`

Source Status: DOC_ONLY

Scope: Définir les limites de reproductibilité du repo Obsidia.

Allowed:
- "F74 Fresh Clone est reproductible sur Windows et Linux avec les procédures documentées"
- "La procédure fresh clone est dans QUICKSTART_FRESH_CLONE.md"

Forbidden:
- "Le repo est deployable en production sans configuration" (F76 bloque)
- "Fresh clone = production deployment"

Inputs: F74_F77_SOURCE.md
Outputs: Frontière reproductibilité ↔ déploiement
Metrics: N/A
Invariants: Reproductibilité locale ≠ production readiness
X108 Boundary: KX108_ONLY
Tests Required: Test fresh clone sur Windows + Linux
Proof Expected: Procédure exécutable
Runtime Status: DOC_ONLY
Claim-Scope Notes: Reproductibilité = F74 COMPLETE. Production = F76 PROD_BLOCKED.
Open Questions: Aucune
