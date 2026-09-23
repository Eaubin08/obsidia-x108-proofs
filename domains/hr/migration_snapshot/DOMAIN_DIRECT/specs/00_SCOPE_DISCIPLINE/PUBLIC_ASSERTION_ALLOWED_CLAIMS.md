# PUBLIC_ASSERTION_ALLOWED_CLAIMS

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `docs/PROOF_SCOPE.md`, `docs/V3_V4_GAP_ANALYSIS.md`, `docs/architecture/F74_F77_FINALIZATION_AUDIT.md`
- `docs/blockchain/GENCOIN_NOT_A_TOKEN_POLICY_V1.md`
- `docs/release/BRODY_GPT_V1_LIMITATIONS_AND_BOUNDARIES.md`

Source Status: SOURCE_CANON + DOC_ONLY

Scope: Liste exhaustive des claims publics autorisés et interdits.

Allowed:
**Claims autorisés :**
- "Obsidia X-108 est un moteur de gouvernance déterministe"
- "Le périmètre public P1 contient des preuves Lean 4, TLA+, Python et Sigma"
- "Le noyau X-108 est l'unique autorité décisionnelle (ALLOW/HOLD/BLOCK)"
- "22 domaines V3+V4 implémentés en Python — 194 tests pass"
- "Gencoin est un ledger de valeur candidate — pas un token blockchain"
- "Brody est readonly et advisory — pas de décision autonome"
- "F74 Fresh Clone est reproductible sur Windows et Linux"
- "Les 34 arbres cognitifs fournissent des signaux contextuels — pas des décisions"
- "NPL est une couche de signaux contextuels narratifs, readonly"

Forbidden:
**Claims interdits :**
- "production-ready" (F76 PROD_BLOCKED)
- "cloud-ready" (F76 blockers)
- "AGI-ready" (HORS_SCOPE)
- "fully formally proven" (seul noyau Lean)
- "Gencoin est un token" (INTERDIT)
- "Jcoin existe dans le repo" (ABSENT)
- "NPL diagnostique/décide/prouve provenance"
- "GPS/aviation en défense production" (DRY_RUN)
- "Lyapunov formellement prouvé" (FORMAL_PROOF_PENDING)

Inputs: Sources Plan 1 + Plan 1 NPL
Outputs: Guide de discours public
Metrics: N/A
Invariants: Tout claim public = source traçable
X108 Boundary: KX108_ONLY
Tests Required: Scan docs publiques
Proof Expected: N/A
Runtime Status: DOC_ONLY
Claim-Scope Notes: Cette spec est la référence pour tout discours public sur Obsidia.
Open Questions: Jcoin / 7 flux / .xyz — décision humaine requise
