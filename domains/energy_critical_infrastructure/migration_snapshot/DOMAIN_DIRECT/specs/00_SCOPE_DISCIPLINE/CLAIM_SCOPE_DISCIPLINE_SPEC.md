# CLAIM_SCOPE_DISCIPLINE_SPEC

Status: SOURCE_ORGANIZED
Authority: KX108_ONLY

Source Paths:
- `docs/PROOF_SCOPE.md` (SOURCE_CANON)
- `docs/V3_V4_GAP_ANALYSIS.md`
- `docs/architecture/F74_F77_FINALIZATION_AUDIT.md`
- `_source_discovery/OBSIDIA_SOURCE_DISCOVERY_MAP_V1/SOURCE_DISCOVERY_REPORT.md`

Source Status: SOURCE_CANON + DOC_ONLY

Scope:
Définir précisément ce qu'Obsidia peut affirmer publiquement, et ce qui est interdit en claim-scope.

Allowed:
- "Le périmètre public P1 contient 4 catégories de preuves distinctes"
- "22 domaines V3+V4 sont implémentés en Python avec 194 tests"
- "F74 Fresh Clone est reproductible"
- "Obsidia calcule Lyapunov, PoG, governed_state en Python"
- "Gencoin est un ledger de valeur candidate — pas un token"
- "GPS connector = DRY_RUN local — pas défense production"

Forbidden:
- "Obsidia est production-ready" (tant que F76 PROD_BLOCKED)
- "Obsidia est cloud-ready" (blockers présents)
- "Obsidia est AGI-ready" (HORS_SCOPE)
- "Lyapunov est formellement prouvé" (FORMAL_PROOF_PENDING)
- "Gencoin est un token réel" (INTERDIT absolu)
- "GPS = défense production" (DRY_RUN seulement)
- "NPL prouve la provenance d'une pensée"
- "fully formally proven" (seul le noyau Lean est LEAN_PROVEN)

Inputs: Sources Plan 1 + Plan 1 NPL Extension

Outputs: Liste de claims autorisés et interdits, sourcés

Metrics: Aucune métrique — règle de discours

Invariants:
- Tout claim public doit être tracé à une source réelle
- COMPLETE ≠ preuve formelle
- PASS Python ≠ LEAN_PROVEN
- DRY_RUN ≠ production

X108 Boundary:
- KX108_ONLY pour toute action — le claim-scope ne contourne pas X108

Tests Required:
- Scan des docs publiques pour détecter les claims interdits

Proof Expected: Aucun proof formel — règle documentaire

Runtime Status: DOC_ONLY

Claim-Scope Notes:
Cette spec est elle-même une limite de discours — elle ne nécessite pas de runtime.

Open Questions:
- Jcoin : alias Gencoin ou concept distinct ? (ABSENT_UNDER_THIS_NAME)
- 7 flux exacts : dans périmètre public ou hors ? (HORS selon docs/REPO_BOUNDARY.md)
